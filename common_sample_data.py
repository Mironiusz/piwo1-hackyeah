"""Typed sample-loading records shared by the service, storage and common loader."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from hashlib import sha256

from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict, WayBarrierState
from accessibility_db.tables import OffsetInstant

SAMPLE_POINT_ASSOCIATION_DISTANCE_M = 15
SAMPLE_AMENITY_DISTANCE_M = 50


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
    SURFACE_NOT_ABSENT = "surface_not_absent"
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
class SampleDefinition:
    """A fixed fictional fact and the real path used to validate its site."""

    fact_id: int
    fact_type: FactType
    latitude: float
    longitude: float
    reference_way_id: int
    description: str
    step_count: int | None = None
    geozone_radius_m: int | None = None


@dataclass(frozen=True)
class SampleNearbyWay:
    """A candidate path and its measured geography distance to a sample point."""

    way_id: int
    distance_m: float


@dataclass(frozen=True)
class SampleNetworkPrerequisites:
    """Network measurements from one transaction snapshot for one definition."""

    fact_id: int
    has_copy: bool
    reference_exists: bool
    poor_surface_state: WayBarrierState | None
    nearest_ways: tuple[SampleNearbyWay, ...]
    reference_distance_m: float | None
    contradiction_path_distance_m: float | None


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
class StoredInitialVote:
    """One historical vote with the reserved fictional author's identity."""

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


def build_sample_voter_hash(sample_id: int) -> bytes:
    """Builds the reserved fictional author identity from a sample identifier."""
    return sha256(f"sample-data:initial-author:v1:{sample_id}".encode()).digest()
