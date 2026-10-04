"""Check source semantics at the real database model boundary."""

from datetime import UTC, datetime

from accessibility_db.closed_lists import WayBarrierState

from data.osm_reader import OsmElementSnapshot
from service.osm_database_rows import build_osm_database_network
from service.osm_preparation import OsmPreparedNetwork


def test_original_tags_and_external_motor_membership_are_preserved():
    """Repeated references survive and source-wide motor membership is not inferred from selected ways."""
    now = datetime(2026, 10, 4, tzinfo=UTC)
    first = OsmElementSnapshot("node", 1, now, {}, coordinates=((19.0, 50.0),))
    second = OsmElementSnapshot("node", 2, now, {}, coordinates=((19.1, 50.1),))
    way = OsmElementSnapshot("way", 10, now, {"highway": "steps", "wheelchair": "no"}, node_ids=(1, 2, 1), coordinates=((19.0, 50.0), (19.1, 50.1), (19.0, 50.0)))
    nodes, ways, memberships = build_osm_database_network(OsmPreparedNetwork((first, second), (way,)), frozenset({1}))
    assert nodes[0].is_on_motor_traffic_way
    assert not nodes[1].is_on_motor_traffic_way
    assert ways[0].stairs_state == WayBarrierState.PRESENT
    assert ways[0].is_marked_wheelchair_no
    assert [(row.sequence_index, row.node_id) for row in memberships] == [(0, 1), (1, 2), (2, 1)]
    assert nodes[0].geog == "SRID=4326;POINT (19 50)"
