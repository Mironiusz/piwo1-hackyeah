"""Read, copy and place the map tile archive in the directory the proxy serves, in chunks bounded by a run deadline."""

import hashlib
import os
import sys
import tempfile
from pathlib import Path

from common_time import Deadline, DeadlineExpiredError, fetch_monotonic_seconds, resolve_remaining_milliseconds

TILE_FILE_CHUNK_BYTES = 1048576
TILE_TEMPORARY_PREFIX = ".tile-archive-"


class TileFileError(RuntimeError):
    """Report a failed read or write of a tile archive file with a constant message that names no path."""


def fetch_tile_directory_presence(directory: Path) -> bool:
    """Say whether the path is a real directory, not a link to one."""
    return not directory.is_symlink() and directory.is_dir()


def fetch_tile_file_digest(path: Path, deadline: Deadline) -> str | None:
    """
    Read the SHA-256 hex digest of a regular file chunk by chunk, checking the run deadline before each chunk.

    A missing path, a directory and a link all give None, because the step treats them as no file. A failed read raises
    TileFileError and an exhausted deadline raises DeadlineExpiredError.
    """
    try:
        if path.is_symlink() or not path.is_file():
            return None
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while True:
                resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
                chunk = stream.read(TILE_FILE_CHUNK_BYTES)
                if not chunk:
                    return digest.hexdigest()
                digest.update(chunk)
    except DeadlineExpiredError:
        raise
    except OSError as error:
        raise TileFileError("Cannot read tile archive file") from error


def apply_tile_file_copy(source: Path, directory: Path, deadline: Deadline) -> Path:
    """
    Copy the source into a new temporary file of the directory chunk by chunk, sync it to disk and return its path.

    The run deadline is checked before each chunk. When the copy fails or the deadline runs out, the partial file is
    removed first; a failed copy then raises TileFileError and an exhausted deadline passes on as DeadlineExpiredError.
    DeadlineExpiredError is a TimeoutError and so an OSError, which is why it is handled before the OSError of a failed
    copy.
    """
    try:
        writer = tempfile.NamedTemporaryFile(mode="wb", dir=directory, prefix=TILE_TEMPORARY_PREFIX, delete=False)
    except OSError as error:
        raise TileFileError("Cannot copy tile archive file") from error
    temporary = Path(writer.name)
    try:
        with writer, source.open("rb") as reader:
            while True:
                resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
                chunk = reader.read(TILE_FILE_CHUNK_BYTES)
                if not chunk:
                    break
                writer.write(chunk)
            writer.flush()
            os.fsync(writer.fileno())
    except DeadlineExpiredError:
        apply_tile_file_removal(temporary)
        raise
    except OSError as error:
        apply_tile_file_removal(temporary)
        raise TileFileError("Cannot copy tile archive file") from error
    return temporary


def apply_tile_file_placement(temporary: Path, target: Path) -> None:
    """Put the temporary file under the target name in one atomic replacement and, on Linux, sync the directory so the new name survives a crash."""
    try:
        os.replace(temporary, target)
        if sys.platform == "linux":
            descriptor = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    except OSError as error:
        raise TileFileError("Cannot place tile archive file") from error


def apply_tile_file_removal(path: Path) -> None:
    """Remove one file if it is still there."""
    try:
        path.unlink(missing_ok=True)
    except OSError as error:
        raise TileFileError("Cannot remove tile archive file") from error


def apply_tile_leftover_removal(directory: Path) -> int:
    """Remove the temporary files an interrupted run left in the directory and return how many were removed; no other file is touched."""
    try:
        leftovers = [entry for entry in directory.iterdir() if entry.name.startswith(TILE_TEMPORARY_PREFIX) and not entry.is_symlink() and entry.is_file()]
    except OSError as error:
        raise TileFileError("Cannot remove tile archive file") from error
    for leftover in leftovers:
        apply_tile_file_removal(leftover)
    return len(leftovers)
