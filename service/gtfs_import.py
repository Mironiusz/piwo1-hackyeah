"""Run the manual GTFS step of the loading program: fetch the three feeds, keep the last complete copy and build the routing data with public transport for the OpenStreetMap copy in use."""

from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from config.logging import fetch_logger
from data.engine import build_import_engine
from data.gtfs_copy import GtfsCopy, GtfsCopyError, apply_gtfs_copy, apply_gtfs_preparation, build_gtfs_feed_path, fetch_gtfs_copy, fetch_gtfs_preparations
from data.gtfs_source import GTFS_FEEDS, GtfsSourceError, build_gtfs_http_client, fetch_gtfs_feed
from data.import_process import ImportProcessFailedError
from data.import_workspace import ImportWorkspaceUnconfirmed, WorkspaceLease
from data.local_lock import ImportAlreadyRunning
from data.locks import ImportLeaseLost, apply_import_exclusion
from data.osm_valhalla import OsmTileBuildError, apply_osm_valhalla_config, fetch_osm_valhalla_template
from data.routing_data import ROUTING_COPIES_NAME, RoutingDataError, apply_routing_directory_removal, build_routing_copy_name, fetch_osm_routing_manifest, fetch_routing_pointer
from data.transit_build import (
    TRANSIT_ARCHIVE_NAME,
    TransitBuildError,
    apply_transit_build,
    apply_transit_pointer,
    apply_transit_preparation,
    build_transit_directory,
    build_transit_name,
    fetch_transit_pointer,
    fetch_transit_preparations,
    resolve_transit_copy_name,
)
from service.gtfs_feeds import GtfsFeedError, apply_gtfs_feed_preparation
from service.osm_routing_preparation import build_osm_valhalla_config

GTFS_IMPORT_RUN_SECONDS = 1800
GTFS_IMPORT_GUARD_STATEMENT_TIMEOUT_MS = 5000
TRANSIT_FEEDS_NAME = "transit_feeds"
GTFS_CHECK_NAME = "gtfs_check"
TRANSIT_TILES_NAME = "transit_tiles"
TRANSIT_TIMEZONE_NAME = "timezones.sqlite"
TRANSIT_CONFIG_NAME = "valhalla_transit.json"

type GtfsImportOutcome = Literal["built", "reused", "skipped", "no_gtfs_copy", "no_osm_copy"]
type GtfsFetchOutcome = Literal["fetched", "failed", "not_run"]

GTFS_IMPORT_NAMED_ERRORS: tuple[type[Exception], ...] = (
    GtfsSourceError,
    GtfsCopyError,
    GtfsFeedError,
    TransitBuildError,
    OsmTileBuildError,
    RoutingDataError,
    ImportLeaseLost,
    ImportWorkspaceUnconfirmed,
    ImportProcessFailedError,
    DeadlineExpiredError,
)
"""Failures of the GTFS step whose messages are constant texts without data, so the operator report may show them."""


@dataclass(frozen=True)
class GtfsImportSettings:
    """Hold the paths of the importer the GTFS step reuses, already validated by the configuration."""

    workspace_root: Path
    routing_root: Path
    tool_directory: Path
    config_template: Path


@dataclass(frozen=True)
class GtfsImportResult:
    """Report what one run achieved: its outcome, what became of the fresh fetch and the routing data with public transport it pointed to."""

    outcome: GtfsImportOutcome
    fetch: GtfsFetchOutcome
    transit_name: str | None


def apply_gtfs_import_command(settings: GtfsImportSettings) -> GtfsImportResult:
    """Run one GTFS step with its own HTTP client and a 30-minute run deadline, for the administrative entry point."""
    with build_gtfs_http_client() as client:
        return apply_gtfs_import(settings, client, build_deadline(GTFS_IMPORT_RUN_SECONDS, fetch_monotonic_seconds()))


def apply_gtfs_import(settings: GtfsImportSettings, client: httpx.Client, deadline: Deadline) -> GtfsImportResult:
    """
    Run one GTFS step under the exclusion of the importer.

    The step takes the same exclusion as python -m worker.osm_import, because only that exclusion admits a workspace and
    so that the step never overlaps an import that moves the pointer of the OpenStreetMap copy. Another run holding it
    gives skipped.
    """
    engine = build_import_engine(GTFS_IMPORT_GUARD_STATEMENT_TIMEOUT_MS)
    try:
        with ExitStack() as stack:
            try:
                lease = stack.enter_context(apply_import_exclusion(engine, settings.workspace_root))
            except ImportAlreadyRunning:
                return GtfsImportResult("skipped", "not_run", None)
            return apply_gtfs_import_run(settings, client, lease.workspace_lease, deadline)
    finally:
        engine.dispose()


def apply_gtfs_import_run(settings: GtfsImportSettings, client: httpx.Client, lease: WorkspaceLease, deadline: Deadline) -> GtfsImportResult:
    """
    Carry out an admitted run: remove leftover preparations, fetch a fresh GTFS copy, then build or reuse the routing data with public transport and point at it.

    A failed fetch keeps the earlier GTFS copy and the build still runs from it. Without a complete GTFS copy or an
    OpenStreetMap copy in use nothing is built. Data of the same OpenStreetMap copy and GTFS copy is never built twice,
    because a placed directory is complete and never changes.
    """
    root = settings.routing_root
    for preparation in (*fetch_gtfs_preparations(root), *fetch_transit_preparations(root)):
        apply_routing_directory_removal(preparation)
    fetch: GtfsFetchOutcome = "fetched" if apply_gtfs_fetch(root, client, lease.workspace, deadline) else "failed"
    gtfs = fetch_gtfs_copy(root)
    if gtfs is None:
        return GtfsImportResult("no_gtfs_copy", fetch, None)
    copy_name = fetch_routing_pointer(root)
    if copy_name is None:
        return GtfsImportResult("no_osm_copy", fetch, None)
    name = build_transit_name(copy_name, gtfs.name)
    directory = build_transit_directory(root, name)
    is_reused = directory.is_dir() and not directory.is_symlink()
    if not is_reused:
        apply_transit_data(settings, lease, gtfs, copy_name, name, deadline)
    apply_transit_pointer(root, name)
    return GtfsImportResult("reused" if is_reused else "built", fetch, name)


def apply_gtfs_fetch(root: Path, client: httpx.Client, workspace: Path, deadline: Deadline) -> bool:
    """
    Fetch the three feeds into a preparation and make them the GTFS copy in use.

    Return False and keep the earlier copy when a feed fails, is incomplete or cannot be prepared for the ingest, so a
    feed the rules of gtfs_feeds.py refuse never becomes the copy in use. A copy that cannot be stored, a directory or a
    pointer that cannot be written, is not a failed fetch and ends the run.
    """
    preparation = apply_gtfs_preparation(root)
    try:
        days = {feed: fetch_gtfs_feed(client, feed, build_gtfs_feed_path(preparation, feed), deadline) for feed in GTFS_FEEDS}
        apply_gtfs_feed_check(preparation, workspace / GTFS_CHECK_NAME)
        apply_gtfs_copy(root, days, preparation)
    except (GtfsSourceError, GtfsCopyError, GtfsFeedError) as failure:
        fetch_logger(__name__).warning("GTFS fetch failed, the earlier copy stays in use cause=%s: %s", type(failure).__name__, failure)
        apply_preparation_cleanup(preparation)
        return False
    except BaseException:
        apply_preparation_cleanup(preparation)
        raise
    return True


def apply_gtfs_feed_check(preparation: Path, check_directory: Path) -> None:
    """Prepare every fetched feed into a throwaway directory of the run workspace and remove it, refusing the fetch with GtfsFeedError when a feed cannot be prepared."""
    try:
        for feed in GTFS_FEEDS:
            apply_gtfs_feed_preparation(build_gtfs_feed_path(preparation, feed), check_directory / feed)
    finally:
        apply_preparation_cleanup(check_directory)


def apply_preparation_cleanup(preparation: Path) -> None:
    """Remove a directory that was not placed, leaving it for a later cleanup - the next run or the end of the workspace - when it cannot be removed now."""
    if not preparation.exists():
        return
    try:
        apply_routing_directory_removal(preparation)
    except RoutingDataError:
        fetch_logger(__name__).warning("Directory was left for a later cleanup")


def build_transit_valhalla_config(template: dict[str, Any], workspace: Path, archive_path: Path) -> dict[str, Any]:
    """Specialize the configuration of the walking build for a build with public transport: the GTFS input, the ingest output and the timezone database in the run workspace."""
    config = build_osm_valhalla_config(template, workspace / "tiles", archive_path)
    config["mjolnir"].update(transit_dir=str(workspace / TRANSIT_TILES_NAME), transit_feeds_dir=str(workspace / TRANSIT_FEEDS_NAME), timezone=str(workspace / TRANSIT_TIMEZONE_NAME))
    return config


def apply_transit_data(settings: GtfsImportSettings, lease: WorkspaceLease, gtfs: GtfsCopy, copy_name: str, name: str, deadline: Deadline) -> Path:
    """
    Build the routing data with public transport of one OpenStreetMap copy and one GTFS copy and place it under its name.

    The network file comes from the verified copy directory of the OpenStreetMap copy in use, each feed is prepared into
    its own directory of the ingest input, and the archive is built into a preparation that is removed when the build
    fails.
    """
    copy_directory = settings.routing_root / ROUTING_COPIES_NAME / copy_name
    manifest = fetch_osm_routing_manifest(copy_directory)
    if build_routing_copy_name(manifest.state_at) != copy_name:
        raise RoutingDataError("Routing manifest belongs to another copy")
    template = fetch_osm_valhalla_template(settings.config_template)
    workspace = lease.workspace
    try:
        (workspace / TRANSIT_TILES_NAME).mkdir()
    except OSError as error:
        raise TransitBuildError("Cannot prepare the public transport workspace") from error
    for feed in GTFS_FEEDS:
        apply_gtfs_feed_preparation(build_gtfs_feed_path(gtfs.directory, feed), workspace / TRANSIT_FEEDS_NAME / feed)
    preparation = apply_transit_preparation(settings.routing_root)
    try:
        config_path = workspace / TRANSIT_CONFIG_NAME
        apply_osm_valhalla_config(config_path, build_transit_valhalla_config(template, workspace, preparation / TRANSIT_ARCHIVE_NAME))
        network_path = copy_directory / "network.osm.pbf"
        return apply_transit_build(lease, config_path, settings.tool_directory, network_path, workspace / TRANSIT_TIMEZONE_NAME, preparation, settings.routing_root, name, manifest.state_at, deadline)
    except BaseException:
        apply_preparation_cleanup(preparation)
        raise


def fetch_transit_serves_copy_in_use(root: Path) -> bool:
    """Say whether the routing data with public transport in use was built from the OpenStreetMap copy the pointer current names."""
    copy_name = fetch_routing_pointer(root)
    transit_name = fetch_transit_pointer(root)
    return copy_name is not None and transit_name is not None and resolve_transit_copy_name(transit_name) == copy_name
