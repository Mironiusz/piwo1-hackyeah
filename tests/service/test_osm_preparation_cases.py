"""Verify complete-boundary selection and original-versus-routing snapshots."""

from dataclasses import replace
from datetime import UTC, datetime

import pytest
from shapely.geometry import MultiPolygon, Polygon

from data.osm_reader import OsmElementSnapshot
from service.osm_geometry import OsmGeometryError
from service.osm_preparation import build_osm_boundary, build_osm_network, build_osm_routing_network

STATE_AT = datetime(2026, 10, 3, tzinfo=UTC)


def build_invented_boundary():
    """Return a small boundary with a hole and independently identified ring ways."""
    outer = ((19.9, 50), (20, 50), (20, 50.1), (19.9, 50.1), (19.9, 50))
    inner = ((19.94, 50.04), (19.96, 50.04), (19.96, 50.06), (19.94, 50.06), (19.94, 50.04))
    boundary = Polygon(outer, [inner])
    relation = OsmElementSnapshot("relation", 449696, STATE_AT, {"type": "boundary"}, members=(("w", 1, "outer"), ("w", 2, "inner")))
    area = replace(relation, area_wkb=boundary.wkb)
    ways = (OsmElementSnapshot("way", 1, STATE_AT, {}, node_ids=(1, 2, 3, 4, 1), coordinates=outer), OsmElementSnapshot("way", 2, STATE_AT, {}, node_ids=(5, 6, 7, 8, 5), coordinates=inner))
    return boundary, (relation, area, *ways)


def test_boundary_preserves_holes():
    boundary, elements = build_invented_boundary()
    assert build_osm_boundary(iter(elements)).equals(boundary)


@pytest.mark.parametrize("omitted", [0, 1, 2, 3])
def test_missing_relation_area_or_ring_fails(omitted):
    _, elements = build_invented_boundary()
    with pytest.raises(OsmGeometryError):
        build_osm_boundary(element for index, element in enumerate(elements) if index != omitted)


def test_native_area_cannot_silently_drop_a_hole():
    boundary, elements = build_invented_boundary()
    area = replace(elements[1], area_wkb=Polygon(boundary.exterior).wkb)
    with pytest.raises(OsmGeometryError, match="omits"):
        build_osm_boundary((elements[0], area, *elements[2:]))


def test_network_retains_whole_crossing_ways_and_source_tags():
    boundary, _ = build_invented_boundary()
    coordinates = ((19.92, 50.02), (20.1, 50.02), (19.95, 50.05), (19.951, 50.051))
    nodes = tuple(OsmElementSnapshot("node", index, STATE_AT, {"barrier": "gate"}, coordinates=(coordinate,)) for index, coordinate in enumerate(coordinates, 1))
    crossing = OsmElementSnapshot("way", 10, STATE_AT, {"highway": "path", "foot": "yes", "access": "private"}, node_ids=(1, 2, 1), coordinates=(coordinates[0], coordinates[1], coordinates[0]))
    hole_way = OsmElementSnapshot("way", 11, STATE_AT, {"highway": "path"}, node_ids=(3, 4), coordinates=(coordinates[2], coordinates[3]))
    original = build_osm_network((*nodes, crossing, hole_way), boundary)
    assert original.ways == (crossing,)
    assert [node.element_id for node in original.nodes] == [1, 2]
    routing = build_osm_routing_network(original)
    assert "access" not in routing.ways[0].tags
    assert original.ways[0].tags["access"] == "private"
    assert routing.ways[0].node_ids == (1, 2, 1)


def test_selected_missing_node_fails():
    boundary, _ = build_invented_boundary()
    way = OsmElementSnapshot("way", 10, STATE_AT, {"highway": "path"}, node_ids=(1, 2), coordinates=((19.91, 50.01), (19.92, 50.02)))
    with pytest.raises(OsmGeometryError, match="Missing selected"):
        build_osm_network((way,), boundary)


def test_complete_outer_rings_can_touch_at_one_shared_node():
    boundary, elements = build_invented_boundary()
    outer = ((19.9, 50), (19.8, 50), (19.8, 49.9), (19.9, 49.9), (19.9, 50))
    second = OsmElementSnapshot("way", 3, STATE_AT, {}, node_ids=(1, 9, 10, 11, 1), coordinates=outer)
    combined = MultiPolygon((boundary, Polygon(outer)))
    relation = replace(elements[0], members=(*elements[0].members, ("w", 3, "outer")))
    area = replace(elements[1], area_wkb=combined.wkb)
    assert combined.is_valid
    assert build_osm_boundary((relation, area, *elements[2:], second)).equals(combined)
