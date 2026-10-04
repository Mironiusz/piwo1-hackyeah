"""
Pobiera z Overpass API sieć pieszą, miejsca i punkty udogodnień centrum Krakowa dla aplikacji EnableMe.

Uruchamiane na maszynie z dostępem do internetu (make aw-osm). Wynik trafia do zasobów aplikacji jako
rawfile/data/osm_krakow.json; aplikacja wybiera go zamiast schematycznej próbki. Dane OpenStreetMap
są na licencji ODbL, aplikacja pokazuje oznaczenie źródła.

Użycie: python3 tools/accessway_fetch_osm.py <plik wyjściowy> [south,west,north,east]
"""

import datetime
import json
import sys
import urllib.parse
import urllib.request

DEFAULT_BBOX = "50.0440,19.9180,50.0700,19.9560"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
HIGHWAYS = "footway|pedestrian|path|living_street|residential|service|steps|tertiary|secondary|primary|unclassified|cycleway|track|corridor|tertiary_link|secondary_link|primary_link|elevator"


def build_query(bbox):
    return f"""[out:json][timeout:180];
way["highway"~"^({HIGHWAYS})$"]({bbox})->.w;
.w out body qt;
node(w.w)->.wn;
.wn out body qt;
(
  nwr["name"]["amenity"]({bbox});
  nwr["name"]["tourism"]({bbox});
  nwr["name"]["historic"]({bbox});
  nwr["name"]["public_transport"]({bbox});
  nwr["name"]["railway"="station"]({bbox});
  nwr["name"]["healthcare"]({bbox});
  nwr["name"]["shop"]["wheelchair"]({bbox});
  node["amenity"~"^(bench|toilets)$"]({bbox});
  node["leisure"="picnic_table"]({bbox});
  node["highway"="elevator"]({bbox});
  node["entrance"]({bbox});
);
out center meta qt;
"""


def fetch(query):
    body = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=body, headers={"User-Agent": "EnableMe-HackYeah/1.0"})
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.loads(resp.read().decode("utf-8")), url
        except Exception as exc:
            print(f"{url}: {exc}", file=sys.stderr)
            last = exc
    raise SystemExit(f"Overpass niedostępny: {last}")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "osm_krakow.json"
    bbox = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BBOX
    data, url = fetch(build_query(bbox))
    elements = data.get("elements", [])
    ways = sum(1 for e in elements if e.get("type") == "way" and "highway" in e.get("tags", {}))
    if ways == 0:
        raise SystemExit("Odpowiedź bez sieci pieszej - plik nie został zapisany")
    data["accessway_fetched_at"] = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["accessway_source"] = url
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{out}: {len(elements)} elementów, {ways} dróg, stan OSM {data.get('osm3s', {}).get('timestamp_osm_base')}")


if __name__ == "__main__":
    main()
