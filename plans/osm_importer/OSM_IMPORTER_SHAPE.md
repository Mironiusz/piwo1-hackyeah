# Shape: Implement the OpenStreetMap importer for Kraków

Document state: 2026-10-03, interview closed
Regulator: C:40

## Problem

The project has decided where its OpenStreetMap data comes from and how tags become barriers and amenities, but the importer has not been built. Without a complete first copy, the app has no pedestrian network or initial OpenStreetMap facts for Kraków.

The user created `osm_importer` to carry this implementation separately from the MVP initiative, which a colleague is currently working on. The user explicitly prohibited editing that initiative and its plan, and asked for any absolutely necessary change there to be reported as a decision with a visible warning in capital letters.

The task prefix is `OSM_IMPORTER`, following the initiative name given by the user. The seed preserves the request, and this shape records its scope together with the decisions already present in the repository.

## Recipient and trigger

The recipients are the project backend and its routing engine, which need one coherent copy of the pedestrian network and accessibility facts, and the team member who prepares the demo or requests a refresh.

A team member starts the first import before the demo and explicitly starts subsequent refreshes. An app user's request never starts an import, and the prototype has no scheduled refresh. This follows from `docs/product/specification.md` M6 and `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-11.

Creating this initiative does not authorize running an import against the hosted demo database or changing the hosted services. Such actions still require the explicit request specified in `AGENTS.md`.

## Current state

The following list records the repository state at creation, rather than the state of later phases.

- `docs/product/specification.md` version 5 is the source of truth for product behavior. M2 defines the pedestrian network, M3 the closed list of facts, M4 their identity and fate across refreshes, and M6 the tag mapping and the complete-copy rule.
- `plans_finished/osm_data_source/` delivered the source and refresh decisions. Its PRD explicitly excludes building the importer and assigns that work to the MVP. Its PLAN supplies the download, validation, area, reconciliation, failure behavior and required tests.
- `plans_finished/osm_barrier_mapping/` delivered the rules for deriving barriers, amenities and way attributes. Those rules are reflected in the product specification, rather than being new product choices for this initiative.
- `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-4 and D-11 require the imported pedestrian network with ordered nodes and their coordinates. Building the route engine remains outside this initiative.
- At creation, `plans/mvp/MVP_PLAN.md` is in progress. D-4 and D-5 still assign import work and its tests to an MVP work package, and Q-11 owns the backend architecture and the import trigger. The sections Scope of changes, Rollout order and Definition of Done are empty.
- `plans/fact_schema/FACT_SCHEMA_PLAN.md` is closed as a plan, but its target document `docs/product/schema.md` is not present in the tree read for this task. Its sibling task `SCHEMA_REVISION` still has an interview in progress. Neither the target schema nor an applied revision is assumed to exist.
- There is no product backend or importer code in the tree read for this task. Runtime dependencies in `pyproject.toml` are empty. The preparation plans are evidence of decisions, not proof of implemented services.

Refresh on 2026-10-03, before phase A of `plan-prd`: the product specification is now version 7, and the target schema `docs/product/schema.md` exists and is part of the specification since version 6. The model initiative is archived at `plans_finished/fact_schema/`; its first revision is a separate initiative at `plans/schema_revision/`. These documents supply the target contract, not evidence of an applied revision. The MVP plan still assigns import work to its work packages and leaves the backend architecture, import trigger and execution machine to a separate backend initiative. The scope below stays the same; phase B must verify the shared implementation and coordinate ownership before naming implementation steps.

### WARNING: IMPORT OWNERSHIP HANDOFF BEFORE IMPLEMENTATION

The user assigns implementation of the importer to `osm_importer`. This instruction takes precedence over the earlier assignment to an MVP work package. No file under `plans/mvp/` is changed by this initiative's creation.

Before the colleague finalizes or executes the MVP import work package, its owner needs to record that `osm_importer` supplies the importer and its tests, while the MVP consumes the resulting data and retains responsibility for its shared backend setup. D-4 and D-5 currently describe the earlier ownership; the data-source and product decisions themselves do not need to change.

The concrete handoff for the user to relay is: reference `plans/osm_importer/` as the executor of the import work, avoid a second implementation of that work in MVP, and keep the shared backend and database prerequisites explicit. This is coordination for implementation, not a prerequisite for creating this shape. The agent reports the handoff to the user and does not edit the colleague's files or send a message to the colleague.

On 2026-10-04 the user reported that Rafał, who owns the MVP work, confirmed he would handle this handoff. The user approved `OSM_IMPORTER_PRD.md` and requested the technical plan. This authorizes phase B; the backend integration contracts still need to be verified.

## Smallest meaningful scope

Deliver the complete importer that obtains the selected source, checks it, limits it to Kraków, derives the agreed pedestrian network and accessibility information, and makes a complete copy available in the shared project database.

The same importer performs the first import and subsequent manual refreshes, preserves existing votes and user facts under the product rules, and leaves the last complete copy unchanged on failure. Verification, operating instructions and documentation of the imported data are part of this scope.

This is the full importer discussed in the preceding conversation, rather than a task limited to downloading a file. The shared backend setup, database environment and schema delivery remain dependencies owned outside this initiative. Agent decision at C:40, without asking: this follows from the user's extraction of the importer and the ownership recorded in the existing initiatives.

## Out of scope

- Editing any file of the MVP initiative, including its seed, shape, PRD and plan.
- Reopening product rules already settled in the specification, or choosing a second source because the chosen one is unavailable.
- Designing a separate database model, implementing the shared schema revision or creating a separate backend for the importer. The importer must use the shared project contracts after their owners deliver them.
- Implementing routing, address search, the frontend, map tile production, or an end-user endpoint that triggers an import.
- A scheduled refresh, data outside Kraków, or writing reports back to OpenStreetMap.
- Deploying or running the importer in the hosted demo without an explicit request.

## Functional requirements

1. A team-triggered run supplies the first complete copy for Kraków and can later refresh it from the selected OpenStreetMap source.
2. The imported network follows M2, with geometry, ordered nodes and coordinates sufficient for the routing engine. Barriers, amenities and way attributes follow M3 and M6, independently of a person's preferences.
3. The copy and each OpenStreetMap fact retain their source and relevant dates. The copy date describes the state of OpenStreetMap, not the day it was downloaded.
4. New OpenStreetMap facts start unverified. An absent or unknown attribute is not a fact and does not become a confirmation of accessibility.
5. The network, facts, refresh reconciliation and copy date become current together. A failure leaves the last complete copy unchanged, and a failed first import publishes no partial data.
6. Refreshes preserve fact identity and votes according to M4. The disappearance and return of an OpenStreetMap fact do not cause automatic merging with nearby user reports.
7. Import runs do not overlap. Processing the same source state again does not create duplicate facts or votes or move the copy date backwards.
8. The operator can distinguish a successful update, an unchanged copy, a skipped concurrent run and a failed run. Instructions cover the first import, refresh, verification and failure outcomes.
9. The importer is verified against the source, mapping, reconciliation and database requirements already recorded in the dependency plans. Real OpenStreetMap data does not enter the repository tree.

## Scenarios: input, flow, expected state after the run

1. First import: no copy exists; a team member starts a run with a valid source; the complete network and facts for Kraków become available with the source-state date. New facts have no votes and are unverified.
2. Failed first import: no copy exists; the source cannot be obtained or validated; the run fails without publishing a partial network or inventing a date.
3. Successful refresh: a complete copy exists; a later valid source is processed; the network, facts and date switch together, and votes remain attached to the same fact identities.
4. Failed refresh: a complete copy exists; download, validation, processing or persistence fails; the previous network, facts, votes and copy date remain current.
5. Disappearing fact: an OpenStreetMap fact is missing from a later copy; confirmations and denials are evaluated under M4; it becomes a user fact when confirmations outweigh denials, otherwise it becomes outdated. Its votes remain in its history.
6. Returning fact: a later copy restores the same fact type on the same OpenStreetMap element; the same fact becomes an OpenStreetMap fact again with its votes. A nearby independent user report remains separate.
7. Repeated or overlapping run: the operator starts two imports, or fetches the state already in use; the concurrent run is skipped, and reprocessing the current state leaves the data unchanged.

## Challenging own assumptions

- Does an archived source initiative mean the importer already exists? No. Its PRD excludes code delivery, and the current tree has no importer. This initiative owns implementation, not another source-selection exercise.
- Does extracting the importer permit editing the colleague's plan? No. The user's instruction explicitly prohibits it. The ownership discrepancy is recorded here and reported for the colleague to resolve before implementation overlaps.
- Can a downloaded file alone count as success? No. The backend needs a coherent stored copy and correct handling of existing facts and votes.
- Can a closed schema plan be treated as an existing database contract? No. The target schema and applied revision must be verified at the technical planning stage. This initiative does not invent substitute tables.
- Should this initiative also produce the map background? No. The source PRD explicitly separates base map tiles from the imported routing and accessibility data.

## Domain rules or explicit TODO

The rules in `docs/product/specification.md` M2, M3, M4 and M6 are adopted without alteration. In particular, fact identity is the OpenStreetMap element type and identifier together with the fact type, never proximity; a disappearing fact follows the latest-vote rules of M4; a returning fact keeps its history; an independent user fact is never merged automatically; and all-or-nothing publication applies to the entire copy.

Technical planning must re-read the source, mapping and routing decisions against the then-current product specification, verify the delivered shared schema and backend contracts, and agree file ownership before implementation. Those dependencies are not resolved by guessing in this shape. Any proposed change to product behavior must return to the user.

If a necessary MVP change is identified later, record the concrete decision here or in the subsequent artifacts and report it to the user with a warning in capital letters. Do not apply that change to the MVP initiative.

## Notes on data, performance and security

- The run obtains public source data, not a person's route, location, preferences or account data. Nothing of a route request is sent to a source service.
- The source plan already records file size and processing measurements. They are evidence from the environment where they were made, not a guarantee for the current machine or the hosted demo. Technical planning verifies resource limits and the execution environment.
- Source validation, timestamps, atomic publication and preservation of votes are integrity requirements. A download failure is not permission to create a second data source or claim the empty map is current.
- Public OpenStreetMap extracts, their slices and checksums are not saved in the repository tree. Tests use invented elements as required by the source plan.
- Database setup and migrations remain with their owners. No target-environment address, login or secret is placed in initiative artifacts.
- Product and dependency documents may change while the colleague works. Re-read them before the next phase and report conflicting contracts without overwriting their edits.

## Open questions

None for the product scope of this shape. The request and the existing specification settle the behavior and the user has authorized the separate initiative. No new domain decision is introduced.

The shared schema, backend entry points, configuration and implementation file ownership are prerequisites to verify and settle in phase B of `plan-prd`. This shape does not claim that they have been delivered or that an implementation plan is ready. The next phase is started only on the user's request.
