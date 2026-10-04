"""Decide which stored OpenStreetMap facts a fresh copy makes disappear for the first time."""

from collections.abc import Iterable

from accessibility_db.closed_lists import FactSource

from data.osm_copy import OsmFactIdentity, OsmStoredFact


class OsmReconciliationError(ValueError):
    """Refuse a refresh that would need the shared vote evaluator, which is not delivered yet."""


def resolve_osm_disappearing_facts(stored: Iterable[OsmStoredFact], fresh: Iterable[OsmFactIdentity]) -> tuple[OsmStoredFact, ...]:
    """
    Return the stored facts that disappear from OpenStreetMap with this copy for the first time.

    Such a fact still has the source openstreetmap and no removal mark, and its identity is absent from the fresh copy.
    A fact already converted to a user report or already marked removed needs no new decision when it stays absent,
    and a returning fact is restored by the present-fact upsert, so neither is returned.
    """
    present = frozenset(fresh)
    return tuple(fact for fact in stored if fact.source == FactSource.OPENSTREETMAP and not fact.is_removed_from_osm and fact.identity not in present)
