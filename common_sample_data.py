"""Typed sample-loading records shared by the service, storage and common loader."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from hashlib import sha256

from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import OffsetInstant

SAMPLE_POINT_ASSOCIATION_DISTANCE_M = 15


class SampleDataOutcome(StrEnum):
    """An acknowledged sample transaction's effect on the fixed dataset."""

    CREATED = "created"
    UNCHANGED = "unchanged"


class SampleCommitState(StrEnum):
    """The completion evidence available for an unsuccessful invocation."""

    NOT_ATTEMPTED = "not_attempted"
    ROLLED_BACK = "rolled_back"
    UNKNOWN = "unknown"


class SampleFailureReason(StrEnum):
    """Safe failure codes that carry no database or contributor content."""

    COPY_MISSING = "copy_missing"
    SITE_INVALID = "site_invalid"
    CONTRADICTION_MISSING = "contradiction_missing"
    IDENTITY_COLLISION = "identity_collision"
    CONTENT_MISMATCH = "content_mismatch"
    INITIAL_VOTE_INVALID = "initial_vote_invalid"
    DATABASE_FAILED = "database_failed"
    COMMIT_UNKNOWN = "commit_unknown"


class SampleDataError(Exception):
    """Reports a safe loading failure without replacing uncertainty with success."""

    def __init__(self, reason: SampleFailureReason, commit_state: SampleCommitState = SampleCommitState.NOT_ATTEMPTED) -> None:
        """Keeps the reason and completion evidence as explicit provider fields."""
        self.reason = reason
        self.commit_state = commit_state
        super().__init__(reason.value)


SampleDataFailure = SampleDataError
"""The approved provider exception name, preserving the public handoff contract."""


@dataclass(frozen=True)
class SampleVoteDefinition:
    """One fictional vote without an account, as a verdict and its whole minutes before the first loading."""

    verdict: VoteVerdict
    minutes_before_loading: int


@dataclass(frozen=True)
class SampleDefinition:
    """
    A fixed fictional fact, the real way used to validate its place, and its votes and moderation.

    Every time is given in whole minutes before the first successful loading. A flag or a hiding without minutes is
    absent. Only a fact that needs a lowered kerb of the copy to contradict it requires the kerb contradiction.
    """

    fact_id: int
    fact_type: FactType
    latitude: float
    longitude: float
    reference_way_id: int
    description: str | None
    created_minutes_before_loading: int
    votes: tuple[SampleVoteDefinition, ...]
    step_count: int | None = None
    geozone_radius_m: int | None = None
    flagged_minutes_before_loading: int | None = None
    hidden_minutes_before_loading: int | None = None
    requires_kerb_contradiction: bool = False


@dataclass(frozen=True)
class SampleNearbyWay:
    """A candidate path and its measured geography distance to a sample point."""

    way_id: int
    distance_m: float


@dataclass(frozen=True)
class SampleNetworkPrerequisites:
    """
    Network measurements from one transaction snapshot for one definition.

    The storage measures the copy and the ways; the service establishes the kerb contradiction from the route graph. Until
    it does, the contradiction stays false, because missing evidence never establishes one.
    """

    fact_id: int
    has_copy: bool
    reference_exists: bool
    nearest_ways: tuple[SampleNearbyWay, ...]
    reference_distance_m: float | None
    has_kerb_contradiction: bool = False


@dataclass(frozen=True)
class SampleFactRow:
    """A definition ready to insert, with the creation pair and the flag and hide pairs it starts with."""

    definition: SampleDefinition
    created_at: OffsetInstant
    flagged_at: OffsetInstant | None
    hidden_at: OffsetInstant | None


@dataclass(frozen=True)
class SampleVoteRow:
    """One sample vote ready to insert or expected in storage: its fact, fictional voter, verdict and pair."""

    fact_id: int
    voter_hash: bytes
    verdict: VoteVerdict
    cast_at: OffsetInstant


@dataclass(frozen=True)
class StoredSample:
    """Immutable fact content used for reconciliation, excluding moderation fields."""

    fact_id: int
    fact_type: FactType
    source: FactSource
    latitude: float
    longitude: float
    geozone_radius_m: int | None
    description: str | None
    step_count: int | None
    is_sample: bool
    idempotency_key: bytes | None
    osm_element_type: OsmElementType | None
    osm_element_id: int | None
    osm_edited_on: date | None
    is_removed_from_osm: bool
    created_at: OffsetInstant


@dataclass(frozen=True)
class StoredSampleVote:
    """One stored vote cast under a fictional sample voter identity."""

    fact_id: int
    verdict: VoteVerdict
    is_cast_with_account: bool
    account_id: int | None
    voter_hash: bytes
    cast_at: OffsetInstant


@dataclass(frozen=True)
class SampleDataResult:
    """The acknowledged effect and counts handed to the common loading program."""

    outcome: SampleDataOutcome
    created_count: int
    unchanged_count: int
    initial_votes_created_count: int
    fact_ids: tuple[int, ...]


def build_sample_voter_hash(sample_id: int, vote_index: int) -> bytes:
    """Builds the fictional voter identity of one sample vote from its fact identifier and 1-based vote index."""
    return sha256(f"sample-data:voter:v2:{sample_id}:{vote_index}".encode()).digest()
