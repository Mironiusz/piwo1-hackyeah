"""Build the API foundation without product data or schema side effects."""

from fastapi import FastAPI

from api.errors import apply_error_handlers
from api.request_context import RequestContextMiddleware


def build_app() -> FastAPI:
    """Build an extendable application with the contracted failure foundation."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    apply_error_handlers(app)
    app.add_middleware(RequestContextMiddleware)
    return app
