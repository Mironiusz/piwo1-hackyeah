"""Fetch the static GTFS feeds of ZTP Kraków over HTTPS, one file per feed, without following a redirect or retrying."""

from collections.abc import Mapping
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path
from types import MappingProxyType

import httpx

from common_time import Deadline, DeadlineExpiredError, build_business_day, fetch_monotonic_seconds, resolve_remaining_milliseconds

GTFS_FEED_URLS: Mapping[str, str] = MappingProxyType(
    {
        "GTFS_KRK_T": "https://gtfs.ztp.krakow.pl/GTFS_KRK_T.zip",
        "GTFS_KRK_A": "https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip",
        "GTFS_KRK_M": "https://gtfs.ztp.krakow.pl/GTFS_KRK_M.zip",
    }
)
GTFS_FEEDS = tuple(GTFS_FEED_URLS)
GTFS_REQUEST_TIMEOUT_SECONDS = 30.0


class GtfsSourceError(ValueError):
    """Describe a feed that could not be fetched completely together with the day it was published."""


def build_gtfs_http_client() -> httpx.Client:
    """Create the client of the GTFS step: TLS verification, 30-second connection and inactivity limits, no redirect and no proxy from the environment."""
    return httpx.Client(timeout=httpx.Timeout(GTFS_REQUEST_TIMEOUT_SECONDS), follow_redirects=False, trust_env=False, headers={"Accept-Encoding": "identity"})


def build_gtfs_published_day(last_modified: str | None) -> date:
    """
    Turn the Last-Modified header of a feed into the calendar day it was published in the business zone.

    A missing header, an unreadable one and one without a zone are refused. Only the parsing is guarded, so a failure
    of the configuration that gives the zone is never reported as a header problem.
    """
    if last_modified is None:
        raise GtfsSourceError("GTFS feed has no valid Last-Modified header")
    try:
        instant = parsedate_to_datetime(last_modified)
    except (TypeError, ValueError):
        raise GtfsSourceError("GTFS feed has no valid Last-Modified header") from None
    if instant.utcoffset() is None:
        raise GtfsSourceError("GTFS feed has no valid Last-Modified header")
    return build_business_day(instant)


def fetch_gtfs_feed(client: httpx.Client, feed: str, target: Path, deadline: Deadline) -> date:
    """
    Stream one feed into a new file and return the day it was published.

    Only a 200 response with a valid Last-Modified header and a nonempty body of its declared length is accepted. A
    redirect, another status and every transport failure are refused with GtfsSourceError and nothing is retried,
    because the next manual run is the retry. The run deadline is checked before the request and between chunks.
    """
    if feed not in GTFS_FEED_URLS:
        raise GtfsSourceError("Unknown GTFS feed")
    size = 0
    try:
        resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
        with client.stream("GET", GTFS_FEED_URLS[feed]) as response:
            if response.status_code != 200:
                raise GtfsSourceError("GTFS feed request failed")
            published_on = build_gtfs_published_day(response.headers.get("last-modified"))
            with target.open("xb") as output:
                for chunk in response.iter_bytes():
                    resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
                    output.write(chunk)
                    size += len(chunk)
            if not size:
                raise GtfsSourceError("GTFS feed is empty")
            expected_size = response.headers.get("content-length")
            if expected_size is not None and (not expected_size.isdecimal() or int(expected_size) != size):
                raise GtfsSourceError("GTFS feed length mismatch")
    except DeadlineExpiredError:
        raise
    except (httpx.HTTPError, OSError) as error:
        raise GtfsSourceError("Cannot download GTFS feed") from error
    return published_on
