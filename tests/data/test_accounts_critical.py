"""
Critical tests of `data/accounts.py` against the local database of `db/compose.yaml` with its chain applied.

They prove what the index of the pseudonym and the foreign key of a vote decide for accounts
(`plans_finished/accounts/ACCOUNTS_PLAN.md` D-9, D-10): the uniqueness of a pseudonym without regard to letter case, also between
two concurrent registrations (AC-3 of `plans_finished/accounts/ACCOUNTS_PRD.md`), a deletion that detaches votes and keeps their
weight (AC-10), a released pseudonym taken by a new account (AC-11) and a deletion interleaved with a vote insert (AC-12).
Facts and votes, which the service account cannot delete, are written only inside transactions rolled back after the
test; an account a test commits is registered in `stored_account_cleanup` before the commit.
"""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from typing import cast

import pytest
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict
from accessibility_db.tables import Account, Fact, Vote, build_offset_instant
from sqlalchemy import Connection, Table, func, insert, select
from sqlalchemy.exc import IntegrityError

from data.accounts import StoredAccount, apply_account_delete, apply_account_insert, fetch_account_by_id, fetch_account_by_pseudonym
from data.engine import fetch_api_engine

pytestmark = pytest.mark.critical

CREATED_AT = datetime.fromisoformat("2026-10-04T10:00:00.123+02:00")
CAST_AT = datetime.fromisoformat("2026-10-04T11:00:00.000+02:00")
PASSWORD_HASH = "$argon2id$v=19$m=19456,t=2,p=1$invented"
BLOCKED_SECONDS = 0.5
RELEASED_SECONDS = 10
_account = cast(Table, Account.__table__)
_fact = cast(Table, Fact.__table__)
_vote = cast(Table, Vote.__table__)


@pytest.fixture
def connection() -> Iterator[Connection]:
    """A connection of the service account inside one transaction rolled back after the test."""
    with fetch_api_engine().connect() as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


def apply_invented_account(connection: Connection, pseudonym: str) -> int:
    """Insert an ordinary account that must not collide with another one and return its identifier."""
    account_id = apply_account_insert(connection, pseudonym, PASSWORD_HASH, build_offset_instant(CREATED_AT))
    assert account_id is not None
    return account_id


def apply_invented_fact(connection: Connection) -> int:
    """Insert one sample fact, which needs no idempotency key, and return its identifier."""
    instant = build_offset_instant(CAST_AT)
    parameters = {
        "fact_type": FactType.STAIRS,
        "source": FactSource.USER_REPORT,
        "geog": "SRID=4326;POINT(19.9370 50.0614)",
        "is_sample": True,
        "is_removed_from_osm": False,
        "_created_at": instant.instant,
        "_created_at_utc_offset_minutes": instant.utc_offset_minutes,
    }
    return connection.execute(insert(_fact).returning(_fact.c.id), parameters).scalar_one()


def apply_invented_vote(connection: Connection, fact_id: int, account_id: int) -> int:
    """Insert a confirmation of a fact cast with an account at CAST_AT and return its identifier."""
    instant = build_offset_instant(CAST_AT)
    parameters = {
        "fact_id": fact_id,
        "verdict": VoteVerdict.CONFIRM,
        "is_cast_with_account": True,
        "account_id": account_id,
        "_cast_at": instant.instant,
        "_cast_at_utc_offset_minutes": instant.utc_offset_minutes,
    }
    return connection.execute(insert(_vote).returning(_vote.c.id), parameters).scalar_one()


def test_insert_and_both_reads_keep_the_account_and_the_offset_of_its_creation(connection: Connection) -> None:
    """Read back an inserted ordinary account by its identifier and by its pseudonym in another letter case, with the offset of created_at kept."""
    account_id = apply_invented_account(connection, "Wózek_KRK")
    expected = StoredAccount(account_id=account_id, pseudonym="Wózek_KRK", password_hash=PASSWORD_HASH, is_moderator=False)
    assert fetch_account_by_id(connection, account_id) == expected
    assert fetch_account_by_pseudonym(connection, "WÓZEK_KRK") == expected
    created = connection.execute(select(_account.c._created_at, _account.c._created_at_utc_offset_minutes).where(_account.c.id == account_id)).one()
    assert tuple(created) == (CREATED_AT, 120)


def test_missing_account_reads_as_none(connection: Connection) -> None:
    """Give None for an identifier and a pseudonym no account has."""
    assert fetch_account_by_id(connection, -1) is None
    assert fetch_account_by_pseudonym(connection, "nikt_taki") is None


@pytest.mark.parametrize(("first", "second"), [("Wózek_KRK", "wózek_krk"), ("ŁUKASZ", "łukasz")])
def test_pseudonym_equal_up_to_letter_case_is_refused(connection: Connection, first: str, second: str) -> None:
    """Refuse a second account whose pseudonym differs only in letter case, the Polish letters included."""
    apply_invented_account(connection, first)
    assert apply_account_insert(connection, second, PASSWORD_HASH, build_offset_instant(CREATED_AT)) is None


def test_two_concurrent_registrations_create_one_account(stored_account_cleanup) -> None:
    """Let the unique index decide: the second insert waits for the first transaction and finds the pseudonym taken."""
    stored_account_cleanup("Wózek_KRK")
    engine = fetch_api_engine()
    with engine.connect() as first, engine.connect() as second, ThreadPoolExecutor(max_workers=1) as pool:
        first_transaction = first.begin()
        second_transaction = second.begin()
        first_id = apply_account_insert(first, "Wózek_KRK", PASSWORD_HASH, build_offset_instant(CREATED_AT))
        pending = pool.submit(apply_account_insert, second, "wózek_krk", PASSWORD_HASH, build_offset_instant(CREATED_AT))
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        first_transaction.commit()
        second_id = pending.result(timeout=RELEASED_SECONDS)
        second_transaction.commit()
    assert first_id is not None
    assert second_id is None
    with engine.connect() as reader:
        count = reader.execute(select(func.count()).select_from(_account).where(func.lower(_account.c.pseudonym) == func.lower("Wózek_KRK"))).scalar_one()
    assert count == 1


def test_deletion_detaches_the_vote_and_keeps_its_weight(connection: Connection) -> None:
    """Delete an account with a vote: the vote stays, without its account, still cast with an account and with its verdict."""
    fact_id = apply_invented_fact(connection)
    account_id = apply_invented_account(connection, "Wózek_KRK")
    vote_id = apply_invented_vote(connection, fact_id, account_id)
    assert apply_account_delete(connection, account_id) is True
    assert fetch_account_by_id(connection, account_id) is None
    vote = connection.execute(select(_vote.c.account_id, _vote.c.is_cast_with_account, _vote.c.verdict).where(_vote.c.id == vote_id)).one()
    assert tuple(vote) == (None, True, VoteVerdict.CONFIRM)
    assert apply_account_delete(connection, account_id) is False


def test_released_pseudonym_gives_a_new_account_that_can_vote_on_the_same_day(connection: Connection) -> None:
    """Register the pseudonym of a deleted account again: a new identifier, and its vote on the same fact on the same day is accepted."""
    fact_id = apply_invented_fact(connection)
    old_id = apply_invented_account(connection, "Wózek_KRK")
    apply_invented_vote(connection, fact_id, old_id)
    apply_account_delete(connection, old_id)
    new_id = apply_invented_account(connection, "wózek_krk")
    assert new_id != old_id
    apply_invented_vote(connection, fact_id, new_id)
    votes = connection.execute(select(_vote.c.account_id).where(_vote.c.fact_id == fact_id).order_by(_vote.c.id)).scalars().all()
    assert votes == [None, new_id]


def test_deletion_waits_for_an_uncommitted_vote_insert_of_the_account(stored_account_cleanup) -> None:
    """Hold the deletion while another transaction inserts a vote of the account, and let it finish when that transaction ends."""
    stored_account_cleanup("Kolejka_1")
    engine = fetch_api_engine()
    with engine.begin() as setup:
        account_id = apply_invented_account(setup, "Kolejka_1")
    with engine.connect() as voter, engine.connect() as deleter, ThreadPoolExecutor(max_workers=1) as pool:
        vote_transaction = voter.begin()
        apply_invented_vote(voter, apply_invented_fact(voter), account_id)
        delete_transaction = deleter.begin()
        pending = pool.submit(apply_account_delete, deleter, account_id)
        assert not wait([pending], timeout=BLOCKED_SECONDS).done
        vote_transaction.rollback()
        assert pending.result(timeout=RELEASED_SECONDS) is True
        delete_transaction.commit()
    with engine.connect() as reader:
        assert fetch_account_by_id(reader, account_id) is None


def test_vote_insert_after_a_committed_deletion_is_refused_on_the_foreign_key(stored_account_cleanup, connection: Connection) -> None:
    """Refuse a vote of an account deleted before it, on fk_vote_account, which a consumer answers with session_expired."""
    stored_account_cleanup("Spozniony_1")
    engine = fetch_api_engine()
    with engine.begin() as setup:
        account_id = apply_invented_account(setup, "Spozniony_1")
    with engine.begin() as deletion:
        assert apply_account_delete(deletion, account_id) is True
    fact_id = apply_invented_fact(connection)
    with pytest.raises(IntegrityError) as refused:
        apply_invented_vote(connection, fact_id, account_id)
    assert refused.value.orig.diag.constraint_name == "fk_vote_account"


def test_failed_deletion_leaves_the_account_in_place(stored_account_cleanup) -> None:
    """Roll back a deletion that fails after its statement, so the account is neither partly nor wholly removed."""
    stored_account_cleanup("Zostaje_1")
    engine = fetch_api_engine()
    with engine.begin() as setup:
        account_id = apply_invented_account(setup, "Zostaje_1")
    with pytest.raises(RuntimeError), engine.begin() as deletion:
        assert apply_account_delete(deletion, account_id) is True
        raise RuntimeError("invented failure after the deletion")
    with engine.connect() as reader:
        assert fetch_account_by_id(reader, account_id) == StoredAccount(account_id=account_id, pseudonym="Zostaje_1", password_hash=PASSWORD_HASH, is_moderator=False)
