"""
Checks against the local database that the stored data refuses by itself the states the rules forbid.

These are the refusals of FR-15 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` with the vote limit by calendar day of
version 13, the second fact with an idempotency key already saved, and the hash of a vote without an account of another
length than 32 bytes. Each refusal is asserted by the name of the constraint the database reports.
"""

from collections.abc import Mapping
from datetime import datetime

import psycopg
import pytest
from common_stored_rows import INSERT_ACCOUNT_SQL, INSERT_ACCOUNT_VOTE_SQL, INSERT_HASH_VOTE_SQL, INSERT_OSM_FACT_SQL, INSERT_USER_REPORT_SQL, build_idempotency_key, build_voter_hash
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.critical

SELECT_VOTES_OF_FACT_SQL = """
SELECT account_id IS NOT NULL AS is_account, verdict, cast_at FROM vote WHERE fact_id = :fact_id ORDER BY cast_at
"""


def apply_refused_write(connection: Connection, statement: str, parameters: Mapping[str, object]) -> str:
    """Runs a write that must be refused inside a savepoint and gives the name of the constraint that refused it."""
    with pytest.raises(IntegrityError) as refusal, connection.begin_nested():
        connection.execute(text(statement), parameters)
    driver_error = refusal.value.orig
    assert isinstance(driver_error, psycopg.Error)
    assert driver_error.diag.constraint_name is not None
    return driver_error.diag.constraint_name


def test_geozone_radius_outside_the_list_is_refused(service_connection: Connection) -> None:
    """A geozone with a radius of 30 m is refused."""
    parameters = {"fact_type": "stairs", "geozone_radius_m": 30, "idempotency_key": build_idempotency_key("geozone 30 m")}
    assert apply_refused_write(service_connection, INSERT_USER_REPORT_SQL, parameters) == "ck_fact_geozone"


def test_fact_type_outside_the_closed_list_is_refused(service_connection: Connection) -> None:
    """A fact of a type outside the closed list is refused."""
    parameters = {"fact_type": "bench", "geozone_radius_m": None, "idempotency_key": build_idempotency_key("bench")}
    assert apply_refused_write(service_connection, INSERT_USER_REPORT_SQL, parameters) == "ck_fact_type_closed_list"


@pytest.mark.parametrize(
    ("stored_source", "stored_is_removed_from_osm"),
    [("openstreetmap", False), ("user_report", False), ("openstreetmap", True)],
    ids=["from OpenStreetMap", "converted", "outdated"],
)
def test_second_fact_with_the_same_osm_identity_is_refused(service_connection: Connection, stored_source: str, stored_is_removed_from_osm: bool) -> None:
    """A fact with the OpenStreetMap identity of a stored fact is refused, also when the stored one is converted or outdated."""
    service_connection.execute(text(INSERT_OSM_FACT_SQL), {"source": stored_source, "is_removed_from_osm": stored_is_removed_from_osm})
    parameters = {"source": "openstreetmap", "is_removed_from_osm": False}
    assert apply_refused_write(service_connection, INSERT_OSM_FACT_SQL, parameters) == "ux_fact_osm_identity"


def test_pseudonym_differing_only_in_letter_case_is_refused(service_connection: Connection) -> None:
    """An account "kuba" next to an account "Kuba" is refused."""
    service_connection.execute(text(INSERT_ACCOUNT_SQL), {"pseudonym": "Kuba"})
    assert apply_refused_write(service_connection, INSERT_ACCOUNT_SQL, {"pseudonym": "kuba"}) == "ux_account_pseudonym_lower"


def test_second_fact_with_a_saved_idempotency_key_is_refused(service_connection: Connection) -> None:
    """A second fact with an idempotency key already saved is refused, so a repeated save finds the first fact."""
    parameters = {"fact_type": "stairs", "geozone_radius_m": None, "idempotency_key": build_idempotency_key("saved once")}
    service_connection.execute(text(INSERT_USER_REPORT_SQL), parameters)
    assert apply_refused_write(service_connection, INSERT_USER_REPORT_SQL, parameters) == "ux_fact_idempotency_key"


def test_second_vote_on_the_same_calendar_day_is_refused(service_connection: Connection, stored_fact_id: int) -> None:
    """Scenario 2 of the shape: a person votes once per calendar day in Europe/Warsaw, whatever the hours between the votes."""
    account_id = service_connection.execute(text(INSERT_ACCOUNT_SQL), {"pseudonym": "A"}).scalar_one()
    voter_hash = build_voter_hash("H")
    runs = [
        (INSERT_ACCOUNT_VOTE_SQL, {"account_id": account_id, "verdict": "confirm", "cast_at": "2026-10-04 10:00:00+02"}, True),
        (INSERT_ACCOUNT_VOTE_SQL, {"account_id": account_id, "verdict": "deny", "cast_at": "2026-10-04 15:00:00+02"}, False),
        (INSERT_ACCOUNT_VOTE_SQL, {"account_id": account_id, "verdict": "deny", "cast_at": "2026-10-05 00:05:00+02"}, True),
        (INSERT_HASH_VOTE_SQL, {"voter_hash": voter_hash, "verdict": "confirm", "cast_at": "2026-10-04 23:50:00+02"}, True),
        (INSERT_HASH_VOTE_SQL, {"voter_hash": voter_hash, "verdict": "deny", "cast_at": "2026-10-05 00:10:00+02"}, True),
        (INSERT_HASH_VOTE_SQL, {"voter_hash": voter_hash, "verdict": "confirm", "cast_at": "2026-10-04 22:30:00+00"}, False),
    ]
    for statement, parameters, is_accepted in runs:
        stored_id = service_connection.execute(text(statement), {"fact_id": stored_fact_id, **parameters}).scalar_one_or_none()
        assert (stored_id is not None) == is_accepted, parameters
    votes = service_connection.execute(text(SELECT_VOTES_OF_FACT_SQL), {"fact_id": stored_fact_id}).all()
    assert [(vote.is_account, vote.verdict, vote.cast_at) for vote in votes] == [
        (True, "confirm", datetime.fromisoformat("2026-10-04T10:00:00+02:00")),
        (False, "confirm", datetime.fromisoformat("2026-10-04T23:50:00+02:00")),
        (True, "deny", datetime.fromisoformat("2026-10-05T00:05:00+02:00")),
        (False, "deny", datetime.fromisoformat("2026-10-05T00:10:00+02:00")),
    ]


def test_vote_hash_of_another_length_is_refused(service_connection: Connection, stored_fact_id: int) -> None:
    """Scenario 5 of the shape: a hash of 20 bytes is refused, a hash of 32 bytes is kept."""
    short_hash = {"fact_id": stored_fact_id, "voter_hash": build_voter_hash("short", length=20), "verdict": "deny", "cast_at": "2026-10-04 10:00:00+02"}
    assert apply_refused_write(service_connection, INSERT_HASH_VOTE_SQL, short_hash) == "ck_vote_voter_hash_sha256"
    full_hash = {**short_hash, "voter_hash": build_voter_hash("full")}
    assert service_connection.execute(text(INSERT_HASH_VOTE_SQL), full_hash).scalar_one_or_none() is not None
