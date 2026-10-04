# Common demo-loading contract

Document state: 2026-10-04, contract in progress; approved decisions recorded, common result proposal awaiting the user and provider integration contracts still open

## Status and ownership

This document records the decisions approved in `plans/osm_import/OSM_IMPORT_PLAN.md` D-6 - D-17. It is a planning handoff, not evidence of a working command or completed integration. The proposed result contract below remains a proposal until approved.

For continuation of the initiative, read [OSM_IMPORT_HANDOFF.md](../../plans/osm_import/OSM_IMPORT_HANDOFF.md). It identifies approved decisions, the pending result proposal, dependency gaps and the checks already performed.

`osm_import` owns the common program and the current-copy read. Mateusz retains the importer, routing-data preparation and pointer publication under `osm_importer`, and the sample provider under `sample_data`. Adrian supplies the tile provider through `map_tiles`. Shared configuration, engines, logging, session handling and exclusion remain with their existing initiatives. This handoff changes no hosted environment and supplies no host, credential or provider implementation.

## Approved execution and exclusion

The full loading and manual full-flow retry command is `python -m worker.load_demo`. The standalone OpenStreetMap refresh remains `python -m worker.osm_import`.

Run OpenStreetMap, tiles and samples in that order. Stop on the first unsuccessful required step and mark later steps as not started. Preserve earlier committed effects. A manually triggered retry repeats every step through its provider's repeat-safe operation; it does not resume selectively or reset community contributions.

Full loading and standalone imports mutually exclude each other. A competing invocation refuses admission immediately and starts no provider work. The caller acquires exclusion through the shared `apply_import_exclusion`, passes its live `ImportLease` explicitly to importer service and retains ownership of that lease. The loader holds it through tiles and samples; importer service validates the supplied lease without reacquiring or closing it. Exact validation and abnormal-loss rules remain open with the shared foundation.

## Approved execution budgets

Each provider has its own finite whole-step execution budget. There is no additional deadline shared by the entire loader. OpenStreetMap retains its 60-minute whole-import deadline and its existing nested publication and network limits. Tile and sample whole-step values and enforcement still require their provider contracts; a statement or inactivity limit alone does not settle them.

Budget expiration stops later steps, preserves actual effects and does not prove that outstanding work stopped or rolled back. Exclusion release requires the completion evidence established by the shared contract. A caller-side timer is not provider cancellation evidence.

## Approved outcomes and terminal output

Return 0 only when all three required steps have established complete loading. Return 1 for every incomplete attempt, including an ordinary error, refused admission or uncertain commit. The summary distinguishes these conditions even though they share an exit status.

Print one English plain-text summary on stdout with the overall outcome and all three ordered step outcomes. Include safe reason codes, confirmed or uncertain effects and available sample aggregate counts. Do not expose paths, exception text, connection values or contributor records. Diagnostic logs continue through the shared central logger.

After an acknowledged OpenStreetMap commit and successful matching routing-pointer publication followed by a tile failure, the summary can read:

```text
Loading: incomplete
OSM: complete; database committed; routing pointer published
Tiles: failed
Samples: not started
```

The failed step also reports its supplied safe reason code. This example does not define an as-yet-unagreed tile reason. A pointer failure instead retains the committed database effect and reports incomplete OpenStreetMap work. An uncertain commit remains unknown. Loading does not establish that Valhalla restarted or serves the prepared copy.

## Approved current-copy read

The shared selector is `data.osm_copy.fetch_current_osm_copy(connection: Connection) -> OffsetInstant | None`, using SQLAlchemy's connection and `accessibility_db.tables.OffsetInstant`. The caller owns the connection and transaction. Select the source instant and original offset from the row with greatest `state_at`. No row returns None; database failure propagates. The selector opens no engine and commits nothing.

The service is `service.osm_copy.fetch_osm_copy_date() -> date | None`. It builds an engine through `data.engine.build_engine(5000)`, owns a short read-only transaction, calls the selector and releases its connection and invocation-owned engine on every path. Convert the instant through the product-rule constant `OSM_COPY_DISPLAY_ZONE = ZoneInfo("Europe/Warsaw")`. Machine and configurable write-time zones do not change this presentation rule.

`GET /api/osm-copy` keeps its existing optional-token contract. An invalid supplied token is refused and a valid token is renewed through the accounts-owned adapter; no-token reads remain public. The shared adapter and router-registration binding still need their concrete handoff.

## Approved sample-provider handoff

Consume `service.sample_data.apply_sample_data() -> SampleDataResult` and the records in `common_sample_data.py` under `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`. The synchronous provider owns its transaction and returns created or unchanged only after acknowledged commit. Both outcomes complete the sample effect.

Retain `created_count`, `unchanged_count`, `initial_votes_created_count` and `fact_ids` in the typed result; print only the approved aggregate counts. A named failure preserves its safe reason and commit state. An unknown commit remains unknown, and an unexpected exception establishes neither success nor confirmed rollback. A sample failure never implies rollback of earlier OpenStreetMap or tile effects.

## Proposed common result contract

The following service interface and records are a proposal for user approval under plan Q-3. They settle the common representation without claiming finalized importer or tile callables.

Proposed entry point: `service.demo_loading.apply_demo_load() -> DemoLoadResult`. Service binds the three fixed providers and owns shared admission. Worker consumes the returned record to build the terminal summary and select the approved exit status.

Define frozen records and enums in `service/demo_loading_records.py`:

| Record | Field | Type | Meaning |
| --- | --- | --- | --- |
| `DemoLoadResult` | `outcome` | `DemoLoadOutcome` | complete or incomplete |
| `DemoLoadResult` | `reason` | Nullable `str` | A supplied safe overall reason code, never exception text |
| `DemoLoadResult` | `steps` | Ordered tuple of three `DemoLoadStepResult` values | Exactly osm, tiles and samples, including unstarted steps |
| `DemoLoadStepResult` | `step` | `DemoLoadStep` | Fixed provider identifier |
| `DemoLoadStepResult` | `outcome` | `DemoLoadStepOutcome` | complete, failed, unknown or not_started |
| `DemoLoadStepResult` | `reason` | Nullable `str` | A supplied safe provider or integration reason code |
| `DemoLoadStepResult` | `effects` | Tuple of `DemoLoadEffectResult` values | Separate required resource effects |
| `DemoLoadStepResult` | `sample_result` | Nullable `SampleDataResult` | Successful sample metadata, only for the sample step |
| `DemoLoadEffectResult` | `effect` | `DemoLoadEffect` | Fixed required resource identifier |
| `DemoLoadEffectResult` | `outcome` | `DemoLoadEffectOutcome` | complete, unchanged, failed, unknown or not_started |
| `DemoLoadEffectResult` | `commit_state` | Nullable `DemoLoadCommitState` | Database-commit evidence; absent for filesystem-only effects |

The enum domains are fixed:

- `DemoLoadOutcome`: `complete`, `incomplete`.
- `DemoLoadStep`: `osm`, `tiles`, `samples`.
- `DemoLoadStepOutcome`: `complete`, `failed`, `unknown`, `not_started`.
- `DemoLoadEffect`: `osm_database`, `osm_routing_data`, `osm_routing_pointer`, `tile_archive`, `sample_dataset`.
- `DemoLoadEffectOutcome`: `complete`, `unchanged`, `failed`, `unknown`, `not_started`.
- `DemoLoadCommitState`: `not_attempted`, `committed`, `rolled_back`, `unknown`.

The osm step has three effects, tiles one and samples one. Unstarted steps retain their expected effects marked `not_started`. A confirmed existing effect can be unchanged while the step is complete. A database copy committed before pointer failure retains committed evidence; failed filesystem publication does not change that evidence. An uncertain required effect prevents complete loading and remains visible as unknown. Database rollback is reported only when acknowledged.

Successful sample metadata is retained under `sample_result`; the terminal renderer prints its aggregate counts without fact identifiers. A sample failure retains its provider-supplied commit state on the `sample_dataset` effect. A successful read-only unchanged sample invocation still has an acknowledged provider commit, even though it inserts no new examples.

Reason values must come from fixed integration codes or agreed provider allowlists. The root integration codes proposed here are `already_running`, `configuration_failed`, `lease_lost`, `step_failed`, `commit_unknown`, `integration_missing` and `unexpected_failure`. The provider allowlists and exact outcome mappings remain open with their handoffs. A supplied reason never establishes a successful effect or a proven rollback by itself.

## Remaining integration requirements

- Approve or revise the proposed common entry point and result records.
- Finalize the importer service signature, live-lease validation, effect mapping and manual retry after a committed copy with failed pointer publication. Importer planning stays with Mateusz.
- Finalize the tile callable, outcome and failure records, repeat safety and execution budget with Adrian.
- Supplement the sample provider with its finite whole-step budget and safe enforcement under the approved independent-budget rule.
- Finalize shared lease-loss and completion behavior across provider work, including filesystem and sample effects outside importer publication.
- Finalize the optional-session adapter, router registration, local critical fixtures and actual test commands with their existing owners.

These requirements keep the plan and this handoff in progress. They are not successful placeholder integrations and do not authorize implementation of another initiative.
