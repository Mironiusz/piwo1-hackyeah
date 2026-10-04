"""Build the bodies of the walking requests to the routing service and decide which barriers and geozones a route avoids."""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from accessibility_db.closed_lists import FactSource
from pyproj import Transformer
from shapely import LineString, Point, Polygon, to_wkt
from shapely.ops import transform

from service.fact_status import FactStatus
from service.osm_geometry import OSM_CALCULATION_CRS, OSM_STORAGE_CRS
from service.route_graph import RouteGraph, RoutePoint, build_projected_coordinates, build_stretch_node_rows, build_way_stretch_ids

if TYPE_CHECKING:
    from service.route_segments import PlacedFact, RouteFacts

PEDESTRIAN_COSTING_OPTIONS = {
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
CORRIDOR_MIN_HALF_WIDTH_M = 1000
CORRIDOR_LENGTH_DIVISOR = 4
GEOZONE_POLYGON_VERTICES = 32
STRETCH_SNAP_TOLERANCE_M = 0
NODE_SNAP_TOLERANCE_M = 1
POLYLINE_PRECISION = 1_000_000
SHAPE_MATCH_EDGE_WALK = "edge_walk"
SHAPE_MATCH_WALK_OR_SNAP = "walk_or_snap"


@dataclass(frozen=True)
class ExcludedLocation:
    """A place the route must not pass, with the snap tolerance of a barrier of a stretch or of a node."""

    lat: float
    lon: float
    node_snap_tolerance: int


@dataclass(frozen=True)
class RouteExclusions:
    """The excluded locations and the excluded polygons of one walking request."""

    locations: tuple[ExcludedLocation, ...]
    polygons: tuple[tuple[tuple[float, float], ...], ...]


def build_polyline_points(encoded: str) -> tuple[tuple[float, float], ...]:
    """Decode an encoded polyline of precision 6 into longitude and latitude pairs, refusing a truncated one with ValueError."""
    points: list[tuple[float, float]] = []
    index = lat = lon = 0
    while index < len(encoded):
        deltas: list[int] = []
        for _ in range(2):
            result = shift = 0
            while True:
                if index >= len(encoded):
                    raise ValueError("Truncated encoded polyline")
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if byte < 0x20:
                    break
            deltas.append(~(result >> 1) if result & 1 else result >> 1)
        lat += deltas[0]
        lon += deltas[1]
        points.append((lon / POLYLINE_PRECISION, lat / POLYLINE_PRECISION))
    return tuple(points)


def build_reverse_transformer() -> Transformer:
    """Build the transformer from the metres of EPSG:2180 back to WGS 84."""
    return Transformer.from_crs(OSM_CALCULATION_CRS, OSM_STORAGE_CRS, always_xy=True)


def build_projected_point(point: RoutePoint) -> Point:
    """Project a chosen point into EPSG:2180."""
    x, y = build_projected_coordinates(np.asarray([point.lon]), np.asarray([point.lat]))
    return Point(float(x[0]), float(y[0]))


def build_corridor_wkt(start: RoutePoint, destination: RoutePoint) -> str:
    """Give, as WKT in longitude and latitude, the rectangle around the straight line between two points, each side max(1000, length / 4) metres wide."""
    first, last = build_projected_point(start), build_projected_point(destination)
    length = first.distance(last)
    half_width = max(CORRIDOR_MIN_HALF_WIDTH_M, length / CORRIDOR_LENGTH_DIVISOR)
    axis = LineString([first, last]) if length > 0 else first
    corridor = axis.buffer(half_width, cap_style="square", join_style="mitre")
    return to_wkt(transform(build_reverse_transformer().transform, corridor), rounding_precision=7)


def build_geozone_polygon(lat: float, lon: float, radius_m: float) -> tuple[tuple[float, float], ...]:
    """Give the closed ring of the polygon of 32 vertices circumscribed about the circle of a geozone, computed in EPSG:2180."""
    centre = build_projected_point(RoutePoint(lat, lon))
    vertex_radius = radius_m / math.cos(math.pi / GEOZONE_POLYGON_VERTICES)
    angles = [2 * math.pi * index / GEOZONE_POLYGON_VERTICES for index in range(GEOZONE_POLYGON_VERTICES)]
    ring = Polygon([(centre.x + vertex_radius * math.cos(angle), centre.y + vertex_radius * math.sin(angle)) for angle in angles])
    coordinates = transform(build_reverse_transformer().transform, ring).exterior.coords
    return tuple((float(x), float(y)) for x, y in coordinates)


def resolve_geozone_holds_point(fact: "PlacedFact", point: RoutePoint) -> bool:
    """Decide whether the circle of a geozone holds a chosen point, which the routing service could not route out of."""
    radius = fact.view.fact.geozone_radius_m
    return radius is not None and Point(fact.x, fact.y).distance(build_projected_point(point)) <= radius


def resolve_avoided_barriers(facts: "RouteFacts", avoid: frozenset[str]) -> tuple["PlacedFact", ...]:
    """
    Choose what a route avoids by M2.

    A barrier fact of OpenStreetMap of the profile that is not outdated and not replaced by a contradicting report, a user
    report of the profile that is confirmed and lies on a stretch, and a geozone of a type of the profile that is not
    outdated. An unverified or disputed report is not avoided, so its segment stays red and the alternative avoids it.
    """
    avoided: list[PlacedFact] = []
    for fact in facts.facts:
        if fact.fact_type.value not in avoid or not fact.is_visible_on_route:
            continue
        if fact.is_geozone:
            avoided.append(fact)
        elif fact.view.fact.source == FactSource.OPENSTREETMAP:
            if fact.node_row is not None or fact.way_row is not None:
                avoided.append(fact)
        elif fact.view.status.status == FactStatus.CONFIRMED and fact.stretch_id is not None:
            avoided.append(fact)
    return tuple(avoided)


def build_stretch_location(graph: RouteGraph, stretch_id: int) -> ExcludedLocation:
    """Give the middle of the longest pair of consecutive nodes of a stretch, where a barrier of the whole stretch is excluded with tolerance 0."""
    rows = build_stretch_node_rows(graph, stretch_id)
    lengths = np.hypot(np.diff(graph.node_x[rows]), np.diff(graph.node_y[rows]))
    pair = int(np.argmax(lengths))
    lon = (float(graph.network.node_lon[rows[pair]]) + float(graph.network.node_lon[rows[pair + 1]])) / 2
    lat = (float(graph.network.node_lat[rows[pair]]) + float(graph.network.node_lat[rows[pair + 1]])) / 2
    return ExcludedLocation(lat, lon, STRETCH_SNAP_TOLERANCE_M)


def build_route_exclusions(graph: RouteGraph, avoided: Iterable["PlacedFact"], start: RoutePoint, destination: RoutePoint) -> RouteExclusions:
    """
    Turn avoided facts into the exclusions of a request.

    A barrier of a node is excluded at the node with tolerance 1, a fact of a way on every stretch of its way, a report on
    its stretch, and a geozone as its polygon, except a geozone whose circle holds the start or the destination.
    """
    locations: dict[tuple[float, float, int], ExcludedLocation] = {}
    polygons: list[tuple[tuple[float, float], ...]] = []
    for fact in avoided:
        radius = fact.view.fact.geozone_radius_m
        if radius is not None:
            if not resolve_geozone_holds_point(fact, start) and not resolve_geozone_holds_point(fact, destination):
                polygons.append(build_geozone_polygon(fact.view.fact.lat, fact.view.fact.lon, radius))
            continue
        found: list[ExcludedLocation] = []
        if fact.node_row is not None:
            found.append(ExcludedLocation(float(graph.network.node_lat[fact.node_row]), float(graph.network.node_lon[fact.node_row]), NODE_SNAP_TOLERANCE_M))
        elif fact.way_row is not None:
            found.extend(build_stretch_location(graph, int(stretch_id)) for stretch_id in build_way_stretch_ids(graph, fact.way_row))
        elif fact.stretch_id is not None:
            found.append(build_stretch_location(graph, fact.stretch_id))
        for location in found:
            locations[(location.lat, location.lon, location.node_snap_tolerance)] = location
    return RouteExclusions(tuple(locations.values()), tuple(polygons))


def build_route_body(start: RoutePoint, destination: RoutePoint, exclusions: RouteExclusions) -> dict[str, object]:
    """Build the walking request of D-4 and D-5 of the Valhalla plan, which never sends the pedestrian type wheelchair."""
    body: dict[str, object] = {
        "locations": [{"lat": start.lat, "lon": start.lon}, {"lat": destination.lat, "lon": destination.lon}],
        "costing": "pedestrian",
        "costing_options": {"pedestrian": dict(PEDESTRIAN_COSTING_OPTIONS)},
        "directions_type": "none",
    }
    if exclusions.locations:
        body["exclude_locations"] = [{"lat": item.lat, "lon": item.lon, "radius": 0, "minimum_reachability": 0, "node_snap_tolerance": item.node_snap_tolerance} for item in exclusions.locations]
    if exclusions.polygons:
        body["exclude_polygons"] = [[[lon, lat] for lon, lat in ring] for ring in exclusions.polygons]
    return body


def build_trace_body(shape: str, shape_match: str) -> dict[str, object]:
    """Build the trace of a route shape with the same costing as its request."""
    return {"encoded_polyline": shape, "shape_match": shape_match, "costing": "pedestrian", "costing_options": {"pedestrian": dict(PEDESTRIAN_COSTING_OPTIONS)}}
