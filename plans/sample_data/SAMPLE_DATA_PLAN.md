# Plan: Sample reports and geozones for the demo

Document state: 2026-10-04, plan closed

Implementation state: 2026-10-04, not started; the user deferred the implementation of this plan, and the four-example provider of the first plan stays in the tree until S-1 - S-4 replace it

## Goal

Implement the approved `SAMPLE_DATA_PRD.md` in its rewritten form. The goal is eight sample facts with the content of `DemoSeed.ets`, placed on real ways around the proxy route Tauron Arena -> M1 Kraków. They carry 25 fictional votes without an account, the flagged and hidden states of S-6 - S-8 and dates relative to the first successful loading. A repeat-safe service step serves the common demo-loading program. The current product schema and public interface stay. The provider contract of the first plan is kept by name, with one changed failure code.

This plan reuses what the first plan delivered: the records module, the transaction and commit classification, the bound batch statements, the critical-fixture registry and the local-only collection guard. It replaces the dataset, the prerequisite rules and the tests that encode the four examples.

## Facts

F-1. The shape was reopened and closed again on 2026-10-04 at C:40, with Q-3 - Q-7 answered by the user, and the rewritten PRD was approved the same day. | doc:`SAMPLE_DATA_SHAPE.md` state, Current state, functional requirements 6 - 8 and Open questions; doc:`SAMPLE_DATA_PRD.md` state | 2026-10-04
F-2. The content of the eight facts comes from `demoReports`, with the type, steps, description, vote weights and offsets of 0.1 - 2 days, and flags on S-6 - S-8. | code:`mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets` function `demoReports` | 2026-10-04
F-3. The scenario requires S-5 at 1.5 before the presenter's vote. It allows a replacement destination when the default route lacks a lowered kerb crossing or a way around S-2. | doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SHAPE.md` Domain rules and Scenarios item 2; doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_DRAFT.md` section on the sample facts | 2026-10-04
F-4. The fact table allows explicit identifiers, flag and hide pairs, null descriptions and geozones of 25 and 50 m for barrier types. A hidden fact must be flagged, and samples carry no report-save key or OpenStreetMap identity. | doc:`docs/product/schema.md` Facts; code:`db/accessibility_db/migrations/versions/0001_target_schema.py` `CREATE_TARGET_SCHEMA_SQL` fact definition | 2026-10-04
F-5. A vote without an account needs a 32-byte hash and no account. `cast_on` is derived in Europe/Warsaw, and `UX_vote_hash_day` makes one vote per hash, fact and day unique. | doc:`docs/product/schema.md` Accounts and votes | 2026-10-04
F-6. The service account can insert and update facts and votes and cannot delete them. | doc:`docs/product/schema.md` Rights of the service account | 2026-10-04
F-7. A kerb report lies on the nearest stretch of its nearest way. An opposite kerb point on that stretch within 5 m contradicts it. Route planning implements this in its graph helpers. | doc:`docs/product/specification.md` M2; code:`service/route_segments.py` functions `build_nearest_stretch` and `resolve_report_contradiction`; code:`service/route_graph.py` functions `fetch_route_graph`, `build_way_row` and `build_projected_coordinates` | 2026-10-04
F-8. The route graph is built once per copy from the whole network inside the caller's transaction, with a 60 s statement limit for the build, and cached in the process. | code:`service/route_graph.py` constants `GRAPH_BUILD_STATEMENT_TIMEOUT_MS` and `ROUTE_GRAPH_CACHE`, function `fetch_route_graph` | 2026-10-04
F-9. The current copy is read by `fetch_current_osm_copy`, which gives the state instant the graph cache is keyed by. | code:`data/osm_copy.py` function `fetch_current_osm_copy` and class `OsmCopySnapshot` | 2026-10-04
F-10. Route planning places a user report by the nearest way within 15 m, ordered by distance and identifier. | code:`data/route_facts.py` constant `REPORT_STRETCH_DISTANCE_M` and the lateral `_nearest_way` | 2026-10-04
F-11. The shared backend now provides `build_engine`, `fetch_business_now` and `fetch_logger`. `build_business_day` converts an aware instant to the configured zone, and no helper gives the aware business datetime of an instant. | code:`data/engine.py` function `build_engine`; code:`common_time.py` functions `fetch_business_now` and `build_business_day`; code:`config/logging.py` function `fetch_logger` | 2026-10-04
F-12. `build_migration_engine` was removed by the user's decision at the merge of `mw-osm-import`. The schema-owner engine of critical fixtures comes from `--scratch-database-url` through `apply_engine_construction`, and no `schema_owner_engine` fixture exists. | doc:`plans_finished/backend_skeleton/BACKEND_SKELETON_PLAN.md` D-10 change note; code:`tests/conftest.py` function `pytest_addoption` and fixture `database_cleanup_registry`; code:`tests/data/conftest.py` fixture `scratch_database` | 2026-10-04
F-13. The delivered four-example provider, its records, transaction handling and tests pass their noncritical cases, and mypy finds no issue in its three modules. | cmd:`python -m pytest -o addopts=-ra -m "not critical" tests/service/test_sample_data_cases.py tests/service/test_sample_data_integration.py tests/data/test_sample_data_transaction_cases.py tests/data/test_sample_fixture_cleanup_cases.py tests/architecture/test_sample_critical_guard.py` -> 73 passed; cmd:`mypy common_sample_data.py service/sample_data.py data/sample_data.py` -> no issues | 2026-10-04
F-14. Public OpenStreetMap data of the area, read with the importer's own tag rules, has 2451 network ways and 136 lowered kerb points. | cmd:`curl --fail --max-time 90 --user-agent piwo1-hackyeah-sample-data/0.2 'https://api.openstreetmap.org/api/0.6/map?bbox=19.985,50.062,20.012,50.076'` -> 43605 nodes, 7960 ways, newest element 2026-10-04T06:45:43Z; cmd:`python analyze.py stats` with `resolve_is_pedestrian_network_way` and `resolve_node_facts` -> 2451 ways, 136 lowered | 2026-10-04
F-15. The proxy wheelchair route from the Tauron Arena to Ogród Doświadczeń crosses no street, so it has no kerb crossing for S-5. The proxy route to M1 Kraków, al. Pokoju 67, crosses al. Pokoju at node 317034340 with `kerb=lowered`. | cmd:`python analyze.py route ... --wheelchair` -> 1024 m without crossing nodes; cmd:`python analyze.py fullroute --wheelchair` -> 1091 m through node 317034340; doc:`SAMPLE_DATA_OSM_EVIDENCE.md` Route and destination | 2026-10-04
F-16. The eight proposed places meet their placement conditions on the proxy route: unique nearest ways within 15 m, S-5 1.49 m from the lowered kerb on one stretch, a way around S-2, the route bending around S-4, a new crossing after S-5 is confirmed, and S-1, S-6 - S-8 off the route. | cmd:`python analyze.py scenario --wheelchair` -> the results recorded in `SAMPLE_DATA_OSM_EVIDENCE.md`; doc:`SAMPLE_DATA_OSM_EVIDENCE.md` Places | 2026-10-04
F-17. The common loader is paused and consumes the provider only by its names. It carries the counts through without assuming the dataset size, and the provider contract has one source in this initiative's loading handoff. | doc:`plans/osm_import/OSM_IMPORT_HANDOFF.md` Continuation state of 2026-10-04 and Coordination with parallel sessions | 2026-10-04
F-18. The fact operations of `community_facts_api` do not exist yet. Its plan validates identifiers as non-boolean integers without a positive-only rule. | doc:`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-3 and state; cmd:`ls api` -> no fact operation module | 2026-10-04
F-19. Docker is reachable and the local database images of `db/compose.yaml` are cached. The two running database containers belong to other initiatives. | cmd:`docker ps` -> `osm-importer-check-database-1` and `route-planning-db-database-1`; cmd:`docker images` -> database and migrate images of earlier checks | 2026-10-04

## Decisions

D-1. Keep the schema and the provider contract. Use no revision, grant change, new table or report-save key. Keep `service.sample_data.apply_sample_data() -> SampleDataResult`, the fields of `SampleDataResult`, `SampleDataOutcome`, `SampleCommitState`, `SampleDataError` with its alias `SampleDataFailure`, and every failure code except one. `surface_not_absent` becomes `contradiction_missing`, because the contradiction is now a kerb. `initial_votes_created_count` counts the sample votes inserted with newly created facts, from 0 to 25. Agent decision at C:40, without asking: the paused loader consumes the names (F-17), so one renamed code is announced in the handoff and to its session.

D-2. Reserve -1 - -8 for S-1 - S-8 in that order, as the user decided in Q-6. Insert with `OVERRIDING SYSTEM VALUE`, bound values and `ON CONFLICT (id) DO NOTHING RETURNING id`. Verify every existing row's immutable content and never overwrite a conflicting row. Record the convention in `docs/product/schema.md`, section Facts, without a schema change, as awaiting Kuba's confirmation.

D-3. Fix the dataset as follows, latitude and longitude in this order, with the reference way of each place from F-16. Every fact is a user report with `is_sample=true`.

| Fact | Type, radius, steps  | Point                    | Reference way | Description                                                       | Created, minutes before loading | Votes, verdict and minutes before loading | Flagged and hidden, minutes before loading |
| ---- | -------------------- | ------------------------ | ------------- | ----------------------------------------------------------------- | ------------------------------- | ----------------------------------------- | ------------------------------------------ |
| -1   | high_kerb            | 50.0676150, 19.9888900   | 1222443126    | none                                                              | 288                             | confirm 288, 288, 144, 144                | none                                       |
| -2   | stairs, 4 steps      | 50.0663721, 19.99663575  | 926589685     | `Brak poręczy po prawej stronie.`                                 | 1440                            | confirm 1440, 1440                        | none                                       |
| -3   | ramp                 | 50.0668, 19.99536        | 28837534      | none                                                              | 2880                            | confirm 2880, 2880, 2160, 2160            | none                                       |
| -4   | poor_surface, 25 m   | 50.06645, 19.99455       | 360935725     | `Remont chodnika, rozkopana nawierzchnia.`                        | 2880                            | confirm 2880, 2880; deny 1440, 1440       | none                                       |
| -5   | high_kerb            | 50.06574634, 19.99708082 | 252778084     | none                                                              | 432                             | confirm 432, 432, 432                     | none                                       |
| -6   | stairs, 3 steps      | 50.06763615, 19.9893127  | 306727457     | `Schody pod domem pana [nazwisko], zawsze zastawione jego autem.` | 144                             | confirm 144, 144                          | flagged 144                                |
| -7   | narrow_passage, 50 m | 50.07595, 20.00285       | 83093546      | `Rusztowanie na całej szerokości chodnika.`                       | 1440                            | confirm 1440, 1440; deny 720, 720         | flagged 720                                |
| -8   | high_kerb            | 50.06754, 19.98907       | 1222443122    | `tekst z numerem telefonu, ukryty.`                               | 2880                            | confirm 2880, 2880                        | flagged 2880, hidden 2880                  |

The offsets are those of `DemoSeed.ets` in whole minutes. Each vote of weight 1 becomes two votes at its instant, and S-5's third confirmation shares its creation instant. Agent decision at C:40, without asking: a flag or a hiding is dated at the fact's latest sample vote, never earlier than the fact, because `DemoSeed.ets` gives no flag date; S-5's extra vote and the split votes share the instant of the vote they replace.

D-4. Voter identities are SHA-256 of `sample-data:voter:v2:` followed by the fact identifier and the 1-based vote index in decimal, joined by `:`, in UTF-8. They are fictional and differ for every vote, so the presenter's identity never collides with them. Agent decision at C:40, without asking: `v2` separates them from the never-loaded author scheme of the first plan.

D-5. The loading instant is `common_time.fetch_business_now()` truncated to whole seconds. Every sample instant is the loading instant minus its minutes, computed in UTC and converted to the business zone. A new `common_time.build_business_datetime(instant)` performs that conversion, and `build_business_day` reuses it. Each pair is stored through `build_offset_instant`. On a retry, an existing fact's expected vote, flag and hide instants are derived from its stored creation instant and the same minute differences, so retry needs no knowledge of the first loading instant. Agent decision at C:40, without asking: whole seconds avoid a millisecond-rounding mismatch with `timestamptz(3)`, and the helper avoids duplicating the zone conversion.

D-6. Validate in one Repeatable Read transaction before writes. A copy must exist and every reference way must exist. For each point fact, the reference way must be the unique nearest way within 15 m. For each geozone, the reference way must lie within its radius. For S-5, the contradiction must hold in the route graph of the current copy. The provider reads the copy with `fetch_current_osm_copy`, takes the graph with `fetch_route_graph` and the way row with `build_way_row`, projects the point with `build_projected_coordinates`, and takes the stretch with `build_nearest_stretch`. It requires a non-empty result of `resolve_report_contradiction` for `high_kerb`. Agent decision at C:40, without asking: reusing route planning's own stretch and contradiction code makes the check the same rule the route applies (F-7, F-8), with no second implementation in SQL. The 60 s graph build is acceptable in a manually started one-off step.

D-7. On a retry, compare only the immutable content of each existing fact: source, sample mark, coordinates, type, radius, steps, description and null source fields. Then verify its sample votes by voter hash. Each defined hash appears exactly once, with its verdict, without an account and at its expected instant and offset. Flags, hiding, other votes and status are never compared or reset. A changed content gives `content_mismatch`, a broken vote history `initial_vote_invalid`, a foreign row on a reserved identifier `identity_collision`.

D-8. Insert all missing facts in one batch with their creation, flag and hide pairs. Then insert the sample votes of exactly the identifiers returned as newly inserted, in one batch, and verify that the number of inserted votes equals the definitions' count. Commit both together. The failure, commit and logging rules of the first plan stay: the result comes only after an acknowledged commit, a lost acknowledgement is `commit_unknown`, there is no automatic retry, and the logs carry safe reason codes and counts.

D-9. Remove what only the four examples needed: the poor-surface state read, the separation distance from the old S-1, `SAMPLE_AMENITY_DISTANCE_M` and the rest-place rule. The amenity distance of the route is checked jointly on the actual route (PRD AC-5), not by the loader.

D-10. Define `schema_owner_engine` in `tests/data/conftest.py`. It builds the engine from `--scratch-database-url` with `apply_engine_construction`, unpooled, as the delivered scratch fixture does. It fails the test when the option is absent and disposes the engine after the dependent fixtures. `scratch_database` consumes it instead of building its own owner engine. Update the backend handoff and the naming registry to this contract. Agent decision at C:40, without asking: F-12 records the user's removal of `build_migration_engine`, and one owner-engine fixture serves both scratch and sample tests.

D-11. Critical fixtures seed an invented network: the eight reference ways with their recorded geometry shortened around each point, the nodes and memberships the route graph needs, the lowered kerb node 317034340 on way 252778084, and one copy marker. They reset `ROUTE_GRAPH_CACHE.graph` before and after each test, so a changed fixture state is never answered from a graph cached for the same copy instant. Cleanup deletes votes, facts, memberships, nodes, ways and the copy marker by exact keys and creation pairs, through the owner engine.

D-12. Record the places, the method and the replacement destination in `SAMPLE_DATA_OSM_EVIDENCE.md`. The proposal of M1 Kraków as the destination is the user's decision of 2026-10-04, made in the agent's delegation for the stage7 scenario. Mateusz and Rafał accept or change it, and Kuber decides about `DemoSeed.ets`. This initiative does not edit the artifacts of `stage7_demo_scenario`.

## Scope of changes

### S-1. Shared records

In `common_sample_data.py`, add `SampleVoteDefinition` with `verdict: VoteVerdict` and `minutes_before_loading: int`. Extend `SampleDefinition` with `description: str | None`, `created_minutes_before_loading: int`, `votes: tuple[SampleVoteDefinition, ...]`, `flagged_minutes_before_loading: int | None`, `hidden_minutes_before_loading: int | None` and `requires_kerb_contradiction: bool`. Replace `SampleNetworkPrerequisites.poor_surface_state` and `contradiction_path_distance_m` with `has_kerb_contradiction: bool`. Rename `SURFACE_NOT_ABSENT` to `CONTRADICTION_MISSING = "contradiction_missing"`. Replace `build_sample_voter_hash(sample_id)` with `build_sample_voter_hash(sample_id: int, vote_index: int) -> bytes` of D-4. Add `SampleFactRow`, a definition with its `created_at`, `flagged_at` and `hidden_at` pairs, and `SampleVoteRow` with `fact_id`, `voter_hash`, `verdict` and `cast_at`, so the data layer receives ready rows. Rename `StoredInitialVote` to `StoredSampleVote`. Remove `SAMPLE_AMENITY_DISTANCE_M`. In `common_time.py`, add `build_business_datetime(instant: datetime) -> datetime` and let `build_business_day` use it. Input: D-3 - D-5. Output: typed records with no positional rows.

### S-2. Data layer

In `data/sample_data.py`:

- reduce `SELECT_SAMPLE_PREREQUISITES_SQL` to the copy, the reference way, the two nearest ways within 15 m and the reference distance;
- extend `INSERT_SAMPLE_FACTS_SQL` with per-fact `created_at`, flag and hide pairs from the bound JSON batch;
- make `INSERT_INITIAL_SAMPLE_VOTES_SQL` take per-vote fact, hash, verdict and pair from the bound JSON batch;
- make `SELECT_INITIAL_SAMPLE_VOTES_SQL` read every vote of the defined hashes with its verdict.

Change `apply_sample_inserts` to `apply_sample_inserts(connection, fact_rows: Sequence[SampleFactRow], vote_rows: Sequence[SampleVoteRow]) -> tuple[int, ...]`: it inserts the facts, inserts the vote rows of the returned identifiers only and refuses a vote count that differs from those rows, with no time arithmetic of its own. Rename `fetch_initial_sample_votes` to `fetch_sample_votes`. `apply_sample_rollback`, `apply_sample_connection` and `apply_sample_transaction` stay. No DDL, delete, update or source write is present.

### S-3. Service

In `service/sample_data.py`:

- replace `SAMPLE_DEFINITIONS` with D-3;
- add `build_sample_insert_rows(definitions, loading_at) -> tuple[tuple[SampleFactRow, ...], tuple[SampleVoteRow, ...]]`, which returns the fact and vote rows with their pairs;
- add `build_expected_sample_votes(definition, created_at)`, which returns the expected hash, verdict and pair of every vote;
- add `fetch_sample_kerb_contradiction(connection, definition) -> bool` of D-6;
- adapt `resolve_sample_prerequisites` to D-6 and `resolve_existing_sample` to D-7.

`apply_sample_contents` keeps its order: prerequisites, existing content, inserts, final verification of all eight facts and votes. The result reports `created_count`, `unchanged_count = 8 - created_count`, `initial_votes_created_count` and `fact_ids = (-1, ..., -8)`. Update `tests/service/test_sample_data_cases.py` and `tests/service/test_sample_data_integration.py`. They cover the dataset content against the PRD tables, the derived statuses through `service.fact_status` for all eight facts, the date pairs including a DST boundary, the unique-nearest and radius rules, a missing or non-lowered kerb, changed content, a missing or changed vote and an unrelated identifier.

### S-4. Critical storage evidence

Add `schema_owner_engine` of D-10 to `tests/data/conftest.py` and make `scratch_database` use it. Rewrite `tests/data/common_sample_data_fixtures.py` and `tests/data/test_sample_data_critical.py` for D-11. The tests run the real `apply_sample_data` with the restricted service account and cover:

- the first loading with 8 facts and 25 votes and their pairs, statuses and moderation;
- an immediate and a later-day repetition that change nothing;
- preserved community votes and moderation;
- a missing copy and a missing reference way;
- a kerb point that is not lowered or lies more than 5 m away;
- a wrong nearest way;
- an unrelated row on a reserved identifier and changed content;
- an injected failure between the fact and vote batches, which leaves nothing;
- two concurrent invocations, which leave one fact per identifier and one vote per hash.

Keep `tests/data/test_sample_data_transaction_cases.py` and `tests/data/test_sample_fixture_cleanup_cases.py`, adapted only to changed names.

### S-5. Contracts and documentation

- Rewrite `SAMPLE_DATA_OSM_EVIDENCE.md` with D-12.
- Update `SAMPLE_DATA_LOADING_HANDOFF.md` with D-1 - D-5 and D-8, and `SAMPLE_DATA_BACKEND_HANDOFF.md` with D-10.
- Add the identifier convention to `docs/product/schema.md`, section Facts.
- Update the `schema_owner_engine` entry of `docs/standards/naming_registry.md`.
- Rewrite `docs/data/sample_data.md`.
- Update the sample sections of `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md`, and of `data/DATA.md` and `data/DATA_ALGORITHM.md` where they describe the sample layer.
- Send the renamed failure code to the `osm_import` session.

## Rollout order

1. S-1 - S-3 with their noncritical cases.
2. S-4 against a separate local database of `db/compose.yaml` under its own project name, started with throwaway local values passed only through the process environment, never written to a file. Run the migrate profile, then `python -m pytest -o addopts=-ra -m critical tests/data/test_sample_data_critical.py --scratch-database-url=<local owner URL>`. Stop and remove only that project afterwards.
3. S-5, then `ruff check`, `ruff format --check`, `mypy`, `bandit`, `deptry`, `vulture` on the owned scope, the noncritical suite, Prettier on the owned documents, and the implementation review of the whole initiative.

Human-only steps: coordinate the replacement destination with Rafał and Mateusz, confirm the identifier convention with Kuba, tell Kuber about S-5's departure, run the common loader and the joint route checks when their dependencies exist, and commit. This plan performs no hosted operation.

## Definition of Done

1. The eight facts, 25 votes, moderation states and dates match D-3 - D-5 and the PRD tables, with no schema change and no account.
2. The provider validates one snapshot, including the kerb contradiction through route planning's own rule, writes atomically, and reports only acknowledged success. Its critical tests pass on a real local database.
3. Retry and concurrency never duplicate, refresh or reset, as AC-7 - AC-9 require.
4. The handoffs, the schema convention and the documentation describe the delivered behavior, and the `osm_import` session knows of the renamed code.
5. The repository gates of `docs/standards/standard_review.md` pass on the owned scope, and failures elsewhere are reported, not hidden.
6. The joint checks of PRD AC-3 - AC-5 and AC-10 are recorded as waiting for `community_facts_api`, `route_planning` with the imported copy, `frontend_app` and the common loader. The review verdict states that scope.

## Risks

- R-1. The places come from public data and a proxy route without Valhalla's costing. The imported copy and the actual route can differ, and loading then fails visibly or the joint check moves a place.
- R-2. M1 Kraków as the destination is a proposal outside this initiative's ownership. The scenario's owners may choose another, which moves S-2 - S-5.
- R-3. Building the route graph reads the whole copy inside the sample transaction, which lengthens it to the graph-build time. A concurrent import makes the transaction fail with a serialization error, and the manual retry repeats it.
- R-4. The reserved identifiers are not yet accepted by built operations or confirmed by Kuba.
- R-5. A live vote before the pitch changes the starting state, and loading does not restore it.

## Open questions

None. The dataset, voting, dates, moderation, identifiers and places were decided by the user on 2026-10-04 (Q-3 - Q-7 and the replacement destination). The technical choices above are recorded as agent decisions at C:40.

## Supplementary files

- `SAMPLE_DATA_SEED.md`, `SAMPLE_DATA_SHAPE.md` and `SAMPLE_DATA_PRD.md`.
- `SAMPLE_DATA_OSM_EVIDENCE.md`, the source, method and places.
- `SAMPLE_DATA_LOADING_HANDOFF.md` and `SAMPLE_DATA_BACKEND_HANDOFF.md`.
- `mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets`, function `demoReports`.
- `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SHAPE.md` and `STAGE7_DEMO_SCENARIO_DRAFT.md`.
- `docs/product/specification.md` M2, M4, M5, M9 - M11 and `docs/product/schema.md` Facts, Accounts and votes.
