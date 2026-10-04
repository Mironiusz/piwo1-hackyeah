"""Build the shared object Fact of the contract from a stored fact and the status the rule of M4 derived for it, and the bodies of the community facts that carry it."""

from datetime import date

from accessibility_db.closed_lists import FactSource

from service.community_facts import AreaFacts, FlaggedFactView, NearbyFactView
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


def build_fact_item_body(fact: FactView) -> dict[str, object]:
    """Build the body of read_fact, create_fact and cast_vote: the one fact."""
    return {"fact": build_fact_body(fact)}


def build_area_facts_body(area: AreaFacts) -> dict[str, object]:
    """Build the body of list_facts_in_area: the facts of the rectangle and whether it holds more."""
    return {"facts": [build_fact_body(view) for view in area.facts], "is_truncated": area.is_truncated}


def build_nearby_facts_body(nearby: tuple[NearbyFactView, ...]) -> dict[str, object]:
    """Build the body of find_nearby_facts: each fact with its distance in whole metres, nearest first."""
    return {"facts": [{"fact": build_fact_body(item.view), "distance_m": item.distance_m} for item in nearby]}


def build_flagged_fact_body(item: FlaggedFactView) -> dict[str, object]:
    """Build the moderator item of a flagged fact: the fact, the day of its first flag and whether it is hidden, nothing about who flagged it."""
    return {"fact": build_fact_body(item.view), "flagged_on": build_day(item.flagged_on), "is_hidden": item.is_hidden}


def build_flagged_facts_body(items: tuple[FlaggedFactView, ...]) -> dict[str, object]:
    """Build the body of list_flagged_facts in the order of the service, the latest flag first."""
    return {"facts": [build_flagged_fact_body(item) for item in items]}
