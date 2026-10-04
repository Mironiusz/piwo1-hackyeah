"""
Disposable sample network and ownership-bounded cleanup for critical runs.

The network holds the eight reference ways of the samples, each shortened to the nodes around its sample point, with the
node positions of the public OpenStreetMap response recorded in plans/sample_data/SAMPLE_DATA_OSM_EVIDENCE.md
(OpenStreetMap contributors, ODbL). Only the lowered kerb next to S-5 carries a kerb point; the way states are invented.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from accessibility_db.closed_lists import KerbPointState, WayBarrierState
from accessibility_db.tables import OffsetInstant, build_offset_instant
from sqlalchemy import Connection, text

from common_sample_data import SampleFactRow
from service.sample_data import SAMPLE_DEFINITIONS, build_sample_insert_rows

SAMPLE_FIXTURE_COPY_ID = -10001
SAMPLE_FIXTURE_LOCK_NAMESPACE = 1346983759
SAMPLE_FIXTURE_LOCK_KEY = 3
SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID = 317034340
SAMPLE_FIXTURE_NODES: dict[int, tuple[float, float]] = {
    11337808279: (50.067608, 19.9887602),
    3659608137: (50.0676121, 19.988836),
    8593724948: (50.0676157, 19.9889097),
    2915697524: (50.066515, 19.9965575),
    317034335: (50.0664819, 19.9965783),
    317034336: (50.0662623, 19.9966932),
    12903379330: (50.0662529, 19.9967953),
    317034337: (50.0662184, 19.9968267),
    930454119: (50.0669076, 19.994923),
    317034333: (50.0668475, 19.9952253),
    12903379354: (50.0667527, 19.9954863),
    3654754211: (50.0666188, 19.9958877),
    12903379351: (50.0665653, 19.9959153),
    12903379352: (50.0665474, 19.995469),
    317034307: (50.0664789, 19.9935115),
    6878813259: (50.0664742, 19.9933883),
    8738705859: (50.0657896, 19.9970643),
    3654754191: (50.065753, 19.9970781),
    317034340: (50.0657334, 19.9970861),
    8738705860: (50.0656769, 19.9971093),
    3659601891: (50.0676214, 19.9890268),
    3659602695: (50.0676231, 19.9890461),
    2964227322: (50.0676492, 19.9895793),
    11273287982: (50.0760419, 20.0026561),
    966736200: (50.0760252, 20.0026667),
    3123458028: (50.0758344, 20.0028237),
    966736056: (50.075559, 20.0030613),
    8593724940: (50.0674958, 19.9890893),
    3659610431: (50.067503, 19.9890885),
    10773395335: (50.0675733, 19.9890519),
}
SAMPLE_FIXTURE_WAYS: dict[int, tuple[int, ...]] = {
    1222443126: (11337808279, 3659608137, 8593724948),
    926589685: (2915697524, 317034335, 317034336, 12903379330, 317034337),
    28837534: (930454119, 317034333, 12903379354, 3654754211),
    360935725: (12903379351, 12903379352, 317034307, 6878813259),
    252778084: (8738705859, 3654754191, 317034340, 8738705860),
    306727457: (3659601891, 3659602695, 2964227322),
    83093546: (11273287982, 966736200, 3123458028, 966736056),
    1222443122: (8593724940, 3659610431, 10773395335, 3659601891),
}

INSERT_FIXTURE_COPY_SQL = """
INSERT INTO osm_copy (id, state_at, state_at_utc_offset_minutes, file_name, made_current_at, made_current_at_utc_offset_minutes)
OVERRIDING SYSTEM VALUE
VALUES (:copy_id, :instant, :offset, :marker, :instant, :offset)
"""
INSERT_FIXTURE_NODE_SQL = """
INSERT INTO osm_node (id, geog, kerb_point, is_crossing, is_on_motor_traffic_way)
VALUES (:node_id, ST_GeogFromText(:geog), :kerb_point, false, false)
"""
INSERT_FIXTURE_WAY_SQL = """
INSERT INTO osm_way (id, geog, stairs_state, poor_surface_state, steep_incline_state, narrow_passage_state,
                     is_marked_wheelchair_no, is_motor_traffic, is_crossing)
VALUES (:way_id, ST_GeogFromText(:geog), :stairs, :other, :other, :other, false, false, false)
"""
INSERT_FIXTURE_MEMBERSHIP_SQL = "INSERT INTO osm_way_node (way_id, sequence_index, node_id) VALUES (:way_id, :sequence_index, :node_id)"
APPLY_FIXTURE_WAY_GEOMETRY_SQL = """
UPDATE osm_way SET geog = (
    SELECT ST_MakeLine(n.geog::geometry ORDER BY m.sequence_index)::geography
    FROM osm_way_node AS m JOIN osm_node AS n ON n.id = m.node_id
    WHERE m.way_id = :way_id
)
WHERE id = :way_id
"""
SELECT_FIXTURE_OCCUPANCY_SQL = """
SELECT EXISTS (SELECT 1 FROM osm_copy) OR EXISTS (SELECT 1 FROM osm_way) OR EXISTS (SELECT 1 FROM osm_node)
       OR EXISTS (SELECT 1 FROM fact WHERE id = ANY(CAST(:sample_ids AS bigint[])))
"""
SELECT_FIXTURE_COPY_OWNERSHIP_SQL = """
SELECT EXISTS (SELECT 1 FROM osm_copy WHERE id = :copy_id AND file_name = :marker)
       AND NOT EXISTS (SELECT 1 FROM osm_copy WHERE id <> :copy_id)
"""
OWNED_FACTS_SQL = """
jsonb_to_recordset(CAST(:owned AS jsonb)) AS o(fact_id bigint, created_at timestamptz, created_at_utc_offset_minutes smallint)
"""
SELECT_FIXTURE_COLLISION_SQL = f"""
SELECT EXISTS (
    SELECT 1 FROM fact AS f JOIN {OWNED_FACTS_SQL} ON f.id = o.fact_id
    WHERE NOT (f.created_at = o.created_at AND f.created_at_utc_offset_minutes = o.created_at_utc_offset_minutes)
)
"""
DELETE_FIXTURE_VOTES_SQL = f"""
DELETE FROM vote WHERE fact_id IN (
    SELECT f.id FROM fact AS f JOIN {OWNED_FACTS_SQL}
      ON f.id = o.fact_id AND f.created_at = o.created_at AND f.created_at_utc_offset_minutes = o.created_at_utc_offset_minutes
)
"""
DELETE_FIXTURE_FACTS_SQL = f"""
DELETE FROM fact AS f USING {OWNED_FACTS_SQL}
WHERE f.id = o.fact_id AND f.created_at = o.created_at AND f.created_at_utc_offset_minutes = o.created_at_utc_offset_minutes
"""
DELETE_FIXTURE_LINKS_SQL = "DELETE FROM osm_way_node WHERE way_id = ANY(CAST(:way_ids AS bigint[]))"
DELETE_FIXTURE_WAYS_SQL = "DELETE FROM osm_way WHERE id = ANY(CAST(:way_ids AS bigint[]))"
DELETE_FIXTURE_NODES_SQL = "DELETE FROM osm_node WHERE id = ANY(CAST(:node_ids AS bigint[]))"
DELETE_FIXTURE_COPY_SQL = "DELETE FROM osm_copy WHERE id = :copy_id AND file_name = :marker"


def build_point_text(node_id: int, position: tuple[float, float] | None = None) -> str:
    """Writes the position of a fixture node, or a given latitude and longitude, as EWKT."""
    latitude, longitude = SAMPLE_FIXTURE_NODES[node_id] if position is None else position
    return f"SRID=4326;POINT({longitude} {latitude})"


def build_line_text(node_ids: tuple[int, ...]) -> str:
    """Writes the line through fixture nodes in their order as EWKT."""
    return "SRID=4326;LINESTRING(" + ", ".join(f"{SAMPLE_FIXTURE_NODES[node_id][1]} {SAMPLE_FIXTURE_NODES[node_id][0]}" for node_id in node_ids) + ")"


@dataclass
class SampleCriticalDataset:
    """The invented clock, copy marker and exact keys owned by one sample fixture."""

    marker: str
    business_now: datetime
    original_loading_at: datetime
    durable_setup_completed: bool = False

    def fetch_business_now(self) -> datetime:
        """Supplies an invented aware clock while exercising the real provider."""
        return self.business_now

    def build_copy_parameters(self) -> dict[str, object]:
        """Builds the copy marker values, dated at the invented first loading."""
        copy_at = build_offset_instant(self.original_loading_at)
        return {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": self.marker, "instant": copy_at.instant, "offset": copy_at.utc_offset_minutes}

    def build_original_rows(self) -> tuple[SampleFactRow, ...]:
        """Gives the fact rows the first loading writes, whose creation pairs mark the facts this fixture owns."""
        fact_rows, _vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, self.original_loading_at)
        return fact_rows

    def build_created_at(self, fact_id: int) -> OffsetInstant:
        """Gives the creation pair the first loading writes for one sample fact."""
        return next(row.created_at for row in self.build_original_rows() if row.definition.fact_id == fact_id)

    def build_owned_facts(self) -> str:
        """Serializes the owned fact identifiers with their original creation pairs as one bound parameter."""
        return json.dumps(
            [
                {"fact_id": row.definition.fact_id, "created_at": row.created_at.instant.isoformat(), "created_at_utc_offset_minutes": row.created_at.utc_offset_minutes}
                for row in self.build_original_rows()
            ]
        )

    def apply_cleanup(self, connection: Connection) -> None:
        """Deletes only the fixture's marker, network keys and the facts with their original creation pairs."""
        owns_copy = connection.execute(text(SELECT_FIXTURE_COPY_OWNERSHIP_SQL), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": self.marker}).scalar_one()
        if not owns_copy:
            if self.durable_setup_completed:
                raise RuntimeError("Sample fixture cleanup cannot establish ownership of its missing copy marker.")
            return
        owned = {"owned": self.build_owned_facts()}
        if connection.execute(text(SELECT_FIXTURE_COLLISION_SQL), owned).scalar_one():
            raise RuntimeError("Sample fixture cleanup refused content with a different creation identity.")
        connection.execute(text(DELETE_FIXTURE_VOTES_SQL), owned)
        connection.execute(text(DELETE_FIXTURE_FACTS_SQL), owned)
        way_parameters = {"way_ids": list(SAMPLE_FIXTURE_WAYS)}
        connection.execute(text(DELETE_FIXTURE_LINKS_SQL), way_parameters)
        connection.execute(text(DELETE_FIXTURE_WAYS_SQL), way_parameters)
        connection.execute(text(DELETE_FIXTURE_NODES_SQL), {"node_ids": list(SAMPLE_FIXTURE_NODES)})
        connection.execute(text(DELETE_FIXTURE_COPY_SQL), {"copy_id": SAMPLE_FIXTURE_COPY_ID, "marker": self.marker})


def build_sample_critical_dataset(business_now: datetime) -> SampleCriticalDataset:
    """Builds an invented clock with whole milliseconds and a unique local copy marker."""
    marker = f"sample-fixture-{uuid4().hex}"
    clock = business_now.replace(microsecond=int(uuid4().int % 1000) * 1000)
    return SampleCriticalDataset(marker, clock, clock.replace(microsecond=0))


def apply_sample_network_fixture(connection: Connection, dataset: SampleCriticalDataset) -> None:
    """Seeds the copy marker, nodes, ways and memberships only after refusing an occupied fixture environment."""
    occupied = connection.execute(text(SELECT_FIXTURE_OCCUPANCY_SQL), {"sample_ids": [item.fact_id for item in SAMPLE_DEFINITIONS]}).scalar_one()
    if occupied:
        raise RuntimeError("Sample critical fixtures require an empty current copy/network and free reserved sample identifiers.")
    connection.execute(text(INSERT_FIXTURE_COPY_SQL), dataset.build_copy_parameters())
    connection.execute(
        text(INSERT_FIXTURE_NODE_SQL),
        [
            {"node_id": node_id, "geog": build_point_text(node_id), "kerb_point": KerbPointState.LOWERED.value if node_id == SAMPLE_FIXTURE_LOWERED_KERB_NODE_ID else None}
            for node_id in SAMPLE_FIXTURE_NODES
        ],
    )
    connection.execute(
        text(INSERT_FIXTURE_WAY_SQL),
        [
            {"way_id": way_id, "geog": build_line_text(node_ids), "stairs": WayBarrierState.ABSENT_BY_DEFAULT.value, "other": WayBarrierState.UNKNOWN.value}
            for way_id, node_ids in SAMPLE_FIXTURE_WAYS.items()
        ],
    )
    connection.execute(
        text(INSERT_FIXTURE_MEMBERSHIP_SQL),
        [{"way_id": way_id, "sequence_index": index, "node_id": node_id} for way_id, node_ids in SAMPLE_FIXTURE_WAYS.items() for index, node_id in enumerate(node_ids)],
    )
