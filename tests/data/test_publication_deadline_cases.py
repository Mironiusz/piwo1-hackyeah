"""Check the exact shared deadline without real waiting."""

import pytest

from common_time import DeadlineExpiredError, build_deadline, build_publication_deadline, resolve_remaining_milliseconds


def test_80_seconds_wait_plus_50_seconds_work_does_not_refresh_budget():
    """Reject the 130-second total against one 120-second ceiling."""
    deadline = build_publication_deadline(build_deadline(300, 0), 0)
    assert resolve_remaining_milliseconds(deadline, 80) == 40000
    with pytest.raises(DeadlineExpiredError):
        resolve_remaining_milliseconds(deadline, 130)


def test_45_seconds_remaining_wins_over_publication_ceiling():
    """Keep the earlier absolute run deadline unchanged."""
    deadline = build_publication_deadline(build_deadline(45, 80), 80)
    assert deadline.expires_at == 125
    assert resolve_remaining_milliseconds(deadline, 100) == 25000
