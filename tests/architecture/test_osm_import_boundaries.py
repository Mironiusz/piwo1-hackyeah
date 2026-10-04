"""Keep importer integrations in the data layer and prevent reversed dependencies."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_importer_data_never_imports_rules_or_input_layers():
    for path in (ROOT / "data").glob("osm_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in {"service", "api", "worker"}, path
            elif isinstance(node, ast.Import):
                assert not {alias.name.split(".")[0] for alias in node.names} & {"service", "api", "worker"}, path


def test_http_transport_and_child_process_creation_stay_in_data():
    for path in (ROOT / "service").glob("osm_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"create_subprocess_exec", "create_subprocess_shell", "Popen", "AsyncClient", "Client"}, path


def test_importer_has_no_environment_reader_or_database_connection_factory():
    for directory in (ROOT / "service", ROOT / "data"):
        for path in directory.glob("osm_*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                    assert name not in {"getenv", "create_engine", "create_async_engine", "sessionmaker"}, path
