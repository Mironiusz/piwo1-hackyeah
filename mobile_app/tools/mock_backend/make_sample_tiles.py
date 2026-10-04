"""
Builds `tiles/sample.pmtiles`, a small vector tile archive of the schematic sample area around Tauron Arena,
from the same file the app routes on (`accessway/entry/src/main/resources/rawfile/data/osm_sample.json`).
The layers and kinds follow the Protomaps basemap, so the app draws it exactly like the real Kraków archive.
It is a fallback for working without internet and for tests; the demo uses `make tiles`.

Usage: python3 tools/mock_backend/make_sample_tiles.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pmtiles_mvt import encode_mvt, lonlat_to_tile, lonlat_to_tile_px, write_pmtiles

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "accessway/entry/src/main/resources/rawfile/data/osm_sample.json")
OUT = os.path.join(ROOT, "tiles/sample.pmtiles")
MIN_Z, MAX_Z = 12, 15
EXTENT = 4096

ROAD_KIND = {"motorway": "highway", "trunk": "highway", "primary": "major_road", "secondary": "major_road",
             "tertiary": "major_road", "residential": "minor_road", "living_street": "minor_road",
             "unclassified": "minor_road", "service": "minor_road", "pedestrian": "path", "footway": "path",
             "path": "path", "steps": "path", "cycleway": "path", "track": "path"}


def load():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)
    nodes = {}
    for el in data["elements"]:
        if el["type"] == "node":
            nodes[el["id"]] = (el["lon"], el["lat"])
    feats = []
    for el in data["elements"]:
        if el["type"] != "way":
            continue
        tags = el.get("tags", {})
        pts = [nodes[n] for n in el["nodes"] if n in nodes]
        if len(pts) < 2:
            continue
        if "highway" in tags:
            feats.append(("roads", 2, {"kind": ROAD_KIND.get(tags["highway"], "other"), "name": tags.get("name", "")}, pts))
        elif "building" in tags:
            feats.append(("buildings", 3, {"kind": "building"}, pts))
        elif tags.get("leisure") in ("park", "garden") or tags.get("landuse") in ("grass", "park"):
            feats.append(("landuse", 3, {"kind": "park", "name": tags.get("name", "")}, pts))
    return feats


def main():
    feats = load()
    lons = [p[0] for f in feats for p in f[3]]
    lats = [p[1] for f in feats for p in f[3]]
    bounds = (min(lons) - 0.004, min(lats) - 0.003, max(lons) + 0.004, max(lats) + 0.003)
    tiles = {}
    for z in range(MIN_Z, MAX_Z + 1):
        x0, y1 = lonlat_to_tile(z, bounds[0], bounds[1])
        x1, y0 = lonlat_to_tile(z, bounds[2], bounds[3])
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                layers = {"earth": [{"type": 3, "props": {"kind": "earth"},
                                     "parts": [[(0, 0), (EXTENT, 0), (EXTENT, EXTENT), (0, EXTENT), (0, 0)]]}]}
                for layer, gtype, props, pts in feats:
                    px = [lonlat_to_tile_px(z, x, y, lon, lat, EXTENT) for lon, lat in pts]
                    if max(p[0] for p in px) < -64 or min(p[0] for p in px) > EXTENT + 64 or \
                            max(p[1] for p in px) < -64 or min(p[1] for p in px) > EXTENT + 64:
                        continue
                    clean = {k: v for k, v in props.items() if v != ""}
                    layers.setdefault(layer, []).append({"type": gtype, "props": clean, "parts": [px]})
                tiles[(z, x, y)] = encode_mvt(layers, EXTENT)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    center = ((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, 15)
    write_pmtiles(OUT, tiles, MIN_Z, MAX_Z, bounds, center,
                  {"attribution": "Schematyczna próbka AccessWay, nie są to dane OpenStreetMap",
                   "accessway_build": "sample"})
    print("%s: %d tiles, %d bytes" % (OUT, len(tiles), os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
