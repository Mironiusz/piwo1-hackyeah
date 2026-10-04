"""Check the status rule of M4 on the scenarios of the shape of community_facts and on its edge cases."""

from datetime import UTC, date, datetime, timedelta, timezone

import pytest
from accessibility_db.closed_lists import VoteVerdict
from accessibility_db.tables import build_offset_instant

from data.route_facts import StoredVote
from service.fact_status import FactStatus, FactStatusResult, resolve_fact_status

pytestmark = pytest.mark.usefixtures("runtime_settings")

WARSAW_SUMMER = timezone(timedelta(hours=2))
HASH_H1 = b"\x01" * 32
HASH_H2 = b"\x02" * 32


def build_vote(vote_id: int, verdict: VoteVerdict, cast_at: datetime, account_id: int | None = None, voter_hash: bytes | None = None, with_account: bool | None = None) -> StoredVote:
    """Build one invented vote; a vote with an account weighs 1 and one with a hash 0.5, unless with_account says otherwise."""
    is_cast_with_account = account_id is not None if with_account is None else with_account
    return StoredVote(vote_id, 1, verdict, is_cast_with_account, build_offset_instant(cast_at), account_id, voter_hash)


def build_warsaw(day: int, hour: int, minute: int = 0) -> datetime:
    """Build an instant of October 2026 in the summer offset of Europe/Warsaw."""
    return datetime(2026, 10, day, hour, minute, tzinfo=WARSAW_SUMMER)


def test_scenario_two_statuses_of_a_report_step_by_step() -> None:
    """Follow the report of H1 through the votes of A - E as scenario 2 of the shape of community_facts states."""
    votes = [build_vote(1, VoteVerdict.CONFIRM, build_warsaw(1, 10), voter_hash=HASH_H1)]
    expected = [
        (build_vote(2, VoteVerdict.CONFIRM, build_warsaw(1, 12), account_id=10), FactStatus.UNVERIFIED, 1.5, 0.0),
        (build_vote(3, VoteVerdict.CONFIRM, build_warsaw(2, 9), account_id=11), FactStatus.CONFIRMED, 2.5, 0.0),
        (build_vote(4, VoteVerdict.DENY, build_warsaw(2, 18), account_id=12), FactStatus.DISPUTED, 2.5, 1.0),
        (build_vote(5, VoteVerdict.DENY, build_warsaw(3, 9), account_id=13), FactStatus.DISPUTED, 2.5, 2.0),
        (build_vote(6, VoteVerdict.DENY, build_warsaw(3, 12), account_id=14), FactStatus.OUTDATED, 2.0, 3.0),
    ]
    for vote, status, confirmations, denials in expected:
        votes.append(vote)
        result = resolve_fact_status(votes, False)
        assert (result.status, result.confirmations, result.denials) == (status, confirmations, denials)
    assert resolve_fact_status(votes, False).last_confirmed_on == date(2026, 10, 2)


def test_scenario_seven_sums_for_the_publication() -> None:
    """Give G 1.0 against 0.5 and J 1.0 against 1.0, the sums the publication compares."""
    fact_g = [build_vote(1, VoteVerdict.CONFIRM, build_warsaw(2, 9), account_id=10), build_vote(2, VoteVerdict.DENY, build_warsaw(2, 10), voter_hash=HASH_H2)]
    fact_j = [build_vote(3, VoteVerdict.CONFIRM, build_warsaw(2, 9), account_id=10), build_vote(4, VoteVerdict.DENY, build_warsaw(2, 10), account_id=11)]
    assert (resolve_fact_status(fact_g, False).confirmations, resolve_fact_status(fact_g, False).denials) == (1.0, 0.5)
    assert (resolve_fact_status(fact_j, False).confirmations, resolve_fact_status(fact_j, False).denials) == (1.0, 1.0)


def test_scenario_eight_votes_of_a_deleted_account_count_as_persons_of_their_own() -> None:
    """Count two confirmations of account A once while it exists and twice after it is deleted."""
    before = [build_vote(1, VoteVerdict.CONFIRM, build_warsaw(2, 9), account_id=10), build_vote(2, VoteVerdict.CONFIRM, build_warsaw(3, 9), account_id=10)]
    after = [build_vote(1, VoteVerdict.CONFIRM, build_warsaw(2, 9), with_account=True), build_vote(2, VoteVerdict.CONFIRM, build_warsaw(3, 9), with_account=True)]
    assert resolve_fact_status(before, False) == FactStatusResult(FactStatus.UNVERIFIED, 1.0, 0.0, date(2026, 10, 3))
    assert resolve_fact_status(after, False) == FactStatusResult(FactStatus.CONFIRMED, 2.0, 0.0, date(2026, 10, 3))


def test_openstreetmap_fact_without_votes_is_unverified() -> None:
    """Give a fact nobody voted on the status unverified, sums of 0 and no day of confirmation."""
    assert resolve_fact_status([], False) == FactStatusResult(FactStatus.UNVERIFIED, 0.0, 0.0, None)


def test_removed_fact_is_outdated_and_keeps_its_sums() -> None:
    """Make a fact removed in OpenStreetMap outdated with its three confirmations still summed."""
    votes = [build_vote(index, VoteVerdict.CONFIRM, build_warsaw(2, 9 + index), account_id=10 + index) for index in range(3)]
    result = resolve_fact_status(votes, True)
    assert (result.status, result.confirmations, result.denials) == (FactStatus.OUTDATED, 3.0, 0.0)


def test_report_with_only_the_confirmation_of_its_author_has_that_day() -> None:
    """Give a report confirmed only by its author on 1 October that day as the day of its latest confirmation."""
    result = resolve_fact_status([build_vote(1, VoteVerdict.CONFIRM, build_warsaw(1, 10), voter_hash=HASH_H1)], False)
    assert result == FactStatusResult(FactStatus.UNVERIFIED, 0.5, 0.0, date(2026, 10, 1))


def test_person_voting_twice_counts_once_with_the_later_vote() -> None:
    """Count only the later denial of an account that first confirmed, so no weight is added by voting again."""
    votes = [build_vote(1, VoteVerdict.CONFIRM, build_warsaw(1, 10), account_id=10), build_vote(2, VoteVerdict.DENY, build_warsaw(2, 10), account_id=10)]
    result = resolve_fact_status(votes, False)
    assert (result.status, result.confirmations, result.denials) == (FactStatus.UNVERIFIED, 0.0, 1.0)
    assert result.last_confirmed_on == date(2026, 10, 1)


def test_six_persons_leave_the_first_out_of_the_window() -> None:
    """Leave the denial of the earliest of six persons out, so five confirmations make the fact confirmed and not disputed."""
    votes = [build_vote(1, VoteVerdict.DENY, build_warsaw(1, 8), account_id=99)]
    votes += [build_vote(index + 2, VoteVerdict.CONFIRM, build_warsaw(1, 9 + index), account_id=10 + index) for index in range(5)]
    assert resolve_fact_status(votes, False) == FactStatusResult(FactStatus.CONFIRMED, 5.0, 0.0, date(2026, 10, 1))
    assert resolve_fact_status(votes[:5], False).status == FactStatus.DISPUTED


def test_two_votes_with_the_same_instant_order_by_identity() -> None:
    """Take the later stored of two votes of one person with the same instant as the one that counts."""
    instant = build_warsaw(2, 9)
    votes = [build_vote(2, VoteVerdict.CONFIRM, instant, account_id=10), build_vote(1, VoteVerdict.DENY, instant, account_id=10)]
    result = resolve_fact_status(votes, False)
    assert (result.confirmations, result.denials) == (1.0, 0.0)


def test_day_of_confirmation_is_the_warsaw_day() -> None:
    """Give a confirmation at 23:30 UTC on 3 October the day 4 October."""
    result = resolve_fact_status([build_vote(1, VoteVerdict.CONFIRM, datetime(2026, 10, 3, 23, 30, tzinfo=UTC), account_id=10)], False)
    assert result.last_confirmed_on == date(2026, 10, 4)


def test_denials_that_do_not_outweigh_keep_the_fact_disputed() -> None:
    """Keep two denials against two confirmations disputed, because outdated needs the denials to outweigh."""
    votes = [build_vote(index + 1, VoteVerdict.CONFIRM if index < 2 else VoteVerdict.DENY, build_warsaw(1, 9 + index), account_id=10 + index) for index in range(4)]
    assert resolve_fact_status(votes, False).status == FactStatus.DISPUTED
