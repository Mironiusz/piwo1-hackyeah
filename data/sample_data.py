"""Reads sample snapshots and performs bound batch inserts in one transaction."""

import json
from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import cast

from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict, WayBarrierState
from accessibility_db.tables import OffsetInstant
from sqlalchemy import Connection, RowMapping, text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from common_sample_data import (
    SAMPLE_POINT_ASSOCIATION_DISTANCE_M,
    SampleCommitState,
    SampleDataFailure,
    SampleDataResult,
    SampleDefinition,
    SampleFailureReason,
    SampleNearbyWay,
    SampleNetworkPrerequisites,
    StoredInitialVote,
    StoredSample,
    build_sample_voter_hash,
)

SELECT_SAMPLE_PREREQUISITES_SQL = """
WITH point AS (
    SELECT ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography AS geog
), nearby AS (
    SELECT w.id, ST_Distance(w.geog, p.geog) AS distance_m
    FROM osm_way AS w CROSS JOIN point AS p
    WHERE ST_DWithin(w.geog, p.geog, :association_distance_m)
    ORDER BY distance_m, w.id
    LIMIT 2
)
SELECT EXISTS (SELECT 1 FROM osm_copy) AS has_copy,
       EXISTS (SELECT 1 FROM osm_way WHERE id = :reference_way_id) AS reference_exists,
       (SELECT poor_surface_state FROM osm_way WHERE id = :reference_way_id) AS poor_surface_state,
       ARRAY(SELECT id FROM nearby ORDER BY distance_m, id) AS nearest_ids,
       ARRAY(SELECT distance_m FROM nearby ORDER BY distance_m, id) AS nearest_distances,
       (SELECT ST_Distance(w.geog, p.geog) FROM osm_way AS w CROSS JOIN point AS p WHERE w.id = :reference_way_id) AS reference_distance_m,
       (SELECT ST_Distance(w.geog, p.geog) FROM osm_way AS w CROSS JOIN point AS p WHERE w.id = :contradiction_way_id) AS contradiction_path_distance_m
"""

SELECT_STORED_SAMPLES_SQL = """
SELECT id, fact_type, source, ST_Y(geog::geometry) AS latitude, ST_X(geog::geometry) AS longitude,
       geozone_radius_m, description, step_count, is_sample, idempotency_key,
       osm_element_type, osm_element_id, osm_edited_on, is_removed_from_osm,
       created_at, created_at_utc_offset_minutes
FROM fact
WHERE id = ANY(CAST(:sample_ids AS bigint[]))
"""

SELECT_INITIAL_SAMPLE_VOTES_SQL = """
SELECT v.fact_id, v.verdict, v.is_cast_with_account, v.account_id, v.voter_hash,
       v.cast_at, v.cast_at_utc_offset_minutes
FROM vote AS v
JOIN jsonb_to_recordset(CAST(:authors AS jsonb)) AS a(fact_id bigint, voter_hash_hex text)
  ON v.fact_id = a.fact_id AND v.voter_hash = decode(a.voter_hash_hex, 'hex')
ORDER BY v.fact_id, v.cast_at, v.id
"""

INSERT_SAMPLE_FACTS_SQL = """
INSERT INTO fact (id, fact_type, source, geog, geozone_radius_m, description, step_count,
                  is_sample, idempotency_key, osm_element_type, osm_element_id, osm_edited_on,
                  is_removed_from_osm, created_at, created_at_utc_offset_minutes)
OVERRIDING SYSTEM VALUE
SELECT d.fact_id, CAST(d.fact_type AS fact_type), CAST(:source AS fact_source),
       ST_SetSRID(ST_MakePoint(d.longitude, d.latitude), 4326)::geography,
       d.geozone_radius_m, d.description, d.step_count,
       true, NULL, NULL, NULL, NULL, false, :created_at, :created_at_utc_offset_minutes
FROM jsonb_to_recordset(CAST(:definitions AS jsonb))
     AS d(fact_id bigint, fact_type text, latitude double precision, longitude double precision,
          geozone_radius_m smallint, description text, step_count smallint)
WHERE true
ON CONFLICT (id) DO NOTHING
RETURNING id
"""

INSERT_INITIAL_SAMPLE_VOTES_SQL = """
INSERT INTO vote (fact_id, verdict, is_cast_with_account, account_id, voter_hash, cast_at, cast_at_utc_offset_minutes)
SELECT a.fact_id, CAST(:verdict AS vote_verdict), false, NULL, decode(a.voter_hash_hex, 'hex'), :created_at, :created_at_utc_offset_minutes
FROM jsonb_to_recordset(CAST(:authors AS jsonb)) AS a(fact_id bigint, voter_hash_hex text)
RETURNING fact_id
"""


def fetch_sample_prerequisites(connection: Connection, definitions: Sequence[SampleDefinition]) -> tuple[SampleNetworkPrerequisites, ...]:
    """Reads measured path relations and current-copy presence for the fixed sites."""
    prerequisites: list[SampleNetworkPrerequisites] = []
    contradiction_way_id = definitions[0].reference_way_id
    for definition in definitions:
        parameters = {
            "latitude": definition.latitude,
            "longitude": definition.longitude,
            "reference_way_id": definition.reference_way_id,
            "contradiction_way_id": contradiction_way_id,
            "association_distance_m": SAMPLE_POINT_ASSOCIATION_DISTANCE_M,
        }
        row = connection.execute(text(SELECT_SAMPLE_PREREQUISITES_SQL), parameters).mappings().one()
        state = row["poor_surface_state"]
        candidates = tuple(SampleNearbyWay(way_id, distance) for way_id, distance in zip(row["nearest_ids"], row["nearest_distances"], strict=True))
        prerequisites.append(
            SampleNetworkPrerequisites(
                definition.fact_id,
                row["has_copy"],
                row["reference_exists"],
                WayBarrierState(state) if state is not None else None,
                candidates,
                row["reference_distance_m"],
                row["contradiction_path_distance_m"],
            )
        )
    return tuple(prerequisites)


def build_stored_sample(row: RowMapping) -> StoredSample:
    """Maps an explicit fact projection to the immutable reconciliation record."""
    element_type = row["osm_element_type"]
    return StoredSample(
        fact_id=cast(int, row["id"]),
        fact_type=FactType(row["fact_type"]),
        source=FactSource(row["source"]),
        latitude=cast(float, row["latitude"]),
        longitude=cast(float, row["longitude"]),
        geozone_radius_m=cast(int | None, row["geozone_radius_m"]),
        description=cast(str | None, row["description"]),
        step_count=cast(int | None, row["step_count"]),
        is_sample=cast(bool, row["is_sample"]),
        idempotency_key=cast(bytes | None, row["idempotency_key"]),
        osm_element_type=OsmElementType(element_type) if element_type is not None else None,
        osm_element_id=cast(int | None, row["osm_element_id"]),
        osm_edited_on=cast(date | None, row["osm_edited_on"]),
        is_removed_from_osm=cast(bool, row["is_removed_from_osm"]),
        created_at=OffsetInstant(cast(datetime, row["created_at"]), cast(int, row["created_at_utc_offset_minutes"])),
    )


def fetch_stored_samples(connection: Connection, sample_ids: Sequence[int]) -> dict[int, StoredSample]:
    """Reads fixed content without loading contributor or moderation data."""
    rows = connection.execute(text(SELECT_STORED_SAMPLES_SQL), {"sample_ids": list(sample_ids)}).mappings()
    return {sample.fact_id: sample for sample in (build_stored_sample(row) for row in rows)}


def build_sample_authors(sample_ids: Sequence[int]) -> str:
    """Serializes the invented author identities as one bound batch parameter."""
    return json.dumps([{"fact_id": sample_id, "voter_hash_hex": build_sample_voter_hash(sample_id).hex()} for sample_id in sample_ids])


def fetch_initial_sample_votes(connection: Connection, definitions: Sequence[SampleDefinition]) -> dict[int, tuple[StoredInitialVote, ...]]:
    """Reads only historical votes of the reserved fictional authors."""
    rows = connection.execute(text(SELECT_INITIAL_SAMPLE_VOTES_SQL), {"authors": build_sample_authors(tuple(item.fact_id for item in definitions))}).mappings()
    votes: dict[int, tuple[StoredInitialVote, ...]] = {}
    for row in rows:
        vote = StoredInitialVote(
            row["fact_id"],
            VoteVerdict(row["verdict"]),
            row["is_cast_with_account"],
            row["account_id"],
            row["voter_hash"],
            OffsetInstant(row["cast_at"], row["cast_at_utc_offset_minutes"]),
        )
        votes[vote.fact_id] = (*votes.get(vote.fact_id, ()), vote)
    return votes


def apply_sample_inserts(connection: Connection, definitions: Sequence[SampleDefinition], created_at: OffsetInstant) -> tuple[int, ...]:
    """Inserts missing facts and only their original author votes in bound batches."""
    payloads = [
        {
            "fact_id": item.fact_id,
            "fact_type": item.fact_type.value,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "geozone_radius_m": item.geozone_radius_m,
            "description": item.description,
            "step_count": item.step_count,
        }
        for item in definitions
    ]
    time_parameters = {"created_at": created_at.instant, "created_at_utc_offset_minutes": created_at.utc_offset_minutes}
    returned_ids: set[int] = set(connection.execute(text(INSERT_SAMPLE_FACTS_SQL), {"definitions": json.dumps(payloads), "source": FactSource.USER_REPORT.value, **time_parameters}).scalars())
    inserted_ids = tuple(item.fact_id for item in definitions if item.fact_id in returned_ids)
    if inserted_ids:
        voted_ids: set[int] = set(
            connection.execute(text(INSERT_INITIAL_SAMPLE_VOTES_SQL), {"authors": build_sample_authors(inserted_ids), "verdict": VoteVerdict.CONFIRM.value, **time_parameters}).scalars()
        )
        if voted_ids != returned_ids:
            raise SampleDataFailure(SampleFailureReason.INITIAL_VOTE_INVALID)
    return inserted_ids


def apply_sample_rollback(connection: Connection, reason: SampleFailureReason) -> SampleDataFailure:
    """Acknowledges rollback or preserves uncertainty when rollback itself fails."""
    if connection.invalidated or connection.closed:
        return SampleDataFailure(reason, SampleCommitState.UNKNOWN)
    transaction = connection.get_transaction()
    if transaction is None or not transaction.is_active:
        return SampleDataFailure(reason, SampleCommitState.UNKNOWN)
    try:
        connection.rollback()
    except SQLAlchemyError:
        return SampleDataFailure(reason, SampleCommitState.UNKNOWN)
    return SampleDataFailure(reason, SampleCommitState.ROLLED_BACK)


def apply_sample_connection(connection: Connection, action: Callable[[Connection], SampleDataResult]) -> SampleDataResult:
    """Executes one action and distinguishes acknowledged commit from lost evidence."""
    connection.execution_options(isolation_level="REPEATABLE READ")
    connection.begin()
    try:
        result = action(connection)
    except SampleDataFailure as failure:
        raise apply_sample_rollback(connection, failure.reason) from None
    except SQLAlchemyError:
        raise apply_sample_rollback(connection, SampleFailureReason.DATABASE_FAILED) from None
    except Exception:
        rollback_failure = apply_sample_rollback(connection, SampleFailureReason.DATABASE_FAILED)
        if rollback_failure.commit_state == SampleCommitState.UNKNOWN:
            raise rollback_failure from None
        raise
    try:
        connection.commit()
    except DBAPIError as failure:
        sqlstate = getattr(failure.orig, "sqlstate", None)
        if sqlstate in ("40001", "40P01") and not failure.connection_invalidated:
            raise apply_sample_rollback(connection, SampleFailureReason.DATABASE_FAILED) from None
        raise SampleDataFailure(SampleFailureReason.COMMIT_UNKNOWN, SampleCommitState.UNKNOWN) from None
    except SQLAlchemyError:
        raise SampleDataFailure(SampleFailureReason.COMMIT_UNKNOWN, SampleCommitState.UNKNOWN) from None
    except Exception:
        raise SampleDataFailure(SampleFailureReason.COMMIT_UNKNOWN, SampleCommitState.UNKNOWN) from None
    return result


def apply_sample_transaction(action: Callable[[Connection], SampleDataResult]) -> SampleDataResult:
    """Uses the shared engine for a stable snapshot without adding automatic retries."""
    from data.engine import build_engine

    try:
        connection = build_engine(5000).connect()
    except SQLAlchemyError:
        raise SampleDataFailure(SampleFailureReason.DATABASE_FAILED) from None
    with connection:
        return apply_sample_connection(connection, action)
