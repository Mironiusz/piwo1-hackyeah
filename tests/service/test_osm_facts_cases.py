"""Check which elements of a copy give present facts, where those facts are located and which day they carry."""

from datetime import UTC, date, datetime
from types import MappingProxyType
from typing import Literal
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactType, OsmElementType
from shapely import from_wkt, to_wkb
from shapely.geometry import MultiPolygon, Point, Polygon

from data.osm_reader import OsmElementSnapshot
from service.osm_facts import build_osm_fact_data
from service.osm_geometry import OsmGeometryError
from service.osm_preparation import OsmPreparedNetwork

BOUNDARY = Polygon(((19.9, 50.0), (20.0, 50.0), (20.0, 50.1), (19.9, 50.1)))
ZONE = ZoneInfo("Europe/Warsaw")
EDITED_AT = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)


def build_node(element_id: int, lon: float, lat: float, tags: dict[str, str] | None = None, edited_at: datetime = EDITED_AT) -> OsmElementSnapshot:
    """Build an invented node snapshot."""
    return OsmElementSnapshot("node", element_id, edited_at, MappingProxyType(tags or {}), coordinates=((lon, lat),))


def build_way(element_id: int, nodes: tuple[OsmElementSnapshot, ...], tags: dict[str, str]) -> OsmElementSnapshot:
    """Build an invented way snapshot over the given nodes."""
    return OsmElementSnapshot("way", element_id, EDITED_AT, MappingProxyType(tags), tuple(node.element_id for node in nodes), tuple(node.coordinates[0] for node in nodes))


def build_area(element_type: Literal["way", "relation"], element_id: int, polygon: Polygon, tags: dict[str, str]) -> OsmElementSnapshot:
    """Build an invented assembled area snapshot of a way or a relation."""
    return OsmElementSnapshot(element_type, element_id, EDITED_AT, MappingProxyType(tags), area_wkb=to_wkb(MultiPolygon([polygon])))


def build_relation(element_id: int, way_ids: tuple[int, ...], tags: dict[str, str]) -> OsmElementSnapshot:
    """Build an invented relation snapshot with way members."""
    return OsmElementSnapshot("relation", element_id, EDITED_AT, MappingProxyType(tags), members=tuple(("w", way_id, "outer") for way_id in way_ids))


def build_fact_keys(facts) -> set[tuple[OsmElementType, int, FactType]]:
    """Reduce facts to their identities."""
    return {(fact.identity.element_type, fact.identity.element_id, fact.identity.fact_type) for fact in facts}


def test_network_way_gives_barriers_and_steps_amenities_at_half_its_length():
    start = build_node(1, 19.91, 50.05)
    end = build_node(2, 19.93, 50.05)
    steps = build_way(10, (start, end), {"highway": "steps", "step_count": "5", "handrail": "yes", "ramp": "yes"})
    data = build_osm_fact_data((start, end, steps), BOUNDARY, OsmPreparedNetwork((start, end), (steps,)), ZONE)
    assert build_fact_keys(data.facts) == {
        (OsmElementType.WAY, 10, FactType.STAIRS),
        (OsmElementType.WAY, 10, FactType.HANDRAIL_AT_STAIRS),
        (OsmElementType.WAY, 10, FactType.RAMP),
    }
    stairs = next(fact for fact in data.facts if fact.identity.fact_type == FactType.STAIRS)
    assert stairs.step_count == 5
    assert all(fact.step_count is None for fact in data.facts if fact.identity.fact_type != FactType.STAIRS)
    location = from_wkt(stairs.geog.removeprefix("SRID=4326;"))
    assert location.x == pytest.approx(19.92, abs=1e-6)
    assert location.y == pytest.approx(50.05, abs=1e-6)


def test_network_node_gives_kerb_and_point_barrier_and_knows_motor_traffic():
    kerb = build_node(1, 19.91, 50.05, {"barrier": "kerb", "kerb": "raised"})
    gate = build_node(2, 19.92, 50.05, {"barrier": "kissing_gate"})
    other = build_node(3, 19.93, 50.05)
    footway = build_way(10, (kerb, gate, other), {"highway": "footway"})
    road = build_way(11, (kerb, other), {"highway": "residential"})
    elements = (kerb, gate, other, footway, road)
    data = build_osm_fact_data(elements, BOUNDARY, OsmPreparedNetwork((kerb, gate, other), (footway, road)), ZONE)
    assert build_fact_keys(data.facts) == {(OsmElementType.NODE, 1, FactType.HIGH_KERB), (OsmElementType.NODE, 2, FactType.NARROW_PASSAGE)}
    assert data.motor_traffic_node_ids == frozenset({1, 3})


def test_point_barrier_off_the_network_gives_no_fact():
    step = build_node(1, 19.91, 50.05, {"barrier": "step"})
    data = build_osm_fact_data((step,), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert data.facts == ()


def test_amenity_node_counts_only_inside_the_boundary():
    inside = build_node(1, 19.95, 50.05, {"amenity": "bench"})
    outside = build_node(2, 20.5, 50.05, {"amenity": "bench"})
    on_edge = build_node(3, 19.9, 50.05, {"amenity": "bench"})
    data = build_osm_fact_data((inside, outside, on_edge), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert build_fact_keys(data.facts) == {(OsmElementType.NODE, 1, FactType.REST_PLACE)}
    assert data.facts[0].geog == "SRID=4326;POINT (19.95 50.05)"


def test_absent_and_unknown_amenities_give_no_fact():
    shelter = build_node(1, 19.95, 50.05, {"amenity": "shelter", "bench": "no"})
    toilets = build_node(2, 19.95, 50.06, {"amenity": "toilets", "wheelchair": "limited"})
    contradiction = build_node(3, 19.95, 50.07, {"entrance": "yes", "ramp": "yes", "ramp:wheelchair": "no"})
    area_elevator = build_area("way", 20, Polygon(((19.94, 50.04), (19.96, 50.04), (19.96, 50.06))), {"highway": "elevator"})
    data = build_osm_fact_data((shelter, toilets, contradiction, area_elevator), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert data.facts == ()


def test_amenity_area_of_a_way_is_located_strictly_inside():
    corners = tuple(build_node(index, lon, lat) for index, (lon, lat) in enumerate(((19.94, 50.04), (19.96, 50.04), (19.96, 50.06), (19.94, 50.06)), 1))
    tags = {"amenity": "toilets", "wheelchair": "yes"}
    outline = build_way(20, (*corners, corners[0]), tags)
    polygon = Polygon(tuple(node.coordinates[0] for node in corners))
    data = build_osm_fact_data((*corners, outline, build_area("way", 20, polygon, tags)), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert build_fact_keys(data.facts) == {(OsmElementType.WAY, 20, FactType.ACCESSIBLE_TOILET)}
    location = from_wkt(data.facts[0].geog.removeprefix("SRID=4326;"))
    assert polygon.contains(location)


def test_closed_network_way_keeps_its_facts_on_the_line_it_routes():
    corners = tuple(build_node(index, lon, lat) for index, (lon, lat) in enumerate(((19.94, 50.04), (19.96, 50.04), (19.96, 50.06), (19.94, 50.06)), 1))
    tags = {"highway": "footway", "surface": "gravel"}
    loop = build_way(30, (*corners, corners[0]), tags)
    polygon = Polygon(tuple(node.coordinates[0] for node in corners))
    data = build_osm_fact_data((*corners, loop, build_area("way", 30, polygon, tags)), BOUNDARY, OsmPreparedNetwork(corners, (loop,)), ZONE)
    assert build_fact_keys(data.facts) == {(OsmElementType.WAY, 30, FactType.POOR_SURFACE)}
    location = from_wkt(data.facts[0].geog.removeprefix("SRID=4326;"))
    assert polygon.exterior.distance(location) == pytest.approx(0, abs=1e-9)


def test_relation_area_in_the_copy_is_located_inside_and_keeps_relation_identity():
    member_nodes = (build_node(1, 19.94, 50.04), build_node(2, 19.96, 50.04), build_node(3, 19.96, 50.06))
    member = build_way(40, (*member_nodes, member_nodes[0]), {})
    tags = {"type": "multipolygon", "amenity": "toilets", "wheelchair": "designated"}
    polygon = Polygon(tuple(node.coordinates[0] for node in member_nodes))
    elements = (*member_nodes, member, build_relation(500, (40,), tags), build_area("relation", 500, polygon, tags))
    data = build_osm_fact_data(elements, BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert build_fact_keys(data.facts) == {(OsmElementType.RELATION, 500, FactType.ACCESSIBLE_TOILET)}
    assert polygon.contains(from_wkt(data.facts[0].geog.removeprefix("SRID=4326;")))


def test_non_area_relation_with_an_amenity_in_the_copy_fails_the_copy():
    member_nodes = (build_node(1, 19.94, 50.04), build_node(2, 19.96, 50.04))
    member = build_way(40, member_nodes, {})
    relation = build_relation(500, (40,), {"type": "site", "toilets:wheelchair": "yes"})
    with pytest.raises(OsmGeometryError, match="Non-area relation"):
        build_osm_fact_data((*member_nodes, member, relation), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)


def test_non_area_relation_outside_the_copy_is_ignored():
    member_nodes = (build_node(1, 20.4, 50.04), build_node(2, 20.5, 50.04))
    member = build_way(40, member_nodes, {})
    relation = build_relation(500, (40,), {"type": "site", "toilets:wheelchair": "yes"})
    assert build_osm_fact_data((*member_nodes, member, relation), BOUNDARY, OsmPreparedNetwork((), ()), ZONE).facts == ()


def test_amenity_way_crossing_the_boundary_is_kept_whole():
    inside = build_node(1, 19.99, 50.05)
    outside = build_node(2, 20.2, 50.05)
    way = build_way(50, (inside, outside), {"amenity": "bench"})
    data = build_osm_fact_data((inside, outside, way), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert build_fact_keys(data.facts) == {(OsmElementType.WAY, 50, FactType.REST_PLACE)}


def test_edit_day_is_the_business_zone_day_of_the_element_edit():
    late = datetime(2026, 10, 1, 23, 30, tzinfo=UTC)
    bench = build_node(1, 19.95, 50.05, {"amenity": "bench"}, late)
    data = build_osm_fact_data((bench,), BOUNDARY, OsmPreparedNetwork((), ()), ZONE)
    assert data.facts[0].edited_on == date(2026, 10, 2)


def test_network_way_without_usable_geometry_fails_instead_of_guessing():
    node = build_node(1, 19.95, 50.05)
    way = OsmElementSnapshot("way", 60, EDITED_AT, MappingProxyType({"highway": "steps"}), (1,), node.coordinates)
    with pytest.raises(OsmGeometryError):
        build_osm_fact_data((node, way), BOUNDARY, OsmPreparedNetwork((node,), (way,)), ZONE)


def test_network_node_amenity_is_kept_at_its_coordinates():
    node = build_node(1, 19.95, 50.05, {"highway": "elevator"})
    footway = build_way(70, (node, build_node(2, 19.96, 50.05)), {"highway": "footway"})
    data = build_osm_fact_data((node, footway), BOUNDARY, OsmPreparedNetwork((node,), (footway,)), ZONE)
    assert (OsmElementType.NODE, 1, FactType.ELEVATOR) in build_fact_keys(data.facts)
    assert Point(19.95, 50.05).wkt in data.facts[0].geog
