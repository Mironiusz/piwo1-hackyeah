"""Check which stored facts a fresh copy makes disappear for the first time."""

from accessibility_db.closed_lists import FactSource, FactType, OsmElementType

from data.osm_copy import OsmFactIdentity, OsmStoredFact
from service.osm_reconciliation import resolve_osm_disappearing_facts

STAIRS = OsmFactIdentity(OsmElementType.WAY, 10, FactType.STAIRS)
BENCH = OsmFactIdentity(OsmElementType.NODE, 20, FactType.REST_PLACE)


def test_first_import_has_nothing_to_reconcile():
    assert resolve_osm_disappearing_facts((), (STAIRS, BENCH)) == ()


def test_facts_still_present_do_not_disappear():
    stored = (OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False),)
    assert resolve_osm_disappearing_facts(stored, (STAIRS,)) == ()


def test_present_fact_missing_from_the_fresh_copy_disappears():
    fact = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    assert resolve_osm_disappearing_facts((fact,), (BENCH,)) == (fact,)


def test_converted_and_removed_facts_that_stay_absent_need_no_decision():
    converted = OsmStoredFact(1, STAIRS, FactSource.USER_REPORT, False)
    removed = OsmStoredFact(2, BENCH, FactSource.OPENSTREETMAP, True)
    assert resolve_osm_disappearing_facts((converted, removed), ()) == ()


def test_returning_converted_and_removed_facts_need_no_decision():
    converted = OsmStoredFact(1, STAIRS, FactSource.USER_REPORT, False)
    removed = OsmStoredFact(2, BENCH, FactSource.OPENSTREETMAP, True)
    assert resolve_osm_disappearing_facts((converted, removed), (STAIRS, BENCH)) == ()


def test_a_split_way_with_a_new_identity_does_not_inherit_the_old_fact():
    old = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    split = OsmFactIdentity(OsmElementType.WAY, 11, FactType.STAIRS)
    assert resolve_osm_disappearing_facts((old,), (split,)) == (old,)


def test_another_fact_type_on_the_same_element_is_another_identity():
    fact = OsmStoredFact(1, STAIRS, FactSource.OPENSTREETMAP, False)
    ramp = OsmFactIdentity(OsmElementType.WAY, 10, FactType.RAMP)
    assert resolve_osm_disappearing_facts((fact,), (ramp,)) == (fact,)
