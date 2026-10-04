"""Select the pedestrian network under M2 of the product specification."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

from service import osm_tag_thresholds as thresholds

type BarrierState = Literal["present", "absent", "absent_by_default", "unknown"]


@dataclass(frozen=True)
class WayFacts:
    """Keep network attributes separate from the present facts that may be published."""

    stairs_state: BarrierState
    poor_surface_state: BarrierState
    steep_incline_state: BarrierState
    narrow_passage_state: BarrierState
    is_marked_wheelchair_no: bool
    is_motor_traffic: bool
    is_crossing: bool
    step_count: int | None
    fact_types: frozenset[str]


@dataclass(frozen=True)
class NodeFacts:
    """Describe a network node's kerb, crossing membership and present facts."""

    kerb_point: Literal["high", "lowered", "unknown"] | None
    is_crossing: bool
    is_on_motor_traffic_way: bool
    step_count: int | None
    fact_types: frozenset[str]


def resolve_is_pedestrian_network_way(tags: Mapping[str, str]) -> bool:
    """Require an allowed highway and apply pedestrian access and separate-sidewalk exclusions."""
    highway = tags.get("highway")
    foot = tags.get("foot")
    is_motor_traffic_way = highway in thresholds.MOTOR_TRAFFIC_HIGHWAY_VALUES
    is_allowed_highway = highway in thresholds.PEDESTRIAN_HIGHWAY_VALUES or is_motor_traffic_way or (highway == "cycleway" and foot in thresholds.PERMITTED_FOOT_VALUES)
    if not is_allowed_highway or foot in thresholds.FORBIDDEN_FOOT_VALUES or tags.get("motorroad") == "yes":
        return False
    if tags.get("access") in thresholds.RESTRICTED_ACCESS_VALUES and foot not in thresholds.PERMITTED_FOOT_VALUES:
        return False
    return not (is_motor_traffic_way and (tags.get("sidewalk") == "separate" or tags.get("sidewalk:both") == "separate"))


def resolve_osm_consensus(states: tuple[BarrierState, ...]) -> BarrierState:
    """Keep conflicting explicit presence and absence unknown rather than inventing certainty."""
    known = set(states) - {"unknown"}
    if "present" in known and "absent" in known:
        return "unknown"
    if "present" in known:
        return "present"
    if "absent" in known:
        return "absent"
    return "unknown"


def resolve_osm_boolean_tag(value: str | None) -> BarrierState:
    """Read only the explicit yes and no values of an amenity tag."""
    return "present" if value == "yes" else "absent" if value == "no" else "unknown"


def resolve_osm_handrail_state(tags: Mapping[str, str]) -> BarrierState:
    """Allow a handrail on either side, keeping a contradictory overall tag unknown."""
    side_values = tuple(tags[key] for key in ("handrail:left", "handrail:right", "handrail:center") if key in tags)
    side_state: BarrierState = "present" if "yes" in side_values else "absent" if side_values and all(value == "no" for value in side_values) else "unknown"
    return resolve_osm_consensus((resolve_osm_boolean_tag(tags.get("handrail")), side_state))


def resolve_osm_surface_state(tags: Mapping[str, str]) -> BarrierState:
    """Let a provided smoothness value decide, retaining unlisted values as unknown."""
    if "smoothness" in tags:
        smoothness = tags["smoothness"]
        return "present" if smoothness in thresholds.POOR_SMOOTHNESS_VALUES else "absent" if smoothness in thresholds.GOOD_SMOOTHNESS_VALUES else "unknown"
    value = tags.get("surface")
    return "present" if value in thresholds.POOR_SURFACE_VALUES else "absent" if value in thresholds.GOOD_SURFACE_VALUES else "unknown"


def resolve_osm_amenity_states(tags: Mapping[str, str], element_type: Literal["node", "way", "relation"]) -> Mapping[str, BarrierState]:
    """Classify the non-kerb amenities without turning unknown or contradictory tags into facts."""
    states: dict[str, BarrierState] = {"ramp": "unknown", "elevator": "unknown", "accessible_toilet": "unknown", "rest_place": "unknown", "handrail_at_stairs": "unknown"}
    is_steps = element_type == "way" and tags.get("highway") == "steps"
    if is_steps or (element_type == "node" and "entrance" in tags):
        states["ramp"] = resolve_osm_consensus(tuple(resolve_osm_boolean_tag(tags.get(key)) for key in ("ramp", "ramp:wheelchair")))
    if element_type == "node" and tags.get("highway") == "elevator":
        states["elevator"] = "present"
    toilet_states: tuple[BarrierState, ...] = (resolve_osm_boolean_tag(tags.get("toilets:wheelchair")),)
    if tags.get("amenity") == "toilets":
        wheelchair = tags.get("wheelchair")
        toilet_states += ("present" if wheelchair in ("yes", "designated") else "absent" if wheelchair in ("no", "limited") else "unknown",)
    states["accessible_toilet"] = resolve_osm_consensus(toilet_states)
    is_rest_place = tags.get("amenity") == "bench" or tags.get("leisure") == "picnic_table"
    is_stop_or_shelter = tags.get("highway") == "bus_stop" or tags.get("public_transport") == "platform" or tags.get("amenity") == "shelter"
    if is_rest_place or is_stop_or_shelter:
        states["rest_place"] = resolve_osm_consensus(("present" if is_rest_place else "unknown", resolve_osm_boolean_tag(tags.get("bench"))))
    if is_steps:
        states["handrail_at_stairs"] = resolve_osm_handrail_state(tags)
    return MappingProxyType(states)


def resolve_osm_way_surface_tags(tags: Mapping[str, str]) -> Mapping[str, str]:
    """Select the explicit sidewalk keys or carriageway keys required by M6."""
    if tags.get("highway") not in thresholds.MOTOR_TRAFFIC_HIGHWAY_VALUES:
        return tags
    sidewalk_values = (tags.get("sidewalk"), tags.get("sidewalk:both"))
    has_sidewalk = any(value in thresholds.SIDEWALK_PRESENT_VALUES for value in sidewalk_values)
    no_sidewalk = sidewalk_values[0] in ("no", "none") or sidewalk_values[1] == "no"
    if has_sidewalk and no_sidewalk:
        return MappingProxyType({})
    if no_sidewalk:
        return tags
    if has_sidewalk:
        selected: dict[str, str] = {}
        for quantity in ("surface", "smoothness", "width"):
            values = {tags[key] for key in ("sidewalk:" + quantity, "sidewalk:both:" + quantity) if key in tags}
            if len(values) == 1:
                selected[quantity] = next(iter(values))
            elif values:
                selected[quantity] = "conflicting"
        return MappingProxyType(selected)
    return MappingProxyType({})


def resolve_way_facts(tags: Mapping[str, str]) -> WayFacts:
    """Map a selected network way into barrier states, flags and only present facts."""
    from service.osm_tag_values import resolve_osm_incline_percent, resolve_osm_length_m, resolve_osm_step_count

    stairs: BarrierState = "present" if tags.get("highway") == "steps" else "absent_by_default"
    surface_tags = resolve_osm_way_surface_tags(tags)
    surface = resolve_osm_surface_state(surface_tags)
    incline = resolve_osm_incline_percent(tags.get("incline"))
    incline_state: BarrierState = "unknown" if incline is None else "present" if abs(incline) > thresholds.STEEP_INCLINE_THRESHOLD_PERCENT else "absent"
    width = resolve_osm_length_m(surface_tags.get("width"))
    narrow: BarrierState = "unknown" if width is None else "present" if width < thresholds.NARROW_PASSAGE_THRESHOLD_WIDTH_M else "absent"
    facts = {kind for kind, state in (("stairs", stairs), ("poor_surface", surface), ("steep_incline", incline_state), ("narrow_passage", narrow)) if state == "present"}
    facts.update(kind for kind, state in resolve_osm_amenity_states(tags, "way").items() if state == "present")
    return WayFacts(
        stairs,
        surface,
        incline_state,
        narrow,
        tags.get("wheelchair") == "no",
        tags.get("highway") in thresholds.MOTOR_TRAFFIC_HIGHWAY_VALUES,
        any(tags.get(key) == "crossing" for key in ("footway", "path", "cycleway")),
        resolve_osm_step_count(tags.get("step_count")) if stairs == "present" else None,
        frozenset(facts),
    )


def resolve_node_facts(tags: Mapping[str, str], is_on_motor_traffic_way: bool) -> NodeFacts:
    """Map a node of the pedestrian network, excluding boarding-edge kerbs."""
    from service.osm_tag_values import resolve_osm_length_m, resolve_osm_step_count

    is_stop = tags.get("highway") == "bus_stop" or tags.get("public_transport") in ("platform", "stop_position") or tags.get("railway") in ("platform", "tram_stop")
    has_kerb = not is_stop and ("kerb" in tags or "kerb:height" in tags or tags.get("barrier") == "kerb")
    kerb_point: Literal["high", "lowered", "unknown"] | None = None
    facts = {kind for kind, state in resolve_osm_amenity_states(tags, "node").items() if state == "present"}
    if has_kerb:
        height = resolve_osm_length_m(tags.get("kerb:height"))
        height_state: BarrierState = "unknown" if height is None else "present" if height > thresholds.HIGH_KERB_THRESHOLD_HEIGHT_M else "absent"
        kerb_value = tags.get("kerb")
        value_state: BarrierState = "present" if kerb_value == "raised" else "absent" if kerb_value in thresholds.LOWERED_KERB_VALUES else "unknown"
        state = resolve_osm_consensus((height_state, value_state))
        kerb_point = "high" if state == "present" else "lowered" if state == "absent" else "unknown"
        if kerb_point != "unknown":
            facts.add("high_kerb" if kerb_point == "high" else "lowered_kerb")
    is_step = tags.get("barrier") == "step"
    if is_step:
        facts.add("stairs")
    if tags.get("barrier") in thresholds.NARROW_BARRIER_VALUES:
        facts.add("narrow_passage")
    return NodeFacts(kerb_point, tags.get("highway") == "crossing", is_on_motor_traffic_way, resolve_osm_step_count(tags.get("step_count")) if is_step else None, frozenset(facts))
