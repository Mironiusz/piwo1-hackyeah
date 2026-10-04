"""Check every outcome of one import run and that the pointer changes only after a confirmed commit."""

import asyncio
from contextlib import asynccontextmanager, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from zoneinfo import ZoneInfo

import httpx
import pytest
from accessibility_db.tables import OffsetInstant
from shapely import Polygon

from data.local_lock import ImportAlreadyRunning
from data.osm_copy import OsmCopySnapshot
from data.publication import PublicationOutcomeUnknown, PublicationResult, PublicationRolledBack
from data.routing_data import ROUTING_COPIES_NAME, RoutingDataError, apply_osm_routing_manifest, apply_routing_preparation_directory, build_routing_copy_name, fetch_routing_pointer
from service.osm_acquisition import OsmExtract
from service.osm_import import OsmImportError, OsmImportSettings, apply_osm_import, build_osm_stamp
from service.osm_preparation import OsmPreparedNetwork
from service.osm_publication import OsmPublicationCounts
from service.osm_routing_preparation import OsmPreparedCopy
from service.osm_routing_recovery import OsmRoutingIntegrityError
from service.osm_source_validation import OsmSourceError

OLD_STATE = datetime(2026, 10, 2, tzinfo=UTC)
NEW_STATE = datetime(2026, 10, 3, tzinfo=UTC)
COUNTS = OsmPublicationCounts(3, 2, 4, 5)
INVENTED_BOUNDARY = Polygon(((19.9, 50.0), (20.0, 50.0), (20.0, 50.1), (19.9, 50.0)))


class InventedRun:
    """Replace acquisition, preparation, publication and the database reads of one run, recording the order of steps."""

    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, history: tuple[datetime, ...] = (), source_state: datetime = NEW_STATE):
        self.steps: list[str] = []
        self.routing_root = tmp_path / "routing"
        self.routing_root.mkdir()
        self.settings = OsmImportSettings(tmp_path / "workspace", self.routing_root, tmp_path / "tools", tmp_path / "valhalla.json", ZoneInfo("Europe/Warsaw"))
        self.publication: object = PublicationResult(COUNTS)
        self.commit_outcome: bool | None = None
        lease = SimpleNamespace(engine=SimpleNamespace(connect=self.build_connection), workspace_lease=SimpleNamespace(workspace=tmp_path))
        snapshots = tuple(OsmCopySnapshot(index, OffsetInstant(state, 0), "invented") for index, state in enumerate(sorted(history, reverse=True), 1))
        for state in history:
            self.apply_committed_copy(state)

        @contextmanager
        def apply_exclusion(engine, workspace_root):
            self.steps.append("exclusion")
            try:
                yield lease
            finally:
                self.steps.append("release")

        @asynccontextmanager
        async def fetch_extract(client, directory, deadline):
            self.steps.append("acquisition")
            yield OsmExtract(tmp_path / "source.osm.pbf", "malopolskie-261003.osm.pbf", source_state)

        def apply_routing_preparation(lease, routing_root, network, boundary, state_at, committed_names, template, tool_directory, deadline):
            self.steps.append("routing")
            assert committed_names == frozenset(build_routing_copy_name(state) for state in history)
            return routing_root / ROUTING_COPIES_NAME / build_routing_copy_name(state_at)

        def apply_publication(lease, run_deadline, write):
            self.steps.append("publication")
            if isinstance(self.publication, BaseException):
                raise self.publication
            return self.publication

        monkeypatch.setattr("service.osm_import.build_import_engine", lambda timeout: SimpleNamespace(dispose=lambda: None))
        monkeypatch.setattr("service.osm_import.apply_import_exclusion", apply_exclusion)
        monkeypatch.setattr("service.osm_import.fetch_osm_valhalla_template", lambda path: {"mjolnir": {}})
        monkeypatch.setattr("service.osm_import.fetch_business_now", lambda: datetime(2026, 10, 4, 8, 0, 0, 123456, tzinfo=ZoneInfo("Europe/Warsaw")))
        monkeypatch.setattr("service.osm_import.fetch_osm_copy_history", lambda connection: snapshots)
        monkeypatch.setattr("service.osm_import.fetch_osm_extract", fetch_extract)
        monkeypatch.setattr(
            "service.osm_import.fetch_osm_prepared_copy", lambda path, deadline, zone: self.apply_step("preparation", OsmPreparedCopy(OsmPreparedNetwork((), ()), frozenset(), (), INVENTED_BOUNDARY))
        )
        monkeypatch.setattr("service.osm_import.apply_osm_routing_preparation", apply_routing_preparation)
        monkeypatch.setattr("service.osm_import.apply_publication", apply_publication)
        monkeypatch.setattr("service.osm_import.fetch_osm_commit_outcome", lambda lease, state_at, deadline: self.apply_step("commit_check", self.commit_outcome))

    @contextmanager
    def build_connection(self):
        """Stand in for a short read connection of the exclusion engine."""
        yield object()

    def apply_step(self, name: str, value):
        """Record a step and return its invented result."""
        self.steps.append(name)
        return value

    def apply_committed_copy(self, state: datetime) -> None:
        """Place a complete routing copy of a committed source instant."""
        directory = self.routing_root / ROUTING_COPIES_NAME / build_routing_copy_name(state)
        directory.mkdir(parents=True)
        (directory / "network.osm.pbf").write_bytes(b"network")
        (directory / "valhalla_tiles.tar").write_bytes(b"tiles")
        (directory / "krakow_boundary.wkb").write_bytes(b"boundary")
        apply_osm_routing_manifest(directory, state)

    def apply_run(self):
        """Run the import with an unused HTTP client."""
        return asyncio.run(apply_osm_import(self.settings, cast(httpx.AsyncClient, object())))


def test_first_import_publishes_then_points_at_the_new_copy(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch)
    result = run.apply_run()
    assert (result.outcome, result.state_at, result.counts) == ("updated", NEW_STATE, COUNTS)
    assert run.steps == ["exclusion", "acquisition", "preparation", "routing", "publication", "release"]
    assert fetch_routing_pointer(run.routing_root) == build_routing_copy_name(NEW_STATE)


def test_a_concurrent_run_is_skipped_without_touching_anything(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch)

    class RefusedExclusion:
        """Refuse admission the way a held database admission lock does."""

        def __enter__(self):
            raise ImportAlreadyRunning("Another import owns database admission")

        def __exit__(self, *_):
            return False

    monkeypatch.setattr("service.osm_import.apply_import_exclusion", lambda engine, workspace_root: RefusedExclusion())
    result = run.apply_run()
    assert result.outcome == "skipped" and result.state_at is None
    assert run.steps == [] and fetch_routing_pointer(run.routing_root) is None


def test_the_current_state_is_unchanged_and_nothing_is_prepared(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch, history=(NEW_STATE,))
    (run.routing_root / "current").write_text(build_routing_copy_name(NEW_STATE) + "\n")
    result = run.apply_run()
    assert (result.outcome, result.state_at) == ("unchanged", NEW_STATE)
    assert run.steps == ["exclusion", "acquisition", "release"]


def test_an_older_state_fails_before_preparation(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch, history=(NEW_STATE,), source_state=OLD_STATE)
    (run.routing_root / "current").write_text(build_routing_copy_name(NEW_STATE) + "\n")
    with pytest.raises(OsmSourceError, match="older"):
        run.apply_run()
    assert run.steps == ["exclusion", "acquisition", "release"]


def test_a_missing_pointer_of_the_committed_copy_is_recovered_before_acquisition(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch, history=(NEW_STATE,))
    result = run.apply_run()
    assert result.outcome == "unchanged"
    assert fetch_routing_pointer(run.routing_root) == build_routing_copy_name(NEW_STATE)


def test_incomplete_files_of_the_committed_copy_stop_the_run_before_acquisition(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch, history=(OLD_STATE,))
    (run.routing_root / ROUTING_COPIES_NAME / build_routing_copy_name(OLD_STATE) / "valhalla_tiles.tar").write_bytes(b"other")
    with pytest.raises(OsmRoutingIntegrityError):
        run.apply_run()
    assert run.steps == ["exclusion", "release"]
    assert fetch_routing_pointer(run.routing_root) is None


def test_leftover_preparations_are_removed_before_anything_else(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch)
    leftover = apply_routing_preparation_directory(run.routing_root)
    (leftover / "network.osm.pbf").write_bytes(b"partial")
    run.apply_run()
    assert not leftover.exists()


def test_a_named_refusal_inside_publication_is_reported_by_name_and_the_pointer_is_kept(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch, history=(OLD_STATE,))
    old_name = build_routing_copy_name(OLD_STATE)
    (run.routing_root / "current").write_text(old_name + "\n")

    def apply_refusing_publication(lease, run_deadline, write):
        run.steps.append("publication")
        try:
            write(object())
        except Exception:
            raise PublicationRolledBack("Publication failed before commit") from None

    def apply_refusing_copy(connection, prepared, state_at, filename, made_current_at):
        raise OsmSourceError("Source state is no longer newer than the current copy")

    monkeypatch.setattr("service.osm_import.apply_publication", apply_refusing_publication)
    monkeypatch.setattr("service.osm_import.apply_osm_copy_publication", apply_refusing_copy)
    with pytest.raises(OsmSourceError, match="no longer newer"):
        run.apply_run()
    assert fetch_routing_pointer(run.routing_root) == old_name


def test_a_rollback_keeps_the_previous_pointer(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch, history=(OLD_STATE,))
    (run.routing_root / "current").write_text(build_routing_copy_name(OLD_STATE) + "\n")
    run.publication = PublicationRolledBack("Publication deadline expired")
    with pytest.raises(PublicationRolledBack):
        run.apply_run()
    assert fetch_routing_pointer(run.routing_root) == build_routing_copy_name(OLD_STATE)


@pytest.mark.parametrize(("committed", "outcome", "pointer"), [(None, "commit_unknown", None), (True, "updated", NEW_STATE)])
def test_a_lost_commit_confirmation_is_settled_before_the_pointer(tmp_path, monkeypatch, committed, outcome, pointer):
    run = InventedRun(tmp_path, monkeypatch)
    run.publication = PublicationOutcomeUnknown("Commit outcome is unknown")
    run.commit_outcome = committed
    result = run.apply_run()
    assert (result.outcome, result.counts) == (outcome, None)
    assert run.steps[-2:] == ["commit_check", "release"]
    assert fetch_routing_pointer(run.routing_root) == (None if pointer is None else build_routing_copy_name(pointer))


def test_a_copy_proven_absent_after_a_lost_confirmation_is_a_failure(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch)
    run.publication = PublicationOutcomeUnknown("Commit outcome is unknown")
    run.commit_outcome = False
    with pytest.raises(OsmImportError):
        run.apply_run()
    assert fetch_routing_pointer(run.routing_root) is None


def test_a_pointer_failure_after_commit_reports_incomplete_routing_not_a_rollback(tmp_path, monkeypatch):
    run = InventedRun(tmp_path, monkeypatch)

    def apply_failed_pointer(root, name):
        raise RoutingDataError("Cannot publish routing pointer")

    monkeypatch.setattr("service.osm_import.apply_routing_pointer", apply_failed_pointer)
    result = run.apply_run()
    assert (result.outcome, result.counts) == ("routing_incomplete", COUNTS)


def test_server_stamp_is_cut_to_the_stored_millisecond():
    assert build_osm_stamp(datetime(2026, 10, 4, 8, 0, 0, 123456, tzinfo=UTC)) == datetime(2026, 10, 4, 8, 0, 0, 123000, tzinfo=UTC)
