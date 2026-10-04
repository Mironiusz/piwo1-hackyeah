"""
Checks against the local database that the shared model describes the stored data: the same tables, columns and closed lists.

A drift between the model and the revisions shows here as a failing test instead of as a fact the import writes and the
backend does not know.
"""

import re

import pytest
from accessibility_db import closed_lists
from accessibility_db.tables import TableBase
from sqlalchemy import Connection, text

pytestmark = pytest.mark.critical

SELECT_TABLE_COLUMNS_SQL = """
SELECT column_name, is_nullable = 'YES' AS is_nullable FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = :table
ORDER BY ordinal_position
"""

SELECT_DOMAIN_CHECK_SQL = """
SELECT pg_get_constraintdef(con.oid) FROM pg_constraint con
JOIN pg_type t ON t.oid = con.contypid
WHERE t.typnamespace = 'public'::regnamespace AND t.typname = :domain AND con.contype = 'c'
"""

CLOSED_LIST_DOMAINS = {
    closed_lists.FactType: "fact_type",
    closed_lists.FactSource: "fact_source",
    closed_lists.OsmElementType: "osm_element_type",
    closed_lists.WayBarrierState: "way_barrier_state",
    closed_lists.KerbPointState: "kerb_point_state",
    closed_lists.VoteVerdict: "vote_verdict",
}


def test_mapped_tables_match_stored_columns(service_connection: Connection) -> None:
    """Every mapped table has the columns of its stored table, in the same order and with the same nullability."""
    assert len(TableBase.metadata.tables) == 7
    for name, table in TableBase.metadata.tables.items():
        stored = [(row.column_name, row.is_nullable) for row in service_connection.execute(text(SELECT_TABLE_COLUMNS_SQL), {"table": name})]
        assert [(column.name, column.nullable) for column in table.columns] == stored, name


def test_closed_lists_match_stored_domains(service_connection: Connection) -> None:
    """Every enumeration has exactly the values of the check of its domain, in the same order."""
    for closed_list, domain in CLOSED_LIST_DOMAINS.items():
        definition = service_connection.execute(text(SELECT_DOMAIN_CHECK_SQL), {"domain": domain}).scalar_one()
        assert re.findall(r"'(\w+)'", definition) == [member.value for member in closed_list], domain
