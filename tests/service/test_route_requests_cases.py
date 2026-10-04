"""Check the walking request bodies, the exclusions, the corridor, the polyline and what a route avoids, on invented networks."""

import math

import numpy as np
import pytest
from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, OsmElementType, WayBarrierState
from shapely import from_wkt
from shapely.ops import transform

from service.fact_status import FactStatus
from service.route_graph import RoutePoint, build_projected_coordinates, build_route_graph
from service.route_requests import (
    GEOZONE_POLYGON_VERTICES,
    build_corridor_wkt,
    build_geozone_polygon,
    build_polyline_points,
    build_route_body,
    build_route_exclusions,
    resolve_avoided_barriers,
)
from service.route_segments import build_route_facts
from tests.common_route_network import INVENTED_STATE_AT, InventedNode, InventedWay, build_invented_fact, build_invented_network, build_invented_view

pytestmark = pytest.mark.usefixtures("runtime_settings")

NODES = [
    InventedNode(1, 0, 0),
    InventedNode(2, 50, 0),
    InventedNode(3, 150, 0, kerb=KerbPointState.HIGH, is_crossing=True),
    InventedNode(4, 200, 0),
    InventedNode(5, 150, 60),
    InventedNode(6, 50, -60),
]
WAYS = [InventedWay(100, (1, 2, 3, 4), stairs=WayBarrierState.PRESENT), InventedWay(200, (3, 5)), InventedWay(300, (2, 6))]
NODE_BY_ID = {node.id: node for node in NODES}


def build_graph():
    """Build the graph of the invented network of this module."""
    return build_route_graph(build_invented_network(NODES, WAYS), INVENTED_STATE_AT)


def build_far_point(east_m: float, north_m: float) -> RoutePoint:
    """Give a chosen point at an offset from the base point."""
    node = InventedNode(0, east_m, north_m)
    return RoutePoint(node.lat, node.lon)


def test_walking_request_carries_the_costing_options_of_d4() -> None:
    """Send the pedestrian costing of type foot with the neutral options the spike measured, and never wheelchair."""
    body = build_route_body(build_far_point(0, 0), build_far_point(100, 0), build_route_exclusions(build_graph(), (), build_far_point(0, 0), build_far_point(100, 0)))
    assert body["costing"] == "pedestrian"
    assert body["costing_options"] == {
        "pedestrian": {
            "type": "foot",
            "max_hiking_difficulty": 6,
            "step_penalty": 0,
            "elevator_penalty": 0,
            "walkway_factor": 1.0,
            "sidewalk_factor": 1.0,
            "alley_factor": 1.0,
            "driveway_factor": 1.0,
            "use_living_streets": 0.5,
            "use_ferry": 0,
        }
    }
    assert "exclude_locations" not in body and "exclude_polygons" not in body


def test_report_is_excluded_at_the_middle_of_the_longest_pair_of_its_stretch() -> None:
    """Exclude a confirmed report of stairs at the middle of the longest pair of its stretch with tolerance 0."""
    graph = build_graph()
    report = build_invented_fact(1, FactType.STAIRS, NODE_BY_ID[2], nearest_way_id=100, east_shift_m=30, north_shift_m=5)
    facts = build_route_facts(graph, [build_invented_view(report, FactStatus.CONFIRMED, 2.0)])
    exclusions = build_route_exclusions(graph, resolve_avoided_barriers(facts, frozenset({"stairs"})), build_far_point(-500, 0), build_far_point(700, 0))
    assert len(exclusions.locations) == 1
    location = exclusions.locations[0]
    assert location.node_snap_tolerance == 0
    assert location.lon == pytest.approx((NODE_BY_ID[2].lon + NODE_BY_ID[3].lon) / 2)
    assert location.lat == pytest.approx((NODE_BY_ID[2].lat + NODE_BY_ID[3].lat) / 2)


def test_node_barrier_is_excluded_at_its_node_with_tolerance_one() -> None:
    """Exclude a high kerb of OpenStreetMap at its node with tolerance 1."""
    graph = build_graph()
    kerb = build_invented_fact(2, FactType.HIGH_KERB, NODE_BY_ID[3], FactSource.OPENSTREETMAP, (OsmElementType.NODE, 3))
    facts = build_route_facts(graph, [build_invented_view(kerb)])
    exclusions = build_route_exclusions(graph, resolve_avoided_barriers(facts, frozenset({"high_kerb"})), build_far_point(-500, 0), build_far_point(700, 0))
    assert [(location.lat, location.lon, location.node_snap_tolerance) for location in exclusions.locations] == [(pytest.approx(NODE_BY_ID[3].lat), pytest.approx(NODE_BY_ID[3].lon), 1)]


def test_every_stretch_of_an_avoided_steps_way_is_excluded() -> None:
    """Exclude each of the three stretches of a way tagged as steps, whose fact stands at its middle."""
    graph = build_graph()
    steps = build_invented_fact(3, FactType.STAIRS, NODE_BY_ID[3], FactSource.OPENSTREETMAP, (OsmElementType.WAY, 100))
    facts = build_route_facts(graph, [build_invented_view(steps)])
    exclusions = build_route_exclusions(graph, resolve_avoided_barriers(facts, frozenset({"stairs"})), build_far_point(-500, 0), build_far_point(700, 0))
    assert len(exclusions.locations) == 3
    assert {location.node_snap_tolerance for location in exclusions.locations} == {0}


def test_geozone_polygon_is_circumscribed_with_32_vertices() -> None:
    """Place every vertex of the polygon of a 50 m geozone at the radius divided by the cosine of pi over 32."""
    centre = NODE_BY_ID[1]
    ring = build_geozone_polygon(centre.lat, centre.lon, 50)
    assert len(ring) == GEOZONE_POLYGON_VERTICES + 1 and ring[0] == ring[-1]
    xs, ys = build_projected_coordinates(np.asarray([point[0] for point in ring]), np.asarray([point[1] for point in ring]))
    cx, cy = build_projected_coordinates(np.asarray([centre.lon]), np.asarray([centre.lat]))
    distances = np.hypot(xs - cx[0], ys - cy[0])
    assert distances == pytest.approx(50 / math.cos(math.pi / 32), abs=0.01)


def test_geozone_holding_the_start_is_not_sent() -> None:
    """Send a geozone as a polygon, except one whose circle holds the start."""
    graph = build_graph()
    far = build_invented_fact(4, FactType.POOR_SURFACE, NODE_BY_ID[4], geozone_radius_m=25)
    holding = build_invented_fact(5, FactType.POOR_SURFACE, NODE_BY_ID[1], geozone_radius_m=100)
    facts = build_route_facts(graph, [build_invented_view(far), build_invented_view(holding)])
    exclusions = build_route_exclusions(graph, resolve_avoided_barriers(facts, frozenset({"poor_surface"})), build_far_point(10, 0), build_far_point(700, 0))
    assert len(exclusions.polygons) == 1
    body = build_route_body(build_far_point(10, 0), build_far_point(700, 0), exclusions)
    assert len(body["exclude_polygons"]) == 1


@pytest.mark.parametrize(("length_m", "half_width_m"), [(1000, 1000), (8000, 2000)])
def test_corridor_is_a_rectangle_around_the_straight_line(length_m: float, half_width_m: float) -> None:
    """Give a 1 km line a corridor of 1000 m on each side and an 8 km line one of a quarter of its length."""
    corridor = from_wkt(build_corridor_wkt(build_far_point(0, 0), build_far_point(length_m, 0)))
    projected = transform(lambda lon, lat: build_projected_coordinates(np.asarray(lon), np.asarray(lat)), corridor)
    assert projected.area == pytest.approx((length_m + 2 * half_width_m) * 2 * half_width_m, rel=0.01)


def test_polyline_of_precision_six_is_decoded_into_longitude_and_latitude() -> None:
    """Decode the three-point example of the encoded polyline algorithm at precision 6."""
    assert build_polyline_points("_p~iF~ps|U_ulLnnqC_mqNvxq`@") == ((-12.02, 3.85), (-12.095, 4.07), (-12.6453, 4.3252))


def test_truncated_polyline_is_refused() -> None:
    """Refuse an encoded polyline cut in the middle of a value."""
    with pytest.raises(ValueError):
        build_polyline_points("_p~iF~ps|U_")


def test_only_prevailing_barriers_of_the_profile_are_avoided() -> None:
    """Avoid a confirmed report and not an unverified one, not an outdated fact of OpenStreetMap, and not a high kerb replaced by a confirmed lowered kerb report."""
    graph = build_graph()
    unverified = build_invented_fact(10, FactType.STAIRS, NODE_BY_ID[5], nearest_way_id=200, north_shift_m=-10)
    confirmed = build_invented_fact(11, FactType.STAIRS, NODE_BY_ID[6], nearest_way_id=300, north_shift_m=10)
    outdated = build_invented_fact(12, FactType.STAIRS, NODE_BY_ID[3], FactSource.OPENSTREETMAP, (OsmElementType.WAY, 100))
    replaced = build_invented_fact(13, FactType.HIGH_KERB, NODE_BY_ID[3], FactSource.OPENSTREETMAP, (OsmElementType.NODE, 3))
    lowered_report = build_invented_fact(14, FactType.LOWERED_KERB, NODE_BY_ID[3], nearest_way_id=100, east_shift_m=2)
    facts = build_route_facts(
        graph,
        [
            build_invented_view(unverified, FactStatus.UNVERIFIED, 0.5),
            build_invented_view(confirmed, FactStatus.CONFIRMED, 2.0),
            build_invented_view(outdated, FactStatus.OUTDATED, 0.0, 2.0),
            build_invented_view(replaced),
            build_invented_view(lowered_report, FactStatus.CONFIRMED, 2.0),
        ],
    )
    avoided = {fact.view.fact.id for fact in resolve_avoided_barriers(facts, frozenset({"stairs", "high_kerb"}))}
    assert avoided == {11}
