"""The one point object of `docs/product/api_contract.md`, section Conventions, shared by every operation that takes a point."""

from pydantic import BaseModel, ConfigDict, Field


class PointBody(BaseModel):
    """A point in degrees of WGS 84; a string for a number or a coordinate outside its range is refused."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
