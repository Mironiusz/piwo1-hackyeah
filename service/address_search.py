"""Search an address or a place in Kraków: prepare the text, keep answers in the process, respect the limit of the public instance and label the places."""

from asyncio import sleep
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass

from common_time import fetch_monotonic_seconds
from config.logging import fetch_logger
from data.nominatim import NominatimPlace, NominatimRequestError, fetch_nominatim_places

SEARCH_TEXT_MAX_LENGTH = 200
REMOVED_STREET_WORDS = frozenset({"ul.", "ulica"})
KRAKOW_CITY = "Kraków"
CACHE_TIME_TO_LIVE_SECONDS = 86400.0
CACHE_MAX_ENTRIES = 1000
GATE_INTERVAL_SECONDS = 1.1
GATE_MAX_WAIT_SECONDS = 3.0


class InvalidSearchTextError(ValueError):
    """A search text the contract refuses: more than 200 characters as received, or nothing left once prepared."""


class AddressSearchUnavailableError(RuntimeError):
    """A search that cannot be answered now, because the public instance failed or the search got no turn at the gate."""


@dataclass(frozen=True)
class AddressSuggestion:
    """One match of a search: its full label and its point."""

    label: str
    lat: float
    lon: float


def resolve_search_text(text: str) -> str:
    """Prepare a search text: refuse more than 200 characters, trim it, join every run of whitespace into one space and drop the standalone words ul. and ulica in any letter case."""
    if len(text) > SEARCH_TEXT_MAX_LENGTH:
        raise InvalidSearchTextError("Search text is too long")
    prepared = " ".join(word for word in text.split() if word.casefold() not in REMOVED_STREET_WORDS)
    if not prepared:
        raise InvalidSearchTextError("Search text is empty")
    return prepared


def build_address_label(place: NominatimPlace) -> str:
    """Build the full label of a place: its name when it differs from the street, the street or the estate with the house number, the district, and the postcode with Kraków."""
    parts: list[str] = []
    if place.name is not None and place.name != place.road:
        parts.append(place.name)
    street = place.road if place.road is not None else place.neighbourhood
    if street is not None:
        parts.append(street if place.house_number is None else f"{street} {place.house_number}")
    district = next((value for value in (place.quarter, place.suburb, place.city_district) if value is not None), None)
    if district is not None:
        parts.append(district)
    parts.append(KRAKOW_CITY if place.postcode is None else f"{place.postcode} {KRAKOW_CITY}")
    return ", ".join(parts)


def build_address_suggestions(places: Sequence[NominatimPlace]) -> tuple[AddressSuggestion, ...]:
    """Keep the places in Kraków in the order of the service, label them and leave out a place whose label an earlier place already has."""
    suggestions: dict[str, AddressSuggestion] = {}
    for place in places:
        if place.city != KRAKOW_CITY:
            continue
        label = build_address_label(place)
        suggestions.setdefault(label, AddressSuggestion(label, place.lat, place.lon))
    return tuple(suggestions.values())


class SearchCache:
    """Answers of the running process keyed by the prepared text alone, without who asked, kept for 24 hours and at most 1000 of them, the oldest dropped first."""

    def __init__(self) -> None:
        """Start empty; nothing survives a restart of the process."""
        self.entries: OrderedDict[str, tuple[float, tuple[AddressSuggestion, ...]]] = OrderedDict()

    def fetch_suggestions(self, key: str, now: float) -> tuple[AddressSuggestion, ...] | None:
        """Give the kept answer of a key, or None when there is none or it has reached 24 hours, in which case it is removed."""
        entry = self.entries.get(key)
        if entry is None:
            return None
        stored_at, suggestions = entry
        if now - stored_at >= CACHE_TIME_TO_LIVE_SECONDS:
            del self.entries[key]
            return None
        return suggestions

    def apply_suggestions(self, key: str, suggestions: tuple[AddressSuggestion, ...], now: float) -> None:
        """Keep an answer as the newest entry and drop the oldest entries while more than 1000 remain."""
        self.entries[key] = (now, suggestions)
        self.entries.move_to_end(key)
        while len(self.entries) > CACHE_MAX_ENTRIES:
            self.entries.popitem(last=False)


class SearchGate:
    """The turn of the process for an outgoing search: starts at least 1.1 seconds apart, and no turn for a search that would wait more than 3 seconds."""

    def __init__(self) -> None:
        """Start with a turn free at once."""
        self.next_start_at = float("-inf")

    def resolve_wait_seconds(self, now: float) -> float | None:
        """Take the next turn and give the wait until it, or give None and take nothing when the turn is more than 3 seconds away."""
        turn = max(now, self.next_start_at)
        wait = turn - now
        if wait > GATE_MAX_WAIT_SECONDS:
            return None
        self.next_start_at = turn + GATE_INTERVAL_SECONDS
        return wait


async def fetch_address_suggestions(text: str) -> tuple[AddressSuggestion, ...]:
    """Answer a search: prepare the text, give the kept answer when there is one, otherwise wait for the turn of the process and ask the public instance once, keeping its answer and never a failure."""
    prepared = resolve_search_text(text)
    key = prepared.casefold()
    kept = SEARCH_CACHE.fetch_suggestions(key, fetch_monotonic_seconds())
    if kept is not None:
        return kept
    logger = fetch_logger(__name__)
    wait = SEARCH_GATE.resolve_wait_seconds(fetch_monotonic_seconds())
    if wait is None:
        logger.warning("Address search refused by the gate")
        raise AddressSearchUnavailableError("Address search got no turn at the gate")
    await sleep(wait)
    started = fetch_monotonic_seconds()
    try:
        places = await fetch_nominatim_places(prepared)
    except NominatimRequestError as error:
        logger.exception("Address search unavailable cause=%s status=%s elapsed_ms=%.0f", error.cause, error.status, (fetch_monotonic_seconds() - started) * 1000)
        raise AddressSearchUnavailableError("Address search is unavailable") from error
    suggestions = build_address_suggestions(places)
    SEARCH_CACHE.apply_suggestions(key, suggestions, fetch_monotonic_seconds())
    return suggestions


SEARCH_CACHE = SearchCache()
SEARCH_GATE = SearchGate()
