"""Prepare the approved pedestrian network from complete source snapshots."""

from collections.abc import Iterable
from dataclasses import dataclass, replace

from shapely import from_wkb
from shapely.errors import GEOSException
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from shapely.ops import unary_union

from data.osm_reader import OsmElementSnapshot
from service.osm_geometry import OsmGeometryError, resolve_osm_element_coverage
from service.osm_routing_tags import build_osm_routing_node_tags, build_osm_routing_way_tags
from service.osm_tag_rule import resolve_is_pedestrian_network_way

OSM_KRAKOW_RELATION_ID = 449696


@dataclass(frozen=True)
class OsmPreparedNetwork:
    """Keep original selected snapshots for storage and subsequent routing normalization."""

    nodes: tuple[OsmElementSnapshot, ...]
    ways: tuple[OsmElementSnapshot, ...]


def build_osm_boundary(elements: Iterable[OsmElementSnapshot]) -> Polygon | MultiPolygon:
    """Require Kraków's assembled boundary and every referenced ring way."""
    relation = None
    area = None
    ways = {}
    for element in elements:
        if element.element_type == "way" and element.area_wkb is None:
            ways[element.element_id] = element
        elif element.element_type == "relation" and element.element_id == OSM_KRAKOW_RELATION_ID:
            if element.area_wkb is None:
                if relation is not None:
                    raise OsmGeometryError("Duplicate administrative boundary relation")
                relation = element
            else:
                if area is not None:
                    raise OsmGeometryError("Duplicate assembled administrative boundary")
                area = element
    if relation is None or area is None or area.area_wkb is None:
        raise OsmGeometryError("Missing complete administrative boundary")
    ring_geometry = build_osm_boundary_rings(relation, ways)
    try:
        boundary = from_wkb(area.area_wkb)
    except GEOSException as error:
        raise OsmGeometryError("Cannot read administrative boundary geometry") from error
    if not isinstance(boundary, (Polygon, MultiPolygon)) or boundary.is_empty or not boundary.is_valid:
        raise OsmGeometryError("Invalid administrative boundary geometry")
    if not boundary.boundary.equals(ring_geometry):
        raise OsmGeometryError("Assembled boundary omits or changes a ring")
    return boundary


def build_osm_network(elements: Iterable[OsmElementSnapshot], boundary: Polygon | MultiPolygon) -> OsmPreparedNetwork:
    """Select whole permitted ways and keep all their original referenced nodes."""
    nodes = {}
    selected = {}
    for element in elements:
        if element.element_type == "node":
            if element.element_id in nodes:
                raise OsmGeometryError("Duplicate source node identity")
            nodes[element.element_id] = element
        elif element.element_type == "way" and element.area_wkb is None and resolve_is_pedestrian_network_way(element.tags):
            if len(element.node_ids) < 2 or len(element.node_ids) != len(element.coordinates):
                raise OsmGeometryError("Incomplete network way geometry")
            if resolve_osm_element_coverage(boundary, LineString(element.coordinates)):
                if element.element_id in selected:
                    raise OsmGeometryError("Duplicate selected way identity")
                selected[element.element_id] = element
    needed_nodes = {node_id for way in selected.values() for node_id in way.node_ids}
    if not needed_nodes <= nodes.keys():
        raise OsmGeometryError("Missing selected network node")
    for way in selected.values():
        if any(nodes[node_id].coordinates != (coordinate,) for node_id, coordinate in zip(way.node_ids, way.coordinates, strict=True)):
            raise OsmGeometryError("Inconsistent selected network coordinates")
    return OsmPreparedNetwork(tuple(nodes[node_id] for node_id in sorted(needed_nodes)), tuple(selected[way_id] for way_id in sorted(selected)))


def build_osm_routing_network(network: OsmPreparedNetwork) -> OsmPreparedNetwork:
    """Normalize a copy while preserving original source tags for database mapping."""
    return OsmPreparedNetwork(
        tuple(replace(node, tags=build_osm_routing_node_tags(node.tags)) for node in network.nodes),
        tuple(replace(way, tags=build_osm_routing_way_tags(way.tags)) for way in network.ways),
    )


def build_osm_boundary_rings(relation: OsmElementSnapshot, ways: dict[int, OsmElementSnapshot]) -> LineString | MultiLineString:
    """Verify referenced ring connectivity independently of native area assembly."""
    rings = [(ref, role) for kind, ref, role in relation.members if kind == "w" and role in ("", "outer", "inner")]
    if not rings or any(ref not in ways for ref, _ in rings):
        raise OsmGeometryError("Missing administrative boundary ring way")
    if any(kind == "r" and role in ("", "outer", "inner") for kind, _, role in relation.members):
        raise OsmGeometryError("Nested administrative boundary ring is unsupported")
    endpoints: dict[tuple[str, int], int] = {}
    for ref, role in rings:
        way = ways[ref]
        if len(way.node_ids) < 2 or len(way.node_ids) != len(way.coordinates):
            raise OsmGeometryError("Incomplete administrative boundary ring")
        for node_id in (way.node_ids[0], way.node_ids[-1]):
            key = (role or "outer", node_id)
            endpoints[key] = endpoints.get(key, 0) + 1
    if any(count % 2 for count in endpoints.values()):
        raise OsmGeometryError("Open administrative boundary ring")
    geometry = unary_union([LineString(ways[ref].coordinates) for ref, _ in rings])
    if not isinstance(geometry, (LineString, MultiLineString)):
        raise OsmGeometryError("Invalid administrative boundary rings")
    return geometry
