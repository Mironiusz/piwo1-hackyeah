"""
Scenario tests of saving a report or a geozone and of casting a vote with the data layer replaced at its seam: one save per
idempotency key, the confirmation of the author in the same transaction, the daily limit by the calendar day in Warsaw, the
shared identity of an IP address and User-Agent, the lock before any decision and an account deleted after its session was
resolved (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-4; AC-5 - AC-11 of `COMMUNITY_FACTS_API_PRD.md`).
"""

from dataclasses import replace
from datetime import date, datetime, timedelta
from uuid import UUID

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict

from data.community_facts import AccountVoter
from service.actors import AccountActor
from service.anonymous_voters import build_anonymous_voter_input
from service.community_facts import (
    FactNotFoundError,
    IdempotencyKeyReusedError,
    VoteTooSoonError,
    apply_fact_creation,
    apply_fact_vote,
    fetch_fact,
)
from service.fact_rules import FactCreationInput, InvalidFactInputError
from service.fact_status import FactStatus
from service.session_tokens import SessionExpiredError
from tests.service.common_community_fact_store import CZYZYNY_LAT, CZYZYNY_LON, WARSAW, InventedFactStore

KEY = UUID("6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40")
PERSON_A = build_anonymous_voter_input("203.0.113.7", "Mozilla/5.0 (invented)")
PERSON_B = build_anonymous_voter_input("::ffff:203.0.113.7", "Mozilla/5.0 (invented)")
PERSON_C = build_anonymous_voter_input("203.0.113.7", "Mozilla/5.0 (another invented)")
ACCOUNT_1 = AccountActor(account_id=501, pseudonym="Wózek_KRK", is_moderator=False)
ACCOUNT_2 = AccountActor(account_id=502, pseudonym="Laska_KRK", is_moderator=False)
SAVED_AT = datetime(2026, 10, 1, 9, 0, tzinfo=WARSAW)


def build_stairs(step_count: int | None = 3, description: str | None = "Three steps at the side entrance") -> FactCreationInput:
    """Build the request of a stairs report at the invented point of Czyżyny."""
    return FactCreationInput(FactType.STAIRS, CZYZYNY_LAT, CZYZYNY_LON, description, step_count, None)


def fetch_writes(store: InventedFactStore) -> list[str]:
    """Give the kinds of the recorded writes and block ends, in order."""
    return [str(event[0]) for event in store.events if event[0] in ("insert_fact", "insert_vote", "commit", "rollback")]


def test_first_save_creates_an_unverified_fact_with_the_confirmation_of_its_author(fact_store: InventedFactStore) -> None:
    result = apply_fact_creation(build_stairs(), KEY, PERSON_A, SAVED_AT)
    assert result.is_created is True
    assert (result.view.fact.fact_type, result.view.fact.step_count, result.view.fact.source) == (FactType.STAIRS, 3, FactSource.USER_REPORT)
    assert (result.view.status.status, result.view.status.confirmations, result.view.status.last_confirmed_on) == (FactStatus.UNVERIFIED, 0.5, date(2026, 10, 1))
    assert len(fact_store.facts) == 1 and len(fact_store.votes) == 1
    assert fact_store.votes[0].cast_at.utc_offset_minutes == 120
    assert fetch_writes(fact_store) == ["insert_fact", "insert_vote", "commit"]


def test_report_of_an_account_starts_with_the_weight_of_an_account(fact_store: InventedFactStore) -> None:
    assert apply_fact_creation(build_stairs(), KEY, ACCOUNT_1, SAVED_AT).view.status.confirmations == 1.0
    assert fact_store.votes[0].account_id == ACCOUNT_1.account_id


def test_repeated_save_with_the_same_content_answers_the_first_fact_and_stores_nothing(fact_store: InventedFactStore) -> None:
    first = apply_fact_creation(build_stairs(), KEY, PERSON_A, SAVED_AT)
    repeated = apply_fact_creation(build_stairs(description="  Three steps at the side entrance "), KEY, ACCOUNT_1, SAVED_AT + timedelta(minutes=5))
    assert repeated.is_created is False
    assert repeated.view == first.view
    assert len(fact_store.facts) == 1 and len(fact_store.votes) == 1


def test_repeated_key_with_another_content_is_refused_and_changes_nothing(fact_store: InventedFactStore) -> None:
    apply_fact_creation(build_stairs(), KEY, PERSON_A, SAVED_AT)
    with pytest.raises(IdempotencyKeyReusedError):
        apply_fact_creation(build_stairs(step_count=4), KEY, PERSON_A, SAVED_AT)
    assert [fact.step_count for fact in fact_store.facts.values()] == [3]
    assert len(fact_store.votes) == 1
    assert fetch_writes(fact_store)[-1] == "rollback"


@pytest.mark.parametrize("step_count", [3, 4], ids=["same-content", "other-content"])
def test_repeated_save_of_a_hidden_fact_is_missing_whatever_its_content(fact_store: InventedFactStore, step_count: int) -> None:
    created = apply_fact_creation(build_stairs(), KEY, PERSON_A, SAVED_AT)
    fact_store.facts[created.view.fact.id] = replace(created.view.fact, is_hidden=True)
    with pytest.raises(FactNotFoundError):
        apply_fact_creation(build_stairs(step_count=step_count), KEY, PERSON_A, SAVED_AT)


def test_input_outside_its_rules_opens_no_transaction(fact_store: InventedFactStore) -> None:
    with pytest.raises(InvalidFactInputError):
        apply_fact_creation(build_stairs(step_count=1000), KEY, PERSON_A, SAVED_AT)
    assert fact_store.events == []


@pytest.mark.parametrize("radius", [10, 25, 50, 100])
def test_barrier_geozone_is_saved_with_each_permitted_radius(fact_store: InventedFactStore, radius: int) -> None:
    request = FactCreationInput(FactType.POOR_SURFACE, CZYZYNY_LAT, CZYZYNY_LON, None, None, radius)
    assert apply_fact_creation(request, UUID(int=radius), PERSON_A, SAVED_AT).view.fact.geozone_radius_m == radius


def test_report_of_an_account_deleted_after_its_session_was_resolved_stores_nothing(fact_store: InventedFactStore) -> None:
    fact_store.deleted_accounts.add(ACCOUNT_1.account_id)
    with pytest.raises(SessionExpiredError):
        apply_fact_creation(build_stairs(), KEY, ACCOUNT_1, SAVED_AT)
    assert fact_store.facts == {} and fact_store.votes == [] and fact_store.keys == {}
    assert fetch_writes(fact_store)[-1] == "rollback"


def test_confirmations_progress_from_anonymous_to_two_accounts_and_a_denial_disputes(fact_store: InventedFactStore) -> None:
    fact_id = apply_fact_creation(build_stairs(), KEY, PERSON_A, SAVED_AT).view.fact.id
    fact_store.now = datetime(2026, 10, 2, 9, 0, tzinfo=WARSAW)
    first = apply_fact_vote(fact_id, VoteVerdict.CONFIRM, ACCOUNT_1)
    assert (first.status.confirmations, first.status.status) == (1.5, FactStatus.UNVERIFIED)
    second = apply_fact_vote(fact_id, VoteVerdict.CONFIRM, ACCOUNT_2)
    assert (second.status.confirmations, second.status.status) == (2.5, FactStatus.CONFIRMED)
    fact_store.now = datetime(2026, 10, 3, 9, 0, tzinfo=WARSAW)
    denied = apply_fact_vote(fact_id, VoteVerdict.DENY, ACCOUNT_1)
    assert (denied.status.confirmations, denied.status.denials, denied.status.status) == (1.5, 1.0, FactStatus.DISPUTED)
    assert denied.status.last_confirmed_on == date(2026, 10, 2)


def test_second_vote_of_one_day_is_refused_with_the_next_midnight(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    fact_store.now = datetime(2026, 10, 4, 23, 59, 59, 0, tzinfo=WARSAW)
    apply_fact_vote(1, VoteVerdict.CONFIRM, ACCOUNT_1)
    fact_store.now = datetime(2026, 10, 4, 23, 59, 59, 900000, tzinfo=WARSAW)
    with pytest.raises(VoteTooSoonError) as refusal:
        apply_fact_vote(1, VoteVerdict.DENY, ACCOUNT_1)
    assert refusal.value.repeat_allowed_at.isoformat(timespec="milliseconds") == "2026-10-05T00:00:00.000+02:00"
    assert len(fact_store.votes) == 1
    fact_store.now = datetime(2026, 10, 5, 0, 0, 0, 1000, tzinfo=WARSAW)
    assert apply_fact_vote(1, VoteVerdict.DENY, ACCOUNT_1).status.denials == 1.0
    with pytest.raises(VoteTooSoonError) as retry:
        apply_fact_vote(1, VoteVerdict.DENY, ACCOUNT_1)
    assert retry.value.repeat_allowed_at.isoformat(timespec="milliseconds") == "2026-10-06T00:00:00.000+02:00"


def test_same_address_and_user_agent_are_one_person_and_another_user_agent_is_another(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    apply_fact_vote(1, VoteVerdict.CONFIRM, PERSON_A)
    fact_store.now += timedelta(minutes=1)
    with pytest.raises(VoteTooSoonError):
        apply_fact_vote(1, VoteVerdict.CONFIRM, PERSON_B)
    assert apply_fact_vote(1, VoteVerdict.CONFIRM, PERSON_C).status.confirmations == 1.0
    fact_store.now += timedelta(days=1)
    after_midnight = apply_fact_vote(1, VoteVerdict.DENY, PERSON_B)
    assert (after_midnight.status.confirmations, after_midnight.status.denials) == (0.5, 0.5)


def test_vote_locks_its_fact_before_any_decision_and_reads_the_clock_after_the_wait(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    fact_store.now = datetime(2026, 10, 4, 23, 59, 30, tzinfo=WARSAW)
    fact_store.lock_wait = timedelta(seconds=45)
    apply_fact_vote(1, VoteVerdict.CONFIRM, ACCOUNT_1)
    kinds = [event[0] for event in fact_store.events]
    assert kinds == ["begin", "timeout", "lock_for_vote", "timeout", "clock", "insert_vote", "votes", "commit"]
    assert [event[1] for event in fact_store.events if event[0] == "timeout"] == [120000, 5000]
    assert fact_store.votes[0].cast_at.instant.astimezone(WARSAW).date() == date(2026, 10, 5)


@pytest.mark.parametrize("is_existing", [True, False], ids=["hidden", "missing"])
def test_vote_on_a_hidden_or_missing_fact_is_missing_after_the_lock(fact_store: InventedFactStore, is_existing: bool) -> None:
    if is_existing:
        fact_store.add_fact(1, is_hidden=True, flagged_at=SAVED_AT)
    with pytest.raises(FactNotFoundError):
        apply_fact_vote(1, VoteVerdict.CONFIRM, PERSON_A)
    assert [event[0] for event in fact_store.events][:3] == ["begin", "timeout", "lock_for_vote"]
    assert fact_store.votes == []


def test_vote_on_a_fact_of_openstreetmap_is_accepted_and_a_removed_one_stays_outdated(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, source=FactSource.OPENSTREETMAP)
    fact_store.add_fact(2, source=FactSource.OPENSTREETMAP, is_removed_from_osm=True)
    assert apply_fact_vote(1, VoteVerdict.CONFIRM, ACCOUNT_1).status.confirmations == 1.0
    assert apply_fact_vote(2, VoteVerdict.CONFIRM, ACCOUNT_1).status.status == FactStatus.OUTDATED


def test_vote_of_an_account_deleted_after_its_session_was_resolved_stores_nothing(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    fact_store.deleted_accounts.add(ACCOUNT_1.account_id)
    with pytest.raises(SessionExpiredError):
        apply_fact_vote(1, VoteVerdict.CONFIRM, ACCOUNT_1)
    assert fact_store.votes == []
    assert fetch_writes(fact_store)[-1] == "rollback"


def test_votes_of_a_deleted_account_keep_their_weight(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    fact_store.add_vote(1, VoteVerdict.CONFIRM, AccountVoter(501), SAVED_AT)
    fact_store.add_vote(1, VoteVerdict.CONFIRM, AccountVoter(502), SAVED_AT)
    fact_store.votes = [replace(vote, account_id=None) for vote in fact_store.votes]
    view = fetch_fact(1)
    assert (view.status.confirmations, view.status.status) == (2.0, FactStatus.CONFIRMED)
