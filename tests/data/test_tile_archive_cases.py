"""Check the file operations of the tile step on a temporary directory: the chunked digest, the copy into a temporary file, the placement and the removal of leftovers."""

import hashlib
import logging
import stat
import sys
from pathlib import Path

import pytest

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from data.tile_archive import (
    TILE_FILE_CHUNK_BYTES,
    TILE_FILE_MODE,
    TILE_TEMPORARY_PREFIX,
    TileFileError,
    apply_tile_file_copy,
    apply_tile_file_placement,
    apply_tile_leftover_removal,
    fetch_tile_directory_presence,
    fetch_tile_file_digest,
)

INVENTED_ARCHIVE = bytes(range(256)) * (TILE_FILE_CHUNK_BYTES * 5 // 512)
EXPIRED_AFTER_FIRST_CHUNK = Deadline(100.0)


def build_open_deadline() -> Deadline:
    """Give a deadline far enough away that no test reaches it."""
    return build_deadline(60, fetch_monotonic_seconds())


def build_link(link: Path, target: Path) -> None:
    """Create a symbolic link, skipping the test on a machine that refuses to create one."""
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("This machine refuses to create a symbolic link")


def apply_expiry_after_first_chunk(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stand in for the monotonic clock so the first chunk passes EXPIRED_AFTER_FIRST_CHUNK and every later chunk finds it expired."""
    readings = iter([0.0])
    monkeypatch.setattr("data.tile_archive.fetch_monotonic_seconds", lambda: next(readings, 200.0))


def fetch_temporary_files(directory: Path) -> list[Path]:
    """List the files of the directory that carry the temporary prefix of the step."""
    return [entry for entry in directory.iterdir() if entry.name.startswith(TILE_TEMPORARY_PREFIX)]


def test_the_digest_of_a_regular_file_is_its_sha256(tmp_path):
    """Read the digest of a file of more than one chunk and find the value hashlib gives for its bytes."""
    path = tmp_path / "krakow.pmtiles"
    path.write_bytes(INVENTED_ARCHIVE)
    assert fetch_tile_file_digest(path, build_open_deadline()) == hashlib.sha256(INVENTED_ARCHIVE).hexdigest()


def test_a_missing_path_and_a_directory_have_no_digest(tmp_path):
    """Treat a missing path and a directory as no file."""
    assert fetch_tile_file_digest(tmp_path / "missing.pmtiles", build_open_deadline()) is None
    assert fetch_tile_file_digest(tmp_path, build_open_deadline()) is None


def test_a_link_has_no_digest_even_to_a_regular_file(tmp_path):
    """Treat a link as no file, so the step never reads through one."""
    target = tmp_path / "target.pmtiles"
    target.write_bytes(INVENTED_ARCHIVE)
    link = tmp_path / "krakow.pmtiles"
    build_link(link, target)
    assert fetch_tile_file_digest(link, build_open_deadline()) is None


def test_an_expired_deadline_stops_the_digest(tmp_path):
    """Refuse to read a file once the run deadline has passed."""
    path = tmp_path / "krakow.pmtiles"
    path.write_bytes(INVENTED_ARCHIVE)
    with pytest.raises(DeadlineExpiredError):
        fetch_tile_file_digest(path, Deadline(fetch_monotonic_seconds() - 1))


def test_the_copy_writes_the_same_bytes_into_a_temporary_file_of_the_directory(tmp_path):
    """Copy the source into a file of the directory with the temporary prefix and the same bytes."""
    source = tmp_path / "krakow.pmtiles"
    source.write_bytes(INVENTED_ARCHIVE)
    served = tmp_path / "served"
    served.mkdir()
    temporary = apply_tile_file_copy(source, served, build_open_deadline())
    assert temporary.parent == served
    assert temporary.name.startswith(TILE_TEMPORARY_PREFIX)
    assert temporary.read_bytes() == INVENTED_ARCHIVE


@pytest.mark.skipif(sys.platform == "win32", reason="Windows keeps no read permission bits for others")
def test_the_copy_is_readable_by_everyone_and_writable_only_by_its_owner(tmp_path):
    """Give the copy the mode a proxy running as another user can read, since a temporary file starts readable by its owner alone."""
    source = tmp_path / "krakow.pmtiles"
    source.write_bytes(INVENTED_ARCHIVE)
    served = tmp_path / "served"
    served.mkdir()
    temporary = apply_tile_file_copy(source, served, build_open_deadline())
    assert stat.S_IMODE(temporary.stat().st_mode) == TILE_FILE_MODE == 0o644


def test_a_deadline_expiring_during_the_copy_leaves_no_temporary_file(tmp_path, monkeypatch):
    """Stop a copy of three chunks after its first chunk and find no partial file left behind."""
    source = tmp_path / "krakow.pmtiles"
    source.write_bytes(INVENTED_ARCHIVE)
    served = tmp_path / "served"
    served.mkdir()
    apply_expiry_after_first_chunk(monkeypatch)
    with pytest.raises(DeadlineExpiredError):
        apply_tile_file_copy(source, served, EXPIRED_AFTER_FIRST_CHUNK)
    assert fetch_temporary_files(served) == []


def test_a_partial_file_that_cannot_be_removed_does_not_hide_an_expired_deadline(tmp_path, monkeypatch, caplog):
    """Keep the expired deadline as the failure of the copy when its partial file cannot be removed, and log that the file was left for the next run."""
    source = tmp_path / "krakow.pmtiles"
    source.write_bytes(INVENTED_ARCHIVE)
    served = tmp_path / "served"
    served.mkdir()
    apply_expiry_after_first_chunk(monkeypatch)

    def apply_refused_removal(path):
        raise TileFileError("Cannot remove tile archive file")

    monkeypatch.setattr("data.tile_archive.apply_tile_file_removal", apply_refused_removal)
    application = logging.getLogger("piwo1-hackyeah")
    monkeypatch.setattr(application, "handlers", [caplog.handler])
    with pytest.raises(DeadlineExpiredError):
        apply_tile_file_copy(source, served, EXPIRED_AFTER_FIRST_CHUNK)
    assert [record.getMessage() for record in caplog.records] == ["Tile archive temporary file was left for the next run"]


def test_a_copy_of_a_missing_source_fails_and_leaves_no_temporary_file(tmp_path):
    """Refuse to copy a source that is not there, with the constant failure and no partial file."""
    served = tmp_path / "served"
    served.mkdir()
    with pytest.raises(TileFileError) as caught:
        apply_tile_file_copy(tmp_path / "missing.pmtiles", served, build_open_deadline())
    assert str(caught.value) == "Cannot copy tile archive file"
    assert fetch_temporary_files(served) == []


def test_the_placement_replaces_the_target_with_the_temporary_file(tmp_path):
    """Put the temporary file under the served name over an earlier file, leaving the temporary name empty."""
    target = tmp_path / "krakow.pmtiles"
    target.write_bytes(b"earlier archive")
    temporary = tmp_path / (TILE_TEMPORARY_PREFIX + "invented")
    temporary.write_bytes(INVENTED_ARCHIVE)
    apply_tile_file_placement(temporary, target)
    assert target.read_bytes() == INVENTED_ARCHIVE
    assert not temporary.exists()


def test_leftover_removal_removes_only_the_temporary_files(tmp_path):
    """Remove the two temporary files of interrupted runs and keep the archive and an unrelated file."""
    for name in (TILE_TEMPORARY_PREFIX + "first", TILE_TEMPORARY_PREFIX + "second", "krakow.pmtiles", "readme.txt"):
        (tmp_path / name).write_bytes(b"invented")
    assert apply_tile_leftover_removal(tmp_path) == 2
    assert sorted(entry.name for entry in tmp_path.iterdir()) == ["krakow.pmtiles", "readme.txt"]


def test_directory_presence_is_true_only_for_a_directory(tmp_path):
    """Find a directory present, and a missing path and a file absent."""
    file = tmp_path / "krakow.pmtiles"
    file.write_bytes(b"invented")
    assert fetch_tile_directory_presence(tmp_path) is True
    assert fetch_tile_directory_presence(tmp_path / "missing") is False
    assert fetch_tile_directory_presence(file) is False
