"""Start one manual OpenStreetMap import: python -m worker.osm_import, for the first import and every refresh."""

import logging
import sys
from zoneinfo import ZoneInfo

from common_time import fetch_monotonic_seconds
from config.logging import fetch_logger
from config.settings import ENVIRONMENT_ENTRY_FILES, ConfigurationError
from service.administrative import apply_administrative_run
from service.osm_import import OSM_IMPORT_NAMED_ERRORS, OsmImportResult, OsmImportSettings, apply_osm_import_command

OSM_IMPORT_EXIT_CODES = {"updated": 0, "unchanged": 0, "skipped": 2, "routing_incomplete": 1, "commit_unknown": 1}


def build_osm_import_settings() -> OsmImportSettings:
    """Collect the import paths and the business zone, naming every missing optional path entry and its file."""
    from config.config import BUSINESS_TIMEZONE, IMPORT_WORKSPACE_ROOT, ROUTING_DATA_DIR, VALHALLA_CONFIG_TEMPLATE, VALHALLA_TOOL_DIR

    paths = {"IMPORT_WORKSPACE_ROOT": IMPORT_WORKSPACE_ROOT, "VALHALLA_TOOL_DIR": VALHALLA_TOOL_DIR, "VALHALLA_CONFIG_TEMPLATE": VALHALLA_CONFIG_TEMPLATE}
    present = {name: value for name, value in paths.items() if value is not None}
    missing = [name for name in paths if name not in present]
    if missing:
        raise ConfigurationError("Missing or invalid configuration: " + ", ".join(f"{name} ({ENVIRONMENT_ENTRY_FILES[name]})" for name in missing))
    return OsmImportSettings(present["IMPORT_WORKSPACE_ROOT"], ROUTING_DATA_DIR, present["VALHALLA_TOOL_DIR"], present["VALHALLA_CONFIG_TEMPLATE"], ZoneInfo(BUSINESS_TIMEZONE))


def apply_osm_import_report(result: OsmImportResult, duration_seconds: float) -> int:
    """Write the one outcome line the operator reads and return the exit code of that outcome."""
    counts = result.counts
    level = logging.ERROR if OSM_IMPORT_EXIT_CODES[result.outcome] == 1 else logging.INFO
    fetch_logger(__name__).log(
        level,
        "OSM import outcome=%s state_at=%s duration_s=%.1f nodes=%s ways=%s memberships=%s facts=%s invalid_areas=%s",
        result.outcome,
        "-" if result.state_at is None else result.state_at.isoformat(),
        duration_seconds,
        "-" if counts is None else counts.nodes,
        "-" if counts is None else counts.ways,
        "-" if counts is None else counts.memberships,
        "-" if counts is None else counts.facts,
        "-" if result.invalid_area_count is None else result.invalid_area_count,
    )
    return OSM_IMPORT_EXIT_CODES[result.outcome]


def apply_osm_import_action() -> int:
    """
    Run the import and report it: updated and unchanged exit 0, skipped exits 2, every other outcome exits 1.

    A named importer failure is reported with its constant message; any other failure is reported by its type and
    passed on, so the shared wrapper logs its redacted traceback.
    """
    started = fetch_monotonic_seconds()
    settings = build_osm_import_settings()
    try:
        result = apply_osm_import_command(settings)
    except OSM_IMPORT_NAMED_ERRORS as failure:
        fetch_logger(__name__).error("OSM import outcome=failed cause=%s: %s duration_s=%.1f", type(failure).__name__, failure, fetch_monotonic_seconds() - started)
        return 1
    except Exception as failure:
        fetch_logger(__name__).error("OSM import outcome=failed cause=%s duration_s=%.1f", type(failure).__name__, fetch_monotonic_seconds() - started)
        raise
    return apply_osm_import_report(result, fetch_monotonic_seconds() - started)


if __name__ == "__main__":
    sys.exit(apply_administrative_run("osm_import", apply_osm_import_action))
