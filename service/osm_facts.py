"""Derive the present OpenStreetMap facts of one copy under M6 and the mapping decisions of the importer plan."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from accessibility_db.closed_lists import FactType, OsmElementType
from shapely import from_wkb
from shapely.errors import GEOSException
from shapely.geometry import LineString, MultiPolygon, Point, Polygon

from data.osm_copy import OsmFactIdentity, OsmPresentFact
from data.osm_reader import OsmElementSnapshot
from service import osm_tag_thresholds as thresholds
from service.osm_geometry import OsmGeometryError, resolve_osm_element_coverage, resolve_osm_fact_location
from service.osm_preparation import OsmPreparedNetwork
from service.osm_tag_rule import resolve_node_facts, resolve_osm_amenity_states, resolve_way_facts


@dataclass(frozen=True)
class OsmFactData:
    """Keep the present facts of a copy together with the node membership the network rows need."""

    facts: tuple[OsmPresentFact, ...]
    motor_traffic_node_ids: frozenset[int]


@dataclass
class OsmFactCandidate:
    """Collect the fact types, step count and geometry of one element identity before its location is computed."""

    element_type: Literal["node", "way", "relation"]
    element_id: int
    edited_at: datetime
    fact_types: set[str] = field(default_factory=set)
    step_count: int | None = None
    geometry: Point | LineString | Polygon | MultiPolygon | None = None


def build_osm_present_amenities(tags: Mapping[str, str], element_type: Literal["node", "way", "relation"]) -> frozenset[str]:
    """Return the amenity types that an element's own tags make present."""
    return frozenset(kind for kind, state in resolve_osm_amenity_states(tags, element_type).items() if state == "present")


def build_osm_line(element: OsmElementSnapshot) -> LineString:
    """Build the line of a way, refusing one that cannot give a location."""
    if len(element.coordinates) < 2:
        raise OsmGeometryError("Way fact has no usable line geometry")
    return LineString(element.coordinates)


def build_osm_area(element: OsmElementSnapshot) -> Polygon | MultiPolygon:
    """Read the assembled area of an element, refusing an unreadable or non-areal geometry."""
    if element.area_wkb is None:
        raise OsmGeometryError("Missing assembled area geometry")
    try:
        area = from_wkb(element.area_wkb)
    except GEOSException as error:
        raise OsmGeometryError("Cannot read assembled area geometry") from error
    if not isinstance(area, (Polygon, MultiPolygon)):
        raise OsmGeometryError("Assembled area is not a polygon")
    return area


def build_osm_way_is_covered(boundary: Polygon | MultiPolygon, element: OsmElementSnapshot) -> bool:
    """Apply the whole-way coverage rule to a way's own coordinates, with no coordinate meaning outside the copy."""
    if not element.coordinates:
        return False
    if len(element.coordinates) == 1:
        return resolve_osm_element_coverage(boundary, Point(element.coordinates[0]))
    return resolve_osm_element_coverage(boundary, LineString(element.coordinates))


@dataclass
class OsmSourceScan:
    """Hold what one pass over the complete source collects for the facts of a copy."""

    motor_traffic_node_ids: set[int] = field(default_factory=set)
    covered_way_ids: set[int] = field(default_factory=set)
    relation_way_members: dict[int, tuple[int, ...]] = field(default_factory=dict)
    amenity_relation_ids: set[int] = field(default_factory=set)
    candidates: dict[tuple[str, int], OsmFactCandidate] = field(default_factory=dict)
    areas: list[OsmElementSnapshot] = field(default_factory=list)


def build_osm_fact_data(elements: Iterable[OsmElementSnapshot], boundary: Polygon | MultiPolygon, network: OsmPreparedNetwork, zone: ZoneInfo) -> OsmFactData:
    """
    Make one pass over the complete source and return the present facts of the copy and the motor-traffic node membership.

    Way barriers come only from network ways and point barriers and kerbs only from network nodes. Amenities come from
    every node, way and assembled area of the copy. One identity gets one location: a node its coordinates, a network
    way or a way without an assembled area half its length, another way with an assembled area or a relation area its
    strict interior. A non-area relation of the copy whose tags make an amenity present has no approved location and
    fails the whole copy.
    """
    scan = build_osm_source_scan(elements, boundary, network)
    scan.candidates.update(build_osm_network_candidates(network, scan.motor_traffic_node_ids))
    network_way_ids = frozenset(way.element_id for way in network.ways)
    for area in scan.areas:
        if resolve_osm_area_is_in_copy(area, scan, network_way_ids):
            candidate = scan.candidates.setdefault((area.element_type, area.element_id), OsmFactCandidate(area.element_type, area.element_id, area.edited_at))
            candidate.fact_types.update(build_osm_present_amenities(area.tags, area.element_type))
            candidate.geometry = build_osm_area(area)
    area_relation_ids = {area.element_id for area in scan.areas if area.element_type == "relation"}
    for relation_id in scan.amenity_relation_ids - area_relation_ids:
        if any(member in scan.covered_way_ids for member in scan.relation_way_members[relation_id]):
            raise OsmGeometryError("Non-area relation fact has no approved location")
    return OsmFactData(build_osm_present_facts(scan.candidates.values(), zone), frozenset(scan.motor_traffic_node_ids))


def build_osm_source_scan(elements: Iterable[OsmElementSnapshot], boundary: Polygon | MultiPolygon, network: OsmPreparedNetwork) -> OsmSourceScan:
    """Collect motor-traffic membership, covered ways, relation members, amenity areas and the amenities of elements off the network."""
    network_way_ids = frozenset(way.element_id for way in network.ways)
    network_node_ids = frozenset(node.element_id for node in network.nodes)
    scan = OsmSourceScan()
    for element in elements:
        if element.area_wkb is not None:
            if build_osm_present_amenities(element.tags, element.element_type):
                scan.areas.append(element)
        elif element.element_type == "node":
            if element.element_id not in network_node_ids:
                build_osm_node_amenity(scan, element, boundary)
        elif element.element_type == "way":
            build_osm_way_scan(scan, element, boundary, element.element_id in network_way_ids)
        else:
            scan.relation_way_members[element.element_id] = tuple(ref for kind, ref, _ in element.members if kind == "w")
            if build_osm_present_amenities(element.tags, "relation"):
                scan.amenity_relation_ids.add(element.element_id)
    return scan


def build_osm_node_amenity(scan: OsmSourceScan, element: OsmElementSnapshot, boundary: Polygon | MultiPolygon) -> None:
    """Add a node off the network whose own tags make an amenity present, when the node lies inside the boundary."""
    if not element.tags:
        return
    amenities = build_osm_present_amenities(element.tags, "node")
    if amenities and resolve_osm_element_coverage(boundary, Point(element.coordinates[0])):
        scan.candidates[("node", element.element_id)] = OsmFactCandidate("node", element.element_id, element.edited_at, set(amenities), None, Point(element.coordinates[0]))


def build_osm_way_scan(scan: OsmSourceScan, element: OsmElementSnapshot, boundary: Polygon | MultiPolygon, is_network_way: bool) -> None:
    """Record a way's motor-traffic nodes and coverage, and add its amenities when it is a covered way off the network."""
    if element.tags.get("highway") in thresholds.MOTOR_TRAFFIC_HIGHWAY_VALUES:
        scan.motor_traffic_node_ids.update(element.node_ids)
    if not build_osm_way_is_covered(boundary, element):
        return
    scan.covered_way_ids.add(element.element_id)
    amenities = frozenset() if is_network_way else build_osm_present_amenities(element.tags, "way")
    if amenities:
        scan.candidates[("way", element.element_id)] = OsmFactCandidate("way", element.element_id, element.edited_at, set(amenities), None, build_osm_line(element))


def build_osm_network_candidates(network: OsmPreparedNetwork, motor_traffic_node_ids: set[int]) -> dict[tuple[str, int], OsmFactCandidate]:
    """Give every network way its way facts at half its length and every network node its point facts at its coordinates."""
    candidates = {}
    for way in network.ways:
        way_facts = resolve_way_facts(way.tags)
        if way_facts.fact_types:
            candidates[("way", way.element_id)] = OsmFactCandidate("way", way.element_id, way.edited_at, set(way_facts.fact_types), way_facts.step_count, build_osm_line(way))
    for node in network.nodes:
        node_facts = resolve_node_facts(node.tags, node.element_id in motor_traffic_node_ids)
        if node_facts.fact_types:
            candidates[("node", node.element_id)] = OsmFactCandidate("node", node.element_id, node.edited_at, set(node_facts.fact_types), node_facts.step_count, Point(node.coordinates[0]))
    return candidates


def resolve_osm_area_is_in_copy(area: OsmElementSnapshot, scan: OsmSourceScan, network_way_ids: frozenset[int]) -> bool:
    """Keep the area of a covered way off the network and the area of a relation with a covered member way."""
    if area.element_type == "way":
        return area.element_id in scan.covered_way_ids and area.element_id not in network_way_ids
    return any(member in scan.covered_way_ids for member in scan.relation_way_members.get(area.element_id, ()))


def build_osm_present_facts(candidates: Iterable[OsmFactCandidate], zone: ZoneInfo) -> tuple[OsmPresentFact, ...]:
    """Locate each candidate once and expand it into one present fact per fact type, in a stable order."""
    facts = []
    for candidate in candidates:
        if candidate.geometry is None:
            raise OsmGeometryError("Fact has no source geometry")
        location = resolve_osm_fact_location(candidate.geometry)
        geog = f"SRID=4326;{location.wkt}"
        edited_on = candidate.edited_at.astimezone(zone).date()
        element_type = OsmElementType(candidate.element_type)
        for kind in candidate.fact_types:
            step_count = candidate.step_count if kind == FactType.STAIRS else None
            facts.append(OsmPresentFact(OsmFactIdentity(element_type, candidate.element_id, FactType(kind)), geog, edited_on, step_count))
    return tuple(sorted(facts, key=lambda fact: (fact.identity.element_type, fact.identity.element_id, fact.identity.fact_type)))
