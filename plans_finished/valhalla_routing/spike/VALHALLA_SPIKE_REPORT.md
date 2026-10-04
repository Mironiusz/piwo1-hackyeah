# Valhalla spike - accessible walking routes in Kraków

Copied on 2026-10-04 from the directory of the spike, run by the user outside the repository on 2026-10-03 - 2026-10-04. Characters forbidden by `docs/standards/standard_formatting.md` were replaced by their plain forms and bold was removed; the content is otherwise unchanged. The scripts, raw results and configuration the text refers to were not copied; the two patches are next to this file.

Date: 2026-10-03, 22:31-23:17 CEST, plus a follow-up 23:24-00:06 that patched Valhalla for rule 5 (section 6). Valhalla 3.9.0 (official image `ghcr.io/valhalla/valhalla:3.9.0`).
Every container was capped at 4 CPUs and 4 GB RAM to mimic the target server. The host had 12 cores and 14 GB, but only 3-8 GB was free during the run.
Python 3.12 was used (3.13 isn't installed here), with pyosmium 4.3.1, scipy 1.18 and shapely 2.1.
Nothing was sent to any public routing service. Everything ran on `127.0.0.1`.

Everything is in `valhalla-spike/`. Scripts are in `scripts/`, raw numbers in `results/`, the time log in `TIMELOG.md`, and the Compose sketch in `docker-compose.yml`.

---

## 1. Steps and wall-clock time

The wall-clock figures are the agent's own time, including reading Valhalla source, writing scripts and debugging. End times were taken with `date` as the work happened.

| #   | Step                                                                                        | Elapsed | What blocked or slowed it                                                                  |
| --- | ------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------ |
| 0   | Environment check                                                                           | 0:08    | Only ~2.9 GB RAM free at start (swap full). Python 3.12, not 3.13                          |
| 1   | Downloads (PBF 202 MB, GTFS 28 MB), image pull, venv                                        | 1:20    | -                                                                                          |
| 2   | Builder image (Valhalla + osmium-tool), bbox cut                                            | 0:11    | The container wrote root-owned files, so later runs use `--user`                           |
| 3   | Read Valhalla's Lua and pedestrian costing source; write and run the rule-1 filter          | 5:01    | ~1 min lost to a desktop-app restart; one pyosmium API slip                                |
| 4   | Config, timezones, `build_tiles`, tile extract                                              | 1:09    | Found that `include_platforms=false` is the default (it drops `highway=platform`)          |
| 5   | Start the service, pick the 5/15/30 km pairs, read the loki exclusion code, write the bench | 2:35    | Default limits are too low: 50 `exclude_locations`, 100 polygon vertices                   |
| 6   | Rule-2 bench and scaling test                                                               | 1:14    | -                                                                                          |
| 7   | Rule-3 prototype, rule-4 `trace_attributes`                                                 | 5:25    | The exact fallback first failed. loki's `node_snap_tolerance` (5 m) blocks whole junctions |
| 8   | Rule-3 stress test (2.5 km enclosure)                                                       | 0:20    | -                                                                                          |
| 9   | Rule 5: GTFS analysis, transit source reading, GTFS preprocessor                            | 1:53    | Valhalla treats only the value `1` as accessible; tram `route_type` 900 is unsupported     |
| 10  | `valhalla_ingest_transit`                                                                   | 2:36    | Peak 3.83 GB against the 4 GB limit                                                        |
| 11  | `convert_transit` and `build_tiles` with transit                                            | 3:58    | Misleading `ERROR ... 2,485,997 stop pairs with invalid service dates` (routes still work) |
| 12  | Multimodal route; exclusions on walking legs                                                | 3:40    | Exclusions are ignored on multimodal walking legs                                          |
| 13  | `linear_cost_factors` experiment (soft barriers)                                            | 7:44    | Unreliable for pedestrian barriers in both directions; abandoned                           |
| 14  | GTFS accessibility variant, wheelchair type, `edge_walk` robustness                         | 1:52    | Variant build: 264 s machine time, run in the background                                   |
| 15  | Clean RAM re-measurement                                                                    | 1:34    | -                                                                                          |
| 16  | Report and Compose sketch                                                                   | 5:26    | -                                                                                          |
|     | Total                                                                                       | 46:06   |                                                                                            |

These times are for an agent that reads C++ and Lua quickly and works with no meetings. A team doing the same exploration should expect roughly 1.5-2 working days for the spike itself. The estimates in section 4 are for the team, not for the agent.

---

## 2. Measurements

### A. Setup and build (walking only)

| Item                                       | Value                                                                                                                                                                                               |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bbox cut (`osmium extract`, complete ways) | 9.2 s, 202 MB -> 39.6 MB (3.85 M nodes, 625 k ways)                                                                                                                                                 |
| Rule-1 filter (pyosmium, 2 passes)         | 19 s with the default location index, 42 s with `sparse_mem_array`. Peak RSS 2.1 GB                                                                                                                 |
| Filter output                              | 166,000 network ways, 636 k nodes, 8.5 MB PBF                                                                                                                                                       |
| Excluded by the rule                       | `access=private` 19,235 , `sidewalk=separate` 4,903 , `foot=no` 995 , `access=no` 969 , cycleway without foot 896 , `foot=use_sidepath` 836 , construction 492 , motorway (+link) 711 , others ~600 |
| Timezone DB                                | 6 s, 116 MB                                                                                                                                                                                         |
| `valhalla_build_tiles`                     | 9.8 s, peak cgroup memory 827 MB (includes page cache)                                                                                                                                              |
| Tiles on disk                              | 58 MB (tar extract 58 MB)                                                                                                                                                                           |
| `valhalla_service` RAM                     | 96-107 MiB idle, 404-543 MiB peak under the rule-2/3 workloads. It grew to 2.1 GiB after the pathological whole-graph searches in step 13 (`thor.clear_reserved_memory` is false by default)        |

### B. Rule 2: 200 geozones + 2000 point barriers in one request

Barriers are real OSM facts from the network within 500 m of the routes: 954 bad-surface stretches, 921 steps, 111 kerbs and a few narrow/steep/turnstile. Geozones are 100 placed on the routes and 100 random, with radii 10/25/50/100 m, sent as circumscribed 16-gons. Latency is the median of 5 sequential requests, end to end from Python (including ~360 KB of JSON).

| Route                    | Baseline        | Zones only | Zones + 2000 barriers (`exclude_locations`) | Zones + barriers as tiny polygons | Barriers / zones crossed |
| ------------------------ | --------------- | ---------- | ------------------------------------------- | --------------------------------- | ------------------------ |
| R5 Rynek -> Tauron Arena | 4.58 km, 18 ms  | 71 ms      | 4.91 km, 558 ms                             | 491 ms                            | baseline 8 / 24 -> 0 / 0 |
| R15 Bronowice -> Mogiła  | 14.09 km, 62 ms | 117 ms     | 14.64 km, 597 ms                            | 540 ms                            | 8 / 30 -> 0 / 0          |
| R30 Tyniec -> Wyciąże    | 28.84 km, 56 ms | 131 ms     | 30.84 km, 610 ms                            | 547 ms                            | 3 / 24 -> 0 / 0          |

- Cost scales linearly at ~0.25 ms per barrier (250 -> 59 ms, 1000 -> 228 ms, 2000 -> 514 ms), with no real difference between locations and polygons. Each request re-snaps every barrier.
- Every request takes effect immediately; no tile rebuild is involved.
- Correction from the follow-up: the numbers above sent every barrier with `node_snap_tolerance: 0`. That is wrong for barriers that sit exactly on an OSM node (kerbs): a point on a junction then excludes only 2 of its directed edges, i.e. one direction of travel. Re-run with node barriers at 1 m (whole node blocked) and stretch barriers at the midpoint of a segment, verified by Valhalla edge ids: 0 barriers / 0 zones crossed, 576 / 615 / 609 ms (`results/rule2_bench_v2.json`).

### C. Rule 3: every path crosses a barrier

Test case: the destination (Tauron Arena) is enclosed by two complete rings of barriers (150 m and 400 m; 107 barriers). Those are added on top of the 2000 barriers and 200 zones, so the optimum is 2 barriers.

| Approach                                                                                                                                                                                                                          | Valhalla calls | Latency                                                        | Result                                            |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| B - exact (prototyped, recommended). Strict call -> 442 -> lexicographic Dijkstra (barriers x 10⁶ + metres) on our own scipy copy of the filtered network -> one Valhalla call with every barrier excluded except the chosen ones | 2 + graph      | 1.31-1.48 s (strict 0.59 s, graph 0.13-0.30 s, relaxed 0.59 s) | 2 barriers (one per ring), 5.35 km, 0 zones       |
| B, stress: 2.5 km enclosure (422 + 2000 barriers) from Bronowice                                                                                                                                                                  | 2 + graph      | 1.72-1.84 s (the strict call takes 0.81 s to fail)             | 1 barrier, 10.1 km                                |
| A - Valhalla only. Relax all barriers, try single relaxations, then a greedy deletion filter                                                                                                                                      | 13             | 5.5-5.8 s                                                      | 2 barriers, 5.05 km. Not guaranteed to be minimal |
| `linear_cost_factors` (native soft penalty, one call)                                                                                                                                                                             | 1              | 3.9-5.2 s                                                      | Wrong. It still crossed 1-6 barriers (see E/F)    |

Graph copy for B: built in 3.9 s from the same 8.5 MB PBF (636 k nodes, 691 k segments). The FastAPI process grew to ~630 MB RSS (this can be trimmed).

### D. Rule 4: segment -> OSM ids

`trace_attributes` with `shape_match: edge_walk` on the returned shape takes 6-11 ms (169 edges for R5). Each edge carries:

```json
{
  "way_id": 244622823,
  "node_id": 1913875698,
  "end_node": { "node_id": 2519190132, "type": "street_intersection" },
  "begin_shape_index": 9,
  "end_shape_index": 24,
  "length": 0.104,
  "names": ["Plac Mariacki"],
  "use": "footway",
  "surface": "paved"
}
```

- `node_id` / `end_node.node_id` are the OSM ids of the edge's start and end graph nodes. They need `mjolnir.keep_osm_node_ids=true` at build time.
- `/locate?verbose=true` also returns all OSM node ids along an edge (with `keep_all_osm_node_ids=true`).
- `edge_walk` failed on 1 of 40 random routes (error 443). `walk_or_snap` matched that route completely. Trace with exactly the same costing options as the route request.

### E. Rule 5: public transport (GTFS -> transit tiles)

| Item                                              | Value                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Feeds                                             | Trams: 352 stops, 15 k trips. MPK buses: 2,984 stops, 86 k trips. Mobilis: 767 stops, 23 k trips. 2.7 M stop_times. `calendar.txt` is all zeros; service comes only from `calendar_dates`                                                                                                                  |
| GTFS preprocessing (our code)                     | Accessibility: empty/0 -> `1`, keep `2`. `route_type` 900 -> 0 (tram)                                                                                                                                                                                                                                      |
| `valhalla_ingest_transit`                         | 137 s, peak 3.83 GB (3.85 GB in the second build)                                                                                                                                                                                                                                                          |
| `valhalla_convert_transit`                        | 57 s, peak 1.29 GB                                                                                                                                                                                                                                                                                         |
| `build_tiles` with transit (+ extract)            | 61 s, peak 0.94 GB (the transit builder is 50 s of that). Tiles 102 MB, intermediate transit files 579 MB                                                                                                                                                                                                  |
| Full transit rebuild                              | ≈ 4.4 min machine time                                                                                                                                                                                                                                                                                     |
| Multimodal Rondo Mogilskie -> Tauron Arena, "now" | Tram 15 -> Os. Piastów, 3 stops, 2.81 km, 16-17 min, 233 ms (later calls 68-166 ms). Departure times are correct Europe/Warsaw (+02:00 in Oct, +01:00 in Nov)                                                                                                                                              |
| Coverage                                          | ZTP trams, MPK buses and Mobilis buses all appear in routes. Saturday, Sunday and weekday departures work up to 2026-11-30. From 2026-12-03 the request fails with "No path could be found": Valhalla stores only a 60-day schedule from the build date, and multimodal then does not fall back to walking |

| Rule-5 check                                   | Result (evidence)                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rule 1 on walking legs                         | Yes: same tiles, same network                                                                                                                                                                                                                                                                                                                                                               |
| Exclusions (rule 2) on walking legs            | Stock: no. The route is byte-identical with and without `exclude_locations` / `exclude_polygons` and passes through the excluded point. The pedestrian-only control on the same tiles detours (0.766 -> 0.788 km). Source: `loki/worker.cc` `parse_costing()` attaches the excluded edges to `costings[multimodal]`, while thor walks with `costings[pedestrian]`. Patched: yes (section 6) |
| Pedestrian options on walking legs             | Yes: `walking_speed` 2 km/h changes 16 -> 33 min; `type: wheelchair` changes the travel type                                                                                                                                                                                                                                                                                                |
| Trip accessibility (`wheelchair_accessible=2`) | Yes, with `transit.wheelchair=true`, after our 0/empty -> 1 rewrite. In the variant feed, line 15 marked 2 -> tram 5 is used instead. Without the rewrite every trip would count as inaccessible (`ingest_transit.cc:575`: only `TripAccess::Yes`)                                                                                                                                          |
| Stop accessibility (`wheelchair_boarding=2`)   | Stock: only with pedestrian `type: wheelchair`. With `transit.wheelchair=true` alone the route still boards at a stop marked 2. With `type: wheelchair` it walks to Lubicz and takes tram 12 - but that switches on Valhalla's own wheelchair barrier rules (see F). Patched: yes with `type: foot` (section 6)                                                                             |

---

## 3. Per rule: what works, what doesn't, what needs our code

| Rule                    | Status with stock Valhalla 3.9.0                                                                                                                                                                               | Our code needed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Network               | Works, with a PBF pre-filter and three config flags                                                                                                                                                            | The pyosmium filter (same predicate as our PostGIS importer, unit-tested). It sets `foot=yes` on network ways, drops non-network ways, strips `access`/`sac_scale`/`foot:*`/`*:conditional`/`smoothness=impassable`, removes `area=yes` (except pedestrian), and whitelists node tags so Valhalla never blocks a node itself. Config: `include_platforms=true`, `keep_osm_node_ids=true`, `keep_all_osm_node_ids=true`. Why a pre-filter and not a custom `graph.lua`: one Python predicate shared with the DB importer and tests, and stock Lua (2,489 lines) on Valhalla upgrades. Remaining engine decisions: escalators (`conveying` + `oneway`) stay one-way; pedestrian areas are routed along their outline (`pedestrian_areas=false`; enabling it would create edges without OSM ids)                                                                                                             |
| 2 Per-request avoidance | Works, ~0.6 s for 2000 + 200                                                                                                                                                                                   | Request builder from DB facts. Raise `max_exclude_locations` (50 -> 5000), `max_exclude_polygons_length` (10 km -> 1000 km) and `max_exclude_polygons_vertices` (100 -> 50 000). Send `radius: 0`, `minimum_reachability: 0` and `node_snap_tolerance` per barrier type: 0 for a barrier on a way stretch (sent as the midpoint of a segment, never on a node; the default 5 m would exclude 6-10 edges of a nearby junction), 1 m for a barrier on an OSM node (with 0 a point exactly on a junction excludes only one direction of travel). Never send a geozone that contains the origin or destination (no route at all otherwise). Verify every route afterwards (rule 4 ids against barrier edge ids): loki silently drops the whole `exclude_locations` set if the lookup throws (`catch (...) { LOG_WARN }`). Prefer sending only barriers in the O-D corridor, since cost is 0.25 ms per barrier |
| 3 Fewest barriers       | Not available natively (exclusions are hard). `linear_cost_factors` exist but failed (below)                                                                                                                   | Approach B: ~250 lines of Python with scipy plus the 2-call flow, 1.3-1.8 s measured. Map barriers to graph arcs by OSM ids when barriers change. Consistency check against Valhalla, and a plain error if the relaxed call still fails                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 4 Attribution           | Works (`trace_attributes`: way id, begin/end OSM node id, shape indices)                                                                                                                                       | One extra call per leg (~10 ms). `walk_or_snap` retry on error 443. Join with our facts                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 5 Transit               | Stock: partial. Walking legs ignore exclusions and stop accessibility needs `type: wheelchair`. With our two patches (section 6): works - exclusions, trip and stop accessibility in one request, `type: foot` | GTFS preprocessing (done). Patched Valhalla image (Dockerfile done). A rebuild at least every 60 days and on every feed update, on a machine with more than 4 GB. A walking fallback when multimodal finds no transit. Clean-up of transit leg geometry (GTFS shape artefact, section 6)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

### F. Where Valhalla's pedestrian costing decides barriers on its own (from the 3.9.0 source and tests)

- `type: wheelchair` excludes:
  - edges without wheelchair access (e.g. steps: 1 -> 0 steps on R5);
  - surfaces worse than `compacted`;
  - any `sac_scale` way.

  It also adds `step_penalty` 600 s and a fixed 4 km/h speed. Its `max_distance` is capped at 10 km in code, but that check doesn't fire (14 km and 29 km wheelchair routes succeed). `pedestriancost.cc` l.687 reads `((!allow_transit_connections_ && dist) > max_distance_)`, which looks like a precedence slip. Don't rely on either behaviour. Use `type: foot`.

- `max_grade` has no effect at all: the check is commented out in `Allowed()`. There is also no elevation data in our build, so inclines must come from our rules.
- `max_hiking_difficulty` defaults to T1, so `sac_scale` ≥ T2 ways are silently excluded. We strip `sac_scale` and send 6.
- `step_penalty` (30 s for foot), `alley_factor` 2, `driveway_factor` 5, `use_living_streets` and `elevator_penalty` are soft preferences. We send neutral values; product decision.
- Surface: `smoothness=impassable` maps to `Surface::kImpassable` and excludes the way even for foot. We strip it.
- Access: Valhalla's own rules differ from ours:
  - `foot=use_sidepath` and `access=private` are walkable in Valhalla;
  - cycleway and bridleway are not;
  - `area=yes` ways are dropped;
  - platforms are dropped by default config;
  - `*:conditional` is evaluated at request time.

  The pre-filter neutralises all of these.

- Node barriers: `barrier=wall/fence/jersey_barrier/debris` and `access=no` on nodes block pedestrians, and gates add a 10 s penalty. We strip node access and barrier tags so these become our DB's per-request barriers.
- Exclusion semantics: see rule 2 (`node_snap_tolerance`, silently swallowed failures).
- Multimodal: `max_multimodal_walking_distance` defaults to 10 km. In stock 3.9.0, `transit.wheelchair` only filters trips; stop accessibility needs `type: wheelchair`, because `transitbuilder.cc` resets every transit node's access to "all" and keeps the stop's wheelchair flag only on the stop's connection edges. Fixed by patch 2 (section 6).

---

## 4. Integration estimate (team hours)

Assumptions: 1-2 developers who know Python, FastAPI, Docker and PostGIS but not Valhalla, starting from this spike's scripts and findings. Includes code review; excludes UI work.

### Walking only (rules 1-4)

| Work package                                                                                                                                                             | Best | Realistic |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | --------- |
| Data pipeline: admin-boundary cut, productionised filter + unit tests, builder image, versioned tile swap, weekly rebuild job                                            | 4    | 8         |
| Docker Compose service, internal network, health check, resource limits                                                                                                  | 1    | 2         |
| Request builder from DB facts: barriers -> points per edge, geozones -> polygons, corridor selection, limits, O/D-inside-zone rules                                      | 4    | 8         |
| Rule-3 fallback: graph load at startup (or from PostGIS), barrier -> arc mapping on barrier change, 2-call flow, consistency checks, memory trimming (630 MB -> ~200 MB) | 8    | 16        |
| Rule-4 attribution: `trace_attributes`, 443 fallback, join with our facts, post-hoc barrier verification                                                                 | 3    | 6         |
| Error handling: Valhalla down or timeout -> plain message, never a guessed route; map error codes 171/442/443/157/167/176                                                | 2    | 4         |
| Tests: unit, integration with a small fixture PBF and Valhalla in CI (~1 min tile build), golden routes, latency budget                                                  | 6    | 12        |
| Ops and docs: monitoring, rebuild schedule, runbook                                                                                                                      | 2    | 4         |
| Total                                                                                                                                                                    | 30 h | 60 h      |

Confidence: medium. The hard unknowns were resolved in the spike: exclusion limits and semantics, attribution, and a working fallback. The remaining risk is product edge cases (origin or destination on a barrier or inside a zone, corridor selection) and the fallback's graph diverging from Valhalla on exotic topology. Realistic range 50-75 h.

### Public transport on top (rule 5) - revised after the patches (section 6)

| Work package                                                                                                                                                                       | Best | Realistic |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | --------- |
| GTFS pipeline: download, preprocess, ingest/convert/build with the patched tools on a machine with more than 4 GB, rebuild every feed update and at least every 60 days, tile swap | 4    | 8         |
| Multimodal request/response mapping (legs, stops, Europe/Warsaw times, "now"), and a walking fallback when no transit is found                                                     | 3    | 6         |
| Patched Valhalla image in CI (Dockerfile exists, ~8 min build), upstream PRs, re-applying on Valhalla upgrades                                                                     | 2    | 5         |
| Rule-3 fallback and rule-4 attribution for walking legs (trace each walking part; connection edges at stops)                                                                       | 3    | 8         |
| Transit leg geometry: clip or replace broken GTFS shapes using stop coordinates                                                                                                    | 1    | 3         |
| Tests, including the stop/exclusion regression cases from section 6                                                                                                                | 3    | 6         |
| Total                                                                                                                                                                              | 16 h | 36 h      |

Confidence: medium. The engine-side blockers are now fixed and measured; the remaining work is ordinary integration. The main lasting cost is owning a patched Valhalla build until the fixes are upstream.

---

## 5. Recommendation for rule 5 within the 4.5 h budget: still NO-GO, but no longer blocked

- With stock Valhalla 3.9.0 a rule-compliant route is impossible: walking legs ignore every per-request exclusion, so a wheelchair user could be sent over steps on the way to a stop (proven in step 12).
- The follow-up fixed that. Two small patches (+67 lines) make exclusions, trip accessibility and stop accessibility work together in one multimodal request with `type: foot`, at +5-12% latency (section 6).
- What remains is ordinary integration of about 16-36 h, still 3-8x the 4.5 h budget. Operations also stay heavier than walking: transit ingest needs ~3.9 GB RAM (the whole target server), tiles are valid for 60 days, and multimodal returns "no path" instead of walking when no schedule is available.

Recommendation: ship walking only (rules 1-4) first. Then do rule 5 as a separate ~2-5 day task on the patched image, and open the upstream PRs early so the fork is temporary.

### Not done or not measured in this spike

- Cut to the administrative boundary (the bbox was used).
- Load/concurrency test (all latencies are sequential on a single connection).
- Load/concurrency test of the patched build; upstream PRs not opened yet.
- The transit leg geometry artefact (section 6) is documented, not fixed.
- `/route` with `format=pbf` as an alternative to `trace_attributes`.
- pgRouting as an alternative for the fallback graph.
- Elevation data.
- Behaviour when Valhalla is down (trivial; covered by the estimate).

---

## 6. Follow-up: patched Valhalla for rule 5 (measured)

Two patches against the 3.9.0 tag, in `patch/` (`multimodal-exclusions.patch`, `stop-accessibility.patch`, `Dockerfile.patched`). Upstream `master` has the same code, so there was nothing to cherry-pick.

| Patch                   | Files                                                                                                                  | What it changes                                                                                                                                                                                                                                                                                                                                             |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Multimodal exclusions | `src/loki/worker.cc` (+43/-14)                                                                                         | loki attached excluded edges only to `costings[multimodal]`, but `CostFactory::CreateModeCosting` walks with the costing built from `costings[pedestrian]`. Excluded edges now go to every costing in `kCostingTypeMapping[costing]` (also fixes `bikeshare` and `auto_pedestrian`).                                                                        |
| 2 Stop accessibility    | `src/thor/multimodal_transit.cc` (+22), `src/mjolnir/convert_transit.cc` (-3), `src/mjolnir/transitbuilder.cc` (+5/-1) | With `transit.wheelchair=true`, nobody boards, alights or transfers at a platform with `wheelchair_boarding` ≠ 1; riding through on the same vehicle stays allowed. `transitbuilder` keeps the stop's wheelchair bit on the transit node instead of resetting it, and `convert_transit` no longer marks every stop of an inaccessible trip as inaccessible. |

Build: only `valhalla_service`, `valhalla_convert_transit` and `valhalla_build_tiles`, in a container based on the official image (it ships prime_server headers). 3 min 34 s for the service alone, 5 min 10 s with the data tools (`-j4`, peak ~1.6 GB), 18 s for an incremental rebuild. Road tiles from the stock tools are reused; transit tiles must go through the patched `convert_transit` + `build_tiles`.

Results (same tiles, stock vs patched; walking parts checked against the barriers and zones that were sent):

| Test                                                                               | Stock 3.9.0                         | Patched                                                      |
| ---------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------ |
| One excluded point / 25 m zone on the final walk (Rondo Mogilskie -> Tauron Arena) | ignored, route passes through it    | avoided: walk 0.878 -> 0.899 km                              |
| Rondo Mogilskie -> Tauron Arena, 2000 barriers + 199 zones                         | 7 zones on the walks                | 0 / 0, tram 1 instead of 15, 644-722 ms                      |
| Rynek -> Tyniec, same load                                                         | 1 zone                              | 0 / 0, 741-803 ms                                            |
| Bronowice -> Mogiła, same load                                                     | 1 barrier (steps)                   | 0 / 0, 751-790 ms                                            |
| Board at a stop marked 2, `transit.wheelchair=true`                                | boards there (tram 5)               | walks to Teatr Variété, tram 14                              |
| Alight at a stop marked 2                                                          | alights there (tram 16)             | alights at Cystersów and walks                               |
| Ride through a stop marked 2                                                       | allowed                             | allowed (tram 1)                                             |
| `transit.wheelchair=false`                                                         | -                                   | identical to stock                                           |
| Everything in one request (exclusions + trip 2 + stop 2)                           | 7 zones, boards at the blocked stop | 0 barriers, 0 zones, no blocked stop, no line 15, 623-786 ms |
| Pedestrian-only routes R5/R15/R30 with 2000 + 200                                  | -                                   | byte-identical shapes, same latency (634 / 662 / 654 ms)     |

Latency cost of patch 1 on multimodal requests with 2000 + 200 exclusions: +5-12%. Service RAM after the tests: 650-780 MiB.

New findings on the way:

- Rule-2 builder fix (also for walking): see section 2B. A barrier exactly on a junction needs `node_snap_tolerance` ≥ 1 m to block both directions.
- Geozone containing the origin: the patched multimodal returns "no path", exactly like a walking request with the same exclusions. The request builder must not send such zones (product rule).
- Transit leg geometry artefact: the tram 18 leg towards Czerwone Maki P+R ends with a point at Górka Narodowa, 11 km from the alighting stop (GTFS shape cut). It affects map drawing, not routing. Clip legs to stop coordinates.
- The "invalid service dates" ERROR appears again with the patched tools and is harmless (departures work across the 60-day window).
- Multimodal does return walk-only routes for short trips, but not when there is no schedule at all (the 60-day window case), so keep a pedestrian fallback.

Image: `Dockerfile.patched` built from scratch from the two `.patch` files in 11 min 33 s (apt ~2 min, clone, compile; 659 MB vs 638 MB official). Smoke test on the image itself: the stop tests pass and the exclusion test passes (baseline walks through the point, both exclusion types avoid it).

Wall clock for the follow-up: 29 min for the patches and tests (P1-P8, 23:24-23:53) plus 12 min for the image build and smoke test (P9), with the report updated in parallel. See `TIMELOG.md`.
