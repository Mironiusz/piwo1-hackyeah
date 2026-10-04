"""Read the visible facts, their votes and the ways of the geozones that one route request needs, inside the snapshot of its caller."""

from collections.abc import Collection
from dataclasses import dataclass
from datetime import date
from itertools import batched
from typing import cast

from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import Fact, OffsetInstant, OsmWay, Vote
from sqlalchemy import BigInteger, Connection, Float, Select, Table, Text, and_, any_, bindparam, func, or_, select, true
from sqlalchemy.dialects.postgresql import ARRAY

REPORT_STRETCH_DISTANCE_M = 15
FACT_ID_BATCH_SIZE = 10000

_fact = cast(Table, Fact.__table__)
_way = cast(Table, OsmWay.__table__)
_vote = cast(Table, Vote.__table__)

VISIBLE_FACT_CONDITION = and_(_fact.c._hidden_at.is_(None), _fact.c.is_removed_from_osm.is_(False))


@dataclass(frozen=True)
class StoredFact:
    """Every stored field of a fact the shared object Fact of the contract shows, with the OpenStreetMap identity behind it."""

    id: int
    fact_type: FactType
    source: FactSource
    lat: float
    lon: float
    geozone_radius_m: int | None
    description: str | None
    step_count: int | None
    is_sample: bool
    osm_element_type: OsmElementType | None
    osm_element_id: int | None
    osm_edited_on: date | None
    is_removed_from_osm: bool


@dataclass(frozen=True)
class StoredRouteFact(StoredFact):
    """A fact of a route with, for a fact of the source user report, the nearest way of the network within 15 m."""

    nearest_way_id: int | None


@dataclass(frozen=True)
class StoredVote:
    """One stored vote with the fields the status rule of M4 reads."""

    id: int
    fact_id: int
    verdict: VoteVerdict
    is_cast_with_account: bool
    cast_at: OffsetInstant
    account_id: int | None
    voter_hash: bytes | None


_nearest_way = (
    select(_way.c.id)
    .where(_fact.c.source == FactSource.USER_REPORT.value, func.ST_DWithin(_way.c.geog, _fact.c.geog, REPORT_STRETCH_DISTANCE_M))
    .order_by(func.ST_Distance(_way.c.geog, _fact.c.geog), _way.c.id)
    .limit(1)
    .lateral("nearest_way")
)
_route_fact_columns: Select = (
    select(
        _fact.c.id,
        _fact.c.fact_type,
        _fact.c.source,
        func.ST_Y(func.geometry(_fact.c.geog), type_=Float).label("lat"),
        func.ST_X(func.geometry(_fact.c.geog), type_=Float).label("lon"),
        _fact.c.geozone_radius_m,
        _fact.c.description,
        _fact.c.step_count,
        _fact.c.is_sample,
        _fact.c.osm_element_type,
        _fact.c.osm_element_id,
        _fact.c.osm_edited_on,
        _fact.c.is_removed_from_osm,
        _nearest_way.c.id.label("nearest_way_id"),
    )
    .select_from(_fact.outerjoin(_nearest_way, true()))
    .where(VISIBLE_FACT_CONDITION, _fact.c.fact_type == any_(bindparam("fact_types", type_=ARRAY(Text))))
    .order_by(_fact.c.id)
)
_area_condition = func.ST_DWithin(_fact.c.geog, func.ST_GeogFromText(bindparam("area", type_=Text)), bindparam("distance", type_=Float) + func.coalesce(_fact.c.geozone_radius_m, 0))
_way_fact_condition = and_(_fact.c.osm_element_type == OsmElementType.WAY.value, _fact.c.osm_element_id == any_(bindparam("way_ids", type_=ARRAY(BigInteger))))
FETCH_ROUTE_FACTS_SQL = _route_fact_columns.where(or_(_area_condition, _way_fact_condition))
FETCH_COPY_ROUTE_FACTS_SQL = _route_fact_columns
FETCH_FACT_VOTES_SQL = (
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
)
FETCH_GEOZONE_WAYS_SQL = (
    select(_fact.c.id.label("geozone_id"), _way.c.id.label("way_id"))
    .select_from(_fact.join(_way, func.ST_DWithin(_way.c.geog, _fact.c.geog, _fact.c.geozone_radius_m)))
    .where(_fact.c.id == any_(bindparam("geozone_ids", type_=ARRAY(BigInteger))), _fact.c.geozone_radius_m.is_not(None))
    .order_by(_fact.c.id, _way.c.id)
)


def fetch_route_facts(connection: Connection, area_wkt: str | None, distance_m: float, fact_types: Collection[str], way_ids: Collection[int]) -> tuple[StoredRouteFact, ...]:
    """
    Read every visible fact of the given types near an area or on the given ways, or every such fact of the copy.

    A fact is read when its point lies within distance_m of the area given as WKT in longitude and latitude - a geozone
    within distance_m plus its radius - or when it is the fact of one of the ways, whose point stands at the middle of the
    way and may lie far from the part a route takes. With no area every visible fact of the types is read. Hidden facts
    and facts removed in OpenStreetMap are never read. Every geometry and distance is a bound parameter.
    """
    if area_wkt is None:
        rows = connection.execute(FETCH_COPY_ROUTE_FACTS_SQL, {"fact_types": sorted(fact_types)}).mappings()
    else:
        rows = connection.execute(FETCH_ROUTE_FACTS_SQL, {"fact_types": sorted(fact_types), "area": area_wkt, "distance": float(distance_m), "way_ids": sorted(way_ids)}).mappings()
    return tuple(
        StoredRouteFact(
            id=row["id"],
            fact_type=FactType(row["fact_type"]),
            source=FactSource(row["source"]),
            lat=row["lat"],
            lon=row["lon"],
            geozone_radius_m=row["geozone_radius_m"],
            description=row["description"],
            step_count=row["step_count"],
            is_sample=row["is_sample"],
            osm_element_type=None if row["osm_element_type"] is None else OsmElementType(row["osm_element_type"]),
            osm_element_id=row["osm_element_id"],
            osm_edited_on=row["osm_edited_on"],
            is_removed_from_osm=row["is_removed_from_osm"],
            nearest_way_id=row["nearest_way_id"],
        )
        for row in rows
    )


def fetch_fact_votes(connection: Connection, fact_ids: Collection[int]) -> tuple[StoredVote, ...]:
    """Read every vote of the given facts in fact and vote order, without locking them."""
    votes = []
    for batch in batched(sorted(set(fact_ids)), FACT_ID_BATCH_SIZE, strict=False):
        for row in connection.execute(FETCH_FACT_VOTES_SQL, {"fact_ids": list(batch)}).mappings():
            votes.append(
                StoredVote(
                    row["id"],
                    row["fact_id"],
                    VoteVerdict(row["verdict"]),
                    row["is_cast_with_account"],
                    OffsetInstant(row["cast_at"], row["cast_at_utc_offset_minutes"]),
                    row["account_id"],
                    row["voter_hash"],
                )
            )
    return tuple(votes)


def fetch_geozone_ways(connection: Connection, geozone_ids: Collection[int]) -> tuple[tuple[int, int], ...]:
    """Read the pairs of a geozone and a way of the network that lies within its radius."""
    pairs: list[tuple[int, int]] = []
    for batch in batched(sorted(set(geozone_ids)), FACT_ID_BATCH_SIZE, strict=False):
        pairs.extend((row["geozone_id"], row["way_id"]) for row in connection.execute(FETCH_GEOZONE_WAYS_SQL, {"geozone_ids": list(batch)}).mappings())
    return tuple(pairs)
