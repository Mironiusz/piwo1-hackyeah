"""Decide which stored OpenStreetMap facts a fresh copy makes disappear for the first time, and what each of them becomes."""

from collections import defaultdict
from collections.abc import Iterable

from accessibility_db.closed_lists import FactSource

from data.osm_copy import OsmFactChange, OsmFactIdentity, OsmStoredFact, OsmVoteSnapshot
from service.fact_status import resolve_fact_status


def resolve_osm_disappearing_facts(stored: Iterable[OsmStoredFact], fresh: Iterable[OsmFactIdentity]) -> tuple[OsmStoredFact, ...]:
    """
    Return the stored facts that disappear from OpenStreetMap with this copy for the first time.

    Such a fact still has the source openstreetmap and no removal mark, and its identity is absent from the fresh copy.
    A fact already converted to a user report or already marked removed needs no new decision when it stays absent,
    and a returning fact is restored by the present-fact upsert, so neither is returned.
    """
    present = frozenset(fresh)
    return tuple(fact for fact in stored if fact.source == FactSource.OPENSTREETMAP and not fact.is_removed_from_osm and fact.identity not in present)


def resolve_osm_fact_changes(facts: Iterable[OsmStoredFact], votes: Iterable[OsmVoteSnapshot]) -> tuple[OsmFactChange, ...]:
    """
    Decide by M4 what each disappearing fact becomes, from its own votes and the shared evaluator.

    A fact whose confirmations exceed its denials, both summed over the latest votes of five persons, becomes a user
    report and keeps its votes. Every other fact - no votes, only denials or a tie - stays an OpenStreetMap fact marked
    as removed. Only the sums decide, so the evaluator is asked as for a fact not removed yet.
    """
    votes_by_fact: defaultdict[int, list[OsmVoteSnapshot]] = defaultdict(list)
    for vote in votes:
        votes_by_fact[vote.fact_id].append(vote)
    changes = []
    for fact in facts:
        sums = resolve_fact_status(votes_by_fact[fact.id], is_removed_from_osm=False)
        if sums.confirmations > sums.denials:
            changes.append(OsmFactChange(fact.id, FactSource.USER_REPORT, False))
        else:
            changes.append(OsmFactChange(fact.id, FactSource.OPENSTREETMAP, True))
    return tuple(changes)
