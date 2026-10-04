"""Exercise real pyosmium reading on invented local files."""

import tempfile
import unittest
from pathlib import Path

import osmium
import pytest
from shapely import from_wkb

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from data.osm_reader import OsmInvalidAreaTally, OsmReadError, fetch_osm_elements, fetch_osm_header_timestamp

SOURCE_XML = """<osm version="0.6">
<node id="1" lat="50" lon="19.9" timestamp="2026-10-03T00:00:00Z"/>
<node id="2" lat="50" lon="20" timestamp="2026-10-03T00:00:00Z"/>
<node id="3" lat="50.1" lon="20" timestamp="2026-10-03T00:00:00Z"/>
<node id="4" lat="50.1" lon="19.9" timestamp="2026-10-03T00:00:00Z"/>
<way id="10" timestamp="2026-10-03T00:00:00Z"><nd ref="1"/><nd ref="2"/><nd ref="3"/><nd ref="4"/><nd ref="1"/><tag k="highway" v="path"/></way>
<relation id="449696" timestamp="2026-10-03T00:00:00Z"><member type="way" ref="10" role="outer"/><tag k="type" v="multipolygon"/><tag k="boundary" v="administrative"/></relation>
</osm>"""
OPEN_RING_WAY_XML = '<way id="20" timestamp="2026-10-03T00:00:00Z"><nd ref="1"/><nd ref="2"/><nd ref="3"/></way>'
BROKEN_MULTIPOLYGON_XML = '<relation id="30" timestamp="2026-10-03T00:00:00Z"><member type="way" ref="20" role="outer"/><tag k="type" v="multipolygon"/><tag k="landuse" v="grass"/></relation>'


def build_broken_source_xml() -> str:
    """Add a multipolygon whose only outer ring is open, which native assembly leaves without an outer ring."""
    return SOURCE_XML.replace('<relation id="449696"', OPEN_RING_WAY_XML + '<relation id="449696"').replace("</osm>", BROKEN_MULTIPOLYGON_XML + "</osm>")


def build_test_deadline() -> Deadline:
    """Give a reading budget that no invented file can exhaust."""
    return build_deadline(60, fetch_monotonic_seconds())


@pytest.mark.integration
class OsmReaderIntegration(unittest.TestCase):
    """Require owned snapshots, original identities and complete node references."""

    def test_snapshots_survive_iterator_end_and_have_original_area_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML)
            snapshots = list(fetch_osm_elements(path, build_test_deadline()))
        way = next(element for element in snapshots if element.element_type == "way" and element.area_wkb is None)
        self.assertEqual(way.node_ids, (1, 2, 3, 4, 1))
        self.assertEqual(way.tags["highway"], "path")
        self.assertEqual(way.coordinates[0], way.coordinates[-1])
        with self.assertRaises(TypeError):
            way.tags["highway"] = "road"
        area = next(element for element in snapshots if element.area_wkb is not None and element.element_type == "relation")
        self.assertEqual(area.element_id, 449696)
        self.assertTrue(from_wkb(area.area_wkb).is_valid)

    def test_an_area_without_an_outer_ring_is_skipped_and_counted_while_the_rest_is_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(build_broken_source_xml())
            invalid_areas = OsmInvalidAreaTally()
            snapshots = list(fetch_osm_elements(path, build_test_deadline(), invalid_areas))
        self.assertEqual(invalid_areas.count, 1)
        areas = {(element.element_type, element.element_id) for element in snapshots if element.area_wkb is not None}
        self.assertEqual(areas, {("way", 10), ("relation", 449696)})
        relation = next(element for element in snapshots if element.element_type == "relation" and element.element_id == 30)
        self.assertIsNone(relation.area_wkb)
        self.assertEqual(relation.members, (("w", 20, "outer"),))

    def test_an_area_without_an_outer_ring_is_skipped_without_a_tally(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(build_broken_source_xml())
            snapshots = list(fetch_osm_elements(path, build_test_deadline()))
        self.assertFalse(any(element.element_id == 30 and element.area_wkb is not None for element in snapshots))

    def test_missing_references_fail_instead_of_dropping_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML.replace('<nd ref="2"/>', '<nd ref="999"/>'))
            with self.assertRaises(OsmReadError):
                list(fetch_osm_elements(path, build_test_deadline()))

    def test_missing_edit_timestamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML.replace(' timestamp="2026-10-03T00:00:00Z"', "", 1))
            with self.assertRaises(OsmReadError):
                list(fetch_osm_elements(path, build_test_deadline()))

    def test_header_and_elements_round_trip_through_an_invented_pbf(self):
        with tempfile.TemporaryDirectory() as directory:
            xml = Path(directory) / "invented.osm"
            pbf = Path(directory) / "invented.osm.pbf"
            xml.write_text(SOURCE_XML)
            header = osmium.io.Header()
            header.set("osmosis_replication_timestamp", "2026-10-03T00:00:00Z")
            with osmium.SimpleWriter(str(pbf), header=header) as writer:
                for element in osmium.FileProcessor(xml):
                    writer.add(element)
            self.assertEqual(fetch_osm_header_timestamp(pbf), "2026-10-03T00:00:00Z")
            snapshots = list(fetch_osm_elements(pbf, build_test_deadline()))
            self.assertEqual(sum(element.element_type == "node" for element in snapshots), 4)

    def test_unreadable_source_is_a_named_failure(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(OsmReadError):
            list(fetch_osm_elements(Path(directory) / "absent.osm.pbf", build_test_deadline()))

    def test_expired_deadline_stops_reading_with_the_deadline_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML)
            with self.assertRaises(DeadlineExpiredError):
                list(fetch_osm_elements(path, Deadline(fetch_monotonic_seconds() - 1)))
