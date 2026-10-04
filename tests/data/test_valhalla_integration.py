"""Check the calls to the routing service and the reading of its answers through an invented transport, without a network."""

import httpx
import pytest

from data import valhalla
from data.valhalla import (
    RoutingServiceNoRouteError,
    RoutingServiceTraceError,
    RoutingServiceUnavailableError,
    ValhallaEdge,
    build_valhalla_client,
    fetch_served_copy_instant,
    fetch_valhalla_route,
    fetch_valhalla_trace,
)
from tests.common_runtime_settings import apply_invented_runtime_settings

pytestmark = pytest.mark.integration

ROUTE_ANSWER = {"trip": {"legs": [{"shape": "_p~iF~ps|U_ulLnnqC", "summary": {"length": 1.84}}], "summary": {"length": 1.84}}}
TRACE_ANSWER = {
    "shape": "_p~iF~ps|U_ulLnnqC",
    "edges": [{"way_id": 244622823, "node_id": 1913875698, "end_node": {"node_id": 2519190132, "type": "street_intersection"}, "begin_shape_index": 0, "end_shape_index": 1}],
}


def apply_invented_service(monkeypatch: pytest.MonkeyPatch, answer) -> list[httpx.Request]:
    """Serve every call from an invented handler at the configured address and record the requests."""
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        """Record the request and give the invented answer."""
        requests.append(request)
        return answer(request)

    client = httpx.Client(base_url="http://routing:8002", transport=httpx.MockTransport(handle), timeout=valhalla.VALHALLA_CALL_TIMEOUT_SECONDS)
    monkeypatch.setattr(valhalla, "build_valhalla_client", lambda: client)
    return requests


def test_client_is_bound_to_the_configured_address_without_proxies_or_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build the one client at ROUTING_SERVICE_URL with the timeout of 2 seconds, no proxies from the environment and no redirects."""
    with apply_invented_runtime_settings(monkeypatch):
        build_valhalla_client.cache_clear()
        try:
            client = build_valhalla_client()
            assert str(client.base_url) == "http://routing:8002"
            assert client.timeout == httpx.Timeout(2.0)
            assert client.follow_redirects is False
            assert client.trust_env is False
        finally:
            build_valhalla_client.cache_clear()


def test_served_instant_is_read_from_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read tileset_last_modified of /status."""
    requests = apply_invented_service(monkeypatch, lambda _request: httpx.Response(200, json={"version": "3.9.0", "tileset_last_modified": 1790972494}))
    assert fetch_served_copy_instant() == 1790972494
    assert [(request.method, request.url.path) for request in requests] == [("GET", "/status")]


def test_route_gives_its_shape_and_length(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read the shape and length of the first leg of a route."""
    requests = apply_invented_service(monkeypatch, lambda _request: httpx.Response(200, json=ROUTE_ANSWER))
    route = fetch_valhalla_route({"costing": "pedestrian"})
    assert (route.shape, route.length_km) == ("_p~iF~ps|U_ulLnnqC", 1.84)
    assert all(request.url.host == "routing" and request.url.port == 8002 for request in requests)


def test_trace_gives_its_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read every edge with its way, its two nodes and its shape indices."""
    apply_invented_service(monkeypatch, lambda _request: httpx.Response(200, json=TRACE_ANSWER))
    assert fetch_valhalla_trace({"shape_match": "edge_walk"}).edges == (ValhallaEdge(244622823, 1913875698, 2519190132, 0, 1),)


@pytest.mark.parametrize(("code", "error"), [(442, RoutingServiceNoRouteError), (443, RoutingServiceTraceError), (171, RoutingServiceUnavailableError)])
def test_error_codes_raise_their_errors(monkeypatch: pytest.MonkeyPatch, code: int, error: type[Exception]) -> None:
    """Raise the error of 442 and 443, and RoutingServiceUnavailableError for any other code."""
    apply_invented_service(monkeypatch, lambda _request: httpx.Response(400, json={"error_code": code, "error": "invented", "status_code": 400}))
    with pytest.raises(error):
        fetch_valhalla_route({"costing": "pedestrian"})


def raise_timeout(request: httpx.Request) -> httpx.Response:
    """Fail like a service that answers after its time limit."""
    raise httpx.ReadTimeout("invented timeout", request=request)


@pytest.mark.parametrize(
    "answer",
    [lambda _request: httpx.Response(500, text="failure"), raise_timeout, lambda _request: httpx.Response(200, json={"no": "trip"}), lambda _request: httpx.Response(200, json=[1])],
)
def test_failures_and_malformed_bodies_make_the_service_unavailable(monkeypatch: pytest.MonkeyPatch, answer) -> None:
    """Treat a status 500, a timeout, a body without a trip and a body that is not an object as an unavailable service."""
    apply_invented_service(monkeypatch, answer)
    with pytest.raises(RoutingServiceUnavailableError):
        fetch_valhalla_route({"costing": "pedestrian"})


def test_status_without_an_instant_makes_the_service_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse a status that does not name the instant of the served data."""
    apply_invented_service(monkeypatch, lambda _request: httpx.Response(200, json={"version": "3.9.0"}))
    with pytest.raises(RoutingServiceUnavailableError):
        fetch_served_copy_instant()
