r"""
Checks the live public Nominatim instance once against the decisions of the address search of
`plans_finished/geocoding/GEOCODING_PLAN.md` D-4 - D-10, and records every response in one JSON file.

A run sends every text of `CHECK_ITEMS` once, with the request of D-5 there, no faster than one request per
1.1 seconds, and waits at most 5 seconds for each blocking operation. The first failure stops the run at once:
nothing is retried and no further text is sent, because the usage policy of the instance warns that a client
repeating queries may be blocked, and that would block the machine of the team for the rest of the hackathon.

Run it only by the decision of a person, never from a test or an automatic check of the repository. A refused
request may get the machine blocked, so after a stopped run another run waits for a person to decide again.

The command, from the root of the repository, with `<day>` the calendar day of the start of the run in
Europe/Warsaw, in the form YYYY-MM-DD:

    venv\Scripts\python.exe plans_finished\nominatim_client\attachments\nominatim_check.py plans_finished\nominatim_client\attachments\nominatim_check_<day>.json

The only argument is the path of the recording. The script refuses to start when the argument is missing, when
the file already exists or when its directory does not exist, so a recording is never overwritten.

Exit codes: 0 for a full run, in which every text got status 200 with a JSON body; 1 for a run stopped by a
failure or by Ctrl+C, with the entries received so far still recorded; 2 for a refused start, with nothing sent.

The usage policy and the privacy policy behind the check are read again by hand, outside the run, because they
are web pages, not searches:

- https://operations.osmfoundation.org/policies/nominatim/
- https://osmfoundation.org/wiki/Privacy_Policy

The recording is not covered by any formatting gate of the repository, so after a run it is scanned by hand for
the characters forbidden by `docs/standards/standard_formatting.md`.
"""

from __future__ import annotations

import http.client
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

SEARCH_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "piwo1-hackyeah (HackYeah 2026 accessibility prototype)"
FIXED_PARAMETERS: dict[str, str] = {
    "format": "jsonv2",
    "addressdetails": "1",
    "limit": "10",
    "countrycodes": "pl",
    "viewbox": "19.7922355,50.1261338,20.2173455,49.9676668",
    "bounded": "1",
    "accept-language": "pl",
}
MINIMUM_INTERVAL_SECONDS = 1.1
TIMEOUT_SECONDS = 5.0
MAXIMUM_TEXTS = 40
CHECK_ITEMS: tuple[tuple[str, str], ...] = (
    ("F-1", "Kraków"),
    ("F-2", "Tauron Arena"),
    ("F-3, F-7", "Biedronka"),
    ("F-3", "Rynek Górny, Wieliczka"),
    ("F-4", "Rynek Glowny"),
    ("F-4", "Florianska 1"),
    ("F-5", "Lema 7"),
    ("F-5", "ul. Lema 7"),
    ("F-5", "ulica Lema 7"),
    ("F-5", "ul. Lipska 5"),
    ("F-5, F-7", "Lipska 5"),
    ("F-5", "al. Pokoju 7"),
    ("F-5", "os. Strusia 23"),
    ("F-6", "Szpital Uniwersytecki, Jakubowskiego 2"),
    ("F-6", "Szpital Uniwersytecki"),
    ("F-6", "Jakubowskiego 2"),
    ("stop", "Rondo Mogilskie"),
    ("stop", "Czerwone Maki P+R"),
    ("letter case", "tauron arena"),
    ("letter case", "TAURON ARENA"),
    ("postcode", "Stanisława Lema 7, 31-571"),
    ("postcode", "31-571 Kraków"),
    ("no match", "Qwxzvbn"),
    ("typo", "Tauron Arnea"),
    ("typo", "Florjanska 1"),
)
"""
The texts of the check, each paired with the label of what it checks: a fact F-1 - F-7 of
`plans_finished/geocoding/GEOCODING_PLAN.md`, sent with the same input as on 2026-10-03, or one of the five new
cases. Every text is the name of a public place or the address of a public building, never an address tied to
a person, because the recording stays in a public repository.
"""

EXIT_FULL_RUN = 0
EXIT_STOPPED_RUN = 1
EXIT_REFUSED_START = 2


class RecordedEntry(TypedDict):
    """
    One sent request and what came back: the label and the text, the aware UTC instant it was sent, how long it
    took, the HTTP status when one arrived, the outcome in `error` (`None` for a usable answer, otherwise one of
    `http_status`, `timeout`, `connection_error` and `invalid_json`) and the parsed JSON body, kept exactly as the
    instance sent it, the `licence` of every result included, or `None` when there is no valid body.
    """

    check_item: str
    text: str
    sent_at: str
    elapsed_seconds: float
    status: int | None
    error: str | None
    body: object


def build_search_url(text: str) -> str:
    """
    Builds the address of one search: the text as it is, without any normalization, followed by the fixed
    parameters of the search decision.
    """
    query = urllib.parse.urlencode({"q": text, **FIXED_PARAMETERS})
    return f"{SEARCH_URL}?{query}"


def fetch_search_entry(check_item: str, text: str) -> RecordedEntry:
    """
    Sends one search to the instance and returns its entry for the recording.

    No failure escapes as an exception: a refusal, a timeout, a broken connection or a body that is not JSON
    is written into `error`, so that the caller records it and decides whether the run stops. A status other
    than 200 that urllib does not raise counts as `http_status` too, because only 200 is an answer the search
    can use.
    """
    request = urllib.request.Request(build_search_url(text), headers={"User-Agent": USER_AGENT})
    sent_at = datetime.now(UTC).isoformat(timespec="milliseconds")
    started = time.monotonic()
    status: int | None = None
    error: str | None = None
    body: object = None

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            raw_body = response.read()
        if status == http.client.OK:
            body = json.loads(raw_body.decode("utf-8"))
        else:
            error = "http_status"
    except urllib.error.HTTPError as http_error:
        status = http_error.code
        error = "http_status"
    except urllib.error.URLError as url_error:
        error = "timeout" if isinstance(url_error.reason, TimeoutError) else "connection_error"
    except TimeoutError:
        error = "timeout"
    except (OSError, http.client.HTTPException):
        error = "connection_error"
    except (UnicodeDecodeError, json.JSONDecodeError):
        error = "invalid_json"

    return RecordedEntry(
        check_item=check_item,
        text=text,
        sent_at=sent_at,
        elapsed_seconds=round(time.monotonic() - started, 3),
        status=status,
        error=error,
        body=body,
    )


def resolve_run_must_stop(entry: RecordedEntry) -> bool:
    """Decides whether the run stops after this entry: any outcome other than a usable answer stops it."""
    return entry["error"] is not None


def build_recording(started_at: str, finished_at: str, entries: list[RecordedEntry]) -> dict[str, object]:
    """
    Assembles the whole recording of a run: what was asked and how, when the run started and ended, and every
    entry in the order sent. The run stopped early when it did not send every text or when an entry failed.
    """
    stopped_early = len(entries) < len(CHECK_ITEMS) or any(resolve_run_must_stop(entry) for entry in entries)
    return {
        "service_url": SEARCH_URL,
        "user_agent": USER_AGENT,
        "parameters": FIXED_PARAMETERS,
        "started_at": started_at,
        "finished_at": finished_at,
        "stopped_early": stopped_early,
        "entries": entries,
    }


def apply_recording(path: Path, recording: dict[str, object]) -> None:
    """
    Writes the recording as UTF-8 JSON with LF line endings, keeping the Polish letters readable. The mode `x`
    fails when the file exists, so a recording is never overwritten, even one created after the start.
    """
    with path.open("x", encoding="utf-8", newline="\n") as recording_file:
        json.dump(recording, recording_file, ensure_ascii=False, indent=2)
        recording_file.write("\n")


def main(argv: list[str]) -> int:
    """
    Runs the check: refuses to start on a wrong argument or a list longer than the limit, then sends the texts
    one by one at the pace of the gate, prints one line per request, stops at the first failure, and writes
    the recording even when the run is stopped by a failure or by Ctrl+C.
    """
    if len(argv) != 2:
        print("Usage: nominatim_check.py <path of the recording>", file=sys.stderr)
        return EXIT_REFUSED_START

    recording_path = Path(argv[1])

    if recording_path.exists():
        print(f"Refused: the recording {recording_path} already exists.", file=sys.stderr)
        return EXIT_REFUSED_START

    if not recording_path.parent.is_dir():
        print(f"Refused: the directory {recording_path.parent} does not exist.", file=sys.stderr)
        return EXIT_REFUSED_START

    if len(CHECK_ITEMS) > MAXIMUM_TEXTS:
        print(f"Refused: {len(CHECK_ITEMS)} texts exceed the limit of {MAXIMUM_TEXTS}.", file=sys.stderr)
        return EXIT_REFUSED_START

    entries: list[RecordedEntry] = []
    started_at = datetime.now(UTC).isoformat(timespec="milliseconds")
    previous_start: float | None = None
    exit_code = EXIT_FULL_RUN

    try:
        for number, (check_item, text) in enumerate(CHECK_ITEMS, start=1):
            if previous_start is not None:
                time.sleep(max(0.0, previous_start + MINIMUM_INTERVAL_SECONDS - time.monotonic()))
            previous_start = time.monotonic()
            entry = fetch_search_entry(check_item, text)
            entries.append(entry)
            print(f"{number:>2}. {check_item}: {entry['error'] or entry['status']} in {entry['elapsed_seconds']:.3f} s")
            if resolve_run_must_stop(entry):
                exit_code = EXIT_STOPPED_RUN
                break
    except KeyboardInterrupt:
        print("Stopped by Ctrl+C.", file=sys.stderr)
        exit_code = EXIT_STOPPED_RUN
    finally:
        finished_at = datetime.now(UTC).isoformat(timespec="milliseconds")
        apply_recording(recording_path, build_recording(started_at, finished_at, entries))

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
