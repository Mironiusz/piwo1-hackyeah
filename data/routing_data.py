"""Store and verify immutable manifests of prepared routing files."""

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROUTING_FILE_NAMES = ("network.osm.pbf", "valhalla_tiles.tar")
ROUTING_MANIFEST_NAME = "manifest.json"
ROUTING_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


class RoutingDataError(ValueError):
    """Describe incomplete routing files that must not be activated."""


@dataclass(frozen=True)
class RoutingFileDigest:
    """Identify one immutable routing file by name, byte count and checksum."""

    filename: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class RoutingManifest:
    """Tie prepared routing files to their source instant."""

    state_at: datetime
    files: tuple[RoutingFileDigest, ...]


def fetch_routing_file_digest(directory: Path, filename: str) -> RoutingFileDigest:
    """Hash one regular prepared file without loading its contents into memory."""
    path = directory / filename
    if filename not in ROUTING_FILE_NAMES or path.is_symlink() or not path.is_file():
        raise RoutingDataError("Missing or invalid routing file")
    try:
        with path.open("rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
    except OSError as error:
        raise RoutingDataError("Cannot read routing file") from error
    if size <= 0:
        raise RoutingDataError("Empty routing file")
    return RoutingFileDigest(filename, size, digest)


def apply_osm_routing_manifest(directory: Path, state_at: datetime) -> RoutingManifest:
    """Create a complete manifest atomically without overwriting an existing copy's manifest."""
    if state_at.utcoffset() is None:
        raise RoutingDataError("Routing source instant must be aware")
    files = tuple(fetch_routing_file_digest(directory, name) for name in ROUTING_FILE_NAMES)
    manifest = RoutingManifest(state_at, files)
    payload = {"version": 1, "state_at": state_at.isoformat(), "files": {item.filename: {"size_bytes": item.size_bytes, "sha256": item.sha256} for item in files}}
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, prefix=".manifest-", delete=False) as stream:
            temporary_path = Path(stream.name)
            json.dump(payload, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_path, directory / ROUTING_MANIFEST_NAME)
    except OSError as error:
        raise RoutingDataError("Cannot create immutable routing manifest") from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return manifest


def fetch_osm_routing_manifest(directory: Path) -> RoutingManifest:
    """Read a manifest and require both files to match its sizes and SHA-256 checksums."""
    path = directory / ROUTING_MANIFEST_NAME
    if path.is_symlink():
        raise RoutingDataError("Invalid routing manifest")
    try:
        with path.open(encoding="utf-8") as stream:
            payload = json.load(stream)
        if not isinstance(payload, dict) or set(payload) != {"version", "state_at", "files"} or type(payload["version"]) is not int or payload["version"] != 1:
            raise RoutingDataError("Invalid routing manifest format")
        state_at = datetime.fromisoformat(payload["state_at"])
        if state_at.utcoffset() is None:
            raise RoutingDataError("Invalid routing source instant")
        records = payload["files"]
        if not isinstance(records, dict) or set(records) != set(ROUTING_FILE_NAMES):
            raise RoutingDataError("Invalid routing manifest file list")
        files = tuple(fetch_routing_file_digest(directory, name) for name in ROUTING_FILE_NAMES)
        for item in files:
            record = records[item.filename]
            if not isinstance(record, dict) or set(record) != {"size_bytes", "sha256"} or type(record["size_bytes"]) is not int:
                raise RoutingDataError("Invalid routing manifest file record")
            if not isinstance(record["sha256"], str) or not ROUTING_SHA256_PATTERN.fullmatch(record["sha256"]):
                raise RoutingDataError("Invalid routing manifest checksum")
            if record["size_bytes"] != item.size_bytes or record["sha256"] != item.sha256:
                raise RoutingDataError("Routing file integrity mismatch")
    except (OSError, ValueError, TypeError, KeyError) as error:
        if isinstance(error, RoutingDataError):
            raise
        raise RoutingDataError("Cannot verify routing manifest") from error
    return RoutingManifest(state_at, files)
