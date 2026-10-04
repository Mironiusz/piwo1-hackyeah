"""Correlate every HTTP response and log only approved request fields."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from common_time import fetch_monotonic_seconds
from config.logging import apply_log_scope, build_request_id, fetch_logger


class RequestContextMiddleware:
    """Keep correlation separate from request bodies and URL log data."""

    def __init__(self, app: ASGIApp) -> None:
        """Retain the next ASGI application."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Attach one response identifier and one completed-request entry."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        candidates = [value.decode("latin-1") for key, value in scope["headers"] if key.lower() == b"x-request-id"]
        identifier = build_request_id(candidates[0] if len(candidates) == 1 else None)
        scope.setdefault("state", {})["request_id"] = identifier
        started = fetch_monotonic_seconds()
        status = 500

        async def apply_response(message: Message) -> None:
            """Replace duplicate correlation headers before sending the response."""
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                headers = [(key, value) for key, value in message.get("headers", ()) if key.lower() != b"x-request-id"]
                message["headers"] = [*headers, (b"x-request-id", identifier.encode("ascii"))]
            await send(message)

        with apply_log_scope(identifier):
            try:
                await self.app(scope, receive, apply_response)
            finally:
                route = scope.get("route")
                operation = getattr(route, "name", "unmatched")
                duration = max(0, (fetch_monotonic_seconds() - started) * 1000)
                fetch_logger(__name__).info("Request completed method=%s operation=%s status=%s duration_ms=%.3f", scope["method"], operation, status, duration)
