"""Check copy directory names, the routing pointer and the handling of unpublished routing directories."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from data.routing_data import (
    ROUTING_COPIES_NAME,
    ROUTING_POINTER_NAME,
    RoutingDataError,
    apply_routing_copy_placement,
    apply_routing_directory_removal,
    apply_routing_pointer,
    apply_routing_preparation_directory,
    build_routing_copy_name,
    fetch_routing_pointer,
    fetch_routing_preparations,
)


def test_copy_name_is_the_instant_in_whole_epoch_seconds_whatever_its_offset():
    assert build_routing_copy_name(datetime(2026, 10, 2, 20, 21, 34, tzinfo=UTC)) == "1790972494"
    assert build_routing_copy_name(datetime(2026, 10, 2, 22, 21, 34, tzinfo=timezone(timedelta(hours=2)))) == "1790972494"


def test_copy_name_refuses_a_naive_instant_and_a_fraction_of_a_second():
    with pytest.raises(RoutingDataError):
        build_routing_copy_name(datetime(2026, 10, 2, 20, 21, 34))
    with pytest.raises(RoutingDataError):
        build_routing_copy_name(datetime(2026, 10, 2, 20, 21, 34, 5, tzinfo=UTC))


def test_pointer_is_absent_until_published_and_is_replaced_whole(tmp_path):
    assert fetch_routing_pointer(tmp_path) is None
    apply_routing_pointer(tmp_path, "1791058894")
    assert (tmp_path / ROUTING_POINTER_NAME).read_text(encoding="ascii") == "1791058894\n"
    apply_routing_pointer(tmp_path, "1791145294")
    assert fetch_routing_pointer(tmp_path) == "1791145294"
    assert sorted(entry.name for entry in tmp_path.iterdir()) == [ROUTING_POINTER_NAME]


def test_pointer_refuses_an_invalid_name_and_invalid_content(tmp_path):
    with pytest.raises(RoutingDataError):
        apply_routing_pointer(tmp_path, "../1791058894")
    (tmp_path / ROUTING_POINTER_NAME).write_text("copies/1791058894\n", encoding="ascii")
    with pytest.raises(RoutingDataError):
        fetch_routing_pointer(tmp_path)


def test_preparations_are_listed_and_never_mistaken_for_copies(tmp_path):
    assert fetch_routing_preparations(tmp_path) == ()
    preparation = apply_routing_preparation_directory(tmp_path)
    (tmp_path / ROUTING_COPIES_NAME / "1791058894").mkdir()
    assert fetch_routing_preparations(tmp_path) == (preparation,)
    apply_routing_directory_removal(preparation)
    assert fetch_routing_preparations(tmp_path) == ()


def test_placement_moves_a_preparation_but_never_replaces_a_copy(tmp_path):
    preparation = apply_routing_preparation_directory(tmp_path)
    (preparation / "manifest.json").write_text("{}")
    target = apply_routing_copy_placement(preparation, tmp_path, "1791058894")
    assert target == tmp_path / ROUTING_COPIES_NAME / "1791058894"
    assert (target / "manifest.json").exists() and not preparation.exists()
    second = apply_routing_preparation_directory(tmp_path)
    with pytest.raises(RoutingDataError):
        apply_routing_copy_placement(second, tmp_path, "1791058894")
    assert (target / "manifest.json").exists() and second.exists()
