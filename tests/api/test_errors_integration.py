"""Verify the exact safe response contract without a product database."""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from api.app import build_app
from config.logging import apply_logging_configuration

pytestmark = pytest.mark.integration


class Payload(BaseModel):
    """Represent one invented request field for validation verification."""

    count: int


def test_unknown_methods_and_paths_follow_contract(_runtime_settings) -> None:
    """Return not_found and one correlation header for unmatched operations."""
    app = build_app()
    apply_logging_configuration()
    with TestClient(app) as client:
        for method in ("GET", "POST", "DELETE"):
            response = client.request(method, "/invented?protected-search=private", headers={"X-Request-Id": "safe-id"})
            assert response.status_code == 404
            assert response.json() == {"error": {"code": "not_found"}}
            assert response.headers.get_list("X-Request-Id") == ["safe-id"]
        assert client.get("/openapi.json").status_code == 404


def test_uncaught_error_is_correlated_and_logs_no_protected_text(_runtime_settings, capsys) -> None:
    """Keep one safe response and diagnostic even above context middleware."""
    app = build_app()
    apply_logging_configuration()

    @app.get("/invented", name="invented_operation")
    def apply_failure() -> None:
        """Raise an invented failure with deliberately protected text."""
        raise ValueError("password=private-secret coordinates=50.1 token=private-token")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/invented", headers={"X-Request-Id": "failure-id"})
    assert response.status_code == 500
    assert response.json() == {"error": {"code": "internal_error"}}
    assert response.headers.get_list("X-Request-Id") == ["failure-id"]
    output = capsys.readouterr().out
    assert output.count("Request completed") == 1
    assert "request_id=failure-id" in output
    assert "Traceback" in output
    assert "private-secret" not in output
    assert "private-token" not in output
    assert "50.1" not in output


def test_validation_returns_paths_without_input(_runtime_settings) -> None:
    """Expose field paths without validation-library input dumps."""
    app = build_app()

    @app.post("/invented", name="invented_validation")
    def apply_payload(payload: Payload) -> dict[str, int]:
        """Return an invented validated value."""
        return {"count": payload.count}

    with TestClient(app) as client:
        response = client.post("/invented", json={"count": "private-secret"})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "fields": ["count"]}}
