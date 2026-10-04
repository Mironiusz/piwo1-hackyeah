"""Decide and carry out the recovery of the routing pointer before a new import starts."""

from datetime import datetime
from pathlib import Path
from typing import Literal

from config.logging import fetch_logger
from data.routing_data import ROUTING_COPIES_NAME, RoutingDataError, apply_routing_pointer, build_routing_copy_name, fetch_osm_routing_manifest, fetch_routing_pointer

type OsmRoutingRecovery = Literal["none", "publish", "integrity_failure"]


class OsmRoutingIntegrityError(ValueError):
    """Stop a run whose committed copy has routing files that cannot be verified or whose pointer is inconsistent."""


def resolve_osm_routing_recovery(committed_name: str | None, pointer_name: str | None) -> OsmRoutingRecovery:
    """
    Compare the pointer with the latest committed copy.

    Without a committed copy there is nothing to recover. A pointer naming that copy needs nothing; a missing pointer
    or one naming an older copy is republished after its files are verified; a pointer naming a newer copy than the
    database holds is inconsistent and stops the run.
    """
    if committed_name is None or pointer_name == committed_name:
        return "none"
    if pointer_name is None or int(pointer_name) < int(committed_name):
        return "publish"
    return "integrity_failure"


def apply_osm_routing_recovery(routing_root: Path, committed_state_at: datetime | None) -> None:
    """
    Republish the pointer of the latest committed copy when the decision requires it, after verifying its manifest.

    Missing or incomplete files, a manifest of another source instant and an inconsistent pointer stop the run with
    the pointer and the database unchanged; nothing is downloaded or rebuilt here.
    """
    committed_name = None if committed_state_at is None else build_routing_copy_name(committed_state_at)
    decision = resolve_osm_routing_recovery(committed_name, fetch_routing_pointer(routing_root))
    if decision == "integrity_failure":
        raise OsmRoutingIntegrityError("Routing pointer names a copy newer than the database")
    if decision == "none" or committed_name is None:
        return
    try:
        manifest = fetch_osm_routing_manifest(routing_root / ROUTING_COPIES_NAME / committed_name)
    except RoutingDataError as error:
        raise OsmRoutingIntegrityError("Committed routing copy has missing or incomplete files") from error
    if manifest.state_at != committed_state_at:
        raise OsmRoutingIntegrityError("Committed routing copy belongs to another source instant")
    apply_routing_pointer(routing_root, committed_name)
    fetch_logger(__name__).info("Routing pointer recovered copy=%s", committed_name)
