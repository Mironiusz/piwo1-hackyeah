"""Guards refusal to clean unowned fixture data without a database."""

from datetime import datetime
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Connection, Engine

from tests.common_database_fixtures import DatabaseFixtureRegistry
from tests.common_runtime_settings import apply_invented_runtime_settings
from tests.data.common_sample_data_fixtures import build_sample_critical_dataset

WINTER_CLOCK = datetime(2026, 1, 10, 8, 0, tzinfo=ZoneInfo("Europe/Warsaw"))


def test_cleanup_registry_runs_registered_actions_in_reverse_order() -> None:
    """Allows dependent fixture objects to be removed before their parents."""
    owner = MagicMock(spec=Engine)
    registry = DatabaseFixtureRegistry(owner)
    order: list[str] = []
    registry.apply_registration(lambda _connection: order.append("parent"))
    registry.apply_registration(lambda _connection: order.append("child"))
    registry.apply_cleanup()
    registry.apply_cleanup()
    assert order == ["child", "parent"]
    owner.begin.assert_called_once_with()


def test_missing_marker_after_durable_setup_is_not_silent_cleanup_success() -> None:
    """Refuses cleanup when it cannot establish ownership of an exercised fixture."""
    dataset = build_sample_critical_dataset(WINTER_CLOCK)
    dataset.durable_setup_completed = True
    connection = MagicMock(spec=Connection)
    connection.execute.return_value.scalar_one.return_value = False
    with pytest.raises(RuntimeError, match="cannot establish ownership"):
        dataset.apply_cleanup(connection)
    assert connection.execute.call_count == 1


def test_occupied_sample_with_another_creation_pair_is_not_deleted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Checks ownership before any vote, fact or network cleanup statement."""
    dataset = build_sample_critical_dataset(WINTER_CLOCK)
    dataset.durable_setup_completed = True
    connection = MagicMock(spec=Connection)
    connection.execute.return_value.scalar_one.side_effect = [True, True]
    with apply_invented_runtime_settings(monkeypatch), pytest.raises(RuntimeError, match="different creation identity"):
        dataset.apply_cleanup(connection)
    assert connection.execute.call_count == 2
