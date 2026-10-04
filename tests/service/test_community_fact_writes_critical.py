"""
Critical tests of saving and voting through `service/community_facts.py` against the local database of `db/compose.yaml` with its chain applied.

They prove on stored data what the scenario tests prove on an invented seam: the report and the confirmation of its author stored together
with their offsets, the exact point compared on a repeated save, a changed content refused, a deleted account answered as an expired
session with nothing stored, one fact of concurrent saves with one key, the daily limit by the calendar day in Warsaw with the next
midnight, the identity of an IP address and User-Agent, one vote of concurrent votes of one person, and a vote that waits for the
publication of a fresh OpenStreetMap copy and counts its commit or its rollback (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md`
S-4; AC-5 - AC-11 and AC-14 of `COMMUNITY_FACTS_API_PRD.md`). Every committed row is registered for owner cleanup before its commit.
"""

from concurrent.futures import ThreadPoolExecutor, wait
from datetime import date
from uuid import UUID

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict
from sqlalchemy import text

from data.accounts import apply_account_delete
from data.engine import fetch_api_engine
from data.osm_copy import OsmFactChange, apply_osm_fact_changes, fetch_osm_fact_history, fetch_osm_facts_for_update
from service.community_facts import FactNotFoundError, IdempotencyKeyReusedError, VoteTooSoonError, apply_fact_creation, apply_fact_flag, apply_fact_hiding, apply_fact_vote, fetch_fact
from service.fact_rules import FactCreationInput
from service.fact_status import FactStatus
from service.session_tokens import SessionExpiredError
from tests.service.common_community_fact_seeds import (
    BLOCKED_SECONDS,
    COUNT_FACTS_BY_KEY_SQL,
    COUNT_VOTES_BY_FACT_SQL,
    COUNT_VOTES_BY_KEY_SQL,
    RELEASED_SECONDS,
    apply_account,
    apply_osm_fact,
    build_instant,
    build_person,
    build_point,
    fetch_count,
    register_report_cleanup,
)

pytestmark = pytest.mark.critical

EXACT_LAT, EXACT_LON = build_point(3.21)
FETCH_SAVED_INSTANTS_SQL = text(
    "SELECT fact.created_at, fact.created_at_utc_offset_minutes, vote.cast_at, vote.cast_at_utc_offset_minutes, vote.is_cast_with_account, octet_length(vote.voter_hash) "
    "FROM fact JOIN vote ON vote.fact_id = fact.id WHERE fact.idempotency_key = :key"
)
PERSON_A = build_person("Mozilla/5.0 (invented A)")
PERSON_B = build_person("Mozilla/5.0 (invented B)")


def build_stairs(step_count: int = 3, description: str | None = "  Trzy stopnie przy wejściu  ") -> FactCreationInput:
    """Build the request of a stairs report at the exact invented point."""
    return FactCreationInput(FactType.STAIRS, EXACT_LAT, EXACT_LON, description, step_count, None)


def apply_clock(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    """Set the business clock the vote reads after its lock."""
    monkeypatch.setattr("service.community_facts.fetch_business_now", lambda: build_instant(value))


@pytest.mark.parametrize(("key", "saved_at", "offset"), [(UUID(int=0x9301001), "2026-10-04T23:30:00.000+02:00", 120), (UUID(int=0x9301002), "2026-12-01T10:00:00.000+01:00", 60)])
def test_saved_report_keeps_its_point_its_offsets_and_the_vote_of_its_author(database_cleanup_registry, key: UUID, saved_at: str, offset: int) -> None:
    stored_key = register_report_cleanup(database_cleanup_registry, key)
    result = apply_fact_creation(build_stairs(), key, PERSON_A, build_instant(saved_at))
    assert result.is_created is True
    assert (result.view.fact.lat, result.view.fact.lon, result.view.fact.description, result.view.fact.source) == (EXACT_LAT, EXACT_LON, "Trzy stopnie przy wejściu", FactSource.USER_REPORT)
    assert (result.view.status.status, result.view.status.confirmations, result.view.status.last_confirmed_on) == (FactStatus.UNVERIFIED, 0.5, build_instant(saved_at).date())
    with database_cleanup_registry.owner_engine.connect() as connection:
        created_at, created_offset, cast_at, cast_offset, with_account, hash_length = connection.execute(FETCH_SAVED_INSTANTS_SQL, {"key": stored_key}).one()
    assert (created_at, created_offset, cast_at, cast_offset) == (build_instant(saved_at), offset, build_instant(saved_at), offset)
    assert (with_account, hash_length) == (False, 32)
    assert fetch_fact(result.view.fact.id) == result.view


def test_repeated_save_answers_the_first_fact_and_another_content_changes_nothing(database_cleanup_registry) -> None:
    key = UUID(int=0x9301003)
    stored_key = register_report_cleanup(database_cleanup_registry, key)
    first = apply_fact_creation(build_stairs(), key, PERSON_A, build_instant("2026-10-04T10:00:00.000+02:00"))
    repeated = apply_fact_creation(build_stairs(description="Trzy stopnie przy wejściu"), key, PERSON_B, build_instant("2026-10-04T10:05:00.000+02:00"))
    assert (repeated.is_created, repeated.view) == (False, first.view)
    with pytest.raises(IdempotencyKeyReusedError):
        apply_fact_creation(build_stairs(step_count=4), key, PERSON_A, build_instant("2026-10-04T10:06:00.000+02:00"))
    engine = fetch_api_engine()
    assert (fetch_count(engine, COUNT_FACTS_BY_KEY_SQL, {"key": stored_key}), fetch_count(engine, COUNT_VOTES_BY_KEY_SQL, {"key": stored_key})) == (1, 1)
    assert fetch_fact(first.view.fact.id).fact.step_count == 3


def test_repeated_save_of_a_hidden_report_is_missing(database_cleanup_registry) -> None:
    key = UUID(int=0x9301004)
    register_report_cleanup(database_cleanup_registry, key)
    fact_id = apply_fact_creation(build_stairs(), key, PERSON_A, build_instant("2026-10-04T10:00:00.000+02:00")).view.fact.id
    apply_fact_flag(fact_id, build_instant("2026-10-04T10:10:00.000+02:00"))
    apply_fact_hiding(fact_id, build_instant("2026-10-04T10:20:00.000+02:00"))
    with pytest.raises(FactNotFoundError):
        apply_fact_creation(build_stairs(), key, PERSON_A, build_instant("2026-10-04T10:30:00.000+02:00"))


def test_save_of_an_account_deleted_after_its_session_was_resolved_stores_nothing(database_cleanup_registry, stored_account_cleanup) -> None:
    key = UUID(int=0x9301005)
    stored_key = register_report_cleanup(database_cleanup_registry, key)
    engine = fetch_api_engine()
    actor = apply_account(engine, stored_account_cleanup, "Usuniety_9301005")
    with engine.begin() as connection:
        apply_account_delete(connection, actor.account_id)
    with pytest.raises(SessionExpiredError):
        apply_fact_creation(build_stairs(), key, actor, build_instant("2026-10-04T10:00:00.000+02:00"))
    assert fetch_count(engine, COUNT_FACTS_BY_KEY_SQL, {"key": stored_key}) == 0


def test_concurrent_saves_with_one_key_store_one_fact_and_one_vote(database_cleanup_registry) -> None:
    key = UUID(int=0x9301006)
    stored_key = register_report_cleanup(database_cleanup_registry, key)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda person: apply_fact_creation(build_stairs(), key, person, build_instant("2026-10-04T10:00:00.000+02:00")), [PERSON_A, PERSON_B] * 2))
    assert sorted(result.is_created for result in results) == [False, False, False, True]
    assert len({result.view.fact.id for result in results}) == 1
    engine = fetch_api_engine()
    assert (fetch_count(engine, COUNT_FACTS_BY_KEY_SQL, {"key": stored_key}), fetch_count(engine, COUNT_VOTES_BY_KEY_SQL, {"key": stored_key})) == (1, 1)


def test_daily_limit_follows_the_calendar_day_in_warsaw_and_one_address_and_user_agent_is_one_person(database_cleanup_registry, monkeypatch: pytest.MonkeyPatch) -> None:
    fact_id = apply_osm_fact(fetch_api_engine(), database_cleanup_registry, 9300100001, distance_m=40)
    apply_clock(monkeypatch, "2026-10-04T23:59:59.000+02:00")
    assert apply_fact_vote(fact_id, VoteVerdict.CONFIRM, PERSON_A).status.confirmations == 0.5
    apply_clock(monkeypatch, "2026-10-04T23:59:59.900+02:00")
    with pytest.raises(VoteTooSoonError) as refusal:
        apply_fact_vote(fact_id, VoteVerdict.DENY, build_person("Mozilla/5.0 (invented A)"))
    assert refusal.value.repeat_allowed_at.isoformat(timespec="milliseconds") == "2026-10-05T00:00:00.000+02:00"
    assert apply_fact_vote(fact_id, VoteVerdict.CONFIRM, PERSON_B).status.confirmations == 1.0
    apply_clock(monkeypatch, "2026-10-05T00:00:00.100+02:00")
    after_midnight = apply_fact_vote(fact_id, VoteVerdict.DENY, PERSON_A)
    assert (after_midnight.status.confirmations, after_midnight.status.denials, after_midnight.status.last_confirmed_on) == (0.5, 0.5, date(2026, 10, 4))
    with pytest.raises(VoteTooSoonError) as retry:
        apply_fact_vote(fact_id, VoteVerdict.DENY, PERSON_A)
    assert retry.value.repeat_allowed_at.isoformat(timespec="milliseconds") == "2026-10-06T00:00:00.000+02:00"
    assert fetch_count(fetch_api_engine(), COUNT_VOTES_BY_FACT_SQL, {"fact_id": fact_id}) == 3


def test_next_vote_after_the_autumn_clock_change_starts_at_midnight_of_winter_time(database_cleanup_registry, monkeypatch: pytest.MonkeyPatch) -> None:
    fact_id = apply_osm_fact(fetch_api_engine(), database_cleanup_registry, 9300100002, distance_m=45)
    apply_clock(monkeypatch, "2026-10-25T23:00:00.000+01:00")
    apply_fact_vote(fact_id, VoteVerdict.CONFIRM, PERSON_A)
    with pytest.raises(VoteTooSoonError) as refusal:
        apply_fact_vote(fact_id, VoteVerdict.CONFIRM, PERSON_A)
    assert refusal.value.repeat_allowed_at.isoformat(timespec="milliseconds") == "2026-10-26T00:00:00.000+01:00"


def test_concurrent_votes_of_one_person_on_one_day_store_one(database_cleanup_registry, monkeypatch: pytest.MonkeyPatch) -> None:
    fact_id = apply_osm_fact(fetch_api_engine(), database_cleanup_registry, 9300100003, distance_m=50)
    apply_clock(monkeypatch, "2026-10-04T12:00:00.000+02:00")

    def apply_one_vote(_number: int) -> str:
        """Cast the same confirmation and name its outcome."""
        try:
            apply_fact_vote(fact_id, VoteVerdict.CONFIRM, PERSON_A)
        except VoteTooSoonError:
            return "refused"
        return "stored"

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = sorted(pool.map(apply_one_vote, range(4)))
    assert outcomes == ["refused", "refused", "refused", "stored"]
    assert fetch_count(fetch_api_engine(), COUNT_VOTES_BY_FACT_SQL, {"fact_id": fact_id}) == 1


@pytest.mark.parametrize(("element_id", "publication_commits", "status"), [(9300100004, True, FactStatus.OUTDATED), (9300100005, False, FactStatus.DISPUTED)], ids=["commit", "rollback"])
def test_vote_waits_for_a_publication_and_counts_its_outcome(
    database_cleanup_registry, stored_account_cleanup, monkeypatch: pytest.MonkeyPatch, element_id: int, publication_commits: bool, status: FactStatus
) -> None:
    engine = fetch_api_engine()
    fact_id = apply_osm_fact(engine, database_cleanup_registry, element_id, distance_m=60)
    first, second, third = (apply_account(engine, stored_account_cleanup, f"Konto_{name}_{element_id}") for name in "ABC")
    apply_clock(monkeypatch, "2026-10-03T09:00:00.000+02:00")
    apply_fact_vote(fact_id, VoteVerdict.CONFIRM, first)
    apply_fact_vote(fact_id, VoteVerdict.DENY, second)
    apply_clock(monkeypatch, "2026-10-04T03:00:02.000+02:00")
    with engine.connect() as publication, ThreadPoolExecutor(max_workers=1) as pool:
        transaction = publication.begin()
        fetch_osm_facts_for_update(publication, [fact_id])
        fetch_osm_fact_history(publication, [fact_id])
        pending = pool.submit(apply_fact_vote, fact_id, VoteVerdict.CONFIRM, third)
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        if publication_commits:
            apply_osm_fact_changes(publication, [OsmFactChange(fact_id, FactSource.OPENSTREETMAP, True)])
            transaction.commit()
        else:
            transaction.rollback()
        view = pending.result(timeout=RELEASED_SECONDS)
    assert (view.status.status, view.fact.is_removed_from_osm) == (status, publication_commits)
    assert (view.status.confirmations, view.status.denials) == (2.0, 1.0)
    assert fetch_fact(fact_id) == view


def test_votes_of_a_deleted_account_keep_their_weight(database_cleanup_registry, stored_account_cleanup, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = fetch_api_engine()
    fact_id = apply_osm_fact(engine, database_cleanup_registry, 9300100006, distance_m=70)
    first, second = (apply_account(engine, stored_account_cleanup, f"Konto_{name}_9300100006") for name in "AB")
    apply_clock(monkeypatch, "2026-10-04T12:00:00.000+02:00")
    apply_fact_vote(fact_id, VoteVerdict.CONFIRM, first)
    assert apply_fact_vote(fact_id, VoteVerdict.CONFIRM, second).status.status == FactStatus.CONFIRMED
    with engine.begin() as connection:
        apply_account_delete(connection, first.account_id)
    view = fetch_fact(fact_id)
    assert (view.status.status, view.status.confirmations) == (FactStatus.CONFIRMED, 2.0)
    with pytest.raises(SessionExpiredError):
        apply_fact_vote(fact_id, VoteVerdict.DENY, first)
