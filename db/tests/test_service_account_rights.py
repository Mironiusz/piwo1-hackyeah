"""
Checks against the local database that the service account has exactly the rights of the target schema.

A table whose grant is forgotten passes the revision and fails only in the service, so the rights are proven here by
behavior: the privileges the database reports, and the refusals of creating, dropping, altering and deleting.
"""

import psycopg
import pytest
from common_target_schema import fetch_service_account_rights
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError

pytestmark = pytest.mark.critical

TABLE_PRIVILEGES = ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER", "MAINTAIN")
INSUFFICIENT_PRIVILEGE = "42501"
SELECT_TABLE_PRIVILEGE_SQL = "SELECT has_table_privilege(current_user, :table, :privilege)"


def apply_refused_statement(connection: Connection, statement: str) -> str:
    """Runs a statement that must be refused inside a savepoint and gives the SQLSTATE of the refusal."""
    with pytest.raises(DBAPIError) as refusal, connection.begin_nested():
        connection.execute(text(statement))
    driver_error = refusal.value.orig
    assert isinstance(driver_error, psycopg.Error)
    assert driver_error.sqlstate is not None
    return driver_error.sqlstate


def test_service_account_has_exactly_the_rights_of_the_target_schema(service_connection: Connection) -> None:
    """Each table grants exactly its rights from the target schema, and the version table of Alembic grants none."""
    rights = fetch_service_account_rights()
    for table, granted in rights.items():
        for privilege in TABLE_PRIVILEGES:
            has_privilege = service_connection.execute(text(SELECT_TABLE_PRIVILEGE_SQL), {"table": f"public.{table}", "privilege": privilege}).scalar_one()
            assert has_privilege == (privilege in granted), (table, privilege)
    for privilege in TABLE_PRIVILEGES:
        assert not service_connection.execute(text(SELECT_TABLE_PRIVILEGE_SQL), {"table": "public.alembic_version", "privilege": privilege}).scalar_one(), privilege


def test_service_account_cannot_create_a_table_in_public(service_connection: Connection) -> None:
    """The service account is refused a new table in the public schema."""
    assert apply_refused_statement(service_connection, "CREATE TABLE public.not_allowed (id integer)") == INSUFFICIENT_PRIVILEGE


def test_service_account_cannot_drop_a_table_of_the_revision(service_connection: Connection) -> None:
    """The service account is refused dropping a table the first revision created."""
    assert apply_refused_statement(service_connection, "DROP TABLE vote") == INSUFFICIENT_PRIVILEGE


def test_service_account_cannot_alter_a_table_of_the_revision(service_connection: Connection) -> None:
    """The service account is refused altering a table the first revision created."""
    assert apply_refused_statement(service_connection, "ALTER TABLE vote ADD COLUMN not_allowed integer") == INSUFFICIENT_PRIVILEGE


def test_service_account_cannot_delete_a_vote(service_connection: Connection) -> None:
    """The service account is refused a write the target schema does not allow: no one deletes a vote."""
    assert apply_refused_statement(service_connection, "DELETE FROM vote") == INSUFFICIENT_PRIVILEGE
