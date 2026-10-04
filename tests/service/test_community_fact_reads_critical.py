"""
Critical test of the visibility of the community facts through `service/community_facts.py` against the local database of `db/compose.yaml`.

One invented neighbourhood holds an unverified report, an ordinary outdated report, a hidden report, a fact removed in OpenStreetMap, a
geozone, a report of another type and a report too far away, and the matrix checks each read on both sides: the area, a fact by
identifier, the nearby check and the moderator list (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-3; AC-2 - AC-4 and the
moderator side of AC-13 of `COMMUNITY_FACTS_API_PRD.md`). Every committed row is registered for owner cleanup before its commit.
"""

from datetime import date
from uuid import UUID

import pytest
from accessibility_db.closed_lists import FactType, VoteVerdict

from data.engine import fetch_api_engine
from service.community_facts import (
    FactNotFoundError,
    apply_fact_creation,
    apply_fact_flag,
    apply_fact_hiding,
    apply_fact_vote,
    fetch_fact,
    fetch_facts_in_area,
    fetch_flagged_facts,
    fetch_nearby_facts,
)
from service.fact_rules import FactCreationInput, resolve_fact_area
from service.fact_status import FactStatus
from tests.service.common_community_fact_seeds import ORIGIN_LAT, ORIGIN_LON, apply_osm_fact, build_instant, build_person, build_point, register_report_cleanup

pytestmark = pytest.mark.critical

AUTHOR = build_person("Mozilla/5.0 (invented author)")
SAVED_AT = build_instant("2026-10-02T10:00:00.000+02:00")


def apply_report(registry, number: int, distance_m: float, fact_type: FactType = FactType.STAIRS, radius: int | None = None) -> int:
    """Save an invented report the given distance north of the origin through the service, registered for cleanup first, and give its identity."""
    key = UUID(int=0x9302000 + number)
    register_report_cleanup(registry, key)
    lat, lon = build_point(distance_m)
    return apply_fact_creation(FactCreationInput(fact_type, lat, lon, None, None, radius), key, AUTHOR, SAVED_AT).view.fact.id


def test_each_read_shows_exactly_the_facts_its_rule_allows(database_cleanup_registry, monkeypatch: pytest.MonkeyPatch) -> None:
    unverified = apply_report(database_cleanup_registry, 1, 3.0)
    outdated = apply_report(database_cleanup_registry, 2, 8.0)
    monkeypatch.setattr("service.community_facts.fetch_business_now", lambda: build_instant("2026-10-03T10:00:00.000+02:00"))
    for user_agent in ("one", "two", "three", "four"):
        apply_fact_vote(outdated, VoteVerdict.DENY, build_person(f"Mozilla/5.0 (invented {user_agent})"))
    hidden = apply_report(database_cleanup_registry, 3, 5.0)
    apply_fact_flag(hidden, build_instant("2026-10-03T21:30:00.000+02:00"))
    apply_fact_hiding(hidden, build_instant("2026-10-04T09:00:00.000+02:00"))
    removed = apply_osm_fact(fetch_api_engine(), database_cleanup_registry, 9300200001, distance_m=6.0, removed=True)
    geozone = apply_report(database_cleanup_registry, 4, 30.0, FactType.POOR_SURFACE, 100)
    other_type = apply_report(database_cleanup_registry, 5, 2.0, FactType.HIGH_KERB)
    too_far = apply_report(database_cleanup_registry, 6, 20.0)

    north_lat, _north_lon = build_point(40.0)
    area = fetch_facts_in_area(resolve_fact_area(ORIGIN_LAT - 0.0001, ORIGIN_LON - 0.0001, north_lat, ORIGIN_LON + 0.0001))
    assert sorted(view.fact.id for view in area.facts) == sorted([unverified, outdated, geozone, other_type, too_far])
    assert area.is_truncated is False
    assert {view.fact.id: view.status.status for view in area.facts}[outdated] == FactStatus.OUTDATED

    assert fetch_fact(outdated).status.status == FactStatus.OUTDATED
    assert (fetch_fact(removed).status.status, fetch_fact(removed).fact.is_removed_from_osm) == (FactStatus.OUTDATED, True)
    with pytest.raises(FactNotFoundError):
        fetch_fact(hidden)

    nearby = fetch_nearby_facts(FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON)
    assert [(item.view.fact.id, item.distance_m) for item in nearby] == [(unverified, 3), (outdated, 8)]

    flagged = [item for item in fetch_flagged_facts() if item.view.fact.id == hidden]
    assert [(item.flagged_on, item.is_hidden) for item in flagged] == [(date(2026, 10, 3), True)]
