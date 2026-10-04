# Review: Walking routes of the MVP

Document state: 2026-10-04, initiative closed by the user with S-17 handed over to check 4.1 of FINAL_CHECKLIST.md

## Implementation run of 2026-10-04

Done and green in local runs: S-1 (documents, by a subagent; `MVP.md` not committed yet), S-2, S-3, S-4 code, S-5, S-6, S-9, S-10 - S-13 and S-15 code. Tests added and passing: `tests/service/test_fact_status_cases.py`, `test_route_graph_cases.py`, `test_route_requests_cases.py`, `test_route_segments_cases.py`, `test_route_boundary_cases.py`, `test_route_planning_cases.py`, `tests/data/test_routing_boundary_integration.py`, `tests/data/test_valhalla_integration.py`, the cases of `tests/test_common_time_cases.py` and `tests/config/test_settings_cases.py`.

Not done yet: `tests/api/test_route_integration.py` (S-15 tests); the critical tests of S-4, S-7 and S-8 (`tests/data/test_engine_critical.py`, `test_route_network_critical.py`, `test_route_facts_critical.py`) against the local database started from `db/compose.yaml` as the Compose project `route-planning-db` on port 55432, with invented credentials kept outside the repository; S-14 (overrides, start script, Dockerfile, README; the image `valhalla-patched:3.9.0-a11y` is built and `valhalla_build_config` prints JSON); the importer side of D-20, waiting for the commit of the session of the importer; S-16 (layer documents, naming registry); `make check`; memory entries; the DoD review; S-17.

Agent decisions at C:40, without asking, during the implementation:

- `RoutePoint` lives in `service/route_graph.py`, and `RoutingUnavailableError`, `SegmentState` and `MissingAttribute` in `service/route_segments.py`, instead of `service/route_planning.py` as D-15 names them, because the graph and the segments need them and importing them from `route_planning` would make an import cycle.
- `fetch_osm_boundary` takes the instant of the copy as a second argument, because D-5 asks it to refuse a manifest of another instant.
- `ROUTING_DATA_DIR` was found added by the session of the importer as optional; it was made required as D-7 decides, keeping the one definition and its shared path validators, agreed with that session.
- A segment with no attribute relevant to the profile, a profile of a high kerb alone on a footway that meets no carriageway, is `no_barrier`: nothing relevant is missing (M7, M10).
- A report of the source `user_report` with an OpenStreetMap identity, a converted fact, is placed like any report by its nearest way, so the nearest way is read for every fact of that source.
- A repeated request of the check of D-12 that answers 442 ends with `RoutingUnavailableError`.
- The tests share invented settings through `tests/common_runtime_settings.py`, and `tests/api/conftest.py` uses it.

Noticed and not changed: `MVP.md`, section Scope, names version 15 as S-1 asks, while another session made the specification version 16 the same day; `docs/product/api_contract.md`, plan_route, still says the service does not log the current location without naming the log of the routing service.

## Continuation run of 2026-10-04 from 07:21

### Check before the continuation

- The shape has the regulator C:40 and no open question; the plan has none either.
- Changed on the tree since the first run: `plans/osm_importer/` was finished with the verdict ready and moved to `plans_finished/osm_importer/` by the user, who chose not to wait for D-20 and named this review as the place of its note; `plans/address_search/` moved to `plans_finished/`; `api/accounts.py`, `api/sessions.py` and `api/address_search.py` joined `build_app`; `config/settings.py` gained the required `SESSION_SIGNING_KEY`; `plans/public_transport_routing/` changed `plan_route` in `docs/product/api_contract.md` with `route_kind`, `public_transport_unavailable` and the segment field `public_transport` and wrote version 17 of the specification. None of these changes touches a rule of this plan; the fields of O9 are the stage 2 of that initiative.
- S-1 was confirmed in the files: the contract, the views, the interface texts, version 15 in the specification, both entries of the registry under Resolved decisions, and both rows of `MVP.md`. The item of S-1 on the plan of the importer was never written there; D-20 had already turned it into a note, which stands below because that plan is archived.

### Done in this run

- S-15: `tests/api/test_route_integration.py`, 15 cases.
- S-14: `valhalla/valhalla_overrides.json`, `valhalla/start_routing_service.py`, the `COPY` and `CMD` of `valhalla/Dockerfile`, section Starting the service of `valhalla/README.md`, `tests/service/test_routing_service_config_cases.py` with 9 cases, and the script in `[tool.mypy] files`, `[tool.vulture] paths` and two Bandit passes of the `makefile`. `valhalla_build_config` of the image printed JSON before anything was written, so the gate of S-14 held.
- S-4, S-7 and S-8: `test_read_only_snapshot_refuses_a_write` and `test_statement_timeout_applies_to_the_transaction` in `tests/data/test_engine_critical.py`, `tests/data/test_route_network_critical.py` and `tests/data/test_route_facts_critical.py`, with the fixture `service_transaction` of `tests/data/conftest.py`.
- S-16: `api/API.md` and `api/API_ALGORITHM.md`, new; the section Walking route and the status of a fact of `service/SERVICE.md`, the sections Status of a fact and Walking route of `service/SERVICE_ALGORITHM.md`, the section Walking route of `data/DATA.md` and `data/DATA_ALGORITHM.md`; the section Walking route names of `docs/standards/naming_registry.md`; four memory entries.
- D-20, the boundary only, as the user chose: `ROUTING_BOUNDARY_NAME` is the third name of `ROUTING_FILE_NAMES`, `apply_osm_boundary_file` of `data/routing_data.py` writes the boundary, `OsmPreparedCopy` carries it, and `apply_osm_routing_preparation` writes it before the manifest; the importer tests and documents follow (`service/SERVICE.md`, `service/SERVICE_ALGORITHM.md`, `data/DATA.md`, `data/DATA_ALGORITHM.md`, `docs/import/osm_importer.md`).
- `ruff format` of the files of this initiative the first run left unformatted.

### Runs

- Without a database: the route, boundary, status, settings, API and start script tests pass, and the 73 importer, GTFS and boundary tests that touch the routing directory pass with `--basetemp` on an ASCII path.
- Critical, against the local database of the Compose project `route-planning-db`: the three engine tests and the four route read tests pass.
- The image `valhalla-patched:3.9.0-a11y` rebuilt with the start script: it waited for `current`, started `valhalla_service` on `/data/copies/1790972494/valhalla_tiles.tar`, and `/status` gave `tileset_last_modified` 1790972494, the modification time of the archive. Through `data/valhalla.py` and the bodies of `service/route_requests.py` it answered a route, a trace whose edges carry the way and both OpenStreetMap nodes, a detour around an excluded stretch and 442 for a closed start.
- End to end on an invented grid of eight footways committed into that local database with a stairs fact on the direct way, the routing service on the same tiles and `python -m api`: a profile without barriers gave `not_assessed` on every segment with the stairs in `additional_barriers`; avoiding stairs gave the 438 m detour instead of the 216 m line; avoiding poor surface and high kerbs gave `no_barrier` on the ways; a start outside the boundary gave 422 with `points` `["start"]`, both points `["start", "destination"]`, and a latitude of 91 `invalid_request` with `start.lat`. Each route took 0.2 - 0.4 s, and the request log named `plan_route` with no coordinate.

### Decisions of this run

- User decision of 2026-10-04: D-20 is made for the boundary only. `build_osm_valhalla_config` keeps setting `include_platforms`, `keep_osm_node_ids` and `keep_all_osm_node_ids` itself and does not merge `valhalla/valhalla_overrides.json`, because no image of the backend exists yet to say where the import would find that file. The three keys therefore stand in two places, which `valhalla/README.md` says.
- Agent decision at C:40, without asking: `fetch_osm_boundary` no longer checks that the manifest lists the boundary, because `fetch_osm_routing_manifest` now refuses every manifest without it.
- Agent decision at C:40, without asking: the start script stops with 1 when `current` names no copy or the copy has no tile archive, and with 2 without exactly one argument, writes the configuration to `/opt/enableme/valhalla_service.json` next to itself, and its Bandit pass skips B404, B603, B606 and B607 with the reason in the `makefile`.
- Agent decision at C:40, without asking: `fetch_valhalla_answer` builds its client outside the `try`, because `ConfigurationError` derives from `ValueError` and was reported as an unavailable routing service.
- Agent decision at C:40, without asking: `api/API.md` lists the files of `accounts` and `address_search` in its file structure and leaves their description to those initiatives.

### Not done

- S-17 on Kraków: no copy of Kraków exists locally, and the import runs its Valhalla tools only in a Linux container of the backend image that `plans/deployment_config/` has not built yet; AC-14 needs the hosted demo. The end-to-end run above stands in for it on invented data.

### Noticed and not changed

- A copy prepared before this change has no boundary: its routes end with `routing_unavailable` until a newer extract is imported, which builds a new directory with the boundary.
- With a profile that avoids only stairs, a way whose stairs are absent by default is `no_data` with no missing attribute, as D-13 rules; the end-to-end run showed it, and a client may find an empty list under `no_data` odd.
- `plan_route` refuses `route_kind` as an unknown field until `public_transport_routing` adds it in its stage 2.
- `MVP.md` fails `prettier --check` in the row of `osm_importer` left by its archiving; `mobile_app/` fails the prose, ruff, deptry and prettier checks; `tests/service/test_actors_cases.py` has a vulture finding. None of these is a file of this initiative.
- The local database of `route-planning-db` holds the invented end-to-end copy and must be recreated before the critical import scenario can run on it.

## Review of 2026-10-04 by implementation-dod-review

Scope: the code, tests and documents of S-1 - S-16 and of the boundary part of D-20, from both runs. Three read-only reviewers read the service rules of the route, the segments and the graph, and the data, status, API, configuration and start script; the reviewing session ran the tools of the map.

### Blockers, fixed in this run

Z-1. `service/route_planning.py`, `resolve_alternative`: when no route avoided every barrier, the check of the alternative did not know the barriers the path with the fewest barriers had chosen, counted them as crossed, and the repeated request answered 442, so a valid answer with `barrier_free_route_exists` false ended as `routing_unavailable`. `CheckedRoute` now carries `chosen_ids` and the alternative is checked with them, as D-12 and D-14 decide. `test_alternative_of_the_route_with_the_fewest_barriers_may_cross_the_chosen_ones` covers it and fails without the fix.

Z-2. `service/route_segments.py`, `build_route_facts`: an outdated report whose confirmations reached 2 still replaced the kerb fact of OpenStreetMap, which M4 allows, for example 2 confirmations against 3 denials. A report replaces only when it is not outdated, as D-11 and D-13 leave outdated facts out. `test_outdated_kerb_report_never_replaces_openstreetmap` covers it.

### Other fixes of this run

- Agent decision at C:40, without asking: an answer 442 to any request of the alternative, its repeated request after a crossing included, gives no alternative instead of ending the route, as D-14 says of 442; `resolve_checked_route` now raises 442 to its caller, and the route itself still ends as `routing_unavailable` through `resolve_route`. `test_no_route_for_the_repeated_alternative_request_gives_no_alternative` covers it.
- `service/route_boundary.py`: the cache keeps the instant and the boundary in one entry, so a reader never pairs a new instant with the boundary of the earlier copy.
- `service/route_segments.py`, `build_route_segments`: a shape index of an edge outside the traced shape raises `RoutingUnavailableError` instead of an `IndexError` that would answer 500.
- `geozone_radius_m or 0` in `service/route_planning.py`, `service/route_requests.py` and `service/route_segments.py` became a test of the radius itself, so no fallback stands where the type already says a geozone has a radius.
- `tests/service/test_route_segments_cases.py`: the helper `assess_way` became `resolve_way_assessment`, and `build_whole_way_segment` lost its unused parameter.

### Risks left for a decision

- A report on the stretch where the route starts or ends counts as lying on the route even when it lies behind the start, because D-13 places a report on a stretch while D-12 keeps only the traversed part of the first and last edge. Such a confirmed report triggers the repeated request of D-12, and a second crossing ends the route as `routing_unavailable`. The plan does not settle which rule wins.
- The first route after a change of the copy verifies the manifest, which hashes the tile archive, about 60 MB for Kraków, inside the snapshot of that request; the cache of the boundary is not warmed at start.
- A profile that avoids only stairs gives `no_data` with an empty list of missing attributes on a way whose stairs are absent by default, as D-13 rules.
- AC-1 - AC-14 were not run on Kraków and AC-14 not on the hosted demo (S-17).

### Deviations from the names of the plan

- `fetch_osm_boundary` takes `(directory, state_at)`, not `(directory)` of D-5, because D-5 itself refuses a manifest of another instant.
- `RouteFactView` holds its fact in the field `view`, where D-15 writes `fact`, so that `item.view.fact` reads as the stored fact of the view.
- `RoutePoint` stands in `service/route_graph.py` and `RoutingUnavailableError` in `service/route_segments.py`, as the first run recorded.

### Verification

| Standard                       | State                 | Result                                                                                                                                                                                                                |
| ------------------------------ | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard_agentic_workflow.md` | Checked automatically | `tests/architecture` passes apart from the two prose tests below                                                                                                                                                      |
| `standard_agent_docs.md`       | Checked automatically | `test_plan_document_contract.py` passes                                                                                                                                                                               |
| `standard_review.md`           | Checked manually      | Every standard listed; verdict scoped                                                                                                                                                                                 |
| `standard_documentation.md`    | Checked manually      | The new pair of `api/`, the sections of the route in the documents of `service/` and `data/`, docstrings on every function, no line comment                                                                           |
| `standard_formatting.md`       | Checked automatically | `ruff format --check` clean for every file of this initiative; prettier clean for every changed document; `test_prose_style.py` fails only on `mobile_app/`, and `MVP.md` fails prettier in the row of `osm_importer` |
| `standard_git.md`              | Checked automatically | `test_conflict_markers.py` passes; no add, commit, push or history operation                                                                                                                                          |
| `standard_architecture.md`     | Checked automatically | `test_layer_boundaries.py` passes; `data/valhalla.py` is the one call site of the routing service                                                                                                                     |
| `standard_config.md`           | Checked automatically | `test_environment_contract.py` skips without `.env.local` on this machine, `test_critical_environment_guard.py` passes; the two validators of D-7 have cases                                                          |
| `standard_database.md`         | Checked automatically | Bandit B608 clean; every geometry, distance and list a bound parameter; one visibility predicate                                                                                                                      |
| `standard_errors.md`           | Checked manually      | Z-1 and the shape index fixed; the client of the routing service has a timeout of 2 seconds and retries nothing                                                                                                       |
| `standard_idempotency.md`      | Not applicable        | The route only reads                                                                                                                                                                                                  |
| `standard_code_quality.md`     | Checked automatically | ruff check clean outside `mobile_app/`; mypy clean on 77 sources; vulture finds only `tests/service/test_actors_cases.py` of `accounts`; deptry finds only `mobile_app/`                                              |
| `standard_logging.md`          | Checked automatically | ruff G clean; no entry of the route holds a coordinate, by test and by the end-to-end run                                                                                                                             |
| `standard_naming.md`           | Checked automatically | ruff N clean; prefixes checked by hand after the rename of the test helper; registry updated                                                                                                                          |
| `standard_security.md`         | Checked automatically | `make security` passes with the new pass of the start script; pip-audit finds no known vulnerability with numpy 2.5.3 and scipy 1.18.1                                                                                |
| `standard_tests.md`            | Checked automatically | 842 tests pass outside the critical set with an ASCII base directory, the 2 failures being the prose tests of `mobile_app/`; the 7 critical tests of the route pass on the local database                             |
| `standard_time.md`             | Checked manually      | Instants compared as aware values; the day of a copy and of a confirmation in the business zone                                                                                                                       |
| `standard_worker.md`           | Not applicable        | No worker change                                                                                                                                                                                                      |
| `standard_frontend.md`         | Not applicable        | No frontend change                                                                                                                                                                                                    |

### Verdict

Ready, for the code, tests and documents of S-1 - S-16 and of the boundary part of D-20. Not for the whole initiative: S-17 and with it AC-1 - AC-14 on Kraków and AC-14 on the hosted demo are open, so the directory does not qualify for `plans_finished/` by this verdict.

## Closure

The user chose on 2026-10-04, after the verdict above, to close the initiative now rather than keep it in `plans/` until S-17 can run. S-17 - AC-1 - AC-14 on Kraków and AC-14 on the hosted demo - is handed over to check 4.1 of `FINAL_CHECKLIST.md`, which already asks for the same run on the running service; it waits for a copy of Kraków imported in the backend image of `plans/deployment_config/`. The risks of the review stay open for the user, and a fix that S-17 calls for goes through a resumption under ch. 4.6 of `docs/standards/standard_agentic_workflow.md` or a new initiative. The directory moves to `plans_finished/route_planning/`.
