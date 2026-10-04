"""Tie a traced route to the stretches of the copy, place its facts, and decide the state of every segment and the list of the route."""

from collections.abc import Collection, Iterable
from dataclasses import dataclass, replace
from enum import StrEnum
from itertools import pairwise

import numpy as np
from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, OsmElementType, WayBarrierState
from pyproj import Geod
from shapely import LineString, Point

from data.route_facts import StoredRouteFact
from data.route_network import KERB_POINT_STATES, NO_KERB_POINT, WAY_BARRIER_STATES
from data.valhalla import ValhallaTrace
from service.fact_status import FactStatus, FactView
from service.route_graph import (
    RouteGraph,
    RoutePoint,
    build_node_row,
    build_projected_coordinates,
    build_stretch_coordinates,
    build_stretch_node_rows,
    build_stretch_of_position,
    build_way_node_rows,
    build_way_row,
    build_way_stretch_ids,
)
from service.route_requests import build_polyline_points

KERB_CONTRADICTION_DISTANCE_M = 5
AMENITY_DISTANCE_M = 50
REPORT_REPLACEMENT_CONFIRMATIONS = 2.0
PARTIAL_EDGE_TOLERANCE_M = 0.5
BARRIER_TYPES = frozenset({FactType.STAIRS, FactType.HIGH_KERB, FactType.POOR_SURFACE, FactType.STEEP_INCLINE, FactType.NARROW_PASSAGE})
WAY_STATE_COLUMNS = {FactType.STAIRS: 0, FactType.POOR_SURFACE: 1, FactType.STEEP_INCLINE: 2, FactType.NARROW_PASSAGE: 3}
OPPOSITE_KERB = {FactType.HIGH_KERB: KerbPointState.LOWERED, FactType.LOWERED_KERB: KerbPointState.HIGH}
OPPOSITE_KERB_FACT = {FactType.HIGH_KERB: FactType.LOWERED_KERB, FactType.LOWERED_KERB: FactType.HIGH_KERB}
WGS84_GEOD = Geod(ellps="WGS84")


class RoutingUnavailableError(RuntimeError):
    """No route can be computed right now, and none is guessed."""


class SegmentState(StrEnum):
    """The four states of M7 and the state of a route of a profile without barriers."""

    BARRIER = "barrier"
    NO_BARRIER = "no_barrier"
    PARTIAL_DATA = "partial_data"
    NO_DATA = "no_data"
    NOT_ASSESSED = "not_assessed"


class MissingAttribute(StrEnum):
    """The attributes behind the barriers of the profile, in the order the contract lists them."""

    KERBS = "kerbs"
    SURFACE = "surface"
    INCLINE = "incline"
    WIDTH = "width"
    STEPS = "steps"


BARRIER_ATTRIBUTES = {
    FactType.HIGH_KERB: MissingAttribute.KERBS,
    FactType.POOR_SURFACE: MissingAttribute.SURFACE,
    FactType.STEEP_INCLINE: MissingAttribute.INCLINE,
    FactType.NARROW_PASSAGE: MissingAttribute.WIDTH,
    FactType.STAIRS: MissingAttribute.STEPS,
}
ATTRIBUTE_ORDER = tuple(MissingAttribute)


class AttributeKnowledge(StrEnum):
    """What a segment knows about the attribute behind one barrier of the profile."""

    KNOWN = "known"
    KNOWN_BY_DEFAULT = "known_by_default"
    UNKNOWN = "unknown"
    IRRELEVANT = "irrelevant"


@dataclass(frozen=True)
class TracedSegment:
    """A part of one stretch the route takes, or a straight stretch to the network without a stretch, with the nodes that count for it."""

    line: tuple[tuple[float, float], ...]
    length_m: int
    stretch_id: int | None
    node_rows: tuple[int, ...]


@dataclass(frozen=True)
class PlacedFact:
    """
    A fact of a route with its place in the graph and its standing against OpenStreetMap.

    A fact from OpenStreetMap has the row of its node or way, a report has the stretch it lies on, and a geozone covers
    every stretch within its radius. A report contradicted by OpenStreetMap is overruled until its confirmations reach 2;
    then it replaces the facts of OpenStreetMap it contradicts.
    """

    view: FactView
    x: float
    y: float
    node_row: int | None
    way_row: int | None
    stretch_id: int | None
    is_overruled_by_osm: bool
    is_replaced: bool

    @property
    def fact_type(self) -> FactType:
        """The type of the fact."""
        return self.view.fact.fact_type

    @property
    def is_geozone(self) -> bool:
        """Whether the fact is a geozone."""
        return self.view.fact.geozone_radius_m is not None

    @property
    def is_visible_on_route(self) -> bool:
        """Whether the fact is neither outdated nor replaced, so it may stand on a route and its list."""
        return self.view.status.status != FactStatus.OUTDATED and not self.is_replaced

    @property
    def is_prevailing(self) -> bool:
        """Whether the fact counts as present where it lies: visible, and for a report placed on a stretch and not overruled."""
        if not self.is_visible_on_route:
            return False
        if self.view.fact.source == FactSource.OPENSTREETMAP or self.is_geozone:
            return True
        return self.stretch_id is not None and not self.is_overruled_by_osm


@dataclass(frozen=True)
class RouteFacts:
    """The placed facts of a route and the kerb points whose knowledge a vote or a report changed."""

    facts: tuple[PlacedFact, ...]
    kerb_overrides: dict[int, KerbPointState]


@dataclass(frozen=True)
class SegmentAssessment:
    """The state of a segment, its missing attributes and the marking of its way."""

    state: SegmentState
    missing_attributes: tuple[MissingAttribute, ...]
    is_marked_wheelchair_no: bool


@dataclass(frozen=True)
class RouteFactView:
    """A fact of the list of a route with its distance along the route and whether OpenStreetMap overrules it."""

    view: FactView
    distance_from_start_m: int
    is_overruled_by_osm: bool


@dataclass(frozen=True)
class RouteLists:
    """The three groups of M8 in order along the route."""

    profile_barriers: tuple[RouteFactView, ...]
    additional_barriers: tuple[RouteFactView, ...]
    amenities: tuple[RouteFactView, ...]


def build_nearest_stretch(graph: RouteGraph, way_row: int, x: float, y: float) -> int | None:
    """Give the stretch of a way nearest to a point in EPSG:2180."""
    best: tuple[float, int] | None = None
    point = Point(x, y)
    for stretch_id in build_way_stretch_ids(graph, way_row):
        distance = LineString(build_stretch_coordinates(graph, int(stretch_id))).distance(point)
        if best is None or distance < best[0]:
            best = (distance, int(stretch_id))
    return None if best is None else best[1]


def build_fact_place(graph: RouteGraph, view: FactView, x: float, y: float) -> tuple[int | None, int | None, int | None]:
    """Give the node row and the way row of a fact of OpenStreetMap, or the stretch a report lies on, each none when it does not apply."""
    fact = view.fact
    if fact.source == FactSource.OPENSTREETMAP and fact.osm_element_id is not None:
        if fact.osm_element_type == OsmElementType.NODE:
            return build_node_row(graph, fact.osm_element_id), None, None
        if fact.osm_element_type == OsmElementType.WAY:
            return None, build_way_row(graph, fact.osm_element_id), None
        return None, None, None
    if fact.geozone_radius_m is None and isinstance(fact, StoredRouteFact) and fact.nearest_way_id is not None:
        report_way = build_way_row(graph, fact.nearest_way_id)
        if report_way is not None:
            return None, None, build_nearest_stretch(graph, report_way, x, y)
    return None, None, None


def build_route_facts(graph: RouteGraph, views: Iterable[FactView]) -> RouteFacts:
    """
    Place every fact of a route in the graph and decide which reports OpenStreetMap contradicts.

    A report lies on the stretch of its nearest way nearest to it; a kerb report is contradicted by an opposite kerb point
    on that stretch within 5 m, a report of a barrier of a way by the state absent of that barrier on its way, and a
    report of stairs never. A contradicted report that is not outdated and whose confirmations reach 2 replaces the
    opposite kerb facts of OpenStreetMap it met; otherwise it is overruled. An outdated or replaced kerb fact leaves its
    kerb point unknown or turns it into the kerb the report states.
    """
    items = list(views)
    if not items:
        return RouteFacts((), {})
    xs, ys = build_projected_coordinates(np.asarray([item.fact.lon for item in items]), np.asarray([item.fact.lat for item in items]))
    placed: list[PlacedFact] = []
    replaced_nodes: dict[tuple[int, FactType], KerbPointState] = {}
    for item, x, y in zip(items, xs, ys, strict=True):
        fact = item.fact
        node_row, way_row, stretch_id = build_fact_place(graph, item, float(x), float(y))
        is_overruled = False
        if stretch_id is not None:
            contradicting_nodes = resolve_report_contradiction(graph, fact.fact_type, stretch_id, float(x), float(y))
            if contradicting_nodes is not None:
                if item.status.status != FactStatus.OUTDATED and item.status.confirmations >= REPORT_REPLACEMENT_CONFIRMATIONS:
                    for row in contradicting_nodes:
                        replaced_nodes[(row, OPPOSITE_KERB_FACT[fact.fact_type])] = KerbPointState.HIGH if fact.fact_type == FactType.HIGH_KERB else KerbPointState.LOWERED
                else:
                    is_overruled = True
        placed.append(PlacedFact(item, float(x), float(y), node_row, way_row, stretch_id, is_overruled, False))
    kerb_overrides: dict[int, KerbPointState] = {}
    replaced_ids: set[int] = set()
    for candidate in placed:
        if candidate.view.fact.source != FactSource.OPENSTREETMAP or candidate.node_row is None or candidate.fact_type not in OPPOSITE_KERB:
            continue
        if (candidate.node_row, candidate.fact_type) in replaced_nodes:
            replaced_ids.add(candidate.view.fact.id)
            kerb_overrides[candidate.node_row] = replaced_nodes[(candidate.node_row, candidate.fact_type)]
        elif candidate.view.status.status == FactStatus.OUTDATED:
            kerb_overrides[candidate.node_row] = KerbPointState.UNKNOWN
    return RouteFacts(tuple(replace(candidate, is_replaced=True) if candidate.view.fact.id in replaced_ids else candidate for candidate in placed), kerb_overrides)


def resolve_report_contradiction(graph: RouteGraph, fact_type: FactType, stretch_id: int, x: float, y: float) -> tuple[int, ...] | None:
    """Give the kerb nodes that contradict a report on its stretch, an empty tuple for a contradiction by a way state, or none when nothing contradicts it."""
    if fact_type in OPPOSITE_KERB:
        rows = build_stretch_node_rows(graph, stretch_id)
        opposite = KERB_POINT_STATES.index(OPPOSITE_KERB[fact_type])
        near = tuple(int(row) for row in rows if graph.network.node_kerb[row] == opposite and float(np.hypot(graph.node_x[row] - x, graph.node_y[row] - y)) <= KERB_CONTRADICTION_DISTANCE_M)
        return near or None
    if fact_type in WAY_STATE_COLUMNS and fact_type != FactType.STAIRS:
        way_row = int(graph.stretch_way[stretch_id])
        state = WAY_BARRIER_STATES[int(graph.network.way_states[way_row, WAY_STATE_COLUMNS[fact_type]])]
        return () if state == WayBarrierState.ABSENT else None
    return None


def build_segment_way_row(graph: RouteGraph, segment: TracedSegment) -> int | None:
    """Give the way row of a segment, or none for a straight stretch to the network."""
    return None if segment.stretch_id is None else int(graph.stretch_way[segment.stretch_id])


def resolve_fact_on_segment(graph: RouteGraph, fact: PlacedFact, segment: TracedSegment) -> bool:
    """Decide whether a fact lies on a segment: its node counts for it, its way is the way of it, its report lies on its stretch, or its geozone covers its stretch."""
    if segment.stretch_id is None:
        return False
    if fact.is_geozone:
        radius = fact.view.fact.geozone_radius_m or 0
        return LineString(build_stretch_coordinates(graph, segment.stretch_id)).distance(Point(fact.x, fact.y)) <= radius
    if fact.node_row is not None:
        return fact.node_row in segment.node_rows
    if fact.way_row is not None:
        return fact.way_row == build_segment_way_row(graph, segment)
    return fact.stretch_id is not None and fact.stretch_id == segment.stretch_id


def build_effective_kerb(graph: RouteGraph, facts: RouteFacts, node_row: int) -> KerbPointState | None:
    """Give the kerb point of a node as votes and reports leave it, or none when the node is not a kerb point."""
    if node_row in facts.kerb_overrides:
        return facts.kerb_overrides[node_row]
    code = int(graph.network.node_kerb[node_row])
    return None if code == NO_KERB_POINT else KERB_POINT_STATES[code]


def resolve_attribute_knowledge(graph: RouteGraph, facts: RouteFacts, segment: TracedSegment, lying: Collection[PlacedFact], barrier: FactType) -> AttributeKnowledge:
    """Decide what a segment of a way knows about the attribute behind one barrier, by D-7 of the mapping plan."""
    way_row = int(graph.stretch_way[segment.stretch_id]) if segment.stretch_id is not None else -1
    if barrier == FactType.HIGH_KERB:
        flags = graph.network.way_flags[way_row]
        nodes = segment.node_rows
        meets_carriageway = bool(flags[2]) or any(
            graph.network.node_kerb[row] != NO_KERB_POINT or graph.network.node_is_crossing[row] or graph.network.node_is_on_motor_traffic_way[row] for row in nodes
        )
        if bool(flags[1]) or not meets_carriageway:
            return AttributeKnowledge.IRRELEVANT
        kerbs = [build_effective_kerb(graph, facts, row) for row in nodes]
        present = [kerb for kerb in kerbs if kerb is not None]
        return AttributeKnowledge.KNOWN if present and all(kerb == KerbPointState.LOWERED for kerb in present) else AttributeKnowledge.UNKNOWN
    state = WAY_BARRIER_STATES[int(graph.network.way_states[way_row, WAY_STATE_COLUMNS[barrier]])]
    if barrier == FactType.STAIRS:
        stale_step = any(fact.fact_type == FactType.STAIRS and fact.node_row is not None and not fact.is_visible_on_route for fact in lying)
        return AttributeKnowledge.KNOWN_BY_DEFAULT if state == WayBarrierState.ABSENT_BY_DEFAULT and not stale_step else AttributeKnowledge.UNKNOWN
    return AttributeKnowledge.KNOWN if state == WayBarrierState.ABSENT else AttributeKnowledge.UNKNOWN


def build_ordered_attributes(barriers: Iterable[FactType]) -> tuple[MissingAttribute, ...]:
    """Give the attributes behind barriers in the order kerbs, surface, incline, width, steps."""
    attributes = {BARRIER_ATTRIBUTES[barrier] for barrier in barriers}
    return tuple(attribute for attribute in ATTRIBUTE_ORDER if attribute in attributes)


def resolve_segment_state(segment: TracedSegment, graph: RouteGraph, facts: RouteFacts, avoid: frozenset[str]) -> SegmentAssessment:
    """
    Decide the state of one segment by M7.

    An empty profile gives not_assessed. A straight stretch to the network is no_data with every attribute of the profile
    missing, its stairs included. A prevailing barrier of the profile on the segment makes it barrier. Otherwise the
    segment is no_barrier when every relevant attribute is known, partial_data when some are, and no_data when none is
    known other than the stairs by default; a way marked wheelchair=no is never no_barrier.
    """
    profile = [FactType(value) for value in sorted(avoid)]
    if segment.stretch_id is None:
        if not profile:
            return SegmentAssessment(SegmentState.NOT_ASSESSED, (), False)
        return SegmentAssessment(SegmentState.NO_DATA, build_ordered_attributes(profile), False)
    way_row = int(graph.stretch_way[segment.stretch_id])
    is_marked_wheelchair_no = bool(graph.network.way_flags[way_row, 0])
    if not profile:
        return SegmentAssessment(SegmentState.NOT_ASSESSED, (), is_marked_wheelchair_no)
    lying = [fact for fact in facts.facts if fact.fact_type in BARRIER_TYPES and resolve_fact_on_segment(graph, fact, segment)]
    if any(fact.is_prevailing and fact.fact_type in profile for fact in lying):
        return SegmentAssessment(SegmentState.BARRIER, (), is_marked_wheelchair_no)
    knowledge = {barrier: resolve_attribute_knowledge(graph, facts, segment, lying, barrier) for barrier in profile}
    relevant = {barrier: value for barrier, value in knowledge.items() if value != AttributeKnowledge.IRRELEVANT}
    unknown = [barrier for barrier, value in relevant.items() if value == AttributeKnowledge.UNKNOWN]
    known = [barrier for barrier, value in relevant.items() if value == AttributeKnowledge.KNOWN]
    if not relevant:
        state = SegmentState.NO_BARRIER
    elif not known:
        state = SegmentState.NO_DATA
    elif unknown:
        state = SegmentState.PARTIAL_DATA
    else:
        state = SegmentState.NO_BARRIER
    if state == SegmentState.NO_BARRIER and is_marked_wheelchair_no:
        state = SegmentState.PARTIAL_DATA
    missing = build_ordered_attributes(unknown) if state in (SegmentState.PARTIAL_DATA, SegmentState.NO_DATA) else ()
    return SegmentAssessment(state, missing, is_marked_wheelchair_no)


def build_geodesic_length(line: tuple[tuple[float, float], ...]) -> int:
    """Give the geodesic length of a line of longitude and latitude pairs on WGS 84 in whole metres."""
    if len(line) < 2:
        return 0
    return round(WGS84_GEOD.line_length([point[0] for point in line], [point[1] for point in line]))


def build_edge_positions(graph: RouteGraph, way_row: int, begin_node_id: int, end_node_id: int) -> tuple[int, int]:
    """Give the positions in its way of the two nodes of an edge, the closest pair when a node repeats, or raise RoutingUnavailableError."""
    begin_row, end_row = build_node_row(graph, begin_node_id), build_node_row(graph, end_node_id)
    if begin_row is None or end_row is None:
        raise RoutingUnavailableError("An edge of the route names a node the copy does not hold")
    rows = build_way_node_rows(graph, way_row)
    begins, ends = np.flatnonzero(rows == begin_row), np.flatnonzero(rows == end_row)
    pairs = [(int(begin), int(end)) for begin in begins for end in ends if begin != end]
    if not pairs:
        raise RoutingUnavailableError("An edge of the route does not match its way in the copy")
    return min(pairs, key=lambda pair: abs(pair[0] - pair[1]))


def build_route_segments(graph: RouteGraph, trace: ValhallaTrace, start: RoutePoint, destination: RoutePoint) -> tuple[TracedSegment, ...]:
    """
    Turn a traced route into segments of the stretches of the copy, with the two straight stretches to the network.

    Every edge maps by its way and its two nodes to the positions of that way; an edge across several stretches is split
    at the vertex of its shape nearest to each graph node inside it; the first and the last edge keep only the nodes of
    their traversed part; consecutive pieces of one stretch join into one segment. An edge the copy cannot place, or whose
    shape indices fall outside the traced shape, raises RoutingUnavailableError.
    """
    try:
        points = build_polyline_points(trace.shape)
    except ValueError as error:
        raise RoutingUnavailableError("The traced route has a malformed shape") from error
    if not points:
        raise RoutingUnavailableError("The traced route has no shape")
    xs, ys = build_projected_coordinates(np.asarray([point[0] for point in points]), np.asarray([point[1] for point in points]))
    pieces: list[tuple[int, int, int, list[int]]] = []
    last_edge = len(trace.edges) - 1
    for index, edge in enumerate(trace.edges):
        if not (0 <= edge.begin_shape_index < len(points) and 0 <= edge.end_shape_index < len(points)):
            raise RoutingUnavailableError("An edge of the route points outside the traced shape")
        way_row = build_way_row(graph, edge.way_id)
        if way_row is None:
            raise RoutingUnavailableError("An edge of the route names a way the copy does not hold")
        first, last = build_edge_positions(graph, way_row, edge.begin_node_id, edge.end_node_id)
        step = 1 if last > first else -1
        rows = build_way_node_rows(graph, way_row)
        positions = list(range(first, last + step, step))
        kept = set(positions)
        if index in (0, last_edge):
            kept = resolve_traversed_positions(graph, rows, positions, xs, ys, edge.begin_shape_index if index == 0 else None, edge.end_shape_index if index == last_edge else None)
        shape_low, shape_high = edge.begin_shape_index, max(edge.begin_shape_index, edge.end_shape_index)
        boundaries = [first] + [position for position in positions[1:-1] if graph.graph_index[rows[position]] >= 0] + [last]
        shape_cuts = [shape_low]
        for position in boundaries[1:-1]:
            row = rows[position]
            window = np.arange(shape_cuts[-1], shape_high + 1)
            nearest = int(window[np.argmin(np.hypot(xs[window] - graph.node_x[row], ys[window] - graph.node_y[row]))])
            shape_cuts.append(nearest)
        shape_cuts.append(shape_high)
        for (position_a, position_b), (cut_a, cut_b) in zip(pairwise(boundaries), pairwise(shape_cuts), strict=True):
            stretch_id = build_stretch_of_position(graph, way_row, position_a, position_b)
            if stretch_id is None:
                raise RoutingUnavailableError("An edge of the route does not match the stretches of the copy")
            low, high = min(position_a, position_b), max(position_a, position_b)
            node_rows = [int(rows[position]) for position in range(low, high + 1) if position in kept]
            if cut_a == cut_b and not node_rows:
                continue
            pieces.append((stretch_id, cut_a, cut_b, node_rows))
    segments: list[TracedSegment] = [build_connector(start, points[0])]
    merged: list[tuple[int, int, int, list[int]]] = []
    for piece in pieces:
        if merged and merged[-1][0] == piece[0]:
            previous = merged[-1]
            merged[-1] = (previous[0], previous[1], piece[2], previous[3] + [row for row in piece[3] if row not in previous[3]])
        else:
            merged.append(piece)
    for stretch_id, cut_a, cut_b, node_rows in merged:
        line = tuple(points[cut_a : cut_b + 1]) if cut_b > cut_a else (points[cut_a], points[cut_a])
        segments.append(TracedSegment(line, build_geodesic_length(line), stretch_id, tuple(node_rows)))
    segments.append(build_connector(destination, points[-1], reverse=True))
    return tuple(segments)


def resolve_traversed_positions(graph: RouteGraph, rows: np.ndarray, positions: list[int], xs: np.ndarray, ys: np.ndarray, begin_shape_index: int | None, end_shape_index: int | None) -> set[int]:
    """Keep the positions of a first or last edge that the route passes, by projecting its start or end onto the line of the edge."""
    coordinates = [(float(graph.node_x[rows[position]]), float(graph.node_y[rows[position]])) for position in positions]
    if len(coordinates) < 2 or len(set(coordinates)) < 2:
        return set(positions)
    line = LineString(coordinates)
    along = [line.project(Point(coordinate)) for coordinate in coordinates]
    low = line.project(Point(float(xs[begin_shape_index]), float(ys[begin_shape_index]))) - PARTIAL_EDGE_TOLERANCE_M if begin_shape_index is not None else float("-inf")
    high = line.project(Point(float(xs[end_shape_index]), float(ys[end_shape_index]))) + PARTIAL_EDGE_TOLERANCE_M if end_shape_index is not None else float("inf")
    return {position for position, distance in zip(positions, along, strict=True) if low <= distance <= high}


def build_connector(point: RoutePoint, joined: tuple[float, float], reverse: bool = False) -> TracedSegment:
    """Build the straight stretch between a chosen point and the place the route joins the network, even when it is 0 m long."""
    chosen = (point.lon, point.lat)
    line = (joined, chosen) if reverse else (chosen, joined)
    return TracedSegment(line, build_geodesic_length(line), None, ())


def build_route_line(segments: Iterable[TracedSegment]) -> LineString:
    """Join the lines of the segments into one line of the route in EPSG:2180."""
    points: list[tuple[float, float]] = []
    for segment in segments:
        for point in segment.line:
            if not points or points[-1] != point:
                points.append(point)
    if len(points) == 1:
        points.append(points[0])
    xs, ys = build_projected_coordinates(np.asarray([point[0] for point in points]), np.asarray([point[1] for point in points]))
    return LineString(list(zip(xs.tolist(), ys.tolist(), strict=True)))


def resolve_route_lists(segments: tuple[TracedSegment, ...], graph: RouteGraph, facts: RouteFacts, avoid: frozenset[str], need: frozenset[str]) -> RouteLists:
    """
    Build the three groups of M8 from the visible facts of a route.

    The barriers of the profile and the other barriers that lie on the route, geozones included, and the amenities of the
    need within 50 m of it, each ordered by the distance along the route to the projection of its point. With an empty
    profile every barrier is in the second group.
    """
    line = build_route_line(segments)
    profile: list[RouteFactView] = []
    additional: list[RouteFactView] = []
    amenities: list[RouteFactView] = []
    for fact in facts.facts:
        if not fact.is_visible_on_route:
            continue
        point = Point(fact.x, fact.y)
        item = RouteFactView(fact.view, round(line.project(point)), fact.is_overruled_by_osm)
        if fact.fact_type in BARRIER_TYPES:
            if any(resolve_fact_on_segment(graph, fact, segment) for segment in segments):
                (profile if fact.fact_type.value in avoid else additional).append(item)
        elif fact.fact_type.value in need and line.distance(point) <= AMENITY_DISTANCE_M:
            amenities.append(item)
    return RouteLists(*(tuple(sorted(group, key=lambda entry: (entry.distance_from_start_m, entry.view.fact.id))) for group in (profile, additional, amenities)))


def resolve_crossed_barriers(segments: tuple[TracedSegment, ...], graph: RouteGraph, avoided: Iterable[PlacedFact], excepted_ids: Collection[int]) -> tuple[PlacedFact, ...]:
    """Give every avoided barrier or geozone that lies on a segment of the route, other than the excepted ones."""
    return tuple(fact for fact in avoided if fact.view.fact.id not in excepted_ids and any(resolve_fact_on_segment(graph, fact, segment) for segment in segments))
