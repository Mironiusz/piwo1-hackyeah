"""
The three moderator operations of `docs/product/api_contract.md`, section Moderation.

Each needs a valid token of an account that holds the moderator role at the moment of the request: without a token it is
refused with `authentication_required`, with a token of an ordinary account with `moderator_role_required`, and the role is
read again on every request, so a removed role takes effect on the next one (M11). A moderator sees hidden facts, and no
answer carries anything about who flagged a fact (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-2, D-7).
"""

from fastapi import APIRouter, Depends, FastAPI

from api.fact_body import build_flagged_fact_body, build_flagged_facts_body
from api.fact_models import FactIdPath
from api.sessions import fetch_moderator_actor
from common_time import fetch_business_now
from service.community_facts import apply_fact_hiding, apply_fact_restoration, fetch_flagged_facts

MODERATION_ROUTER = APIRouter()


@MODERATION_ROUTER.get("/api/moderation/flagged-facts", name="list_flagged_facts", dependencies=[Depends(fetch_moderator_actor)])
def list_flagged_facts() -> dict[str, object]:
    """Answer every flagged fact, hidden ones included, the latest flag first."""
    return build_flagged_facts_body(fetch_flagged_facts())


@MODERATION_ROUTER.post("/api/moderation/flagged-facts/{id}/hide", name="hide_fact", dependencies=[Depends(fetch_moderator_actor)])
def hide_fact(fact_id: FactIdPath) -> dict[str, object]:
    """Hide a flagged fact and answer its moderator item, also when it was already hidden."""
    return build_flagged_fact_body(apply_fact_hiding(fact_id, fetch_business_now()))


@MODERATION_ROUTER.post("/api/moderation/flagged-facts/{id}/restore", name="restore_fact", dependencies=[Depends(fetch_moderator_actor)])
def restore_fact(fact_id: FactIdPath) -> dict[str, object]:
    """Restore a flagged fact with the votes it kept and answer its moderator item, also when it was not hidden."""
    return build_flagged_fact_body(apply_fact_restoration(fact_id))


def apply_moderation_routes(app: FastAPI) -> None:
    """Register the three moderator operations; their refusals are answered by the handlers of the community facts and of the sessions."""
    app.include_router(MODERATION_ROUTER)
