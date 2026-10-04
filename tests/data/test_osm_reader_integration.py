"""Exercise real pyosmium reading on invented local files."""

import tempfile
import unittest
from pathlib import Path

import osmium
import pytest
from shapely import from_wkb

from data.osm_reader import OsmReadError, fetch_osm_elements, fetch_osm_header_timestamp

SOURCE_XML = """<osm version="0.6">
<node id="1" lat="50" lon="19.9" timestamp="2026-10-03T00:00:00Z"/>
<node id="2" lat="50" lon="20" timestamp="2026-10-03T00:00:00Z"/>
<node id="3" lat="50.1" lon="20" timestamp="2026-10-03T00:00:00Z"/>
<node id="4" lat="50.1" lon="19.9" timestamp="2026-10-03T00:00:00Z"/>
<way id="10" timestamp="2026-10-03T00:00:00Z"><nd ref="1"/><nd ref="2"/><nd ref="3"/><nd ref="4"/><nd ref="1"/><tag k="highway" v="path"/></way>
<relation id="449696" timestamp="2026-10-03T00:00:00Z"><member type="way" ref="10" role="outer"/><tag k="type" v="multipolygon"/><tag k="boundary" v="administrative"/></relation>
</osm>"""


@pytest.mark.integration
class OsmReaderIntegration(unittest.TestCase):
    """Require owned snapshots, original identities and complete node references."""

    def test_snapshots_survive_iterator_end_and_have_original_area_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML)
            snapshots = list(fetch_osm_elements(path))
        way = next(element for element in snapshots if element.element_type == "way" and element.area_wkb is None)
        self.assertEqual(way.node_ids, (1, 2, 3, 4, 1))
        self.assertEqual(way.tags["highway"], "path")
        self.assertEqual(way.coordinates[0], way.coordinates[-1])
        with self.assertRaises(TypeError):
            way.tags["highway"] = "road"
        area = next(element for element in snapshots if element.area_wkb is not None and element.element_type == "relation")
        self.assertEqual(area.element_id, 449696)
        self.assertTrue(from_wkb(area.area_wkb).is_valid)

    def test_missing_references_fail_instead_of_dropping_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML.replace('<nd ref="2"/>', '<nd ref="999"/>'))
            with self.assertRaises(OsmReadError):
                list(fetch_osm_elements(path))

    def test_missing_edit_timestamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invented.osm"
            path.write_text(SOURCE_XML.replace(' timestamp="2026-10-03T00:00:00Z"', "", 1))
            with self.assertRaises(OsmReadError):
                list(fetch_osm_elements(path))

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
            snapshots = list(fetch_osm_elements(pbf))
            self.assertEqual(sum(element.element_type == "node" for element in snapshots), 4)

    def test_unreadable_source_is_a_named_failure(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(OsmReadError):
            list(fetch_osm_elements(Path(directory) / "absent.osm.pbf"))
