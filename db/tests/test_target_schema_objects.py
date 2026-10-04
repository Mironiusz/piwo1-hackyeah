"""
Checks against the local database that the stored data holds exactly the objects the first revision creates.

Objects that belong to an extension, such as the reference systems of PostGIS, the version table of Alembic and the
not-null constraints PostgreSQL 18 keeps in `pg_constraint` are not objects of the target schema and are left out.
"""

import pytest
from common_target_schema import build_created_object_names, build_table_columns, fetch_first_revision
from sqlalchemy import Connection, text

pytestmark = pytest.mark.critical

SELECT_EXTENSIONS_SQL = "SELECT extname FROM pg_extension WHERE extname <> 'plpgsql'"

SELECT_DOMAINS_SQL = """
SELECT t.typname FROM pg_type t
WHERE t.typnamespace = 'public'::regnamespace AND t.typtype = 'd'
AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.classid = 'pg_type'::regclass AND d.objid = t.oid AND d.deptype = 'e')
"""

SELECT_TABLES_SQL = """
SELECT c.relname FROM pg_class c
WHERE c.relnamespace = 'public'::regnamespace AND c.relkind = 'r' AND c.relname <> 'alembic_version'
AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.classid = 'pg_class'::regclass AND d.objid = c.oid AND d.deptype = 'e')
"""

SELECT_CONSTRAINTS_SQL = """
SELECT con.conname FROM pg_constraint con
WHERE con.contype IN ('p', 'f', 'u', 'c')
AND (con.conrelid IN (SELECT c.oid FROM pg_class c WHERE c.relnamespace = 'public'::regnamespace AND c.relname = ANY(:tables))
OR con.contypid IN (SELECT t.oid FROM pg_type t WHERE t.typnamespace = 'public'::regnamespace AND t.typname = ANY(:domains)))
"""

SELECT_INDEXES_SQL = "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND tablename = ANY(:tables)"

SELECT_TABLE_COLUMNS_SQL = """
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = :table
ORDER BY ordinal_position
"""


def test_stored_data_holds_exactly_the_objects_of_the_target_schema(service_connection: Connection) -> None:
    """The extensions, domains, tables, constraints, indexes and columns are those of the first revision and nothing else."""
    statements = fetch_first_revision().CREATE_TARGET_SCHEMA_SQL
    expected = build_created_object_names(statements)
    tables = sorted(expected["table"])
    domains = sorted(expected["domain"])
    assert set(service_connection.execute(text(SELECT_EXTENSIONS_SQL)).scalars()) == expected["extension"]
    assert set(service_connection.execute(text(SELECT_DOMAINS_SQL)).scalars()) == expected["domain"]
    assert set(service_connection.execute(text(SELECT_TABLES_SQL)).scalars()) == expected["table"]
    stored_constraints = set(service_connection.execute(text(SELECT_CONSTRAINTS_SQL), {"tables": tables, "domains": domains}).scalars())
    assert stored_constraints == expected["constraint"]
    stored_indexes = set(service_connection.execute(text(SELECT_INDEXES_SQL), {"tables": tables}).scalars())
    assert stored_indexes == expected["index"] | expected["unique_constraint"]
    for table, columns in build_table_columns(statements).items():
        assert tuple(service_connection.execute(text(SELECT_TABLE_COLUMNS_SQL), {"table": table}).scalars()) == columns, table


def test_postgis_exists_and_btree_gist_does_not(service_connection: Connection) -> None:
    """The first revision created PostGIS, and the extension of the former exclusion constraints is absent."""
    extensions = set(service_connection.execute(text(SELECT_EXTENSIONS_SQL)).scalars())
    assert "postgis" in extensions
    assert "btree_gist" not in extensions
