# PRD: Choice of the local PostgreSQL environment with PostGIS for the MVP

Document state: 2026-10-03

## Business goal

By 11:00 on 4 October 2026 the backend of `plans/mvp/` is written and tested against a real database, so that the code that reads or writes data meets the Definition of Done of the repository instead of being checked only by tests that never touch a database. Every member of the team who writes backend code needs a database for it on their own machine tonight. The Huawei challenge also scores a build from the README alone (`docs/hackathon/challenge_requirements.md`, Judging of Challenge 2), so the way the team gets that database has to be one a stranger can repeat from written instructions.

This task makes the decision that goal needs. A work package of `plans/mvp/` delivers the setup itself.

## Problem and its consequences

How each member of the team gets a local PostgreSQL with PostGIS was not decided in phase B of `plans/mvp/`; the user handed the decision to the db person of the team. As long as it stays open:

- nobody can run a critical test, and `docs/standards/standard_tests.md` requires one for every piece of code that reads or writes the database, so no such code can be finished,
- the first schema change of `plans_finished/schema_revision/`, which creates the stored data of facts and votes, has no database to run on,
- `plans/mvp/MVP_PLAN.md` cannot be closed, because its open question Q-4 waits for this decision,
- every member would set up a database their own way, and the locale of a database cannot be changed once it is created (`docs/standards/standard_database.md`, Queries in code): a database created with the wrong one breaks searching by a fragment of a Polish name and has to be set up again from scratch.

## Scope

- The choice of how each member of the team gets their own local PostgreSQL with PostGIS, with the pgRouting extension available, recorded with its reason.
- The database accounts of the local environment and the rights of each.
- Recording the decision where people look for it: the MVP plan and the deferred decisions registry.
- Handing over to the task `DEPLOYMENT` of `plans_finished/deployment/` the consequence this decision has for the hosted database of the demo.

## Out of scope

- The other technical decisions delegated in the same conversation, each with its own initiative: `plans_finished/api_contract/`, `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans_finished/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/geocoding/`, `plans_finished/account_sessions/`.
- The setup itself: the instructions in the README, the script creating the database and the accounts, the entries of the environment templates and the configuration that applies schema changes. A work package of `plans/mvp/` builds them, as with `plans_finished/geocoding/` and `plans_finished/osm_data_source/`. The user cut them from this initiative on 2026-10-03 (`LOCAL_DATABASE_SHAPE.md`, question 1).
- A trial run of the chosen environment on a machine of the team. The first run is part of that work package. Agent reading of question 1 at C:40: the user chose the decision alone over delivering the setup.
- A database shared by the team, ruled out by `docs/standards/standard_tests.md`, because a critical test seeds data durably and therefore always runs against the local database (`LOCAL_DATABASE_SHAPE.md`, question 2).
- The hosted database of the demo, which is `plans_finished/demo_environment/`. This task only hands over the consequence of FR-4.
- Creating the pgRouting extension in the database, which waits for `plans_finished/routing_engine/` to choose it.
- The content of the first schema change, which `plans_finished/schema_revision/` writes.

## Functional requirements

FR-1. Choice of the local environment. The decision names how each member of the team gets their own local PostgreSQL with PostGIS: what a member installs and starts, in which versions, and on which operating systems it works. The work package of `plans/mvp/` then builds the setup from the decision without making a choice of its own. The chosen environment:

- lets every member who writes backend code run the critical tests against their own database,
- allows a database with the locale that `docs/standards/standard_database.md` requires,
- can be repeated from written instructions alone,
- carries the pgRouting extension next to PostGIS without creating it, so that a choice of pgRouting by `plans_finished/routing_engine/` needs at most a new schema change, not a rebuilt environment on every machine.

The decision is recorded with its reason and with the alternatives it was chosen against.

FR-2. Database accounts. The decision names the accounts of the local database by their role and the rights of each, as the section Domain rules describes, so that the work package of `plans/mvp/` creates them and `plans_finished/schema_revision/` writes its first schema change for them.

FR-3. The decision recorded. The open question Q-4 of `plans/mvp/MVP_PLAN.md` is closed by a decision entry that points to this initiative and states the constraints for the rest of that plan: a work package of that plan builds the local setup, the accounts and their rights follow FR-2, the first schema change in the chain creates PostGIS, and the environment carries pgRouting. The entry Technical directions of the MVP plan of `docs/standards/decision_registry.md` records that this initiative is decided and who builds the setup and the configuration that applies schema changes. The entry stays open as long as other initiatives listed in it are undecided.

FR-4. Consequence for the demo handed over. The task `DEPLOYMENT` of `plans_finished/deployment/` gets the consequence this decision has for the hosted database as an input of its interview, without deciding it there. The consequence: the same chain of schema changes runs on the hosted database, so the account that applies them is a superuser there too, and the server of the demo also runs other services of its owner.

## Acceptance criteria

AC-1 (FR-1). The recorded choice names what a member installs and starts, the PostgreSQL version and why it allows the required locale, how PostGIS and pgRouting become available, the operating systems it was checked for, its reason and the alternatives it was chosen against. Every claim about availability rests on a source checked in phase B: the documentation of the product, its published contents or a run. The choice names no address, account name or password.

AC-2 (FR-2). The recorded decision names the two accounts with the rights of the section Domain rules, and names the first schema change in the chain as the one that creates PostGIS.

AC-3 (FR-3). Q-4 is no longer among the open questions of `plans/mvp/MVP_PLAN.md`. A decision entry there points to this initiative and states the four constraints of FR-3. The registry entry Technical directions of the MVP plan no longer says that nobody builds the configuration that applies schema changes.

AC-4 (FR-4). The shape of the task `DEPLOYMENT` carries the consequence of FR-4 as an input with a pointer to this initiative. Its open questions and decisions are unchanged.

## Domain rules

- Every member of the team who runs critical tests has their own local database. The team shares no database for development or tests (`docs/standards/standard_tests.md`).
- The local environment has two accounts besides whatever the database server itself creates at installation:
  - The schema owner applies schema changes. It is a superuser of the local database, and the first schema change in the chain, applied by it, creates PostGIS. PostGIS can only be created by a superuser, because it is not marked as a trusted extension. Nothing outside the chain of schema changes creates the extension. Decided by the user on 2026-10-03 (`LOCAL_DATABASE_SHAPE.md`, question 3).
  - The service account is used by the running app. It is not a superuser, owns nothing in the database, and gets its rights only from grants written in schema changes (`LOCAL_DATABASE_SHAPE.md`, section Domain rules).
- The setup creates only the database, with the locale required by `docs/standards/standard_database.md`, and the two accounts. Everything else in the database comes from the chain of schema changes.
- A schema change never happens on its own when the environment starts. It is applied with a separate command, by a human decision (`docs/standards/standard_database.md`).
- The names of the accounts, their passwords and the address of the database are entries of the local environment files of each member. None of them stands in the repository, not even as an example (`docs/standards/standard_config.md`, Secrets).
- The decision is recorded in the repository by 22:00 on 3 October 2026, the deadline the team set for the choice of the hosting, which has the same owner (`LOCAL_DATABASE_SHAPE.md`, question 4).

## Dependencies and impact on other modules

- `plans/mvp/MVP_PLAN.md` gets Q-4 closed (FR-3) and gains a work package that builds the local setup. The plan stays open while its other questions wait.
- `plans_finished/schema_revision/` writes the first schema change, which creates PostGIS and grants the service account its rights (FR-2). Its stored data still waits for the setup of the work package of `plans/mvp/`.
- `plans_finished/routing_engine/` still considers pgRouting. FR-1 keeps the decision independent of its result.
- `plans_finished/demo_environment/`: the hosted database has to meet the same database standard as the local one (`DEMO_ENVIRONMENT_PRD.md`, Dependencies), and the task `DEPLOYMENT` of `plans_finished/deployment/` receives the consequence of FR-4.
- `docs/standards/decision_registry.md`: the entry Technical directions of the MVP plan changes (FR-3).
- `docs/standards/standard_database.md`, `docs/standards/standard_config.md` and `docs/standards/standard_tests.md` do not change. The decision follows them as they stand.

## Risks and notes

- The answers behind this PRD were given by the user, who has not stated being the db person. The ruling of the db person is still to be confirmed, as in `plans_finished/fact_schema/`.
- Ending with the decision alone delays the first schema change of `plans_finished/schema_revision/`. That change waits for the setup and the configuration that applies schema changes, which come from a work package of `plans/mvp/`, and that plan is implemented only once it is closed. The user chose this knowing the cost.
- The chosen environment is not tried on a machine of the team within this task. A wrong claim about it, for example a missing extension or a version too old for the required locale, surfaces only in the work package of `plans/mvp/`. AC-1 lowers this risk by requiring a checked source for every such claim, not a run.
- Only the machine of the agent's session is known: Windows 11, a PostgreSQL 18 installation without PostGIS that does not answer, and a Docker client whose engine was not running on 2026-10-03. The machines of the other members are not known, so the operating systems of FR-1 have to be stated by the team in phase B.
- On the hosted demo the account that applies schema changes needs superuser rights. If the PostgreSQL instance of the demo server also holds the databases of the other services of its owner, that account can read and drop them. FR-4 hands this over, and it is not decided here.
- An environment that carries pgRouting may carry a dependency the project never uses, if `plans_finished/routing_engine/` chooses another engine.
