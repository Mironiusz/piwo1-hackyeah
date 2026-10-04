"""
Generuje schematyczną próbkę sieci pieszej okolic Tauron Areny w Krakowie w formacie odpowiedzi Overpass API.

Próbka jest oznaczona polem accessway_sample i aplikacja pokazuje ją jako dane przykładowe. Geometria jest
uproszczona i ułożona jak na makietach zespołu: ulica Stanisława Lema od Tauron Areny, dalej aleja Pokoju do
Parku Lotników i Ogrodu Doświadczeń. Atrybuty dostępności są dobrane tak, żeby pokaz miał odcinki we wszystkich
czterech stanach, obniżony krawężnik, strome nachylenie, schody przy wejściu do parku i trasę alternatywną.

Użycie: python3 tools/accessway_sample.py <plik wyjściowy>
"""

import json
import math
import sys

LAT0 = 50.0676
LON0 = 19.9914
M_LAT = 111320.0
M_LON = 111320.0 * math.cos(math.radians(LAT0))


def ll(x, y):
    """Metry na wschód (x) i północ (y) od wejścia do Tauron Areny na szerokość i długość geograficzną."""
    return (round(LAT0 + y / M_LAT, 7), round(LON0 + x / M_LON, 7))


P = {
    "L_W2": (-420, 0), "L_W": (-150, 0), "L0": (0, 0), "L1": (200, 0), "L1B": (382, 0), "L2": (400, 0), "J": (450, 0),
    "L_E": (520, -40), "L_E2": (760, -150),
    "N1_S": (400, -170), "N1_N": (400, 140), "N1_M": (400, -80),
    "W_S": (-150, -170), "W_N": (-150, 160),
    "P1": (530, 50), "P2": (650, 125), "P3": (820, 230), "P4": (980, 330), "P5": (1090, 400),
    "P6": (1140, 430), "PK": (1190, 470), "P_E": (1400, 600),
    "Q1": (1050, 470), "Q2": (1100, 560),
    "PP": (1300, 610), "PW": (-300, -90), "PW2": (-60, -40),
}

NODE_TAGS = {
    "L1": {"highway": "crossing", "kerb": "lowered"},
    "L_W": {"highway": "crossing", "kerb": "lowered"},
    "L2": {"highway": "crossing"},
}

NODE_DATES = {"L1": "2025-05-12T10:00:00Z", "L_W": "2025-05-12T10:00:00Z"}

PAVING = {"surface": "paving_stones", "incline": "0%", "width": "2.5"}
ASPHALT = {"surface": "asphalt", "incline": "1%", "width": "2.0"}


def way(points, date=None, **tags):
    return (points, tags, date)


WAYS = [
    way(["L_W2", "L_W", "L0"], highway="footway", name="Stanisława Lema", **PAVING),
    way(["L0", "L1", "L1B", "L2", "J"], highway="footway", name="Stanisława Lema", **PAVING),
    way(["J", "L_E", "L_E2"], highway="footway", name="Stanisława Lema", **PAVING),
    way(["N1_S", "N1_M", "L2", "N1_N"], highway="residential", name="Ignacego Mościckiego", surface="asphalt"),
    way(["W_S", "L_W", "W_N"], highway="residential", name="Medweckiego", surface="asphalt"),
    way(["J", "P1"], "2025-06-14T09:00:00Z", highway="footway", name="aleja Pokoju", surface="asphalt",
        incline="8%"),
    way(["P1", "P2"], highway="footway", name="aleja Pokoju", surface="asphalt", incline="2%"),
    way(["P2", "P3", "P4"], highway="footway", name="aleja Pokoju"),
    way(["P4", "P5"], highway="footway", name="aleja Pokoju"),
    way(["P5", "P6"], highway="footway", name="aleja Pokoju"),
    way(["P6", "PK"], highway="footway", name="aleja Pokoju", **PAVING),
    way(["PK", "P_E"], highway="footway", name="aleja Pokoju", **ASPHALT),
    way(["P5", "Q1", "Q2", "PK"], highway="footway", name="Park Lotników Polskich", **ASPHALT),
    way(["PK", "PP"], "2025-03-08T09:00:00Z", highway="steps", name="aleja Pokoju, wejście do parku",
        step_count="12", incline="up"),
    way(["PW", "PW2", "L0"], highway="footway", name="Tauron Arena Kraków", **PAVING),
]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


AREAS = [
    ({"building": "yes"}, rect(-260, -260, 120, -60)),
    ({"building": "yes"}, rect(150, -180, 360, -40)),
    ({"building": "yes"}, rect(440, -260, 620, -90)),
    ({"building": "yes"}, rect(-120, 40, 120, 220)),
    ({"building": "yes"}, rect(160, 40, 360, 200)),
    ({"building": "yes"}, rect(-420, 40, -190, 220)),
    ({"building": "yes"}, rect(520, 140, 640, 330)),
    ({"building": "yes"}, rect(700, 10, 900, 160)),
    ({"building": "yes"}, rect(860, 300, 940, 480)),
    ({"leisure": "park", "name": "Park Lotników Polskich"},
     [(940, 520), (1150, 380), (1700, 380), (1700, 1100), (900, 1100), (940, 520)]),
]

PLACES = [
    ("Tauron Arena Kraków", -10, -22, {"amenity": "events_venue", "wheelchair": "yes",
     "addr:street": "Stanisława Lema", "addr:housenumber": "7", "addr:suburb": "Czyżyny", "addr:postcode": "31-571",
     "addr:city": "Kraków"}),
    ("Ogród Doświadczeń im. Stanisława Lema", 1215, 492, {"leisure": "garden", "tourism": "attraction",
     "addr:street": "aleja Pokoju", "addr:housenumber": "68", "addr:suburb": "Czyżyny", "addr:postcode": "31-564",
     "addr:city": "Kraków"}),
    ("Park Lotników Polskich", 1320, 640, {"leisure": "park", "addr:suburb": "Czyżyny", "addr:city": "Kraków"}),
    ("Tauron Arena Kraków Wieczysta", 470, 30, {"public_transport": "platform", "highway": "bus_stop",
     "addr:city": "Kraków"}),
    ("Centrum Handlowe Czyżyny", -300, 130, {"shop": "mall", "addr:street": "Medweckiego", "addr:housenumber": "2",
     "addr:city": "Kraków"}),
]

FEATURES = [
    (1170, 455, {"amenity": "bench"}, "2025-04-02T10:00:00Z"),
    (1260, 520, {"amenity": "bench"}, "2025-04-02T10:00:00Z"),
    (-40, -40, {"amenity": "toilets", "wheelchair": "yes"}, "2025-02-10T10:00:00Z"),
]


def build():
    elements = []
    ids = {}
    nid = 1
    for key, (x, y) in P.items():
        lat, lon = ll(x, y)
        ids[key] = nid
        el = {"type": "node", "id": nid, "lat": lat, "lon": lon}
        if key in NODE_TAGS:
            el["tags"] = NODE_TAGS[key]
        if key in NODE_DATES:
            el["timestamp"] = NODE_DATES[key]
        elements.append(el)
        nid += 1
    wid = 1000
    for pts, tags, date in WAYS:
        el = {"type": "way", "id": wid, "nodes": [ids[p] for p in pts], "tags": tags}
        if date is not None:
            el["timestamp"] = date
        elements.append(el)
        wid += 1
    for tags, pts in AREAS:
        refs = []
        for x, y in pts[:-1]:
            lat, lon = ll(x, y)
            elements.append({"type": "node", "id": nid, "lat": lat, "lon": lon})
            refs.append(nid)
            nid += 1
        refs.append(refs[0])
        elements.append({"type": "way", "id": wid, "nodes": refs, "tags": tags})
        wid += 1
    pid = 5000
    for name, x, y, tags in PLACES:
        lat, lon = ll(x, y)
        t = dict(tags)
        t["name"] = name
        elements.append({"type": "node", "id": pid, "lat": lat, "lon": lon, "tags": t,
                         "timestamp": "2025-06-01T00:00:00Z"})
        pid += 1
    for x, y, tags, date in FEATURES:
        lat, lon = ll(x, y)
        elements.append({"type": "node", "id": pid, "lat": lat, "lon": lon, "tags": tags, "timestamp": date})
        pid += 1
    return {
        "version": 0.6,
        "generator": "accessway_sample.py",
        "osm3s": {"timestamp_osm_base": "2026-10-02T00:00:00Z",
                  "copyright": "Schematyczna próbka, nie są to dane OpenStreetMap"},
        "accessway_sample": True,
        "accessway_fetched_at": "2026-10-02T00:00:00Z",
        "elements": elements,
    }


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "osm_sample.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(), f, ensure_ascii=False)
    print(out)
