"""Validates and loads the eight sample facts of the demo scenario without resetting contributions."""

from collections import Counter
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from math import isfinite

import numpy as np
from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict
from accessibility_db.tables import OffsetInstant, build_offset_instant
from sqlalchemy import Connection

from common_sample_data import (
    SAMPLE_POINT_ASSOCIATION_DISTANCE_M,
    SampleCommitState,
    SampleDataFailure,
    SampleDataOutcome,
    SampleDataResult,
    SampleDefinition,
    SampleFactRow,
    SampleFailureReason,
    SampleNetworkPrerequisites,
    SampleVoteDefinition,
    SampleVoteRow,
    StoredSample,
    StoredSampleVote,
    build_sample_voter_hash,
)
from common_time import build_business_datetime, fetch_business_now
from config.logging import fetch_logger
from data import sample_data as sample_storage
from data.osm_copy import fetch_current_osm_copy
from service.route_graph import build_projected_coordinates, build_way_row, fetch_route_graph
from service.route_segments import build_nearest_stretch, resolve_report_contradiction


def build_sample_votes(verdict: VoteVerdict, *minutes_before_loading: int) -> tuple[SampleVoteDefinition, ...]:
    """Builds votes of one verdict, one for each given count of minutes before the first loading."""
    return tuple(SampleVoteDefinition(verdict, minutes) for minutes in minutes_before_loading)


SAMPLE_DEFINITIONS: tuple[SampleDefinition, ...] = (
    SampleDefinition(-1, FactType.HIGH_KERB, 50.0676150, 19.9888900, 1222443126, None, 288, build_sample_votes(VoteVerdict.CONFIRM, 288, 288, 144, 144)),
    SampleDefinition(-2, FactType.STAIRS, 50.0663721, 19.99663575, 926589685, "Brak poręczy po prawej stronie.", 1440, build_sample_votes(VoteVerdict.CONFIRM, 1440, 1440), step_count=4),
    SampleDefinition(-3, FactType.RAMP, 50.0668, 19.99536, 28837534, None, 2880, build_sample_votes(VoteVerdict.CONFIRM, 2880, 2880, 2160, 2160)),
    SampleDefinition(
        -4,
        FactType.POOR_SURFACE,
        50.06645,
        19.99455,
        360935725,
        "Remont chodnika, rozkopana nawierzchnia.",
        2880,
        build_sample_votes(VoteVerdict.CONFIRM, 2880, 2880) + build_sample_votes(VoteVerdict.DENY, 1440, 1440),
        geozone_radius_m=25,
    ),
    SampleDefinition(-5, FactType.HIGH_KERB, 50.06574634, 19.99708082, 252778084, None, 432, build_sample_votes(VoteVerdict.CONFIRM, 432, 432, 432), requires_kerb_contradiction=True),
    SampleDefinition(
        -6,
        FactType.STAIRS,
        50.06763615,
        19.9893127,
        306727457,
        "Schody pod domem pana [nazwisko], zawsze zastawione jego autem.",
        144,
        build_sample_votes(VoteVerdict.CONFIRM, 144, 144),
        step_count=3,
        flagged_minutes_before_loading=144,
    ),
    SampleDefinition(
        -7,
        FactType.NARROW_PASSAGE,
        50.07595,
        20.00285,
        83093546,
        "Rusztowanie na całej szerokości chodnika.",
        1440,
        build_sample_votes(VoteVerdict.CONFIRM, 1440, 1440) + build_sample_votes(VoteVerdict.DENY, 720, 720),
        geozone_radius_m=50,
        flagged_minutes_before_loading=720,
    ),
    SampleDefinition(
        -8,
        FactType.HIGH_KERB,
        50.06754,
        19.98907,
        1222443122,
        "tekst z numerem telefonu, ukryty.",
        2880,
        build_sample_votes(VoteVerdict.CONFIRM, 2880, 2880),
        flagged_minutes_before_loading=2880,
        hidden_minutes_before_loading=2880,
    ),
)


def build_shifted_instant(instant: datetime, minutes: int) -> OffsetInstant:
    """Moves an aware instant by whole minutes in UTC and pairs the result with the business-zone offset in force at it."""
    return build_offset_instant(build_business_datetime(instant.astimezone(UTC) + timedelta(minutes=minutes)))


def build_sample_instant(definition: SampleDefinition, created_at: OffsetInstant, minutes_before_loading: int) -> OffsetInstant:
    """Dates a vote, flag or hiding of a fact from its creation pair, by the difference of their minutes before the first loading."""
    return build_shifted_instant(created_at.instant, definition.created_minutes_before_loading - minutes_before_loading)


def build_expected_sample_votes(definition: SampleDefinition, created_at: OffsetInstant) -> tuple[SampleVoteRow, ...]:
    """Gives every sample vote of a fact with its fictional voter, verdict and pair, dated from the creation pair of the fact."""
    return tuple(
        SampleVoteRow(definition.fact_id, build_sample_voter_hash(definition.fact_id, index), vote.verdict, build_sample_instant(definition, created_at, vote.minutes_before_loading))
        for index, vote in enumerate(definition.votes, start=1)
    )


def build_sample_insert_rows(definitions: Sequence[SampleDefinition], loading_at: datetime) -> tuple[tuple[SampleFactRow, ...], tuple[SampleVoteRow, ...]]:
    """Gives the fact rows with their creation, flag and hide pairs and the vote rows with theirs, all dated back from the loading instant."""
    fact_rows: list[SampleFactRow] = []
    vote_rows: list[SampleVoteRow] = []
    for definition in definitions:
        created_at = build_shifted_instant(loading_at, -definition.created_minutes_before_loading)
        flagged, hidden = definition.flagged_minutes_before_loading, definition.hidden_minutes_before_loading
        fact_rows.append(
            SampleFactRow(
                definition,
                created_at,
                None if flagged is None else build_sample_instant(definition, created_at, flagged),
                None if hidden is None else build_sample_instant(definition, created_at, hidden),
            )
        )
        vote_rows.extend(build_expected_sample_votes(definition, created_at))
    return tuple(fact_rows), tuple(vote_rows)


def fetch_sample_kerb_contradiction(connection: Connection, definition: SampleDefinition) -> bool:
    """
    Decides with route planning's own rule whether an opposite kerb point of the current copy contradicts a kerb sample.

    The sample lies on the stretch of its reference way nearest to it, and the contradiction needs an opposite kerb point on
    that stretch within 5 m. No copy, a way the route graph does not hold or a way without a stretch establish none.
    """
    copy = fetch_current_osm_copy(connection)
    if copy is None:
        return False
    graph = fetch_route_graph(connection, copy.state_at.instant)
    way_row = build_way_row(graph, definition.reference_way_id)
    if way_row is None:
        return False
    xs, ys = build_projected_coordinates(np.asarray([definition.longitude]), np.asarray([definition.latitude]))
    x, y = float(xs[0]), float(ys[0])
    stretch_id = build_nearest_stretch(graph, way_row, x, y)
    if stretch_id is None:
        return False
    return bool(resolve_report_contradiction(graph, definition.fact_type, stretch_id, x, y))


def resolve_sample_prerequisites(definition: SampleDefinition, prerequisites: SampleNetworkPrerequisites) -> None:
    """Refuses a missing copy, a place that does not meet its condition on its reference way, or a missing kerb contradiction."""
    if not prerequisites.has_copy:
        raise SampleDataFailure(SampleFailureReason.COPY_MISSING)
    if prerequisites.fact_id != definition.fact_id or not prerequisites.reference_exists:
        raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
    if definition.geozone_radius_m is None:
        resolve_sample_point_association(definition, prerequisites)
    else:
        distance = prerequisites.reference_distance_m
        if distance is None or not isfinite(distance) or distance < 0 or distance > definition.geozone_radius_m:
            raise SampleDataFailure(SampleFailureReason.SITE_INVALID)
    if definition.requires_kerb_contradiction and not prerequisites.has_kerb_contradiction:
        raise SampleDataFailure(SampleFailureReason.CONTRADICTION_MISSING)


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


def resolve_existing_sample(definition: SampleDefinition, stored: StoredSample, votes: Sequence[StoredSampleVote]) -> None:
    """Checks the fixed content and the sample vote history dated from the stored creation, leaving every other vote and moderation alone."""
    if stored.fact_id != definition.fact_id or not stored.is_sample or stored.source != FactSource.USER_REPORT:
        raise SampleDataFailure(SampleFailureReason.IDENTITY_COLLISION)
    expected_content = (definition.fact_type, definition.latitude, definition.longitude, definition.geozone_radius_m, definition.description, definition.step_count)
    stored_content = (stored.fact_type, stored.latitude, stored.longitude, stored.geozone_radius_m, stored.description, stored.step_count)
    source_fields = (stored.idempotency_key, stored.osm_element_type, stored.osm_element_id, stored.osm_edited_on)
    if stored_content != expected_content or any(value is not None for value in source_fields) or stored.is_removed_from_osm:
        raise SampleDataFailure(SampleFailureReason.CONTENT_MISMATCH)
    expected_votes = Counter((row.fact_id, row.voter_hash, row.verdict, False, None, row.cast_at) for row in build_expected_sample_votes(definition, stored.created_at))
    stored_votes = Counter((vote.fact_id, vote.voter_hash, vote.verdict, vote.is_cast_with_account, vote.account_id, vote.cast_at) for vote in votes)
    if stored_votes != expected_votes:
        raise SampleDataFailure(SampleFailureReason.INITIAL_VOTE_INVALID)


def fetch_sample_network_prerequisites(connection: Connection) -> tuple[SampleNetworkPrerequisites, ...]:
    """Reads the measured places of every definition and adds the kerb contradiction of the facts that need one."""
    measured = sample_storage.fetch_sample_prerequisites(connection, SAMPLE_DEFINITIONS)
    return tuple(
        replace(prerequisites, has_kerb_contradiction=fetch_sample_kerb_contradiction(connection, definition)) if definition.requires_kerb_contradiction else prerequisites
        for definition, prerequisites in zip(SAMPLE_DEFINITIONS, measured, strict=True)
    )


def apply_sample_contents(connection: Connection) -> SampleDataResult:
    """Executes validation and reconciliation inside the storage-owned transaction."""
    for definition, prerequisites in zip(SAMPLE_DEFINITIONS, fetch_sample_network_prerequisites(connection), strict=True):
        resolve_sample_prerequisites(definition, prerequisites)
    sample_ids = tuple(definition.fact_id for definition in SAMPLE_DEFINITIONS)
    stored = sample_storage.fetch_stored_samples(connection, sample_ids)
    votes = sample_storage.fetch_sample_votes(connection, SAMPLE_DEFINITIONS)
    for definition in SAMPLE_DEFINITIONS:
        if definition.fact_id in stored:
            resolve_existing_sample(definition, stored[definition.fact_id], votes.get(definition.fact_id, ()))
    missing = tuple(definition for definition in SAMPLE_DEFINITIONS if definition.fact_id not in stored)
    inserted_ids: tuple[int, ...] = ()
    votes_created_count = 0
    if missing:
        fact_rows, vote_rows = build_sample_insert_rows(missing, fetch_business_now().replace(microsecond=0))
        inserted_ids = sample_storage.apply_sample_inserts(connection, fact_rows, vote_rows)
        votes_created_count = sum(1 for row in vote_rows if row.fact_id in inserted_ids)
    final_samples = sample_storage.fetch_stored_samples(connection, sample_ids)
    final_votes = sample_storage.fetch_sample_votes(connection, SAMPLE_DEFINITIONS)
    for definition in SAMPLE_DEFINITIONS:
        if definition.fact_id not in final_samples:
            raise SampleDataFailure(SampleFailureReason.IDENTITY_COLLISION)
        resolve_existing_sample(definition, final_samples[definition.fact_id], final_votes.get(definition.fact_id, ()))
    count = len(inserted_ids)
    return SampleDataResult(SampleDataOutcome.CREATED if count else SampleDataOutcome.UNCHANGED, count, len(SAMPLE_DEFINITIONS) - count, votes_created_count, sample_ids)


def apply_sample_data() -> SampleDataResult:
    """Loads the fixed sample facts and returns counts only after acknowledged commit."""
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
