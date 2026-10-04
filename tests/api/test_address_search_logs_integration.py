"""Check that no outcome of a search writes its text, the request sent out, the answer or a point to the log, at the most detailed level."""

import asyncio
import functools

import httpx
import pytest
from fastapi.testclient import TestClient

from api.app import build_app
from common_time import fetch_monotonic_seconds
from config.logging import apply_logging_configuration
from data import nominatim
from service import address_search
from service.address_search import SearchCache, SearchGate
from tests.common_nominatim_answers import RECORDED_ANSWERS

pytestmark = pytest.mark.integration

SEARCHED_TEXT = "ul. Szpital Uniwersytecki"
PROTECTED_FRAGMENTS = ("Szpital", "szpital uniwersytecki", "q=", "nominatim.openstreetmap.org/search", "Tauron Arena Kraków", "50.0677202")


def build_recorded_answer(request: httpx.Request) -> httpx.Response:
    """Answer with the recorded places of Tauron Arena."""
    return httpx.Response(200, json=RECORDED_ANSWERS["Tauron Arena"])


def build_empty_answer(request: httpx.Request) -> httpx.Response:
    """Answer that nothing was found."""
    return httpx.Response(200, json=[])


def build_limited_answer(request: httpx.Request) -> httpx.Response:
    """Refuse for an exceeded limit."""
    return httpx.Response(429, json=[])


def apply_connection_refusal(request: httpx.Request) -> httpx.Response:
    """Refuse the connection."""
    raise httpx.ConnectError("Connection refused", request=request)


async def build_late_answer(request: httpx.Request) -> httpx.Response:
    """Answer after the limit of the whole call."""
    await asyncio.sleep(1)
    return httpx.Response(200, json=[])


def build_html_answer(request: httpx.Request) -> httpx.Response:
    """Answer with a page instead of JSON."""
    return httpx.Response(200, content=b"<html>")


def apply_unexpected_failure(request: httpx.Request) -> httpx.Response:
    """Fail unexpectedly with the searched words in the message."""
    raise RuntimeError("Szpital Uniwersytecki")


@pytest.mark.parametrize(
    ("answer", "text", "is_gate_closed", "status"),
    [
        (build_recorded_answer, SEARCHED_TEXT, False, 200),
        (build_empty_answer, SEARCHED_TEXT, False, 200),
        (build_limited_answer, SEARCHED_TEXT, False, 503),
        (apply_connection_refusal, SEARCHED_TEXT, False, 503),
        (build_late_answer, SEARCHED_TEXT, False, 503),
        (build_html_answer, SEARCHED_TEXT, False, 503),
        (build_empty_answer, SEARCHED_TEXT, True, 503),
        (build_empty_answer, (SEARCHED_TEXT + " ") * 8, False, 422),
        (apply_unexpected_failure, SEARCHED_TEXT, False, 500),
    ],
)
def test_no_outcome_logs_protected_search_data(_runtime_settings, monkeypatch: pytest.MonkeyPatch, capsys, answer, text: str, is_gate_closed: bool, status: int) -> None:
    """Every outcome, an unexpected failure included, leaves only the request line and the cause in the log, never the text, the request sent out, the answer or a point."""
    gate = SearchGate()
    if is_gate_closed:
        gate.next_start_at = fetch_monotonic_seconds() + 100.0
    monkeypatch.setattr(address_search, "SEARCH_CACHE", SearchCache())
    monkeypatch.setattr(address_search, "SEARCH_GATE", gate)
    monkeypatch.setattr(nominatim, "NOMINATIM_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(nominatim, "build_nominatim_client", functools.partial(nominatim.build_nominatim_client, httpx.MockTransport(answer)))
    app = build_app()
    apply_logging_configuration()
    response = TestClient(app, raise_server_exceptions=False).post("/api/address-search", json={"text": text})
    output = capsys.readouterr().out
    assert response.status_code == status
    assert f"operation=search_address status={status}" in output
    for fragment in PROTECTED_FRAGMENTS:
        assert fragment not in output
