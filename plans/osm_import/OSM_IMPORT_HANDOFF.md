# OpenStreetMap read and common loading handoff

Document state: 2026-10-04, continuation handoff updated after the second planning session; `plans/tile_loading/` delivered the tile step on 2026-10-04, which ends the hold of plan D-21; technical plan remains in progress

## Purpose and current state

This handoff lets the next person or session continue `osm_import` without repeating the completed interview or treating a proposed contract as approved. The user requested a handoff after reviewing the proposed common result model. That request did not approve the model or change initiative ownership.

`OSM_IMPORT_SHAPE.md` is closed at C:40. `OSM_IMPORT_PRD.md` is approved. `OSM_IMPORT_PLAN.md` remains marked `plan in progress`, with blocking Q-3, Q-4 and Q-5. No implementation or end-to-end loading verification has been completed by this work. The initiative remains in `plans/osm_import`.

The immediate pending decision is plan D-18: approve or revise `service.demo_loading.apply_demo_load() -> DemoLoadResult` and the frozen records described in the loading contract. Do not infer approval from the earlier answers A: the last such answer approved plain-text terminal output in D-17.

## Continuation state of 2026-10-04

A second session resumed phase B on 2026-10-04 after the user asked to complete this initiative in full and then archive it. It verified the delivered contracts below, coordinated with the parallel `sample_data` and `community_facts` sessions and stopped at the user's request before settling D-18 or Q-3 - Q-5. No code was written. The sections after this one describe the state of the first session and stay as written; where they disagree with this section, this section reflects the later check.

### User decisions of the second session

- Full completion of this initiative, then archiving it under ch. 4.6 of `docs/standards/standard_agentic_workflow.md`.
- Plan D-20: GTFS stays out of `python -m worker.load_demo`; its integration becomes a new initiative created after this one is archived.
- Plan D-21: the tile step goes to `plans/tile_loading/`, whose seed records the request; this initiative is held until that initiative settles how the tile requirements of PRD FR-3, FR-4, AC-4 and AC-6 are met.

### Delivered contracts verified in the code

- Importer: `service/osm_import.py` `apply_osm_import_run(settings: OsmImportSettings, client: httpx.AsyncClient, lease: ImportLease, run_deadline: Deadline) -> OsmImportResult` is async and accepts a caller's live lease without acquiring exclusion itself, which is the handoff of plan D-14. The HTTP client is `data/osm_source.py` `build_osm_http_client() -> httpx.AsyncClient`; the run budget is `OSM_IMPORT_RUN_SECONDS = 3600` with `common_time.py` `build_deadline`. `OsmImportOutcome` is `updated`, `unchanged`, `skipped`, `routing_incomplete` or `commit_unknown`; `skipped` comes only from `apply_osm_import`, which acquires its own lease. A hard failure is an exception from `OSM_IMPORT_NAMED_ERRORS`, not an outcome value.
- Recovery after a committed copy with a failed routing pointer: `service/osm_routing_recovery.py` `apply_osm_routing_recovery` runs at the start of every run, before the source comparison. A retry with an unchanged source republishes the pointer from the verified committed copy and returns `unchanged`; missing or inconsistent files raise `OsmRoutingIntegrityError`. Risk R-2 of the plan is settled by the delivered importer (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-22 and D-23).
- Settings: `worker/osm_import.py` `build_osm_import_settings() -> OsmImportSettings` reads `IMPORT_WORKSPACE_ROOT`, `ROUTING_DATA_DIR`, `VALHALLA_TOOL_DIR`, `VALHALLA_CONFIG_TEMPLATE` and `BUSINESS_TIMEZONE`. Service must not import worker (`tests/architecture/test_layer_boundaries.py` `FORBIDDEN`), while worker may import worker, as `worker/gtfs_import.py` does; the common service entry point therefore needs the settings as an argument, which D-18 does not yet show.
- Exclusion: `data/locks.py` `apply_import_exclusion(engine: Engine, workspace_root: Path) -> Iterator[ImportLease]` takes the local `admission.lock` of the workspace and two PostgreSQL advisory keys without waiting and raises `ImportAlreadyRunning` when busy; `ImportLease.apply_lease_validation(connection)` raises `ImportLeaseLost`; leaving the context can raise `ImportWorkspaceUnconfirmed`. Both `apply_osm_import` and `service/gtfs_import.py` `apply_gtfs_import` acquire the same exclusion and return `skipped` when busy, so a loader holding the lease across all its steps refuses both standalone commands, as D-10 and D-11 require.
- Samples: `service/sample_data.py` `apply_sample_data() -> SampleDataResult` is synchronous and owns its transaction; records and `SampleDataError` (alias `SampleDataFailure`) with `SampleFailureReason` and `SampleCommitState` are in `common_sample_data.py`. The provider has no whole-step timer: its statements are limited by `build_engine(5000)`, connect and pool waits by 5 s each, and the number of statements is fixed. Later the same day the provider changed: when the process holds no graph of the current copy it builds one inside its transaction under `service/route_graph.py` `GRAPH_BUILD_STATEMENT_TIMEOUT_MS = 60000`, the reason `SURFACE_NOT_ABSENT` became `CONTRADICTION_MISSING`, and the dataset grew to eight facts and twenty-five sample votes; the callable, record fields, the other reasons and the commit states kept their names (`plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`).
- Tiles: `plans/tile_loading/` delivered `service/tile_archive.py` `apply_tile_archive_run(settings, deadline) -> TileArchiveResult` and the command `python -m worker.tile_archive`; the contract is in `docs/deployment/loading_program.md`, section Tile-provider handoff. The repository still has no proxy configuration that serves the archive.
- Copy-date read: `data/osm_copy.py` `fetch_current_osm_copy(connection: Connection) -> OsmCopySnapshot | None` exists, delivered with the importer and used by route planning; it orders by `state_at` descending with a limit of one and returns `OsmCopySnapshot(id, state_at: OffsetInstant, file_name)`, not the bare `OffsetInstant` of plan D-15. `data/engine.py` provides the cached pooled `fetch_api_engine()` and `fetch_read_only_snapshot(engine)`, the pattern of `service/route_planning.py` `resolve_route`, which makes the per-invocation engine of D-16 unnecessary. `common_time.py` `build_business_day(instant)` converts to the configured `BUSINESS_TIMEZONE`, and route planning already uses it for `osm_copy_date`; plan D-3 instead fixes a constant Europe/Warsaw zone, so the two operations could show different days for one copy if the setting differed.
- API: `GET /api/osm-copy` is not registered, although `frontend/src/shell/Menu.tsx` calls `readOsmCopy`. The optional-token seam is `api/sessions.py` `fetch_request_session(request: Request) -> SessionResolution`; `SessionTokenMiddleware` and `apply_session_error_handlers` are installed application-wide from `api/accounts.py` `apply_account_routes`, so a new route needs only `Depends(fetch_request_session)`. `community_facts` plans the same use without moving that registration.
- Environment: `venv/Scripts/python.exe` is Python 3.13 with fastapi, SQLAlchemy, psycopg, pytest, httpx and `accessibility_db`. No `.env` or `.env.local` exists, so the local-only guard of `tests/conftest.py` stops critical tests until a local configuration is supplied.

### Questions still to put to the user

- D-18, revised with a settings argument and with the tile step depending on `tile_loading`.
- D-15 and D-16 against the delivered selector and API engine above.
- D-3 against `build_business_day` and `BUSINESS_TIMEZONE`, for one rule across `read_osm_copy` and `plan_route`.
- The outcome mapping from `OsmImportOutcome`, `OSM_IMPORT_NAMED_ERRORS` and `SampleDataError` to the common records.
- The sample budget: the `sample_data` session agreed to describe it as finite by construction, with the wording that every stage is bounded and a lost commit acknowledgement stays `commit_unknown`, never as a hard wall-clock limit. The bound now includes the 60 s graph-build statement.

### Coordination with parallel sessions

- `sample_data` may change the sample set from four facts to eight under `stage7_demo_scenario`; the callable, record names, enums and reason codes stay, only the counts and identifiers change. Later the same day that session reported that the user chose the `stage7_demo_scenario` dataset and that the `sample_data` shape is reopened, with a new PRD and plan to follow; it plans to keep the provider names and to announce any change before making it. Re-read `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md` before relying on the provider contract. The adapter must treat `created_count`, `unchanged_count`, `initial_votes_created_count` and `fact_ids` as opaque values for the report. That session defines `schema_owner_engine` in `tests/data/conftest.py` and edits only its own sample sections of `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md`, after this initiative signals it has finished those files.
- `community_facts` touches no code of `api/`; it shares only `MVP.md` and `FINAL_CHECKLIST.md`, in other rows. Both sides edit those files with targeted edits after a fresh read.

## Read first

1. [OSM_IMPORT_PLAN.md](OSM_IMPORT_PLAN.md), especially Decisions, Open questions and Scope of changes.
2. [loading_program.md](../../docs/deployment/loading_program.md), especially Proposed common result contract and Remaining integration requirements.
3. [OSM_IMPORT_PRD.md](OSM_IMPORT_PRD.md), the approved requirements and acceptance criteria.
4. [specification.md](../../docs/product/specification.md), M6 and M10; [api_contract.md](../../docs/product/api_contract.md), OpenStreetMap copy and Sessions and actors; [schema.md](../../docs/product/schema.md), OpenStreetMap copy.
5. [SAMPLE_DATA_LOADING_HANDOFF.md](../sample_data/SAMPLE_DATA_LOADING_HANDOFF.md) and [SAMPLE_DATA_BACKEND_HANDOFF.md](../sample_data/SAMPLE_DATA_BACKEND_HANDOFF.md), the provider and critical-fixture contracts supplied during parallel work.

The specification prevails over this handoff and all other initiative artifacts. Use the standards map and deferred-decision registry when resuming. The detailed result-field table has one location, in the loading contract; this handoff does not replace it.

## Scope and ownership

`osm_import` delivers `GET /api/osm-copy` and the common manual loading program. It consumes the importer, tile and sample services.

Mateusz retains `osm_importer`: source acquisition, mapping, reconciliation, database publication, network PBF and Valhalla walking-data preparation, routing-pointer publication, their tests and remaining planning. Its plan D-22 explicitly retains this handoff of ownership. This work has not changed that initiative.

Rafał supplies the tile-loading step through `tile_loading`. Mateusz supplies samples through `sample_data`. Shared engine, configuration, logging, administrative and exclusion contracts belong to `backend_skeleton`; optional-session validation and renewal belong to accounts. Provider integrations require their actual contracts, not inferred signatures or successful placeholders.

## Decisions already settled

| Area              | Settled behavior                                                                                                                                                                                                                                   | Plan reference          |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Commands          | `python -m worker.load_demo` performs full loading or full retry; `python -m worker.osm_import` remains the standalone refresh.                                                                                                                    | D-6                     |
| Order and failure | OpenStreetMap, tiles, samples. Stop at the first unsuccessful step; later steps are not started. Previously committed effects remain.                                                                                                              | D-7                     |
| Recovery          | Manual recovery repeats the full flow. Providers must preserve contributions and avoid duplicate imported or sample data. No automatic retry or selective resume was chosen.                                                                       | D-5 and PRD FR-6        |
| Exit status       | 0 only for complete loading; 1 for every incomplete result, including busy admission and uncertain commit. The summary distinguishes the causes.                                                                                                   | D-8                     |
| Exclusion         | Full runs and standalone imports mutually exclude each other, including while the loader is processing tiles or samples. A competing run refuses immediately and starts no provider steps.                                                         | D-10 and D-11           |
| Lease ownership   | The caller acquires exclusion and explicitly passes its live `ImportLease` to importer service. Importer validates it without reacquiring or closing it. The loader retains it through all steps.                                                  | D-14                    |
| Budgets           | Each provider has its own finite execution budget; the loader adds no shared elapsed deadline. Importer retains its 60-minute budget and nested limits. Tiles have 120 seconds under `tile_loading`; the sample value and enforcement remain open. | D-13                    |
| Terminal output   | One English plain-text summary on stdout with all three steps, retained effects, safe reasons, available sample counts and explicit uncertainty. There is no JSON output contract.                                                                 | D-17                    |
| Samples           | `apply_sample_data()` returns created or unchanged after acknowledged commit; both complete the effect. Preserve counts, identifiers, failure reason and commit state.                                                                             | D-12 and sample handoff |
| Freshness         | Read the greatest source-state instant, preserve its offset pair and display its Warsaw calendar day. No-copy is null; database failure is an error.                                                                                               | D-2, D-3, D-15 and D-16 |

The two approved freshness signatures are:

```python
data.osm_copy.fetch_current_osm_copy(connection: Connection) -> OffsetInstant | None
service.osm_copy.fetch_osm_copy_date() -> date | None
```

The selector uses the existing `accessibility_db.tables.OffsetInstant`; its caller owns the transaction. It selects only the source instant and original offset, opens no engine and commits nothing. The service obtains an engine through the shared `build_engine(5000)`, performs a short read-only transaction and closes the connection and disposes its invocation-owned engine on every path.

The presentation constant is `OSM_COPY_DISPLAY_ZONE = ZoneInfo("Europe/Warsaw")`. It implements a fixed product rule independently of the machine zone and the configurable business zone used for writes. The public operation keeps its optional-token behavior: reject an invalid supplied token, renew a valid token and allow requests with no token through the shared adapter.

## Proposal still awaiting approval

Plan D-18 proposes `service.demo_loading.apply_demo_load() -> DemoLoadResult`, with records and enums in `service/demo_loading_records.py`. The loading contract's Proposed common result contract contains the exact fields, enum values and proposed integration reason codes.

The main records are `DemoLoadResult`, `DemoLoadStepResult` and `DemoLoadEffectResult`. The result contains exactly three ordered steps. Required effects are represented separately as `osm_database`, `osm_routing_data`, `osm_routing_pointer`, `tile_archive` and `sample_dataset`. Database commit evidence distinguishes `not_attempted`, `committed`, `rolled_back` and `unknown`.

This separation preserves an acknowledged database commit when routing-pointer publication fails. An uncertain required effect prevents complete loading. The sample result retains provider metadata internally; the terminal summary exposes aggregate counts without fact identifiers.

Approval of this proposal would settle the common representation, not the missing importer callable, their outcome mappings, lease-loss handling or provider deadlines. Record the answer in plan D-18 and update the proposal state in the loading contract before implementation.

## Blocking integration work

| Question | Required resolution                                                                                                                                                                                                                                             | Relevant source                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Q-3      | Approve or revise D-18; coordinate the shared selector file; finalize importer signature, validated lease input, result/effect mapping and recovery after committed copy with failed pointer; bind the administrative wrapper and the delivered tile interface. | Plan Open questions; importer plan Q-1; loading contract       |
| Q-4      | Finalize router registration and accounts-owned optional-session adapter; consume the supplied critical-fixture contract and finish missing local-owner/backend inputs; record actual runtime commands and verify the local schema before test writes.          | Backend/accounts plans; sample backend handoff; `db/README.md` |
| Q-5      | Finalize shared lease validation, completion and abnormal-loss behavior across all providers; supply the finite sample whole-step budget and safe enforcement.                                                                                                  | Backend plan Q-2; plan D-13 and D-14; provider handoffs        |

The importer has an unresolved unchanged-source recovery path: a retry after database commit but failed routing-pointer publication cannot report success merely because the source state is unchanged. Mateusz must supply the recovery behavior; the common loader preserves its reported effects.

The sample plan is closed and its handoff specifies a 5000 ms statement limit, but neither supplies a finite whole-sample execution budget. The newer common-loader decision therefore needs an explicit provider-contract supplement. A caller-side timer cannot establish cancellation, completed rollback or safe release of exclusion.

The shared fixture contract now supplies `database_cleanup_registry`, `DatabaseFixtureRegistry` and the local-only critical collection guard. Backend delivery still must provide the configured service engine, local `schema_owner_engine`, clock and logger. Preserve the existing shared fixture files; do not create parallel guards or connection factories. The contract is not evidence of an applied schema or a completed loader test.

## Work products and parallel edits

Planning produced `OSM_IMPORT_SHAPE.md`, `OSM_IMPORT_PRD.md`, `OSM_IMPORT_PLAN.md` and the draft `docs/deployment/loading_program.md`. This handoff adds `OSM_IMPORT_HANDOFF.md`. The seed and stage marker retain their existing content. There is no implementation review verdict for this initiative.

Parallel sample work has added provider code, tests, fixture infrastructure and its own handoffs, and modified `pyproject.toml` and `makefile`. These changes belong to that work and were not implemented or validated here. Recheck `git status --short` before editing shared files and preserve concurrent edits, including service/data package files and test fixtures.

This work has created no commit, staged no file, pushed nothing and performed no hosted operation. The proposed command is not evidence that `python -m worker.load_demo` already runs.

## Validation and limits

The planning work checked the plan's Facts using the existing validator from `tests/architecture/test_plan_document_contract.py`, verified the in-progress marker and checked document structure, whitespace and prose constraints. It also ran `git diff --check`. These are document checks, not runtime or database test evidence.

At the latest recorded environment probe, the default Python lacked SQLAlchemy, psycopg and pytest; Node.js, npm and psql were absent. Service/data sample code had appeared, while api, worker and config were absent. Recheck the current environment and tree before relying on that snapshot, because parallel implementation is active.

No query timing, applied local schema, provider cancellation, lease-loss behavior, runtime session handling or complete three-provider loading has been verified by this work. Per-request engine construction in D-16 also needs a local performance check once the shared factory is delivered.

## How to resume

1. `plans/tile_loading/` delivered the tile step (plan D-21); read `docs/deployment/loading_program.md`, section Tile-provider handoff. Then read this handoff, starting with Continuation state of 2026-10-04, and the linked plan and loading contract; retain the approved SHAPE and PRD.
2. Recheck the working tree and current provider/backend handoffs. Incorporate newly delivered contracts instead of inventing replacements.
3. Resume technical planning at D-18 and Q-3 - Q-5. Ask about the pending proposal and genuine contract gaps, one decision at a time; do not repeat settled choices.
4. Finalize the common loading contract and concrete call signatures, mappings, deadlines, fixture inputs and verification commands. Keep provider implementation with its existing initiatives.
5. Mark the plan closed only after Open questions is empty and every implementation step has concrete inputs and outputs. Then follow the repository's authorized transition to implementation and final review.

The initiative stays active until its full scope is implemented and reviewed. This requested handoff is not a completion or cancellation verdict.
