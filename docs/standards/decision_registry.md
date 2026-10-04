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

### Hash length reported by Kuba

- Affects: the hash representation and length constraints consumed by the database and backend. On 2026-10-04 the user relayed Kuba's requirement that the hash should be 32 bytes and requested recording it here. This records the reported size, not an instruction to change the schema in the backend-skeleton initiative.
- Variants: apply the 32-byte requirement to the anonymous voter identifier, to the fact-save idempotency digest, or to both, once Kuba identifies the intended fields. A 32-byte binary digest and its 64-character hexadecimal encoding represent the same digest but are different storage representations; do not apply this requirement to password hashes without an explicit contract.
- Blocks: the report does not identify which hash Kuba meant or its storage representation. The current target schema has binary voter and fact-save idempotency hashes and a separate text password hash. No algorithm, constraint or column change is inferred from the report.
- Condition: Kuba names the affected hash fields and confirms the binary representation; the agreed requirement then lands in the target schema and the responsible database/backend implementation with a length check before this entry moves to Resolved decisions.

### Technology stack and the Python profile of the standards

- Affects: whether the twelve Python profile standards stay in force (`docs/standards/README.md`), the tools in `pyproject.toml` and `makefile`, the gates that check code, and the shape of every plan.
- Variants: a backend in Python with PostgreSQL (possibly with PostGIS), which keeps the profile as it is; another backend, which removes the profile following the steps in `README.md`; no own backend, which also removes the profile.
- Blocks: the stack follows from what the product has to do; the MVP scope it has to serve is in `docs/product/specification.md` since 2026-10-03. On 2026-10-03, in phase B of `plans_finished/mvp/`, the user chose the backend - Python 3.13 with FastAPI, on PostgreSQL with PostGIS - and with it kept the Python profile (`plans_finished/mvp/MVP_PLAN.md` D-1). That decision lives in `plans_finished/mvp/MVP_PLAN.md` D-1 and in `MVP.md`, and the first backend code that carries it is built by the initiative `backend_skeleton` (`MVP.md`). On 2026-10-03 `plans_finished/frontend_stack/` decided the frontend technology and recorded how frontend code is held to the standards: the workflow core and `standard_frontend.md` in the standards map (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`).
- Condition: the backend decision lands in the first backend code and in the standards map. The frontend half of this entry is met. The profile is kept or removed in the same change, never left in force by inertia.

### HarmonyOS port and the Huawei submission

- Affects: whether the project is submitted to the Huawei challenge at all, the architecture of the clients, the time left for the Kraków deliverables.
- Variants: a native ArkTS/ArkUI client using the same backend as the web app; a React Native for OpenHarmony client; no Huawei submission. A web build alone is explicitly not a valid Huawei submission. An ArkTS application that embeds the web app was a variant until 2026-10-03, when the repository owner decided, and the frontend person accepted, that the port, if it is built, is a second client of the same programming interface and not an embedding of the web app (`plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`, section Domain rules).
- Blocks: the progress of the web app, which comes first.
- Condition: the team sets a go/no-go time for the port. A `.hap` package, its build instructions, a recorded demo and `AI_WORKFLOW.md` need several hours before the deadline, so the decision has to come early enough to leave them.

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
- Blocks: on 2026-10-04 the initiative stood on branch mw, not merged into the line of plans_finished/mvp, with a plan in progress. The user decided that an unfinished initiative does not stop plans_finished/mvp and adds its content to MVP.md later. The importer handoff of osm_importer does not settle this independent MSIP scope decision.
- Condition: the branch is merged, or Rafał and the initiative owner decide whether the stops of MSIP enter the MVP. MVP.md follows in the same change.

### When the initiative of O9 starts its code

- Affects: the initiative `public_transport_routing` of `MVP.md`, its time box of 4.5 hours of work of the people of the team, and the order of the section Order and critical path of `MVP.md`.
- Variants: `public_transport_routing` waits for `route_planning` and `osm_importer`, as `plans_finished/mvp/MVP_PLAN.md` D-15, amended by D-20, and `MVP.md` record; or it starts at once, in parallel with them, as the section Optional features of `docs/product/specification.md` says of O9 - built first and in parallel with the mandatory features - with the parts it shares with `route_planning` and `osm_importer` agreed between their owners.
- Blocks: the specification prevails over the plan, but the waits of D-15 were approved by the user on 2026-10-04, and the user decided that no question is asked while `plans_finished/mvp/` is carried out. Both `route_planning` and `public_transport_routing` are owned by Marek.
- Condition: Rafał and Marek decide the start of `public_transport_routing`, at the latest when its seed goes into `plan-shape`; `MVP.md` follows in the same change.

### Wording of the public transport segment of O9

- Affects: the exception of O9 in M7 and M10 of `docs/product/specification.md` and the state the initiative `public_transport_routing` of `MVP.md` shows for a public transport segment.
- Variants: the exception of M7 also names a segment the GTFS marks as accessible, next to a segment whose GTFS gives no accessibility information, and names the alighting at the stop next to "the ride and the boarding at the stop", as the item of O9 on stops and trips already names boarding and alighting; or the text stays as it is, and those two cases are read from that item of O9.
- Blocks: the first review of `plans_finished/valhalla_routing/` found the gap on 2026-10-04 (`plans_finished/valhalla_routing/VALHALLA_ROUTING_REVIEW.md`, I-2), and Rafał decided on 2026-10-04, when that initiative closed, to leave the text of the specification unchanged and to hand the wording to the initiative that builds O9.
- Condition: Marek and Rafał decide the wording when the seed of `public_transport_routing` goes into `plan-shape`; a changed wording lands in a new version of the specification, and this entry then moves to Resolved decisions.

### Street name of an item of a list

- Affects: the place of an item of the list of a route and of the list of the map of facts (`docs/product/views.md`, decision 13), the route response and the facts of an area of `docs/product/api_contract.md`, which have no field for the name of a way, `docs/product/schema.md`, which keeps no name of a way, and the initiatives `osm_import`, `route_planning`, `community_facts` and `frontend_app` of `MVP.md`.
- Variants: the contract and the stored data carry the name a way has in OpenStreetMap, so the place of an item is that name with the distance from the start, as M8 of `docs/product/specification.md` says since version 11; or the MVP leaves the name out, so a row of a route shows the distance alone, as M8 gives for a way without a name, and a row of the map of facts shows no place line, as `docs/product/views.md` decision 13 gives for a row without a street name.
- Blocks: version 11 of the specification added the name to M8 without a field in the contract or a column in the target schema, and the user deferred it until Marek tests the programming interface (`docs/product/specification.md`, Decision provenance, version 11).
- Condition: Marek has tested the programming interface. The name then lands in `docs/product/api_contract.md` and, through a new version of the specification, in `docs/product/schema.md`, or leaving it out lands in M8; this entry then moves to Resolved decisions.

### Intellectual property between the two challenges and the repository licence

- Affects: whether both prizes can be accepted, and which licence, if any, the public repository carries.
- Variants: no licence file (the repository is public, all rights reserved); an open-source licence (which grants licences to everyone, while the Kraków transfer agreement has the authors declare that they have granted none); submitting to one challenge only.
- Blocks: it needs an answer from the organizers - the City of Kraków challenge mentors and Huawei - on how the copyright transfer for the Kraków prize relates to the Huawei licence and to a public repository (`docs/hackathon/challenge_requirements.md`, Conflicts and open points 2 and 3). An agent does not decide this, and nothing written here is legal advice.
- Condition: the organizers have answered, before a licence file is added to the repository.

## Resolved decisions

### OpenStreetMap importer ownership and Valhalla data preparation

Resolved on 2026-10-04: the user authorized modifying MVP and approved including network PBF preparation, Valhalla walking-data construction and post-commit routing-pointer publication in osm_importer. The importer and its tests are assigned there; osm_import retains read_osm_copy and the common demo-loading program, consuming the importer. The decisions live in plans/osm_importer/OSM_IMPORTER_PLAN.md D-19 - D-21 and plans_finished/mvp/MVP_PLAN.md D-20, and MVP.md records the ownership, requirements and dependencies. Shared backend, schema delivery and the vote-lock integration remain outstanding prerequisites.

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
