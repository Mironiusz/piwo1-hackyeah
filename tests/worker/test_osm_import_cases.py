"""Check the manual import entry point: its settings, its exit codes and the outcome line the operator reads."""

import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest

from config.settings import ConfigurationError
from service.osm_import import OsmImportResult
from service.osm_publication import OsmPublicationCounts
from service.osm_source_validation import OsmSourceError
from worker.osm_import import apply_osm_import_action, apply_osm_import_report, build_osm_import_settings

ROOT = Path(__file__).resolve().parent


def apply_invented_config(monkeypatch: pytest.MonkeyPatch, **paths: Path | None) -> None:
    """Stand in for the configuration facade so the test needs no environment files."""
    module = ModuleType("config.config")
    values = {"BUSINESS_TIMEZONE": "Europe/Warsaw", "ROUTING_DATA_DIR": ROOT / "routing"}
    values.update({name: paths.get(name, ROOT / name.lower()) for name in ("IMPORT_WORKSPACE_ROOT", "VALHALLA_TOOL_DIR", "VALHALLA_CONFIG_TEMPLATE")})
    for name, value in values.items():
        setattr(module, name, value)
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


def test_settings_carry_the_configured_paths_and_zone(monkeypatch):
    apply_invented_config(monkeypatch)
    settings = build_osm_import_settings()
    assert settings.routing_root == ROOT / "routing"
    assert settings.tool_directory == ROOT / "valhalla_tool_dir"
    assert str(settings.zone) == "Europe/Warsaw"


def test_missing_import_paths_are_named_with_their_file(monkeypatch):
    apply_invented_config(monkeypatch, IMPORT_WORKSPACE_ROOT=None, VALHALLA_CONFIG_TEMPLATE=None)
    with pytest.raises(ConfigurationError) as caught:
        build_osm_import_settings()
    assert str(caught.value) == "Missing or invalid configuration: IMPORT_WORKSPACE_ROOT (.env.local), VALHALLA_CONFIG_TEMPLATE (.env.local)"


@pytest.mark.parametrize(
    ("outcome", "code", "level"),
    [("updated", 0, logging.INFO), ("unchanged", 0, logging.INFO), ("skipped", 2, logging.INFO), ("routing_incomplete", 1, logging.ERROR), ("commit_unknown", 1, logging.ERROR)],
)
def test_each_outcome_has_its_exit_code_and_one_report_line(report, outcome, code, level):
    is_updated = outcome == "updated"
    result = OsmImportResult(outcome, datetime(2026, 10, 3, tzinfo=UTC), OsmPublicationCounts(3, 2, 4, 5) if is_updated else None, 24 if is_updated else None)
    assert apply_osm_import_report(result, 12.34) == code
    record = report.records[-1]
    assert record.levelno == level
    assert f"outcome={outcome}" in record.getMessage() and "duration_s=12.3" in record.getMessage()
    assert record.getMessage().endswith("invalid_areas=24" if is_updated else "invalid_areas=-")


def test_a_named_failure_is_reported_with_its_constant_message_and_exits_1(monkeypatch, report):
    apply_invented_config(monkeypatch)

    def apply_failed_import(settings):
        raise OsmSourceError("Source checksum mismatch")

    monkeypatch.setattr("worker.osm_import.apply_osm_import_command", apply_failed_import)
    assert apply_osm_import_action() == 1
    assert "outcome=failed cause=OsmSourceError: Source checksum mismatch" in report.records[-1].getMessage()


def test_an_unexpected_failure_is_reported_by_type_only_and_passed_on(monkeypatch, report):
    apply_invented_config(monkeypatch)

    def apply_failed_import(settings):
        raise LookupError("private detail")

    monkeypatch.setattr("worker.osm_import.apply_osm_import_command", apply_failed_import)
    with pytest.raises(LookupError):
        apply_osm_import_action()
    message = report.records[-1].getMessage()
    assert "cause=LookupError" in message and "private detail" not in message
