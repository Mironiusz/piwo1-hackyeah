"""
The session of a request at the boundary of the programming interface (`docs/product/api_contract.md`, section Sessions and actors).

An operation that admits a person without an account depends on `fetch_request_session`, one that needs an account on
`fetch_account_actor` and a moderator one on `fetch_moderator_actor`; an operation that takes no token depends on none
of them, so it ignores the header `Authorization` and renews nothing (`plans_finished/accounts/ACCOUNTS_PLAN.md` D-7).

The renewed token travels through the state of the request: `fetch_request_session` stores it, and
`SessionTokenMiddleware` writes it into the header `Session-Token` when the response starts, so it reaches a successful
response and a refusal built by an exception handler alike (D-8). A refusal with `session_expired` clears it, because
the client deletes its token on that answer. A response of `internal_error` built outside the handlers carries none.
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from api.errors import build_error_response
from common_time import fetch_utc_now
from service.actors import (
    AccountActor,
    AuthenticationRequiredError,
    ModeratorRoleRequiredError,
    SessionExpiredError,
    SessionResolution,
    resolve_account_actor,
    resolve_moderator_actor,
    resolve_request_actor,
)

SESSION_TOKEN_HEADER = b"session-token"
SESSION_STATE_KEY = "session_token"


def fetch_request_session(request: Request) -> SessionResolution:
    """Resolves who makes the request from its one header `Authorization` and keeps the renewed token for the response; a repeated header is a malformed session."""
    authorizations = request.headers.getlist("authorization")
    if len(authorizations) > 1:
        raise SessionExpiredError
    resolution = resolve_request_actor(authorizations[0] if authorizations else None, fetch_utc_now())
    apply_session_token(request, resolution.renewed_token)
    return resolution


def fetch_account_actor(resolution: Annotated[SessionResolution, Depends(fetch_request_session)]) -> AccountActor:
    """Gives the account of the request, refusing a person without an account."""
    return resolve_account_actor(resolution)


def fetch_moderator_actor(resolution: Annotated[SessionResolution, Depends(fetch_request_session)]) -> AccountActor:
    """Gives the account of the request when it holds the moderator role now, refusing anybody else."""
    return resolve_moderator_actor(resolution)


def apply_session_token(request: Request, token: str | None) -> None:
    """Sets the token the response of this request carries in `Session-Token`, or clears it with None."""
    request.scope.setdefault("state", {})[SESSION_STATE_KEY] = token


class SessionTokenMiddleware:
    """Writes the session token kept in the state of a request into the header `Session-Token` of its response."""

    def __init__(self, app: ASGIApp) -> None:
        """Retain the next ASGI application."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Add the header when the response starts and the state of the request holds a token."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def apply_session_header(message: Message) -> None:
            """Append `Session-Token` to the start of the response when a token is kept."""
            token = scope.get("state", {}).get(SESSION_STATE_KEY)
            if message["type"] == "http.response.start" and token is not None:
                message["headers"] = [*message.get("headers", ()), (SESSION_TOKEN_HEADER, token.encode("ascii"))]
            await send(message)

        await self.app(scope, receive, apply_session_header)


def apply_session_error_handlers(app: FastAPI) -> None:
    """Install the answers of the three session refusals every operation with a token can return."""

    async def apply_session_expired(request: Request, error: Exception) -> JSONResponse:
        """Answer a malformed, wrongly signed or expired token or one of a deleted account, without a renewed token."""
        apply_session_token(request, None)
        return build_error_response("session_expired", 401)

    async def apply_authentication_required(request: Request, error: Exception) -> JSONResponse:
        """Answer an operation that needs an account requested without a token."""
        return build_error_response("authentication_required", 401)

    async def apply_moderator_role_required(request: Request, error: Exception) -> JSONResponse:
        """Answer a moderator operation requested by an account without the moderator role."""
        return build_error_response("moderator_role_required", 403)

    app.add_exception_handler(SessionExpiredError, apply_session_expired)
    app.add_exception_handler(AuthenticationRequiredError, apply_authentication_required)
    app.add_exception_handler(ModeratorRoleRequiredError, apply_moderator_role_required)
