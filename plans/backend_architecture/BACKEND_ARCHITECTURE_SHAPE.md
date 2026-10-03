# Shape: Backend architecture with the worker, Q-11 of the MVP plan

Document state: 2026-10-04, interview in progress
Regulator: C:40

## Problem

`plans/mvp/MVP_PLAN.md` cannot be closed, and `plan-implement` cannot start on it, while Q-11 is open: it is the only open question of that plan and its critical path (`plans/mvp/MVP_PLAN.md`, section Risks). Q-11 decides what the settled decisions D-3 - D-12 of that plan leave to the backend architecture: how the one backend process is started, how the worker and its periodic task run, where the import and refresh run executes, how the route computation is fed when the copy in use changes, where each process runs on the server of the demo, the names of the modules and functions the finished initiatives left open, and the structure that implements the operations of `docs/product/api_contract.md` (seed). The Kraków submission closes at 11:00 on 4 October 2026.

## Recipient and trigger

- Recipient: the members of the team who build the work packages of `plans/mvp/` - the import, the route, the voting, the accounts, the moderation and the address search - which put their code into the structure decided here; the work package of D-7 of `plans/mvp/MVP_PLAN.md`, which names the files of the Alembic configuration inside the backend skeleton; and the task `DEPLOYMENT` of `plans/deployment/`, whose trigger is Q-11 decided and the first backend code written (`plans/deployment/DEPLOYMENT_SHAPE.md`, section Recipient and trigger).
- Owner: the backend person (`plans/mvp/MVP_PLAN.md` Q-11). Answers the user gives in this interview are recorded as given by the user for the backend person, as in the finished initiatives of the same owner, until the backend person confirms them.
- Trigger: the request of the user on 2026-10-03 (seed).

## Current state

- No backend code exists: there is no `api/`, `service/`, `data/`, `worker/` or `backend/` directory in the repository, and `tests/` holds only architecture tests (checked by the agent on 2026-10-03; `plans/mvp/MVP_PLAN.md` F-3).
- The backend is Python 3.13 with FastAPI on PostgreSQL with PostGIS, and the Python profile of the standards stays in force (`plans/mvp/MVP_PLAN.md` D-1).
- The standards already fix the outline of the backend. The service has an input layer, a rules layer and a data layer with a one-way dependency (`docs/standards/standard_architecture.md`, section Layer boundary). The layer directories `api`, `service`, `data` and `worker` sit in the repository root (`docs/standards/standard_naming.md`, section File names). The worker is a second entry point of the same image, not a separate service; it has one registry of periodic tasks in the rules layer and a database lock for every task (`docs/standards/standard_worker.md`, sections One process, one task registry and Locks).
- The backend that answers the address search runs as exactly one process, because the cache and the rate gate of the search live in its memory (`plans_finished/geocoding/GEOCODING_PLAN.md` D-15).
- The route graph is built in the memory of that process when it starts and rebuilt there when the instant of the copy in use changes (`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-3, in force as D-9 of `plans/mvp/MVP_PLAN.md`). `plans/valhalla_routing/VALHALLA_ROUTING_SHAPE.md`, with its interview closed and no PRD, proposes replacing that graph with Valhalla run by the project as a separate service.
- The import and refresh run is an administrative run started by a member of the team, never by request handling and never on a schedule, with a database lock that skips a second trigger; the form of its trigger and the machine it runs on are left to Q-11 (`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-11). One run took 297 - 377 seconds with a peak of 980 MB of memory on the machine of the agent's session, and the downloaded file of 202 232 967 bytes is deleted after the run (F-11, D-14 there).
- The periodic task of the worker clears `voter_hash` 30 days after `cast_at` (`docs/product/schema.md`, section Who writes what). The specification says the hash "is deleted 30 days after the vote" (`docs/product/specification.md`, line 197), and AC-4 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` says "No identifier of a vote exists 30 days after the vote was cast, while the vote still counts."
- The demo runs on the virtual private server of the db person, with 4 GB of free memory, 64 GB of free disk and 4 cores after the other services of its owner (`plans/mvp/MVP_PLAN.md` D-10, `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8). An uncommitted change of `plans/deployment/DEPLOYMENT_SHAPE.md` of 2026-10-03 records that the demo moves to another server, owned by the user and standing in a data centre, with 16 GB of memory and 16 cores, and that everything of the demo that can run in Docker containers runs in them.
- The page, the programming interface and the map tiles are served from one host (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-3, in force as D-6 of `plans/mvp/MVP_PLAN.md`).
- The implementation of the operations of `docs/product/api_contract.md` goes with Q-11 (`plans_finished/api_contract/API_CONTRACT_PLAN.md` D-1).

## Smallest meaningful scope

Following from the seed, the items Q-11 lists:

1. How the one backend process is started.
2. The form of the trigger of the import and refresh run and the machine it runs on.
3. How the route computation gets the copy in use when the backend process starts and when the copy changes.
4. The placement of the backend process, the worker, PostgreSQL with PostGIS and the static frontend on the server of the demo.
5. The periodic task of the worker that clears the hash of a vote without an account.
6. The names of the modules and functions of the address search and of the tag rule, left open by `plans_finished/geocoding/GEOCODING_PLAN.md` D-2 and `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-14 and D-16.
7. The structure that implements the operations of `docs/product/api_contract.md`.

Items 3 and 4 wait for the decision of `plans/valhalla_routing/`, because Valhalla, if adopted, replaces the graph of item 3 and adds a service to the placement of item 4; the other items are decided first. Decided by the user for the backend person on 2026-10-03, answering question 2.

The initiative delivers only these decisions, recorded in documents. Decided by the user for the backend person on 2026-10-03, answering question 1, against the decisions together with the backend skeleton and against the decisions, the skeleton and the implementation of every operation of `docs/product/api_contract.md`.

## Out of scope

- Any code, the backend skeleton included: the layer directories, the two entry points and the Alembic configuration are built by the work packages of `plans/mvp/`, the skeleton by the work package of D-7 there. Decided by the user on 2026-10-03, answering question 1.
- The implementation of the operations of `docs/product/api_contract.md`. It goes to the work packages of `plans/mvp/`, not to this initiative, which departs from `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-1, where "the implementation of the operations goes with it", meaning with Q-11. Decided by the user on 2026-10-03, answering question 1; the archived plan keeps its wording as history (`docs/standards/standard_agentic_workflow.md` ch. 4.6).

## Functional requirements

1. Every item of the section Smallest meaningful scope is decided and recorded in the plan of this initiative, so that Q-11 of `plans/mvp/MVP_PLAN.md` closes with a decision that names this initiative, as D-3 - D-12 there name theirs.
2. The documents in force that hand the implementation of the operations to Q-11 - D-12 of `plans/mvp/MVP_PLAN.md`, which says "the implementation of the operations goes with Q-11" - hand it to the work packages of `plans/mvp/` instead. Agent decision at C:40, without asking: a consequence of the answer to question 1.
3. D-10 of `plans/mvp/MVP_PLAN.md` names the server of the user in a data centre, with 16 GB of memory and 16 cores and the demo in Docker containers, in place of the virtual private server of the db person, and records that the user decided the move for the db person, who owns D-10. The archived `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8 keeps its wording as history. Decided by the user on 2026-10-04, answering question 6, against leaving the update to the task `DEPLOYMENT` and against leaving it to the db person.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Is Q-11 a shape at all, when almost every item of it is technical? Most items - how the process starts, the form of the trigger, the names of modules - are decisions of phase B of `plan-prd`, and the names follow `docs/standards/standard_naming.md`. The shape asks only about the scope, about the inputs that two sources describe differently, and about the rules that touch a blocking risk category.
- Does waiting for `plans/valhalla_routing/` move the critical path of the MVP plan? Yes: Q-11 closes only with items 3 and 4 decided, so the MVP plan now closes no earlier than the routing decision. The user chose this knowingly on 2026-10-03 (question 2); the cost is that a delay of that decision is a delay of every work package of `plans/mvp/`.
- Does "only decisions" leave the backend skeleton without an executor? Not without one, but without a date: the skeleton is built by a work package of `plans/mvp/`, and that plan has no work packages until it closes (`plans/mvp/MVP_PLAN.md`, sections Scope of changes and Rollout order are empty). The task `DEPLOYMENT`, whose trigger is the first backend code, therefore waits for Q-11, for the closing of the MVP plan and for the first work package.
- Does the periodic task of item 5 ever clear anything in the demo? No: the demo and all its data are deleted on 4 October 2026 (`CLAUDE.md`, section Target environment), so no vote reaches 30 days in it. The task is still required by the specification and by AC-4, so it is shown by a test, not by the demo.

## Domain rules or explicit TODO

- Q-11 plans for the server of the user in a data centre, with 16 GB of memory and 16 cores, where everything of the demo that can run in Docker containers runs in them, as the uncommitted change of `plans/deployment/DEPLOYMENT_SHAPE.md` of 2026-10-03 records. Decided by the user for the backend person on 2026-10-03, answering question 3, against the virtual private server of the db person of D-10 of `plans/mvp/MVP_PLAN.md` and against leaving the server open. D-10 there and `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8 still name the virtual private server of the db person; what else runs on the new server and how much disk is free is not known (`plans/deployment/DEPLOYMENT_SHAPE.md`, section Current state), so the narrow hosted demo environment of `CLAUDE.md`, section Target environment, applies to it unchanged.

## Notes on data, performance and security

## Open questions

2. Which routing does Q-11 plan for: the graph in the memory of the backend process of D-9 of `plans/mvp/MVP_PLAN.md`, still in force, or Valhalla of `plans/valhalla_routing/`, whose interview is closed but which is not decided? Signal 1: the two sources say different things about the target state. On 2026-10-03 the user answered that items 3 and 4 of the section Smallest meaningful scope wait for the decision of `plans/valhalla_routing/`, and that the other items are decided now, against planning for D-9 with Valhalla taking item 3 over if adopted and against planning for Valhalla at once. The question stays open until that decision. `Block: no`
4. Does the import and refresh run execute on the server of the demo, or on a team machine writing to the database of the demo over the network, so that the database accepts connections from outside the server and an account able to write the OpenStreetMap tables is held outside it? `Block: yes` (category: read visibility and permissions)
5. When exactly is the hash of a vote without an account cleared: so that none exists 30 days after the vote, as AC-4 reads, which means the task clears it a little before the 30 days pass; or at the first run of the task after the 30 days pass, so that it exists up to 30 days plus the interval of the task? `Block: yes` (category: personal data)
