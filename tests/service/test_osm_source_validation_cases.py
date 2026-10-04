"""Exercise source validation with invented metadata and no external dependencies."""

import unittest
from datetime import UTC, date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from service.osm_source_validation import OsmSourceError, resolve_osm_checksum, resolve_osm_source_is_newer, resolve_osm_source_location, resolve_osm_source_state


class OsmSourceValidationCases(unittest.TestCase):
    """Keep invalid sources and stale copies from reaching publication."""

    def test_dated_source_location_is_accepted(self):
        location = "https://download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf"
        self.assertEqual(resolve_osm_source_location(location), location)

    def test_other_source_locations_are_rejected(self):
        locations = (
            "http://download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf",
            "https://example.invalid/europe/poland/malopolskie-261003.osm.pbf",
            "https://download.geofabrik.de.example.invalid/europe/poland/malopolskie-261003.osm.pbf",
            "https://user@download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf",
            "https://download.geofabrik.de:443/europe/poland/malopolskie-261003.osm.pbf",
            "https://download.geofabrik.de/europe/poland/malopolskie-latest.osm.pbf",
            "https://download.geofabrik.de/europe/malopolskie-261003.osm.pbf",
            "https://download.geofabrik.de/europe/poland/../poland/malopolskie-261003.osm.pbf",
            "https://download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf?other=1",
            "https://download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf#other",
            "/europe/poland/malopolskie-261003.osm.pbf",
            "\nhttps://download.geofabrik.de/europe/poland/malopolskie-261003.osm.pbf",
            "https://[/malopolskie-261003.osm.pbf",
        )
        for location in locations:
            with self.subTest(location=location), self.assertRaises(OsmSourceError):
                resolve_osm_source_location(location)

    def test_checksum_formats_match_the_selected_file(self):
        digest = "0123456789abcdef0123456789abcdef"
        filename = "malopolskie-261003.osm.pbf"
        for published in (digest, digest.upper() + "\n", digest + "  " + filename, digest + " *" + filename):
            with self.subTest(published=published):
                self.assertEqual(resolve_osm_checksum(published, filename, digest), digest)

    def test_corrupt_or_ambiguous_checksums_are_rejected(self):
        digest = "0123456789abcdef0123456789abcdef"
        for published in ("", "bad", digest + " other.osm.pbf", digest + "\n" + digest, "f" * 32, digest + " filename extra"):
            with self.subTest(published=published), self.assertRaises(OsmSourceError):
                resolve_osm_checksum(published, "malopolskie-261003.osm.pbf", digest)
        with self.assertRaises(OsmSourceError):
            resolve_osm_checksum(digest, "malopolskie-261003.osm.pbf", "invalid")
        with self.assertRaises(OsmSourceError):
            resolve_osm_checksum(digest, "malopolskie-latest.osm.pbf", digest)

    def test_source_instant_preserves_its_offset(self):
        instant = resolve_osm_source_state("2026-10-03T22:00:00.123+02:00")
        self.assertEqual(instant.utcoffset(), timedelta(hours=2))
        self.assertEqual(instant.microsecond, 123000)
        self.assertEqual(instant.astimezone(UTC), datetime(2026, 10, 3, 20, 0, 0, 123000, tzinfo=UTC))
        self.assertEqual(resolve_osm_source_state("2026-10-03T22:00:00.123456Z").microsecond, 123456)

    def test_source_days_follow_warsaw_midnight(self):
        cases = (
            ("2026-10-02T20:21:34Z", date(2026, 10, 2)),
            ("2026-10-02T22:30:00Z", date(2026, 10, 3)),
            ("2026-12-31T23:30:00Z", date(2027, 1, 1)),
        )
        for timestamp, expected in cases:
            with self.subTest(timestamp=timestamp):
                self.assertEqual(resolve_osm_source_state(timestamp).astimezone(ZoneInfo("Europe/Warsaw")).date(), expected)

    def test_invalid_or_naive_source_instants_are_rejected(self):
        for timestamp in ("", "2026-10-03", "2026-10-03T12:00:00", "2026-02-30T12:00:00Z", "2026-10-03T12:00:00+15:00", "2026-10-03T12:00:00+02:60", "2026-10-03T12:00:00.1234567Z"):
            with self.subTest(timestamp=timestamp), self.assertRaises(OsmSourceError):
                resolve_osm_source_state(timestamp)

    def test_first_and_newer_copies_are_accepted(self):
        state_at = datetime(2026, 10, 3, tzinfo=UTC)
        self.assertTrue(resolve_osm_source_is_newer(state_at, None))
        self.assertTrue(resolve_osm_source_is_newer(state_at, datetime(2026, 10, 2, tzinfo=UTC)))

    def test_equal_instants_in_different_offsets_are_unchanged(self):
        self.assertFalse(resolve_osm_source_is_newer(datetime(2026, 10, 3, 2, tzinfo=timezone(timedelta(hours=2))), datetime(2026, 10, 3, tzinfo=UTC)))

    def test_repeated_local_hour_is_compared_by_instant(self):
        zone = ZoneInfo("Europe/Warsaw")
        first_occurrence = datetime(2026, 10, 25, 2, 30, tzinfo=zone, fold=0)
        second_occurrence = datetime(2026, 10, 25, 2, 30, tzinfo=zone, fold=1)
        self.assertTrue(resolve_osm_source_is_newer(second_occurrence, first_occurrence))
        with self.assertRaises(OsmSourceError):
            resolve_osm_source_is_newer(first_occurrence, second_occurrence)

    def test_older_and_naive_copies_are_rejected(self):
        with self.assertRaises(OsmSourceError):
            resolve_osm_source_is_newer(datetime(2026, 10, 2, tzinfo=UTC), datetime(2026, 10, 3, tzinfo=UTC))
        with self.assertRaises(OsmSourceError):
            resolve_osm_source_is_newer(datetime(2026, 10, 3), None)
        with self.assertRaises(OsmSourceError):
            resolve_osm_source_is_newer(datetime(2026, 10, 3, tzinfo=UTC), datetime(2026, 10, 3))
