"""
The one place that turns a request into an actor and checks the moderator role (`plans_finished/accounts/ACCOUNTS_PLAN.md` D-7).

A request without the header `Authorization` is a person without an account. A present header must be the scheme
`Bearer`, compared without regard to letter case, one space and a token without spaces; anything else, a token that
`resolve_session_claims` refuses, and a token of an account that no longer exists end in `SessionExpiredError`, never
in a person without an account (`docs/product/api_contract.md`, section Sessions and actors). The account is read again
on every request, so a deleted account and a removed moderator role take effect on the next request (M9, M11).

Every operation of another initiative depends on one of the three resolutions here: an operation open to a person
without an account takes the `SessionResolution`, one that needs an account `resolve_account_actor` and a moderator one
`resolve_moderator_actor`. A consumer whose write fails on `fk_vote_account`, because the account was deleted after its
resolution, answers `session_expired` too.
"""

from dataclasses import dataclass, field
from datetime import datetime

from data.accounts import fetch_account_by_id
from data.engine import fetch_api_engine
from service.session_tokens import SessionExpiredError, build_session_token, resolve_session_claims

BEARER_SCHEME = "bearer"


class AuthenticationRequiredError(Exception):
    """An operation that needs an account was requested without a session token."""


class ModeratorRoleRequiredError(Exception):
    """A moderator operation was requested by an account that does not hold the moderator role at that moment."""


@dataclass(frozen=True)
class AccountActor:
    """The account that makes a request, with its moderator role as stored at the moment of the request."""

    account_id: int
    pseudonym: str
    is_moderator: bool


@dataclass(frozen=True)
class SessionResolution:
    """Who makes a request: an account with the token renewed for it, or a person without an account and no token."""

    actor: AccountActor | None
    renewed_token: str | None = field(repr=False)


def resolve_request_actor(authorization: str | None, now: datetime) -> SessionResolution:
    """Turns the header `Authorization` of a request made at `now` into its actor and a renewed token, or refuses it with `SessionExpiredError`."""
    if authorization is None:
        return SessionResolution(actor=None, renewed_token=None)
    signing_key = fetch_session_signing_key()
    claims = resolve_session_claims(resolve_bearer_token(authorization), now, signing_key)
    with fetch_api_engine().begin() as connection:
        account = fetch_account_by_id(connection, claims.account_id)
    if account is None:
        raise SessionExpiredError
    actor = AccountActor(account_id=account.account_id, pseudonym=account.pseudonym, is_moderator=account.is_moderator)
    return SessionResolution(actor=actor, renewed_token=build_session_token(account.account_id, now, signing_key))


def resolve_bearer_token(authorization: str) -> str:
    """Takes the token out of `Bearer <token>`, refusing another scheme, a missing token or more than one space as a malformed session."""
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.lower() != BEARER_SCHEME or not token or " " in token:
        raise SessionExpiredError
    return token


def resolve_account_actor(resolution: SessionResolution) -> AccountActor:
    """Gives the account of a request, or refuses a person without an account with `AuthenticationRequiredError`."""
    if resolution.actor is None:
        raise AuthenticationRequiredError
    return resolution.actor


def resolve_moderator_actor(resolution: SessionResolution) -> AccountActor:
    """Gives the account of a request that holds the moderator role now, or refuses it with `AuthenticationRequiredError` or `ModeratorRoleRequiredError`."""
    actor = resolve_account_actor(resolution)
    if not actor.is_moderator:
        raise ModeratorRoleRequiredError
    return actor


def fetch_session_signing_key() -> bytes:
    """Reads the key that signs session tokens from the configuration facade, imported here so a module import needs no configuration."""
    from config.config import SESSION_SIGNING_KEY

    return SESSION_SIGNING_KEY.get_secret_value().encode("utf-8")
