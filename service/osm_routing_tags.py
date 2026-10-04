"""Normalize an already selected pedestrian network for Valhalla's walking tiles."""

from collections.abc import Mapping

ROUTING_NODE_TAG_KEYS = frozenset(("name", "ref"))


def build_osm_routing_way_tags(tags: Mapping[str, str]) -> dict[str, str]:
    """Apply the approved walking-network transformation without mutating source tags."""
    result = {key: value for key, value in tags.items() if key not in ("access", "sac_scale") and not key.startswith("foot:") and not key.endswith(":conditional")}
    result["foot"] = "yes"
    if result.get("smoothness") == "impassable":
        del result["smoothness"]
    if result.get("area") == "yes" and result.get("highway") != "pedestrian":
        del result["area"]
    return result


def build_osm_routing_node_tags(tags: Mapping[str, str]) -> dict[str, str]:
    """Keep only node name and reference tags, excluding barrier and access interpretations."""
    return {key: value for key, value in tags.items() if key in ROUTING_NODE_TAG_KEYS}
