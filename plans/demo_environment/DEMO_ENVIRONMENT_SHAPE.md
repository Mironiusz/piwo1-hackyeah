# Shape: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) is demonstrated live on 4 October 2026 and recorded on video. Where it runs during the demo - a team laptop or a hosted service - was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it. The choice also fills the open entry Target environment for the demo in `docs/standards/decision_registry.md`, on which the permission levels of the agent in `CLAUDE.md` and `AGENTS.md`, section Target environment, depend.

## Recipient and trigger

- The owner of the decision is the db person of the team, as the role closest to the infrastructure; the backend person is consulted, because the service runs there. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-7, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- `CLAUDE.md`, section Target environment: until the environment is chosen and the three permission levels are filled in, the agent has no access to any target environment, and deployment is done by a human. No address, host, login or secret of the target environment enters the repository (`docs/standards/standard_config.md`).
- The Kraków brief says the prototype does not have to stay online after the hackathon, and asks for a proposal of who hosts, updates, secures and pays for the service (`docs/hackathon/challenge_requirements.md`, Technical and organizational requirements).
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: a decision on where the demo runs, taken by the right people. Whether this initiative also prepares that environment is open (question 1).

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`. The hosting part of the business model in the Kraków presentation is a deliverable outside the app.

## Functional requirements

1. The main scenario of `plans/mvp/MVP_PRD.md` works in the chosen environment during the live demo and the video.
2. The demo shows a source being unavailable (FR-17, AC-16) in a way the environment allows.
3. The three permission levels of the agent in `CLAUDE.md` and `AGENTS.md`, section Target environment, are filled in together with the choice.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Does the jury need a link to a running app, or is a demo from a laptop enough? The brief lists a demo link as optional (`docs/hackathon/challenge_requirements.md`, Formal deliverables); it is still to be confirmed with the team (question 2).
- Is the environment a technical choice only? No: real people may create accounts and votes in a hosted demo, which brings personal data and its protection into play (question 3).

## Domain rules or explicit TODO

- Kept personal data: the pseudonym and password of an account and the 30-day identifier of a vote without an account (`docs/product/specification.md`, section Personal data).

## Notes on data, performance and security

- The Kraków brief asks for secure connections and basic data protection (`docs/hackathon/challenge_requirements.md`, Technical and organizational requirements).
- Secrets and target environment details never enter the repository (`docs/standards/standard_config.md`, section Secrets).

## Open questions

1. Does the initiative end with the recorded decision and the permission levels, or does it also prepare the environment? `Block: no`
2. Does the submission need a public link to a running app, or a laptop demo and the video only? `Block: no`
3. Will people outside the team create accounts or votes in the demo environment, and who is responsible for that data and its deletion after the hackathon? `Block: yes` (category: personal data)
4. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
