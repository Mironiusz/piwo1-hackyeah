"""
Integration tests of the six public operations of the community facts through `build_app`, with the service and the session
resolution replaced.

They check every status, body and error envelope of `docs/product/api_contract.md`, section Facts: the exact Fact object,
201 and 200 of a save, 201 of a vote, 204 of a flag, the six refusals, unknown fields, wrong scalar types, invalid paths,
the renewed token on success and on a handled refusal, a refused token that is never turned into a person without an
account, the inputs of the identity read only for a person without an account, and a request log that holds no
identifying input (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-6; AC-1, AC-10 and AC-11 of
`COMMUNITY_FACTS_API_PRD.md`). No database and no network is used, and the client is built without the lifespan that loads
the graph of the route.
"""

from collections.abc import Callable
from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from accessibility_db.closed_lists import FactSource, FactType, OsmElementType, VoteVerdict
from accessibility_db.tables import build_offset_instant
from fastapi.testclient import TestClient

from api.app import build_app
from config.logging import apply_logging_configuration
from data.community_facts import StoredCommunityFact
from service.actors import AccountActor, SessionExpiredError, SessionResolution
from service.anonymous_voters import AnonymousVoterInput
from service.community_facts import (
    AreaFacts,
    FactCreationResult,
    FactNotFlaggableError,
    FactNotFoundError,
    IdempotencyKeyReusedError,
    NearbyFactView,
    VoteTooSoonError,
)
from service.fact_rules import FactArea, FactCreationInput, InvalidFactInputError
from service.fact_status import FactStatus, FactStatusResult, FactView

pytestmark = pytest.mark.integration

WARSAW = ZoneInfo("Europe/Warsaw")
SESSION_TOKEN = "private-session-token"
RENEWED_TOKEN = "private-renewed-token"
VALID_HEADERS = {"Authorization": f"Bearer {SESSION_TOKEN}"}
ACCOUNT = AccountActor(account_id=987654321, pseudonym="Wózek_KRK", is_moderator=False)
KEY = "6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40"
PERSON_ADDRESS = "203.0.113.7"
PERSON_AGENT = "Mozilla/5.0 (invented private agent)"
DESCRIPTION = "Trzy stopnie przy wejściu bocznym"
REPORT = StoredCommunityFact(
    id=1042,
    fact_type=FactType.STAIRS,
    source=FactSource.USER_REPORT,
    lat=50.0661,
    lon=19.9878,
    geozone_radius_m=None,
    description=DESCRIPTION,
    step_count=3,
    is_sample=False,
    osm_element_type=None,
    osm_element_id=None,
    osm_edited_on=None,
    is_removed_from_osm=False,
    flagged_at=build_offset_instant(datetime(2026, 10, 3, 18, 0, tzinfo=WARSAW)),
    is_hidden=False,
)
OSM_FACT = StoredCommunityFact(
    id=7,
    fact_type=FactType.HIGH_KERB,
    source=FactSource.OPENSTREETMAP,
    lat=50.0662,
    lon=19.9879,
    geozone_radius_m=None,
    description=None,
    step_count=None,
    is_sample=True,
    osm_element_type=OsmElementType.NODE,
    osm_element_id=9300000007,
    osm_edited_on=date(2026, 9, 14),
    is_removed_from_osm=False,
    flagged_at=None,
    is_hidden=False,
)
REPORT_VIEW = FactView(REPORT, FactStatusResult(FactStatus.UNVERIFIED, 0.5, 0.0, date(2026, 10, 4)))
OSM_VIEW = FactView(OSM_FACT, FactStatusResult(FactStatus.CONFIRMED, 2.0, 0.0, date(2026, 10, 3)))
REPORT_BODY = {
    "id": 1042,
    "type": "stairs",
    "point": {"lat": 50.0661, "lon": 19.9878},
    "geozone_radius_m": None,
    "description": DESCRIPTION,
    "step_count": 3,
    "source": "user_report",
    "status": "unverified",
    "is_removed_from_osm": False,
    "osm_edited_on": None,
    "last_confirmed_on": "2026-10-04",
    "is_sample": False,
    "can_be_flagged": True,
}
OSM_BODY = {
    "id": 7,
    "type": "high_kerb",
    "point": {"lat": 50.0662, "lon": 19.9879},
    "geozone_radius_m": None,
    "description": None,
    "step_count": None,
    "source": "openstreetmap",
    "status": "confirmed",
    "is_removed_from_osm": False,
    "osm_edited_on": "2026-09-14",
    "last_confirmed_on": "2026-10-03",
    "is_sample": True,
    "can_be_flagged": False,
}
AREA_REQUEST = {"south_west": {"lat": 50.064, "lon": 19.983}, "north_east": {"lat": 50.07, "lon": 19.995}}
NEARBY_REQUEST = {"type": "stairs", "point": {"lat": 50.0661, "lon": 19.9878}}
CREATE_REQUEST = {"idempotency_key": KEY, "type": "stairs", "point": {"lat": 50.0661, "lon": 19.9878}, "description": DESCRIPTION, "step_count": 3, "geozone_radius_m": None}


class InventedService:
    """The fact service and the session resolution replaced by invented answers, recording what they were called with."""

    def __init__(self) -> None:
        """Answer a person without an account for no header and an ordinary account for a token, and record nothing yet."""
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.answer: Callable[[], object] = lambda: None
        self.resolution: Callable[[], SessionResolution] = lambda: SessionResolution(actor=ACCOUNT, renewed_token=RENEWED_TOKEN)

    def resolve_request_actor(self, authorization: str | None, now: object) -> SessionResolution:
        """Record a resolution and answer a person without an account for no header, or the invented resolution."""
        self.calls.append(("resolve_request_actor", (authorization,)))
        return SessionResolution(actor=None, renewed_token=None) if authorization is None else self.resolution()

    def fetch_facts_in_area(self, area: FactArea) -> object:
        """Record an area read and answer it."""
        self.calls.append(("fetch_facts_in_area", (area,)))
        return self.answer()

    def fetch_fact(self, fact_id: int) -> object:
        """Record a read by identifier and answer it."""
        self.calls.append(("fetch_fact", (fact_id,)))
        return self.answer()

    def fetch_nearby_facts(self, fact_type: FactType, lat: float, lon: float) -> object:
        """Record a nearby check and answer it."""
        self.calls.append(("fetch_nearby_facts", (fact_type, lat, lon)))
        return self.answer()

    def apply_fact_creation(self, request: FactCreationInput, key: UUID, author: object, now: datetime) -> object:
        """Record a save and answer it."""
        self.calls.append(("apply_fact_creation", (request, key, author)))
        return self.answer()

    def apply_fact_vote(self, fact_id: int, verdict: VoteVerdict, actor: object) -> object:
        """Record a vote and answer it."""
        self.calls.append(("apply_fact_vote", (fact_id, verdict, actor)))
        return self.answer()

    def apply_fact_flag(self, fact_id: int, now: datetime) -> None:
        """Record a flag and answer it."""
        self.calls.append(("apply_fact_flag", (fact_id,)))
        self.answer()


def apply_refusal(error: Exception) -> Callable[[], object]:
    """Build an invented answer that raises a refusal of the service."""

    def raise_refusal() -> object:
        """Raise the refusal."""
        raise error

    return raise_refusal


@pytest.fixture
def service(_runtime_settings, monkeypatch: pytest.MonkeyPatch) -> InventedService:
    """Replace every call of the fact operations into the service and the session resolution with the invented service."""
    invented = InventedService()
    for name in ("fetch_facts_in_area", "fetch_fact", "fetch_nearby_facts", "apply_fact_creation", "apply_fact_vote", "apply_fact_flag"):
        monkeypatch.setattr(f"api.facts.{name}", getattr(invented, name))
    monkeypatch.setattr("api.sessions.resolve_request_actor", invented.resolve_request_actor)
    return invented


@pytest.fixture
def client(service: InventedService) -> TestClient:
    """A client of the whole application whose connection comes from an invented public address."""
    invented = TestClient(build_app(), client=(PERSON_ADDRESS, 50000), raise_server_exceptions=False)
    invented.headers["User-Agent"] = PERSON_AGENT
    return invented


def fetch_service_calls(service: InventedService) -> list[str]:
    """Give the names of the service calls other than the session resolution."""
    return [name for name, _arguments in service.calls if name != "resolve_request_actor"]


def test_list_facts_in_area_answers_the_facts_and_the_truncation(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: AreaFacts(facts=(REPORT_VIEW, OSM_VIEW), is_truncated=True)
    response = client.post("/api/facts/in-area", json=AREA_REQUEST)
    assert response.status_code == 200
    assert response.json() == {"facts": [REPORT_BODY, OSM_BODY], "is_truncated": True}
    assert service.calls[-1] == ("fetch_facts_in_area", (FactArea(south=50.064, west=19.983, north=50.07, east=19.995),))


@pytest.mark.parametrize(
    ("north_east", "fields"),
    [({"lat": 50.06, "lon": 19.995}, ["north_east.lat", "south_west.lat"]), ({"lat": 50.07, "lon": 19.983}, ["north_east.lon", "south_west.lon"])],
    ids=["not-south", "not-west"],
)
def test_area_with_unordered_corners_is_refused_before_any_read(client: TestClient, service: InventedService, north_east: dict[str, float], fields: list[str]) -> None:
    response = client.post("/api/facts/in-area", json={"south_west": AREA_REQUEST["south_west"], "north_east": north_east})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": fields}}
    assert fetch_service_calls(service) == []


def test_read_fact_answers_the_fact(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: REPORT_VIEW
    response = client.get("/api/facts/1042")
    assert response.status_code == 200
    assert response.json() == {"fact": REPORT_BODY}
    assert service.calls[-1] == ("fetch_fact", (1042,))


@pytest.mark.parametrize("path", ["/api/facts/-5", "/api/facts/0"])
def test_identifier_no_fact_can_have_reaches_the_service_and_is_not_found(client: TestClient, service: InventedService, path: str) -> None:
    service.answer = apply_refusal(FactNotFoundError())
    response = client.get(path)
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "fact_not_found"}}


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/api/facts/abc", None),
        ("GET", "/api/facts/1.5", None),
        ("GET", "/api/facts/9223372036854775808", None),
        ("POST", "/api/facts/abc/votes", {"verdict": "confirm"}),
        ("POST", "/api/facts/abc/flag", None),
    ],
)
def test_identifier_that_is_not_a_stored_integer_is_refused(client: TestClient, service: InventedService, method: str, path: str, payload: object) -> None:
    response = client.request(method, path, json=payload)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": ["id"]}}
    assert fetch_service_calls(service) == []


def test_find_nearby_facts_answers_each_fact_with_its_distance(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: (NearbyFactView(view=REPORT_VIEW, distance_m=8),)
    response = client.post("/api/facts/nearby", json=NEARBY_REQUEST)
    assert response.status_code == 200
    assert response.json() == {"facts": [{"fact": REPORT_BODY, "distance_m": 8}]}
    assert service.calls[-1] == ("fetch_nearby_facts", (FactType.STAIRS, 50.0661, 19.9878))


def test_first_save_answers_201_and_a_repeated_one_200(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: FactCreationResult(view=REPORT_VIEW, is_created=True)
    first = client.post("/api/facts", json=CREATE_REQUEST)
    service.answer = lambda: FactCreationResult(view=REPORT_VIEW, is_created=False)
    repeated = client.post("/api/facts", json=CREATE_REQUEST)
    assert (first.status_code, repeated.status_code) == (201, 200)
    assert first.json() == repeated.json() == {"fact": REPORT_BODY}
    request, key, author = service.calls[-1][1]
    assert request == FactCreationInput(FactType.STAIRS, 50.0661, 19.9878, DESCRIPTION, 3, None)
    assert key == UUID(KEY)
    assert isinstance(author, AnonymousVoterInput)
    assert (author.address.compressed, author.user_agent) == (PERSON_ADDRESS, PERSON_AGENT)


def test_save_without_the_optional_fields_passes_them_as_absent(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: FactCreationResult(view=REPORT_VIEW, is_created=True)
    response = client.post("/api/facts", json={"idempotency_key": KEY.upper(), "type": "ramp", "point": {"lat": 50, "lon": 19.9}})
    assert response.status_code == 201
    request, key, _author = service.calls[-1][1]
    assert request == FactCreationInput(FactType.RAMP, 50, 19.9, None, None, None)
    assert key == UUID(KEY)


def test_save_with_an_account_passes_the_account_and_renews_its_token(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: FactCreationResult(view=REPORT_VIEW, is_created=True)
    response = client.post("/api/facts", json=CREATE_REQUEST, headers=VALID_HEADERS)
    assert response.status_code == 201
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]
    assert service.calls[-1][1][2] == ACCOUNT


@pytest.mark.parametrize(
    ("refusal", "status", "body"),
    [
        (InvalidFactInputError("step_count"), 422, {"error": {"code": "invalid_request", "fields": ["step_count"]}}),
        (InvalidFactInputError("type"), 422, {"error": {"code": "invalid_request", "fields": ["type"]}}),
        (IdempotencyKeyReusedError(), 409, {"error": {"code": "idempotency_key_reused"}}),
        (FactNotFoundError(), 404, {"error": {"code": "fact_not_found"}}),
    ],
    ids=["field-outside-rules", "amenity-geozone", "key-reused", "hidden-on-retry"],
)
def test_save_refusals_follow_the_contract_and_keep_the_renewed_token(client: TestClient, service: InventedService, refusal: Exception, status: int, body: dict[str, object]) -> None:
    service.answer = apply_refusal(refusal)
    response = client.post("/api/facts", json=CREATE_REQUEST, headers=VALID_HEADERS)
    assert response.status_code == status
    assert response.json() == body
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


@pytest.mark.parametrize(
    ("change", "fields"),
    [
        ({"colour": "red"}, ["colour"]),
        ({"type": "bench"}, ["type"]),
        ({"step_count": "3"}, ["step_count"]),
        ({"step_count": True}, ["step_count"]),
        ({"geozone_radius_m": 10.5}, ["geozone_radius_m"]),
        ({"idempotency_key": KEY.replace("-", "")}, ["idempotency_key"]),
        ({"idempotency_key": 42}, ["idempotency_key"]),
        ({"point": {"lat": "50.0661", "lon": 19.9878}}, ["point.lat"]),
        ({"point": {"lat": 91, "lon": 19.9878}}, ["point.lat"]),
        ({"description": 7}, ["description"]),
    ],
)
def test_save_outside_its_shape_is_refused_before_the_service(client: TestClient, service: InventedService, change: dict[str, object], fields: list[str]) -> None:
    response = client.post("/api/facts", json={**CREATE_REQUEST, **change})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": fields}}
    assert fetch_service_calls(service) == []


@pytest.mark.parametrize("missing", ["idempotency_key", "type", "point"])
def test_save_without_a_required_field_is_refused(client: TestClient, service: InventedService, missing: str) -> None:
    response = client.post("/api/facts", json={key: value for key, value in CREATE_REQUEST.items() if key != missing})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": [missing]}}


def test_cast_vote_answers_201_with_the_fact_after_the_vote(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: REPORT_VIEW
    response = client.post("/api/facts/1042/votes", json={"verdict": "deny"}, headers=VALID_HEADERS)
    assert response.status_code == 201
    assert response.json() == {"fact": REPORT_BODY}
    assert service.calls[-1] == ("apply_fact_vote", (1042, VoteVerdict.DENY, ACCOUNT))
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


def test_vote_too_soon_names_the_next_midnight_with_its_offset(client: TestClient, service: InventedService) -> None:
    service.answer = apply_refusal(VoteTooSoonError(datetime(2026, 10, 5, 0, 0, tzinfo=WARSAW)))
    response = client.post("/api/facts/1042/votes", json={"verdict": "confirm"})
    assert response.status_code == 409
    assert response.json() == {"error": {"code": "vote_too_soon", "repeat_allowed_at": "2026-10-05T00:00:00.000+02:00"}}
    actor = service.calls[-1][1][2]
    assert isinstance(actor, AnonymousVoterInput)


@pytest.mark.parametrize("verdict", ["CONFIRM", "maybe", 1, None])
def test_vote_outside_its_closed_list_is_refused(client: TestClient, service: InventedService, verdict: object) -> None:
    response = client.post("/api/facts/1042/votes", json={"verdict": verdict})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": ["verdict"]}}
    assert fetch_service_calls(service) == []


def test_vote_on_a_hidden_fact_is_missing(client: TestClient, service: InventedService) -> None:
    service.answer = apply_refusal(FactNotFoundError())
    response = client.post("/api/facts/1042/votes", json={"verdict": "confirm"})
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "fact_not_found"}}


def test_flag_answers_204_without_a_body(client: TestClient, service: InventedService) -> None:
    response = client.post("/api/facts/1042/flag")
    assert response.status_code == 204
    assert response.content == b""
    assert service.calls[-1] == ("apply_fact_flag", (1042,))


@pytest.mark.parametrize(
    ("refusal", "status", "code"),
    [(FactNotFlaggableError(), 409, "fact_not_flaggable"), (FactNotFoundError(), 404, "fact_not_found")],
)
def test_flag_refusals_follow_the_contract(client: TestClient, service: InventedService, refusal: Exception, status: int, code: str) -> None:
    service.answer = apply_refusal(refusal)
    response = client.post("/api/facts/7/flag")
    assert response.status_code == status
    assert response.json() == {"error": {"code": code}}


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("POST", "/api/facts/in-area", AREA_REQUEST),
        ("GET", "/api/facts/1042", None),
        ("POST", "/api/facts/nearby", NEARBY_REQUEST),
        ("POST", "/api/facts", CREATE_REQUEST),
        ("POST", "/api/facts/1042/votes", {"verdict": "confirm"}),
        ("POST", "/api/facts/1042/flag", None),
    ],
)
def test_refused_token_is_never_handled_as_a_person_without_an_account(client: TestClient, service: InventedService, method: str, path: str, payload: object) -> None:
    service.resolution = apply_refusal(SessionExpiredError())
    response = client.request(method, path, json=payload, headers={"Authorization": "Bearer private-expired"})
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "session_expired"}}
    assert "Session-Token" not in response.headers
    assert fetch_service_calls(service) == []


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [("POST", "/api/facts/in-area", AREA_REQUEST), ("GET", "/api/facts/1042", None), ("POST", "/api/facts/nearby", NEARBY_REQUEST), ("POST", "/api/facts/1042/flag", None)],
)
def test_operation_with_a_valid_token_renews_it(client: TestClient, service: InventedService, method: str, path: str, payload: object) -> None:
    service.answer = lambda: AreaFacts(facts=(), is_truncated=False) if path.endswith("in-area") else (() if path.endswith("nearby") else REPORT_VIEW)
    response = client.request(method, path, json=payload, headers=VALID_HEADERS)
    assert response.status_code in (200, 204)
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


def test_person_without_an_account_gets_no_session_token(client: TestClient, service: InventedService) -> None:
    service.answer = lambda: REPORT_VIEW
    response = client.get("/api/facts/1042")
    assert response.status_code == 200
    assert "Session-Token" not in response.headers


def test_request_log_holds_no_identifying_input_or_content(client: TestClient, service: InventedService, capsys) -> None:
    service.answer = lambda: FactCreationResult(view=REPORT_VIEW, is_created=True)
    apply_logging_configuration()
    response = client.post("/api/facts", json=CREATE_REQUEST, headers=VALID_HEADERS)
    output = capsys.readouterr().out
    assert response.status_code == 201
    assert "operation=create_fact status=201" in output
    for fragment in (PERSON_ADDRESS, "private agent", KEY, "Trzy stopnie", "50.0661", SESSION_TOKEN, RENEWED_TOKEN, ACCOUNT.pseudonym):
        assert fragment not in output
