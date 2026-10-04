"""
Integration tests of the three moderator operations through `build_app`, with the service and the session resolution replaced.

They check the matrix of every role of the contract for the list and for each change - a person without an account, an
ordinary account, a moderator, a moderator whose role was removed before the next request and a refused token - on both
sides, the exact moderator item without anything about who flagged, the refusals `fact_not_flagged` and `fact_not_found`, and
the renewed token (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` S-6; AC-11 and AC-13 of `COMMUNITY_FACTS_API_PRD.md`).
"""

from collections.abc import Callable
from datetime import date

import pytest
from accessibility_db.closed_lists import FactSource, FactType
from fastapi.testclient import TestClient

from api.app import build_app
from data.community_facts import StoredCommunityFact
from service.actors import AccountActor, SessionExpiredError, SessionResolution
from service.community_facts import FactNotFlaggedError, FactNotFoundError, FlaggedFactView
from service.fact_status import FactStatus, FactStatusResult, FactView

pytestmark = pytest.mark.integration

RENEWED_TOKEN = "private-renewed-token"
VALID_HEADERS = {"Authorization": "Bearer private-session-token"}
MODERATOR = AccountActor(account_id=11, pseudonym="Moderator_KRK", is_moderator=True)
ORDINARY = AccountActor(account_id=12, pseudonym="Wózek_KRK", is_moderator=False)
GEOZONE = StoredCommunityFact(
    id=2001,
    fact_type=FactType.POOR_SURFACE,
    source=FactSource.USER_REPORT,
    lat=50.0661,
    lon=19.9878,
    geozone_radius_m=25,
    description="Kocie łby",
    step_count=None,
    is_sample=False,
    osm_element_type=None,
    osm_element_id=None,
    osm_edited_on=None,
    is_removed_from_osm=False,
    flagged_at=None,
    is_hidden=True,
)
ITEM = FlaggedFactView(view=FactView(GEOZONE, FactStatusResult(FactStatus.CONFIRMED, 2.0, 0.0, date(2026, 10, 2))), flagged_on=date(2026, 10, 3), is_hidden=True)
ITEM_BODY = {
    "fact": {
        "id": 2001,
        "type": "poor_surface",
        "point": {"lat": 50.0661, "lon": 19.9878},
        "geozone_radius_m": 25,
        "description": "Kocie łby",
        "step_count": None,
        "source": "user_report",
        "status": "confirmed",
        "is_removed_from_osm": False,
        "osm_edited_on": None,
        "last_confirmed_on": "2026-10-02",
        "is_sample": False,
        "can_be_flagged": True,
    },
    "flagged_on": "2026-10-03",
    "is_hidden": True,
}
OPERATIONS = [
    ("GET", "/api/moderation/flagged-facts"),
    ("POST", "/api/moderation/flagged-facts/2001/hide"),
    ("POST", "/api/moderation/flagged-facts/2001/restore"),
]


class InventedService:
    """The moderation service and the session resolution replaced by invented answers, recording what they were called with."""

    def __init__(self) -> None:
        """Answer a moderator for a token and the invented item, and record nothing yet."""
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.answer: Callable[[], object] = lambda: ITEM
        self.resolution: Callable[[], SessionResolution] = lambda: SessionResolution(actor=MODERATOR, renewed_token=RENEWED_TOKEN)

    def resolve_request_actor(self, authorization: str | None, now: object) -> SessionResolution:
        """Record a resolution and answer a person without an account for no header, or the invented resolution."""
        self.calls.append(("resolve_request_actor", (authorization,)))
        return SessionResolution(actor=None, renewed_token=None) if authorization is None else self.resolution()

    def fetch_flagged_facts(self) -> object:
        """Record a read of the moderator list and answer it."""
        self.calls.append(("fetch_flagged_facts", ()))
        return (self.answer(),)

    def apply_fact_hiding(self, fact_id: int, now: object) -> object:
        """Record a hiding and answer it."""
        self.calls.append(("apply_fact_hiding", (fact_id,)))
        return self.answer()

    def apply_fact_restoration(self, fact_id: int) -> object:
        """Record a restoration and answer it."""
        self.calls.append(("apply_fact_restoration", (fact_id,)))
        return self.answer()


def apply_refusal(error: Exception) -> Callable[[], object]:
    """Build an invented answer that raises a refusal of the service."""

    def raise_refusal() -> object:
        """Raise the refusal."""
        raise error

    return raise_refusal


@pytest.fixture
def service(_runtime_settings, monkeypatch: pytest.MonkeyPatch) -> InventedService:
    """Replace every call of the moderator operations into the service and the session resolution with the invented service."""
    invented = InventedService()
    for name in ("fetch_flagged_facts", "apply_fact_hiding", "apply_fact_restoration"):
        monkeypatch.setattr(f"api.moderation.{name}", getattr(invented, name))
    monkeypatch.setattr("api.sessions.resolve_request_actor", invented.resolve_request_actor)
    return invented


@pytest.fixture
def client(service: InventedService) -> TestClient:
    """A client of the whole application."""
    return TestClient(build_app(), raise_server_exceptions=False)


def fetch_service_calls(service: InventedService) -> list[str]:
    """Give the names of the service calls other than the session resolution."""
    return [name for name, _arguments in service.calls if name != "resolve_request_actor"]


def test_moderator_reads_every_flagged_fact_with_a_renewed_token(client: TestClient, service: InventedService) -> None:
    response = client.get("/api/moderation/flagged-facts", headers=VALID_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"facts": [ITEM_BODY]}
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


@pytest.mark.parametrize(("path", "call"), [("/api/moderation/flagged-facts/2001/hide", "apply_fact_hiding"), ("/api/moderation/flagged-facts/2001/restore", "apply_fact_restoration")])
def test_moderator_change_answers_the_moderator_item(client: TestClient, service: InventedService, path: str, call: str) -> None:
    response = client.post(path, headers=VALID_HEADERS)
    assert response.status_code == 200
    assert response.json() == ITEM_BODY
    assert service.calls[-1] == (call, (2001,))
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


@pytest.mark.parametrize(("method", "path"), OPERATIONS)
@pytest.mark.parametrize(
    ("headers", "resolution", "status", "code", "is_renewed"),
    [
        ({}, None, 401, "authentication_required", False),
        (VALID_HEADERS, SessionResolution(actor=ORDINARY, renewed_token=RENEWED_TOKEN), 403, "moderator_role_required", True),
        (VALID_HEADERS, SessionResolution(actor=AccountActor(11, "Moderator_KRK", is_moderator=False), renewed_token=RENEWED_TOKEN), 403, "moderator_role_required", True),
        (VALID_HEADERS, SessionExpiredError(), 401, "session_expired", False),
    ],
    ids=["without-account", "ordinary-account", "role-removed", "refused-token"],
)
def test_nobody_but_a_current_moderator_can_moderate(
    client: TestClient,
    service: InventedService,
    method: str,
    path: str,
    headers: dict[str, str],
    resolution: object,
    status: int,
    code: str,
    is_renewed: bool,
) -> None:
    if isinstance(resolution, Exception):
        service.resolution = apply_refusal(resolution)
    elif isinstance(resolution, SessionResolution):
        service.resolution = lambda: resolution
    response = client.request(method, path, headers=headers)
    assert response.status_code == status
    assert response.json() == {"error": {"code": code}}
    assert response.headers.get_list("Session-Token") == ([RENEWED_TOKEN] if is_renewed else [])
    assert fetch_service_calls(service) == []


@pytest.mark.parametrize(("method", "path"), OPERATIONS[1:])
@pytest.mark.parametrize(
    ("refusal", "status", "code"),
    [(FactNotFlaggedError(), 409, "fact_not_flagged"), (FactNotFoundError(), 404, "fact_not_found")],
)
def test_moderator_change_refusals_follow_the_contract(client: TestClient, service: InventedService, method: str, path: str, refusal: Exception, status: int, code: str) -> None:
    service.answer = apply_refusal(refusal)
    response = client.request(method, path, headers=VALID_HEADERS)
    assert response.status_code == status
    assert response.json() == {"error": {"code": code}}
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


@pytest.mark.parametrize("path", ["/api/moderation/flagged-facts/x/hide", "/api/moderation/flagged-facts/9223372036854775808/restore"])
def test_moderator_change_of_an_identifier_that_is_not_a_stored_integer_is_refused(client: TestClient, service: InventedService, path: str) -> None:
    response = client.post(path, headers=VALID_HEADERS)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": ["id"]}}
    assert fetch_service_calls(service) == []
