"""
Checks against the local database that the shared model writes and reads an instant together with its offset.

An instant written with an offset is read back with the same offset, not only as the same instant, because a driver
that normalizes everything to UTC would pass a comparison of instants alone (`docs/standards/standard_tests.md`,
Mandatory tests). The writes go through the mapped classes of `accessibility_db.tables`, so the test also proves the
mapping of the pairs, of a geography and of the stored calendar day of a vote.
"""

from datetime import date, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict
from accessibility_db.tables import Fact, Vote, build_local_datetime, build_offset_instant
from common_stored_rows import build_idempotency_key, build_voter_hash
from sqlalchemy import Connection
from sqlalchemy.orm import Session

pytestmark = pytest.mark.critical

FACT_POINT = "SRID=4326;POINT(19.937 50.0614)"


def apply_stored_fact(session: Session) -> Fact:
    """Builds and stores a point report of stairs through the mapped class, without a flag."""
    fact = Fact(
        fact_type=FactType.STAIRS,
        source=FactSource.USER_REPORT,
        geog=FACT_POINT,
        is_sample=False,
        idempotency_key=build_idempotency_key("round trip"),
        is_removed_from_osm=False,
        created_at=build_offset_instant(datetime.fromisoformat("2026-10-04T10:00:00.123+02:00")),
    )
    session.add(fact)
    session.flush()
    return fact


def test_cast_at_keeps_its_offset(service_connection: Connection) -> None:
    """A vote written in summer time and one written in winter time come back with their own offsets and days."""
    session = Session(bind=service_connection, join_transaction_mode="create_savepoint")
    fact = apply_stored_fact(session)
    summer = datetime.fromisoformat("2026-07-14T00:30:00.250+02:00")
    winter = datetime.fromisoformat("2026-01-14T06:00:00.000+01:00")
    summer_vote = Vote(fact_id=fact.id, verdict=VoteVerdict.CONFIRM, is_cast_with_account=False, voter_hash=build_voter_hash("summer"), cast_at=build_offset_instant(summer))
    winter_vote = Vote(fact_id=fact.id, verdict=VoteVerdict.DENY, is_cast_with_account=False, voter_hash=build_voter_hash("winter"), cast_at=build_offset_instant(winter))
    session.add_all([summer_vote, winter_vote])
    session.flush()
    session.expire_all()
    stored_summer = session.get_one(Vote, summer_vote.id)
    stored_winter = session.get_one(Vote, winter_vote.id)
    assert stored_summer.cast_at.utc_offset_minutes == 120
    assert build_local_datetime(stored_summer.cast_at).isoformat() == summer.isoformat()
    assert stored_summer.cast_on == date(2026, 7, 14)
    assert stored_winter.cast_at.utc_offset_minutes == 60
    assert build_local_datetime(stored_winter.cast_at).isoformat() == winter.isoformat()
    assert stored_winter.cast_on == date(2026, 1, 14)
    assert stored_summer.verdict is VoteVerdict.CONFIRM
    session.close()


def test_unflagged_fact_reads_its_flag_as_none(service_connection: Connection) -> None:
    """A fact without a flag and without hiding reads both pairs as None, not as a pair of nulls."""
    session = Session(bind=service_connection, join_transaction_mode="create_savepoint")
    fact_id = apply_stored_fact(session).id
    session.expire_all()
    stored = session.get_one(Fact, fact_id)
    assert stored.flagged_at is None
    assert stored.hidden_at is None
    session.close()


def test_fact_point_reads_back_as_written(service_connection: Connection) -> None:
    """A point written as EWKT text through the model is read back as the same text, with its closed lists as members."""
    session = Session(bind=service_connection, join_transaction_mode="create_savepoint")
    fact_id = apply_stored_fact(session).id
    session.expire_all()
    stored = session.get_one(Fact, fact_id)
    assert stored.geog == FACT_POINT
    assert stored.fact_type is FactType.STAIRS
    assert stored.source is FactSource.USER_REPORT
    session.close()
