"""Guards completion classification; these substitutes do not prove database behavior."""

from unittest.mock import Mock

import pytest
from sqlalchemy import Connection
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from common_sample_data import SampleCommitState, SampleDataFailure, SampleDataOutcome, SampleDataResult, SampleFailureReason
from data.sample_data import apply_sample_connection

SAMPLE_IDS = (-1, -2, -3, -4, -5, -6, -7, -8)


@pytest.fixture
def sample_connection() -> Mock:
    """Builds an open transaction-capable substitute without database state."""
    connection = Mock(spec=Connection)
    connection.invalidated = False
    connection.closed = False
    connection.get_transaction.return_value.is_active = True
    return connection


def test_success_is_returned_only_after_commit_acknowledgement(sample_connection: Mock) -> None:
    """Requires the single stable-snapshot transaction to finish before returning."""
    result = SampleDataResult(SampleDataOutcome.CREATED, 8, 0, 25, SAMPLE_IDS)
    action = Mock(return_value=result)
    assert apply_sample_connection(sample_connection, action) is result
    sample_connection.execution_options.assert_called_once_with(isolation_level="REPEATABLE READ")
    sample_connection.begin.assert_called_once_with()
    sample_connection.commit.assert_called_once_with()
    sample_connection.rollback.assert_not_called()


def test_domain_refusal_acknowledges_rollback_before_raising(sample_connection: Mock) -> None:
    """Reports the original safe reason with acknowledged rollback evidence."""
    action = Mock(side_effect=SampleDataFailure(SampleFailureReason.CONTENT_MISMATCH))
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_connection(sample_connection, action)
    assert raised.value.reason == SampleFailureReason.CONTENT_MISMATCH
    assert raised.value.commit_state == SampleCommitState.ROLLED_BACK
    sample_connection.rollback.assert_called_once_with()
    sample_connection.commit.assert_not_called()


@pytest.mark.parametrize("invalidated, rollback_error", [(True, None), (False, SQLAlchemyError("invented private driver text"))])
def test_failed_rollback_is_not_reported_as_acknowledged(invalidated: bool, rollback_error: Exception | None, sample_connection: Mock) -> None:
    """Refuses to treat connection invalidation or a failed rollback as proof."""
    sample_connection.invalidated = invalidated
    sample_connection.rollback.side_effect = rollback_error
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_connection(sample_connection, Mock(side_effect=SQLAlchemyError("invented private driver text")))
    assert raised.value.reason == SampleFailureReason.DATABASE_FAILED
    assert raised.value.commit_state == SampleCommitState.UNKNOWN
    assert "private" not in str(raised.value)


@pytest.mark.parametrize("commit_error", [SQLAlchemyError("invented private commit text"), OSError("invented lost acknowledgement")])
def test_lost_commit_evidence_remains_unknown(commit_error: Exception, sample_connection: Mock) -> None:
    """Does not turn a later cleanup action into proof that a sent commit failed."""
    sample_connection.commit.side_effect = commit_error
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_connection(sample_connection, Mock(return_value=SampleDataResult(SampleDataOutcome.UNCHANGED, 0, 8, 0, SAMPLE_IDS)))
    assert raised.value.reason == SampleFailureReason.COMMIT_UNKNOWN
    assert raised.value.commit_state == SampleCommitState.UNKNOWN
    sample_connection.rollback.assert_not_called()


def test_server_serialization_refusal_is_an_explicit_failure(sample_connection: Mock) -> None:
    """Allows a manual retry after acknowledged server rejection and rollback."""
    driver_error = Mock(spec=Exception)
    driver_error.sqlstate = "40001"
    sample_connection.commit.side_effect = DBAPIError(None, None, driver_error, connection_invalidated=False)
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_connection(sample_connection, Mock(return_value=SampleDataResult(SampleDataOutcome.CREATED, 8, 0, 25, SAMPLE_IDS)))
    assert raised.value.reason == SampleFailureReason.DATABASE_FAILED
    assert raised.value.commit_state == SampleCommitState.ROLLED_BACK
    sample_connection.rollback.assert_called_once_with()


def test_inactive_transaction_cannot_supply_rollback_acknowledgement(sample_connection: Mock) -> None:
    """Does not mistake SQLAlchemy's inactive-transaction cleanup for a server rollback."""
    sample_connection.get_transaction.return_value.is_active = False
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_connection(sample_connection, Mock(side_effect=SQLAlchemyError("Invented storage failure.")))
    assert raised.value.commit_state == SampleCommitState.UNKNOWN
    sample_connection.rollback.assert_not_called()


def test_commit_cancellation_is_not_proof_of_rollback(sample_connection: Mock) -> None:
    """Keeps commit uncertainty when only a cancellation error is available."""
    driver_error = Mock(spec=Exception)
    driver_error.sqlstate = "57014"
    sample_connection.commit.side_effect = DBAPIError(None, None, driver_error, connection_invalidated=False)
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_connection(sample_connection, Mock(return_value=SampleDataResult(SampleDataOutcome.CREATED, 8, 0, 25, SAMPLE_IDS)))
    assert raised.value.reason == SampleFailureReason.COMMIT_UNKNOWN
    assert raised.value.commit_state == SampleCommitState.UNKNOWN
    sample_connection.rollback.assert_not_called()
