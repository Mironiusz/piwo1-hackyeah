"""Check the preparation of a GTFS feed for the ingest on invented rows: the exception of O9 for missing accessibility, the value 2 kept and the tram type."""

import csv
import zipfile

import pytest

from service.gtfs_feeds import GtfsFeedError, apply_gtfs_feed_preparation, build_gtfs_route_rows, build_gtfs_stop_rows, build_gtfs_trip_rows
from tests.common_gtfs_feed import INVENTED_GTFS_TABLES, apply_invented_gtfs_feed


def build_stop(stop_id: str, value: str, parent: str = "") -> dict[str, str]:
    """Build one invented stop row with its accessibility and parent station."""
    return {"stop_id": stop_id, "parent_station": parent, "wheelchair_boarding": value}


def test_a_child_stop_without_a_value_inherits_its_station_and_every_other_empty_or_0_becomes_1():
    rows = [
        build_stop("S2", "2"),
        build_stop("S2a", "", "S2"),
        build_stop("S2b", "0", "S2"),
        build_stop("S1", "1"),
        build_stop("S1a", "0", "S1"),
        build_stop("S0", ""),
        build_stop("S0a", "", "S0"),
        build_stop("S9", "0"),
    ]
    assert [row["wheelchair_boarding"] for row in build_gtfs_stop_rows(rows)] == ["2", "2", "2", "1", "1", "1", "1", "1"]


def test_a_stop_value_given_by_the_feed_never_changes():
    rows = [build_stop("S1", "1"), build_stop("S1a", "2", "S1"), build_stop("S2", "2"), build_stop("S2a", "1", "S2")]
    assert [row["wheelchair_boarding"] for row in build_gtfs_stop_rows(rows)] == ["1", "2", "2", "1"]


def test_a_trip_without_a_value_becomes_accessible_and_2_stays():
    rows = [{"trip_id": trip_id, "wheelchair_accessible": value} for trip_id, value in (("T1", ""), ("T2", "0"), ("T3", "1"), ("T4", "2"))]
    assert [row["wheelchair_accessible"] for row in build_gtfs_trip_rows(rows)] == ["1", "1", "1", "2"]


def test_the_tram_service_type_900_becomes_the_tram_type_0_and_other_types_stay():
    rows = [{"route_id": "R1", "route_type": "900"}, {"route_id": "R2", "route_type": "3"}, {"route_id": "R3", "route_type": "0"}]
    assert [row["route_type"] for row in build_gtfs_route_rows(rows)] == ["0", "3", "0"]


def test_an_accessibility_value_outside_the_gtfs_reference_is_refused():
    with pytest.raises(GtfsFeedError):
        build_gtfs_trip_rows([{"trip_id": "T1", "wheelchair_accessible": "3"}])


def read_table(path) -> list[dict[str, str]]:
    """Read a prepared table back as rows."""
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_a_feed_is_unpacked_with_its_tables_rewritten_its_other_files_unchanged_and_a_missing_column_added(tmp_path):
    tables = dict(INVENTED_GTFS_TABLES, **{"stops.txt": "﻿stop_id,stop_name,parent_station\r\nS1,Invented stop,\r\n"})
    source = apply_invented_gtfs_feed(tmp_path / "feed.zip", tables)
    target = tmp_path / "feeds" / "GTFS_KRK_T"
    target.parent.mkdir()
    apply_gtfs_feed_preparation(source, target)
    assert sorted(path.name for path in target.iterdir()) == sorted(tables)
    assert not (target / "stops.txt").read_bytes().startswith(b"\xef\xbb\xbf")
    assert read_table(target / "stops.txt") == [{"stop_id": "S1", "stop_name": "Invented stop", "parent_station": "", "wheelchair_boarding": "1"}]
    assert read_table(target / "trips.txt") == [{"route_id": "R1", "service_id": "SV1", "trip_id": "T1", "wheelchair_accessible": "1"}]
    assert [row["route_type"] for row in read_table(target / "routes.txt")] == ["0", "3"]
    assert (target / "stop_times.txt").read_bytes() == tables["stop_times.txt"].encode("utf-8")


def test_a_member_outside_the_root_of_the_feed_is_refused(tmp_path):
    source = tmp_path / "feed.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("../stops.txt", "stop_id\r\nS1\r\n")
    with pytest.raises(GtfsFeedError):
        apply_gtfs_feed_preparation(source, tmp_path / "GTFS_KRK_T")
    assert not (tmp_path / "stops.txt").exists()


def test_routes_without_a_route_type_are_refused(tmp_path):
    source = apply_invented_gtfs_feed(tmp_path / "feed.zip", dict(INVENTED_GTFS_TABLES, **{"routes.txt": "route_id,route_short_name\r\nR1,1\r\n"}))
    with pytest.raises(GtfsFeedError):
        apply_gtfs_feed_preparation(source, tmp_path / "GTFS_KRK_T")


def test_a_file_that_is_not_a_zip_is_refused(tmp_path):
    source = tmp_path / "feed.zip"
    source.write_bytes(b"invented bytes, not a zip")
    with pytest.raises(GtfsFeedError):
        apply_gtfs_feed_preparation(source, tmp_path / "GTFS_KRK_T")


def test_the_rewritten_table_keeps_a_stop_name_with_a_comma(tmp_path):
    source = apply_invented_gtfs_feed(tmp_path / "feed.zip", dict(INVENTED_GTFS_TABLES, **{"stops.txt": 'stop_id,stop_name\r\nS1,"Invented, stop"\r\n'}))
    apply_gtfs_feed_preparation(source, tmp_path / "GTFS_KRK_T")
    [stop] = read_table(tmp_path / "GTFS_KRK_T" / "stops.txt")
    assert stop["stop_name"] == "Invented, stop"
