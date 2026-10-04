"""Check the one call to the public Nominatim instance and the reading of its answers through an invented transport, without a network."""

import asyncio
import functools
import json
import time

import httpx
import pytest

from data import nominatim
from data.nominatim import NOMINATIM_SEARCH_PARAMETERS, NOMINATIM_SEARCH_URL, NOMINATIM_USER_AGENT, NominatimPlace, NominatimRequestError, build_nominatim_client, fetch_nominatim_places
from tests.common_nominatim_answers import RECORDED_ANSWERS

SEARCHED_TEXT = "Tauron Arena"


def apply_invented_instance(monkeypatch: pytest.MonkeyPatch, answer) -> list[httpx.Request]:
    """Serve every search from an invented handler through the real client and record the requests it receives."""
    requests: list[httpx.Request] = []

    def apply_recorded_request(request: httpx.Request):
        """Record the request and give the invented answer, which may be awaited."""
        requests.append(request)
        return answer(request)

    monkeypatch.setattr(nominatim, "build_nominatim_client", functools.partial(build_nominatim_client, httpx.MockTransport(apply_recorded_request)))
    return requests


def fetch_failure(monkeypatch: pytest.MonkeyPatch, answer) -> NominatimRequestError:
    """Run one search that has to fail and give its error, checking that its message names neither the text nor the address of the request."""
    apply_invented_instance(monkeypatch, answer)
    with pytest.raises(NominatimRequestError) as caught:
        asyncio.run(fetch_nominatim_places(SEARCHED_TEXT))
    assert SEARCHED_TEXT not in str(caught.value)
    assert "nominatim.openstreetmap.org" not in str(caught.value)
    return caught.value


def test_request_carries_only_the_text_the_fixed_parameters_and_the_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    """The search is one GET of the search address with q first, the seven fixed parameters, the User-Agent and nothing of a person."""
    requests = apply_invented_instance(monkeypatch, lambda request: httpx.Response(200, json=[]))
    assert asyncio.run(fetch_nominatim_places(SEARCHED_TEXT)) == []
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "GET"
    assert str(request.url.copy_with(query=None)) == NOMINATIM_SEARCH_URL
    assert list(request.url.params.multi_items()) == [("q", SEARCHED_TEXT), *NOMINATIM_SEARCH_PARAMETERS.items()]
    assert sorted(request.headers.keys()) == ["accept", "accept-encoding", "connection", "host", "user-agent"]
    assert request.headers["user-agent"] == NOMINATIM_USER_AGENT


@pytest.mark.parametrize("text", RECORDED_ANSWERS)
def test_each_recorded_answer_is_read_in_the_order_of_the_service(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """Every recorded answer becomes one place per result, in the order received."""
    apply_invented_instance(monkeypatch, lambda request: httpx.Response(200, json=RECORDED_ANSWERS[text]))
    places = asyncio.run(fetch_nominatim_places(text))
    assert [(place.lat, place.lon) for place in places] == [(float(item["lat"]), float(item["lon"])) for item in RECORDED_ANSWERS[text]]


def test_recorded_places_keep_their_parts_and_drop_an_empty_name() -> None:
    """The arena keeps every part it has, the empty name of Florianska 1 becomes absent, and os. Strusia 23 has no road while Wieliczka has no city."""
    arena = nominatim.build_nominatim_places(json.dumps(RECORDED_ANSWERS["Tauron Arena"]).encode())[0]
    assert arena == NominatimPlace("Tauron Arena Kraków", "Stanisława Lema", "7", None, "Czyżyny", "Czyżyny", "Czyżyny", "31-571", "Kraków", 50.0677202, 19.9915490)
    assert nominatim.build_nominatim_places(json.dumps(RECORDED_ANSWERS["Florianska 1"]).encode())[0].name is None
    estate = nominatim.build_nominatim_places(json.dumps(RECORDED_ANSWERS["os. Strusia 23"]).encode())[0]
    assert (estate.road, estate.neighbourhood, estate.house_number) == (None, "Osiedle Józefa Strusia", "23")
    assert {place.city for place in nominatim.build_nominatim_places(json.dumps(RECORDED_ANSWERS["Rynek Górny, Wieliczka"]).encode())} == {None}


@pytest.mark.parametrize("status", [403, 429, 500])
def test_status_other_than_200_names_the_status(monkeypatch: pytest.MonkeyPatch, status: int) -> None:
    """A refusal, an exceeded limit and a failure of the service end as the cause status with its code."""
    error = fetch_failure(monkeypatch, lambda request: httpx.Response(status, json=[]))
    assert (error.cause, error.status) == ("status", status)


def test_connection_error_names_the_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    """A service that cannot be reached ends as the cause connection."""

    def apply_connection_refusal(request: httpx.Request) -> httpx.Response:
        """Refuse the connection."""
        raise httpx.ConnectError("Connection refused", request=request)

    assert fetch_failure(monkeypatch, apply_connection_refusal).cause == "connection"


def test_read_timeout_names_the_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """A read timeout of the client ends as the cause timeout."""

    def apply_read_timeout(request: httpx.Request) -> httpx.Response:
        """Time out while reading."""
        raise httpx.ReadTimeout("Read timed out", request=request)

    assert fetch_failure(monkeypatch, apply_read_timeout).cause == "timeout"


def test_slow_answer_ends_at_the_limit_of_the_whole_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """An answer slower than the limit of the whole call ends as the cause timeout once the limit has passed, without a retry."""
    monkeypatch.setattr(nominatim, "NOMINATIM_TIMEOUT_SECONDS", 0.05)

    async def build_late_answer(request: httpx.Request) -> httpx.Response:
        """Answer only after one second."""
        await asyncio.sleep(1)
        return httpx.Response(200, json=[])

    started = time.monotonic()
    requests = apply_invented_instance(monkeypatch, build_late_answer)
    with pytest.raises(NominatimRequestError) as caught:
        asyncio.run(fetch_nominatim_places(SEARCHED_TEXT))
    assert caught.value.cause == "timeout"
    assert time.monotonic() - started < 0.5
    assert len(requests) == 1


@pytest.mark.parametrize(
    "body",
    [
        b"<html>",
        b"{}",
        b"[1]",
        b'[{"name": "Invented", "lon": "19.9", "address": {"city": "Krak\\u00f3w"}}]',
        b'[{"name": "Invented", "lat": "nan", "lon": "19.9", "address": {"city": "Krak\\u00f3w"}}]',
        b'[{"name": "Invented", "lat": 50.06, "lon": "19.9", "address": {"city": "Krak\\u00f3w"}}]',
        b'[{"name": "Invented", "lat": "50.06", "lon": "19.9"}]',
        b'[{"name": "Invented", "lat": "50.06", "lon": "19.9", "address": "Krak\\u00f3w"}]',
    ],
)
def test_body_that_is_not_the_expected_list_names_the_invalid_body(monkeypatch: pytest.MonkeyPatch, body: bytes) -> None:
    """A body that is not JSON, not a list, or holds a result without a finite coordinate string or without an address object ends as the cause invalid_body."""
    assert fetch_failure(monkeypatch, lambda request: httpx.Response(200, content=body)).cause == "invalid_body"
