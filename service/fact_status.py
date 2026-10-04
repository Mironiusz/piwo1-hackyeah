"""Derive the reliability status of a fact from its stored votes by the one rule of M4, for every caller alike."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol

from accessibility_db.closed_lists import VoteVerdict
from accessibility_db.tables import OffsetInstant

from common_time import build_business_day
from data.route_facts import StoredFact

ACCOUNT_VOTE_WEIGHT = 1.0
ANONYMOUS_VOTE_WEIGHT = 0.5
STATUS_PERSON_COUNT = 5
STATUS_WEIGHT_THRESHOLD = 2.0


class FactStatus(StrEnum):
    """The four reliability statuses of M4."""

    UNVERIFIED = "unverified"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    OUTDATED = "outdated"


class FactVoteRecord(Protocol):
    """The fields of one stored vote the rule reads, met by every vote row of the data layer."""

    @property
    def id(self) -> int:
        """The identity of the vote, which grows with every insert."""
        ...

    @property
    def verdict(self) -> VoteVerdict:
        """A confirmation or a denial."""
        ...

    @property
    def is_cast_with_account(self) -> bool:
        """Whether the vote was cast with an account, which decides its weight."""
        ...

    @property
    def account_id(self) -> int | None:
        """The account of the vote, or none without an account or after the account was deleted."""
        ...

    @property
    def voter_hash(self) -> bytes | None:
        """The hashed identifier of a person without an account."""
        ...

    @property
    def cast_at(self) -> OffsetInstant:
        """The instant of the vote with its offset."""
        ...


@dataclass(frozen=True)
class FactStatusResult:
    """The status of a fact, its weighted sums over the latest votes of five persons and the day of its latest confirmation."""

    status: FactStatus
    confirmations: float
    denials: float
    last_confirmed_on: date | None


@dataclass(frozen=True)
class FactView:
    """A stored fact together with the status the rule derived for it."""

    fact: StoredFact
    status: FactStatusResult


def build_vote_person(vote: FactVoteRecord) -> tuple[str, int | bytes]:
    """Name the person of a vote: its account, else its hash, else the vote itself, as a vote of a deleted account is a person of its own."""
    if vote.account_id is not None:
        return ("account", vote.account_id)
    if vote.voter_hash is not None:
        return ("hash", vote.voter_hash)
    return ("vote", vote.id)


def build_vote_weight(vote: FactVoteRecord) -> float:
    """Give a vote cast with an account the weight 1 and a vote without one the weight 0.5."""
    return ACCOUNT_VOTE_WEIGHT if vote.is_cast_with_account else ANONYMOUS_VOTE_WEIGHT


def resolve_fact_status(votes: Iterable[FactVoteRecord], is_removed_from_osm: bool) -> FactStatusResult:
    """
    Derive the status of a fact from all its votes by M4.

    Votes are ordered by their instant and then by their identity, so of two votes with the same instant the later stored
    one counts as later. Only the latest vote of each person counts, and only for the five persons who voted most recently:
    outdated when the denials reach 2 and outweigh the confirmations, otherwise disputed when both exist, otherwise
    confirmed when the confirmations reach 2, otherwise unverified. A fact removed in OpenStreetMap is outdated whatever its
    votes, and its sums are still returned, because the publication of a fresh copy compares them. The day of the latest
    confirmation is taken over every vote, since older votes stop counting only toward the status.
    """
    ordered = sorted(votes, key=lambda vote: (vote.cast_at.instant, vote.id))
    latest_by_person: dict[tuple[str, int | bytes], FactVoteRecord] = {}
    for vote in ordered:
        person = build_vote_person(vote)
        latest_by_person.pop(person, None)
        latest_by_person[person] = vote
    window = list(latest_by_person.values())[-STATUS_PERSON_COUNT:]
    confirmations = sum(build_vote_weight(vote) for vote in window if vote.verdict == VoteVerdict.CONFIRM)
    denials = sum(build_vote_weight(vote) for vote in window if vote.verdict == VoteVerdict.DENY)
    confirming = [vote for vote in ordered if vote.verdict == VoteVerdict.CONFIRM]
    last_confirmed_on = build_business_day(confirming[-1].cast_at.instant) if confirming else None
    return FactStatusResult(resolve_status_from_sums(confirmations, denials, is_removed_from_osm), float(confirmations), float(denials), last_confirmed_on)


def resolve_status_from_sums(confirmations: float, denials: float, is_removed_from_osm: bool) -> FactStatus:
    """Apply the order of M4 to the weighted sums of the latest votes of five persons."""
    if is_removed_from_osm:
        return FactStatus.OUTDATED
    if denials >= STATUS_WEIGHT_THRESHOLD and denials > confirmations:
        return FactStatus.OUTDATED
    if confirmations > 0 and denials > 0:
        return FactStatus.DISPUTED
    if confirmations >= STATUS_WEIGHT_THRESHOLD:
        return FactStatus.CONFIRMED
    return FactStatus.UNVERIFIED
