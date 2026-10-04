"""
Checks against the local database what its setup gives without any revision: the locale and the available extensions.

These are the critical tests of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 that do not depend on the
first revision; they belong to `db/` because its image and its script create the database.
"""

import pytest
from sqlalchemy import Connection, text

pytestmark = pytest.mark.critical

SELECT_LOWER_CASE_SQL = "SELECT lower('ŁÓDŹ')"
SELECT_BYTE_ORDER_SQL = "SELECT 'B' < 'a'"
SELECT_AVAILABLE_PGROUTING_SQL = "SELECT installed_version FROM pg_available_extensions WHERE name = 'pgrouting'"


def test_database_lowers_polish_letters_and_compares_text_by_bytes(service_connection: Connection) -> None:
    """The database lowers Polish capital letters and orders text by bytes, as the builtin locale C.UTF-8 does."""
    assert service_connection.execute(text(SELECT_LOWER_CASE_SQL)).scalar_one() == "łódź"
    assert service_connection.execute(text(SELECT_BYTE_ORDER_SQL)).scalar_one() is True


def test_pgrouting_is_available_and_not_created(service_connection: Connection) -> None:
    """pgRouting is available in the image, and no revision creates it."""
    rows = service_connection.execute(text(SELECT_AVAILABLE_PGROUTING_SQL)).all()
    assert len(rows) == 1
    assert rows[0].installed_version is None
