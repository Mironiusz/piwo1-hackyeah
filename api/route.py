"""Accept plan_route, refuse a request outside its contract and answer the planned route or a contracted refusal."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import APIRouter, FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, field_validator

from api.errors import build_error_response
from api.fact_body import build_fact_body
from api.point_body import PointBody
from service.route_graph import RoutePoint, build_route_graph_at_start
from service.route_planning import PlannedRoute, PointOutsideKrakowError, RouteAnswer, resolve_route
from service.route_segments import RouteFactView, RoutingUnavailableError

type BarrierType = Literal["stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"]
type AmenityType = Literal["ramp", "elevator", "lowered_kerb", "accessible_toilet", "rest_place", "handrail_at_stairs"]

router = APIRouter()


class RouteRequestBody(BaseModel):
    """The request of plan_route: two points and the barrier and amenity types of the profile, each at most once."""

    model_config = ConfigDict(extra="forbid", strict=True)
    start: PointBody
    destination: PointBody
    avoid: list[BarrierType]
    need: list[AmenityType]

    @field_validator("avoid", "need")
    @classmethod
    def apply_unique_type_validation(cls, value: list[str]) -> list[str]:
        """Refuse a type repeated in avoid or need."""
        if len(set(value)) != len(value):
            raise ValueError("repeated_type")
        return value


def build_route_fact_body(item: RouteFactView) -> dict[str, object]:
    """Build a route fact: the fields of a fact with its distance from the start and whether OpenStreetMap overrules it."""
    return {**build_fact_body(item.view), "distance_from_start_m": item.distance_from_start_m, "is_overruled_by_osm": item.is_overruled_by_osm}


def build_planned_route_body(route: PlannedRoute) -> dict[str, object]:
    """Build a route of the contract with its segments in order and the three groups of its list."""
    return {
        "length_m": route.length_m,
        "segments": [
            {
                "line": [[lon, lat] for lon, lat in segment.line],
                "length_m": segment.length_m,
                "state": segment.state.value,
                "missing_attributes": [attribute.value for attribute in segment.missing_attributes],
                "is_marked_wheelchair_no": segment.is_marked_wheelchair_no,
            }
            for segment in route.segments
        ],
        "profile_barriers": [build_route_fact_body(item) for item in route.profile_barriers],
        "additional_barriers": [build_route_fact_body(item) for item in route.additional_barriers],
        "amenities": [build_route_fact_body(item) for item in route.amenities],
    }


def build_route_answer_body(answer: RouteAnswer) -> dict[str, object]:
    """Build the response 200 of plan_route."""
    alternative = answer.alternative
    return {
        "osm_copy_date": answer.osm_copy_date.isoformat(),
        "barrier_free_route_exists": answer.barrier_free_route_exists,
        "route": build_planned_route_body(answer.route),
        "alternative": None
        if alternative is None
        else {"route": build_planned_route_body(alternative.route), "avoided_barriers": [build_route_fact_body(item) for item in alternative.avoided_barriers]},
    }


@router.post("/api/routes", name="plan_route")
def plan_route(body: RouteRequestBody) -> dict[str, object]:
    """Plan a walking route without a token; nothing of the request is stored or logged beyond the request log entry."""
    answer = resolve_route(RoutePoint(body.start.lat, body.start.lon), RoutePoint(body.destination.lat, body.destination.lon), frozenset(body.avoid), frozenset(body.need))
    return build_route_answer_body(answer)


def apply_route_routes(app: FastAPI) -> None:
    """Register plan_route and the answers of its two refusals, routing_unavailable and point_outside_krakow."""

    async def apply_routing_unavailable(request: Request, error: Exception) -> JSONResponse:
        """Answer that no route can be computed right now, with no route."""
        return build_error_response("routing_unavailable", 503)

    async def apply_point_outside_krakow(request: Request, error: Exception) -> JSONResponse:
        """Answer which chosen points lie outside Kraków."""
        points = error.points if isinstance(error, PointOutsideKrakowError) else ()
        return build_error_response("point_outside_krakow", 422, points=points)

    app.include_router(router)
    app.add_exception_handler(RoutingUnavailableError, apply_routing_unavailable)
    app.add_exception_handler(PointOutsideKrakowError, apply_point_outside_krakow)


@asynccontextmanager
async def apply_route_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the graph of the copy in use in the thread pool when the process starts."""
    await run_in_threadpool(build_route_graph_at_start)
    yield
