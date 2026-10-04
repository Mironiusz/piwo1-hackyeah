"""Hold the administrative boundary of Kraków of the copy in use and tell which chosen points of a route lie outside it."""

import threading
from datetime import datetime

from shapely import MultiPolygon, Point, Polygon, from_wkb, prepare
from shapely.errors import GEOSException, ShapelyError

from data.routing_data import RoutingDataError, build_routing_copy_directory, fetch_osm_boundary
from service.route_graph import RoutePoint
from service.route_segments import RoutingUnavailableError


class RouteBoundaryCache:
    """The boundary of one copy kept by the process together with the instant of that copy in one entry, read and replaced at once, with the lock its rebuild holds."""

    def __init__(self) -> None:
        """Start without a boundary."""
        self.entry: tuple[datetime, Polygon | MultiPolygon] | None = None
        self.lock = threading.Lock()


ROUTE_BOUNDARY_CACHE = RouteBoundaryCache()


def fetch_krakow_boundary(state_at: datetime) -> Polygon | MultiPolygon:
    """
    Give the boundary of Kraków of the copy whose instant is state_at, reading it again only when the copy changes.

    A missing, refused or unreadable boundary raises RoutingUnavailableError and is never kept, because without it no point
    can be told inside or outside Kraków and none is guessed.
    """
    entry = ROUTE_BOUNDARY_CACHE.entry
    if entry is not None and entry[0] == state_at:
        return entry[1]
    with ROUTE_BOUNDARY_CACHE.lock:
        entry = ROUTE_BOUNDARY_CACHE.entry
        if entry is not None and entry[0] == state_at:
            return entry[1]
        from config.config import ROUTING_DATA_DIR

        try:
            geometry = from_wkb(fetch_osm_boundary(build_routing_copy_directory(ROUTING_DATA_DIR, state_at), state_at))
        except (RoutingDataError, GEOSException, ShapelyError, ValueError, TypeError) as error:
            raise RoutingUnavailableError("The boundary of Kraków of the copy in use cannot be read") from error
        if not isinstance(geometry, Polygon | MultiPolygon) or geometry.is_empty or not geometry.is_valid:
            raise RoutingUnavailableError("The boundary of Kraków of the copy in use is not a valid area")
        prepare(geometry)
        ROUTE_BOUNDARY_CACHE.entry = (state_at, geometry)
        return geometry


def resolve_points_outside_krakow(state_at: datetime, start: RoutePoint, destination: RoutePoint) -> tuple[str, ...]:
    """Name the chosen points outside the boundary of Kraków of the copy, start before destination; a point on the boundary counts as inside."""
    boundary = fetch_krakow_boundary(state_at)
    return tuple(name for name, point in (("start", start), ("destination", destination)) if not boundary.covers(Point(point.lon, point.lat)))
