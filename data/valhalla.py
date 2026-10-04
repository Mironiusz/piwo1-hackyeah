"""Call the routing service of the project, the one place of the code that does, and read its answers into plain values."""

import functools
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

VALHALLA_CALL_TIMEOUT_SECONDS = 2.0
VALHALLA_NO_ROUTE_ERROR_CODE = 442
VALHALLA_TRACE_ERROR_CODE = 443


class RoutingServiceError(RuntimeError):
    """A call to the routing service that gave no usable answer."""


class RoutingServiceNoRouteError(RoutingServiceError):
    """The routing service found no path for the request, error 442."""


class RoutingServiceTraceError(RoutingServiceError):
    """The routing service could not match the shape of a route to its edges, error 443."""


class RoutingServiceUnavailableError(RoutingServiceError):
    """The routing service did not answer, answered too late, failed or answered a body that cannot be read."""


@dataclass(frozen=True)
class ValhallaRoute:
    """The encoded shape of precision 6 and the length in kilometres of the first leg of a route."""

    shape: str
    length_km: float


@dataclass(frozen=True)
class ValhallaEdge:
    """One edge of a traced route: its way, the OpenStreetMap nodes it begins and ends at, and its part of the traced shape."""

    way_id: int
    begin_node_id: int
    end_node_id: int
    begin_shape_index: int
    end_shape_index: int


@dataclass(frozen=True)
class ValhallaTrace:
    """The traced shape of precision 6 and its edges in order."""

    shape: str
    edges: tuple[ValhallaEdge, ...]


@functools.cache
def build_valhalla_client() -> httpx.Client:
    """Build the one client of the routing service, bound to its configured address, without proxies from the environment and without redirects."""
    from config.config import ROUTING_SERVICE_URL

    return httpx.Client(base_url=ROUTING_SERVICE_URL, timeout=VALHALLA_CALL_TIMEOUT_SECONDS, trust_env=False, follow_redirects=False)


def fetch_valhalla_answer(method: str, path: str, body: Mapping[str, object] | None) -> dict[str, Any]:
    """
    Send one call and give its JSON object, raising the error of its error code or RoutingServiceUnavailableError for any other failure.

    The client is built before the call, so a failure of the configuration surfaces as itself and is never taken for an
    unavailable routing service.
    """
    client = build_valhalla_client()
    try:
        response = client.request(method, path, json=body)
        payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise RoutingServiceUnavailableError("The routing service gave no readable answer") from error
    if not isinstance(payload, dict):
        raise RoutingServiceUnavailableError("The routing service answered a body that is not an object")
    if response.is_success:
        return payload
    code = payload.get("error_code")
    if code == VALHALLA_NO_ROUTE_ERROR_CODE:
        raise RoutingServiceNoRouteError("The routing service found no path")
    if code == VALHALLA_TRACE_ERROR_CODE:
        raise RoutingServiceTraceError("The routing service could not trace the shape")
    raise RoutingServiceUnavailableError("The routing service answered an error")


def fetch_served_copy_instant() -> int:
    """Read tileset_last_modified of /status, the instant in whole seconds of the routing data the service serves."""
    payload = fetch_valhalla_answer("GET", "/status", None)
    instant = payload.get("tileset_last_modified")
    if type(instant) is not int:
        raise RoutingServiceUnavailableError("The routing service did not name the instant of its data")
    return instant


def fetch_valhalla_route(body: Mapping[str, object]) -> ValhallaRoute:
    """Request a route and read the shape and length of its first leg."""
    payload = fetch_valhalla_answer("POST", "/route", body)
    try:
        leg = payload["trip"]["legs"][0]
        shape, length = leg["shape"], leg["summary"]["length"]
    except (KeyError, IndexError, TypeError) as error:
        raise RoutingServiceUnavailableError("The routing service answered a route without a leg") from error
    if not isinstance(shape, str) or not isinstance(length, int | float):
        raise RoutingServiceUnavailableError("The routing service answered a malformed leg")
    return ValhallaRoute(shape, float(length))


def fetch_valhalla_trace(body: Mapping[str, object]) -> ValhallaTrace:
    """Trace a shape and read every edge with its way, its two OpenStreetMap nodes and its shape indices."""
    payload = fetch_valhalla_answer("POST", "/trace_attributes", body)
    try:
        shape = payload["shape"]
        edges = tuple(
            ValhallaEdge(int(edge["way_id"]), int(edge["node_id"]), int(edge["end_node"]["node_id"]), int(edge["begin_shape_index"]), int(edge["end_shape_index"])) for edge in payload["edges"]
        )
    except (KeyError, TypeError, ValueError) as error:
        raise RoutingServiceUnavailableError("The routing service answered a malformed trace") from error
    if not isinstance(shape, str) or not edges:
        raise RoutingServiceUnavailableError("The routing service answered an empty trace")
    return ValhallaTrace(shape, edges)
