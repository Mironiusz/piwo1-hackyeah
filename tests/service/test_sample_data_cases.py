"""Guards the eight sample facts, their votes and dates, their place conditions and their preserved history."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactSource, FactType, KerbPointState, VoteVerdict
from accessibility_db.tables import OffsetInstant, build_offset_instant
from sqlalchemy import Connection

from common_sample_data import (
    SampleDataFailure,
    SampleFactRow,
    SampleFailureReason,
    SampleNearbyWay,
    SampleNetworkPrerequisites,
    SampleVoteRow,
    StoredSample,
    StoredSampleVote,
    build_sample_voter_hash,
)
from data.osm_copy import OsmCopySnapshot
from data.route_facts import StoredVote
from service import sample_data
from service.fact_status import FactStatus, resolve_fact_status
from service.route_graph import build_route_graph
from service.sample_data import SAMPLE_DEFINITIONS, build_expected_sample_votes, build_sample_insert_rows, fetch_sample_kerb_contradiction, resolve_existing_sample, resolve_sample_prerequisites
from tests.common_route_network import INVENTED_STATE_AT, InventedNode, InventedWay, build_invented_network

WARSAW = ZoneInfo("Europe/Warsaw")
PRD_CONTENT = {
    -1: (FactType.HIGH_KERB, None, None, None, False, False),
    -2: (FactType.STAIRS, 4, "Brak poręczy po prawej stronie.", None, False, False),
    -3: (FactType.RAMP, None, None, None, False, False),
    -4: (FactType.POOR_SURFACE, None, "Remont chodnika, rozkopana nawierzchnia.", 25, False, False),
    -5: (FactType.HIGH_KERB, None, None, None, False, False),
    -6: (FactType.STAIRS, 3, "Schody pod domem pana [nazwisko], zawsze zastawione jego autem.", None, True, False),
    -7: (FactType.NARROW_PASSAGE, None, "Rusztowanie na całej szerokości chodnika.", 50, True, False),
    -8: (FactType.HIGH_KERB, None, "tekst z numerem telefonu, ukryty.", None, True, True),
}
PRD_STATUSES = {
    -1: (2.0, 0.0, 4, FactStatus.CONFIRMED),
    -2: (1.0, 0.0, 2, FactStatus.UNVERIFIED),
    -3: (2.0, 0.0, 4, FactStatus.CONFIRMED),
    -4: (1.0, 1.0, 4, FactStatus.DISPUTED),
    -5: (1.5, 0.0, 3, FactStatus.UNVERIFIED),
    -6: (1.0, 0.0, 2, FactStatus.UNVERIFIED),
    -7: (1.0, 1.0, 4, FactStatus.DISPUTED),
    -8: (1.0, 0.0, 2, FactStatus.UNVERIFIED),
}
LOADING_INSTANTS = [
    datetime(2026, 1, 10, 8, 0, tzinfo=WARSAW),
    datetime(2026, 7, 10, 8, 0, tzinfo=WARSAW),
    datetime(2026, 3, 30, 8, 0, tzinfo=WARSAW),
    datetime(2026, 10, 26, 10, 0, tzinfo=WARSAW),
]
KERB_WAY_ID = 9200000001
SIDE_WAY_ID = 9200000002


def build_stored_votes(rows: tuple[SampleVoteRow, ...]) -> list[StoredVote]:
    """Gives vote rows the identities storage would give them, in insert order, for the status rule."""
    return [StoredVote(index, row.fact_id, row.verdict, False, row.cast_at, None, row.voter_hash) for index, row in enumerate(rows, start=1)]


def build_fact_votes(vote_rows: tuple[SampleVoteRow, ...], fact_id: int) -> tuple[SampleVoteRow, ...]:
    """Selects the vote rows of one fact."""
    return tuple(row for row in vote_rows if row.fact_id == fact_id)


def test_dataset_matches_the_content_of_the_prd() -> None:
    """Keeps the identifiers, types, steps, descriptions, radii and moderation of the PRD table, with 25 votes in all."""
    assert [item.fact_id for item in SAMPLE_DEFINITIONS] == [-1, -2, -3, -4, -5, -6, -7, -8]
    for item in SAMPLE_DEFINITIONS:
        content = (item.fact_type, item.step_count, item.description, item.geozone_radius_m, item.flagged_minutes_before_loading is not None, item.hidden_minutes_before_loading is not None)
        assert content == PRD_CONTENT[item.fact_id]
    assert sum(len(item.votes) for item in SAMPLE_DEFINITIONS) == 25
    assert [item.fact_id for item in SAMPLE_DEFINITIONS if item.requires_kerb_contradiction] == [-5]


@pytest.mark.usefixtures("runtime_settings")
def test_sample_votes_give_every_fact_its_intended_status() -> None:
    """Derives the status of each fact through the one rule of M4 from its sample votes alone."""
    _fact_rows, vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, LOADING_INSTANTS[0])
    for fact_id, (confirmations, denials, persons, status) in PRD_STATUSES.items():
        votes = build_fact_votes(vote_rows, fact_id)
        result = resolve_fact_status(build_stored_votes(votes), False)
        assert (result.confirmations, result.denials, result.status) == (confirmations, denials, status)
        assert len({row.voter_hash for row in votes}) == persons


@pytest.mark.usefixtures("runtime_settings")
def test_one_anonymous_presenter_confirmation_brings_the_contradicted_kerb_to_confirmed() -> None:
    """Leaves S-5 one confirmation without an account below the threshold, as the contradiction scene needs."""
    loading_at = LOADING_INSTANTS[0]
    _fact_rows, vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, loading_at)
    votes = build_stored_votes(build_fact_votes(vote_rows, -5))
    presenter = StoredVote(len(votes) + 1, -5, VoteVerdict.CONFIRM, False, build_offset_instant(loading_at + timedelta(hours=1)), None, sha256(b"invented presenter").digest())
    assert resolve_fact_status(votes, False).status == FactStatus.UNVERIFIED
    result = resolve_fact_status([*votes, presenter], False)
    assert (result.confirmations, result.status) == (2.0, FactStatus.CONFIRMED)


def test_fictional_voter_hashes_are_stable_distinct_and_sha256() -> None:
    """Gives every one of the 25 sample votes its own fictional voter, without account or client inputs."""
    hashes = [build_sample_voter_hash(item.fact_id, index) for item in SAMPLE_DEFINITIONS for index in range(1, len(item.votes) + 1)]
    assert len(set(hashes)) == 25
    assert all(len(value) == 32 for value in hashes)
    assert hashes[0] == sha256(b"sample-data:voter:v2:-1:1").digest()


@pytest.mark.usefixtures("runtime_settings")
@pytest.mark.parametrize("loading_at", LOADING_INSTANTS)
def test_every_sample_date_lies_before_the_loading_with_its_own_offset(loading_at: datetime) -> None:
    """Dates every fact, vote, flag and hiding 0.1 to 2 days back in UTC, each with the Warsaw offset of its own instant."""
    fact_rows, vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, loading_at)
    loading_utc = loading_at.astimezone(UTC)
    instants: list[OffsetInstant] = []
    for row in fact_rows:
        definition = row.definition
        assert row.created_at.instant == loading_utc - timedelta(minutes=definition.created_minutes_before_loading)
        for minutes, pair in ((definition.flagged_minutes_before_loading, row.flagged_at), (definition.hidden_minutes_before_loading, row.hidden_at)):
            assert (pair is None) == (minutes is None)
            if pair is not None:
                assert pair.instant == loading_utc - timedelta(minutes=minutes)
                assert pair.instant >= row.created_at.instant
        assert row.hidden_at is None or row.flagged_at is not None
        instants.extend(pair for pair in (row.created_at, row.flagged_at, row.hidden_at) if pair is not None)
    created = {row.definition.fact_id: row.created_at.instant for row in fact_rows}
    for row in vote_rows:
        assert row.cast_at.instant >= created[row.fact_id]
        instants.append(row.cast_at)
    for pair in instants:
        assert timedelta(minutes=144) <= loading_utc - pair.instant <= timedelta(days=2)
        assert pair.utc_offset_minutes * 60 == pair.instant.astimezone(WARSAW).utcoffset().total_seconds()
        assert pair.instant.microsecond == 0


@pytest.mark.usefixtures("runtime_settings")
def test_dates_across_the_autumn_clock_change_keep_summer_and_winter_offsets() -> None:
    """Keeps +02:00 on the ramp created two days before a winter loading and +01:00 on the denial of the poor surface a day later."""
    fact_rows, vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, datetime(2026, 10, 26, 10, 0, tzinfo=WARSAW))
    assert {row.definition.fact_id: row.created_at.utc_offset_minutes for row in fact_rows}[-3] == 120
    assert [row.cast_at.utc_offset_minutes for row in build_fact_votes(vote_rows, -4)] == [120, 120, 60, 60]


@pytest.mark.usefixtures("runtime_settings")
@pytest.mark.parametrize("loading_at", LOADING_INSTANTS)
def test_retry_dates_the_votes_from_the_stored_creation_alone(loading_at: datetime) -> None:
    """Rebuilds the first loading's vote pairs from each stored creation pair, without knowing the first loading instant."""
    fact_rows, vote_rows = build_sample_insert_rows(SAMPLE_DEFINITIONS, loading_at)
    for row in fact_rows:
        stored_created_at = OffsetInstant(row.created_at.instant.astimezone(UTC), row.created_at.utc_offset_minutes)
        assert build_expected_sample_votes(row.definition, stored_created_at) == build_fact_votes(vote_rows, row.definition.fact_id)


def test_every_definition_accepts_its_measured_place(sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Accepts a coherent snapshot supporting all eight places and the kerb contradiction of S-5."""
    for definition, prerequisites in zip(SAMPLE_DEFINITIONS, sample_prerequisites, strict=True):
        resolve_sample_prerequisites(definition, prerequisites)


def test_missing_copy_fails_before_sample_writes(sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Distinguishes missing publication from an invalid individual place."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[0], replace(sample_prerequisites[0], has_copy=False))
    assert raised.value.reason == SampleFailureReason.COPY_MISSING


@pytest.mark.parametrize(
    "changes",
    [
        {"reference_exists": False},
        {"fact_id": -100},
        {"nearest_ways": ()},
        {"nearest_ways": (SampleNearbyWay(1, 0.0),)},
        {"nearest_ways": (SampleNearbyWay(1222443126, 15.01),)},
        {"nearest_ways": (SampleNearbyWay(1222443126, float("nan")),)},
        {"nearest_ways": (SampleNearbyWay(1222443126, 2.0), SampleNearbyWay(1, 2.0))},
    ],
)
def test_invalid_point_association_is_not_silently_relocated(changes: dict[str, object], sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Rejects a missing, distant, different or ambiguously nearest way."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[0], replace(sample_prerequisites[0], **changes))
    assert raised.value.reason == SampleFailureReason.SITE_INVALID


@pytest.mark.parametrize("index, distance", [(3, 25.01), (6, 50.01), (3, None), (6, float("nan")), (3, -1.0)])
def test_geozone_reference_way_must_lie_within_its_radius(index: int, distance: float | None, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Rejects a geozone whose reference way lies outside its circle or has no measured distance."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[index], replace(sample_prerequisites[index], reference_distance_m=distance))
    assert raised.value.reason == SampleFailureReason.SITE_INVALID


@pytest.mark.parametrize("index, distance", [(3, 25.0), (6, 7.67)])
def test_geozone_accepts_its_reference_way_inside_the_radius(index: int, distance: float, sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Accepts a reference way on or inside the circle, whatever other ways lie nearer."""
    resolve_sample_prerequisites(SAMPLE_DEFINITIONS[index], replace(sample_prerequisites[index], reference_distance_m=distance, nearest_ways=(SampleNearbyWay(1, 0.0),)))


def test_missing_kerb_contradiction_is_a_visible_failure(sample_prerequisites: tuple[SampleNetworkPrerequisites, ...]) -> None:
    """Refuses S-5 when the route graph does not establish the contradiction, never assuming it."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_sample_prerequisites(SAMPLE_DEFINITIONS[4], replace(sample_prerequisites[4], has_kerb_contradiction=False))
    assert raised.value.reason == SampleFailureReason.CONTRADICTION_MISSING


def build_kerb_network(kerb: KerbPointState | None, kerb_east_m: float, junction: bool) -> tuple[object, object]:
    """Builds a graph of one way with a kerb node, and optionally a side way that splits it before the kerb node."""
    nodes = [InventedNode(1, 0.0, 0.0), InventedNode(2, 10.0, 0.0), InventedNode(3, kerb_east_m, 0.0, kerb=kerb), InventedNode(4, 30.0, 0.0), InventedNode(5, 10.0, 20.0)]
    ways = [InventedWay(KERB_WAY_ID, (1, 2, 3, 4))]
    if junction:
        ways.append(InventedWay(SIDE_WAY_ID, (2, 5)))
    return build_route_graph(build_invented_network(nodes, ways), INVENTED_STATE_AT), OsmCopySnapshot(1, build_offset_instant(INVENTED_STATE_AT), "invented.osm.pbf")


@pytest.mark.parametrize(
    "kerb, kerb_east_m, junction, expected",
    [
        (KerbPointState.LOWERED, 10.5, False, True),
        (KerbPointState.LOWERED, 13.9, False, True),
        (KerbPointState.HIGH, 10.5, False, False),
        (KerbPointState.UNKNOWN, 10.5, False, False),
        (None, 10.5, False, False),
        (KerbPointState.LOWERED, 15.5, False, False),
        (KerbPointState.LOWERED, 12.0, True, False),
    ],
)
def test_kerb_contradiction_follows_the_rule_of_route_planning(kerb: KerbPointState | None, kerb_east_m: float, junction: bool, expected: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    """Requires a lowered kerb point within 5 m on the stretch the sample lies on; a high, unknown, distant or other-stretch kerb is none."""
    graph, copy = build_kerb_network(kerb, kerb_east_m, junction)
    point = InventedNode(0, 9.0, 0.0)
    definition = replace(SAMPLE_DEFINITIONS[4], latitude=point.lat, longitude=point.lon, reference_way_id=KERB_WAY_ID)
    monkeypatch.setattr(sample_data, "fetch_current_osm_copy", lambda _connection: copy)
    monkeypatch.setattr(sample_data, "fetch_route_graph", lambda _connection, _state_at: graph)
    assert fetch_sample_kerb_contradiction(Mock(spec=Connection), definition) is expected


def test_kerb_contradiction_needs_a_copy_and_the_reference_way(monkeypatch: pytest.MonkeyPatch) -> None:
    """Establishes nothing without a current copy or when the graph does not hold the reference way."""
    graph, copy = build_kerb_network(KerbPointState.LOWERED, 10.5, False)
    point = InventedNode(0, 9.0, 0.0)
    definition = replace(SAMPLE_DEFINITIONS[4], latitude=point.lat, longitude=point.lon, reference_way_id=KERB_WAY_ID)
    monkeypatch.setattr(sample_data, "fetch_route_graph", lambda _connection, _state_at: graph)
    monkeypatch.setattr(sample_data, "fetch_current_osm_copy", lambda _connection: None)
    assert not fetch_sample_kerb_contradiction(Mock(spec=Connection), definition)
    monkeypatch.setattr(sample_data, "fetch_current_osm_copy", lambda _connection: copy)
    assert not fetch_sample_kerb_contradiction(Mock(spec=Connection), replace(definition, reference_way_id=SIDE_WAY_ID))


def test_existing_samples_keep_their_original_history(stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]) -> None:
    """Validates the stored history without comparing it to a fresh clock or the current status."""
    for definition in SAMPLE_DEFINITIONS:
        resolve_existing_sample(definition, stored_samples[definition.fact_id], sample_votes[definition.fact_id])


@pytest.mark.parametrize("changes", [{"is_sample": False}, {"source": FactSource.OPENSTREETMAP}, {"fact_id": -100}])
def test_reserved_id_collision_does_not_overwrite_an_unrelated_fact(changes: dict[str, object], stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]) -> None:
    """Refuses an occupied identifier instead of allocating or replacing a fact."""
    with pytest.raises(SampleDataFailure) as raised:
        resolve_existing_sample(SAMPLE_DEFINITIONS[0], replace(stored_samples[-1], **changes), sample_votes[-1])
    assert raised.value.reason == SampleFailureReason.IDENTITY_COLLISION


@pytest.mark.parametrize(
    "index, changes",
    [
        (1, {"description": "Changed definition"}),
        (0, {"description": "Added description"}),
        (0, {"latitude": 50.0}),
        (1, {"step_count": 1}),
        (3, {"geozone_radius_m": 50}),
        (0, {"fact_type": FactType.LOWERED_KERB}),
        (0, {"idempotency_key": b"x" * 32}),
        (0, {"is_removed_from_osm": True}),
    ],
)
def test_definition_changes_are_not_reconciled_by_overwriting(
    index: int, changes: dict[str, object], stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]
) -> None:
    """Detects changed content and invalid provenance fields."""
    definition = SAMPLE_DEFINITIONS[index]
    with pytest.raises(SampleDataFailure) as raised:
        resolve_existing_sample(definition, replace(stored_samples[definition.fact_id], **changes), sample_votes[definition.fact_id])
    assert raised.value.reason == SampleFailureReason.CONTENT_MISMATCH


def test_missing_repeated_or_extra_sample_votes_are_an_integrity_error(stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]) -> None:
    """Does not fabricate a missing vote on a later day or accept a voter twice."""
    votes = sample_votes[-1]
    for broken in (votes[1:], (*votes, votes[0]), ()):
        with pytest.raises(SampleDataFailure) as raised:
            resolve_existing_sample(SAMPLE_DEFINITIONS[0], stored_samples[-1], broken)
        assert raised.value.reason == SampleFailureReason.INITIAL_VOTE_INVALID


@pytest.mark.parametrize(
    "changes",
    [{"verdict": VoteVerdict.CONFIRM}, {"is_cast_with_account": True}, {"account_id": 1}, {"voter_hash": b"x" * 32}, {"fact_id": -2}],
)
def test_changed_sample_vote_is_not_accepted(changes: dict[str, object], stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]) -> None:
    """Requires each fictional voter's exact verdict, without an account, on its own fact."""
    votes = sample_votes[-4]
    with pytest.raises(SampleDataFailure) as raised:
        resolve_existing_sample(SAMPLE_DEFINITIONS[3], stored_samples[-4], (*votes[:-1], replace(votes[-1], **changes)))
    assert raised.value.reason == SampleFailureReason.INITIAL_VOTE_INVALID


def test_sample_vote_moved_in_time_is_not_accepted(stored_samples: dict[int, StoredSample], sample_votes: dict[int, tuple[StoredSampleVote, ...]]) -> None:
    """Requires each vote's original instant and offset, dated from the stored creation."""
    votes = sample_votes[-3]
    last = votes[-1]
    for moved in (replace(last.cast_at, instant=last.cast_at.instant + timedelta(days=1)), replace(last.cast_at, utc_offset_minutes=120)):
        with pytest.raises(SampleDataFailure):
            resolve_existing_sample(SAMPLE_DEFINITIONS[2], stored_samples[-3], (*votes[:-1], replace(last, cast_at=moved)))


def test_fact_rows_carry_only_the_moderation_of_the_definition(sample_insert_rows: tuple[tuple[SampleFactRow, ...], tuple[SampleVoteRow, ...]]) -> None:
    """Flags S-6 and S-7, flags and hides S-8, and leaves the other facts without moderation."""
    fact_rows, _vote_rows = sample_insert_rows
    states = {row.definition.fact_id: (row.flagged_at is not None, row.hidden_at is not None) for row in fact_rows}
    assert states == {fact_id: content[4:] for fact_id, content in PRD_CONTENT.items()}
