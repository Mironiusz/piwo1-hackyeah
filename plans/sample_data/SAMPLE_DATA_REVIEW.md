# Sample-data implementation run and review

Document state: 2026-10-04, rewritten plan implemented; ready for S-1 - S-5, not ready for the whole initiative

## 2026-10-04 - Implementation authorized

The user authorized `plan-implement` after the plan was closed. The plan, source evidence, loading handoff, schema package and documented backend contracts were rechecked. Shared runtime factories, clock, logger and configuration remain absent. The plan explicitly permits owned preparation before those deliveries; no private runtime replacement was added.

### Implementation and decisions

- S-1 - S-3: delivered `common_sample_data.py`, `service/sample_data.py` and `data/sample_data.py`, fixed definitions, pure decisions, typed projections, bound batch SQL and transaction completion classification.
- S-4: the user authorized defining the missing fixture contract here. Plan D-13 and `SAMPLE_DATA_BACKEND_HANDOFF.md` record the exact registry, guard and owner-engine dependency. Critical fixture/test code is delivered, but executing it requires the backend and local schema; no fake owner engine or successful skip is supplied.
- S-5: the provider handoff is delivered and concurrent `osm_import` planning now references it. The actual common adapter, real imported copy, demo route, fact operations and clients remain delivery dependencies; this initiative implements none of those missing consumers.
- S-6: added service documentation, the operation runbook, required tool scopes and local-package installation instructions. Assessed durable memory and recorded the reserved-id/history pattern and transaction evidence rules. The data layer's documentation-pair creation condition is recorded instead of adding empty domain documentation.
- Agent decision at C:40, without asking: `SampleDataFailure` aliases `SampleDataError`, because the approved exception name collides with Ruff N818. This preserves the consumer contract without suppressing the naming rule.
- Agent decision at C:40, without asking: backend dependencies bind inside the actual runtime operation. Pure validation imports remain executable without an environment-reading facade; missing runtime dependencies still fail explicitly.
- Agent decision at C:40, without asking: point/site and transaction-case tests additionally check nonfinite distances, invalidated connections, rollback failure and lost commit acknowledgement. These are safety evidence for the existing requirements, not new domain behavior.
- Agent decision at C:40, without asking: mypy reads the shared package source through `mypy_path = "db"`. The installed package currently has no `py.typed` marker; no ignored-import suppression or database-package edit was added.

### Evidence and remaining work

The isolated sample, fixture-cleanup, guard and dependency-direction checks passed: 74 cases, with 17 critical cases deselected. The separate critical collection attempt was refused with exit 4 before fixture writes because the validated backend facade is absent. This is guard evidence, not real-database acceptance. Docker listing was refused by OS permissions both normally and after escalation.

The full root noncritical suite ran with the available pinned tools: 199 passed, 3 skipped, 17 deselected and 2 failures in the existing repository-wide prose gate. Those failures name the mobile module's existing documents and a locally installed third-party HarmonyOS README, not owned sample changes. They are not repaired as part of another session's work.

Ruff passes on owned production/test code. Bandit passes at medium/high confidence and in the separate B608 pass; vulture reports no owned dead-code issue. Mypy resolves the database package but fails on the three absent backend modules: `data.engine`, `common_time` and `config.logging`. Deptry likewise reports absent `common_time` and `config`, plus existing mobile mock imports of `pmtiles_mvt`. These failures remain visible; no success-shaped replacement or suppression was introduced.

Real SQL, permissions, concurrent inserts, PostGIS distance checks, original offset preservation and atomic database failure are not yet executed. Source-copy/actual-route evidence, sample presentation, negative-id consumer acceptance and common-command failure/retry evidence also remain incomplete. The initiative stays in `plans/` and does not claim readiness or qualify for archiving.

## 2026-10-04 - Final implementation DoD review

Scope: the whole `sample_data` initiative and its owned changes. Concurrent `osm_import` artifacts and mobile code are not edited. The review uses the standards map and deferred-decision registry and assesses the actual tree; fixture and provider contracts alone are not treated as runtime delivery.

### Blockers

- B-1. `data/sample_data.py`, `apply_sample_transaction`, and `service/sample_data.py`, `apply_sample_data`/`apply_sample_contents`: the required `data.engine`, `common_time` and `config.logging` are still absent. Mypy and deptry expose the missing delivery. The provider cannot run on the real backend, and no private replacement is authorized by the plan.
- B-2. `tests/data/test_sample_data_critical.py` and `SAMPLE_DATA_BACKEND_HANDOFF.md`, Shared backend inputs: the 17 critical cases require the validated local facade, applied first revision, restricted runtime engine and `schema_owner_engine`. The collector correctly refuses the present missing facade with exit 4 before writes. Docker access remains denied after escalation. No critical storage criterion has a successful database run.
- B-3. Plan S-5 and PRD AC-3 - AC-5/AC-6: the common adapter and command, actual imported copy, actual route, fact consumers and clients are not delivered in this tree. Their integration and presentation acceptance remain outstanding; negative-id support is not inferred from a schema definition.
- B-4. Required global gates are red in the current tree. `make check` stops on 25 existing mobile Ruff findings. Whole-tree `ruff format --check .` identifies five mobile files. Global Prettier identifies ten files, including concurrent loader artifacts and mobile/third-party files. The root noncritical suite has two existing prose-gate failures. These are documented environment/tree limitations and are not silently repaired in someone else's work; the full gate is not reported passed.

### Risks

- R-1. The checked public OSM response differs from the actual importer snapshot by design. A further local planar check found the S-4 centre approximately 103.9 m from the whole S-1 source path and S-3 approximately 3.65 m from it; this supports the proposal only and does not replace PostGIS or imported-copy evidence.
- R-2. Whole-step sample timeout and common-loader exclusion completion remain contracts of `osm_import` Q-5. This provider uses the approved shared 5000 ms statement bound and does not invent the loader's remaining budget interface.
- R-3. The SQLAlchemy commit-failure path can deactivate its transaction before `Connection.rollback()` is called. Code inspection of the installed pinned library and the [official connection documentation](https://docs.sqlalchemy.org/en/21/core/connections.html) showed that cleanup alone is not a rollback acknowledgement. `apply_sample_rollback` now refuses inactive, closed or invalidated transaction evidence. Commit cancellation remains unknown; no timeout is used as proof that a sent commit rolled back. Real transport evidence remains part of B-2.
- R-4. Sample fixtures require an empty current network and free reserved ids. Cleanup uses the sole unique copy marker and original creation pair; a later publication or changed identity refuses cleanup rather than deleting unowned data. This is intentionally unsuitable for a local database already holding a real source copy.

### Improvements

No optional rewrite is proposed. Deliver the named prerequisites and complete the existing acceptance runs before extending the provider.

### Verification

Commands used Python 3.14.4 with the repository's pinned tools already available in a temporary tool installation. Installed `accessibility_db.tables` and `closed_lists` were compared with the repository and match byte-for-byte. Prettier 3.7.4 ran through its existing local Node binary; this is the pinned formatter, not a different formatting implementation. Python 3.13 runtime acceptance is not claimed.

| Standard                       | State                 | Evidence and limits                                                                                                                                                                                                                                                                                                |
| ------------------------------ | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `standard_agentic_workflow.md` | checked automatically | Parity tests passed in the focused architecture run; approved chain decisions and ownership were checked manually. No history mutation, skill change or archive move occurred.                                                                                                                                     |
| `standard_agent_docs.md`       | checked automatically | Closed-plan evidence/open-question checks passed. Review and memory formats were checked manually. Seeds are unchanged.                                                                                                                                                                                            |
| `standard_review.md`           | checked manually      | All mapped standards appear here; known failing or unavailable runs prevent readiness for the whole initiative.                                                                                                                                                                                                    |
| `standard_documentation.md`    | checked manually      | Service behavior/construction pair, sample runbook, backend/loading handoffs and data-pair creation condition are supplied. Runtime limitations remain explicit.                                                                                                                                                   |
| `standard_formatting.md`       | checked automatically | Owned Ruff format and prose checks pass; owned Prettier passes. Global formatting/prose failures are B-4.                                                                                                                                                                                                          |
| `standard_git.md`              | checked automatically | Conflict-marker checks and `git diff --check` pass. Status/mtime were checked after unexpected red results. No commit, push, staging or history change occurred.                                                                                                                                                   |
| `standard_architecture.md`     | checked manually      | Service decisions and data I/O remain separated; the additional import-direction gate passes. Shared factories/configuration are required rather than duplicated.                                                                                                                                                  |
| `standard_config.md`           | checked automatically | Existing environment-contract cases passed or reported three missing-local-file/template skips. Eight sentinel/subprocess guard cases prove local-only refusal, including collect-only. No environment entry was added.                                                                                            |
| `standard_database.md`         | checked automatically | Bandit B608 passes; explicit projections, bound values, unchanged schema and one transaction were reviewed. Real SQL and grants remain B-2.                                                                                                                                                                        |
| `standard_errors.md`           | checked manually      | Named safe failures, acknowledged completion, unknown commit and no automatic retry were checked. Two added cases guard inactive-transaction rollback and commit cancellation.                                                                                                                                     |
| `standard_idempotency.md`      | checked manually      | Existing primary key backs stable negative ids; only returned new fact ids get author votes. Repetition and concurrency SQL still need critical evidence.                                                                                                                                                          |
| `standard_code_quality.md`     | checked automatically | Owned Ruff and configured vulture pass. Mypy has three missing-module errors; deptry has four findings, including two existing mobile imports. `make check` is red as recorded in B-4.                                                                                                                             |
| `standard_logging.md`          | checked automatically | Ruff G passes. Safe lazy reason/count fields and traceback calls were reviewed. Real central diagnostic redaction requires B-1's delivered logger.                                                                                                                                                                 |
| `standard_naming.md`           | checked automatically | Ruff N passes, the public exception alias is documented, query names follow the standard and actual sample interfaces are recorded in the naming registry.                                                                                                                                                         |
| `standard_security.md`         | checked automatically | Both owned Bandit passes have no findings. `pip-audit --path` completed after permitted network escalation with no known vulnerabilities; the local unpublished `accessibility-db` itself is reported unauditable by PyPI. Its external dependencies were included. No hosted data or secrets were accessed.       |
| `standard_tests.md`            | checked automatically | Final owned cases: 76 passed, 17 critical cases deselected. The broader focused architecture/provider run had 113 passed and 3 skipped before the last two new transaction cases. The earlier whole-root run had 199 passed, 2 failed and 3 skipped; no full-suite success is claimed. Critical acceptance is B-2. |
| `standard_time.md`             | checked manually      | Typed aware instant/offset pairs come from the database package and the shared business clock. Retry uses original history; winter/summer storage cases are supplied but unexecuted.                                                                                                                               |
| `standard_worker.md`           | not applicable        | This initiative adds no worker entry point or periodic task. One-off worker rules remain deliberately deferred in the registry.                                                                                                                                                                                    |
| `standard_frontend.md`         | not applicable        | No frontend implementation is changed; sample marking and actual route/client acceptance remain the joint B-3 checks.                                                                                                                                                                                              |

### Verdict

Not ready for the whole `sample_data` initiative. Owned provider, critical-test code, documentation and contracts are delivered and isolated verification passes. B-1 - B-4 prevent runtime and complete acceptance. Keep the initiative in `plans/sample_data/`; it does not qualify for `plans_finished/`. Continue with the delivered shared backend and owner fixture, run the existing local critical suite, then complete S-5's actual-source/client/common-program checks and the final global gates. No further permission is needed for those already authorized local implementation checks.

## 2026-10-04 - Resumption toward completion stopped on a contract conflict

The user asked to finish everything in this initiative. The run resumed `plan-implement` on `SAMPLE_DATA_PLAN.md`. During the fact check the user switched to `dev`, pulled and merged `dev` back into `rm/requirements-preparation`; the transient missing files were that checkout, not someone else's edit. The facts were rechecked on `25c64eb`. The merge changed nine files, among them `docs/product/specification.md`, `docs/product/api_contract.md` and the new `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_PRD.md`; none of the owned sample files changed.

### State of the earlier blockers

- B-1 is resolved by the delivered backend. `data.engine.build_engine`, `common_time.fetch_business_now` and `config.logging.fetch_logger` exist. Mypy on `common_sample_data.py`, `service/sample_data.py` and `data/sample_data.py` reports no issues; deptry reports only the two existing mobile `pmtiles_mvt` imports. The owned noncritical cases ran: 73 passed.
- B-2 is still open, and its contract changed. The archived `plans_finished/backend_skeleton/BACKEND_SKELETON_PLAN.md`, D-2 and the verification decision, records the user's change at the merge of `mw-osm-import`: `build_migration_engine` was removed, and the schema owner engine is built from the `--scratch-database-url` option inside the scratch fixture of `tests/data/conftest.py`. No `schema_owner_engine` fixture exists, so plan D-13 and `SAMPLE_DATA_BACKEND_HANDOFF.md`, Shared backend inputs, name an interface that will not be delivered. No local `.env` exists, so the critical collection still refuses with exit 4 before writes. Docker is now reachable; the two running containers belong to other initiatives and were not used.
- B-3 is still open. `service/demo_loading.py` and `worker/load_demo.py` do not exist and `plans/osm_import/OSM_IMPORT_PLAN.md` is still in progress. The fact operations of `community_facts` have only their new API shape, PRD and plan.

### Conflict with the demo scenario

`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SHAPE.md`, closed at C:40, records the user's decisions of 2026-10-04 in its Domain rules: the server sample facts are S-1 - S-8 taken one to one from `mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets`, with their intended statuses and the sample votes producing them, S-5 at confirmation weight 1.5 near a real lowered kerb, the flagged S-6 and S-7 and the hidden S-8 placed off the route, on the route from the Tauron Arena to Ogród Doświadczeń. Its PRD, awaiting the user's confirmation, hands these as requirements to this initiative.

That contradicts this initiative's approved contract: `SAMPLE_DATA_SHAPE.md`, functional requirement 6, and `SAMPLE_DATA_PRD.md`, FR-4, fix four examples, each unverified with exactly one fictional confirmation of weight 0.5 and no preloaded confirmations or denials, and the shape states that the dataset is not inferred from the mobile mock. Plan D-2, D-3 and D-7 and the delivered code build on four reserved identifiers and one initial vote per fact. Finishing the current plan would therefore deliver a dataset the demo scenario cannot use, and adopting the scenario reopens the approved shape and PRD. Neither is decided by the agent. Implementation stopped before any code change; the question went to the user.

### Coordination with the parallel sessions

At the user's request the question was held until the two parallel sessions answered.

- The `osm_import` session is closing its plan and has written no code yet. Its adapter in `service/demo_loading.py` will consume only the names of the provider contract: the callable, the result fields, the outcome and failure enums. It carries the counts through without assuming four examples, one vote per fact or the identifiers -1 to -4, so a changed dataset does not break it while those names stay. It does not touch the test fixtures; `schema_owner_engine` may be defined in `tests/data/conftest.py`. The shared files are the sample sections of `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md`, which this initiative edits only after that session finishes its own sections. Its proposed sample-step budget, finite statements each bound by `build_engine(5000)` with no loader timer, was accepted with the note that a silently lost commit acknowledgement stays `commit_unknown` and no hard wall-clock limit is claimed. Nobody in either session owns the tile loading step.
- The `community_facts` session reports that no fact operation exists in code. Kuba's data layer has a closed shape only, and Marek's `COMMUNITY_FACTS_API_PLAN.md` is in progress, blocked by its Q-1 - Q-4. Its D-3 validates identifiers as non-boolean integers without a positive-only rule, but nothing guarantees negative identifiers until the code exists, and the reservation is not recorded in `docs/product/schema.md`. The sample voter hash fits `CK_vote_voter_hash_sha256` and cannot block the presenter's vote, because `UX_vote_hash_day` includes the hash. Status is derived from votes on every read, with no cache. Flags and hiding are the `flagged_at` and `hidden_at` pairs of `fact`; `CK_fact_hidden_only_flagged` requires a hidden fact to be flagged, and `docs/product/schema.md`, Who writes what, says the backend writes them. Whether samples may write them directly is a contract decision for the user. That session is splitting `plans/community_facts/` and edits `MVP.md`, `docs/standards/decision_registry.md` and `FINAL_CHECKLIST.md`; it does not touch `plans/sample_data/`.

Consequence for S-5: the joint negative-identifier and live-vote checks cannot run in this initiative until the fact operations and the common adapter exist, whichever dataset is chosen.

### User decision and return up the chain

On 2026-10-04 the user chose the dataset of the demo scenario for the hosted demo: the eight facts of `STAGE7_DEMO_SCENARIO_SHAPE.md`, Domain rules, in place of the four approved examples. This overturns `SAMPLE_DATA_SHAPE.md` functional requirements 1, 2 and 6 and the PRD built on them, so the plan is no longer a valid contract. Following ch. 4.3 of `docs/standards/standard_agentic_workflow.md`, implementation does not continue on it: the shape is reopened with the decision recorded and new open questions, then the PRD and the plan are redone through `plan-prd`. The delivered code stays in the tree unchanged until the new plan says what of it is reused. The stage7 PRD itself still awaits the user's confirmation in its own initiative.

## 2026-10-04 - Shape, PRD and plan redone; implementation deferred by the user

The reopened shape was closed after the user answered Q-3 - Q-7. All sample votes are fictional votes without an account, of weight 0.5. Dates are relative to the first loading. The loader writes the moderation of S-6 - S-8 directly. The identifiers -1 - -8 are recorded as a convention in `docs/product/schema.md`. The agent chooses the places from public OpenStreetMap data. The user approved the rewritten PRD.

During phase B the proxy check of public data showed that the wheelchair route from the Tauron Arena to Ogród Doświadczeń crosses no street, so it has no kerb crossing for S-5. The user chose to propose M1 Kraków, al. Pokoju 67, as the replacement destination of the scenario, and the places were fitted to it. The method, the places and the checks are in `SAMPLE_DATA_OSM_EVIDENCE.md`. The plan was rewritten, closed, and passed the plan-format and prose checks: 54 passed.

The user then chose not to implement the plan now. No code, test or shared document was changed by this run. `common_sample_data.py`, `service/sample_data.py`, `data/sample_data.py`, their tests and `docs/data/sample_data.md` still describe the four examples of the first plan, which no longer match the approved PRD.

### Verdict

Not ready. The scope of this entry is the initiative's artifacts: the shape, the PRD, the plan, the OSM evidence and this review. The delivered code implements a superseded dataset. The initiative stays in `plans/sample_data/` and does not qualify for `plans_finished/`. The next step is `plan-implement` on the closed `SAMPLE_DATA_PLAN.md`, from S-1.

Open items outside this initiative:

- Rafał and Mateusz accept or change the replacement destination in `stage7_demo_scenario`.
- Kuber decides about S-5's departure in `DemoSeed.ets`.
- Kuba confirms the identifier convention.
- The `osm_import` session was told of the planned code rename `surface_not_absent` -> `contradiction_missing`; the loading handoff changes only when S-5 of the plan is implemented.

## 2026-10-04 - Implementation of the rewritten plan

The user asked to implement `SAMPLE_DATA_PLAN.md`. The fact check found the facts true on `abe1377`: the staged merge of `b480093` changed only the docstring of `demoReports` in `DemoSeed.ets`, so F-2 holds, and the functions of F-7 - F-12 exist as cited. During the run the user completed that merge and committed twice (`d6ee8ea`, `fd66a90`); the commits took in the work in progress and changed nothing of it.

### Run into during implementation

- `fetch_route_network` of `data/route_network.py` set `yield_per` on the connection it received. In SQLAlchemy 2.x that changes the connection in place, so after the route graph was built inside the sample transaction every later statement ran as a server-side cursor and the fact insert failed with a syntax error at `INSERT`, confirmed on the local database. The plan did not foresee it. The user chose to fix it at the source: the three statements carry `yield_per` themselves and the connection keeps its options. `tests/data/test_route_network_critical.py` gained `test_reading_the_network_leaves_the_connection_able_to_write`.
- A `ruff format tests/data/` run of this session removed the trailing blank line of `tests/data/test_tile_archive_cases.py`, work in progress of the `tile_loading` session. The line was restored at once and the file has no diff from this session; later formatting named only owned files.
- A helper script wrote `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md` with CRLF line endings. Both were restored to LF; their content, including the uncommitted tile section of the other session, is unchanged apart from the sample sections.

### Delivered

- S-1: `common_sample_data.py` with `SampleVoteDefinition`, the extended `SampleDefinition`, `SampleNetworkPrerequisites.has_kerb_contradiction`, `SampleFactRow`, `SampleVoteRow`, `StoredSampleVote`, `CONTRADICTION_MISSING` and `build_sample_voter_hash(sample_id, vote_index)`; `SAMPLE_AMENITY_DISTANCE_M` removed. `common_time.build_business_datetime`, reused by `build_business_day`.
- S-2: `data/sample_data.py` with the reduced prerequisite read, per-fact pairs and per-vote rows in bound JSON batches, `fetch_sample_votes` and `apply_sample_inserts(connection, fact_rows, vote_rows)`.
- S-3: `service/sample_data.py` with the dataset of D-3, `build_sample_insert_rows`, `build_expected_sample_votes`, `fetch_sample_kerb_contradiction` and the adapted decisions; the cases and integration tests rewritten.
- S-4: `schema_owner_engine` in `tests/data/conftest.py`, consumed by `scratch_database` and the registry; the invented eight-way network with the lowered kerb 317034340; 17 critical cases.
- S-5: both handoffs, the identifier convention in `docs/product/schema.md`, section Facts, the naming registry, `docs/data/sample_data.md`, the sample sections of the service and data documents, a fixture note in `SAMPLE_DATA_OSM_EVIDENCE.md`, and the message about `contradiction_missing` to the `osm_import` session.

### Decisions

- Agent decision at C:40, without asking: `has_kerb_contradiction` defaults to false in the record, and `fetch_sample_network_prerequisites` of the service sets it for S-5 only, because the storage cannot measure a rule that lives in the route graph. False is the rule of M2 for missing evidence, not a substitute value.
- Agent decision at C:40, without asking: no current copy, a reference way the graph does not hold and a way without a stretch establish no contradiction. Validation reports `copy_missing` or `site_invalid` first when those are the cause, so `contradiction_missing` names only a failed kerb rule.
- Agent decision at C:40, without asking: the clock, logger and engine are imported at module level instead of at call time. The earlier reason, modules that did not exist, no longer holds, and none of them reads configuration on import; the tests replace the names of `service.sample_data`.
- Agent decision at C:40, without asking: `fetch_business_now` reuses `build_business_datetime` together with `build_business_day`, so the zone conversion has one place.
- Agent decision at C:40, without asking: the internal serializer `build_sample_authors` became `build_sample_voters`, because it now serializes all 25 voters. The query constants keep the names of plan S-2.
- Agent decision at C:40, without asking: `data/DATA.md` and `data/DATA_ALGORITHM.md` had no sample section to update, so each gained a short one; the data layer documents every other feature that way.
- Agent decision at C:40, without asking: `tests/data/test_sample_data_insert_cases.py` covers which votes the batches carry and the refused vote count, which a real database cannot be made to show. The opaque result values of the transaction cases follow the eight-fact dataset.
- Agent decision at C:40, without asking: a fixture way of more than five nodes keeps its segment nearest to the sample point and one node on each side, a shorter one stays whole. The critical cases also cover the missing ways of S-5 and S-7 and a geozone whose way lies outside its radius.

### Verification

Python 3.13 of the repository `venv`. The local database is a separate project `sample-data-check` of `db/compose.yaml` on a loopback port, with the first revision applied by its migrate profile and throwaway values passed only through the process environment.

| Check                                                                                                                      | Result                                                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Critical sample cases, `tests/data/test_sample_data_critical.py`                                                           | 17 passed; the database held no fact, vote, way, node, membership or copy afterwards                                                                                             |
| Other critical data cases on the same database, including every user of `scratch_database` and the route network and facts | 27 passed, 1 skipped for Linux only                                                                                                                                              |
| Owned noncritical cases, architecture tests and time cases                                                                 | 255 passed, 3 skipped for absent local environment files                                                                                                                         |
| Full noncritical suite                                                                                                     | 975 passed, 11 skipped, 6 failed; the 6 OSM cases fail because osmium cannot open a temporary path with the non-ASCII user name, and pass with an ASCII `--basetemp` (22 passed) |
| `ruff check` and `ruff format --check` on the 16 owned Python files                                                        | pass                                                                                                                                                                             |
| `mypy`                                                                                                                     | no issues in 83 files                                                                                                                                                            |
| `bandit` passes of the makefile for `service`, `data`, the root modules and B608                                           | no findings                                                                                                                                                                      |
| `vulture`                                                                                                                  | no findings                                                                                                                                                                      |
| `deptry .`                                                                                                                 | 4 findings, all imports of `mobile_app/tools/mock_backend`                                                                                                                       |
| Prettier on the owned and edited documents                                                                                 | pass                                                                                                                                                                             |
| Whole-tree `ruff check .`, `ruff format --check .` and Prettier                                                            | red only in `mobile_app` and vendored skill files, which this initiative does not own                                                                                            |

### Remaining

- PRD AC-3 - AC-5 and AC-10 wait for `community_facts_api`, `route_planning` on the imported copy, `frontend_app` and the common loader of `osm_import`.
- The places are checked against public data and an invented network, not the imported copy or the actual route.
- Human-only steps: Rafał and Mateusz accept or change M1 Kraków as the destination, Kuba confirms the identifier convention, Kuber decides about S-5 in `DemoSeed.ets`, and the common loader and joint checks run when their dependencies exist.
- The local project `sample-data-check` was stopped and removed with its volumes after the review; the containers of other initiatives were not touched. Its two built images stay in the local Docker cache. Pytest left its temporary directory `C:\sample-check-pytest` outside the repository.

## 2026-10-04 - Implementation DoD review

Scope: S-1 - S-5 of `SAMPLE_DATA_PLAN.md` and the fix of `data/route_network.py`, on the files listed in the entry above. The tile files of `tile_loading` and `mobile_app` are other sessions' work and outside the scope. The review used the standards map, the deferred-decision registry and the tool map of `docs/standards/standard_review.md`, and ran its commands.

### Blockers

None in the scope of the implementation.

### Risks

- R-1. `docs/product/schema.md` is changed and approved like the specification, as a new version of it (its section Why this document exists). The identifier convention added to its section Facts follows plan D-2 and awaits Kuba's confirmation, but no version of `docs/product/specification.md` records it. Whether it becomes a version is for the user and Kuba to decide.
- R-2. `data/route_network.py` belongs to the finished `route_planning`, owned by Marek. The fix keeps its reads and their streaming and is covered by a new critical case, but Marek should know of it.
- R-3. The graph build inside the sample transaction, plan R-3, is not yet measured on the imported copy of Kraków.
- R-4. The full noncritical suite has six environmental failures on this machine, which pass with an ASCII `--basetemp`; a green full suite is shown only with that workaround.

### Improvements

- I-1. The docstring of `database_cleanup_registry` in `tests/conftest.py` still named a skeleton-owned engine. Fixed after the review: it names the engine of `tests/data/conftest.py`; ruff passes and the 19 critical sample and route-network cases and 97 noncritical cases ran green again.
- I-2. `fetch_sample_network_prerequisites` builds the route graph for S-5 before the places of S-1 - S-4 are judged, which costs a graph build on a failing place. The result is correct; left as it is.

### Verification

| Standard                       | State                 | Evidence                                                                                                                                                 |
| ------------------------------ | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard_agentic_workflow.md` | checked automatically | parity, vendored content, session context and dangerous commands tests pass                                                                              |
| `standard_agent_docs.md`       | checked automatically | `test_plan_document_contract.py` passes; review and memory formats checked manually                                                                      |
| `standard_review.md`           | checked manually      | this entry                                                                                                                                               |
| `standard_documentation.md`    | checked manually      | docstrings on every function, no line comments, sample sections in the service and data documents and `docs/data/sample_data.md`                         |
| `standard_formatting.md`       | checked automatically | owned Python and documents pass ruff format and Prettier, `test_prose_style.py` passes; whole-tree failures lie in `mobile_app` and vendored skill files |
| `standard_git.md`              | checked automatically | `test_conflict_markers.py` and `git diff --check` pass; no commit, push or staging by the agent                                                          |
| `standard_architecture.md`     | checked automatically | `test_layer_boundaries.py` and `test_sample_layer_boundaries.py` pass                                                                                    |
| `standard_config.md`           | checked automatically | environment contract and critical guard pass, with three skips for absent local files; no environment entry added                                        |
| `standard_database.md`         | checked automatically | bandit B608 passes; bound values, no DDL, update or delete in the provider                                                                               |
| `standard_errors.md`           | checked manually      | acknowledged commit, `commit_unknown`, no automatic retry; transaction cases pass                                                                        |
| `standard_idempotency.md`      | checked manually      | primary key with `ON CONFLICT DO NOTHING`, votes only for returned identifiers; critical repetition and concurrency cases pass                           |
| `standard_code_quality.md`     | checked automatically | owned ruff passes, mypy has no issue in 83 files, vulture has no finding, deptry's four findings lie in `mobile_app`                                     |
| `standard_logging.md`          | checked automatically | ruff G passes; logs carry reason codes and counts only                                                                                                   |
| `standard_naming.md`           | checked automatically | ruff N passes; the naming registry lists the sample names                                                                                                |
| `standard_security.md`         | checked automatically | bandit passes on `service`, `data` and the root modules; pip-audit not applicable without a new dependency                                               |
| `standard_tests.md`            | checked automatically | 17 critical sample cases and 27 other critical data cases pass on a local database; noncritical as R-4 says                                              |
| `standard_time.md`             | checked manually      | UTC arithmetic with the offset of each instant; clock-change cases pass, one of them critical                                                            |
| `standard_worker.md`           | not applicable        | no worker entry point or periodic task                                                                                                                   |
| `standard_frontend.md`         | not applicable        | no frontend change                                                                                                                                       |

### Verdict

Ready for the scope of S-1 - S-5 and the fix of `data/route_network.py`, after the minor fix I-1, which is applied. Not ready for the whole `sample_data` initiative: PRD AC-3 - AC-5 and AC-10 and the human-only steps remain. The initiative stays in `plans/sample_data/` and does not qualify for `plans_finished/`.
