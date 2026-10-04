"""Protect publication ownership using the delivered SQLAlchemy models."""

from datetime import UTC, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType
from sqlalchemy.dialects import postgresql

from data.osm_copy import (
    APPLY_OSM_PRESENT_FACTS_SQL,
    FETCH_OSM_FACT_HISTORY_SQL,
    FETCH_OSM_FACTS_FOR_UPDATE_SQL,
    OsmFactIdentity,
    OsmPresentFact,
    apply_osm_present_facts,
    build_osm_instant_parameters,
)


class RecordingConnection:
    """Record execution without providing transaction management methods."""

    def __init__(self):
        """Start an empty execution record."""
        self.calls = []

    def execute(self, statement, parameters):
        """Keep the actual statement and bound parameters."""
        self.calls.append((statement, parameters))


def test_present_fact_update_preserves_user_history():
    """A returning source fact must not replace identity or moderation columns."""
    sql = str(APPLY_OSM_PRESENT_FACTS_SQL.compile(dialect=postgresql.dialect()))
    assignments = sql.split("DO UPDATE SET", 1)[1]
    for protected in ("id =", "created_at =", "flagged_at =", "hidden_at =", "description =", "is_sample ="):
        assert protected not in assignments
    assert "source = excluded.source" in assignments
    assert "is_removed_from_osm = excluded.is_removed_from_osm" in assignments
    assert "ON CONFLICT (osm_element_type, osm_element_id, fact_type)" in sql


def test_present_fact_batches_keep_source_and_do_not_commit():
    """Bounded writes retain exact insertion time and source identity."""
    connection = RecordingConnection()
    now = datetime(2026, 10, 4, tzinfo=UTC)
    facts = (OsmPresentFact(OsmFactIdentity(OsmElementType.NODE, index, FactType.ELEVATOR), "SRID=4326;POINT(19 50)", now.date(), None) for index in range(1, 1002))
    assert apply_osm_present_facts(connection, facts, now) == 1001
    assert [len(parameters) for _, parameters in connection.calls] == [1000, 1]
    values = connection.calls[0][1][0]
    assert values["source"] == FactSource.OPENSTREETMAP
    assert values["_created_at"] == now
    assert values["osm_element_id"] == 1
    compiled = APPLY_OSM_PRESENT_FACTS_SQL.values(values).compile(dialect=postgresql.dialect())
    assert "ST_GeogFromText" in str(compiled)
    assert "created_at" in str(compiled)


def test_lock_order_is_explicit():
    """Fact and vote locks have the stable ordering required by reconciliation."""
    dialect = postgresql.dialect()
    facts = str(FETCH_OSM_FACTS_FOR_UPDATE_SQL.compile(dialect=dialect))
    votes = str(FETCH_OSM_FACT_HISTORY_SQL.compile(dialect=dialect))
    assert "ORDER BY fact.id FOR UPDATE" in facts
    assert "ORDER BY vote.fact_id, vote.id FOR UPDATE" in votes


@pytest.mark.parametrize("value", [datetime(2026, 10, 4), datetime(2026, 10, 4, microsecond=1, tzinfo=UTC)])
def test_unrepresentable_instants_fail(value):
    """Never silently drop timezone or timestamp precision at the database boundary."""
    with pytest.raises(ValueError, match="cannot be represented"):
        build_osm_instant_parameters(value)
