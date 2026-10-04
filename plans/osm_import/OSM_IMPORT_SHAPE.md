# Shape: OpenStreetMap copy read and common demo loading

Document state: 2026-10-04, interview closed
Regulator: C:40

## Problem

The demo needs one manually started program that loads its OpenStreetMap copy with matching walking-routing data, its map tile archive and its sample reports and geozones. Clients also need the date of the OpenStreetMap copy currently in use. Without those effects, the deployment cannot complete its loading step and the interface cannot explain the freshness of its open data.

The original seed included the importer itself. The ownership handoff recorded in `MVP.md`, sections How the MVP is built and Initiatives, assigns acquisition, mapping, reconciliation and walking-routing data preparation to `osm_importer`. This initiative consumes that importer and retains the copy-read operation and the common loading program. The seed remains unchanged.

## Recipient and trigger

- A client of the service requests the date of the copy in use. The operation is public with an optional session token, under the existing rules of `docs/product/api_contract.md`, sections Sessions and actors and OpenStreetMap copy.
- A member of the team starts the loading program manually after applying the schema revisions, locally or in the hosted demo environment. The service start and a restart after a fix never trigger loading (`docs/deployment/hosted_demo.md`, sections Starting the demo, Loading the data and Restarting after a fix; `MVP.md` D-14).
- Adrian adds the tile-loading step through `map_tiles`; Mateusz adds the sample-loading step through `sample_data`, following the common step contract this initiative supplies (`MVP.md`, section Initiatives).

## Current state

This initiative holds its seed and a stage marker of 3. Check 3.2 of `FINAL_CHECKLIST.md` verifies its effect after the importer of check 3.1 works; the stage does not prevent planning from starting now.

The existing programming-interface contract names `read_osm_copy`: `GET /api/osm-copy`, no request body, a successful response containing `date`, and `null` before the first copy exists. `docs/product/schema.md`, section OpenStreetMap copy, identifies the copy in use by the latest source-state instant and gives its displayed calendar day in Europe/Warsaw. The download day and the publication day are not the freshness date.

The repository currently has the `db/accessibility_db/` package and its first revision, but no root `api/`, `service/`, `data/` or `worker/` implementation. The existence of revision files does not prove that a local database has that revision applied. `backend_skeleton` owns the shared backend structure.

`plans/osm_importer/OSM_IMPORTER_PLAN.md` is still a plan in progress. Its D-14 and D-20 assign the manual import command, local and server execution, walking-data preparation and post-commit pointer publication; D-21 explicitly retains this initiative's responsibilities. Its remaining shared integration questions are prerequisites for an executable integration plan, not interfaces to invent here.

`map_tiles` and `sample_data` currently have seeds. Their loading implementations and the common step contract are not delivered yet. `docs/deployment/hosted_demo.md` specifies the three loading effects. The user settled manual recovery across them in this interview on 2026-10-04: repeat the entire loading flow with repeat-safe steps.

Technical-planning recheck on 2026-10-04: `sample_data` now has a closed shape and a PRD created concurrently. Its sample step requires the OpenStreetMap data first and must preserve initial votes and later community or moderation changes on retry. No loading interface or implementation plan has been delivered. These findings do not change this initiative's approved scope.

## Smallest meaningful scope

Deliver the public read of the current copy date and the common manual loading flow that consumes the existing importer and accepts the tile and sample steps supplied by their initiatives. Write the common step contract before those initiatives implement their loading integration. Verify the OpenStreetMap part locally once its backend and importer prerequisites exist; verify the complete three-part flow once all steps exist.

Agent decision at C:40, without asking: this preserves the current ownership in `MVP.md`, section Initiatives, and the effects of checks 3.2 - 3.4 of `FINAL_CHECKLIST.md`; it does not reinterpret the older seed as authorization for a second importer.

## Out of scope

- A second implementation of downloading, tag mapping, network selection, reconciliation or Valhalla data construction. `osm_importer` supplies those effects and their tests.
- The contents and implementation of the tile-loading step, owned by `map_tiles`, and the sample-loading step, owned by `sample_data`.
- Schema changes, shared backend setup, authentication rules and new rules for fact status or voting.
- Starting or restarting the routing service, the deployment commands and hosted configuration, assigned to `route_planning` and `deployment_config`.
- Automatic loading at service startup, a scheduled refresh, or deleting demo data.
- Running loading or reading personal data in the hosted demo without an explicit user request. This request authorizes repository work and local verification.

## Functional requirements

1. The service returns the calendar day in Europe/Warsaw of the current OpenStreetMap source state, or `null` before any copy exists, through the established public operation. No response field, path or authentication contract changes.
2. The common program is started manually, independently of service startup and schema revisions, and consumes the importer supplied by `osm_importer`.
3. The OpenStreetMap loading effect includes the matching walking-routing data and the importer's pointer-publication result. The program must not declare complete success when the importer reports incomplete routing-data activation or an uncertain database-commit outcome.
4. The common program accommodates the tile archive and the sample reports and geozones as steps supplied by their owners. Its step contract is a written handoff to those initiatives before their integrations are implemented.
5. A completed full loading run means that all three required loading effects have succeeded. Missing or failed steps must not be silently treated as successful. Agent decision at C:40, without asking: `docs/deployment/hosted_demo.md`, section Loading the data, requires all three effects; the repository forbids guessed fallbacks.
6. The loading result distinguishes complete success from failure after some effects were already committed. It preserves the importer's truthful publication outcome and does not claim that a committed copy was rolled back because another loading step failed (`plans/osm_importer/OSM_IMPORTER_PRD.md` FR-13 and AC-14).
7. After partial success, the operator fixes the cause and manually starts the entire loading flow again, including previously successful steps. Every step must be repeat-safe: the retry preserves community reports, votes and accounts and does not duplicate sample records. Decided by the user on 2026-10-04, answering Q-1 with option A. The precise sample deduplication contract belongs to `sample_data` and must be agreed before that integration is implemented.

## Scenarios: input, flow, expected state after the run

1. No copy yet. Input: a reachable database with the current schema but no published copy. Flow: a client requests the copy date. State after: a successful response with `date` equal to `null`; no guessed date and no database write.
2. Published copy. Input: one or more published copies. Flow: a client requests the date. State after: the day in Europe/Warsaw of the latest source-state instant, including when it falls on a different day than in UTC or than the download and publication. Routing-service restart does not define which copy date is returned.
3. First complete loading. Input: schema revisions applied, importer and both additional steps available, and the required local configuration and assets. Flow: a member of the team starts the common program manually. State after: the copy with its walking data, the tile archive and marked sample data have been loaded; the program reports success. Starting the routing service on those data follows separately under the deployment instructions.
4. Import cannot complete. Input: a previously published complete copy and a failure before publication of a fresh copy. Flow: the loading program consumes the importer's failure result. State after: the previous copy and its date remain; the program does not report successful full loading. No copy or date is invented.
5. Partial loading and recovery. Input: the importer has committed a copy and published its routing-data pointer, and a later tile or sample step fails. Flow: the operator fixes the cause and manually starts the entire loading flow again, including the importer and every other required step. State after the failed attempt: the committed copy remains readable and the loading program reports that full loading is incomplete. State after a successful retry: all three required effects have succeeded, previously successful steps have safely repeated, community contributions are preserved and sample records are not duplicated. Decided by the user on 2026-10-04, answering Q-1 with option A.
6. Service restart after a fix. Input: the loaded demo and existing community contributions. Flow: the service is restarted through its own start command. State after: loading is not triggered and the existing data remain (`docs/deployment/hosted_demo.md`, section Restarting after a fix).

## Challenging own assumptions

- Does the name of the initiative imply that it builds the importer? No. The explicit later handoff in `MVP.md` and importer D-21 retains only the read operation and common loading flow here.
- Is the displayed date the moment of download, publication or routing activation? No. M6 of the specification and the schema identify the source-state day in Europe/Warsaw. A committed database copy can precede routing activation.
- Can one all-or-nothing OpenStreetMap publication guarantee rollback of the whole demo-loading program? No. The importer commits before publishing its routing pointer, and the tile archive is a separate resource. No cross-step rollback guarantee is established.
- Does starting work at stage 3 require waiting for stage 2 code? No. `FINAL_CHECKLIST.md`, section Stages, and `MVP.md`, section Order and critical path, distinguish starting from documents from verifying a working integration.
- Can absent tile or sample integrations be skipped and full loading still be reported as done? No. The deployment loading step requires all three effects; incomplete delivery must stay visible.
- Is retry behavior already decided by the statement that the loading step is not repeated after a restart? No. That excludes automatic restart loading, but does not settle manual recovery from partial loading. The user separately settled Q-1 on 2026-10-04: manually repeat the entire loading flow with repeat-safe steps.

## Domain rules or explicit TODO

Adopt M6 and M10 of `docs/product/specification.md` without alteration: freshness refers to the source copy, dates are calendar days in Europe/Warsaw, a failed fresh import preserves the previous complete copy, refresh is manual and sample data are marked. Existing authentication and failure rules of `docs/product/api_contract.md` apply unchanged to the copy-read operation.

The importer continues to own the M4 reconciliation rules and atomic publication of the OpenStreetMap copy, facts and metadata. Recovery of the common loading flow must not weaken those rules or remove community data. A manual retry repeats every required loading step; it does not resume only the unfinished steps. This does not introduce a cross-step rollback guarantee or automatic retries.

Technical planning must verify the delivered backend read and worker seams, importer invocation and result contract, applied local schema and test fixtures, and agree the loading-step input, output, ordering and failure contract with `map_tiles` and `sample_data`. Those names and interfaces are not guessed during shaping.

## Notes on data, performance and security

Reading freshness needs only the current copy metadata, not a scan of facts or votes. No new collection of personal data is introduced. Request logs follow the existing service contract; loading logs must not include credentials or records identifying contributors.

The existing import budgets and concurrency safeguards remain with `osm_importer`; this shape does not extend them to other steps without an agreed contract. A full loading run and each retry require manual intent. No hosting address, host, login or secret is recorded in these artifacts.

The importer plan has unresolved integration questions. The backend layers and additional loading steps do not yet exist. Their absence limits runtime verification, but does not prevent defining this initiative's scope or handing off its loading-step contract.

## Open questions

None. Q-1 was resolved by the user on 2026-10-04 with option A: manually repeat the entire loading flow with repeat-safe steps. Its behavior is recorded in functional requirement 7 and scenario 5. Technical integration contracts remain work for the implementation-planning phase.
