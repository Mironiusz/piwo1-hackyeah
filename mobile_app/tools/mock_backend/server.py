"""
Mock of the host of the project for EnableMe, standard library only: the programming interface and the map.

The documents of the project decide one host that serves the programming interface of
`docs/product/api_contract.md` under `/api` and one PMTiles archive of Kraków read by every client in byte ranges
(piwo1-hackyeah, `plans_finished/frontend_stack/` D-3 and D-5, `docs/standards/standard_frontend.md`). This server
stands in for that host during development, so the HarmonyOS app talks to it the way it will to the hosted demo.

  /api/...                    the sixteen operations of the contract, in memory (`api_mock.py`)
  GET /<archive file name>    the archive, with byte ranges (Range header, 206 Partial Content), also HEAD
  GET /health                 "ok"

Usage: python3 tools/mock_backend/server.py [--archive tiles/krakow.pmtiles] [--port 8090] [--host 0.0.0.0]
The emulator reaches the computer running this server at http://10.0.2.2:<port>; the address to put into
`tiles_url` of `rawfile/config/api.json` is printed at start.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api_mock import Api, ApiError, Network, Store
from pmtiles_mvt import PMTilesReader

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RANGE_RE = re.compile(r"^bytes=(\d*)-(\d*)$")
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class Handler(BaseHTTPRequestHandler):
    archive = ""
    size = 0
    name = ""
    api = None
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        if not self.path.startswith("/api"):
            sys.stderr.write("%s %s %s\n" % (self.command, self.path.split("?", 1)[0], self.headers.get("Range", "")))

    def _api(self):
        """One operation of the contract; the log line carries only the operation, status, duration and request id."""
        started = time.monotonic()
        rid = self.headers.get("X-Request-Id", "")
        if not REQUEST_ID_RE.match(rid):
            rid = uuid.uuid4().hex
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length > 0 else b""
        hint = hashlib.sha256(("%s|%s" % (self.client_address[0], self.headers.get("User-Agent", ""))).encode()).hexdigest()
        op = "unknown"
        try:
            op, status, body, extra = Handler.api.handle(self.command, self.path.split("?", 1)[0], self.headers, raw, hint)
        except ApiError as e:
            op = getattr(e, "op", op)
            status, extra = e.status, dict(e.headers)
            err = {"code": e.code}
            err.update(e.extra)
            body = {"error": err}
        except Exception:
            import traceback
            traceback.print_exc()
            status, extra, body = 500, {}, {"error": {"code": "internal_error"}}
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Request-Id", rid)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Expose-Headers", "Session-Token, X-Request-Id")
        for k, v in extra.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)
        sys.stderr.write("api %s %d %.0fms %s\n" % (op, status, (time.monotonic() - started) * 1000, rid))

    def _is_api(self):
        path = self.path.split("?", 1)[0]
        return path == "/api" or path.startswith("/api/")

    def do_POST(self):
        if self._is_api():
            return self._api()
        return self._send(404, b"not found", "text/plain")

    def do_DELETE(self):
        self.do_POST()

    def do_PUT(self):
        self.do_POST()

    def do_PATCH(self):
        self.do_POST()

    def _send(self, status, body, ctype, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Expose-Headers", "Content-Range, Content-Length, Accept-Ranges")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Range, Authorization, Content-Type, X-Request-Id")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, HEAD, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if self._is_api():
            return self._api()
        if path == "/health":
            return self._send(200, b"ok", "text/plain")
        if path == "/" + Handler.name:
            return self._archive()
        return self._send(404, b"not found", "text/plain")

    def _archive(self):
        size = Handler.size
        rng = self.headers.get("Range")
        if rng is None:
            with open(Handler.archive, "rb") as f:
                return self._send(200, f.read(), "application/octet-stream", {"Accept-Ranges": "bytes"})
        m = RANGE_RE.match(rng.strip())
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return self._send(416, b"", "application/octet-stream", {"Content-Range": "bytes */%d" % size})
        if m.group(1) == "":
            start = max(0, size - int(m.group(2)))
            end = size - 1
        else:
            start = int(m.group(1))
            end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
        if start > end or start >= size:
            return self._send(416, b"", "application/octet-stream", {"Content-Range": "bytes */%d" % size})
        with open(Handler.archive, "rb") as f:
            f.seek(start)
            body = f.read(end - start + 1)
        return self._send(206, body, "application/octet-stream",
                          {"Accept-Ranges": "bytes", "Content-Range": "bytes %d-%d/%d" % (start, end, size)})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", default="")
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--facts", type=int, default=6000, help="number of sample facts placed on the network")
    ap.add_argument("--seed", type=int, default=20261004, help="seed of the sample facts")
    ap.add_argument("--moderator-password", default="moderator",
                    help="password of the account `moderator`, the only one with the moderator role")
    a = ap.parse_args()
    path = a.archive
    if not path:
        for cand in ("tiles/krakow.pmtiles", "tiles/sample.pmtiles"):
            full = os.path.join(ROOT, cand)
            if os.path.exists(full):
                path = full
                break
    if not path or not os.path.exists(path):
        sys.exit("No tile archive. Run `make tiles` (Kraków, needs internet) or `make tiles-sample` first.")
    reader = PMTilesReader(path)
    build_file = path + ".build"
    osm_copy = None
    if os.path.exists(build_file):
        b = open(build_file, encoding="utf-8").read().strip()
        if re.match(r"^\d{8}$", b):
            osm_copy = "%s-%s-%s" % (b[:4], b[4:6], b[6:])
    started = time.monotonic()
    network = Network.build(path)
    Handler.api = Api(Store(network, osm_copy, a.moderator_password, a.facts, a.seed))
    print("Network: %d nodes, %d stretches, %d sample facts (%.1f s)" % (len(network.nodes), len(network.edges),
                                                                         len(Handler.api.s.facts),
                                                                         time.monotonic() - started))
    Handler.archive = path
    Handler.size = os.path.getsize(path)
    Handler.name = os.path.basename(path)
    print("Serving %s (%.1f MB, zoom %d-%d) on http://%s:%d/%s" % (path, Handler.size / 1e6, reader.min_zoom,
                                                                    reader.max_zoom, a.host, a.port, Handler.name))
    print("For the emulator, rawfile/config/api.json: base_url http://10.0.2.2:%d, tiles_url http://10.0.2.2:%d/%s"
          % (a.port, a.port, Handler.name))
    print("Moderator account: pseudonym moderator, password given by --moderator-password")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
