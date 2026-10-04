# Shape: Backend skeleton and local database of the MVP

Document state: 2026-10-04, interview closed
Regulator: C:40

## Problem

The MVP has agreed backend technology, architecture and a programming interface contract, but this working tree has no backend implementation. Mateusz cannot integrate the OpenStreetMap importer with shared infrastructure, and Kuba cannot deliver the first schema revision without the local setup and revision runner.

On 2026-10-04 the user selected backend skeleton work after discussing parallel work alongside another Codex session developing `osm_importer`, and requested an initiative for it. The English translation of the activation request is: "Then we are doing backend skeleton. Let's create a new initiative for it."

The existing `plans/backend_skeleton/` initiative already has the same scope and its immutable seed. This shape starts work on that initiative under its existing name and task prefix; it does not replace the seed or create a second builder for the same MVP responsibility. Agent decision at C:40, without asking: the user selected the initiative proposed in this conversation, and `MVP.md`, section Initiatives, already assigns that scope to it.

## Recipient and trigger

- Marek receives a runnable foundation for the backend operations implemented by later initiatives.
- Mateusz receives shared infrastructure for integrating the importer and address search.
- Kuba receives a local database setup and a configured revision runner for the first schema revision.
- The deployment configuration initiative receives the backend launch contract it needs to assemble the demo services.

The trigger is a team member preparing local development, launching the backend, preparing a schema revision or integrating an administrative operation. This initiative is not an end-user feature.

## Current state

- `MVP.md`, D-1, chooses Python 3.13 with FastAPI on PostgreSQL with PostGIS and keeps the Python profile of the standards.
- `MVP.md`, D-7 and D-14, carries the local database and backend architecture decisions. `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` and `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` contain their detailed contracts.
- This checkout has no backend layer directories, shared configuration implementation or Alembic setup. The runtime dependency list in `pyproject.toml` is empty, checked on 2026-10-04.
- `plans/backend_skeleton/` contains its seed and has no archived counterpart. The seed assigns the foundation and the local setup to this initiative, without any product operation.
- `MVP.md`, section Order and critical path, places skeleton first. The first schema revision, address search and deployment configuration consume its results.
- Another Codex session is editing `plans/osm_importer/`. The existing modifications to its artifacts and `docs/standards/decision_registry.md` belong to that session.
- The importer requests shared connection/session handling, logging, a clock, import exclusion and deadline enforcement, and a shared vote evaluator (`plans/osm_importer/OSM_IMPORTER_PLAN.md`, Q-1). On 2026-10-04 the user assigned shared import exclusion and whole-publication deadline enforcement to skeleton in response to Q-1 of this shape. The vote evaluator remains outside skeleton.
- During this interview the other session updated `MVP.md`, D-14, to use `python -m worker.osm_import` locally and in a one-off backend container, following importer D-14 and D-20. Importer D-20 assigns the network PBF, Valhalla walking-data build and post-commit pointer publication to `osm_importer`; D-21 keeps the copy-read operation and common demo loader in `osm_import`. These current handoffs supersede the earlier scope and launch discrepancies; the exact infrastructure interfaces remain work for phase B.

## Smallest meaningful scope

A team member can prepare the documented local environment, start the backend, use the shared infrastructure and hand a configured schema-change runner to Kuba. Later initiatives can add operations using the agreed layer boundaries rather than inventing their own configuration, logger or database connection mechanism.

The baseline scope is the existing seed and `MVP.md`, section Initiatives: backend layer structure and launch foundations, shared configuration and logging, database access, local database setup, revision-runner configuration, applicable gates and critical checks independent of the first schema revision.

On 2026-10-04 the user extended this scope to shared exclusion of concurrent import runs and enforcement of the entire publication deadline, including interruption and rollback of an uncommitted transaction. This resolves Q-1. Marek delivers these shared mechanisms through skeleton; the importer consumes them and still owns its acquisition, preparation and publication orchestration.

## Out of scope

- The first schema revision and checks that require its objects or grants. Their builder is `schema_first_revision`; keeping them there prevents a dependency cycle (`MVP.md`, section Order and critical path).
- Product operations for accounts, reports, votes, moderation, address search, copy metadata and route planning. Their builders are the initiatives named in `MVP.md`.
- Downloading or parsing OpenStreetMap, mapping tags, reconciling imported facts and preparing routing data. Their import ownership is being settled in the other session.
- The shared vote-status evaluator and vote-writing behavior, including fact locking before a vote, remain with the community-facts backend work under the current MVP allocation. No duplication belongs in skeleton.
- Hosted deployment, hosted data loading or access to the hosted database. Deployment configuration remains its own initiative, and this request authorizes no hosted action.
- A periodic worker or scheduled import. `MVP.md`, D-14, explicitly specifies no periodic task.

## Functional requirements

1. Provide the agreed backend layer structure and a runnable application foundation that later initiatives can extend.
2. Provide one shared configuration and validation mechanism and one logging mechanism usable by request handling and administrative runs.
3. Provide one shared database connection mechanism with the agreed service-account boundary and UTC session setting.
4. Provide the documented local database setup and configure the schema-change runner without applying a product revision at application startup.
5. Prepare the administrative launch foundation under the current `MVP.md`, D-14, contract, without implementing the import itself.
6. Set up the checks required with the first backend code, including architecture boundaries and local critical-test protection, and verify the local setup independently of the first schema revision.
7. Document the delivered readiness and verification commands so Kuba and Mateusz can consume concrete results. Record the chosen backend in the standards map and resolve the technology-profile deferral when its implementation condition is met.
8. Deliver shared exclusion of concurrent import runs, with zero wait for a second run and ownership retained until outstanding work, rollback and cleanup have ended, including private-file cleanup after loss of all database connections. The user confirmed this abnormal-loss boundary on 2026-10-04.
9. Deliver enforcement of one deadline for the whole publication transaction, including lock waiting, all statements and commit. On expiration stop further publication and roll back an uncommitted transaction; do not report an uncertain commit as a proven rollback.

Requirements 1 - 7 follow from the existing seed, `MVP.md`, D-1, D-7 and D-14, and the local database plan, D-8. They do not reopen those choices. Requirements 8 and 9 follow from the user's answer to Q-1 on 2026-10-04; their consumer behavior follows importer D-16 and D-17 and the source plan D-11.

## Scenarios: input, flow, expected state after the run

1. Local preparation. Input: a clean checkout and the team member's local configuration. Flow: follow the documented setup. Expected state: the local database is available and the schema-change runner is configured; no product schema revision or import is applied by application startup.
2. Application startup. Input: the prepared runtime and valid configuration, before product data exists. Flow: start the backend. Expected state: the application foundation runs without requiring a delivered importer or route graph. Product-specific startup behavior is added by its owner when that operation exists.
3. Shared database use. Input: the local service account and the delivered connection mechanism. Flow: a consumer opens a connection. Expected state: the connection uses the configured local database and the agreed session zone; it does not acquire schema-owner privileges.
4. Revision handoff. Input: the delivered local setup and revision-runner configuration. Flow: Kuba adds the first revision in its own initiative. Expected state: he does not need to create another backend configuration mechanism, and skeleton completion does not wait for his revision.
5. Import integration. Input: the infrastructure skeleton delivers and an agreed administrative launch contract. Flow: Mateusz connects his modules through shared infrastructure. Expected state: the importer reuses the delivered mechanisms; publication remains unavailable until the revision and other shared prerequisites are actually delivered.
6. Critical-test protection. Input: a critical test invocation under target-environment configuration. Flow: initialize the test session. Expected state: the session refuses to run before a test can write. Local critical tests verify only the checks assigned to skeleton.
7. Concurrent import launch. Input: run A already owns import exclusion. Flow: run B tries to acquire it. Expected state: B is refused without waiting or starting acquisition, while A retains exclusion until its outstanding work and cleanup end.
8. Whole-publication deadline. Input: a 120-second budget beginning at transaction start. Flow: the transaction waits for a lock until second 80, then needs another 50 seconds of work. Expected state: publication is interrupted at its deadline rather than allowed a new 120 seconds per statement; an uncommitted transaction rolls back and preserves the previous database copy. If less whole-run time remains, the earlier deadline applies, as importer D-16 requires.
9. Expiration and cleanup. Input: the deadline expires while publication work is outstanding. Flow: stop further work, finish rollback and cleanup, then release exclusion. Expected state: no second import starts while the expired run can still mutate data. A commit with an uncertain outcome is reported distinctly and is not declared rolled back.

## Challenging own assumptions

- Does the user need another initiative directory? The same scope already has a seed and an MVP owner. Continuing that initiative preserves its history and avoids two builders for one foundation.
- Does skeleton completion mean the importer can publish data? No. The actual revision, vote evaluator, concurrency protocol and routing-data handoff remain separate prerequisites.
- Should skeleton implement empty product endpoints or a substitute vote evaluator to make integration appear ready? No. The seed expressly assigns no product operation, and a missing contract is not permission to invent one.
- Must skeleton wait for the first revision to prove its local setup? No. Checks that require that revision belong to Kuba's initiative; the skeleton checks the foundation independently.
- Are all importer requests automatically skeleton responsibilities? No. The user explicitly assigned shared exclusion and deadline enforcement to skeleton in this interview. That answer does not assign the vote evaluator, importer orchestration or routing-data preparation to it.

## Domain rules or explicit TODO

- `docs/product/specification.md` and its target schema remain the product authority. Skeleton changes no accessibility, account or vote rule.
- `docs/product/api_contract.md` remains the external API contract. Foundation behavior must not invent alternative error responses or product operations.
- Startup never applies schema revisions or loads data. Administrative operations remain explicit.
- Import publication has a user-decided 120-second total transaction budget, including lock waiting, as recorded in importer D-16. Skeleton now owns shared enforcement. The effective deadline is the earlier of that budget and the remaining whole-run time. This scope decision does not claim implementation is already delivered.
- The shared mechanisms are infrastructure, not permission to add schema objects, a second importer or vote rules. Technical interfaces, cancellation behavior, commit-outcome reporting and local verification commands must be settled and verified in phase B before implementation.

## Notes on data, performance and security

- Local development and critical tests use a team member's own local database. No target address, login or secret enters artifacts.
- Logs follow the existing privacy contract and do not record request bodies, route coordinates, search text, passwords or tokens.
- A statement timeout and a deadline for an entire publication transaction have different effects. The shared enforcement now in scope must include waiting and all statements through commit, with exclusion retained until outstanding work has ended.
- Actual schema objects and permissions are verified only after the responsible revision is delivered. A target-schema document does not prove applied database state.
- Parallel work stays in separate files: this session prepares `plans/backend_skeleton/`; the other session owns its current importer and registry edits. Shared implementation file ownership is finalized in the plan.
- Dependency pins, specific infrastructure interfaces and executable commands are verified in phase B rather than guessed in this shape.

## Open questions

None at the shape stage. Q-1 was answered by the user on 2026-10-04, assigning shared import exclusion and deadline enforcement to skeleton. Q-2 was answered from the updated `MVP.md`, D-14, and importer D-14 and D-20: the administrative entry point is `python -m worker.osm_import` in both agreed environments. Phase B still has to finalize and verify the technical handoff; closing this interview proves scope agreement, not importer readiness.

## 2026-10-04 - Abnormal-loss cleanup boundary confirmed

The user required a new importer to wait until the old run has finished cleaning its files even if all database lock sessions are lost. This confirms requirement 8 without accepting an abnormal-loss exception. Database completion alone is insufficient. Technical-plan Q-3 asks how cleanup and admission recovery are completed when the old process crashes; no recovery policy has been inferred from this answer.

## 2026-10-04 - Automatic crash cleanup requested

The user selected automatic cleanup and admission release after a process crash. No human cleanup or manual unlock is required for the intended recovery. The trigger remains open in technical-plan Q-4: recovery during the next manual launch, or independently without another launch. This answer does not authorize automatic fresh imports or identify a storage mechanism.

## 2026-10-04 - Recovery trigger selected

The user selected automatic cleanup during the next manually launched import, before it acquires new source data. If no new launch occurs, cleanup remains pending. No independent background recovery service or automatic fresh import is required. Q-4 is resolved; technical-plan Q-5 asks whether all runs for one database share one execution machine and a persistent workspace accessible across replacement containers.

## 2026-10-04 - One execution machine and persistent workspace agreed

The user confirmed one execution machine and one shared persistent workspace for all imports into a given database, including across replacement containers. Hosted imports use the demo server; development imports use the local machine and local database. Q-5 is answered. No hosted operation, product-schema lease or separate background service is authorized. Technical-plan closure still requires a concrete exclusion and recovery protocol satisfying the agreed boundaries.
