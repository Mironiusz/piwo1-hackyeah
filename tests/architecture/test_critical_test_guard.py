"""
Guards the rule that a session with a critical test refuses to start outside the local environment.

The critical tests of the repository live in `db/tests/` and write to a real database. Their guard is the hook
`pytest_collection_finish` of `db/tests/common_critical_guard.py`, which `db/tests/conftest.py` exposes to pytest
(`docs/standards/standard_tests.md`, section Test layers). This test loads the guard from its file, because its
directory is not a package of this repository, and checks it by behavior.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT_DIR / "db" / "tests" / "common_critical_guard.py"
CONFTEST_PATH = ROOT_DIR / "db" / "tests" / "conftest.py"


class CollectedItem:
    """A collected test that carries the critical marker or not."""

    def __init__(self, is_critical: bool) -> None:
        """Keeps whether the test is critical."""
        self.is_critical = is_critical

    def get_closest_marker(self, name: str) -> object | None:
        """Returns a marker for `critical` on a critical test, as pytest does, and nothing otherwise."""
        return object() if name == "critical" and self.is_critical else None


class CollectedSession:
    """A session that holds the collected tests, as pytest gives it to the hook."""

    def __init__(self, items: list[CollectedItem]) -> None:
        """Keeps the collected tests."""
        self.items = items


def fetch_guard() -> ModuleType:
    """Loads the guard module from its file."""
    spec = importlib.util.spec_from_file_location("critical_guard", GUARD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_conftest_of_the_critical_tests_exposes_the_guard() -> None:
    """The conftest of `db/tests/` imports the hook of the guard, so pytest runs it for every session there."""
    assert "from common_critical_guard import pytest_collection_finish" in CONFTEST_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("environment", ["target", ""])
def test_guard_stops_a_critical_session_outside_the_local_environment(monkeypatch: pytest.MonkeyPatch, environment: str) -> None:
    """A critical test collected with another or no environment ends the session with the usage error code."""
    monkeypatch.setenv("DB_ENVIRONMENT", environment)
    with pytest.raises(pytest.exit.Exception) as stop:
        fetch_guard().pytest_collection_finish(CollectedSession([CollectedItem(is_critical=True)]))
    assert stop.value.returncode == pytest.ExitCode.USAGE_ERROR


def test_guard_lets_a_critical_session_run_locally(monkeypatch: pytest.MonkeyPatch) -> None:
    """A critical test collected in the local environment runs."""
    monkeypatch.setenv("DB_ENVIRONMENT", "local")
    fetch_guard().pytest_collection_finish(CollectedSession([CollectedItem(is_critical=True)]))


def test_guard_lets_a_session_without_critical_tests_run_anywhere(monkeypatch: pytest.MonkeyPatch) -> None:
    """A session without a critical test is never stopped by the guard."""
    monkeypatch.setenv("DB_ENVIRONMENT", "target")
    fetch_guard().pytest_collection_finish(CollectedSession([CollectedItem(is_critical=False)]))
