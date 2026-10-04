"""
Integration tests of the four account operations and of the session header, through `build_app`, with the service replaced.

They check every status, body and error envelope of `docs/product/api_contract.md`, section Accounts, the header
`Session-Token` on success, on a handled refusal and on an operation without a token (AC-7 and AC-8 of
`plans_finished/accounts/ACCOUNTS_PRD.md`), and the request log without any personal or secret value (AC-13). No database and no
network is used; the client is built without the lifespan of the application, which loads the graph of the route.
"""

from collections.abc import Callable
from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

from api.app import build_app
from api.sessions import fetch_account_actor, fetch_moderator_actor
from config.logging import apply_logging_configuration
from service.account_rules import InvalidAccountInputError
from service.accounts import AccountView, InvalidCredentialsError, LoginResult, PseudonymTakenError
from service.actors import AccountActor, SessionExpiredError, SessionResolution

pytestmark = pytest.mark.integration

PSEUDONYM = "Wózek_KRK"
PASSWORD = "private-password"
SESSION_TOKEN = "private-login-token"
RENEWED_TOKEN = "private-renewed-token"
ACCOUNT_ID = 987654321
ORDINARY = AccountActor(account_id=ACCOUNT_ID, pseudonym=PSEUDONYM, is_moderator=False)
ACCOUNT_BODY = {"account": {"pseudonym": PSEUDONYM, "is_moderator": False}}
VALID_HEADERS = {"Authorization": f"Bearer {SESSION_TOKEN}"}


class InventedBody(BaseModel):
    """An invented request body of a test-only operation with an account."""

    count: int


class InventedService:
    """The account service and the actor resolution replaced by invented answers, recording what they were called with."""

    def __init__(self) -> None:
        """Answer an ordinary account by default and record nothing yet."""
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.creation: Callable[[], AccountView] = lambda: AccountView(pseudonym=PSEUDONYM, is_moderator=False)
        self.login: Callable[[], LoginResult] = lambda: LoginResult(account=AccountView(pseudonym=PSEUDONYM, is_moderator=False), session_token=SESSION_TOKEN)
        self.deletion: Callable[[], None] = lambda: None
        self.resolution: Callable[[], SessionResolution] = lambda: SessionResolution(actor=ORDINARY, renewed_token=RENEWED_TOKEN)

    def apply_account_creation(self, pseudonym: str, password: str, now: object) -> AccountView:
        """Record a registration and answer it."""
        self.calls.append(("apply_account_creation", (pseudonym, password)))
        return self.creation()

    def resolve_login(self, pseudonym: str, password: str, now: object) -> LoginResult:
        """Record a login and answer it."""
        self.calls.append(("resolve_login", (pseudonym, password)))
        return self.login()

    def apply_account_deletion(self, actor: AccountActor) -> None:
        """Record a deletion and answer it."""
        self.calls.append(("apply_account_deletion", (actor,)))
        self.deletion()

    def resolve_request_actor(self, authorization: str | None, now: object) -> SessionResolution:
        """Record a resolution and answer a person without an account for no header, or the invented resolution."""
        self.calls.append(("resolve_request_actor", (authorization,)))
        return SessionResolution(actor=None, renewed_token=None) if authorization is None else self.resolution()


def apply_refusal(error: Exception) -> Callable[[], object]:
    """Build an invented answer that raises a refusal of the service."""

    def raise_refusal() -> object:
        """Raise the refusal."""
        raise error

    return raise_refusal


@pytest.fixture
def service(_runtime_settings, monkeypatch: pytest.MonkeyPatch) -> InventedService:
    """Replace every call of the API layer into the service with the invented service."""
    invented = InventedService()
    monkeypatch.setattr("api.accounts.apply_account_creation", invented.apply_account_creation)
    monkeypatch.setattr("api.accounts.resolve_login", invented.resolve_login)
    monkeypatch.setattr("api.accounts.apply_account_deletion", invented.apply_account_deletion)
    monkeypatch.setattr("api.sessions.resolve_request_actor", invented.resolve_request_actor)
    return invented


@pytest.fixture
def client(service: InventedService) -> TestClient:
    """A client of the whole application with two test-only operations, one with an account and one moderator one."""
    app = build_app()

    @app.post("/invented/account", name="invented_account")
    def apply_invented_account(body: InventedBody, actor: Annotated[AccountActor, Depends(fetch_account_actor)]) -> dict[str, int]:
        """Answer an invented operation that needs an account and a body."""
        return {"count": body.count}

    @app.get("/invented/moderator", name="invented_moderator")
    def apply_invented_moderator(actor: Annotated[AccountActor, Depends(fetch_moderator_actor)]) -> dict[str, bool]:
        """Answer an invented moderator operation."""
        return {"moderator": actor.is_moderator}

    @app.get("/invented/open", name="invented_open")
    def apply_invented_open() -> dict[str, bool]:
        """Answer an invented operation that takes no token."""
        return {"open": True}

    return TestClient(app, raise_server_exceptions=False)


def test_create_account_answers_201_without_a_session(client: TestClient, service: InventedService) -> None:
    """Register without logging in, passing the input to the service unchanged and ignoring a sent token."""
    response = client.post("/api/accounts", json={"pseudonym": f"  {PSEUDONYM}  ", "password": PASSWORD}, headers=VALID_HEADERS)
    assert response.status_code == 201
    assert response.json() == ACCOUNT_BODY
    assert "Session-Token" not in response.headers
    assert service.calls == [("apply_account_creation", (f"  {PSEUDONYM}  ", PASSWORD))]


@pytest.mark.parametrize(
    ("refusal", "status", "body"),
    [
        (InvalidAccountInputError("pseudonym"), 422, {"error": {"code": "invalid_request", "fields": ["pseudonym"]}}),
        (InvalidAccountInputError("password"), 422, {"error": {"code": "invalid_request", "fields": ["password"]}}),
        (PseudonymTakenError(), 409, {"error": {"code": "pseudonym_taken"}}),
    ],
    ids=["pseudonym-outside-rules", "password-outside-rules", "pseudonym-taken"],
)
def test_create_account_refusals_follow_the_contract(client: TestClient, service: InventedService, refusal: Exception, status: int, body: dict[str, object]) -> None:
    """Answer each refusal of a registration with its status and envelope."""
    service.creation = apply_refusal(refusal)
    response = client.post("/api/accounts", json={"pseudonym": PSEUDONYM, "password": PASSWORD})
    assert response.status_code == status
    assert response.json() == body


@pytest.mark.parametrize("path", ["/api/accounts", "/api/sessions"])
@pytest.mark.parametrize(
    ("payload", "fields"),
    [
        ({"pseudonym": PSEUDONYM, "password": PASSWORD, "email": "x"}, ["email"]),
        ({"pseudonym": 12345, "password": PASSWORD}, ["pseudonym"]),
        ({"pseudonym": PSEUDONYM}, ["password"]),
    ],
    ids=["unknown-field", "number-as-pseudonym", "missing-password"],
)
def test_request_outside_its_shape_is_refused_before_the_service(client: TestClient, service: InventedService, path: str, payload: dict[str, object], fields: list[str]) -> None:
    """Refuse an unknown field, a value of a wrong type and a missing field with invalid_request and their paths."""
    response = client.post(path, json=payload)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": fields}}
    assert service.calls == []


def test_log_in_gives_the_token_in_session_token(client: TestClient, service: InventedService) -> None:
    """Answer 200 with the account and the token of the new session, ignoring a sent token."""
    response = client.post("/api/sessions", json={"pseudonym": "wózek_krk", "password": PASSWORD}, headers={"Authorization": "Bearer stale"})
    assert response.status_code == 200
    assert response.json() == ACCOUNT_BODY
    assert response.headers.get_list("Session-Token") == [SESSION_TOKEN]
    assert service.calls == [("resolve_login", ("wózek_krk", PASSWORD))]


def test_failed_log_in_answers_invalid_credentials_without_a_token(client: TestClient, service: InventedService) -> None:
    """Answer 401 invalid_credentials and no token."""
    service.login = apply_refusal(InvalidCredentialsError())
    response = client.post("/api/sessions", json={"pseudonym": PSEUDONYM, "password": PASSWORD})
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "invalid_credentials"}}
    assert "Session-Token" not in response.headers


def test_read_own_account_answers_the_account_with_a_renewed_token(client: TestClient, service: InventedService) -> None:
    """Answer the pseudonym and the role of the session with the renewed token."""
    response = client.get("/api/accounts/me", headers=VALID_HEADERS)
    assert response.status_code == 200
    assert response.json() == ACCOUNT_BODY
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]
    assert service.calls == [("resolve_request_actor", (VALID_HEADERS["Authorization"],))]


@pytest.mark.parametrize(("method", "path"), [("GET", "/api/accounts/me"), ("DELETE", "/api/accounts/me")])
def test_operation_with_an_account_refuses_a_request_without_a_token(client: TestClient, service: InventedService, method: str, path: str) -> None:
    """Answer 401 authentication_required without a token and without deleting anything."""
    response = client.request(method, path)
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "authentication_required"}}
    assert "Session-Token" not in response.headers
    assert ("apply_account_deletion", (ORDINARY,)) not in service.calls


@pytest.mark.parametrize(("method", "path"), [("GET", "/api/accounts/me"), ("DELETE", "/api/accounts/me")])
def test_expired_session_is_refused_without_a_token(client: TestClient, service: InventedService, method: str, path: str) -> None:
    """Answer 401 session_expired for a token the resolution refuses, never as a person without an account."""
    service.resolution = apply_refusal(SessionExpiredError())
    response = client.request(method, path, headers=VALID_HEADERS)
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "session_expired"}}
    assert "Session-Token" not in response.headers


def test_repeated_authorization_header_is_an_expired_session(client: TestClient, service: InventedService) -> None:
    """Refuse two headers `Authorization` as a malformed session, without resolving either."""
    response = client.get("/api/accounts/me", headers=[("Authorization", "Bearer one"), ("Authorization", "Bearer two")])
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "session_expired"}}
    assert service.calls == []


def test_delete_own_account_answers_204_without_a_body_or_a_token(client: TestClient, service: InventedService) -> None:
    """Delete the account of the session and answer with nothing, not even the renewed token."""
    response = client.delete("/api/accounts/me", headers=VALID_HEADERS)
    assert response.status_code == 204
    assert response.content == b""
    assert "Session-Token" not in response.headers
    assert ("apply_account_deletion", (ORDINARY,)) in service.calls


def test_deletion_of_an_account_deleted_first_answers_session_expired_without_a_token(client: TestClient, service: InventedService) -> None:
    """Clear the renewed token when the account was deleted by another request between the resolution and the deletion."""
    service.deletion = apply_refusal(SessionExpiredError())
    response = client.delete("/api/accounts/me", headers=VALID_HEADERS)
    assert response.status_code == 401
    assert response.json() == {"error": {"code": "session_expired"}}
    assert "Session-Token" not in response.headers


def test_moderator_refusal_carries_the_renewed_token(client: TestClient) -> None:
    """Answer 403 moderator_role_required to an ordinary account, with its renewed token."""
    response = client.get("/invented/moderator", headers=VALID_HEADERS)
    assert response.status_code == 403
    assert response.json() == {"error": {"code": "moderator_role_required"}}
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


def test_moderator_operation_admits_a_moderator(client: TestClient, service: InventedService) -> None:
    """Admit an account that holds the moderator role now."""
    service.resolution = lambda: SessionResolution(actor=AccountActor(account_id=1, pseudonym="Moderator_1", is_moderator=True), renewed_token=RENEWED_TOKEN)
    response = client.get("/invented/moderator", headers=VALID_HEADERS)
    assert response.status_code == 200
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


def test_invalid_body_with_a_valid_token_carries_the_renewed_token(client: TestClient) -> None:
    """Keep the session of a request whose body is refused with invalid_request."""
    response = client.post("/invented/account", json={"count": "many"}, headers=VALID_HEADERS)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": ["count"]}}
    assert response.headers.get_list("Session-Token") == [RENEWED_TOKEN]


def test_operation_without_a_token_ignores_the_header_and_renews_nothing(client: TestClient, service: InventedService) -> None:
    """Answer an operation that takes no token without resolving the header and without `Session-Token`."""
    response = client.get("/invented/open", headers=VALID_HEADERS)
    assert response.status_code == 200
    assert "Session-Token" not in response.headers
    assert service.calls == []


def test_request_log_holds_no_personal_or_secret_value(client: TestClient, capsys: pytest.CaptureFixture[str]) -> None:
    """Log only the operation, the status, the duration and the request identifier of every account operation."""
    apply_logging_configuration()
    correlation = {"X-Request-Id": "log-check"}
    client.post("/api/accounts", json={"pseudonym": PSEUDONYM, "password": PASSWORD}, headers=correlation)
    client.post("/api/sessions", json={"pseudonym": PSEUDONYM, "password": PASSWORD}, headers=correlation)
    client.get("/api/accounts/me", headers={**VALID_HEADERS, **correlation})
    client.delete("/api/accounts/me", headers={**VALID_HEADERS, **correlation})
    output = capsys.readouterr().out
    for operation in ("create_account", "log_in", "read_own_account", "delete_own_account"):
        assert f"operation={operation} " in output
    for value in (PSEUDONYM, PASSWORD, SESSION_TOKEN, RENEWED_TOKEN, str(ACCOUNT_ID), "Bearer"):
        assert value not in output
