"""Read the pedestrian network seeded in a rolled-back transaction of the local database of db/ into the arrays of the route graph."""

import numpy as np
import pytest
from sqlalchemy import text

from data.route_network import KERB_POINT_STATES, NO_KERB_POINT, WAY_BARRIER_STATES, fetch_route_network

pytestmark = pytest.mark.critical

FIRST_WAY_ID = 9100000001
SECOND_WAY_ID = 9100000002
NODES = {
    9100000011: (19.9301, 50.0601, "lowered", False, True),
    9100000012: (19.9311, 50.0601, None, True, True),
    9100000013: (19.9321, 50.0601, None, False, False),
    9100000014: (19.9311, 50.0611, "high", False, False),
}
INSERT_NODE_SQL = text("INSERT INTO osm_node (id, geog, kerb_point, is_crossing, is_on_motor_traffic_way) VALUES (:id, ST_GeogFromText(:point), :kerb_point, :is_crossing, :is_on_motor_traffic_way)")
INSERT_WAY_SQL = text(
    "INSERT INTO osm_way (id, geog, stairs_state, poor_surface_state, steep_incline_state, narrow_passage_state, is_marked_wheelchair_no, is_motor_traffic, is_crossing) "
    "VALUES (:id, ST_GeogFromText(:line), :stairs, :surface, :incline, :width, :wheelchair_no, :motor, :crossing)"
)
INSERT_WAY_NODE_SQL = text("INSERT INTO osm_way_node (way_id, sequence_index, node_id) VALUES (:way_id, :sequence_index, :node_id)")


def build_line(node_ids: list[int]) -> str:
    """Write the line through the given invented nodes as EWKT."""
    return "SRID=4326;LINESTRING(" + ", ".join(f"{NODES[node][0]} {NODES[node][1]}" for node in node_ids) + ")"


def test_two_ways_sharing_a_node_are_read_in_order_with_their_states_flags_and_coordinates(service_transaction):
    """Seed two invented ways sharing one node and read them back with their ordered nodes, barrier states, flags and node attributes."""
    for node_id, (lon, lat, kerb, crossing, motor) in NODES.items():
        service_transaction.execute(INSERT_NODE_SQL, {"id": node_id, "point": f"SRID=4326;POINT({lon} {lat})", "kerb_point": kerb, "is_crossing": crossing, "is_on_motor_traffic_way": motor})
    ways = {
        FIRST_WAY_ID: ([9100000011, 9100000012, 9100000013], ("present", "absent", "unknown", "absent"), (False, True, False)),
        SECOND_WAY_ID: ([9100000014, 9100000012], ("absent_by_default", "present", "absent", "unknown"), (True, False, True)),
    }
    for way_id, (node_ids, (stairs, surface, incline, width), (wheelchair_no, motor, crossing)) in ways.items():
        service_transaction.execute(
            INSERT_WAY_SQL,
            {
                "id": way_id,
                "line": build_line(node_ids),
                "stairs": stairs,
                "surface": surface,
                "incline": incline,
                "width": width,
                "wheelchair_no": wheelchair_no,
                "motor": motor,
                "crossing": crossing,
            },
        )
        for sequence_index, node_id in enumerate(node_ids):
            service_transaction.execute(INSERT_WAY_NODE_SQL, {"way_id": way_id, "sequence_index": sequence_index, "node_id": node_id})

    network = fetch_route_network(service_transaction)

    assert np.all(np.diff(network.way_ids) > 0)
    assert np.all(np.diff(network.node_ids) > 0)
    for way_id, (node_ids, states, flags) in ways.items():
        row = int(np.searchsorted(network.way_ids, way_id))
        assert network.way_ids[row] == way_id
        assert network.way_node_ids[network.way_node_offsets[row] : network.way_node_offsets[row + 1]].tolist() == node_ids
        assert [WAY_BARRIER_STATES[index].value for index in network.way_states[row]] == list(states)
        assert tuple(bool(flag) for flag in network.way_flags[row]) == flags
    for node_id, (lon, lat, kerb, crossing, motor) in NODES.items():
        row = int(np.searchsorted(network.node_ids, node_id))
        assert network.node_ids[row] == node_id
        assert (network.node_lon[row], network.node_lat[row]) == pytest.approx((lon, lat), abs=1e-9)
        expected_kerb = NO_KERB_POINT if kerb is None else [state.value for state in KERB_POINT_STATES].index(kerb)
        assert network.node_kerb[row] == expected_kerb
        assert (bool(network.node_is_crossing[row]), bool(network.node_is_on_motor_traffic_way[row])) == (crossing, motor)


def test_reading_the_network_leaves_the_connection_able_to_write(service_transaction):
    """Read the network and then write on the same connection, which fails when the streaming of the reads leaks into the options of the connection."""
    node_id, (lon, lat, kerb, crossing, motor) = next(iter(NODES.items()))

    fetch_route_network(service_transaction)

    assert "yield_per" not in service_transaction.get_execution_options()
    written = service_transaction.execute(
        text(INSERT_NODE_SQL.text + " RETURNING id"), {"id": node_id, "point": f"SRID=4326;POINT({lon} {lat})", "kerb_point": kerb, "is_crossing": crossing, "is_on_motor_traffic_way": motor}
    ).scalar_one()
    assert written == node_id
