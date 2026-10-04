"""Connect local source reading, network selection and walking-file preparation."""

import asyncio
import copy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from data.osm_network_file import apply_osm_network_pbf
from data.osm_reader import fetch_osm_elements, fetch_osm_header_timestamp
from data.osm_valhalla import OsmTileBuildError, apply_osm_valhalla_config, apply_osm_valhalla_tiles
from data.routing_data import RoutingManifest, apply_osm_routing_manifest
from service.osm_preparation import OsmPreparedNetwork, build_osm_boundary, build_osm_network, build_osm_routing_network
from service.osm_source_validation import resolve_osm_source_state


@dataclass(frozen=True)
class OsmNetworkData:
    """Keep source state and original selected values alongside a written routing PBF."""

    state_at: datetime
    network: OsmPreparedNetwork


def prepare_osm_network_data(source_path: Path, network_path: Path) -> OsmNetworkData:
    """Read the full source twice and write exactly the selected normalized network."""
    state_at = resolve_osm_source_state(fetch_osm_header_timestamp(source_path))
    boundary = build_osm_boundary(fetch_osm_elements(source_path))
    network = build_osm_network(fetch_osm_elements(source_path), boundary)
    routing = build_osm_routing_network(network)
    apply_osm_network_pbf(network_path, routing.nodes, routing.ways, state_at)
    return OsmNetworkData(state_at, network)


def build_osm_valhalla_config(template: dict[str, Any], directory: Path) -> dict[str, Any]:
    """Specialize a supplied Valhalla configuration for one walking-data build."""
    config = copy.deepcopy(template)
    mjolnir = config.get("mjolnir")
    if not isinstance(mjolnir, dict):
        raise OsmTileBuildError("Valhalla configuration requires mjolnir settings")
    mjolnir.update(
        tile_dir=str(directory.resolve() / "tiles"), tile_extract=str(directory.resolve() / "valhalla_tiles.tar"), include_platforms=True, keep_osm_node_ids=True, keep_all_osm_node_ids=True
    )
    mjolnir.pop("transit_dir", None)
    mjolnir.pop("transit_feeds_dir", None)
    return config


async def prepare_osm_routing_data(source_path: Path, directory: Path, template: dict[str, Any], tool_directory: Path, deadline: float) -> RoutingManifest:
    """Prepare a new directory and manifest without connecting to a database or activating it."""
    if asyncio.get_running_loop().time() >= deadline:
        raise OsmTileBuildError("Routing preparation deadline expired")
    config = build_osm_valhalla_config(template, directory)
    config_path = apply_osm_valhalla_config(directory, config)
    prepared = prepare_osm_network_data(source_path, directory / "network.osm.pbf")
    await apply_osm_valhalla_tiles(directory, config_path, tool_directory, prepared.state_at, deadline)
    return apply_osm_routing_manifest(directory, prepared.state_at)
