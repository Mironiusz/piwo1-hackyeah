"""
Start the routing service of the project on the copy the pointer current names, as D-6 of the backend architecture decides.

The script is run by python3 of the routing image, Python 3.12, with the directory of the routing data inside the
container as its one argument, so it reads no environment entry next to the facade of config/config.py. It waits until
current exists, reading it again every 5 seconds, takes the defaults of valhalla_build_config, merges
valhalla_overrides.json, sets mjolnir.tile_extract to the absolute path of the tile archive of the named copy, writes the
result next to itself and replaces itself with valhalla_service with one thread. The image holds none of the code of the
repository, so the names of the pointer, the copies directory and the tile archive repeat those of data/routing_data.py.
Its own lines name the directory and never a request; the output of valhalla_service is left as it is.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

POINTER_NAME = "current"
COPIES_NAME = "copies"
TILE_ARCHIVE_NAME = "valhalla_tiles.tar"
POINTER_POLL_SECONDS = 5
BUILD_CONFIG_TOOL = "valhalla_build_config"
SERVICE_TOOL = "valhalla_service"
SERVICE_THREAD_COUNT = "1"
OVERRIDES_PATH = Path(__file__).with_name("valhalla_overrides.json")
CONFIG_PATH = Path(__file__).with_name("valhalla_service.json")


def build_merged_config(defaults: dict[str, object], overrides: dict[str, object]) -> dict[str, object]:
    """Merge the overrides into the defaults key by key: a mapping merges into a mapping, any other value replaces the default."""
    merged = dict(defaults)
    for key, value in overrides.items():
        current = merged.get(key)
        if isinstance(value, dict) and isinstance(current, dict):
            merged[key] = build_merged_config(current, value)
        else:
            merged[key] = value
    return merged


def build_routing_service_config(defaults: dict[str, object], overrides: dict[str, object], tile_extract: Path) -> dict[str, object]:
    """Build the configuration of the service: the defaults with the overrides of the project and the tile archive of one copy, given by its absolute path."""
    if not tile_extract.is_absolute():
        raise ValueError("The tile archive must be given by an absolute path")
    merged = build_merged_config(defaults, overrides)
    mjolnir = merged.get("mjolnir")
    if not isinstance(mjolnir, dict):
        raise ValueError("The configuration of the routing service has no mjolnir mapping")
    merged["mjolnir"] = {**mjolnir, "tile_extract": str(tile_extract)}
    return merged


def fetch_default_config() -> dict[str, object]:
    """Read the default configuration valhalla_build_config of the image prints."""
    printed = subprocess.run([BUILD_CONFIG_TOOL], check=True, capture_output=True, text=True).stdout
    defaults = json.loads(printed)
    if not isinstance(defaults, dict):
        raise ValueError("valhalla_build_config printed no configuration mapping")
    return defaults


def fetch_overrides() -> dict[str, object]:
    """Read the settings of the project from valhalla_overrides.json next to this script."""
    overrides = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    if not isinstance(overrides, dict):
        raise ValueError("valhalla_overrides.json holds no mapping")
    return overrides


def fetch_current_copy_name(directory: Path) -> str:
    """Wait until the pointer current exists in the directory, reading it every 5 seconds, and give the name of the copy it holds."""
    pointer = directory / POINTER_NAME
    if not pointer.exists():
        print(f"Waiting for {pointer}", flush=True)
    while not pointer.exists():
        time.sleep(POINTER_POLL_SECONDS)
    return pointer.read_text(encoding="utf-8").removesuffix("\n")


def main() -> int:
    """Start valhalla_service on the copy current names, or stop with a non-zero code naming what is wrong."""
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Usage: start_routing_service.py <directory of the routing data>", file=sys.stderr)
        return 2
    directory = Path(arguments[0]).absolute()
    name = fetch_current_copy_name(directory)
    if not name.isascii() or not name.isdigit():
        print(f"The pointer {directory / POINTER_NAME} does not name a copy", file=sys.stderr)
        return 1
    tile_extract = directory / COPIES_NAME / name / TILE_ARCHIVE_NAME
    if not tile_extract.is_file():
        print(f"The copy named by {directory / POINTER_NAME} has no tile archive {tile_extract}", file=sys.stderr)
        return 1
    config = build_routing_service_config(fetch_default_config(), fetch_overrides(), tile_extract)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Starting the routing service on {tile_extract}", flush=True)
    os.execvp(SERVICE_TOOL, [SERVICE_TOOL, str(CONFIG_PATH), SERVICE_THREAD_COUNT])


if __name__ == "__main__":
    sys.exit(main())
