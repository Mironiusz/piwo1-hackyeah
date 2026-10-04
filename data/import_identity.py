"""Identify only the database backends owned by one import run."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Connection, text

FETCH_BACKEND_IDENTITY_SQL = text("SELECT pg_backend_pid() AS pid, backend_start, datid FROM pg_stat_activity WHERE pid = pg_backend_pid()")
FETCH_BACKEND_PRESENCE_SQL = text("SELECT EXISTS (SELECT 1 FROM pg_stat_activity WHERE pid = :pid AND backend_start = :started AND datid = :database_oid)")


@dataclass(frozen=True)
class BackendIdentity:
    """Prevent a reused process identifier from matching an old publication."""

    pid: int
    backend_started_at: datetime
    database_oid: int


def fetch_backend_identity(connection: Connection) -> BackendIdentity:
    """Read the identity of this dedicated service-account session."""
    row = connection.execute(FETCH_BACKEND_IDENTITY_SQL).one()
    return BackendIdentity(row.pid, row.backend_start, row.datid)


def fetch_backend_presence(connection: Connection, identity: BackendIdentity) -> bool:
    """Check precisely one registered backend without reading query text."""
    return bool(connection.execute(FETCH_BACKEND_PRESENCE_SQL, {"pid": identity.pid, "started": identity.backend_started_at, "database_oid": identity.database_oid}).scalar_one())
