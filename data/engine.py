"""Construct every database engine of the service account of db/ through one explicit account boundary."""

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.pool import NullPool


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
