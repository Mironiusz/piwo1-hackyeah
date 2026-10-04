"""Construct every database engine through one explicit account boundary."""

from pydantic import SecretStr
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import NullPool


def apply_engine_construction(address: SecretStr, statement_timeout_ms: int, unpooled: bool) -> Engine:
    """Create an engine with UTC sessions, bounded waits and hidden parameters."""
    if statement_timeout_ms < 1:
        raise ValueError("Database timeout must be positive")
    options = {"connect_timeout": 5, "options": f"-c timezone=UTC -c statement_timeout={statement_timeout_ms}"}
    if unpooled:
        return create_engine(address.get_secret_value(), connect_args=options, poolclass=NullPool, hide_parameters=True)
    return create_engine(address.get_secret_value(), connect_args=options, pool_pre_ping=True, pool_timeout=5, hide_parameters=True)


def build_engine(statement_timeout_ms: int) -> Engine:
    """Open pooled service-account connections with the supplied statement limit."""
    from config.config import DATABASE_URL

    return apply_engine_construction(DATABASE_URL, statement_timeout_ms, False)


def build_import_engine(statement_timeout_ms: int) -> Engine:
    """Open dedicated service-account sessions for guards and publication."""
    from config.config import DATABASE_URL

    return apply_engine_construction(DATABASE_URL, statement_timeout_ms, True)


def build_migration_engine(address: SecretStr) -> Engine:
    """Use an explicitly supplied owner address outside runtime configuration."""
    return apply_engine_construction(address, 30000, True)
