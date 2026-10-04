"""
Fixtures of the tests of `db/tests/` and the guard of the critical tests.

The critical tests connect as the service account to the local database the chain was applied to, each inside a
transaction rolled back after the test, so no test leaves a row behind and no cleanup fixture is needed. The connection
entries are read directly from the environment: the tests run outside the application, without a configuration facade
(`docs/standards/standard_config.md`, the exception of tests).
"""

import os
from collections.abc import Iterator

import pytest
from common_critical_guard import pytest_collection_finish
from common_stored_rows import INSERT_USER_REPORT_SQL, build_idempotency_key
from sqlalchemy import URL, Connection, Engine, create_engine, text

__all__ = ["pytest_collection_finish"]

STATEMENT_TIMEOUT_MS = 5000


def fetch_environment_value(name: str) -> str:
    """Reads one required connection entry from the environment and stops with its name when it is missing."""
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Set the environment entry {name} to run the critical tests, as db/compose.yaml does.")
    return value


@pytest.fixture(scope="session")
def service_engine() -> Iterator[Engine]:
    """Opens an engine as the service account, with the session zone pinned to UTC and the statement timeout of the backend."""
    url = URL.create(
        "postgresql+psycopg",
        username=fetch_environment_value("DB_SERVICE_ACCOUNT_NAME"),
        password=fetch_environment_value("DB_SERVICE_ACCOUNT_PASSWORD"),
        host=fetch_environment_value("DB_HOST"),
        port=int(fetch_environment_value("DB_PORT")),
        database=fetch_environment_value("DB_NAME"),
    )
    engine = create_engine(url, connect_args={"options": f"-c timezone=UTC -c statement_timeout={STATEMENT_TIMEOUT_MS}"})
    yield engine
    engine.dispose()


@pytest.fixture
def service_connection(service_engine: Engine) -> Iterator[Connection]:
    """Gives a connection of the service account inside a transaction that is rolled back after the test."""
    with service_engine.connect() as connection:
        transaction = connection.begin()
        yield connection
        transaction.rollback()


@pytest.fixture
def stored_fact_id(service_connection: Connection) -> int:
    """Stores one point report of stairs and gives its identifier."""
    parameters = {"fact_type": "stairs", "geozone_radius_m": None, "idempotency_key": build_idempotency_key("stored fact")}
    return service_connection.execute(text(INSERT_USER_REPORT_SQL), parameters).scalar_one()
