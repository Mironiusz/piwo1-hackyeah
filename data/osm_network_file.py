"""Write prepared network snapshots to a PBF without applying product selection rules."""

import os
import tempfile
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import osmium

from data.osm_reader import OsmElementSnapshot


class OsmNetworkFileError(ValueError):
    """Describe a network file that cannot be prepared for tile construction."""


def apply_osm_network_pbf(path: Path, nodes: Iterable[OsmElementSnapshot], ways: Iterable[OsmElementSnapshot], state_at: datetime) -> None:
    """Write already selected and normalized nodes and ways with their original identities."""
    if state_at.utcoffset() is None:
        raise OsmNetworkFileError("Network source instant must be aware")
    prepared_nodes = tuple(nodes)
    prepared_ways = tuple(ways)
    node_ids = {node.element_id for node in prepared_nodes}
    if len(node_ids) != len(prepared_nodes) or any(node.element_type != "node" or len(node.coordinates) != 1 for node in prepared_nodes):
        raise OsmNetworkFileError("Invalid prepared network node")
    if len({way.element_id for way in prepared_ways}) != len(prepared_ways) or any(
        way.element_type != "way" or way.area_wkb is not None or len(way.node_ids) < 2 or any(ref not in node_ids for ref in way.node_ids) for way in prepared_ways
    ):
        raise OsmNetworkFileError("Invalid prepared network way")
    header = osmium.io.Header()
    header.set("osmosis_replication_timestamp", state_at.astimezone(UTC).isoformat().replace("+00:00", "Z"))
    try:
        with tempfile.TemporaryDirectory(dir=path.parent) as directory:
            temporary_path = Path(directory) / "network.osm.pbf"
            with osmium.SimpleWriter(str(temporary_path), header=header) as writer:
                for node in prepared_nodes:
                    writer.add_node(osmium.osm.mutable.Node(id=node.element_id, timestamp=node.edited_at, location=node.coordinates[0], tags=dict(node.tags)))
                for way in prepared_ways:
                    writer.add_way(osmium.osm.mutable.Way(id=way.element_id, timestamp=way.edited_at, nodes=way.node_ids, tags=dict(way.tags)))
            os.link(temporary_path, path)
    except (RuntimeError, OSError) as error:
        raise OsmNetworkFileError("Cannot write prepared network file") from error
