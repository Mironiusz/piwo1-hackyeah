"""Check real session defaults and service privilege restrictions."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

pytestmark = pytest.mark.critical


def test_service_sessions_use_utc_and_cannot_create_roles(scratch_database):
    """Observe UTC independently of host defaults and reject service DDL."""
    _owner, service = scratch_database
    with service.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        assert connection.execute(text("SHOW TimeZone")).scalar_one() == "UTC"
        assert connection.execute(text("SELECT lower('ŁÓDŹ')")).scalar_one() == "łódź"
        assert connection.execute(text("SELECT CAST('Zażółć gęślą jaźń' AS text)")).scalar_one() == "Zażółć gęślą jaźń"
        assert not connection.execute(text("SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication FROM pg_roles WHERE rolname=current_user")).scalar_one()
        with pytest.raises(SQLAlchemyError):
            connection.execute(text("CREATE ROLE backend_skeleton_forbidden_ddl"))
