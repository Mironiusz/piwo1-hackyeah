"""Check the sessions the backend engine opens; the locale, extensions and account rights of the database are checked by db/tests."""

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.critical


def test_service_sessions_use_utc_and_keep_polish_text(scratch_database):
    """Observe UTC independently of host defaults and a Polish text round trip through the service engine."""
    _owner, service = scratch_database
    with service.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        assert connection.execute(text("SHOW TimeZone")).scalar_one() == "UTC"
        assert connection.execute(text("SELECT CAST('Zażółć gęślą jaźń' AS text)")).scalar_one() == "Zażółć gęślą jaźń"
