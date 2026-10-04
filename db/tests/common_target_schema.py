"""
Shared reads of the target schema and of the first revision for the tests of `db/tests/`.

The target schema is read from `docs/product/schema.md` in the repository, and the first revision is loaded from its
file, because its module name starts with a digit and cannot be imported by name.
"""

import importlib.util
import re
from importlib.resources import files
from pathlib import Path
from types import ModuleType

SCHEMA_DOCUMENT_PATH = Path(__file__).resolve().parents[2] / "docs" / "product" / "schema.md"
FIRST_REVISION_RESOURCE = "migrations/versions/0001_target_schema.py"
SQL_BLOCK_PATTERN = re.compile(r"```sql\n(.*?)```", re.DOTALL)
STATEMENT_END_PATTERN = re.compile(r";\s*\n")
RIGHTS_ROW_PATTERN = re.compile(r"^\|\s*((?:`\w+`(?:,\s*)?)+)\s*\|\s*([a-z, ]+?)\s*\|$", re.MULTILINE)
GRANT_PATTERN = re.compile(r"GRANT (.+?) ON (.+?) TO %I")
CREATED_NAME_PATTERNS = {
    "extension": re.compile(r"^CREATE EXTENSION (\w+)"),
    "domain": re.compile(r"^CREATE DOMAIN (\w+)"),
    "table": re.compile(r"^CREATE TABLE (\w+)"),
    "index": re.compile(r"^CREATE (?:UNIQUE )?INDEX (\w+)"),
}
CONSTRAINT_PATTERN = re.compile(r"CONSTRAINT (\w+) (PRIMARY KEY|FOREIGN KEY|UNIQUE|CHECK)")
COLUMN_LINE_PATTERN = re.compile(r"^\s+(\w+) ", re.MULTILINE)


def fetch_schema_statements() -> tuple[str, ...]:
    """Reads every statement of the `sql` blocks of the target schema, in order, without the final semicolon."""
    text = SCHEMA_DOCUMENT_PATH.read_text(encoding="utf-8")
    return tuple(statement.strip() for block in SQL_BLOCK_PATTERN.findall(text) for statement in STATEMENT_END_PATTERN.split(block) if statement.strip())


def fetch_service_account_rights() -> dict[str, frozenset[str]]:
    """Reads the table Rights of the service account of the target schema as the rights of each table, in upper case."""
    text = SCHEMA_DOCUMENT_PATH.read_text(encoding="utf-8")
    rights: dict[str, frozenset[str]] = {}
    for tables, privileges in RIGHTS_ROW_PATTERN.findall(text):
        for table in re.findall(r"`(\w+)`", tables):
            rights[table] = frozenset(privilege.strip().upper() for privilege in privileges.split(","))
    return rights


def fetch_first_revision() -> ModuleType:
    """Loads the module of the first revision of the chain from its file in the package."""
    path = Path(str(files("accessibility_db") / FIRST_REVISION_RESOURCE))
    spec = importlib.util.spec_from_file_location("first_revision", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"The first revision cannot be loaded from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_normalized_statement(statement: str) -> str:
    """Builds the statement with every run of whitespace collapsed to one space, for a comparison of the text alone."""
    return " ".join(statement.split())


def build_granted_rights(grant_statements: tuple[str, ...]) -> dict[str, frozenset[str]]:
    """Builds the rights of each table from the grant statements of a revision."""
    rights: dict[str, frozenset[str]] = {}
    for statement in grant_statements:
        match = GRANT_PATTERN.search(statement)
        if match is None:
            raise ValueError(f"Not a grant statement: {statement}")
        privileges = frozenset(privilege.strip() for privilege in match.group(1).split(","))
        for table in match.group(2).split(","):
            rights[table.strip()] = privileges
    return rights


def build_created_object_names(statements: tuple[str, ...]) -> dict[str, frozenset[str]]:
    """Builds the lower-case names of the extensions, domains, tables, constraints and indexes the statements create."""
    names: dict[str, set[str]] = {kind: set() for kind in ("extension", "domain", "table", "constraint", "unique_constraint", "index")}
    for statement in statements:
        for kind, pattern in CREATED_NAME_PATTERNS.items():
            match = pattern.match(statement)
            if match is not None:
                names[kind].add(match.group(1).lower())
        for constraint_name, constraint_kind in CONSTRAINT_PATTERN.findall(statement):
            names["constraint"].add(constraint_name.lower())
            if constraint_kind in ("PRIMARY KEY", "UNIQUE"):
                names["unique_constraint"].add(constraint_name.lower())
    return {kind: frozenset(found) for kind, found in names.items()}


def build_table_columns(statements: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Builds the column names of each created table, in the order of its statement."""
    columns: dict[str, tuple[str, ...]] = {}
    for statement in statements:
        match = CREATED_NAME_PATTERNS["table"].match(statement)
        if match is not None:
            columns[match.group(1)] = tuple(name for name in COLUMN_LINE_PATTERN.findall(statement) if name != "CONSTRAINT")
    return columns
