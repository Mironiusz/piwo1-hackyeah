"""Preserve approved walking semantics while removing Valhalla access restrictions."""

import pytest

from service.osm_routing_tags import build_osm_routing_node_tags, build_osm_routing_way_tags


@pytest.mark.parametrize(("highway", "keeps_area"), (("pedestrian", True), ("footway", False), ("steps", False)))
def test_area_normalization_keeps_only_pedestrian_areas(highway, keeps_area):
    result = build_osm_routing_way_tags({"highway": highway, "area": "yes"})
    assert ("area" in result) == keeps_area
    assert result["foot"] == "yes"


def test_node_barriers_and_access_tags_are_removed():
    assert build_osm_routing_node_tags({"name": "Invented", "ref": "A", "barrier": "bollard", "access": "private", "foot": "no", "wheelchair": "no"}) == {"name": "Invented", "ref": "A"}


def test_non_impassable_smoothness_and_escalator_direction_are_preserved():
    tags = {"highway": "steps", "smoothness": "bad", "conveying": "forward"}
    result = build_osm_routing_way_tags(tags)
    assert result["smoothness"] == "bad"
    assert result["conveying"] == "forward"
    assert "foot" not in tags
