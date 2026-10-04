"""Run one manual OpenStreetMap import from exclusion to the routing pointer and return its outcome."""

import asyncio
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy import Connection

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_business_now, fetch_monotonic_seconds
from config.logging import fetch_logger
from data.engine import build_import_engine
from data.import_process import ImportProcessFailedError
from data.import_workspace import ImportWorkspaceUnconfirmed
from data.local_lock import ImportAlreadyRunning
from data.locks import ImportLease, ImportLeaseLost, apply_import_exclusion
from data.osm_copy import fetch_osm_copy_history
from data.osm_network_file import OsmNetworkFileError
from data.osm_reader import OsmReadError
from data.osm_source import OsmDownloadError, build_osm_http_client
from data.osm_valhalla import OsmTileBuildError, fetch_osm_valhalla_template
from data.publication import PublicationOutcomeUnknown, PublicationRolledBack, apply_publication
from data.routing_data import RoutingDataError, apply_routing_directory_removal, apply_routing_pointer, build_routing_copy_name, fetch_routing_preparations
from service.osm_acquisition import fetch_osm_extract
from service.osm_geometry import OsmGeometryError
from service.osm_publication import OsmPublicationCounts, apply_osm_copy_publication, fetch_osm_commit_outcome
from service.osm_routing_preparation import OsmPreparedCopy, apply_osm_routing_preparation, fetch_osm_prepared_copy
from service.osm_routing_recovery import OsmRoutingIntegrityError, apply_osm_routing_recovery
from service.osm_source_validation import OsmSourceError, resolve_osm_source_is_newer
from service.osm_tag_values import OsmTagError

OSM_IMPORT_RUN_SECONDS = 3600
OSM_IMPORT_GUARD_STATEMENT_TIMEOUT_MS = 5000

type OsmImportOutcome = Literal["updated", "unchanged", "skipped", "routing_incomplete", "commit_unknown"]


class OsmImportError(RuntimeError):
    """Report a publication that is proven not to have been committed."""


OSM_IMPORT_NAMED_ERRORS: tuple[type[Exception], ...] = (
    OsmImportError,
    OsmSourceError,
    OsmDownloadError,
    OsmReadError,
    OsmGeometryError,
    OsmTagError,
    OsmNetworkFileError,
    OsmTileBuildError,
    RoutingDataError,
    OsmRoutingIntegrityError,
    PublicationRolledBack,
    ImportLeaseLost,
    ImportWorkspaceUnconfirmed,
    ImportProcessFailedError,
    DeadlineExpiredError,
)
"""Importer failures whose messages are constant texts without data, so the operator report may show them."""


@dataclass(frozen=True)
class OsmImportSettings:
    """Hold the paths and the business zone one import needs, already validated by the configuration."""

    workspace_root: Path
    routing_root: Path
    tool_directory: Path
    config_template: Path
    zone: ZoneInfo


@dataclass(frozen=True)
class OsmImportResult:
    """Report what one run achieved: its outcome, the source instant it handled and what publication wrote."""

    outcome: OsmImportOutcome
    state_at: datetime | None
    counts: OsmPublicationCounts | None


def apply_osm_import_command(settings: OsmImportSettings) -> OsmImportResult:
    """Run one import with the importer's own HTTP client policy, for the administrative entry point."""

    async def apply_run() -> OsmImportResult:
        """Own the HTTP client for the whole run."""
        async with build_osm_http_client() as client:
            return await apply_osm_import(settings, client)

    return asyncio.run(apply_run())


async def apply_osm_import(settings: OsmImportSettings, client: httpx.AsyncClient) -> OsmImportResult:
    """
    Run one import under import exclusion and one 60-minute run deadline.

    Another run holding exclusion gives skipped. Everything after admission - recovery, acquisition, preparation,
    publication and the pointer - happens while exclusion is held, and exclusion is released only after every file,
    tool and database operation of the run has ended.
    """
    run_deadline = build_deadline(OSM_IMPORT_RUN_SECONDS, fetch_monotonic_seconds())
    engine = build_import_engine(OSM_IMPORT_GUARD_STATEMENT_TIMEOUT_MS)
    try:
        with ExitStack() as stack:
            try:
                lease = stack.enter_context(apply_import_exclusion(engine, settings.workspace_root))
            except ImportAlreadyRunning:
                return OsmImportResult("skipped", None, None)
            return await apply_osm_import_run(settings, client, lease, run_deadline)
    finally:
        engine.dispose()


async def apply_osm_import_run(settings: OsmImportSettings, client: httpx.AsyncClient, lease: ImportLease, run_deadline: Deadline) -> OsmImportResult:
    """
    Carry out an admitted run in the order recovery, acquisition, preparation, publication and pointer.

    An equal source state gives unchanged after recovery; preparation finishes before the database transaction starts;
    the pointer changes only after a confirmed commit, and a pointer failure after commit gives routing_incomplete.
    """
    template = fetch_osm_valhalla_template(settings.config_template)
    for preparation in fetch_routing_preparations(settings.routing_root):
        apply_routing_directory_removal(preparation)
    with lease.engine.connect() as connection:
        history = fetch_osm_copy_history(connection)
    committed_state_at = history[0].state_at.instant if history else None
    apply_osm_routing_recovery(settings.routing_root, committed_state_at)
    async with fetch_osm_extract(client, lease.workspace_lease.workspace, run_deadline.expires_at) as extract:
        if not resolve_osm_source_is_newer(extract.state_at, committed_state_at):
            return OsmImportResult("unchanged", extract.state_at, None)
        prepared = fetch_osm_prepared_copy(extract.path, run_deadline, settings.zone)
    committed_names = frozenset(build_routing_copy_name(snapshot.state_at.instant) for snapshot in history)
    apply_osm_routing_preparation(lease.workspace_lease, settings.routing_root, prepared.network, prepared.boundary, extract.state_at, committed_names, template, settings.tool_directory, run_deadline)
    publication, counts = apply_osm_publication_step(lease, prepared, extract.state_at, extract.filename, run_deadline)
    if publication == "commit_unknown":
        return OsmImportResult("commit_unknown", extract.state_at, None)
    try:
        apply_routing_pointer(settings.routing_root, build_routing_copy_name(extract.state_at))
    except RoutingDataError:
        fetch_logger(__name__).exception("Routing pointer publication failed after commit")
        return OsmImportResult("routing_incomplete", extract.state_at, counts)
    return OsmImportResult("updated", extract.state_at, counts)


def build_osm_stamp(value: datetime) -> datetime:
    """Cut a server-stamped instant to the whole millisecond the schema's timestamptz(3) columns store."""
    return value.replace(microsecond=value.microsecond // 1000 * 1000)


def apply_osm_publication_step(
    lease: ImportLease, prepared: OsmPreparedCopy, state_at: datetime, filename: str, run_deadline: Deadline
) -> tuple[Literal["committed", "commit_unknown"], OsmPublicationCounts | None]:
    """
    Publish through the shared transaction and say whether the copy is committed, with the counts when they are known.

    The shared transaction reports any refusal inside the callback only as a rollback, so the callback keeps its named
    refusal to report it instead. A lost commit confirmation is settled by the bounded outcome checks: a copy proven
    absent is a failure, a copy proven present is committed with unknown counts, and no answer leaves it unknown.
    """
    made_current_at = build_osm_stamp(fetch_business_now())
    refusals: list[Exception] = []

    def apply_write(connection: Connection) -> OsmPublicationCounts:
        """Keep a named refusal of the publication rules before the transaction rolls back."""
        try:
            return apply_osm_copy_publication(connection, prepared, state_at, filename, made_current_at)
        except OsmSourceError as refusal:
            refusals.append(refusal)
            raise

    try:
        return "committed", apply_publication(lease, run_deadline, apply_write).value
    except PublicationRolledBack:
        if refusals:
            raise refusals[0] from None
        raise
    except PublicationOutcomeUnknown:
        committed = fetch_osm_commit_outcome(lease, state_at, run_deadline)
        if committed is None:
            return "commit_unknown", None
        if not committed:
            raise OsmImportError("Publication was not committed") from None
        return "committed", None
