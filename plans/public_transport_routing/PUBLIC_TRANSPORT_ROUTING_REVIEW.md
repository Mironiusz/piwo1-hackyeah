# Review: Routes with public transport, the optional feature O9

Document state: 2026-10-04, stage 1 implemented with S-9, review of S-9 ready, stage 2 not started

## Implementation run of 2026-10-04 from 07:04

### Check before implementation

- The shape has a closed interview, regulator C:40, and no open question; the plan has no open question and no TODO.
- Another session works on `route_planning` on the same tree: `data/valhalla.py`, `service/route_requests.py`, `service/route_segments.py`, `service/route_graph.py` and `data/route_network.py` are untracked, and `service/route_planning.py`, `api/route.py` and `valhalla/start_routing_service.py` do not exist. D-1 therefore keeps stage 2, S-10 - S-14, closed; this run covers stage 1 only.
- F-12 was outdated: the specification was at version 16, version 15 written by `plans/route_planning/` and version 16 the name of the product. F-12 was corrected in the plan with the check date 2026-10-04, and S-2 wrote version 17, the next free one, as D-16 says.
- F-5 was imprecise: `apply_workspace_exclusion` grants an inactive lease, and only `apply_workspace_recovery` activates it, after proving that the earlier runs and their database work ended; `apply_import_exclusion` of `data/locks.py` does both under the advisory lock of the import. F-5 was corrected in the plan with the check date 2026-10-04.
- F-23 holds: `valhalla_build_timezones` of the image `valhalla-patched:3.9.0-a11y` downloads the boundaries from GitHub into its working directory and writes the database to its standard output. The image was already built by another session at about 06:56, so S-9 did not rebuild it; `valhalla_build_timezones`, `valhalla_ingest_transit`, `valhalla_convert_transit`, `valhalla_build_config`, `valhalla_build_tiles`, `valhalla_build_extract` and `valhalla_service` are all in `/usr/local/bin`.
- The tram feed fetched at 07:14 still carries `Last-Modified: Thu, 01 Oct 2026 22:59:31 GMT` (F-18). Its files lie flat at the root of the zip, without a byte order mark, with CRLF line ends; `stops.txt` has an empty `wheelchair_boarding`, `trips.txt` has `wheelchair_accessible` 0, and `routes.txt` has `route_type` 900. It also carries `calendar.txt`, `shapes.txt`, `blocks.txt` and `feed_info.txt`. The file stayed in the scratch directory of the session and did not enter the repository.

### Done

- S-1: `docs/product/api_contract.md` - the state line, section Conventions, `route_kind`, `public_transport_unavailable`, `public_transport` of a segment with its example, the row 409 `public_transport_disabled`, and the section Public transport with `read_public_transport`.
- S-2: `docs/product/specification.md` version 17, awaiting the approval of Rafał, which its state line and its entry of Decision provenance say.
- S-3: both entries of O9 of `docs/standards/decision_registry.md` moved to Resolved decisions.
- S-4: `MVP.md` D-12 with seventeen operations, the rows of `osm_import` and of this initiative, section Order and critical path and section Open decisions and confirmations.
- S-5: `docs/deployment/hosted_demo.md`, section Loading the data.
- S-6: `docs/product/views.md`, V-13 and the item on O9 under what no view covers.
- S-7: `FINAL_CHECKLIST.md`, checks 1.4 and 1.5.
- S-8: `PUBLIC_TRANSPORT_ENABLED` in `config/settings.py`, `config/config.py`, `.env.local.example` and `docs/standards/standard_config.md`, with cases in `tests/config/test_settings_cases.py`; `tests/config` passes.

### Deviations from the plan

O-1. `PUBLIC_TRANSPORT_ENABLED` accepts only the exact texts `true` and `false` and the empty template marker, which means `false`; any other text stops the facade with the name of the entry. Agent decision at C:40, without asking: D-5 turns the switch on only for `true`, and the empty marker has to be readable because the template holds only empty markers.

O-2. The row 409 of `plan_route` writes the code and the field names in backticks, as the other rows of the contract do, instead of the plain text of S-1. Agent decision at C:40, without asking.

O-3. `MVP.md`, section Scope, still says the mandatory features of version 15 of the specification, while version 17 changes M7 and M10. No step of the plan names that line, so it was left for Rafał.

### Decisions prepared for S-9, not yet written as code

These are agent decisions at C:40, without asking, taken while reading the code; the next run writes them as they stand or asks the user if one turns out wrong.

- The GTFS step takes `apply_import_exclusion(build_import_engine(...), IMPORT_WORKSPACE_ROOT)` as `service/osm_import.py` does, because no other function activates a workspace lease, and so that it never overlaps an import that moves the pointer `current`. `ImportAlreadyRunning` gives the outcome skipped.
- The service follows the shape of `service/osm_import.py` instead of `apply_gtfs_import(deadline) -> int` of D-10: `worker/gtfs_import.py` builds `GtfsImportSettings` from the facade and maps the result to the exit code, and the service has `apply_gtfs_import_command(settings)` and `apply_gtfs_import(settings, client, deadline) -> GtfsImportResult`; the exit code follows D-10, 0 only when `transit/current` names the copy `current` names, read by a service function, because the worker may not import the data layer.
- The pointer `gtfs/current` reuses `apply_routing_pointer` and `fetch_routing_pointer` of `data/routing_data.py` on `ROUTING_DATA_DIR/gtfs`, since its names are digits; `transit/current` needs its own pattern `[0-9]+-[0-9]+` in `data/transit_build.py`, because the names of D-8 carry a hyphen. `data/routing_data.py` is being changed by another session, so it was not generalized.
- `data/transit_build.py` also gets a preparation directory `transit/.prepare-*` and a placement by rename, so that the pointer is written only after a complete directory is in place; the configuration of D-8 is built in the service, because `build_osm_valhalla_config` lives there and the data layer may not import it.
- `service/gtfs_feeds.py` adds the columns `wheelchair_boarding` and `wheelchair_accessible` when a feed lacks them, reads with `utf-8-sig`, and refuses a member of a zip whose name holds a path separator.

### What is left

- S-9: `data/gtfs_source.py`, `data/gtfs_copy.py`, `data/transit_build.py`, `service/gtfs_feeds.py`, `service/gtfs_import.py`, `worker/gtfs_import.py`, their tests, their sections in the layer documents and their names in `docs/standards/naming_registry.md`.
- `npx --no-install prettier --write` on the changed documents, then `make test` and `make lint-docs`, the review of `implementation-dod-review`, and stage 2 once D-1 opens it.
- Rafał approves version 17 of the specification and the change of the contract; the entry of version 17 then drops "Awaiting the approval of Rafał".
- `.env.local` of every machine needs the line `PUBLIC_TRANSPORT_ENABLED=`, or `tests/architecture/test_environment_contract.py` fails there.

## Implementation run of 2026-10-04 from 07:20

### Check before implementation

- At 07:21 `valhalla/start_routing_service.py` did not exist and `plans/route_planning/ROUTE_PLANNING_REVIEW.md` said its run was interrupted by the usage limit, so D-1 kept stage 2 closed and this run started with S-9.
- The facts S-9 rests on were read again in the code: F-3, F-4, F-5 as corrected, F-6, F-7 and F-8 hold. `config/settings.py` now also requires `SESSION_SIGNING_KEY`, added by another session; it does not touch S-9.

### Done

- S-9: `data/gtfs_source.py`, `data/gtfs_copy.py`, `data/transit_build.py`, `data/routing_directories.py`, `service/gtfs_feeds.py`, `service/gtfs_import.py` and `worker/gtfs_import.py`, with `tests/data/test_gtfs_source_integration.py`, `tests/data/test_gtfs_copy_integration.py`, `tests/data/test_transit_build_integration.py`, `tests/service/test_gtfs_feeds_cases.py`, `tests/service/test_gtfs_import_integration.py`, `tests/worker/test_gtfs_import_cases.py` and the shared invented feeds `tests/common_gtfs_feed.py`.
- The sections GTFS step of `data/DATA.md`, `data/DATA_ALGORITHM.md`, `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md`, and the section Public transport names of `docs/standards/naming_registry.md`.
- The five decisions prepared for S-9 in the run from 07:04 were written as they stood, except the pointer of `gtfs/`, see O-5.

### Deviations from the plan

O-4. `fetch_gtfs_feed` takes the run deadline as a fourth parameter and checks it before the request and between chunks, while D-10 names three parameters. Agent decision at C:40, without asking: the 30-second inactivity limit alone lets a slow server keep one feed going past the 30 minutes of the run, and `docs/standards/standard_errors.md`, section Timeouts, asks for a timeout of the whole run.

O-5. `data/routing_directories.py`, a module the plan does not name, holds the preparation directory, the placement by a rename and the pointer for any parent directory and pattern of names; `gtfs/` and `transit/` both use it, instead of `gtfs/current` reusing `apply_routing_pointer` of `data/routing_data.py` as prepared. Agent decision at C:40, without asking: one mechanism for the two parents of this initiative, while `data/routing_data.py` was being changed by `route_planning`. `data/routing_data.py` keeps its own copy for `copies/`, a duplication to remove once that initiative is done.

O-6. The data of an OpenStreetMap copy and a GTFS copy already placed is reused without a build, with the outcome `reused`. D-10 says the build still runs from a kept GTFS copy; building the same two copies again would collide with the directory of the same name, which never changes after its placement. Agent decision at C:40, without asking.

O-7. A named failure ends the command with 1 even when `transit/current` still names data of the OpenStreetMap copy in use, while D-10 gives 0 whenever the pointer matches. Agent decision at C:40, without asking: a run that failed is not reported as a success; the outcome line still says whether the data in use matches.

O-8. `worker/gtfs_import.py` collects its four paths through `build_osm_import_settings` of `worker/osm_import.py`, so a missing path is named exactly as the import names it (D-11). Agent decision at C:40, without asking.

O-9. A value of `wheelchair_boarding` or `wheelchair_accessible` other than empty, 0, 1 and 2, a `routes.txt` without `route_type`, a `stops.txt` without `stop_id` and a member of a feed with a path in its name refuse the feed with `GtfsFeedError`; D-7 does not name these cases. Agent decision at C:40, without asking: an unknown value is never guessed as accessible.

O-10. The service creates `transit_feeds` and `transit_tiles` in the run workspace before the ingest, and checks that the manifest of the OpenStreetMap copy carries the instant of its name. Agent decision at C:40, without asking: whether `valhalla_ingest_transit` creates its output directory itself was not checked, and creating it is harmless.

O-11. The results carry the outcome `built`, `reused`, `skipped`, `no_gtfs_copy` or `no_osm_copy` and the fetch `fetched`, `failed` or `not_run`, and the service exposes `apply_gtfs_import_run`, `apply_gtfs_fetch`, `apply_transit_data`, `build_transit_valhalla_config` and `fetch_transit_serves_copy_in_use` besides the functions of D-10. `apply_gtfs_import` takes the settings and the HTTPX client next to the deadline and returns a `GtfsImportResult`, in place of `apply_gtfs_import(deadline) -> int` of D-10, and the exit code is made by `worker/gtfs_import.py`, as for the import. Agent decision at C:40, without asking.

O-12. Every fetched feed is prepared by `service/gtfs_feeds.py` in a throwaway directory of the workspace before the copy is placed, and a feed it refuses counts as a failed fetch, so `gtfs/current` never names a copy the build cannot use. D-6 checks only the zip and its files; without this, a feed with a value outside the GTFS reference would become the copy in use and every later run would fail on it. Agent decision at C:40, without asking, taken on Risk 1 of the review below; it costs one more unpacking of the three feeds, a few seconds on the real ones.

O-13. A copy that cannot be stored - a directory that already exists under the same name, a directory or a pointer that cannot be written - raises `RoutingDataError` and ends the run, while a failed, incomplete or refused fetch keeps the earlier copy and the build runs from it. D-10 does not separate the two. Agent decision at C:40, without asking, taken on Risk 2 of the review below: a fault of the storage is not a fault of the source, and the operator has to see it.

O-14. A GTFS copy is named by the instant it is made, read right after the three feeds are fetched and checked, not by the instant the fetch started that D-6 calls fetched_at; the difference is seconds and no reader of the name depends on it. An unexpected failure is reported by its type in the outcome line and then by the shared wrapper with its redacted traceback, as the import does, so such a run writes more than the one line of D-10. Agent decisions at C:40, without asking.

### Found and corrected during the run

- `build_gtfs_published_day` first caught every `ValueError`, so a `ConfigurationError` of the facade, which is a `ValueError`, was reported as a missing `Last-Modified` header. The run on the real feeds showed it; only the parsing of the header is guarded now, and `test_a_configuration_failure_is_not_reported_as_a_header_problem` keeps it so.

### Verification

- The tests of S-9 with `tests/config` and `tests/architecture/test_layer_boundaries.py`: 114 passed before the review; after the fixes of the review the six test files of S-9 gave 56 passed. The whole suite without `critical`, run with `--basetemp` on a short ASCII path, failed only in the two prose checks of `tests/architecture/test_prose_style.py`, every violation under `mobile_app/` (F-31). With the default temporary directory the osmium tests of the importer also fail, because the temporary path of this machine holds a non-ASCII letter (`data/DATA.md`, section Architectural decisions); that is not a change of this run.
- `mypy` and `ruff` report nothing, `bandit` finds no issue in the new modules, `vulture` nothing in them, `deptry` only `mobile_app/`, and prettier reports the changed documents formatted.
- At about 07:35 the fetch, the copy and the preparation ran on the three real feeds in the scratch directory of the session, outside the repository: all three published on 2026-10-02 (F-18), all three intact with every required file, every stop and trip without accessibility information made 1 (352, 2984 and 767 stops; 15361, 86234 and 22644 trips), the 23 tram routes of type 900 made 0, the bus routes kept 3.
- In the image `valhalla-patched:3.9.0-a11y`, `valhalla_build_config` names the keys `mjolnir.transit_dir`, `mjolnir.transit_feeds_dir` and `mjolnir.timezone`, and `valhalla_ingest_transit` and `valhalla_convert_transit` take `-c` with the configuration.
- Not run: a build of the tiles with public transport through this code on Linux, the critical tests, and `make test` on Linux.

### Review of S-9

The review of `implementation-dod-review` ran at about 07:50 on the files of S-9 only, with a separate reviewer for the manual checklists; S-1 - S-8 of the run from 07:04 were not reviewed.

Commands of the map in `docs/standards/standard_review.md`, section Standard - verifying tool map:

- the tests of `standard_agentic_workflow.md`, `standard_agent_docs.md`, `standard_git.md`, `standard_architecture.md` and `standard_config.md`: 111 passed, 3 skipped, the environment files absent on this machine;
- `ruff check .` and `ruff format --check .`: findings only in `mobile_app/` and in files of `route_planning`, none in this change;
- `npx --no-install prettier --check` on the changed documents: formatted;
- `tests/architecture/test_prose_style.py`: the two failures of F-31, every violation under `mobile_app/`;
- `mypy`, also with `--platform linux` on the new modules: no issue; `vulture`: nothing in this change; `deptry .`: only `mobile_app/`;
- `bandit` with medium confidence and `-t B608` on the new modules: no issue; `pip-audit` not needed, no new dependency;
- `pytest`: see Verification above.

Findings and what became of them:

- Blocker: damaged compressed bytes of a feed raised `zlib.error`, which neither `apply_gtfs_feed_validation` nor `apply_gtfs_feed_preparation` caught, so the run ended with an unnamed failure instead of keeping the earlier copy. Fixed: both catch `zlib.error`, with `test_damaged_compressed_bytes_are_a_named_refusal` and a fourth damage case in `tests/data/test_gtfs_copy_integration.py`.
- Risk: `gtfs/current` moved before the rules of D-7 ran. Fixed by O-12, with `test_a_feed_the_rules_refuse_never_becomes_the_copy_in_use`.
- Risk: a storage failure during the placement ended the run, unlike the text of D-10. Kept and recorded as O-13; `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md` say so.
- Risk: `apply_gtfs_feed_validation` and `apply_timezone_validation` only read and refuse, while `standard_naming.md` gives `apply_` to executing a decision. Kept: `apply_*_validation` is the name the repository already gives a validator, in `config/settings.py`, `data/locks.py` and `api/route.py`.
- Improvements: the signature of `apply_gtfs_import` recorded in O-11, the name of a GTFS copy and the extra log lines in O-14 with the documents aligned, and `tests/service/test_gtfs_import_cases.py` renamed to `tests/service/test_gtfs_import_integration.py` with the marker `integration`, because it joins the service with the real data layer (`standard_tests.md`).

Verdict: ready, for S-9 of stage 1 only. Stage 2, S-10 - S-14, is not started, so the initiative is not finished and stays in `plans/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6).

### What is left after this run

- Stage 2, S-10 - S-14. At 07:43 `valhalla/start_routing_service.py` existed, created at 07:31, so the condition of D-1 holds; the session of `route_planning` was still writing `data/valhalla.py`, `valhalla/` and `tests/api/` between 07:31 and 07:42.
- S-14 needs a copy of Kraków, the import and this step run on Linux, and the routing service of `route_planning` S-14.
- Rafał approves version 17 of the specification and the change of the contract.
- `.env.local` of every machine needs the line `PUBLIC_TRANSPORT_ENABLED=`.

## Time box

The hours of work of the people of the team on O9 from 04:32 on 2026-10-04, the work of agents not counted, are recorded here by the people themselves: the person, the time from and to, and what was done. No entry was given to this run.
