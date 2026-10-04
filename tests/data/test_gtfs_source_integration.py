"""Check the fetch of one GTFS feed with an HTTPX mock transport and invented bytes: the day it was published and every refusal."""

from datetime import date

import httpx
import pytest

from common_time import Deadline, DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from config.settings import ConfigurationError
from data.gtfs_source import GtfsSourceError, build_gtfs_http_client, fetch_gtfs_feed
from tests.common_runtime_settings import apply_invented_runtime_settings

pytestmark = pytest.mark.integration

LAST_MODIFIED = "Thu, 01 Oct 2026 22:59:31 GMT"


@pytest.fixture(autouse=True)
def runtime_settings(monkeypatch):
    """Load invented settings, because the day of a feed is read in the business zone of the configuration."""
    with apply_invented_runtime_settings(monkeypatch):
        yield


def build_test_deadline() -> Deadline:
    """Give a fetch a budget no invented response can exhaust."""
    return build_deadline(60, fetch_monotonic_seconds())


def test_client_has_explicit_limits_and_follows_no_redirect():
    with build_gtfs_http_client() as client:
        assert client.timeout.connect == client.timeout.read == 30
        assert not client.follow_redirects


def test_a_feed_modified_late_on_1_october_gmt_was_published_on_2_october_in_warsaw(tmp_path):
    requests = []

    def respond(request):
        requests.append(str(request.url))
        return httpx.Response(200, headers={"Last-Modified": LAST_MODIFIED}, content=b"invented feed")

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert fetch_gtfs_feed(client, "GTFS_KRK_T", tmp_path / "GTFS_KRK_T.zip", build_test_deadline()) == date(2026, 10, 2)
    assert (tmp_path / "GTFS_KRK_T.zip").read_bytes() == b"invented feed"
    assert requests == ["https://gtfs.ztp.krakow.pl/GTFS_KRK_T.zip"]


def apply_complete_answer(request: httpx.Request) -> httpx.Response:
    """Stand in for the server answering one complete feed."""
    return httpx.Response(200, headers={"Last-Modified": LAST_MODIFIED}, content=b"invented feed")


def apply_timeout(request: httpx.Request) -> httpx.Response:
    """Stand in for a server that does not answer within the read limit."""
    raise httpx.ReadTimeout("invented timeout", request=request)


@pytest.mark.parametrize(
    "respond",
    [
        pytest.param(lambda request: httpx.Response(200, content=b"invented feed"), id="missing_last_modified"),
        pytest.param(lambda request: httpx.Response(200, headers={"Last-Modified": "yesterday"}, content=b"invented feed"), id="unreadable_last_modified"),
        pytest.param(lambda request: httpx.Response(200, headers={"Last-Modified": "Thu, 01 Oct 2026 22:59:31 -0000"}, content=b"invented feed"), id="last_modified_without_zone"),
        pytest.param(lambda request: httpx.Response(404, headers={"Last-Modified": LAST_MODIFIED}), id="status_404"),
        pytest.param(lambda request: httpx.Response(302, headers={"Location": "https://invented.invalid/feed.zip", "Last-Modified": LAST_MODIFIED}), id="redirect"),
        pytest.param(lambda request: httpx.Response(200, headers={"Last-Modified": LAST_MODIFIED}, content=b""), id="empty_body"),
        pytest.param(apply_timeout, id="timeout"),
    ],
)
def test_a_feed_without_a_complete_answer_is_refused(tmp_path, respond):
    with httpx.Client(transport=httpx.MockTransport(respond)) as client, pytest.raises(GtfsSourceError):
        fetch_gtfs_feed(client, "GTFS_KRK_A", tmp_path / "GTFS_KRK_A.zip", build_test_deadline())


def test_a_configuration_failure_is_not_reported_as_a_header_problem(tmp_path, monkeypatch):
    def build_failed_day(instant):
        raise ConfigurationError("Missing or invalid configuration: BUSINESS_TIMEZONE (.env.local)")

    monkeypatch.setattr("data.gtfs_source.build_business_day", build_failed_day)
    with httpx.Client(transport=httpx.MockTransport(apply_complete_answer)) as client, pytest.raises(ConfigurationError):
        fetch_gtfs_feed(client, "GTFS_KRK_T", tmp_path / "GTFS_KRK_T.zip", build_test_deadline())


def test_an_unknown_feed_is_refused_before_any_request(tmp_path):
    with httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail("no request expected"))) as client, pytest.raises(GtfsSourceError):
        fetch_gtfs_feed(client, "GTFS_KRK_X", tmp_path / "GTFS_KRK_X.zip", build_test_deadline())


def test_a_spent_run_deadline_stops_the_fetch_before_any_request(tmp_path):
    with httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail("no request expected"))) as client, pytest.raises(DeadlineExpiredError):
        fetch_gtfs_feed(client, "GTFS_KRK_M", tmp_path / "GTFS_KRK_M.zip", Deadline(fetch_monotonic_seconds() - 1))
