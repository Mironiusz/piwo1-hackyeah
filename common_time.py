"""Separate aware civil time from monotonic publication budgets."""

import math
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo


class DeadlineExpiredError(TimeoutError):
    """Refuse work when its absolute monotonic budget is exhausted."""


@dataclass(frozen=True)
class Deadline:
    """Keep one absolute monotonic expiration instant."""

    expires_at: float


def fetch_utc_now() -> datetime:
    """Read the current instant as an aware UTC datetime."""
    return datetime.now(UTC)


def fetch_business_now() -> datetime:
    """Read the current instant in the configured business zone."""
    from config.config import BUSINESS_TIMEZONE

    return fetch_utc_now().astimezone(ZoneInfo(BUSINESS_TIMEZONE))


def fetch_monotonic_seconds() -> float:
    """Read elapsed-time coordinates independent of wall-clock changes."""
    return time.monotonic()


def build_deadline(seconds: float, now: float) -> Deadline:
    """Build a finite absolute deadline from an explicit elapsed budget."""
    if not math.isfinite(seconds) or not math.isfinite(now) or seconds <= 0 or not math.isfinite(now + seconds):
        raise ValueError("Invalid elapsed-time budget")
    return Deadline(now + seconds)


def build_publication_deadline(run_deadline: Deadline, now: float) -> Deadline:
    """Cap publication at 120 seconds without extending the run deadline."""
    resolve_remaining_milliseconds(run_deadline, now)
    return Deadline(min(run_deadline.expires_at, now + 120))


def resolve_remaining_milliseconds(deadline: Deadline, now: float) -> int:
    """Return a nonzero PostgreSQL budget or refuse expired work."""
    remaining = deadline.expires_at - now
    if not math.isfinite(remaining) or remaining < 0.001:
        raise DeadlineExpiredError("Elapsed-time budget exhausted")
    return math.floor(remaining * 1000)
