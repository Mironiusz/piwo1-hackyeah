# OpenStreetMap read and common loading handoff

Document state: 2026-10-04, continuation handoff prepared at the user's request; technical plan remains in progress

## Purpose and current state

This handoff lets the next person or session continue `osm_import` without repeating the completed interview or treating a proposed contract as approved. The user requested a handoff after reviewing the proposed common result model. That request did not approve the model or change initiative ownership.

`OSM_IMPORT_SHAPE.md` is closed at C:40. `OSM_IMPORT_PRD.md` is approved. `OSM_IMPORT_PLAN.md` remains marked `plan in progress`, with blocking Q-3, Q-4 and Q-5. No implementation or end-to-end loading verification has been completed by this work. The initiative remains in `plans/osm_import`.

The immediate pending decision is plan D-18: approve or revise `service.demo_loading.apply_demo_load() -> DemoLoadResult` and the frozen records described in the loading contract. Do not infer approval from the earlier answers A: the last such answer approved plain-text terminal output in D-17.

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

Adrian supplies the tile-loading step through `map_tiles`. Mateusz supplies samples through `sample_data`. Shared engine, configuration, logging, administrative and exclusion contracts belong to `backend_skeleton`; optional-session validation and renewal belong to accounts. Provider integrations require their actual contracts, not inferred signatures or successful placeholders.

## Decisions already settled

| Area | Settled behavior | Plan reference |
| --- | --- | --- |
| Commands | `python -m worker.load_demo` performs full loading or full retry; `python -m worker.osm_import` remains the standalone refresh. | D-6 |
| Order and failure | OpenStreetMap, tiles, samples. Stop at the first unsuccessful step; later steps are not started. Previously committed effects remain. | D-7 |
| Recovery | Manual recovery repeats the full flow. Providers must preserve contributions and avoid duplicate imported or sample data. No automatic retry or selective resume was chosen. | D-5 and PRD FR-6 |
| Exit status | 0 only for complete loading; 1 for every incomplete result, including busy admission and uncertain commit. The summary distinguishes the causes. | D-8 |
| Exclusion | Full runs and standalone imports mutually exclude each other, including while the loader is processing tiles or samples. A competing run refuses immediately and starts no provider steps. | D-10 and D-11 |
| Lease ownership | The caller acquires exclusion and explicitly passes its live `ImportLease` to importer service. Importer validates it without reacquiring or closing it. The loader retains it through all steps. | D-14 |
| Budgets | Each provider has its own finite execution budget; the loader adds no shared elapsed deadline. Importer retains its 60-minute budget and nested limits. Tile/sample values and enforcement remain open. | D-13 |
| Terminal output | One English plain-text summary on stdout with all three steps, retained effects, safe reasons, available sample counts and explicit uncertainty. There is no JSON output contract. | D-17 |
| Samples | `apply_sample_data()` returns created or unchanged after acknowledged commit; both complete the effect. Preserve counts, identifiers, failure reason and commit state. | D-12 and sample handoff |
| Freshness | Read the greatest source-state instant, preserve its offset pair and display its Warsaw calendar day. No-copy is null; database failure is an error. | D-2, D-3, D-15 and D-16 |

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

Approval of this proposal would settle the common representation, not the missing importer/tile callables, their outcome mappings, lease-loss handling or provider deadlines. Record the answer in plan D-18 and update the proposal state in the loading contract before implementation.

## Blocking integration work

| Question | Required resolution | Relevant source |
| --- | --- | --- |
| Q-3 | Approve or revise D-18; coordinate the shared selector file; finalize importer signature, validated lease input, result/effect mapping and recovery after committed copy with failed pointer; bind the administrative wrapper and tile interface. | Plan Open questions; importer plan Q-1; loading contract |
| Q-4 | Finalize router registration and accounts-owned optional-session adapter; consume the supplied critical-fixture contract and finish missing local-owner/backend inputs; record actual runtime commands and verify the local schema before test writes. | Backend/accounts plans; sample backend handoff; `db/README.md` |
| Q-5 | Finalize shared lease validation, completion and abnormal-loss behavior across all providers; supply finite tile/sample whole-step budgets and safe enforcement; confirm tile repeat safety. | Backend plan Q-2; plan D-13 and D-14; provider handoffs |

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

1. Read this handoff and the linked plan and loading contract; retain the approved SHAPE and PRD.
2. Recheck the working tree and current provider/backend handoffs. Incorporate newly delivered contracts instead of inventing replacements.
3. Resume technical planning at D-18 and Q-3 - Q-5. Ask about the pending proposal and genuine contract gaps, one decision at a time; do not repeat settled choices.
4. Finalize the common loading contract and concrete call signatures, mappings, deadlines, fixture inputs and verification commands. Keep provider implementation with its existing initiatives.
5. Mark the plan closed only after Open questions is empty and every implementation step has concrete inputs and outputs. Then follow the repository's authorized transition to implementation and final review.

The initiative stays active until its full scope is implemented and reviewed. This requested handoff is not a completion or cancellation verdict.
