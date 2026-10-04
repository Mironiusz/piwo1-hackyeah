"""Guards the dependency direction of the sample provider and its shared records."""

import ast
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "relative_path, forbidden",
    [("data/sample_data.py", {"service", "api", "worker"}), ("service/sample_data.py", {"api", "worker"}), ("common_sample_data.py", {"api", "service", "data", "worker", "config"})],
)
def test_sample_modules_preserve_the_one_way_layer_dependencies(relative_path: str, forbidden: set[str]) -> None:
    """Inspects local and module-level imports without requiring runtime configuration."""
    tree = ast.parse((ROOT_DIR / relative_path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported = {alias.name.split(".", 1)[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported = {(node.module or "").split(".", 1)[0]}
        else:
            continue
        assert not imported.intersection(forbidden), f"{relative_path} imports a forbidden layer"
