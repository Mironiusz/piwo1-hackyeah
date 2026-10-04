"""
The input rules of the community facts and the boundary of the next vote (M3 - M5 of the specification).

A report or a geozone is checked and normalized here before anything is stored: a step count belongs only to stairs and
is from 1 to 999, a geozone is a barrier with a radius of 10, 25, 50 or 100 m, and a description loses the spaces U+0020
at both ends, becomes absent when nothing is left and holds at most 500 code points that text in UTF-8 and PostgreSQL can
carry. A rectangle of the map has its south-west corner strictly south and west of its north-east corner. Every refusal
names the paths of the request fields it concerns (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-4).

The key of a save is the SHA-256 hash of the text `create_fact:` followed by the canonical form of the UUID of the
request, as `docs/product/schema.md` defines `idempotency_key`. The next vote of a person is accepted from the midnight
that starts the calendar day after the day of the stored vote, in the business zone, with the offset in force at that
midnight; it is calendar arithmetic, not 24 hours added to an instant (D-9).
"""

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from accessibility_db.closed_lists import FactType

from data.community_facts import FactContent
from service.route_segments import BARRIER_TYPES

DESCRIPTION_MAX_LENGTH = 500
STEP_COUNT_MIN = 1
STEP_COUNT_MAX = 999
GEOZONE_RADII_M = frozenset({10, 25, 50, 100})
AREA_FACT_LIMIT = 1000
NEARBY_FACT_DISTANCE_M = 15.0
FACT_IDEMPOTENCY_KEY_PREFIX = "create_fact:"


class InvalidFactInputError(Exception):
    """A field of a request of the community facts outside its rules; `fields` names the paths of the request fields it concerns."""

    def __init__(self, *fields: str) -> None:
        super().__init__(*fields)
        self.fields = fields


@dataclass(frozen=True)
class FactCreationInput:
    """A report or a geozone as the request of create_fact carries it, before its rules are checked."""

    fact_type: FactType
    lat: float
    lon: float
    description: str | None
    step_count: int | None
    geozone_radius_m: int | None


@dataclass(frozen=True)
class FactArea:
    """A rectangle of the map in degrees of WGS 84, its south-west corner strictly south and west of its north-east one."""

    south: float
    west: float
    north: float
    east: float


def resolve_fact_creation_input(request: FactCreationInput) -> FactContent:
    """Gives the normalized content of a report or a geozone, or refuses the first field outside its rules with `InvalidFactInputError`."""
    if request.geozone_radius_m is not None and request.geozone_radius_m not in GEOZONE_RADII_M:
        raise InvalidFactInputError("geozone_radius_m")
    if request.geozone_radius_m is not None and request.fact_type not in BARRIER_TYPES:
        raise InvalidFactInputError("type")
    if request.step_count is not None and (request.fact_type != FactType.STAIRS or not STEP_COUNT_MIN <= request.step_count <= STEP_COUNT_MAX):
        raise InvalidFactInputError("step_count")
    return FactContent(
        fact_type=request.fact_type,
        lat=request.lat,
        lon=request.lon,
        description=resolve_description(request.description),
        step_count=request.step_count,
        geozone_radius_m=request.geozone_radius_m,
    )


def resolve_description(raw: str | None) -> str | None:
    """Trims the spaces U+0020 at both ends of a description and gives None for nothing left, or refuses a description that is too long or cannot be stored."""
    if raw is None:
        return None
    description = raw.strip(" ")
    if len(description) > DESCRIPTION_MAX_LENGTH or "\x00" in description:
        raise InvalidFactInputError("description")
    try:
        description.encode("utf-8")
    except UnicodeEncodeError as error:
        raise InvalidFactInputError("description") from error
    return description or None


def resolve_fact_area(south_west_lat: float, south_west_lon: float, north_east_lat: float, north_east_lon: float) -> FactArea:
    """Gives the rectangle of two corners, or refuses corners that are not strictly south and west of each other, naming both coordinates at fault."""
    if south_west_lat >= north_east_lat:
        raise InvalidFactInputError("south_west.lat", "north_east.lat")
    if south_west_lon >= north_east_lon:
        raise InvalidFactInputError("south_west.lon", "north_east.lon")
    return FactArea(south=south_west_lat, west=south_west_lon, north=north_east_lat, east=north_east_lon)


def build_fact_idempotency_key(key: UUID) -> bytes:
    """Builds the 32 bytes stored as the idempotency key of a save: SHA-256 of `create_fact:` and the UUID in 36 lowercase characters with hyphens."""
    return hashlib.sha256(f"{FACT_IDEMPOTENCY_KEY_PREFIX}{key}".encode("ascii")).digest()


def build_repeat_allowed_at(cast_on: date) -> datetime:
    """Builds the midnight in the business zone that starts the calendar day after `cast_on`, from which the next vote of the person is accepted."""
    from config.config import BUSINESS_TIMEZONE

    return datetime.combine(cast_on + timedelta(days=1), time(0), tzinfo=ZoneInfo(BUSINESS_TIMEZONE))
