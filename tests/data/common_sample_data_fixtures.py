"""Disposable sample network and ownership-bounded cleanup for critical runs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from accessibility_db.closed_lists import WayBarrierState
from accessibility_db.tables import OffsetInstant, build_offset_instant
from sqlalchemy import Connection, text

from service.sample_data import SAMPLE_DEFINITIONS

SAMPLE_FIXTURE_COPY_ID = -10001
SAMPLE_FIXTURE_LOCK_NAMESPACE = 1346983759
SAMPLE_FIXTURE_LOCK_KEY = 3

INSERT_FIXTURE_COPY_SQL = """
INSERT INTO osm_copy (id, state_at, state_at_utc_offset_minutes, file_name, made_current_at, made_current_at_utc_offset_minutes)
OVERRIDING SYSTEM VALUE
VALUES (:copy_id, :instant, :offset, :marker, :instant, :offset)
"""
INSERT_FIXTURE_WAY_SQL = """
INSERT INTO osm_way (id, geog, stairs_state, poor_surface_state, steep_incline_state, narrow_passage_state,
                     is_marked_wheelchair_no, is_motor_traffic, is_crossing)
VALUES (:way_id, ST_GeogFromText(:geog), :stairs, :surface, :other, :other, false, false, false)
"""
SELECT_FIXTURE_OCCUPANCY_SQL = """
SELECT EXISTS (SELECT 1 FROM osm_copy) OR EXISTS (SELECT 1 FROM osm_way)
       OR EXISTS (SELECT 1 FROM fact WHERE id = ANY(CAST(:sample_ids AS bigint[])))
"""
DELETE_FIXTURE_VOTES_SQL = """
DELETE FROM vote WHERE fact_id IN (
    SELECT id FROM fact WHERE id = ANY(CAST(:sample_ids AS bigint[]))
      AND created_at = :instant AND created_at_utc_offset_minutes = :offset
)
"""
DELETE_FIXTURE_FACTS_SQL = """
DELETE FROM fact WHERE id = ANY(CAST(:sample_ids AS bigint[]))
  AND created_at = :instant AND created_at_utc_offset_minutes = :offset
"""
DELETE_FIXTURE_LINKS_SQL = "DELETE FROM osm_way_node WHERE way_id = ANY(CAST(:way_ids AS bigint[]))"
DELETE_FIXTURE_WAYS_SQL = "DELETE FROM osm_way WHERE id = ANY(CAST(:way_ids AS bigint[]))"
DELETE_FIXTURE_COPY_SQL = "DELETE FROM osm_copy WHERE id = :copy_id AND file_name = :marker"


@dataclass
class SampleCriticalDataset:
    """The invented clock, copy marker and exact keys owned by one sample fixture."""

    marker: str
    business_now: datetime
    original_created_at: OffsetInstant
    durable_setup_completed: bool = False

    def fetch_business_now(self) -> datetime:
        """Supplies an invented aware clock while exercising the real provider."""
        return self.business_now

    def build_time_parameters(self) -> dict[str, object]:
        """Builds the original creation predicate used for safe cleanup."""
        return {"instant": self.original_created_at.instant, "offset": self.original_created_at.utc_offset_minutes}

    def apply_cleanup(self, connection: Connection) -> None:
        """Deletes only the fixture's marker, keys and original creation pair."""
        owns_copy = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM osm_copy WHERE id = :copy_id AND file_name = :marker) AND NOT EXISTS (SELECT 1 FROM osm_copy WHERE id <> :copy_id)"),
            {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": self.marker},
        ).scalar_one()
        if not owns_copy:
            if self.durable_setup_completed:
                raise RuntimeError("Sample fixture cleanup cannot establish ownership of its missing copy marker.")
            return
        sample_parameters = {"sample_ids": [item.fact_id for item in SAMPLE_DEFINITIONS], **self.build_time_parameters()}
        collision = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM fact WHERE id = ANY(CAST(:sample_ids AS bigint[])) AND NOT (created_at = :instant AND created_at_utc_offset_minutes = :offset))"), sample_parameters
        ).scalar_one()
        if collision:
            raise RuntimeError("Sample fixture cleanup refused content with a different creation identity.")
        connection.execute(text(DELETE_FIXTURE_VOTES_SQL), sample_parameters)
        connection.execute(text(DELETE_FIXTURE_FACTS_SQL), sample_parameters)
        way_parameters = {"way_ids": list({item.reference_way_id for item in SAMPLE_DEFINITIONS})}
        connection.execute(text(DELETE_FIXTURE_LINKS_SQL), way_parameters)
        connection.execute(text(DELETE_FIXTURE_WAYS_SQL), way_parameters)
        connection.execute(text(DELETE_FIXTURE_COPY_SQL), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": self.marker})


def build_sample_critical_dataset(month: int) -> SampleCriticalDataset:
    """Builds an invented winter or summer clock and a unique local copy marker."""
    marker = f"sample-fixture-{uuid4().hex}"
    business_now = datetime(2026, month, 10, 8, 0, 0, int(uuid4().int % 1000) * 1000, tzinfo=ZoneInfo("Europe/Warsaw"))
    return SampleCriticalDataset(marker, business_now, build_offset_instant(business_now))


def apply_sample_network_fixture(connection: Connection, dataset: SampleCriticalDataset) -> None:
    """Seeds three invented lines only after refusing an occupied fixture environment."""
    occupied = connection.execute(text(SELECT_FIXTURE_OCCUPANCY_SQL), {"sample_ids": [item.fact_id for item in SAMPLE_DEFINITIONS]}).scalar_one()
    if occupied:
        raise RuntimeError("Sample critical fixtures require an empty current copy/network and free reserved sample identifiers.")
    connection.execute(text(INSERT_FIXTURE_COPY_SQL), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": dataset.marker, **dataset.build_time_parameters()})
    ways: list[dict[str, object]] = []
    for definition in (SAMPLE_DEFINITIONS[0], SAMPLE_DEFINITIONS[1], SAMPLE_DEFINITIONS[3]):
        geog = f"SRID=4326;LINESTRING({definition.longitude} {definition.latitude - 0.00001}, {definition.longitude} {definition.latitude + 0.00001})"
        ways.append(
            {"way_id": definition.reference_way_id, "geog": geog, "stairs": WayBarrierState.ABSENT_BY_DEFAULT.value, "surface": WayBarrierState.ABSENT.value, "other": WayBarrierState.UNKNOWN.value}
        )
    connection.execute(text(INSERT_FIXTURE_WAY_SQL), ways)
