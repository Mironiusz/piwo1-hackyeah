"""Build the shared object Fact of the contract from a stored fact and the status the rule of M4 derived for it."""

from datetime import date

from accessibility_db.closed_lists import FactSource

from service.fact_status import FactView


def build_day(value: date | None) -> str | None:
    """Write a calendar day as YYYY-MM-DD, or null."""
    return None if value is None else value.isoformat()


def build_fact_body(fact: FactView) -> dict[str, object]:
    """Build the fields of a fact the contract names, and nothing about the persons behind its votes or their weights."""
    stored = fact.fact
    is_openstreetmap = stored.source == FactSource.OPENSTREETMAP
    return {
        "id": stored.id,
        "type": stored.fact_type.value,
        "point": {"lat": stored.lat, "lon": stored.lon},
        "geozone_radius_m": stored.geozone_radius_m,
        "description": stored.description,
        "step_count": stored.step_count,
        "source": stored.source.value,
        "status": fact.status.status.value,
        "is_removed_from_osm": stored.is_removed_from_osm,
        "osm_edited_on": build_day(stored.osm_edited_on) if is_openstreetmap else None,
        "last_confirmed_on": build_day(fact.status.last_confirmed_on),
        "is_sample": stored.is_sample,
        "can_be_flagged": not is_openstreetmap,
    }
