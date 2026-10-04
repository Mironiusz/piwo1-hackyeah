"""
The account operations of `docs/product/api_contract.md`, section Accounts: registering, logging in and deleting one's own account.

Registration checks the pseudonym and the password by M9, hashes the password before the transaction opens and leaves the
uniqueness of the pseudonym to the database, so two concurrent registrations of one pseudonym end in one account
(`plans_finished/accounts/ACCOUNTS_PLAN.md` D-9). A login does not tell apart a pseudonym with no account, a pseudonym or a
password outside the rules and a wrong password: all of them end in `InvalidCredentialsError`, and a pseudonym with no
account is verified against `UNKNOWN_ACCOUNT_PASSWORD_HASH`, so it takes as long as a wrong password (D-5). Deleting an
account removes its row in one statement and its reports and votes stay with their weight (D-10).

No function here logs a pseudonym, an identifier, a password or a token.
"""

from dataclasses import dataclass, field
from datetime import datetime

from accessibility_db.tables import build_offset_instant

from data.accounts import apply_account_delete, apply_account_insert, fetch_account_by_pseudonym
from data.engine import fetch_api_engine
from service.account_rules import InvalidAccountInputError, resolve_password, resolve_pseudonym
from service.actors import AccountActor, fetch_session_signing_key
from service.passwords import UNKNOWN_ACCOUNT_PASSWORD_HASH, build_password_hash, resolve_password_match
from service.session_tokens import SessionExpiredError, build_session_token


class PseudonymTakenError(Exception):
    """An account already has a pseudonym that differs from the requested one at most in letter case."""


class InvalidCredentialsError(Exception):
    """No account has the pseudonym, or the password is wrong; the two are deliberately not told apart."""


@dataclass(frozen=True)
class AccountView:
    """The account of the session itself as the contract shows it: its pseudonym and its moderator role."""

    pseudonym: str
    is_moderator: bool


@dataclass(frozen=True)
class LoginResult:
    """A successful login: the account and the token of its new session."""

    account: AccountView
    session_token: str = field(repr=False)


def apply_account_creation(pseudonym: str, password: str, now: datetime) -> AccountView:
    """Registers an ordinary account at `now`, an aware instant in the business zone, or refuses the input or a taken pseudonym."""
    accepted_pseudonym = resolve_pseudonym(pseudonym)
    password_hash = build_password_hash(resolve_password(password))
    with fetch_api_engine().begin() as connection:
        account_id = apply_account_insert(connection, accepted_pseudonym, password_hash, build_offset_instant(now))
    if account_id is None:
        raise PseudonymTakenError
    return AccountView(pseudonym=accepted_pseudonym, is_moderator=False)


def resolve_login(pseudonym: str, password: str, now: datetime) -> LoginResult:
    """Logs an account in at `now` and gives it a token valid for 24 hours, or refuses the login with `InvalidCredentialsError`."""
    try:
        accepted_pseudonym = resolve_pseudonym(pseudonym)
        accepted_password = resolve_password(password)
    except InvalidAccountInputError:
        raise InvalidCredentialsError from None
    with fetch_api_engine().begin() as connection:
        account = fetch_account_by_pseudonym(connection, accepted_pseudonym)
    if account is None:
        resolve_password_match(UNKNOWN_ACCOUNT_PASSWORD_HASH, accepted_password)
        raise InvalidCredentialsError
    if not resolve_password_match(account.password_hash, accepted_password):
        raise InvalidCredentialsError
    view = AccountView(pseudonym=account.pseudonym, is_moderator=account.is_moderator)
    return LoginResult(account=view, session_token=build_session_token(account.account_id, now, fetch_session_signing_key()))


def apply_account_deletion(actor: AccountActor) -> None:
    """Deletes the account of the actor, or refuses with `SessionExpiredError` when another request deleted it first."""
    with fetch_api_engine().begin() as connection:
        deleted = apply_account_delete(connection, actor.account_id)
    if not deleted:
        raise SessionExpiredError
