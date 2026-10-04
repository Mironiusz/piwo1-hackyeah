"""Check M6 mapping, numeric boundaries and the approved unknown-on-conflict rule."""

import math

import pytest

from service import osm_tag_thresholds as thresholds
from service.osm_tag_rule import resolve_node_facts, resolve_osm_amenity_states, resolve_way_facts
from service.osm_tag_values import OsmTagError, resolve_osm_incline_percent, resolve_osm_length_m, resolve_osm_step_count


@pytest.mark.parametrize(("value", "expected"), (("0.9", 0.9), ("0.4m", 0.4), ("0.03 m", 0.03), ("0", 0.0), ("0,9", None), ("3 ft", None), ("1;2", None), ("-1", None), ("nan", None)))
def test_lengths_accept_only_approved_metre_forms(value, expected):
    assert resolve_osm_length_m(value) == expected


@pytest.mark.parametrize(("value", "expected"), (("6%", 6.0), ("-6.1 %", -6.1), ("+6%", 6.0), ("45\N{DEGREE SIGN}", 100.0), ("up", None), ("down", None), ("6", None), ("6,1%", None), ("6%;7%", None)))
def test_inclines_accept_only_explicit_units(value, expected):
    actual = resolve_osm_incline_percent(value)
    if expected is None:
        assert actual is None
    else:
        assert actual == pytest.approx(expected)


@pytest.mark.parametrize(("value", "expected"), (("1", 1), ("003", 3), ("32767", 32767), ("0", None), ("-1", None), ("3.0", None), ("3;4", None)))
def test_step_count_keeps_only_positive_integers(value, expected):
    assert resolve_osm_step_count(value) == expected


@pytest.mark.parametrize("value", ("32768", "999999999999999999999999999999999999999999"))
def test_step_count_overflow_fails_the_import(value):
    with pytest.raises(OsmTagError):
        resolve_osm_step_count(value)


@pytest.mark.parametrize(("incline", "expected"), (("6%", "absent"), ("6.1%", "present"), ("-6.1%", "present"), ("up", "unknown")))
def test_incline_threshold_applies_in_both_directions(incline, expected):
    assert resolve_way_facts({"highway": "path", "incline": incline}).steep_incline_state == expected


@pytest.mark.parametrize(("width", "expected"), (("0.9", "absent"), ("0.89", "present"), ("1 ft", "unknown")))
def test_width_threshold_and_unknown_units(width, expected):
    assert resolve_way_facts({"highway": "path", "width": width}).narrow_passage_state == expected


@pytest.mark.parametrize("value", tuple(thresholds.POOR_SURFACE_VALUES))
def test_each_poor_surface_is_present(value):
    result = resolve_way_facts({"highway": "path", "surface": value})
    assert result.poor_surface_state == "present"
    assert "poor_surface" in result.fact_types


@pytest.mark.parametrize("value", tuple(thresholds.GOOD_SURFACE_VALUES))
def test_each_good_surface_is_an_attribute_without_a_fact(value):
    result = resolve_way_facts({"highway": "path", "surface": value})
    assert result.poor_surface_state == "absent"
    assert "poor_surface" not in result.fact_types


def test_smoothness_precedence_retains_unlisted_values_as_unknown():
    assert resolve_way_facts({"highway": "path", "surface": "asphalt", "smoothness": "bad"}).poor_surface_state == "present"
    assert resolve_way_facts({"highway": "path", "surface": "gravel", "smoothness": "good"}).poor_surface_state == "absent"
    assert resolve_way_facts({"highway": "path", "surface": "asphalt", "smoothness": "unlisted"}).poor_surface_state == "unknown"


def test_missing_tags_do_not_create_confirmed_absence_or_facts():
    result = resolve_way_facts({"highway": "path"})
    assert result.stairs_state == "absent_by_default"
    assert (result.poor_surface_state, result.steep_incline_state, result.narrow_passage_state) == ("unknown", "unknown", "unknown")
    assert not result.fact_types


def test_motor_traffic_attributes_require_known_sidewalk_context():
    tags = {"highway": "residential", "surface": "asphalt", "width": "5", "incline": "7%"}
    result = resolve_way_facts(tags)
    assert result.is_motor_traffic
    assert result.poor_surface_state == result.narrow_passage_state == "unknown"
    assert result.steep_incline_state == "present"
    assert resolve_way_facts(tags | {"sidewalk": "no"}).poor_surface_state == "absent"
    result = resolve_way_facts(tags | {"sidewalk": "yes", "sidewalk:surface": "gravel", "sidewalk:width": "0.8"})
    assert result.poor_surface_state == result.narrow_passage_state == "present"
    assert resolve_way_facts(tags | {"sidewalk": "yes", "sidewalk:surface": "gravel", "sidewalk:both:surface": "asphalt"}).poor_surface_state == "unknown"


@pytest.mark.parametrize(("height", "expected"), (("0.03", "lowered"), ("0.031", "high"), ("rolled", "unknown")))
def test_kerb_threshold(height, expected):
    assert resolve_node_facts({"kerb:height": height}, False).kerb_point == expected


def test_conflicting_kerb_assertions_are_unknown_without_opposite_facts():
    result = resolve_node_facts({"kerb": "raised", "kerb:height": "0.01"}, True)
    assert result.kerb_point == "unknown"
    assert not result.fact_types
    assert result.is_on_motor_traffic_way


@pytest.mark.parametrize("tags", ({"highway": "bus_stop"}, {"public_transport": "platform"}, {"public_transport": "stop_position"}, {"railway": "platform"}, {"railway": "tram_stop"}))
def test_stop_boarding_edges_do_not_create_pedestrian_kerb_facts(tags):
    result = resolve_node_facts(tags | {"kerb": "raised"}, True)
    assert result.kerb_point is None
    assert "high_kerb" not in result.fact_types


def test_stairs_and_narrow_node_barriers_keep_separate_identity_rules():
    assert resolve_node_facts({"barrier": "step", "step_count": "2"}, False).fact_types == frozenset(("stairs",))
    assert resolve_node_facts({"barrier": "turnstile"}, False).fact_types == frozenset(("narrow_passage",))
    result = resolve_way_facts({"highway": "steps", "step_count": "4", "ramp": "yes", "handrail": "yes"})
    assert result.step_count == 4
    assert result.fact_types == frozenset(("stairs", "ramp", "handrail_at_stairs"))


def test_conflicting_ramp_and_toilet_tags_never_create_amenity_facts():
    ramp = resolve_way_facts({"highway": "steps", "ramp": "yes", "ramp:wheelchair": "no"})
    assert "ramp" not in ramp.fact_types
    states = resolve_osm_amenity_states({"amenity": "toilets", "wheelchair": "no", "toilets:wheelchair": "yes"}, "node")
    assert states["accessible_toilet"] == "unknown"


def test_elevator_is_only_a_node_amenity():
    assert resolve_osm_amenity_states({"highway": "elevator"}, "node")["elevator"] == "present"
    assert resolve_osm_amenity_states({"highway": "elevator"}, "way")["elevator"] == "unknown"
    assert resolve_osm_amenity_states({"highway": "elevator"}, "relation")["elevator"] == "unknown"


def test_thresholds_are_read_from_the_single_rule_module(monkeypatch):
    monkeypatch.setattr(thresholds, "STEEP_INCLINE_THRESHOLD_PERCENT", 8)
    assert resolve_way_facts({"highway": "path", "incline": "7%"}).steep_incline_state == "absent"


def test_unknown_numeric_values_are_finite_or_missing():
    assert resolve_osm_length_m("9" * 400) is None
    assert resolve_osm_incline_percent("9" * 400 + "%") is None
    assert math.isfinite(resolve_osm_incline_percent("3\N{DEGREE SIGN}"))
