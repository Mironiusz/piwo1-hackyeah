"""Validate source metadata without downloading files or accessing the database."""

import re
from datetime import UTC, datetime
from urllib.parse import urlsplit

OSM_SOURCE_DIRECTORY = "https://download.geofabrik.de/europe/poland/"
OSM_DATED_FILENAME_PATTERN = re.compile(r"malopolskie-[0-9]{6}\.osm\.pbf")
OSM_MD5_PATTERN = re.compile(r"[0-9a-fA-F]{32}")
OSM_STATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?(?:Z|[+-][0-9]{2}:[0-9]{2})")


class OsmSourceError(ValueError):
    """Describe source metadata that cannot be accepted for a complete import."""


def resolve_osm_source_location(location: str) -> str:
    """Accept only an absolute dated extract URL in the selected source directory."""
    if any(character.isspace() or ord(character) < 32 for character in location):
        raise OsmSourceError("Invalid source location")
    try:
        parsed = urlsplit(location)
    except ValueError as error:
        raise OsmSourceError("Invalid source location") from error
    filename = parsed.path.removeprefix("/europe/poland/")
    if parsed.scheme != "https" or parsed.netloc != "download.geofabrik.de" or parsed.query or parsed.fragment or not OSM_DATED_FILENAME_PATTERN.fullmatch(filename):
        raise OsmSourceError("Invalid source location")
    if location != OSM_SOURCE_DIRECTORY + filename:
        raise OsmSourceError("Invalid source location")
    return location


def resolve_osm_checksum(checksum_text: str, filename: str, actual_checksum: str) -> str:
    """Require one published MD5 for the selected filename and a matching computed digest."""
    if not OSM_DATED_FILENAME_PATTERN.fullmatch(filename):
        raise OsmSourceError("Invalid checksum filename")
    lines = checksum_text.strip().splitlines()
    if len(lines) != 1:
        raise OsmSourceError("Invalid published checksum")
    fields = lines[0].split()
    if len(fields) not in (1, 2) or not OSM_MD5_PATTERN.fullmatch(fields[0]):
        raise OsmSourceError("Invalid published checksum")
    if len(fields) == 2 and fields[1] not in (filename, "*" + filename):
        raise OsmSourceError("Checksum belongs to another file")
    if not OSM_MD5_PATTERN.fullmatch(actual_checksum):
        raise OsmSourceError("Invalid computed checksum")
    expected_checksum = fields[0].lower()
    if expected_checksum != actual_checksum.lower():
        raise OsmSourceError("Source checksum mismatch")
    return expected_checksum


def resolve_osm_source_state(header_timestamp: str) -> datetime:
    """Read an aware source instant without dropping its supplied precision or offset."""
    if not OSM_STATE_PATTERN.fullmatch(header_timestamp):
        raise OsmSourceError("Invalid source state instant")
    if not header_timestamp.endswith("Z") and int(header_timestamp[-2:]) > 59:
        raise OsmSourceError("Invalid source state offset")
    try:
        state_at = datetime.fromisoformat(header_timestamp)
    except ValueError as error:
        raise OsmSourceError("Invalid source state instant") from error
    offset = state_at.utcoffset()
    if offset is None or abs(offset.total_seconds()) > 14 * 60 * 60:
        raise OsmSourceError("Invalid source state offset")
    return state_at


def resolve_osm_source_is_newer(state_at: datetime, current_state_at: datetime | None) -> bool:
    """Allow a first or newer copy, leave an equal instant unchanged, and refuse older data."""
    if state_at.utcoffset() is None or (current_state_at is not None and current_state_at.utcoffset() is None):
        raise OsmSourceError("Source state comparison requires aware instants")
    if current_state_at is None:
        return True
    source_instant = state_at.astimezone(UTC)
    current_instant = current_state_at.astimezone(UTC)
    if source_instant < current_instant:
        raise OsmSourceError("Source state is older than the current copy")
    return source_instant > current_instant
