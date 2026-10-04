"""Check which stored facts a fresh copy makes disappear for the first time, and what each of them becomes by M4."""

from datetime import UTC, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import build_offset_instant

from data.osm_copy import OsmFactChange, OsmFactIdentity, OsmStoredFact, OsmVoteSnapshot
from service.osm_reconciliation import resolve_osm_disappearing_facts, resolve_osm_fact_changes

STAIRS = OsmFactIdentity(OsmElementType.WAY, 10, FactType.STAIRS)
BENCH = OsmFactIdentity(OsmElementType.NODE, 20, FactType.REST_PLACE)


def test_first_import_has_nothing_to_reconcile():
    assert resolve_osm_disappearing_facts((), (STAIRS, BENCH)) == ()


def test_facts_still_present_do_not_disappear():
    stored = (OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False),)
    assert resolve_osm_disappearing_facts(stored, (STAIRS,)) == ()


def test_present_fact_missing_from_the_fresh_copy_disappears():
    fact = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    assert resolve_osm_disappearing_facts((fact,), (BENCH,)) == (fact,)


def test_converted_and_removed_facts_that_stay_absent_need_no_decision():
    converted = OsmStoredFact(1, STAIRS, FactSource.USER_REPORT, False)
    removed = OsmStoredFact(2, BENCH, FactSource.OPENSTREETMAP, True)
    assert resolve_osm_disappearing_facts((converted, removed), ()) == ()


def test_returning_converted_and_removed_facts_need_no_decision():
    converted = OsmStoredFact(1, STAIRS, FactSource.USER_REPORT, False)
    removed = OsmStoredFact(2, BENCH, FactSource.OPENSTREETMAP, True)
    assert resolve_osm_disappearing_facts((converted, removed), (STAIRS, BENCH)) == ()


def test_a_split_way_with_a_new_identity_does_not_inherit_the_old_fact():
    old = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    split = OsmFactIdentity(OsmElementType.WAY, 11, FactType.STAIRS)
    assert resolve_osm_disappearing_facts((old,), (split,)) == (old,)


def test_another_fact_type_on_the_same_element_is_another_identity():
    fact = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    ramp = OsmFactIdentity(OsmElementType.WAY, 10, FactType.RAMP)
    assert resolve_osm_disappearing_facts((fact,), (ramp,)) == (fact,)


CONFIRM = VoteVerdict.CONFIRM
DENY = VoteVerdict.DENY
CONVERTED = OsmFactChange(1, FactSource.USER_REPORT, False)
REMOVED = OsmFactChange(1, FactSource.OPENSTREETMAP, True)


def build_votes(*votes: tuple[VoteVerdict, int | None, bytes | None, bool], fact_id: int = 1) -> tuple[OsmVoteSnapshot, ...]:
    """Build invented votes cast one hour apart in the given order: verdict, account, hash and whether cast with an account."""
    return tuple(
        OsmVoteSnapshot(index, fact_id, verdict, with_account, build_offset_instant(datetime(2026, 10, 3, index, tzinfo=UTC)), account_id, voter_hash)
        for index, (verdict, account_id, voter_hash, with_account) in enumerate(votes, 1)
    )


def build_anonymous(verdict: VoteVerdict, person: int) -> tuple[VoteVerdict, int | None, bytes | None, bool]:
    """Describe a vote of an invented person without an account, weighing 0.5."""
    return (verdict, None, bytes([person]) * 32, False)


def build_account(verdict: VoteVerdict, account_id: int) -> tuple[VoteVerdict, int | None, bytes | None, bool]:
    """Describe a vote cast with an invented account, weighing 1."""
    return (verdict, account_id, None, True)


DETACHED_CONFIRM = (CONFIRM, None, None, True)


@pytest.mark.usefixtures("runtime_settings")
@pytest.mark.parametrize(
    ("votes", "expected"),
    [
        pytest.param(build_votes(build_account(CONFIRM, 10), build_anonymous(CONFIRM, 1), build_anonymous(DENY, 2)), CONVERTED, id="1.5 against 0.5 converts"),
        pytest.param(build_votes(build_anonymous(CONFIRM, 1)), CONVERTED, id="a confirmation total below 2 still converts"),
        pytest.param((), REMOVED, id="no votes removes"),
        pytest.param(build_votes(build_anonymous(DENY, 1), build_account(DENY, 10)), REMOVED, id="only denials remove"),
        pytest.param(build_votes(build_anonymous(CONFIRM, 1), build_anonymous(DENY, 2)), REMOVED, id="a tie of 0.5 against 0.5 removes"),
        pytest.param(build_votes(build_anonymous(DENY, 1), build_anonymous(CONFIRM, 1)), CONVERTED, id="the latest vote of a person replaces the older one"),
        pytest.param(
            build_votes(build_account(CONFIRM, 10), build_anonymous(CONFIRM, 2), build_anonymous(CONFIRM, 3), build_anonymous(DENY, 4), build_anonymous(DENY, 5), build_anonymous(DENY, 6)),
            REMOVED,
            id="a person outside the five most recent does not count",
        ),
        pytest.param(build_votes(DETACHED_CONFIRM, DETACHED_CONFIRM, build_account(DENY, 10)), CONVERTED, id="detached votes keep weight 1 and are separate persons"),
    ],
)
def test_a_disappearing_fact_becomes_a_user_fact_only_when_confirmations_outweigh_denials(votes, expected):
    fact = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    assert resolve_osm_fact_changes((fact,), votes) == (expected,)


@pytest.mark.usefixtures("runtime_settings")
def test_each_fact_is_decided_by_its_own_votes_only():
    stairs = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    bench = OsmStoredFact(2, BENCH, FactSource.OPENSTREETMAP, False)
    votes = build_votes(build_account(CONFIRM, 10), fact_id=2)
    assert resolve_osm_fact_changes((stairs, bench), votes) == (REMOVED, OsmFactChange(2, FactSource.USER_REPORT, False))
