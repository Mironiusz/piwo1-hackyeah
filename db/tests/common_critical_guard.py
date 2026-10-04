"""
The guard that stops a session with a critical test unless the environment is the local one.

A critical test writes to a real database, so it runs only against the local database of `db/compose.yaml`
(`docs/standards/standard_tests.md`, section Test layers). The guard reads `DB_ENVIRONMENT`, the entry by which the
compose files of `db/` choose the environment, and ends the session with the usage error code before the first test,
also during collection alone. The message names no address. `tests/architecture/test_critical_test_guard.py` in the
repository root checks this guard.
"""

import os

import pytest

CRITICAL_MARKER = "critical"
LOCAL_ENVIRONMENT = "local"
REFUSAL_MESSAGE = "Critical tests run only against the local database: set DB_ENVIRONMENT=local, as db/compose.yaml does."


def pytest_collection_finish(session: pytest.Session) -> None:
    """Ends the session before the first test when a critical test was collected outside the local environment."""
    has_critical_test = any(item.get_closest_marker(CRITICAL_MARKER) is not None for item in session.items)
    if has_critical_test and os.environ.get("DB_ENVIRONMENT") != LOCAL_ENVIRONMENT:
        pytest.exit(REFUSAL_MESSAGE, returncode=pytest.ExitCode.USAGE_ERROR)
