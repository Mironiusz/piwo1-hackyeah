"""
Reads and writes of the `account` table for the account operations, on a connection the service layer opens.

A pseudonym is unique without regard to letter case through the index `UX_account_pseudonym_lower` on
`lower(pseudonym)`, so the insert leaves the decision between two concurrent registrations to that index and the
lookup by pseudonym compares the same expression; letter case, the Polish letters included, follows the database, not
Python (`plans_finished/accounts/ACCOUNTS_PLAN.md` D-9). Deleting an account deletes only its row; the database detaches its votes
in the same statement through `FK_vote_account` (D-10).
"""

from dataclasses import dataclass, field
from typing import Any, cast

from accessibility_db.tables import Account, OffsetInstant
from sqlalchemy import Connection, Row, Table, bindparam, delete, func, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert

_account = cast(Table, Account.__table__)

APPLY_ACCOUNT_INSERT_SQL = postgres_insert(_account).on_conflict_do_nothing(index_elements=[func.lower(_account.c.pseudonym)]).returning(_account.c.id)
FETCH_ACCOUNT_SQL = select(_account.c.id, _account.c.pseudonym, _account.c.password_hash, _account.c.is_moderator)
FETCH_ACCOUNT_BY_ID_SQL = FETCH_ACCOUNT_SQL.where(_account.c.id == bindparam("account_id"))
FETCH_ACCOUNT_BY_PSEUDONYM_SQL = FETCH_ACCOUNT_SQL.where(func.lower(_account.c.pseudonym) == func.lower(bindparam("pseudonym")))
APPLY_ACCOUNT_DELETE_SQL = delete(_account).where(_account.c.id == bindparam("account_id")).returning(_account.c.id)


@dataclass(frozen=True)
class StoredAccount:
    """An account as stored: its identifier, its pseudonym as registered, its password hash and its moderator role."""

    account_id: int
    pseudonym: str
    password_hash: str = field(repr=False)
    is_moderator: bool


def apply_account_insert(connection: Connection, pseudonym: str, password_hash: str, created_at: OffsetInstant) -> int | None:
    """Inserts an ordinary account and returns its identifier, or None when an account already has the pseudonym up to letter case."""
    parameters = {
        "pseudonym": pseudonym,
        "password_hash": password_hash,
        "is_moderator": False,
        "_created_at": created_at.instant,
        "_created_at_utc_offset_minutes": created_at.utc_offset_minutes,
    }
    return connection.execute(APPLY_ACCOUNT_INSERT_SQL, parameters).scalar_one_or_none()


def fetch_account_by_id(connection: Connection, account_id: int) -> StoredAccount | None:
    """Reads the account with this identifier, or None when it does not exist."""
    return build_stored_account(connection.execute(FETCH_ACCOUNT_BY_ID_SQL, {"account_id": account_id}).one_or_none())


def fetch_account_by_pseudonym(connection: Connection, pseudonym: str) -> StoredAccount | None:
    """Reads the account whose pseudonym equals this one without regard to letter case, or None when there is none."""
    return build_stored_account(connection.execute(FETCH_ACCOUNT_BY_PSEUDONYM_SQL, {"pseudonym": pseudonym}).one_or_none())


def build_stored_account(row: Row[Any] | None) -> StoredAccount | None:
    """Builds the stored account of one read row, or None for no row."""
    return None if row is None else StoredAccount(row.id, row.pseudonym, row.password_hash, row.is_moderator)


def apply_account_delete(connection: Connection, account_id: int) -> bool:
    """Deletes the account with this identifier and says whether a row was deleted; its votes stay, detached by the database."""
    return connection.execute(APPLY_ACCOUNT_DELETE_SQL, {"account_id": account_id}).one_or_none() is not None
