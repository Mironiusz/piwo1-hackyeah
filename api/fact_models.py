"""
The requests of the community facts of `docs/product/api_contract.md`, sections Facts and Moderation, as strict Pydantic models.

Each model refuses an unknown field, a missing required field and a value of a wrong type, a string for a number and a
boolean for an integer included, and a type or a verdict outside its closed list; the type is read into `FactType` of the closed lists
with only its own values accepted, so a refused type names the field `type` and nothing else. The shape is all they check; the rules
that tie fields together, such as a step count only for stairs or the order of the corners of a rectangle, belong to
`service/fact_rules.py`. The identifier of a fact in a path is an integer of the range PostgreSQL stores, so a larger one is
refused here instead of reaching the database (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-3).
"""

from typing import Annotated, Literal

from accessibility_db.closed_lists import FactType
from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from api.point_body import PointBody

UUID_PATTERN = r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
FACT_ID_MIN = -(2**63)
FACT_ID_MAX = 2**63 - 1

type FactIdPath = Annotated[int, Path(alias="id", ge=FACT_ID_MIN, le=FACT_ID_MAX)]


class FactAreaRequest(BaseModel):
    """The request of list_facts_in_area: the south-west and the north-east corner of a rectangle."""

    model_config = ConfigDict(extra="forbid", strict=True)
    south_west: PointBody
    north_east: PointBody


class NearbyFactsRequest(BaseModel):
    """The request of find_nearby_facts: the type of the report and its point."""

    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=False)
    fact_type: FactType = Field(alias="type", strict=False)
    point: PointBody


class CreateFactRequest(BaseModel):
    """The request of create_fact: the idempotency key as a UUID with hyphens, the type, the point and the three optional fields."""

    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=False)
    idempotency_key: StrictStr = Field(pattern=UUID_PATTERN)
    fact_type: FactType = Field(alias="type", strict=False)
    point: PointBody
    description: StrictStr | None = None
    step_count: StrictInt | None = None
    geozone_radius_m: StrictInt | None = None


class CastVoteRequest(BaseModel):
    """The request of cast_vote: a confirmation or a denial."""

    model_config = ConfigDict(extra="forbid", strict=True)
    verdict: Literal["confirm", "deny"]
