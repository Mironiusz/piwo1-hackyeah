"""
Mock backend for the map tiles of AccessWay, standard library only.

Serves one PMTiles archive of Kraków (`make tiles`) or the sample archive (`make tiles-sample`):

  GET /tiles/info.json             bounds, zoom range, attribution and the build the archive was cut from
  GET /tiles/{z}/{x}/{y}.json      one tile ready to draw for the HarmonyOS app: geometry by render class,
                                   simplified and in integer tile pixels (see Tiles.tile_json)
  GET /tiles/krakow.pmtiles        the archive itself with byte ranges (Range header), for MapLibre in the web app
  GET /health                      "ok"

Usage: python3 tools/mock_backend/server.py [--archive tiles/krakow.pmtiles] [--port 8090] [--host 0.0.0.0]
The emulator reaches the computer running this server at http://10.0.2.2:<port>.
"""

import argparse
import functools
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pmtiles_mvt import PMTilesReader, decode_mvt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TILE_RE = re.compile(r"^/tiles/(\d+)/(\d+)/(\d+)\.json$")
OUT_EXTENT = 512
GREEN_KINDS = frozenset(("park", "grass", "garden", "forest", "wood", "nature_reserve", "cemetery",
                         "recreation_ground", "pitch", "playground", "golf_course", "meadow", "allotments",
                         "village_green", "grassland", "scrub", "orchard", "zoo"))
FILL_CLASSES = ("green", "water", "building")
LINE_CLASSES = ("path", "minor", "major")


def prop_kind(props):
    return str(props.get("kind") or props.get("pmap:kind") or "")


def prop_name(props):
    return str(props.get("name:pl") or props.get("name") or "")


def classify(layer, ftype, kind, z):
    """Render class of one feature at zoom z, or None when the app does not draw it at that zoom."""
    if ftype == 3:
        if layer == "landcover" or (layer == "landuse" and kind in GREEN_KINDS):
            return "green"
        if layer == "water":
            return "water"
        if layer == "buildings" and z >= 14:
            return "building"
        return None
    if ftype == 2 and layer == "roads":
        if kind in ("major_road", "highway"):
            return "major"
        if kind == "minor_road" and z >= 13:
            return "minor"
        if kind in ("path", "other") and z >= 14:
            return "path"
    return None


def simplify(pts, tol):
    """Douglas-Peucker on a list of (x, y), iterative, keeps the first and the last point."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    tol2 = tol * tol
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        best, idx = tol2, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if den == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = ((px - ax) * dx + (py - ay) * dy) / den
                t = 0 if t < 0 else (1 if t > 1 else t)
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > best:
                best, idx = d, i
        if idx >= 0:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(pts, keep) if k]


def compact(part, extent, closed):
    """One part simplified to about one screen pixel and quantized to OUT_EXTENT, flat [x, y, ...] or None."""
    scale = OUT_EXTENT / extent
    pts = simplify(part, 0.7 / scale)
    flat = []
    lx = ly = None
    xs, ys = [], []
    for px, py in pts:
        qx, qy = int(round(px * scale)), int(round(py * scale))
        if qx == lx and qy == ly:
            continue
        flat.append(qx)
        flat.append(qy)
        xs.append(qx)
        ys.append(qy)
        lx, ly = qx, qy
    if closed:
        if len(xs) < 3 or (max(xs) - min(xs)) * (max(ys) - min(ys)) < 2:
            return None
    elif len(xs) < 2 or (max(xs) - min(xs)) + (max(ys) - min(ys)) < 2:
        return None
    return flat


class Tiles:
    def __init__(self, path):
        self.path = path
        self.reader = PMTilesReader(path)
        self.size = os.path.getsize(path)
        meta = self.reader.metadata()
        build = ""
        side = path + ".build"
        if os.path.exists(side):
            with open(side, encoding="utf-8") as f:
                build = f.read().strip()
        self.info = {
            "min_zoom": self.reader.min_zoom,
            "max_zoom": self.reader.max_zoom,
            "bounds": [self.reader.min_lon, self.reader.min_lat, self.reader.max_lon, self.reader.max_lat],
            "center": [self.reader.center_lon, self.reader.center_lat, self.reader.center_zoom],
            "attribution": meta.get("attribution") or "© OpenStreetMap contributors",
            "build": build or meta.get("accessway_build", ""),
            "archive_bytes": self.size,
            "tile_format": "render-v2",
        }

    @functools.lru_cache(maxsize=1024)
    def tile_json(self, z, x, y):
        """
        One tile ready to draw: geometry grouped by render class, simplified to about one pixel of a tile drawn
        512 px wide and stored as integer tile pixels 0..512 (the app maps them to the screen with one scale
        and offset per tile). Classes the app does not draw at this zoom are left out.
        """
        fills = {k: [] for k in FILL_CLASSES}
        lines = {k: [] for k in LINE_CLASSES}
        labels = []
        data = self.reader.tile(z, x, y)
        if data is not None:
            for name, (extent, feats) in decode_mvt(data).items():
                for f in feats:
                    kind = prop_kind(f["props"])
                    cls = classify(name, f["type"], kind, z)
                    if cls is None:
                        continue
                    closed = f["type"] == 3
                    parts = [p for p in (compact(part, extent, closed) for part in f["parts"]) if p is not None]
                    if not parts:
                        continue
                    (fills if closed else lines)[cls].extend(parts)
                    label = prop_name(f["props"])
                    if not closed and label and (cls == "major" or (cls == "minor" and z >= 14)):
                        labels.append({"name": label, "geom": parts})
        body = {"z": z, "x": x, "y": y, "extent": OUT_EXTENT, "fills": fills, "lines": lines, "labels": labels}
        return json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    tiles = None

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    def _send(self, status, body, ctype, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Expose-Headers", "Content-Range, Content-Length, Accept-Ranges")
        self.send_header("Cache-Control", "public, max-age=3600")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        t = Handler.tiles
        path = self.path.split("?", 1)[0]
        if path == "/health":
            return self._send(200, b"ok", "text/plain")
        if path == "/tiles/info.json":
            return self._send(200, json.dumps(t.info).encode("utf-8"), "application/json")
        m = TILE_RE.match(path)
        if m:
            z, x, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if z > t.reader.max_zoom or x >= (1 << z) or y >= (1 << z):
                return self._send(404, b'{"error":{"code":"not_found"}}', "application/json")
            return self._send(200, t.tile_json(z, x, y), "application/json")
        if path in ("/tiles/krakow.pmtiles", "/tiles/archive.pmtiles"):
            return self._archive()
        return self._send(404, b'{"error":{"code":"not_found"}}', "application/json")

    def _archive(self):
        t = Handler.tiles
        rng = self.headers.get("Range")
        if rng is None:
            with open(t.path, "rb") as f:
                return self._send(200, f.read(), "application/octet-stream", {"Accept-Ranges": "bytes"})
        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        if not m:
            return self._send(416, b"", "application/octet-stream", {"Content-Range": "bytes */%d" % t.size})
        start_s, end_s = m.group(1), m.group(2)
        if start_s == "":
            start = max(0, t.size - int(end_s))
            end = t.size - 1
        else:
            start = int(start_s)
            end = min(int(end_s), t.size - 1) if end_s else t.size - 1
        if start > end or start >= t.size:
            return self._send(416, b"", "application/octet-stream", {"Content-Range": "bytes */%d" % t.size})
        with open(t.path, "rb") as f:
            f.seek(start)
            body = f.read(end - start + 1)
        return self._send(206, body, "application/octet-stream",
                          {"Accept-Ranges": "bytes", "Content-Range": "bytes %d-%d/%d" % (start, end, t.size)})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", default="")
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--host", default="0.0.0.0")
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
    Handler.tiles = Tiles(path)
    info = Handler.tiles.info
    print("Serving %s (%.1f MB, zoom %d-%d) on http://%s:%d" % (path, info["archive_bytes"] / 1e6, info["min_zoom"],
                                                                 info["max_zoom"], a.host, a.port))
    print("Emulator address: http://10.0.2.2:%d" % a.port)
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
