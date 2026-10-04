"""Translate framework failures into the existing safe error envelope."""

from collections.abc import Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from config.logging import apply_log_scope, fetch_logger


def build_error_response(code: str, status: int, fields: Sequence[str] = ()) -> JSONResponse:
    """Build a contracted failure without protected input or exception text."""
    error: dict[str, object] = {"code": code}
    if code == "invalid_request":
        error["fields"] = list(fields)
    return JSONResponse({"error": error}, status_code=status)


def apply_error_handlers(app: FastAPI) -> None:
    """Install adapters for validation, unmatched operations and uncaught errors."""

    async def apply_validation_error(request: Request, error: Exception) -> JSONResponse:
        """Return only schema field paths for invalid request input."""
        if not isinstance(error, RequestValidationError):
            return build_error_response("internal_error", 500)
        fields = [".".join(str(part) for part in item["loc"] if part not in ("body", "query", "path", "header")) for item in error.errors()]
        return build_error_response("invalid_request", 422, sorted(set(fields)))

    async def apply_http_error(request: Request, error: Exception) -> JSONResponse:
        """Normalize unknown methods and paths without framework details."""
        if not isinstance(error, HTTPException):
            return build_error_response("internal_error", 500)
        if error.status_code in (404, 405):
            return build_error_response("not_found", 404)
        return build_error_response("internal_error", 500)

    async def apply_uncaught_error(request: Request, error: Exception) -> JSONResponse:
        """Restore correlation for a redacted uncaught-error diagnostic."""
        identifier = request.scope["state"]["request_id"]
        with apply_log_scope(identifier):
            fetch_logger(__name__).error("Request failed", exc_info=(type(error), error, error.__traceback__))
        response = build_error_response("internal_error", 500)
        response.headers["X-Request-Id"] = identifier
        return response

    app.add_exception_handler(RequestValidationError, apply_validation_error)
    app.add_exception_handler(HTTPException, apply_http_error)
    app.add_exception_handler(Exception, apply_uncaught_error)
