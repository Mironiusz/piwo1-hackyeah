"""Construct every database engine of the service account of db/ through one explicit account boundary."""

import functools
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import URL, Connection, Engine, create_engine, text
from sqlalchemy.pool import NullPool

API_STATEMENT_TIMEOUT_MS = 5000
APPLY_STATEMENT_TIMEOUT_SQL = text("SELECT set_config('statement_timeout', :timeout, true)")


def apply_engine_construction(address: URL, statement_timeout_ms: int, unpooled: bool) -> Engine:
    """Create an engine with UTC sessions, bounded waits and hidden parameters."""
    if statement_timeout_ms < 1:
        raise ValueError("Database timeout must be positive")
    options = {"connect_timeout": 5, "options": f"-c timezone=UTC -c statement_timeout={statement_timeout_ms}"}
    if unpooled:
        return create_engine(address, connect_args=options, poolclass=NullPool, hide_parameters=True)
    return create_engine(address, connect_args=options, pool_pre_ping=True, pool_timeout=5, hide_parameters=True)


def build_database_url() -> URL:
    """Assemble the service-account address of the database of db/ from the configured DB_ entries; its text form hides the password."""
    from config.config import DB_HOST, DB_NAME, DB_PORT, DB_SERVICE_ACCOUNT_NAME, DB_SERVICE_ACCOUNT_PASSWORD

    return URL.create("postgresql+psycopg", username=DB_SERVICE_ACCOUNT_NAME, password=DB_SERVICE_ACCOUNT_PASSWORD.get_secret_value(), host=DB_HOST, port=DB_PORT, database=DB_NAME)


def build_engine(statement_timeout_ms: int) -> Engine:
    """Open pooled service-account connections with the supplied statement limit."""
    return apply_engine_construction(build_database_url(), statement_timeout_ms, False)


def build_import_engine(statement_timeout_ms: int) -> Engine:
    """Open dedicated service-account sessions for guards and publication."""
    return apply_engine_construction(build_database_url(), statement_timeout_ms, True)


@functools.cache
def fetch_api_engine() -> Engine:
    """Give the one pooled engine of the API process, built on first use with the statement limit of a request."""
    return build_engine(API_STATEMENT_TIMEOUT_MS)


@contextmanager
def fetch_read_only_snapshot(engine: Engine) -> Iterator[Connection]:
    """Open one REPEATABLE READ READ ONLY transaction, so every read inside it sees the same state of the database, and roll it back at the end."""
    with engine.connect().execution_options(isolation_level="REPEATABLE READ", postgresql_readonly=True) as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


def apply_statement_timeout(connection: Connection, milliseconds: int) -> None:
    """Set the statement limit of the current transaction only, passing the value as a bound parameter."""
    if milliseconds < 1:
        raise ValueError("Database timeout must be positive")
    connection.execute(APPLY_STATEMENT_TIMEOUT_SQL, {"timeout": str(milliseconds)})