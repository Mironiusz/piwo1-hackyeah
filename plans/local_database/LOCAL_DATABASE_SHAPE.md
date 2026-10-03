# Shape: Choice of the local PostgreSQL environment with PostGIS for the MVP

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The backend of the MVP runs on PostgreSQL with PostGIS (`plans/mvp/MVP_PLAN.md` D-1), and the standards require code that touches the database to have critical tests against a real database. How each member of the team gets such a database locally was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the db person of the team. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-4, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code and no database schema exist.
- On 2026-10-03, on the machine of the agent's session: a local PostgreSQL 18 installation exists, but it did not answer on port 5432, no Windows service for it was found, and its extension directory has no PostGIS; the Docker client 29.6.1 is installed, but the Docker Desktop engine was not running.
- `docs/standards/standard_database.md`: every schema change is an Alembic revision with raw SQL; permissions are granted in revisions; the database is created with the builtin locale provider and the locale `C.UTF-8`, which requires PostgreSQL 17 or newer; a schema change never happens on its own at startup.
- `docs/standards/standard_tests.md`: a critical test runs against the local database, and a session with a critical test refuses to start when the configuration points to the target environment.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: a decision on how the team gets a local PostgreSQL with PostGIS, taken by the right people. Whether this initiative also prepares the setup instructions and scripts is open (question 1).

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/geocoding/`, `plans/account_sessions/`. The database of the demo environment is `plans/demo_environment/`.

## Functional requirements

1. Every member of the team who writes backend code can run the critical tests against a real PostgreSQL with PostGIS.
2. The setup satisfies `docs/standards/standard_database.md` (locale, revisions, permissions) and `docs/standards/standard_config.md` (environment entries without secrets in the repository).
3. The Huawei challenge scores a build from the README alone (`docs/hackathon/challenge_requirements.md`, Judging of Challenge 2), so the setup is reproducible from written instructions.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Is a local database per person needed at all, or would one shared database serve the team faster? A shared database changes who may write to it and turns the setup into an operation on a shared database, which is a human step (question 2).
- Is enabling PostGIS only an environment matter? No: creating the extension is a schema change and, under `docs/standards/standard_database.md`, an Alembic revision, which needs a database account allowed to create it (question 3).

## Domain rules or explicit TODO

- A schema change never happens on its own at environment startup (`docs/standards/standard_database.md`, Form of schema changes).

## Notes on data, performance and security

- Real personal data in a local database is allowed, but nothing from it leaves the machine (`docs/standards/standard_security.md`, Real personal data in the local environment).
- Database credentials are secrets and live only in the local environment files (`docs/standards/standard_config.md`).

## Open questions

1. Does the initiative end with the recorded decision handed to `plans/mvp/MVP_PLAN.md` Q-4, or does it also deliver the setup instructions and scripts? `Block: no`
2. Does every member of the team run their own local database, or does the team share one? `Block: no`
3. Which database account creates the PostGIS extension in the first revision, and which accounts does the service use afterwards? `Block: yes` (category: form of a schema change)
4. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
