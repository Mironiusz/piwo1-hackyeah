"""Validates and loads the four fictional examples without resetting contributions."""

from collections.abc import Sequence
from math import isfinite

from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict, WayBarrierState
from accessibility_db.tables import build_offset_instant
from sqlalchemy import Connection

from common_sample_data import (
    SAMPLE_AMENITY_DISTANCE_M,
    SAMPLE_POINT_ASSOCIATION_DISTANCE_M,
    SampleCommitState,
    SampleDataFailure,
    SampleDataOutcome,
    SampleDataResult,
    SampleDefinition,
    SampleFailureReason,
    SampleNetworkPrerequisites,
    StoredInitialVote,
    StoredSample,
    build_sample_voter_hash,
)
from data import sample_data as sample_storage

SAMPLE_DEFINITIONS: tuple[SampleDefinition, ...] = (
    SampleDefinition(-1, FactType.POOR_SURFACE, 50.06741305, 19.9947175, 926589691, "Sample data: fictional poor surface on an asphalt path."),
    SampleDefinition(-2, FactType.STAIRS, 50.0677843, 19.9934245, 360933256, "Sample data: fictional stairs with three steps.", step_count=3),
    SampleDefinition(-3, FactType.REST_PLACE, 50.06737, 19.99468, 926589691, "Sample data: fictional rest place near the demonstration path."),
    SampleDefinition(-4, FactType.POOR_SURFACE, 50.0681175, 19.99363775, 28837556, "Sample data: fictional poor-surface area with a 25 m radius.", geozone_radius_m=25),
)


def resolve_sample_prerequisites(definition: SampleDefinition, prerequisites: SampleNetworkPrerequisites) -> None:
    """Refuses missing source, invalid path association or a lost explicit contradiction."""
    if not prerequisites.has_copy:
        raise SampleDataFailure(SampleFailureReason.COPY_MISSING)
    if prerequisites.fact_id != definition.fact_id or not prerequisites.reference_exists:
        raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
    if definition.fact_id in (-1, -2):
        resolve_sample_point_association(definition, prerequisites)
    if definition.fact_id == -1 and prerequisites.poor_surface_state != WayBarrierState.ABSENT:
        raise SampleDataFailure(SampleFailureReason.SURFACE_NOT_ABSENT)
    distance = prerequisites.reference_distance_m
    if definition.fact_type == FactType.REST_PLACE and (distance is None or not isfinite(distance) or distance > SAMPLE_AMENITY_DISTANCE_M):
        raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
    if definition.geozone_radius_m is not None:
        separation = prerequisites.contradiction_path_distance_m
        if distance is None or separation is None or not isfinite(distance) or not isfinite(separation):
            raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
        if distance > definition.geozone_radius_m or separation <= definition.geozone_radius_m:
            raise SampleDataFailure(SampleFailureReason.SITE_INVALID)


def resolve_sample_point_association(definition: SampleDefinition, prerequisites: SampleNetworkPrerequisites) -> None:
    """Accepts only the intended uniquely nearest path within the association distance."""
    candidates = prerequisites.nearest_ways
    if not candidates or candidates[0].way_id != definition.reference_way_id:
        raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
    nearest = candidates[0].distance_m
    if not isfinite(nearest) or nearest < 0 or nearest > SAMPLE_POINT_ASSOCIATION_DISTANCE_M:
        raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
    if len(candidates) > 1 and candidates[1].distance_m <= nearest:
        raise SampleDataFailure(SampleFailureReason.SITE_INVALID)


def resolve_existing_sample(definition: SampleDefinition, stored: StoredSample, votes: Sequence[StoredInitialVote]) -> None:
    """Checks fixed content and original author history while leaving moderation alone."""
    if stored.fact_id != definition.fact_id or not stored.is_sample or stored.source != FactSource.USER_REPORT:
        raise SampleDataFailure(SampleFailureReason.IDENTITY_COLLISION)
    expected_content = (definition.fact_type, definition.latitude, definition.longitude, definition.geozone_radius_m, definition.description, definition.step_count)
    stored_content = (stored.fact_type, stored.latitude, stored.longitude, stored.geozone_radius_m, stored.description, stored.step_count)
    source_fields = (stored.idempotency_key, stored.osm_element_type, stored.osm_element_id, stored.osm_edited_on)
    if stored_content != expected_content or any(value is not None for value in source_fields) or stored.is_removed_from_osm:
        raise SampleDataFailure(SampleFailureReason.CONTENT_MISMATCH)
    if len(votes) != 1:
        raise SampleDataFailure(SampleFailureReason.INITIAL_VOTE_INVALID)
    vote = votes[0]
    if (
        vote.fact_id != definition.fact_id
        or vote.voter_hash != build_sample_voter_hash(definition.fact_id)
        or vote.verdict != VoteVerdict.CONFIRM
        or vote.is_cast_with_account
        or vote.account_id is not None
        or vote.cast_at != stored.created_at
    ):
        raise SampleDataFailure(SampleFailureReason.INITIAL_VOTE_INVALID)


def apply_sample_contents(connection: Connection) -> SampleDataResult:
    """Executes validation and reconciliation inside the storage-owned transaction."""
    for definition, prerequisites in zip(SAMPLE_DEFINITIONS, sample_storage.fetch_sample_prerequisites(connection, SAMPLE_DEFINITIONS), strict=True):
        resolve_sample_prerequisites(definition, prerequisites)
    stored = sample_storage.fetch_stored_samples(connection, tuple(definition.fact_id for definition in SAMPLE_DEFINITIONS))
    initial_votes = sample_storage.fetch_initial_sample_votes(connection, SAMPLE_DEFINITIONS)
    for definition in SAMPLE_DEFINITIONS:
        if definition.fact_id in stored:
            resolve_existing_sample(definition, stored[definition.fact_id], initial_votes.get(definition.fact_id, ()))
    missing = tuple(definition for definition in SAMPLE_DEFINITIONS if definition.fact_id not in stored)
    inserted_ids: tuple[int, ...] = ()
    if missing:
        from common_time import fetch_business_now

        created_at = build_offset_instant(fetch_business_now())
        inserted_ids = sample_storage.apply_sample_inserts(connection, missing, created_at)
    final_samples = sample_storage.fetch_stored_samples(connection, tuple(definition.fact_id for definition in SAMPLE_DEFINITIONS))
    final_votes = sample_storage.fetch_initial_sample_votes(connection, SAMPLE_DEFINITIONS)
    for definition in SAMPLE_DEFINITIONS:
        if definition.fact_id not in final_samples:
            raise SampleDataFailure(SampleFailureReason.IDENTITY_COLLISION)
        resolve_existing_sample(definition, final_samples[definition.fact_id], final_votes.get(definition.fact_id, ()))
    count = len(inserted_ids)
    return SampleDataResult(SampleDataOutcome.CREATED if count else SampleDataOutcome.UNCHANGED, count, len(SAMPLE_DEFINITIONS) - count, count, tuple(item.fact_id for item in SAMPLE_DEFINITIONS))


def apply_sample_data() -> SampleDataResult:
    """Loads the fixed examples and returns counts only after acknowledged commit."""
    from config.logging import fetch_logger

    logger = fetch_logger(__name__)
    try:
        result = sample_storage.apply_sample_transaction(apply_sample_contents)
    except SampleDataFailure as failure:
        logger.exception("Sample loading failed reason=%s commit_state=%s", failure.reason.value, failure.commit_state.value)
        raise
    except Exception:
        logger.exception("Sample loading failed reason=%s commit_state=%s", SampleFailureReason.DATABASE_FAILED.value, SampleCommitState.UNKNOWN.value)
        raise
    logger.info(
        "Sample loading completed outcome=%s created_count=%s unchanged_count=%s initial_votes_created_count=%s",
        result.outcome.value,
        result.created_count,
        result.unchanged_count,
        result.initial_votes_created_count,
    )
    return result
