"""Read and write importer-owned fields through a supplied publication connection."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import date, datetime
from itertools import batched
from typing import Any, cast

from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, OsmElementType, VoteVerdict, WayBarrierState
from accessibility_db.tables import Fact, OffsetInstant, OsmCopy, OsmNode, OsmWay, OsmWayNode, Vote, build_offset_instant
from sqlalchemy import BigInteger, Connection, Table, any_, bindparam, delete, insert, select, update
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import insert as postgres_insert

OSM_WRITE_BATCH_SIZE = 1000


@dataclass(frozen=True)
class OsmFactIdentity:
    """Identify one imported fact independently of its geometry and votes."""

    element_type: OsmElementType
    element_id: int
    fact_type: FactType


@dataclass(frozen=True)
class OsmCopySnapshot:
    """Describe a recorded source copy without changing its offset representation."""

    id: int
    state_at: OffsetInstant
    file_name: str


@dataclass(frozen=True)
class OsmNodeRow:
    """Carry exactly the stored node fields derived from original source tags."""

    id: int
    geog: str
    kerb_point: KerbPointState | None
    is_crossing: bool
    is_on_motor_traffic_way: bool


@dataclass(frozen=True)
class OsmWayRow:
    """Carry the geometry, four barrier states and flags of a selected way."""

    id: int
    geog: str
    stairs_state: WayBarrierState
    poor_surface_state: WayBarrierState
    steep_incline_state: WayBarrierState
    narrow_passage_state: WayBarrierState
    is_marked_wheelchair_no: bool
    is_motor_traffic: bool
    is_crossing: bool


@dataclass(frozen=True)
class OsmMembershipRow:
    """Keep repeated node identities at distinct sequence positions."""

    way_id: int
    sequence_index: int
    node_id: int


@dataclass(frozen=True)
class OsmPresentFact:
    """Carry only the source-owned attributes of a fact present in a fresh copy."""

    identity: OsmFactIdentity
    geog: str
    edited_on: date
    step_count: int | None


@dataclass(frozen=True)
class OsmStoredFact:
    """Read the fields needed for disappearance without exposing moderation or descriptions."""

    id: int
    identity: OsmFactIdentity
    source: FactSource
    is_removed_from_osm: bool


@dataclass(frozen=True)
class OsmVoteSnapshot:
    """Keep locked vote history for the shared evaluator without printing person identifiers."""

    id: int
    fact_id: int
    verdict: VoteVerdict
    is_cast_with_account: bool
    cast_at: OffsetInstant
    account_id: int | None = field(repr=False)
    voter_hash: bytes | None = field(repr=False)


@dataclass(frozen=True)
class OsmFactChange:
    """Describe a disappearance decision already made by the rules layer."""

    id: int
    source: FactSource
    is_removed_from_osm: bool


_node = cast(Table, OsmNode.__table__)
_way = cast(Table, OsmWay.__table__)
_membership = cast(Table, OsmWayNode.__table__)
_fact = cast(Table, Fact.__table__)
_copy = cast(Table, OsmCopy.__table__)
_vote = cast(Table, Vote.__table__)

_node_insert = postgres_insert(_node)
APPLY_OSM_NODES_SQL = _node_insert.on_conflict_do_update(
    index_elements=[_node.c.id], set_={key: _node_insert.excluded[key] for key in ("geog", "kerb_point", "is_crossing", "is_on_motor_traffic_way")}
)
_way_insert = postgres_insert(_way)
APPLY_OSM_WAYS_SQL = _way_insert.on_conflict_do_update(
    index_elements=[_way.c.id],
    set_={
        key: _way_insert.excluded[key]
        for key in ("geog", "stairs_state", "poor_surface_state", "steep_incline_state", "narrow_passage_state", "is_marked_wheelchair_no", "is_motor_traffic", "is_crossing")
    },
)
APPLY_OSM_MEMBERSHIPS_SQL = insert(_membership)
DELETE_OSM_MEMBERSHIPS_SQL = delete(_membership)
DELETE_OBSOLETE_OSM_WAYS_SQL = delete(_way).where(~(_way.c.id == any_(bindparam("way_ids", type_=ARRAY(BigInteger)))))
DELETE_UNREFERENCED_OSM_NODES_SQL = delete(_node).where(~select(_membership.c.node_id).where(_membership.c.node_id == _node.c.id).exists())
_fact_insert = postgres_insert(_fact)
APPLY_OSM_PRESENT_FACTS_SQL = _fact_insert.on_conflict_do_update(
    index_elements=[_fact.c.osm_element_type, _fact.c.osm_element_id, _fact.c.fact_type],
    set_={key: _fact_insert.excluded[key] for key in ("source", "geog", "step_count", "osm_edited_on", "is_removed_from_osm")},
)
APPLY_OSM_FACT_CHANGES_SQL = (
    update(_fact).where(_fact.c.id == bindparam("fact_id"), _fact.c.osm_element_id.is_not(None)).values(source=bindparam("new_source"), is_removed_from_osm=bindparam("removed"))
)
APPLY_OSM_COPY_METADATA_SQL = insert(_copy)
FETCH_OSM_COPY_HISTORY_SQL = select(_copy.c.id, _copy.c._state_at.label("state_at"), _copy.c._state_at_utc_offset_minutes.label("state_at_utc_offset_minutes"), _copy.c.file_name).order_by(
    _copy.c._state_at.desc()
)
FETCH_CURRENT_OSM_COPY_SQL = FETCH_OSM_COPY_HISTORY_SQL.limit(1)
FETCH_OSM_FACTS_SQL = (
    select(_fact.c.id, _fact.c.osm_element_type, _fact.c.osm_element_id, _fact.c.fact_type, _fact.c.source, _fact.c.is_removed_from_osm)
    .where(_fact.c.osm_element_id.is_not(None))
    .order_by(_fact.c.id)
)
FETCH_OSM_FACT_HISTORY_SQL = (
    select(
        _vote.c.id,
        _vote.c.fact_id,
        _vote.c.verdict,
        _vote.c.is_cast_with_account,
        _vote.c._cast_at.label("cast_at"),
        _vote.c._cast_at_utc_offset_minutes.label("cast_at_utc_offset_minutes"),
        _vote.c.account_id,
        _vote.c.voter_hash,
    )
    .where(_vote.c.fact_id == any_(bindparam("fact_ids", type_=ARRAY(BigInteger))))
    .order_by(_vote.c.fact_id, _vote.c.id)
    .with_for_update()
)


def build_osm_parameters(row: OsmNodeRow | OsmWayRow | OsmMembershipRow) -> dict[str, Any]:
    """Expose only fields explicitly declared by the immutable importer row."""
    return {key: getattr(row, key) for key in row.__dataclass_fields__}


def apply_osm_batches(connection: Connection, statement: Any, parameters: Iterable[dict[str, Any]]) -> int:
    """Write bounded batches on the caller's transaction without committing it."""
    count = 0
    for batch in batched(parameters, OSM_WRITE_BATCH_SIZE, strict=False):
        connection.execute(statement, list(batch))
        count += len(batch)
    return count


def apply_osm_network(connection: Connection, nodes: Iterable[OsmNodeRow], ways: Iterable[OsmWayRow], memberships: Iterable[OsmMembershipRow]) -> None:
    """Replace network membership while retaining source identities in one supplied transaction."""
    prepared_ways = tuple(ways)
    apply_osm_batches(connection, APPLY_OSM_NODES_SQL, (build_osm_parameters(row) for row in nodes))
    apply_osm_batches(connection, APPLY_OSM_WAYS_SQL, (build_osm_parameters(row) for row in prepared_ways))
    connection.execute(DELETE_OSM_MEMBERSHIPS_SQL)
    apply_osm_batches(connection, APPLY_OSM_MEMBERSHIPS_SQL, (build_osm_parameters(row) for row in memberships))
    connection.execute(DELETE_OBSOLETE_OSM_WAYS_SQL, {"way_ids": [row.id for row in prepared_ways]})
    connection.execute(DELETE_UNREFERENCED_OSM_NODES_SQL)


def build_osm_instant_parameters(value: datetime) -> OffsetInstant:
    """Refuse time precision or offsets that the delivered schema cannot preserve."""
    offset = value.utcoffset()
    if offset is None or offset.total_seconds() % 60 or abs(offset.total_seconds()) > 840 * 60 or value.microsecond % 1000:
        raise ValueError("Imported instant cannot be represented by the schema")
    return build_offset_instant(value)


def apply_osm_present_facts(connection: Connection, facts: Iterable[OsmPresentFact], created_at: datetime) -> int:
    """Upsert imported attributes while retaining fact identity, votes and moderation fields."""
    instant = build_osm_instant_parameters(created_at)

    def build_parameters() -> Iterator[dict[str, Any]]:
        """Produce source-owned insertion values and no user-content updates."""
        for fact in facts:
            yield {
                "fact_type": fact.identity.fact_type,
                "source": FactSource.OPENSTREETMAP,
                "geog": fact.geog,
                "step_count": fact.step_count,
                "is_sample": False,
                "osm_element_type": fact.identity.element_type,
                "osm_element_id": fact.identity.element_id,
                "osm_edited_on": fact.edited_on,
                "is_removed_from_osm": False,
                "_created_at": instant.instant,
                "_created_at_utc_offset_minutes": instant.utc_offset_minutes,
            }

    return apply_osm_batches(connection, APPLY_OSM_PRESENT_FACTS_SQL, build_parameters())


def apply_osm_fact_changes(connection: Connection, changes: Iterable[OsmFactChange]) -> int:
    """Write only the disappearance fields selected by the rules layer."""
    return apply_osm_batches(connection, APPLY_OSM_FACT_CHANGES_SQL, ({"fact_id": row.id, "new_source": row.source, "removed": row.is_removed_from_osm} for row in changes))


def apply_osm_copy_metadata(connection: Connection, state_at: datetime, filename: str, made_current_at: datetime) -> None:
    """Append one source-copy record within the caller's publication transaction."""
    state = build_osm_instant_parameters(state_at)
    published = build_osm_instant_parameters(made_current_at)
    connection.execute(
        APPLY_OSM_COPY_METADATA_SQL,
        {
            "_state_at": state.instant,
            "_state_at_utc_offset_minutes": state.utc_offset_minutes,
            "file_name": filename,
            "_made_current_at": published.instant,
            "_made_current_at_utc_offset_minutes": published.utc_offset_minutes,
        },
    )


def fetch_current_osm_copy(connection: Connection) -> OsmCopySnapshot | None:
    """Read the latest copy without using download time as source time."""
    row = connection.execute(FETCH_CURRENT_OSM_COPY_SQL).mappings().one_or_none()
    return None if row is None else OsmCopySnapshot(row["id"], OffsetInstant(row["state_at"], row["state_at_utc_offset_minutes"]), row["file_name"])


def fetch_osm_copy_history(connection: Connection) -> tuple[OsmCopySnapshot, ...]:
    """Read immutable copy history for later guarded routing-directory decisions."""
    return tuple(OsmCopySnapshot(row["id"], OffsetInstant(row["state_at"], row["state_at_utc_offset_minutes"]), row["file_name"]) for row in connection.execute(FETCH_OSM_COPY_HISTORY_SQL).mappings())


def fetch_osm_facts(connection: Connection) -> tuple[OsmStoredFact, ...]:
    """Read source-identified facts in ascending identity order without row locks, which only facts under reconciliation take."""
    return tuple(
        OsmStoredFact(row["id"], OsmFactIdentity(OsmElementType(row["osm_element_type"]), row["osm_element_id"], FactType(row["fact_type"])), FactSource(row["source"]), row["is_removed_from_osm"])
        for row in connection.execute(FETCH_OSM_FACTS_SQL).mappings()
    )


def fetch_osm_fact_history(connection: Connection, fact_ids: Iterable[int]) -> tuple[OsmVoteSnapshot, ...]:
    """Lock vote rows in stable fact and vote order without evaluating them in data."""
    result = []
    for batch in batched(sorted(set(fact_ids)), OSM_WRITE_BATCH_SIZE, strict=False):
        for row in connection.execute(FETCH_OSM_FACT_HISTORY_SQL, {"fact_ids": list(batch)}).mappings():
            result.append(
                OsmVoteSnapshot(
                    row["id"],
                    row["fact_id"],
                    VoteVerdict(row["verdict"]),
                    row["is_cast_with_account"],
                    OffsetInstant(row["cast_at"], row["cast_at_utc_offset_minutes"]),
                    row["account_id"],
                    row["voter_hash"],
                )
            )
    return tuple(result)
