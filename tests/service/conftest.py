"""Provide invented runtime settings for the rules that read the business zone or the logger through the configuration facade, invented typed snapshots for sample validation and the invented data seam of the community facts."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactSource

from common_sample_data import SampleFactRow, SampleNearbyWay, SampleNetworkPrerequisites, SampleVoteRow, StoredSample, StoredSampleVote
from service.sample_data import SAMPLE_DEFINITIONS, build_sample_insert_rows
from tests.common_runtime_settings import apply_invented_runtime_settings
from tests.service.common_community_fact_store import InventedFactStore, apply_invented_fact_store

SAMPLE_LOADING_AT = datetime(2026, 1, 10, 8, 0, tzinfo=ZoneInfo("Europe/Warsaw"))


@pytest.fixture
def runtime_settings(monkeypatch: pytest.MonkeyPatch):
    """Load valid invented configuration and restore module state afterwards."""
    with apply_invented_runtime_settings(monkeypatch):
        yield


@pytest.fixture
def fact_store(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> InventedFactStore:
    """Replace the data layer, the engine and the clock of the community facts with an empty invented store, with the invented runtime settings loaded."""
    request.getfixturevalue("runtime_settings")
    store = InventedFactStore()
    apply_invented_fact_store(monkeypatch, store)
    return store


@pytest.fixture
def sample_prerequisites() -> tuple[SampleNetworkPrerequisites, ...]:
    """Builds valid measured-place snapshots for the eight fixed definitions, with the kerb contradiction where one is required."""
    return tuple(SampleNetworkPrerequisites(item.fact_id, True, True, (SampleNearbyWay(item.reference_way_id, 0.0),), 0.0, item.requires_kerb_contradiction) for item in SAMPLE_DEFINITIONS)


@pytest.fixture
def sample_insert_rows(request: pytest.FixtureRequest) -> tuple[tuple[SampleFactRow, ...], tuple[SampleVoteRow, ...]]:
    """Builds the fact and vote rows of a first loading on an invented winter morning, keeping the invented settings loaded for the test."""
    request.getfixturevalue("runtime_settings")
    return build_sample_insert_rows(SAMPLE_DEFINITIONS, SAMPLE_LOADING_AT)


@pytest.fixture
def stored_samples(sample_insert_rows: tuple[tuple[SampleFactRow, ...], tuple[SampleVoteRow, ...]]) -> dict[int, StoredSample]:
    """Builds the exact fixed content of every fact as the first loading stored it."""
    fact_rows, _vote_rows = sample_insert_rows
    return {
        row.definition.fact_id: StoredSample(
            row.definition.fact_id,
            row.definition.fact_type,
            FactSource.USER_REPORT,
            row.definition.latitude,
            row.definition.longitude,
            row.definition.geozone_radius_m,
            row.definition.description,
            row.definition.step_count,
            True,
            None,
            None,
            None,
            None,
            False,
            row.created_at,
        )
        for row in fact_rows
    }


@pytest.fixture
def sample_votes(sample_insert_rows: tuple[tuple[SampleFactRow, ...], tuple[SampleVoteRow, ...]]) -> dict[int, tuple[StoredSampleVote, ...]]:
    """Builds every sample vote of every fact as the first loading stored it."""
    _fact_rows, vote_rows = sample_insert_rows
    votes: dict[int, tuple[StoredSampleVote, ...]] = {}
    for row in vote_rows:
        votes[row.fact_id] = (*votes.get(row.fact_id, ()), StoredSampleVote(row.fact_id, row.verdict, False, None, row.voter_hash, row.cast_at))
    return votes
