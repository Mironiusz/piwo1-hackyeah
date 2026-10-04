"""Check the directory of a copy and the reading of its boundary of Kraków against its manifest, in a temporary directory."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from data import routing_data
from data.routing_data import ROUTING_BOUNDARY_NAME, RoutingDataError, apply_osm_boundary_file, apply_osm_routing_manifest, build_routing_copy_directory, fetch_osm_boundary

pytestmark = pytest.mark.integration

STATE_AT = datetime(2026, 10, 2, 20, 21, 34, tzinfo=UTC)


def apply_invented_copy(directory: Path, monkeypatch: pytest.MonkeyPatch, with_boundary: bool) -> None:
    """Write invented routing files and their manifest; without the boundary the manifest is the one of a copy prepared before the boundary was kept."""
    directory.mkdir(parents=True)
    names = routing_data.ROUTING_FILE_NAMES if with_boundary else tuple(name for name in routing_data.ROUTING_FILE_NAMES if name != ROUTING_BOUNDARY_NAME)
    for name in names:
        (directory / name).write_bytes(b"invented " + name.encode())
    with monkeypatch.context() as earlier:
        earlier.setattr(routing_data, "ROUTING_FILE_NAMES", names)
        apply_osm_routing_manifest(directory, STATE_AT)


def test_directory_of_a_copy_is_named_by_its_instant(tmp_path: Path) -> None:
    """Name the directory of 2026-10-02T20:21:34Z after 1790972494 under copies."""
    assert build_routing_copy_directory(tmp_path, STATE_AT) == tmp_path / "copies" / "1790972494"


def test_boundary_listed_by_the_manifest_is_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the bytes of a boundary the manifest of the same copy lists."""
    directory = tmp_path / "copy"
    apply_invented_copy(directory, monkeypatch, True)
    assert fetch_osm_boundary(directory, STATE_AT) == b"invented " + ROUTING_BOUNDARY_NAME.encode()


def test_manifest_without_the_boundary_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse a copy whose manifest does not list the boundary."""
    directory = tmp_path / "copy"
    apply_invented_copy(directory, monkeypatch, False)
    (directory / ROUTING_BOUNDARY_NAME).write_bytes(b"unguarded")
    with pytest.raises(RoutingDataError):
        fetch_osm_boundary(directory, STATE_AT)


def test_manifest_of_another_instant_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse a boundary whose manifest belongs to another copy."""
    directory = tmp_path / "copy"
    apply_invented_copy(directory, monkeypatch, True)
    assert json.loads((directory / "manifest.json").read_text(encoding="utf-8"))["state_at"] == STATE_AT.isoformat()
    with pytest.raises(RoutingDataError):
        fetch_osm_boundary(directory, datetime(2026, 10, 3, tzinfo=UTC))


def test_boundary_file_is_written_once(tmp_path: Path) -> None:
    """Write the boundary into a preparation directory and refuse to write over it."""
    apply_osm_boundary_file(tmp_path, b"invented boundary")
    assert (tmp_path / ROUTING_BOUNDARY_NAME).read_bytes() == b"invented boundary"
    with pytest.raises(RoutingDataError):
        apply_osm_boundary_file(tmp_path, b"another boundary")
    assert (tmp_path / ROUTING_BOUNDARY_NAME).read_bytes() == b"invented boundary"
