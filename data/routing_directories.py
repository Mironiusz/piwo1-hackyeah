"""Keep immutable data directories beside each other: private preparations, placement by a rename and a pointer replaced atomically."""

import os
import re
import tempfile
from pathlib import Path

from data.routing_data import RoutingDataError

PREPARATION_PREFIX = ".prepare-"
POINTER_NAME = "current"


def fetch_preparation_directories(parent: Path) -> tuple[Path, ...]:
    """List the preparation directories an interrupted run left under a parent; no preparation is ever pointed to."""
    try:
        return tuple(sorted(entry for entry in parent.iterdir() if entry.name.startswith(PREPARATION_PREFIX))) if parent.exists() else ()
    except OSError as error:
        raise RoutingDataError("Cannot list preparation directories") from error


def apply_preparation_directory(parent: Path) -> Path:
    """Create a new private preparation directory under a parent, creating the parent when it is missing."""
    try:
        parent.mkdir(exist_ok=True)
        return Path(tempfile.mkdtemp(prefix=PREPARATION_PREFIX, dir=parent))
    except OSError as error:
        raise RoutingDataError("Cannot create preparation directory") from error


def apply_directory_placement(preparation: Path, target: Path) -> Path:
    """Move a complete preparation to its final name by a rename, never replacing an existing directory."""
    if target.exists() or target.is_symlink():
        raise RoutingDataError("Data directory already exists")
    try:
        os.rename(preparation, target)
    except OSError as error:
        raise RoutingDataError("Cannot place data directory") from error
    return target


def fetch_directory_pointer(parent: Path, pattern: re.Pattern[str]) -> str | None:
    """Read the directory name the pointer of a parent selects, or None while no pointer has been written."""
    path = parent / POINTER_NAME
    if path.is_symlink():
        raise RoutingDataError("Invalid data pointer")
    try:
        content = path.read_text(encoding="ascii")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        raise RoutingDataError("Cannot read data pointer") from error
    name = content.removesuffix("\n")
    if not pattern.fullmatch(name):
        raise RoutingDataError("Invalid data pointer")
    return name


def apply_directory_pointer(parent: Path, name: str, pattern: re.Pattern[str]) -> None:
    """Point a parent at one of its directories by replacing the pointer through a synced temporary file and a rename."""
    if not pattern.fullmatch(name):
        raise RoutingDataError("Invalid data directory name")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="ascii", dir=parent, prefix=".current-", delete=False) as stream:
            temporary_path = Path(stream.name)
            stream.write(name + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, parent / POINTER_NAME)
        temporary_path = None
    except OSError as error:
        raise RoutingDataError("Cannot publish data pointer") from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
