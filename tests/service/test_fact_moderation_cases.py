"""
Scenario tests of flagging, hiding and restoring with the data layer replaced at its seam: who can be flagged, the first flag
kept, only flagged facts hidden or restored, repeated actions harmless and a restored fact counting again with its votes
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-5; AC-12 and AC-13 of `COMMUNITY_FACTS_API_PRD.md`).
"""

from datetime import date, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict

from data.community_facts import AccountVoter
from service.actors import AccountActor
from service.community_facts import (
    FactNotFlaggableError,
    FactNotFlaggedError,
    FactNotFoundError,
    apply_fact_flag,
    apply_fact_hiding,
    apply_fact_restoration,
    apply_fact_vote,
    fetch_fact,
    fetch_facts_in_area,
    fetch_flagged_facts,
    fetch_nearby_facts,
)
from service.fact_rules import FactArea
from service.fact_status import FactStatus
from tests.service.common_community_fact_store import CZYZYNY_LAT, CZYZYNY_LON, WARSAW, InventedFactStore

OCTOBER_3 = datetime(2026, 10, 3, 18, 0, tzinfo=WARSAW)
OCTOBER_4 = datetime(2026, 10, 4, 9, 0, tzinfo=WARSAW)
AREA = FactArea(south=50.06, west=19.98, north=50.07, east=19.99)
ACCOUNT = AccountActor(account_id=503, pseudonym="Kula_KRK", is_moderator=False)


def apply_confirmed_votes(store: InventedFactStore, fact_id: int) -> None:
    """Give a fact two account confirmations, which make it confirmed."""
    store.add_vote(fact_id, VoteVerdict.CONFIRM, AccountVoter(501), OCTOBER_3)
    store.add_vote(fact_id, VoteVerdict.CONFIRM, AccountVoter(502), OCTOBER_3)


@pytest.mark.parametrize(
    "options",
    [{}, {"geozone_radius_m": 25, "fact_type": FactType.POOR_SURFACE}, {"osm_element_id": 9300000101}],
    ids=["report", "geozone", "converted-fact"],
)
def test_visible_user_content_is_flagged_and_keeps_its_first_flag(fact_store: InventedFactStore, options: dict[str, object]) -> None:
    fact_store.add_fact(1, **options)
    apply_fact_flag(1, OCTOBER_3)
    apply_fact_flag(1, OCTOBER_4)
    assert [(item.view.fact.id, item.flagged_on, item.is_hidden) for item in fetch_flagged_facts()] == [(1, date(2026, 10, 3), False)]


def test_fact_of_openstreetmap_cannot_be_flagged(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, source=FactSource.OPENSTREETMAP)
    with pytest.raises(FactNotFlaggableError):
        apply_fact_flag(1, OCTOBER_3)
    assert fact_store.facts[1].flagged_at is None


@pytest.mark.parametrize("is_existing", [True, False], ids=["hidden", "missing"])
def test_flag_of_a_hidden_or_missing_fact_is_missing(fact_store: InventedFactStore, is_existing: bool) -> None:
    if is_existing:
        fact_store.add_fact(1, is_hidden=True, flagged_at=OCTOBER_3)
    with pytest.raises(FactNotFoundError):
        apply_fact_flag(1, OCTOBER_4)
    assert not any(event[0] == "flag" for event in fact_store.events)


def test_hiding_a_flagged_confirmed_report_removes_it_from_every_public_operation(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    apply_confirmed_votes(fact_store, 1)
    apply_fact_flag(1, OCTOBER_3)
    item = apply_fact_hiding(1, OCTOBER_4)
    assert (item.view.fact.id, item.flagged_on, item.is_hidden, item.view.status.status) == (1, date(2026, 10, 3), True, FactStatus.CONFIRMED)
    assert fetch_facts_in_area(AREA).facts == ()
    assert fetch_nearby_facts(FactType.STAIRS, CZYZYNY_LAT, CZYZYNY_LON) == ()
    for refused in (lambda: fetch_fact(1), lambda: apply_fact_vote(1, VoteVerdict.DENY, ACCOUNT), lambda: apply_fact_flag(1, OCTOBER_4)):
        with pytest.raises(FactNotFoundError):
            refused()
    assert apply_fact_hiding(1, OCTOBER_4).is_hidden is True
    assert [item.is_hidden for item in fetch_flagged_facts()] == [True]


def test_restoring_brings_the_fact_back_with_the_votes_it_kept(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, is_hidden=True, flagged_at=OCTOBER_3)
    apply_confirmed_votes(fact_store, 1)
    item = apply_fact_restoration(1)
    assert (item.is_hidden, item.flagged_on, item.view.status.status, item.view.status.confirmations) == (False, date(2026, 10, 3), FactStatus.CONFIRMED, 2.0)
    assert [view.fact.id for view in fetch_facts_in_area(AREA).facts] == [1]
    assert apply_fact_restoration(1).is_hidden is False
    assert len(fact_store.votes) == 2


@pytest.mark.parametrize("action", [lambda: apply_fact_hiding(1, OCTOBER_4), lambda: apply_fact_restoration(1)], ids=["hide", "restore"])
def test_unflagged_fact_is_neither_hidden_nor_restored(fact_store: InventedFactStore, action) -> None:
    fact_store.add_fact(1)
    with pytest.raises(FactNotFlaggedError):
        action()
    assert not any(event[0] in ("hide", "restore") for event in fact_store.events)


@pytest.mark.parametrize("action", [lambda: apply_fact_hiding(1, OCTOBER_4), lambda: apply_fact_restoration(1)], ids=["hide", "restore"])
def test_missing_fact_is_not_found_by_a_moderator(fact_store: InventedFactStore, action) -> None:
    with pytest.raises(FactNotFoundError):
        action()


def test_moderation_locks_the_fact_before_it_decides(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, flagged_at=OCTOBER_3)
    apply_fact_hiding(1, OCTOBER_4)
    assert [event[0] for event in fact_store.events] == ["begin", "lock_for_change", "hide", "votes", "commit"]
