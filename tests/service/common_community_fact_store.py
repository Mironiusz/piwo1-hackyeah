"""
An invented data seam of the community facts for the scenario tests of `service/community_facts.py`.

It stands in for the functions of `data/community_facts.py`, `fetch_fact_votes`, the API engine, the read-only snapshot,
the statement limit and the business clock, keeping facts and votes in memory. A write transaction keeps a copy of the state
and puts it back when the block fails, so a test sees whether a failed operation left anything behind. The rules of the
data layer are mirrored only as far as the service relies on them: the two visibility predicates, the daily limit by the
calendar day in Europe/Warsaw, the first flag and hiding kept, and the failure of a vote of a deleted account. Every call is
recorded in `events`, so a test can check the order of the lock, the statement limits and the writes.
"""

import copy
import math
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import OffsetInstant, build_offset_instant

from data.community_facts import (
    AccountVoter,
    FactContent,
    FactInsertOutcome,
    StoredCommunityFact,
    StoredNearbyFact,
    StoredVoteInsert,
    VoteAccountMissingError,
    VoteDayTaken,
    VoteInsertOutcome,
    Voter,
)
from data.route_facts import StoredVote

WARSAW = ZoneInfo("Europe/Warsaw")
EARTH_RADIUS_M = 6371008.8
CZYZYNY_LAT = 50.0661
CZYZYNY_LON = 19.9878


@dataclass(frozen=True)
class InventedConnection:
    """A stand-in for a connection: the kind of block it belongs to and the number of that block."""

    kind: str
    number: int


class InventedFactStore:
    """Facts, votes, idempotency keys and deleted accounts in memory, with the recorded calls of the service."""

    def __init__(self) -> None:
        """Start empty on an invented autumn morning in Warsaw."""
        self.facts: dict[int, StoredCommunityFact] = {}
        self.votes: list[StoredVote] = []
        self.keys: dict[bytes, int] = {}
        self.deleted_accounts: set[int] = set()
        self.events: list[tuple[object, ...]] = []
        self.now = datetime(2026, 10, 4, 10, 0, tzinfo=WARSAW)
        self.lock_wait = timedelta(0)
        self.blocks = 0

    def add_fact(
        self,
        fact_id: int,
        fact_type: FactType = FactType.STAIRS,
        source: FactSource = FactSource.USER_REPORT,
        lat: float = CZYZYNY_LAT,
        lon: float = CZYZYNY_LON,
        is_hidden: bool = False,
        is_removed_from_osm: bool = False,
        flagged_at: datetime | None = None,
        geozone_radius_m: int | None = None,
        osm_element_id: int | None = None,
    ) -> StoredCommunityFact:
        """Store an invented fact; a fact from OpenStreetMap or one converted from it carries an element identity."""
        is_from_osm = source == FactSource.OPENSTREETMAP or osm_element_id is not None
        fact = StoredCommunityFact(
            id=fact_id,
            fact_type=fact_type,
            source=source,
            lat=lat,
            lon=lon,
            geozone_radius_m=geozone_radius_m,
            description=None,
            step_count=None,
            is_sample=False,
            osm_element_type=OsmElementType.NODE if is_from_osm else None,
            osm_element_id=(osm_element_id or 9300000000 + fact_id) if is_from_osm else None,
            osm_edited_on=self.now.date() if source == FactSource.OPENSTREETMAP else None,
            is_removed_from_osm=is_removed_from_osm,
            flagged_at=None if flagged_at is None else build_offset_instant(flagged_at),
            is_hidden=is_hidden,
        )
        self.facts[fact_id] = fact
        return fact

    def add_vote(self, fact_id: int, verdict: VoteVerdict, voter: Voter, cast_at: datetime) -> None:
        """Store an invented vote without the daily limit, as an earlier day left it."""
        self.votes.append(build_stored_vote(len(self.votes) + 1, fact_id, verdict, voter, build_offset_instant(cast_at)))

    def build_invented_engine(self) -> "InventedEngine":
        """Give the stand-in of the API engine."""
        return InventedEngine(self)

    @contextmanager
    def apply_invented_snapshot(self, engine: "InventedEngine") -> Iterator[InventedConnection]:
        """Open a read-only block; it writes nothing."""
        self.blocks += 1
        connection = InventedConnection("snapshot", self.blocks)
        self.events.append(("snapshot", connection.number))
        yield connection

    @contextmanager
    def apply_invented_transaction(self) -> Iterator[InventedConnection]:
        """Open a write block that puts the state back when it fails."""
        self.blocks += 1
        connection = InventedConnection("write", self.blocks)
        saved = copy.deepcopy((self.facts, self.votes, self.keys))
        self.events.append(("begin", connection.number))
        try:
            yield connection
        except BaseException:
            self.facts, self.votes, self.keys = saved
            self.events.append(("rollback", connection.number))
            raise
        self.events.append(("commit", connection.number))

    def fetch_business_now(self) -> datetime:
        """Read the invented business clock."""
        self.events.append(("clock",))
        return self.now

    def apply_statement_timeout(self, connection: InventedConnection, milliseconds: int) -> None:
        """Record a statement limit of the current block."""
        self.events.append(("timeout", milliseconds))

    def fetch_stored_facts_in_area(self, connection: InventedConnection, south: float, west: float, north: float, east: float, limit: int) -> tuple[StoredCommunityFact, ...]:
        """Read the visible facts whose point lies in the rectangle, edge included, by identity, at most limit."""
        self.events.append(("area", connection, limit))
        inside = [fact for fact in self.fetch_visible_facts() if south <= fact.lat <= north and west <= fact.lon <= east]
        return tuple(inside[:limit])

    def fetch_stored_fact(self, connection: InventedConnection, fact_id: int) -> StoredCommunityFact | None:
        """Read one fact unless it is hidden or missing."""
        self.events.append(("detail", connection, fact_id))
        fact = self.facts.get(fact_id)
        return None if fact is None or fact.is_hidden else fact

    def fetch_stored_nearby_facts(self, connection: InventedConnection, fact_type: FactType, lat: float, lon: float, distance_m: float) -> tuple[StoredNearbyFact, ...]:
        """Read the visible facts of the type within distance_m, nearest first and by identity among equals."""
        self.events.append(("nearby", connection, distance_m))
        found = [(build_distance_m(lat, lon, fact.lat, fact.lon), fact) for fact in self.fetch_visible_facts() if fact.fact_type == fact_type]
        return tuple(StoredNearbyFact(fact, distance) for distance, fact in sorted(found, key=lambda item: (item[0], item[1].id)) if distance <= distance_m)

    def fetch_stored_flagged_facts(self, connection: InventedConnection) -> tuple[StoredCommunityFact, ...]:
        """Read every flagged fact, hidden ones included, the latest flag first and by identity descending."""
        self.events.append(("flagged", connection))
        flagged = [fact for fact in self.facts.values() if fact.flagged_at is not None]
        return tuple(sorted(flagged, key=lambda fact: (fact.flagged_at.instant if fact.flagged_at else datetime.min, fact.id), reverse=True))

    def fetch_stored_fact_for_vote(self, connection: InventedConnection, fact_id: int) -> StoredCommunityFact | None:
        """Lock a fact for a vote, hidden or not, letting the invented wait pass on the clock."""
        self.events.append(("lock_for_vote", fact_id))
        self.now += self.lock_wait
        return self.facts.get(fact_id)

    def fetch_stored_fact_for_change(self, connection: InventedConnection, fact_id: int) -> StoredCommunityFact | None:
        """Lock a fact for a flag, a hiding or a restoration, hidden or not."""
        self.events.append(("lock_for_change", fact_id))
        return self.facts.get(fact_id)

    def fetch_fact_votes(self, connection: InventedConnection, fact_ids: list[int]) -> tuple[StoredVote, ...]:
        """Read every vote of the given facts in fact and vote order."""
        self.events.append(("votes", connection, tuple(fact_ids)))
        wanted = set(fact_ids)
        return tuple(sorted((vote for vote in self.votes if vote.fact_id in wanted), key=lambda vote: (vote.fact_id, vote.id)))

    def apply_fact_insert(self, connection: InventedConnection, content: FactContent, idempotency_key: bytes, created_at: OffsetInstant, author: Voter) -> FactInsertOutcome:
        """Save a user report once per key with the confirmation of its author, or give the fact already stored under the key."""
        self.events.append(("insert_fact", idempotency_key))
        if idempotency_key in self.keys:
            return FactInsertOutcome(fact=self.facts[self.keys[idempotency_key]], is_created=False)
        fact_id = max(self.facts, default=0) + 1
        fact = StoredCommunityFact(
            id=fact_id,
            fact_type=content.fact_type,
            source=FactSource.USER_REPORT,
            lat=content.lat,
            lon=content.lon,
            geozone_radius_m=content.geozone_radius_m,
            description=content.description,
            step_count=content.step_count,
            is_sample=False,
            osm_element_type=None,
            osm_element_id=None,
            osm_edited_on=None,
            is_removed_from_osm=False,
            flagged_at=None,
            is_hidden=False,
        )
        self.facts[fact_id] = fact
        self.keys[idempotency_key] = fact_id
        self.apply_vote_insert(connection, fact_id, VoteVerdict.CONFIRM, author, created_at)
        return FactInsertOutcome(fact=fact, is_created=True)

    def apply_vote_insert(self, connection: InventedConnection, fact_id: int, verdict: VoteVerdict, voter: Voter, cast_at: OffsetInstant) -> VoteInsertOutcome:
        """Store a vote unless the person already voted on the fact on the same calendar day in Warsaw, refusing a deleted account."""
        self.events.append(("insert_vote", fact_id, cast_at))
        if isinstance(voter, AccountVoter) and voter.account_id in self.deleted_accounts:
            raise VoteAccountMissingError
        day = cast_at.instant.astimezone(WARSAW).date()
        same = [vote for vote in self.votes if vote.fact_id == fact_id and build_vote_person(vote) == build_voter_person(voter)]
        if any(vote.cast_at.instant.astimezone(WARSAW).date() == day for vote in same):
            latest = max(same, key=lambda vote: (vote.cast_at.instant, vote.id))
            return VoteDayTaken(cast_on=latest.cast_at.instant.astimezone(WARSAW).date())
        vote = build_stored_vote(len(self.votes) + 1, fact_id, verdict, voter, cast_at)
        self.votes.append(vote)
        return StoredVoteInsert(vote_id=vote.id, cast_on=day)

    def apply_fact_flag(self, connection: InventedConnection, fact_id: int, flagged_at: OffsetInstant) -> StoredCommunityFact:
        """Flag a fact, keeping the first instant."""
        self.events.append(("flag", fact_id))
        fact = self.facts[fact_id]
        self.facts[fact_id] = replace(fact, flagged_at=fact.flagged_at or flagged_at)
        return self.facts[fact_id]

    def apply_fact_hiding(self, connection: InventedConnection, fact_id: int, hidden_at: OffsetInstant) -> StoredCommunityFact:
        """Hide a fact, which the database allows only for a flagged one."""
        self.events.append(("hide", fact_id))
        assert self.facts[fact_id].flagged_at is not None
        self.facts[fact_id] = replace(self.facts[fact_id], is_hidden=True)
        return self.facts[fact_id]

    def apply_fact_restoration(self, connection: InventedConnection, fact_id: int) -> StoredCommunityFact:
        """Clear the hidden mark of a fact."""
        self.events.append(("restore", fact_id))
        self.facts[fact_id] = replace(self.facts[fact_id], is_hidden=False)
        return self.facts[fact_id]

    def fetch_visible_facts(self) -> list[StoredCommunityFact]:
        """Give the facts neither hidden nor removed in OpenStreetMap, by identity."""
        return [self.facts[fact_id] for fact_id in sorted(self.facts) if not self.facts[fact_id].is_hidden and not self.facts[fact_id].is_removed_from_osm]


@dataclass(frozen=True)
class InventedEngine:
    """A stand-in for the API engine whose begin opens a write block of the store."""

    store: InventedFactStore

    def begin(self):
        """Open a write block."""
        return self.store.apply_invented_transaction()


def build_stored_vote(vote_id: int, fact_id: int, verdict: VoteVerdict, voter: Voter, cast_at: OffsetInstant) -> StoredVote:
    """Build the stored vote of a person."""
    if isinstance(voter, AccountVoter):
        return StoredVote(vote_id, fact_id, verdict, True, cast_at, voter.account_id, None)
    return StoredVote(vote_id, fact_id, verdict, False, cast_at, None, voter.voter_hash)


def build_vote_person(vote: StoredVote) -> tuple[str, object]:
    """Name the person of a stored vote."""
    return ("account", vote.account_id) if vote.account_id is not None else ("hash", vote.voter_hash)


def build_voter_person(voter: Voter) -> tuple[str, object]:
    """Name the person of a new vote."""
    return ("account", voter.account_id) if isinstance(voter, AccountVoter) else ("hash", voter.voter_hash)


def build_distance_m(lat: float, lon: float, other_lat: float, other_lon: float) -> float:
    """Give the haversine distance in metres between two points, close enough to the geodesic one for invented facts."""
    first, second = math.radians(lat), math.radians(other_lat)
    delta_lat, delta_lon = second - first, math.radians(other_lon - lon)
    half = math.sin(delta_lat / 2) ** 2 + math.cos(first) * math.cos(second) * math.sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(half))


def build_point_north(metres: float) -> float:
    """Give the latitude that lies the given number of metres north of the invented point of Czyżyny."""
    return CZYZYNY_LAT + math.degrees(metres / EARTH_RADIUS_M)


def apply_invented_fact_store(monkeypatch: pytest.MonkeyPatch, store: InventedFactStore) -> None:
    """Replace every call of `service.community_facts` into the data layer, the engine and the clock with the store."""
    module = "service.community_facts"
    monkeypatch.setattr(f"{module}.fetch_api_engine", store.build_invented_engine)
    monkeypatch.setattr(f"{module}.fetch_read_only_snapshot", store.apply_invented_snapshot)
    monkeypatch.setattr(f"{module}.apply_statement_timeout", store.apply_statement_timeout)
    monkeypatch.setattr(f"{module}.fetch_business_now", store.fetch_business_now)
    monkeypatch.setattr(f"{module}.fetch_fact_votes", store.fetch_fact_votes)
    for name in (
        "fetch_stored_facts_in_area",
        "fetch_stored_fact",
        "fetch_stored_nearby_facts",
        "fetch_stored_flagged_facts",
        "fetch_stored_fact_for_vote",
        "fetch_stored_fact_for_change",
        "apply_fact_insert",
        "apply_vote_insert",
    ):
        monkeypatch.setattr(f"{module}.{name}", getattr(store, name))
    monkeypatch.setattr(f"{module}.apply_stored_fact_flag", store.apply_fact_flag)
    monkeypatch.setattr(f"{module}.apply_stored_fact_hiding", store.apply_fact_hiding)
    monkeypatch.setattr(f"{module}.apply_stored_fact_restoration", store.apply_fact_restoration)
