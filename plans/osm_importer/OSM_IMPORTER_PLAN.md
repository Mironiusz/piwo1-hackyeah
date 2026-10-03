# Plan: Implement the OpenStreetMap importer for Kraków

Document state: 2026-10-04, plan in progress

## Goal

Implement `OSM_IMPORTER_PRD.md` FR-1 - FR-12 and AC-1 - AC-11, approved by the user on 2026-10-04. Deliver the first import, manual refresh, source validation, the pedestrian network, accessibility mapping, atomic publication and reconciliation without losing votes or moderation state.

The user reported that Rafał, who owns the MVP work, confirmed he would handle the import ownership handoff. No file under `plans/mvp/` is edited by this initiative. The shared backend, local database setup and schema revision remain external prerequisites.

This is a technical draft, not an executable closed plan. The file allocation below is a proposal for the backend owner to review, not a claim that those modules or shared interfaces already exist. Q-1 - Q-3 must be answered before the allocation, adapters and rollout commands are finalized.

## Facts

F-1. The shape has a closed interview at C:40, and its scope assigns the complete importer and its tests to this initiative while excluding shared backend and schema delivery. | doc:`plans/osm_importer/OSM_IMPORTER_SHAPE.md` header, Smallest meaningful scope and Out of scope | 2026-10-04
F-2. The user approved the PRD and requested the technical plan, reporting Rafał's commitment to handle the MVP handoff. | doc:`plans/osm_importer/OSM_IMPORTER_PRD.md` state and Risks and notes; doc:`plans/osm_importer/OSM_IMPORTER_SHAPE.md` WARNING: IMPORT OWNERSHIP HANDOFF BEFORE IMPLEMENTATION | 2026-10-04
F-3. The current specification is version 7; M2, M3, M4 and M6 define the network, fact list, votes, disappearance, return and copy freshness. | doc:`docs/product/specification.md` state and M2 - M6 | 2026-10-04
F-4. The selected source is the Geofabrik extract of Małopolska; the agreed reader is osmium 4.3.1, and the area is Kraków relation 449696 with selected ways kept whole. | doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-1, D-2 and D-6 | 2026-10-04
F-5. The source plan fixes dated downloads, the published MD5 check, the header state instant, explicit timeouts, no retries within a run, database exclusion before download and temporary-file cleanup. | doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-3 - D-5 and D-11 - D-16 | 2026-10-04
F-6. The target schema is part of the specification; the import writes osm_copy, osm_way, osm_node, osm_way_node and facts with an OpenStreetMap identity in one transaction. | doc:`docs/product/schema.md` Why this document exists and Who writes what | 2026-10-04
F-7. The current-copy history is append-only in osm_copy; fact identity remains unique across conversion and removal, and no fact or vote is deleted. | doc:`docs/product/schema.md` OpenStreetMap copy, Facts and Who writes what | 2026-10-04
F-8. The service role has no DDL rights; osm_copy permits select and insert, the network tables permit select, insert, update and delete, and fact and vote permit select, insert and update. | doc:`docs/product/schema.md` Rights of the service account | 2026-10-04
F-9. No product backend, Alembic revision or database setup is present among the current repository files; the tree has architecture tests and planning documents instead. | cmd:`rg --files -g '*.py' -g '*.sql' -g '*compose*' -g '*alembic*' -g '*engine*' -g '*database*' -g '!node_modules/**'` -> no product Python code, SQL revision, Compose file or engine; doc:`plans/schema_revision/SCHEMA_REVISION_SHAPE.md` Recipient and trigger | 2026-10-04
F-10. Runtime dependencies are empty and the project requires Python 3.13 or newer; the dev group pins pytest 9.1.1. | code:`pyproject.toml:12`; code:`pyproject.toml:13`; code:`pyproject.toml:21` | 2026-10-04
F-11. The MVP plan still leaves the import trigger, execution machine, tag module names, shared backend structure and database timeouts to the backend architecture owner. | doc:`plans/mvp/MVP_PLAN.md` D-4, D-5 and Q-11; doc:`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-12 | 2026-10-04
F-12. Routing consumes ordered node identities and positions; its graph is rebuilt when the current source-state instant changes, and its reads must describe one copy. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-3, D-4 and D-11 | 2026-10-04
F-13. Shared connections, configuration and logging must have one definition; the prescribed root layers are api, service, data and worker. | doc:`docs/standards/standard_architecture.md` Layer boundary, Shared helpers and Loggers; doc:`docs/standards/standard_naming.md` File names; doc:`docs/standards/standard_config.md` Three configuration layers and four storage places | 2026-10-04
F-14. The specification makes unlisted tag values unknown and lists an elevator as a point; the archived mapping plan instead permits surface fallback for unlisted smoothness and elevators on areas. | doc:`docs/product/specification.md` M6 Reading OpenStreetMap tags, Poor surface and Elevator; doc:`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-10 and D-13 | 2026-10-04
F-15. Unit tests exclude filesystem, network and database access; integration tests may use invented files with fake downloads, and database writes require critical tests confined to a local database. | doc:`docs/standards/standard_tests.md` Test layers and Mandatory tests; doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-16 and D-22 | 2026-10-04
F-16. The default Python is 3.14.2, while the pytest executable belongs to Anaconda Python 3.8 with pytest 5.4.3; that executable is not the project's configured test environment. | cmd:`python --version` -> Python 3.14.2; cmd:`pytest --version` -> pytest 5.4.3 from anaconda3/lib/python3.8/site-packages | 2026-10-04
F-17. The current machine reports approximately 22 GB available RAM and 593 GB available space on the filesystem containing /tmp; these are local observations, not hosted-demo resource guarantees or importer measurements. | cmd:`free -m` -> available 22758 MiB; cmd:`df -Pm /tmp` -> available 593754 MiB | 2026-10-04
F-18. The previous source measurement recorded a roughly 202 MB download and 297 - 377 seconds of processing at 980 MB peak memory; it did not measure this implementation or its database publication. | doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` F-3, F-4 and F-11 | 2026-10-04
F-19. Official pyosmium documentation describes location storage for ways, area assembly with outer and inner rings, and original identities for areas; arbitrary relation geometries are not assembled automatically. | doc:`https://docs.osmcode.org/pyosmium/latest/user_manual/03-Working-with-Geometries/` Line geometries, Areas and Geometries from other relation types | 2026-10-04

## Decisions

D-1. Retain the source, reader and acquisition contract already chosen in the source initiative. This work does not introduce Overpass or another fallback. Dependency decision adopted from F-4 and F-5, not a new source choice.

D-2. Follow version 7 of the specification wherever historical mapping artifacts differ. In particular, an unlisted smoothness value must not become an explicit absence through surface fallback, and an area tagged as an elevator is not automatically a point-elevator fact. Test both divergences. Agent decision at C:40, without asking: the specification's precedence is explicit, and this does not authorize changing product behavior (F-3, F-14).

D-3. Keep source acquisition and persistence in data, product decisions in service, and the administrative trigger in worker. Reuse the shared connection, configuration, clock, logger and vote-rule interfaces the backend owner supplies. No substitute infrastructure is built to bypass Q-1. Agent decision at C:40, without asking: the layer and shared-helper standards already require this (F-13).

D-4. Use the same source-state comparison for the first import and refresh. A source state equal to the latest osm_copy.state_at yields unchanged; an earlier state fails; a later state can proceed. No publication is attempted for unchanged or skipped runs. Dependency decision adopted from source D-5 and PRD FR-10.

D-5. Complete download, checksum, header validation, boundary assembly, reference checks and derivation before starting the publication transaction. Hold import exclusion from before the download until publication ends. The lock must survive that separation without keeping a write transaction open during network waits; its connection and lifetime depend on Q-1. Agent decision at C:40, without asking: this combines the already agreed exclusion and complete-copy requirements (F-5, F-6).

D-6. The publication transaction upserts the current network and imported facts, removes obsolete network membership, ways and nodes, reconciles disappearing facts and appends the copy history row. It never uses TRUNCATE, creates persistent staging tables or changes permissions. Agent decision at C:40, without asking: the target schema and service rights permit these DML operations and reserve schema delivery for its owner (F-6 - F-8).

D-7. Preserve fact.id, created_at and its offset, flagged_at, hidden_at and their offsets when an identity is refreshed or returns. Update only imported geometry, step count, source, edit day and the removal marker as the product requires. Never issue a write against vote, account or independent user facts. Agent decision at C:40, without asking: these fields have separate ownership in the target schema and PRD FR-6 - FR-9 requires preserving history and moderation.

D-8. Select vote history in bounded batches and call the same pure vote evaluator the backend uses. Confirmations must outweigh denials over the latest votes of five persons; a confirmation total below 2 can still cause conversion. Detached votes retain their weight and each count as a separate person. The shared evaluator and concurrency contract are unresolved in Q-1; they are not duplicated in the importer. Agent decision at C:40, without asking: this follows M4 and the rule of one source for cross-cutting decisions.

D-9. Source state_at comes from the aware source header instant, with its original offset; osm_edited_on is that element's edit instant converted to a Warsaw day. Server-created timestamps and offsets use the shared clock and configured business zone. Elapsed durations use a monotonic clock. No download timestamp replaces source freshness. Agent decision at C:40, without asking: these are different time meanings fixed by the specification, schema and time standard.

D-10. Keep source directory, malopolskie stem, Kraków relation, timeouts, mapping thresholds and tag lists in third-layer constants next to their rules. Source requests have 30-second redirect/checksum deadlines, a 15-minute file-download deadline and a 60-minute whole-run deadline. Do not add a schedule. Database deadlines and enforcement of the whole-run cancellation remain Q-1. Dependency decisions adopted from source D-11, D-12 and D-15 and mapping D-14.

D-11. Temporary downloads and location storage stay outside the repository and are removed after success, unchanged or failure. Use immutable typed snapshots of pyosmium objects rather than retaining iterator-backed objects across callbacks. Store only the agreed current network and derived facts; do not add a raw OSM archive to the database. Agent decision at C:40, without asking: this implements the existing retention and shared-schema scope.

D-12. Batch database work, parameterize values and explicitly list returned columns. No per-fact vote query, geometry matching of identities, automatic vote, status column or deletion of a fact is added. Integrity and parsing failures abort the whole run rather than silently dropping a required element. Agent decision at C:40, without asking: these are direct consequences of PRD FR-5 - FR-10 and the database, idempotency and quality standards.

## Scope of changes

The following paths and function names are proposed importer-owned files. They follow the prescribed layer directories but are not an agreed handoff yet. No existing shared module is assigned to this initiative. Q-1 may change this allocation before the plan is closed; the final plan must replace each unresolved shared adapter with its verified callable, input, output and owner.

### Step 1. Source acquisition and cleanup

Proposed files: `data/osm_source.py`, `tests/data/test_osm_source_cases.py`.

`fetch_osm_extract` takes the shared HTTP client and a run-local temporary directory. It requests the latest URL without following redirects, validates the dated Location against the exact HTTPS source directory and malopolskie filename pattern, then streams that dated PBF and its dated checksum. Redirects for those dated resources are not silently followed to another source. The declared deadlines also bound elapsed download time rather than just inactivity between chunks.

`resolve_osm_source_location` and `resolve_osm_checksum` implement pure validation over already obtained values. The output is a validated local file and dated filename, or a named source exception. Tests cover invalid hosts, paths, names, HTTP statuses, corrupt checksums, transport failures, timeouts and cleanup. No live source call is part of the tests.

### Step 2. PBF reading, boundary and geometry

Proposed files: `data/osm_reader.py`, `service/osm_geometry.py`, `tests/service/test_osm_geometry_cases.py`, `tests/data/test_osm_reader_integration.py`.

`fetch_osm_elements` reads the file header and required elements through osmium. `build_osm_boundary` assembles relation 449696 with every ring required for the area; a missing, open or unusable boundary fails. `resolve_osm_element_coverage` applies source D-6: inside nodes, whole ways with at least one inside node, and the agreed selected relations without treating their other members as imported network.

Preserve node order, repeated node identities, coordinates and source timestamps. Validate every required reference before producing a network row. Assemble geometry from the full source before applying the selected-area cut, so reference loss in a cut does not produce an invented location. Q-3 decides the geometry tool, representative point rule and treatment of selected relations whose full geometry cannot be built.

Output: typed element snapshots with original node, way or relation identity, geometry, tags and edit time. The invented-file integration test covers holes, multiple outer rings, ways crossing the boundary, missing references and invalid geometries.

### Step 3. Network selection and tag mapping

Proposed files: `service/osm_tags.py`, `tests/service/test_osm_tags_cases.py`.

`resolve_osm_pedestrian_way` implements exactly M2, with the accepted highway and foot values and all exclusions. Compute motor-traffic membership from the appropriate source ways independently of whether those ways themselves remain walkable, so crossing nodes do not lose that information.

`resolve_osm_way_attributes` produces the four stored barrier states, wheelchair marking, motor-traffic marking and crossing marking. `resolve_osm_node_attributes` produces the kerb state or null, crossing flag and motor-traffic membership. `build_osm_facts` produces only present facts of the eleven accepted types, with original element identity, edit day, geometry and optional step count.

Input: already read typed elements, geometry and memberships. Output: typed rows matching osm_way, osm_node, osm_way_node and imported fact fields in `docs/product/schema.md`. No preference, database read or network call enters the mapping.

Tests cover all lists and thresholds, unsupported units, unknown values, the sidewalk rules, kerb conflicts and stop exclusions, ramp and handrail rules and D-2's specification precedence. The importer does not implement route-segment combination or contradiction evaluation; those remain routing responsibilities.

### Step 4. Fact reconciliation

Proposed files: `service/osm_reconciliation.py`, `tests/service/test_osm_reconciliation_cases.py`.

`resolve_osm_fact_changes` takes the fresh identities, stored imported facts and the output of the shared latest-vote evaluator from Q-1. It returns typed imported-field updates: present facts use openstreetmap and clear is_removed_from_osm; newly missing OpenStreetMap facts either become user_report without the removal mark or remain openstreetmap with the mark. Previously converted or removed facts that remain absent are not converted again solely because a later refresh occurs. No identity or vote history is replaced.

Tests exercise all PRD conversion and return cases, latest-person selection through the shared evaluator, detached votes, changed attributes, a nearby independent report, new identities after a split and preservation of hidden and flagged state.

### Step 5. Database publication

Proposed files: `data/osm_copy.py`, `tests/data/test_osm_copy_critical.py`.

`fetch_current_osm_copy`, `fetch_osm_fact_history` and `apply_osm_copy` use only the shared connection/session mechanism agreed in Q-1 and the service role. `fetch_osm_fact_history` selects explicit vote fields in batches without logging voter identifiers. `apply_osm_copy` takes the complete typed network, fact updates and copy metadata and executes one publication transaction.

Upsert nodes and ways, remove old way-node memberships and replace them with ordered memberships from the new copy, remove obsolete ways and then unreferenced obsolete nodes, and upsert facts under UX_fact_osm_identity. Only imported fields appear in the conflict-update clause. Apply disappearance decisions and append osm_copy within the same transaction. An unchanged state produces no new history row. No TRUNCATE, DDL, fact deletion or vote write occurs.

Input and output must be finalized against the delivered revision in Q-2. Publication and community changes must observe the concurrency protocol from Q-1; reading votes before download and applying a stale decision afterwards is forbidden. Critical tests cover initial publication, refresh, obsolete memberships, rollback at several stages, identity uniqueness, role rights, timestamp/offset round trips and concurrent community writes.

### Step 6. Administrative orchestration

Proposed files: `service/osm_import.py`, `worker/osm_import.py`, `tests/service/test_osm_import_integration.py`, `tests/worker/test_osm_import_cases.py`.

`apply_osm_import` orchestrates exclusion, acquisition, reading, mapping, state comparison, reconciliation and publication through the agreed data seams. The worker entry point calls that service operation through the shared launcher; its exact command and shared interfaces are Q-1.

Output: a typed outcome of updated, unchanged or skipped; a named failure records that the run failed. INFO records start, outcome, duration and aggregate counts; errors include a safe cause and caught traceback without connection strings, vote identifiers or raw external responses. A cleanup or post-publication reporting error must not misreport a committed copy as rolled back. The whole-run timeout must cancel or terminate outstanding work before releasing exclusion, including a blocked parser or database operation.

Tests fake acquisition and persistence and run the full mapping pipeline on an invented OSM file. Critical tests hold exclusion in a second connection to verify skipped concurrent runs and verify release after failure. Register no periodic task.

### Step 7. Dependencies and checks

Existing files affected: `pyproject.toml` and `makefile`. Proposed verification file: `tests/architecture/test_osm_import_boundaries.py`.

Add the previously selected `osmium==4.3.1` pin without replacing dependencies concurrently added by other owners. Q-1 and Q-3 determine whether any additional shared HTTP or geometry dependency is needed; do not introduce a second tool for a covered problem. Verify wheels on the project's Python 3.13 baseline and audit newly introduced dependencies at implementation time.

Extend the existing mypy, vulture and security scope to the delivered importer modules, keeping all current shared scopes. Confirm who owns the general architecture gates; add only importer-specific guards here, checking that the administrative trigger calls service rather than data and is absent from the public API and periodic schedule. Consume the shared critical-test refusal and cleanup fixtures supplied under Q-2 rather than duplicating them.

### Step 8. Documentation and handoff

Proposed operating document: `docs/import/osm_importer.md`. Proposed service documentation: `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md`, updated with the backend owner rather than overwritten. Their creation or extension follows the code-unit condition in `standard_documentation.md`; other layer pairs are added only when that condition is met.

Document the exact launch and verification commands settled in Q-1 and Q-2, source validation, current-copy query, outcomes, temporary-data retention and the integrity failure path. State the source-state day separately from download and publication time. Include source provenance, ODbL attribution references and the recorded verification method without copying target-environment identifiers.

The implementation review records the acceptance results in `OSM_IMPORTER_REVIEW.md`. Append durable memory only for actual reusable decisions discovered during implementation. Keep this initiative in plans while its implementation remains unfinished.

## Rollout order

1. Answer Q-1 - Q-3 and replace proposed allocations and shared adapters with the agreed contracts. Re-read the current PRD, schema and backend changes before closing this plan. No step implements the shared backend or schema as part of this initiative.
2. After the user separately requests implementation, build the pure source validation, network/tag mapping and reconciliation with invented-input tests (steps 1, 3 and 4).
3. Build the reader and geometry integration (step 2) with the agreed geometry contract.
4. Once the local setup, shared engine, revision and local-only critical fixtures have been delivered by their owners, implement and exercise publication (step 5). Verify the actual local schema and rights before the first test write.
5. Connect administrative orchestration, exclusion, deadlines, outcomes and shared logging (step 6), then finish dependency and architecture checks and documentation (steps 7 and 8).
6. Run the applicable quality gates and local critical scenarios. Measure parsing and publication duration and peak memory on the selected execution machine; the historical source measurements do not replace this run. A real local import uses temporary storage outside the repository and no exported vote/account data. Any hosted-demo run still requires the user's explicit request.
7. Perform the implementation DoD review. Do not archive the initiative merely because the technical plan has been closed.

Steps for a human: complete local secret files, if required; explicitly invoke schema changes and hosted-demo operations that need human authorization; handle the MVP ownership edit; create commits and the Merge Request.

## Definition of Done

- This plan has the state plan closed only after Q-1 - Q-3 are answered, final shared names and launch/verification commands are recorded, proposed allocations are agreed, and Open questions states None.
- PRD AC-1 - AC-11 are covered by the listed unit, scenario, integration and local critical runs. Results show complete-copy rollback, exclusion, identity preservation, current-copy dates, mapping boundaries and untouched votes, independent reports and moderation fields.
- No app request or schedule starts an import. The routing consumer can load every stored way with its ordered node coordinates and detect the new source-state instant.
- Network tables and fact writes use only the delivered shared schema and permitted DML. No migration, raw archive, status column, vote write, geometry deduplication or fallback source is added.
- The shared latest-vote rule is called, not rewritten. Tests cover confirmations versus denials, five latest persons, repeated votes and detached identities.
- Current specification behavior wins over archived mapping deviations, with explicit tests for the two differences of D-2.
- Checkpoints report updated, unchanged, skipped and failed accurately, including failures after a successful commit. Temporary source data never enters the repository and is cleaned up after the run.
- The implementation passes the applicable make check gates with pinned development tools; local critical tests pass under the shared environment guard. Any unavailable check is recorded explicitly and prevents a claim that its requirement passed.
- English operating and code-unit documentation is complete. The implementation review reports every applicable standard and reaches ready for the implemented scope before the initiative is treated as finished.
- No file under plans/mvp is edited by this initiative, and no target address, login or secret enters any artifact.

## Risks

- R-1. The shared interfaces do not exist in this tree yet. The proposed modules are not permission to define a separate backend, logger, engine or vote evaluator. Closing the plan before Q-1 is resolved would guess contracts.
- R-2. The target schema has not been verified on a delivered local database in this phase. Revision correctness, grants, serializable/concurrent behavior and PostGIS operations still require the owner's handoff and real critical tests. No hosted database was inspected.
- R-3. A publication based on inconsistent vote reads could convert a disappearing fact incorrectly while votes or anonymous identifiers change. Excluding a second importer does not itself exclude these backend writes. Q-1 must define the shared transaction protocol and its failure behavior.
- R-4. Historical mapping D-10 and D-13 differ from the current specification (F-14). Applying those historical statements without checking precedence would invent known accessibility or broaden the fact list's interpretation.
- R-5. Invalid geometry, missing source references and a positive step_count outside the schema's smallint range can make a selected source element impossible to publish. Do not silently truncate, invent a point or drop that element; settle Q-3 and retain the complete-copy failure policy.
- R-6. The old runtime and memory measurements exclude this publication implementation. A hosted import may compete with the existing owner's services, and a local resource check does not settle the execution machine. Q-1 and a real local measurement must resolve that placement.
- R-7. The whole-run deadline cannot be merely a timeout while background parsing or a database transaction continues. Exclusion stays held until that work has ended, with rollback or an accurately reported commit.
- R-8. WARNING: MVP OWNERSHIP EDIT IS RAFAŁ'S RESPONSIBILITY. The user confirmed his commitment; this is not evidence that the current MVP file has already been edited. This initiative supplies the importer and its tests and consumes shared prerequisites. No further MVP change is made or requested here.
- R-9. The available Anaconda pytest is incompatible with the project's required environment. The document checks must use a compatible interpreter and the pinned pytest, rather than claiming that an old executable validates the project.

## Open questions

- Q-1. Block: yes; categories: source of truth for data, read visibility and permissions, idempotency and deduplication. Which agreed backend contract supplies the shared connection/session, logger, clock, current-vote evaluator, exclusion wrapper, transaction isolation and database deadlines? Where do importer modules belong, what command starts a manual run and on which machine does it execute? The user has been asked to point to Rafał's file or branch, or state that this contract is to be decided with the user in this initiative. No answer is inferred from elapsed time. Include the publication/community-write concurrency protocol and ownership of shared check files in this handoff.
- Q-2. Block: yes; categories: database schema and form of a schema change. Which local setup, revision identifier and shared critical-test fixtures will the schema/backend owners deliver, and what exact readiness and test commands will the importer consume? The target is docs/product/schema.md; this initiative neither creates the revision nor treats that target document as proof of applied schema. Delivery can be a rollout prerequisite, but the interface and owner must be unambiguous before the plan closes.
- Q-3. Block: yes; category: source of truth for data. Which geometry tool and representative-point contract should the importer use for fact locations on ways and within selected areas? The target schema requires one point per fact, but no shared geometry implementation is delivered. Confirm how selected non-area relations or missing geometry references end the run; the proposal is a named failure preserving the previous complete copy, with no guessed location. The proposal introduces no second geometry tool if the backend contract already covers this work.

## Supplementary files

- `OSM_IMPORTER_SEED.md`, the unchanged request and MVP restriction.
- `OSM_IMPORTER_SHAPE.md` and `OSM_IMPORTER_PRD.md`, the agreed scope and approval record.
- `docs/product/specification.md` and `docs/product/schema.md`, the authoritative behavior and target schema.
- `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md`, source D-1 - D-22.
- `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md`, mapping inputs subject to specification precedence.
- `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md`, network consumption and current-copy detection.
- `plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, revision ownership and prerequisites.
- `agent_docs/memory/_cross_cutting.md`, existing shared decisions read before this plan.
- `https://docs.osmcode.org/pyosmium/latest/user_manual/03-Working-with-Geometries/`, the primary reader reference inspected in this phase.
