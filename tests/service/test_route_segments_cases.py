"""Check the segments of a traced route, their states of M7, the contradictions of reports and the list of M8 on invented networks."""

import numpy as np
import pytest
from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, OsmElementType, WayBarrierState

from data.valhalla import ValhallaEdge, ValhallaTrace
from service.fact_status import FactStatus
from service.route_graph import RoutePoint, build_route_graph, build_stretch_node_rows
from service.route_segments import (
    MissingAttribute,
    RoutingUnavailableError,
    SegmentState,
    TracedSegment,
    build_route_facts,
    build_route_segments,
    resolve_crossed_barriers,
    resolve_route_lists,
    resolve_segment_state,
)
from tests.common_route_network import (
    INVENTED_STATE_AT,
    InventedNode,
    InventedWay,
    build_encoded_polyline,
    build_invented_fact,
    build_invented_network,
    build_invented_trace,
    build_invented_view,
)

pytestmark = pytest.mark.usefixtures("runtime_settings")

WHEELCHAIR = frozenset({"stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"})
STROLLER = frozenset({"stairs", "high_kerb", "poor_surface", "narrow_passage"})
WALKING_DIFFICULTY = frozenset({"stairs", "poor_surface", "steep_incline"})
PRESETS = [WHEELCHAIR, STROLLER, WALKING_DIFFICULTY]
LINE_NODES = [InventedNode(1, 0, 0), InventedNode(2, 50, 0), InventedNode(3, 100, 0), InventedNode(4, 150, 0), InventedNode(6, 100, 80)]
LINE_BY_ID = {node.id: node for node in LINE_NODES}


def build_line_graph(way: InventedWay | None = None):
    """Build way 100 through nodes 1 - 4 with way 200 leaving node 3, so way 100 has two stretches."""
    main = way or InventedWay(100, (1, 2, 3, 4))
    return build_route_graph(build_invented_network(LINE_NODES, [main, InventedWay(200, (3, 6))]), INVENTED_STATE_AT)


def build_point(node: InventedNode, north_shift_m: float = 0.0) -> RoutePoint:
    """Give a chosen point at a node, shifted north by the given metres."""
    shifted = InventedNode(0, node.east_m, node.north_m + north_shift_m)
    return RoutePoint(shifted.lat, shifted.lon)


def build_whole_way_segment(graph) -> TracedSegment:
    """Build the segment of the first stretch of the graph, with every node of it counted."""
    rows = build_stretch_node_rows(graph, 0)
    line = tuple((float(graph.network.node_lon[row]), float(graph.network.node_lat[row])) for row in rows)
    return TracedSegment(line, 100, 0, tuple(int(row) for row in rows))


def resolve_way_assessment(way: InventedWay, nodes: list[InventedNode], avoid: frozenset[str], views=()):
    """Assess the one stretch of a one-way invented network."""
    graph = build_route_graph(build_invented_network(nodes, [way]), INVENTED_STATE_AT)
    return resolve_segment_state(build_whole_way_segment(graph), graph, build_route_facts(graph, views), avoid)


FOOTWAY_NODES = [InventedNode(1, 0, 0), InventedNode(2, 100, 0)]


def test_edge_across_two_stretches_is_split_in_two_segments() -> None:
    """Split one edge of way 100 from node 1 to node 4 at the shared node 3, with the two straight stretches added."""
    graph = build_line_graph()
    trace = build_invented_trace(LINE_BY_ID, [(100, [1, 2, 3, 4])])
    segments = build_route_segments(graph, trace, build_point(LINE_BY_ID[1]), build_point(LINE_BY_ID[4]))
    assert [segment.stretch_id is None for segment in segments] == [True, False, False, True]
    assert [segment.length_m for segment in segments] == [0, 100, 50, 0]
    assert sorted(int(graph.network.node_ids[row]) for row in segments[1].node_rows) == [1, 2, 3]


def test_first_and_last_edges_keep_only_their_traversed_part() -> None:
    """Leave out node 1 before the start and node 4 after the end of a route that joins way 100 between its nodes."""
    graph = build_line_graph()
    start, end = InventedNode(0, 25, 0), InventedNode(0, 125, 0)
    points = [(start.lon, start.lat), (LINE_BY_ID[2].lon, LINE_BY_ID[2].lat), (LINE_BY_ID[3].lon, LINE_BY_ID[3].lat), (end.lon, end.lat)]
    trace = ValhallaTrace(build_encoded_polyline(points), (ValhallaEdge(100, 1, 4, 0, 3),))
    segments = build_route_segments(graph, trace, RoutePoint(start.lat, start.lon + 0.0003), RoutePoint(end.lat, end.lon))
    network_segments = [segment for segment in segments if segment.stretch_id is not None]
    assert [sorted(int(graph.network.node_ids[row]) for row in segment.node_rows) for segment in network_segments] == [[2, 3], [3]]
    assert segments[0].length_m > 0


def test_straight_stretches_are_no_data_with_steps_missing() -> None:
    """Make the stretch to the network no_data with every attribute of the profile missing, the steps included."""
    graph = build_line_graph()
    segments = build_route_segments(graph, build_invented_trace(LINE_BY_ID, [(100, [1, 2, 3])]), build_point(LINE_BY_ID[1], 20), build_point(LINE_BY_ID[3]))
    assessment = resolve_segment_state(segments[0], graph, build_route_facts(graph, []), frozenset({"stairs", "poor_surface"}))
    assert assessment.state == SegmentState.NO_DATA
    assert assessment.missing_attributes == (MissingAttribute.SURFACE, MissingAttribute.STEPS)


def test_edge_pointing_outside_its_shape_ends_the_request() -> None:
    """Refuse a traced edge whose shape index lies beyond the traced shape, instead of failing with an index error."""
    graph = build_line_graph()
    trace = ValhallaTrace(build_encoded_polyline([(LINE_BY_ID[1].lon, LINE_BY_ID[1].lat), (LINE_BY_ID[2].lon, LINE_BY_ID[2].lat)]), (ValhallaEdge(100, 1, 2, 0, 5),))
    with pytest.raises(RoutingUnavailableError):
        build_route_segments(graph, trace, build_point(LINE_BY_ID[1]), build_point(LINE_BY_ID[2]))


def test_edge_of_a_way_the_graph_lacks_ends_the_request() -> None:
    """Refuse a traced edge whose way the copy does not hold."""
    graph = build_line_graph()
    trace = ValhallaTrace(build_encoded_polyline([(LINE_BY_ID[1].lon, LINE_BY_ID[1].lat), (LINE_BY_ID[2].lon, LINE_BY_ID[2].lat)]), (ValhallaEdge(999, 1, 2, 0, 1),))
    with pytest.raises(RoutingUnavailableError):
        build_route_segments(graph, trace, build_point(LINE_BY_ID[1]), build_point(LINE_BY_ID[2]))


@pytest.mark.parametrize("avoid", PRESETS)
def test_known_footway_without_carriageway_is_no_barrier_for_every_preset(avoid: frozenset[str]) -> None:
    """Make a footway of paving stones, 4% and 2 m that meets no carriageway no_barrier for each preset (mapping AC-2)."""
    way = InventedWay(1, (1, 2), poor_surface=WayBarrierState.ABSENT, steep_incline=WayBarrierState.ABSENT, narrow_passage=WayBarrierState.ABSENT)
    assert resolve_way_assessment(way, FOOTWAY_NODES, avoid).state == SegmentState.NO_BARRIER


def test_segment_y_meeting_a_carriageway_misses_the_kerbs_incline_and_width() -> None:
    """Make asphalt without incline, kerb data or width partial_data for the wheelchair and only the incline missing for walking difficulty (mapping AC-3, AC-8)."""
    way = InventedWay(1, (1, 2), poor_surface=WayBarrierState.ABSENT)
    nodes = [InventedNode(1, 0, 0, is_on_motor_traffic_way=True), InventedNode(2, 100, 0)]
    wheelchair = resolve_way_assessment(way, nodes, WHEELCHAIR)
    assert (wheelchair.state, wheelchair.missing_attributes) == (SegmentState.PARTIAL_DATA, (MissingAttribute.KERBS, MissingAttribute.INCLINE, MissingAttribute.WIDTH))
    walking = resolve_way_assessment(way, nodes, WALKING_DIFFICULTY)
    assert (walking.state, walking.missing_attributes) == (SegmentState.PARTIAL_DATA, (MissingAttribute.INCLINE,))


@pytest.mark.parametrize("avoid", PRESETS)
def test_footway_without_tags_is_no_data_and_with_asphalt_partial_data(avoid: frozenset[str]) -> None:
    """Make an untagged footway no_data for each preset and the same footway with asphalt partial_data (mapping AC-13)."""
    assert resolve_way_assessment(InventedWay(1, (1, 2)), FOOTWAY_NODES, avoid).state == SegmentState.NO_DATA
    assert resolve_way_assessment(InventedWay(1, (1, 2), poor_surface=WayBarrierState.ABSENT), FOOTWAY_NODES, avoid).state == SegmentState.PARTIAL_DATA


@pytest.mark.parametrize("avoid", PRESETS)
def test_way_marked_wheelchair_no_is_never_no_barrier(avoid: frozenset[str]) -> None:
    """Make a known footway marked wheelchair=no partial_data with its marking for each preset (mapping AC-14)."""
    way = InventedWay(1, (1, 2), poor_surface=WayBarrierState.ABSENT, steep_incline=WayBarrierState.ABSENT, narrow_passage=WayBarrierState.ABSENT, is_marked_wheelchair_no=True)
    assessment = resolve_way_assessment(way, FOOTWAY_NODES, avoid)
    assert (assessment.state, assessment.is_marked_wheelchair_no) == (SegmentState.PARTIAL_DATA, True)


def test_profile_of_stairs_alone_on_a_way_not_tagged_as_steps_is_no_data() -> None:
    """Make a way known only by the default of no stairs no_data for a profile that avoids only stairs."""
    assessment = resolve_way_assessment(InventedWay(1, (1, 2)), FOOTWAY_NODES, frozenset({"stairs"}))
    assert (assessment.state, assessment.missing_attributes) == (SegmentState.NO_DATA, ())


def test_contradicted_kerb_report_follows_openstreetmap_until_it_reaches_two() -> None:
    """Overrule a high kerb report at a lowered crossing, then make the segment barrier after the next confirmation (scenario 4, AC-6)."""
    nodes = [InventedNode(1, 0, 0), InventedNode(2, 10, 0, kerb=KerbPointState.LOWERED, is_crossing=True), InventedNode(3, 20, 0)]
    way = InventedWay(1, (1, 2, 3), poor_surface=WayBarrierState.ABSENT, steep_incline=WayBarrierState.ABSENT, narrow_passage=WayBarrierState.ABSENT, is_crossing=True)
    report = build_invented_fact(1, FactType.HIGH_KERB, nodes[1], nearest_way_id=1, north_shift_m=2)
    graph = build_route_graph(build_invented_network(nodes, [way]), INVENTED_STATE_AT)
    segment = build_whole_way_segment(graph)
    before = build_route_facts(graph, [build_invented_view(report, FactStatus.UNVERIFIED, 1.5)])
    assert resolve_segment_state(segment, graph, before, WHEELCHAIR).state == SegmentState.NO_BARRIER
    assert before.facts[0].is_overruled_by_osm
    after = build_route_facts(graph, [build_invented_view(report, FactStatus.UNVERIFIED, 2.0)])
    assert not after.facts[0].is_overruled_by_osm
    assert resolve_segment_state(segment, graph, after, WHEELCHAIR).state == SegmentState.BARRIER


def test_outdated_kerb_report_never_replaces_openstreetmap() -> None:
    """Keep the lowered kerb of OpenStreetMap against an outdated high kerb report, even one whose confirmations reach 2."""
    nodes = [InventedNode(1, 0, 0), InventedNode(2, 10, 0, kerb=KerbPointState.LOWERED, is_crossing=True), InventedNode(3, 20, 0)]
    way = InventedWay(1, (1, 2, 3), poor_surface=WayBarrierState.ABSENT, steep_incline=WayBarrierState.ABSENT, narrow_passage=WayBarrierState.ABSENT, is_crossing=True)
    report = build_invented_fact(1, FactType.HIGH_KERB, nodes[1], nearest_way_id=1, north_shift_m=2)
    graph = build_route_graph(build_invented_network(nodes, [way]), INVENTED_STATE_AT)
    facts = build_route_facts(graph, [build_invented_view(report, FactStatus.OUTDATED, 2.0, 3.0)])
    assert facts.kerb_overrides == {}
    assert not facts.facts[0].is_prevailing
    assert resolve_segment_state(build_whole_way_segment(graph), graph, facts, WHEELCHAIR).state == SegmentState.NO_BARRIER


@pytest.mark.parametrize(("distance_m", "is_overruled"), [(4, True), (6, False)])
def test_kerb_report_is_contradicted_only_within_five_metres(distance_m: float, is_overruled: bool) -> None:
    """Contradict a high kerb report by a lowered kerb point 4 m away and not by one 6 m away."""
    nodes = [InventedNode(1, 0, 0), InventedNode(2, 10, 0, kerb=KerbPointState.LOWERED), InventedNode(3, 40, 0)]
    graph = build_route_graph(build_invented_network(nodes, [InventedWay(1, (1, 2, 3))]), INVENTED_STATE_AT)
    report = build_invented_fact(1, FactType.HIGH_KERB, nodes[1], nearest_way_id=1, east_shift_m=distance_m)
    assert build_route_facts(graph, [build_invented_view(report)]).facts[0].is_overruled_by_osm is is_overruled


def test_way_state_absent_contradicts_a_surface_report_and_never_a_stairs_report() -> None:
    """Contradict a report of poor surface on asphalt, and never a report of stairs on a way not tagged as steps."""
    graph = build_route_graph(build_invented_network(FOOTWAY_NODES, [InventedWay(1, (1, 2), poor_surface=WayBarrierState.ABSENT)]), INVENTED_STATE_AT)
    surface = build_invented_fact(1, FactType.POOR_SURFACE, FOOTWAY_NODES[0], nearest_way_id=1, east_shift_m=50, north_shift_m=3)
    stairs = build_invented_fact(2, FactType.STAIRS, FOOTWAY_NODES[0], nearest_way_id=1, east_shift_m=50, north_shift_m=3)
    facts = build_route_facts(graph, [build_invented_view(surface), build_invented_view(stairs)])
    assert [fact.is_overruled_by_osm for fact in facts.facts] == [True, False]


def build_route_on_line(avoid: frozenset[str], need: frozenset[str], views_of):
    """Build the segments of a route along way 100 and its list, with the facts the callback gives for the graph."""
    graph = build_line_graph(InventedWay(100, (1, 2, 3, 4), stairs=WayBarrierState.PRESENT))
    segments = build_route_segments(graph, build_invented_trace(LINE_BY_ID, [(100, [1, 2, 3, 4])]), build_point(LINE_BY_ID[1]), build_point(LINE_BY_ID[4]))
    facts = build_route_facts(graph, views_of(graph))
    return graph, segments, facts


def test_empty_profile_is_not_assessed_with_every_barrier_additional() -> None:
    """Give every segment of a route of an empty profile not_assessed and list its steps among the additional barriers (AC-7)."""
    steps = build_invented_fact(1, FactType.STAIRS, LINE_BY_ID[2], FactSource.OPENSTREETMAP, (OsmElementType.WAY, 100))
    graph, segments, facts = build_route_on_line(frozenset(), frozenset({"rest_place"}), lambda _graph: [build_invented_view(steps)])
    assert {resolve_segment_state(segment, graph, facts, frozenset()).state for segment in segments} == {SegmentState.NOT_ASSESSED}
    assert all(resolve_segment_state(segment, graph, facts, frozenset()).missing_attributes == () for segment in segments)
    lists = resolve_route_lists(segments, graph, facts, frozenset(), frozenset({"rest_place"}))
    assert [item.view.fact.id for item in lists.additional_barriers] == [1]
    assert lists.profile_barriers == ()


def test_amenity_within_fifty_metres_is_listed_and_one_at_sixty_is_not() -> None:
    """List a rest place 40 m from the route and leave out one 60 m from it, with its distance from the start (AC-8)."""
    near = build_invented_fact(1, FactType.REST_PLACE, LINE_BY_ID[2], north_shift_m=40)
    far = build_invented_fact(2, FactType.REST_PLACE, LINE_BY_ID[2], north_shift_m=60)
    graph, segments, facts = build_route_on_line(WHEELCHAIR, frozenset({"rest_place"}), lambda _graph: [build_invented_view(near), build_invented_view(far)])
    lists = resolve_route_lists(segments, graph, facts, WHEELCHAIR, frozenset({"rest_place"}))
    assert [(item.view.fact.id, item.distance_from_start_m) for item in lists.amenities] == [(1, 50)]


def test_steps_way_on_the_route_is_a_profile_barrier_and_its_segments_are_barrier() -> None:
    """Make every segment of a way of steps barrier for a profile avoiding stairs and list the steps among its barriers."""
    steps = build_invented_fact(1, FactType.STAIRS, LINE_BY_ID[2], FactSource.OPENSTREETMAP, (OsmElementType.WAY, 100))
    graph, segments, facts = build_route_on_line(WHEELCHAIR, frozenset(), lambda _graph: [build_invented_view(steps)])
    states = [resolve_segment_state(segment, graph, facts, WHEELCHAIR).state for segment in segments]
    assert states == [SegmentState.NO_DATA, SegmentState.BARRIER, SegmentState.BARRIER, SegmentState.NO_DATA]
    assert [item.view.fact.id for item in resolve_route_lists(segments, graph, facts, WHEELCHAIR, frozenset()).profile_barriers] == [1]


def test_crossed_excluded_barrier_is_found_unless_excepted() -> None:
    """Find an avoided report lying on a traversed stretch, and not when it was chosen by the path with the fewest barriers."""
    report = build_invented_fact(1, FactType.STAIRS, LINE_BY_ID[2], nearest_way_id=100, north_shift_m=5)
    graph, segments, facts = build_route_on_line(WHEELCHAIR, frozenset(), lambda _graph: [build_invented_view(report, FactStatus.CONFIRMED, 2.0)])
    assert [fact.view.fact.id for fact in resolve_crossed_barriers(segments, graph, facts.facts, ())] == [1]
    assert resolve_crossed_barriers(segments, graph, facts.facts, {1}) == ()
    assert np.isfinite(facts.facts[0].x)
