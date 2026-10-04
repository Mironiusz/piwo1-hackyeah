"""Build the API foundation without product data or schema side effects."""

from fastapi import FastAPI

from api.accounts import apply_account_routes
from api.address_search import apply_address_search_routes
from api.errors import apply_error_handlers
from api.request_context import RequestContextMiddleware
from api.route import apply_route_lifespan, apply_route_routes


def build_app() -> FastAPI:
    """Build an extendable application with the contracted failure foundation."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=apply_route_lifespan)
    apply_error_handlers(app)
    apply_address_search_routes(app)
    apply_route_routes(app)
    apply_account_routes(app)
    app.add_middleware(RequestContextMiddleware)
    return app
