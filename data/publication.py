"""Enforce one transaction budget while preserving uncertain commit outcomes."""

import time
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Connection, event, text
from sqlalchemy.exc import SQLAlchemyError

from common_time import Deadline, DeadlineExpiredError, build_publication_deadline, fetch_monotonic_seconds, resolve_remaining_milliseconds
from config.logging import fetch_logger
from data.engine import build_import_engine
from data.import_identity import fetch_backend_identity
from data.locks import FETCH_SHARED_FENCE_SQL, IMPORT_PUBLICATION_FENCE, ImportAlreadyRunning, ImportLease


class PublicationRolledBackError(RuntimeError):
    """Report publication failure only after rollback is authoritatively confirmed."""


class PublicationOutcomeUnknownError(RuntimeError):
    """Report a lost commit confirmation without claiming rollback or success."""


class PublicationCleanupUnconfirmedError(RuntimeError):
    """Keep exclusion when publication backend completion is not yet confirmed."""


PublicationRolledBack = PublicationRolledBackError
PublicationOutcomeUnknown = PublicationOutcomeUnknownError
PublicationCleanupUnconfirmed = PublicationCleanupUnconfirmedError


@dataclass(frozen=True)
class PublicationResult[T]:
    """Carry the callback result after an acknowledged successful commit."""

    value: T
    outcome: str = "committed"


def apply_transaction[T](lease: ImportLease, deadline: Deadline, connection: Connection, write: Callable[[Connection], T]) -> PublicationResult[T]:
    """Publish synchronously through commit under one nonrenewable deadline."""
    identity = fetch_backend_identity(connection)
    commit_attempted = False
    transaction_started = False
    internal_completion = False
    completed = False
    lease.workspace_lease.apply_backend_registration(identity)

    def apply_statement_guard(_conn, _cursor, statement, _parameters, context, _executemany) -> None:
        """Check the original budget and guard before each callback statement."""
        if internal_completion:
            return
        if statement.strip().upper().split()[0] in ("BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT", "PREPARE"):
            raise ValueError("Publication callback cannot manage transactions")
        resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
        lease.apply_lease_validation(lease.guard)

    try:
        if not connection.execute(FETCH_SHARED_FENCE_SQL, {"namespace": IMPORT_PUBLICATION_FENCE[0], "key": IMPORT_PUBLICATION_FENCE[1]}).scalar_one():
            raise ImportAlreadyRunning("Publication admission is fenced")
        lease.apply_lease_validation(connection)
        budget = resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
        connection.execute(text("SELECT set_config('transaction_timeout', :budget, false)"), {"budget": f"{budget}ms"})
        connection.exec_driver_sql("BEGIN")
        transaction_started = True
        event.listen(connection, "before_cursor_execute", apply_statement_guard)
        value = write(connection)
        resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
        internal_completion = True
        lease.apply_lease_validation(connection)
        lease.workspace_lease.apply_commit_attempt_record()
        resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
        commit_attempted = True
        connection.exec_driver_sql("COMMIT")
        completed = True
        return PublicationResult(value)
    except (Exception, KeyboardInterrupt) as failure:
        fetch_logger(__name__).exception("Publication failed")
        if transaction_started and not commit_attempted:
            try:
                internal_completion = True
                connection.exec_driver_sql("ROLLBACK")
                from psycopg.pq import TransactionStatus

                driver = connection.connection.driver_connection
                completed = driver is not None and driver.info.transaction_status == TransactionStatus.IDLE
            except SQLAlchemyError:
                connection.invalidate()
        elif not transaction_started:
            completed = True
        else:
            connection.invalidate()
        if not completed:
            connection.invalidate()
            apply_completion_wait(lease, identity)
        if commit_attempted:
            raise PublicationOutcomeUnknown("Commit outcome is unknown") from None
        if isinstance(failure, DeadlineExpiredError):
            raise PublicationRolledBack("Publication deadline expired") from None
        raise PublicationRolledBack("Publication failed before commit") from None
    finally:
        if event.contains(connection, "before_cursor_execute", apply_statement_guard):
            event.remove(connection, "before_cursor_execute", apply_statement_guard)


def apply_completion_wait(lease: ImportLease, identity) -> None:
    """Retain exclusion until a fresh session confirms backend termination."""
    while True:
        try:
            if lease.fetch_database_completion(identity):
                return
        except SQLAlchemyError:
            lease.state = "cleanup_pending"
            fetch_logger(__name__).exception("PublicationCleanupUnconfirmed")
        time.sleep(1)


def apply_publication[T](lease: ImportLease, run_deadline: Deadline, write: Callable[[Connection], T]) -> PublicationResult[T]:
    """Preserve the public publication boundary without accepting a lost lease."""
    lease.apply_lease_validation(lease.guard)
    deadline = build_publication_deadline(run_deadline, fetch_monotonic_seconds())
    engine = build_import_engine(resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds()))
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            return apply_transaction(lease, deadline, connection, write)
    finally:
        engine.dispose()
