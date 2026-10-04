"""
The seven tables of the target schema as SQLAlchemy declarative classes.

The classes describe the tables, columns and closed lists of `docs/product/schema.md` for the code that reads and
writes them; they never create anything, because the schema is created only by the revisions in `migrations/versions/`.
A critical test checks that every class matches the columns of the stored data.

Every instant of the schema is a pair of a `timestamptz(3)` column and its `_utc_offset_minutes` column. Each pair is
mapped as one `OffsetInstant` attribute named after its instant column, through `composite()`, as
`docs/standards/standard_time.md` requires; the two columns stay mapped only under private keys that start with an
underscore, because SQLAlchemy keeps an attribute for every column of a composite. A nullable pair reads as `None`.

A `geography` column is written and read as EWKT text, for example `SRID=4326;POINT(19.9370 50.0614)`.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from sqlalchemy import BigInteger, Boolean, Computed, Date, DateTime, Enum, ForeignKey, Identity, Integer, LargeBinary, SmallInteger, Text, func
from sqlalchemy.orm import Composite, DeclarativeBase, Mapped, composite, mapped_column
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.types import UserDefinedType

from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, OsmElementType, VoteVerdict, WayBarrierState


@dataclass(frozen=True)
class OffsetInstant:
    """An instant together with the zone offset in minutes that was in force where and when it was written."""

    instant: datetime
    utc_offset_minutes: int


def build_offset_instant(value: datetime) -> OffsetInstant:
    """Builds the pair of an aware datetime: its instant in UTC and its offset in minutes; a naive value is refused."""
    offset = value.utcoffset()
    if offset is None:
        raise ValueError("An instant needs a zone offset; a naive datetime cannot be stored.")
    return OffsetInstant(instant=value.astimezone(UTC), utc_offset_minutes=int(offset.total_seconds()) // 60)


def build_local_datetime(value: OffsetInstant) -> datetime:
    """Builds the wall-clock time of a pair: its instant shown in the offset it was written with."""
    return value.instant.astimezone(timezone(timedelta(minutes=value.utc_offset_minutes)))


def build_closed_list_values(closed_list: type[StrEnum]) -> list[str]:
    """Builds the stored values of a closed list, so that a column stores the value of a member and not its name."""
    return [member.value for member in closed_list]


def build_closed_list_type(closed_list: type[StrEnum]) -> Enum:
    """Builds the column type of a text domain mapped to its enumeration, without creating any constraint of its own."""
    return Enum(closed_list, native_enum=False, create_constraint=False, values_callable=build_closed_list_values)


def resolve_null_pair(*values: object) -> bool:
    """Decides that a pair is absent when both of its stored columns are null."""
    return all(value is None for value in values)


def build_instant_pair(instant_column: str, *, nullable: bool = False) -> Composite[Any]:
    """Builds the one attribute of a pair of an instant column and its offset column, with the columns under private keys."""
    return composite(
        OffsetInstant,
        mapped_column(instant_column, DateTime(timezone=True), nullable=nullable, key=f"_{instant_column}"),
        mapped_column(f"{instant_column}_utc_offset_minutes", SmallInteger, nullable=nullable, key=f"_{instant_column}_utc_offset_minutes"),
        return_none_on=resolve_null_pair if nullable else None,
    )


class Geography(UserDefinedType[str]):
    """A PostGIS `geography` column in the reference system 4326, written and read as EWKT text."""

    cache_ok = True

    def __init__(self, shape: str) -> None:
        """Keeps the shape of the geography, `Point` or `LineString`."""
        self.shape = shape

    def get_col_spec(self, **_kw: Any) -> str:
        """Returns the type as `docs/product/schema.md` writes it."""
        return f"geography({self.shape}, 4326)"

    def bind_expression(self, bindvalue: ColumnElement[Any]) -> ColumnElement[Any]:
        """Turns the EWKT text of a write into a geography in the database."""
        return func.ST_GeogFromText(bindvalue, type_=self)

    def column_expression(self, colexpr: ColumnElement[Any]) -> ColumnElement[Any]:
        """Turns a geography of a read into EWKT text in the database."""
        return func.ST_AsEWKT(colexpr, type_=self)


class TableBase(DeclarativeBase):
    """The common base of the mapped tables of the target schema."""


class OsmCopy(TableBase):
    """One copy of OpenStreetMap data made current (`osm_copy`)."""

    __tablename__ = "osm_copy"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    state_at: Mapped[OffsetInstant] = build_instant_pair("state_at")
    file_name: Mapped[str] = mapped_column(Text)
    made_current_at: Mapped[OffsetInstant] = build_instant_pair("made_current_at")


class OsmWay(TableBase):
    """A way of the pedestrian network of the copy in use, with the states of its barriers (`osm_way`)."""

    __tablename__ = "osm_way"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    geog: Mapped[str] = mapped_column(Geography("LineString"))
    stairs_state: Mapped[WayBarrierState] = mapped_column(build_closed_list_type(WayBarrierState))
    poor_surface_state: Mapped[WayBarrierState] = mapped_column(build_closed_list_type(WayBarrierState))
    steep_incline_state: Mapped[WayBarrierState] = mapped_column(build_closed_list_type(WayBarrierState))
    narrow_passage_state: Mapped[WayBarrierState] = mapped_column(build_closed_list_type(WayBarrierState))
    is_marked_wheelchair_no: Mapped[bool] = mapped_column(Boolean)
    is_motor_traffic: Mapped[bool] = mapped_column(Boolean)
    is_crossing: Mapped[bool] = mapped_column(Boolean)


class OsmNode(TableBase):
    """A node of the ways of the copy in use (`osm_node`)."""

    __tablename__ = "osm_node"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    geog: Mapped[str] = mapped_column(Geography("Point"))
    kerb_point: Mapped[KerbPointState | None] = mapped_column(build_closed_list_type(KerbPointState), nullable=True)
    is_crossing: Mapped[bool] = mapped_column(Boolean)
    is_on_motor_traffic_way: Mapped[bool] = mapped_column(Boolean)


class OsmWayNode(TableBase):
    """A node of a way at its place in the order of the way, from 0 (`osm_way_node`)."""

    __tablename__ = "osm_way_node"

    way_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("osm_way.id", ondelete="CASCADE"), primary_key=True)
    sequence_index: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    node_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("osm_node.id"))


class Fact(TableBase):
    """A barrier or an amenity: a point report, a geozone, a fact from OpenStreetMap or one converted from it (`fact`)."""

    __tablename__ = "fact"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    fact_type: Mapped[FactType] = mapped_column(build_closed_list_type(FactType))
    source: Mapped[FactSource] = mapped_column(build_closed_list_type(FactSource))
    geog: Mapped[str] = mapped_column(Geography("Point"))
    geozone_radius_m: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_count: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean)
    idempotency_key: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    osm_element_type: Mapped[OsmElementType | None] = mapped_column(build_closed_list_type(OsmElementType), nullable=True)
    osm_element_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    osm_edited_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_removed_from_osm: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[OffsetInstant] = build_instant_pair("created_at")
    flagged_at: Mapped[OffsetInstant | None] = build_instant_pair("flagged_at", nullable=True)
    hidden_at: Mapped[OffsetInstant | None] = build_instant_pair("hidden_at", nullable=True)


class Account(TableBase):
    """A light account: a pseudonym, a password hash and the moderator role (`account`)."""

    __tablename__ = "account"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    pseudonym: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column(Text)
    is_moderator: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[OffsetInstant] = build_instant_pair("created_at")


class Vote(TableBase):
    """
    A confirmation or a denial of a fact by an account or by the hash of a person without one (`vote`).

    `cast_on` is the calendar day of `cast_at` in Europe/Warsaw, computed and stored by the database, so the model never
    writes it; the database reports a generated column as nullable, although `cast_at` is never null.
    """

    __tablename__ = "vote"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    fact_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fact.id"))
    verdict: Mapped[VoteVerdict] = mapped_column(build_closed_list_type(VoteVerdict))
    is_cast_with_account: Mapped[bool] = mapped_column(Boolean)
    account_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("account.id", ondelete="SET NULL"), nullable=True)
    voter_hash: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    cast_at: Mapped[OffsetInstant] = build_instant_pair("cast_at")
    cast_on: Mapped[date] = mapped_column(Date, Computed("(cast_at AT TIME ZONE 'Europe/Warsaw')::date", persisted=True), nullable=True)
