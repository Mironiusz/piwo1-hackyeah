"""Check one tile step on temporary directories with an invented archive standing in for the recorded one: loading, repeat, replacement, every failure, the exclusion and the deadline."""

import hashlib
import tempfile
from collections.abc import Callable
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path

import pytest

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from data.local_lock import ImportAlreadyRunning
from data.tile_archive import TILE_TEMPORARY_PREFIX
from service.tile_archive import TILE_ARCHIVE_NAME, TileArchiveError, TileArchiveResult, TileArchiveSettings, apply_tile_archive, apply_tile_archive_run

pytestmark = pytest.mark.integration

INVENTED_ARCHIVE = (bytes(range(256)) * 7813)[:2000000]
EARLIER_FILE = b"an earlier file of another value"


@dataclass(frozen=True)
class InventedPlaces:
    """Hold the settings of one run and the tmp_path they lie in."""

    settings: TileArchiveSettings
    root: Path

    @property
    def target(self) -> Path:
        """Give the served name of the archive."""
        return self.settings.served_directory / TILE_ARCHIVE_NAME


@pytest.fixture
def places(tmp_path, monkeypatch) -> InventedPlaces:
    """Put the invented archive into a source directory, create an empty served directory and make the invented archive the recorded one."""
    source = tmp_path / "source" / TILE_ARCHIVE_NAME
    source.parent.mkdir()
    source.write_bytes(INVENTED_ARCHIVE)
    served = tmp_path / "served"
    served.mkdir()
    monkeypatch.setattr("service.tile_archive.TILE_ARCHIVE_SHA256", hashlib.sha256(INVENTED_ARCHIVE).hexdigest())
    return InventedPlaces(TileArchiveSettings(source, served), tmp_path)


def build_open_deadline() -> Deadline:
    """Give a deadline far enough away that no test reaches it."""
    return build_deadline(60, fetch_monotonic_seconds())


def fetch_served_state(places: InventedPlaces) -> dict[str, bytes]:
    """Read every file of the served directory with its bytes, so a test can say the directory is as before."""
    return {entry.name: entry.read_bytes() for entry in places.settings.served_directory.iterdir()}


def apply_failed_run(settings: TileArchiveSettings, deadline: Deadline) -> TileArchiveError:
    """Run the step expecting a failure and return it."""
    with pytest.raises(TileArchiveError) as caught:
        apply_tile_archive_run(settings, deadline)
    return caught.value


def test_a_first_run_loads_the_archive_and_leaves_no_temporary_file(places):
    """AC-1: with the archive in the source place and nothing served, one run puts the checked archive under the served name and nothing else."""
    assert apply_tile_archive_run(places.settings, build_open_deadline()) == TileArchiveResult("loaded")
    assert hashlib.sha256(places.target.read_bytes()).hexdigest() == hashlib.sha256(INVENTED_ARCHIVE).hexdigest()
    assert [entry.name for entry in places.settings.served_directory.iterdir()] == [TILE_ARCHIVE_NAME]


def test_a_copy_that_cannot_be_synced_keeps_the_earlier_served_file(places, monkeypatch):
    """AC-2: a copy that fails after part of it was written ends as copy_failed, with the earlier file still served and no temporary file."""
    places.target.write_bytes(EARLIER_FILE)

    def apply_refused_sync(descriptor):
        raise OSError("invented sync failure")

    monkeypatch.setattr("data.tile_archive.os.fsync", apply_refused_sync)
    assert apply_failed_run(places.settings, build_open_deadline()).reason == "copy_failed"
    assert fetch_served_state(places) == {TILE_ARCHIVE_NAME: EARLIER_FILE}


def test_a_deadline_expiring_during_the_copy_keeps_the_earlier_served_file(places, monkeypatch):
    """AC-2: a copy stopped by the run deadline ends as deadline_expired, with the earlier file still served and no temporary file."""
    places.target.write_bytes(EARLIER_FILE)

    def apply_expired_copy(source, directory, deadline):
        raise DeadlineExpiredError("Elapsed-time budget exhausted")

    monkeypatch.setattr("service.tile_archive.apply_tile_file_copy", apply_expired_copy)
    assert apply_failed_run(places.settings, build_open_deadline()).reason == "deadline_expired"
    assert fetch_served_state(places) == {TILE_ARCHIVE_NAME: EARLIER_FILE}


def test_a_repeat_with_the_archive_in_place_writes_nothing_and_needs_no_source(places):
    """AC-3: with the recorded archive served and the source removed, a run gives unchanged and leaves the served file untouched."""
    places.target.write_bytes(INVENTED_ARCHIVE)
    places.settings.source_path.unlink()
    before = places.target.stat()
    assert apply_tile_archive_run(places.settings, build_open_deadline()) == TileArchiveResult("unchanged")
    after = places.target.stat()
    assert (after.st_mtime_ns, after.st_ino) == (before.st_mtime_ns, before.st_ino)


def test_a_served_file_of_another_value_is_replaced_by_the_archive(places):
    """AC-4: with another file under the served name, a run puts the recorded archive there and reports loaded."""
    places.target.write_bytes(EARLIER_FILE)
    assert apply_tile_archive_run(places.settings, build_open_deadline()) == TileArchiveResult("loaded")
    assert fetch_served_state(places) == {TILE_ARCHIVE_NAME: INVENTED_ARCHIVE}


def apply_removed_source(places: InventedPlaces, monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove the source file."""
    places.settings.source_path.unlink()


def apply_shortened_source(places: InventedPlaces, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cut the source short to 1 000 000 bytes, as an interrupted upload leaves it."""
    places.settings.source_path.write_bytes(INVENTED_ARCHIVE[:1000000])


def apply_changed_byte_source(places: InventedPlaces, monkeypatch: pytest.MonkeyPatch) -> None:
    """Change one byte of the source, keeping its size."""
    changed = bytearray(INVENTED_ARCHIVE)
    changed[1000] ^= 0xFF
    places.settings.source_path.write_bytes(bytes(changed))


def apply_mismatched_copy(places: InventedPlaces, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stand in for the copy with one that writes other bytes into a temporary file of the served directory."""

    def apply_other_bytes(source, directory, deadline):
        with tempfile.NamedTemporaryFile(mode="wb", dir=directory, prefix=TILE_TEMPORARY_PREFIX, delete=False) as stream:
            stream.write(EARLIER_FILE)
        return Path(stream.name)

    monkeypatch.setattr("service.tile_archive.apply_tile_file_copy", apply_other_bytes)


@pytest.mark.parametrize(
    ("prepare", "reason"),
    [
        (apply_removed_source, "source_missing"),
        (apply_shortened_source, "source_mismatch"),
        (apply_changed_byte_source, "source_mismatch"),
        (apply_mismatched_copy, "copy_mismatch"),
    ],
)
def test_a_broken_input_fails_with_its_reason_and_leaves_the_served_name_as_it_was(places, monkeypatch, prepare: Callable[[InventedPlaces, pytest.MonkeyPatch], None], reason: str):
    """AC-5: each broken input ends the run with its fixed reason, the served directory as before, no temporary file and no path in the message."""
    places.target.write_bytes(EARLIER_FILE)
    prepare(places, monkeypatch)
    failure = apply_failed_run(places.settings, build_open_deadline())
    assert failure.reason == reason
    assert fetch_served_state(places) == {TILE_ARCHIVE_NAME: EARLIER_FILE}
    assert str(places.root) not in str(failure)


def test_a_source_inside_the_served_directory_is_refused(places):
    """Refuse a source placed inside the served directory, because the proxy would serve it before any check."""
    settings = TileArchiveSettings(places.settings.served_directory / "incoming" / TILE_ARCHIVE_NAME, places.settings.served_directory)
    assert apply_failed_run(settings, build_open_deadline()).reason == "places_overlap"


def test_a_missing_served_directory_is_refused(places):
    """Refuse to create the served directory, which belongs to the proxy configuration, not to the step."""
    settings = TileArchiveSettings(places.settings.source_path, places.root / "missing")
    assert apply_failed_run(settings, build_open_deadline()).reason == "served_directory_missing"
    assert not (places.root / "missing").exists()


class InventedEngine:
    """Stand in for the import engine, recording that it was disposed."""

    def __init__(self) -> None:
        """Start with no disposal recorded."""
        self.disposed = False

    def dispose(self) -> None:
        """Record the disposal."""
        self.disposed = True


def test_a_run_holding_the_exclusion_makes_the_step_skip_without_writing(places, monkeypatch):
    """AC-7: while another run holds the exclusion the step gives skipped at once, writes nothing and disposes its engine."""
    engine = InventedEngine()

    def apply_refused_exclusion(engine, root):
        raise ImportAlreadyRunning("Another import owns database admission")

    monkeypatch.setattr("service.tile_archive.build_import_engine", lambda timeout: engine)
    monkeypatch.setattr("service.tile_archive.apply_import_exclusion", apply_refused_exclusion)
    assert apply_tile_archive(places.settings, places.root / "workspace", build_open_deadline()) == TileArchiveResult("skipped")
    assert fetch_served_state(places) == {}
    assert engine.disposed


def test_an_admitted_run_loads_the_archive_and_disposes_its_engine(places, monkeypatch):
    """AC-7: with the exclusion admitted the step loads the archive and disposes its engine."""
    engine = InventedEngine()
    monkeypatch.setattr("service.tile_archive.build_import_engine", lambda timeout: engine)
    monkeypatch.setattr("service.tile_archive.apply_import_exclusion", lambda engine, root: nullcontext(object()))
    assert apply_tile_archive(places.settings, places.root / "workspace", build_open_deadline()) == TileArchiveResult("loaded")
    assert fetch_served_state(places) == {TILE_ARCHIVE_NAME: INVENTED_ARCHIVE}
    assert engine.disposed


def test_an_expired_deadline_ends_the_run_with_the_served_directory_as_before(places):
    """AC-8: a run past its deadline ends as deadline_expired and writes nothing."""
    places.target.write_bytes(EARLIER_FILE)
    assert apply_failed_run(places.settings, Deadline(fetch_monotonic_seconds() - 1)).reason == "deadline_expired"
    assert fetch_served_state(places) == {TILE_ARCHIVE_NAME: EARLIER_FILE}
