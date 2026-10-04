"""Check how the public transport tools are called, how the archive is stamped and placed, and the pointer of the routing data with public transport."""

import os
import shlex
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from common_time import build_deadline, fetch_monotonic_seconds
from data.import_process import ImportProcessFailedError
from data.import_workspace import WorkspaceLease
from data.routing_data import RoutingDataError
from data.transit_build import (
    TransitBuildError,
    apply_transit_build,
    apply_transit_pointer,
    apply_transit_preparation,
    build_transit_name,
    fetch_transit_pointer,
    resolve_transit_copy_name,
)

pytestmark = pytest.mark.integration

STATE_AT = datetime(2026, 10, 3, tzinfo=UTC)
NAME = "1790985600-1791090000"
INVENTED_LEASE = cast(WorkspaceLease, object())


def apply_invented_tools(monkeypatch, calls: list[list[str]], timezone_path: Path, archive_path: Path, timezone_bytes: bytes = b"invented timezones") -> None:
    """Replace the supervisor of both tool modules: the shell writes the timezone database and the extract tool writes the archive."""

    def apply_process(lease, arguments, deadline):
        calls.append(arguments)
        if arguments[0] == "/bin/sh":
            timezone_path.write_bytes(timezone_bytes)
        if arguments[0].endswith("valhalla_build_extract"):
            archive_path.write_bytes(b"invented archive")

    monkeypatch.setattr("data.transit_build.apply_import_process", apply_process)
    monkeypatch.setattr("data.osm_valhalla.apply_import_process", apply_process)


def build_test_arguments(tmp_path: Path, preparation: Path) -> dict:
    """Give one build invented paths inside the temporary directory."""
    return {
        "lease": INVENTED_LEASE,
        "config_path": tmp_path / "valhalla_transit.json",
        "tool_directory": tmp_path / "tools",
        "network_path": tmp_path / "network.osm.pbf",
        "timezone_path": tmp_path / "timezones.sqlite",
        "preparation": preparation,
        "root": tmp_path / "routing",
        "name": NAME,
        "state_at": STATE_AT,
        "deadline": build_deadline(60, fetch_monotonic_seconds()),
    }


def test_tools_run_in_order_and_the_archive_carries_the_copy_instant_without_a_pointer(tmp_path, monkeypatch):
    calls: list[list[str]] = []
    (tmp_path / "routing").mkdir()
    preparation = apply_transit_preparation(tmp_path / "routing")
    apply_invented_tools(monkeypatch, calls, tmp_path / "timezones.sqlite", preparation / "valhalla_tiles.tar")
    placed = apply_transit_build(**build_test_arguments(tmp_path, preparation))
    tools, config = tmp_path / "tools", str(tmp_path / "valhalla_transit.json")
    assert calls == [
        ["/bin/sh", "-c", f"{shlex.quote(str(tools / 'valhalla_build_timezones'))} > {shlex.quote(str(tmp_path / 'timezones.sqlite'))}"],
        [str(tools / "valhalla_ingest_transit"), "-c", config],
        [str(tools / "valhalla_convert_transit"), "-c", config],
        [str(tools / "valhalla_build_tiles"), "-c", config, str(tmp_path / "network.osm.pbf")],
        [str(tools / "valhalla_build_extract"), "-c", config],
    ]
    assert placed == tmp_path / "routing" / "transit" / NAME
    assert not preparation.exists()
    assert int(os.stat(placed / "valhalla_tiles.tar").st_mtime) == int(STATE_AT.timestamp())
    assert fetch_transit_pointer(tmp_path / "routing") is None


def test_a_failed_tool_is_a_named_failure_and_places_nothing(tmp_path, monkeypatch):
    def apply_failed_process(lease, arguments, deadline):
        if arguments[0] == "/bin/sh":
            (tmp_path / "timezones.sqlite").write_bytes(b"invented timezones")
            return
        raise ImportProcessFailedError("Import process failed")

    monkeypatch.setattr("data.transit_build.apply_import_process", apply_failed_process)
    (tmp_path / "routing").mkdir()
    preparation = apply_transit_preparation(tmp_path / "routing")
    with pytest.raises(TransitBuildError, match="tool failed"):
        apply_transit_build(**build_test_arguments(tmp_path, preparation))
    assert not (tmp_path / "routing" / "transit" / NAME).exists()


def test_an_empty_timezone_database_stops_the_build_before_the_ingest(tmp_path, monkeypatch):
    calls: list[list[str]] = []
    (tmp_path / "routing").mkdir()
    preparation = apply_transit_preparation(tmp_path / "routing")
    apply_invented_tools(monkeypatch, calls, tmp_path / "timezones.sqlite", preparation / "valhalla_tiles.tar", timezone_bytes=b"")
    with pytest.raises(TransitBuildError, match="missing or empty"):
        apply_transit_build(**build_test_arguments(tmp_path, preparation))
    assert [arguments[0] for arguments in calls] == ["/bin/sh"]


def test_the_pointer_names_the_data_and_the_copy_it_was_built_from(tmp_path):
    root = tmp_path / "routing"
    root.mkdir()
    apply_transit_preparation(root)
    name = build_transit_name("1790985600", "1791090000")
    apply_transit_pointer(root, name)
    assert fetch_transit_pointer(root) == name == NAME
    assert resolve_transit_copy_name(name) == "1790985600"


def test_a_name_without_both_copies_is_refused(tmp_path):
    with pytest.raises(TransitBuildError):
        build_transit_name("1790985600", "")
    with pytest.raises(RoutingDataError):
        apply_transit_pointer(tmp_path, "1790985600")
