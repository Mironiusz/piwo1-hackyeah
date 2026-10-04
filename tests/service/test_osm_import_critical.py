"""
Run whole imports of invented sources against the freshly migrated local database of db/compose.yaml.

Publication commits and the service account may neither delete copy rows nor facts, so the scenario needs a database
without any copy and runs its imports in one ordered sequence with increasing source states. The Valhalla tools are
replaced by a step that writes the archive; everything else - reading, mapping, exclusion, publication, routing
directories and the pointer - is real.
"""

import asyncio
import hashlib
from collections.abc import Iterator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from zoneinfo import ZoneInfo

import httpx
import pytest
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError

from data.engine import build_import_engine
from data.locks import apply_import_exclusion
from data.osm_copy import fetch_osm_facts
from data.routing_data import fetch_routing_pointer
from service.osm_acquisition import OsmExtract
from service.osm_import import OsmImportSettings, apply_osm_import
from service.osm_publication import apply_osm_disappearance
from service.osm_routing_preparation import OsmPreparedCopy
from service.osm_source_validation import OsmSourceError
from tests.common_osm_source import INVENTED_RELATIONS_XML, apply_invented_osm_source

pytestmark = pytest.mark.critical

TIMESTAMP = 'timestamp="2026-10-03T00:00:00Z" version="1"'
BOUNDARY_NODES = "".join(f'<node id="{index}" lon="{lon}" lat="{lat}" {TIMESTAMP}/>' for index, (lon, lat) in enumerate(((19.9, 50), (20, 50), (20, 50.1), (19.9, 50.1)), 1))
BOUNDARY_WAY = f'<way id="1" {TIMESTAMP}><nd ref="1"/><nd ref="2"/><nd ref="3"/><nd ref="4"/><nd ref="1"/></way>'
NETWORK_NODES = f'<node id="5" lon="19.92" lat="50.02" {TIMESTAMP}/><node id="6" lon="19.94" lat="50.02" {TIMESTAMP}/>'
KERB_NODE = '<node id="7" lon="19.96" lat="50.02" {timestamp}>{tags}</node>'
KERB_TAGS = '<tag k="barrier" v="kerb"/><tag k="kerb" v="lowered"/>'
BENCH_NODE = f'<node id="8" lon="19.95" lat="50.05" {TIMESTAMP}><tag k="amenity" v="bench"/></node>'
SPUR_NODE = f'<node id="9" lon="19.97" lat="50.03" {TIMESTAMP}/>'
STAIRS_WAY = '<way id="10" {timestamp}><nd ref="5"/><nd ref="6"/><tag k="highway" v="steps"/><tag k="step_count" v="{steps}"/></way>'
ROAD_WAY = f'<way id="11" {TIMESTAMP}><nd ref="6"/><nd ref="7"/><tag k="highway" v="residential"/><tag k="sidewalk" v="no"/><tag k="surface" v="sett"/></way>'
SPUR_WAY = f'<way id="14" {TIMESTAMP}><nd ref="7"/><nd ref="9"/><tag k="highway" v="footway"/></way>'
STATE_A = datetime(2026, 10, 3, tzinfo=UTC)
STATE_B = datetime(2026, 10, 4, tzinfo=UTC)
STATE_C = datetime(2026, 10, 5, tzinfo=UTC)
STATE_D = datetime(2026, 10, 6, tzinfo=UTC)
STATE_E = datetime(2026, 10, 7, tzinfo=UTC)


def build_source_xml(*, bench: bool, spur: bool, steps: int, stairs_edited: str = "2026-10-03T00:00:00Z", kerb: bool = True) -> str:
    """Compose an invented source: boundary, the network of three ways with an optional lowered kerb, an optional bench and an optional spur way."""
    kerb_node = KERB_NODE.format(timestamp=TIMESTAMP, tags=KERB_TAGS if kerb else "")
    nodes = BOUNDARY_NODES + NETWORK_NODES + kerb_node + (BENCH_NODE if bench else "") + (SPUR_NODE if spur else "")
    ways = BOUNDARY_WAY + STAIRS_WAY.format(timestamp=f'timestamp="{stairs_edited}" version="2"', steps=steps) + ROAD_WAY + (SPUR_WAY if spur else "")
    return nodes + ways + INVENTED_RELATIONS_XML


@pytest.fixture
def service_engine() -> Iterator[Engine]:
    """Connect as the service account through the delivered engine and require a database without any copy."""
    engine = build_import_engine(5000)
    with engine.connect() as connection:
        if connection.execute(text("SELECT count(*) FROM osm_copy")).scalar_one():
            pytest.fail("The import scenario needs a freshly migrated local database without any OpenStreetMap copy")
    yield engine
    engine.dispose()


class ImportScenario:
    """Run imports of invented sources with a fake acquisition and fake Valhalla tools, keeping one routing root."""

    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        self.tmp_path = tmp_path
        self.monkeypatch = monkeypatch
        self.routing_root = tmp_path / "routing"
        self.routing_root.mkdir()
        self.runs = 0
        template = tmp_path / "valhalla.json"
        template.write_text('{"mjolnir": {}}', encoding="utf-8")
        self.settings = OsmImportSettings(tmp_path / "workspace", self.routing_root, tmp_path / "tools", template, ZoneInfo("Europe/Warsaw"))

        def apply_tiles(lease, config_path, tool_directory, network_path, archive_path, state_at, deadline):
            archive_path.write_bytes(b"invented tile archive " + state_at.isoformat().encode())

        monkeypatch.setattr("service.osm_routing_preparation.apply_osm_valhalla_tiles", apply_tiles)

    def apply_import(self, elements_xml: str, state_at: datetime):
        """Import one invented source whose acquisition is replaced by an already validated local file."""
        self.runs += 1
        directory = self.tmp_path / f"source-{self.runs}"
        directory.mkdir()
        source = apply_invented_osm_source(directory, elements_xml, state_at.isoformat().replace("+00:00", "Z"))

        @asynccontextmanager
        async def fetch_extract(client, download_directory, deadline):
            yield OsmExtract(source, state_at.strftime("malopolskie-%y%m%d.osm.pbf"), state_at)

        self.monkeypatch.setattr("service.osm_import.fetch_osm_extract", fetch_extract)
        return asyncio.run(apply_osm_import(self.settings, cast(httpx.AsyncClient, object())))


def fetch_rows(engine: Engine, sql: str, **parameters):
    """Read rows for assertions as the service account."""
    with engine.connect() as connection:
        return connection.execute(text(sql), parameters).all()


def apply_anonymous_votes(engine: Engine, fact_id: int, verdicts: tuple[str, ...], first_person: int) -> None:
    """Store one vote of each invented person without an account, one minute apart, as the service account."""
    with engine.begin() as connection:
        for index, verdict in enumerate(verdicts):
            connection.execute(
                text("INSERT INTO vote (fact_id, verdict, is_cast_with_account, voter_hash, cast_at, cast_at_utc_offset_minutes) VALUES (:fact_id, :verdict, false, :voter_hash, :cast_at, 120)"),
                {
                    "fact_id": fact_id,
                    "verdict": verdict,
                    "voter_hash": hashlib.sha256(f"made-up person {first_person + index}".encode()).digest(),
                    "cast_at": datetime(2026, 10, 3, 10, index, tzinfo=UTC),
                },
            )


def test_import_scenario_keeps_identities_votes_and_the_complete_copy(tmp_path, monkeypatch, service_engine):
    scenario = ImportScenario(tmp_path, monkeypatch)

    first = scenario.apply_import(build_source_xml(bench=True, spur=True, steps=4), STATE_A)
    assert first.outcome == "updated"
    assert first.counts is not None and (first.counts.ways, first.counts.facts) == (3, 4)
    assert fetch_routing_pointer(scenario.routing_root) == str(int(STATE_A.timestamp()))
    assert [row.id for row in fetch_rows(service_engine, "SELECT id FROM osm_way ORDER BY id")] == [10, 11, 14]
    facts = {(row.osm_element_type, row.osm_element_id, row.fact_type): row for row in fetch_rows(service_engine, "SELECT * FROM fact WHERE osm_element_id IS NOT NULL")}
    assert set(facts) == {("way", 10, "stairs"), ("way", 11, "poor_surface"), ("node", 7, "lowered_kerb"), ("node", 8, "rest_place")}
    stairs_id = facts[("way", 10, "stairs")].id
    bench_id = facts[("node", 8, "rest_place")].id
    kerb_id = facts[("node", 7, "lowered_kerb")].id
    assert facts[("way", 10, "stairs")].step_count == 4
    assert all(row.source == "openstreetmap" and not row.is_removed_from_osm for row in facts.values())
    copy_row = fetch_rows(service_engine, "SELECT state_at, state_at_utc_offset_minutes, file_name FROM osm_copy")
    assert copy_row == [(STATE_A, 0, "malopolskie-261003.osm.pbf")]

    with service_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO vote (fact_id, verdict, is_cast_with_account, voter_hash, cast_at, cast_at_utc_offset_minutes) "
                "VALUES (:fact_id, 'confirm', false, :voter_hash, '2026-10-03 12:00:00+02', 120)"
            ),
            {"fact_id": stairs_id, "voter_hash": hashlib.sha256(b"made-up person: importer scenario").digest()},
        )
        connection.execute(text("UPDATE fact SET flagged_at = '2026-10-03 12:05:00+02', flagged_at_utc_offset_minutes = 120 WHERE id = :id"), {"id": stairs_id})

    second = scenario.apply_import(build_source_xml(bench=True, spur=False, steps=6, stairs_edited="2026-10-03T23:30:00Z"), STATE_B)
    assert second.outcome == "updated"
    stairs = fetch_rows(service_engine, "SELECT id, step_count, osm_edited_on, flagged_at FROM fact WHERE id = :id", id=stairs_id)[0]
    assert (stairs.step_count, stairs.osm_edited_on) == (6, date(2026, 10, 4))
    assert stairs.flagged_at is not None
    assert fetch_rows(service_engine, "SELECT count(*) FROM vote WHERE fact_id = :id", id=stairs_id)[0][0] == 1
    assert [row.id for row in fetch_rows(service_engine, "SELECT id FROM osm_way ORDER BY id")] == [10, 11]
    assert not fetch_rows(service_engine, "SELECT id FROM osm_node WHERE id = 9")
    assert [row.node_id for row in fetch_rows(service_engine, "SELECT node_id FROM osm_way_node WHERE way_id = 10 ORDER BY sequence_index")] == [5, 6]
    assert fetch_routing_pointer(scenario.routing_root) == str(int(STATE_B.timestamp()))

    assert scenario.apply_import(build_source_xml(bench=True, spur=False, steps=6), STATE_B).outcome == "unchanged"
    with pytest.raises(OsmSourceError, match="older"):
        scenario.apply_import(build_source_xml(bench=True, spur=False, steps=6), STATE_A)
    assert len(fetch_rows(service_engine, "SELECT id FROM osm_copy")) == 2

    apply_anonymous_votes(service_engine, bench_id, ("confirm", "confirm", "confirm", "deny"), 1)
    apply_anonymous_votes(service_engine, kerb_id, ("confirm", "deny"), 5)
    disappeared = scenario.apply_import(build_source_xml(bench=False, spur=False, steps=6, kerb=False), STATE_C)
    assert disappeared.outcome == "updated"
    rows = {row.id: row for row in fetch_rows(service_engine, "SELECT id, source, is_removed_from_osm FROM fact WHERE id IN (:a, :b, :c)", a=bench_id, b=kerb_id, c=stairs_id)}
    assert (rows[bench_id].source, rows[bench_id].is_removed_from_osm) == ("user_report", False)
    assert (rows[kerb_id].source, rows[kerb_id].is_removed_from_osm) == ("openstreetmap", True)
    assert (rows[stairs_id].source, rows[stairs_id].is_removed_from_osm) == ("openstreetmap", False)
    assert fetch_routing_pointer(scenario.routing_root) == str(int(STATE_C.timestamp()))

    assert scenario.apply_import(build_source_xml(bench=False, spur=False, steps=6, kerb=False), STATE_D).outcome == "updated"
    rows = {row.id: row for row in fetch_rows(service_engine, "SELECT id, source, is_removed_from_osm FROM fact WHERE id IN (:a, :b)", a=bench_id, b=kerb_id)}
    assert (rows[bench_id].source, rows[bench_id].is_removed_from_osm) == ("user_report", False)
    assert (rows[kerb_id].source, rows[kerb_id].is_removed_from_osm) == ("openstreetmap", True)

    returned = scenario.apply_import(build_source_xml(bench=True, spur=False, steps=6), STATE_E)
    assert returned.outcome == "updated"
    rows = {row.id: row for row in fetch_rows(service_engine, "SELECT id, source, is_removed_from_osm FROM fact WHERE id IN (:a, :b)", a=bench_id, b=kerb_id)}
    assert (rows[bench_id].source, rows[bench_id].is_removed_from_osm) == ("openstreetmap", False)
    assert (rows[kerb_id].source, rows[kerb_id].is_removed_from_osm) == ("openstreetmap", False)
    votes = dict(fetch_rows(service_engine, "SELECT fact_id, count(*) FROM vote GROUP BY fact_id"))
    assert votes == {stairs_id: 1, bench_id: 4, kerb_id: 2}
    assert len(fetch_rows(service_engine, "SELECT id FROM fact WHERE osm_element_id IS NOT NULL")) == 4
    assert len(fetch_rows(service_engine, "SELECT id FROM osm_copy")) == 5
    apply_lock_check(service_engine, bench_id, stairs_id)


def apply_lock_check(engine: Engine, disappearing_id: int, present_id: int) -> None:
    """
    Show on two connections that reconciliation freezes only the disappearing fact and its votes until its transaction ends.

    The publishing connection decides a copy without the disappearing fact and keeps its transaction open. A second
    connection can still read that fact, cannot lock it or its votes, and can lock a fact that stays present. The
    publishing transaction is rolled back, so the scenario's data stay as they were.
    """
    with engine.connect() as publisher, engine.connect() as voter:
        transaction = publisher.begin()
        kept = tuple(SimpleNamespace(identity=fact.identity) for fact in fetch_osm_facts(publisher) if fact.id != disappearing_id)
        apply_osm_disappearance(publisher, cast(OsmPreparedCopy, SimpleNamespace(facts=kept)))
        assert voter.execute(text("SELECT source FROM fact WHERE id = :id"), {"id": disappearing_id}).scalar_one() == "openstreetmap"
        voter.rollback()
        for sql in ("SELECT id FROM fact WHERE id = :id FOR UPDATE NOWAIT", "SELECT id FROM vote WHERE fact_id = :id FOR UPDATE NOWAIT"):
            with pytest.raises(OperationalError, match="could not obtain lock"):
                voter.execute(text(sql), {"id": disappearing_id})
            voter.rollback()
        assert voter.execute(text("SELECT id FROM fact WHERE id = :id FOR UPDATE NOWAIT"), {"id": present_id}).scalar_one() == present_id
        voter.rollback()
        transaction.rollback()


def test_a_second_import_during_an_active_one_is_skipped(tmp_path, monkeypatch):
    scenario = ImportScenario(tmp_path, monkeypatch)
    holder = build_import_engine(5000)
    try:
        with apply_import_exclusion(holder, tmp_path / "other-workspace"):
            result = scenario.apply_import(build_source_xml(bench=True, spur=False, steps=6), datetime(2026, 10, 7, tzinfo=UTC))
    finally:
        holder.dispose()
    assert result.outcome == "skipped"
