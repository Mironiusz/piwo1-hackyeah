#!/usr/bin/env python3
"""
Point the HarmonyOS app at an API server and check that the server answers the contract.

The app reads its server from `accessway/entry/src/main/resources/rawfile/config/api.json`, which is built into the
package, so the address is set before `make run`. The real backend (`make backend` in the repository root, the API of
`docs/product/api_contract.md`) serves only `/api/...`; the map archive is served next to it by the proxy of the demo, or
locally by `make mock` (port 8090), so `tiles_url` may point to a different host than `base_url`.

    python3 tools/api_target.py show
    python3 tools/api_target.py set --base-url http://192.168.1.20:8000 [--tiles-url http://192.168.1.20:8090/tiles/krakow.pmtiles]
    python3 tools/api_target.py emulator [--api-port 8000] [--tiles-port 8090]   # 10.0.2.2 = the computer running the emulator
    python3 tools/api_target.py device   [--api-port 8000] [--tiles-port 8090]   # LAN address of this computer, for a phone on the same Wi-Fi
    python3 tools/api_target.py offline                                           # no server, data on the device
    python3 tools/api_target.py check [--base-url URL]                            # call the read-only operations from this computer
"""

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "accessway/entry/src/main/resources/rawfile/config/api.json"
EMULATOR_HOST = "10.0.2.2"
HELP = (
    "base_url: address of the API server without /api; empty means no server, data stored on the device. "
    "tiles_url: full address of the PMTiles archive of Krakow, read in byte ranges; empty or unreachable means the sample "
    "base map bundled in the app. 10.0.2.2 is the computer that runs the emulator; a real phone needs the LAN address of "
    "the computer (make api-device) or the public address of the demo server. Set with tools/api_target.py."
)


def read_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"base_url": "", "timeout_ms": 15000, "tiles_url": ""}


def normalize_base(base_url: str) -> str:
    """The address as the app uses it: no trailing slash, no /api, with a scheme."""
    base = base_url.strip().rstrip("/")
    if base.endswith("/api"):
        base = base[: -len("/api")]
    if base and not base.startswith(("http://", "https://")):
        base = "http://" + base
    return base


def write_config(base_url: str, tiles_url: str | None) -> None:
    cfg = read_config()
    base = normalize_base(base_url)
    cfg["base_url"] = base
    if tiles_url is not None:
        cfg["tiles_url"] = tiles_url.strip()
    cfg.setdefault("timeout_ms", 15000)
    cfg["_help"] = HELP
    ordered = {k: cfg[k] for k in ("base_url", "timeout_ms", "tiles_url", "_help") if k in cfg}
    CONFIG.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"mobile_app/{CONFIG.relative_to(CONFIG.parents[6])}:")
    print(f"  base_url  = {ordered['base_url'] or '(empty: offline, data on the device)'}")
    print(f"  tiles_url = {ordered.get('tiles_url') or '(empty: sample base map in the app)'}")
    print("Rebuild and install the app to use it: make run")


def lan_address() -> str:
    """The address this computer uses towards the local network (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("192.0.2.1", 9))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def call(base: str, method: str, path: str, body: object | None) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "EnableMe-HarmonyOS/api-check"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        return 0, str(getattr(e, "reason", e))


def check(base: str) -> int:
    base = normalize_base(base)
    if not base:
        print("base_url is empty: the app works offline. Nothing to check.")
        return 0
    if EMULATOR_HOST in base:
        base = base.replace(EMULATOR_HOST, "127.0.0.1")
        print(f"(10.0.2.2 is this computer as seen from the emulator; checking {base})")
    krakow = {"south_west": {"lat": 50.055, "lon": 19.925}, "north_east": {"lat": 50.07, "lon": 19.95}}
    checks = [
        ("list_facts_in_area", "POST", "/api/facts/in-area", krakow, {(200, None)}),
        ("find_nearby_facts", "POST", "/api/facts/nearby", {"type": "stairs", "point": {"lat": 50.0614, "lon": 19.9372}}, {(200, None)}),
        ("read_fact", "GET", "/api/facts/1", None, {(200, None), (404, "fact_not_found")}),
        ("search_address", "POST", "/api/address-search", {"text": "Rynek Główny"}, {(200, None), (503, "address_search_unavailable")}),
        ("plan_route", "POST", "/api/routes", {"start": {"lat": 50.0614, "lon": 19.9372}, "destination": {"lat": 50.0540, "lon": 19.9354}, "avoid": ["stairs"], "need": []}, {(200, None), (503, "routing_unavailable")}),
        ("read_osm_copy (optional)", "GET", "/api/osm-copy", None, {(200, None), (404, "not_found")}),
    ]
    failed = 0
    for name, method, path, body, ok in checks:
        status, text = call(base, method, path, body)
        detail = ""
        code = None
        if status == 0:
            detail = f"no connection: {text}"
        else:
            try:
                parsed = json.loads(text)
                if "error" in parsed:
                    code = parsed["error"].get("code")
                    detail = f"error {code}"
                elif "facts" in parsed:
                    detail = f"{len(parsed['facts'])} facts"
                elif "matches" in parsed:
                    detail = f"{len(parsed['matches'])} matches"
                elif "route" in parsed:
                    detail = f"route {parsed['route']['length_m']} m, OSM copy {parsed.get('osm_copy_date')}"
            except ValueError:
                detail = text[:80]
        good = (status, code) in ok
        failed += 0 if good else 1
        print(f"  {'OK ' if good else 'BAD'} {status or '---'} {name:28} {detail}")
    if failed:
        print(f"{failed} operation(s) did not answer as the app expects. Is the backend running (make backend in the repository root) and listening on an address the phone can reach (API_BIND_HOST=0.0.0.0)?")
    else:
        print("The server answers the operations the app uses (503 means the routing or address service behind it is not up).")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    p = sub.add_parser("set")
    p.add_argument("--base-url", required=True)
    p.add_argument("--tiles-url")
    for name in ("emulator", "device"):
        p = sub.add_parser(name)
        p.add_argument("--api-port", type=int, default=8000)
        p.add_argument("--tiles-port", type=int, default=8090, help="port of make mock serving the map archive; 0 leaves tiles_url empty")
        p.add_argument("--host", default="", help="override the detected address")
    sub.add_parser("offline")
    p = sub.add_parser("check")
    p.add_argument("--base-url", default=None)
    a = ap.parse_args()

    if a.cmd == "show":
        print(json.dumps(read_config(), indent=2, ensure_ascii=False))
        return 0
    if a.cmd == "set":
        write_config(a.base_url, a.tiles_url)
        return 0
    if a.cmd in ("emulator", "device"):
        host = a.host or (EMULATOR_HOST if a.cmd == "emulator" else lan_address())
        tiles = f"http://{host}:{a.tiles_port}/tiles/krakow.pmtiles" if a.tiles_port else ""
        write_config(f"http://{host}:{a.api_port}", tiles)
        if a.cmd == "device":
            print(f"The phone must be on the same network as this computer ({host}), and the backend must listen on 0.0.0.0:{a.api_port} (API_BIND_HOST=0.0.0.0 in .env.local).")
        return 0
    if a.cmd == "offline":
        write_config("", None)
        return 0
    if a.cmd == "check":
        return check(a.base_url if a.base_url is not None else read_config().get("base_url", ""))
    return 2


if __name__ == "__main__":
    sys.exit(main())
