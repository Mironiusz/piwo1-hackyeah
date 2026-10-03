# Shape: First schema revision of the domain model of facts and votes

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed carries no regulator value, so the default C:40 applies.

## Problem

The domain model and the target schema of facts and votes are decided by the task `FACT_SCHEMA` of `plans_finished/fact_schema/` (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md`), and the initiative also builds the first schema revision with its tests (`plans_finished/fact_schema/FACT_SCHEMA_SHAPE.md`, question 1). The revision needs the local database with PostGIS of `plans_finished/local_database/` and a backend skeleton holding the Alembic configuration, whose file names and locations the work package of `plans/mvp/MVP_PLAN.md` D-7 decides, because they belong to the backend skeleton that Q-11 of that plan shapes (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8). That work package starts only once the MVP plan is closed, and the MVP plan closes only once Q-10 is closed. Kept inside the task `FACT_SCHEMA`, the revision made Q-10 wait for the skeleton while the skeleton waited for Q-10. On 2026-10-03 the user split it out into this task to cut that loop (U-1 of `plans_finished/dependency_check/DEPENDENCY_CHECK_REVIEW.md`). Later the same day the user moved this task into an initiative of its own, `plans/schema_revision/`, so that the rest of `plans/fact_schema/`, with its task `FACT_SCHEMA` finished, could move to `plans_finished/fact_schema/`; the scope of this task did not change.

## Recipient and trigger

- The recipients are the work packages of `plans/mvp/` that read and write facts and votes - the import, the route, voting, geozones, accounts and moderation - and the routing engine of `plans_finished/routing_engine/`, which reads the stored ways and points (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-5).
- The owner of this task is the db person, as the owner of the whole initiative (`plans/mvp/MVP_PLAN.md` Q-10). Agent decision at C:40, without asking: the task was split out of a task the db person owns, and the user named no other owner.
- Trigger: the task `FACT_SCHEMA` is implemented - the target schema `docs/product/schema.md` exists and Q-10 of `plans/mvp/MVP_PLAN.md` is closed - and the local setup and the backend skeleton with the Alembic configuration of the work package of D-7 of that plan exist. The trigger is that part of the work package, not the whole of it: the critical tests that `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 gives that work package - PostGIS existing after `alembic upgrade head`, and the service account refused a `DROP` or `ALTER` of an object of the first revision - need the first revision, so they run after this task. Agent decision at C:40, without asking: it follows from D-7 and D-8 there, under which `plans/schema_revision/` writes the first revision and those tests check it.

## Current state

- No product code, no database schema and no Alembic configuration exist (`plans/mvp/MVP_PLAN.md` F-3).
- The requirements this task builds stand in `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`: the rules of FR-1 - FR-14, which the stored data has to hold, the stored data of FR-15, and the acceptance criteria AC-1 - AC-12 together with the part of AC-13 that asks the stored data to match the target schema line by line. They were handed to this task on 2026-10-03 and stay in that PRD with their numbers, because other documents cite them.
- `plans_finished/local_database/` decided on 2026-10-03 (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-5, D-7, D-8): besides the bootstrap superuser the cluster has the schema owner, a superuser that applies the revisions, and the service account, which owns no object and gets its rights only from grants in revisions; the first revision in the chain creates PostGIS and is written by `plans/schema_revision/`; pgRouting is available and not created; the work package of `plans/mvp/` adds the critical tests of the locale, the extensions and the rights.
- `docs/standards/standard_database.md`: a schema change is an Alembic revision with raw SQL, one statement per call, reviewed line by line against the DDL written in the product specification; integrity constraints, uniqueness included, are required.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans_finished/api_contract/` decided on 2026-10-03 (`docs/product/api_contract.md`, operation `create_fact`; `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-9) that saving a report or a geozone carries an idempotency key, a UUID the client generates once per approved summary and repeats with every attempt of the same save, and that an attempt with a key already saved with the same content returns the first fact instead of creating a second one, as `docs/standards/standard_idempotency.md` requires. `docs/product/schema.md` holds no column for that key, so the stored data needs a change of the target schema, which `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-21 allows only through a new version of the specification approved by the user.

## Smallest meaningful scope

Following from the seed: FR-15 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`, the tests that run AC-1 - AC-12 there on the stored data, and the line by line match of AC-13 there - the first schema revision that creates the model of the target schema, with its tests.

## Out of scope

- The rules of facts and votes, the target schema and closing Q-10 of `plans/mvp/MVP_PLAN.md` - the task `FACT_SCHEMA`.
- The local setup, the Alembic configuration and their critical tests - the work package of `plans/mvp/MVP_PLAN.md` D-7 (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8).
- The job of the worker that deletes the identifiers of votes without an account after 30 days - `plans/mvp/MVP_PLAN.md` Q-11.
- The import, which writes the OpenStreetMap facts by these rules - a work package of `plans/mvp/` after Q-11.

## Functional requirements

1. The stored data refuses, by itself, the states the rules forbid (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-15).
2. Tests run the scenarios of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` AC-1 - AC-12 on the stored data.
3. The stored data matches the target schema of `docs/product/schema.md` line by line (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` AC-13).
4. The first revision in the chain creates PostGIS (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-7).

## Scenarios: input, flow, expected state after the run

The stored data has to run the scenarios of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` AC-1 - AC-12 with the results stated there, without restating them here.

## Challenging own assumptions

- Can the revision be written before the backend skeleton exists? No: `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 leaves the file names and locations of the Alembic configuration to the work package of `plans/mvp/MVP_PLAN.md` D-7, because they belong to the backend skeleton that Q-11 shapes, so a revision written earlier would guess them. That is the reason this task exists separately.
- Does this task wait for the whole work package of D-7, while that package waits for the first revision? No, as long as the trigger is the skeleton with the Alembic configuration and not the finished package: the package builds the skeleton, this task adds the first revision, and the critical tests of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 that check that revision run last (section Recipient and trigger). A plan of `plans/mvp/` that delivers the package as one step together with those tests would bring the loop back.
- Does the split leave the rules of the task `FACT_SCHEMA` unchecked until this task runs? Partly: the scenarios of AC-1 - AC-12 are run against the stored data only here, so a gap in the target schema surfaces only after Q-11 and the skeleton (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md`, Risks and notes).
- Does the revision land in time? It waits for Q-1, Q-7 and Q-11 of `plans/mvp/MVP_PLAN.md`, for the closing of that plan and for the skeleton, which is the longest path to the deadline (question 1).

## Domain rules or explicit TODO

- The rules are those of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`, section Domain rules, and of `docs/product/specification.md` version 4; this task does not change them.

## Notes on data, performance and security

- The revisions are applied by the schema owner, and the service account gets only the grants a revision gives it (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-5).
- The identifier of a vote without an account is pseudonymized personal data in the sense of the GDPR (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md`, Risks and notes).
- Secrets and target environment details never enter the repository (`docs/standards/standard_config.md`, section Secrets).

## Open questions

1. By when must the revision be ready, given that it waits for Q-11 and the backend skeleton of `plans/mvp/MVP_PLAN.md` and that the Kraków submission closes at 11:00 on 4 October 2026? `Block: no`
2. How does the stored data hold the idempotency key of a saved report or geozone that `docs/product/api_contract.md` requires (Current state), and which new version of the specification brings it into `docs/product/schema.md`? `Block: yes` (category: database schema)
