"""Check the specification's network eligibility and exclusions with invented tags."""

import unittest

from service.osm_tag_rule import resolve_is_pedestrian_network_way


class OsmNetworkCases(unittest.TestCase):
    """Keep stored-network and routing-file selection on the same predicate."""

    def test_each_approved_highway_is_walkable_by_default(self):
        highways = (
            "footway",
            "path",
            "pedestrian",
            "steps",
            "living_street",
            "track",
            "bridleway",
            "corridor",
            "road",
            "platform",
            "elevator",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "trunk_link",
            "primary_link",
            "secondary_link",
            "tertiary_link",
            "unclassified",
            "residential",
            "service",
        )
        for highway in highways:
            with self.subTest(highway=highway):
                self.assertTrue(resolve_is_pedestrian_network_way({"highway": highway}))

    def test_other_highways_are_excluded_even_with_foot_permission(self):
        for highway in ("motorway", "motorway_link", "construction", "proposed", "unknown", ""):
            with self.subTest(highway=highway):
                self.assertFalse(resolve_is_pedestrian_network_way({"highway": highway, "foot": "yes"}))
        self.assertFalse(resolve_is_pedestrian_network_way({"foot": "yes"}))

    def test_cycleways_require_an_explicit_approved_foot_permission(self):
        for foot in ("yes", "designated", "permissive", "destination", "delivery", "customers"):
            with self.subTest(foot=foot):
                self.assertTrue(resolve_is_pedestrian_network_way({"highway": "cycleway", "foot": foot}))
        for foot in ("", "no", "private", "use_sidepath", "unknown"):
            with self.subTest(foot=foot):
                self.assertFalse(resolve_is_pedestrian_network_way({"highway": "cycleway", "foot": foot}))

    def test_forbidden_foot_tags_and_motorroads_override_eligible_highways(self):
        for foot in ("no", "private", "use_sidepath"):
            with self.subTest(foot=foot):
                self.assertFalse(resolve_is_pedestrian_network_way({"highway": "path", "foot": foot}))
        self.assertFalse(resolve_is_pedestrian_network_way({"highway": "path", "foot": "yes", "motorroad": "yes"}))

    def test_access_restrictions_require_an_explicit_foot_permission(self):
        for access in ("no", "private"):
            with self.subTest(access=access):
                self.assertFalse(resolve_is_pedestrian_network_way({"highway": "path", "access": access}))
                self.assertFalse(resolve_is_pedestrian_network_way({"highway": "path", "access": access, "foot": "unknown"}))
                self.assertTrue(resolve_is_pedestrian_network_way({"highway": "path", "access": access, "foot": "yes"}))

    def test_separate_sidewalk_excludes_motor_traffic_ways(self):
        for key in ("sidewalk", "sidewalk:both"):
            with self.subTest(key=key):
                self.assertFalse(resolve_is_pedestrian_network_way({"highway": "residential", "foot": "yes", key: "separate"}))
                self.assertTrue(resolve_is_pedestrian_network_way({"highway": "footway", key: "separate"}))

    def test_selection_does_not_mutate_source_tags(self):
        tags = {"highway": "path", "access": "private", "foot": "yes"}
        original = dict(tags)
        self.assertTrue(resolve_is_pedestrian_network_way(tags))
        self.assertEqual(tags, original)
