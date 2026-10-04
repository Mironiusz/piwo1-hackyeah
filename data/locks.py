"""Coordinate local workspace ownership with PostgreSQL admission fences."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import SQLAlchemyError

from config.logging import fetch_logger
from data.import_identity import BackendIdentity, fetch_backend_identity, fetch_backend_presence
from data.import_workspace import ImportWorkspaceUnconfirmed, WorkspaceLease, apply_exact_workspace_cleanup, apply_workspace_exclusion, apply_workspace_recovery
from data.local_lock import ImportAlreadyRunning

IMPORT_ADMISSION_LOCK = (1346983759, 1)
IMPORT_PUBLICATION_FENCE = (1346983759, 2)
FETCH_ADMISSION_SQL = text("SELECT pg_try_advisory_lock(:namespace, :key)")
FETCH_SHARED_FENCE_SQL = text("SELECT pg_try_advisory_lock_shared(:namespace, :key)")
APPLY_UNLOCK_SQL = text("SELECT pg_advisory_unlock(:namespace, :key)")
FETCH_GUARD_LOCK_SQL = text("SELECT EXISTS (SELECT 1 FROM pg_locks WHERE locktype='advisory' AND pid=:pid AND database=:database_oid AND classid=:namespace AND objid=:key AND objsubid=2 AND granted)")


class ImportLeaseLostError(RuntimeError):
    """Forbid publication after an import loses its original guard identity."""


ImportLeaseLost = ImportLeaseLostError


@dataclass
class ImportLease:
    """Keep the original dedicated guard and local workspace ownership."""

    engine: Engine
    guard: Connection
    identity: BackendIdentity
    workspace_lease: WorkspaceLease
    state: Literal["active", "lost", "cleanup_pending", "closed"] = "active"

    def apply_lease_validation(self, connection: Connection) -> None:
        """Refuse a missing original guard without recreating its lease."""
        values = {"pid": self.identity.pid, "database_oid": self.identity.database_oid, "namespace": IMPORT_ADMISSION_LOCK[0], "key": IMPORT_ADMISSION_LOCK[1]}
        if self.guard.closed or self.guard.invalidated:
            self.state = "lost"
            raise ImportLeaseLost("Original import guard is disconnected")
        try:
            valid = self.state == "active" and fetch_backend_presence(connection, self.identity) and connection.execute(FETCH_GUARD_LOCK_SQL, values).scalar_one()
        except SQLAlchemyError:
            fetch_logger(__name__).exception("Import guard validation failed")
            valid = False
        if not valid:
            self.state = "lost"
            raise ImportLeaseLost("Original import guard is no longer active") from None

    def fetch_database_completion(self, identity: BackendIdentity) -> bool:
        """Use a fresh bounded monitor session without restoring lost ownership."""
        with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as monitor:
            return not fetch_backend_presence(monitor, identity)


def fetch_admission(connection: Connection, key: tuple[int, int]) -> bool:
    """Attempt one session-level lock without waiting."""
    return bool(connection.execute(FETCH_ADMISSION_SQL, {"namespace": key[0], "key": key[1]}).scalar_one())


@contextmanager
def apply_import_exclusion(engine: Engine, workspace_root: Path) -> Iterator[ImportLease]:
    """Refuse overlap and recover old private files before admitting new work."""
    with apply_workspace_exclusion(workspace_root) as workspace, engine.connect().execution_options(isolation_level="AUTOCOMMIT") as guard:
        if not fetch_admission(guard, IMPORT_ADMISSION_LOCK):
            raise ImportAlreadyRunning("Another import owns database admission")
        if not fetch_admission(guard, IMPORT_PUBLICATION_FENCE):
            raise ImportAlreadyRunning("Previous publication is still active")
        guard.execute(APPLY_UNLOCK_SQL, {"namespace": IMPORT_PUBLICATION_FENCE[0], "key": IMPORT_PUBLICATION_FENCE[1]})
        identity = fetch_backend_identity(guard)
        workspace.apply_backend_registration(identity)
        lease = ImportLease(engine, guard, identity, workspace)
        apply_workspace_recovery(workspace, lease.fetch_database_completion)
        try:
            yield lease
        finally:
            lease.state = "closed" if lease.state == "active" else lease.state
            workspace.active = False
            for registered in workspace.journal.backends:
                from datetime import datetime

                backend = BackendIdentity(registered.pid, datetime.fromisoformat(registered.backend_started_at), registered.database_oid)
                if backend != identity and not lease.fetch_database_completion(backend):
                    lease.state = "cleanup_pending"
                    raise ImportWorkspaceUnconfirmed("Publication database work remains active")
            try:
                if workspace.journal.windows_job_name is not None:
                    from data.windows_job import fetch_job_completion

                    if not fetch_job_completion(workspace.journal.windows_job_name):
                        raise ImportWorkspaceUnconfirmed("Import writers remain active")
                activity = workspace.run_directory / "activity.lock"
                if activity.exists():
                    from data.import_process import fetch_activity_completion

                    if not fetch_activity_completion(activity):
                        raise ImportWorkspaceUnconfirmed("Import writers remain active")
                apply_exact_workspace_cleanup(workspace.run_directory)
            except OSError:
                lease.state = "cleanup_pending"
                raise ImportWorkspaceUnconfirmed("Import file cleanup is incomplete") from None
