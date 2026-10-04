"""
Critical test of the account operations and the actor resolution through `fetch_api_engine`, against the local database
of `db/compose.yaml` with its chain applied.

One scenario walks an account from its registration to its deletion and the reuse of its pseudonym (AC-1, AC-3, AC-5,
AC-9 - AC-11 of `plans_finished/accounts/ACCOUNTS_PRD.md`). The moderator role is assigned and removed with the statement of
`db/README.md`, section Moderator role, as the team does it by hand (M11). Every instant is explicit.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from data.engine import fetch_api_engine
from service.accounts import AccountView, InvalidCredentialsError, PseudonymTakenError, apply_account_creation, apply_account_deletion, resolve_login
from service.actors import AccountActor, ModeratorRoleRequiredError, SessionExpiredError, resolve_account_actor, resolve_moderator_actor, resolve_request_actor

pytestmark = pytest.mark.critical

REGISTERED_AT = datetime.fromisoformat("2026-10-04T10:00:00.000+02:00")
LOGGED_IN_AT = datetime.fromisoformat("2026-10-04T10:05:00.000+02:00")
PASSWORD = "pięć znaków i więcej"
APPLY_MODERATOR_ROLE_SQL = text("UPDATE account SET is_moderator = :is_moderator WHERE lower(pseudonym) = lower(:pseudonym)")


def apply_moderator_role(pseudonym: str, is_moderator: bool) -> None:
    """Assign or remove the moderator role with the statement the team runs by hand."""
    with fetch_api_engine().begin() as connection:
        assert connection.execute(APPLY_MODERATOR_ROLE_SQL, {"is_moderator": is_moderator, "pseudonym": pseudonym}).rowcount == 1


def test_account_from_registration_to_deletion_and_reuse_of_its_pseudonym(stored_account_cleanup) -> None:
    """Register, log in, resolve, change the role, delete and register the released pseudonym again, with every old token refused."""
    stored_account_cleanup("Wózek_KRK")
    assert apply_account_creation("  Wózek_KRK  ", PASSWORD, REGISTERED_AT) == AccountView(pseudonym="Wózek_KRK", is_moderator=False)
    with pytest.raises(PseudonymTakenError):
        apply_account_creation("wózek_krk", PASSWORD, REGISTERED_AT)

    login = resolve_login(" WÓZEK_KRK ", PASSWORD, LOGGED_IN_AT)
    assert login.account == AccountView(pseudonym="Wózek_KRK", is_moderator=False)
    for pseudonym, password in (("Nikt_Taki", PASSWORD), ("Wózek_KRK", PASSWORD + "!")):
        with pytest.raises(InvalidCredentialsError):
            resolve_login(pseudonym, password, LOGGED_IN_AT)

    header = f"Bearer {login.session_token}"
    actor = resolve_account_actor(resolve_request_actor(header, LOGGED_IN_AT + timedelta(hours=1)))
    assert (actor.pseudonym, actor.is_moderator) == ("Wózek_KRK", False)
    with pytest.raises(ModeratorRoleRequiredError):
        resolve_moderator_actor(resolve_request_actor(header, LOGGED_IN_AT + timedelta(hours=1)))

    apply_moderator_role("wózek_krk", True)
    assert resolve_moderator_actor(resolve_request_actor(header, LOGGED_IN_AT + timedelta(hours=2))) == AccountActor(actor.account_id, "Wózek_KRK", True)
    apply_moderator_role("wózek_krk", False)
    removed = resolve_request_actor(header, LOGGED_IN_AT + timedelta(hours=3))
    assert resolve_account_actor(removed) == actor
    with pytest.raises(ModeratorRoleRequiredError):
        resolve_moderator_actor(removed)

    apply_account_deletion(actor)
    with pytest.raises(SessionExpiredError):
        apply_account_deletion(actor)
    with pytest.raises(SessionExpiredError):
        resolve_request_actor(header, LOGGED_IN_AT + timedelta(hours=4))

    assert apply_account_creation("Wózek_KRK", PASSWORD + " nowe", REGISTERED_AT + timedelta(hours=5)) == AccountView(pseudonym="Wózek_KRK", is_moderator=False)
    with pytest.raises(SessionExpiredError):
        resolve_request_actor(header, LOGGED_IN_AT + timedelta(hours=5))
    renewed = resolve_login("wózek_krk", PASSWORD + " nowe", LOGGED_IN_AT + timedelta(hours=5))
    new_actor = resolve_account_actor(resolve_request_actor(f"Bearer {renewed.session_token}", LOGGED_IN_AT + timedelta(hours=5)))
    assert new_actor.account_id != actor.account_id
    assert new_actor.is_moderator is False
