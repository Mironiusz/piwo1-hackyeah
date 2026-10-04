"""Check the input layer of plan_route with the planning of the route replaced at its seam, so no database or routing service is needed."""

from datetime import date

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType
from fastapi.testclient import TestClient

from api.app import build_app
from config.logging import apply_logging_configuration
from data.route_facts import StoredFact
from service.fact_status import FactStatus, FactStatusResult, FactView
from service.route_graph import RoutePoint
from service.route_planning import PlannedAlternative, PlannedRoute, PointOutsideKrakowError, RouteAnswer, RouteSegment
from service.route_segments import MissingAttribute, RouteFactView, RoutingUnavailableError, SegmentState

pytestmark = pytest.mark.integration

INVENTED_REQUEST = {
    "start": {"lat": 50.0645, "lon": 19.9837},
    "destination": {"lat": 50.0678, "lon": 19.9914},
    "avoid": ["stairs", "high_kerb"],
    "need": ["ramp"],
}
INVENTED_COORDINATE_TEXTS = ("50.0645", "19.9837", "50.0678", "19.9914")
INVENTED_STAIRS = StoredFact(
    id=1042,
    fact_type=FactType.STAIRS,
    source=FactSource.OPENSTREETMAP,
    lat=50.0661,
    lon=19.9871,
    geozone_radius_m=None,
    description=None,
    step_count=3,
    is_sample=False,
    osm_element_type=OsmElementType.WAY,
    osm_element_id=77,
    osm_edited_on=date(2026, 9, 14),
    is_removed_from_osm=False,
)
INVENTED_RAMP = StoredFact(
    id=2001,
    fact_type=FactType.RAMP,
    source=FactSource.USER_REPORT,
    lat=50.0670,
    lon=19.9890,
    geozone_radius_m=None,
    description="invented ramp",
    step_count=None,
    is_sample=True,
    osm_element_type=None,
    osm_element_id=None,
    osm_edited_on=None,
    is_removed_from_osm=False,
)


def build_invented_route(state: SegmentState, missing: tuple[MissingAttribute, ...]) -> PlannedRoute:
    """Build an invented route of two segments with one barrier of the profile and one amenity."""
    stairs = RouteFactView(FactView(INVENTED_STAIRS, FactStatusResult(FactStatus.CONFIRMED, 2.0, 0.0, date(2026, 10, 3))), 120, False)
    ramp = RouteFactView(FactView(INVENTED_RAMP, FactStatusResult(FactStatus.UNVERIFIED, 1.0, 0.0, date(2026, 10, 1))), 300, False)
    segments = (
        RouteSegment(((19.9837, 50.0645), (19.9839, 50.0646)), 14, SegmentState.NO_DATA, (MissingAttribute.KERBS, MissingAttribute.STEPS), False),
        RouteSegment(((19.9839, 50.0646), (19.9914, 50.0678)), 600, state, missing, True),
    )
    return PlannedRoute(614, segments, (stairs,), (), (ramp,))


def apply_invented_answer(monkeypatch: pytest.MonkeyPatch, answer: RouteAnswer | Exception, calls: list[tuple] | None = None) -> None:
    """Replace the planning of the route and the graph built at start, so the request reaches only the input layer."""

    def resolve_invented(start: RoutePoint, destination: RoutePoint, avoid: frozenset[str], need: frozenset[str]) -> RouteAnswer:
        """Answer the invented route or raise the invented refusal, recording what the input layer passed on."""
        if calls is not None:
            calls.append((start, destination, avoid, need))
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr("api.route.resolve_route", resolve_invented)
    monkeypatch.setattr("api.route.build_route_graph_at_start", lambda: None)


def test_valid_request_answers_the_route_of_the_contract(_runtime_settings, monkeypatch) -> None:
    """Answer 200 with the dates as YYYY-MM-DD, the lines as longitude and latitude, and the facts with the fields of the contract."""
    route = build_invented_route(SegmentState.BARRIER, ())
    alternative = PlannedAlternative(build_invented_route(SegmentState.PARTIAL_DATA, (MissingAttribute.SURFACE,)), route.profile_barriers)
    calls: list[tuple] = []
    apply_invented_answer(monkeypatch, RouteAnswer(date(2026, 10, 2), False, route, alternative), calls)
    with TestClient(build_app()) as client:
        response = client.post("/api/routes", json=INVENTED_REQUEST)
    assert response.status_code == 200
    assert calls == [(RoutePoint(50.0645, 19.9837), RoutePoint(50.0678, 19.9914), frozenset({"stairs", "high_kerb"}), frozenset({"ramp"}))]
    body = response.json()
    assert set(body) == {"osm_copy_date", "barrier_free_route_exists", "route", "alternative"}
    assert body["osm_copy_date"] == "2026-10-02"
    assert body["barrier_free_route_exists"] is False
    assert body["route"]["length_m"] == 614
    assert body["route"]["segments"][0] == {
        "line": [[19.9837, 50.0645], [19.9839, 50.0646]],
        "length_m": 14,
        "state": "no_data",
        "missing_attributes": ["kerbs", "steps"],
        "is_marked_wheelchair_no": False,
    }
    assert body["route"]["segments"][1]["state"] == "barrier"
    assert body["route"]["segments"][1]["is_marked_wheelchair_no"] is True
    assert body["route"]["profile_barriers"] == [
        {
            "id": 1042,
            "type": "stairs",
            "point": {"lat": 50.0661, "lon": 19.9871},
            "geozone_radius_m": None,
            "description": None,
            "step_count": 3,
            "source": "openstreetmap",
            "status": "confirmed",
            "is_removed_from_osm": False,
            "osm_edited_on": "2026-09-14",
            "last_confirmed_on": "2026-10-03",
            "is_sample": False,
            "can_be_flagged": False,
            "distance_from_start_m": 120,
            "is_overruled_by_osm": False,
        }
    ]
    ramp = body["route"]["amenities"][0]
    assert (ramp["source"], ramp["osm_edited_on"], ramp["is_sample"], ramp["can_be_flagged"], ramp["last_confirmed_on"]) == ("user_report", None, True, True, "2026-10-01")
    assert body["route"]["additional_barriers"] == []
    assert body["alternative"]["route"]["segments"][1]["missing_attributes"] == ["surface"]
    assert [item["id"] for item in body["alternative"]["avoided_barriers"]] == [1042]


def test_not_assessed_is_passed_through_and_no_alternative_is_null(_runtime_settings, monkeypatch) -> None:
    """Pass the state not_assessed of a profile without barriers as it is, with no missing attribute, and write a missing alternative as null."""
    apply_invented_answer(monkeypatch, RouteAnswer(date(2026, 10, 2), True, build_invented_route(SegmentState.NOT_ASSESSED, ()), None))
    with TestClient(build_app()) as client:
        response = client.post("/api/routes", json={**INVENTED_REQUEST, "avoid": [], "need": []})
    assert response.status_code == 200
    assert response.json()["route"]["segments"][1]["state"] == "not_assessed"
    assert response.json()["route"]["segments"][1]["missing_attributes"] == []
    assert response.json()["alternative"] is None


def test_routing_unavailable_answers_503_without_a_route(_runtime_settings, monkeypatch) -> None:
    """Answer 503 routing_unavailable with the error alone when no route can be computed."""
    apply_invented_answer(monkeypatch, RoutingUnavailableError("invented failure"))
    with TestClient(build_app()) as client:
        response = client.post("/api/routes", json=INVENTED_REQUEST)
    assert response.status_code == 503
    assert response.json() == {"error": {"code": "routing_unavailable"}}


@pytest.mark.parametrize("points", [("start",), ("destination",), ("start", "destination")])
def test_point_outside_krakow_answers_422_naming_the_points(_runtime_settings, monkeypatch, points: tuple[str, ...]) -> None:
    """Answer 422 point_outside_krakow with the points outside, in the order start, destination."""
    apply_invented_answer(monkeypatch, PointOutsideKrakowError(points))
    with TestClient(build_app()) as client:
        response = client.post("/api/routes", json=INVENTED_REQUEST)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "point_outside_krakow", "points": list(points)}}


@pytest.mark.parametrize(
    ("change", "fields"),
    [
        ({"extra": True}, ["extra"]),
        ({"start": {"lat": "50.0645", "lon": 19.9837}}, ["start.lat"]),
        ({"start": {"lat": 91, "lon": 19.9837}}, ["start.lat"]),
        ({"destination": {"lat": 50.0678, "lon": -181}}, ["destination.lon"]),
        ({"avoid": ["stairs", "ramp"]}, ["avoid.1"]),
        ({"need": ["ramp", "ramp"]}, ["need"]),
        ({"avoid": ["stairs", "stairs"]}, ["avoid"]),
    ],
)
def test_request_outside_the_contract_is_refused_with_its_field_path(_runtime_settings, monkeypatch, change: dict[str, object], fields: list[str]) -> None:
    """Refuse an unknown field, a string for a number, a coordinate out of range, a type outside its list and a repeated type, before any route is planned."""
    calls: list[tuple] = []
    apply_invented_answer(monkeypatch, RoutingUnavailableError("never reached"), calls)
    with TestClient(build_app()) as client:
        response = client.post("/api/routes", json={**INVENTED_REQUEST, **change})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": fields}}
    assert calls == []


def test_request_log_names_plan_route_and_holds_no_coordinate(_runtime_settings, monkeypatch, capsys) -> None:
    """Log one completed request naming the operation plan_route, with no coordinate of the request in any entry."""
    apply_invented_answer(monkeypatch, RouteAnswer(date(2026, 10, 2), True, build_invented_route(SegmentState.NO_BARRIER, ()), None))
    app = build_app()
    apply_logging_configuration()
    with TestClient(app) as client:
        assert client.post("/api/routes", json=INVENTED_REQUEST).status_code == 200
    output = capsys.readouterr().out
    assert output.count("Request completed") == 1
    assert "operation=plan_route" in output
    assert not any(text in output for text in INVENTED_COORDINATE_TEXTS)


def test_authorization_header_is_ignored_and_no_session_token_is_answered(_runtime_settings, monkeypatch) -> None:
    """Plan the route of a request with any header Authorization as without it, and renew no token."""
    apply_invented_answer(monkeypatch, RouteAnswer(date(2026, 10, 2), True, build_invented_route(SegmentState.NO_BARRIER, ()), None))
    with TestClient(build_app()) as client:
        response = client.post("/api/routes", json=INVENTED_REQUEST, headers={"Authorization": "Bearer invented-token"})
    assert response.status_code == 200
    assert "Session-Token" not in response.headers
