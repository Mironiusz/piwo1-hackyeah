"""Build Valhalla walking tiles with the supplied tools under the shared import process supervisor."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from common_time import Deadline
from data.import_process import ImportProcessFailedError, apply_import_process
from data.import_workspace import WorkspaceLease


class OsmTileBuildError(ValueError):
    """Describe routing tools that failed to prepare a complete walking archive."""


def fetch_osm_valhalla_template(path: Path) -> dict[str, Any]:
    """Read the supplied Valhalla JSON configuration that each build specializes."""
    try:
        with path.open(encoding="utf-8") as stream:
            template = json.load(stream)
    except (OSError, ValueError) as error:
        raise OsmTileBuildError("Cannot read Valhalla configuration template") from error
    if not isinstance(template, dict):
        raise OsmTileBuildError("Valhalla configuration template must be an object")
    return template


def apply_osm_valhalla_config(path: Path, config: dict[str, Any]) -> None:
    """Write one build's configuration without replacing an existing file."""
    try:
        with path.open("x", encoding="utf-8") as output:
            json.dump(config, output)
    except (OSError, TypeError, ValueError) as error:
        raise OsmTileBuildError("Cannot write Valhalla build configuration") from error


def apply_osm_valhalla_tiles(lease: WorkspaceLease, config_path: Path, tool_directory: Path, network_path: Path, archive_path: Path, state_at: datetime, deadline: Deadline) -> None:
    """Build the walking tiles and their archive with the supplied tools and stamp the archive with the source instant."""
    if state_at.utcoffset() is None:
        raise OsmTileBuildError("Routing source instant must be aware")
    if archive_path.exists() or archive_path.is_symlink():
        raise OsmTileBuildError("Routing archive already exists")
    try:
        apply_import_process(lease, [str(tool_directory / "valhalla_build_tiles"), "-c", str(config_path), str(network_path)], deadline)
        apply_import_process(lease, [str(tool_directory / "valhalla_build_extract"), "-c", str(config_path)], deadline)
    except ImportProcessFailedError as error:
        raise OsmTileBuildError("Routing construction tool failed") from error
    try:
        if archive_path.is_symlink() or not archive_path.is_file() or not archive_path.stat().st_size:
            raise OsmTileBuildError("Routing archive is missing or empty")
        os.utime(archive_path, (state_at.timestamp(), state_at.timestamp()))
    except OSError as error:
        raise OsmTileBuildError("Cannot finalize routing archive") from error
