"""Check that a GTFS copy is placed and pointed to only when all three feeds are complete, and that a refused one leaves the earlier copy in use."""

import json
import zipfile
import zlib
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from data.gtfs_copy import GTFS_REQUIRED_MEMBERS, GtfsCopyError, apply_gtfs_copy, apply_gtfs_preparation, build_gtfs_feed_path, fetch_gtfs_copy, fetch_gtfs_preparations
from data.gtfs_source import GTFS_FEEDS
from tests.common_gtfs_feed import INVENTED_GTFS_TABLES, apply_invented_gtfs_feed

pytestmark = pytest.mark.integration

DAYS = {"GTFS_KRK_T": date(2026, 10, 2), "GTFS_KRK_A": date(2026, 10, 2), "GTFS_KRK_M": date(2026, 10, 1)}
FIRST_FETCH = datetime(2026, 10, 4, 5, 0, tzinfo=UTC)
SECOND_FETCH = datetime(2026, 10, 4, 6, 0, tzinfo=UTC)


def apply_invented_preparation(root: Path) -> Path:
    """Fill a new preparation with one invented feed file per feed."""
    preparation = apply_gtfs_preparation(root)
    for feed in GTFS_FEEDS:
        apply_invented_gtfs_feed(build_gtfs_feed_path(preparation, feed))
    return preparation


def test_three_complete_feeds_are_placed_and_pointed_to_with_their_days(tmp_path, monkeypatch):
    monkeypatch.setattr("data.gtfs_copy.fetch_utc_now", lambda: FIRST_FETCH)
    preparation = apply_invented_preparation(tmp_path)
    name = apply_gtfs_copy(tmp_path, DAYS, preparation)
    assert name == str(int(FIRST_FETCH.timestamp()))
    assert not preparation.exists()
    assert (tmp_path / "gtfs" / "current").read_text(encoding="ascii") == name + "\n"
    copy = fetch_gtfs_copy(tmp_path)
    assert copy is not None
    assert (copy.name, copy.directory, dict(copy.published_on)) == (name, tmp_path / "gtfs" / name, DAYS)
    assert json.loads((copy.directory / "feeds.json").read_text(encoding="utf-8")) == {"GTFS_KRK_A": "2026-10-02", "GTFS_KRK_M": "2026-10-01", "GTFS_KRK_T": "2026-10-02"}


def test_no_copy_is_read_while_none_was_ever_made(tmp_path):
    assert fetch_gtfs_copy(tmp_path) is None


def apply_missing_required_file(preparation: Path) -> dict[str, date]:
    """Replace one feed with a zip that lacks calendar_dates.txt."""
    path = build_gtfs_feed_path(preparation, "GTFS_KRK_A")
    path.unlink()
    apply_invented_gtfs_feed(path, {name: content for name, content in INVENTED_GTFS_TABLES.items() if name != "calendar_dates.txt"})
    return DAYS


def apply_invalid_zip(preparation: Path) -> dict[str, date]:
    """Replace one feed with bytes that are not a zip."""
    build_gtfs_feed_path(preparation, "GTFS_KRK_M").write_bytes(b"invented bytes, not a zip")
    return DAYS


def apply_missing_feed(preparation: Path) -> dict[str, date]:
    """Remove one feed file and its day, as a fetch that failed for it would leave them."""
    build_gtfs_feed_path(preparation, "GTFS_KRK_T").unlink()
    return {feed: day for feed, day in DAYS.items() if feed != "GTFS_KRK_T"}


def apply_corrupt_compression(preparation: Path) -> dict[str, date]:
    """Replace one feed with a zip whose compressed bytes are damaged while its directory stays readable."""
    path = build_gtfs_feed_path(preparation, "GTFS_KRK_T")
    path.unlink()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(GTFS_REQUIRED_MEMBERS):
            archive.writestr(name, "".join(f"{index},{index * 7919 % 104729}\r\n" for index in range(5000)))
    damaged = bytearray(path.read_bytes())
    for offset in range(60, 90):
        damaged[offset] ^= 0xFF
    path.write_bytes(bytes(damaged))
    return DAYS


@pytest.mark.parametrize("apply_damage", [apply_missing_required_file, apply_invalid_zip, apply_missing_feed, apply_corrupt_compression])
def test_an_incomplete_fetch_leaves_the_earlier_copy_and_its_pointer(tmp_path, monkeypatch, apply_damage: Callable[[Path], dict[str, date]]):
    instants = iter((FIRST_FETCH, SECOND_FETCH))
    monkeypatch.setattr("data.gtfs_copy.fetch_utc_now", lambda: next(instants))
    earlier = apply_gtfs_copy(tmp_path, DAYS, apply_invented_preparation(tmp_path))
    preparation = apply_invented_preparation(tmp_path)
    days = apply_damage(preparation)
    with pytest.raises(GtfsCopyError):
        apply_gtfs_copy(tmp_path, days, preparation)
    copy = fetch_gtfs_copy(tmp_path)
    assert copy is not None and copy.name == earlier
    assert fetch_gtfs_preparations(tmp_path) == (preparation,)
    assert sorted(path.name for path in (tmp_path / "gtfs").iterdir() if not path.name.startswith(".")) == sorted([earlier, "current"])


def test_damaged_compressed_bytes_are_a_named_refusal(tmp_path):
    preparation = apply_invented_preparation(tmp_path)
    apply_corrupt_compression(preparation)
    with pytest.raises(GtfsCopyError) as caught:
        apply_gtfs_copy(tmp_path, DAYS, preparation)
    assert isinstance(caught.value.__cause__, zlib.error)


def test_a_copy_with_incomplete_days_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr("data.gtfs_copy.fetch_utc_now", lambda: FIRST_FETCH)
    name = apply_gtfs_copy(tmp_path, DAYS, apply_invented_preparation(tmp_path))
    (tmp_path / "gtfs" / name / "feeds.json").write_text(json.dumps({"GTFS_KRK_T": "2026-10-02"}), encoding="utf-8")
    with pytest.raises(GtfsCopyError):
        fetch_gtfs_copy(tmp_path)
