"""Refuse real-dependency tests on target before any fixture can execute."""

import pytest


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


def pytest_addoption(parser):
    """Accept an explicit local maintenance URL solely for scratch fixtures."""
    parser.addoption("--scratch-database-url", default=None, help="Local owner URL for registered scratch setup only")
