"""Refuses critical writes outside validated local configuration and shares cleanup."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine

from tests.common_database_fixtures import DatabaseFixtureRegistry

CRITICAL_CONFIGURATION_REFUSAL = "Critical tests require the delivered, validated local backend configuration."
CRITICAL_TARGET_REFUSAL = "Critical tests are permitted only in the local environment."


def pytest_collection_finish(session: pytest.Session) -> None:
    """Refuses critical sessions, including collection-only, before fixtures can write."""
    if not any(item.get_closest_marker("critical") is not None for item in session.items):
        return
    try:
        from config.config import APP_ENVIRONMENT
    except Exception:
        pytest.exit(CRITICAL_CONFIGURATION_REFUSAL, returncode=pytest.ExitCode.USAGE_ERROR)
    if APP_ENVIRONMENT != "local":
        pytest.exit(CRITICAL_TARGET_REFUSAL, returncode=pytest.ExitCode.USAGE_ERROR)


@pytest.fixture
def database_cleanup_registry(schema_owner_engine: Engine) -> Iterator[DatabaseFixtureRegistry]:
    """Shares exact cleanup through the skeleton-owned validated local owner engine."""
    registry = DatabaseFixtureRegistry(schema_owner_engine)
    try:
        yield registry
    finally:
        registry.apply_cleanup()
