"""Write one prepared copy inside the shared publication transaction and settle a commit whose outcome was lost."""

import time
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Connection
from sqlalchemy.exc import SQLAlchemyError

from common_time import Deadline, fetch_monotonic_seconds
from config.logging import fetch_logger
from data.locks import ImportLease, ImportLeaseLost
from data.osm_copy import (
    apply_osm_copy_metadata,
    apply_osm_fact_changes,
    apply_osm_network,
    apply_osm_present_facts,
    fetch_current_osm_copy,
    fetch_osm_copy_history,
    fetch_osm_fact_history,
    fetch_osm_facts,
    fetch_osm_facts_for_update,
)
from service.osm_database_rows import build_osm_database_network
from service.osm_reconciliation import resolve_osm_disappearing_facts, resolve_osm_fact_changes
from service.osm_routing_preparation import OsmPreparedCopy
from service.osm_source_validation import OsmSourceError, resolve_osm_source_is_newer

OSM_COMMIT_CHECK_WAITS_SECONDS = (1, 2, 4)


@dataclass(frozen=True)
class OsmPublicationCounts:
    """Count what one publication wrote, for the operator's aggregate report."""

    nodes: int
    ways: int
    memberships: int
    facts: int


def apply_osm_copy_publication(connection: Connection, prepared: OsmPreparedCopy, state_at: datetime, filename: str, made_current_at: datetime) -> OsmPublicationCounts:
    """
    Make one prepared copy current on the connection of the shared publication transaction.

    The latest copy is read again and a state that is not newer is refused. Then the network is replaced and present
    facts are upserted. Facts that disappear for the first time are decided last, so their votes stay frozen only for
    the rest of the transaction, and the copy row is appended.
    """
    current = fetch_current_osm_copy(connection)
    if not resolve_osm_source_is_newer(state_at, None if current is None else current.state_at.instant):
        raise OsmSourceError("Source state is no longer newer than the current copy")
    nodes, ways, memberships = build_osm_database_network(prepared.network, prepared.motor_traffic_node_ids)
    apply_osm_network(connection, nodes, ways, memberships)
    facts = apply_osm_present_facts(connection, prepared.facts, made_current_at)
    apply_osm_disappearance(connection, prepared)
    apply_osm_copy_metadata(connection, state_at, filename, made_current_at)
    return OsmPublicationCounts(len(nodes), len(ways), len(memberships), facts)


def apply_osm_disappearance(connection: Connection, prepared: OsmPreparedCopy) -> None:
    """
    Convert or mark as removed every fact the prepared copy makes disappear for the first time.

    The candidates are read without locks, then locked in ascending identity order together with their votes, and the
    decision is made on what was read under those locks, so no vote can change between the evaluation and the write.
    """
    disappearing = resolve_osm_disappearing_facts(fetch_osm_facts(connection), (fact.identity for fact in prepared.facts))
    fact_ids = [fact.id for fact in disappearing]
    locked = fetch_osm_facts_for_update(connection, fact_ids)
    apply_osm_fact_changes(connection, resolve_osm_fact_changes(locked, fetch_osm_fact_history(connection, fact_ids)))


def fetch_osm_commit_outcome(lease: ImportLease, state_at: datetime, deadline: Deadline) -> bool | None:
    """
    Settle a commit whose confirmation was lost: True when the copy row exists, False when it does not, None when unknown.

    The publication backend has already ended. Each of at most three checks waits first, validates the original guard
    and reads the copy history on a fresh connection; a lost guard or no answer before the deadline leaves the outcome
    unknown, and COMMIT is never repeated.
    """
    for wait in OSM_COMMIT_CHECK_WAITS_SECONDS:
        if fetch_monotonic_seconds() + wait >= deadline.expires_at:
            return None
        time.sleep(wait)
        try:
            lease.apply_lease_validation(lease.guard)
            with lease.engine.connect() as connection:
                history = fetch_osm_copy_history(connection)
        except ImportLeaseLost:
            return None
        except SQLAlchemyError:
            fetch_logger(__name__).warning("Commit outcome check failed attempt_wait_seconds=%s", wait)
            continue
        return any(snapshot.state_at.instant == state_at for snapshot in history)
    return None
