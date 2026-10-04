"""
Scenario tests of the input rules of the community facts and of the boundary of the next vote: radii, step counts,
ordered rectangles, descriptions, canonical keys and the next midnight across both clock changes of 2026
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-4, D-9, S-1).
"""

import hashlib
from datetime import date, timedelta
from uuid import UUID

import pytest
from accessibility_db.closed_lists import FactType

from service.fact_rules import (
    FactArea,
    FactCreationInput,
    InvalidFactInputError,
    build_fact_idempotency_key,
    build_repeat_allowed_at,
    resolve_fact_area,
    resolve_fact_creation_input,
)

BARRIERS = [FactType.STAIRS, FactType.HIGH_KERB, FactType.POOR_SURFACE, FactType.STEEP_INCLINE, FactType.NARROW_PASSAGE]
AMENITIES = [FactType.RAMP, FactType.ELEVATOR, FactType.LOWERED_KERB, FactType.ACCESSIBLE_TOILET, FactType.REST_PLACE, FactType.HANDRAIL_AT_STAIRS]


def build_request(fact_type: FactType = FactType.STAIRS, description: str | None = None, step_count: int | None = None, geozone_radius_m: int | None = None) -> FactCreationInput:
    """Builds a request of create_fact at an invented point of Czyżyny with the given fields."""
    return FactCreationInput(fact_type, 50.0661, 19.9878, description, step_count, geozone_radius_m)


def test_stairs_with_three_steps_keep_every_field() -> None:
    content = resolve_fact_creation_input(build_request(step_count=3, description="Three steps at the side entrance"))
    assert (content.fact_type, content.lat, content.lon, content.step_count, content.geozone_radius_m) == (FactType.STAIRS, 50.0661, 19.9878, 3, None)
    assert content.description == "Three steps at the side entrance"


@pytest.mark.parametrize("step_count", [1, 999])
def test_step_count_at_both_limits_is_accepted(step_count: int) -> None:
    assert resolve_fact_creation_input(build_request(step_count=step_count)).step_count == step_count


@pytest.mark.parametrize("step_count", [0, -1, 1000])
def test_step_count_outside_its_limits_is_refused(step_count: int) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_creation_input(build_request(step_count=step_count))
    assert refusal.value.fields == ("step_count",)


@pytest.mark.parametrize("fact_type", [kind for kind in FactType if kind != FactType.STAIRS])
def test_step_count_of_anything_but_stairs_is_refused(fact_type: FactType) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_creation_input(build_request(fact_type, step_count=3))
    assert refusal.value.fields == ("step_count",)


@pytest.mark.parametrize("fact_type", list(FactType))
def test_every_type_is_a_point_report(fact_type: FactType) -> None:
    assert resolve_fact_creation_input(build_request(fact_type)).fact_type == fact_type


@pytest.mark.parametrize("fact_type", BARRIERS)
@pytest.mark.parametrize("radius", [10, 25, 50, 100])
def test_barrier_geozone_with_every_permitted_radius_is_accepted(fact_type: FactType, radius: int) -> None:
    assert resolve_fact_creation_input(build_request(fact_type, geozone_radius_m=radius)).geozone_radius_m == radius


@pytest.mark.parametrize("radius", [0, 9, 11, 20, 75, 101, 1000, -10])
def test_geozone_radius_off_the_list_is_refused(radius: int) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_creation_input(build_request(FactType.HIGH_KERB, geozone_radius_m=radius))
    assert refusal.value.fields == ("geozone_radius_m",)


@pytest.mark.parametrize("fact_type", AMENITIES)
def test_amenity_geozone_is_refused_by_its_type(fact_type: FactType) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_creation_input(build_request(fact_type, geozone_radius_m=25))
    assert refusal.value.fields == ("type",)


def test_description_loses_the_spaces_at_both_ends_only() -> None:
    assert resolve_fact_creation_input(build_request(description="  Brak poręczy \t ")).description == "Brak poręczy \t"


@pytest.mark.parametrize("description", ["", " ", "     "])
def test_empty_description_becomes_absent(description: str) -> None:
    assert resolve_fact_creation_input(build_request(description=description)).description is None


def test_description_of_500_code_points_after_the_trim_is_accepted() -> None:
    assert resolve_fact_creation_input(build_request(description="  " + "ż" * 500 + "  ")).description == "ż" * 500


@pytest.mark.parametrize("description", ["ż" * 501, "a\x00b", "ab\ud800"])
def test_description_too_long_or_not_storable_is_refused(description: str) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_creation_input(build_request(description=description))
    assert refusal.value.fields == ("description",)


def test_area_with_ordered_corners_is_accepted() -> None:
    assert resolve_fact_area(50.064, 19.983, 50.07, 19.995) == FactArea(south=50.064, west=19.983, north=50.07, east=19.995)


@pytest.mark.parametrize(("south_west_lat", "north_east_lat"), [(50.07, 50.064), (50.07, 50.07)])
def test_area_whose_south_west_corner_is_not_south_is_refused(south_west_lat: float, north_east_lat: float) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_area(south_west_lat, 19.983, north_east_lat, 19.995)
    assert refusal.value.fields == ("south_west.lat", "north_east.lat")


@pytest.mark.parametrize(("south_west_lon", "north_east_lon"), [(19.995, 19.983), (19.99, 19.99)])
def test_area_whose_south_west_corner_is_not_west_is_refused(south_west_lon: float, north_east_lon: float) -> None:
    with pytest.raises(InvalidFactInputError) as refusal:
        resolve_fact_area(50.064, south_west_lon, 50.07, north_east_lon)
    assert refusal.value.fields == ("south_west.lon", "north_east.lon")


def test_idempotency_key_is_the_hash_of_the_operation_and_the_canonical_uuid() -> None:
    key = UUID("6F1C2A9E-0B8D-4C55-9A51-3E2F7D1B9C40")
    expected = hashlib.sha256(b"create_fact:6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40").digest()
    assert build_fact_idempotency_key(key) == expected
    assert len(expected) == 32


def test_idempotency_keys_of_two_uuids_differ() -> None:
    assert build_fact_idempotency_key(UUID(int=1)) != build_fact_idempotency_key(UUID(int=2))


@pytest.mark.parametrize(
    ("cast_on", "midnight", "offset_hours"),
    [
        (date(2026, 10, 4), date(2026, 10, 5), 2),
        (date(2026, 3, 28), date(2026, 3, 29), 1),
        (date(2026, 3, 29), date(2026, 3, 30), 2),
        (date(2026, 10, 24), date(2026, 10, 25), 2),
        (date(2026, 10, 25), date(2026, 10, 26), 1),
        (date(2026, 12, 31), date(2027, 1, 1), 1),
    ],
)
def test_next_vote_starts_at_the_next_midnight_with_its_own_offset(runtime_settings, cast_on: date, midnight: date, offset_hours: int) -> None:
    allowed = build_repeat_allowed_at(cast_on)
    assert (allowed.date(), allowed.hour, allowed.minute, allowed.second, allowed.microsecond) == (midnight, 0, 0, 0, 0)
    assert allowed.utcoffset() == timedelta(hours=offset_hours)
