"""Check how the Valhalla tools are called, how their archive is finalized and how a failed or late tool is reported."""

import json
import os
import stat
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from common_time import DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from data.import_process import ImportProcessFailedError
from data.import_workspace import WorkspaceLease, apply_workspace_exclusion, apply_workspace_recovery
from data.osm_valhalla import OsmTileBuildError, apply_osm_valhalla_config, apply_osm_valhalla_tiles, fetch_osm_valhalla_template

STATE_AT = datetime(2026, 10, 3, 0, 0, tzinfo=UTC)
INVENTED_LEASE = cast(WorkspaceLease, object())


def build_test_deadline():
    """Give the tools a budget no invented tool can exhaust."""
    return build_deadline(60, fetch_monotonic_seconds())


def apply_invented_tools(directory: Path, extract_body: str, tiles_body: str = "") -> Path:
    """Write executable Python tools under the Valhalla names; the extract tool writes the archive named in its configuration."""
    directory.mkdir()
    header = f"#!{sys.executable}\nimport json, sys, time\nfrom pathlib import Path\nconfig = json.loads(Path(sys.argv[2]).read_text())\n"
    for name, body in (("valhalla_build_tiles", tiles_body), ("valhalla_build_extract", extract_body)):
        tool = directory / name
        tool.write_text(header + body)
        tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
    return directory


def test_tools_run_in_order_through_the_supervisor_and_the_archive_carries_the_source_instant(tmp_path, monkeypatch):
    calls = []
    archive = tmp_path / "valhalla_tiles.tar"

    def apply_invented_process(lease, arguments, deadline):
        calls.append(arguments)
        if arguments[0].endswith("valhalla_build_extract"):
            archive.write_bytes(b"invented archive")

    monkeypatch.setattr("data.osm_valhalla.apply_import_process", apply_invented_process)
    apply_osm_valhalla_tiles(INVENTED_LEASE, tmp_path / "build.json", tmp_path / "tools", tmp_path / "network.osm.pbf", archive, STATE_AT, build_test_deadline())
    assert calls == [
        [str(tmp_path / "tools" / "valhalla_build_tiles"), "-c", str(tmp_path / "build.json"), str(tmp_path / "network.osm.pbf")],
        [str(tmp_path / "tools" / "valhalla_build_extract"), "-c", str(tmp_path / "build.json")],
    ]
    assert int(archive.stat().st_mtime) == int(STATE_AT.timestamp())


def test_failed_tool_is_a_named_build_failure(tmp_path, monkeypatch):
    def apply_failed_process(lease, arguments, deadline):
        raise ImportProcessFailedError("Import process failed")

    monkeypatch.setattr("data.osm_valhalla.apply_import_process", apply_failed_process)
    with pytest.raises(OsmTileBuildError, match="tool failed"):
        apply_osm_valhalla_tiles(INVENTED_LEASE, tmp_path / "b.json", tmp_path, tmp_path / "n.pbf", tmp_path / "t.tar", STATE_AT, build_test_deadline())


def test_missing_archive_after_the_tools_is_a_named_build_failure(tmp_path, monkeypatch):
    monkeypatch.setattr("data.osm_valhalla.apply_import_process", lambda lease, arguments, deadline: None)
    with pytest.raises(OsmTileBuildError, match="missing or empty"):
        apply_osm_valhalla_tiles(INVENTED_LEASE, tmp_path / "b.json", tmp_path, tmp_path / "n.pbf", tmp_path / "t.tar", STATE_AT, build_test_deadline())


def test_existing_archive_and_naive_instant_are_refused_before_any_tool(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("data.osm_valhalla.apply_import_process", lambda lease, arguments, deadline: calls.append(arguments))
    archive = tmp_path / "t.tar"
    archive.write_bytes(b"existing")
    with pytest.raises(OsmTileBuildError, match="already exists"):
        apply_osm_valhalla_tiles(INVENTED_LEASE, tmp_path / "b.json", tmp_path, tmp_path / "n.pbf", archive, STATE_AT, build_test_deadline())
    with pytest.raises(OsmTileBuildError, match="aware"):
        apply_osm_valhalla_tiles(INVENTED_LEASE, tmp_path / "b.json", tmp_path, tmp_path / "n.pbf", tmp_path / "u.tar", datetime(2026, 10, 3), build_test_deadline())
    assert calls == []
    assert archive.read_bytes() == b"existing"


def test_template_must_be_a_readable_json_object(tmp_path):
    template = tmp_path / "valhalla.json"
    template.write_text(json.dumps({"mjolnir": {"concurrency": 2}}))
    assert fetch_osm_valhalla_template(template) == {"mjolnir": {"concurrency": 2}}
    template.write_text("[]")
    with pytest.raises(OsmTileBuildError, match="object"):
        fetch_osm_valhalla_template(template)
    template.write_text("{")
    with pytest.raises(OsmTileBuildError, match="Cannot read"):
        fetch_osm_valhalla_template(template)
    with pytest.raises(OsmTileBuildError, match="Cannot read"):
        fetch_osm_valhalla_template(tmp_path / "missing.json")


def test_build_configuration_is_never_overwritten(tmp_path):
    path = tmp_path / "build.json"
    apply_osm_valhalla_config(path, {"mjolnir": {}})
    with pytest.raises(OsmTileBuildError):
        apply_osm_valhalla_config(path, {"mjolnir": {"other": True}})
    assert json.loads(path.read_text()) == {"mjolnir": {}}


@pytest.mark.integration
@pytest.mark.skipif(sys.platform != "linux", reason="Real supervised tools need the Linux process supervisor")
def test_real_supervised_tools_write_the_archive(tmp_path):
    tools = apply_invented_tools(tmp_path / "tools", "Path(config['mjolnir']['tile_extract']).write_bytes(b'invented archive')\n")
    archive = tmp_path / "valhalla_tiles.tar"
    with apply_workspace_exclusion(tmp_path / "workspace") as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        config_path = lease.workspace / "build.json"
        apply_osm_valhalla_config(config_path, {"mjolnir": {"tile_extract": str(archive)}})
        apply_osm_valhalla_tiles(lease, config_path, tools, tmp_path / "network.osm.pbf", archive, STATE_AT, build_test_deadline())
    assert archive.read_bytes() == b"invented archive"
    assert int(os.stat(archive).st_mtime) == int(STATE_AT.timestamp())


@pytest.mark.integration
@pytest.mark.skipif(sys.platform != "linux", reason="Real supervised tools need the Linux process supervisor")
def test_real_tool_past_the_deadline_is_stopped_without_an_archive(tmp_path):
    tools = apply_invented_tools(tmp_path / "tools", "Path(config['mjolnir']['tile_extract']).write_bytes(b'late')\n", "time.sleep(30)\n")
    archive = tmp_path / "valhalla_tiles.tar"
    with apply_workspace_exclusion(tmp_path / "workspace") as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        config_path = lease.workspace / "build.json"
        apply_osm_valhalla_config(config_path, {"mjolnir": {"tile_extract": str(archive)}})
        with pytest.raises(DeadlineExpiredError):
            apply_osm_valhalla_tiles(lease, config_path, tools, tmp_path / "network.osm.pbf", archive, STATE_AT, build_deadline(0.5, fetch_monotonic_seconds()))
    assert not archive.exists()
