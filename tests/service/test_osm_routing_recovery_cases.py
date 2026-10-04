"""Check the decision that recovers the routing pointer before a new import."""

import pytest

from service.osm_routing_recovery import resolve_osm_routing_recovery


@pytest.mark.parametrize(
    ("committed", "pointer", "expected"),
    [
        (None, None, "none"),
        (None, "1791058894", "none"),
        ("1791058894", "1791058894", "none"),
        ("1791058894", None, "publish"),
        ("1791145294", "1791058894", "publish"),
        ("1791058894", "1791145294", "integrity_failure"),
    ],
)
def test_pointer_recovery_decision(committed, pointer, expected):
    assert resolve_osm_routing_recovery(committed, pointer) == expected


def test_names_are_compared_as_instants_not_as_text():
    assert resolve_osm_routing_recovery("1000000000", "999999999") == "publish"
