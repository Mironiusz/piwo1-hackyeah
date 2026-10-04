"""Call the public Nominatim instance, the one place of the code that does, and read its answer into plain places."""

import asyncio
import json
import math
from dataclasses import dataclass

import httpx

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT = "piwo1-hackyeah (HackYeah 2026 accessibility prototype)"
NOMINATIM_SEARCH_PARAMETERS = {
    "format": "jsonv2",
    "addressdetails": "1",
    "limit": "10",
    "countrycodes": "pl",
    "viewbox": "19.7922355,50.1261338,20.2173455,49.9676668",
    "bounded": "1",
    "accept-language": "pl",
}
NOMINATIM_TIMEOUT_SECONDS = 5.0


class NominatimRequestError(RuntimeError):
    """A search the public instance did not answer usably; it names the cause and, for a refusal, the status, never the text or the address of the request."""

    def __init__(self, cause: str, status: int | None = None) -> None:
        """Keep the cause, one of timeout, connection, status and invalid_body, and the status, and build the message of them alone."""
        super().__init__(f"Nominatim request failed cause={cause} status={status}")
        self.cause = cause
        self.status = status


@dataclass(frozen=True)
class NominatimPlace:
    """The parts of one result the label and the filter of Kraków need, each text absent when the result has no usable value for it."""

    name: str | None
    road: str | None
    house_number: str | None
    neighbourhood: str | None
    quarter: str | None
    suburb: str | None
    city_district: str | None
    postcode: str | None
    city: str | None
    lat: float
    lon: float


def build_nominatim_client(transport: httpx.AsyncBaseTransport | None = None) -> httpx.AsyncClient:
    """Build a fresh client for one search, carrying only the User-Agent the terms of the service require, without proxies from the environment and without redirects."""
    return httpx.AsyncClient(transport=transport, headers={"User-Agent": NOMINATIM_USER_AGENT}, timeout=NOMINATIM_TIMEOUT_SECONDS, trust_env=False, follow_redirects=False)


def _build_place_text(value: object) -> str | None:
    """Keep a text value of a result, or give None for a value that is not a string or is blank."""
    return value if isinstance(value, str) and value.strip() else None


def _build_place_coordinate(value: object) -> float:
    """Read a coordinate the service sends as a string, refusing anything that is not a finite number."""
    if not isinstance(value, str):
        raise NominatimRequestError("invalid_body")
    try:
        coordinate = float(value)
    except ValueError as error:
        raise NominatimRequestError("invalid_body") from error
    if not math.isfinite(coordinate):
        raise NominatimRequestError("invalid_body")
    return coordinate


def _build_nominatim_place(item: object) -> NominatimPlace:
    """Read one result, refusing one that is not an object or has no address object."""
    if not isinstance(item, dict):
        raise NominatimRequestError("invalid_body")
    address = item.get("address")
    if not isinstance(address, dict):
        raise NominatimRequestError("invalid_body")
    return NominatimPlace(
        name=_build_place_text(item.get("name")),
        road=_build_place_text(address.get("road")),
        house_number=_build_place_text(address.get("house_number")),
        neighbourhood=_build_place_text(address.get("neighbourhood")),
        quarter=_build_place_text(address.get("quarter")),
        suburb=_build_place_text(address.get("suburb")),
        city_district=_build_place_text(address.get("city_district")),
        postcode=_build_place_text(address.get("postcode")),
        city=_build_place_text(address.get("city")),
        lat=_build_place_coordinate(item.get("lat")),
        lon=_build_place_coordinate(item.get("lon")),
    )


def build_nominatim_places(body: bytes) -> list[NominatimPlace]:
    """Read the body of a search into places in the order of the service, refusing a body that is not the expected JSON list of results."""
    try:
        results = json.loads(body)
    except ValueError as error:
        raise NominatimRequestError("invalid_body") from error
    if not isinstance(results, list):
        raise NominatimRequestError("invalid_body")
    return [_build_nominatim_place(item) for item in results]


async def fetch_nominatim_places(text: str) -> list[NominatimPlace]:
    """Send one search to the public instance without retry, the whole call bounded by NOMINATIM_TIMEOUT_SECONDS, and read its places."""
    try:
        async with asyncio.timeout(NOMINATIM_TIMEOUT_SECONDS), build_nominatim_client() as client:
            response = await client.get(NOMINATIM_SEARCH_URL, params={"q": text, **NOMINATIM_SEARCH_PARAMETERS})
    except (TimeoutError, httpx.TimeoutException) as error:
        raise NominatimRequestError("timeout") from error
    except httpx.HTTPError as error:
        raise NominatimRequestError("connection") from error
    if response.status_code != 200:
        raise NominatimRequestError("status", response.status_code)
    return build_nominatim_places(response.content)
