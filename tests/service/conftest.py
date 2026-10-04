"""Invented typed snapshots for sample validation without external storage."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactSource, VoteVerdict, WayBarrierState
from accessibility_db.tables import build_offset_instant

from common_sample_data import SampleNearbyWay, SampleNetworkPrerequisites, StoredInitialVote, StoredSample, build_sample_voter_hash
from service.sample_data import SAMPLE_DEFINITIONS


@pytest.fixture
def sample_prerequisites() -> tuple[SampleNetworkPrerequisites, ...]:
    """Builds valid measured-path snapshots for the four fixed definitions."""
    return tuple(
        SampleNetworkPrerequisites(item.fact_id, True, True, WayBarrierState.ABSENT, (SampleNearbyWay(item.reference_way_id, 0.0),), 0.0, 100.0 if item.geozone_radius_m else 0.0)
        for item in SAMPLE_DEFINITIONS
    )


@pytest.fixture
def stored_samples() -> dict[int, StoredSample]:
    """Builds exact fixed content with one original winter creation pair."""
    created_at = build_offset_instant(datetime(2026, 1, 10, 8, 0, tzinfo=ZoneInfo("Europe/Warsaw")))
    return {
        item.fact_id: StoredSample(
            item.fact_id,
            item.fact_type,
            FactSource.USER_REPORT,
            item.latitude,
            item.longitude,
            item.geozone_radius_m,
            item.description,
            item.step_count,
            True,
            None,
            None,
            None,
            None,
            False,
            created_at,
        )
        for item in SAMPLE_DEFINITIONS
    }


@pytest.fixture
def initial_votes(stored_samples: dict[int, StoredSample]) -> dict[int, tuple[StoredInitialVote, ...]]:
    """Builds one fictional original confirmation for every sample."""
    return {identifier: (StoredInitialVote(identifier, VoteVerdict.CONFIRM, False, None, build_sample_voter_hash(identifier), item.created_at),) for identifier, item in stored_samples.items()}
