"""
Guards what `data/community_facts.py` fixes without a database: what its records and its error show, the lock modes, the conflict targets and
the visibility predicates of its statements, and the columns its reads select.

These cases read compiled statements and substitutes, so they prove the text of the statements, not their behavior; the behavior is proved by
`tests/data/test_community_facts_critical.py` against the local database (`plans/community_facts/COMMUNITY_FACTS_PLAN.md` D-5, D-7, D-9).
That the module logs nothing is guarded by `tests/architecture/test_community_facts_boundaries.py`.
"""

from dataclasses import fields
from unittest.mock import Mock

import pytest
from accessibility_db.closed_lists import VoteVerdict
from accessibility_db.tables import OffsetInstant
from psycopg.errors import ForeignKeyViolation
from sqlalchemy import Connection
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError

from data.community_facts import (
    APPLY_FACT_INSERT_SQL,
    APPLY_VOTE_INSERT_SQL,
    FETCH_STORED_FACT_FOR_CHANGE_SQL,
    FETCH_STORED_FACT_FOR_VOTE_SQL,
    FETCH_STORED_FACT_SQL,
    FETCH_STORED_FACTS_IN_AREA_SQL,
    FETCH_STORED_FLAGGED_FACTS_SQL,
    FETCH_STORED_NEARBY_FACTS_SQL,
    AccountVoter,
    AnonymousVoter,
    StoredCommunityFact,
    VoteAccountMissingError,
    apply_vote_insert,
)
from data.route_facts import StoredFact

VOTER_HASH = bytes(range(32))
ACCOUNT_ID = 424242
CAST_AT = OffsetInstant(instant=Mock(), utc_offset_minutes=120)
FACT_COLUMNS = {field.name for field in fields(StoredFact)} | {"flagged_at", "flagged_at_utc_offset_minutes", "is_hidden"}
FACT_READS = (
    FETCH_STORED_FACTS_IN_AREA_SQL,
    FETCH_STORED_FACT_SQL,
    FETCH_STORED_FLAGGED_FACTS_SQL,
    FETCH_STORED_FACT_FOR_VOTE_SQL,
    FETCH_STORED_FACT_FOR_CHANGE_SQL,
)
PERSON_COLUMNS = {"account_id", "voter_hash", "idempotency_key"}


def build_sql(statement) -> str:
    """Render a statement for the PostgreSQL dialect with its parameter markers, as the driver would receive it."""
    return str(statement.compile(dialect=postgresql.dialect()))


def build_foreign_key_error(constraint_name: str) -> IntegrityError:
    """Build the integrity error of the driver for the named constraint, carrying the account identifier in its parameters as a real one would."""
    original = Mock(spec=ForeignKeyViolation)
    original.diag.constraint_name = constraint_name
    return IntegrityError("INSERT INTO vote", {"account_id": ACCOUNT_ID}, original)


def test_anonymous_voter_text_carries_no_hash() -> None:
    """Keep the 32 bytes of a person without an account out of the text of the record, so no log or failure message can print them."""
    voter = AnonymousVoter(VOTER_HASH)
    assert VOTER_HASH.hex() not in repr(voter)
    assert repr(VOTER_HASH) not in repr(voter)
    assert voter.voter_hash == VOTER_HASH


def test_account_missing_error_carries_no_identifier_and_no_cause() -> None:
    """Turn the failure of fk_vote_account into the error of the layer, with a constant message and without the driver message that names the key."""
    connection = Mock(spec=Connection)
    connection.execute.side_effect = build_foreign_key_error("fk_vote_account")
    with pytest.raises(VoteAccountMissingError) as raised:
        apply_vote_insert(connection, 1, VoteVerdict.CONFIRM, AccountVoter(ACCOUNT_ID), CAST_AT)
    assert str(ACCOUNT_ID) not in str(raised.value)
    assert str(ACCOUNT_ID) not in repr(raised.value)
    assert raised.value.__cause__ is None
    assert raised.value.__suppress_context__ is True


def test_another_integrity_failure_of_a_vote_propagates_unchanged() -> None:
    """Let every constraint other than fk_vote_account reach the caller as it is, because only the missing account has an answer of its own."""
    connection = Mock(spec=Connection)
    error = build_foreign_key_error("fk_vote_fact")
    connection.execute.side_effect = error
    with pytest.raises(IntegrityError) as raised:
        apply_vote_insert(connection, 1, VoteVerdict.CONFIRM, AccountVoter(ACCOUNT_ID), CAST_AT)
    assert raised.value is error


def test_vote_lock_is_a_share_lock_and_the_change_lock_is_a_no_key_update_lock() -> None:
    """Fix the two lock modes the vote and the moderation rely on: the first conflicts with a publication and a moderation, not with another vote."""
    assert build_sql(FETCH_STORED_FACT_FOR_VOTE_SQL).rstrip().endswith("FOR SHARE")
    assert build_sql(FETCH_STORED_FACT_FOR_CHANGE_SQL).rstrip().endswith("FOR NO KEY UPDATE")


def test_locks_reach_hidden_and_removed_facts() -> None:
    """Keep every visibility condition out of the two locks, which must give the service layer a hidden or a removed fact to decide on."""
    for statement in (FETCH_STORED_FACT_FOR_VOTE_SQL, FETCH_STORED_FACT_FOR_CHANGE_SQL):
        condition = build_sql(statement).split("WHERE")[1]
        assert "hidden_at IS NULL" not in condition
        assert "is_removed_from_osm" not in condition


def test_reading_by_identifier_hides_only_the_hidden_and_the_listings_hide_the_removed_too() -> None:
    """State the two visibility rules of the contract on both sides: a reading by identifier leaves out hidden facts, the map and the check also removed ones."""
    detail = build_sql(FETCH_STORED_FACT_SQL).split("WHERE")[1]
    assert "hidden_at IS NULL" in detail
    assert "is_removed_from_osm" not in detail
    for statement in (FETCH_STORED_FACTS_IN_AREA_SQL, FETCH_STORED_NEARBY_FACTS_SQL):
        condition = build_sql(statement).split("WHERE")[1]
        assert "hidden_at IS NULL" in condition
        assert "is_removed_from_osm" in condition


def test_area_is_compared_as_geometry_and_the_check_as_geography() -> None:
    """Keep the rectangle a geometry intersection and the check a geography distance, the choice D-4 and D-3 explain."""
    area = build_sql(FETCH_STORED_FACTS_IN_AREA_SQL)
    assert "ST_Intersects(geometry(fact.geog), ST_MakeEnvelope(" in area
    assert "ST_DWithin" not in area
    nearby = build_sql(FETCH_STORED_NEARBY_FACTS_SQL)
    assert "ST_DWithin(fact.geog, geography(" in nearby
    assert "ST_Intersects" not in nearby


def test_conflict_targets_are_the_idempotency_key_and_any_vote_constraint() -> None:
    """Keep the save of a fact on the unique index of its key and the vote insert on every unique constraint of the daily limit."""
    assert "ON CONFLICT (idempotency_key) DO NOTHING" in build_sql(APPLY_FACT_INSERT_SQL)
    assert "ON CONFLICT DO NOTHING" in build_sql(APPLY_VOTE_INSERT_SQL)


def test_reads_select_the_listed_columns_and_no_person() -> None:
    """Select exactly the columns of the stored fact, never an account, a voter hash or an idempotency key, and never every column."""
    for statement in (*FACT_READS, FETCH_STORED_NEARBY_FACTS_SQL):
        selected = set(statement.selected_columns.keys())
        assert PERSON_COLUMNS.isdisjoint(selected)
        assert selected >= FACT_COLUMNS
        assert selected - FACT_COLUMNS <= {"distance_m"}
        assert "SELECT *" not in build_sql(statement)


def test_stored_community_fact_adds_only_the_flag_instant_and_the_hidden_mark() -> None:
    """Add to the stored fact of the route only what the contract shows beyond it, and no author, account or idempotency key."""
    added = {field.name for field in fields(StoredCommunityFact)} - {field.name for field in fields(StoredFact)}
    assert added == {"flagged_at", "is_hidden"}
