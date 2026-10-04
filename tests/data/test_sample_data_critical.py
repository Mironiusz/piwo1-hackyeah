"""Exercises the real sample provider through the restricted runtime engine and the local-owner engine."""

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from threading import Barrier, Lock
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.tables import OffsetInstant
from pyproj import Geod
from sqlalchemy import Connection, Engine, Row, event, text
from sqlalchemy.exc import SQLAlchemyError

from common_sample_data import SampleCommitState, SampleDataFailure, SampleDataOutcome, SampleDataResult, SampleFailureReason
from data.route_facts import StoredVote, fetch_fact_votes
from service.fact_status import FactStatus, resolve_fact_status
from service.sample_data import SAMPLE_DEFINITIONS, apply_sample_data, build_sample_insert_rows, build_shifted_instant
from tests.data.common_sample_data_fixtures import (
    APPLY_FIXTURE_WAY_GEOMETRY_SQL,
    INSERT_FIXTURE_COPY_SQL,
    SAMPLE_FIXTURE_COPY_ID,
    SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID,
    SAMPLE_FIXTURE_NODES,
    SampleCriticalDataset,
    build_point_text,
)

pytestmark = pytest.mark.critical

WARSAW = ZoneInfo("Europe/Warsaw")
SAMPLE_IDS = (-1, -2, -3, -4, -5, -6, -7, -8)
INTENDED_STATUSES = {
    -1: (2.0, 0.0, FactStatus.CONFIRMED),
    -2: (1.0, 0.0, FactStatus.UNVERIFIED),
    -3: (2.0, 0.0, FactStatus.CONFIRMED),
    -4: (1.0, 1.0, FactStatus.DISPUTED),
    -5: (1.5, 0.0, FactStatus.UNVERIFIED),
    -6: (1.0, 0.0, FactStatus.UNVERIFIED),
    -7: (1.0, 1.0, FactStatus.DISPUTED),
    -8: (1.0, 0.0, FactStatus.UNVERIFIED),
}
SELECT_SAMPLE_FACTS_SQL = text(
    "SELECT id, fact_type, source, is_sample, description, step_count, geozone_radius_m, created_at, created_at_utc_offset_minutes, "
    "flagged_at, flagged_at_utc_offset_minutes, hidden_at, hidden_at_utc_offset_minutes FROM fact WHERE id = ANY(CAST(:ids AS bigint[])) ORDER BY id"
)
SELECT_SAMPLE_VOTES_SQL = text(
    "SELECT id, fact_id, verdict, is_cast_with_account, account_id, voter_hash, cast_at, cast_at_utc_offset_minutes FROM vote WHERE fact_id = ANY(CAST(:ids AS bigint[])) ORDER BY fact_id, id"
)
COUNT_SAMPLES_SQL = text("SELECT (SELECT count(*) FROM fact WHERE id = ANY(CAST(:ids AS bigint[]))), (SELECT count(*) FROM vote WHERE fact_id = ANY(CAST(:ids AS bigint[])))")


def fetch_sample_rows(engine: Engine) -> tuple[list[Row], list[Row]]:
    """Reads every sample fact with its moderation and every vote on the sample facts."""
    with engine.connect() as connection:
        return list(connection.execute(SELECT_SAMPLE_FACTS_SQL, {"ids": list(SAMPLE_IDS)})), list(connection.execute(SELECT_SAMPLE_VOTES_SQL, {"ids": list(SAMPLE_IDS)}))


def fetch_sample_counts(engine: Engine) -> tuple[int, int]:
    """Counts the facts on the reserved identifiers and the votes on them."""
    with engine.connect() as connection:
        facts, votes = connection.execute(COUNT_SAMPLES_SQL, {"ids": list(SAMPLE_IDS)}).one()
    return facts, votes


def fetch_sample_statuses(engine: Engine) -> dict[int, tuple[float, float, FactStatus]]:
    """Derives the status of every sample fact from its stored votes through the one rule of M4."""
    with engine.connect() as connection:
        votes = fetch_fact_votes(connection, SAMPLE_IDS)
    grouped: dict[int, list[StoredVote]] = defaultdict(list)
    for vote in votes:
        grouped[vote.fact_id].append(vote)
    results = {fact_id: resolve_fact_status(grouped[fact_id], False) for fact_id in SAMPLE_IDS}
    return {fact_id: (result.confirmations, result.denials, result.status) for fact_id, result in results.items()}


def build_pair(row: Row, name: str) -> OffsetInstant | None:
    """Reads one stored instant and offset pair of a row, or none when it is absent."""
    instant = getattr(row, name)
    return None if instant is None else OffsetInstant(instant, getattr(row, f"{name}_utc_offset_minutes"))


def apply_refused_loading(reason: SampleFailureReason, engine: Engine) -> None:
    """Runs the provider, expects an acknowledged rollback with the given reason, and checks that nothing was written."""
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_data()
    assert raised.value.reason == reason
    assert raised.value.commit_state == SampleCommitState.ROLLED_BACK
    assert fetch_sample_counts(engine) == (0, 0)


@pytest.mark.parametrize("sample_critical_dataset", [datetime(2026, 1, 10, 8, 0, tzinfo=WARSAW), datetime(2026, 10, 26, 10, 0, tzinfo=WARSAW)], indirect=True)
def test_first_loading_writes_the_dataset_and_repetitions_change_nothing(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Writes 8 facts and 25 votes with their own pairs, statuses and moderation, then leaves them unchanged now and on a later day."""
    assert apply_sample_data() == SampleDataResult(SampleDataOutcome.CREATED, 8, 0, 25, SAMPLE_IDS)
    facts, votes = fetch_sample_rows(schema_owner_engine)
    fact_rows, vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, sample_critical_dataset.original_loading_at)
    assert [row.id for row in facts] == sorted(SAMPLE_IDS)
    expected_facts = {row.definition.fact_id: row for row in fact_rows}
    for row in facts:
        expected = expected_facts[row.id]
        assert (row.fact_type, row.source, row.is_sample) == (expected.definition.fact_type.value, "user_report", True)
        assert (row.description, row.step_count, row.geozone_radius_m) == (expected.definition.description, expected.definition.step_count, expected.definition.geozone_radius_m)
        assert (build_pair(row, "created_at"), build_pair(row, "flagged_at"), build_pair(row, "hidden_at")) == (expected.created_at, expected.flagged_at, expected.hidden_at)
    stored_votes = Counter((row.fact_id, bytes(row.voter_hash), row.verdict, row.is_cast_with_account, row.account_id, build_pair(row, "cast_at")) for row in votes)
    assert stored_votes == Counter((row.fact_id, row.voter_hash, row.verdict.value, False, None, row.cast_at) for row in vote_rows)
    assert fetch_sample_statuses(schema_owner_engine) == INTENDED_STATUSES
    assert apply_sample_data() == SampleDataResult(SampleDataOutcome.UNCHANGED, 0, 8, 0, SAMPLE_IDS)
    sample_critical_dataset.business_now = (sample_critical_dataset.business_now.astimezone(UTC) + timedelta(days=1)).astimezone(WARSAW)
    assert apply_sample_data() == SampleDataResult(SampleDataOutcome.UNCHANGED, 0, 8, 0, SAMPLE_IDS)
    assert fetch_sample_rows(schema_owner_engine) == (facts, votes)


def test_retry_preserves_community_votes_and_moderation(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Keeps a live confirmation, a new flag, a restored and a newly hidden fact through another loading."""
    apply_sample_data()
    later = build_shifted_instant(sample_critical_dataset.original_loading_at, 5)
    parameters = {"instant": later.instant, "offset": later.utc_offset_minutes, "hash": sha256(b"invented sample fixture presenter").digest()}
    with schema_owner_engine.begin() as connection:
        connection.execute(
            text("INSERT INTO vote (fact_id, verdict, is_cast_with_account, voter_hash, cast_at, cast_at_utc_offset_minutes) VALUES (-5, 'confirm', false, :hash, :instant, :offset)"), parameters
        )
        connection.execute(text("UPDATE fact SET flagged_at = :instant, flagged_at_utc_offset_minutes = :offset WHERE id = -1"), parameters)
        connection.execute(text("UPDATE fact SET hidden_at = NULL, hidden_at_utc_offset_minutes = NULL WHERE id = -8"))
        connection.execute(text("UPDATE fact SET hidden_at = :instant, hidden_at_utc_offset_minutes = :offset WHERE id = -6"), parameters)
    facts, votes = fetch_sample_rows(schema_owner_engine)
    assert apply_sample_data().outcome == SampleDataOutcome.UNCHANGED
    assert fetch_sample_rows(schema_owner_engine) == (facts, votes)
    assert len(votes) == 26
    moderation = {row.id: (row.flagged_at is not None, row.hidden_at is not None) for row in facts}
    assert (moderation[-1], moderation[-6], moderation[-8]) == ((True, False), (True, True), (True, False))
    assert fetch_sample_statuses(schema_owner_engine)[-5] == (2.0, 0.0, FactStatus.CONFIRMED)


def test_missing_copy_is_a_visible_failure(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Refuses absent source metadata and restores the test-owned cleanup marker."""
    with schema_owner_engine.begin() as connection:
        connection.execute(text("DELETE FROM osm_copy WHERE id = :copy_id AND file_name = :marker"), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": sample_critical_dataset.marker})
    try:
        apply_refused_loading(SampleFailureReason.COPY_MISSING, schema_owner_engine)
    finally:
        with schema_owner_engine.begin() as connection:
            connection.execute(text(INSERT_FIXTURE_COPY_SQL), sample_critical_dataset.build_copy_parameters())


@pytest.mark.parametrize("missing_id", [926589685, 252778084, 83093546])
def test_missing_reference_way_fails_without_relocating_samples(missing_id: int, sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Refuses a point, the contradicted kerb or a geozone whose reference way the copy does not hold."""
    with schema_owner_engine.begin() as connection:
        connection.execute(text("DELETE FROM osm_way WHERE id = :id"), {"id": missing_id})
    apply_refused_loading(SampleFailureReason.SITE_INVALID, schema_owner_engine)


@pytest.mark.parametrize("kerb_point", ["high", "unknown", None])
def test_kerb_that_is_not_lowered_establishes_no_contradiction(kerb_point: str | None, sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Refuses S-5 when the kerb point next to it is high, unknown or no kerb point at all."""
    with schema_owner_engine.begin() as connection:
        connection.execute(text("UPDATE osm_node SET kerb_point = :kerb_point WHERE id = :id"), {"kerb_point": kerb_point, "id": SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID})
    apply_refused_loading(SampleFailureReason.CONTRADICTION_MISSING, schema_owner_engine)


def test_lowered_kerb_farther_than_5_m_establishes_no_contradiction(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Moves the lowered kerb to 6 m from S-5 along its way and refuses the contradiction."""
    kerb = SAMPLE_DEFINITIONS[4]
    latitude, longitude = SAMPLE_FIXTURE_NODES[SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID]
    geod = Geod(ellps="WGS84")
    azimuth, _back, _distance = geod.inv(kerb.longitude, kerb.latitude, longitude, latitude)
    moved_longitude, moved_latitude, _back_azimuth = geod.fwd(kerb.longitude, kerb.latitude, azimuth, 6.0)
    with schema_owner_engine.begin() as connection:
        connection.execute(
            text("UPDATE osm_node SET geog = ST_GeogFromText(:geog) WHERE id = :id"),
            {"geog": build_point_text(SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID, (moved_latitude, moved_longitude)), "id": SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID},
        )
        connection.execute(text(APPLY_FIXTURE_WAY_GEOMETRY_SQL), {"way_id": kerb.reference_way_id})
    apply_refused_loading(SampleFailureReason.CONTRADICTION_MISSING, schema_owner_engine)


@pytest.mark.parametrize("case", ["wrong_nearest", "geozone_outside"])
def test_real_geography_measurements_refuse_invalid_places(case: str, sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Runs the PostGIS measurements and refuses a point whose nearest way is another one, or a geozone that does not reach its way."""
    stairs, ramp, area = SAMPLE_DEFINITIONS[1], SAMPLE_DEFINITIONS[2], SAMPLE_DEFINITIONS[3]
    if case == "wrong_nearest":
        changes = {
            stairs.reference_way_id: f"SRID=4326;LINESTRING({stairs.longitude + 0.00005} {stairs.latitude - 0.00001}, {stairs.longitude + 0.00005} {stairs.latitude + 0.00001})",
            ramp.reference_way_id: f"SRID=4326;LINESTRING({stairs.longitude} {stairs.latitude - 0.00001}, {stairs.longitude} {stairs.latitude + 0.00001})",
        }
    else:
        changes = {area.reference_way_id: f"SRID=4326;LINESTRING({area.longitude} {area.latitude + 0.0003}, {area.longitude + 0.0001} {area.latitude + 0.0003})"}
    with schema_owner_engine.begin() as connection:
        for way_id, geog in changes.items():
            connection.execute(text("UPDATE osm_way SET geog = ST_GeogFromText(:geog) WHERE id = :id"), {"id": way_id, "geog": geog})
    apply_refused_loading(SampleFailureReason.SITE_INVALID, schema_owner_engine)


def test_unrelated_occupied_identifier_is_not_overwritten(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Keeps an invented non-sample row on a reserved identifier unchanged and inserts no other fact."""
    created_at = sample_critical_dataset.build_created_at(-1)
    kerb = SAMPLE_DEFINITIONS[0]
    with schema_owner_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO fact (id, fact_type, source, geog, description, is_sample, idempotency_key, is_removed_from_osm, created_at, created_at_utc_offset_minutes) "
                "OVERRIDING SYSTEM VALUE VALUES (-1, 'rest_place', 'user_report', ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography, :description, false, :key, false, :instant, :offset)"
            ),
            {
                "longitude": kerb.longitude,
                "latitude": kerb.latitude,
                "description": "Invented unrelated fixture",
                "key": sha256(b"sample fixture collision").digest(),
                "instant": created_at.instant,
                "offset": created_at.utc_offset_minutes,
            },
        )
    with pytest.raises(SampleDataFailure) as raised:
        apply_sample_data()
    assert raised.value.reason == SampleFailureReason.IDENTITY_COLLISION
    assert fetch_sample_counts(schema_owner_engine) == (1, 0)
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT description, is_sample FROM fact WHERE id = -1")).one() == ("Invented unrelated fixture", False)


def test_changed_content_and_broken_vote_history_are_not_repaired(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Refuses changed content and a missing sample vote on real rows instead of overwriting or refreshing them."""
    apply_sample_data()
    with schema_owner_engine.begin() as connection:
        connection.execute(text("UPDATE fact SET description = :description WHERE id = -2"), {"description": "Invented changed fixture content"})
    with pytest.raises(SampleDataFailure) as changed:
        apply_sample_data()
    assert changed.value.reason == SampleFailureReason.CONTENT_MISMATCH
    with schema_owner_engine.begin() as connection:
        connection.execute(text("UPDATE fact SET description = :description WHERE id = -2"), {"description": SAMPLE_DEFINITIONS[1].description})
        connection.execute(text("DELETE FROM vote WHERE id = (SELECT max(id) FROM vote WHERE fact_id = -3)"))
    with pytest.raises(SampleDataFailure) as missing:
        apply_sample_data()
    assert missing.value.reason == SampleFailureReason.INITIAL_VOTE_INVALID
    assert fetch_sample_counts(schema_owner_engine) == (8, 24)


def test_failure_between_fact_and_vote_batches_leaves_no_partial_samples(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Injects a failure after the real fact batch but before the vote batch."""

    def apply_failure(_connection: Connection, _cursor: object, statement: str, _parameters: object, _context: object, _executemany: bool) -> None:
        """Stops only the sample vote batch on the real runtime connection."""
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
    assert fetch_sample_counts(schema_owner_engine) == (0, 0)


def test_concurrent_invocations_leave_one_fact_per_identifier_and_one_vote_per_voter(sample_critical_dataset: SampleCriticalDataset, schema_owner_engine: Engine) -> None:
    """Forces simultaneous snapshots and permits only an explicit serialization failure of the loser."""
    barrier = Barrier(2, timeout=10)
    gate = Lock()
    arrived = 0

    def apply_snapshot_barrier(_connection: Connection, _cursor: object, statement: str, _parameters: object, _context: object, _executemany: bool) -> None:
        """Makes the first prerequisite read of both invocations take their snapshots together."""
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
    assert fetch_sample_counts(schema_owner_engine) == (8, 25)
    with schema_owner_engine.connect() as connection:
        assert connection.execute(text("SELECT count(DISTINCT (fact_id, voter_hash)) FROM vote WHERE fact_id = ANY(CAST(:ids AS bigint[]))"), {"ids": list(SAMPLE_IDS)}).scalar_one() == 25
