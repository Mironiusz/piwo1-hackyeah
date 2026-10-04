"""Start the manual GTFS step of the loading program: python -m worker.gtfs_import, run after python -m worker.osm_import in the same one-off container."""

import logging
import sys

from common_time import fetch_monotonic_seconds
from config.logging import fetch_logger
from service.administrative import apply_administrative_run
from service.gtfs_import import GTFS_IMPORT_NAMED_ERRORS, GtfsImportResult, GtfsImportSettings, apply_gtfs_import_command, fetch_transit_serves_copy_in_use
from worker.osm_import import build_osm_import_settings


def build_gtfs_import_settings() -> GtfsImportSettings:
    """Collect the four paths of the importer the step reuses, naming every missing one and its file exactly as the import does."""
    settings = build_osm_import_settings()
    return GtfsImportSettings(settings.workspace_root, settings.routing_root, settings.tool_directory, settings.config_template)


def apply_gtfs_import_report(result: GtfsImportResult, is_served: bool, duration_seconds: float) -> int:
    """Write the one outcome line the operator reads and return 0 only when the routing data with public transport in use belongs to the OpenStreetMap copy in use."""
    code = 0 if is_served else 1
    fetch_logger(__name__).log(
        logging.INFO if code == 0 else logging.ERROR,
        "GTFS import outcome=%s fetch=%s transit=%s serves_copy_in_use=%s duration_s=%.1f",
        result.outcome,
        result.fetch,
        "-" if result.transit_name is None else result.transit_name,
        is_served,
        duration_seconds,
    )
    return code


def apply_gtfs_import_action() -> int:
    """
    Run the GTFS step and report it: exit 0 when the routing data with public transport in use was built from the OpenStreetMap copy in use, and 1 otherwise.

    A named failure is reported with its constant message and exits 1 even when earlier data still matches, because the
    run did not finish; any other failure is reported by its type and passed on, so the shared wrapper logs its redacted
    traceback.
    """
    started = fetch_monotonic_seconds()
    settings = build_gtfs_import_settings()
    try:
        result = apply_gtfs_import_command(settings)
        is_served = fetch_transit_serves_copy_in_use(settings.routing_root)
    except GTFS_IMPORT_NAMED_ERRORS as failure:
        fetch_logger(__name__).error("GTFS import outcome=failed cause=%s: %s duration_s=%.1f", type(failure).__name__, failure, fetch_monotonic_seconds() - started)
        return 1
    except Exception as failure:
        fetch_logger(__name__).error("GTFS import outcome=failed cause=%s duration_s=%.1f", type(failure).__name__, fetch_monotonic_seconds() - started)
        raise
    return apply_gtfs_import_report(result, is_served, fetch_monotonic_seconds() - started)


if __name__ == "__main__":
    sys.exit(apply_administrative_run("gtfs_import", apply_gtfs_import_action))
