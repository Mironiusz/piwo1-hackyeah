"""Check the sessions the backend engine opens; the locale, extensions and account rights of the database are checked by db/tests."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from data.engine import API_STATEMENT_TIMEOUT_MS, apply_statement_timeout, build_engine, fetch_read_only_snapshot

pytestmark = pytest.mark.critical

READ_ONLY_TRANSACTION_SQLSTATE = "25006"
QUERY_CANCELED_SQLSTATE = "57014"


@pytest.fixture
def api_engine():
    """Open the pooled engine of a request and dispose of it after the test."""
    engine = build_engine(API_STATEMENT_TIMEOUT_MS)
    yield engine
    engine.dispose()


def test_read_only_snapshot_refuses_a_write(api_engine):
    """Open a REPEATABLE READ READ ONLY transaction in which the database refuses any write."""
    with fetch_read_only_snapshot(api_engine) as connection:
        assert connection.execute(text("SHOW transaction_isolation")).scalar_one() == "repeatable read"
        assert connection.execute(text("SHOW transaction_read_only")).scalar_one() == "on"
        with pytest.raises(DBAPIError) as refused:
            connection.execute(text("CREATE TEMPORARY TABLE route_snapshot_write_probe (value integer)"))
    assert getattr(refused.value.orig, "sqlstate", None) == READ_ONLY_TRANSACTION_SQLSTATE


def test_statement_timeout_applies_to_the_transaction(api_engine):
    """Cancel a statement over the limit set for one transaction, and leave the next transaction with the limit of the engine."""
    with fetch_read_only_snapshot(api_engine) as connection:
        apply_statement_timeout(connection, 100)
        assert connection.execute(text("SHOW statement_timeout")).scalar_one() == "100ms"
        with pytest.raises(DBAPIError) as canceled:
            connection.execute(text("SELECT pg_sleep(1)"))
    assert getattr(canceled.value.orig, "sqlstate", None) == QUERY_CANCELED_SQLSTATE
    with fetch_read_only_snapshot(api_engine) as connection:
        assert connection.execute(text("SHOW statement_timeout")).scalar_one() == "5s"


def test_service_sessions_use_utc_and_keep_polish_text(scratch_database):
    """Observe UTC independently of host defaults and a Polish text round trip through the service engine."""
    _owner, service = scratch_database
    with service.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        assert connection.execute(text("SHOW TimeZone")).scalar_one() == "UTC"
        assert connection.execute(text("SELECT CAST('Zażółć gęślą jaźń' AS text)")).scalar_one() == "Zażółć gęślą jaźń"
