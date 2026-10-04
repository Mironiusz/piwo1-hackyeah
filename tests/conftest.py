"""Refuse real-dependency tests on target before any fixture can execute, and share exact cleanup."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine

from tests.common_database_fixtures import DatabaseFixtureRegistry


def pytest_collection_finish(session: pytest.Session) -> None:
    """Apply the service environment boundary even during collect-only runs."""
    if not any(item.get_closest_marker("critical") for item in session.items):
        return
    try:
        from config.config import APP_ENVIRONMENT
    except Exception:
        pytest.exit("Critical tests require valid local configuration", returncode=4)
    if APP_ENVIRONMENT != "local":
        pytest.exit("Critical tests are forbidden in the target environment", returncode=4)


@pytest.fixture
def registered_cleanup():
    """Register exact scratch-object cleanup before any durable creation."""
    actions = []
    yield actions.append
    for action in reversed(actions):
        action()


@pytest.fixture
def stored_account_cleanup(registered_cleanup):
    """Register the pseudonym of an account a critical test commits, before the commit, so the account is deleted afterwards as the service account."""
    from data.accounts import apply_account_delete, fetch_account_by_pseudonym
    from data.engine import fetch_api_engine

    pseudonyms: list[str] = []

    def apply_cleanup() -> None:
        """Delete every registered account that still exists; the tests commit no vote or fact, which the service account could not delete."""
        with fetch_api_engine().begin() as connection:
            for pseudonym in pseudonyms:
                account = fetch_account_by_pseudonym(connection, pseudonym)
                if account is not None:
                    apply_account_delete(connection, account.account_id)

    registered_cleanup(apply_cleanup)
    return pseudonyms.append


def pytest_addoption(parser):
    """Accept an explicit local maintenance URL solely for scratch fixtures."""
    parser.addoption("--scratch-database-url", default=None, help="Local owner URL for registered scratch setup only")


@pytest.fixture
def database_cleanup_registry(schema_owner_engine: Engine) -> Iterator[DatabaseFixtureRegistry]:
    """Shares exact cleanup through the skeleton-owned validated local owner engine."""
    registry = DatabaseFixtureRegistry(schema_owner_engine)
    try:
        yield registry
    finally:
        registry.apply_cleanup()
