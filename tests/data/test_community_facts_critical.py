"""
Critical tests of `data/community_facts.py` against the local database of `db/compose.yaml` with its chain applied.

They prove the acceptance criteria AC-1 to AC-9 of `plans/community_facts/COMMUNITY_FACTS_PRD.md` on stored data. A case on one connection seeds and
asserts inside `service_transaction`, which rolls back. A case that needs two connections commits invented rows, so it registers with
`database_cleanup_registry` the exact owner cleanup of its facts and votes before the first commit, and its accounts go through
`stored_account_cleanup`; the service account cannot delete a fact or a vote. Those cases need `--scratch-database-url` with a local schema-owner
address. The facts of a case lie around an origin far from Krakow, so facts a developer loaded into the local database cannot enter its rectangles
or radii, and invented OpenStreetMap identities start at 9300000001, apart from the range of `tests/data/test_route_facts_critical.py`.
"""

import hashlib
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass, fields
from datetime import date, datetime
from unittest.mock import Mock

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict
from accessibility_db.tables import OffsetInstant, build_offset_instant
from pyproj import Geod
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError

from data.accounts import apply_account_delete, apply_account_insert
from data.community_facts import (
    AccountVoter,
    AnonymousVoter,
    FactContent,
    StoredCommunityFact,
    StoredVoteInsert,
    VoteAccountMissingError,
    VoteDayTaken,
    VoteInsertOutcome,
    Voter,
    apply_fact_flag,
    apply_fact_hiding,
    apply_fact_insert,
    apply_fact_restoration,
    apply_vote_insert,
    fetch_stored_fact,
    fetch_stored_fact_for_change,
    fetch_stored_fact_for_vote,
    fetch_stored_facts_in_area,
    fetch_stored_flagged_facts,
    fetch_stored_nearby_facts,
)
from data.engine import fetch_api_engine
from data.osm_copy import OsmFactChange, OsmVoteSnapshot, apply_osm_fact_changes, fetch_osm_fact_history, fetch_osm_facts_for_update
from data.route_facts import StoredFact, StoredVote, fetch_fact_votes
from service.fact_status import resolve_fact_status

pytestmark = pytest.mark.critical

ORIGIN_LAT = 49.2
ORIGIN_LON = 20.0
EXACT_LAT = 49.123456789012345
EXACT_LON = 20.987654321098765
WGS84_GEOD = Geod(ellps="WGS84")
BLOCKED_SECONDS = 0.5
RELEASED_SECONDS = 10
READ_TIME_BOUND_SECONDS = 1
MISSING_FACT_ID = 9000000000000000000
PASSWORD_HASH = "$argon2id$v=19$m=19456,t=2,p=1$invented"
CREATED_AT = OffsetInstant(instant=datetime.fromisoformat("2026-10-04T08:00:00.000+00:00"), utc_offset_minutes=120)
OLD_CREATED_AT = OffsetInstant(instant=datetime.fromisoformat("2026-08-01T08:00:00.000+00:00"), utc_offset_minutes=120)
PUBLICATION_OSM_ID_COMMITTED = 9300000001
PUBLICATION_OSM_ID_ROLLED_BACK = 9300000002
SAME_DAY_OSM_ID = 9300000003
FIRST_SEEDED_OSM_ID = 9300001000
SEEDED_FACT_COUNT = 1001
SEEDED_VOTE_PERSONS = 5
AREA_SOUTH = ORIGIN_LAT - 0.01
AREA_WEST = ORIGIN_LON - 0.02
AREA_NORTH = ORIGIN_LAT + 0.02
AREA_EAST = ORIGIN_LON + 0.02
INSERT_OSM_FACT_SQL = text(
    "INSERT INTO fact (fact_type, source, geog, step_count, is_sample, osm_element_type, osm_element_id, osm_edited_on, is_removed_from_osm, created_at, created_at_utc_offset_minutes) "
    "VALUES (:fact_type, 'openstreetmap', ST_GeogFromText(:point), :step_count, false, 'node', :element_id, DATE '2026-09-14', :removed, '2026-10-04 03:00:00+02', 120) "
    "RETURNING id"
)
INSERT_SEEDED_FACTS_SQL = text(
    "INSERT INTO fact (fact_type, source, geog, step_count, is_sample, osm_element_type, osm_element_id, osm_edited_on, is_removed_from_osm, created_at, created_at_utc_offset_minutes) "
    "SELECT 'stairs', 'openstreetmap', "
    "ST_SetSRID(ST_MakePoint(CAST(:west AS double precision) + (series.number % 40) * 0.0005, CAST(:south AS double precision) + (series.number / 40) * 0.0005), 4326)::geography, "
    "4, false, 'node', :first_id + series.number, DATE '2026-09-14', false, '2026-10-04 03:00:00+02', 120 "
    "FROM generate_series(0, :last_number) AS series(number)"
)
INSERT_SEEDED_VOTES_SQL = text(
    "INSERT INTO vote (fact_id, verdict, is_cast_with_account, account_id, voter_hash, cast_at, cast_at_utc_offset_minutes) "
    "SELECT fact.id, CASE WHEN person.number <= fact.id % 6 THEN 'deny' ELSE 'confirm' END, false, NULL, "
    "decode(md5(CAST(fact.id AS text) || ':' || CAST(person.number AS text)) || md5(CAST(person.number AS text) || ':' || CAST(fact.id AS text)), 'hex'), "
    "TIMESTAMPTZ '2026-10-04 10:00:00+02' + person.number * INTERVAL '1 minute', 120 "
    "FROM fact CROSS JOIN generate_series(1, :persons) AS person(number) "
    "WHERE fact.osm_element_type = 'node' AND fact.osm_element_id BETWEEN :first_id AND :last_id"
)
COUNT_FACTS_BY_KEY_SQL = text("SELECT count(*) FROM fact WHERE idempotency_key = :key")
COUNT_VOTES_BY_KEY_SQL = text("SELECT count(*) FROM vote WHERE fact_id IN (SELECT id FROM fact WHERE idempotency_key = :key)")
FETCH_HIDDEN_INSTANT_SQL = text("SELECT hidden_at, hidden_at_utc_offset_minutes FROM fact WHERE id = :fact_id")
DELETE_VOTES_BY_KEY_SQL = text("DELETE FROM vote WHERE fact_id IN (SELECT id FROM fact WHERE idempotency_key = :key)")
DELETE_FACT_BY_KEY_SQL = text("DELETE FROM fact WHERE idempotency_key = :key")
DELETE_VOTES_BY_OSM_ID_SQL = text("DELETE FROM vote WHERE fact_id IN (SELECT id FROM fact WHERE osm_element_type = 'node' AND osm_element_id = :element_id)")
DELETE_FACT_BY_OSM_ID_SQL = text("DELETE FROM fact WHERE osm_element_type = 'node' AND osm_element_id = :element_id")
FACT_FIELD_NAMES = {field.name for field in fields(StoredFact)} | {"flagged_at", "is_hidden"}


@dataclass(frozen=True)
class PublicationRace:
    """What one vote against one publication left behind: the fact as the vote's lock read it, the vote outcome, the votes the publication locked and the stored end state."""

    account_ids: tuple[int, int, int]
    locked_fact: StoredCommunityFact | None
    outcome: VoteInsertOutcome
    publication_vote_ids: tuple[int, ...]
    final_fact: StoredCommunityFact | None
    final_votes: tuple[StoredVote, ...]


def build_instant(value: str) -> OffsetInstant:
    """Build the stored pair of an ISO instant with its offset."""
    return build_offset_instant(datetime.fromisoformat(value))


def build_point(distance_m: float) -> tuple[float, float]:
    """Give the latitude and longitude of the point the given distance north of the origin, on the ellipsoid the database measures on."""
    point_lon, point_lat, _azimuth = WGS84_GEOD.fwd(ORIGIN_LON, ORIGIN_LAT, 0, distance_m)
    return point_lat, point_lon


def build_key(seed: str) -> bytes:
    """Build the invented idempotency key of a seed."""
    return hashlib.sha256(f"create_fact:community facts {seed}".encode()).digest()


def build_voter_hash(seed: str) -> bytes:
    """Build the invented 32 bytes of a person without an account."""
    return hashlib.sha256(f"made-up person: community facts {seed}".encode()).digest()


def apply_report_at(
    connection: Connection,
    seed: str,
    lat: float,
    lon: float,
    fact_type: FactType = FactType.STAIRS,
    radius: int | None = None,
    created_at: OffsetInstant = CREATED_AT,
    author: Voter | None = None,
) -> StoredCommunityFact:
    """Save an invented report of the type at the point with the confirmation of its author and give the stored fact."""
    content = FactContent(fact_type, lat, lon, f"invented {seed}", None, radius)
    outcome = apply_fact_insert(connection, content, build_key(seed), created_at, author or AnonymousVoter(build_voter_hash(seed)))
    assert outcome.is_created
    return outcome.fact


def apply_report_north(
    connection: Connection,
    seed: str,
    distance_m: float,
    fact_type: FactType = FactType.STAIRS,
    created_at: OffsetInstant = CREATED_AT,
    author: Voter | None = None,
) -> StoredCommunityFact:
    """Save an invented report the given distance north of the origin."""
    lat, lon = build_point(distance_m)
    return apply_report_at(connection, seed, lat, lon, fact_type, None, created_at, author)


def apply_osm_fact(connection: Connection, element_id: int, distance_m: float = 0.0, fact_type: str = "stairs", removed: bool = False) -> int:
    """Store an invented fact of OpenStreetMap the given distance north of the origin and give its identity."""
    lat, lon = build_point(distance_m)
    parameters = {"fact_type": fact_type, "point": f"SRID=4326;POINT({lon} {lat})", "step_count": 4 if fact_type == "stairs" else None, "element_id": element_id, "removed": removed}
    return connection.execute(INSERT_OSM_FACT_SQL, parameters).scalar_one()


def apply_account(connection: Connection, pseudonym: str) -> int:
    """Insert an invented ordinary account and give its identifier."""
    account_id = apply_account_insert(connection, pseudonym, PASSWORD_HASH, CREATED_AT)
    assert account_id is not None
    return account_id


def apply_voter(connection: Connection, kind: str, seed: str) -> Voter:
    """Give an invented person of the kind: an account stored in the connection, or the invented bytes of a person without one."""
    if kind == "account":
        return AccountVoter(apply_account(connection, f"Glosujacy {seed}"))
    return AnonymousVoter(build_voter_hash(seed))


def apply_hidden_report(connection: Connection, seed: str, distance_m: float) -> StoredCommunityFact:
    """Save an invented report, flag it and hide it, and give it as it is stored."""
    report = apply_report_north(connection, seed, distance_m)
    apply_fact_flag(connection, report.id, build_instant("2026-10-04T09:00:00.000+02:00"))
    return apply_fact_hiding(connection, report.id, build_instant("2026-10-04T09:30:00.000+02:00"))


def apply_locked_vote(connection: Connection, fact_id: int, verdict: VoteVerdict, voter: Voter, cast_at: OffsetInstant) -> tuple[StoredCommunityFact | None, VoteInsertOutcome]:
    """Run a vote as the service layer does: lock the fact, read it as locked, then store the vote."""
    fact = fetch_stored_fact_for_vote(connection, fact_id)
    return fact, apply_vote_insert(connection, fact_id, verdict, voter, cast_at)


def register_report_cleanup(database_cleanup_registry, key: bytes) -> None:
    """Register before the first commit the exact owner cleanup of the report saved under the key and of its votes."""

    def apply_cleanup(connection: Connection) -> None:
        """Delete the votes and then the fact of the key."""
        connection.execute(DELETE_VOTES_BY_KEY_SQL, {"key": key})
        connection.execute(DELETE_FACT_BY_KEY_SQL, {"key": key})

    database_cleanup_registry.apply_registration(apply_cleanup)


def register_osm_fact_cleanup(database_cleanup_registry, element_id: int) -> None:
    """Register before the first commit the exact owner cleanup of the invented OpenStreetMap fact and of its votes."""

    def apply_cleanup(connection: Connection) -> None:
        """Delete the votes and then the fact of the element."""
        connection.execute(DELETE_VOTES_BY_OSM_ID_SQL, {"element_id": element_id})
        connection.execute(DELETE_FACT_BY_OSM_ID_SQL, {"element_id": element_id})

    database_cleanup_registry.apply_registration(apply_cleanup)


def fetch_area_ids(connection: Connection) -> list[int]:
    """Read the identifiers of the facts of the shared rectangle around the origin, with the limit the service layer passes."""
    return [fact.id for fact in fetch_stored_facts_in_area(connection, AREA_SOUTH, AREA_WEST, AREA_NORTH, AREA_EAST, 1001)]


def apply_publication_race(database_cleanup_registry, stored_account_cleanup, element_id: int, publication_commits: bool) -> PublicationRace:
    """
    Let a publication lock a fact and its votes, start a vote of a third account against it, and end the publication by a commit or a rollback.

    An OpenStreetMap fact with a confirmation of account A and a denial of account B is locked by the importer's own lock statements on one
    connection. The vote of account C locks the fact on another and must wait, not be done after half a second, and finish once the
    publication ends. The publication commits the fact as removed in OpenStreetMap, or rolls back and writes nothing.
    """
    register_osm_fact_cleanup(database_cleanup_registry, element_id)
    pseudonyms = [f"Konto {name} {element_id}" for name in "ABC"]
    for pseudonym in pseudonyms:
        stored_account_cleanup(pseudonym)
    engine = fetch_api_engine()
    with engine.begin() as setup:
        account_a, account_b, account_c = (apply_account(setup, pseudonym) for pseudonym in pseudonyms)
        fact_id = apply_osm_fact(setup, element_id)
        apply_vote_insert(setup, fact_id, VoteVerdict.CONFIRM, AccountVoter(account_a), build_instant("2026-10-03T09:00:00.000+02:00"))
        apply_vote_insert(setup, fact_id, VoteVerdict.DENY, AccountVoter(account_b), build_instant("2026-10-03T09:30:00.000+02:00"))
    with engine.connect() as publication, engine.connect() as voter, ThreadPoolExecutor(max_workers=1) as pool:
        publication_transaction = publication.begin()
        voter_transaction = voter.begin()
        fetch_osm_facts_for_update(publication, [fact_id])
        history: tuple[OsmVoteSnapshot, ...] = fetch_osm_fact_history(publication, [fact_id])
        pending = pool.submit(apply_locked_vote, voter, fact_id, VoteVerdict.CONFIRM, AccountVoter(account_c), build_instant("2026-10-04T03:00:02.000+02:00"))
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        if publication_commits:
            apply_osm_fact_changes(publication, [OsmFactChange(fact_id, FactSource.OPENSTREETMAP, True)])
            publication_transaction.commit()
        else:
            publication_transaction.rollback()
        locked_fact, outcome = pending.result(timeout=RELEASED_SECONDS)
        voter_transaction.commit()
    with engine.connect() as reader:
        final_fact = fetch_stored_fact(reader, fact_id)
        final_votes = fetch_fact_votes(reader, [fact_id])
    return PublicationRace((account_a, account_b, account_c), locked_fact, outcome, tuple(vote.id for vote in history), final_fact, final_votes)


def test_report_saved_once_with_its_author_vote(service_transaction: Connection) -> None:
    """Save a report twice with one key, as after a lost response: one fact with the exact point, one confirmation of its author, and the repeat finds the first fact."""
    connection = service_transaction
    content = FactContent(FactType.STAIRS, EXACT_LAT, EXACT_LON, "Stairs without a ramp", 3, None)
    author = AnonymousVoter(build_voter_hash("author"))
    key = build_key("saved once")

    first = apply_fact_insert(connection, content, key, CREATED_AT, author)
    second = apply_fact_insert(connection, content, key, build_instant("2026-10-04T10:05:00.000+02:00"), author)

    assert first.is_created is True
    assert second.is_created is False
    assert second.fact == first.fact
    fact = first.fact
    assert (fact.lat, fact.lon) == (EXACT_LAT, EXACT_LON)
    assert (fact.fact_type, fact.source, fact.step_count, fact.description, fact.geozone_radius_m) == (FactType.STAIRS, FactSource.USER_REPORT, 3, "Stairs without a ramp", None)
    assert (fact.is_sample, fact.is_removed_from_osm, fact.is_hidden, fact.flagged_at, fact.osm_element_id) == (False, False, False, None, None)
    votes = fetch_fact_votes(connection, [fact.id])
    assert len(votes) == 1
    assert (votes[0].verdict, votes[0].is_cast_with_account, votes[0].account_id, votes[0].voter_hash, votes[0].cast_at) == (VoteVerdict.CONFIRM, False, None, author.voter_hash, CREATED_AT)
    assert connection.execute(COUNT_FACTS_BY_KEY_SQL, {"key": key}).scalar_one() == 1


def test_failed_author_vote_leaves_no_fact(stored_account_cleanup) -> None:
    """Refuse a report whose author account was deleted before it: the error of the layer, and after the rollback of the caller neither the fact nor the vote is stored."""
    stored_account_cleanup("Spozniony_cf1")
    engine = fetch_api_engine()
    with engine.begin() as setup:
        account_id = apply_account(setup, "Spozniony_cf1")
    with engine.begin() as deletion:
        assert apply_account_delete(deletion, account_id) is True
    key = build_key("failed author vote")
    content = FactContent(FactType.STAIRS, EXACT_LAT, EXACT_LON, None, None, None)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(VoteAccountMissingError):
                apply_fact_insert(connection, content, key, CREATED_AT, AccountVoter(account_id))
        finally:
            transaction.rollback()
    with engine.connect() as reader:
        assert reader.execute(COUNT_FACTS_BY_KEY_SQL, {"key": key}).scalar_one() == 0
        assert reader.execute(COUNT_VOTES_BY_KEY_SQL, {"key": key}).scalar_one() == 0


def test_two_concurrent_saves_with_one_key_store_one_fact(database_cleanup_registry) -> None:
    """Let the unique index of the key decide: the second save waits for the first transaction, then finds its fact and stores neither a fact nor a vote."""
    key = build_key("concurrent saves")
    register_report_cleanup(database_cleanup_registry, key)
    content = FactContent(FactType.STAIRS, EXACT_LAT, EXACT_LON, "Saved twice at once", None, None)
    author = AnonymousVoter(build_voter_hash("concurrent author"))
    engine = fetch_api_engine()
    with engine.connect() as first, engine.connect() as second, ThreadPoolExecutor(max_workers=1) as pool:
        first_transaction = first.begin()
        second_transaction = second.begin()
        created = apply_fact_insert(first, content, key, CREATED_AT, author)
        pending = pool.submit(apply_fact_insert, second, content, key, CREATED_AT, author)
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        first_transaction.commit()
        repeated = pending.result(timeout=RELEASED_SECONDS)
        second_transaction.commit()
    assert created.is_created is True
    assert repeated.is_created is False
    assert repeated.fact == created.fact
    with engine.connect() as reader:
        assert reader.execute(COUNT_FACTS_BY_KEY_SQL, {"key": key}).scalar_one() == 1
        assert reader.execute(COUNT_VOTES_BY_KEY_SQL, {"key": key}).scalar_one() == 1


@pytest.mark.parametrize("voter_kind", ["account", "anonymous"])
def test_daily_limit_by_calendar_day_in_warsaw(service_transaction: Connection, voter_kind: str) -> None:
    """Refuse a second vote of one person on one fact on one calendar day in Europe/Warsaw, accept it from the start of the next day, and name the day of the change of the offset."""
    connection = service_transaction
    fact_id = apply_osm_fact(connection, 9300000201)
    voter = apply_voter(connection, voter_kind, "daily limit")

    stored = apply_vote_insert(connection, fact_id, VoteVerdict.CONFIRM, voter, build_instant("2026-10-04T23:59:59.000+02:00"))
    refused = apply_vote_insert(connection, fact_id, VoteVerdict.DENY, voter, build_instant("2026-10-04T23:59:59.900+02:00"))
    next_day = apply_vote_insert(connection, fact_id, VoteVerdict.DENY, voter, build_instant("2026-10-05T00:00:00.500+02:00"))
    repeated = apply_vote_insert(connection, fact_id, VoteVerdict.DENY, voter, build_instant("2026-10-05T00:00:03.000+02:00"))

    assert isinstance(stored, StoredVoteInsert)
    assert stored.cast_on == date(2026, 10, 4)
    assert refused == VoteDayTaken(date(2026, 10, 4))
    assert isinstance(next_day, StoredVoteInsert)
    assert next_day.cast_on == date(2026, 10, 5)
    assert repeated == VoteDayTaken(date(2026, 10, 5))
    votes = fetch_fact_votes(connection, [fact_id])
    assert [vote.verdict for vote in votes] == [VoteVerdict.CONFIRM, VoteVerdict.DENY]
    assert [vote.id for vote in votes] == [stored.vote_id, next_day.vote_id]

    offset_day_fact_id = apply_osm_fact(connection, 9300000202)
    before_change = apply_vote_insert(connection, offset_day_fact_id, VoteVerdict.CONFIRM, voter, build_instant("2026-10-25T01:30:00.000+02:00"))
    after_change = apply_vote_insert(connection, offset_day_fact_id, VoteVerdict.DENY, voter, build_instant("2026-10-25T02:30:00.000+01:00"))
    assert isinstance(before_change, StoredVoteInsert)
    assert before_change.cast_on == date(2026, 10, 25)
    assert after_change == VoteDayTaken(date(2026, 10, 25))


def test_two_concurrent_same_day_votes_store_one(database_cleanup_registry) -> None:
    """Let the unique index of the day decide: two votes of one person do not wait at the lock of the fact, the second waits at the insert and is then refused."""
    register_osm_fact_cleanup(database_cleanup_registry, SAME_DAY_OSM_ID)
    engine = fetch_api_engine()
    with engine.begin() as setup:
        fact_id = apply_osm_fact(setup, SAME_DAY_OSM_ID)
    voter = AnonymousVoter(build_voter_hash("same day"))
    with engine.connect() as first, engine.connect() as second, ThreadPoolExecutor(max_workers=1) as pool:
        first_transaction = first.begin()
        second_transaction = second.begin()
        first_locked, first_outcome = apply_locked_vote(first, fact_id, VoteVerdict.CONFIRM, voter, build_instant("2026-10-04T12:00:00.000+02:00"))
        pending = pool.submit(apply_locked_vote, second, fact_id, VoteVerdict.DENY, voter, build_instant("2026-10-04T12:00:01.000+02:00"))
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        first_transaction.commit()
        second_locked, second_outcome = pending.result(timeout=RELEASED_SECONDS)
        second_transaction.commit()
    assert first_locked is not None
    assert second_locked is not None
    assert isinstance(first_outcome, StoredVoteInsert)
    assert second_outcome == VoteDayTaken(date(2026, 10, 4))
    with engine.connect() as reader:
        votes = fetch_fact_votes(reader, [fact_id])
    assert [(vote.id, vote.verdict) for vote in votes] == [(first_outcome.vote_id, VoteVerdict.CONFIRM)]


def test_vote_waits_for_a_publication_and_sees_its_commit(database_cleanup_registry, stored_account_cleanup) -> None:
    """Hold a vote at its lock while a publication that locked the fact commits it as removed in OpenStreetMap, then give the vote the fact as the publication left it."""
    race = apply_publication_race(database_cleanup_registry, stored_account_cleanup, PUBLICATION_OSM_ID_COMMITTED, True)
    assert race.locked_fact is not None
    assert (race.locked_fact.is_removed_from_osm, race.locked_fact.is_hidden) == (True, False)
    assert isinstance(race.outcome, StoredVoteInsert)
    assert race.final_fact is not None
    assert race.final_fact.is_removed_from_osm is True
    assert [(vote.verdict, vote.account_id) for vote in race.final_votes] == [
        (VoteVerdict.CONFIRM, race.account_ids[0]),
        (VoteVerdict.DENY, race.account_ids[1]),
        (VoteVerdict.CONFIRM, race.account_ids[2]),
    ]
    assert race.publication_vote_ids == tuple(vote.id for vote in race.final_votes[:2])


def test_vote_waits_for_a_publication_and_sees_its_rollback(database_cleanup_registry, stored_account_cleanup) -> None:
    """Hold a vote at its lock while a publication that locked the fact rolls back, then give the vote the fact as it was before the publication."""
    race = apply_publication_race(database_cleanup_registry, stored_account_cleanup, PUBLICATION_OSM_ID_ROLLED_BACK, False)
    assert race.locked_fact is not None
    assert (race.locked_fact.is_removed_from_osm, race.locked_fact.is_hidden) == (False, False)
    assert isinstance(race.outcome, StoredVoteInsert)
    assert race.final_fact is not None
    assert race.final_fact.is_removed_from_osm is False
    assert len(race.final_votes) == 3
    assert race.publication_vote_ids == tuple(vote.id for vote in race.final_votes[:2])


def test_vote_waits_for_a_moderation_of_the_same_fact(database_cleanup_registry) -> None:
    """Hold a vote at its lock while a moderator who locked the fact flags and hides it, then give the vote the fact as hidden."""
    key = build_key("moderation wait")
    register_report_cleanup(database_cleanup_registry, key)
    engine = fetch_api_engine()
    content = FactContent(FactType.STAIRS, EXACT_LAT, EXACT_LON, "Moderated while voted", None, None)
    with engine.begin() as setup:
        outcome = apply_fact_insert(setup, content, key, CREATED_AT, AnonymousVoter(build_voter_hash("moderation wait")))
    fact_id = outcome.fact.id
    with engine.connect() as moderator, engine.connect() as voter, ThreadPoolExecutor(max_workers=1) as pool:
        moderator_transaction = moderator.begin()
        voter_transaction = voter.begin()
        locked = fetch_stored_fact_for_change(moderator, fact_id)
        assert locked is not None
        assert (locked.flagged_at, locked.is_hidden) == (None, False)
        apply_fact_flag(moderator, fact_id, build_instant("2026-10-04T11:00:00.000+02:00"))
        apply_fact_hiding(moderator, fact_id, build_instant("2026-10-04T11:05:00.000+02:00"))
        pending = pool.submit(fetch_stored_fact_for_vote, voter, fact_id)
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        moderator_transaction.commit()
        seen = pending.result(timeout=RELEASED_SECONDS)
        voter_transaction.rollback()
    assert seen is not None
    assert seen.is_hidden is True


def test_nearby_facts_follow_type_distance_and_visibility(service_transaction: Connection) -> None:
    """Read for stairs the outdated report at 8 m and the OpenStreetMap fact at 12 m, nearest first, and leave out the removed, hidden, other-type and distant facts."""
    connection = service_transaction
    outdated = apply_report_north(connection, "nearby outdated", 8, created_at=OLD_CREATED_AT)
    osm_stairs = apply_osm_fact(connection, 9300000101, 12)
    apply_osm_fact(connection, 9300000102, 3, removed=True)
    apply_hidden_report(connection, "nearby hidden", 6)
    kerb = apply_report_north(connection, "nearby kerb", 5, FactType.HIGH_KERB)
    apply_report_north(connection, "nearby distant", 16)

    found = fetch_stored_nearby_facts(connection, FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON, 15)
    kerbs = fetch_stored_nearby_facts(connection, FactType.HIGH_KERB, ORIGIN_LAT, ORIGIN_LON, 15)

    assert [item.fact.id for item in found] == [outdated.id, osm_stairs]
    assert [round(item.distance_m) for item in found] == [8, 12]
    assert found[0].distance_m == pytest.approx(8, abs=0.01)
    assert found[1].distance_m == pytest.approx(12, abs=0.01)
    assert found[1].fact.source == FactSource.OPENSTREETMAP
    assert [item.fact.id for item in kerbs] == [kerb.id]


def test_area_and_detail_visibility_differ_only_in_the_removed_mark(service_transaction: Connection) -> None:
    """Show on one set of facts that the area leaves out hidden and removed facts and keeps a geozone by its point, while the reading by identifier keeps the removed one."""
    connection = service_transaction
    unverified = apply_report_north(connection, "area unverified", 100)
    outdated = apply_report_north(connection, "area outdated", 200, created_at=OLD_CREATED_AT)
    hidden = apply_hidden_report(connection, "area hidden", 300)
    removed_id = apply_osm_fact(connection, 9300000111, 400, removed=True)
    geozone = apply_report_at(connection, "area geozone", ORIGIN_LAT + 0.0098, ORIGIN_LON, radius=100)
    apply_report_north(connection, "area outside", 3000)

    area = fetch_stored_facts_in_area(connection, AREA_SOUTH, AREA_WEST, ORIGIN_LAT + 0.01, AREA_EAST, 1001)

    assert [fact.id for fact in area] == [unverified.id, outdated.id, geozone.id]
    assert area[2].geozone_radius_m == 100
    assert fetch_stored_fact(connection, unverified.id) == area[0]
    removed = fetch_stored_fact(connection, removed_id)
    assert removed is not None
    assert (removed.is_removed_from_osm, removed.source) == (True, FactSource.OPENSTREETMAP)
    assert fetch_stored_fact(connection, hidden.id) is None
    assert fetch_stored_fact(connection, MISSING_FACT_ID) is None


def test_area_rectangle_includes_its_edges_and_a_point_on_its_southern_parallel(service_transaction: Connection) -> None:
    """Compare the rectangle as geometry: a point on its west edge and a point a hair above its southern parallel are inside, a point a hair below is outside."""
    connection = service_transaction
    south, west, north, east = ORIGIN_LAT, ORIGIN_LON, ORIGIN_LAT + 0.1, ORIGIN_LON + 0.1
    middle_lon = ORIGIN_LON + 0.05
    on_west_edge = apply_report_at(connection, "edge west", ORIGIN_LAT + 0.05, west)
    above_parallel = apply_report_at(connection, "edge south inside", south + 0.000001, middle_lon)
    apply_report_at(connection, "edge south outside", south - 0.000001, middle_lon)

    area = fetch_stored_facts_in_area(connection, south, west, north, east, 1001)

    assert [fact.id for fact in area] == [on_west_edge.id, above_parallel.id]


def test_area_read_stops_at_its_limit(service_transaction: Connection) -> None:
    """Read at most the limit of eligible facts by identity, so a limit one above the cap of the contract shows that the rectangle holds more, within a second."""
    connection = service_transaction
    connection.execute(INSERT_SEEDED_FACTS_SQL, {"west": AREA_WEST, "south": AREA_SOUTH, "first_id": FIRST_SEEDED_OSM_ID, "last_number": SEEDED_FACT_COUNT - 1})

    started = time.perf_counter()
    one_above_cap = fetch_stored_facts_in_area(connection, AREA_SOUTH, AREA_WEST, AREA_NORTH, AREA_EAST, 1001)
    elapsed = time.perf_counter() - started
    at_cap = fetch_stored_facts_in_area(connection, AREA_SOUTH, AREA_WEST, AREA_NORTH, AREA_EAST, 1000)

    assert len(one_above_cap) == SEEDED_FACT_COUNT
    assert len(at_cap) == 1000
    assert [fact.id for fact in at_cap] == [fact.id for fact in one_above_cap[:1000]]
    assert [fact.id for fact in one_above_cap] == sorted(fact.id for fact in one_above_cap)
    assert elapsed < READ_TIME_BOUND_SECONDS


def test_votes_of_many_facts_come_in_one_read(service_transaction: Connection) -> None:
    """Read the votes of the 1000 facts of an area in one statement, each vote with its fact, and derive the same statuses as fact by fact."""
    connection = service_transaction
    last_id = FIRST_SEEDED_OSM_ID + SEEDED_FACT_COUNT - 2
    connection.execute(INSERT_SEEDED_FACTS_SQL, {"west": AREA_WEST, "south": AREA_SOUTH, "first_id": FIRST_SEEDED_OSM_ID, "last_number": SEEDED_FACT_COUNT - 2})
    connection.execute(INSERT_SEEDED_VOTES_SQL, {"persons": SEEDED_VOTE_PERSONS, "first_id": FIRST_SEEDED_OSM_ID, "last_id": last_id})
    facts = fetch_stored_facts_in_area(connection, AREA_SOUTH, AREA_WEST, AREA_NORTH, AREA_EAST, 1000)
    assert len(facts) == 1000

    spy = Mock(wraps=connection)
    votes = fetch_fact_votes(spy, [fact.id for fact in facts])

    assert spy.execute.call_count == 1
    assert len(votes) == 1000 * SEEDED_VOTE_PERSONS
    assert {vote.fact_id for vote in votes} == {fact.id for fact in facts}
    votes_by_fact: dict[int, list[StoredVote]] = defaultdict(list)
    for vote in votes:
        votes_by_fact[vote.fact_id].append(vote)
    statuses = {fact.id: resolve_fact_status(votes_by_fact[fact.id], fact.is_removed_from_osm) for fact in facts}
    for fact in facts:
        assert statuses[fact.id] == resolve_fact_status(fetch_fact_votes(connection, [fact.id]), fact.is_removed_from_osm)
    assert len({result.status for result in statuses.values()}) > 1


def test_flag_hide_and_restore_keep_first_instants_and_votes(service_transaction: Connection) -> None:
    """Flag, hide and restore a report: the first flag instant stays, both moderator writes repeat without a change, a hidden fact leaves every read but the list, and its votes survive."""
    connection = service_transaction
    reported = apply_report_north(connection, "moderation first", 100)
    second = apply_report_north(connection, "moderation second", 200)
    osm_id = apply_osm_fact(connection, 9300000121, 300)
    untouched = apply_report_north(connection, "moderation untouched", 400)
    votes_before = fetch_fact_votes(connection, [reported.id])
    first_flag = build_instant("2026-10-03T10:00:00.000+02:00")
    first_hiding = build_instant("2026-10-04T12:00:00.000+02:00")

    locked = fetch_stored_fact_for_change(connection, reported.id)
    assert locked is not None
    assert (locked.flagged_at, locked.is_hidden) == (None, False)
    flagged = apply_fact_flag(connection, reported.id, first_flag)
    assert (flagged.flagged_at, flagged.is_hidden) == (first_flag, False)
    apply_fact_flag(connection, second.id, build_instant("2026-10-04T11:00:00.000+02:00"))
    assert apply_fact_flag(connection, reported.id, build_instant("2026-10-05T09:00:00.000+02:00")).flagged_at == first_flag
    flagged_listing = [fact for fact in fetch_stored_flagged_facts(connection) if fact.id in {reported.id, second.id}]
    assert [(fact.id, fact.is_hidden) for fact in flagged_listing] == [(second.id, False), (reported.id, False)]
    assert flagged_listing[1].flagged_at == first_flag

    locked_osm = fetch_stored_fact_for_change(connection, osm_id)
    assert locked_osm is not None
    assert (locked_osm.source, locked_osm.flagged_at) == (FactSource.OPENSTREETMAP, None)
    osm_fact = fetch_stored_fact(connection, osm_id)
    assert osm_fact is not None
    assert osm_fact.flagged_at is None
    locked_untouched = fetch_stored_fact_for_change(connection, untouched.id)
    assert locked_untouched is not None
    assert (locked_untouched.flagged_at, locked_untouched.is_hidden) == (None, False)
    assert fetch_stored_fact(connection, untouched.id) == untouched

    hidden = apply_fact_hiding(connection, reported.id, first_hiding)
    assert (hidden.is_hidden, hidden.flagged_at) == (True, first_flag)
    assert apply_fact_hiding(connection, reported.id, build_instant("2026-10-05T10:00:00.000+02:00")) == hidden
    stored_hiding = connection.execute(FETCH_HIDDEN_INSTANT_SQL, {"fact_id": reported.id}).one()
    assert (stored_hiding.hidden_at, stored_hiding.hidden_at_utc_offset_minutes) == (first_hiding.instant, first_hiding.utc_offset_minutes)
    assert reported.id not in fetch_area_ids(connection)
    assert reported.id not in [item.fact.id for item in fetch_stored_nearby_facts(connection, FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON, 150)]
    assert fetch_stored_fact(connection, reported.id) is None
    for locked_hidden in (fetch_stored_fact_for_vote(connection, reported.id), fetch_stored_fact_for_change(connection, reported.id)):
        assert locked_hidden is not None
        assert locked_hidden.is_hidden is True
    still_listed = [fact for fact in fetch_stored_flagged_facts(connection) if fact.id == reported.id]
    assert [fact.is_hidden for fact in still_listed] == [True]

    restored = apply_fact_restoration(connection, reported.id)
    assert (restored.is_hidden, restored.flagged_at) == (False, first_flag)
    assert apply_fact_restoration(connection, reported.id) == restored
    assert reported.id in fetch_area_ids(connection)
    assert reported.id in [item.fact.id for item in fetch_stored_nearby_facts(connection, FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON, 150)]
    assert fetch_stored_fact(connection, reported.id) == restored
    assert fetch_fact_votes(connection, [reported.id]) == votes_before


def test_hiding_an_unflagged_fact_is_refused_by_the_database(service_transaction: Connection) -> None:
    """Leave the decision to the service layer and the last guard to the database: hiding a fact that was never flagged fails on ck_fact_hidden_only_flagged."""
    connection = service_transaction
    unflagged = apply_report_north(connection, "hide unflagged", 0)
    with pytest.raises(IntegrityError) as refused:
        apply_fact_hiding(connection, unflagged.id, build_instant("2026-10-04T12:00:00.000+02:00"))
    assert refused.value.orig.diag.constraint_name == "ck_fact_hidden_only_flagged"


def test_votes_of_a_deleted_account_stay_with_the_weight_of_an_account(service_transaction: Connection) -> None:
    """Delete an account with two votes: both stay on the fact without an account and with the weight of an account, each a person of its own for the status rule."""
    connection = service_transaction
    fact_id = apply_osm_fact(connection, 9300000131)
    account_id = apply_account(connection, "Usuniete konto")
    apply_vote_insert(connection, fact_id, VoteVerdict.CONFIRM, AccountVoter(account_id), build_instant("2026-10-02T10:00:00.000+02:00"))
    apply_vote_insert(connection, fact_id, VoteVerdict.CONFIRM, AccountVoter(account_id), build_instant("2026-10-03T10:00:00.000+02:00"))

    assert apply_account_delete(connection, account_id) is True

    votes = fetch_fact_votes(connection, [fact_id])
    assert [(vote.account_id, vote.is_cast_with_account, vote.verdict) for vote in votes] == [(None, True, VoteVerdict.CONFIRM)] * 2
    assert resolve_fact_status(votes, False).confirmations == 2.0


def test_vote_of_a_deleted_account_raises_its_own_error(service_transaction: Connection) -> None:
    """Store nothing for an account that no longer exists and raise the error of the layer, with no identifier in its text and none of the driver as its cause."""
    connection = service_transaction
    fact_id = apply_osm_fact(connection, 9300000132)
    account_id = apply_account(connection, "Usuniete konto 2")
    assert apply_account_delete(connection, account_id) is True

    with pytest.raises(VoteAccountMissingError) as raised, connection.begin_nested():
        apply_vote_insert(connection, fact_id, VoteVerdict.CONFIRM, AccountVoter(account_id), build_instant("2026-10-04T10:00:00.000+02:00"))

    assert str(account_id) not in str(raised.value)
    assert raised.value.__cause__ is None
    assert fetch_fact_votes(connection, [fact_id]) == ()


def test_reads_carry_no_person(service_transaction: Connection) -> None:
    """Return from every read and lock only the fields of a stored fact, with no author, account, voter hash or idempotency key in the records or their text."""
    connection = service_transaction
    account_id = apply_account(connection, "Autor z kontem")
    voter_hash = build_voter_hash("person hash")
    key = build_key("person hash")
    by_account = apply_report_north(connection, "person account", 10, author=AccountVoter(account_id))
    content = FactContent(FactType.STAIRS, *build_point(20), "invented person hash", None, None)
    created = apply_fact_insert(connection, content, key, CREATED_AT, AnonymousVoter(voter_hash))
    repeated = apply_fact_insert(connection, content, key, CREATED_AT, AnonymousVoter(voter_hash))
    apply_fact_flag(connection, created.fact.id, build_instant("2026-10-04T09:00:00.000+02:00"))
    fetched_detail = fetch_stored_fact(connection, by_account.id)
    assert fetched_detail is not None

    results = [
        created.fact,
        repeated.fact,
        fetched_detail,
        *fetch_stored_facts_in_area(connection, AREA_SOUTH, AREA_WEST, AREA_NORTH, AREA_EAST, 1001),
        *(item.fact for item in fetch_stored_nearby_facts(connection, FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON, 50)),
        *fetch_stored_flagged_facts(connection),
        fetch_stored_fact_for_vote(connection, by_account.id),
        fetch_stored_fact_for_change(connection, created.fact.id),
    ]

    assert len(results) > 8
    for fact in results:
        assert fact is not None
        assert {field.name for field in fields(fact)} == FACT_FIELD_NAMES
    text_of_results = " ".join(repr(fact) for fact in results)
    assert voter_hash.hex() not in text_of_results
    assert repr(voter_hash) not in text_of_results
    assert key.hex() not in text_of_results
    assert repr(key) not in text_of_results
