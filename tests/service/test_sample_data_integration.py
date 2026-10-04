"""Exercises the real service while replacing only its immediate dependencies."""

import sys
from dataclasses import replace
from datetime import datetime
from types import ModuleType
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.tables import build_offset_instant
from sqlalchemy import Connection

from common_sample_data import SampleCommitState, SampleDataFailure, SampleDataOutcome, SampleDataResult, SampleFailureReason, SampleNetworkPrerequisites, StoredInitialVote, StoredSample
from service import sample_data

pytestmark = pytest.mark.integration


@pytest.fixture
def service_dependencies(monkeypatch: pytest.MonkeyPatch) -> tuple[Mock, Mock]:
    """Replaces the documented clock and logger calls for isolated service runs."""
    clock = Mock(return_value=datetime(2026, 7, 10, 8, 0, 0, 123000, tzinfo=ZoneInfo("Europe/Warsaw")))
    clock_module = ModuleType("common_time")
    clock_module.fetch_business_now = clock
    monkeypatch.setitem(sys.modules, "common_time", clock_module)
    logger = Mock()
    logging_module = ModuleType("config.logging")
    logging_module.fetch_logger = Mock(return_value=logger)
    monkeypatch.setitem(sys.modules, "config.logging", logging_module)
    return clock, logger


def test_first_loading_uses_one_creation_pair_and_returns_all_four_counts(
    monkeypatch: pytest.MonkeyPatch,
    service_dependencies: tuple[Mock, Mock],
    sample_prerequisites: tuple[SampleNetworkPrerequisites, ...],
    stored_samples: dict[int, StoredSample],
    initial_votes: dict[int, tuple[StoredInitialVote, ...]],
) -> None:
    """Passes only missing samples to storage and validates the final author history."""
    clock, logger = service_dependencies
    instant = build_offset_instant(clock.return_value)
    final_samples = {identifier: replace(item, created_at=instant) for identifier, item in stored_samples.items()}
    final_votes = {identifier: (replace(votes[0], cast_at=instant),) for identifier, votes in initial_votes.items()}
    inserts = Mock(return_value=(-1, -2, -3, -4))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_prerequisites", Mock(return_value=sample_prerequisites))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", Mock(side_effect=[{}, final_samples]))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_initial_sample_votes", Mock(side_effect=[{}, final_votes]))
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    connection = Mock(spec=Connection)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_transaction", lambda action: action(connection))
    result = sample_data.apply_sample_data()
    assert result == SampleDataResult(SampleDataOutcome.CREATED, 4, 0, 4, (-1, -2, -3, -4))
    inserts.assert_called_once_with(connection, sample_data.SAMPLE_DEFINITIONS, instant)
    clock.assert_called_once_with()
    logger.info.assert_called_once()


def test_later_loading_does_not_read_a_clock_or_write_another_vote(
    monkeypatch: pytest.MonkeyPatch,
    service_dependencies: tuple[Mock, Mock],
    sample_prerequisites: tuple[SampleNetworkPrerequisites, ...],
    stored_samples: dict[int, StoredSample],
    initial_votes: dict[int, tuple[StoredInitialVote, ...]],
) -> None:
    """Keeps winter author history unchanged even when the current clock is in summer."""
    clock, _logger = service_dependencies
    inserts = Mock()
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_prerequisites", Mock(return_value=sample_prerequisites))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", Mock(return_value=stored_samples))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_initial_sample_votes", Mock(return_value=initial_votes))
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_transaction", lambda action: action(Mock(spec=Connection)))
    assert sample_data.apply_sample_data() == SampleDataResult(SampleDataOutcome.UNCHANGED, 0, 4, 0, (-1, -2, -3, -4))
    clock.assert_not_called()
    inserts.assert_not_called()


def test_partial_dataset_only_inserts_the_missing_definition(
    monkeypatch: pytest.MonkeyPatch,
    service_dependencies: tuple[Mock, Mock],
    sample_prerequisites: tuple[SampleNetworkPrerequisites, ...],
    stored_samples: dict[int, StoredSample],
    initial_votes: dict[int, tuple[StoredInitialVote, ...]],
) -> None:
    """Allows a verified partial dataset without refreshing existing author timestamps."""
    inserts = Mock(return_value=(-4,))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_prerequisites", Mock(return_value=sample_prerequisites))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", Mock(side_effect=[{key: value for key, value in stored_samples.items() if key != -4}, stored_samples]))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_initial_sample_votes", Mock(return_value=initial_votes))
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    connection = Mock(spec=Connection)
    result = sample_data.apply_sample_contents(connection)
    assert result.created_count == 1
    assert result.unchanged_count == 3
    assert result.initial_votes_created_count == 1
    assert inserts.call_args.args[1] == (sample_data.SAMPLE_DEFINITIONS[3],)


def test_invalid_network_is_rejected_before_any_storage_write(monkeypatch: pytest.MonkeyPatch, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Does not enter fact reconciliation when publication is missing."""
    invalid = tuple(replace(item, has_copy=False) for item in sample_prerequisites)
    inserts = Mock()
    reads = Mock()
    monkeypatch.setattr(sample_data.sample_storage, "fetch_sample_prerequisites", Mock(return_value=invalid))
    monkeypatch.setattr(sample_data.sample_storage, "fetch_stored_samples", reads)
    monkeypatch.setattr(sample_data.sample_storage, "apply_sample_inserts", inserts)
    with pytest.raises(SampleDataFailure, match="copy_missing"):
        sample_data.apply_sample_contents(Mock(spec=Connection))
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
