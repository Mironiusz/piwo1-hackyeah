"""Read the facts and votes of a route from rows seeded in a rolled-back transaction of the local database of db/."""

import hashlib
from datetime import UTC, date, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from pyproj import Geod
from sqlalchemy import Connection, text

from data.route_facts import REPORT_STRETCH_DISTANCE_M, fetch_fact_votes, fetch_geozone_ways, fetch_route_facts

pytestmark = pytest.mark.critical

AMENITY_DISTANCE_M = 50
LINE_LAT = 50.06
LINE_START_LON = 19.93
LINE_END_LON = 19.94
MIDDLE_LON = 19.935
ROUTE_WAY_ID = 9200000001
FAR_WAY_ID = 9200000002
BARRIER_TYPES = ["high_kerb", "narrow_passage", "poor_surface", "stairs", "steep_incline"]
AMENITY_TYPES = ["accessible_toilet", "elevator", "handrail_at_stairs", "lowered_kerb", "ramp", "rest_place"]
WGS84_GEOD = Geod(ellps="WGS84")
LINE_WKT = f"LINESTRING({LINE_START_LON} {LINE_LAT}, {LINE_END_LON} {LINE_LAT})"
INSERT_REPORT_SQL = text(
    "INSERT INTO fact (fact_type, source, geog, geozone_radius_m, description, is_sample, idempotency_key, is_removed_from_osm, created_at, created_at_utc_offset_minutes, "
    "flagged_at, flagged_at_utc_offset_minutes, hidden_at, hidden_at_utc_offset_minutes) "
    "VALUES (:fact_type, 'user_report', ST_GeogFromText(:point), :radius, :description, false, :key, false, '2026-10-04 10:00:00+02', 120, "
    ":hidden_at, CASE WHEN CAST(:hidden_at AS timestamptz) IS NULL THEN NULL ELSE 120 END, :hidden_at, CASE WHEN CAST(:hidden_at AS timestamptz) IS NULL THEN NULL ELSE 120 END) "
    "RETURNING id"
)
INSERT_OSM_FACT_SQL = text(
    "INSERT INTO fact (fact_type, source, geog, step_count, is_sample, osm_element_type, osm_element_id, osm_edited_on, is_removed_from_osm, created_at, created_at_utc_offset_minutes) "
    "VALUES (:fact_type, 'openstreetmap', ST_GeogFromText(:point), :step_count, false, :element_type, :element_id, DATE '2026-09-14', :removed, '2026-10-04 03:00:00+02', 120) "
    "RETURNING id"
)
INSERT_WAY_SQL = text(
    "INSERT INTO osm_way (id, geog, stairs_state, poor_surface_state, steep_incline_state, narrow_passage_state, is_marked_wheelchair_no, is_motor_traffic, is_crossing) "
    "VALUES (:id, ST_GeogFromText(:line), 'absent_by_default', 'unknown', 'unknown', 'unknown', false, false, false)"
)
INSERT_ACCOUNT_SQL = text(
    "INSERT INTO account (pseudonym, password_hash, is_moderator, created_at, created_at_utc_offset_minutes) "
    "VALUES ('Invented route voter', 'made-up hash', false, '2026-10-04 09:00:00+02', 120) RETURNING id"
)
INSERT_VOTE_SQL = text(
    "INSERT INTO vote (fact_id, verdict, is_cast_with_account, account_id, voter_hash, cast_at, cast_at_utc_offset_minutes) "
    "VALUES (:fact_id, :verdict, :with_account, :account_id, :voter_hash, :cast_at, 120) RETURNING id"
)


def build_point_north(distance_m: float, lon: float = MIDDLE_LON) -> str:
    """Write the point the given distance north of the line at the given longitude as EWKT."""
    point_lon, point_lat, _azimuth = WGS84_GEOD.fwd(lon, LINE_LAT, 0, distance_m)
    return f"SRID=4326;POINT({point_lon} {point_lat})"


def apply_report(connection: Connection, seed: str, fact_type: str, distance_m: float, radius: int | None = None, hidden: bool = False) -> int:
    """Store an invented report the given distance north of the line and give its identity."""
    parameters = {
        "fact_type": fact_type,
        "point": build_point_north(distance_m),
        "radius": radius,
        "description": f"invented {seed}",
        "key": hashlib.sha256(f"create_fact:route facts {seed}".encode()).digest(),
        "hidden_at": "2026-10-04 11:00:00+02" if hidden else None,
    }
    return connection.execute(INSERT_REPORT_SQL, parameters).scalar_one()


def apply_osm_fact(connection: Connection, fact_type: str, distance_m: float, element_type: str, element_id: int, removed: bool = False) -> int:
    """Store an invented fact of OpenStreetMap the given distance north of the line and give its identity."""
    parameters = {
        "fact_type": fact_type,
        "point": build_point_north(distance_m),
        "step_count": 4 if fact_type == "stairs" else None,
        "element_type": element_type,
        "element_id": element_id,
        "removed": removed,
    }
    return connection.execute(INSERT_OSM_FACT_SQL, parameters).scalar_one()


def test_route_facts_follow_distance_visibility_and_way_rules(service_transaction):
    """Leave out hidden, removed and distant facts, read near ones, the geozone by its radius, the fact of a given way, the nearest way of a report and the ways a geozone covers."""
    connection = service_transaction
    connection.execute(INSERT_WAY_SQL, {"id": ROUTE_WAY_ID, "line": f"SRID=4326;{LINE_WKT}"})
    hidden = apply_report(connection, "hidden", "stairs", 5, hidden=True)
    removed = apply_osm_fact(connection, "high_kerb", 5, "node", 9200000101, removed=True)
    distant_barrier = apply_report(connection, "16 m", "narrow_passage", 16)
    near_report = apply_report(connection, "10 m", "poor_surface", 10)
    geozone = apply_report(connection, "geozone", "steep_incline", 60, radius=50)
    far_way_fact = apply_osm_fact(connection, "stairs", 200, "way", FAR_WAY_ID)
    near_amenity = apply_report(connection, "amenity 40 m", "ramp", 40)
    distant_amenity = apply_report(connection, "amenity 60 m", "elevator", 60)

    barriers = {fact.id: fact for fact in fetch_route_facts(connection, LINE_WKT, REPORT_STRETCH_DISTANCE_M, BARRIER_TYPES, [FAR_WAY_ID])}
    amenities = {fact.id for fact in fetch_route_facts(connection, LINE_WKT, AMENITY_DISTANCE_M, AMENITY_TYPES, [])}

    assert {hidden, removed, distant_barrier}.isdisjoint(barriers)
    assert {near_report, geozone, far_way_fact} <= set(barriers)
    assert near_amenity in amenities
    assert distant_amenity not in amenities
    report = barriers[near_report]
    assert (report.fact_type, report.source, report.nearest_way_id, report.description) == (FactType.POOR_SURFACE, FactSource.USER_REPORT, ROUTE_WAY_ID, "invented 10 m")
    assert barriers[geozone].geozone_radius_m == 50
    way_fact = barriers[far_way_fact]
    assert (way_fact.osm_element_type, way_fact.osm_element_id, way_fact.osm_edited_on, way_fact.step_count) == (OsmElementType.WAY, FAR_WAY_ID, date(2026, 9, 14), 4)
    assert way_fact.nearest_way_id is None
    covering = apply_report(connection, "covering geozone", "steep_incline", 30, radius=50)
    assert {(geozone_id, way_id) for geozone_id, way_id in fetch_geozone_ways(connection, [geozone, covering]) if way_id == ROUTE_WAY_ID} == {(covering, ROUTE_WAY_ID)}


def test_every_fact_of_the_copy_is_read_without_an_area(service_transaction):
    """Read every visible fact of the given types when no area is given, and still leave out hidden ones."""
    connection = service_transaction
    distant = apply_report(connection, "copy-wide", "stairs", 5000)
    hidden = apply_report(connection, "copy-wide hidden", "stairs", 5, hidden=True)
    read = {fact.id for fact in fetch_route_facts(connection, None, 0, ["stairs"], [])}
    assert distant in read
    assert hidden not in read


def test_votes_of_a_fact_are_read_with_their_fields(service_transaction):
    """Read every vote of the facts asked for, in vote order, with the fields the status rule needs."""
    connection = service_transaction
    fact_id = apply_report(connection, "voted", "stairs", 5)
    other_id = apply_report(connection, "not asked", "stairs", 5)
    account_id = connection.execute(INSERT_ACCOUNT_SQL).scalar_one()
    voter_hash = hashlib.sha256(b"made-up person: route facts").digest()
    first = connection.execute(
        INSERT_VOTE_SQL, {"fact_id": fact_id, "verdict": "confirm", "with_account": True, "account_id": account_id, "voter_hash": None, "cast_at": "2026-10-04 10:05:00+02"}
    ).scalar_one()
    second = connection.execute(
        INSERT_VOTE_SQL, {"fact_id": fact_id, "verdict": "deny", "with_account": False, "account_id": None, "voter_hash": voter_hash, "cast_at": "2026-10-04 10:06:00+02"}
    ).scalar_one()
    connection.execute(INSERT_VOTE_SQL, {"fact_id": other_id, "verdict": "confirm", "with_account": False, "account_id": None, "voter_hash": voter_hash, "cast_at": "2026-10-04 10:07:00+02"})

    votes = fetch_fact_votes(connection, [fact_id])

    assert [vote.id for vote in votes] == [first, second]
    assert (votes[0].fact_id, votes[0].verdict, votes[0].is_cast_with_account, votes[0].account_id, votes[0].voter_hash) == (fact_id, VoteVerdict.CONFIRM, True, account_id, None)
    assert (votes[1].verdict, votes[1].is_cast_with_account, votes[1].account_id, votes[1].voter_hash) == (VoteVerdict.DENY, False, None, voter_hash)
    assert votes[0].cast_at.instant == datetime(2026, 10, 4, 8, 5, tzinfo=UTC)
    assert votes[0].cast_at.utc_offset_minutes == 120
