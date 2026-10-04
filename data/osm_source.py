"""Read Geofabrik responses without applying source selection rules or retrying."""

import asyncio
import hashlib
from pathlib import Path

import httpx

OSM_REQUEST_TIMEOUT_SECONDS = 30.0
OSM_CHECKSUM_MAX_BYTES = 4096


class OsmDownloadError(ValueError):
    """Describe an acquisition that cannot deliver a complete source file."""


def build_osm_http_client() -> httpx.AsyncClient:
    """Create the importer's TLS-verifying transport with explicit inactivity limits."""
    return httpx.AsyncClient(timeout=httpx.Timeout(OSM_REQUEST_TIMEOUT_SECONDS), follow_redirects=False, trust_env=False, headers={"Accept-Encoding": "identity"})


async def fetch_osm_latest_location(client: httpx.AsyncClient, latest_url: str, deadline: float) -> str:
    """Read one latest-file redirect without following it or loading its body."""
    try:
        async with asyncio.timeout_at(min(deadline, asyncio.get_running_loop().time() + OSM_REQUEST_TIMEOUT_SECONDS)):
            async with client.stream("GET", latest_url, follow_redirects=False, timeout=OSM_REQUEST_TIMEOUT_SECONDS) as response:
                if response.status_code not in (301, 302, 303, 307, 308) or "location" not in response.headers:
                    raise OsmDownloadError("Source did not supply a dated redirect")
                return response.headers["location"]
    except (httpx.HTTPError, TimeoutError) as error:
        raise OsmDownloadError("Cannot obtain source redirect") from error


async def fetch_osm_checksum_text(client: httpx.AsyncClient, url: str, deadline: float) -> str:
    """Read a bounded checksum response within its elapsed deadline."""
    try:
        async with asyncio.timeout_at(min(deadline, asyncio.get_running_loop().time() + OSM_REQUEST_TIMEOUT_SECONDS)):
            async with client.stream("GET", url, follow_redirects=False, timeout=OSM_REQUEST_TIMEOUT_SECONDS) as response:
                if response.status_code != 200:
                    raise OsmDownloadError("Source checksum request failed")
                contents = bytearray()
                async for chunk in response.aiter_bytes():
                    contents.extend(chunk)
                    if len(contents) > OSM_CHECKSUM_MAX_BYTES:
                        raise OsmDownloadError("Source checksum response is too large")
                return contents.decode("ascii")
    except (httpx.HTTPError, TimeoutError, UnicodeDecodeError) as error:
        raise OsmDownloadError("Cannot read source checksum") from error


async def apply_osm_download(client: httpx.AsyncClient, url: str, path: Path, deadline: float) -> str:
    """Stream a dated extract to a new run-local file and compute its MD5."""
    digest = hashlib.md5(usedforsecurity=False)
    size = 0
    try:
        async with asyncio.timeout_at(deadline):
            async with client.stream("GET", url, follow_redirects=False, timeout=OSM_REQUEST_TIMEOUT_SECONDS) as response:
                if response.status_code != 200:
                    raise OsmDownloadError("Source extract request failed")
                with path.open("xb") as output:
                    async for chunk in response.aiter_bytes():
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                if not size:
                    raise OsmDownloadError("Source extract is empty")
                expected_size = response.headers.get("content-length")
                if expected_size is not None and (not expected_size.isdecimal() or int(expected_size) != size):
                    raise OsmDownloadError("Source extract length mismatch")
    except (httpx.HTTPError, TimeoutError, OSError) as error:
        raise OsmDownloadError("Cannot download source extract") from error
    return digest.hexdigest()
