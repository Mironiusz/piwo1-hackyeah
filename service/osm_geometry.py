"""Locate source facts using the approved projected geometry rules."""

import math

from pyproj import Transformer
from pyproj.exceptions import ProjError
from shapely import get_coordinates
from shapely.errors import GEOSException
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import transform

OSM_CALCULATION_CRS = "EPSG:2180"
OSM_STORAGE_CRS = "EPSG:4326"


class OsmGeometryError(ValueError):
    """Describe geometry that cannot supply a reliable imported fact location."""


def resolve_osm_fact_location(geometry: Point | LineString | Polygon | MultiPolygon) -> Point:
    """Keep node positions, interpolate half a way's length, or choose a strict area interior."""
    if not isinstance(geometry, (Point, LineString, Polygon, MultiPolygon)) or geometry.is_empty or not geometry.is_valid:
        raise OsmGeometryError("Invalid source geometry")
    if geometry.has_z or geometry.has_m:
        raise OsmGeometryError("Source geometry must have two coordinates")
    coordinates = get_coordinates(geometry)
    if any(not math.isfinite(float(lon)) or not math.isfinite(float(lat)) or not -180 <= lon <= 180 or not -90 <= lat <= 90 for lon, lat in coordinates):
        raise OsmGeometryError("Invalid source coordinates")
    if isinstance(geometry, Point):
        return geometry
    try:
        forward = Transformer.from_crs(OSM_STORAGE_CRS, OSM_CALCULATION_CRS, always_xy=True)
        reverse = Transformer.from_crs(OSM_CALCULATION_CRS, OSM_STORAGE_CRS, always_xy=True)
        projected = transform(forward.transform, geometry)
        if projected.is_empty or not projected.is_valid:
            raise OsmGeometryError("Invalid projected geometry")
        if isinstance(geometry, LineString):
            if not math.isfinite(projected.length) or projected.length <= 0:
                raise OsmGeometryError("Way has no usable length")
            location = projected.interpolate(projected.length / 2)
        else:
            location = projected.representative_point()
            if not projected.contains(location):
                raise OsmGeometryError("Area has no strict interior location")
        result = transform(reverse.transform, location)
    except (ProjError, GEOSException) as error:
        raise OsmGeometryError("Cannot compute fact location") from error
    if not isinstance(result, Point) or result.is_empty or not math.isfinite(result.x) or not math.isfinite(result.y):
        raise OsmGeometryError("Invalid computed fact location")
    if isinstance(geometry, (Polygon, MultiPolygon)) and not geometry.contains(result):
        raise OsmGeometryError("Computed location is outside the source area")
    return result


def resolve_osm_element_coverage(boundary: Polygon | MultiPolygon, geometry: Point | LineString) -> bool:
    """Keep inside nodes and whole ways having at least one source node inside the boundary."""
    if not isinstance(boundary, (Polygon, MultiPolygon)) or boundary.is_empty or not boundary.is_valid:
        raise OsmGeometryError("Invalid administrative boundary")
    if not isinstance(geometry, (Point, LineString)) or geometry.is_empty or not geometry.is_valid:
        raise OsmGeometryError("Invalid element geometry")
    if isinstance(geometry, Point):
        return boundary.contains(geometry)
    return any(boundary.contains(Point(coordinate)) for coordinate in geometry.coords)
