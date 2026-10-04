"""Plan one walking route of M2 for a profile from the copy in use, its facts and the routing service of the project."""

import math
from collections import defaultdict
from collections.abc import Collection, Iterable
from dataclasses import dataclass
from datetime import date

from accessibility_db.closed_lists import FactSource
from shapely import LineString, Point, to_wkt
from sqlalchemy import Connection
from sqlalchemy.exc import SQLAlchemyError

from common_time import build_business_day
from config.logging import fetch_logger
from data.engine import fetch_api_engine, fetch_read_only_snapshot
from data.osm_copy import fetch_current_osm_copy
from data.route_facts import REPORT_STRETCH_DISTANCE_M, StoredVote, fetch_fact_votes, fetch_geozone_ways, fetch_route_facts
from data.valhalla import RoutingServiceError, RoutingServiceNoRouteError, RoutingServiceTraceError, ValhallaRoute, ValhallaTrace, fetch_served_copy_instant, fetch_valhalla_route, fetch_valhalla_trace
from service.fact_status import FactStatus, FactView, resolve_fact_status
from service.route_boundary import resolve_points_outside_krakow
from service.route_graph import RouteGraph, RoutePoint, build_node_stretch_ids, build_stretch_coordinates, build_way_stretch_ids, fetch_route_graph, resolve_fewest_barriers_path
from service.route_requests import (
    SHAPE_MATCH_EDGE_WALK,
    SHAPE_MATCH_WALK_OR_SNAP,
    build_corridor_wkt,
    build_route_body,
    build_route_exclusions,
    build_trace_body,
    resolve_avoided_barriers,
    resolve_geozone_holds_point,
)
from service.route_segments import (
    AMENITY_DISTANCE_M,
    BARRIER_TYPES,
    MissingAttribute,
    PlacedFact,
    RouteFacts,
    RouteFactView,
    RoutingUnavailableError,
    SegmentState,
    TracedSegment,
    build_route_facts,
    build_route_segments,
    resolve_crossed_barriers,
    resolve_fact_on_segment,
    resolve_route_lists,
    resolve_segment_state,
)

ALTERNATIVE_STATUSES = frozenset({FactStatus.UNVERIFIED, FactStatus.DISPUTED})


class PointOutsideKrakowError(Exception):
    """A chosen point lies outside the boundary of Kraków of the copy in use; points names start, destination or both, in this order."""

    def __init__(self, points: tuple[str, ...]) -> None:
        """Keep the names of the points outside."""
        super().__init__("A chosen point lies outside Kraków")
        self.points = points


@dataclass(frozen=True)
class RouteSegment:
    """One segment of a planned route as the contract shows it."""

    line: tuple[tuple[float, float], ...]
    length_m: int
    state: SegmentState
    missing_attributes: tuple[MissingAttribute, ...]
    is_marked_wheelchair_no: bool


@dataclass(frozen=True)
class PlannedRoute:
    """A route with its segments and the three groups of its list."""

    length_m: int
    segments: tuple[RouteSegment, ...]
    profile_barriers: tuple[RouteFactView, ...]
    additional_barriers: tuple[RouteFactView, ...]
    amenities: tuple[RouteFactView, ...]


@dataclass(frozen=True)
class PlannedAlternative:
    """The alternative that avoids the unverified or disputed barriers of the profile the route keeps, with those barriers."""

    route: PlannedRoute
    avoided_barriers: tuple[RouteFactView, ...]


@dataclass(frozen=True)
class RouteAnswer:
    """The answer of plan_route."""

    osm_copy_date: date
    barrier_free_route_exists: bool
    route: PlannedRoute
    alternative: PlannedAlternative | None


@dataclass(frozen=True)
class RouteRequest:
    """What one route request carries: its two points and its profile."""

    start: RoutePoint
    destination: RoutePoint
    avoid: frozenset[str]
    need: frozenset[str]


@dataclass(frozen=True)
class CheckedRoute:
    """
    A route traced, tied to the stretches and checked.

    It keeps the facts of its traced line, what its request excluded, the barriers the path with the fewest barriers chose
    and may cross, and whether it crosses an unavoidable geozone.
    """

    trace: ValhallaTrace
    segments: tuple[TracedSegment, ...]
    facts: RouteFacts
    excluded: tuple[PlacedFact, ...]
    chosen_ids: frozenset[int]
    crosses_unavoidable_geozone: bool


def fetch_placed_facts(connection: Connection, graph: RouteGraph, area_wkt: str | None, distance_m: float, fact_types: Collection[str], way_ids: Collection[int]) -> RouteFacts:
    """Read the facts of an area or of the copy with their votes, derive their statuses and place them in the graph."""
    if not fact_types:
        return RouteFacts((), {})
    stored = fetch_route_facts(connection, area_wkt, distance_m, fact_types, way_ids)
    votes_by_fact: dict[int, list[StoredVote]] = defaultdict(list)
    for vote in fetch_fact_votes(connection, [fact.id for fact in stored]):
        votes_by_fact[vote.fact_id].append(vote)
    return build_route_facts(graph, (FactView(fact, resolve_fact_status(votes_by_fact[fact.id], fact.is_removed_from_osm)) for fact in stored))


def fetch_traced_route(route: ValhallaRoute) -> ValhallaTrace:
    """Trace a route with edge_walk and, after error 443, once more with walk_or_snap."""
    try:
        return fetch_valhalla_trace(build_trace_body(route.shape, SHAPE_MATCH_EDGE_WALK))
    except RoutingServiceTraceError:
        return fetch_valhalla_trace(build_trace_body(route.shape, SHAPE_MATCH_WALK_OR_SNAP))


def fetch_valhalla_route_avoiding(graph: RouteGraph, request: RouteRequest, excluded: Iterable[PlacedFact]) -> ValhallaRoute:
    """Request a walking route that excludes the given barriers and geozones."""
    return fetch_valhalla_route(build_route_body(request.start, request.destination, build_route_exclusions(graph, excluded, request.start, request.destination)))


def build_line_wkt(segments: Iterable[TracedSegment]) -> str:
    """Give the line of a route in longitude and latitude as WKT."""
    points: list[tuple[float, float]] = []
    for segment in segments:
        for point in segment.line:
            if not points or points[-1] != point:
                points.append(point)
    if len(points) == 1:
        points.append(points[0])
    return to_wkt(LineString(points), rounding_precision=7)


def build_segment_way_ids(graph: RouteGraph, segments: Iterable[TracedSegment]) -> tuple[int, ...]:
    """Give the ways of the segments of a route."""
    return tuple(sorted({int(graph.network.way_ids[graph.stretch_way[segment.stretch_id]]) for segment in segments if segment.stretch_id is not None}))


def resolve_checked_route(connection: Connection, graph: RouteGraph, request: RouteRequest, route: ValhallaRoute, excluded: tuple[PlacedFact, ...], chosen_ids: Collection[int]) -> CheckedRoute:
    """
    Trace a route, read the facts of its traced line and check it against everything it had to avoid.

    A route that crosses an avoided barrier or geozone, other than those of the path with the fewest barriers and the
    geozones holding a chosen point, is requested once more with the crossed ones excluded too; a second crossing ends the
    request with RoutingUnavailableError and one entry at ERROR that names no coordinate. An answer 442 to that repeated
    request is raised to the caller, which decides what it means.
    """
    barrier_types = {kind.value for kind in BARRIER_TYPES}
    for attempt in range(2):
        trace = fetch_traced_route(route)
        segments = build_route_segments(graph, trace, request.start, request.destination)
        trace_facts = fetch_placed_facts(connection, graph, build_line_wkt(segments), AMENITY_DISTANCE_M, barrier_types | request.need, build_segment_way_ids(graph, segments))
        avoided = resolve_avoided_barriers(trace_facts, request.avoid)
        unavoidable = {fact.view.fact.id for fact in avoided if fact.is_geozone and (resolve_geozone_holds_point(fact, request.start) or resolve_geozone_holds_point(fact, request.destination))}
        crossed = resolve_crossed_barriers(segments, graph, avoided, set(chosen_ids) | unavoidable)
        if not crossed:
            crosses_unavoidable = any(fact.view.fact.id in unavoidable and any(resolve_fact_on_segment(graph, fact, segment) for segment in segments) for fact in avoided)
            return CheckedRoute(trace, segments, trace_facts, excluded, frozenset(chosen_ids), crosses_unavoidable)
        if attempt == 1:
            fetch_logger(__name__).error("A route crossed %s excluded barriers after it was requested again, so it is not shown", len(crossed))
            raise RoutingUnavailableError("The route crossed an excluded barrier twice")
        excluded = excluded + crossed
        route = fetch_valhalla_route_avoiding(graph, request, excluded)
    raise RoutingUnavailableError("The route could not be checked")


def build_fact_stretches(graph: RouteGraph, fact: PlacedFact, geozone_ways: dict[int, list[int]]) -> tuple[int, ...]:
    """Give the stretches a fact lies on: those of its node, every stretch of its way, its stretch, or the stretches its geozone covers."""
    radius = fact.view.fact.geozone_radius_m
    if radius is not None:
        point = Point(fact.x, fact.y)
        stretches: list[int] = []
        for way_id in geozone_ways.get(fact.view.fact.id, []):
            row = int(graph.network.way_ids.searchsorted(way_id))
            if row < len(graph.network.way_ids) and graph.network.way_ids[row] == way_id:
                stretches.extend(int(stretch_id) for stretch_id in build_way_stretch_ids(graph, row) if LineString(build_stretch_coordinates(graph, int(stretch_id))).distance(point) <= radius)
        return tuple(stretches)
    if fact.node_row is not None:
        return build_node_stretch_ids(graph, fact.node_row)
    if fact.way_row is not None:
        return tuple(int(stretch_id) for stretch_id in build_way_stretch_ids(graph, fact.way_row))
    return () if fact.stretch_id is None else (fact.stretch_id,)


def fetch_fewest_barriers_route(connection: Connection, graph: RouteGraph, request: RouteRequest, corridor_avoided: tuple[PlacedFact, ...]) -> tuple[ValhallaRoute, set[int], tuple[PlacedFact, ...]]:
    """
    Find the route with the fewest barriers when no route avoids them all.

    Every avoided barrier and covering geozone of the profile in the whole copy is counted on its stretches, the graph finds
    the path with the fewest of them, and one more request excludes every avoided barrier and geozone of the corridor
    except those on that path. A failure of that request ends with RoutingUnavailableError.
    """
    copy_avoided = resolve_avoided_barriers(fetch_placed_facts(connection, graph, None, 0, request.avoid, ()), request.avoid)
    geozone_ways: dict[int, list[int]] = defaultdict(list)
    for geozone_id, way_id in fetch_geozone_ways(connection, [fact.view.fact.id for fact in copy_avoided if fact.is_geozone]):
        geozone_ways[geozone_id].append(way_id)
    counts: dict[int, int] = defaultdict(int)
    facts_by_stretch: dict[int, set[int]] = defaultdict(set)
    for fact in copy_avoided:
        for stretch_id in set(build_fact_stretches(graph, fact, geozone_ways)):
            counts[stretch_id] += 1
            facts_by_stretch[stretch_id].add(fact.view.fact.id)
    try:
        path = resolve_fewest_barriers_path(graph, request.start, request.destination, counts)
    except ValueError as error:
        raise RoutingUnavailableError("The graph joins no path between the two points") from error
    chosen = set().union(*(facts_by_stretch.get(stretch_id, set()) for stretch_id in path.stretch_ids))
    excluded = tuple(fact for fact in corridor_avoided if fact.view.fact.id not in chosen)
    try:
        return fetch_valhalla_route_avoiding(graph, request, excluded), chosen, excluded
    except RoutingServiceError as error:
        raise RoutingUnavailableError("The route with the fewest barriers could not be requested") from error


def build_planned_route(graph: RouteGraph, checked: CheckedRoute, request: RouteRequest) -> PlannedRoute:
    """Assess every segment of a checked route and build its list."""
    segments = []
    for segment in checked.segments:
        assessment = resolve_segment_state(segment, graph, checked.facts, request.avoid)
        segments.append(RouteSegment(segment.line, segment.length_m, assessment.state, assessment.missing_attributes, assessment.is_marked_wheelchair_no))
    lists = resolve_route_lists(checked.segments, graph, checked.facts, request.avoid, request.need)
    return PlannedRoute(sum(segment.length_m for segment in segments), tuple(segments), lists.profile_barriers, lists.additional_barriers, lists.amenities)


def build_edge_sequence(trace: ValhallaTrace) -> tuple[tuple[int, int, int], ...]:
    """Give the ways and nodes a traced route passes, in order."""
    return tuple((edge.way_id, edge.begin_node_id, edge.end_node_id) for edge in trace.edges)


def resolve_alternative(connection: Connection, graph: RouteGraph, request: RouteRequest, checked: CheckedRoute, route: PlannedRoute) -> PlannedAlternative | None:
    """
    Propose one alternative around the unverified or disputed reports of the profile the route keeps.

    Those reports are added to the excluded locations; the new route is traced, checked and assessed like the route, with
    the barriers the path with the fewest barriers chose still allowed, and it is the alternative when its ways and nodes
    differ, naming the reports it avoids. An answer 442 to any request of the alternative gives no alternative.
    """
    kept = tuple(
        fact
        for fact in checked.facts.facts
        if fact.fact_type.value in request.avoid
        and not fact.is_geozone
        and fact.view.fact.source != FactSource.OPENSTREETMAP
        and fact.is_prevailing
        and fact.view.status.status in ALTERNATIVE_STATUSES
        and any(resolve_fact_on_segment(graph, fact, segment) for segment in checked.segments)
    )
    if not kept:
        return None
    try:
        alternative_route = fetch_valhalla_route_avoiding(graph, request, checked.excluded + kept)
        alternative = resolve_checked_route(connection, graph, request, alternative_route, checked.excluded + kept, checked.chosen_ids)
    except RoutingServiceNoRouteError:
        return None
    if build_edge_sequence(alternative.trace) == build_edge_sequence(checked.trace):
        return None
    avoided_ids = {fact.view.fact.id for fact in kept if not any(resolve_fact_on_segment(graph, fact, segment) for segment in alternative.segments)}
    if not avoided_ids:
        return None
    avoided_barriers = tuple(item for item in route.profile_barriers if item.view.fact.id in avoided_ids)
    return PlannedAlternative(build_planned_route(graph, alternative, request), avoided_barriers)


def resolve_route_in_snapshot(connection: Connection, request: RouteRequest) -> RouteAnswer:
    """Plan a route inside one read-only snapshot, in the order of D-15 of the route plan."""
    copy = fetch_current_osm_copy(connection)
    if copy is None:
        raise RoutingUnavailableError("No OpenStreetMap copy is in use")
    state_at = copy.state_at.instant
    outside = resolve_points_outside_krakow(state_at, request.start, request.destination)
    if outside:
        raise PointOutsideKrakowError(outside)
    if math.floor(state_at.timestamp()) != fetch_served_copy_instant():
        raise RoutingUnavailableError("The routing service does not serve the copy in use")
    graph = fetch_route_graph(connection, state_at)
    corridor_facts = fetch_placed_facts(connection, graph, build_corridor_wkt(request.start, request.destination), REPORT_STRETCH_DISTANCE_M, request.avoid, ())
    excluded = resolve_avoided_barriers(corridor_facts, request.avoid)
    chosen: set[int] = set()
    barrier_free = True
    try:
        route = fetch_valhalla_route_avoiding(graph, request, excluded)
    except RoutingServiceNoRouteError:
        route, chosen, excluded = fetch_fewest_barriers_route(connection, graph, request, excluded)
        barrier_free = False
    checked = resolve_checked_route(connection, graph, request, route, excluded, chosen)
    planned = build_planned_route(graph, checked, request)
    alternative = resolve_alternative(connection, graph, request, checked, planned)
    return RouteAnswer(build_business_day(state_at), barrier_free and not checked.crosses_unavoidable_geozone, planned, alternative)


def resolve_route(start: RoutePoint, destination: RoutePoint, avoid: frozenset[str], need: frozenset[str]) -> RouteAnswer:
    """
    Plan the walking route of one request in one read-only snapshot of the API engine.

    A point outside Kraków raises PointOutsideKrakowError. A database error or a failure of the routing service becomes
    RoutingUnavailableError, logged at ERROR with its kind and never with a coordinate.
    """
    try:
        with fetch_read_only_snapshot(fetch_api_engine()) as connection:
            return resolve_route_in_snapshot(connection, RouteRequest(start, destination, avoid, need))
    except (SQLAlchemyError, RoutingServiceError) as error:
        fetch_logger(__name__).error("A route request could not be planned: %s", type(error).__name__)
        raise RoutingUnavailableError("No route can be planned right now") from error
