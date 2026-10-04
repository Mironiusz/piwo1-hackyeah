"""
The closed lists of the target schema as enumerations.

Each enumeration mirrors one text domain of `docs/product/schema.md` with the same values in the same order, so the
code uses these members instead of writing the values as text. A critical test compares every enumeration with the
check of its domain in the stored data.
"""

from enum import StrEnum


class FactType(StrEnum):
    """The type of a fact: the barriers and the amenities of M3 of the specification (domain `fact_type`)."""

    STAIRS = "stairs"
    HIGH_KERB = "high_kerb"
    POOR_SURFACE = "poor_surface"
    STEEP_INCLINE = "steep_incline"
    NARROW_PASSAGE = "narrow_passage"
    RAMP = "ramp"
    ELEVATOR = "elevator"
    LOWERED_KERB = "lowered_kerb"
    ACCESSIBLE_TOILET = "accessible_toilet"
    REST_PLACE = "rest_place"
    HANDRAIL_AT_STAIRS = "handrail_at_stairs"


class FactSource(StrEnum):
    """The source a fact shows (domain `fact_source`)."""

    OPENSTREETMAP = "openstreetmap"
    USER_REPORT = "user_report"


class OsmElementType(StrEnum):
    """The type of the OpenStreetMap element a fact comes from (domain `osm_element_type`)."""

    NODE = "node"
    WAY = "way"
    RELATION = "relation"


class WayBarrierState(StrEnum):
    """The state the tag rules of M6 give a barrier on a way (domain `way_barrier_state`)."""

    PRESENT = "present"
    ABSENT = "absent"
    ABSENT_BY_DEFAULT = "absent_by_default"
    UNKNOWN = "unknown"


class KerbPointState(StrEnum):
    """The kerb at a node of a way (domain `kerb_point_state`)."""

    HIGH = "high"
    LOWERED = "lowered"
    UNKNOWN = "unknown"


class VoteVerdict(StrEnum):
    """A confirmation that a fact is still there or a denial that it is (domain `vote_verdict`)."""

    CONFIRM = "confirm"
    DENY = "deny"
