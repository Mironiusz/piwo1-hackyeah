"""Verify absolute budgets independently of the machine clock."""

import pytest

from common_time import Deadline, DeadlineExpiredError, build_deadline, build_publication_deadline, fetch_utc_now, resolve_remaining_milliseconds


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
