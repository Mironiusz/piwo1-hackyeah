# Shape: Choice of the local PostgreSQL environment with PostGIS for the MVP

Document state: 2026-10-03, interview closed
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The backend of the MVP runs on PostgreSQL with PostGIS (`plans/mvp/MVP_PLAN.md` D-1), and the standards require code that touches the database to have critical tests against a real database. How each member of the team gets such a database locally was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the db person of the team. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-4, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.
- The answers of this interview are given by the user, who has not stated being the db person; they remove the questions from the list, but the ruling of the db person is still to be confirmed, as in `plans/fact_schema/`.
- Consumers of the decision: the work package of `plans/mvp/` that builds the local setup, and `plans/fact_schema/`, whose first schema revision runs on the database this decision describes.

## Current state

- No product code and no database schema exist.
- On 2026-10-03, on the machine of the agent's session: a local PostgreSQL 18 installation exists, but it did not answer on port 5432, no Windows service for it was found, and its extension directory has no PostGIS; the Docker client 29.6.1 is installed, but the Docker Desktop engine was not running.
- `docs/standards/standard_database.md`: every schema change is an Alembic revision with raw SQL; permissions are granted in revisions; the database is created with the builtin locale provider and the locale `C.UTF-8`, which requires PostgreSQL 17 or newer; a schema change never happens on its own at startup.
- `docs/standards/standard_tests.md`: a critical test runs against the local database, and a session with a critical test refuses to start when the configuration points to the target environment.
- The standards already separate two kinds of database account. `docs/standards/standard_database.md`, Form of schema changes: "The script creating the database and the accounts keeps to what a revision cannot do: the database itself and the accounts themselves." `docs/standards/standard_config.md`, Rule for assigning a value to a layer: the connection address of the schema owner account, used only when applying revisions, is read by `alembic/env.py` directly from the environment, because "the account that changes the schema has no right to sit in a layer that every service process imports".
- No environment template exists in the repository yet, and `docs/standards/standard_config.md`, section Environment entries, says "The template does not contain any entry yet." The `check` target of `makefile` does not run critical tests; a separate target for them is added together with the first such test.
- The first schema revision is built by `plans/fact_schema/` and waits for this initiative and for "a backend skeleton holding the Alembic configuration, which no plan has built yet" (`plans/fact_schema/FACT_SCHEMA_SHAPE.md`, section Smallest meaningful scope; `docs/standards/decision_registry.md`, Technical directions of the MVP plan).
- `plans_finished/routing_engine/` still considers pgRouting in the PostGIS database, a variant which "Requires an image with pgRouting" (`plans_finished/routing_engine/ROUTING_ENGINE_SEED.md`, agent question 1); that interview is in progress.
- The hosted database of the demo runs on a server of the db person and "has to meet the same database standard as the local one" (`plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-2, D-4; `plans/demo_environment/DEMO_ENVIRONMENT_PRD.md`, Dependencies).
- PostGIS is not a trusted extension, so only a superuser can create it: the control file of the `postgis` extension has no `trusted = true` line on the branches master, stable-3.5 and stable-3.4 of the PostGIS repository (`extensions/postgis/postgis.control.in`, read on 2026-10-03). Under PostgreSQL rules an extension not marked trusted is installed only by a superuser.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

A decision on how the team gets a local PostgreSQL with PostGIS, taken by the right people, recorded and handed to `plans/mvp/MVP_PLAN.md` Q-4. The initiative ends with the recorded decision; the setup itself is built by a work package of `plans/mvp/`, as with `plans_finished/geocoding/` and `plans_finished/osm_data_source/`. Decided by the user on 2026-10-03 (question 1), against also delivering the setup instructions and the script, and against delivering them together with the Alembic configuration.

The decision is recorded in the repository by 22:00 on 3 October 2026, the deadline the team set for the choice of the hosting in `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, which has the same owner. Decided by the user on 2026-10-03 (question 4), against 20:30 and against no deadline of its own, knowing that an earlier decision speeds up nothing downstream while `plans/mvp/MVP_PLAN.md` still waits for the routing engine and the frontend.

Every member of the team who runs critical tests has their own local database, not a shared one. Answered from the repository, not asked: `docs/standards/standard_tests.md`, section Test layers, status ready, says a critical test "may write and runs a durable seed, so it always goes against the local database" (question 2).

## Out of scope

- The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/geocoding/`, `plans/account_sessions/`. The database of the demo environment is `plans/demo_environment/`.
- The setup instructions in the README, the script creating the database and the accounts, the entries of the environment templates and the Alembic configuration: a work package of `plans/mvp/`, cut by the user on 2026-10-03 (question 1).
- A database shared by the team: ruled out by `docs/standards/standard_tests.md` (question 2).

## Functional requirements

The decision has to make these achievable for the work package of `plans/mvp/` that builds the setup:

1. Every member of the team who writes backend code can run the critical tests against their own local PostgreSQL with PostGIS.
2. The setup satisfies `docs/standards/standard_database.md` (locale, revisions, permissions) and `docs/standards/standard_config.md` (environment entries without secrets in the repository).
3. The Huawei challenge scores a build from the README alone (`docs/hackathon/challenge_requirements.md`, Judging of Challenge 2), so the setup the decision describes is reproducible from written instructions.
4. The local environment carries the pgRouting extension files next to PostGIS, while `plans_finished/routing_engine/` still considers pgRouting, so that its choice needs at most a new revision, not a rebuilt environment on every machine. The extension itself is not created until that initiative chooses it. Decided by the user on 2026-10-03 (question 5), following the rule the team applied to the hosting of the demo (`plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, Risks), against an environment with PostGIS only and against waiting for `plans_finished/routing_engine/`.

## Scenarios: input, flow, expected state after the run

Derived by the agent from questions 1 to 5 and from the standards quoted in Current state. Agent decision at C:40, without asking.

1. A member of the team sets up the database for the first time. Input: a machine with the tools the decision names, the repository and the member's own local environment files with the credentials. Flow: the script creates the database with the builtin locale provider and the locale `C.UTF-8` and the two accounts; then the member applies the revisions with a separate command, as the schema owner. State after the run: PostGIS exists because the first revision created it; the service account can use what the revisions granted it and nothing else; nothing changed the schema when the environment started.
2. A member runs the critical tests. Input: the set-up database and a configuration pointing to it. Flow: the critical run of pytest. State after the run: the tests ran against the member's own database, and the seeded rows are cleaned up by their registered keys; a session whose configuration points to the target environment ended with code 4 before the first test (`docs/standards/standard_tests.md`).
3. A revision already applied is fixed. Input: an edited revision. Flow: the member recreates the database from scratch with the script and applies the revisions again, as `docs/standards/standard_database.md` requires. State after the run: the schema equals the chain in the repository.
4. `plans_finished/routing_engine/` chooses pgRouting. Input: its decision. Flow: a new revision creates the extension and is applied by the schema owner. State after the run: no member rebuilt their environment (requirement 4).
5. The service process attempts a schema change. Input: a statement that creates, alters or drops an object, sent with the service account. State after the run: the database refused it, and the schema is unchanged.

## Challenging own assumptions

- Is a local database per person needed at all, or would one shared database serve the team faster? Not under the standards: a critical test writes and seeds durably, so it always goes against the local database (`docs/standards/standard_tests.md`), and two people running critical tests on one database would see each other's seeded rows (question 2).
- Is enabling PostGIS only an environment matter? No: creating the extension is a schema change and, under `docs/standards/standard_database.md`, an Alembic revision, which needs a database account allowed to create it (question 3). Since PostGIS is not a trusted extension, that account has to be a superuser at the moment the extension is created.
- Does ending with the decision alone delay anyone? Yes: the first schema revision of `plans/fact_schema/` waits for the local setup and the Alembic configuration, which now come from a work package of `plans/mvp/`, and `plan-implement` of `plans/mvp/` starts only once its plan is closed (`plans/mvp/MVP_PLAN.md`, Risks). The user chose this knowing the cost (question 1).
- Does the decision have to wait for `plans_finished/routing_engine/`? No: the environment carries pgRouting without creating it, so the choice of the routing engine changes at most the chain of revisions, not the decision (question 5).

## Domain rules or explicit TODO

- A schema change never happens on its own at environment startup (`docs/standards/standard_database.md`, Form of schema changes).
- The account that applies revisions, the schema owner, is a superuser of the local database, and the PostGIS extension is created by the first revision in the chain, applied by that account. Nothing outside the revisions creates the extension, so `docs/standards/standard_database.md` stays unchanged. Decided by the user on 2026-10-03 (question 3), against creating the extension in the setup script with a schema owner that is not a superuser, which would have required changing that standard.
- The service process connects with a separate account that is not a superuser, owns no database object and gets its permissions only from grants in revisions. Agent decision at C:40, without asking: a consequence of question 3 and of `docs/standards/standard_config.md`, which keeps the account that changes the schema out of every service process, and of `docs/standards/standard_database.md`, which grants permissions in revisions.
- The script creating the database and the accounts creates only the database, with the builtin locale provider and the locale `C.UTF-8`, and the two accounts above (`docs/standards/standard_database.md`).

## Notes on data, performance and security

- Real personal data in a local database is allowed, but nothing from it leaves the machine (`docs/standards/standard_security.md`, Real personal data in the local environment).
- Database credentials are secrets and live only in the local environment files (`docs/standards/standard_config.md`).
- The same chain of revisions runs on the hosted database of the demo, so there too the account that applies revisions has to be a superuser when the first revision creates PostGIS. The demo server also runs other services of the db person (`plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-3): if its PostgreSQL instance also holds their databases, that account can read and drop them. The demo database therefore needs a PostgreSQL instance of its own, or another answer of the task `DEPLOYMENT` of `plans/demo_environment/`; this initiative only hands the consequence over (question 3).

## Open questions

None. Questions 1 to 5 were answered on 2026-10-03, question 2 from the repository; the numbering of the answers above follows the original list.
