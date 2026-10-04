"""Read the pedestrian network of the copy in use into compact arrays for the graph of the route with the fewest barriers."""

from dataclasses import dataclass
from typing import cast

import numpy as np
from accessibility_db.closed_lists import KerbPointState, WayBarrierState
from accessibility_db.tables import OsmNode, OsmWay, OsmWayNode
from sqlalchemy import Connection, Float, Table, func, select

NETWORK_PARTITION_ROWS = 100000
WAY_BARRIER_STATES = (WayBarrierState.PRESENT, WayBarrierState.ABSENT, WayBarrierState.ABSENT_BY_DEFAULT, WayBarrierState.UNKNOWN)
WAY_BARRIER_COLUMNS = ("stairs_state", "poor_surface_state", "steep_incline_state", "narrow_passage_state")
KERB_POINT_STATES = (KerbPointState.HIGH, KerbPointState.LOWERED, KerbPointState.UNKNOWN)
NO_KERB_POINT = -1

_way = cast(Table, OsmWay.__table__)
_node = cast(Table, OsmNode.__table__)
_membership = cast(Table, OsmWayNode.__table__)

FETCH_ROUTE_WAYS_SQL = (
    select(_way.c.id, *(_way.c[name] for name in WAY_BARRIER_COLUMNS), _way.c.is_marked_wheelchair_no, _way.c.is_motor_traffic, _way.c.is_crossing)
    .order_by(_way.c.id)
    .execution_options(yield_per=NETWORK_PARTITION_ROWS)
)
FETCH_ROUTE_WAY_NODES_SQL = select(_membership.c.way_id, _membership.c.node_id).order_by(_membership.c.way_id, _membership.c.sequence_index).execution_options(yield_per=NETWORK_PARTITION_ROWS)
FETCH_ROUTE_NODES_SQL = (
    select(
        _node.c.id,
        func.ST_X(func.geometry(_node.c.geog), type_=Float).label("lon"),
        func.ST_Y(func.geometry(_node.c.geog), type_=Float).label("lat"),
        _node.c.kerb_point,
        _node.c.is_crossing,
        _node.c.is_on_motor_traffic_way,
    )
    .order_by(_node.c.id)
    .execution_options(yield_per=NETWORK_PARTITION_ROWS)
)


@dataclass(frozen=True)
class RouteNetworkArrays:
    """
    The ways, their ordered nodes and the nodes of one copy as arrays.

    The ways are sorted by identity; `way_states` holds for each way the index into WAY_BARRIER_STATES of its stairs, poor
    surface, steep incline and narrow passage, and `way_flags` its marking `wheelchair=no`, motor traffic and crossing. The
    nodes of way i are `way_node_ids[way_node_offsets[i]:way_node_offsets[i + 1]]` in their order. The nodes are sorted by
    identity, with longitude and latitude, the index of their kerb point into KERB_POINT_STATES or NO_KERB_POINT, and
    their crossing and motor traffic flags.
    """

    way_ids: np.ndarray
    way_states: np.ndarray
    way_flags: np.ndarray
    way_node_offsets: np.ndarray
    way_node_ids: np.ndarray
    node_ids: np.ndarray
    node_lon: np.ndarray
    node_lat: np.ndarray
    node_kerb: np.ndarray
    node_is_crossing: np.ndarray
    node_is_on_motor_traffic_way: np.ndarray


def fetch_route_network(connection: Connection) -> RouteNetworkArrays:
    """Read every way, its nodes in order and every node of the copy in partitions, inside the transaction of the caller; only these three reads stream, so the options of the connection stay as the caller set them."""
    way_ids: list[int] = []
    way_states: list[tuple[int, int, int, int]] = []
    way_flags: list[tuple[bool, bool, bool]] = []
    state_index = {state.value: index for index, state in enumerate(WAY_BARRIER_STATES)}
    for partition in connection.execute(FETCH_ROUTE_WAYS_SQL).mappings().partitions():
        for row in partition:
            way_ids.append(row["id"])
            way_states.append(cast(tuple[int, int, int, int], tuple(state_index[WayBarrierState(row[name]).value] for name in WAY_BARRIER_COLUMNS)))
            way_flags.append((row["is_marked_wheelchair_no"], row["is_motor_traffic"], row["is_crossing"]))
    membership_way_ids: list[int] = []
    membership_node_ids: list[int] = []
    for partition in connection.execute(FETCH_ROUTE_WAY_NODES_SQL).mappings().partitions():
        for row in partition:
            membership_way_ids.append(row["way_id"])
            membership_node_ids.append(row["node_id"])
    node_ids: list[int] = []
    node_lon: list[float] = []
    node_lat: list[float] = []
    node_kerb: list[int] = []
    node_is_crossing: list[bool] = []
    node_is_on_motor_traffic_way: list[bool] = []
    kerb_index = {state.value: index for index, state in enumerate(KERB_POINT_STATES)}
    for partition in connection.execute(FETCH_ROUTE_NODES_SQL).mappings().partitions():
        for row in partition:
            node_ids.append(row["id"])
            node_lon.append(row["lon"])
            node_lat.append(row["lat"])
            node_kerb.append(NO_KERB_POINT if row["kerb_point"] is None else kerb_index[KerbPointState(row["kerb_point"]).value])
            node_is_crossing.append(row["is_crossing"])
            node_is_on_motor_traffic_way.append(row["is_on_motor_traffic_way"])
    sorted_way_ids = np.asarray(way_ids, dtype=np.int64)
    membership_ways = np.asarray(membership_way_ids, dtype=np.int64)
    counts = np.bincount(np.searchsorted(sorted_way_ids, membership_ways), minlength=len(sorted_way_ids)) if len(membership_ways) else np.zeros(len(sorted_way_ids), dtype=np.int64)
    return RouteNetworkArrays(
        way_ids=sorted_way_ids,
        way_states=np.asarray(way_states, dtype=np.int8).reshape(-1, len(WAY_BARRIER_COLUMNS)),
        way_flags=np.asarray(way_flags, dtype=np.bool_).reshape(-1, 3),
        way_node_offsets=np.concatenate(([0], np.cumsum(counts))).astype(np.int64),
        way_node_ids=np.asarray(membership_node_ids, dtype=np.int64),
        node_ids=np.asarray(node_ids, dtype=np.int64),
        node_lon=np.asarray(node_lon, dtype=np.float64),
        node_lat=np.asarray(node_lat, dtype=np.float64),
        node_kerb=np.asarray(node_kerb, dtype=np.int8),
        node_is_crossing=np.asarray(node_is_crossing, dtype=np.bool_),
        node_is_on_motor_traffic_way=np.asarray(node_is_on_motor_traffic_way, dtype=np.bool_),
    )
