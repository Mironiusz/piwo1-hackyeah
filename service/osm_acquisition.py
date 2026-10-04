"""Acquire a validated source with temporary storage owned by one import run."""

import asyncio
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx

from data.osm_reader import fetch_osm_header_timestamp
from data.osm_source import apply_osm_download, fetch_osm_checksum_text, fetch_osm_latest_location
from service.osm_source_validation import OSM_SOURCE_DIRECTORY, OsmSourceError, resolve_osm_checksum, resolve_osm_source_location, resolve_osm_source_state


@dataclass(frozen=True)
class OsmExtract:
    """Identify validated source bytes available only within the acquisition context."""

    path: Path
    filename: str
    state_at: datetime


@asynccontextmanager
async def fetch_osm_extract(client: httpx.AsyncClient, deadline: float) -> AsyncIterator[OsmExtract]:
    """Validate redirect, checksum and source state and remove temporary data on every exit."""
    location = await fetch_osm_latest_location(client, OSM_SOURCE_DIRECTORY + "malopolskie-latest.osm.pbf", deadline)
    url = resolve_osm_source_location(location)
    filename = url.rsplit("/", 1)[1]
    checksum_text = await fetch_osm_checksum_text(client, url + ".md5", deadline)
    with tempfile.TemporaryDirectory(prefix="osm-import-", dir=tempfile.gettempdir()) as directory:
        path = Path(directory) / filename
        digest = await apply_osm_download(client, url, path, deadline)
        resolve_osm_checksum(checksum_text, filename, digest)
        if asyncio.get_running_loop().time() >= deadline:
            raise OsmSourceError("Source acquisition deadline expired")
        state_at = resolve_osm_source_state(fetch_osm_header_timestamp(path))
        if asyncio.get_running_loop().time() >= deadline:
            raise OsmSourceError("Source acquisition deadline expired")
        yield OsmExtract(path, filename, state_at)
