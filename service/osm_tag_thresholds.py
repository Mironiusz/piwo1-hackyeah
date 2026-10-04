"""Keep the specification's pedestrian-network tag lists in one place."""

MOTOR_TRAFFIC_HIGHWAY_VALUES = frozenset(("trunk", "primary", "secondary", "tertiary", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "unclassified", "residential", "service"))
PEDESTRIAN_HIGHWAY_VALUES = frozenset(("footway", "path", "pedestrian", "steps", "living_street", "track", "bridleway", "corridor", "road", "platform", "elevator"))
PERMITTED_FOOT_VALUES = frozenset(("yes", "designated", "permissive", "destination", "delivery", "customers"))
FORBIDDEN_FOOT_VALUES = frozenset(("no", "private", "use_sidepath"))
RESTRICTED_ACCESS_VALUES = frozenset(("no", "private"))
STEEP_INCLINE_THRESHOLD_PERCENT = 6.0
NARROW_PASSAGE_THRESHOLD_WIDTH_M = 0.9
HIGH_KERB_THRESHOLD_HEIGHT_M = 0.03
POOR_SURFACE_VALUES = frozenset(
    ("sett", "unhewn_cobblestone", "cobblestone", "gravel", "pebblestone", "grass", "grass_paver", "dirt", "earth", "ground", "mud", "sand", "rock", "woodchips", "stepping_stones")
)
GOOD_SURFACE_VALUES = frozenset(("asphalt", "concrete", "concrete:plates", "paving_stones", "compacted", "fine_gravel", "metal", "wood", "rubber"))
POOR_SMOOTHNESS_VALUES = frozenset(("bad", "very_bad", "horrible", "very_horrible", "impassable"))
GOOD_SMOOTHNESS_VALUES = frozenset(("excellent", "good", "intermediate"))
NARROW_BARRIER_VALUES = frozenset(("kissing_gate", "turnstile", "stile", "full-height_turnstile"))
LOWERED_KERB_VALUES = frozenset(("lowered", "flush", "no"))
SIDEWALK_PRESENT_VALUES = frozenset(("both", "left", "right", "yes"))
