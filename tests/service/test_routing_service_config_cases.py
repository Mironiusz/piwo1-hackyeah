"""Check the start script of the routing service, loaded by its path because it runs in the routing image outside the layers of the repository."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "valhalla" / "start_routing_service.py"
INVENTED_DEFAULTS = {
    "mjolnir": {"tile_dir": "/data/valhalla", "tile_extract": "/data/valhalla/tiles.tar", "include_platforms": False, "keep_osm_node_ids": False},
    "service_limits": {"max_exclude_locations": 50, "pedestrian": {"max_distance": 250000}},
    "httpd": {"service": {"listen": "tcp://*:8002"}},
}


class ServiceReplacedError(Exception):
    """Stands for the replacement of the process by valhalla_service, with the command it would run."""

    def __init__(self, command: list[str]) -> None:
        """Keep the command."""
        super().__init__("valhalla_service started")
        self.command = command


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> ModuleType:
    """Load the start script by its path, with its configuration file in a temporary directory and the image tools replaced."""
    specification = importlib.util.spec_from_file_location("start_routing_service", SCRIPT_PATH)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    monkeypatch.setattr(module, "CONFIG_PATH", tmp_path / "valhalla_service.json")
    monkeypatch.setattr(module, "fetch_default_config", lambda: INVENTED_DEFAULTS)

    def apply_invented_exec(_file: str, command: list[str]) -> None:
        """Stop where the real process would be replaced."""
        raise ServiceReplacedError(command)

    monkeypatch.setattr(module.os, "execvp", apply_invented_exec)
    return module


def build_routing_data(root: Path, pointer: str | None, with_archive: bool) -> Path:
    """Lay out an invented routing data directory with one copy and an optional pointer."""
    copy = root / "copies" / "1790972494"
    copy.mkdir(parents=True)
    if with_archive:
        (copy / "valhalla_tiles.tar").write_bytes(b"invented tile archive")
    if pointer is not None:
        (root / "current").write_text(pointer, encoding="utf-8")
    return root


def test_overrides_merge_into_defaults_and_the_tile_archive_is_set(script) -> None:
    """Keep every default the overrides do not name, replace the ones they name and set the tile archive of the copy."""
    tile_extract = Path(__file__).resolve().parent / "copies" / "1790972494" / "valhalla_tiles.tar"
    overrides = {"mjolnir": {"include_platforms": True, "keep_osm_node_ids": True}, "service_limits": {"max_exclude_locations": 5000}}
    config = script.build_routing_service_config(INVENTED_DEFAULTS, overrides, tile_extract)
    assert config["mjolnir"] == {"tile_dir": "/data/valhalla", "tile_extract": str(tile_extract), "include_platforms": True, "keep_osm_node_ids": True}
    assert config["service_limits"] == {"max_exclude_locations": 5000, "pedestrian": {"max_distance": 250000}}
    assert config["httpd"] == INVENTED_DEFAULTS["httpd"]
    assert INVENTED_DEFAULTS["mjolnir"]["tile_extract"] == "/data/valhalla/tiles.tar"


def test_a_relative_tile_archive_is_refused(script) -> None:
    """Refuse a tile archive that is not given by an absolute path."""
    with pytest.raises(ValueError, match="absolute"):
        script.build_routing_service_config(INVENTED_DEFAULTS, {}, Path("copies") / "1790972494" / "valhalla_tiles.tar")


def test_the_overrides_of_the_project_hold_the_limits_and_the_node_identities(script) -> None:
    """Hold the limits of D-5 of the Valhalla plan and keep the platforms and every OpenStreetMap node identity."""
    overrides = json.loads(script.OVERRIDES_PATH.read_text(encoding="utf-8"))
    assert overrides == {
        "mjolnir": {"include_platforms": True, "keep_osm_node_ids": True, "keep_all_osm_node_ids": True},
        "service_limits": {"max_exclude_locations": 5000, "max_exclude_polygons_length": 1000000, "max_exclude_polygons_vertices": 50000},
    }


@pytest.mark.parametrize("arguments", [[], ["first", "second"]])
def test_a_missing_or_extra_argument_is_refused(script, monkeypatch, capsys, arguments: list[str]) -> None:
    """Stop with the code 2 and the usage when the directory of the routing data is not the one argument."""
    monkeypatch.setattr(script.sys, "argv", ["start_routing_service.py", *arguments])
    assert script.main() == 2
    assert "Usage" in capsys.readouterr().err


def test_the_service_starts_on_the_absolute_tile_archive_of_the_current_copy(script, monkeypatch, tmp_path) -> None:
    """Write the merged configuration with the absolute tile archive of the copy current names and start valhalla_service with one thread."""
    root = build_routing_data(tmp_path / "routing", "1790972494\n", True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(script.sys, "argv", ["start_routing_service.py", "routing"])
    with pytest.raises(ServiceReplacedError) as started:
        script.main()
    assert started.value.command == ["valhalla_service", str(script.CONFIG_PATH), "1"]
    written = json.loads(script.CONFIG_PATH.read_text(encoding="utf-8"))
    tile_extract = Path(written["mjolnir"]["tile_extract"])
    assert tile_extract.is_absolute()
    assert tile_extract == root.absolute() / "copies" / "1790972494" / "valhalla_tiles.tar"
    assert written["service_limits"]["max_exclude_locations"] == 5000
    assert written["mjolnir"]["keep_all_osm_node_ids"] is True


@pytest.mark.parametrize(("pointer", "with_archive"), [("../elsewhere\n", True), ("1790972494\n", False)])
def test_a_pointer_without_a_complete_copy_starts_nothing(script, monkeypatch, tmp_path, pointer: str, with_archive: bool) -> None:
    """Stop with the code 1 when current names no copy or a copy without its tile archive."""
    root = build_routing_data(tmp_path / "routing", pointer, with_archive)
    monkeypatch.setattr(script.sys, "argv", ["start_routing_service.py", str(root)])
    assert script.main() == 1
    assert not script.CONFIG_PATH.exists()


def test_the_script_waits_for_the_pointer(script, monkeypatch, tmp_path) -> None:
    """Read the pointer again every 5 seconds while it does not exist, and start nothing meanwhile."""
    root = build_routing_data(tmp_path / "routing", None, True)
    waits: list[float] = []

    def apply_invented_sleep(seconds: float) -> None:
        """Publish the pointer after the second wait."""
        waits.append(seconds)
        if len(waits) == 2:
            (root / "current").write_text("1790972494\n", encoding="utf-8")

    monkeypatch.setattr(script.time, "sleep", apply_invented_sleep)
    monkeypatch.setattr(script.sys, "argv", ["start_routing_service.py", str(root)])
    with pytest.raises(ServiceReplacedError):
        script.main()
    assert waits == [5, 5]
