"""Keep the data layer of the community facts free of logging, so no line of it can carry the identifier of a person without an account (`plans/community_facts/COMMUNITY_FACTS_PLAN.md` D-9)."""

import ast
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "data" / "community_facts.py"


def test_community_facts_data_module_logs_nothing() -> None:
    """Import no logging and call neither print nor a logger factory, because the module handles the 32 bytes of persons without an account."""
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "logging" not in imported
    assert {"print", "getLogger"}.isdisjoint(names)
