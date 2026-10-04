"""Run the tile step of the loading program: put the recorded map tile archive into the directory the proxy serves."""

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_monotonic_seconds, resolve_remaining_milliseconds
from config.logging import fetch_logger
from data.engine import build_import_engine
from data.import_workspace import ImportWorkspaceUnconfirmed
from data.local_lock import ImportAlreadyRunning
from data.locks import apply_import_exclusion
from data.tile_archive import (
    TileFileError,
    apply_tile_file_copy,
    apply_tile_file_placement,
    apply_tile_leftover_removal,
    apply_tile_temporary_cleanup,
    fetch_tile_directory_presence,
    fetch_tile_file_digest,
)

TILE_ARCHIVE_NAME = "krakow.pmtiles"
TILE_ARCHIVE_SHA256 = "21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1"
TILE_ARCHIVE_RUN_SECONDS = 120
TILE_ARCHIVE_GUARD_STATEMENT_TIMEOUT_MS = 5000

type TileArchiveOutcome = Literal["loaded", "unchanged", "skipped"]
type TileArchiveFailureReason = Literal[
    "places_overlap",
    "served_directory_missing",
    "served_unreadable",
    "source_missing",
    "source_unreadable",
    "source_mismatch",
    "copy_failed",
    "copy_mismatch",
    "deadline_expired",
]


@dataclass(frozen=True)
class TileArchiveSettings:
    """Hold the two places of the step, already validated as absolute paths by the configuration: the file a person put on the machine and the directory the proxy serves."""

    source_path: Path
    served_directory: Path


@dataclass(frozen=True)
class TileArchiveResult:
    """Report what one run achieved: loaded and unchanged both leave the recorded archive under the served name, skipped means another run held the exclusion."""

    outcome: TileArchiveOutcome


class TileArchiveError(RuntimeError):
    """End the tile step as failed with a fixed reason code and a constant message that names no path."""

    def __init__(self, reason: TileArchiveFailureReason) -> None:
        """Keep the reason code for the loading program and put it into the constant message the operator reads."""
        super().__init__(f"Tile archive step failed: {reason}")
        self.reason = reason


TILE_ARCHIVE_NAMED_ERRORS: tuple[type[Exception], ...] = (TileArchiveError, ImportWorkspaceUnconfirmed)
"""Failures of the tile step whose messages are constant texts without data, so the operator report may show them."""


def resolve_tile_places_overlap(settings: TileArchiveSettings) -> bool:
    """Say whether the source lies inside the served directory, comparing the two paths as written, without reading the file system."""
    return settings.source_path.is_relative_to(settings.served_directory)


def apply_tile_archive_command(settings: TileArchiveSettings, workspace_root: Path) -> TileArchiveResult:
    """Run one tile step with its own 120-second run deadline, for the administrative entry point."""
    return apply_tile_archive(settings, workspace_root, build_deadline(TILE_ARCHIVE_RUN_SECONDS, fetch_monotonic_seconds()))


def apply_tile_archive(settings: TileArchiveSettings, workspace_root: Path, deadline: Deadline) -> TileArchiveResult:
    """
    Run one tile step under the exclusion of the importer.

    The step takes the same exclusion as python -m worker.osm_import and the common loading program, so a standalone run
    and the program refuse each other at once. Another run holding it gives skipped and nothing is written.
    """
    engine = build_import_engine(TILE_ARCHIVE_GUARD_STATEMENT_TIMEOUT_MS)
    try:
        with ExitStack() as stack:
            try:
                stack.enter_context(apply_import_exclusion(engine, workspace_root))
            except ImportAlreadyRunning:
                return TileArchiveResult("skipped")
            return apply_tile_archive_run(settings, deadline)
    finally:
        engine.dispose()


def apply_tile_archive_run(settings: TileArchiveSettings, deadline: Deadline) -> TileArchiveResult:
    """
    Carry out an admitted run: keep a recorded archive already served, or check the source, copy it beside the served name, check the copy and only then put it under the served name.

    The step the common loading program composes, called while the program holds the exclusion. A served file of the
    recorded value gives unchanged without reading the source. Any other file under the served name, a link included,
    is replaced by the archive. A failure of the step raises TileArchiveError with its reason and leaves the served
    name as it was, with one exception: copy_failed from a directory that cannot be synced after the replacement
    leaves the complete checked archive there. An unexpected exception passes on unchanged. The temporary copy is
    removed on every path that does not end with its placement.
    """
    if resolve_tile_places_overlap(settings):
        raise TileArchiveError("places_overlap")
    directory = settings.served_directory
    if not fetch_tile_directory_presence(directory):
        raise TileArchiveError("served_directory_missing")
    target = directory / TILE_ARCHIVE_NAME
    with apply_tile_failure_reason("copy_failed"):
        apply_tile_leftover_removal(directory)
    with apply_tile_failure_reason("served_unreadable"):
        served_digest = fetch_tile_file_digest(target, deadline)
    if served_digest == TILE_ARCHIVE_SHA256:
        return TileArchiveResult("unchanged")
    with apply_tile_failure_reason("source_unreadable"):
        source_digest = fetch_tile_file_digest(settings.source_path, deadline)
    if source_digest is None:
        raise TileArchiveError("source_missing")
    if source_digest != TILE_ARCHIVE_SHA256:
        raise TileArchiveError("source_mismatch")
    with apply_tile_failure_reason("copy_failed"):
        temporary = apply_tile_file_copy(settings.source_path, directory, deadline)
    try:
        with apply_tile_failure_reason("copy_failed"):
            copy_digest = fetch_tile_file_digest(temporary, deadline)
        if copy_digest != TILE_ARCHIVE_SHA256:
            raise TileArchiveError("copy_mismatch")
        with apply_tile_failure_reason("copy_failed"):
            resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
            apply_tile_file_placement(temporary, target)
    except BaseException:
        apply_tile_temporary_cleanup(temporary)
        raise
    if served_digest is not None:
        fetch_logger(__name__).info("Tile archive replaces a served file of another value")
    return TileArchiveResult("loaded")


@contextmanager
def apply_tile_failure_reason(reason: TileArchiveFailureReason) -> Iterator[None]:
    """Turn a failed file operation inside the block into the given reason of the step and an exhausted deadline into deadline_expired, keeping the original as the cause."""
    try:
        yield
    except DeadlineExpiredError as error:
        raise TileArchiveError("deadline_expired") from error
    except TileFileError as error:
        raise TileArchiveError(reason) from error
