"""Build Valhalla routing data with public transport from one OpenStreetMap copy and one GTFS copy, and keep the pointer to the data in use."""

import re
import shlex
from datetime import datetime
from pathlib import Path

from common_time import Deadline
from data.import_process import ImportProcessFailedError, apply_import_process
from data.import_workspace import WorkspaceLease
from data.osm_valhalla import apply_osm_valhalla_tiles
from data.routing_directories import apply_directory_placement, apply_directory_pointer, apply_preparation_directory, fetch_directory_pointer, fetch_preparation_directories

TRANSIT_DIRECTORY_NAME = "transit"
TRANSIT_ARCHIVE_NAME = "valhalla_tiles.tar"
TRANSIT_NAME_PATTERN = re.compile(r"([0-9]+)-([0-9]+)")
TRANSIT_SHELL = "/bin/sh"


class TransitBuildError(ValueError):
    """Describe tools that failed to prepare complete routing data with public transport."""


def build_transit_name(copy_name: str, gtfs_name: str) -> str:
    """Name the routing data with public transport by the OpenStreetMap copy and the GTFS copy it was built from."""
    name = f"{copy_name}-{gtfs_name}"
    if not TRANSIT_NAME_PATTERN.fullmatch(name):
        raise TransitBuildError("Invalid public transport data name")
    return name


def resolve_transit_copy_name(name: str) -> str:
    """Give the name of the OpenStreetMap copy a directory of routing data with public transport was built from."""
    match = TRANSIT_NAME_PATTERN.fullmatch(name)
    if match is None:
        raise TransitBuildError("Invalid public transport data name")
    return match.group(1)


def build_transit_directory(root: Path, name: str) -> Path:
    """Give the directory of one set of routing data with public transport under ROUTING_DATA_DIR."""
    return root / TRANSIT_DIRECTORY_NAME / name


def fetch_transit_preparations(root: Path) -> tuple[Path, ...]:
    """List the preparations of routing data with public transport an interrupted run left behind."""
    return fetch_preparation_directories(root / TRANSIT_DIRECTORY_NAME)


def apply_transit_preparation(root: Path) -> Path:
    """Create a new private directory the archive of one build is written into."""
    return apply_preparation_directory(root / TRANSIT_DIRECTORY_NAME)


def apply_timezone_validation(path: Path) -> None:
    """Refuse a timezone database the tool left missing or empty, since a shell redirection creates the file even when the tool writes nothing."""
    try:
        if path.is_symlink() or not path.is_file() or not path.stat().st_size:
            raise TransitBuildError("Timezone database is missing or empty")
    except OSError as error:
        raise TransitBuildError("Cannot read timezone database") from error


def apply_transit_build(
    lease: WorkspaceLease,
    config_path: Path,
    tool_directory: Path,
    network_path: Path,
    timezone_path: Path,
    preparation: Path,
    root: Path,
    name: str,
    state_at: datetime,
    deadline: Deadline,
) -> Path:
    """
    Run the public transport tools and the tile tools, then place the preparation as the directory of this name.

    The timezone database is written by valhalla_build_timezones to its standard output, so only that tool runs through
    /bin/sh, which carries the redirection the supervisor cannot. valhalla_ingest_transit and valhalla_convert_transit
    follow, and the walking tile build of the importer then builds the tiles with public transport and the archive,
    stamped with the instant of the OpenStreetMap copy. Every tool runs under the shared supervisor and the run deadline.
    """
    if not TRANSIT_NAME_PATTERN.fullmatch(name):
        raise TransitBuildError("Invalid public transport data name")
    timezone_command = f"{shlex.quote(str(tool_directory / 'valhalla_build_timezones'))} > {shlex.quote(str(timezone_path))}"
    try:
        apply_import_process(lease, [TRANSIT_SHELL, "-c", timezone_command], deadline)
        apply_timezone_validation(timezone_path)
        apply_import_process(lease, [str(tool_directory / "valhalla_ingest_transit"), "-c", str(config_path)], deadline)
        apply_import_process(lease, [str(tool_directory / "valhalla_convert_transit"), "-c", str(config_path)], deadline)
    except ImportProcessFailedError as error:
        raise TransitBuildError("Public transport construction tool failed") from error
    apply_osm_valhalla_tiles(lease, config_path, tool_directory, network_path, preparation / TRANSIT_ARCHIVE_NAME, state_at, deadline)
    return apply_directory_placement(preparation, build_transit_directory(root, name))


def fetch_transit_pointer(root: Path) -> str | None:
    """Read the name of the routing data with public transport in use, or None while none was ever built."""
    return fetch_directory_pointer(root / TRANSIT_DIRECTORY_NAME, TRANSIT_NAME_PATTERN)


def apply_transit_pointer(root: Path, name: str) -> None:
    """Point at the routing data with public transport of this name, through a synced temporary file and a rename."""
    apply_directory_pointer(root / TRANSIT_DIRECTORY_NAME, name, TRANSIT_NAME_PATTERN)
