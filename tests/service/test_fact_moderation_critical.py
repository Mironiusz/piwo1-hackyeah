"""
Critical test of flagging, hiding and restoring through `service/community_facts.py` against the local database of `db/compose.yaml`.

A report flagged on 3 October and again on 4 October keeps the first day, a fact of OpenStreetMap cannot be flagged while one converted
from it can, an unflagged fact is neither hidden nor restored, a hidden fact is missing for every public operation and listed for a
moderator, and a restored fact counts again with the votes it kept (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-5; AC-12 and
AC-13 of `COMMUNITY_FACTS_API_PRD.md`). Every committed row is registered for owner cleanup before its commit.
"""

from datetime import date
from uuid import UUID

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict

from data.engine import fetch_api_engine
from data.osm_copy import OsmFactChange, apply_osm_fact_changes
from service.community_facts import (
    FactNotFlaggableError,
    FactNotFlaggedError,
    FactNotFoundError,
    apply_fact_creation,
    apply_fact_flag,
    apply_fact_hiding,
    apply_fact_restoration,
    apply_fact_vote,
    fetch_fact,
    fetch_flagged_facts,
    fetch_nearby_facts,
)
from service.fact_rules import FactCreationInput
from service.fact_status import FactStatus
from tests.service.common_community_fact_seeds import ORIGIN_LAT, ORIGIN_LON, apply_account, apply_osm_fact, build_instant, build_person, build_point, register_report_cleanup

pytestmark = pytest.mark.critical

AUTHOR = build_person("Mozilla/5.0 (invented author)")


def test_flag_hide_and_restore_of_a_confirmed_report(database_cleanup_registry, stored_account_cleanup, monkeypatch: pytest.MonkeyPatch) -> None:
    key = UUID(int=0x9303001)
    register_report_cleanup(database_cleanup_registry, key)
    lat, lon = build_point(4.0)
    fact_id = apply_fact_creation(FactCreationInput(FactType.STAIRS, lat, lon, None, 2, None), key, AUTHOR, build_instant("2026-10-02T10:00:00.000+02:00")).view.fact.id
    engine = fetch_api_engine()
    monkeypatch.setattr("service.community_facts.fetch_business_now", lambda: build_instant("2026-10-03T10:00:00.000+02:00"))
    for name in "AB":
        apply_fact_vote(fact_id, VoteVerdict.CONFIRM, apply_account(engine, stored_account_cleanup, f"Moderowany_{name}_9303001"))
    with pytest.raises(FactNotFlaggedError):
        apply_fact_hiding(fact_id, build_instant("2026-10-03T11:00:00.000+02:00"))

    apply_fact_flag(fact_id, build_instant("2026-10-03T23:59:00.000+02:00"))
    apply_fact_flag(fact_id, build_instant("2026-10-04T08:00:00.000+02:00"))
    hidden = apply_fact_hiding(fact_id, build_instant("2026-10-04T09:00:00.000+02:00"))
    assert (hidden.flagged_on, hidden.is_hidden, hidden.view.status.status) == (date(2026, 10, 3), True, FactStatus.CONFIRMED)
    assert apply_fact_hiding(fact_id, build_instant("2026-10-04T09:30:00.000+02:00")) == hidden
    for refused in (lambda: fetch_fact(fact_id), lambda: apply_fact_vote(fact_id, VoteVerdict.DENY, AUTHOR), lambda: apply_fact_flag(fact_id, build_instant("2026-10-04T10:00:00.000+02:00"))):
        with pytest.raises(FactNotFoundError):
            refused()
    assert fact_id not in [item.view.fact.id for item in fetch_nearby_facts(FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON)]
    assert [(item.flagged_on, item.is_hidden) for item in fetch_flagged_facts() if item.view.fact.id == fact_id] == [(date(2026, 10, 3), True)]

    restored = apply_fact_restoration(fact_id)
    assert (restored.flagged_on, restored.is_hidden, restored.view.status.status, restored.view.status.confirmations) == (date(2026, 10, 3), False, FactStatus.CONFIRMED, 2.5)
    assert apply_fact_restoration(fact_id) == restored
    assert fetch_fact(fact_id) == restored.view
    assert fact_id in [item.view.fact.id for item in fetch_nearby_facts(FactType.STAIRS, ORIGIN_LAT, ORIGIN_LON)]


def test_fact_of_openstreetmap_cannot_be_flagged_but_a_converted_one_can(database_cleanup_registry) -> None:
    engine = fetch_api_engine()
    current = apply_osm_fact(engine, database_cleanup_registry, 9300300001, distance_m=90.0)
    converted = apply_osm_fact(engine, database_cleanup_registry, 9300300002, distance_m=95.0)
    with engine.begin() as connection:
        apply_osm_fact_changes(connection, [OsmFactChange(converted, FactSource.USER_REPORT, False)])
    with pytest.raises(FactNotFlaggableError):
        apply_fact_flag(current, build_instant("2026-10-04T10:00:00.000+02:00"))
    with pytest.raises(FactNotFlaggedError):
        apply_fact_restoration(current)
    apply_fact_flag(converted, build_instant("2026-10-04T10:00:00.000+02:00"))
    flagged = {item.view.fact.id: item for item in fetch_flagged_facts()}
    assert current not in flagged
    assert (flagged[converted].view.fact.source, flagged[converted].flagged_on, flagged[converted].is_hidden) == (FactSource.USER_REPORT, date(2026, 10, 4), False)
