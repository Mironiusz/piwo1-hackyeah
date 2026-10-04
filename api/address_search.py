"""Accept search_address, refuse a request outside its contract and answer the matches of the search or a contracted refusal."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, field_validator

from api.errors import build_error_response
from service.address_search import AddressSearchUnavailableError, AddressSuggestion, InvalidSearchTextError, fetch_address_suggestions


class SearchAddressRequest(BaseModel):
    """The request of search_address: the search text alone, as a string UTF-8 can carry."""

    model_config = ConfigDict(extra="forbid", strict=True)
    text: str

    @field_validator("text")
    @classmethod
    def resolve_utf8_text(cls, value: str) -> str:
        """Refuse a text holding a lone surrogate, which cannot be sent on as UTF-8."""
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("text_not_utf8") from None
        return value


def build_address_search_response(suggestions: tuple[AddressSuggestion, ...]) -> dict[str, object]:
    """Build the response 200 of search_address: the matches in the order of the search, each with its label and point."""
    return {"matches": [{"label": item.label, "point": {"lat": item.lat, "lon": item.lon}} for item in suggestions]}


async def fetch_address_matches(body: SearchAddressRequest) -> JSONResponse:
    """Search an address without a token and without reading Authorization; a refused text and an unavailable search get their contracted errors."""
    try:
        suggestions = await fetch_address_suggestions(body.text)
    except InvalidSearchTextError:
        return build_error_response("invalid_search_text", 422)
    except AddressSearchUnavailableError:
        return build_error_response("address_search_unavailable", 503)
    return JSONResponse(build_address_search_response(suggestions))


def apply_address_search_routes(app: FastAPI) -> None:
    """Register search_address at POST /api/address-search."""
    app.add_api_route("/api/address-search", fetch_address_matches, methods=["POST"], name="search_address", response_model=None)
