"""Read only the numeric OSM tag forms approved in the mapping contract."""

import math
import re

OSM_LENGTH_PATTERN = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(?:m)?")
OSM_INCLINE_PATTERN = re.compile(r"([+-]?[0-9]+(?:\.[0-9]+)?)\s*([%\N{DEGREE SIGN}])")
OSM_STEP_COUNT_PATTERN = re.compile(r"[0-9]+")
OSM_STEP_COUNT_MAX = 32767


class OsmTagError(ValueError):
    """Describe a valid source quantity that cannot fit the agreed storage schema."""


def resolve_osm_length_m(value: str | None) -> float | None:
    """Accept nonnegative decimal metres with an optional metre suffix."""
    match = OSM_LENGTH_PATTERN.fullmatch(value) if value is not None else None
    if match is None:
        return None
    result = float(match.group(1))
    return result if math.isfinite(result) else None


def resolve_osm_incline_percent(value: str | None) -> float | None:
    """Accept a signed decimal percent or convert a degree value through its tangent."""
    match = OSM_INCLINE_PATTERN.fullmatch(value) if value is not None else None
    if match is None:
        return None
    result = float(match.group(1))
    if not math.isfinite(result):
        return None
    if match.group(2) != "%":
        result = 100 * math.tan(math.radians(result))
    return result if math.isfinite(result) else None


def resolve_osm_step_count(value: str | None) -> int | None:
    """Keep positive integer counts, refusing values outside the schema's smallint range."""
    if value is None or not OSM_STEP_COUNT_PATTERN.fullmatch(value):
        return None
    digits = value.lstrip("0")
    if not digits:
        return None
    if len(digits) > 5 or (len(digits) == 5 and digits > str(OSM_STEP_COUNT_MAX)):
        raise OsmTagError("Step count exceeds storage range")
    return int(digits)
