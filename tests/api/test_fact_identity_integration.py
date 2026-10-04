"""
Integration tests of the two inputs of the identity of a person without an account at the boundary of the programming interface.

The address goes through the proxy handling of uvicorn itself, built from the validated setting `API_TRUSTED_PROXY_ADDRESSES`,
so an untrusted peer keeps its own address whatever X-Forwarded-For it sends and only a trusted proxy hands on the rightmost
untrusted entry; the entry point passes that list to uvicorn explicitly. A missing, empty and repeated User-Agent follows
`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-17, and the request log carries neither input (D-11, D-16, S-2).
"""

import sys
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from api import __main__ as entry_point
from api.app import build_app
from api.fact_identity import fetch_anonymous_voter_input
from config.logging import apply_logging_configuration
from config.settings import Settings
from service.anonymous_voters import AnonymousVoterInput
from tests.common_runtime_settings import INVENTED_RUNTIME_SETTINGS, apply_invented_runtime_settings

pytestmark = pytest.mark.integration

PROXY = "172.18.0.5"
PERSON = "203.0.113.7"
USER_AGENT = "Mozilla/5.0 (invented private agent)"


def build_identity_app() -> FastAPI:
    """Build the whole application with a test-only operation that answers the inputs it read."""
    app = build_app()

    @app.get("/invented/identity", name="invented_identity")
    def read_invented_identity(voter: Annotated[AnonymousVoterInput, Depends(fetch_anonymous_voter_input)]) -> dict[str, str]:
        """Answer the address and the User-Agent of the request."""
        return {"address": voter.address.compressed, "user_agent": voter.user_agent}

    return app


def build_client(peer: str, trusted: str) -> TestClient:
    """Build a client whose connection comes from `peer`, behind the proxy handling of uvicorn trusting the validated entry `trusted`."""
    settings = Settings(**{**INVENTED_RUNTIME_SETTINGS, "API_TRUSTED_PROXY_ADDRESSES": trusted})
    app = ProxyHeadersMiddleware(build_identity_app(), trusted_hosts=list(settings.API_TRUSTED_PROXY_ADDRESSES))
    return TestClient(app, client=(peer, 50000), raise_server_exceptions=False)


@pytest.mark.parametrize("trusted", ["", "10.0.0.0/8"])
def test_untrusted_peer_keeps_its_own_address_whatever_it_forwards(_runtime_settings, trusted: str) -> None:
    response = build_client(PERSON, trusted).get("/invented/identity", headers={"X-Forwarded-For": "198.51.100.1, 198.51.100.2", "User-Agent": USER_AGENT})
    assert response.json()["address"] == PERSON


@pytest.mark.parametrize("trusted", [PROXY, "172.18.0.0/16"])
def test_trusted_proxy_hands_on_the_rightmost_untrusted_entry(_runtime_settings, trusted: str) -> None:
    response = build_client(PROXY, trusted).get("/invented/identity", headers={"X-Forwarded-For": f"198.51.100.1, {PERSON}", "User-Agent": USER_AGENT})
    assert response.json()["address"] == PERSON


def test_trusted_proxy_without_a_forwarded_header_is_the_peer_itself(_runtime_settings) -> None:
    assert build_client(PROXY, PROXY).get("/invented/identity").json()["address"] == PROXY


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ([], ""),
        ([("User-Agent", "")], ""),
        ([("User-Agent", USER_AGENT)], USER_AGENT),
        ([("User-Agent", "first"), ("User-Agent", "second")], "first, second"),
    ],
    ids=["missing", "empty", "one", "repeated"],
)
def test_user_agent_is_the_text_of_its_headers(_runtime_settings, headers: list[tuple[str, str]], expected: str) -> None:
    client = build_client(PERSON, "")
    client.headers.pop("user-agent")
    response = client.get("/invented/identity", headers=headers)
    assert response.json()["user_agent"] == expected


def test_peer_that_is_not_an_ip_address_ends_in_internal_error(_runtime_settings) -> None:
    response = TestClient(build_identity_app(), raise_server_exceptions=False).get("/invented/identity")
    assert response.status_code == 500
    assert response.json() == {"error": {"code": "internal_error"}}


def test_request_log_holds_neither_input(_runtime_settings, capsys) -> None:
    client = build_client(PROXY, PROXY)
    apply_logging_configuration()
    response = client.get("/invented/identity", headers={"X-Forwarded-For": PERSON, "User-Agent": USER_AGENT})
    output = capsys.readouterr().out
    assert response.status_code == 200
    assert "operation=invented_identity status=200" in output
    assert PERSON not in output and PROXY not in output and "private agent" not in output


def test_entry_point_passes_the_trusted_proxy_to_uvicorn_explicitly(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(entry_point.uvicorn, "run", lambda *arguments, **options: calls.append(options))
    with apply_invented_runtime_settings(monkeypatch):
        monkeypatch.setenv("API_TRUSTED_PROXY_ADDRESSES", f"{PROXY}, 10.0.0.0/8")
        sys.modules.pop("config.config")
        entry_point.main()
    assert calls[0]["proxy_headers"] is True
    assert calls[0]["forwarded_allow_ips"] == [PROXY, "10.0.0.0/8"]
