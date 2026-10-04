"""Invented small pedestrian networks, facts and routing service answers for the tests of the route; no OpenStreetMap data."""

from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np
from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, OsmElementType, WayBarrierState

from data.route_facts import StoredRouteFact
from data.route_network import KERB_POINT_STATES, NO_KERB_POINT, WAY_BARRIER_STATES, RouteNetworkArrays
from data.valhalla import ValhallaEdge, ValhallaTrace
from service.fact_status import FactStatus, FactStatusResult, FactView

BASE_LON = 19.94
BASE_LAT = 50.06
INVENTED_STATE_AT = datetime(2026, 10, 2, 20, 21, 34, tzinfo=UTC)


@dataclass(frozen=True)
class InventedNode:
    """A node of an invented network at an offset in metres east and north of the base point."""

    id: int
    east_m: float
    north_m: float
    kerb: KerbPointState | None = None
    is_crossing: bool = False
    is_on_motor_traffic_way: bool = False

    @property
    def lon(self) -> float:
        """The longitude of the node."""
        return BASE_LON + self.east_m / (111320 * np.cos(np.radians(BASE_LAT)))

    @property
    def lat(self) -> float:
        """The latitude of the node."""
        return BASE_LAT + self.north_m / 110574


@dataclass(frozen=True)
class InventedWay:
    """A way of an invented network with its barrier states and flags."""

    id: int
    node_ids: tuple[int, ...]
    stairs: WayBarrierState = WayBarrierState.ABSENT_BY_DEFAULT
    poor_surface: WayBarrierState = WayBarrierState.UNKNOWN
    steep_incline: WayBarrierState = WayBarrierState.UNKNOWN
    narrow_passage: WayBarrierState = WayBarrierState.UNKNOWN
    is_marked_wheelchair_no: bool = False
    is_motor_traffic: bool = False
    is_crossing: bool = False


def build_invented_network(nodes: list[InventedNode], ways: list[InventedWay]) -> RouteNetworkArrays:
    """Build the arrays the data layer reads, from invented nodes and ways."""
    ordered_nodes = sorted(nodes, key=lambda node: node.id)
    ordered_ways = sorted(ways, key=lambda way: way.id)
    counts = [len(way.node_ids) for way in ordered_ways]
    return RouteNetworkArrays(
        way_ids=np.asarray([way.id for way in ordered_ways], dtype=np.int64),
        way_states=np.asarray([[WAY_BARRIER_STATES.index(state) for state in (way.stairs, way.poor_surface, way.steep_incline, way.narrow_passage)] for way in ordered_ways], dtype=np.int8).reshape(
            -1, 4
        ),
        way_flags=np.asarray([(way.is_marked_wheelchair_no, way.is_motor_traffic, way.is_crossing) for way in ordered_ways], dtype=np.bool_).reshape(-1, 3),
        way_node_offsets=np.concatenate(([0], np.cumsum(counts))).astype(np.int64),
        way_node_ids=np.asarray([node_id for way in ordered_ways for node_id in way.node_ids], dtype=np.int64),
        node_ids=np.asarray([node.id for node in ordered_nodes], dtype=np.int64),
        node_lon=np.asarray([node.lon for node in ordered_nodes], dtype=np.float64),
        node_lat=np.asarray([node.lat for node in ordered_nodes], dtype=np.float64),
        node_kerb=np.asarray([NO_KERB_POINT if node.kerb is None else KERB_POINT_STATES.index(node.kerb) for node in ordered_nodes], dtype=np.int8),
        node_is_crossing=np.asarray([node.is_crossing for node in ordered_nodes], dtype=np.bool_),
        node_is_on_motor_traffic_way=np.asarray([node.is_on_motor_traffic_way for node in ordered_nodes], dtype=np.bool_),
    )


def build_encoded_polyline(points: list[tuple[float, float]]) -> str:
    """Encode longitude and latitude pairs as a polyline of precision 6, the inverse of the decoder of the route."""
    encoded: list[str] = []
    previous_lat = previous_lon = 0
    for lon, lat in points:
        lat_value, lon_value = round(lat * 1_000_000), round(lon * 1_000_000)
        for delta in (lat_value - previous_lat, lon_value - previous_lon):
            value = ~(delta << 1) if delta < 0 else delta << 1
            while value >= 0x20:
                encoded.append(chr((0x20 | (value & 0x1F)) + 63))
                value >>= 5
            encoded.append(chr(value + 63))
        previous_lat, previous_lon = lat_value, lon_value
    return "".join(encoded)


def build_invented_trace(nodes: dict[int, InventedNode], edges: list[tuple[int, list[int]]]) -> ValhallaTrace:
    """Build a traced route walking along the given ways through the given node identities, one edge per way and node list."""
    points: list[tuple[float, float]] = []
    trace_edges: list[ValhallaEdge] = []
    for way_id, node_ids in edges:
        begin = max(len(points) - 1, 0)
        for index, node_id in enumerate(node_ids):
            if points and index == 0:
                continue
            points.append((nodes[node_id].lon, nodes[node_id].lat))
        trace_edges.append(ValhallaEdge(way_id, node_ids[0], node_ids[-1], begin, len(points) - 1))
    return ValhallaTrace(build_encoded_polyline(points), tuple(trace_edges))


def build_invented_fact(
    fact_id: int,
    fact_type: FactType,
    node: InventedNode,
    source: FactSource = FactSource.USER_REPORT,
    osm_element: tuple[OsmElementType, int] | None = None,
    nearest_way_id: int | None = None,
    geozone_radius_m: int | None = None,
    east_shift_m: float = 0.0,
    north_shift_m: float = 0.0,
) -> StoredRouteFact:
    """Build a stored fact at a node of an invented network, shifted by the given metres."""
    point = InventedNode(0, node.east_m + east_shift_m, node.north_m + north_shift_m)
    return StoredRouteFact(
        id=fact_id,
        fact_type=fact_type,
        source=source,
        lat=point.lat,
        lon=point.lon,
        geozone_radius_m=geozone_radius_m,
        description=None,
        step_count=None,
        is_sample=False,
        osm_element_type=None if osm_element is None else osm_element[0],
        osm_element_id=None if osm_element is None else osm_element[1],
        osm_edited_on=None if osm_element is None else datetime(2026, 9, 14, tzinfo=UTC).date(),
        is_removed_from_osm=False,
        nearest_way_id=nearest_way_id,
    )


def build_invented_view(fact: StoredRouteFact, status: FactStatus = FactStatus.UNVERIFIED, confirmations: float = 0.0, denials: float = 0.0) -> FactView:
    """Pair an invented fact with a status, as if derived from its votes."""
    return FactView(fact, FactStatusResult(status, confirmations, denials, None))
