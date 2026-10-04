"""Verify source acquisition with HTTPX mock transport and invented bytes."""

import asyncio
import hashlib
from pathlib import Path

import httpx
import pytest

from data.osm_source import OsmDownloadError, apply_osm_download, build_osm_http_client, fetch_osm_checksum_text, fetch_osm_latest_location
from service.osm_acquisition import fetch_osm_extract
from service.osm_source_validation import OSM_SOURCE_DIRECTORY, OsmSourceError

pytestmark = pytest.mark.integration


class InventedStream(httpx.AsyncByteStream):
    """Deliver invented chunks with optional event-loop scheduling delays."""

    def __init__(self, delay: float = 0):
        self.delay = delay

    async def __aiter__(self):
        await asyncio.sleep(self.delay)
        yield b"invented"


def test_client_has_explicit_limits_and_no_redirects():
    async def run():
        async with build_osm_http_client() as client:
            assert client.timeout.connect == client.timeout.read == 30
            assert not client.follow_redirects

    asyncio.run(run())


def test_streamed_download_digest_and_transport_limits(tmp_path):
    async def run():
        def respond(request):
            assert request.extensions["timeout"]["read"] == 30
            return httpx.Response(200, stream=InventedStream())

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            path = tmp_path / "source.pbf"
            digest = await apply_osm_download(client, "https://invented.invalid/source", path, asyncio.get_running_loop().time() + 60)
            assert path.read_bytes() == b"invented"
            assert digest == hashlib.md5(b"invented", usedforsecurity=False).hexdigest()

    asyncio.run(run())


@pytest.mark.parametrize("status", [200, 404, 500])
def test_latest_requires_redirect(status):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(status))) as client:
            with pytest.raises(OsmDownloadError):
                await fetch_osm_latest_location(client, "https://invented.invalid/latest", asyncio.get_running_loop().time() + 60)

    asyncio.run(run())


@pytest.mark.parametrize(
    "response", [httpx.Response(302, headers={"location": "https://elsewhere.invalid"}), httpx.Response(200, content=b""), httpx.Response(200, content=b"a", headers={"content-length": "2"})]
)
def test_bad_extract_response_fails(response, tmp_path):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: response)) as client:
            with pytest.raises(OsmDownloadError):
                await apply_osm_download(client, "https://invented.invalid/source", tmp_path / "source.pbf", asyncio.get_running_loop().time() + 60)

    asyncio.run(run())


def test_checksum_size_is_bounded():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=b"a" * 4097))) as client:
            with pytest.raises(OsmDownloadError):
                await fetch_osm_checksum_text(client, "https://invented.invalid/checksum", asyncio.get_running_loop().time() + 60)

    asyncio.run(run())


def test_whole_run_deadline_interrupts_stream(tmp_path):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=InventedStream(1)))) as client:
            with pytest.raises(OsmDownloadError):
                await apply_osm_download(client, "https://invented.invalid/source", tmp_path / "source.pbf", asyncio.get_running_loop().time() + 0.01)

    asyncio.run(run())


def test_invalid_redirect_is_rejected_before_any_dated_request():
    calls = []

    async def run():
        def respond(request):
            calls.append(str(request.url))
            return httpx.Response(302, headers={"location": "http://download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf"})

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            with pytest.raises(OsmSourceError):
                async with fetch_osm_extract(client, asyncio.get_running_loop().time() + 60):
                    pytest.fail("Invalid redirect must not yield an extract")

    asyncio.run(run())
    assert calls == [OSM_SOURCE_DIRECTORY + "malopolskie-latest.osm.pbf"]


def test_acquisition_validates_pbf_and_cleans_after_caller_failure(tmp_path):
    import osmium

    header = osmium.io.Header()
    header.set("osmosis_replication_timestamp", "2026-10-03T00:00:00Z")
    fixture = tmp_path / "invented.osm.pbf"
    with osmium.SimpleWriter(str(fixture), header=header):
        pass
    contents = fixture.read_bytes()
    acquired: list[Path] = []
    url = OSM_SOURCE_DIRECTORY + "malopolskie-261003.osm.pbf"

    async def run():
        def respond(request):
            if str(request.url).endswith("latest.osm.pbf"):
                return httpx.Response(302, headers={"location": url})
            if str(request.url).endswith(".md5"):
                return httpx.Response(200, text=hashlib.md5(contents, usedforsecurity=False).hexdigest())
            return httpx.Response(200, content=contents)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            with pytest.raises(RuntimeError, match="invented caller failure"):
                async with fetch_osm_extract(client, asyncio.get_running_loop().time() + 60) as extract:
                    acquired.append(extract.path)
                    assert extract.path.read_bytes() == contents
                    assert extract.state_at.isoformat() == "2026-10-03T00:00:00+00:00"
                    raise RuntimeError("invented caller failure")

    asyncio.run(run())
    assert acquired and not acquired[0].exists() and not acquired[0].parent.exists()


@pytest.mark.parametrize("failure", [httpx.ConnectTimeout, httpx.ReadTimeout])
def test_transport_timeouts_are_not_retried(failure, tmp_path):
    calls = []

    async def run():
        def respond(request):
            calls.append(request)
            raise failure("invented transport failure", request=request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            with pytest.raises(OsmDownloadError):
                await apply_osm_download(client, "https://invented.invalid/source", tmp_path / "source.pbf", asyncio.get_running_loop().time() + 60)

    asyncio.run(run())
    assert len(calls) == 1


def test_progressing_download_survives_former_fifteen_minute_ceiling(tmp_path, monkeypatch):
    async def run():
        loop = asyncio.get_running_loop()
        initial = loop.time()
        elapsed = [0.0]
        monkeypatch.setattr(loop, "time", lambda: initial + elapsed[0])

        class ProgressingStream(httpx.AsyncByteStream):
            """Advance invented elapsed time while delivering successive chunks."""

            async def __aiter__(self):
                yield b"first"
                elapsed[0] = 901.0
                await asyncio.sleep(0)
                yield b"second"

        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=ProgressingStream()))) as client:
            path = tmp_path / "source.pbf"
            await apply_osm_download(client, "https://invented.invalid/source", path, initial + 3600)
            assert path.read_bytes() == b"firstsecond"

    asyncio.run(run())
