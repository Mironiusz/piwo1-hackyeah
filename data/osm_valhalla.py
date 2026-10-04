"""Run the delivered Valhalla tools with bounded child-process lifetime."""

import asyncio
import json
import os
import signal
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any


class OsmTileBuildError(ValueError):
    """Describe routing tools that failed to prepare a complete walking archive."""


def apply_osm_valhalla_config(directory: Path, config: dict[str, Any]) -> Path:
    """Create a new build directory and write its supplied configuration without overwrite."""
    try:
        directory.mkdir(exist_ok=False)
        config_path = directory / "build.json"
        with config_path.open("x", encoding="utf-8") as output:
            json.dump(config, output)
        return config_path
    except (OSError, TypeError, ValueError) as error:
        raise OsmTileBuildError("Cannot prepare routing build directory") from error


async def apply_osm_valhalla_command(arguments: tuple[str, ...], deadline: float) -> None:
    """Run one tool without a shell and stop its process group before propagating cancellation."""
    if asyncio.get_running_loop().time() >= deadline:
        raise OsmTileBuildError("Routing construction deadline expired")
    try:
        process = await asyncio.create_subprocess_exec(*arguments, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL, start_new_session=True)
    except OSError as error:
        raise OsmTileBuildError("Cannot start routing construction tool") from error
    try:
        async with asyncio.timeout_at(deadline):
            status = await process.wait()
    except (TimeoutError, asyncio.CancelledError) as error:
        with suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        await process.wait()
        if isinstance(error, asyncio.CancelledError):
            raise
        raise OsmTileBuildError("Routing construction deadline expired") from error
    if status:
        raise OsmTileBuildError("Routing construction tool failed")


async def apply_osm_valhalla_tiles(directory: Path, config_path: Path, tool_directory: Path, state_at: datetime, deadline: float) -> None:
    """Build walking tiles and their archive using the supplied image's tools."""
    if state_at.utcoffset() is None:
        raise OsmTileBuildError("Routing source instant must be aware")
    archive = directory / "valhalla_tiles.tar"
    if archive.exists() or archive.is_symlink():
        raise OsmTileBuildError("Routing archive already exists")
    await apply_osm_valhalla_command((str(tool_directory / "valhalla_build_tiles"), "-c", str(config_path), str(directory / "network.osm.pbf")), deadline)
    await apply_osm_valhalla_command((str(tool_directory / "valhalla_build_extract"), "-c", str(config_path)), deadline)
    try:
        if archive.is_symlink() or not archive.is_file() or not archive.stat().st_size:
            raise OsmTileBuildError("Routing archive is missing or empty")
        os.utime(archive, (state_at.timestamp(), state_at.timestamp()))
    except OSError as error:
        raise OsmTileBuildError("Cannot finalize routing archive") from error
