"""
Invented data and exact owner cleanup for the critical tests of `service/community_facts.py` against the local database of `db/`.

The facts of these tests lie around an origin far from Kraków and from the origin of `tests/data/test_community_facts_critical.py`, so neither
facts a developer loaded nor the facts of the data tests can enter their rectangles or radii. Reports are saved through the service itself
under fixed UUIDs, facts of OpenStreetMap are inserted with invented element identities from 9300100001, and every committed row is
registered for deletion by its exact key or element identity before the first commit, because the service account cannot delete a fact
or a vote (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-14).
"""

from datetime import datetime
from uuid import UUID

from accessibility_db.tables import build_offset_instant
from pyproj import Geod
from sqlalchemy import Connection, Engine, text

from data.accounts import apply_account_insert
from service.actors import AccountActor
from service.anonymous_voters import AnonymousVoterInput, build_anonymous_voter_input
from service.fact_rules import build_fact_idempotency_key
from tests.common_database_fixtures import DatabaseFixtureRegistry

ORIGIN_LAT = 49.35
ORIGIN_LON = 20.35
WGS84_GEOD = Geod(ellps="WGS84")
BLOCKED_SECONDS = 0.5
RELEASED_SECONDS = 10
PASSWORD_HASH = "$argon2id$v=19$m=19456,t=2,p=1$invented"
INSERT_OSM_FACT_SQL = text(
    "INSERT INTO fact (fact_type, source, geog, step_count, is_sample, osm_element_type, osm_element_id, osm_edited_on, is_removed_from_osm, created_at, created_at_utc_offset_minutes) "
    "VALUES (:fact_type, 'openstreetmap', ST_GeogFromText(:point), NULL, false, 'node', :element_id, DATE '2026-09-14', :removed, '2026-10-04 03:00:00+02', 120) "
    "RETURNING id"
)
COUNT_FACTS_BY_KEY_SQL = text("SELECT count(*) FROM fact WHERE idempotency_key = :key")
COUNT_VOTES_BY_KEY_SQL = text("SELECT count(*) FROM vote WHERE fact_id IN (SELECT id FROM fact WHERE idempotency_key = :key)")
COUNT_VOTES_BY_FACT_SQL = text("SELECT count(*) FROM vote WHERE fact_id = :fact_id")
DELETE_VOTES_BY_KEY_SQL = text("DELETE FROM vote WHERE fact_id IN (SELECT id FROM fact WHERE idempotency_key = :key)")
DELETE_FACT_BY_KEY_SQL = text("DELETE FROM fact WHERE idempotency_key = :key")
DELETE_VOTES_BY_OSM_ID_SQL = text("DELETE FROM vote WHERE fact_id IN (SELECT id FROM fact WHERE osm_element_type = 'node' AND osm_element_id = :element_id)")
DELETE_FACT_BY_OSM_ID_SQL = text("DELETE FROM fact WHERE osm_element_type = 'node' AND osm_element_id = :element_id")


def build_point(distance_m: float) -> tuple[float, float]:
    """Give the latitude and longitude of the point the given distance north of the origin, on the ellipsoid the database measures on."""
    point_lon, point_lat, _azimuth = WGS84_GEOD.fwd(ORIGIN_LON, ORIGIN_LAT, 0, distance_m)
    return point_lat, point_lon


def build_instant(value: str) -> datetime:
    """Build an aware instant of an ISO text with milliseconds and offset."""
    return datetime.fromisoformat(value)


def build_person(user_agent: str) -> AnonymousVoterInput:
    """Build an invented person without an account behind one public address, told apart by the User-Agent."""
    return build_anonymous_voter_input("203.0.113.70", user_agent)


def register_report_cleanup(registry: DatabaseFixtureRegistry, key: UUID) -> bytes:
    """Register before the first commit the exact owner cleanup of the report saved under the UUID and of its votes, and give its stored key."""
    stored_key = build_fact_idempotency_key(key)

    def apply_cleanup(connection: Connection) -> None:
        """Delete the votes and then the fact of the key."""
        connection.execute(DELETE_VOTES_BY_KEY_SQL, {"key": stored_key})
        connection.execute(DELETE_FACT_BY_KEY_SQL, {"key": stored_key})

    registry.apply_registration(apply_cleanup)
    return stored_key


def register_osm_fact_cleanup(registry: DatabaseFixtureRegistry, element_id: int) -> None:
    """Register before the first commit the exact owner cleanup of the invented fact of OpenStreetMap and of its votes."""

    def apply_cleanup(connection: Connection) -> None:
        """Delete the votes and then the fact of the element."""
        connection.execute(DELETE_VOTES_BY_OSM_ID_SQL, {"element_id": element_id})
        connection.execute(DELETE_FACT_BY_OSM_ID_SQL, {"element_id": element_id})

    registry.apply_registration(apply_cleanup)


def apply_osm_fact(engine: Engine, registry: DatabaseFixtureRegistry, element_id: int, distance_m: float = 0.0, fact_type: str = "stairs", removed: bool = False) -> int:
    """Commit an invented fact of OpenStreetMap the given distance north of the origin, registered for cleanup first, and give its identity."""
    register_osm_fact_cleanup(registry, element_id)
    lat, lon = build_point(distance_m)
    with engine.begin() as connection:
        return connection.execute(INSERT_OSM_FACT_SQL, {"fact_type": fact_type, "point": f"SRID=4326;POINT({lon} {lat})", "element_id": element_id, "removed": removed}).scalar_one()


def apply_account(engine: Engine, stored_account_cleanup, pseudonym: str, is_moderator: bool = False) -> AccountActor:
    """Commit an invented ordinary account, registered for cleanup first, and give it as a resolved session gives it."""
    stored_account_cleanup(pseudonym)
    with engine.begin() as connection:
        account_id = apply_account_insert(connection, pseudonym, PASSWORD_HASH, build_offset_instant(build_instant("2026-10-01T08:00:00.000+02:00")))
    assert account_id is not None
    return AccountActor(account_id=account_id, pseudonym=pseudonym, is_moderator=is_moderator)


def fetch_count(engine: Engine, statement, parameters: dict[str, object]) -> int:
    """Read one count as the service account."""
    with engine.connect() as connection:
        return connection.execute(statement, parameters).scalar_one()
