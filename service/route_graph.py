"""Hold the graph of the stretches of the copy in use in the process and find the path with the fewest barriers on it."""

import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from itertools import pairwise

import numpy as np
from pyproj import Transformer
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree
from sqlalchemy import Connection
from sqlalchemy.exc import SQLAlchemyError

from config.logging import fetch_logger
from data.engine import API_STATEMENT_TIMEOUT_MS, apply_statement_timeout, fetch_api_engine, fetch_read_only_snapshot
from data.osm_copy import fetch_current_osm_copy
from data.route_network import RouteNetworkArrays, fetch_route_network
from service.osm_geometry import OSM_CALCULATION_CRS, OSM_STORAGE_CRS

GRAPH_BUILD_STATEMENT_TIMEOUT_MS = 60000
BARRIER_STRETCH_WEIGHT = 1_000_000


@dataclass(frozen=True)
class RoutePoint:
    """A chosen start or destination in degrees of WGS 84."""

    lat: float
    lon: float


@dataclass(frozen=True)
class RouteGraph:
    """
    The stretches of one copy with what never changes for its instant.

    A graph node is a node that ends a way or belongs to two or more of them; a stretch is the part of one way between two
    consecutive graph nodes, kept by its way row, the first and last position of its nodes in that way, its two node rows
    and its length in metres in EPSG:2180. The node coordinates in EPSG:2180 serve every distance of a route, and the
    tree holds the graph nodes of the largest connected part, so a joined point always has a path.
    """

    state_at: datetime
    network: RouteNetworkArrays
    node_x: np.ndarray
    node_y: np.ndarray
    membership_node_rows: np.ndarray
    stretch_way: np.ndarray
    stretch_first: np.ndarray
    stretch_last: np.ndarray
    stretch_from: np.ndarray
    stretch_to: np.ndarray
    stretch_length_m: np.ndarray
    stretch_start_membership: np.ndarray
    graph_index: np.ndarray
    graph_node_rows: np.ndarray
    component_node_rows: np.ndarray
    component_tree: cKDTree


@dataclass(frozen=True)
class FewestBarriersPath:
    """The stretches of the path with the fewest barriers, in order, and the number of barriers it crosses."""

    stretch_ids: tuple[int, ...]
    barrier_count: int


class RouteGraphCache:
    """The one graph of the process and the lock its rebuild holds, so concurrent requests wait instead of building twice."""

    def __init__(self) -> None:
        """Start without a graph."""
        self.graph: RouteGraph | None = None
        self.lock = threading.Lock()


ROUTE_GRAPH_CACHE = RouteGraphCache()


def build_projected_coordinates(lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project longitudes and latitudes of WGS 84 into the metres of EPSG:2180."""
    transformer = Transformer.from_crs(OSM_STORAGE_CRS, OSM_CALCULATION_CRS, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)


def build_route_graph(network: RouteNetworkArrays, state_at: datetime) -> RouteGraph:
    """Build the graph nodes, the stretches with their lengths, the largest connected part and its search tree from one copy."""
    node_x, node_y = build_projected_coordinates(network.node_lon, network.node_lat)
    offsets = network.way_node_offsets
    counts = np.diff(offsets)
    membership_node_rows = np.searchsorted(network.node_ids, network.way_node_ids).astype(np.int64)
    membership_way = np.repeat(np.arange(len(network.way_ids), dtype=np.int64), counts)
    usable = counts >= 2
    is_graph_node = np.bincount(membership_node_rows, minlength=len(network.node_ids)) >= 2
    ends = np.concatenate((offsets[:-1][usable], offsets[1:][usable] - 1))
    is_graph_node[membership_node_rows[ends]] = True
    split = is_graph_node[membership_node_rows]
    split_positions = np.flatnonzero(split)
    same_way = membership_way[split_positions[:-1]] == membership_way[split_positions[1:]]
    stretch_start = split_positions[:-1][same_way]
    stretch_end = split_positions[1:][same_way]
    step = np.hypot(np.diff(node_x[membership_node_rows]), np.diff(node_y[membership_node_rows]))
    step[membership_way[:-1] != membership_way[1:]] = 0.0
    cumulative = np.concatenate(([0.0], np.cumsum(step)))
    stretch_way = membership_way[stretch_start]
    graph_node_rows = np.flatnonzero(is_graph_node)
    graph_index = np.full(len(network.node_ids), -1, dtype=np.int64)
    graph_index[graph_node_rows] = np.arange(len(graph_node_rows), dtype=np.int64)
    stretch_from = membership_node_rows[stretch_start]
    stretch_to = membership_node_rows[stretch_end]
    adjacency = csr_matrix((np.ones(len(stretch_start)), (graph_index[stretch_from], graph_index[stretch_to])), shape=(len(graph_node_rows), len(graph_node_rows)))
    component_count, labels = connected_components(adjacency, directed=False)
    largest = np.argmax(np.bincount(labels)) if component_count else 0
    component_node_rows = graph_node_rows[labels == largest] if component_count else graph_node_rows
    return RouteGraph(
        state_at=state_at,
        network=network,
        node_x=node_x,
        node_y=node_y,
        membership_node_rows=membership_node_rows,
        stretch_way=stretch_way,
        stretch_first=stretch_start - offsets[stretch_way],
        stretch_last=stretch_end - offsets[stretch_way],
        stretch_from=stretch_from,
        stretch_to=stretch_to,
        stretch_length_m=cumulative[stretch_end] - cumulative[stretch_start],
        stretch_start_membership=stretch_start,
        graph_index=graph_index,
        graph_node_rows=graph_node_rows,
        component_node_rows=component_node_rows,
        component_tree=cKDTree(np.column_stack((node_x[component_node_rows], node_y[component_node_rows]))),
    )


def build_way_row(graph: RouteGraph, way_id: int) -> int | None:
    """Give the row of a way of the copy, or none when the copy does not hold it."""
    row = int(np.searchsorted(graph.network.way_ids, way_id))
    return row if row < len(graph.network.way_ids) and graph.network.way_ids[row] == way_id else None


def build_node_row(graph: RouteGraph, node_id: int) -> int | None:
    """Give the row of a node of the copy, or none when the copy does not hold it."""
    row = int(np.searchsorted(graph.network.node_ids, node_id))
    return row if row < len(graph.network.node_ids) and graph.network.node_ids[row] == node_id else None


def build_way_node_rows(graph: RouteGraph, way_row: int) -> np.ndarray:
    """Give the node rows of a way in their order."""
    offsets = graph.network.way_node_offsets
    return graph.membership_node_rows[offsets[way_row] : offsets[way_row + 1]]


def build_way_stretch_ids(graph: RouteGraph, way_row: int) -> np.ndarray:
    """Give the stretches of a way in their order."""
    return np.arange(*build_way_stretch_range(graph, way_row))


def build_way_stretch_range(graph: RouteGraph, way_row: int) -> tuple[int, int]:
    """Give the first stretch of a way and the stretch after its last, as the stretches are stored in way order."""
    return int(np.searchsorted(graph.stretch_way, way_row, side="left")), int(np.searchsorted(graph.stretch_way, way_row, side="right"))


def build_stretch_of_position(graph: RouteGraph, way_row: int, first: int, last: int) -> int | None:
    """Give the stretch of a way that holds the positions from first to last, or none when they span more than one."""
    low, high = min(first, last), max(first, last)
    start, end = build_way_stretch_range(graph, way_row)
    index = start + int(np.searchsorted(graph.stretch_first[start:end], low, side="right")) - 1
    if index < start or index >= end or graph.stretch_last[index] < high:
        return None
    return index


def build_stretch_node_rows(graph: RouteGraph, stretch_id: int) -> np.ndarray:
    """Give the node rows of a stretch in the order of its way."""
    rows = build_way_node_rows(graph, int(graph.stretch_way[stretch_id]))
    return rows[int(graph.stretch_first[stretch_id]) : int(graph.stretch_last[stretch_id]) + 1]


def build_stretch_coordinates(graph: RouteGraph, stretch_id: int) -> np.ndarray:
    """Give the coordinates of a stretch in EPSG:2180, one row per node."""
    rows = build_stretch_node_rows(graph, stretch_id)
    return np.column_stack((graph.node_x[rows], graph.node_y[rows]))


def build_node_stretch_ids(graph: RouteGraph, node_row: int) -> tuple[int, ...]:
    """Give every stretch that holds a node, its two end nodes included."""
    memberships = np.flatnonzero(graph.membership_node_rows == node_row)
    stretch_ids: set[int] = set()
    offsets = graph.network.way_node_offsets
    for membership in memberships:
        way_row = int(np.searchsorted(offsets, membership, side="right") - 1)
        position = int(membership - offsets[way_row])
        start, end = build_way_stretch_range(graph, way_row)
        for stretch_id in range(start, end):
            if graph.stretch_first[stretch_id] <= position <= graph.stretch_last[stretch_id]:
                stretch_ids.add(stretch_id)
    return tuple(sorted(stretch_ids))


def build_nearest_component_node(graph: RouteGraph, point: RoutePoint) -> int:
    """Give the node row of the graph node of the largest connected part nearest to a point."""
    x, y = build_projected_coordinates(np.asarray([point.lon]), np.asarray([point.lat]))
    _distance, index = graph.component_tree.query((x[0], y[0]))
    return int(graph.component_node_rows[int(index)])


def resolve_fewest_barriers_path(graph: RouteGraph, start: RoutePoint, destination: RoutePoint, barrier_counts: Mapping[int, int]) -> FewestBarriersPath:
    """
    Find the path with the fewest barriers between the graph nodes nearest to two points.

    The weight of a stretch is its count of barriers times 1 000 000 plus its length, so the path crosses the fewest
    stretches with a barrier and, among those, is the shortest. Of parallel stretches between the same two graph nodes
    the lightest one is taken.
    """
    counts = np.zeros(len(graph.stretch_way), dtype=np.float64)
    for stretch_id, count in barrier_counts.items():
        counts[stretch_id] = count
    weights = counts * BARRIER_STRETCH_WEIGHT + graph.stretch_length_m
    source = graph.graph_index[graph.stretch_from]
    target = graph.graph_index[graph.stretch_to]
    low, high = np.minimum(source, target), np.maximum(source, target)
    node_count = len(graph.graph_node_rows)
    keys = low * node_count + high
    candidates = np.flatnonzero(low != high)
    order = candidates[np.lexsort((weights[candidates], keys[candidates]))]
    unique_keys, first = np.unique(keys[order], return_index=True)
    chosen = order[first]
    matrix = csr_matrix((weights[chosen] + 1e-9, (low[chosen], high[chosen])), shape=(node_count, node_count))
    origin = int(graph.graph_index[build_nearest_component_node(graph, start)])
    goal = int(graph.graph_index[build_nearest_component_node(graph, destination)])
    _distances, predecessors = dijkstra(matrix, directed=False, indices=origin, return_predecessors=True)
    path = [goal]
    while path[-1] != origin:
        previous = int(predecessors[path[-1]])
        if previous < 0:
            raise ValueError("No path joins the two points in the graph")
        path.append(previous)
    path.reverse()
    stretch_ids = []
    for here, there in pairwise(path):
        key = min(here, there) * node_count + max(here, there)
        stretch_ids.append(int(chosen[int(np.searchsorted(unique_keys, key))]))
    return FewestBarriersPath(tuple(stretch_ids), int(sum(counts[stretch_id] for stretch_id in stretch_ids)))


def fetch_route_graph(connection: Connection, state_at: datetime) -> RouteGraph:
    """
    Give the graph of the copy whose instant is state_at, rebuilding it inside the snapshot of the request when it is of another copy.

    The rebuild holds the lock of the process and the longer statement limit of a build, and a failed build is never kept.
    """
    graph = ROUTE_GRAPH_CACHE.graph
    if graph is not None and graph.state_at == state_at:
        return graph
    with ROUTE_GRAPH_CACHE.lock:
        graph = ROUTE_GRAPH_CACHE.graph
        if graph is not None and graph.state_at == state_at:
            return graph
        apply_statement_timeout(connection, GRAPH_BUILD_STATEMENT_TIMEOUT_MS)
        graph = build_route_graph(fetch_route_network(connection), state_at)
        apply_statement_timeout(connection, API_STATEMENT_TIMEOUT_MS)
        ROUTE_GRAPH_CACHE.graph = graph
        return graph


def build_route_graph_at_start() -> None:
    """Build the graph of the copy in use when the process starts, logging at INFO when there is no copy and at WARNING when the database refuses."""
    logger = fetch_logger(__name__)
    try:
        with fetch_read_only_snapshot(fetch_api_engine()) as connection:
            copy = fetch_current_osm_copy(connection)
            if copy is None:
                logger.info("No OpenStreetMap copy is in use, so the route graph waits for the first route request")
                return
            fetch_route_graph(connection, copy.state_at.instant)
    except SQLAlchemyError as error:
        logger.warning("The route graph could not be built at start, so the first route request builds it: %s", type(error).__name__)
