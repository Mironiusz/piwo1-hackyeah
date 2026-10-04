"""
Scenario tests of the one actor resolution of `plans_finished/accounts/ACCOUNTS_PLAN.md` D-7, with the data layer replaced.

The header `Authorization` is turned into an actor or refused with `SessionExpiredError` (AC-8 of
`plans_finished/accounts/ACCOUNTS_PRD.md`), the matrix of a person without an account, an ordinary account and a moderator is
checked against both resolutions in both directions, and the role is read again on every request (AC-9). Every instant
is explicit; no test reads the system clock.
"""

from contextlib import nullcontext
from datetime import datetime, timedelta

import pytest

from data.accounts import StoredAccount
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
from service.session_tokens import SessionClaims, build_session_token, resolve_session_claims
from tests.common_runtime_settings import INVENTED_RUNTIME_SETTINGS

pytestmark = pytest.mark.usefixtures("runtime_settings")

SIGNING_KEY = INVENTED_RUNTIME_SETTINGS["SESSION_SIGNING_KEY"].encode("utf-8")
OTHER_KEY = b"o" * 32
NOW = datetime.fromisoformat("2026-10-04T15:00:00.000+02:00")
ORDINARY = StoredAccount(account_id=7, pseudonym="Wózek_KRK", password_hash="invented-hash", is_moderator=False)
MODERATOR = StoredAccount(account_id=8, pseudonym="Moderator_1", password_hash="invented-hash", is_moderator=True)
MISSING_ACCOUNT_ID = 9


class InventedEngine:
    """An engine whose transaction hands out a placeholder connection and counts how often one was opened."""

    def __init__(self) -> None:
        """Start with no transaction opened."""
        self.transactions = 0

    def begin(self) -> nullcontext[object]:
        """Open one invented transaction."""
        self.transactions += 1
        return nullcontext(object())


@pytest.fixture
def stored_accounts(monkeypatch: pytest.MonkeyPatch) -> dict[int, StoredAccount]:
    """Replace the engine and the read of an account with a dictionary of invented accounts the test may change."""
    accounts = {ORDINARY.account_id: ORDINARY, MODERATOR.account_id: MODERATOR}
    monkeypatch.setattr("service.actors.fetch_api_engine", InventedEngine)
    monkeypatch.setattr("service.actors.fetch_account_by_id", lambda connection, account_id: accounts.get(account_id))
    return accounts


def build_header(account_id: int, issued_at: datetime = NOW, signing_key: bytes = SIGNING_KEY) -> str:
    """Build the header `Authorization` with a token of an account issued at an instant."""
    return f"Bearer {build_session_token(account_id, issued_at, signing_key)}"


def test_request_without_the_header_is_a_person_without_an_account(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give no actor and no token, without opening a transaction."""
    monkeypatch.setattr("service.actors.fetch_api_engine", None)
    assert resolve_request_actor(None, NOW) == SessionResolution(actor=None, renewed_token=None)


@pytest.mark.parametrize(
    "authorization",
    [
        "",
        "Basic x",
        "Bearer",
        "Bearer ",
        f"Bearer  {build_session_token(7, NOW, SIGNING_KEY)}",
        f"Bearer {build_session_token(7, NOW, SIGNING_KEY)} extra",
        f"Token {build_session_token(7, NOW, SIGNING_KEY)}",
        "Bearer not-a-token",
    ],
    ids=["empty", "basic", "bearer-alone", "bearer-and-space", "two-spaces", "trailing-part", "other-scheme", "malformed-token"],
)
def test_malformed_header_is_an_expired_session(stored_accounts, authorization: str) -> None:
    """Refuse a header that is not one Bearer token with session_expired, never as a person without an account."""
    with pytest.raises(SessionExpiredError):
        resolve_request_actor(authorization, NOW)


def test_expired_token_is_refused(stored_accounts) -> None:
    """Refuse a token issued exactly 24 hours before the request."""
    with pytest.raises(SessionExpiredError):
        resolve_request_actor(build_header(ORDINARY.account_id, issued_at=NOW - timedelta(hours=24)), NOW)


def test_wrongly_signed_token_is_refused(stored_accounts) -> None:
    """Refuse a token signed with another key."""
    with pytest.raises(SessionExpiredError):
        resolve_request_actor(build_header(ORDINARY.account_id, signing_key=OTHER_KEY), NOW)


def test_token_of_a_missing_account_is_refused(stored_accounts) -> None:
    """Refuse a valid token whose account no longer exists."""
    with pytest.raises(SessionExpiredError):
        resolve_request_actor(build_header(MISSING_ACCOUNT_ID), NOW)


def test_scheme_is_compared_without_regard_to_letter_case(stored_accounts) -> None:
    """Accept `bearer` in lower case."""
    token = build_session_token(ORDINARY.account_id, NOW, SIGNING_KEY)
    assert resolve_request_actor(f"bearer {token}", NOW).actor == AccountActor(account_id=7, pseudonym="Wózek_KRK", is_moderator=False)


@pytest.mark.parametrize("account", [ORDINARY, MODERATOR], ids=["ordinary", "moderator"])
def test_valid_token_gives_the_actor_and_a_token_renewed_for_24_hours(stored_accounts, account: StoredAccount) -> None:
    """Give the stored account as the actor and a new token of the same account valid until 24 hours after the request."""
    resolution = resolve_request_actor(build_header(account.account_id, issued_at=NOW - timedelta(hours=5)), NOW)
    assert resolution.actor == AccountActor(account_id=account.account_id, pseudonym=account.pseudonym, is_moderator=account.is_moderator)
    assert resolution.renewed_token is not None
    claims = resolve_session_claims(resolution.renewed_token, NOW, SIGNING_KEY)
    assert claims == SessionClaims(account_id=account.account_id, expires_at=NOW + timedelta(hours=24))


ANONYMOUS_RESOLUTION = SessionResolution(actor=None, renewed_token=None)
ORDINARY_ACTOR = AccountActor(account_id=7, pseudonym="Wózek_KRK", is_moderator=False)
MODERATOR_ACTOR = AccountActor(account_id=8, pseudonym="Moderator_1", is_moderator=True)


@pytest.mark.parametrize(
    ("resolution", "account_outcome", "moderator_outcome"),
    [
        (ANONYMOUS_RESOLUTION, AuthenticationRequiredError, AuthenticationRequiredError),
        (SessionResolution(actor=ORDINARY_ACTOR, renewed_token="t"), ORDINARY_ACTOR, ModeratorRoleRequiredError),
        (SessionResolution(actor=MODERATOR_ACTOR, renewed_token="t"), MODERATOR_ACTOR, MODERATOR_ACTOR),
    ],
    ids=["anonymous", "ordinary", "moderator"],
)
def test_actor_matrix_in_both_directions(resolution: SessionResolution, account_outcome: object, moderator_outcome: object) -> None:
    """Admit and refuse each kind of actor exactly as the account and the moderator resolution require."""
    for resolve, outcome in ((resolve_account_actor, account_outcome), (resolve_moderator_actor, moderator_outcome)):
        if isinstance(outcome, type):
            with pytest.raises(outcome):
                resolve(resolution)
        else:
            assert resolve(resolution) == outcome


def test_removed_moderator_role_takes_effect_on_the_next_request(stored_accounts) -> None:
    """Read the role again: after the team removes it, the renewed token passes as an account and is refused as a moderator."""
    first = resolve_request_actor(build_header(MODERATOR.account_id), NOW)
    assert resolve_moderator_actor(first) == MODERATOR_ACTOR
    stored_accounts[MODERATOR.account_id] = StoredAccount(account_id=8, pseudonym="Moderator_1", password_hash="invented-hash", is_moderator=False)
    assert first.renewed_token is not None
    second = resolve_request_actor(f"Bearer {first.renewed_token}", NOW + timedelta(minutes=1))
    assert resolve_account_actor(second) == AccountActor(account_id=8, pseudonym="Moderator_1", is_moderator=False)
    with pytest.raises(ModeratorRoleRequiredError):
        resolve_moderator_actor(second)
