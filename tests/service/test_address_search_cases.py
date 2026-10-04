"""Check the preparation of the text, the label, the filter of Kraków, the memory of answers, the gate and the order of one search, without a network."""

import asyncio
import json

import pytest

from data.nominatim import NominatimPlace, NominatimRequestError, build_nominatim_places
from service import address_search
from service.address_search import (
    CACHE_MAX_ENTRIES,
    CACHE_TIME_TO_LIVE_SECONDS,
    AddressSearchUnavailableError,
    AddressSuggestion,
    InvalidSearchTextError,
    SearchCache,
    SearchGate,
    build_address_label,
    build_address_suggestions,
    fetch_address_suggestions,
    resolve_search_text,
)
from tests.common_nominatim_answers import RECORDED_ANSWERS


def fetch_recorded_places(text: str) -> list[NominatimPlace]:
    """Read the recorded answer of a text into places, as the data layer does."""
    return build_nominatim_places(json.dumps(RECORDED_ANSWERS[text]).encode())


def build_invented_place(**parts: str) -> NominatimPlace:
    """Build an invented place in Kraków with only the given parts present."""
    texts = {name: parts.get(name) for name in ("name", "road", "house_number", "neighbourhood", "quarter", "suburb", "city_district", "postcode")}
    return NominatimPlace(**texts, city="Kraków", lat=50.06, lon=19.94)


class InventedSearch:
    """Stand in for the public instance, the clock and the wait of one process, recording what the search asked for."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, answers: dict[str, list[NominatimPlace] | NominatimRequestError]) -> None:
        """Install a fresh memory, a fresh gate, a clock stopped at 1000 seconds and invented answers keyed by the prepared text."""
        self.answers = answers
        self.texts: list[str] = []
        self.waits: list[float] = []
        self.now = 1000.0
        monkeypatch.setattr(address_search, "SEARCH_CACHE", SearchCache())
        monkeypatch.setattr(address_search, "SEARCH_GATE", SearchGate())
        monkeypatch.setattr(address_search, "fetch_nominatim_places", self.fetch_places)
        monkeypatch.setattr(address_search, "fetch_monotonic_seconds", lambda: self.now)
        monkeypatch.setattr(address_search, "sleep", self.apply_wait)

    async def fetch_places(self, text: str) -> list[NominatimPlace]:
        """Record the text sent out and give its invented answer or raise its invented failure."""
        self.texts.append(text)
        answer = self.answers[text]
        if isinstance(answer, NominatimRequestError):
            raise answer
        return answer

    async def apply_wait(self, seconds: float) -> None:
        """Record the wait instead of waiting."""
        self.waits.append(seconds)


@pytest.mark.parametrize(
    ("text", "prepared"),
    [
        (" Tauron Arena ", "Tauron Arena"),
        ("Tauron \t\n  Arena", "Tauron Arena"),
        ("ul. Lipska 5", "Lipska 5"),
        ("UL. Lipska 5", "Lipska 5"),
        ("Ulica Lipska 5", "Lipska 5"),
        ("ul.Lipska 5", "ul.Lipska 5"),
        ("al. Pokoju 7", "al. Pokoju 7"),
        ("ą" * 200, "ą" * 200),
    ],
)
def test_text_is_trimmed_collapsed_and_loses_only_the_street_words(text: str, prepared: str) -> None:
    """Only whitespace and the standalone words ul. and ulica change, and 200 characters are still accepted."""
    assert resolve_search_text(text) == prepared


@pytest.mark.parametrize("text", ["a" * 201, " ul. ", "", "  ulica  UL. "])
def test_text_too_long_or_empty_once_prepared_is_refused(text: str) -> None:
    """More than 200 characters as received, or nothing left once prepared, is an invalid search text."""
    with pytest.raises(InvalidSearchTextError):
        resolve_search_text(text)


@pytest.mark.parametrize(
    ("text", "label"),
    [
        ("Tauron Arena", "Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków"),
        ("Florianska 1", "Floriańska 1, Stare Miasto, 31-019 Kraków"),
        ("Lipska 5", "Lipska, Płaszów, 30-721 Kraków"),
        ("os. Strusia 23", "Biedronka, Osiedle Józefa Strusia 23, Bieńczyce, 31-810 Kraków"),
    ],
)
def test_label_of_the_first_recorded_place(text: str, label: str) -> None:
    """The name differs from the street, the street or the estate carries the number, then the district and the postcode with Kraków."""
    assert build_address_label(fetch_recorded_places(text)[0]) == label


def test_label_parts_that_are_missing_shorten_it() -> None:
    """Without a postcode the label ends with Kraków alone, the district falls back to suburb and city_district, and a name equal to the estate stays."""
    assert build_address_label(build_invented_place(road="Invented", quarter="Invented quarter")) == "Invented, Invented quarter, Kraków"
    assert build_address_label(build_invented_place(road="Invented", suburb="Invented suburb", city_district="Invented district")) == "Invented, Invented suburb, Kraków"
    assert build_address_label(build_invented_place(road="Invented", city_district="Invented district", postcode="30-001")) == "Invented, Invented district, 30-001 Kraków"
    assert build_address_label(build_invented_place(name="Osiedle Invented", neighbourhood="Osiedle Invented", house_number="1")) == "Osiedle Invented, Osiedle Invented 1, Kraków"


def test_suggestions_keep_krakow_and_the_first_of_each_label() -> None:
    """The arena keeps 9 of 10 results, Lipska 5 keeps 7 of 9 in the order of the first of each label, and Wieliczka keeps none."""
    arena = build_address_suggestions(fetch_recorded_places("Tauron Arena"))
    assert len(arena) == 9
    assert arena[0] == AddressSuggestion("Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków", 50.0677202, 19.9915490)
    assert arena[1] == AddressSuggestion("TAURON Arena Kraków Wieczysta 02, Mogilska, Rakowice, 31-443 Kraków", 50.0709433, 19.9825992)
    assert len({item.label for item in arena}) == 9
    assert [item.label for item in build_address_suggestions(fetch_recorded_places("Lipska 5"))] == [
        "Lipska, Płaszów, 30-721 Kraków",
        "Lipska, Płaszów, 30-724 Kraków",
        "Lipska, Płaszów, 30-716 Kraków",
        "Lipska, Płaszów, 30-733 Kraków",
        "Lipska, Płaszów, 30-725 Kraków",
        "Lipska, Płaszów, 30-720 Kraków",
        "Lipska, Rybitwy, 30-716 Kraków",
    ]
    assert build_address_suggestions(fetch_recorded_places("Rynek Górny, Wieliczka")) == ()


def test_cache_keeps_an_answer_for_less_than_24_hours() -> None:
    """A kept answer, an empty one included, is found until 24 hours have passed and is removed when they have."""
    cache = SearchCache()
    assert cache.fetch_suggestions("tauron arena", 0.0) is None
    cache.apply_suggestions("qwxzvbn", (), 10.0)
    assert cache.fetch_suggestions("qwxzvbn", 10.0 + CACHE_TIME_TO_LIVE_SECONDS - 0.001) == ()
    assert cache.fetch_suggestions("qwxzvbn", 10.0 + CACHE_TIME_TO_LIVE_SECONDS) is None
    assert "qwxzvbn" not in cache.entries


def test_cache_drops_the_oldest_beyond_1000_entries() -> None:
    """The 1001st answer drops the oldest one and keeps the rest."""
    cache = SearchCache()
    for index in range(CACHE_MAX_ENTRIES + 1):
        cache.apply_suggestions(str(index), (), float(index))
    assert len(cache.entries) == CACHE_MAX_ENTRIES
    assert cache.fetch_suggestions("0", 2000.0) is None
    assert cache.fetch_suggestions("1", 2000.0) == ()


def test_gate_gives_turns_1_1_seconds_apart_within_3_seconds() -> None:
    """Five searches at one instant wait 0, 1.1 and 2.2 seconds, the last two get no turn, and a turn is free again once the time has passed."""
    gate = SearchGate()
    waits = [gate.resolve_wait_seconds(100.0) for _ in range(5)]
    assert waits[:3] == pytest.approx([0.0, 1.1, 2.2])
    assert waits[3:] == [None, None]
    assert gate.resolve_wait_seconds(104.0) == 0.0


def test_repeated_search_in_any_letter_case_asks_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """TAURON ARENA after Tauron Arena, and Qwxzvbn twice with nothing found, each reach the public instance once."""
    search = InventedSearch(monkeypatch, {"Tauron Arena": fetch_recorded_places("Tauron Arena"), "Qwxzvbn": []})
    first = asyncio.run(fetch_address_suggestions("Tauron Arena"))
    assert asyncio.run(fetch_address_suggestions("TAURON ARENA")) == first
    assert asyncio.run(fetch_address_suggestions("Qwxzvbn")) == ()
    assert asyncio.run(fetch_address_suggestions("Qwxzvbn")) == ()
    assert search.texts == ["Tauron Arena", "Qwxzvbn"]


def test_prepared_text_is_sent_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """ul. Lipska 5 reaches the public instance as Lipska 5."""
    search = InventedSearch(monkeypatch, {"Lipska 5": fetch_recorded_places("Lipska 5")})
    assert len(asyncio.run(fetch_address_suggestions("ul. Lipska 5"))) == 7
    assert search.texts == ["Lipska 5"]


@pytest.mark.parametrize("failure", [NominatimRequestError("timeout"), NominatimRequestError("connection"), NominatimRequestError("status", 429), NominatimRequestError("invalid_body")])
def test_failure_is_unavailable_and_not_kept(monkeypatch: pytest.MonkeyPatch, failure: NominatimRequestError) -> None:
    """Every cause of a failed call ends as unavailable, and the next search for the same text asks again."""
    search = InventedSearch(monkeypatch, {"Tauron Arena": failure})
    for _ in range(2):
        with pytest.raises(AddressSearchUnavailableError):
            asyncio.run(fetch_address_suggestions("Tauron Arena"))
    assert search.texts == ["Tauron Arena", "Tauron Arena"]


def test_burst_on_a_cold_cache_gets_three_turns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Five different texts at one instant reach the public instance three times, 1.1 seconds apart, and the other two are unavailable."""
    texts = ["Invented one", "Invented two", "Invented three", "Invented four", "Invented five"]
    search = InventedSearch(monkeypatch, {text: [] for text in texts})

    async def fetch_all() -> list[object]:
        """Start the five searches together."""
        return await asyncio.gather(*(fetch_address_suggestions(text) for text in texts), return_exceptions=True)

    outcomes = asyncio.run(fetch_all())
    assert outcomes[:3] == [(), (), ()]
    assert [type(outcome) for outcome in outcomes[3:]] == [AddressSearchUnavailableError, AddressSearchUnavailableError]
    assert search.texts == texts[:3]
    assert search.waits == pytest.approx([0.0, 1.1, 2.2])


def test_invalid_text_asks_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """A refused text takes no turn, keeps nothing and sends nothing out."""
    search = InventedSearch(monkeypatch, {})
    with pytest.raises(InvalidSearchTextError):
        asyncio.run(fetch_address_suggestions(" ul. "))
    assert search.texts == []
    assert address_search.SEARCH_CACHE.entries == {}
    assert address_search.SEARCH_GATE.resolve_wait_seconds(search.now) == 0.0


def test_new_process_memory_asks_again(monkeypatch: pytest.MonkeyPatch) -> None:
    """An answer kept before the memory of the process starts again is not found afterwards."""
    search = InventedSearch(monkeypatch, {"Tauron Arena": fetch_recorded_places("Tauron Arena")})
    asyncio.run(fetch_address_suggestions("Tauron Arena"))
    monkeypatch.setattr(address_search, "SEARCH_CACHE", SearchCache())
    search.now += 10.0
    asyncio.run(fetch_address_suggestions("Tauron Arena"))
    assert search.texts == ["Tauron Arena", "Tauron Arena"]
