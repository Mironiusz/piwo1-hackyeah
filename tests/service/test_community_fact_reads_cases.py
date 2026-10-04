"""
Scenario tests of the four reads of the community facts with the data layer replaced at its seam: the area with its cap of
1000 facts, one fact by identifier, the nearby check and the moderator list, each with statuses derived from the votes of each
fact and the facts and votes of one snapshot (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-3; AC-2 - AC-4 and the
moderator side of AC-13 of `COMMUNITY_FACTS_API_PRD.md`).
"""

from datetime import UTC, date, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict

from data.community_facts import AccountVoter, AnonymousVoter
from service.community_facts import FactNotFoundError, fetch_fact, fetch_facts_in_area, fetch_flagged_facts, fetch_nearby_facts
from service.fact_rules import FactArea
from service.fact_status import FactStatus
from tests.service.common_community_fact_store import CZYZYNY_LAT, CZYZYNY_LON, WARSAW, InventedFactStore, build_point_north

AREA = FactArea(south=50.06, west=19.98, north=50.07, east=19.99)
EARLIER = datetime(2026, 10, 1, 9, 0, tzinfo=WARSAW)


def apply_outdated_votes(store: InventedFactStore, fact_id: int) -> None:
    """Give a fact two account denials, which make it outdated by M4."""
    store.add_vote(fact_id, VoteVerdict.DENY, AccountVoter(501), EARLIER)
    store.add_vote(fact_id, VoteVerdict.DENY, AccountVoter(502), EARLIER)


def test_area_holds_unverified_and_ordinary_outdated_facts_but_neither_hidden_nor_removed(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    fact_store.add_vote(1, VoteVerdict.CONFIRM, AnonymousVoter(b"a" * 32), EARLIER)
    fact_store.add_fact(2)
    apply_outdated_votes(fact_store, 2)
    fact_store.add_fact(3, is_hidden=True, flagged_at=EARLIER)
    fact_store.add_fact(4, source=FactSource.OPENSTREETMAP, is_removed_from_osm=True)
    fact_store.add_fact(5, geozone_radius_m=100)
    area = fetch_facts_in_area(AREA)
    assert [(view.fact.id, view.status.status) for view in area.facts] == [(1, FactStatus.UNVERIFIED), (2, FactStatus.OUTDATED), (5, FactStatus.UNVERIFIED)]
    assert area.is_truncated is False


def test_area_takes_facts_and_votes_from_one_snapshot_in_one_read(fact_store: InventedFactStore) -> None:
    for fact_id in (1, 2, 3):
        fact_store.add_fact(fact_id)
    fetch_facts_in_area(AREA)
    reads = [event for event in fact_store.events if event[0] in ("area", "votes")]
    assert len(reads) == 2
    assert reads[0][1] == reads[1][1]
    assert reads[0][1].kind == "snapshot"
    assert reads[0][2] == 1001
    assert reads[1][2] == (1, 2, 3)


@pytest.mark.parametrize(("count", "shown", "is_truncated"), [(1000, 1000, False), (1001, 1000, True)])
def test_area_shows_at_most_1000_facts_and_says_when_it_holds_more(fact_store: InventedFactStore, count: int, shown: int, is_truncated: bool) -> None:
    for fact_id in range(1, count + 1):
        fact_store.add_fact(fact_id)
    area = fetch_facts_in_area(AREA)
    assert len(area.facts) == shown
    assert area.is_truncated is is_truncated
    votes_read = [event for event in fact_store.events if event[0] == "votes"]
    assert len(votes_read) == 1
    assert len(votes_read[0][2]) == shown


def test_status_of_each_fact_comes_from_its_own_votes(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    fact_store.add_vote(1, VoteVerdict.CONFIRM, AccountVoter(501), EARLIER)
    fact_store.add_vote(1, VoteVerdict.CONFIRM, AccountVoter(502), EARLIER)
    fact_store.add_fact(2)
    fact_store.add_vote(2, VoteVerdict.CONFIRM, AccountVoter(501), EARLIER)
    fact_store.add_vote(2, VoteVerdict.DENY, AccountVoter(502), EARLIER)
    fact_store.add_fact(3)
    statuses = {view.fact.id: (view.status.status, view.status.last_confirmed_on) for view in fetch_facts_in_area(AREA).facts}
    assert statuses == {1: (FactStatus.CONFIRMED, date(2026, 10, 1)), 2: (FactStatus.DISPUTED, date(2026, 10, 1)), 3: (FactStatus.UNVERIFIED, None)}


def test_ordinary_outdated_and_removed_facts_can_be_read_by_identifier(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1)
    apply_outdated_votes(fact_store, 1)
    fact_store.add_fact(2, source=FactSource.OPENSTREETMAP, is_removed_from_osm=True)
    assert fetch_fact(1).status.status == FactStatus.OUTDATED
    removed = fetch_fact(2)
    assert removed.status.status == FactStatus.OUTDATED
    assert removed.fact.is_removed_from_osm is True


@pytest.mark.parametrize("is_existing", [True, False], ids=["hidden", "missing"])
def test_hidden_or_missing_fact_is_not_found_by_identifier(fact_store: InventedFactStore, is_existing: bool) -> None:
    if is_existing:
        fact_store.add_fact(1, is_hidden=True, flagged_at=EARLIER)
    with pytest.raises(FactNotFoundError):
        fetch_fact(1)
    assert not any(event[0] == "votes" for event in fact_store.events)


def test_nearby_check_finds_the_same_type_within_15_metres_nearest_first_in_whole_metres(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, lat=build_point_north(12.6))
    fact_store.add_fact(2, lat=build_point_north(8.2))
    apply_outdated_votes(fact_store, 2)
    fact_store.add_fact(3, lat=build_point_north(8.0), fact_type=FactType.HIGH_KERB)
    fact_store.add_fact(4, lat=build_point_north(3.0), is_hidden=True, flagged_at=EARLIER)
    fact_store.add_fact(5, lat=build_point_north(5.0), source=FactSource.OPENSTREETMAP, is_removed_from_osm=True)
    fact_store.add_fact(6, lat=build_point_north(15.4))
    fact_store.add_fact(7, lat=build_point_north(1.0), source=FactSource.OPENSTREETMAP)
    nearby = fetch_nearby_facts(FactType.STAIRS, CZYZYNY_LAT, CZYZYNY_LON)
    assert [(item.view.fact.id, item.distance_m) for item in nearby] == [(7, 1), (2, 8), (1, 13)]
    assert nearby[1].view.status.status == FactStatus.OUTDATED
    assert [event[2] for event in fact_store.events if event[0] == "nearby"] == [15.0]


def test_moderator_list_holds_every_flagged_fact_the_latest_flag_first(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, flagged_at=datetime(2026, 10, 2, 12, 0, tzinfo=WARSAW))
    fact_store.add_fact(2, flagged_at=datetime(2026, 10, 4, 1, 30, tzinfo=WARSAW), is_hidden=True)
    fact_store.add_fact(3)
    fact_store.add_vote(1, VoteVerdict.CONFIRM, AccountVoter(501), EARLIER)
    items = fetch_flagged_facts()
    assert [(item.view.fact.id, item.flagged_on, item.is_hidden) for item in items] == [(2, date(2026, 10, 4), True), (1, date(2026, 10, 2), False)]
    assert items[1].view.status.last_confirmed_on == date(2026, 10, 1)


def test_flag_day_is_the_calendar_day_in_warsaw(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, flagged_at=datetime(2026, 10, 3, 21, 30, tzinfo=UTC))
    fact_store.add_fact(2, flagged_at=datetime(2026, 10, 3, 22, 30, tzinfo=UTC))
    assert {item.view.fact.id: item.flagged_on for item in fetch_flagged_facts()} == {1: date(2026, 10, 3), 2: date(2026, 10, 4)}


def test_hidden_fact_is_on_the_moderator_list_and_missing_everywhere_public(fact_store: InventedFactStore) -> None:
    fact_store.add_fact(1, is_hidden=True, flagged_at=EARLIER)
    assert [item.view.fact.id for item in fetch_flagged_facts()] == [1]
    assert fetch_facts_in_area(AREA).facts == ()
    assert fetch_nearby_facts(FactType.STAIRS, CZYZYNY_LAT, CZYZYNY_LON) == ()
    with pytest.raises(FactNotFoundError):
        fetch_fact(1)
