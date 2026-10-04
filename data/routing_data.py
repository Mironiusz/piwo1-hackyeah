"""Store and verify immutable manifests of prepared routing files."""

import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROUTING_FILE_NAMES = ("network.osm.pbf", "valhalla_tiles.tar")
ROUTING_MANIFEST_NAME = "manifest.json"
ROUTING_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
ROUTING_COPIES_NAME = "copies"
ROUTING_POINTER_NAME = "current"
ROUTING_PREPARATION_PREFIX = ".prepare-"
ROUTING_COPY_NAME_PATTERN = re.compile(r"[0-9]+")


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


def build_routing_copy_name(state_at: datetime) -> str:
    """Name a copy directory by its source instant in whole seconds since the epoch, refusing a fraction of a second."""
    if state_at.utcoffset() is None:
        raise RoutingDataError("Routing source instant must be aware")
    if state_at.microsecond:
        raise RoutingDataError("Routing source instant must be a whole second")
    return str(int(state_at.timestamp()))


def fetch_routing_pointer(root: Path) -> str | None:
    """Read the copy name the pointer selects, or None while no pointer has been published."""
    path = root / ROUTING_POINTER_NAME
    if path.is_symlink():
        raise RoutingDataError("Invalid routing pointer")
    try:
        content = path.read_text(encoding="ascii")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        raise RoutingDataError("Cannot read routing pointer") from error
    name = content.removesuffix("\n")
    if not ROUTING_COPY_NAME_PATTERN.fullmatch(name):
        raise RoutingDataError("Invalid routing pointer")
    return name


def apply_routing_pointer(root: Path, name: str) -> None:
    """Point the routing service at a copy by replacing the pointer through a synced temporary file and a rename."""
    if not ROUTING_COPY_NAME_PATTERN.fullmatch(name):
        raise RoutingDataError("Invalid routing copy name")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="ascii", dir=root, prefix=".current-", delete=False) as stream:
            temporary_path = Path(stream.name)
            stream.write(name + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, root / ROUTING_POINTER_NAME)
        temporary_path = None
    except OSError as error:
        raise RoutingDataError("Cannot publish routing pointer") from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def fetch_routing_preparations(root: Path) -> tuple[Path, ...]:
    """List the preparation directories left by interrupted imports; no preparation directory is ever published."""
    copies = root / ROUTING_COPIES_NAME
    try:
        return tuple(sorted(entry for entry in copies.iterdir() if entry.name.startswith(ROUTING_PREPARATION_PREFIX))) if copies.exists() else ()
    except OSError as error:
        raise RoutingDataError("Cannot list routing preparations") from error


def apply_routing_preparation_directory(root: Path) -> Path:
    """Create a new private preparation directory beside the published copies."""
    copies = root / ROUTING_COPIES_NAME
    try:
        copies.mkdir(exist_ok=True)
        return Path(tempfile.mkdtemp(prefix=ROUTING_PREPARATION_PREFIX, dir=copies))
    except OSError as error:
        raise RoutingDataError("Cannot create routing preparation directory") from error


def apply_routing_copy_placement(preparation: Path, root: Path, name: str) -> Path:
    """Move a verified preparation into its copy directory, never replacing an existing directory."""
    target = root / ROUTING_COPIES_NAME / name
    if target.exists() or target.is_symlink():
        raise RoutingDataError("Routing copy directory already exists")
    try:
        os.rename(preparation, target)
    except OSError as error:
        raise RoutingDataError("Cannot place routing copy directory") from error
    return target


def apply_routing_directory_removal(path: Path) -> None:
    """Delete an unpublished preparation or an incomplete copy directory that no committed copy owns."""
    if path.is_symlink():
        raise RoutingDataError("Refusing to remove a linked routing directory")
    try:
        shutil.rmtree(path)
    except OSError as error:
        raise RoutingDataError("Cannot remove routing directory") from error
