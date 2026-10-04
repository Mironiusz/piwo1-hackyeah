"""
In-memory mock of the programming interface of `docs/product/api_contract.md` (piwo1-hackyeah), standard library only.

It implements all sixteen operations with their requests, responses, errors, sessions and conventions, and the
behavior behind them from `docs/product/specification.md` where the contract points at it: the statuses of M4
from the latest votes of five persons with weights 1 and 0.5, the vote limit of one day, idempotent reports,
flags and moderation of M11, routes of M2 with the four segment states of M7 and the three lists of M8.

It is a stand-in for development and tests of the clients, not the service. What it invents is marked as such:

- The pedestrian network is built from the `roads` layer of the tile archive at zoom 15 (every road kind except
  `highway`), so routes follow the streets of the base map. Which OpenStreetMap attributes a stretch has is not
  in the archive; the mock assigns them per stretch from a seeded hash, so the states are stable between runs.
- The facts are sample facts placed on the network from a seed, most of them within 1.5 km of the known places: barriers and amenities of every type, from
  OpenStreetMap and from user reports, with seeded votes so that every status appears.
- The address search knows a short list of places in Kraków and the named streets of the network.
- The OpenStreetMap copy is the build day of the archive (`<archive>.build`, written by `make tiles`).

Nothing is stored on disk except a cache of the network next to the archive; every restart starts clean.
"""

import base64
import hashlib
import hmac
import heapq
import json
import math
import os
import pickle
import random
import re
import secrets
import time
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pmtiles_mvt import PMTilesReader, decode_mvt, lonlat_to_tile, tile_to_lonlat

ZONE = ZoneInfo("Europe/Warsaw")
NETWORK_ZOOM = 15
SNAP = 1e-5
JOIN_M = 6.0
BARRIERS = ("stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage")
AMENITIES = ("ramp", "elevator", "lowered_kerb", "accessible_toilet", "rest_place", "handrail_at_stairs")
ATTRIBUTES = ("kerbs", "surface", "incline", "width", "steps")
ATTRIBUTE_OF = {"stairs": "steps", "high_kerb": "kerbs", "poor_surface": "surface", "steep_incline": "incline",
                "narrow_passage": "width"}
GEOZONE_RADII = (10, 25, 50, 100)
PSEUDONYM_EXTRA = "_-"
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def pseudonym_ok(text):
    """3 to 30 characters after leading and trailing spaces are removed: letters, digits, underscore, hyphen (M9)."""
    p = text.strip(" ")
    return 3 <= len(p) <= 30 and all(c.isalpha() or c.isdigit() or c in PSEUDONYM_EXTRA for c in p)
WALK_ROAD_KINDS = ("major_road", "minor_road", "path", "other")
PLACES = [
    ("Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków", 50.0678, 19.9914),
    ("Rynek Główny, Stare Miasto, 31-042 Kraków", 50.0617, 19.9373),
    ("Kraków Główny, Pawia 5a, Stare Miasto, 31-154 Kraków", 50.0677, 19.9476),
    ("Wawel, Stare Miasto, 31-001 Kraków", 50.0540, 19.9354),
    ("Galeria Krakowska, Pawia 5, Stare Miasto, 31-154 Kraków", 50.0672, 19.9457),
    ("Akademia Górniczo-Hutnicza, aleja Adama Mickiewicza 30, Czarna Wieś, 30-059 Kraków", 50.0647, 19.9234),
    ("Plac Nowy, Kazimierz, 31-056 Kraków", 50.0515, 19.9446),
    ("ICE Kraków, Marii Konopnickiej 17, Dębniki, 30-302 Kraków", 50.0477, 19.9327),
    ("Muzeum Narodowe w Krakowie, aleja 3 Maja 1, Czarna Wieś, 30-062 Kraków", 50.0604, 19.9233),
    ("Nowa Huta, Plac Centralny im. Ronalda Reagana, 31-923 Kraków", 50.0718, 20.0377),
    ("Szpital Uniwersytecki, Jakubowskiego 2, Prokocim, 30-688 Kraków", 50.0109, 19.9997),
    ("Bonarka City Center, Henryka Kamieńskiego 11, Podgórze, 30-644 Kraków", 50.0281, 19.9505),
]


class ApiError(Exception):
    """An error response of the contract: status, code and the extra fields that code names."""

    def __init__(self, status, code, **extra):
        super().__init__(code)
        self.status = status
        self.code = code
        self.extra = extra
        self.headers = {}


def invalid(*fields):
    return ApiError(422, "invalid_request", fields=list(fields))


def now():
    return datetime.now(ZONE)


def instant(dt):
    return dt.astimezone(ZONE).isoformat(timespec="milliseconds")


def day(dt):
    return dt.astimezone(ZONE).strftime("%Y-%m-%d")


def meters(lat1, lon1, lat2, lon2):
    k = 111320.0
    dx = (lon2 - lon1) * k * math.cos(math.radians((lat1 + lat2) / 2))
    dy = (lat2 - lat1) * k
    return math.hypot(dx, dy)


def seeded(*parts):
    """A number in [0, 1) that depends only on the parts, so the invented data is the same on every run."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64



def check_fields(body, required, optional=()):
    if not isinstance(body, dict):
        raise invalid("")
    unknown = [k for k in body if k not in required and k not in optional]
    missing = [k for k in required if k not in body]
    if unknown or missing:
        raise invalid(*(unknown + missing))


def check_point(value, path):
    if not isinstance(value, dict) or set(value) != {"lat", "lon"}:
        raise invalid(path)
    for k in ("lat", "lon"):
        v = value[k]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise invalid("%s.%s" % (path, k))
    if not (-90 <= value["lat"] <= 90):
        raise invalid(path + ".lat")
    if not (-180 <= value["lon"] <= 180):
        raise invalid(path + ".lon")
    return float(value["lat"]), float(value["lon"])


def check_type_list(value, path, allowed):
    if not isinstance(value, list) or any(not isinstance(v, str) or v not in allowed for v in value):
        raise invalid(path)
    if len(set(value)) != len(value):
        raise invalid(path)
    return list(value)



class Network:
    """Nodes and edges of the walking network, with a grid index for the nearest node and the nearest edge."""

    def __init__(self, nodes, edges, names):
        self.nodes = nodes
        self.edges = edges
        self.names = names
        self.adj = [[] for _ in nodes]
        for i, (a, b, length, _kind, _name) in enumerate(edges):
            self.adj[a].append((b, i, length))
            self.adj[b].append((a, i, length))
        self.component = self.components()
        self.grid = {}
        for i, (lat, lon) in enumerate(nodes):
            if self.component[i] == 0:
                self.grid.setdefault((int(lat * 500), int(lon * 500)), []).append(i)

    def components(self):
        """Component ids by size, 0 for the largest; routes start and end only in the largest one."""
        comp = [-1] * len(self.nodes)
        sizes = []
        for s in range(len(self.nodes)):
            if comp[s] >= 0:
                continue
            c = len(sizes)
            comp[s] = c
            stack = [s]
            k = 0
            while stack:
                u = stack.pop()
                k += 1
                for v, _e, _l in self.adj[u]:
                    if comp[v] < 0:
                        comp[v] = c
                        stack.append(v)
            sizes.append(k)
        order = sorted(range(len(sizes)), key=lambda c: -sizes[c])
        rank = [0] * len(sizes)
        for r, c in enumerate(order):
            rank[c] = r
        return [rank[c] for c in comp]

    @staticmethod
    def build(archive_path):
        cache = archive_path + ".network.pickle"
        if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(archive_path):
            with open(cache, "rb") as f:
                nodes, edges, names = pickle.load(f)
            return Network(nodes, edges, names)
        reader = PMTilesReader(archive_path)
        z = min(NETWORK_ZOOM, reader.max_zoom)
        x0, y0 = lonlat_to_tile(z, reader.min_lon, reader.max_lat)
        x1, y1 = lonlat_to_tile(z, reader.max_lon, reader.min_lat)
        index = {}
        nodes = []
        edge_keys = {}
        edges = []
        names = {}

        def node(lon, lat):
            key = (round(lat / SNAP), round(lon / SNAP))
            i = index.get(key)
            if i is None:
                i = len(nodes)
                index[key] = i
                nodes.append((key[0] * SNAP, key[1] * SNAP))
            return i

        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                data = reader.tile(z, x, y)
                if data is None:
                    continue
                layers = decode_mvt(data)
                if "roads" not in layers:
                    continue
                extent, feats = layers["roads"]
                for f in feats:
                    props = f["props"]
                    kind = str(props.get("kind") or props.get("pmap:kind") or "")
                    if f["type"] != 2 or kind not in WALK_ROAD_KINDS:
                        continue
                    name = str(props.get("name:pl") or props.get("name") or "")
                    for part in f["parts"]:
                        prev = None
                        for px, py in part:
                            lon, lat = tile_to_lonlat(z, x, y, px, py, extent)
                            cur = node(lon, lat)
                            if prev is not None and prev != cur:
                                key = (min(prev, cur), max(prev, cur))
                                if key not in edge_keys:
                                    la, lo = nodes[prev]
                                    lb, lob = nodes[cur]
                                    edge_keys[key] = len(edges)
                                    edges.append((prev, cur, meters(la, lo, lb, lob), kind, name))
                                    if name:
                                        names.setdefault(name, []).append(len(edges) - 1)
                            prev = cur
        edges = Network.join_loose_ends(nodes, edges)
        names = {}
        for i, e in enumerate(edges):
            if e[4]:
                names.setdefault(e[4], []).append(i)
        with open(cache, "wb") as f:
            pickle.dump((nodes, edges, names), f)
        return Network(nodes, edges, names)

    @staticmethod
    def join_loose_ends(nodes, edges):
        """
        Joins the network where the tiles lost a shared vertex: a way that ends within JOIN_M of another stretch
        is connected to it, splitting that stretch at the nearest point. Without this the base map tiles give
        tens of thousands of separate pieces, because a junction is not always a vertex of both ways in a tile.
        """
        degree = [0] * len(nodes)
        for a, b, _l, _k, _n in edges:
            degree[a] += 1
            degree[b] += 1
        grid = {}
        for i, (a, b, _l, _k, _n) in enumerate(edges):
            (la, lo), (lb, lob) = nodes[a], nodes[b]
            for lat, lon in ((la, lo), (lb, lob), ((la + lb) / 2, (lo + lob) / 2)):
                grid.setdefault((int(lat * 2000), int(lon * 2000)), set()).add(i)
        splits = {}
        extra = []
        for n, d in enumerate(degree):
            if d != 1:
                continue
            lat, lon = nodes[n]
            cx, cy = int(lat * 2000), int(lon * 2000)
            best, best_d, best_t = None, JOIN_M, 0.0
            for gx in (cx - 1, cx, cx + 1):
                for gy in (cy - 1, cy, cy + 1):
                    for i in grid.get((gx, gy), ()):
                        a, b = edges[i][0], edges[i][1]
                        if a == n or b == n:
                            continue
                        (la, lo), (lb, lob) = nodes[a], nodes[b]
                        t, dist = project(lat, lon, la, lo, lb, lob)
                        if dist < best_d:
                            best, best_d, best_t = i, dist, t
            if best is None:
                continue
            a, b = edges[best][0], edges[best][1]
            if best_t <= 0.02:
                target = a
            elif best_t >= 0.98:
                target = b
            else:
                target = None
                splits.setdefault(best, []).append((best_t, n))
            if target is not None and target != n:
                extra.append((n, target, best_d, edges[best][3], ""))
        out = []
        for i, (a, b, length, kind, name) in enumerate(edges):
            if i not in splits:
                out.append((a, b, length, kind, name))
                continue
            (la, lo), (lb, lob) = nodes[a], nodes[b]
            prev = a
            for t, loose in sorted(splits[i]):
                mid = len(nodes)
                nodes.append((la + (lb - la) * t, lo + (lob - lo) * t))
                pl, po = nodes[prev]
                ml, mo = nodes[mid]
                out.append((prev, mid, meters(pl, po, ml, mo), kind, name))
                nl, no = nodes[loose]
                out.append((loose, mid, meters(nl, no, ml, mo), kind, ""))
                prev = mid
            pl, po = nodes[prev]
            out.append((prev, b, meters(pl, po, lb, lob), kind, name))
        return out + extra

    def nearest_node(self, lat, lon, max_m=1500):
        cx, cy = int(lat * 500), int(lon * 500)
        best, best_d = None, max_m
        for r in range(0, 8):
            for gx in range(cx - r, cx + r + 1):
                for gy in range(cy - r, cy + r + 1):
                    if max(abs(gx - cx), abs(gy - cy)) != r:
                        continue
                    for i in self.grid.get((gx, gy), ()):
                        la, lo = self.nodes[i]
                        d = meters(lat, lon, la, lo)
                        if d < best_d:
                            best, best_d = i, d
            if best is not None and r >= 1:
                break
        return best

    def edge_point(self, e, t):
        a, b = self.edges[e][0], self.edges[e][1]
        (la, lo), (lb, lob) = self.nodes[a], self.nodes[b]
        return la + (lb - la) * t, lo + (lob - lo) * t

    def stretch_key(self, e):
        """
        What the invented attributes depend on: the street name or the road kind and a block of about 150 m, so
        that a street keeps one set of attributes along a block instead of changing at every vertex.
        """
        a, b, _l, kind, name = self.edges[e]
        (la, lo), (lb, lob) = self.nodes[a], self.nodes[b]
        lat, lon = (la + lb) / 2, (lo + lob) / 2
        return "%s|%d|%d" % (name or kind, int(lat * 700), int(lon * 450))

    def known_attributes(self, e):
        """
        The OpenStreetMap attributes the mock pretends are tagged on this stretch, stable per street block. The
        steps are always known on the network: a way not tagged as steps counts as known to have no stairs (M7).
        """
        kind = self.edges[e][3]
        key = self.stretch_key(e)
        base = {"major_road": 0.8, "minor_road": 0.65, "path": 0.45, "other": 0.4}.get(kind, 0.4)
        r = seeded("quality", key)
        if r < 0.1:
            known = set()
        elif r > 0.7:
            known = set(ATTRIBUTES)
        else:
            known = {a for a in ATTRIBUTES if seeded("attr", key, a) < base}
        known.add("steps")
        return known

    def marked_wheelchair_no(self, e):
        return seeded("wheelchair_no", self.stretch_key(e)) < 0.02


def project(lat, lon, la, lo, lb, lob):
    """Projection of a point on a segment: (parameter 0..1, distance in metres)."""
    k = math.cos(math.radians(lat)) * 111320.0
    ax, ay = (lo - lon) * k, (la - lat) * 111320.0
    bx, by = (lob - lon) * k, (lb - lat) * 111320.0
    dx, dy = bx - ax, by - ay
    den = dx * dx + dy * dy
    t = 0.0 if den == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / den))
    return t, math.hypot(ax + t * dx, ay + t * dy)



class Fact:
    def __init__(self, fid, ftype, lat, lon, source, edge, created):
        self.id = fid
        self.type = ftype
        self.lat = lat
        self.lon = lon
        self.source = source
        self.edge = edge
        self.created = created
        self.geozone_radius_m = None
        self.description = None
        self.step_count = None
        self.osm_edited_on = None
        self.is_sample = False
        self.is_removed_from_osm = False
        self.votes = []
        self.flagged_on = None
        self.is_hidden = False

    def latest_persons(self):
        """The latest vote of each of the five persons who voted most recently (M4)."""
        seen = {}
        for v in sorted(self.votes, key=lambda v: v["at"], reverse=True):
            if v["person"] not in seen:
                seen[v["person"]] = v
            if len(seen) == 5:
                break
        return list(seen.values())

    def status(self):
        if self.is_removed_from_osm:
            return "outdated"
        latest = self.latest_persons()
        conf = sum(v["weight"] for v in latest if v["verdict"] == "confirm")
        deny = sum(v["weight"] for v in latest if v["verdict"] == "deny")
        if deny >= 2 and deny > conf:
            return "outdated"
        if conf > 0 and deny > 0:
            return "disputed"
        if conf >= 2:
            return "confirmed"
        return "unverified"

    def last_confirmed_on(self):
        days = [v["at"] for v in self.votes if v["verdict"] == "confirm"]
        return day(max(days)) if days else None

    def to_json(self):
        return {
            "id": self.id,
            "type": self.type,
            "point": {"lat": round(self.lat, 7), "lon": round(self.lon, 7)},
            "geozone_radius_m": self.geozone_radius_m,
            "description": self.description,
            "step_count": self.step_count,
            "source": self.source,
            "status": self.status(),
            "is_removed_from_osm": self.is_removed_from_osm,
            "osm_edited_on": self.osm_edited_on if self.source == "openstreetmap" else None,
            "last_confirmed_on": self.last_confirmed_on(),
            "is_sample": self.is_sample,
            "can_be_flagged": self.source != "openstreetmap",
        }


class Store:
    """The state of the mock: network, facts, accounts, idempotency keys; all in memory."""

    def __init__(self, network, osm_copy_date, moderator_password, fact_count, seed):
        self.net = network
        self.osm_copy_date = osm_copy_date
        self.secret = secrets.token_bytes(32)
        self.facts = {}
        self.accounts = {}
        self.next_account = 1
        self.next_fact = 1000
        self.idempotency = {}
        self.fact_grid = {}
        mod = self.add_account("moderator", moderator_password)
        mod["is_moderator"] = True
        self.seed_facts(fact_count, seed)


    def add_account(self, pseudonym, password):
        salt = secrets.token_bytes(16)
        acc = {"id": self.next_account, "pseudonym": pseudonym, "salt": salt,
               "hash": hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 20000), "is_moderator": False}
        self.accounts[acc["id"]] = acc
        self.next_account += 1
        return acc

    def find_account(self, pseudonym):
        key = pseudonym.strip(" ").lower()
        for acc in self.accounts.values():
            if acc["pseudonym"].lower() == key:
                return acc
        return None

    def token(self, acc):
        payload = json.dumps({"a": acc["id"], "e": int(time.time()) + 24 * 3600}).encode()
        body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
        sig = base64.urlsafe_b64encode(hmac.new(self.secret, body.encode(), "sha256").digest()).decode().rstrip("=")
        return body + "." + sig

    def account_of(self, token):
        try:
            body, sig = token.split(".")
            good = base64.urlsafe_b64encode(hmac.new(self.secret, body.encode(), "sha256").digest()).decode().rstrip("=")
            if not hmac.compare_digest(sig, good):
                return None
            payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
            if payload["e"] < time.time():
                return None
            return self.accounts.get(payload["a"])
        except (ValueError, KeyError, TypeError):
            return None


    def index_fact(self, f):
        self.fact_grid.setdefault((int(f.lat * 500), int(f.lon * 500)), []).append(f.id)

    def facts_near(self, lat, lon, radius_m):
        cx, cy = int(lat * 500), int(lon * 500)
        reach = int(radius_m / 150) + 1
        out = []
        for gx in range(cx - reach, cx + reach + 1):
            for gy in range(cy - reach, cy + reach + 1):
                for fid in self.fact_grid.get((gx, gy), ()):
                    f = self.facts[fid]
                    d = meters(lat, lon, f.lat, f.lon)
                    if d <= radius_m:
                        out.append((f, d))
        return out

    def attach_edge(self, lat, lon):
        """The stretch of the network a point report lies on: the nearest one within 15 m (M2), or None."""
        n = self.net.nearest_node(lat, lon, 300)
        if n is None:
            return None
        best, best_d = None, 15.0
        seen = set()
        for _b, e, _l in self.net.adj[n]:
            seen.add(e)
        for nb, _e, _l in self.net.adj[n]:
            for _b2, e2, _l2 in self.net.adj[nb]:
                seen.add(e2)
        for e in seen:
            a, b = self.net.edges[e][0], self.net.edges[e][1]
            (la, lo), (lb, lob) = self.net.nodes[a], self.net.nodes[b]
            _t, d = project(lat, lon, la, lo, lb, lob)
            if d <= best_d:
                best, best_d = e, d
        return best

    def new_fact(self, ftype, lat, lon, source, created):
        f = Fact(self.next_fact, ftype, lat, lon, source, self.attach_edge(lat, lon), created)
        self.next_fact += 1
        self.facts[f.id] = f
        self.index_fact(f)
        return f

    def seed_facts(self, count, seed):
        rnd = random.Random(seed)
        edges = [i for i, e in enumerate(self.net.edges) if e[2] >= 8 and self.net.component[e[0]] == 0]
        if not edges:
            return
        centers = [(lat, lon) for _label, lat, lon in PLACES]
        near = []
        for i in edges:
            la, lo = self.net.nodes[self.net.edges[i][0]]
            if any(abs(la - lat) < 0.0135 and abs(lo - lon) < 0.021 for lat, lon in centers):
                near.append(i)
        start = now() - timedelta(days=40)
        types = list(BARRIERS) + list(AMENITIES)
        weights = [3, 4, 2, 2, 2, 2, 1, 4, 1, 2, 1]
        for k in range(count):
            e = rnd.choice(near if near and rnd.random() < 0.7 else edges)
            lat, lon = self.net.edge_point(e, rnd.uniform(0.2, 0.8))
            ftype = rnd.choices(types, weights)[0]
            osm = rnd.random() < 0.55
            f = self.new_fact(ftype, lat, lon, "openstreetmap" if osm else "user_report", start)
            f.edge = e
            if ftype == "stairs":
                f.step_count = rnd.choice([None, 2, 3, 5, 12])
            if osm:
                f.osm_edited_on = (start - timedelta(days=rnd.randint(30, 900))).strftime("%Y-%m-%d")
            else:
                f.is_sample = True
                if ftype in BARRIERS and rnd.random() < 0.12:
                    f.geozone_radius_m = rnd.choice(GEOZONE_RADII)
                    f.description = rnd.choice(["Roboty drogowe, chodnik zamknięty", "Kocie łby na całym odcinku",
                                                None])
                f.votes.append({"person": "seed-author-%d" % k, "verdict": "confirm", "weight": 0.5,
                                "at": start + timedelta(hours=rnd.randint(0, 200))})
            pattern = rnd.random()
            voters = rnd.randint(0, 4)
            for j in range(voters):
                if pattern < 0.55:
                    verdict = "confirm"
                elif pattern < 0.8:
                    verdict = "confirm" if j % 2 == 0 else "deny"
                else:
                    verdict = "deny"
                f.votes.append({"person": "seed-%d-%d" % (k, j), "verdict": verdict,
                                "weight": rnd.choice([1, 0.5]),
                                "at": start + timedelta(hours=rnd.randint(200, 900))})

    def visible(self, fid):
        f = self.facts.get(fid)
        if f is None or f.is_hidden:
            raise ApiError(404, "fact_not_found")
        return f



class Router:
    """Routes of M2 over the mock network: avoided barriers, segment states of M7 and the lists of M8."""

    def __init__(self, store):
        self.s = store
        self.net = store.net

    def edge_facts(self):
        by_edge = {}
        for f in self.s.facts.values():
            if f.is_hidden or f.status() == "outdated":
                continue
            if f.geozone_radius_m:
                for e in self.edges_within(f.lat, f.lon, f.geozone_radius_m):
                    by_edge.setdefault(e, []).append(f)
            elif f.edge is not None:
                by_edge.setdefault(f.edge, []).append(f)
        return by_edge

    def edges_within(self, lat, lon, radius):
        out = set()
        n = self.net.nearest_node(lat, lon, radius + 200)
        if n is None:
            return out
        frontier = [n]
        seen = {n}
        while frontier:
            cur = frontier.pop()
            for nb, e, _l in self.net.adj[cur]:
                a, b = self.net.edges[e][0], self.net.edges[e][1]
                (la, lo), (lb, lob) = self.net.nodes[a], self.net.nodes[b]
                _t, d = project(lat, lon, la, lo, lb, lob)
                if d <= radius:
                    out.add(e)
                    if nb not in seen:
                        seen.add(nb)
                        frontier.append(nb)
        return out

    @staticmethod
    def avoided(f, avoid):
        """Whether the route avoids this fact: OpenStreetMap or confirmed barriers, geozones not outdated (M2)."""
        if f.type not in avoid:
            return False
        if f.geozone_radius_m:
            return True
        return f.source == "openstreetmap" or f.status() == "confirmed"

    def shortest(self, s, t, penalty):
        dist = {s: 0.0}
        prev = {}
        heap = [(0.0, s)]
        while heap:
            d, u = heapq.heappop(heap)
            if u == t:
                break
            if d > dist.get(u, math.inf):
                continue
            for v, e, length in self.net.adj[u]:
                nd = d + length + penalty.get(e, 0.0)
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = (u, e)
                    heapq.heappush(heap, (nd, v))
        if t not in dist:
            return None
        path = []
        cur = t
        while cur != s:
            u, e = prev[cur]
            path.append((u, cur, e))
            cur = u
        path.reverse()
        return path

    def build_route(self, start, dest, s_node, t_node, path, avoid, need, by_edge):
        profile_attrs = [a for a in ATTRIBUTES if any(ATTRIBUTE_OF[b] == a for b in avoid)]
        pieces = []
        sl, so = start
        nl, no = self.net.nodes[s_node]
        pieces.append(([[so, sl], [no, nl]], meters(sl, so, nl, no), "no_data", list(profile_attrs), False, None))
        for u, v, e in path:
            (la, lo), (lb, lob) = self.net.nodes[u], self.net.nodes[v]
            facts = by_edge.get(e, [])
            wheel_no = self.net.marked_wheelchair_no(e)
            if any(f.type in avoid and not self.overruled(f, e) for f in facts):
                state, missing = "barrier", []
            else:
                known = self.net.known_attributes(e)
                missing = [a for a in profile_attrs if a not in known]
                known_relevant = [a for a in profile_attrs if a in known and a != "steps"]
                if not missing:
                    state = "partial_data" if wheel_no else "no_barrier"
                elif known_relevant:
                    state = "partial_data"
                else:
                    state = "no_data"
            pieces.append(([[lo, la], [lob, lb]], self.net.edges[e][2], state, missing, wheel_no, e))
        dl, do = dest
        tl, to = self.net.nodes[t_node]
        pieces.append(([[to, tl], [do, dl]], meters(tl, to, dl, do), "no_data", list(profile_attrs), False, None))

        segments = []
        for line, length, state, missing, wheel_no, e in pieces:
            last = segments[-1] if segments else None
            joinable = last is not None and e is not None and last["_net"] and last["state"] == state and \
                last["missing_attributes"] == missing and last["is_marked_wheelchair_no"] == wheel_no
            if joinable:
                last["line"].append(line[1])
                last["_len"] += length
            else:
                segments.append({"line": [line[0], line[1]], "_len": length, "state": state,
                                 "missing_attributes": list(missing), "is_marked_wheelchair_no": wheel_no,
                                 "_net": e is not None})
        segments = [{"line": [[round(p[0], 7), round(p[1], 7)] for p in seg["line"]],
                     "length_m": int(round(seg["_len"])), "state": seg["state"],
                     "missing_attributes": seg["missing_attributes"] if seg["state"] in ("partial_data", "no_data") else [],
                     "is_marked_wheelchair_no": seg["is_marked_wheelchair_no"]} for seg in segments]

        along = 0.0
        offsets = {}
        for _line, length, _state, _missing, _w, e in pieces:
            if e is not None and e not in offsets:
                offsets[e] = along
            along += length
        total = along
        profile_barriers, additional, amenities = [], [], []
        seen = set()
        for u, v, e in path:
            for f in by_edge.get(e, []):
                if f.id in seen or f.type not in BARRIERS:
                    continue
                seen.add(f.id)
                at = offsets[e] + self.offset_on_edge(f, e)
                (profile_barriers if f.type in avoid else additional).append((at, f, self.overruled(f, e)))
        if need:
            polyline = []
            for line, length, _state, _missing, _w, _e in pieces:
                polyline.append((line[0][1], line[0][0], line[1][1], line[1][0], length))
            for f in self.s.facts.values():
                if f.type not in need or f.is_hidden or f.is_removed_from_osm:
                    continue
                best_d, best_at, acc = 50.0, None, 0.0
                for la, lo, lb, lob, length in polyline:
                    t, d = project(f.lat, f.lon, la, lo, lb, lob)
                    if d <= best_d:
                        best_d, best_at = d, acc + t * length
                    acc += length
                if best_at is not None:
                    amenities.append((best_at, f, False))

        def route_fact(at, f, overruled):
            out = f.to_json()
            out["distance_from_start_m"] = int(round(at))
            out["is_overruled_by_osm"] = overruled
            return out

        return {
            "length_m": int(round(total)),
            "segments": segments,
            "profile_barriers": [route_fact(*t) for t in sorted(profile_barriers, key=lambda t: t[0])],
            "additional_barriers": [route_fact(*t) for t in sorted(additional, key=lambda t: t[0])],
            "amenities": [route_fact(*t) for t in sorted(amenities, key=lambda t: t[0])],
        }

    def overruled(self, f, e):
        """
        A user report of a barrier that OpenStreetMap contradicts and that has not reached the threshold of M4: the
        stretch carries the attribute behind the barrier, and the mock lets half of such reports, chosen from a
        seed, be contradicted by it. The segment then follows OpenStreetMap (M7). The default of no stairs never
        contradicts a report of stairs.
        """
        if f.source != "user_report" or f.type not in ATTRIBUTE_OF or f.type == "stairs" or f.geozone_radius_m:
            return False
        if f.status() == "confirmed":
            return False
        return ATTRIBUTE_OF[f.type] in self.net.known_attributes(e) and seeded("overruled", f.id) < 0.5

    def offset_on_edge(self, f, e):
        a, b = self.net.edges[e][0], self.net.edges[e][1]
        (la, lo), (lb, lob) = self.net.nodes[a], self.net.nodes[b]
        t, _d = project(f.lat, f.lon, la, lo, lb, lob)
        return t * self.net.edges[e][2]

    def plan(self, start, dest, avoid, need):
        s_node = self.net.nearest_node(*start)
        t_node = self.net.nearest_node(*dest)
        if s_node is None or t_node is None:
            raise ApiError(503, "routing_unavailable")
        by_edge = self.edge_facts()
        penalty = {}
        for e, facts in by_edge.items():
            n = sum(1 for f in facts if self.avoided(f, avoid))
            if n:
                penalty[e] = 1e6 * n
        path = self.shortest(s_node, t_node, penalty)
        if path is None:
            raise ApiError(503, "routing_unavailable")
        crossed = [f for _u, _v, e in path for f in by_edge.get(e, []) if self.avoided(f, avoid)]
        route = self.build_route(start, dest, s_node, t_node, path, avoid, need, by_edge)
        alternative = None
        soft = {}
        for _u, _v, e in path:
            for f in by_edge.get(e, []):
                if f.type in avoid and not self.avoided(f, avoid) and f.status() in ("unverified", "disputed"):
                    soft[f.id] = (e, f)
        if soft:
            penalty2 = dict(penalty)
            for e, _f in soft.values():
                penalty2[e] = penalty2.get(e, 0.0) + 1e6
            alt_path = self.shortest(s_node, t_node, penalty2)
            if alt_path is not None:
                alt_edges = {e for _u, _v, e in alt_path}
                avoided = [f for e, f in soft.values() if e not in alt_edges]
                if avoided and [e for _u, _v, e in alt_path] != [e for _u, _v, e in path]:
                    alt_route = self.build_route(start, dest, s_node, t_node, alt_path, avoid, need, by_edge)
                    base = {f["id"]: f for f in route["profile_barriers"]}
                    alternative = {"route": alt_route,
                                   "avoided_barriers": [base[f.id] for f in avoided if f.id in base]}
        return {"osm_copy_date": self.s.osm_copy_date, "barrier_free_route_exists": not crossed,
                "route": route, "alternative": alternative}



class Api:
    """Dispatch of the operations of the contract by method and path."""

    ROUTES = [
        ("POST", r"^/api/routes$", "plan_route"),
        ("POST", r"^/api/address-search$", "search_address"),
        ("GET", r"^/api/osm-copy$", "read_osm_copy"),
        ("POST", r"^/api/facts/in-area$", "list_facts_in_area"),
        ("POST", r"^/api/facts/nearby$", "find_nearby_facts"),
        ("GET", r"^/api/facts/(\d+)$", "read_fact"),
        ("POST", r"^/api/facts$", "create_fact"),
        ("POST", r"^/api/facts/(\d+)/votes$", "cast_vote"),
        ("POST", r"^/api/facts/(\d+)/flag$", "flag_fact"),
        ("POST", r"^/api/accounts$", "create_account"),
        ("POST", r"^/api/sessions$", "log_in"),
        ("GET", r"^/api/accounts/me$", "read_own_account"),
        ("DELETE", r"^/api/accounts/me$", "delete_own_account"),
        ("GET", r"^/api/moderation/flagged-facts$", "list_flagged_facts"),
        ("POST", r"^/api/moderation/flagged-facts/(\d+)/hide$", "hide_fact"),
        ("POST", r"^/api/moderation/flagged-facts/(\d+)/restore$", "restore_fact"),
    ]
    NO_TOKEN = ("plan_route", "search_address", "create_account", "log_in")
    TOKEN_REQUIRED = ("read_own_account", "delete_own_account", "list_flagged_facts", "hide_fact", "restore_fact")
    MODERATOR = ("list_flagged_facts", "hide_fact", "restore_fact")
    NO_BODY = ("read_osm_copy", "read_fact", "flag_fact", "read_own_account", "delete_own_account",
               "list_flagged_facts", "hide_fact", "restore_fact")

    def __init__(self, store):
        self.s = store
        self.router = Router(store)
        self.compiled = [(m, re.compile(p), name) for m, p, name in self.ROUTES]

    def handle(self, method, path, headers, raw_body, person_hint):
        """Returns (operation name, status, body dict or None, extra headers)."""
        op, args = None, ()
        for m, rx, name in self.compiled:
            match = rx.match(path)
            if match and m == method:
                op, args = name, match.groups()
                break
        if op is None:
            raise ApiError(404, "not_found")
        try:
            return self.run(op, args, method, headers, raw_body, person_hint)
        except ApiError as e:
            e.op = op
            raise

    def run(self, op, args, method, headers, raw_body, person_hint):
        account = None
        auth = headers.get("Authorization")
        if op not in self.NO_TOKEN and auth is not None:
            token = auth[7:] if auth.startswith("Bearer ") else ""
            account = self.s.account_of(token)
            if account is None:
                raise ApiError(401, "session_expired")
        try:
            if op in self.TOKEN_REQUIRED and account is None:
                raise ApiError(401, "authentication_required")
            if op in self.MODERATOR and not account["is_moderator"]:
                raise ApiError(403, "moderator_role_required")
            body = None
            if op not in self.NO_BODY:
                try:
                    body = json.loads(raw_body.decode("utf-8")) if raw_body else None
                except (UnicodeDecodeError, json.JSONDecodeError):
                    raise invalid("")
            person = ("account:%d" % account["id"]) if account else ("anon:" + person_hint)
            status, out, extra = getattr(self, op)(body, args, account, person)
        except ApiError as e:
            if account is not None and account["id"] in self.s.accounts:
                e.headers = {"Session-Token": self.s.token(account)}
            raise
        if account is not None and op != "delete_own_account":
            extra = dict(extra)
            extra["Session-Token"] = self.s.token(account)
        return op, status, out, extra


    def plan_route(self, body, _args, _acc, _person):
        check_fields(body, ("start", "destination", "avoid", "need"))
        start = check_point(body["start"], "start")
        dest = check_point(body["destination"], "destination")
        avoid = check_type_list(body["avoid"], "avoid", BARRIERS)
        need = check_type_list(body["need"], "need", AMENITIES)
        return 200, self.router.plan(start, dest, avoid, need), {}

    def search_address(self, body, _args, _acc, _person):
        check_fields(body, ("text",))
        text = body["text"]
        if not isinstance(text, str):
            raise invalid("text")
        words = [w for w in text.split() if w.casefold() not in ("ul.", "ulica")]
        if len(text) > 200 or not words:
            raise ApiError(422, "invalid_search_text")
        q = " ".join(words).casefold()
        matches = [{"label": label, "point": {"lat": lat, "lon": lon}}
                   for label, lat, lon in PLACES if q in label.casefold()]
        for name, edges in self.s.net.names.items():
            if len(matches) >= 10:
                break
            if q in name.casefold():
                e = max(edges, key=lambda i: self.s.net.edges[i][2])
                lat, lon = self.s.net.edge_point(e, 0.5)
                matches.append({"label": "%s, Kraków" % name, "point": {"lat": round(lat, 7), "lon": round(lon, 7)}})
        return 200, {"matches": matches[:10]}, {}

    def read_osm_copy(self, _body, _args, _acc, _person):
        return 200, {"date": self.s.osm_copy_date}, {}


    def list_facts_in_area(self, body, _args, _acc, _person):
        check_fields(body, ("south_west", "north_east"))
        s, w = check_point(body["south_west"], "south_west")
        n, e = check_point(body["north_east"], "north_east")
        if s >= n or w >= e:
            raise invalid("south_west", "north_east")
        found = [f for f in self.s.facts.values()
                 if not f.is_hidden and not f.is_removed_from_osm and s <= f.lat <= n and w <= f.lon <= e]
        return 200, {"facts": [f.to_json() for f in found[:1000]], "is_truncated": len(found) > 1000}, {}

    def read_fact(self, _body, args, _acc, _person):
        return 200, {"fact": self.s.visible(int(args[0])).to_json()}, {}

    def find_nearby_facts(self, body, _args, _acc, _person):
        check_fields(body, ("type", "point"))
        if body["type"] not in BARRIERS + AMENITIES:
            raise invalid("type")
        lat, lon = check_point(body["point"], "point")
        near = [(f, d) for f, d in self.s.facts_near(lat, lon, 15.0) if f.type == body["type"] and not f.is_hidden]
        near.sort(key=lambda t: t[1])
        return 200, {"facts": [{"fact": f.to_json(), "distance_m": int(round(d))} for f, d in near]}, {}

    def create_fact(self, body, _args, acc, person):
        check_fields(body, ("idempotency_key", "type", "point"), ("description", "step_count", "geozone_radius_m"))
        key = body["idempotency_key"]
        try:
            if not isinstance(key, str) or not UUID_RE.match(key):
                raise ValueError("not a UUID")
        except ValueError:
            raise invalid("idempotency_key")
        ftype = body["type"]
        if ftype not in BARRIERS + AMENITIES:
            raise invalid("type")
        lat, lon = check_point(body["point"], "point")
        desc = body.get("description")
        if desc is not None:
            if not isinstance(desc, str) or len(desc.strip()) > 500:
                raise invalid("description")
            desc = desc.strip() or None
        steps = body.get("step_count")
        if steps is not None:
            if isinstance(steps, bool) or not isinstance(steps, int) or not (1 <= steps <= 999) or ftype != "stairs":
                raise invalid("step_count")
        radius = body.get("geozone_radius_m")
        if radius is not None:
            if isinstance(radius, bool) or not isinstance(radius, int) or radius not in GEOZONE_RADII or ftype not in BARRIERS:
                raise invalid("geozone_radius_m")
        content = json.dumps([ftype, lat, lon, desc, steps, radius])
        known = self.s.idempotency.get(key)
        if known is not None:
            if known[0] != content:
                raise ApiError(409, "idempotency_key_reused")
            return 200, {"fact": self.s.facts[known[1]].to_json()}, {}
        f = self.s.new_fact(ftype, lat, lon, "user_report", now())
        f.description = desc
        f.step_count = steps
        f.geozone_radius_m = radius
        f.votes.append({"person": person, "verdict": "confirm", "weight": 1 if acc else 0.5, "at": now()})
        self.s.idempotency[key] = (content, f.id)
        return 201, {"fact": f.to_json()}, {}

    def cast_vote(self, body, args, acc, person):
        check_fields(body, ("verdict",))
        if body["verdict"] not in ("confirm", "deny"):
            raise invalid("verdict")
        f = self.s.visible(int(args[0]))
        mine = [v for v in f.votes if v["person"] == person]
        if mine:
            last = max(v["at"] for v in mine)
            if now() - last < timedelta(days=1):
                raise ApiError(409, "vote_too_soon", repeat_allowed_at=instant(last + timedelta(days=1)))
        f.votes.append({"person": person, "verdict": body["verdict"], "weight": 1 if acc else 0.5, "at": now()})
        return 201, {"fact": f.to_json()}, {}

    def flag_fact(self, _body, args, _acc, _person):
        f = self.s.visible(int(args[0]))
        if f.source == "openstreetmap":
            raise ApiError(409, "fact_not_flaggable")
        f.flagged_on = now()
        return 204, None, {}


    def create_account(self, body, _args, _acc, _person):
        check_fields(body, ("pseudonym", "password"))
        p, pw = body["pseudonym"], body["password"]
        if not isinstance(p, str) or not pseudonym_ok(p):
            raise invalid("pseudonym")
        if not isinstance(pw, str) or not (5 <= len(pw) <= 128):
            raise invalid("password")
        if self.s.find_account(p) is not None:
            raise ApiError(409, "pseudonym_taken")
        acc = self.s.add_account(p.strip(" "), pw)
        return 201, {"account": {"pseudonym": acc["pseudonym"], "is_moderator": False}}, {}

    def log_in(self, body, _args, _acc, _person):
        check_fields(body, ("pseudonym", "password"))
        p, pw = body["pseudonym"], body["password"]
        if not isinstance(p, str):
            raise invalid("pseudonym")
        if not isinstance(pw, str):
            raise invalid("password")
        acc = self.s.find_account(p)
        if acc is None or not hmac.compare_digest(
                acc["hash"], hashlib.pbkdf2_hmac("sha256", pw.encode(), acc["salt"], 20000)):
            raise ApiError(401, "invalid_credentials")
        return 200, {"account": {"pseudonym": acc["pseudonym"], "is_moderator": acc["is_moderator"]}}, \
            {"Session-Token": self.s.token(acc)}

    def read_own_account(self, _body, _args, acc, _person):
        return 200, {"account": {"pseudonym": acc["pseudonym"], "is_moderator": acc["is_moderator"]}}, {}

    def delete_own_account(self, _body, _args, acc, _person):
        person = "account:%d" % acc["id"]
        detached = "deleted:%s" % secrets.token_hex(4)
        for f in self.s.facts.values():
            for i, v in enumerate(f.votes):
                if v["person"] == person:
                    v["person"] = "%s:%d" % (detached, i)
        del self.s.accounts[acc["id"]]
        return 204, None, {}


    def flagged_item(self, f):
        return {"fact": f.to_json(), "flagged_on": day(f.flagged_on), "is_hidden": f.is_hidden}

    def list_flagged_facts(self, _body, _args, _acc, _person):
        flagged = sorted((f for f in self.s.facts.values() if f.flagged_on is not None),
                         key=lambda f: f.flagged_on, reverse=True)
        return 200, {"facts": [self.flagged_item(f) for f in flagged]}, {}

    def moderated(self, fid):
        f = self.s.facts.get(fid)
        if f is None:
            raise ApiError(404, "fact_not_found")
        if f.flagged_on is None:
            raise ApiError(409, "fact_not_flagged")
        return f

    def hide_fact(self, _body, args, _acc, _person):
        f = self.moderated(int(args[0]))
        f.is_hidden = True
        return 200, self.flagged_item(f), {}

    def restore_fact(self, _body, args, _acc, _person):
        f = self.moderated(int(args[0]))
        f.is_hidden = False
        return 200, self.flagged_item(f), {}
