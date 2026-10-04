"""Read a validated source into a prepared copy and place the matching walking-routing data."""

import copy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from shapely import MultiPolygon, Polygon, to_wkb

from common_time import Deadline
from config.logging import fetch_logger
from data.import_workspace import WorkspaceLease
from data.osm_copy import OsmPresentFact
from data.osm_network_file import apply_osm_network_pbf
from data.osm_reader import OsmInvalidAreaTally, fetch_osm_elements
from data.osm_valhalla import OsmTileBuildError, apply_osm_valhalla_config, apply_osm_valhalla_tiles
from data.routing_data import (
    ROUTING_COPIES_NAME,
    RoutingDataError,
    apply_osm_boundary_file,
    apply_osm_routing_manifest,
    apply_routing_copy_placement,
    apply_routing_directory_removal,
    apply_routing_preparation_directory,
    build_routing_copy_name,
    fetch_osm_routing_manifest,
)
from service.osm_facts import build_osm_fact_data
from service.osm_preparation import OsmPreparedNetwork, build_osm_boundary, build_osm_network, build_osm_routing_network
from service.osm_routing_recovery import OsmRoutingIntegrityError


@dataclass(frozen=True)
class OsmPreparedCopy:
    """Keep the original network, the motor-traffic node membership, the present facts, the boundary of Kraków and the count of skipped invalid areas of one source."""

    network: OsmPreparedNetwork
    motor_traffic_node_ids: frozenset[int]
    facts: tuple[OsmPresentFact, ...]
    boundary: Polygon | MultiPolygon
    invalid_area_count: int


def fetch_osm_prepared_copy(source_path: Path, deadline: Deadline, zone: ZoneInfo) -> OsmPreparedCopy:
    """
    Read the complete source in three passes - the Kraków boundary, the pedestrian network and the facts of the copy.

    Every pass skips the same invalid areas of the source, so the count of the first pass is the count of the copy. A
    skipped area is treated as a missing one: a skipped boundary of Kraków fails the boundary pass, a skipped area
    relation of the copy whose tags make an amenity present fails the fact pass, and a closed way of the copy whose
    area was skipped keeps its amenity at half its length.
    """
    invalid_areas = OsmInvalidAreaTally()
    boundary = build_osm_boundary(fetch_osm_elements(source_path, deadline, invalid_areas))
    network = build_osm_network(fetch_osm_elements(source_path, deadline), boundary)
    fact_data = build_osm_fact_data(fetch_osm_elements(source_path, deadline), boundary, network, zone)
    return OsmPreparedCopy(network, fact_data.motor_traffic_node_ids, fact_data.facts, boundary, invalid_areas.count)


def build_osm_valhalla_config(template: dict[str, Any], tile_directory: Path, archive_path: Path) -> dict[str, Any]:
    """Specialize a supplied Valhalla configuration for one walking-data build without public transport inputs."""
    config = copy.deepcopy(template)
    mjolnir = config.get("mjolnir")
    if not isinstance(mjolnir, dict):
        raise OsmTileBuildError("Valhalla configuration requires mjolnir settings")
    mjolnir.update(tile_dir=str(tile_directory), tile_extract=str(archive_path), include_platforms=True, keep_osm_node_ids=True, keep_all_osm_node_ids=True)
    mjolnir.pop("transit_dir", None)
    mjolnir.pop("transit_feeds_dir", None)
    return config


def apply_osm_routing_preparation(
    lease: WorkspaceLease,
    routing_root: Path,
    network: OsmPreparedNetwork,
    boundary: Polygon | MultiPolygon,
    state_at: datetime,
    committed_names: frozenset[str],
    template: dict[str, Any],
    tool_directory: Path,
    deadline: Deadline,
) -> Path:
    """
    Return the verified copy directory of this source instant, preparing it when it is missing or incomplete.

    A complete directory whose manifest names this instant is reused. An incomplete directory of an instant never
    committed is replaced only after its replacement has been built and verified; one of a committed copy is preserved
    and stops the run. The boundary of Kraków is written as WKB in longitude and latitude next to the network and the
    tiles before the manifest, so the manifest guards it too. Tiles and the build configuration stay in the run
    workspace, and nothing in a placed copy is overwritten.
    """
    name = build_routing_copy_name(state_at)
    target = routing_root / ROUTING_COPIES_NAME / name
    is_incomplete = False
    if target.exists() or target.is_symlink():
        try:
            if fetch_osm_routing_manifest(target).state_at == state_at:
                return target
        except RoutingDataError:
            fetch_logger(__name__).info("Routing copy directory is incomplete copy=%s", name)
        if name in committed_names:
            raise OsmRoutingIntegrityError("Committed routing copy has incomplete files")
        is_incomplete = True
    preparation = apply_routing_preparation_directory(routing_root)
    try:
        network_path = preparation / "network.osm.pbf"
        archive_path = preparation / "valhalla_tiles.tar"
        config_path = lease.workspace / "valhalla.json"
        routing = build_osm_routing_network(network)
        apply_osm_network_pbf(network_path, routing.nodes, routing.ways, state_at)
        apply_osm_valhalla_config(config_path, build_osm_valhalla_config(template, lease.workspace / "tiles", archive_path))
        apply_osm_valhalla_tiles(lease, config_path, tool_directory, network_path, archive_path, state_at, deadline)
        apply_osm_boundary_file(preparation, to_wkb(boundary))
        apply_osm_routing_manifest(preparation, state_at)
        fetch_osm_routing_manifest(preparation)
        if is_incomplete:
            apply_routing_directory_removal(target)
        return apply_routing_copy_placement(preparation, routing_root, name)
    except BaseException:
        try:
            apply_routing_directory_removal(preparation)
        except RoutingDataError:
            fetch_logger(__name__).warning("Routing preparation was left for removal by the next run")
        raise
