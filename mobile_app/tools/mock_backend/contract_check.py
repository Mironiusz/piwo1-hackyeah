"""
Checks a running service against `docs/product/api_contract.md`: every operation once on its success path and on
the errors it names, plus the shared conventions (X-Request-Id, Session-Token renewal, error bodies).

Usage: python3 tools/mock_backend/contract_check.py [base url, default http://127.0.0.1:8090] [moderator password]
Exits with 1 when a check fails. It creates an account, reports and votes, so it is meant for the mock or a
throwaway service, never the hosted demo.
"""

import json
import re
import sys
import urllib.error
import urllib.request
import uuid

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8090"
MOD_PASSWORD = sys.argv[2] if len(sys.argv) > 2 else "moderator"
FACT_KEYS = {"id", "type", "point", "geozone_radius_m", "description", "step_count", "source", "status",
             "is_removed_from_osm", "osm_edited_on", "last_confirmed_on", "is_sample", "can_be_flagged"}
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INSTANT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}$")
failures = []
passed = 0


def call(method, path, body=None, token=None, headers=None):
    data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None), dict(r.headers)
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, (json.loads(raw) if raw else None), dict(e.headers)


def check(name, cond, detail=""):
    global passed
    if cond:
        passed += 1
    else:
        failures.append("%s %s" % (name, detail))
        print("FAIL", name, detail)


def is_fact(f):
    return isinstance(f, dict) and set(f) == FACT_KEYS and all(
        f[k] is None or DAY_RE.match(f[k]) for k in ("osm_edited_on", "last_confirmed_on"))


def main():
    st, body, h = call("GET", "/api/osm-copy", headers={"X-Request-Id": "check-1"})
    check("read_osm_copy", st == 200 and set(body) == {"date"} and (body["date"] is None or DAY_RE.match(body["date"])))
    check("x_request_id kept", h.get("X-Request-Id") == "check-1", str(h.get("X-Request-Id")))
    st, body, h = call("GET", "/api/osm-copy", headers={"X-Request-Id": "bad id!"})
    check("x_request_id replaced", h.get("X-Request-Id") not in (None, "bad id!"))

    st, body, _ = call("GET", "/api/nothing")
    check("not_found", st == 404 and body == {"error": {"code": "not_found"}}, str(body))
    st, body, _ = call("POST", "/api/address-search", b"{not json")
    check("invalid json", st == 422 and body["error"]["code"] == "invalid_request")

    st, body, _ = call("POST", "/api/address-search", {"text": "Tauron Arena"})
    check("search_address", st == 200 and body["matches"] and set(body["matches"][0]) == {"label", "point"})
    st, body, _ = call("POST", "/api/address-search", {"text": "  ul.  "})
    check("invalid_search_text", st == 422 and body["error"]["code"] == "invalid_search_text", str(body))
    st, body, _ = call("POST", "/api/address-search", {"text": "x", "extra": 1})
    check("unknown field", st == 422 and "extra" in body["error"]["fields"], str(body))

    area = {"south_west": {"lat": 50.055, "lon": 19.925}, "north_east": {"lat": 50.075, "lon": 19.995}}
    st, body, _ = call("POST", "/api/facts/in-area", area)
    check("list_facts_in_area", st == 200 and isinstance(body["facts"], list) and body["facts"]
          and all(is_fact(f) for f in body["facts"]) and isinstance(body["is_truncated"], bool))
    facts = body["facts"]
    st, body, _ = call("POST", "/api/facts/in-area", {"south_west": area["north_east"], "north_east": area["south_west"]})
    check("in_area order refused", st == 422 and body["error"]["code"] == "invalid_request")

    some = facts[0]
    st, body, _ = call("GET", "/api/facts/%d" % some["id"])
    check("read_fact", st == 200 and body["fact"]["id"] == some["id"])
    st, body, _ = call("GET", "/api/facts/999999999")
    check("fact_not_found", st == 404 and body["error"]["code"] == "fact_not_found")

    st, body, _ = call("POST", "/api/facts/nearby", {"type": some["type"], "point": some["point"]})
    check("find_nearby_facts", st == 200 and any(x["fact"]["id"] == some["id"] for x in body["facts"])
          and all(isinstance(x["distance_m"], int) for x in body["facts"]))

    for avoid, need in (([], []), (["stairs", "high_kerb", "poor_surface", "narrow_passage"], ["elevator", "ramp",
                                                                                                 "lowered_kerb"])):
        st, body, _ = call("POST", "/api/routes", {"start": {"lat": 50.0617, "lon": 19.9373},
                                                   "destination": {"lat": 50.0678, "lon": 19.9914},
                                                   "avoid": avoid, "need": need})
        ok = st == 200 and set(body) == {"osm_copy_date", "barrier_free_route_exists", "public_transport_unavailable", "route",
                                         "alternative"} and body["public_transport_unavailable"] is False
        if ok:
            r = body["route"]
            ok = set(r) == {"length_m", "segments", "profile_barriers", "additional_barriers", "amenities"} and \
                r["length_m"] > 3000 and all(
                    set(s) == {"line", "length_m", "state", "missing_attributes", "is_marked_wheelchair_no", "public_transport"}
                    and s["public_transport"] is None
                    and s["state"] in ("barrier", "no_barrier", "partial_data", "no_data", "not_assessed") for s in r["segments"])
            if avoid:
                ok = ok and r["segments"][0]["state"] == "no_data" and r["segments"][-1]["state"] == "no_data"
            else:
                ok = ok and all(s["state"] == "not_assessed" for s in r["segments"])
            ok = ok and all({"distance_from_start_m", "is_overruled_by_osm"} <= set(f) for f in
                            r["profile_barriers"] + r["additional_barriers"] + r["amenities"])
            if not avoid:
                ok = ok and all(s["missing_attributes"] == [] for s in r["segments"])
        check("plan_route avoid=%d" % len(avoid), ok, json.dumps(body)[:300])
    st, body, _ = call("POST", "/api/routes", {"start": {"lat": 50.06}, "destination": {"lat": 50.0, "lon": 19.9},
                                               "avoid": [], "need": []})
    check("plan_route invalid", st == 422 and "start" in body["error"]["fields"][0], str(body))
    st, body, _ = call("POST", "/api/routes", {"start": {"lat": 50.0617, "lon": 19.9373}, "destination": {"lat": 52.23, "lon": 21.01},
                                               "avoid": [], "need": []})
    check("point_outside_krakow", st == 422 and body == {"error": {"code": "point_outside_krakow", "points": ["destination"]}}, str(body))
    st, body, _ = call("POST", "/api/routes", {"start": {"lat": 50.0617, "lon": 19.9373}, "destination": {"lat": 50.0678, "lon": 19.9914},
                                               "avoid": [], "need": [], "route_kind": "public_transport"})
    check("public_transport_disabled", st == 409 and body["error"]["code"] == "public_transport_disabled", str(body))
    st, body, _ = call("GET", "/api/public-transport")
    check("read_public_transport", st == 200 and body == {"is_enabled": False, "feeds": []}, str(body))

    pseudo = "Test_%s" % uuid.uuid4().hex[:8]
    st, body, _ = call("POST", "/api/accounts", {"pseudonym": " %s " % pseudo, "password": "haslo1"})
    check("create_account", st == 201 and body == {"account": {"pseudonym": pseudo, "is_moderator": False}}, str(body))
    st, body, _ = call("POST", "/api/accounts", {"pseudonym": pseudo.lower(), "password": "haslo1"})
    check("pseudonym_taken", st == 409 and body["error"]["code"] == "pseudonym_taken")
    st, body, _ = call("POST", "/api/accounts", {"pseudonym": "ab", "password": "haslo1"})
    check("pseudonym rule", st == 422 and body["error"]["fields"] == ["pseudonym"])
    st, body, _ = call("POST", "/api/sessions", {"pseudonym": pseudo, "password": "wrong"})
    check("invalid_credentials", st == 401 and body["error"]["code"] == "invalid_credentials")
    st, body, h = call("POST", "/api/sessions", {"pseudonym": pseudo.upper(), "password": "haslo1"})
    token = h.get("Session-Token")
    check("log_in", st == 200 and token and body["account"]["pseudonym"] == pseudo)
    st, body, h = call("GET", "/api/accounts/me", token=token)
    check("read_own_account", st == 200 and body["account"]["pseudonym"] == pseudo and h.get("Session-Token"))
    st, body, _ = call("GET", "/api/accounts/me")
    check("authentication_required", st == 401 and body["error"]["code"] == "authentication_required")
    st, body, _ = call("GET", "/api/accounts/me", token="garbage")
    check("session_expired", st == 401 and body["error"]["code"] == "session_expired")
    st, body, h = call("POST", "/api/routes", {"start": {"lat": 50.0617, "lon": 19.9373},
                                               "destination": {"lat": 50.0627, "lon": 19.9393}, "avoid": [], "need": []},
                       token=token)
    check("plan_route ignores token", st == 200 and "Session-Token" not in h)

    key = str(uuid.uuid4())
    report = {"idempotency_key": key, "type": "stairs", "point": {"lat": 50.0617, "lon": 19.9373},
              "description": "  Trzy stopnie  ", "step_count": 3, "geozone_radius_m": None}
    st, body, _ = call("POST", "/api/facts", report, token=token)
    new = body["fact"] if st == 201 else None
    check("create_fact", st == 201 and is_fact(new) and new["status"] == "unverified" and new["source"] == "user_report"
          and new["description"] == "Trzy stopnie" and new["last_confirmed_on"] is not None, str(body))
    st, body, _ = call("POST", "/api/facts", report, token=token)
    check("create_fact idempotent", st == 200 and body["fact"]["id"] == new["id"])
    changed = dict(report, step_count=4)
    st, body, _ = call("POST", "/api/facts", changed, token=token)
    check("idempotency_key_reused", st == 409 and body["error"]["code"] == "idempotency_key_reused")
    st, body, _ = call("POST", "/api/facts", dict(report, idempotency_key=str(uuid.uuid4()), type="ramp"))
    check("step_count only for stairs", st == 422 and body["error"]["fields"] == ["step_count"], str(body))

    st, body, _ = call("POST", "/api/facts/%d/votes" % new["id"], {"verdict": "confirm"})
    check("cast_vote anon", st == 201 and body["fact"]["status"] == "unverified", str(body))
    st, body, _ = call("POST", "/api/facts/%d/votes" % new["id"], {"verdict": "deny"})
    check("vote_too_soon", st == 409 and body["error"]["code"] == "vote_too_soon"
          and INSTANT_RE.match(body["error"]["repeat_allowed_at"]) and "T00:00:00.000" in body["error"]["repeat_allowed_at"], str(body))
    st, body, _ = call("POST", "/api/facts/%d/votes" % new["id"], {"verdict": "confirm"}, token=token)
    check("vote_too_soon author", st == 409, str(body))

    osm = next((f for f in facts if f["source"] == "openstreetmap"), None)
    if osm:
        st, body, _ = call("POST", "/api/facts/%d/flag" % osm["id"])
        check("fact_not_flaggable", st == 409 and body["error"]["code"] == "fact_not_flaggable")
    st, body, _ = call("POST", "/api/facts/%d/flag" % new["id"])
    check("flag_fact", st == 204 and body is None)
    st, body, _ = call("GET", "/api/moderation/flagged-facts", token=token)
    check("moderator_role_required", st == 403 and body["error"]["code"] == "moderator_role_required")
    st, _b, h = call("POST", "/api/sessions", {"pseudonym": "moderator", "password": MOD_PASSWORD})
    mod = h.get("Session-Token")
    st, body, _ = call("GET", "/api/moderation/flagged-facts", token=mod)
    check("list_flagged_facts", st == 200 and any(x["fact"]["id"] == new["id"] and DAY_RE.match(x["flagged_on"])
                                                  for x in body["facts"]), str(body)[:200])
    st, body, _ = call("POST", "/api/moderation/flagged-facts/%d/hide" % new["id"], token=mod)
    check("hide_fact", st == 200 and body["is_hidden"] is True)
    st, body, _ = call("GET", "/api/facts/%d" % new["id"])
    check("hidden fact gone", st == 404 and body["error"]["code"] == "fact_not_found")
    st, body, _ = call("POST", "/api/moderation/flagged-facts/%d/restore" % new["id"], token=mod)
    check("restore_fact", st == 200 and body["is_hidden"] is False)
    if osm:
        st, body, _ = call("POST", "/api/moderation/flagged-facts/%d/hide" % osm["id"], token=mod)
        check("fact_not_flagged", st == 409 and body["error"]["code"] == "fact_not_flagged")

    st, body, h = call("GET", "/api/facts/999999999", token=token)
    check("token renewed on error", st == 404 and h.get("Session-Token"), str(h.get("Session-Token")))
    st, body, h = call("GET", "/api/moderation/flagged-facts", token=token)
    check("token renewed on 403", st == 403 and h.get("Session-Token"))
    st, body, h = call("PUT", "/api/facts", {"x": 1})
    check("unknown method is json not_found", st == 404 and body == {"error": {"code": "not_found"}}
          and h.get("X-Request-Id"), str(body))
    st, body, _ = call("POST", "/api/facts", {"idempotency_key": str(uuid.uuid4()), "type": "stairs",
                                              "point": {"lat": 50.0661, "lon": 19.9878}, "geozone_radius_m": 10.5})
    check("geozone radius must be one of the four", st == 422 and body["error"]["fields"] == ["geozone_radius_m"], str(body))
    st, body, _ = call("POST", "/api/facts", {"idempotency_key": uuid.uuid4().hex, "type": "ramp",
                                              "point": {"lat": 50.0661, "lon": 19.9878}})
    check("idempotency key is a hyphenated uuid", st == 422 and body["error"]["fields"] == ["idempotency_key"], str(body))
    st, body, _ = call("POST", "/api/accounts", {"pseudonym": "ab\u00d7cd", "password": "haslo1"})
    check("pseudonym letters only", st == 422 and body["error"]["fields"] == ["pseudonym"], str(body))
    second = None
    for _ in range(2):
        st, _b, _h = call("POST", "/api/facts/%d/flag" % new["id"])
    st, body, _ = call("GET", "/api/moderation/flagged-facts", token=mod)
    check("latest flag first", st == 200 and body["facts"] and body["facts"][0]["fact"]["id"] == new["id"], str(body)[:200])

    states_ok = True
    for avoid in (["stairs"], ["stairs", "high_kerb", "poor_surface", "steep_incline", "narrow_passage"]):
        st, body, _ = call("POST", "/api/routes", {"start": {"lat": 50.0617, "lon": 19.9373},
                                                   "destination": {"lat": 50.0678, "lon": 19.9914},
                                                   "avoid": avoid, "need": []})
        segs = body["route"]["segments"][1:-1]
        if avoid == ["stairs"]:
            states_ok = states_ok and all(s["state"] != "no_data" and "steps" not in s["missing_attributes"] for s in segs)
        states_ok = states_ok and not any(s["is_marked_wheelchair_no"] and s["state"] == "no_barrier" for s in segs)
        for group in ("profile_barriers", "additional_barriers"):
            for f in body["route"][group]:
                if f["is_overruled_by_osm"] and f["source"] != "user_report":
                    states_ok = False
    check("segment states of M7 (steps default, wheelchair=no never green)", states_ok)

    st, body, h = call("DELETE", "/api/accounts/me", token=token)
    check("delete_own_account", st == 204 and body is None and "Session-Token" not in h)
    st, body, _ = call("GET", "/api/accounts/me", token=token)
    check("deleted token expired", st == 401 and body["error"]["code"] == "session_expired")

    print("%d passed, %d failed" % (passed, len(failures)))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
