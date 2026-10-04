"""
Checks without a database that the first revision is the target schema of `docs/product/schema.md`, statement by statement.

Reviewing a revision is a line by line comparison with the target schema (`docs/standards/standard_database.md`); for
the first revision that comparison is mechanical, so this test makes it.
"""

import pytest
from common_target_schema import build_granted_rights, build_normalized_statement, fetch_first_revision, fetch_schema_statements, fetch_service_account_rights


def test_first_revision_creates_the_target_schema_statement_by_statement() -> None:
    """Every statement of the target schema stands in the first revision in the same order and with the same text."""
    revision = fetch_first_revision()
    expected = [build_normalized_statement(statement) for statement in fetch_schema_statements()]
    actual = [build_normalized_statement(statement) for statement in revision.CREATE_TARGET_SCHEMA_SQL]
    assert actual == expected


def test_first_revision_grants_every_row_of_the_rights_table() -> None:
    """The grants of the first revision give each table exactly the rights of the table Rights of the service account."""
    revision = fetch_first_revision()
    assert build_granted_rights(revision.GRANT_SERVICE_ACCOUNT_SQL) == fetch_service_account_rights()


def test_first_revision_refuses_a_downgrade() -> None:
    """Going below the first revision is refused with a message that points to recreating the database."""
    revision = fetch_first_revision()
    with pytest.raises(NotImplementedError, match="Recreate the local database"):
        revision.downgrade()
