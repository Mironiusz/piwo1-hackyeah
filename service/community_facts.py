"""
The rules of the nine operations of the community facts of `docs/product/api_contract.md`, sections Facts and Moderation, on the data layer of `data/community_facts.py`.

Visibility has two rules, both kept by the data layer: the area and the nearby check leave out hidden facts and facts
removed in OpenStreetMap, a reading by identifier leaves out only hidden ones. A hidden fact is missing for every operation
that is not a moderator one, a vote, a flag and a repeated save included, while a moderator sees it. Every read takes its facts
and their votes from one read-only snapshot, and the status of each fact comes from the one rule of M4 over all its votes
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-5, D-6).

Every write is one transaction of the API engine in its READ COMMITTED default, which builds its answer before it ends and
leaves nothing behind when it fails. A save stores the report and the confirmation of its author together once per
idempotency key; a repeated key answers the first fact only when it is not hidden and its content is the same (D-10). A vote
locks its fact first, waiting up to 120 seconds for the publication of a fresh OpenStreetMap copy or a moderation that holds
it, then checks visibility and takes its instant from the business clock, so a wait through midnight counts on the day of the
write (D-12). A flag records nothing about who flagged, and only a flagged fact is hidden or restored. A vote or a save of an
account deleted after its session was resolved answers `SessionExpiredError` (D-7).

Nothing here logs, and no answer carries an author, a voter, a weight or the hash of a person without an account.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from accessibility_db.closed_lists import FactSource, FactType, VoteVerdict
from accessibility_db.tables import build_offset_instant
from sqlalchemy import Connection

from common_time import build_business_day, fetch_business_now
from data.community_facts import (
    AccountVoter,
    AnonymousVoter,
    FactContent,
    StoredCommunityFact,
    VoteAccountMissingError,
    VoteDayTaken,
    Voter,
    apply_fact_insert,
    apply_vote_insert,
    fetch_stored_fact,
    fetch_stored_fact_for_change,
    fetch_stored_fact_for_vote,
    fetch_stored_facts_in_area,
    fetch_stored_flagged_facts,
    fetch_stored_nearby_facts,
)
from data.community_facts import apply_fact_flag as apply_stored_fact_flag
from data.community_facts import apply_fact_hiding as apply_stored_fact_hiding
from data.community_facts import apply_fact_restoration as apply_stored_fact_restoration
from data.engine import API_STATEMENT_TIMEOUT_MS, apply_statement_timeout, fetch_api_engine, fetch_read_only_snapshot
from data.route_facts import fetch_fact_votes
from service.actors import AccountActor
from service.anonymous_voters import AnonymousVoterInput, build_anonymous_voter_hash, fetch_voter_hash_key
from service.fact_rules import (
    AREA_FACT_LIMIT,
    NEARBY_FACT_DISTANCE_M,
    FactArea,
    FactCreationInput,
    build_fact_idempotency_key,
    build_repeat_allowed_at,
    resolve_fact_creation_input,
)
from service.fact_status import FactView, build_fact_views
from service.session_tokens import SessionExpiredError

VOTE_LOCK_WAIT_MS = 120000

type FactActor = AccountActor | AnonymousVoterInput


class FactNotFoundError(Exception):
    """No fact has the identifier, or the fact is hidden and the operation is not a moderator one."""


class IdempotencyKeyReusedError(Exception):
    """The idempotency key of a save was already used for a save with a different content."""


class VoteTooSoonError(Exception):
    """The person already voted on the fact on the same calendar day; `repeat_allowed_at` is the midnight from which the next vote is accepted."""

    def __init__(self, repeat_allowed_at: datetime) -> None:
        super().__init__()
        self.repeat_allowed_at = repeat_allowed_at


class FactNotFlaggableError(Exception):
    """The fact is from OpenStreetMap, which cannot be flagged."""


class FactNotFlaggedError(Exception):
    """The fact is not flagged, so it can be neither hidden nor restored."""


@dataclass(frozen=True)
class AreaFacts:
    """The facts of a rectangle, at most 1000 of them, and whether the rectangle holds more."""

    facts: tuple[FactView, ...]
    is_truncated: bool


@dataclass(frozen=True)
class NearbyFactView:
    """A fact of the nearby check with its distance from the point in whole metres."""

    view: FactView
    distance_m: int


@dataclass(frozen=True)
class FlaggedFactView:
    """A flagged fact as a moderator sees it: the fact, the day of its first flag and whether it is hidden."""

    view: FactView
    flagged_on: date
    is_hidden: bool


@dataclass(frozen=True)
class FactCreationResult:
    """The fact of a save and whether this save created it, a repeated save with the same key and content answering the first fact."""

    view: FactView
    is_created: bool


def fetch_facts_in_area(area: FactArea) -> AreaFacts:
    """Read the visible facts of a rectangle with their statuses, at most 1000, saying whether the rectangle holds more."""
    with fetch_read_only_snapshot(fetch_api_engine()) as connection:
        stored = fetch_stored_facts_in_area(connection, area.south, area.west, area.north, area.east, AREA_FACT_LIMIT + 1)
        views = fetch_fact_views(connection, stored[:AREA_FACT_LIMIT])
    return AreaFacts(facts=views, is_truncated=len(stored) > AREA_FACT_LIMIT)


def fetch_fact(fact_id: int) -> FactView:
    """Read one fact that is not hidden, in any status, with its status, or refuse a missing or hidden one with `FactNotFoundError`."""
    with fetch_read_only_snapshot(fetch_api_engine()) as connection:
        stored = fetch_stored_fact(connection, fact_id)
        if stored is None:
            raise FactNotFoundError
        (view,) = fetch_fact_views(connection, (stored,))
    return view


def fetch_nearby_facts(fact_type: FactType, lat: float, lon: float) -> tuple[NearbyFactView, ...]:
    """Read the visible facts of the type within 15 m of the point, nearest first, with their statuses and distances in whole metres."""
    with fetch_read_only_snapshot(fetch_api_engine()) as connection:
        nearby = fetch_stored_nearby_facts(connection, fact_type, lat, lon, NEARBY_FACT_DISTANCE_M)
        views = fetch_fact_views(connection, [item.fact for item in nearby])
    return tuple(NearbyFactView(view=view, distance_m=round(item.distance_m)) for item, view in zip(nearby, views, strict=True))


def fetch_flagged_facts() -> tuple[FlaggedFactView, ...]:
    """Read every flagged fact for a moderator, hidden ones included, the latest flag first, with its status, flag day and hidden mark."""
    with fetch_read_only_snapshot(fetch_api_engine()) as connection:
        stored = fetch_stored_flagged_facts(connection)
        views = fetch_fact_views(connection, stored)
    return tuple(build_flagged_fact_view(fact, view) for fact, view in zip(stored, views, strict=True))


def apply_fact_creation(request: FactCreationInput, key: UUID, author: FactActor, now: datetime) -> FactCreationResult:
    """
    Save a report or a geozone at `now`, an aware instant in the business zone, with the confirmation of its author, once per key.

    The input is checked and normalized first. A repeated key answers the first fact without storing anything, refusing a hidden
    fact with `FactNotFoundError` and a different content with `IdempotencyKeyReusedError`; an author whose account was deleted after
    its session was resolved ends in `SessionExpiredError` with nothing stored.
    """
    content = resolve_fact_creation_input(request)
    voter = build_fact_voter(author)
    try:
        with fetch_api_engine().begin() as connection:
            outcome = apply_fact_insert(connection, content, build_fact_idempotency_key(key), build_offset_instant(now), voter)
            fact = outcome.fact if outcome.is_created else resolve_repeated_save(outcome.fact, content)
            (view,) = fetch_fact_views(connection, (fact,))
    except VoteAccountMissingError:
        raise SessionExpiredError from None
    return FactCreationResult(view=view, is_created=outcome.is_created)


def apply_fact_vote(fact_id: int, verdict: VoteVerdict, actor: FactActor) -> FactView:
    """
    Store a confirmation or a denial of a fact that is not hidden and give the fact with its status after the vote.

    The fact is locked before anything is decided, waiting up to 120 seconds for a publication or a moderation that holds it,
    and the instant of the vote is read after the lock. A second vote of the person on the same calendar day is refused with
    `VoteTooSoonError` and the next midnight, a missing or hidden fact with `FactNotFoundError`, and an account deleted after its
    session was resolved with `SessionExpiredError`; none of them stores anything.
    """
    voter = build_fact_voter(actor)
    try:
        with fetch_api_engine().begin() as connection:
            apply_statement_timeout(connection, VOTE_LOCK_WAIT_MS)
            stored = fetch_stored_fact_for_vote(connection, fact_id)
            apply_statement_timeout(connection, API_STATEMENT_TIMEOUT_MS)
            if stored is None or stored.is_hidden:
                raise FactNotFoundError
            outcome = apply_vote_insert(connection, fact_id, verdict, voter, build_offset_instant(fetch_business_now()))
            if isinstance(outcome, VoteDayTaken):
                raise VoteTooSoonError(build_repeat_allowed_at(outcome.cast_on))
            (view,) = fetch_fact_views(connection, (stored,))
    except VoteAccountMissingError:
        raise SessionExpiredError from None
    return view


def apply_fact_flag(fact_id: int, now: datetime) -> None:
    """Flag a visible report, geozone or converted fact at `now`, keeping its first flag; a missing or hidden fact or one from OpenStreetMap is refused."""
    with fetch_api_engine().begin() as connection:
        stored = fetch_stored_fact_for_change(connection, fact_id)
        if stored is None or stored.is_hidden:
            raise FactNotFoundError
        if stored.source == FactSource.OPENSTREETMAP:
            raise FactNotFlaggableError
        apply_stored_fact_flag(connection, fact_id, build_offset_instant(now))


def apply_fact_hiding(fact_id: int, now: datetime) -> FlaggedFactView:
    """Hide a flagged fact at `now` for a moderator, keeping the first hiding, and give its moderator item; a missing or unflagged fact is refused."""
    with fetch_api_engine().begin() as connection:
        resolve_moderated_fact(fetch_stored_fact_for_change(connection, fact_id))
        hidden = apply_stored_fact_hiding(connection, fact_id, build_offset_instant(now))
        (view,) = fetch_fact_views(connection, (hidden,))
    return build_flagged_fact_view(hidden, view)


def apply_fact_restoration(fact_id: int) -> FlaggedFactView:
    """Restore a flagged fact for a moderator with the votes it kept and give its moderator item; a missing or unflagged fact is refused."""
    with fetch_api_engine().begin() as connection:
        resolve_moderated_fact(fetch_stored_fact_for_change(connection, fact_id))
        restored = apply_stored_fact_restoration(connection, fact_id)
        (view,) = fetch_fact_views(connection, (restored,))
    return build_flagged_fact_view(restored, view)


def fetch_fact_views(connection: Connection, facts: Sequence[StoredCommunityFact]) -> tuple[FactView, ...]:
    """Read the votes of all the facts in one read on the given connection and pair every fact with its status, in the given order."""
    return build_fact_views(facts, fetch_fact_votes(connection, [fact.id for fact in facts]))


def build_fact_voter(actor: FactActor) -> Voter:
    """Build the person of a vote: an account by its identifier, or a person without an account by the hash of its address and User-Agent."""
    if isinstance(actor, AccountActor):
        return AccountVoter(account_id=actor.account_id)
    return AnonymousVoter(voter_hash=build_anonymous_voter_hash(actor, fetch_voter_hash_key()))


def build_saved_content(fact: StoredCommunityFact) -> FactContent:
    """Build the content a stored report or geozone was saved with, to compare it with a repeated save."""
    return FactContent(
        fact_type=fact.fact_type,
        lat=fact.lat,
        lon=fact.lon,
        description=fact.description,
        step_count=fact.step_count,
        geozone_radius_m=fact.geozone_radius_m,
    )


def resolve_repeated_save(stored: StoredCommunityFact, content: FactContent) -> StoredCommunityFact:
    """Give the fact a repeated save answers, refusing a hidden one as missing first and a different content second."""
    if stored.is_hidden:
        raise FactNotFoundError
    if build_saved_content(stored) != content:
        raise IdempotencyKeyReusedError
    return stored


def resolve_moderated_fact(stored: StoredCommunityFact | None) -> StoredCommunityFact:
    """Give the locked fact a moderator hides or restores, refusing a missing one with `FactNotFoundError` and an unflagged one with `FactNotFlaggedError`."""
    if stored is None:
        raise FactNotFoundError
    if stored.flagged_at is None:
        raise FactNotFlaggedError
    return stored


def build_flagged_fact_view(fact: StoredCommunityFact, view: FactView) -> FlaggedFactView:
    """Build the moderator item of a flagged fact with the calendar day of its first flag in the business zone."""
    if fact.flagged_at is None:
        raise ValueError("A moderator item needs a flagged fact")
    return FlaggedFactView(view=view, flagged_on=build_business_day(fact.flagged_at.instant), is_hidden=fact.is_hidden)
