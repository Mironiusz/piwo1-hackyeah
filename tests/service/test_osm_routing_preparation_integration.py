"""Read an invented source into a prepared copy and place its routing data with controlled tile tools."""

import json
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactType, OsmElementType

from common_time import build_deadline, fetch_monotonic_seconds
from data.import_workspace import apply_workspace_exclusion, apply_workspace_recovery
from data.osm_reader import fetch_osm_elements
from data.osm_valhalla import OsmTileBuildError
from data.routing_data import ROUTING_COPIES_NAME, apply_osm_routing_manifest, fetch_osm_routing_manifest, fetch_routing_preparations
from service.osm_routing_preparation import apply_osm_routing_preparation, build_osm_valhalla_config, fetch_osm_prepared_copy
from service.osm_routing_recovery import OsmRoutingIntegrityError
from tests.common_osm_source import apply_invented_osm_source

STATE_AT = datetime(2026, 10, 3, tzinfo=UTC)
ZONE = ZoneInfo("Europe/Warsaw")
NAME = "1790985600"

pytestmark = pytest.mark.integration


def build_test_deadline():
    """Give reading and building a budget no invented source can exhaust."""
    return build_deadline(60, fetch_monotonic_seconds())


def apply_invented_tiles(monkeypatch, calls: list[Path]) -> None:
    """Replace the tile tools with a step that writes the archive named in the build configuration."""

    def apply_tiles(lease, config_path, tool_directory, network_path, archive_path, state_at, deadline):
        config = json.loads(config_path.read_text())
        assert config["mjolnir"]["tile_extract"] == str(archive_path)
        assert config["mjolnir"]["keep_all_osm_node_ids"] is True
        assert Path(config["mjolnir"]["tile_dir"]).parent == lease.workspace
        calls.append(network_path)
        archive_path.write_bytes(b"invented tile archive")

    monkeypatch.setattr("service.osm_routing_preparation.apply_osm_valhalla_tiles", apply_tiles)


def test_source_gives_network_facts_and_motor_membership(tmp_path):
    prepared = fetch_osm_prepared_copy(apply_invented_osm_source(tmp_path), build_test_deadline(), ZONE)
    assert [way.element_id for way in prepared.network.ways] == [10, 11]
    assert [node.element_id for node in prepared.network.nodes] == [5, 6, 7]
    assert prepared.motor_traffic_node_ids == frozenset({6, 7})
    keys = {(fact.identity.element_type, fact.identity.element_id, fact.identity.fact_type) for fact in prepared.facts}
    assert keys == {
        (OsmElementType.WAY, 10, FactType.STAIRS),
        (OsmElementType.WAY, 11, FactType.POOR_SURFACE),
        (OsmElementType.NODE, 7, FactType.LOWERED_KERB),
        (OsmElementType.NODE, 8, FactType.REST_PLACE),
    }
    assert next(fact for fact in prepared.facts if fact.identity.fact_type == FactType.STAIRS).step_count == 4


def test_configuration_copy_has_no_transit_inputs(tmp_path):
    template = {"mjolnir": {"transit_dir": "invented", "transit_feeds_dir": "invented"}, "loki": {"use_connectivity": True}}
    result = build_osm_valhalla_config(template, tmp_path / "tiles", tmp_path / "valhalla_tiles.tar")
    assert "transit_dir" not in result["mjolnir"] and "transit_feeds_dir" not in result["mjolnir"]
    assert result["mjolnir"]["tile_dir"] == str(tmp_path / "tiles")
    assert template["mjolnir"]["transit_dir"] == "invented"
    assert result["loki"] == template["loki"]


def test_configuration_without_mjolnir_is_refused(tmp_path):
    with pytest.raises(OsmTileBuildError):
        build_osm_valhalla_config({}, tmp_path / "tiles", tmp_path / "valhalla_tiles.tar")


def test_new_copy_is_built_verified_and_placed_without_a_pointer(tmp_path, monkeypatch):
    calls: list[Path] = []
    apply_invented_tiles(monkeypatch, calls)
    prepared = fetch_osm_prepared_copy(apply_invented_osm_source(tmp_path), build_test_deadline(), ZONE)
    routing_root = tmp_path / "routing"
    routing_root.mkdir()
    with apply_workspace_exclusion(tmp_path / "workspace") as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        target = apply_osm_routing_preparation(lease, routing_root, prepared.network, STATE_AT, frozenset(), {"mjolnir": {}}, tmp_path / "tools", build_test_deadline())
    assert target == routing_root / ROUTING_COPIES_NAME / NAME
    assert fetch_osm_routing_manifest(target).state_at == STATE_AT
    elements = tuple(fetch_osm_elements(target / "network.osm.pbf", build_test_deadline()))
    assert [(element.element_type, element.element_id) for element in elements] == [("node", 5), ("node", 6), ("node", 7), ("way", 10), ("way", 11)]
    assert "access" not in elements[3].tags and elements[3].tags["foot"] == "yes"
    assert sorted(entry.name for entry in target.iterdir()) == ["manifest.json", "network.osm.pbf", "valhalla_tiles.tar"]
    assert not (routing_root / "current").exists()
    assert fetch_routing_preparations(routing_root) == ()
    assert len(calls) == 1


def test_complete_copy_of_the_same_instant_is_reused_without_building(tmp_path, monkeypatch):
    calls: list[Path] = []
    apply_invented_tiles(monkeypatch, calls)
    target = tmp_path / "routing" / ROUTING_COPIES_NAME / NAME
    target.mkdir(parents=True)
    (target / "network.osm.pbf").write_bytes(b"network")
    (target / "valhalla_tiles.tar").write_bytes(b"tiles")
    apply_osm_routing_manifest(target, STATE_AT)
    prepared = fetch_osm_prepared_copy(apply_invented_osm_source(tmp_path), build_test_deadline(), ZONE)
    with apply_workspace_exclusion(tmp_path / "workspace") as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        result = apply_osm_routing_preparation(lease, tmp_path / "routing", prepared.network, STATE_AT, frozenset(), {"mjolnir": {}}, tmp_path / "tools", build_test_deadline())
    assert result == target and calls == []
    assert (target / "network.osm.pbf").read_bytes() == b"network"


def test_incomplete_uncommitted_copy_is_replaced_and_a_committed_one_is_preserved(tmp_path, monkeypatch):
    calls: list[Path] = []
    apply_invented_tiles(monkeypatch, calls)
    target = tmp_path / "routing" / ROUTING_COPIES_NAME / NAME
    target.mkdir(parents=True)
    (target / "network.osm.pbf").write_bytes(b"truncated")
    prepared = fetch_osm_prepared_copy(apply_invented_osm_source(tmp_path), build_test_deadline(), ZONE)
    with apply_workspace_exclusion(tmp_path / "workspace") as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        with pytest.raises(OsmRoutingIntegrityError):
            apply_osm_routing_preparation(lease, tmp_path / "routing", prepared.network, STATE_AT, frozenset({NAME}), {"mjolnir": {}}, tmp_path / "tools", build_test_deadline())
        assert (target / "network.osm.pbf").read_bytes() == b"truncated" and calls == []
        result = apply_osm_routing_preparation(lease, tmp_path / "routing", prepared.network, STATE_AT, frozenset(), {"mjolnir": {}}, tmp_path / "tools", build_test_deadline())
    assert result == target
    assert fetch_osm_routing_manifest(target).state_at == STATE_AT


def test_failed_tiles_leave_no_copy_and_no_preparation(tmp_path, monkeypatch):
    def apply_failed_tiles(lease, config_path, tool_directory, network_path, archive_path, state_at, deadline):
        raise OsmTileBuildError("Invented build failure")

    monkeypatch.setattr("service.osm_routing_preparation.apply_osm_valhalla_tiles", apply_failed_tiles)
    prepared = fetch_osm_prepared_copy(apply_invented_osm_source(tmp_path), build_test_deadline(), ZONE)
    routing_root = tmp_path / "routing"
    routing_root.mkdir()
    with apply_workspace_exclusion(tmp_path / "workspace") as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        with pytest.raises(OsmTileBuildError, match="Invented build failure"):
            apply_osm_routing_preparation(lease, routing_root, prepared.network, STATE_AT, frozenset(), {"mjolnir": {}}, tmp_path / "tools", build_test_deadline())
    assert not (routing_root / ROUTING_COPIES_NAME / NAME).exists()
    assert fetch_routing_preparations(routing_root) == ()
