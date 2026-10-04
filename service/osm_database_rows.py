"""Map original selected network snapshots onto the delivered database contract."""

from accessibility_db.closed_lists import KerbPointState, WayBarrierState
from shapely.geometry import LineString, Point

from data.osm_copy import OsmMembershipRow, OsmNodeRow, OsmWayRow
from service.osm_preparation import OsmPreparedNetwork
from service.osm_tag_rule import resolve_node_facts, resolve_way_facts


def build_osm_database_network(network: OsmPreparedNetwork, motor_traffic_node_ids: frozenset[int]) -> tuple[tuple[OsmNodeRow, ...], tuple[OsmWayRow, ...], tuple[OsmMembershipRow, ...]]:
    """Preserve original tags and ordered references, using motor membership from the whole source."""
    nodes = []
    ways = []
    memberships: list[OsmMembershipRow] = []
    for node in network.nodes:
        facts = resolve_node_facts(node.tags, node.element_id in motor_traffic_node_ids)
        nodes.append(
            OsmNodeRow(
                node.element_id, f"SRID=4326;{Point(node.coordinates[0]).wkt}", None if facts.kerb_point is None else KerbPointState(facts.kerb_point), facts.is_crossing, facts.is_on_motor_traffic_way
            )
        )
    for way in network.ways:
        way_facts = resolve_way_facts(way.tags)
        ways.append(
            OsmWayRow(
                way.element_id,
                f"SRID=4326;{LineString(way.coordinates).wkt}",
                WayBarrierState(way_facts.stairs_state),
                WayBarrierState(way_facts.poor_surface_state),
                WayBarrierState(way_facts.steep_incline_state),
                WayBarrierState(way_facts.narrow_passage_state),
                way_facts.is_marked_wheelchair_no,
                way_facts.is_motor_traffic,
                way_facts.is_crossing,
            )
        )
        memberships.extend(OsmMembershipRow(way.element_id, index, node_id) for index, node_id in enumerate(way.node_ids))
    return tuple(nodes), tuple(ways), tuple(memberships)
