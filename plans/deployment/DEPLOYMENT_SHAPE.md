# Shape: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed carries no regulator value, so the default C:40 applies.

## Problem

The hosted demo of `plans/mvp/` needs a deployment configuration and written instructions in the repository, a secure connection, and a way to make the routing service unreachable during the live demo. All three need the skeleton of the app: the configuration names how the service and the worker start, which `plans/mvp/MVP_PLAN.md` decides in Q-11 only after its Q-7 - the choice of the demo environment - is closed. Kept inside the task `DEMO_ENVIRONMENT`, this work made that task wait for Q-11 while Q-11 waited for it. The backend architecture with the worker was part of Q-10 of that plan when this task was split out, and moved to Q-11 when Q-10 was narrowed to the domain model on 2026-10-03. On 2026-10-03 the user split it out into this task to cut that loop. Later on 2026-10-03 the user moved this task out of the initiative `demo_environment` into an initiative of its own, so that `demo_environment` could be archived with its task `DEMO_ENVIRONMENT` finished (`plans_finished/demo_environment/DEMO_ENVIRONMENT_REVIEW.md`, entry Initiative closed).

## Recipient and trigger

- The recipient is the db person of the team, who stands the hosted environment up using what this task delivers (`plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, section Out of scope).
- The owner of this task is the db person, as the owner of the whole initiative. Agent decision at C:40, without asking: the task was split out of a task the db person owns, and the user named no other owner.
- Trigger: the skeleton of the app exists in `plans/mvp/` - Q-11 of `plans/mvp/MVP_PLAN.md` is decided and the first backend code is written - and the hosting is chosen in the task `DEMO_ENVIRONMENT`.

## Current state

- No product code exists (`plans/mvp/MVP_PLAN.md`, F-3). The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- The hosting was chosen on 2026-10-03 (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8): the virtual private server of the db person, with 4 GB of free memory, 64 GB of free disk and 4 cores after the other services of its owner, reached at its IP address because no domain points at it; the team may buy one later. Without a domain the secure connection of requirement 2 uses a Let's Encrypt certificate for the IP address, valid for 160 hours and validated only through port 80 or 443 (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` F-12, F-13). Whether these ports are free of the services of the owner is not known, so this task chooses between the demo answering on them itself and a proxy of the owner that only the db person configures. Agent decision at C:40, without asking: the item replaces the one saying the hosting was not chosen, which D-8 made untrue.
- The seed refers to requirements by their numbers in `plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md` at the moment of the question: FR-2 the deployment configuration and written instructions, FR-3 the secure connection, FR-4 the unavailable source in the live demo. After the split that PRD was renumbered, and these three no longer stand in it.
- Decisions of the task `DEMO_ENVIRONMENT` this task inherits (`plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`): the demo runs on a hosted service at a public link given in the HackTribe submission, and the live demo runs from it; the db person stands the environment up; the owner of the repository deletes it on 4 October 2026, after the results, without keeping a copy of the data; no address, host, login or secret of the hosting enters the repository.
- Written instructions for deleting the environment were proposed by the agent and cut by the user at the PRD gate of `DEMO_ENVIRONMENT` on 2026-10-03.
- The deployment configuration has to serve the static frontend decided in `plans_finished/frontend_stack/` on 2026-10-03, with its tile archive read in byte ranges, from the same host as the programming interface (`plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, Current state, last item).
- `plans_finished/local_database/` decided on 2026-10-03 (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-1, D-3, D-5, D-7) that the local database is PostgreSQL 18.6 with PostGIS 3.6.4 and the files of pgRouting 4.0.1 in a project image started by Docker Compose, and that the first schema revision, applied by the schema owner account, creates PostGIS. The same chain of revisions runs on the hosted database of the demo, so there too the account that applies them is a superuser, because PostGIS is not a trusted extension. The server of the demo also runs other services of its owner (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-3): if its PostgreSQL instance also holds their databases, that account can read and drop them. How the hosted database is separated from them is for this task to decide; `plans_finished/local_database/` only hands the consequence over.
- `plans_finished/geocoding/` decided on 2026-10-03 (`plans_finished/geocoding/GEOCODING_PLAN.md` D-15, D-16) that the backend which answers the address search runs as exactly one process, because its cache and its gate of one request per 1.1 seconds to the public Nominatim instance live in the memory of that process, and that after the first deployment one search from the hosted service is checked to return a list, because a hosting address shared with other customers may be blocked by that instance. The deployment configuration starts the service with one process and does not scale it automatically. Added on 2026-10-03 by `plans_finished/consistency_check/`.
- `plans_finished/routing_engine/` decided on 2026-10-03 (`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-1, D-3, D-13) that routes are computed by a graph in the memory of the backend process, with no routing service of its own and none outside the project. Routing stops answering only when the graph cannot be built - no copy in the database, or a failed build - or when a read of the stored network or facts fails or times out; the app then shows the plain message of FR-17 of `plans/mvp/MVP_PRD.md`. How the live demo provokes that and undoes it, for functional requirement 3 of this shape, is for this task; `plans_finished/routing_engine/` decides no switch for it.

- At the review of this shape on 2026-10-03, after 22:00, the trigger is not met: Q-11 of `plans/mvp/MVP_PLAN.md` is open, no product code exists on `dev` or on any remote branch, and neither `frontend/` nor a backend directory exists (`git fetch` and `git branch -a` on 2026-10-03, `dev` at `33a9ce7`).
- `docs/product/specification.md`, section on the demo, requires the demo to show what the user sees when a source is unavailable: "when the routing service does not answer, a plain message and no guessed route". FR-17 and AC-16 of `plans/mvp/MVP_PRD.md` use the same words. `plans_finished/routing_engine/` decided later that day that no routing service exists, so "the routing service does not answer" now means the cases of D-3 of that plan listed in the previous items; the specification and the MVP PRD were not reworded after it.

- Later on 2026-10-03 the initiative `plans/valhalla_routing/` was opened, with its shape closed: it proposes replacing the own routing engine of `plans_finished/routing_engine/` with Valhalla, a routing service run by the project on the server of the demo, with optional public transport routes from the static GTFS of ZTP Kraków. It has no PRD or plan yet, and D-9 of `plans/mvp/MVP_PLAN.md` still names the own engine. If it is adopted, the deployment carries a second service with its tiles, and FR-3 again means making a routing service unreachable (question 6).

## Smallest meaningful scope

Following from the seed: the three requirements moved out of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`.

## Out of scope

- The choice of the hosting, the permission levels of the agent, recording the decision and the privacy information about the deletion - the task `DEMO_ENVIRONMENT`.
- Standing the environment up and deleting it - steps of the db person and of the owner of the repository.
- Written instructions for deleting the environment, cut by the user on 2026-10-03.

## Functional requirements

1. The repository holds the deployment configuration and written instructions with which a member of the team deploys the app of `plans/mvp/` to the chosen hosting and opens it at the public link on a phone, without help from the person who wrote them. No address, host, login or secret of the hosting is in the repository.
2. The public link is served over a secure connection: the Kraków brief asks for secure connections, and browsers give a page the current location, which FR-2 of `plans/mvp/MVP_PRD.md` uses as a start, only over a secure connection.
3. The chosen environment lets the team make routing stop answering during the live demo, so the case of FR-17 of `plans/mvp/MVP_PRD.md` can be shown, and bring it back afterwards. Reworded at the review on 2026-10-03: it said "make the routing service unreachable", and no routing service exists (`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-1).

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Can the configuration be written before the app exists? No: it names how the service and the worker start, which `plans/mvp/` decides in Q-11. That is the reason this task exists separately.
- Does the trigger come in time? At the review, after 22:00 on 3 October 2026, Q-11 is open and no code exists, so the configuration cannot be written yet and the night before 11:00 on 4 October 2026 is the whole window for the skeleton, the configuration, standing the environment up and checking the link (question 1).
- Is the hosted database automatically separate from the other services of the server? No: `plans_finished/local_database/` hands over that the account applying the revisions is a superuser, and if the demo shares a PostgreSQL instance with databases of the owner, that account can read and drop them, which `CLAUDE.md`, section Target environment, forbids the agent to touch unconditionally (question 2).
- Is the scene of FR-3 harmless for the jury? Routing lives in the one backend process (`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-1, `plans_finished/geocoding/GEOCODING_PLAN.md` D-15), so while the team shows it, routing stops answering for everyone who has the public link open, the jury included (question 3).
- Does the deadline of 22:00 on 3 October 2026 from `plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md` bind this task? It was set while the configuration was part of that task, before it was known to wait for the skeleton of the app; whether it still holds is open (question 1).

## Domain rules or explicit TODO

- Kept personal data, its deletion on 4 October 2026 and the person responsible for it are those of `plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, section Domain rules; this task does not change them.

## Notes on data, performance and security

- Secrets and target environment details never enter the repository (`docs/standards/standard_config.md`, section Secrets).

## Open questions

1. By when must the deployment configuration and instructions be ready, given that they wait for the skeleton of the app and that the Kraków submission closes at 11:00 on 4 October 2026, and what happens if the skeleton is not there by then? `Block: no`
2. Does the hosted database of the demo run in a PostgreSQL instance of its own, or in an instance that also holds databases of the owner of the server? `Block: yes` (category: read visibility and permissions)
3. How long may routing stay down for everyone during the scene of FR-3, and must it be shown on the hosted link at all, given that the specification requires the demo to show it? `Block: no`
4. Are ports 80 and 443 of the server free, or does a proxy of the owner already answer on them? Fact to be stated by the db person; it decides whether the secure connection of FR-2 is possible (`plans_finished/demo_environment/DEMO_ENVIRONMENT_REVIEW.md` R-5). `Block: no`
5. Do updates deployed during the night keep the data already in the hosted database, and is filling the database with the OpenStreetMap copy and serving the tile archive part of the written instructions? `Block: no`
6. Which routing does this task deploy: the own engine of `plans_finished/routing_engine/`, still in force as D-9 of `plans/mvp/MVP_PLAN.md`, or Valhalla of `plans/valhalla_routing/`, whose shape is closed but not yet decided? Signal 1: the two sources say different things about the target state. `Block: no`
