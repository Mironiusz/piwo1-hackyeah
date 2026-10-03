# Shape: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed carries no regulator value, so the default C:40 applies.

## Problem

The hosted demo of `plans/mvp/` needs a deployment configuration and written instructions in the repository, a secure connection, and a way to make the routing service unreachable during the live demo. All three need the skeleton of the app: the configuration names how the service and the worker start, which `plans/mvp/MVP_PLAN.md` decides in Q-11 only after its Q-7 - the choice of the demo environment - is closed. Kept inside the task `DEMO_ENVIRONMENT`, this work made that task wait for Q-11 while Q-11 waited for it. The backend architecture with the worker was part of Q-10 of that plan when this task was split out, and moved to Q-11 when Q-10 was narrowed to the domain model on 2026-10-03. On 2026-10-03 the user split it out into this task to cut that loop.

## Recipient and trigger

- The recipient is the db person of the team, who stands the hosted environment up using what this task delivers (`DEMO_ENVIRONMENT_SHAPE.md`, section Out of scope).
- The owner of this task is the db person, as the owner of the whole initiative. Agent decision at C:40, without asking: the task was split out of a task the db person owns, and the user named no other owner.
- Trigger: the skeleton of the app exists in `plans/mvp/` - Q-11 of `plans/mvp/MVP_PLAN.md` is decided and the first backend code is written - and the hosting is chosen in the task `DEMO_ENVIRONMENT`.

## Current state

- No product code exists (`plans/mvp/MVP_PLAN.md`, F-3). The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- The hosting is not chosen yet; its choice is FR-1 of `DEMO_ENVIRONMENT_PRD.md`.
- The seed refers to requirements by their numbers in `DEMO_ENVIRONMENT_PRD.md` at the moment of the question: FR-2 the deployment configuration and written instructions, FR-3 the secure connection, FR-4 the unavailable source in the live demo. After the split that PRD was renumbered, and these three no longer stand in it.
- Decisions of the task `DEMO_ENVIRONMENT` this task inherits (`DEMO_ENVIRONMENT_SHAPE.md`): the demo runs on a hosted service at a public link given in the HackTribe submission, and the live demo runs from it; the db person stands the environment up; the owner of the repository deletes it on 4 October 2026, after the results, without keeping a copy of the data; no address, host, login or secret of the hosting enters the repository.
- Written instructions for deleting the environment were proposed by the agent and cut by the user at the PRD gate of `DEMO_ENVIRONMENT` on 2026-10-03.
- The deployment configuration has to serve the static frontend decided in `plans/frontend_stack/` on 2026-10-03, with its tile archive read in byte ranges, from the same host as the programming interface (`DEMO_ENVIRONMENT_SHAPE.md`, Current state, last item).

## Smallest meaningful scope

Following from the seed: the three requirements moved out of `DEMO_ENVIRONMENT_PRD.md`.

## Out of scope

- The choice of the hosting, the permission levels of the agent, recording the decision and the privacy information about the deletion - the task `DEMO_ENVIRONMENT`.
- Standing the environment up and deleting it - steps of the db person and of the owner of the repository.
- Written instructions for deleting the environment, cut by the user on 2026-10-03.

## Functional requirements

1. The repository holds the deployment configuration and written instructions with which a member of the team deploys the app of `plans/mvp/` to the chosen hosting and opens it at the public link on a phone, without help from the person who wrote them. No address, host, login or secret of the hosting is in the repository.
2. The public link is served over a secure connection: the Kraków brief asks for secure connections, and browsers give a page the current location, which FR-2 of `plans/mvp/MVP_PRD.md` uses as a start, only over a secure connection.
3. The chosen environment lets the team make the routing service unreachable for the app during the live demo, so the case of FR-17 of `plans/mvp/MVP_PRD.md` can be shown, and bring it back afterwards.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Can the configuration be written before the app exists? No: it names how the service and the worker start, which `plans/mvp/` decides in Q-11. That is the reason this task exists separately.
- Does the deadline of 22:00 on 3 October 2026 from `DEMO_ENVIRONMENT_SHAPE.md` bind this task? It was set while the configuration was part of that task, before it was known to wait for the skeleton of the app; whether it still holds is open (question 1).

## Domain rules or explicit TODO

- Kept personal data, its deletion on 4 October 2026 and the person responsible for it are those of `DEMO_ENVIRONMENT_SHAPE.md`, section Domain rules; this task does not change them.

## Notes on data, performance and security

- Secrets and target environment details never enter the repository (`docs/standards/standard_config.md`, section Secrets).

## Open questions

1. By when must the deployment configuration and instructions be ready, given that they wait for the skeleton of the app and that the Kraków submission closes at 11:00 on 4 October 2026? `Block: no`
