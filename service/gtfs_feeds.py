"""Prepare one GTFS feed for the Valhalla ingest: unpack it and let missing accessibility count as accessible, the exception of O9."""

import csv
import io
import shutil
import zipfile
import zlib
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from types import MappingProxyType

GTFS_ACCESSIBILITY_VALUES = frozenset({"", "0", "1", "2"})
GTFS_KNOWN_ACCESSIBILITY = frozenset({"1", "2"})
GTFS_TRAM_ROUTE_TYPE = "0"
GTFS_TRAM_SERVICE_ROUTE_TYPE = "900"


class GtfsFeedError(ValueError):
    """Describe a feed whose files cannot be prepared for the ingest."""


type GtfsRow = dict[str, str]


def resolve_gtfs_accessibility(value: str, inherited: str | None) -> str:
    """Decide the accessibility of a stop or a trip: 1 and 2 never change, while empty or 0 takes an inherited 1 or 2 when there is one and becomes 1 otherwise."""
    if value not in GTFS_ACCESSIBILITY_VALUES:
        raise GtfsFeedError("Invalid GTFS accessibility value")
    if value in GTFS_KNOWN_ACCESSIBILITY:
        return value
    return inherited if inherited in GTFS_KNOWN_ACCESSIBILITY else "1"


def build_gtfs_stop_rows(rows: Sequence[GtfsRow]) -> list[GtfsRow]:
    """Rewrite wheelchair_boarding of every stop; a child stop inherits 1 or 2 of its parent station, as the GTFS reference defines for an empty child value."""
    stations = {row["stop_id"]: row.get("wheelchair_boarding") or "" for row in rows}
    return [{**row, "wheelchair_boarding": resolve_gtfs_accessibility(row.get("wheelchair_boarding") or "", stations.get(row.get("parent_station") or ""))} for row in rows]


def build_gtfs_trip_rows(rows: Sequence[GtfsRow]) -> list[GtfsRow]:
    """Rewrite wheelchair_accessible of every trip, so that only a trip marked 2 counts as not accessible."""
    return [{**row, "wheelchair_accessible": resolve_gtfs_accessibility(row.get("wheelchair_accessible") or "", None)} for row in rows]


def build_gtfs_route_rows(rows: Sequence[GtfsRow]) -> list[GtfsRow]:
    """Give a route of the extended type 900, tram service, the basic tram type 0 the ingest reads, keeping every other route as it is."""
    return [{**row, "route_type": GTFS_TRAM_ROUTE_TYPE} if row.get("route_type") == GTFS_TRAM_SERVICE_ROUTE_TYPE else row for row in rows]


GTFS_TABLE_RULES: Mapping[str, Callable[[Sequence[GtfsRow]], list[GtfsRow]]] = MappingProxyType(
    {"stops.txt": build_gtfs_stop_rows, "trips.txt": build_gtfs_trip_rows, "routes.txt": build_gtfs_route_rows}
)
GTFS_REQUIRED_COLUMNS: Mapping[str, frozenset[str]] = MappingProxyType({"stops.txt": frozenset({"stop_id"}), "trips.txt": frozenset(), "routes.txt": frozenset({"route_type"})})
GTFS_ADDED_COLUMNS: Mapping[str, str] = MappingProxyType({"stops.txt": "wheelchair_boarding", "trips.txt": "wheelchair_accessible"})


def apply_gtfs_table(archive: zipfile.ZipFile, name: str, target: Path) -> None:
    """Read one rewritten table of a feed, apply its rule and write it in UTF-8, adding the accessibility column when the feed lacks it."""
    with archive.open(name) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        fieldnames = list(reader.fieldnames or ())
        rows = list(reader)
    if not GTFS_REQUIRED_COLUMNS[name] <= set(fieldnames):
        raise GtfsFeedError("GTFS table lacks a required column")
    added = GTFS_ADDED_COLUMNS.get(name)
    if added is not None and added not in fieldnames:
        fieldnames.append(added)
    with target.open("x", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(GTFS_TABLE_RULES[name](rows))


def apply_gtfs_feed_preparation(source: Path, target: Path) -> None:
    """
    Unpack one feed into a new directory of the ingest input.

    stops.txt, trips.txt and routes.txt are rewritten by the rules of this module and every other file is copied
    unchanged. The feed is read with utf-8-sig, so a byte order mark is dropped. A member in a subdirectory or with a
    path in its name is refused, so nothing is ever written outside the target.
    """
    try:
        target.mkdir(parents=True)
        with zipfile.ZipFile(source) as archive:
            for member in archive.infolist():
                name = member.filename
                if "/" in name or "\\" in name or name in {"", ".", ".."}:
                    raise GtfsFeedError("GTFS feed holds a file outside its root")
                if name in GTFS_TABLE_RULES:
                    apply_gtfs_table(archive, name, target / name)
                    continue
                with archive.open(member) as stream, (target / name).open("xb") as output:
                    shutil.copyfileobj(stream, output)
    except GtfsFeedError:
        raise
    except (OSError, EOFError, RuntimeError, NotImplementedError, ValueError, csv.Error, zipfile.BadZipFile, zlib.error) as error:
        raise GtfsFeedError("Cannot prepare GTFS feed") from error
