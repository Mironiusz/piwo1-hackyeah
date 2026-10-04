"""Check the standalone tile step entry point: its settings, its exit codes and the outcome line the operator reads."""

import logging
import sys
from pathlib import Path
from types import ModuleType

import pytest

from config.settings import ConfigurationError
from service.tile_archive import TileArchiveError, TileArchiveResult
from worker.tile_archive import apply_tile_archive_action, apply_tile_archive_report, build_tile_archive_settings, build_tile_archive_workspace_root

ROOT = Path(__file__).resolve().parent
PATH_ENTRIES = ("TILE_ARCHIVE_SOURCE", "TILE_ARCHIVE_DIR", "IMPORT_WORKSPACE_ROOT")


def apply_invented_config(monkeypatch: pytest.MonkeyPatch, **paths: Path | None) -> None:
    """Stand in for the configuration facade so the test needs no environment files."""
    module = ModuleType("config.config")
    for name in PATH_ENTRIES:
        setattr(module, name, paths.get(name, ROOT / name.lower()))
    monkeypatch.setitem(sys.modules, "config.config", module)


@pytest.fixture
def report(caplog):
    """Capture the application logger, which does not propagate to the root logger pytest listens on."""
    application = logging.getLogger("piwo1-hackyeah")
    previous_level = application.level
    application.addHandler(caplog.handler)
    caplog.handler.setLevel(logging.INFO)
    application.setLevel(logging.INFO)
    yield caplog
    application.removeHandler(caplog.handler)
    application.setLevel(previous_level)


def test_settings_carry_the_source_and_the_served_directory(monkeypatch):
    """Build the settings of the step from the two configured places."""
    apply_invented_config(monkeypatch)
    settings = build_tile_archive_settings()
    assert settings.source_path == ROOT / "tile_archive_source"
    assert settings.served_directory == ROOT / "tile_archive_dir"
    assert build_tile_archive_workspace_root() == ROOT / "import_workspace_root"


def test_missing_places_are_named_with_their_file(monkeypatch):
    """Name both missing places of the archive and their file, without any value."""
    apply_invented_config(monkeypatch, TILE_ARCHIVE_SOURCE=None, TILE_ARCHIVE_DIR=None)
    with pytest.raises(ConfigurationError) as caught:
        build_tile_archive_settings()
    assert str(caught.value) == "Missing or invalid configuration: TILE_ARCHIVE_SOURCE (.env.local), TILE_ARCHIVE_DIR (.env.local)"


def test_a_missing_workspace_is_named_with_its_file(monkeypatch):
    """Name the missing import workspace, whose exclusion the command needs, and its file."""
    apply_invented_config(monkeypatch, IMPORT_WORKSPACE_ROOT=None)
    with pytest.raises(ConfigurationError) as caught:
        build_tile_archive_workspace_root()
    assert str(caught.value) == "Missing or invalid configuration: IMPORT_WORKSPACE_ROOT (.env.local)"


@pytest.mark.parametrize(("outcome", "code"), [("loaded", 0), ("unchanged", 0), ("skipped", 2)])
def test_each_outcome_has_its_exit_code_and_a_line_without_a_path(report, outcome, code):
    """Exit 0 when the archive is in place and 2 when another run held the exclusion, writing the outcome without any path."""
    assert apply_tile_archive_report(TileArchiveResult(outcome), 12.34) == code
    record = report.records[-1]
    assert record.levelno == logging.INFO
    assert record.getMessage() == f"Tile archive outcome={outcome} duration_s=12.3"


def test_a_named_failure_is_reported_with_its_reason_and_exits_1(monkeypatch, report):
    """AC-6: a failed step tells the person why the archive is not in place, with its reason code and no path, and exits 1."""
    apply_invented_config(monkeypatch)

    def apply_failed_step(settings, workspace_root):
        raise TileArchiveError("source_mismatch")

    monkeypatch.setattr("worker.tile_archive.apply_tile_archive_command", apply_failed_step)
    assert apply_tile_archive_action() == 1
    record = report.records[-1]
    assert record.levelno == logging.ERROR
    message = record.getMessage()
    assert "outcome=failed cause=TileArchiveError: Tile archive step failed: source_mismatch" in message
    assert str(ROOT) not in message


def test_an_unexpected_failure_is_reported_by_type_only_and_passed_on(monkeypatch, report):
    """AC-6: an unforeseen failure is named by its type alone and passed on to the shared wrapper, which exits 1."""
    apply_invented_config(monkeypatch)

    def apply_failed_step(settings, workspace_root):
        raise RuntimeError("private detail")

    monkeypatch.setattr("worker.tile_archive.apply_tile_archive_command", apply_failed_step)
    with pytest.raises(RuntimeError):
        apply_tile_archive_action()
    message = report.records[-1].getMessage()
    assert "outcome=failed cause=RuntimeError" in message and "private detail" not in message
