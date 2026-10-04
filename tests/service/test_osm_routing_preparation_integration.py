"""Run real PBF selection with invented source data and controlled tile tools."""

import asyncio
import hashlib
import json
from pathlib import Path

import httpx
import osmium
import pytest

from data.osm_reader import fetch_osm_elements
from data.osm_valhalla import OsmTileBuildError
from data.routing_data import fetch_osm_routing_manifest
from service.osm_acquisition import fetch_osm_extract
from service.osm_routing_preparation import build_osm_valhalla_config, prepare_osm_routing_data
from service.osm_source_validation import OSM_SOURCE_DIRECTORY


def apply_invented_source(directory: Path) -> Path:
    """Write a small complete administrative relation and a crossing pedestrian way."""
    xml = directory / "invented.osm"
    timestamp = 'timestamp="2026-10-03T00:00:00Z" version="1"'
    coordinates = ((19.9, 50), (20, 50), (20, 50.1), (19.9, 50.1), (19.92, 50.02), (20.1, 50.02))
    nodes = "".join(f'<node id="{index}" lon="{lon}" lat="{lat}" {timestamp}/>' for index, (lon, lat) in enumerate(coordinates, 1))
    xml.write_text(
        f'<osm version="0.6">{nodes}<way id="1" {timestamp}><nd ref="1"/><nd ref="2"/><nd ref="3"/><nd ref="4"/><nd ref="1"/></way>'
        f'<way id="10" {timestamp}><nd ref="5"/><nd ref="6"/><tag k="highway" v="path"/><tag k="foot" v="yes"/><tag k="access" v="private"/></way>'
        f'<relation id="449696" {timestamp}><member type="way" ref="1" role="outer"/><tag k="type" v="multipolygon"/><tag k="boundary" v="administrative"/></relation></osm>',
        encoding="utf-8",
    )
    header = osmium.io.Header()
    header.set("osmosis_replication_timestamp", "2026-10-03T00:00:00Z")
    source = directory / "invented.osm.pbf"
    with osmium.SimpleWriter(str(source), header=header) as writer:
        for element in osmium.FileProcessor(xml):
            writer.add(element)
    return source


@pytest.mark.integration
def test_download_to_network_and_verified_manifest(tmp_path, monkeypatch):
    source = apply_invented_source(tmp_path)
    directory = tmp_path / "prepared"
    calls = []
    acquired = []
    source_bytes = source.read_bytes()

    async def apply_invented_command(arguments, deadline):
        calls.append(arguments)
        config = json.loads(Path(arguments[2]).read_text())
        assert config["mjolnir"]["keep_osm_node_ids"] is True
        assert config["mjolnir"]["keep_all_osm_node_ids"] is True
        assert config["mjolnir"]["include_platforms"] is True
        if arguments[0].endswith("valhalla_build_extract"):
            Path(config["mjolnir"]["tile_extract"]).write_bytes(b"invented tile archive")

    monkeypatch.setattr("data.osm_valhalla.apply_osm_valhalla_command", apply_invented_command)

    async def run():
        def respond(request):
            url = str(request.url)
            if url.endswith("latest.osm.pbf"):
                return httpx.Response(302, headers={"location": OSM_SOURCE_DIRECTORY + "malopolskie-261003.osm.pbf"})
            if url.endswith(".md5"):
                return httpx.Response(200, text=hashlib.md5(source_bytes, usedforsecurity=False).hexdigest())
            return httpx.Response(200, content=source_bytes)

        deadline = asyncio.get_running_loop().time() + 60
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client, fetch_osm_extract(client, deadline) as extract:
            acquired.append(extract.path)
            return await prepare_osm_routing_data(extract.path, directory, {"mjolnir": {}}, tmp_path / "tools", deadline)

    manifest = asyncio.run(run())
    assert acquired and not acquired[0].exists()
    assert manifest == fetch_osm_routing_manifest(directory)
    assert [Path(call[0]).name for call in calls] == ["valhalla_build_tiles", "valhalla_build_extract"]
    elements = tuple(fetch_osm_elements(directory / "network.osm.pbf"))
    assert [(element.element_type, element.element_id) for element in elements] == [("node", 5), ("node", 6), ("way", 10)]
    assert "access" not in elements[-1].tags
    assert elements[-1].node_ids == (5, 6)
    assert int((directory / "valhalla_tiles.tar").stat().st_mtime) == int(manifest.state_at.timestamp())
    assert not (directory / "current").exists()


def test_configuration_copy_has_no_transit_inputs(tmp_path):
    template = {"mjolnir": {"transit_dir": "invented", "transit_feeds_dir": "invented"}, "loki": {"use_connectivity": True}}
    result = build_osm_valhalla_config(template, tmp_path)
    assert "transit_dir" not in result["mjolnir"]
    assert "transit_feeds_dir" not in result["mjolnir"]
    assert template["mjolnir"]["transit_dir"] == "invented"
    assert result["loki"] == template["loki"]


def test_existing_preparation_directory_is_preserved(tmp_path):
    directory = tmp_path / "prepared"
    directory.mkdir()
    (directory / "sentinel").write_bytes(b"existing")

    async def run():
        with pytest.raises(OsmTileBuildError):
            await prepare_osm_routing_data(tmp_path / "missing.osm.pbf", directory, {"mjolnir": {}}, tmp_path / "tools", asyncio.get_running_loop().time() + 60)

    asyncio.run(run())
    assert (directory / "sentinel").read_bytes() == b"existing"


@pytest.mark.integration
def test_failed_tiles_never_produce_a_manifest_or_pointer(tmp_path, monkeypatch):
    source = apply_invented_source(tmp_path)
    directory = tmp_path / "prepared"

    async def apply_failed_command(arguments, deadline):
        raise OsmTileBuildError("Invented build failure")

    monkeypatch.setattr("data.osm_valhalla.apply_osm_valhalla_command", apply_failed_command)

    async def run():
        with pytest.raises(OsmTileBuildError, match="Invented build failure"):
            await prepare_osm_routing_data(source, directory, {"mjolnir": {}}, tmp_path / "tools", asyncio.get_running_loop().time() + 60)

    asyncio.run(run())
    assert (directory / "network.osm.pbf").exists()
    assert not (directory / "manifest.json").exists()
    assert not (directory / "current").exists()
