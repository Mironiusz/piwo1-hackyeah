"""Check one GTFS step with the fetch and the tools replaced at their seams: a fresh copy, a failed fetch building from the kept copy, reuse and every ending without a build."""

import json
from contextlib import contextmanager
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from common_time import build_deadline, fetch_monotonic_seconds
from data.gtfs_copy import fetch_gtfs_copy
from data.gtfs_source import GtfsSourceError
from data.import_workspace import apply_workspace_exclusion, apply_workspace_recovery
from data.local_lock import ImportAlreadyRunning
from data.routing_data import ROUTING_COPIES_NAME, ROUTING_FILE_NAMES, apply_osm_routing_manifest, apply_routing_pointer, build_routing_copy_name
from data.transit_build import TransitBuildError, fetch_transit_pointer
from service.gtfs_import import (
    GtfsImportResult,
    GtfsImportSettings,
    apply_gtfs_import,
    apply_gtfs_import_run,
    build_transit_valhalla_config,
    fetch_transit_serves_copy_in_use,
)
from tests.common_gtfs_feed import INVENTED_GTFS_TABLES, apply_invented_gtfs_feed

pytestmark = pytest.mark.integration

FIRST_COPY_AT = datetime(2026, 10, 3, tzinfo=UTC)
SECOND_COPY_AT = datetime(2026, 10, 4, tzinfo=UTC)
FIRST_FETCH = datetime(2026, 10, 4, 5, 0, tzinfo=UTC)
SECOND_FETCH = datetime(2026, 10, 4, 6, 0, tzinfo=UTC)
PUBLISHED_ON = date(2026, 10, 2)
TEMPLATE = {"mjolnir": {"tile_dir": "/invented/tiles", "transit_dir": "/invented/transit"}}


@pytest.fixture
def settings(tmp_path) -> GtfsImportSettings:
    """Give one run invented paths, a configuration template and a routing root."""
    (tmp_path / "routing").mkdir()
    (tmp_path / "template.json").write_text(json.dumps(TEMPLATE), encoding="utf-8")
    return GtfsImportSettings(tmp_path / "workspace", tmp_path / "routing", tmp_path / "tools", tmp_path / "template.json")


@contextmanager
def apply_admitted_workspace(settings: GtfsImportSettings):
    """Admit a workspace without a database, as the exclusion of the importer does after recovery."""
    with apply_workspace_exclusion(settings.workspace_root) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        yield lease


def apply_osm_copy(root: Path, state_at: datetime) -> str:
    """Place a verified invented OpenStreetMap copy directory and point at it, as a finished import leaves it."""
    name = build_routing_copy_name(state_at)
    directory = root / ROUTING_COPIES_NAME / name
    directory.mkdir(parents=True)
    for filename in ROUTING_FILE_NAMES:
        (directory / filename).write_bytes(b"invented " + filename.encode())
    apply_osm_routing_manifest(directory, state_at)
    apply_routing_pointer(root, name)
    return name


def apply_invented_fetch(monkeypatch, failing_feed: str | None = None, refused_feed: str | None = None) -> None:
    """Replace the fetch: every feed is an invented zip of the given day, except a failing one that raises GtfsSourceError and a refused one with a trip value outside the GTFS reference."""

    def fetch_feed(client, feed, target, deadline):
        if feed == failing_feed:
            raise GtfsSourceError("GTFS feed request failed")
        tables = dict(INVENTED_GTFS_TABLES, **{"trips.txt": "route_id,service_id,trip_id,wheelchair_accessible\r\nR1,SV1,T1,3\r\n"}) if feed == refused_feed else INVENTED_GTFS_TABLES
        apply_invented_gtfs_feed(target, tables)
        return PUBLISHED_ON

    monkeypatch.setattr("service.gtfs_import.fetch_gtfs_feed", fetch_feed)


def apply_invented_build(monkeypatch, builds: list[dict]) -> None:
    """Replace the tool run: record what it got, check the pointer is not yet written and place the preparation as a finished build does."""

    def build(lease, config_path, tool_directory, network_path, timezone_path, preparation, root, name, state_at, deadline):
        assert fetch_transit_pointer(root) != name
        builds.append({"config": json.loads(config_path.read_text(encoding="utf-8")), "network": network_path, "name": name, "state_at": state_at, "workspace": lease.workspace})
        (preparation / "valhalla_tiles.tar").write_bytes(b"invented archive")
        target = root / "transit" / name
        preparation.rename(target)
        return target

    monkeypatch.setattr("service.gtfs_import.apply_transit_build", build)


def apply_run(settings: GtfsImportSettings) -> GtfsImportResult:
    """Run one admitted step with a budget no invented step can exhaust."""
    with apply_admitted_workspace(settings) as lease:
        return apply_gtfs_import_run(settings, object(), lease, build_deadline(60, fetch_monotonic_seconds()))


def apply_fetch_instants(monkeypatch, *instants: datetime) -> None:
    """Name the GTFS copies of the following fetches by the given instants."""
    sequence = iter(instants)
    monkeypatch.setattr("data.gtfs_copy.fetch_utc_now", lambda: next(sequence))


def test_a_fresh_copy_is_built_with_the_osm_copy_in_use_and_pointed_to(settings, monkeypatch):
    copy_name = apply_osm_copy(settings.routing_root, FIRST_COPY_AT)
    apply_fetch_instants(monkeypatch, FIRST_FETCH)
    apply_invented_fetch(monkeypatch)
    builds: list[dict] = []
    apply_invented_build(monkeypatch, builds)
    result = apply_run(settings)
    gtfs_name = str(int(FIRST_FETCH.timestamp()))
    assert result == GtfsImportResult("built", "fetched", f"{copy_name}-{gtfs_name}")
    assert fetch_transit_pointer(settings.routing_root) == result.transit_name
    assert fetch_transit_serves_copy_in_use(settings.routing_root)
    [build] = builds
    assert build["network"] == settings.routing_root / ROUTING_COPIES_NAME / copy_name / "network.osm.pbf"
    assert build["state_at"] == FIRST_COPY_AT
    mjolnir = build["config"]["mjolnir"]
    assert mjolnir["transit_feeds_dir"] == str(build["workspace"] / "transit_feeds")
    assert sorted(path.name for path in (build["workspace"] / "transit_feeds").iterdir()) == ["GTFS_KRK_A", "GTFS_KRK_M", "GTFS_KRK_T"]
    assert dict(fetch_gtfs_copy(settings.routing_root).published_on) == {"GTFS_KRK_T": PUBLISHED_ON, "GTFS_KRK_A": PUBLISHED_ON, "GTFS_KRK_M": PUBLISHED_ON}


def test_a_failed_fetch_keeps_the_earlier_copy_and_builds_the_new_osm_copy_from_it(settings, monkeypatch):
    apply_osm_copy(settings.routing_root, FIRST_COPY_AT)
    apply_fetch_instants(monkeypatch, FIRST_FETCH)
    apply_invented_fetch(monkeypatch)
    builds: list[dict] = []
    apply_invented_build(monkeypatch, builds)
    apply_run(settings)
    kept = fetch_gtfs_copy(settings.routing_root).name
    second_copy = apply_osm_copy(settings.routing_root, SECOND_COPY_AT)
    apply_invented_fetch(monkeypatch, failing_feed="GTFS_KRK_A")
    result = apply_run(settings)
    assert result == GtfsImportResult("built", "failed", f"{second_copy}-{kept}")
    assert fetch_gtfs_copy(settings.routing_root).name == kept
    assert [path.name for path in (settings.routing_root / "gtfs").iterdir() if path.name.startswith(".")] == []
    assert [build["state_at"] for build in builds] == [FIRST_COPY_AT, SECOND_COPY_AT]
    assert fetch_transit_serves_copy_in_use(settings.routing_root)


def test_a_feed_the_rules_refuse_never_becomes_the_copy_in_use(settings, monkeypatch):
    apply_osm_copy(settings.routing_root, FIRST_COPY_AT)
    apply_fetch_instants(monkeypatch, FIRST_FETCH, SECOND_FETCH)
    apply_invented_fetch(monkeypatch)
    builds: list[dict] = []
    apply_invented_build(monkeypatch, builds)
    first = apply_run(settings)
    kept = fetch_gtfs_copy(settings.routing_root).name
    apply_invented_fetch(monkeypatch, refused_feed="GTFS_KRK_M")
    assert apply_run(settings) == GtfsImportResult("reused", "failed", first.transit_name)
    assert fetch_gtfs_copy(settings.routing_root).name == kept
    assert [path.name for path in (settings.routing_root / "gtfs").iterdir() if path.name.startswith(".")] == []
    assert len(builds) == 1


def test_data_of_the_same_copies_is_reused_without_a_build(settings, monkeypatch):
    apply_osm_copy(settings.routing_root, FIRST_COPY_AT)
    apply_fetch_instants(monkeypatch, FIRST_FETCH)
    apply_invented_fetch(monkeypatch)
    builds: list[dict] = []
    apply_invented_build(monkeypatch, builds)
    first = apply_run(settings)
    apply_invented_fetch(monkeypatch, failing_feed="GTFS_KRK_T")
    assert apply_run(settings) == GtfsImportResult("reused", "failed", first.transit_name)
    assert len(builds) == 1


def test_without_a_gtfs_copy_nothing_is_built(settings, monkeypatch):
    apply_osm_copy(settings.routing_root, FIRST_COPY_AT)
    apply_invented_fetch(monkeypatch, failing_feed="GTFS_KRK_M")
    builds: list[dict] = []
    apply_invented_build(monkeypatch, builds)
    assert apply_run(settings) == GtfsImportResult("no_gtfs_copy", "failed", None)
    assert builds == [] and fetch_transit_pointer(settings.routing_root) is None
    assert not fetch_transit_serves_copy_in_use(settings.routing_root)


def test_without_an_osm_copy_in_use_nothing_is_built(settings, monkeypatch):
    apply_fetch_instants(monkeypatch, FIRST_FETCH)
    apply_invented_fetch(monkeypatch)
    builds: list[dict] = []
    apply_invented_build(monkeypatch, builds)
    assert apply_run(settings) == GtfsImportResult("no_osm_copy", "fetched", None)
    assert builds == []


def test_a_failed_build_leaves_no_data_no_preparation_and_the_earlier_pointer(settings, monkeypatch):
    apply_osm_copy(settings.routing_root, FIRST_COPY_AT)
    apply_fetch_instants(monkeypatch, FIRST_FETCH, SECOND_FETCH)
    apply_invented_fetch(monkeypatch)
    apply_invented_build(monkeypatch, [])
    earlier = apply_run(settings).transit_name

    def apply_failed_build(*arguments):
        raise TransitBuildError("Public transport construction tool failed")

    monkeypatch.setattr("service.gtfs_import.apply_transit_build", apply_failed_build)
    with pytest.raises(TransitBuildError):
        apply_run(settings)
    assert fetch_transit_pointer(settings.routing_root) == earlier
    assert sorted(path.name for path in (settings.routing_root / "transit").iterdir()) == sorted([earlier, "current"])


def test_another_run_holding_the_exclusion_gives_skipped(settings, monkeypatch):
    disposed = []

    class InventedEngine:
        """Stand in for the import engine, recording that it was disposed."""

        def dispose(self) -> None:
            disposed.append(True)

    def apply_refused_exclusion(engine, root):
        raise ImportAlreadyRunning("Another import owns database admission")

    monkeypatch.setattr("service.gtfs_import.build_import_engine", lambda timeout: InventedEngine())
    monkeypatch.setattr("service.gtfs_import.apply_import_exclusion", apply_refused_exclusion)
    assert apply_gtfs_import(settings, object(), build_deadline(60, fetch_monotonic_seconds())) == GtfsImportResult("skipped", "not_run", None)
    assert disposed == [True]


def test_the_configuration_of_a_build_with_public_transport_points_every_input_into_the_workspace(tmp_path):
    config = build_transit_valhalla_config(TEMPLATE, tmp_path, tmp_path / "archive.tar")
    assert config["mjolnir"]["tile_dir"] == str(tmp_path / "tiles")
    assert config["mjolnir"]["tile_extract"] == str(tmp_path / "archive.tar")
    assert config["mjolnir"]["transit_dir"] == str(tmp_path / "transit_tiles")
    assert config["mjolnir"]["transit_feeds_dir"] == str(tmp_path / "transit_feeds")
    assert config["mjolnir"]["timezone"] == str(tmp_path / "timezones.sqlite")
    assert TEMPLATE["mjolnir"] == {"tile_dir": "/invented/tiles", "transit_dir": "/invented/transit"}
