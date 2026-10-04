"""Exercises the real service while replacing only its immediate dependencies."""

from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Connection

from common_sample_data import (
    SampleCommitState,
    SampleDataFailure,
    SampleDataOutcome,
    SampleDataResult,
    SampleFactRow,
    SampleFailureReason,
    SampleNetworkPrerequisites,
    SampleVoteRow,
    StoredSample,
    StoredSampleVote,
)
from service import sample_data

pytestmark = pytest.mark.integration

SAMPLE_IDS = (-1, -2, -3, -4, -5, -6, -7, -8)


@pytest.fixture
def service_dependencies(monkeypatch: pytest.MonkeyPatch, runtime_settings) -> tuple[Mock, Mock]:
    """Replaces the clock and logger the service calls, with a summer clock carrying milliseconds."""
    clock = Mock(return_value=datetime(2026, 7, 10, 8, 0, 0, 123000, tzinfo=ZoneInfo("Europe/Warsaw")))
    monkeypatch.setattr(sample_data, "fetch_business_now", clock)
    logger = Mock()
    monkeypatch.setattr(sample_data, "fetch_logger", Mock(return_value=logger))
    return clock, logger


@pytest.fixture
def network_reads(monkeypatch: pytest.MonkeyPatch, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> Mock:
    """Supplies measured places without the contradiction and a route-graph check that establishes it."""
    measured = tuple(replace(item, has_kerb_contradiction=False) for item in sample_prerequisites)
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_prerequisites", Mock(return_value=measured))
    contradiction = Mock(return_value=True)
    monkeypatch.setattr(sample_data, "fetch_sample_kerb_contradiction", contradiction)
    return contradiction


def build_stored_from_rows(
    fact_rows: tuple[SampleFactRow, ...], vote_rows: tuple[SampleVoteRow, ...], stored: dict[int, StoredSample]
) -> tuple[dict[int, StoredSample], dict[int, tuple[StoredSampleVote, ...]]]:
    """Gives the facts and votes storage would hold after inserting the rows."""
    facts = {row.definition.fact_id: replace(stored[row.definition.fact_id], created_at=row.created_at) for row in fact_rows}
    votes: dict[int, tuple[StoredSampleVote, ...]] = {}
    for row in vote_rows:
        votes[row.fact_id] = (*votes.get(row.fact_id, ()), StoredSampleVote(row.fact_id, row.verdict, False, None, row.voter_hash, row.cast_at))
    return facts, votes


@pytest.mark.usefixtures("network_reads")
def test_first_loading_inserts_eight_facts_and_25_votes_dated_from_whole_seconds(
    monkeypatch: pytest.MonkeyPatch, service_dependencies: tuple[Mock, Mock], stored_samples: dict[int, StoredSample]
) -> None:
    """Passes every definition and its votes to storage, dated back from the loading instant without its milliseconds."""
    clock, logger = service_dependencies
    loading_at = clock.return_value.replace(microsecond=0)
    fact_rows, vote_rows = sample_data.build_sample_insert_rows(sample_data.SAMPLE_DEFINITIONS, loading_at)
    final_samples, final_votes = build_stored_from_rows(fact_rows, vote_rows, stored_samples)
    inserts = Mock(return_value=SAMPLE_IDS)
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", Mock(side_effect=[{}, final_samples]))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_votes", Mock(side_effect=[{}, final_votes]))
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    connection = Mock(spec=Connection)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_transaction", lambda action: action(connection))
    assert sample_data.apply_sample_data() == SampleDataResult(SampleDataOutcome.CREATED, 8, 0, 25, SAMPLE_IDS)
    inserts.assert_called_once_with(connection, fact_rows, vote_rows)
    assert len(vote_rows) == 25
    clock.assert_called_once_with()
    logger.info.assert_called_once()


def test_kerb_contradiction_is_established_only_for_the_fact_that_needs_it(monkeypatch: pytest.MonkeyPatch, network_reads: Mock) -> None:
    """Builds the route-graph check for S-5 alone and hands its result to validation."""
    connection = Mock(spec=Connection)
    prerequisites = sample_data.fetch_sample_network_prerequisites(connection)
    network_reads.assert_called_once_with(connection, sample_data.SAMPLE_DEFINITIONS[4])
    assert [item.has_kerb_contradiction for item in prerequisites] == [False, False, False, False, True, False, False, False]


@pytest.mark.usefixtures("network_reads")
def test_later_loading_does_not_read_a_clock_or_write_another_vote(
    monkeypatch: pytest.MonkeyPatch, service_dependencies: tuple[Mock, Mock], stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]
) -> None:
    """Keeps winter history unchanged even when the current clock is in summer."""
    clock, _logger = service_dependencies
    inserts = Mock()
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", Mock(return_value=stored_samples))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_votes", Mock(return_value=sample_votes))
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_transaction", lambda action: action(Mock(spec=Connection)))
    assert sample_data.apply_sample_data() == SampleDataResult(SampleDataOutcome.UNCHANGED, 0, 8, 0, SAMPLE_IDS)
    clock.assert_not_called()
    inserts.assert_not_called()


@pytest.mark.usefixtures("network_reads")
def test_partial_dataset_only_inserts_the_missing_definition(
    monkeypatch: pytest.MonkeyPatch, service_dependencies: tuple[Mock, Mock], stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]
) -> None:
    """Allows a verified partial dataset and inserts the hidden fact with its own two votes only."""
    clock, _logger = service_dependencies
    missing = (sample_data.SAMPLE_DEFINITIONS[7],)
    fact_rows, vote_rows = sample_data.build_sample_insert_rows(missing, clock.return_value.replace(microsecond=0))
    final_samples, final_votes = build_stored_from_rows(fact_rows, vote_rows, stored_samples)
    inserts = Mock(return_value=(-8,))
    earlier_samples = {key: value for key, value in stored_samples.items() if key != -8}
    earlier_votes = {key: value for key, value in sample_votes.items() if key != -8}
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", Mock(side_effect=[earlier_samples, {**earlier_samples, **final_samples}]))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_votes", Mock(side_effect=[earlier_votes, {**earlier_votes, **final_votes}]))
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    connection = Mock(spec=Connection)
    result = sample_data.apply_sample_contents(connection)
    assert (result.outcome, result.created_count, result.unchanged_count, result.initial_votes_created_count) == (SampleDataOutcome.CREATED, 1, 7, 2)
    inserts.assert_called_once_with(connection, fact_rows, vote_rows)


@pytest.mark.parametrize("field, reason", [("has_copy", SampleFailureReason.COPY_MISSING), ("has_kerb_contradiction", SampleFailureReason.CONTRADICTION_MISSING)])
def test_invalid_network_is_rejected_before_any_storage_write(
    field: str, reason: SampleFailureReason, monkeypatch: pytest.MonkeyPatch, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]
) -> None:
    """Does not enter fact reconciliation when the copy is missing or the kerb contradiction does not hold."""
    measured = tuple(replace(item, has_copy=field != "has_copy", has_kerb_contradiction=False) for item in sample_prerequisites)
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_prerequisites", Mock(return_value=measured))
    monkeypatch.setattr(sample_data, "fetch_sample_kerb_contradiction", Mock(return_value=False))
    inserts = Mock()
    reads = Mock()
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", reads)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    with pytest.raises(SampleDataFailure) as raised:
        sample_data.apply_sample_contents(Mock(spec=Connection))
    assert raised.value.reason == reason
    reads.assert_not_called()
    inserts.assert_not_called()


@pytest.mark.parametrize("reason", list(SampleFailureReason))
def test_safe_storage_failures_never_return_success(reason: SampleFailureReason, monkeypatch: pytest.MonkeyPatch, service_dependencies: tuple[Mock, Mock]) -> None:
    """Preserves reason and commit evidence for the common adapter."""
    failure = SampleDataFailure(reason, SampleCommitState.UNKNOWN)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_transaction", Mock(side_effect=failure))
    with pytest.raises(SampleDataFailure) as raised:
        sample_data.apply_sample_data()
    assert raised.value is failure
    _clock, logger = service_dependencies
    logger.info.assert_not_called()
    assert logger.exception.call_args.args[1:] == (reason.value, "unknown")


def test_unexpected_storage_exception_is_not_a_success_fallback(monkeypatch: pytest.MonkeyPatch, service_dependencies: tuple[Mock, Mock]) -> None:
    """Leaves an unexpected exception unsuccessful without logging its raw text."""
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_transaction", Mock(side_effect=RuntimeError("invented protected driver text")))
    with pytest.raises(RuntimeError):
        sample_data.apply_sample_data()
    _clock, logger = service_dependencies
    logger.info.assert_not_called()
    assert logger.exception.call_args.args[1:] == ("database_failed", "unknown")
