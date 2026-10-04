"""
The four account operations of `docs/product/api_contract.md`, section Accounts, and the answers of their refusals.

`create_account` and `log_in` take no token and ignore the header `Authorization`; `log_in` gives the token of the new
session in `Session-Token`. `read_own_account` and `delete_own_account` need a token, and `delete_own_account` answers
`204` without `Session-Token`, because the account it renewed the token of no longer exists.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictStr

from api.errors import build_error_response
from api.sessions import SessionTokenMiddleware, apply_session_error_handlers, apply_session_token, fetch_account_actor
from common_time import fetch_business_now, fetch_utc_now
from service.account_rules import InvalidAccountInputError
from service.accounts import AccountView, InvalidCredentialsError, PseudonymTakenError, apply_account_creation, apply_account_deletion, resolve_login
from service.actors import AccountActor

ACCOUNTS_ROUTER = APIRouter()


class AccountCredentialsRequest(BaseModel):
    """A pseudonym and a password, both strings, with no other field."""

    model_config = ConfigDict(extra="forbid")
    pseudonym: StrictStr
    password: StrictStr


class CreateAccountRequest(AccountCredentialsRequest):
    """The request of create_account."""


class LogInRequest(AccountCredentialsRequest):
    """The request of log_in."""


def build_account_body(account: AccountView) -> dict[str, object]:
    """Build the body with the shared object Account of the contract."""
    return {"account": {"pseudonym": account.pseudonym, "is_moderator": account.is_moderator}}


@ACCOUNTS_ROUTER.post("/api/accounts", name="create_account", status_code=201)
def create_account(body: CreateAccountRequest) -> dict[str, object]:
    """Register an ordinary account without logging it in."""
    return build_account_body(apply_account_creation(body.pseudonym, body.password, fetch_business_now()))


@ACCOUNTS_ROUTER.post("/api/sessions", name="log_in")
def log_in(body: LogInRequest, request: Request) -> dict[str, object]:
    """Log an account in and give the token of its new session in `Session-Token`."""
    result = resolve_login(body.pseudonym, body.password, fetch_utc_now())
    apply_session_token(request, result.session_token)
    return build_account_body(result.account)


@ACCOUNTS_ROUTER.get("/api/accounts/me", name="read_own_account")
def read_own_account(actor: Annotated[AccountActor, Depends(fetch_account_actor)]) -> dict[str, object]:
    """Give the pseudonym and the current moderator role of the account of the session."""
    return build_account_body(AccountView(pseudonym=actor.pseudonym, is_moderator=actor.is_moderator))


@ACCOUNTS_ROUTER.delete("/api/accounts/me", name="delete_own_account", status_code=204)
def delete_own_account(request: Request, actor: Annotated[AccountActor, Depends(fetch_account_actor)]) -> Response:
    """Delete the account of the session and answer without a body and without a renewed token."""
    apply_account_deletion(actor)
    apply_session_token(request, None)
    return Response(status_code=204)


def apply_account_routes(app: FastAPI) -> None:
    """Register the account operations, the answers of their refusals, the session refusals and the header of the renewed token."""

    async def apply_invalid_account_input(request: Request, error: Exception) -> JSONResponse:
        """Answer a pseudonym or a password outside its rules with its field; any other exception is not this handler's and is raised again."""
        if not isinstance(error, InvalidAccountInputError):
            raise error
        return build_error_response("invalid_request", 422, [error.field])

    async def apply_pseudonym_taken(request: Request, error: Exception) -> JSONResponse:
        """Answer a pseudonym an account already has up to letter case."""
        return build_error_response("pseudonym_taken", 409)

    async def apply_invalid_credentials(request: Request, error: Exception) -> JSONResponse:
        """Answer a failed login without saying why it failed."""
        return build_error_response("invalid_credentials", 401)

    apply_session_error_handlers(app)
    app.include_router(ACCOUNTS_ROUTER)
    app.add_exception_handler(InvalidAccountInputError, apply_invalid_account_input)
    app.add_exception_handler(PseudonymTakenError, apply_pseudonym_taken)
    app.add_exception_handler(InvalidCredentialsError, apply_invalid_credentials)
    app.add_middleware(SessionTokenMiddleware)
