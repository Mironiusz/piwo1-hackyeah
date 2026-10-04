"""
Reads and writes of the `fact` and `vote` tables for the nine operations of the community facts, on a connection the service layer opens.

The layer writes and reads and never decides whether a write may be performed (`docs/standards/standard_architecture.md`, Layer
boundary): a lock gives the service layer the state it decides on, and a write does what it is told. No function here commits, opens
a connection, sets a statement limit or logs anything (`plans/community_facts/COMMUNITY_FACTS_PLAN.md` D-1 - D-9).

Two rules of the contract decide which facts a read shows, and they differ on purpose. The map and the check for existing facts use
`VISIBLE_FACT_CONDITION` of `data/route_facts.py`, which leaves out hidden facts and facts removed in OpenStreetMap. The reading of one
fact by its identifier uses `UNHIDDEN_FACT_CONDITION`, which leaves out only the hidden ones. The votes of the facts of any read come
from `fetch_fact_votes` of `data/route_facts.py` in one call for all of them.

Every vote is cast by a `Voter`: an account, or the 32 bytes of a person without an account that the caller derives. A vote of one person
on one fact is accepted once per calendar day in Europe/Warsaw, which the generated column `cast_on` and the indexes `UX_vote_account_day`
and `UX_vote_hash_day` hold in the database. The insert of a fact that takes an idempotency key waits on its unique index, so a caller that
runs it must use the READ COMMITTED isolation of the engine default for the read after a conflict to see the committed fact.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any, cast

from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import Fact, OffsetInstant, Vote
from psycopg.errors import ForeignKeyViolation
from sqlalchemy import Connection, DateTime, Float, Integer, RowMapping, SmallInteger, Table, bindparam, func, select, update
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.exc import IntegrityError

from data.route_facts import VISIBLE_FACT_CONDITION, StoredFact

WGS84_SRID = 4326
VOTE_ACCOUNT_CONSTRAINT_NAME = "fk_vote_account"
VOTE_ACCOUNT_MISSING_MESSAGE = "The account of the vote no longer exists"

_fact = cast(Table, Fact.__table__)
_vote = cast(Table, Vote.__table__)

UNHIDDEN_FACT_CONDITION = _fact.c._hidden_at.is_(None)


@dataclass(frozen=True)
class StoredCommunityFact(StoredFact):
    """A stored fact with the instant of its first flag and whether it is hidden; it carries no author, no account and no idempotency key."""

    flagged_at: OffsetInstant | None
    is_hidden: bool


@dataclass(frozen=True)
class StoredNearbyFact:
    """A stored fact with its exact geodesic distance in metres from the point of the check; the service layer rounds it to whole metres."""

    fact: StoredCommunityFact
    distance_m: float


@dataclass(frozen=True)
class FactContent:
    """The content of a report or a geozone as the caller normalized it: its type, point, description, step count and geozone radius."""

    fact_type: FactType
    lat: float
    lon: float
    description: str | None
    step_count: int | None
    geozone_radius_m: int | None


@dataclass(frozen=True)
class AccountVoter:
    """A person with an account."""

    account_id: int


@dataclass(frozen=True)
class AnonymousVoter:
    """A person without an account, known only by the 32 bytes the caller derived; the bytes stay out of the text of the record."""

    voter_hash: bytes = field(repr=False)


Voter = AccountVoter | AnonymousVoter


@dataclass(frozen=True)
class FactInsertOutcome:
    """The fact of a save and whether this save created it; a repeated save with the same idempotency key gives the first fact and false."""

    fact: StoredCommunityFact
    is_created: bool


@dataclass(frozen=True)
class StoredVoteInsert:
    """A stored vote with the calendar day in Europe/Warsaw the database gave it."""

    vote_id: int
    cast_on: date


@dataclass(frozen=True)
class VoteDayTaken:
    """The calendar day of the stored vote that refused the new one; the next vote of the person is accepted from the next day."""

    cast_on: date


VoteInsertOutcome = StoredVoteInsert | VoteDayTaken


class VoteAccountMissingError(Exception):
    """A vote named an account that no longer exists; the message carries no identifier and the failure leaves the transaction aborted."""


_stored_fact_columns = (
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
    _fact.c._flagged_at.label("flagged_at"),
    _fact.c._flagged_at_utc_offset_minutes.label("flagged_at_utc_offset_minutes"),
    _fact.c._hidden_at.is_not(None).label("is_hidden"),
)
_stored_fact_by_id = select(*_stored_fact_columns).where(_fact.c.id == bindparam("fact_id"))
_area_envelope = func.ST_MakeEnvelope(bindparam("west", type_=Float), bindparam("south", type_=Float), bindparam("east", type_=Float), bindparam("north", type_=Float), WGS84_SRID)
_report_point = func.ST_SetSRID(func.ST_MakePoint(bindparam("lon", type_=Float), bindparam("lat", type_=Float)), WGS84_SRID)
_nearby_distance = func.ST_Distance(_fact.c.geog, func.geography(_report_point), type_=Float).label("distance_m")

FETCH_STORED_FACTS_IN_AREA_SQL = (
    select(*_stored_fact_columns).where(VISIBLE_FACT_CONDITION, func.ST_Intersects(func.geometry(_fact.c.geog), _area_envelope)).order_by(_fact.c.id).limit(bindparam("row_limit", type_=Integer))
)
FETCH_STORED_FACT_SQL = _stored_fact_by_id.where(UNHIDDEN_FACT_CONDITION)
FETCH_STORED_NEARBY_FACTS_SQL = (
    select(*_stored_fact_columns, _nearby_distance)
    .where(
        VISIBLE_FACT_CONDITION,
        _fact.c.fact_type == bindparam("fact_type"),
        func.ST_DWithin(_fact.c.geog, func.geography(_report_point), bindparam("distance", type_=Float)),
    )
    .order_by(_nearby_distance, _fact.c.id)
)
FETCH_STORED_FLAGGED_FACTS_SQL = select(*_stored_fact_columns).where(_fact.c._flagged_at.is_not(None)).order_by(_fact.c._flagged_at.desc(), _fact.c.id.desc())
FETCH_STORED_FACT_FOR_VOTE_SQL = _stored_fact_by_id.with_for_update(read=True)
FETCH_STORED_FACT_FOR_CHANGE_SQL = _stored_fact_by_id.with_for_update(key_share=True)
FETCH_FACT_BY_IDEMPOTENCY_KEY_SQL = select(*_stored_fact_columns).where(_fact.c.idempotency_key == bindparam("idempotency_key"))
APPLY_FACT_INSERT_SQL = postgres_insert(_fact).values(geog=func.geography(_report_point)).on_conflict_do_nothing(index_elements=[_fact.c.idempotency_key]).returning(*_stored_fact_columns)
APPLY_VOTE_INSERT_SQL = postgres_insert(_vote).on_conflict_do_nothing().returning(_vote.c.id, _vote.c.cast_on)
_latest_vote_day = select(_vote.c.cast_on).where(_vote.c.fact_id == bindparam("fact_id")).order_by(_vote.c._cast_at.desc(), _vote.c.id.desc()).limit(1)
FETCH_ACCOUNT_VOTE_DAY_SQL = _latest_vote_day.where(_vote.c.account_id == bindparam("account_id"))
FETCH_HASH_VOTE_DAY_SQL = _latest_vote_day.where(_vote.c.voter_hash == bindparam("voter_hash"))
APPLY_FACT_FLAG_SQL = (
    update(_fact)
    .where(_fact.c.id == bindparam("fact_id"))
    .values(
        _flagged_at=func.coalesce(_fact.c._flagged_at, bindparam("new_instant", type_=DateTime(timezone=True))),
        _flagged_at_utc_offset_minutes=func.coalesce(_fact.c._flagged_at_utc_offset_minutes, bindparam("new_offset_minutes", type_=SmallInteger)),
    )
    .returning(*_stored_fact_columns)
)
APPLY_FACT_HIDING_SQL = (
    update(_fact)
    .where(_fact.c.id == bindparam("fact_id"))
    .values(
        _hidden_at=func.coalesce(_fact.c._hidden_at, bindparam("new_instant", type_=DateTime(timezone=True))),
        _hidden_at_utc_offset_minutes=func.coalesce(_fact.c._hidden_at_utc_offset_minutes, bindparam("new_offset_minutes", type_=SmallInteger)),
    )
    .returning(*_stored_fact_columns)
)
APPLY_FACT_RESTORATION_SQL = update(_fact).where(_fact.c.id == bindparam("fact_id")).values(_hidden_at=None, _hidden_at_utc_offset_minutes=None).returning(*_stored_fact_columns)


def build_stored_community_fact(row: RowMapping) -> StoredCommunityFact:
    """Builds the stored fact of one row of the column list of these queries, with the pair of its first flag as one instant or None."""
    return StoredCommunityFact(
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
        flagged_at=None if row["flagged_at"] is None else OffsetInstant(row["flagged_at"], row["flagged_at_utc_offset_minutes"]),
        is_hidden=row["is_hidden"],
    )


def build_optional_stored_community_fact(row: RowMapping | None) -> StoredCommunityFact | None:
    """Builds the stored fact of one read row, or None for no row."""
    return None if row is None else build_stored_community_fact(row)


def build_vote_voter_columns(voter: Voter) -> dict[str, Any]:
    """Builds the three columns that tell a vote of an account from a vote of a person without one, so that the checks of the table hold."""
    if isinstance(voter, AccountVoter):
        return {"is_cast_with_account": True, "account_id": voter.account_id, "voter_hash": None}
    return {"is_cast_with_account": False, "account_id": None, "voter_hash": voter.voter_hash}


def fetch_stored_facts_in_area(connection: Connection, south: float, west: float, north: float, east: float, limit: int) -> tuple[StoredCommunityFact, ...]:
    """
    Read the visible facts whose point lies in the rectangle, the edge included, ordered by identity and at most limit of them.

    The rectangle is compared as geometry, because the edges of a geography rectangle are geodesic and bulge north of the parallels, so
    a point near the southern edge the client sent would fall outside it. A geozone counts by its point, not by its circle. The caller
    passes one more than the cap it shows, to learn whether the rectangle holds more.
    """
    parameters = {"south": float(south), "west": float(west), "north": float(north), "east": float(east), "row_limit": limit}
    return tuple(build_stored_community_fact(row) for row in connection.execute(FETCH_STORED_FACTS_IN_AREA_SQL, parameters).mappings())


def fetch_stored_fact(connection: Connection, fact_id: int) -> StoredCommunityFact | None:
    """Read one fact by its identifier in any status, a fact removed in OpenStreetMap included, or None when it is hidden or missing."""
    return build_optional_stored_community_fact(connection.execute(FETCH_STORED_FACT_SQL, {"fact_id": fact_id}).mappings().one_or_none())


def fetch_stored_nearby_facts(connection: Connection, fact_type: FactType, lat: float, lon: float, distance_m: float) -> tuple[StoredNearbyFact, ...]:
    """Read the visible facts of one type within distance_m of the point, the distance included, nearest first and by identity among equals."""
    parameters = {"fact_type": fact_type, "lat": float(lat), "lon": float(lon), "distance": float(distance_m)}
    return tuple(StoredNearbyFact(build_stored_community_fact(row), row["distance_m"]) for row in connection.execute(FETCH_STORED_NEARBY_FACTS_SQL, parameters).mappings())


def fetch_stored_flagged_facts(connection: Connection) -> tuple[StoredCommunityFact, ...]:
    """Read every flagged fact, the hidden ones included, the most recently flagged first and by identity descending among equals."""
    return tuple(build_stored_community_fact(row) for row in connection.execute(FETCH_STORED_FLAGGED_FACTS_SQL).mappings())


def fetch_stored_fact_for_vote(connection: Connection, fact_id: int) -> StoredCommunityFact | None:
    """
    Lock a fact for a vote and read it as it is once locked, hidden or removed in OpenStreetMap or not, or None when it does not exist.

    The lock is a share lock, so a vote waits for a publication of a fresh OpenStreetMap copy that holds the fact and for a moderation of
    it, while two votes on one fact do not wait for each other. The caller sets and restores the limit of the wait around this call.
    """
    return build_optional_stored_community_fact(connection.execute(FETCH_STORED_FACT_FOR_VOTE_SQL, {"fact_id": fact_id}).mappings().one_or_none())


def fetch_stored_fact_for_change(connection: Connection, fact_id: int) -> StoredCommunityFact | None:
    """Lock a fact for a flag, a hiding or a restoration and read it as it is once locked, or None when it does not exist; a vote insert does not block this lock."""
    return build_optional_stored_community_fact(connection.execute(FETCH_STORED_FACT_FOR_CHANGE_SQL, {"fact_id": fact_id}).mappings().one_or_none())


def fetch_taken_vote_day(connection: Connection, fact_id: int, voter: Voter) -> date:
    """Read the calendar day of the latest vote of the person on the fact, which is the vote that refused a new one on its day."""
    if isinstance(voter, AccountVoter):
        return connection.execute(FETCH_ACCOUNT_VOTE_DAY_SQL, {"fact_id": fact_id, "account_id": voter.account_id}).scalar_one()
    return connection.execute(FETCH_HASH_VOTE_DAY_SQL, {"fact_id": fact_id, "voter_hash": voter.voter_hash}).scalar_one()


def apply_vote_row(connection: Connection, fact_id: int, verdict: VoteVerdict, voter: Voter, cast_at: OffsetInstant) -> StoredVoteInsert | None:
    """
    Insert one vote and give its identifier and day, or None when the person already has a vote of that day on the fact.

    A vote of an account that no longer exists becomes VoteAccountMissingError and leaves the transaction aborted; any other
    integrity failure propagates unchanged.
    """
    parameters = {
        "fact_id": fact_id,
        "verdict": verdict,
        **build_vote_voter_columns(voter),
        "_cast_at": cast_at.instant,
        "_cast_at_utc_offset_minutes": cast_at.utc_offset_minutes,
    }
    try:
        row = connection.execute(APPLY_VOTE_INSERT_SQL, parameters).one_or_none()
    except IntegrityError as error:
        if isinstance(error.orig, ForeignKeyViolation) and error.orig.diag.constraint_name == VOTE_ACCOUNT_CONSTRAINT_NAME:
            raise VoteAccountMissingError(VOTE_ACCOUNT_MISSING_MESSAGE) from None
        raise
    return None if row is None else StoredVoteInsert(vote_id=row.id, cast_on=row.cast_on)


def apply_vote_insert(connection: Connection, fact_id: int, verdict: VoteVerdict, voter: Voter, cast_at: OffsetInstant) -> VoteInsertOutcome:
    """
    Store a vote at the instant the caller supplies, or say which day refused it.

    The database keeps the daily limit: the insert does nothing when the person already voted on the fact on the same calendar day in
    Europe/Warsaw, and the answer is then the day of that vote. The caller takes cast_at from the business clock after the lock of the fact.
    A vote of an account that no longer exists raises VoteAccountMissingError and leaves the transaction aborted, so the caller rolls back.
    """
    stored = apply_vote_row(connection, fact_id, verdict, voter, cast_at)
    if stored is not None:
        return stored
    return VoteDayTaken(cast_on=fetch_taken_vote_day(connection, fact_id, voter))


def apply_fact_insert(connection: Connection, content: FactContent, idempotency_key: bytes, created_at: OffsetInstant, author: Voter) -> FactInsertOutcome:
    """
    Save a report or a geozone and the confirmation of its author as its first vote, once per idempotency key.

    A first save stores the fact and the confirmation at created_at and gives the fact with true. A repeated save with the same key waits
    for the first one to end, then reads the fact stored under the key, hidden or not, stores nothing and gives it with false; the caller
    compares its content. The point is built from the bound longitude and latitude. A failure of the vote, such as an author whose account
    no longer exists, leaves the transaction aborted, so the caller rolls it back and neither the fact nor the vote is stored.
    """
    parameters = {
        "fact_type": content.fact_type,
        "source": FactSource.USER_REPORT,
        "lat": float(content.lat),
        "lon": float(content.lon),
        "geozone_radius_m": content.geozone_radius_m,
        "description": content.description,
        "step_count": content.step_count,
        "is_sample": False,
        "idempotency_key": idempotency_key,
        "is_removed_from_osm": False,
        "_created_at": created_at.instant,
        "_created_at_utc_offset_minutes": created_at.utc_offset_minutes,
    }
    row = connection.execute(APPLY_FACT_INSERT_SQL, parameters).mappings().one_or_none()
    if row is None:
        stored = connection.execute(FETCH_FACT_BY_IDEMPOTENCY_KEY_SQL, {"idempotency_key": idempotency_key}).mappings().one()
        return FactInsertOutcome(fact=build_stored_community_fact(stored), is_created=False)
    fact = build_stored_community_fact(row)
    if apply_vote_row(connection, fact.id, VoteVerdict.CONFIRM, author, created_at) is None:
        raise RuntimeError("The first vote of a new fact met an earlier vote")
    return FactInsertOutcome(fact=fact, is_created=True)


def apply_fact_flag(connection: Connection, fact_id: int, flagged_at: OffsetInstant) -> StoredCommunityFact:
    """Mark a fact flagged at the instant given and keep the first instant when it is already flagged; the source and the hidden mark are not checked here."""
    parameters = {"fact_id": fact_id, "new_instant": flagged_at.instant, "new_offset_minutes": flagged_at.utc_offset_minutes}
    return build_stored_community_fact(connection.execute(APPLY_FACT_FLAG_SQL, parameters).mappings().one())


def apply_fact_hiding(connection: Connection, fact_id: int, hidden_at: OffsetInstant) -> StoredCommunityFact:
    """Hide a fact at the instant given and keep the first instant when it is already hidden; the database refuses a fact that was never flagged."""
    parameters = {"fact_id": fact_id, "new_instant": hidden_at.instant, "new_offset_minutes": hidden_at.utc_offset_minutes}
    return build_stored_community_fact(connection.execute(APPLY_FACT_HIDING_SQL, parameters).mappings().one())


def apply_fact_restoration(connection: Connection, fact_id: int) -> StoredCommunityFact:
    """Clear the hidden mark of a fact, which keeps its flag and all its votes, and change nothing when it is not hidden."""
    return build_stored_community_fact(connection.execute(APPLY_FACT_RESTORATION_SQL, {"fact_id": fact_id}).mappings().one())
