"""Keep complete copies of the three GTFS feeds under ROUTING_DATA_DIR/gtfs, with the day each feed was published and the pointer to the copy in use."""

import json
import os
import re
import zipfile
import zlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType

from common_time import fetch_utc_now
from data.gtfs_source import GTFS_FEEDS
from data.routing_directories import apply_directory_placement, apply_directory_pointer, apply_preparation_directory, fetch_directory_pointer, fetch_preparation_directories

GTFS_DIRECTORY_NAME = "gtfs"
GTFS_DAYS_NAME = "feeds.json"
GTFS_COPY_NAME_PATTERN = re.compile(r"[0-9]+")
GTFS_REQUIRED_MEMBERS = frozenset({"agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt", "calendar_dates.txt"})


class GtfsCopyError(ValueError):
    """Describe a GTFS copy that is incomplete or invalid and must not be used."""


@dataclass(frozen=True)
class GtfsCopy:
    """Name one complete GTFS copy, its directory and the day each of its feeds was published."""

    name: str
    directory: Path
    published_on: Mapping[str, date]


def build_gtfs_feed_path(directory: Path, feed: str) -> Path:
    """Give the file of one feed inside a GTFS copy or its preparation."""
    return directory / f"{feed}.zip"


def fetch_gtfs_preparations(root: Path) -> tuple[Path, ...]:
    """List the GTFS preparations an interrupted run left behind."""
    return fetch_preparation_directories(root / GTFS_DIRECTORY_NAME)


def apply_gtfs_preparation(root: Path) -> Path:
    """Create a new private directory the feeds of one fetch are written into."""
    return apply_preparation_directory(root / GTFS_DIRECTORY_NAME)


def apply_gtfs_feed_validation(path: Path) -> None:
    """Refuse a feed file that is not a regular, intact zip holding at its root every GTFS file a route with public transport needs."""
    if path.is_symlink() or not path.is_file():
        raise GtfsCopyError("Missing GTFS feed file")
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise GtfsCopyError("Corrupt GTFS feed file")
            names = frozenset(archive.namelist())
    except (OSError, EOFError, RuntimeError, NotImplementedError, zipfile.BadZipFile, zlib.error) as error:
        raise GtfsCopyError("Invalid GTFS feed file") from error
    if not GTFS_REQUIRED_MEMBERS.issubset(names):
        raise GtfsCopyError("GTFS feed lacks a required file")


def apply_gtfs_copy(root: Path, feeds: Mapping[str, date], preparation: Path) -> str:
    """
    Make a filled preparation the GTFS copy in use and return its name.

    All three feeds must be present with their days, and each must be an intact zip with the required GTFS files. The
    days go to feeds.json, the preparation is renamed to the instant of the fetch in whole seconds since the epoch, and
    only then does the pointer gtfs/current name it. A refused preparation leaves the earlier copy and its pointer as
    they were.
    """
    if set(feeds) != set(GTFS_FEEDS):
        raise GtfsCopyError("GTFS copy needs all three feeds")
    for feed in GTFS_FEEDS:
        apply_gtfs_feed_validation(build_gtfs_feed_path(preparation, feed))
    try:
        with (preparation / GTFS_DAYS_NAME).open("x", encoding="utf-8") as stream:
            json.dump({feed: feeds[feed].isoformat() for feed in GTFS_FEEDS}, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise GtfsCopyError("Cannot write GTFS feed days") from error
    name = str(int(fetch_utc_now().timestamp()))
    parent = root / GTFS_DIRECTORY_NAME
    apply_directory_placement(preparation, parent / name)
    apply_directory_pointer(parent, name, GTFS_COPY_NAME_PATTERN)
    return name


def fetch_gtfs_copy(root: Path) -> GtfsCopy | None:
    """Read the GTFS copy the pointer names with the day of each feed, or None while no copy was ever made; a copy with a missing file or day is refused."""
    parent = root / GTFS_DIRECTORY_NAME
    name = fetch_directory_pointer(parent, GTFS_COPY_NAME_PATTERN)
    if name is None:
        return None
    directory = parent / name
    days_path = directory / GTFS_DAYS_NAME
    try:
        if days_path.is_symlink():
            raise ValueError("Linked GTFS feed days")
        payload = json.loads(days_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or set(payload) != set(GTFS_FEEDS) or not all(isinstance(value, str) for value in payload.values()):
            raise ValueError("Invalid GTFS feed days")
        published_on = {feed: date.fromisoformat(payload[feed]) for feed in GTFS_FEEDS}
    except (OSError, ValueError) as error:
        raise GtfsCopyError("Cannot read GTFS feed days") from error
    for feed in GTFS_FEEDS:
        path = build_gtfs_feed_path(directory, feed)
        if path.is_symlink() or not path.is_file():
            raise GtfsCopyError("Missing GTFS feed file")
    return GtfsCopy(name, directory, MappingProxyType(published_on))
