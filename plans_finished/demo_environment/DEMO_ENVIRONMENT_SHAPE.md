# Shape: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03, interview closed
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) is demonstrated live on 4 October 2026 and recorded on video. Where it runs during the demo - a team laptop or a hosted service - was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it. The choice also fills the open entry Target environment for the demo in `docs/standards/decision_registry.md`, on which the permission levels of the agent in `CLAUDE.md` and `AGENTS.md`, section Target environment, depend.

## Recipient and trigger

- The owner of the decision is the db person of the team, as the role closest to the infrastructure; the backend person is consulted, because the service runs there. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- The interview from 2026-10-03 on is answered by the user together with the db person, so its answers are decisions of the owner of the initiative.
- `plans/mvp/MVP_PLAN.md`, open question Q-7, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- `CLAUDE.md`, section Target environment: until the environment is chosen and the three permission levels are filled in, the agent has no access to any target environment, and deployment is done by a human. No address, host, login or secret of the target environment enters the repository (`docs/standards/standard_config.md`).
- The Kraków brief says the prototype does not have to stay online after the hackathon, and asks for a proposal of who hosts, updates, secures and pays for the service (`docs/hackathon/challenge_requirements.md`, Technical and organizational requirements).
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- What the hosting has to carry depends on two other initiatives: `plans_finished/routing_engine/` decides whether a routing engine runs on our own server or an external service is used, and `plans_finished/frontend_stack/` decides whether the frontend is static or rendered on the server. Neither was decided when this interview was held; the frontend was decided later on 2026-10-03 (next item), and the routing engine is still in its interview.
- `plans_finished/frontend_stack/` decided on 2026-10-03 (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-3, D-5, D-6, D-13) that the frontend is static files and nothing is rendered on the server. The hosting stores about 50 MB for it: one archive of map tiles of 34.8 MB, map fonts and sprites of 11.2 MB, and the built page of a few megabytes. The server has to answer byte range requests for the tile archive, and the page, the programming interface and the tiles have to be served from one host.
- `plans_finished/geocoding/` decided on 2026-10-03 (`plans_finished/geocoding/GEOCODING_PLAN.md` D-1, D-15, D-16) that the backend calls the public Nominatim instance from the hosted service and runs as exactly one process, and that after the first deployment one search from the hosted service is checked to return a list, because a hosting address shared with other customers may be blocked by that instance. Step 6 of that plan, skipped on 2026-10-03 because this initiative was then being written in another session, added on 2026-10-03 by `plans_finished/consistency_check/`.

## Smallest meaningful scope

Following from the seed: a decision on where the demo runs, taken by the right people. The team decided on 2026-10-03 that the demo runs on a hosted service reachable at a public link, that the live demo uses the same hosted service, not a team laptop, and that the initiative ends with the choice of the hosting, the permission levels of the agent, and the deployment configuration with written instructions in the repository; standing the environment up is outside it. On 2026-10-03, in phase B of `plan-prd`, the user moved the deployment configuration with the instructions, the secure connection and the unavailable source out to the task `DEPLOYMENT` of this initiative (section Out of scope); this task keeps the choice of the hosting, the permission levels, recording the decision and the privacy information.

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans_finished/api_contract/`, `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans_finished/account_sessions/`. The hosting part of the business model in the Kraków presentation is a deliverable outside the app.

Standing the hosted environment up - creating the account with the hosting provider, the first deployment, and checking the main scenario at the public link before the submission - was taken out of this initiative by the team on 2026-10-03. The initiative delivers what that work needs; the db person does the work, outside this initiative, as decided by the team on 2026-10-03.

The deployment configuration with the written instructions, the secure connection and showing an unavailable source in the live demo moved to the task `DEPLOYMENT` of this initiative (`plans/deployment/DEPLOYMENT_SEED.md`), decided by the user on 2026-10-03 in phase B of `plan-prd`. Reason: the configuration names how the service and the worker start, which `plans/mvp/MVP_PLAN.md` decides in Q-11 only after its Q-7 is closed by this task, so keeping it here made each wait for the other. At the time of the split that question was Q-10, which was narrowed to the domain model later on 2026-10-03. Scenarios 1 and 3 below are served by that task.

## Functional requirements

1. The three permission levels of the agent in `CLAUDE.md` and `AGENTS.md`, section Target environment, are filled in together with the choice, as decided in the section Domain rules.
2. The decision lands where people look for it: the entry Target environment for the demo in `docs/standards/decision_registry.md` moves to the resolved section, and Q-7 of `plans/mvp/MVP_PLAN.md` is closed. This follows from the rules of the registry, section How to use it.
3. The privacy information page of the hosted demo states, in Polish and English, that the demo and all its data are deleted on 4 October 2026, after the results are announced. Decided by the team on 2026-10-03. The page itself is built in `plans/mvp/`, so this extends FR-20 and AC-19 of `plans/mvp/MVP_PRD.md`, whose gate was already passed; the extension has to be raised there, not applied silently.

## Scenarios: input, flow, expected state after the run

1. Setup from the instructions. Input: the deployment configuration and the written instructions in the repository, and an account with the hosting provider created by the db person. Flow: the db person follows the instructions alone, deploys the app and opens the public link on a phone. State after: the main scenario works at the link, the link can go into the HackTribe submission, and no address, host, login or secret of the hosting entered the repository.
2. The jury tries the app. Input: the public link from the submission. Flow: at 10:30 on 4 October a jury member opens the link on a phone, picks a preset, plans a route, creates an account and reports stairs. State after: the hosted database holds the pseudonym, the password and the report; the privacy page told the jury member, in the language of the browser, that the demo and all its data are deleted on 4 October 2026.
3. A source is unavailable during the live demo. Input: the hosted app during the presentation. Flow: the team makes the routing service unreachable in a way the chosen environment allows and plans a route. State after: the app shows the plain message and no route (FR-17, AC-16); after the routing service is reachable again, routes are planned as before.
4. The agent during the night. Input: requests of the team between the first deployment and the results. Flow: at 02:00 the app answers with errors and the agent reads the logs of the hosted service without asking; at 02:30 the team asks the agent to deploy a fixed version and it does; at 03:00 someone asks the agent to delete the database or to change the database password in the hosting, and it refuses both despite the explicit request. State after: the fixed version runs, the database and the secrets are unchanged.
5. Deletion after the results. Input: the results announced on 4 October 2026. Flow: the owner of the repository deletes the hosted service and its database, without taking a copy. State after: the link does not answer, and no personal data of people outside the team remains with the team, in the hosting or in the repository.

## Challenging own assumptions

- Does the jury need a link to a running app, or is a demo from a laptop enough? The brief lists a demo link as optional (`docs/hackathon/challenge_requirements.md`, Formal deliverables). The team chose a public link on 2026-10-03, so the jury can try the app on its own; the cost is that anyone who gets the link can create accounts and votes.
- Is the environment a technical choice only? No: real people create accounts and votes in a hosted demo, which brings personal data and its protection into play. The team settled who is responsible for that data, how long it lives and what the privacy page says about it (section Domain rules, requirement 3).
- Does "the agent may do anything on request" leave the level forbidden unconditionally empty? The team named two things for it: deleting the environment, which stays with the owner of the repository, and changing the secrets of the hosting.
- Can this initiative meet 22:00 on its own? No: the hosting has to carry whatever `plans_finished/routing_engine/` and `plans_finished/frontend_stack/` choose, so the deadline holds only if both are decided earlier that evening. If they are not, the choice of the hosting here is a guess about their contract, which the rules of the repository forbid; the deadline then moves, it is not met with a guess.
- Does a decision alone get the demo online? No: a recorded choice without anyone standing the environment up leaves the public link without an executor. The team gave that work to the db person, outside this initiative.

## Domain rules or explicit TODO

- Kept personal data: the pseudonym and password of an account and the 30-day identifier of a vote without an account (`docs/product/specification.md`, section Personal data).
- Anyone who gets the public link can create accounts, reports and votes, so the hosted database holds personal data of people outside the team, jury members included.
- The hosted service and its database are deleted on 4 October 2026, after the results are announced, and no copy of the data is kept. Decided by the team on 2026-10-03. The data therefore lives less than a day, and the 30-day deletion of vote identifiers never has to run in this environment.
- The owner of the repository is responsible for the personal data in the hosted demo and deletes the service and the database on 4 October 2026. Decided by the team on 2026-10-03.
- Permission levels of the agent in the hosted demo environment, decided by the team on 2026-10-03: without asking, the agent reads the logs of the hosted service, next to the repository and local tools; on an explicit request, the agent may do anything in that environment except what is forbidden; forbidden unconditionally, even on explicit request: deleting the hosted service or its database, and changing the secrets of the hosting. Reading personal data from the demo database is therefore allowed on an explicit request. The ban on bringing any address, host, login or secret of the target environment into the repository stays in force regardless (`docs/standards/standard_config.md`).
- The db person stands the environment up, and the owner of the repository deletes it. So the owner of the repository gets access to the hosting account that is enough to delete the service and the database already when the environment is stood up, not only on 4 October 2026. Agent decision at C:40, without asking: it follows from the two decisions above, and without it the deletion has no one able to perform it.
- The choice of the hosting and the deployment configuration with the instructions are ready in the repository by 22:00 on 3 October 2026, so the night is left for standing the environment up, checking the link, the video and fixes. Decided by the team on 2026-10-03. After the split the deadline binds the choice of the hosting here; whether it still binds the configuration is an open question of the task `DEPLOYMENT`.

## Notes on data, performance and security

- The Kraków brief asks for secure connections and basic data protection (`docs/hackathon/challenge_requirements.md`, Technical and organizational requirements).
- Browsers give a page the current location, which FR-2 of `plans/mvp/MVP_PRD.md` uses as a start, only over a secure connection, so the public link is served over HTTPS. Agent decision at C:40, without asking: it follows from FR-2 and from the brief above.
- Secrets and target environment details never enter the repository (`docs/standards/standard_config.md`, section Secrets).
- Logs of a hosting platform usually hold the IP addresses of visitors, jury members included. The agent reads them without asking, so that personal data reaches the context of the model without a request each time. The agent named this risk to the team on 2026-10-03, and the team kept logs at the level without asking.

## Open questions

None.
