"""Guards source contradictions, fixed identity and preserved author history."""

from dataclasses import replace
from datetime import timedelta

import pytest
from accessibility_db.closed_lists import FactSource, VoteVerdict, WayBarrierState

from common_sample_data import SampleDataFailure, SampleFailureReason, SampleNearbyWay, SampleNetworkPrerequisites, StoredInitialVote, StoredSample, build_sample_voter_hash
from service.sample_data import SAMPLE_DEFINITIONS, resolve_existing_sample, resolve_sample_prerequisites


def test_every_definition_accepts_its_measured_site(sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Accepts a coherent source snapshot supporting all four intended locations."""
    for definition, prerequisites in zip(SAMPLE_DEFINITIONS, sample_prerequisites, strict=True):
        resolve_sample_prerequisites(definition, prerequisites)


@pytest.mark.parametrize("state", [WayBarrierState.PRESENT, WayBarrierState.UNKNOWN, WayBarrierState.ABSENT_BY_DEFAULT, None])
def test_contradiction_requires_explicit_surface_absence(state: WayBarrierState | None, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Refuses defaults and missing information as evidence of a contradiction."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[0], replace(sample_prerequisites[0], poor_surface_state=state))
    assert raised.value.reason == SampleFailureReason.SURFACE_NOT_ABSENT


def test_missing_copy_fails_before_sample_writes(sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Distinguishes missing publication from an invalid individual site."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[0], replace(sample_prerequisites[0], has_copy=False))
    assert raised.value.reason == SampleFailureReason.COPY_MISSING


@pytest.mark.parametrize(
    "changes",
    [
        {"reference_exists": False},
        {"fact_id": -100},
        {"nearest_ways": ()},
        {"nearest_ways": (SampleNearbyWay(1, 0.0),)},
        {"nearest_ways": (SampleNearbyWay(926589691, 15.01),)},
        {"nearest_ways": (SampleNearbyWay(926589691, float("nan")),)},
        {"nearest_ways": (SampleNearbyWay(926589691, 2.0), SampleNearbyWay(1, 2.0))},
    ],
)
def test_invalid_point_association_is_not_silently_relocated(changes: dict[str, object], sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Rejects missing, distant, different or ambiguously nearest paths."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[0], replace(sample_prerequisites[0], **changes))
    assert raised.value.reason == SampleFailureReason.SITE_INVALID


@pytest.mark.parametrize("distance", [50.01, float("inf"), None])
def test_rest_place_must_be_near_the_contradiction_path(distance: float | None, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Checks required path proximity without claiming actual-route evidence."""
    with pytest.raises(SampleDataFailure):
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[2], replace(sample_prerequisites[2], reference_distance_m=distance))


@pytest.mark.parametrize("distance, separation", [(25.01, 100.0), (0.0, 25.0), (0.0, 24.99), (None, 100.0), (0.0, None), (0.0, float("nan"))])
def test_geozone_must_intersect_its_path_and_leave_the_contradiction_separate(distance: float | None, separation: float | None, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Rejects an isolated area or a circle covering the contradiction corridor."""
    with pytest.raises(SampleDataFailure):
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[3], replace(sample_prerequisites[3], reference_distance_m=distance, contradiction_path_distance_m=separation))


def test_existing_samples_keep_original_creation_history(stored_samples: dict[int, StoredSample], initial_votes: dict[int, tuple[StoredInitialVote, ...]]) -> None:
    """Validates old history without comparing it to a fresh clock or current status."""
    for definition in SAMPLE_DEFINITIONS:
        resolve_existing_sample(definition, stored_samples[definition.fact_id], initial_votes[definition.fact_id])


@pytest.mark.parametrize("changes", [{"is_sample": False}, {"source": FactSource.OPENSTREETMAP}, {"fact_id": -100}])
def test_reserved_id_collision_does_not_overwrite_an_unrelated_fact(
    changes: dict[str, object], stored_samples: dict[int, StoredSample], initial_votes: dict[int, tuple[StoredInitialVote, ...]]
) -> None:
    """Refuses an occupied identifier instead of allocating or replacing a fact."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], replace(stored_samples[-1], **changes), initial_votes[-1])
    assert raised.value.reason == SampleFailureReason.IDENTITY_COLLISION


@pytest.mark.parametrize("changes", [{"description": "Changed definition"}, {"latitude": 50.0}, {"step_count": 1}, {"idempotency_key": b"x" * 32}, {"is_removed_from_osm": True}])
def test_definition_changes_are_not_reconciled_by_overwriting(changes: dict[str, object], stored_samples: dict[int, StoredSample], initial_votes: dict[int, tuple[StoredInitialVote, ...]]) -> None:
    """Detects changed content and invalid provenance fields."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], replace(stored_samples[-1], **changes), initial_votes[-1])
    assert raised.value.reason == SampleFailureReason.CONTENT_MISMATCH


@pytest.mark.parametrize("vote_count", [0, 2])
def test_missing_or_repeated_initial_history_is_an_integrity_error(vote_count: int, stored_samples: dict[int, StoredSample], initial_votes: dict[int, tuple[StoredInitialVote, ...]]) -> None:
    """Does not fabricate a later-day confirmation to repair original history."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], stored_samples[-1], initial_votes[-1] * vote_count)
    assert raised.value.reason == SampleFailureReason.INITIAL_VOTE_INVALID


@pytest.mark.parametrize("changes", [{"verdict": VoteVerdict.DENY}, {"is_cast_with_account": True}, {"account_id": 1}, {"voter_hash": b"x" * 32}, {"fact_id": -2}])
def test_original_vote_actor_and_verdict_are_not_guessed(changes: dict[str, object], stored_samples: dict[int, StoredSample], initial_votes: dict[int, tuple[StoredInitialVote, ...]]) -> None:
    """Requires the one exact fictional actor and its original confirmation."""
    with pytest.raises(SampleDataFailure):
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], stored_samples[-1], (replace(initial_votes[-1][0], **changes),))


def test_later_day_author_vote_cannot_replace_the_original(stored_samples: dict[int, StoredSample], initial_votes: dict[int, tuple[StoredInitialVote, ...]]) -> None:
    """Requires the fact's original instant and offset for the fictional author."""
    original = initial_votes[-1][0]
    changed_time = replace(original.cast_at, instant=original.cast_at.instant + timedelta(days=1))
    with pytest.raises(SampleDataFailure):
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], stored_samples[-1], (replace(original, cast_at=changed_time),))
    with pytest.raises(SampleDataFailure):
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], stored_samples[-1], (replace(original, cast_at=replace(original.cast_at, utc_offset_minutes=120)),))


def test_fictional_author_hashes_are_stable_and_distinct() -> None:
    """Keeps four fictional identities without account or client inputs."""
    identifiers = [item.fact_id for item in SAMPLE_DEFINITIONS]
    hashes = [build_sample_voter_hash(identifier) for identifier in identifiers]
    assert identifiers == [-1, -2, -3, -4]
    assert len(set(hashes)) == 4
    assert all(len(value) == 32 for value in hashes)
    assert hashes == [build_sample_voter_hash(identifier) for identifier in identifiers]
