# Review: OpenStreetMap importer

Document state: 2026-10-04, implementation in progress

## Implementation record

The user authorized proceeding with independent importer work while backend_skeleton is being implemented, without modifying that initiative or assigning it new tasks. The user also confirmed that backend implementation, migration and connection configuration do not exist on another branch. Database test execution remains deferred under D-34.

Implemented the pure subset: source URL, checksum, source timestamp and source-state comparison in `service/osm_source_validation.py`; M2 pedestrian-network selection in `service/osm_tag_rule.py`; closed network tag lists in `service/osm_tag_thresholds.py`; 18 unittest cases; layer documentation and naming registration. No runtime dependency, shared configuration, backend image, migration or hosted data was changed.

Agent decision at C:40, without asking: source metadata validation belongs in service rather than data because it decides acceptability without I/O. Keep transport in the future data integration. Follow the existing architecture contract's predicate and tag-list filenames instead of the draft's conflicting names. The plan records this bounded subset under D-35; its remaining shared contracts are still open.

Agent decision at C:40, without asking: use unittest TestCase tests compatible with pytest collection because this environment has no pytest and venv creation fails without ensurepip. This supplies executable evidence for pure rules without claiming the required pytest gates passed.

Agent decision at C:40, without asking: checksum validation accepts the published single digest and standard single-file text/binary MD5 formats, always binding a supplied filename to the selected extract. Header parsing rejects naive or malformed instants and precision beyond datetime's microsecond representation instead of silently dropping precision. Persistence precision remains outside this subset.

## Blockers

B-1. The complete importer is not implemented. HTTP acquisition, PBF reading, geometry, accessibility fact mapping, reconciliation, routing-data preparation, database publication, recovery and the administrative entry point remain outstanding. Q-1 and Q-2 do not provide executable shared contracts yet. These rules must not be presented as a runnable importer.

B-2. Full quality gates cannot run in this environment. `make -k check` reports missing ruff, npx, mypy, vulture, deptry, bandit, pip-audit and pytest. `python3 -m venv /tmp/osm-importer-venv` fails because ensurepip is absent. Python is 3.14.4, so the project's Python 3.13 baseline has not been exercised. Formatting, static typing, security and architecture gates remain unverified.

B-3. Shared gate scopes currently cover hooks rather than service code. Additive service coverage in mypy, vulture and security commands must be integrated with the ongoing foundation work before merge. This session did not modify the shared pyproject.toml or makefile while the user prohibited new backend_skeleton work.

B-4. The user-selected hosted database-test exception is recorded in D-33 but is not implemented in the repository-wide test policy. Do not bypass the critical-test guard. No hosted database test or publication ran.

## Risks

R-1. Source metadata tests do not verify live redirect handling, real download integrity, HTTP cancellation or source data completeness. The pure checksum rule receives an already computed digest and does not read a file.

R-2. Network selection does not infer accessibility. Future mapping must preserve unknown attributes and the default-versus-explicit absence distinction.

## Improvements

No optional improvement is required for this subset beyond the pending gates and integration work.

## Verification

| Standard | State | Evidence or reason |
| -------- | ----- | ------------------ |
| standard_agentic_workflow.md | Checked manually; automatic checks unavailable | Independent subset only; no archive, commit or skeleton edit; pytest absent |
| standard_agent_docs.md | Checked manually; automatic checks unavailable | Plan remains in progress; scoped review; pytest absent |
| standard_review.md | Checked manually | All standards listed; incomplete scope receives not ready |
| standard_documentation.md | Checked manually | SERVICE.md and SERVICE_ALGORITHM.md describe implemented rules |
| standard_formatting.md | Partly checked automatically | git diff --check and Python line-length inspection pass; ruff, prettier and prose pytest unavailable |
| standard_git.md | Checked manually; automatic check unavailable | No history or index mutation; pytest absent |
| standard_architecture.md | Checked manually | Pure service decisions; no substitute infrastructure |
| standard_config.md | Not applicable | No environment entry or configuration implementation |
| standard_database.md | Not applicable | No SQL, migration or database access |
| standard_errors.md | Checked manually | Named source rejection; no retry or hidden failure |
| standard_idempotency.md | Checked manually | Equal instant unchanged and older source rejected in tests |
| standard_code_quality.md | Partly checked automatically | compileall and AST parsing pass; mapped static tools unavailable |
| standard_logging.md | Not applicable | No logging or shared logger change |
| standard_naming.md | Checked manually; automatic check unavailable | Binding prefixes and architecture names; registry updated; ruff absent |
| standard_security.md | Checked manually; automatic check unavailable | No secrets, new dependency or I/O; bandit absent |
| standard_tests.md | Partly checked automatically | 18 unittest tests pass; pytest unavailable; database tests deferred |
| standard_time.md | Checked manually and by unit cases | Aware parsing, offset preservation, equivalent instants, the repeated daylight-saving hour and Warsaw day boundaries |
| standard_worker.md | Not applicable | No worker or schedule implemented |
| standard_frontend.md | Not applicable | No frontend change |

Executed `python3 -m unittest discover -s tests/service -p 'test_osm*_cases.py' -v`: 18 tests passed. Executed `python3 -m compileall -q service tests/service`: passed. Parsed all five added Python files and checked their line lengths: passed. Executed `git diff --check`: passed. These checks do not substitute for the missing mapped gates.

## Verdict

Not ready for the implemented subset to merge, because required quality gates and shared gate coverage remain outstanding. Not ready for the whole initiative, because the remaining importer implementation and shared integration contracts are incomplete. The initiative stays in plans/osm_importer; no closure or archival move is authorized by this review.

## 2026-10-04 - Extended independent subset review

This entry supersedes the earlier tool-availability results for the independent subset. The complete initiative remains in progress. D-36 covers mapping, geometry, immutable source snapshots, routing tags, PBF writing and integrity manifests. D-37 records user-approved contradictory tags as unknown. No backend_skeleton artifact, shared backend interface or hosted database was changed.

### Verification

| Standard | State | Evidence or limitation |
| -------- | ----- | ---------------------- |
| standard_agentic_workflow.md | Checked | Scoped implementation and review; initiative remains active |
| standard_agent_docs.md | Checked | Plan decisions and reusable service memory updated |
| standard_review.md | Checked | Applicable standards and incomplete gates recorded |
| standard_documentation.md | Checked manually | Service and data purpose and algorithm documents describe implemented scope |
| standard_formatting.md | Partly checked | Ruff check and format, git diff --check pass; Prettier unavailable; repository prose gates fail in separate wrkt tree |
| standard_git.md | Checked | No index or history mutation; no remote publication |
| standard_architecture.md | Checked manually | Data performs file I/O; service owns mapping and selection; no guessed infrastructure |
| standard_config.md | Not applicable | No environment configuration or target address added |
| standard_database.md | Deferred | No database access or SQL; schema and publication integration remain pending |
| standard_errors.md | Checked | Named source, geometry, numeric, reader and file failures; no silent fallback |
| standard_idempotency.md | Checked for subset | Source-state comparisons and non-overwriting PBF and manifest publication tested; full-copy protocol pending |
| standard_code_quality.md | Partly checked | Ruff, mypy, Bandit and Vulture pass; deptry fails only on nested wrkt tests importing pytest |
| standard_logging.md | Not applicable | No logger or orchestration added |
| standard_naming.md | Checked | Ruff passes; actual public names added to registry |
| standard_security.md | Checked for subset | Bandit passes; pip-audit reports no known vulnerabilities in the temporary dependency environment |
| standard_tests.md | Partly checked | 118 importer tests pass; 235 of 238 combined importer and architecture tests pass; three repository-wide failures originate in wrkt |
| standard_time.md | Checked | Aware instants, source timestamp preservation, UTC PBF header and missing-metadata rejection tested |
| standard_worker.md | Not applicable | No entry point, worker or schedule implemented |
| standard_frontend.md | Not applicable | No frontend changes |

Executed with Python 3.14.4 and pinned temporary tools: pytest on tests/data and tests/service (118 passed); Ruff check and format (passed); mypy on service and data (passed); Bandit and Vulture on the importer (passed); pip-audit (no known vulnerabilities). The combined run including tests/architecture has 235 passes and three failures: conflict markers, forbidden characters and prose bold in the separate untracked wrkt tree. Deptry reports three pytest development-dependency imports in that same tree. These files are outside this change and were not modified or excluded from repository gates.

### Risks and remaining work

PBF writing materializes the selected snapshots to validate references before opening the writer; its memory use grows with network size. Temporary-file publication prevents a failed write from exposing a partial destination and never overwrites an existing destination. Manifest verification requires the future caller's import exclusion; it does not prove database commit or activate routing data.

The real Valhalla tile build was unavailable because Docker socket access was denied. Python 3.13 baseline wheel verification, Prettier and full source acquisition are outstanding. Kraków boundary selection, full orchestration, transactions, vote reconciliation, recovery, activation and database integration still require completion. Missing source edit metadata is rejected using pyosmium's epoch sentinel rather than guessed timestamps. No production database tests ran.

### Verdict

The implemented independent components pass their executed local functional and static checks. Not ready for a full merge-readiness claim: the listed formatting and repository-wide gates remain incomplete or failing, and the full importer contracts and implementation remain unfinished. Keep the initiative in plans/osm_importer.

## 2026-10-04 - Acquisition and integrated walking preparation review

### Blockers

B-1. The full administrative importer is incomplete. Shared engine, logger, clock, exclusion, vote evaluation and applied revision are not delivered in this checkout. Database writes, reconciliation, commit recovery and pointer activation remain pending; no substitute implementation or backend_skeleton change was introduced.

B-2. Synchronous parsing in service/osm_routing_preparation.py is not cancelled by asyncio deadlines. The final worker must run it inside the agreed process-level cancellation mechanism before the whole-run deadline can be claimed. Acquisition checks elapsed time around header reading, but cannot interrupt a blocked native header read.

B-3. A real Valhalla tile build and full Geofabrik import remain unverified. Synthetic tool tests verify command arguments, configuration, sequencing, output checks and process lifetime, rather than routing correctness. Docker access was unavailable in this environment.

B-4. Full merge readiness remains unclaimed: Prettier is unavailable, repository prose gates fail in the separate wrkt tree, and deptry flags three development-dependency imports in that tree. The latest architecture run has 121 passes and two prose failures; the previously observed conflict-marker failure no longer occurs. No outside tree was edited or excluded.

### Risks

R-1. Boundary validation and network preparation retain source ways or nodes in memory, with separate full-source passes. Extract-scale time and memory are unmeasured for this implementation. Nested boundary ring relations fail explicitly; no guessed geometry is supplied.

R-2. Child-process termination uses Linux process groups, matching the delivered container environment. Configuration and executable paths are supplied by the caller; this subset does not provide or build the image. Failed preparation can leave a new unpublished directory without a manifest. Cleanup and reuse remain subject to the future exclusion and database-history checks.

### Improvements and implementation decisions

Agent decision at C:40, without asking: split domain acquisition orchestration into service/osm_acquisition.py and transport into data/osm_source.py to preserve dependency direction. Use HTTPX 0.28.1 with an injectable asynchronous client; existing importer decisions already selected HTTPX and its timeout policy. Disable automatic redirects and retries, retain TLS verification and use event-loop monotonic deadlines. Bound checksum bodies at 4096 bytes, comfortably above the accepted single MD5 record, to avoid unbounded metadata buffering.

Agent decision at C:40, without asking: connect existing preparation stages through service/osm_routing_preparation.py, with the caller supplying Valhalla's existing configuration and tool directory. Enable the three approved platform/node-identity options and omit transit inputs. Invoke the documented build_tiles and build_extract tools without a shell. No shared environment or image contract is invented.

Agent decision at C:40, without asking: independently compare the assembled boundary outline with all referenced ring ways. Even endpoint degree allows valid outer rings touching at one node; odd degree detects open rings. The native polygon must still be valid and match every ring. Source identity and original tags survive subsequent normalization.

Primary references checked: [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/), [HTTPX streaming](https://www.python-httpx.org/quickstart/), [Valhalla 3.9.0 build_tiles source](https://github.com/valhalla/valhalla/blob/3.9.0/src/mjolnir/valhalla_build_tiles.cc) and [build_extract source](https://github.com/valhalla/valhalla/blob/3.9.0/scripts/valhalla_build_extract). Existing backend and Valhalla plans contain the technology contracts; missing delivered code does not mean those decisions are missing.

### Verification

| Standard | State | Evidence |
| -------- | ----- | -------- |
| standard_agentic_workflow.md | Checked automatically and manually | Plan-contract tests pass; authorized independent scope; no archival move or skeleton edit |
| standard_agent_docs.md | Checked automatically and manually | Plan-contract tests pass; implementation results recorded here and reusable knowledge in service memory |
| standard_review.md | Checked manually | All standards listed; verdict explicitly scoped |
| standard_documentation.md | Checked manually | Service/data purpose and algorithm documents extended; docs/import/osm_importer.md describes APIs and limits |
| standard_formatting.md | Checked automatically; incomplete | Ruff and git diff --check pass; 42 importer files have no prose violations; global prose tests fail in wrkt; Prettier unavailable |
| standard_git.md | Checked automatically and manually | Architecture hook tests ran; no commit, push, add, rebase or outside-tree mutation |
| standard_architecture.md | Checked automatically and manually | Three importer guards pass; data never imports service and integrations stay in data |
| standard_config.md | Checked automatically and manually | No environment reader or parallel connection factory; caller supplies tools and configuration; no target identifiers stored |
| standard_database.md | Not applicable to added code | No database operation, DDL or query added; B608 pass remains clean |
| standard_errors.md | Checked manually and by tests | Named acquisition/tool failures; no retries, redirects, silent fallback or false activation |
| standard_idempotency.md | Checked automatically and manually | Existing destinations preserved; only new preparation directories written; manifest created after successful build |
| standard_code_quality.md | Checked automatically; incomplete globally | Ruff, mypy and Vulture pass for importer; deptry fails only on three wrkt test imports |
| standard_logging.md | Checked manually | No separate logger configured; raw build output suppressed; final aggregate reporting remains unimplemented |
| standard_naming.md | Checked automatically and manually | Ruff passes and public names added to registry |
| standard_security.md | Checked automatically | Bandit including B608 passes; pip-audit reports no known vulnerabilities after HTTPX installation |
| standard_tests.md | Checked automatically | 150 importer tests and 28 targeted architecture/plan tests pass; production database not touched |
| standard_time.md | Checked manually and by tests | Source header instant retained; monotonic deadlines; UTC PBF header; source-time tile archive mtime |
| standard_worker.md | Not applicable to this subset | No worker entry point or periodic schedule added |
| standard_frontend.md | Not applicable | No frontend changes |

Executed pytest on tests/service, tests/data, tests/architecture/test_osm_import_boundaries.py and tests/architecture/test_plan_document_contract.py: 178 passed. The full architecture run has 121 passes and two failures, both in repository-wide prose checks of wrkt. Ruff check and format, mypy on 16 source files, Bandit, Vulture and git diff --check pass. Pip-audit of the temporary tool/dependency environment reports no known vulnerabilities. Python 3.14.4 was used; baseline Python 3.13 verification remains outstanding.

The integrated synthetic test covers mocked download, dated checksum and header validation, real pyosmium boundary assembly, whole-way selection, normalized PBF writing, controlled tile-tool calls, source-time archive metadata, validated manifest and downloaded-file cleanup. Separate real local process tests prove cancellation and deadline termination. Failure never creates a manifest or current pointer. A fake-clock test proves a progressing transfer survives the former 15-minute ceiling.

### Verdict

Not ready for the complete initiative or a full merge-readiness claim. The added independent preparation stages pass their executed functional and static checks, but the blockers above remain. Keep plans/osm_importer active. No production import or database-backed test was performed.

## 2026-10-04 - Merge resolution and database availability

Resolved the five conflicted files by preserving both database and importer content. The database security pass and importer passes coexist, and Vulture scans both scopes. The naming registry retains the database entries and importer entries. The approved importer accessibility rule becomes specification version 14, preserving version 13 account and vote-calendar decisions; current service documentation and the plan follow the renumbering. The independent ownership handoff formerly numbered D-22 is retained as D-39 with its original conversation scope, while the approved recovery D-22 remains intact.

The real database implementation is now present in db/, including shared tables, enumerations and Alembic revision 0001. An AST-based comparison using the repository's schema-test normalization verifies all 22 schema statements and service-account grants against the target document. This proves source agreement, not an applied server revision. The interpreter lacks the installed database package and driver; neither .env nor .env.local exists and no database connection setting is supplied through the process environment. Docker socket access is denied both inside and outside the sandbox, so a live connection could not be checked. No database was started, migrated or modified.

Executed targeted importer, architecture, plan-contract and conflict-marker tests: 186 passed. Ruff check and format and git diff --check pass. Requested git add includes the resolved files and importer-owned source, tests and documents only; the separate wrkt worktree is excluded. No commit is made because AGENTS.md forbids agent-created commits even on explicit request. The database source prerequisite is now delivered, while actual connection and full importer execution remain unverified. The initiative remains active.

After staging, git diff --cached --check reports pre-existing whitespace warnings in mobile_app artifacts already in the index, including vendored files. They were not edited as part of conflict resolution. The five resolved files have no staged whitespace errors, git ls-files -u is empty and only the separate wrkt worktree remains untracked.

## Delivered database adapter review - 2026-10-04

Scope: data/osm_copy.py, service/osm_database_rows.py, their tests and dependency/documentation updates. Verdict: not ready for the whole initiative; live execution, complete fact selection, shared vote evaluation, exclusion, publication and routing recovery remain unfinished. The adapter subset has passing local checks but no PostgreSQL execution evidence. No initiative archival is warranted.

Verification:

- standard_agentic_workflow.md: checked automatically; architecture suite ran, parity and hook checks passed. No backend initiative or separate worktree edits.
- standard_agent_docs.md: checked automatically; 25 plan contract tests passed. Progress and durable memory updated.
- standard_review.md: checked manually; this result covers the adapter subset only.
- standard_documentation.md: checked manually; service/data documentation pairs and operating instructions updated.
- standard_formatting.md: checked automatically; scoped Ruff format passed. Global prose tests failed on existing mobile_app and wrkt content; no clean global gate is claimed.
- standard_git.md: checked manually; no commit, push or history operation performed.
- standard_architecture.md: checked automatically; all three importer boundary tests passed. Connection creation and transaction ownership remain outside the adapter.
- standard_config.md: checked manually; no environment reads, secrets or connection factory added. Environment contract tests skipped three absent configuration files.
- standard_database.md: checked manually; delivered table metadata and PostGIS binding used, SQL compilation tests passed. Deployed schema and execution remain unverified.
- standard_errors.md: checked manually; database exceptions propagate to the future transaction owner, no retry or commit guessing added.
- standard_idempotency.md: checked manually; present facts use the delivered OSM identity unique constraint and preserve identity and user fields. Full run recovery remains blocked.
- standard_code_quality.md: checked automatically; scoped Ruff, mypy for all 18 service/data modules and Vulture passed. Root deptry failed on dependencies in separate wrkt and mobile_app code; global dependency readiness is not claimed.
- standard_logging.md: checked automatically; Ruff passed and no independent logging or person identifier rendering added.
- standard_naming.md: checked automatically; Ruff passed and registry updated.
- standard_security.md: checked automatically; scoped Bandit passed with the existing subprocess suppressions. pip-audit found no known vulnerabilities in installed dependencies; local accessibility-db is unavailable on PyPI and skipped by the vulnerability service.
- standard_tests.md: checked automatically; 156 importer tests and 25 plan tests passed. Architecture: 128 passed, 3 skipped, 2 global prose failures. No live database test ran.
- standard_time.md: checked manually; aware instants retain offsets and schema precision loss fails explicitly. Date selection and the shared clock remain caller responsibilities.
- standard_worker.md: not applicable; no worker entry point or periodic task added, recorded deferral retained.
- standard_frontend.md: not applicable; no frontend changes.

## 2026-10-04 - Plan closed and importer completed on the delivered shared interfaces

Scope: closing Q-1 - Q-3 of OSM_IMPORTER_PLAN.md and implementing steps 2 - 8 against the interfaces the backend skeleton delivered. The earlier entries remain historical; their blockers on the missing engine, exclusion, publication, logger, clock and Python 3.13 environment are superseded by this entry.

### User decisions recorded in the plan

D-40 refuses a refresh with a first disappearance while the shared vote evaluator is not delivered. D-41 takes the Valhalla tool directory and template from the settings and leaves the image to plans/deployment_config/. D-42 moves database-backed tests to the local database of db/compose.yaml, superseding D-33. D-51 keeps the needs of plans/route_planning/ out of this implementation. The user approved installing the pinned dependencies, starting the local database and pulling the Valhalla image for a temporary verification container.

### Implementation decisions

Agent decision at C:40, without asking: D-43 - D-50 close the remaining parts of Q-1 - Q-3 with the delivered interfaces: engine, exclusion, publication, deadlines, clock, logger, routing layout and pointer, fact derivation scope, unlocked fact reads, commit-outcome checks, outcomes and exit codes, download into the run workspace and the settings entries. The plan records each of them.

Agent decision at C:40, without asking: the shared apply_transaction raises every callback failure as an anonymous rollback, so the publication step keeps a named refusal of its callback and re-raises it after the rollback. This keeps D-46's checks inside the transaction while the operator still sees the D-40 refusal by name.

Agent decision at C:40, without asking: build_osm_stamp cuts the server stamp to the whole millisecond before it is written, because the schema stores timestamptz(3) and the adapter refuses finer precision. The critical scenario found this; the unit fakes did not.

Agent decision at C:40, without asking: the HTTP client is built in service/osm_import.py by apply_osm_import_command rather than in the worker. Step 6 of the plan said the worker builds it, while step 7 forbids the worker to import data; the boundary wins.

Agent decision at C:40, without asking: the database checks of step 5 run as one ordered scenario in tests/service/test_osm_import_critical.py instead of a separate tests/data/test_osm_copy_critical.py. Publication commits and the service account may not delete copies or facts, so independent tests cannot clean up; the scenario requires a database without any copy and is run on a freshly recreated one.

Agent decision at C:40, without asking: recovery with no committed copy does nothing even when a pointer exists, because D-22 concerns the confirmed copy and the next commit replaces the pointer.

Agent decision at C:40, without asking: resolve_osm_element_coverage no longer validates the boundary on every call and tests points against a prepared boundary, because build_osm_boundary already validates it and the fact pass tests every way of the extract.

Agent decision at C:40, without asking: the shared path validators of config/settings.py were renamed to build_path_entry and apply_absolute_path_validation, because they now serve four entries, ROUTING_DATA_DIR of route_planning included.

The test environment files with generated local passwords live in the session scratchpad, not in the repository root, so other sessions' configuration-dependent tests on the shared tree are not changed.

### Coordination with concurrent sessions

plans/route_planning/ added ROUTING_DATA_DIR to the settings as a required entry while this work ran. Under D-51 its single definition replaces D-50's optional entry; VALHALLA_TOOL_DIR and VALHALLA_CONFIG_TEMPLATE stay optional. That session wrote the records of all four entries in standard_config.md. With this session's agreement it may append its boundary helpers at the end of data/routing_data.py. The S-6 example of its plan used a wrong epoch value; the session was told and corrected it. A human commit at 06:53 already contains a snapshot of this work. Another session is writing service/fact_status.py with resolve_fact_status, which may become the shared evaluator D-40 waits for; it is uncommitted and not agreed for the importer, so it is not used.

### Verification

| Check                                                                                                                           | Result                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Importer, data, worker, config, boundary and plan-contract tests on Windows, Python 3.13.14                                     | 416 passed, 6 Linux-only skipped, critical deselected                                                                    |
| Critical import scenario and concurrent skip on a freshly migrated local database of db/compose.yaml                            | 2 passed                                                                                                                 |
| Importer, data and worker tests in a Linux container with Python 3.13                                                           | 122 passed, including real process supervision and deadline termination                                                  |
| Real tile build from an invented source through apply_osm_routing_preparation in a container of ghcr.io/valhalla/valhalla:3.9.0 | copies/1790985600 with the three files, archive time equal to the source instant, Valhalla routes 2.86 km over the tiles |
| Ruff check and format, mypy, Vulture, Bandit                                                                                    | clean for every changed file; remaining findings belong to mobile*app, route*\* and other sessions' files                |
| Prose style and Prettier 3.7.4                                                                                                  | clean for every changed document; remaining findings are in mobile_app                                                   |
| Plan contract                                                                                                                   | 25 passed with the plan closed                                                                                           |

The critical scenario covers first import, refresh with preserved fact identity, vote and flag, updated step count and edit day, removal of an obsolete way and node, unchanged, older refused, the D-40 refusal leaving the database and pointer unchanged, a converted fact staying absent, and the return of a converted and a removed fact with their votes.

### Not verified

A real Geofabrik import has not run: it needs the user's approval of the download, and this machine had about 1.7 GB of free memory. Peak memory and duration on the whole Małopolska extract are unmeasured. The backend image of plans/deployment_config/ does not exist, so the in-image command is not verified. pip-audit was not run because no dependency was added. The shared apply_completion_wait waits without an upper bound, which can exceed the run deadline after a lost commit confirmation (R-15).

## 2026-10-04 - Shared vote evaluator connected in place of the D-40 refusal

Scope: the last open piece of code of the initiative - the decision on facts that disappear from OpenStreetMap for the first time (step 4 and step 5 of OSM_IMPORTER_PLAN.md, D-8, D-15, D-40). The earlier entries stay as they were; their statements about the missing evaluator are superseded by this one.

### User decisions recorded in the plan

D-52 connects `resolve_fact_status` of `service/fact_status.py`, delivered by plans/route_planning/, as the shared evaluator D-40 waited for, although D-40 named plans/community_facts/ as its owner. D-53 leaves the real Geofabrik import and its measurement to a human after the closure. The user also chose to run the critical scenario on a new, separate Compose project of db/compose.yaml, removed after the run, rather than recreating the database another session had started. Facts F-3 (specification version 17) and F-27 (the delivered evaluator) were corrected before the implementation.

### Implementation decisions

Agent decision at C:40, without asking: the disappearing facts are decided in `apply_osm_disappearance`, after the network and the present facts are written and right before the copy row, so the votes of those facts stay frozen only for the rest of the transaction (D-15 asks for a brief freeze). The decision is made on the rows read under the locks, not on the unlocked read that found them.

Agent decision at C:40, without asking: `OsmReconciliationError` is removed together with its place in `OSM_IMPORT_NAMED_ERRORS` and in the named refusal of `apply_osm_publication_step`, because no refusal remains. The unit test of the named refusal now uses `OsmSourceError`, the one refusal the callback still has.

Agent decision at C:40, without asking: `OsmPublicationCounts` gets no count of converted or removed facts, because D-48 and FR-11 do not ask for one; it is listed below as an improvement rather than added as an unagreed change of the operator report.

Agent decision at C:40, without asking: the check that the locks are held runs at the end of the ordered critical scenario, in a publishing transaction that is rolled back, because the service account cannot delete the facts and votes such a check needs and the scenario already leaves them in a known state.

### Coordination with concurrent sessions

Other sessions changed the tree while this work ran: route planning, public transport and their tests. Their files are not touched here. `ruff format --check` reports data/engine.py, data/route_network.py, service/route_requests.py and service/route_segments.py; Vulture reports tests/service/test_actors_cases.py, tests/service/test_gtfs_import_cases.py and tests/service/test_routing_service_config_cases.py; the repository-wide prose checks fail only on mobile_app content. plans/route_planning/ D-20 makes the boundary file and the Valhalla overrides of D-51 itself once the importer's work is committed; that commit is a step for a human.

### Verification

| Check                                                                                                                                                                                                                                                       | Result                                                                                                                                                                                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit tests of the decision: AC-6 (1.5 against 0.5 converts; no votes, only denials and a 0.5 tie remove), a confirmation total below 2, AC-7 (latest vote of a person, the window of five persons, detached votes), one fact's votes never deciding another | 9 new cases pass                                                                                                                                                                                                                                                                                         |
| SQL of the fact lock                                                                                                                                                                                                                                        | Compiles to `fact.id = ANY (...) ORDER BY fact.id FOR UPDATE`                                                                                                                                                                                                                                            |
| Tests of service, data, worker, config, architecture and common time on Windows, Python 3.13.14 of the repository venv, not critical                                                                                                                        | 765 passed, 9 skipped; the 2 failures are the prose checks of mobile_app                                                                                                                                                                                                                                 |
| Critical scenario and concurrent skip on the freshly migrated Compose project osm-importer-close of db/compose.yaml                                                                                                                                         | 2 passed: conversion of a fact with 1.5 against 0.5, removal of a fact with a 0.5 tie, both staying absent in the next copy, both returning with all votes, and on two connections the disappearing fact and its votes locked with `NOWAIT` refused, a plain read going on and a present fact not locked |
| Ruff check and format, mypy, Bandit with B608                                                                                                                                                                                                               | Clean for every changed file; mypy clean for all 77 configured sources                                                                                                                                                                                                                                   |
| Vulture                                                                                                                                                                                                                                                     | No finding in the importer; findings only in other sessions' tests                                                                                                                                                                                                                                       |
| Prettier 3.7.4 and the plan contract                                                                                                                                                                                                                        | Clean for every changed document; plan contract passes                                                                                                                                                                                                                                                   |
| git diff --check                                                                                                                                                                                                                                            | Clean for every changed file                                                                                                                                                                                                                                                                             |

### Not verified and remaining risks

- The real import of the Geofabrik extract, its duration and peak memory (D-53, R-13) and the failure of R-14 on real data remain a step for a human.
- The vote write that locks its fact before validating (D-15, R-8) belongs to plans/community_facts/ and does not exist yet; until it does, no vote write can race the freeze.
- The shape of plans/community_facts/ still lists a status evaluator of its own (R-12); a change of `resolve_fact_status` must be followed by `resolve_osm_fact_changes`.
- The backend image of plans/deployment_config/ and the hosted-demo run are not part of this initiative.

### Improvements

- The operator report could count converted and removed facts next to the facts written; it needs an agreed change of D-48.

### DoD review of the evaluator integration and of the initiative

Blockers: none in the scope of the initiative.

Risks:

- R-1. The repository-wide gates are not clean, but every finding lies outside this initiative: `ruff check` and `deptry` only in mobile_app, `ruff format --check` in mobile_app, data/engine.py and the route planning files, Vulture in tests of other sessions, the prose checks in mobile_app, and Prettier in mobile_app, valhalla/README.md, plans/accounts/ACCOUNTS_PLAN.md and the account tables another session added to data/DATA.md and service/SERVICE.md during this review.
- R-2. The earlier entries of this review keep their unaligned tables, so Prettier reports this file while it lies in plans/; the entries are protected history and are not reformatted, and `.prettierignore` skips plans_finished/.
- R-3. The open decision Standards of the worker without periodic tasks of docs/standards/decision_registry.md now meets its condition, because worker/osm_import.py exists; plans/repository_consistency/ tracks the rewrite as U-4, and it is not work of this initiative.
- R-4. The vote write of D-15 and the evaluator ownership of plans/community_facts/ stay with that initiative, recorded as Backend handoff for vote locking during OSM publication in docs/standards/decision_registry.md and as R-12 of the plan.
- R-5. The real Geofabrik import, the backend image, the hosted-demo run, the commits and the Merge Request are steps for a human (D-53, Rollout order); closing the initiative proves nothing about them.

Improvements: the operator report could count converted and removed facts after an agreed change of D-48. The stale Goal paragraph of the plan that still called it a technical draft was corrected during this review.

| Standard                     | State                 | Evidence                                                                                                               |
| ---------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| standard_agentic_workflow.md | Checked automatically | Parity, vendored content, session context and dangerous command hook tests pass                                        |
| standard_agent_docs.md       | Checked automatically | Plan contract passes; review and memory entries follow the format                                                      |
| standard_review.md           | Checked manually      | Every standard listed; verdict scoped                                                                                  |
| standard_documentation.md    | Checked manually      | Data and service purpose and algorithm documents, operating instructions and docstrings describe the decision          |
| standard_formatting.md       | Checked automatically | Ruff format and Prettier clean for every changed file and every new entry; remaining findings outside the initiative   |
| standard_git.md              | Checked automatically | Conflict marker test passes; no add, commit, push or history operation                                                 |
| standard_architecture.md     | Checked automatically | Layer boundary and importer boundary tests pass; service decides, data locks and writes                                |
| standard_config.md           | Checked automatically | Environment contract and critical environment guard tests pass; no new entry; local credentials only in the scratchpad |
| standard_database.md         | Checked automatically | Bandit B608 clean; parameterized batches, locks in ascending identity order, permitted UPDATE grant on fact and vote   |
| standard_errors.md           | Checked manually      | No new exception; database failures roll the whole publication back                                                    |
| standard_idempotency.md      | Checked manually      | A converted or removed fact that stays absent is not decided again; an equal source state stays unchanged              |
| standard_code_quality.md     | Checked automatically | Ruff check, mypy on 77 sources and Vulture clean for the importer; deptry findings only in mobile_app                  |
| standard_logging.md          | Checked automatically | Ruff check clean; no log line added                                                                                    |
| standard_naming.md           | Checked automatically | Ruff check clean; fetch, resolve and apply prefixes; registry updated                                                  |
| standard_security.md         | Checked automatically | Bandit clean; no dependency added, so pip-audit is not required                                                        |
| standard_tests.md            | Checked automatically | 765 tests pass outside the critical set; the critical scenario and the skip pass on a freshly migrated local database  |
| standard_time.md             | Checked manually      | The evaluator orders votes by their instants; the business day comes from the configured zone                          |
| standard_worker.md           | Not applicable        | No worker change; the open registry entry covers the one-off command                                                   |
| standard_frontend.md         | Not applicable        | No frontend change                                                                                                     |

### Verdict

Ready, for the whole initiative: the code, tests and documentation of FR-1 - FR-13 and AC-1 - AC-14 under the plan, with the evaluator of D-52 connected. The steps of R-5 stay with a human.

### Archiving

The user chose on 2026-10-04 to archive the initiative now rather than wait for plans/route_planning/ to make the change of its D-20. That change touches importer code and documents, which stay editable, but its note can no longer go to the Implementation progress section of this plan without a resumption under ch. 4.6 of docs/standards/standard_agentic_workflow.md; plans/route_planning/ records it in its own review instead. The directory moves to plans_finished/osm_importer/.
