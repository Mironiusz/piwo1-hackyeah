"""Check the graph of the stretches, its cache and the path with the fewest barriers on invented networks."""

from datetime import timedelta

import pytest

from service import route_graph
from service.route_graph import RouteGraphCache, RoutePoint, build_route_graph, build_way_row, fetch_route_graph, resolve_fewest_barriers_path
from tests.common_route_network import INVENTED_STATE_AT, InventedNode, InventedWay, build_invented_network

NODES = [
    InventedNode(1, 0, 0),
    InventedNode(2, 50, 0),
    InventedNode(3, 100, 0),
    InventedNode(4, 150, 0),
    InventedNode(6, 100, 80),
    InventedNode(7, 5000, 5000),
    InventedNode(8, 5050, 5000),
]
WAYS = [InventedWay(100, (1, 2, 3, 4)), InventedWay(200, (3, 6)), InventedWay(300, (7, 8))]


def build_graph():
    """Build the graph of the invented network of this module."""
    return build_route_graph(build_invented_network(NODES, WAYS), INVENTED_STATE_AT)


def test_graph_nodes_are_way_ends_and_shared_nodes() -> None:
    """Make every way end and the node shared by two ways a graph node, and nothing else."""
    graph = build_graph()
    graph_node_ids = {int(graph.network.node_ids[row]) for row in graph.graph_node_rows}
    assert graph_node_ids == {1, 3, 4, 6, 7, 8}


def test_stretch_keeps_its_way_and_positions() -> None:
    """Split way 100 at the shared node into two stretches that keep their way and positions, with lengths in metres."""
    graph = build_graph()
    way_row = build_way_row(graph, 100)
    stretches = [(int(graph.stretch_first[index]), int(graph.stretch_last[index])) for index in range(len(graph.stretch_way)) if graph.stretch_way[index] == way_row]
    assert stretches == [(0, 2), (2, 3)]
    lengths = [round(float(graph.stretch_length_m[index])) for index in range(len(graph.stretch_way)) if graph.stretch_way[index] == way_row]
    assert lengths == [100, 50]


def test_isolated_piece_is_out_of_the_largest_part() -> None:
    """Leave the far away way 300 out of the part a point is joined to."""
    graph = build_graph()
    component_ids = {int(graph.network.node_ids[row]) for row in graph.component_node_rows}
    assert component_ids == {1, 3, 4, 6}


def test_cache_is_rebuilt_only_when_the_instant_changes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build once per instant, rebuild for a new instant, and keep no graph from a failed build."""
    builds: list[int] = []

    def fetch_invented_network(_connection):
        """Count the reads of the network."""
        builds.append(1)
        return build_invented_network(NODES, WAYS)

    monkeypatch.setattr(route_graph, "ROUTE_GRAPH_CACHE", RouteGraphCache())
    monkeypatch.setattr(route_graph, "fetch_route_network", fetch_invented_network)
    monkeypatch.setattr(route_graph, "apply_statement_timeout", lambda _connection, _milliseconds: None)
    first = fetch_route_graph(None, INVENTED_STATE_AT)
    assert fetch_route_graph(None, INVENTED_STATE_AT) is first
    assert len(builds) == 1
    later = INVENTED_STATE_AT + timedelta(days=1)
    assert fetch_route_graph(None, later).state_at == later
    assert len(builds) == 2

    def fetch_failing_network(_connection):
        """Fail the read of the network."""
        raise RuntimeError("invented failure")

    monkeypatch.setattr(route_graph, "fetch_route_network", fetch_failing_network)
    with pytest.raises(RuntimeError):
        fetch_route_graph(None, later + timedelta(days=1))
    assert route_graph.ROUTE_GRAPH_CACHE.graph is not None
    assert route_graph.ROUTE_GRAPH_CACHE.graph.state_at == later


def build_parallel_graph():
    """Build three ways between A and B with a middle node each, and a short barrier-free bypass of the third."""
    nodes = [
        InventedNode(1, 0, 0),
        InventedNode(2, 400, 0),
        InventedNode(11, 200, 100),
        InventedNode(12, 200, 200),
        InventedNode(13, 200, 300),
    ]
    ways = [InventedWay(10, (1, 11, 2)), InventedWay(20, (1, 12, 2)), InventedWay(30, (1, 13, 2))]
    return build_route_graph(build_invented_network(nodes, ways), INVENTED_STATE_AT), nodes


def test_fewest_barriers_path_crosses_the_stairs_of_one() -> None:
    """Cross the way with 1 barrier among ways with 1, 2 and 4 known barriers (AC-5)."""
    graph, nodes = build_parallel_graph()
    counts = {}
    for way_id, count in ((10, 2), (20, 4), (30, 1)):
        row = build_way_row(graph, way_id)
        counts[next(index for index in range(len(graph.stretch_way)) if graph.stretch_way[index] == row)] = count
    path = resolve_fewest_barriers_path(graph, RoutePoint(nodes[0].lat, nodes[0].lon), RoutePoint(nodes[1].lat, nodes[1].lon), counts)
    assert path.barrier_count == 1
    assert [int(graph.network.way_ids[graph.stretch_way[stretch]]) for stretch in path.stretch_ids] == [30]


def test_fewest_barriers_path_takes_the_shorter_of_two_free_paths() -> None:
    """Take the shortest way when no path crosses a barrier."""
    graph, nodes = build_parallel_graph()
    path = resolve_fewest_barriers_path(graph, RoutePoint(nodes[0].lat, nodes[0].lon), RoutePoint(nodes[1].lat, nodes[1].lon), {})
    assert path.barrier_count == 0
    assert [int(graph.network.way_ids[graph.stretch_way[stretch]]) for stretch in path.stretch_ids] == [10]
