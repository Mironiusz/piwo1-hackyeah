"""Check the manual GTFS step entry point: its settings, its exit codes and the outcome line the operator reads."""

import logging
import sys
from pathlib import Path
from types import ModuleType

import pytest

from config.settings import ConfigurationError
from data.transit_build import TransitBuildError
from service.gtfs_import import GtfsImportResult
from worker.gtfs_import import apply_gtfs_import_action, apply_gtfs_import_report, build_gtfs_import_settings

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


def test_settings_carry_the_four_paths_of_the_importer(monkeypatch):
    apply_invented_config(monkeypatch)
    settings = build_gtfs_import_settings()
    assert settings.routing_root == ROOT / "routing"
    assert settings.workspace_root == ROOT / "import_workspace_root"
    assert settings.tool_directory == ROOT / "valhalla_tool_dir"
    assert settings.config_template == ROOT / "valhalla_config_template"


def test_missing_paths_are_named_with_their_file(monkeypatch):
    apply_invented_config(monkeypatch, VALHALLA_TOOL_DIR=None)
    with pytest.raises(ConfigurationError) as caught:
        build_gtfs_import_settings()
    assert str(caught.value) == "Missing or invalid configuration: VALHALLA_TOOL_DIR (.env.local)"


@pytest.mark.parametrize(
    ("result", "is_served", "code", "level"),
    [
        (GtfsImportResult("built", "fetched", "1-2"), True, 0, logging.INFO),
        (GtfsImportResult("built", "failed", "1-2"), True, 0, logging.INFO),
        (GtfsImportResult("reused", "failed", "1-2"), True, 0, logging.INFO),
        (GtfsImportResult("skipped", "not_run", None), True, 0, logging.INFO),
        (GtfsImportResult("skipped", "not_run", None), False, 1, logging.ERROR),
        (GtfsImportResult("no_gtfs_copy", "failed", None), False, 1, logging.ERROR),
        (GtfsImportResult("no_osm_copy", "fetched", None), False, 1, logging.ERROR),
    ],
)
def test_the_exit_code_says_whether_the_data_in_use_belongs_to_the_osm_copy_in_use(report, result, is_served, code, level):
    assert apply_gtfs_import_report(result, is_served, 12.34) == code
    record = report.records[-1]
    assert record.levelno == level
    message = record.getMessage()
    assert f"outcome={result.outcome}" in message and f"fetch={result.fetch}" in message and "duration_s=12.3" in message


def test_a_failed_fetch_building_from_the_kept_copy_exits_0(monkeypatch, report):
    apply_invented_config(monkeypatch)
    monkeypatch.setattr("worker.gtfs_import.apply_gtfs_import_command", lambda settings: GtfsImportResult("built", "failed", "1-2"))
    monkeypatch.setattr("worker.gtfs_import.fetch_transit_serves_copy_in_use", lambda root: True)
    assert apply_gtfs_import_action() == 0
    assert "fetch=failed transit=1-2 serves_copy_in_use=True" in report.records[-1].getMessage()


def test_a_named_failure_is_reported_with_its_constant_message_and_exits_1(monkeypatch, report):
    apply_invented_config(monkeypatch)

    def apply_failed_step(settings):
        raise TransitBuildError("Public transport construction tool failed")

    monkeypatch.setattr("worker.gtfs_import.apply_gtfs_import_command", apply_failed_step)
    monkeypatch.setattr("worker.gtfs_import.fetch_transit_serves_copy_in_use", lambda root: True)
    assert apply_gtfs_import_action() == 1
    assert "outcome=failed cause=TransitBuildError: Public transport construction tool failed" in report.records[-1].getMessage()


def test_an_unexpected_failure_is_reported_by_type_only_and_passed_on(monkeypatch, report):
    apply_invented_config(monkeypatch)

    def apply_failed_step(settings):
        raise LookupError("private detail")

    monkeypatch.setattr("worker.gtfs_import.apply_gtfs_import_command", apply_failed_step)
    with pytest.raises(LookupError):
        apply_gtfs_import_action()
    message = report.records[-1].getMessage()
    assert "cause=LookupError" in message and "private detail" not in message
