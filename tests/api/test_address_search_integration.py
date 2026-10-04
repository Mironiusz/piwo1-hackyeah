"""Check the endpoint of search_address against its contract with the search replaced, without a network."""

import pytest
from fastapi.testclient import TestClient

from api import address_search
from api.app import build_app
from config.logging import apply_logging_configuration
from service.address_search import AddressSearchUnavailableError, AddressSuggestion, InvalidSearchTextError

pytestmark = pytest.mark.integration

ARENA = AddressSuggestion("Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków", 50.0677202, 19.9915490)


def apply_invented_search(monkeypatch: pytest.MonkeyPatch, outcome: tuple[AddressSuggestion, ...] | Exception) -> list[str]:
    """Replace the search of the rules layer with an invented outcome and record the texts it receives."""
    texts: list[str] = []

    async def fetch_suggestions(text: str) -> tuple[AddressSuggestion, ...]:
        """Record the text and give the invented answer or raise the invented failure."""
        texts.append(text)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(address_search, "fetch_address_suggestions", fetch_suggestions)
    return texts


@pytest.mark.parametrize(
    ("outcome", "body"),
    [
        ((ARENA,), {"matches": [{"label": ARENA.label, "point": {"lat": 50.0677202, "lon": 19.9915490}}]}),
        ((), {"matches": []}),
    ],
)
def test_matches_follow_the_contract(_runtime_settings, monkeypatch: pytest.MonkeyPatch, outcome, body) -> None:
    """A list and an empty list are answered with 200 in the shape of the contract."""
    texts = apply_invented_search(monkeypatch, outcome)
    response = TestClient(build_app()).post("/api/address-search", json={"text": "Tauron Arena"})
    assert (response.status_code, response.json()) == (200, body)
    assert texts == ["Tauron Arena"]


@pytest.mark.parametrize(
    ("failure", "status", "code"),
    [(InvalidSearchTextError("Search text is empty"), 422, "invalid_search_text"), (AddressSearchUnavailableError("Address search is unavailable"), 503, "address_search_unavailable")],
)
def test_refusals_follow_the_contract(_runtime_settings, monkeypatch: pytest.MonkeyPatch, failure: Exception, status: int, code: str) -> None:
    """A refused text and an unavailable search get exactly their contracted errors."""
    apply_invented_search(monkeypatch, failure)
    response = TestClient(build_app()).post("/api/address-search", json={"text": "Tauron Arena"})
    assert (response.status_code, response.json()) == (status, {"error": {"code": code}})


@pytest.mark.parametrize(
    ("content", "fields"),
    [
        (b"{}", ["text"]),
        (b'{"text": 5}', ["text"]),
        (b'{"text": null}', ["text"]),
        (b'{"text": "a", "x": 1}', ["x"]),
        (b'{"text": "\\ud800"}', ["text"]),
    ],
)
def test_body_outside_the_contract_is_an_invalid_request(_runtime_settings, monkeypatch: pytest.MonkeyPatch, content: bytes, fields: list[str]) -> None:
    """A missing text, a text that is not a string, an unknown field and a lone surrogate are refused with their fields before any search."""
    texts = apply_invented_search(monkeypatch, ())
    response = TestClient(build_app()).post("/api/address-search", content=content, headers={"Content-Type": "application/json"})
    assert (response.status_code, response.json()) == (422, {"error": {"code": "invalid_request", "fields": fields}})
    assert texts == []


def test_token_is_ignored_and_no_session_is_renewed(_runtime_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    """A request with a token gets the same answer as without it and no renewed token."""
    apply_invented_search(monkeypatch, (ARENA,))
    client = TestClient(build_app())
    without = client.post("/api/address-search", json={"text": "Tauron Arena"})
    with_token = client.post("/api/address-search", json={"text": "Tauron Arena"}, headers={"Authorization": "Bearer invented"})
    assert (with_token.status_code, with_token.json()) == (without.status_code, without.json())
    assert "Session-Token" not in with_token.headers


def test_other_method_is_not_found(_runtime_settings) -> None:
    """Only POST serves the search."""
    response = TestClient(build_app()).get("/api/address-search")
    assert (response.status_code, response.json()) == (404, {"error": {"code": "not_found"}})


def test_request_log_names_the_operation(_runtime_settings, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """The request log entry names search_address."""
    apply_invented_search(monkeypatch, ())
    app = build_app()
    apply_logging_configuration()
    TestClient(app).post("/api/address-search", json={"text": "Tauron Arena"})
    assert "operation=search_address status=200" in capsys.readouterr().out
