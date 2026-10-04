"""Check the refusal of a chosen point outside an invented boundary of Kraków and the cache of the boundary."""

from datetime import timedelta

import pytest
from shapely import Polygon, to_wkb

from data.routing_data import RoutingDataError
from service import route_boundary
from service.route_boundary import RouteBoundaryCache, resolve_points_outside_krakow
from service.route_graph import RoutePoint
from service.route_segments import RoutingUnavailableError
from tests.common_route_network import INVENTED_STATE_AT

pytestmark = pytest.mark.usefixtures("runtime_settings")

INVENTED_BOUNDARY = Polygon([(19.80, 50.00), (20.20, 50.00), (20.20, 50.15), (19.80, 50.15)])
RYNEK = RoutePoint(50.0617, 19.9373)
WIELICZKA = RoutePoint(49.9870, 20.0650)


@pytest.fixture
def boundary_reads(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Serve the invented boundary from a fresh cache and count its reads."""
    reads: list[int] = []

    def fetch_invented_boundary(_directory, _state_at) -> bytes:
        """Give the invented boundary as WKB."""
        reads.append(1)
        return to_wkb(INVENTED_BOUNDARY)

    monkeypatch.setattr(route_boundary, "ROUTE_BOUNDARY_CACHE", RouteBoundaryCache())
    monkeypatch.setattr(route_boundary, "fetch_osm_boundary", fetch_invented_boundary)
    return reads


@pytest.mark.usefixtures("boundary_reads")
def test_start_in_wieliczka_is_named() -> None:
    """Name the start in Wieliczka outside the boundary, with the Rynek Główny inside as the destination (AC-9)."""
    assert resolve_points_outside_krakow(INVENTED_STATE_AT, WIELICZKA, RYNEK) == ("start",)
    assert resolve_points_outside_krakow(INVENTED_STATE_AT, RYNEK, WIELICZKA) == ("destination",)


@pytest.mark.usefixtures("boundary_reads")
def test_both_points_outside_are_named_in_order() -> None:
    """Name both points, start before destination."""
    assert resolve_points_outside_krakow(INVENTED_STATE_AT, WIELICZKA, RoutePoint(50.30, 19.90)) == ("start", "destination")


@pytest.mark.usefixtures("boundary_reads")
def test_point_fifty_metres_inside_and_a_point_on_the_boundary_are_inside() -> None:
    """Accept a point 50 m inside the boundary and a point lying on it."""
    assert resolve_points_outside_krakow(INVENTED_STATE_AT, RoutePoint(50.00045, 20.0), RoutePoint(50.0, 20.0)) == ()


def test_boundary_is_read_again_only_for_a_new_copy(boundary_reads: list[int]) -> None:
    """Read the boundary once per instant of the copy."""
    resolve_points_outside_krakow(INVENTED_STATE_AT, RYNEK, RYNEK)
    resolve_points_outside_krakow(INVENTED_STATE_AT, RYNEK, RYNEK)
    assert len(boundary_reads) == 1
    resolve_points_outside_krakow(INVENTED_STATE_AT + timedelta(days=1), RYNEK, RYNEK)
    assert len(boundary_reads) == 2


def test_missing_boundary_makes_routing_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse to guess a point inside or outside when the boundary of the copy cannot be read, and keep nothing."""

    def fetch_missing_boundary(_directory, _state_at) -> bytes:
        """Fail like a copy without a boundary file."""
        raise RoutingDataError("Routing manifest does not list the boundary")

    monkeypatch.setattr(route_boundary, "ROUTE_BOUNDARY_CACHE", RouteBoundaryCache())
    monkeypatch.setattr(route_boundary, "fetch_osm_boundary", fetch_missing_boundary)
    with pytest.raises(RoutingUnavailableError):
        resolve_points_outside_krakow(INVENTED_STATE_AT, RYNEK, RYNEK)
    assert route_boundary.ROUTE_BOUNDARY_CACHE.entry is None
