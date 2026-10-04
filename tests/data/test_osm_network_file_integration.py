"""Verify network PBF normalization on invented snapshots with real pyosmium."""

import tempfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import osmium
import pytest

from data.osm_network_file import OsmNetworkFileError, apply_osm_network_pbf
from data.osm_reader import OsmElementSnapshot
from service.osm_routing_tags import build_osm_routing_node_tags, build_osm_routing_way_tags


@pytest.mark.integration
def test_prepared_pbf_keeps_node_identities_order_and_source_state():
    state_at = datetime(2026, 10, 3, tzinfo=UTC)
    raw_tags = {"highway": "steps", "access": "private", "foot": "yes", "foot:conditional": "no", "sac_scale": "hiking", "smoothness": "impassable", "area": "yes", "conveying": "forward"}
    nodes = tuple(
        OsmElementSnapshot("node", node_id, state_at, build_osm_routing_node_tags({"barrier": "gate", "access": "no", "name": "Invented"}), coordinates=((lon, 50.05),))
        for node_id, lon in ((1, 19.95), (2, 19.96))
    )
    way = OsmElementSnapshot("way", 10, state_at, build_osm_routing_way_tags(raw_tags), node_ids=(1, 2, 1))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "network.osm.pbf"
        apply_osm_network_pbf(path, nodes, (way,), state_at)
        copied = []
        with osmium.io.Reader(str(path)) as reader:
            assert reader.header().get("osmosis_replication_timestamp") == "2026-10-03T00:00:00Z"
        for item in osmium.FileProcessor(path):
            copied.append((item.id, dict(item.tags), tuple(node.ref for node in item.nodes) if isinstance(item, osmium.osm.Way) else ()))
    assert copied == [(1, {"name": "Invented"}, ()), (2, {"name": "Invented"}, ()), (10, {"highway": "steps", "foot": "yes", "conveying": "forward"}, (1, 2, 1))]
    assert raw_tags["access"] == "private"


@pytest.mark.integration
def test_missing_references_fail_without_overwriting_existing_files():
    state_at = datetime(2026, 10, 3, tzinfo=UTC)
    way = OsmElementSnapshot("way", 10, state_at, {"highway": "path", "foot": "yes"}, node_ids=(1, 2))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "network.osm.pbf"
        with pytest.raises(OsmNetworkFileError):
            apply_osm_network_pbf(path, (), (way,), state_at)
        assert not path.exists()
        path.write_bytes(b"existing network")
        contents = path.read_bytes()
        with pytest.raises(OsmNetworkFileError):
            apply_osm_network_pbf(path, (), (replace(way, node_ids=(1,)),), state_at)
        assert path.read_bytes() == contents
