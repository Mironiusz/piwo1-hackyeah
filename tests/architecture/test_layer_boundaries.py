"""Guard the runtime layer directions and centralized connection construction."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = {"api": {"data", "worker"}, "service": {"api", "worker"}, "data": {"api", "service", "worker"}, "worker": {"api", "data"}, "config": {"api", "service", "data", "worker"}}


@pytest.mark.parametrize("layer", FORBIDDEN)
def test_layer_imports_follow_one_way_boundaries(layer):
    """Reject upward imports while allowing shared configuration and time."""
    for path in (ROOT / layer).rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in FORBIDDEN[layer], f"Invalid dependency in {path.relative_to(ROOT)}"


def test_engine_construction_has_one_runtime_location():
    """Reject direct driver opens and engine construction in other layers."""
    for layer in FORBIDDEN:
        for path in (ROOT / layer).rglob("*.py"):
            if path == ROOT / "data" / "engine.py":
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom):
                    assert not any(alias.name in {"create_engine", "ConnectionPool"} for alias in node.names)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    assert not (node.func.value.id in {"psycopg", "psycopg2"} and node.func.attr == "connect")
