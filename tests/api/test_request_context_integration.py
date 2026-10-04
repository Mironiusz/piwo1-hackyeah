"""Verify correlation sanitization and header uniqueness."""

import pytest
from fastapi.testclient import TestClient
from starlette.responses import Response

from api.app import build_app

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("candidate", ["valid_id-123", "invalid id", "x" * 129, "", "żółć"])
def test_request_identifier_is_safe_and_unique(_runtime_settings, candidate: str) -> None:
    """Keep safe input or replace it with a generated ASCII identifier."""
    app = build_app()

    @app.get("/invented", name="invented_success")
    def apply_success() -> Response:
        """Supply a duplicate header to verify middleware ownership."""
        return Response(headers={"X-Request-Id": "endpoint-owned"})

    headers = {"X-Request-Id": candidate} if candidate.isascii() else {}
    with TestClient(app) as client:
        response = client.get("/invented", headers=headers)
    identifiers = response.headers.get_list("X-Request-Id")
    assert len(identifiers) == 1
    assert identifiers[0] == candidate if candidate == "valid_id-123" else identifiers[0] != candidate
