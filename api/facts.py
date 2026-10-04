"""
The six public operations of the community facts of `docs/product/api_contract.md`, section Facts.

Every operation takes an optional token: without the header `Authorization` the person has no account, and a token that
does not resolve is refused with `session_expired` before anything is read or written, never handled as a person without an
account. Only a save and a vote of a person without an account read the address and the User-Agent of the request, to derive
the identity the service hashes. Each endpoint is a plain `def`, so FastAPI runs it in its thread pool while the service
waits for the database; its route is named after the operation of the contract, so the request log names it and nothing
of the request (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-2, D-7).
"""

from typing import Annotated
from uuid import UUID

from accessibility_db.closed_lists import VoteVerdict
from fastapi import APIRouter, Depends, FastAPI, Request, Response

from api.fact_body import build_area_facts_body, build_fact_item_body, build_nearby_facts_body
from api.fact_errors import apply_fact_error_handlers
from api.fact_identity import fetch_anonymous_voter_input
from api.fact_models import CastVoteRequest, CreateFactRequest, FactAreaRequest, FactIdPath, NearbyFactsRequest
from api.sessions import fetch_request_session
from common_time import fetch_business_now
from service.actors import SessionResolution
from service.community_facts import FactActor, apply_fact_creation, apply_fact_flag, apply_fact_vote, fetch_fact, fetch_facts_in_area, fetch_nearby_facts
from service.fact_rules import FactCreationInput, resolve_fact_area

FACTS_ROUTER = APIRouter()


def fetch_fact_actor(request: Request, resolution: SessionResolution) -> FactActor:
    """Give the account of the session, or for a person without an account the two inputs of their identity."""
    return resolution.actor if resolution.actor is not None else fetch_anonymous_voter_input(request)


@FACTS_ROUTER.post("/api/facts/in-area", name="list_facts_in_area", dependencies=[Depends(fetch_request_session)])
def list_facts_in_area(body: FactAreaRequest) -> dict[str, object]:
    """Answer the visible facts of a rectangle, at most 1000, and whether it holds more."""
    area = resolve_fact_area(body.south_west.lat, body.south_west.lon, body.north_east.lat, body.north_east.lon)
    return build_area_facts_body(fetch_facts_in_area(area))


@FACTS_ROUTER.get("/api/facts/{id}", name="read_fact", dependencies=[Depends(fetch_request_session)])
def read_fact(fact_id: FactIdPath) -> dict[str, object]:
    """Answer one fact that is not hidden, in any status."""
    return build_fact_item_body(fetch_fact(fact_id))


@FACTS_ROUTER.post("/api/facts/nearby", name="find_nearby_facts", dependencies=[Depends(fetch_request_session)])
def find_nearby_facts(body: NearbyFactsRequest) -> dict[str, object]:
    """Answer the visible facts of the type within 15 m of the point, nearest first."""
    return build_nearby_facts_body(fetch_nearby_facts(body.fact_type, body.point.lat, body.point.lon))


@FACTS_ROUTER.post("/api/facts", name="create_fact", status_code=201)
def create_fact(body: CreateFactRequest, request: Request, response: Response, resolution: Annotated[SessionResolution, Depends(fetch_request_session)]) -> dict[str, object]:
    """Save a report or a geozone with the confirmation of its author, answering 201 for the first save and 200 for a repeated one."""
    fact_request = FactCreationInput(body.fact_type, body.point.lat, body.point.lon, body.description, body.step_count, body.geozone_radius_m)
    result = apply_fact_creation(fact_request, UUID(body.idempotency_key), fetch_fact_actor(request, resolution), fetch_business_now())
    if not result.is_created:
        response.status_code = 200
    return build_fact_item_body(result.view)


@FACTS_ROUTER.post("/api/facts/{id}/votes", name="cast_vote", status_code=201)
def cast_vote(fact_id: FactIdPath, body: CastVoteRequest, request: Request, resolution: Annotated[SessionResolution, Depends(fetch_request_session)]) -> dict[str, object]:
    """Store a confirmation or a denial and answer the fact with its status after the vote."""
    return build_fact_item_body(apply_fact_vote(fact_id, VoteVerdict(body.verdict), fetch_fact_actor(request, resolution)))


@FACTS_ROUTER.post("/api/facts/{id}/flag", name="flag_fact", status_code=204, dependencies=[Depends(fetch_request_session)])
def flag_fact(fact_id: FactIdPath) -> Response:
    """Flag a report, a geozone or a converted fact without recording who flagged it, and answer without a body."""
    apply_fact_flag(fact_id, fetch_business_now())
    return Response(status_code=204)


def apply_fact_routes(app: FastAPI) -> None:
    """Register the six public operations of the community facts and the answers of their refusals."""
    apply_fact_error_handlers(app)
    app.include_router(FACTS_ROUTER)
