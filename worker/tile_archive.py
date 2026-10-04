"""Start the tile step of the loading program on its own: python -m worker.tile_archive."""

import sys
from pathlib import Path

from common_time import fetch_monotonic_seconds
from config.logging import fetch_logger
from config.settings import ENVIRONMENT_ENTRY_FILES, ConfigurationError
from service.administrative import apply_administrative_run
from service.tile_archive import TILE_ARCHIVE_NAMED_ERRORS, TileArchiveResult, TileArchiveSettings, apply_tile_archive_command

TILE_ARCHIVE_EXIT_CODES = {"loaded": 0, "unchanged": 0, "skipped": 2}


def build_required_paths(paths: dict[str, Path | None]) -> dict[str, Path]:
    """Return the given path entries of the configuration, refusing with one ConfigurationError that names every missing entry and its file."""
    missing = [name for name, value in paths.items() if value is None]
    if missing:
        raise ConfigurationError("Missing or invalid configuration: " + ", ".join(f"{name} ({ENVIRONMENT_ENTRY_FILES[name]})" for name in missing))
    return {name: value for name, value in paths.items() if value is not None}


def build_tile_archive_settings() -> TileArchiveSettings:
    """Collect the source and the served directory of the tile archive, naming every missing entry and its file; the common loading program reuses it."""
    from config.config import TILE_ARCHIVE_DIR, TILE_ARCHIVE_SOURCE

    paths = build_required_paths({"TILE_ARCHIVE_SOURCE": TILE_ARCHIVE_SOURCE, "TILE_ARCHIVE_DIR": TILE_ARCHIVE_DIR})
    return TileArchiveSettings(paths["TILE_ARCHIVE_SOURCE"], paths["TILE_ARCHIVE_DIR"])


def build_tile_archive_workspace_root() -> Path:
    """Collect the import workspace whose exclusion the standalone command takes, naming the entry and its file when it is missing."""
    from config.config import IMPORT_WORKSPACE_ROOT

    return build_required_paths({"IMPORT_WORKSPACE_ROOT": IMPORT_WORKSPACE_ROOT})["IMPORT_WORKSPACE_ROOT"]


def apply_tile_archive_report(result: TileArchiveResult, duration_seconds: float) -> int:
    """Write the one outcome line the operator reads and return the exit code of that outcome."""
    fetch_logger(__name__).info("Tile archive outcome=%s duration_s=%.1f", result.outcome, duration_seconds)
    return TILE_ARCHIVE_EXIT_CODES[result.outcome]


def apply_tile_archive_action() -> int:
    """
    Run the tile step and report it: loaded and unchanged exit 0, skipped exits 2, a failure exits 1.

    A named failure is reported with its constant message, which carries the reason code and no path; any other failure
    is reported by its type and passed on, so the shared wrapper logs its redacted traceback.
    """
    started = fetch_monotonic_seconds()
    settings = build_tile_archive_settings()
    workspace_root = build_tile_archive_workspace_root()
    try:
        result = apply_tile_archive_command(settings, workspace_root)
    except TILE_ARCHIVE_NAMED_ERRORS as failure:
        fetch_logger(__name__).error("Tile archive outcome=failed cause=%s: %s duration_s=%.1f", type(failure).__name__, failure, fetch_monotonic_seconds() - started)
        return 1
    except Exception as failure:
        fetch_logger(__name__).error("Tile archive outcome=failed cause=%s duration_s=%.1f", type(failure).__name__, fetch_monotonic_seconds() - started)
        raise
    return apply_tile_archive_report(result, fetch_monotonic_seconds() - started)


if __name__ == "__main__":
    sys.exit(apply_administrative_run("tile_archive", apply_tile_archive_action))
