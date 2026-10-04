"""Check approved fact locations with invented lines and polygons."""

import unittest

from pyproj import Transformer
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import transform

from service.osm_geometry import OsmGeometryError, resolve_osm_element_coverage, resolve_osm_fact_location


class OsmGeometryCases(unittest.TestCase):
    """Refuse guessed positions and preserve the whole-way boundary rule."""

    def test_node_coordinates_are_kept(self):
        point = Point(19.95, 50.05)
        self.assertEqual(resolve_osm_fact_location(point), point)

    def test_midpoint_follows_metric_length_rather_than_vertex_count(self):
        to_source = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)
        to_metric = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
        source = transform(to_source.transform, LineString(((560000, 240000), (560010, 240000), (560100, 240000))))
        result = transform(to_metric.transform, resolve_osm_fact_location(source))
        self.assertAlmostEqual(result.x, 560050, places=4)
        self.assertAlmostEqual(result.y, 240000, places=4)

    def test_area_location_avoids_holes_and_concave_exterior(self):
        shell = ((19.9, 50), (20, 50), (20, 50.1), (19.9, 50.1), (19.9, 50))
        hole = ((19.93, 50.03), (19.97, 50.03), (19.97, 50.07), (19.93, 50.07), (19.93, 50.03))
        area = Polygon(shell, (hole,))
        self.assertTrue(area.contains(resolve_osm_fact_location(area)))
        concave = Polygon(((19.9, 50), (20, 50), (20, 50.02), (19.92, 50.02), (19.92, 50.1), (19.9, 50.1)))
        self.assertTrue(concave.contains(resolve_osm_fact_location(concave)))

    def test_multiple_outer_areas_have_a_location_in_one_component(self):
        area = MultiPolygon((Polygon(((19.9, 50), (19.91, 50), (19.91, 50.01), (19.9, 50.01))), Polygon(((20, 50), (20.01, 50), (20.01, 50.01), (20, 50.01)))))
        self.assertTrue(area.contains(resolve_osm_fact_location(area)))

    def test_unusable_geometry_is_rejected(self):
        geometries = (
            Point(),
            Point(float("inf"), 50),
            Point(181, 50),
            Point(19.9, 91),
            Point(19.9, 50, 3),
            LineString(((19.9, 50), (19.9, 50))),
            Polygon(((19.9, 50), (20, 50.1), (20, 50), (19.9, 50.1))),
        )
        for geometry in geometries:
            with self.subTest(geometry=geometry), self.assertRaises(OsmGeometryError):
                resolve_osm_fact_location(geometry)

    def test_way_with_inside_node_is_kept_whole(self):
        boundary = Polygon(((19.9, 50), (20, 50), (20, 50.1), (19.9, 50.1)))
        way = LineString(((19.95, 50.05), (20.1, 50.05)))
        original = tuple(way.coords)
        self.assertTrue(resolve_osm_element_coverage(boundary, way))
        self.assertEqual(tuple(way.coords), original)
        self.assertFalse(resolve_osm_element_coverage(boundary, LineString(((19.8, 50.05), (20.1, 50.05)))))

    def test_holes_are_outside_the_import_area(self):
        boundary = Polygon(((19.9, 50), (20, 50), (20, 50.1), (19.9, 50.1)), (((19.93, 50.03), (19.97, 50.03), (19.97, 50.07), (19.93, 50.07)),))
        self.assertFalse(resolve_osm_element_coverage(boundary, Point(19.95, 50.05)))
        self.assertTrue(resolve_osm_element_coverage(boundary, Point(19.91, 50.01)))
