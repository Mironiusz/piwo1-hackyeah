"""
The answers of the refusals of the community facts of `docs/product/api_contract.md`, sections Facts, Moderation and Errors.

Every refusal goes through `build_error_response`, so it has the one safe envelope; `vote_too_soon` adds the instant of the
next accepted vote and `invalid_request` the paths of the fields outside their rules. A refusal answered with a valid session
still carries the renewed token, which the session middleware adds. `InvalidAnonymousVoterInputError` has no answer here on
purpose: a request without a client IP address is a fault of the transport and ends in the sanitized `internal_error`
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-8, D-11).
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.errors import build_error_response
from service.community_facts import FactNotFlaggableError, FactNotFlaggedError, FactNotFoundError, IdempotencyKeyReusedError, VoteTooSoonError
from service.fact_rules import InvalidFactInputError


def apply_fact_error_handlers(app: FastAPI) -> None:
    """Install the answers of the six refusals of the community facts."""

    async def apply_invalid_fact_input(request: Request, error: Exception) -> JSONResponse:
        """Answer a field outside its rules with the sorted paths of the fields it concerns; another exception is not this handler's and is answered as internal_error."""
        if not isinstance(error, InvalidFactInputError):
            return build_error_response("internal_error", 500)
        return build_error_response("invalid_request", 422, sorted(error.fields))

    async def apply_fact_not_found(request: Request, error: Exception) -> JSONResponse:
        """Answer a missing fact, or a hidden one outside a moderator operation."""
        return build_error_response("fact_not_found", 404)

    async def apply_idempotency_key_reused(request: Request, error: Exception) -> JSONResponse:
        """Answer a key already used for a save with a different content."""
        return build_error_response("idempotency_key_reused", 409)

    async def apply_vote_too_soon(request: Request, error: Exception) -> JSONResponse:
        """Answer a second vote of one calendar day with the midnight from which the next vote is accepted; another exception is answered as internal_error."""
        if not isinstance(error, VoteTooSoonError):
            return build_error_response("internal_error", 500)
        return build_error_response("vote_too_soon", 409, repeat_allowed_at=error.repeat_allowed_at)

    async def apply_fact_not_flaggable(request: Request, error: Exception) -> JSONResponse:
        """Answer a flag of a fact from OpenStreetMap."""
        return build_error_response("fact_not_flaggable", 409)

    async def apply_fact_not_flagged(request: Request, error: Exception) -> JSONResponse:
        """Answer a hiding or a restoration of a fact that is not flagged."""
        return build_error_response("fact_not_flagged", 409)

    app.add_exception_handler(InvalidFactInputError, apply_invalid_fact_input)
    app.add_exception_handler(FactNotFoundError, apply_fact_not_found)
    app.add_exception_handler(IdempotencyKeyReusedError, apply_idempotency_key_reused)
    app.add_exception_handler(VoteTooSoonError, apply_vote_too_soon)
    app.add_exception_handler(FactNotFlaggableError, apply_fact_not_flaggable)
    app.add_exception_handler(FactNotFlaggedError, apply_fact_not_flagged)
