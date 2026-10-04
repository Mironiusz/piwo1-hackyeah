"""Check the scenarios of the route on an invented copy with the database and the routing service replaced at their seam."""

import math
from contextlib import contextmanager
from datetime import UTC, date, datetime

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import OffsetInstant, build_offset_instant

from config.logging import apply_logging_configuration
from data.osm_copy import OsmCopySnapshot
from data.route_facts import StoredVote
from data.valhalla import RoutingServiceNoRouteError, RoutingServiceTraceError, RoutingServiceUnavailableError, ValhallaRoute
from service import route_planning
from service.fact_status import FactStatus
from service.route_graph import RoutePoint, build_route_graph
from service.route_planning import PointOutsideKrakowError, resolve_route
from service.route_segments import RoutingUnavailableError, SegmentState
from tests.common_route_network import INVENTED_STATE_AT, InventedNode, InventedWay, build_invented_fact, build_invented_network, build_invented_trace

pytestmark = pytest.mark.usefixtures("runtime_settings")

NODES = {node.id: node for node in (InventedNode(1, 0, 0), InventedNode(2, 100, 0), InventedNode(3, 200, 0), InventedNode(4, 100, 100))}
SHORT, DETOUR = 10, 20
WAYS = [InventedWay(SHORT, (1, 2, 3)), InventedWay(DETOUR, (1, 4, 3))]
START = RoutePoint(NODES[1].lat, NODES[1].lon)
DESTINATION = RoutePoint(NODES[3].lat, NODES[3].lon)
WHEELCHAIR = frozenset({"stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"})
ROUTE_NODES = {SHORT: [1, 2, 3], DETOUR: [1, 4, 3]}


def build_midpoint(first: int, second: int) -> tuple[float, float]:
    """Give the middle of two invented nodes as latitude and longitude."""
    return (NODES[first].lat + NODES[second].lat) / 2, (NODES[first].lon + NODES[second].lon) / 2


BLOCKING_POINTS = {SHORT: (build_midpoint(1, 2), build_midpoint(2, 3)), DETOUR: (build_midpoint(1, 4), build_midpoint(4, 3))}


def build_votes(fact_id: int, status: FactStatus) -> list[StoredVote]:
    """Give the votes of a fact that yield the status asked for."""
    instant = build_offset_instant(datetime(2026, 10, 3, 9, tzinfo=UTC))
    if status == FactStatus.CONFIRMED:
        return [StoredVote(fact_id * 10 + index, fact_id, VoteVerdict.CONFIRM, True, instant, 500 + index, None) for index in range(2)]
    return [StoredVote(fact_id * 10, fact_id, VoteVerdict.CONFIRM, False, instant, None, bytes([fact_id % 256]) * 32)]


class InventedWorld:
    """The copy, its facts and a routing service that honours or drops exclusions, as a test sets them."""

    def __init__(self) -> None:
        """Start with a copy served by the routing service and no facts."""
        self.graph = build_route_graph(build_invented_network(list(NODES.values()), WAYS), INVENTED_STATE_AT)
        self.copy: OsmCopySnapshot | None = OsmCopySnapshot(1, OffsetInstant(INVENTED_STATE_AT, 0), "invented.osm.pbf")
        self.served_instant = math.floor(INVENTED_STATE_AT.timestamp())
        self.facts: list = []
        self.statuses: dict[int, FactStatus] = {}
        self.outside: tuple[str, ...] = ()
        self.drops_exclusions = False
        self.route_failure: Exception | None = None
        self.trace_failures: list[Exception] = []
        self.route_calls: list[dict] = []
        self.trace_calls: list[dict] = []
        self.scripted_routes: list[str | Exception | None] = []

    def add_fact(self, fact, status: FactStatus) -> None:
        """Store a fact with the status its votes give."""
        self.facts.append(fact)
        self.statuses[fact.id] = status

    def fetch_route(self, body: dict) -> ValhallaRoute:
        """Answer the short way unless it is excluded, else the detour, else 442."""
        self.route_calls.append(body)
        if self.route_failure is not None:
            raise self.route_failure
        scripted = self.scripted_routes.pop(0) if self.scripted_routes else None
        if isinstance(scripted, Exception):
            raise scripted
        if scripted is not None:
            return ValhallaRoute(scripted, 0.2)
        excluded = {(round(location["lat"], 9), round(location["lon"], 9)) for location in body.get("exclude_locations", [])}
        for way_id in (SHORT, DETOUR):
            blocking = {(round(lat, 9), round(lon, 9)) for lat, lon in BLOCKING_POINTS[way_id]}
            if self.drops_exclusions or not blocking & excluded:
                return ValhallaRoute(f"way-{way_id}", 0.2)
        raise RoutingServiceNoRouteError("invented 442")

    def fetch_trace(self, body: dict):
        """Trace the invented route named by its shape."""
        self.trace_calls.append(body)
        if self.trace_failures:
            raise self.trace_failures.pop(0)
        way_id = int(body["encoded_polyline"].removeprefix("way-"))
        return build_invented_trace(NODES, [(way_id, ROUTE_NODES[way_id])])

    def fetch_votes(self, _connection, fact_ids) -> tuple[StoredVote, ...]:
        """Give the votes of the facts asked for."""
        return tuple(vote for fact_id in fact_ids for vote in build_votes(fact_id, self.statuses[fact_id]))


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> InventedWorld:
    """Replace the database, the boundary and the routing service at their seam with an invented world."""
    invented = InventedWorld()

    @contextmanager
    def fetch_invented_snapshot(_engine):
        """Give no connection, since every read is replaced."""
        yield None

    monkeypatch.setattr(route_planning, "fetch_api_engine", lambda: None)
    monkeypatch.setattr(route_planning, "fetch_read_only_snapshot", fetch_invented_snapshot)
    monkeypatch.setattr(route_planning, "fetch_current_osm_copy", lambda _connection: invented.copy)
    monkeypatch.setattr(route_planning, "resolve_points_outside_krakow", lambda _state_at, _start, _destination: invented.outside)
    monkeypatch.setattr(route_planning, "fetch_served_copy_instant", lambda: invented.served_instant)
    monkeypatch.setattr(route_planning, "fetch_route_graph", lambda _connection, _state_at: invented.graph)
    monkeypatch.setattr(route_planning, "fetch_route_facts", lambda _connection, _area, _distance, types, _ways: tuple(fact for fact in invented.facts if fact.fact_type.value in types))
    monkeypatch.setattr(route_planning, "fetch_fact_votes", invented.fetch_votes)
    monkeypatch.setattr(route_planning, "fetch_geozone_ways", lambda _connection, _ids: ())
    monkeypatch.setattr(route_planning, "fetch_valhalla_route", invented.fetch_route)
    monkeypatch.setattr(route_planning, "fetch_valhalla_trace", invented.fetch_trace)
    return invented


def build_stairs_report(fact_id: int, way_id: int) -> object:
    """Build a report of stairs 5 m beside the middle node of a way."""
    node = NODES[2] if way_id == SHORT else NODES[4]
    return build_invented_fact(fact_id, FactType.STAIRS, node, nearest_way_id=way_id, north_shift_m=5 if way_id == SHORT else -5)


def build_way_steps(fact_id: int, way_id: int) -> object:
    """Build the fact of OpenStreetMap of a way of steps."""
    node = NODES[2] if way_id == SHORT else NODES[4]
    return build_invented_fact(fact_id, FactType.STAIRS, node, FactSource.OPENSTREETMAP, (OsmElementType.WAY, way_id))


def build_way_ids(answer_route) -> set[str]:
    """Give the states of the network segments of a route."""
    return {segment.state for segment in answer_route.segments[1:-1]}


def test_scenario_one_route_without_barriers(world: InventedWorld) -> None:
    """Answer the short way with every segment in a state of M7, no alternative and the day of the copy."""
    answer = resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert answer.barrier_free_route_exists is True
    assert answer.alternative is None
    assert answer.osm_copy_date == date(2026, 10, 2)
    assert {segment.state for segment in answer.route.segments} <= {SegmentState.BARRIER, SegmentState.NO_BARRIER, SegmentState.PARTIAL_DATA, SegmentState.NO_DATA}
    assert answer.route.length_m == 200


def test_scenario_two_unverified_stairs_get_an_alternative(world: InventedWorld) -> None:
    """Keep an unverified report of stairs, make its segment barrier and propose the detour naming the stairs as unverified (AC-4)."""
    world.add_fact(build_stairs_report(1, SHORT), FactStatus.UNVERIFIED)
    answer = resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert SegmentState.BARRIER in {segment.state for segment in answer.route.segments}
    assert answer.alternative is not None
    assert [(item.view.fact.id, item.view.status.status) for item in answer.alternative.avoided_barriers] == [(1, FactStatus.UNVERIFIED)]
    assert answer.alternative.route.length_m > answer.route.length_m


def test_scenario_three_no_route_without_barriers(world: InventedWorld) -> None:
    """Answer the path with the fewest stairs, say no route without barriers exists and name where the stairs are (AC-5)."""
    world.add_fact(build_way_steps(1, SHORT), FactStatus.UNVERIFIED)
    world.add_fact(build_way_steps(2, DETOUR), FactStatus.UNVERIFIED)
    answer = resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert answer.barrier_free_route_exists is False
    assert [item.view.fact.id for item in answer.route.profile_barriers] == [1]
    assert answer.route.length_m == 200


@pytest.mark.parametrize("failure", [RoutingServiceUnavailableError("down"), RoutingServiceUnavailableError("timeout"), RoutingServiceUnavailableError("error 171")])
def test_scenario_four_routing_does_not_answer(world: InventedWorld, failure: Exception) -> None:
    """End with routing_unavailable when the routing service is down, too late or failing."""
    world.route_failure = failure
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())


def test_failed_status_makes_routing_unavailable(world: InventedWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """End with routing_unavailable when /status cannot be read."""

    def fetch_failing_status() -> int:
        """Fail like a service that does not answer."""
        raise RoutingServiceUnavailableError("down")

    monkeypatch.setattr(route_planning, "fetch_served_copy_instant", fetch_failing_status)
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())


def test_scenario_five_fresh_copy_not_yet_served(world: InventedWorld) -> None:
    """End with routing_unavailable while the service serves the data of another copy, before any route is requested."""
    world.served_instant -= 86400
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert world.route_calls == []


def test_no_copy_makes_routing_unavailable(world: InventedWorld) -> None:
    """End with routing_unavailable when no copy is in use."""
    world.copy = None
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())


def test_scenario_six_dropped_exclusions_end_with_one_error_entry(world: InventedWorld, capsys: pytest.CaptureFixture[str]) -> None:
    """End with routing_unavailable and one ERROR entry without coordinates when the route crosses a confirmed barrier twice (AC-11)."""
    apply_logging_configuration()
    world.add_fact(build_stairs_report(1, SHORT), FactStatus.CONFIRMED)
    world.drops_exclusions = True
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    output = capsys.readouterr().out
    assert output.count("ERROR") == 1
    assert f"{START.lat:.4f}"[:6] not in output and f"{START.lon:.4f}"[:6] not in output
    assert len(world.route_calls) == 2


def test_scenario_seven_profile_without_barriers_is_not_assessed(world: InventedWorld) -> None:
    """Give every segment, the straight stretches included, the state not_assessed and list the stairs as additional (AC-7)."""
    world.add_fact(build_way_steps(1, SHORT), FactStatus.UNVERIFIED)
    answer = resolve_route(START, DESTINATION, frozenset(), frozenset({"rest_place"}))
    assert {segment.state for segment in answer.route.segments} == {SegmentState.NOT_ASSESSED}
    assert answer.barrier_free_route_exists is True
    assert [item.view.fact.id for item in answer.route.additional_barriers] == [1]
    assert answer.route.profile_barriers == ()


def test_scenario_eight_point_outside_krakow_computes_no_route(world: InventedWorld) -> None:
    """Refuse a start outside Kraków naming it, without calling the routing service."""
    world.outside = ("start",)
    with pytest.raises(PointOutsideKrakowError) as caught:
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert caught.value.points == ("start",)
    assert world.route_calls == [] and world.trace_calls == []


def test_trace_is_repeated_once_with_walk_or_snap(world: InventedWorld) -> None:
    """Trace again with walk_or_snap after error 443, and end with routing_unavailable after a second 443."""
    world.trace_failures = [RoutingServiceTraceError("443")]
    resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert [call["shape_match"] for call in world.trace_calls] == ["edge_walk", "walk_or_snap"]
    world.trace_failures = [RoutingServiceTraceError("443"), RoutingServiceTraceError("443")]
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())


def test_new_confirmed_report_changes_the_next_route(world: InventedWorld) -> None:
    """Route around a confirmed report of stairs saved after the first route, with the same graph and no import (AC-10)."""
    first = resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    world.add_fact(build_stairs_report(1, SHORT), FactStatus.CONFIRMED)
    second = resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert first.route.length_m == 200
    assert second.route.length_m > first.route.length_m
    assert second.barrier_free_route_exists is True


def test_logger_holds_no_coordinate_of_the_request(world: InventedWorld, capsys: pytest.CaptureFixture[str]) -> None:
    """Write no coordinate of the request into any log entry, also when the request fails."""
    apply_logging_configuration()
    world.route_failure = RoutingServiceUnavailableError("down")
    with pytest.raises(RoutingUnavailableError):
        resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    output = capsys.readouterr().out
    assert "RoutingServiceUnavailableError" in output
    for value in (START.lat, START.lon, DESTINATION.lat, DESTINATION.lon):
        assert f"{value:.3f}" not in output


COMMON = 30
SHARED_NODES = {**NODES, 0: InventedNode(0, -100, 0)}
SHARED_PATHS = {"short": [(COMMON, [0, 1]), (SHORT, [1, 2, 3])], "detour": [(COMMON, [0, 1]), (DETOUR, [1, 4, 3])]}
COMMON_BLOCKING = (round((SHARED_NODES[0].lat + NODES[1].lat) / 2, 9), round((SHARED_NODES[0].lon + NODES[1].lon) / 2, 9))


class SharedStartWorld(InventedWorld):
    """A copy whose start reaches both ways only through one common way, so a barrier on it lies on every route."""

    def __init__(self) -> None:
        """Add the common way from node 0 to node 1 before the short way and the detour."""
        super().__init__()
        self.graph = build_route_graph(build_invented_network(list(SHARED_NODES.values()), [InventedWay(COMMON, (0, 1)), *WAYS]), INVENTED_STATE_AT)

    def fetch_route(self, body: dict) -> ValhallaRoute:
        """Answer the common way with the short way unless one of them is excluded, else with the detour, else 442."""
        self.route_calls.append(body)
        excluded = {(round(location["lat"], 9), round(location["lon"], 9)) for location in body.get("exclude_locations", [])}
        blocked = {way_id for way_id, points in BLOCKING_POINTS.items() if {(round(lat, 9), round(lon, 9)) for lat, lon in points} & excluded}
        if COMMON_BLOCKING in excluded:
            blocked.add(COMMON)
        for name, edges in SHARED_PATHS.items():
            if not {way_id for way_id, _nodes in edges} & blocked:
                return ValhallaRoute(f"path-{name}", 0.3)
        raise RoutingServiceNoRouteError("invented 442")

    def fetch_trace(self, body: dict):
        """Trace the invented path named by its shape."""
        self.trace_calls.append(body)
        return build_invented_trace(SHARED_NODES, SHARED_PATHS[body["encoded_polyline"].removeprefix("path-")])


def test_alternative_of_the_route_with_the_fewest_barriers_may_cross_the_chosen_ones(monkeypatch: pytest.MonkeyPatch, world: InventedWorld) -> None:
    """Propose the detour around an unverified report when no route avoids the stairs every route crosses, instead of ending the request."""
    shared = SharedStartWorld()
    monkeypatch.setattr(route_planning, "fetch_route_graph", lambda _connection, _state_at: shared.graph)
    monkeypatch.setattr(route_planning, "fetch_route_facts", lambda _connection, _area, _distance, types, _ways: tuple(fact for fact in shared.facts if fact.fact_type.value in types))
    monkeypatch.setattr(route_planning, "fetch_fact_votes", shared.fetch_votes)
    monkeypatch.setattr(route_planning, "fetch_valhalla_route", shared.fetch_route)
    monkeypatch.setattr(route_planning, "fetch_valhalla_trace", shared.fetch_trace)
    shared.add_fact(build_invented_fact(1, FactType.STAIRS, InventedNode(0, -50, 0), FactSource.OPENSTREETMAP, (OsmElementType.WAY, COMMON)), FactStatus.UNVERIFIED)
    shared.add_fact(build_stairs_report(3, SHORT), FactStatus.UNVERIFIED)
    answer = resolve_route(RoutePoint(SHARED_NODES[0].lat, SHARED_NODES[0].lon), DESTINATION, WHEELCHAIR, frozenset())
    assert answer.barrier_free_route_exists is False
    assert {item.view.fact.id for item in answer.route.profile_barriers} == {1, 3}
    assert answer.alternative is not None
    assert [item.view.fact.id for item in answer.alternative.avoided_barriers] == [3]
    assert [item.view.fact.id for item in answer.alternative.route.profile_barriers] == [1]


def test_no_route_for_the_repeated_alternative_request_gives_no_alternative(world: InventedWorld) -> None:
    """Answer the route without an alternative when the alternative crosses an avoided barrier and its repeated request finds no path."""
    world.add_fact(build_stairs_report(3, SHORT), FactStatus.UNVERIFIED)
    world.add_fact(build_stairs_report(4, DETOUR), FactStatus.CONFIRMED)
    world.scripted_routes = [None, f"way-{DETOUR}", RoutingServiceNoRouteError("invented 442")]
    answer = resolve_route(START, DESTINATION, WHEELCHAIR, frozenset())
    assert answer.barrier_free_route_exists is True
    assert answer.alternative is None
    assert answer.route.length_m == 200
    assert len(world.route_calls) == 3
