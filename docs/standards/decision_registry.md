# Deferred decisions registry

Document state: 2026-10-04

## Why this document exists

This file collects decisions that are known to be needed but have been deliberately postponed - because a measurement is missing, because they depend on a contract with someone outside, or because their moment has not come yet. Without such a place, a decision deferred in a conversation disappears together with the conversation and comes back only as a surprise during implementation, when it is already the most expensive.

This is not a standard and it has no core sections. It is a registry, like `naming_registry.md` - it describes the actual state of the decision process, not the target state of the repository.

Boundary with the neighbors: `docs/standards/README.md`, in the section on boundaries and debts, describes decisions already made and debt already present in closed initiatives - it looks to the past. This file looks to the future. The `<TASK>_REVIEW.md` artifact in `plans/` records what the agent ran into during one task; if such a finding leads to a decision that goes beyond that task, its place is here.

## How to use it

An entry is created at the moment someone states that the decision cannot responsibly be made today. It always contains four things: what the decision affects, what the variants are, what blocks resolving it, and how we will know it can be made.

An entry leaves the list of open decisions only when the decision has landed where people look for it - in the right standard, in the product specification or in the code. It then moves to the resolved section with one sentence about how it turned out and where it lives now. The entry here is never the source of truth for a rule - it is only a record that the rule does not exist yet.

A deferral needs a reason. "We did not want to think about it" is not a reason; "we have no measurement on the target driver" is.

## Open decisions

### Standards of the worker without periodic tasks

- Affects: `standard_worker.md`, sections One process, one task registry, Periodic task contract, Locks and Adding a new task; the parts of other standards that assume a worker keeping time - `standard_time.md`, section Writing the pair: one value, not two columns (the periodic control task), `standard_errors.md`, section Reaction in a periodic task, `standard_naming.md`, section File names, and `standard_architecture.md`, section Calls to external systems; the run identifier, which `standard_logging.md` and `standard_worker.md` each leave to the other; and the import command of `osm_importer`.
- Variants: `standard_worker.md` is narrowed or extended to describe a one-off administrative command started by hand - its run deadline, the protection against two runs at the same time, its result and its reaction to errors - and the other standards follow it; or the periodic rules stay as the target for a later periodic task, next to a new section on one-off commands.
- Blocks: `MVP.md` D-14 decides that no periodic task exists and that the import is the one-off command `python -m worker.osm_import`, while the Python profile was written for a service with a worker that keeps time. No worker code exists yet, and `plans/backend_skeleton/` and `plans_finished/osm_importer/` are still planning the first one. The user decided on 2026-10-04 in `plans/repository_consistency/` to defer the rewrite until that code exists instead of guessing its shape.
- Condition: the first worker code of `backend_skeleton` or `osm_importer` exists; the standards are then changed to match it, and this entry moves to Resolved decisions.

### HarmonyOS port and the Huawei submission

- Affects: the architecture of the HarmonyOS client and the time left for the Kraków deliverables.
- Variants: a native ArkTS/ArkUI client using the same backend as the web app; or a React Native for OpenHarmony client. Not submitting to Huawei is no longer a variant: the Huawei submission is mandatory since 2026-10-04 (`plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7). A web build alone is explicitly not a valid Huawei submission. An ArkTS application that embeds the web app was a variant until 2026-10-03, when the repository owner decided, and the frontend person accepted, that the port, if it is built, is a second client of the same programming interface and not an embedding of the web app (`plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`, section Domain rules).
- Blocks: the choice between the two clients is made by the shape of `plans/stage5_harmonyos_port/`, which holds only its seed so far.
- Condition: the shape of `plans/stage5_harmonyos_port/` chooses the client, check 8.1 of `FINAL_CHECKLIST.md`; this entry then moves to Resolved decisions. A `.hap` package, its build instructions, a recorded demo and `AI_WORKFLOW.md` need several hours before the deadline, so the choice has to come early enough to leave them.

### Optional features of the MVP

- Affects: the optional queue O1-O8 of `docs/product/specification.md` - QR transfer of the profile, photos, points and ranking, open city data, geozone corrections, place cards, live alerts, voice. Three of them come straight from the seed of `plans_finished/mvp/`: points with the ranking, geozone corrections and voice.
- Variants: a pass of `plan-prd` for O1-O3 only, which the team can still reach before the deadline; a pass for the whole queue; leaving them as ideas for the presentation.
- Blocks: the specification describes them only in sketches, and the team decided on 2026-10-03 to plan and build the mandatory core M1-M11 first.
- Condition: M1-M11 meet the acceptance criteria of `plans_finished/mvp/MVP_PRD.md`. Then the optional features get their own pass of `plan-prd`, starting with O1.

### Technical directions of the MVP plan

- Affects: the initiative `backend_skeleton` and, through it, the implementation initiatives of `MVP.md` that wait for it; until 2026-10-04 also `plans_finished/mvp/MVP_PLAN.md`, which could not be closed before these directions were decided.
- Variants: the variants the agent offered for each direction are quoted in the seed of its initiative.
- Blocks: on 2026-10-03 the user decided that every technical direction of the MVP plan is decided by the team role responsible for it, in its own initiative, not in phase B of `plans_finished/mvp/`. The initiatives and their owners: `plans_finished/routing_engine/` (backend), `plans_finished/valhalla_routing/` (backend), `plans_finished/osm_data_source/` (import), `plans_finished/frontend_stack/` (frontend), `plans_finished/demo_environment/` (db), `plans_finished/deployment/` (db, since 2026-10-03 the owner of the server of the demo), `plans/deployment_config/` (db, the owner of the server of the demo), `plans_finished/osm_barrier_mapping/` (import, approved as a product rule by the owner of the specification), `plans_finished/local_database/` (db), `plans_finished/geocoding/` (external API), `plans_finished/account_sessions/` (backend), `plans_finished/api_contract/` (backend), `plans_finished/backend_architecture/` (backend), `plans_finished/schema_revision/` (db), `plans_finished/fact_schema/` (db). The last one decides the domain model and database schema of facts and votes, together with the identifier of a vote without an account, and also builds the first schema revision (user decision of 2026-10-03, `plans_finished/fact_schema/FACT_SCHEMA_SHAPE.md`, question 1), a decision reversed later on 2026-10-03 in `plans_finished/schema_revision/`. That revision waits for the local database with PostGIS and for a backend skeleton holding the Alembic configuration. On 2026-10-03 the revision became the separate task `SCHEMA_REVISION` of `plans_finished/schema_revision/`, and Q-10 of the MVP plan closes with the task `FACT_SCHEMA`, which decides the model and writes the target schema, because the layout of that skeleton follows Q-11 and the MVP plan cannot close before Q-10 (U-1 of `plans_finished/dependency_check/`). `plans_finished/local_database/` decided on 2026-10-03 how the team gets that database (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md`), and the initiative `backend_skeleton` builds the local setup and the Alembic configuration (`plans_finished/mvp/MVP_PLAN.md` D-7), which since 2026-10-04 the initiative `schema_first_revision` builds instead in the package `db/` (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_PLAN.md` D-14); the decision on the model does not wait for either. State on 2026-10-04: decided and archived in `plans_finished/` are `geocoding`, `osm_data_source`, `osm_barrier_mapping`, `frontend_stack` and `local_database` (`plans_finished/mvp/MVP_PLAN.md` D-3 - D-7); `plans_finished/fact_schema/` decided the model and the target schema `docs/product/schema.md` in its task `FACT_SCHEMA` (`plans_finished/mvp/MVP_PLAN.md` D-11) and is archived, and its former task `SCHEMA_REVISION`, moved into an initiative of its own on 2026-10-03, built no code, wrote version 12 of the specification with the idempotency key and is archived in `plans_finished/schema_revision/`, and the initiative `schema_first_revision` builds the first revision (`plans_finished/mvp/MVP_PLAN.md` D-11); `plans_finished/demo_environment/` is decided and archived, and its former task `DEPLOYMENT`, moved into an initiative of its own on 2026-10-03, moved the demo to a server of a member of the team in a data centre, wrote the instructions `docs/deployment/hosted_demo.md` on 2026-10-04 and is archived in `plans_finished/deployment/`, while its former task `DEPLOYMENT_CONFIG`, which writes the deployment configuration, moved to `plans/deployment_config/` on 2026-10-04 and has only its seed (`plans_finished/mvp/MVP_PLAN.md` D-10); `plans_finished/routing_engine/` was decided on 2026-10-03 and on 2026-10-04 `plans_finished/valhalla_routing/` superseded it for D-9 with one Valhalla service run by the project (`plans_finished/mvp/MVP_PLAN.md` D-9), sending the optional feature O9, routes with public transport, to a separate initiative set up by the user; `plans_finished/account_sessions/` is decided (`plans_finished/mvp/MVP_PLAN.md` D-8); `plans_finished/api_contract/` decided the contract `docs/product/api_contract.md` (`plans_finished/mvp/MVP_PLAN.md` D-12); the backend architecture of Q-11 was decided on 2026-10-04 in `plans_finished/backend_architecture/`, which is archived (`plans_finished/mvp/MVP_PLAN.md` D-14), and the implementation of the operations of that contract goes to the initiatives of `MVP.md`. On 2026-10-04 the user decided that `plans_finished/mvp/` implements nothing and hands the implementation to the initiatives of `MVP.md` (`plans_finished/mvp/MVP_PLAN.md` D-13).
- Condition: each initiative records its decision; the matching open question of `plans_finished/mvp/MVP_PLAN.md` is then closed, and the backend architecture of Q-11 is decided in `plans_finished/backend_architecture/` (`plans_finished/mvp/MVP_PLAN.md` D-14).

### Initiatives outside MVP.md that overlap its initiatives

- Affects: the stops of buses and trams from the MSIP service of Kraków with a daily import in `plans/bus_station_api_integration/`, the no-periodic-task rule of `plans_finished/mvp/MVP_PLAN.md` D-14, and optional features O4 and O9 of `docs/product/specification.md`. The importer ownership overlap formerly tracked here is resolved below.
- Variants: `bus_station_api_integration` enters the MVP, requiring a decision against D-14 and O4 being outside the MVP, or remains outside it as part of O4 or O9.
- Blocks: on 2026-10-04 the initiative stood on the branch `mw`, not merged into the line of `plans_finished/mvp/`, with a plan in progress. The user decided that an unfinished initiative does not stop `plans_finished/mvp/` and adds its content to `MVP.md` later. The importer handoff of `osm_importer` does not settle this independent MSIP scope decision.
- Condition: the branch is merged, or Rafał and the initiative owner decide whether the stops of MSIP enter the MVP. `MVP.md` follows in the same change.

### Street name of an item of a list

- Affects: the place of an item of the list of a route and of the list of the map of facts (`docs/product/views.md`, decision 13), the route response and the facts of an area of `docs/product/api_contract.md`, which have no field for the name of a way, `docs/product/schema.md`, which keeps no name of a way, and the initiatives `osm_importer`, `route_planning`, `community_facts` and `frontend_app` of `MVP.md`.
- Variants: the contract and the stored data carry the name a way has in OpenStreetMap, so the place of an item is that name with the distance from the start, as M8 of `docs/product/specification.md` says since version 11; or the MVP leaves the name out, so a row of a route shows the distance alone, as M8 gives for a way without a name, and a row of the map of facts shows no place line, as `docs/product/views.md` decision 13 gives for a row without a street name.
- Blocks: version 11 of the specification added the name to M8 without a field in the contract or a column in the target schema, and the user deferred it until Marek tests the programming interface (`docs/product/specification.md`, Decision provenance, version 11).
- Condition: Marek has tested the programming interface. The name then lands in `docs/product/api_contract.md` and, through a new version of the specification, in `docs/product/schema.md`, or leaving it out lands in M8; this entry then moves to Resolved decisions.

### Backend handoff for vote locking during OSM publication

- Affects: the operation `cast_vote` of the initiative `community_facts` of `MVP.md`, the publication of a fresh OpenStreetMap copy of `osm_importer` (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-15 and its risk R-8), and the statuses of M4 of `docs/product/specification.md` computed during that publication.
- Variants: `cast_vote` locks its fact before it checks that the fact is visible and writes the vote, so that a vote on a fact being reconciled waits until the publication commits or rolls back, as D-15 of the importer plan assumes; or the owner of `community_facts` proposes another mechanism with the same guarantee, and the importer plan follows it.
- Blocks: the user chose on 2026-10-04, in the plan of `osm_importer`, to freeze the votes of the facts being reconciled during the final publication instead of reconciling against a snapshot, and that choice rests on the code of another initiative. `community_facts` has only its seed, and its owner has not agreed to the lock; R-8 of the importer plan pointed to this entry before it existed. Recorded on 2026-10-04 by `plans/repository_consistency/` at the request of the user. On 2026-10-04 Kuba, who builds the vote write in the data layer of `community_facts`, agreed to the first variant in `plans/community_facts/COMMUNITY_FACTS_SHAPE.md`, question 3; the rule has not reached the plan of `community_facts` yet.
- Condition: the owner of `community_facts` and Mateusz agree on the lock at the latest when `cast_vote` is planned in the shape of `community_facts`; the agreed rule lands in the plans of both initiatives, and this entry moves to Resolved decisions.

### Intellectual property between the two challenges and the repository licence

- Affects: whether both prizes can be accepted, and which licence, if any, the public repository carries.
- Variants: no licence file (the repository is public, all rights reserved); an open-source licence (which grants licences to everyone, while the Kraków transfer agreement has the authors declare that they have granted none); submitting to one challenge only.
- Blocks: it needs an answer from the organizers - the City of Kraków challenge mentors and Huawei - on how the copyright transfer for the Kraków prize relates to the Huawei licence and to a public repository (`docs/hackathon/challenge_requirements.md`, Conflicts and open points 2 and 3). An agent does not decide this, and nothing written here is legal advice.
- Condition: the organizers have answered, before a licence file is added to the repository.

### Executor of the API and service layers of the community facts

- Affects: the API and service layers of the nine operations of the initiative `community_facts` of `MVP.md` - `list_facts_in_area`, `read_fact`, `find_nearby_facts`, `create_fact`, `cast_vote`, `flag_fact`, `list_flagged_facts`, `hide_fact` and `restore_fact` of `docs/product/api_contract.md`, sections Facts and Moderation - with the identifier of a person without an account of M9 of `docs/product/specification.md`, and checks 5.1 - 5.3 of `FINAL_CHECKLIST.md`, which are verified on the running service.
- Variants: Marek builds both layers of all nine operations on the data layer and the status evaluator of `plans/community_facts/`; or the layers follow the owners of `MVP.md` - Marek for the reports and geozones, Kuba for the votes, flags and moderation; or another member of the team takes them.
- Blocks: Kuba narrowed `plans/community_facts/COMMUNITY_FACTS_SHAPE.md` on 2026-10-04 to the part that touches the database - the data layer of the nine operations and the status evaluator - while the seed of the initiative orders the operations themselves. After the cut nobody is named to build the endpoints, the validation of a request, the mapping to the responses and errors of the contract, the orchestration of a request into one transaction and the identifier of a person without an account. That identifier carries the blocking category of personal data: which characteristics of the browser are combined with the IP address, whether the hash is keyed, and how the address of the person reaches the service behind the reverse proxy of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-10. Recorded on 2026-10-04 at the request of Kuba.
- Condition: Rafał and Marek name the executor before the work of check 5.1 of `FINAL_CHECKLIST.md` starts on the service. The executor settles the identifier of a person without an account in its own shape, the column Owner of `MVP.md`, section Initiatives, follows in the same change, and this entry moves to Resolved decisions.
- Progress on 2026-10-04: the user accepted Marek's API and service work for all nine operations and confirmed the task `COMMUNITY_FACTS_API` within `plans/community_facts/`. `MVP.md` now records that split with Kuba's data layer and evaluator. The user then chose IP + User-Agent as the only identifying inputs, accepting a shared identity and daily limit for identical pairs; version 18 of the specification and the task's closed shape record that decision. Hashing and the trusted-proxy boundary still need resolution in the implementation plan. The entry remains open until these decisions and the team handoff are settled.

## Resolved decisions

### When the initiative of O9 starts its code

Resolved on 2026-10-04 by Rafał in the shape interview of `plans/public_transport_routing/`, question 1: `public_transport_routing` starts its code at once, in parallel with `route_planning` and `osm_importer`, as the section Optional features of `docs/product/specification.md` says of O9, against waiting for them as `plans_finished/mvp/MVP_PLAN.md` D-15 and D-20 recorded. What does not need the code of `route_planning` goes first - the interface in `docs/product/api_contract.md`, the copy of the GTFS and the routing data with public transport - and the route with public transport joins the code of `route_planning` once it exists (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-1). It lives in `MVP.md`, sections Initiatives and Order and critical path. The entry named Rafał and Marek, so Marek's confirmation is still to come.

### Wording of the public transport segment of O9

Resolved on 2026-10-04 by Rafał in the shape interview of `plans/public_transport_routing/`, question 2: the exception of O9 in M7, M10 and O9 names the boarding at the stop, the ride and the alighting at the stop, green whether the GTFS marks them as accessible or gives no accessibility information for them, against leaving the text as it was and reading both cases from the item of O9 on stops and trips. It lives in version 17 of `docs/product/specification.md`, with what the segment shows and its missing state for a profile without barriers. The entry named Marek and Rafał, so Marek's confirmation is still to come.

### Route without assessment in the contract

Resolved on 2026-10-04 by Rafał in place of Marek in `plans_finished/route_planning/`: with a profile that names no barrier, every segment of a route and of its alternative, the straight stretches to the network included, carries the state `not_assessed` of `plan_route`, a value of `state` outside the four states of M7 that appears in no other case, so the client derives nothing from its own request. It lives in `docs/product/api_contract.md`, section plan_route, and in `docs/product/views.md`, section The views read against the contract of the team, still to be confirmed by Kuber and Adrian.

### Refusal of a point outside Kraków in the contract

Resolved on 2026-10-04 by Rafał in place of Marek in `plans_finished/route_planning/`: `plan_route` refuses a start or a destination outside the administrative boundary of Kraków of the copy in use with `point_outside_krakow` and the status 422, whose field `points` names the point, and the client also checks a point against the bounds of the map of Kraków when it is set; a point inside the bounds but outside the boundary stays set until the route is requested, as M2 of `docs/product/specification.md` says since version 15. It lives in `docs/product/api_contract.md`, section plan_route, and in `docs/product/views.md`, section The views read against the contract of the team and V-4, still to be confirmed by Kuber and Adrian.

### Hash length reported by Kuba

Resolved on 2026-10-04: Kuba named the hash of a vote without an account as the affected field and kept it binary - `voter_hash` of `vote` is 32 bytes, held by `CK_vote_voter_hash_sha256`, next to the 32 bytes of `CK_fact_idempotency_key_sha256` the idempotency key already had, and the password hash stays outside it. It lives in version 13 of `docs/product/specification.md`, in `docs/product/schema.md`, section Accounts and votes, and in the first revision of the package `db/` (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_PLAN.md` D-3); the user moved this entry here while merging `dev` into `jmi/odklejka_v1`.

### OpenStreetMap importer ownership and Valhalla data preparation

Resolved on 2026-10-04: the user authorized modifying MVP and approved including network PBF preparation, Valhalla walking-data construction and post-commit routing-pointer publication in `osm_importer`. The importer and its tests are assigned there; `osm_import` retains `read_osm_copy` and the common demo-loading program, consuming the importer. The decisions live in `plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-19 - D-21 and `plans_finished/mvp/MVP_PLAN.md` D-20, and `MVP.md` records the ownership, requirements and dependencies. Shared backend, schema delivery and the vote-lock integration remain outstanding prerequisites.

### Language of the repository

Resolved on 2026-10-03 by the user: everything in the repository is written in English, the conversation with the user stays in Polish. It lives in `CLAUDE.md` and `AGENTS.md`, section Language and communication style.

### Location of the product specification

Resolved on 2026-10-03 by the user: the specification lives in the repository, in `docs/product/`. It lives in `CLAUDE.md`, section What we are building.

### Product specification and the scope of the prototype

Resolved on 2026-10-03 by the user: the prototype is narrowed to wheelchair users, parents with baby strollers and people with walking difficulties, matched through barrier and amenity preferences rather than a disability, and the MVP is split into mandatory and optional features. It lives in `docs/product/specification.md`; product behavior not described there still goes to the user.

### Blocking risk categories

Resolved on 2026-10-03 by the user: the ten categories of the template stay unchanged. It lives in `docs/standards/standard_agentic_workflow.md` ch. 3.3.

### Target environment for the demo

Resolved on 2026-10-03 by the user, answering for the db person, and changed on 2026-10-04 by the user in `plans_finished/deployment/`. The demo runs on a server of the user in a data centre, reached at its IP address over plain HTTP, and is deleted with all its data on 4 October 2026. The virtual private server of the db person, chosen in `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8, is superseded. The choice lives in `plans_finished/deployment/DEPLOYMENT_PRD.md` FR-5 and `plans_finished/mvp/MVP_PLAN.md` D-10, the permission levels of the agent in `CLAUDE.md` and `AGENTS.md`, section Target environment.

### Technology stack and the Python profile of the standards

Resolved on 2026-10-04 in the backend foundation: `api/`, `config/`, `data/`, `service/` and `worker/` implement the Python/FastAPI/PostgreSQL stack chosen in `plans_finished/mvp/MVP_PLAN.md` D-1. The standards map keeps the Python profile explicitly; frontend remains governed by its separate profile. Platform acceptance is recorded in `plans_finished/backend_skeleton/BACKEND_SKELETON_REVIEW.md`.
