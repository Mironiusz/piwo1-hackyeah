"""Detect missing, truncated and replaced routing files using invented contents."""

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

import pytest

from data.routing_data import ROUTING_FILE_NAMES, RoutingDataError, apply_osm_routing_manifest, fetch_osm_routing_manifest


@pytest.mark.integration
class RoutingDataIntegration(unittest.TestCase):
    """Verify manifests without building tiles or connecting to a database."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        for name in ROUTING_FILE_NAMES:
            (self.directory / name).write_bytes(b"invented routing contents")
        self.state_at = datetime(2026, 10, 3, tzinfo=UTC)

    def test_manifest_round_trip_keeps_source_identity_and_both_checksums(self):
        created = apply_osm_routing_manifest(self.directory, self.state_at)
        self.assertEqual(fetch_osm_routing_manifest(self.directory), created)
        self.assertEqual(tuple(item.filename for item in created.files), ROUTING_FILE_NAMES)
        self.assertFalse(list(self.directory.glob(".manifest-*")))

    def test_an_existing_manifest_is_never_overwritten(self):
        apply_osm_routing_manifest(self.directory, self.state_at)
        path = self.directory / "manifest.json"
        original = path.read_bytes()
        with self.assertRaises(RoutingDataError):
            apply_osm_routing_manifest(self.directory, self.state_at)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(list(self.directory.glob(".manifest-*")))

    def test_missing_and_empty_files_prevent_manifest_creation(self):
        path = self.directory / ROUTING_FILE_NAMES[0]
        path.write_bytes(b"")
        with self.assertRaises(RoutingDataError):
            apply_osm_routing_manifest(self.directory, self.state_at)
        path.unlink()
        with self.assertRaises(RoutingDataError):
            apply_osm_routing_manifest(self.directory, self.state_at)
        self.assertFalse((self.directory / "manifest.json").exists())

    def test_truncated_and_same_size_replacements_are_detected(self):
        apply_osm_routing_manifest(self.directory, self.state_at)
        path = self.directory / ROUTING_FILE_NAMES[0]
        original = path.read_bytes()
        for changed in (original[:-1], b"X" * len(original)):
            path.write_bytes(changed)
            with self.assertRaises(RoutingDataError):
                fetch_osm_routing_manifest(self.directory)

    def test_naive_state_and_invalid_manifest_are_rejected(self):
        with self.assertRaises(RoutingDataError):
            apply_osm_routing_manifest(self.directory, datetime(2026, 10, 3))
        (self.directory / "manifest.json").write_text("not JSON")
        with self.assertRaises(RoutingDataError):
            fetch_osm_routing_manifest(self.directory)

    def test_malformed_file_record_is_rejected(self):
        apply_osm_routing_manifest(self.directory, self.state_at)
        path = self.directory / "manifest.json"
        payload = json.loads(path.read_text())
        payload["files"][ROUTING_FILE_NAMES[0]]["size_bytes"] = True
        path.write_text(json.dumps(payload))
        with self.assertRaises(RoutingDataError):
            fetch_osm_routing_manifest(self.directory)
