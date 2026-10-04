"""Exercises real sample storage through restricted runtime and local-owner engines."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
from threading import Barrier, Lock

import pytest
from accessibility_db.closed_lists import WayBarrierState
from sqlalchemy import Connection, Engine, event, text
from sqlalchemy.exc import SQLAlchemyError

from common_sample_data import SampleCommitState, SampleDataFailure, SampleDataOutcome, SampleFailureReason
from service import sample_data
from service.sample_data import SAMPLE_DEFINITIONS, apply_sample_data
from tests.data.common_sample_data_fixtures import INSERT_FIXTURE_COPY_SQL, SAMPLE_FIXTURE_COPY_ID, SampleCriticalDataset

pytestmark = pytest.mark.critical


@pytest.mark.parametrize("sample_critical_dataset", [1, 7], indirect=True)
def test_first_load_and_later_day_retry_preserve_original_author_pairs(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Proves exact counts, millisecond offsets and no refreshed daily author votes."""
    result = apply_sample_data()
    assert result.outcome == SampleDataOutcome.CREATED
    assert (result.created_count, result.unchanged_count, result.initial_votes_created_count) == (4, 0, 4)
    with schema_owner_engine.connect() as connection:
        history = connection.execute(
            text(
                "SELECT f.id, f.created_at, f.created_at_utc_offset_minutes, v.cast_at, v.cast_at_utc_offset_minutes, v.is_cast_with_account FROM fact AS f JOIN vote AS v ON v.fact_id = f.id WHERE f.id = ANY(CAST(:ids AS bigint[])) ORDER BY f.id"
            ),
            {"ids": [-1, -2, -3, -4]},
        ).all()
    assert len(history) == 4
    expected_offset = sample_critical_dataset.original_created_at.utc_offset_minutes
    assert expected_offset in (60, 120)
    for row in history:
        assert row.created_at == row.cast_at == sample_critical_dataset.original_created_at.instant
        assert row.created_at_utc_offset_minutes == row.cast_at_utc_offset_minutes == expected_offset
        assert not row.is_cast_with_account
    assert apply_sample_data().outcome == SampleDataOutcome.UNCHANGED
    sample_critical_dataset.business_now += timedelta(days=1)
    assert apply_sample_data().outcome == SampleDataOutcome.UNCHANGED
    with schema_owner_engine.connect() as connection:
        repeated_history = connection.execute(
            text(
                "SELECT f.id, f.created_at, f.created_at_utc_offset_minutes, v.cast_at, v.cast_at_utc_offset_minutes, v.is_cast_with_account FROM fact AS f JOIN vote AS v ON v.fact_id = f.id WHERE f.id = ANY(CAST(:ids AS bigint[])) ORDER BY f.id"
            ),
            {"ids": [-1, -2, -3, -4]},
        ).all()
    assert repeated_history == history


def test_retry_preserves_community_vote_and_moderation(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Proves that normal contributions and hiding are not reset by another load."""
    apply_sample_data()
    instant = sample_critical_dataset.original_created_at
    parameters = {"instant": instant.instant + timedelta(minutes=5), "offset": instant.utc_offset_minutes, "hash": sha256(b"invented sample fixture contributor").digest()}
    with schema_owner_engine.begin() as connection:
        connection.execute(
            text("INSERT INTO vote (fact_id, verdict, is_cast_with_account, voter_hash, cast_at, cast_at_utc_offset_minutes) VALUES (-1, 'deny', false, :hash, :instant, :offset)"), parameters
        )
        connection.execute(
            text("UPDATE fact SET flagged_at = :instant, flagged_at_utc_offset_minutes = :offset, hidden_at = :instant, hidden_at_utc_offset_minutes = :offset WHERE id = -2"), parameters
        )
    assert apply_sample_data().outcome == SampleDataOutcome.UNCHANGED
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM vote WHERE fact_id = -1")).scalar_one() == 2
        hidden = connection.execute(text("SELECT flagged_at, hidden_at FROM fact WHERE id = -2")).one()
        assert hidden.flagged_at == hidden.hidden_at == parameters["instant"]


@pytest.mark.parametrize("state", [WayBarrierState.UNKNOWN, WayBarrierState.PRESENT])
def test_imported_surface_must_explicitly_support_the_contradiction(state: WayBarrierState, sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Executes the imported-state read and rejects unknown or present surface."""
    with schema_owner_engine.begin() as connection:
        connection.execute(text("UPDATE osm_way SET poor_surface_state = :state WHERE id = :id"), {"state": state.value, "id": SAMPLE_DEFINITIONS[0].reference_way_id})
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_data()
    assert raised.value.reason == SampleFailureReason.SURFACE_NOT_ABSENT
    assert raised.value.commit_state == SampleCommitState.ROLLED_BACK
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM fact WHERE id = ANY(CAST(:ids AS bigint[]))"), {"ids": [-1, -2, -3, -4]}).scalar_one() == 0


def test_missing_copy_is_a_visible_failure(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Refuses absent source metadata and restores the test-owned cleanup marker."""
    with schema_owner_engine.begin() as connection:
        connection.execute(text("DELETE FROM osm_copy WHERE id = :copy_id AND file_name = :marker"), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": sample_critical_dataset.marker})
    try:
        with pytest.raises(SampleDataFailure) as raised:
            apply_sample_data()
        assert raised.value.reason == SampleFailureReason.COPY_MISSING
    finally:
        with schema_owner_engine.begin() as connection:
            connection.execute(text(INSERT_FIXTURE_COPY_SQL), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": sample_critical_dataset.marker, **sample_critical_dataset.build_time_parameters()})


@pytest.mark.parametrize("missing_id", [926589691, 360933256, 28837556])
def test_missing_reference_way_fails_without_relocating_samples(missing_id: int, sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Executes the missing-site checks against the real current-network table."""
    with schema_owner_engine.begin() as connection:
        connection.execute(text("DELETE FROM osm_way WHERE id = :id"), {"id": missing_id})
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_data()
    assert raised.value.reason == SampleFailureReason.SITE_INVALID


@pytest.mark.parametrize("changes", ["wrong_nearest", "circle_overlap", "circle_isolated", "rest_distant"])
def test_real_geography_measurements_refuse_invalid_sites(changes: str, sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    """Runs PostGIS distance queries for association, radius and amenity limits."""
    first, second, rest, circle = SAMPLE_DEFINITIONS
    if changes == "wrong_nearest":
        target = first
        identifier = second.reference_way_id
    elif changes == "circle_overlap":
        target = circle
        identifier = first.reference_way_id
    elif changes == "circle_isolated":
        target = second
        identifier = circle.reference_way_id
    else:
        monkeypatch.setattr(sample_data, "SAMPLE_DEFINITIONS", (first, second, replace(rest, latitude=50.07, longitude=20.00), circle))
        with pytest.raises(SampleDataFailure) as raised:
            apply_sample_data()
        assert raised.value.reason == SampleFailureReason.SITE_INVALID
        return
    geog = f"SRID=4326;LINESTRING({target.longitude} {target.latitude - 0.000001}, {target.longitude} {target.latitude + 0.000001})"
    if changes == "circle_overlap":
        geog = f"SRID=4326;LINESTRING({first.longitude} {first.latitude}, {circle.longitude} {circle.latitude})"
    elif changes == "circle_isolated":
        geog = "SRID=4326;LINESTRING(20.005 50.07, 20.006 50.07)"
    with schema_owner_engine.begin() as connection:
        if changes == "wrong_nearest":
            connection.execute(
                text("UPDATE osm_way SET geog = ST_GeogFromText(:geog) WHERE id = :id"),
                {"id": first.reference_way_id, "geog": f"SRID=4326;LINESTRING({first.longitude + 0.0001} {first.latitude}, {first.longitude + 0.0001} {first.latitude + 0.00001})"},
            )
        connection.execute(text("UPDATE osm_way SET geog = ST_GeogFromText(:geog) WHERE id = :id"), {"id": identifier, "geog": geog})
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_data()
    assert raised.value.reason == SampleFailureReason.SITE_INVALID


def test_changed_existing_definition_and_missing_history_are_not_repaired(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Refuses changed content and missing original author history on real rows."""
    apply_sample_data()
    with schema_owner_engine.begin() as connection:
        connection.execute(text("UPDATE fact SET description = :description WHERE id = -1"), {"description": "Invented changed fixture content"})
    with pytest.raises(SampleDataFailure) as changed:
        apply_sample_data()
    assert changed.value.reason == SampleFailureReason.CONTENT_MISMATCH
    with schema_owner_engine.begin() as connection:
        connection.execute(text("UPDATE fact SET description = :description WHERE id = -1"), {"description": SAMPLE_DEFINITIONS[0].description})
        connection.execute(text("DELETE FROM vote WHERE fact_id = -1"))
    with pytest.raises(SampleDataFailure) as missing:
        apply_sample_data()
    assert missing.value.reason == SampleFailureReason.INITIAL_VOTE_INVALID


def test_unrelated_occupied_identifier_is_not_overwritten(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Keeps an invented non-sample collision unchanged and inserts no other fact."""
    with schema_owner_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO fact (id, fact_type, source, geog, description, is_sample, idempotency_key, is_removed_from_osm, created_at, created_at_utc_offset_minutes) OVERRIDING SYSTEM VALUE VALUES (-1, 'rest_place', 'user_report', ST_SetSRID(ST_MakePoint(19.9947175, 50.06741305), 4326)::geography, :description, false, :key, false, :instant, :offset)"
            ),
            {"description": "Invented unrelated fixture", "key": sha256(b"sample fixture collision").digest(), **sample_critical_dataset.build_time_parameters()},
        )
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_data()
    assert raised.value.reason == SampleFailureReason.IDENTITY_COLLISION
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM fact WHERE id = ANY(CAST(:ids AS bigint[]))"), {"ids": [-1, -2, -3, -4]}).scalar_one() == 1
        assert connection.execute(text("SELECT description FROM fact WHERE id = -1")).scalar_one() == "Invented unrelated fixture"


def test_failure_between_fact_and_vote_batches_leaves_no_partial_samples(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Injects a transport-layer failure after real fact inserts but before votes."""

    def apply_failure(_connection: Connection, _cursor: object, statement: str, _parameters: object, _context: object, _executemany: bool) -> None:
        """Stops only the initial vote batch on the real runtime connection."""
        if statement.lstrip().startswith("INSERT INTO vote"):
            raise SQLAlchemyError("Invented failure before the vote batch.")

    event.listen(Engine, "before_cursor_execute", apply_failure)
    try:
        with pytest.raises(SampleDataFailure) as raised:
            apply_sample_data()
        assert raised.value.reason == SampleFailureReason.DATABASE_FAILED
        assert raised.value.commit_state == SampleCommitState.ROLLED_BACK
    finally:
        event.remove(Engine, "before_cursor_execute", apply_failure)
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM fact WHERE id = ANY(CAST(:ids AS bigint[]))"), {"ids": [-1, -2, -3, -4]}).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM vote WHERE fact_id = ANY(CAST(:ids AS bigint[]))"), {"ids": [-1, -2, -3, -4]}).scalar_one() == 0


def test_concurrent_invocations_have_one_fact_and_original_vote_per_identifier(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Forces simultaneous snapshots and permits only explicit serialization failure."""
    barrier = Barrier(2, timeout=10)
    gate = Lock()
    arrived = 0

    def apply_snapshot_barrier(_connection: Connection, _cursor: object, statement: str, _parameters: object, _context: object, _executemany: bool) -> None:
        """Makes two real initial prerequisite reads acquire concurrent snapshots."""
        nonlocal arrived
        should_wait = False
        if "WITH point AS" in statement:
            with gate:
                if arrived < 2:
                    arrived += 1
                    should_wait = True
        if should_wait:
            barrier.wait()

    def apply_attempt() -> SampleDataOutcome | SampleFailureReason:
        """Keeps only safe outcome evidence from each real concurrent invocation."""
        try:
            return apply_sample_data().outcome
        except SampleDataFailure as failure:
            assert failure.commit_state == SampleCommitState.ROLLED_BACK
            return failure.reason

    event.listen(Engine, "after_cursor_execute", apply_snapshot_barrier)
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _index: apply_attempt(), range(2)))
    finally:
        event.remove(Engine, "after_cursor_execute", apply_snapshot_barrier)
    assert SampleDataOutcome.CREATED in outcomes
    assert all(outcome in (SampleDataOutcome.CREATED, SampleDataOutcome.UNCHANGED, SampleFailureReason.DATABASE_FAILED) for outcome in outcomes)
    assert apply_sample_data().outcome == SampleDataOutcome.UNCHANGED
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM fact WHERE id = ANY(CAST(:ids AS bigint[]))"), {"ids": [-1, -2, -3, -4]}).scalar_one() == 4
        assert connection.execute(text("SELECT count(*) FROM vote WHERE fact_id = ANY(CAST(:ids AS bigint[]))"), {"ids": [-1, -2, -3, -4]}).scalar_one() == 4
