"""Verify absolute budgets independently of the machine clock."""

from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from common_time import Deadline, DeadlineExpiredError, build_business_day, build_deadline, build_publication_deadline, fetch_utc_now, resolve_remaining_milliseconds
from tests.common_runtime_settings import apply_invented_runtime_settings


def test_publication_uses_one_nonrenewable_budget() -> None:
    """Refuse the 80-second wait plus 50-second work example at second 120."""
    deadline = build_publication_deadline(build_deadline(3600, 0), 0)
    assert resolve_remaining_milliseconds(deadline, 80) == 40000
    with pytest.raises(DeadlineExpiredError):
        resolve_remaining_milliseconds(deadline, 130)


def test_remaining_run_budget_shortens_publication() -> None:
    """Use the 45 seconds left in the run instead of a fresh 120 seconds."""
    assert build_publication_deadline(Deadline(145), 100) == Deadline(145)


@pytest.mark.parametrize("now", [10, 11, 9.9999])
def test_exhausted_budget_never_becomes_zero_timeout(now: float) -> None:
    """Refuse expiration and sub-millisecond work rather than disable timeouts."""
    with pytest.raises(DeadlineExpiredError):
        resolve_remaining_milliseconds(Deadline(10), now)


def test_utc_clock_is_aware() -> None:
    """Return a UTC instant independent of the machine's local zone."""
    assert fetch_utc_now().utcoffset().total_seconds() == 0


@pytest.fixture
def runtime_settings(monkeypatch: pytest.MonkeyPatch):
    """Load the invented configuration whose business zone is Europe/Warsaw."""
    with apply_invented_runtime_settings(monkeypatch):
        yield


@pytest.mark.usefixtures("runtime_settings")
def test_business_day_of_a_late_utc_instant_is_the_next_warsaw_day() -> None:
    """Give 4 October for 23:30 UTC on 3 October 2026, which is 01:30 in Europe/Warsaw."""
    assert build_business_day(datetime(2026, 10, 3, 23, 30, tzinfo=UTC)) == date(2026, 10, 4)


@pytest.mark.usefixtures("runtime_settings")
def test_business_day_ignores_the_offset_the_instant_was_written_with() -> None:
    """Give the same Warsaw day for one instant written with two offsets."""
    instant = datetime(2026, 10, 3, 21, 59, tzinfo=UTC)
    assert build_business_day(instant) == build_business_day(instant.astimezone(timezone(timedelta(hours=-5)))) == date(2026, 10, 3)


@pytest.mark.usefixtures("runtime_settings")
def test_business_day_refuses_a_naive_instant() -> None:
    """Refuse a value without a zone offset instead of guessing its zone."""
    with pytest.raises(ValueError):
        build_business_day(datetime(2026, 10, 3, 23, 30))