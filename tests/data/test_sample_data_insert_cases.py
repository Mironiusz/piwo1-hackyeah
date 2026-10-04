"""Guards which sample votes the insert batches carry; these substitutes do not prove database behavior."""

import json
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from accessibility_db.closed_lists import VoteVerdict
from accessibility_db.tables import OffsetInstant
from sqlalchemy import Connection

from common_sample_data import SampleDataFailure, SampleFactRow, SampleFailureReason, SampleVoteRow, build_sample_voter_hash
from data.sample_data import apply_sample_inserts
from service.sample_data import SAMPLE_DEFINITIONS

CREATED_AT = OffsetInstant(datetime(2026, 1, 8, 7, 0, tzinfo=UTC), 60)
FACT_ROWS = (SampleFactRow(SAMPLE_DEFINITIONS[0], CREATED_AT, None, None), SampleFactRow(SAMPLE_DEFINITIONS[7], CREATED_AT, CREATED_AT, CREATED_AT))
VOTE_ROWS = (
    SampleVoteRow(-1, build_sample_voter_hash(-1, 1), VoteVerdict.CONFIRM, CREATED_AT),
    SampleVoteRow(-1, build_sample_voter_hash(-1, 2), VoteVerdict.CONFIRM, CREATED_AT),
    SampleVoteRow(-8, build_sample_voter_hash(-8, 1), VoteVerdict.CONFIRM, CREATED_AT),
)


def build_connection(*returned: list[int]) -> Mock:
    """Builds a connection substitute whose statements return the given identifiers in order."""
    connection = Mock(spec=Connection)
    connection.execute.side_effect = [Mock(scalars=Mock(return_value=ids)) for ids in returned]
    return connection


def test_only_the_votes_of_newly_inserted_facts_are_written() -> None:
    """Skips the votes of a fact another invocation already holds, and returns the new identifiers in definition order."""
    connection = build_connection([-1], [-1, -1])
    assert apply_sample_inserts(connection, FACT_ROWS, VOTE_ROWS) == (-1,)
    votes = json.loads(connection.execute.call_args_list[1].args[1]["votes"])
    assert [(vote["fact_id"], vote["voter_hash_hex"]) for vote in votes] == [(-1, build_sample_voter_hash(-1, 1).hex()), (-1, build_sample_voter_hash(-1, 2).hex())]


def test_no_vote_statement_runs_when_no_fact_is_new() -> None:
    """Writes no vote when every fact already exists."""
    connection = build_connection([])
    assert apply_sample_inserts(connection, FACT_ROWS, VOTE_ROWS) == ()
    assert connection.execute.call_count == 1


def test_a_lost_vote_is_refused() -> None:
    """Refuses a vote batch that returns fewer rows than it was given."""
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_inserts(build_connection([-1, -8], [-1, -1]), FACT_ROWS, VOTE_ROWS)
    assert raised.value.reason == SampleFailureReason.INITIAL_VOTE_INVALID


def test_fact_batch_carries_each_pair_and_null_moderation() -> None:
    """Binds the creation, flag and hide pairs of every fact, with both columns null for an absent pair."""
    connection = build_connection([-1, -8], [-1, -1, -8])
    apply_sample_inserts(connection, FACT_ROWS, VOTE_ROWS)
    facts = json.loads(connection.execute.call_args_list[0].args[1]["facts"])
    assert (facts[0]["created_at"], facts[0]["created_at_utc_offset_minutes"]) == (CREATED_AT.instant.isoformat(), 60)
    assert (facts[0]["flagged_at"], facts[0]["flagged_at_utc_offset_minutes"], facts[0]["hidden_at"], facts[0]["hidden_at_utc_offset_minutes"]) == (None, None, None, None)
    assert (facts[1]["hidden_at"], facts[1]["hidden_at_utc_offset_minutes"], facts[1]["description"]) == (CREATED_AT.instant.isoformat(), 60, "tekst z numerem telefonu, ukryty.")
