# PRD: First schema revision of the MVP

Document state: 2026-10-04

## Business goal

By 11:00 on 4 October 2026 the team has a working prototype of the main scenario in Kraków (`MVP.md`, section Goal and deadline). Every backend initiative that reads or writes the OpenStreetMap copy, facts, votes or accounts - `osm_import`, `accounts`, `community_facts`, `route_planning` and `sample_data` - waits for the first schema revision, so this initiative and `backend_skeleton` are the critical path of the MVP (`MVP.md`, section Order and critical path).

This initiative gives them the database they build on: the stored data of the target schema, which refuses by itself the states the rules forbid, one shared description of its tables and closed lists that the import and the backend both use, and the documents that tell each of them which rule and which scenario it now carries.

It serves the judging criterion "Data reliability, presentation and updates" of the Kraków brief: a vote counted twice or a fact saved twice weakens the status every person sees on the map.

## Problem and its consequences

- No schema revision exists. Until it does, no backend initiative can write a fact, a vote, an account or a copy of OpenStreetMap, and every hour of waiting is taken from the time before the deadline.
- The target schema has never run with its spatial parts or its rights. A defect found only when the revision is written needs a new version of the specification during the night of the implementation (`plans_finished/mvp/MVP_PLAN.md`, section Risks).
- Without one shared description of the tables, the import and the backend each describe the same tables and the same closed lists on their own. The first difference between the two - a fact type the import writes and the backend does not know - shows as a fact that disappears from the map or a failed save.
- `plans_finished/mvp/MVP_PLAN.md` D-11 gave the builder of the first revision every scenario of AC-1 - AC-12 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` with the code of the rules they need, while the seed of this initiative and `MVP.md` say it builds no operation. Read literally, this initiative would build the statuses, the reconciliation of a fresh copy, the deletion of an account, hiding, the duplicate check and the readings - the core of three other initiatives - and hold every one of them back.
- The vote limit of the specification in force, version 12, counts a day from the instant of the previous vote, and version 11 built on it the own vote the app shows, with the moment of the next vote kept on the device and the texts of the interface. Kuba, the owner of the database, decided on 2026-10-04 that it counts calendar days (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_SHAPE.md`, section Domain rules). Until a new version of the specification says so, `community_facts` builds voting and `frontend_app` builds the own vote by the old rule.
- The target schema still holds what served only the clearing of the hash of a vote without an account, a task that version 9 of the specification removed.
- The hash of a vote without an account has no length check, while the idempotency key of a saved fact has one. A hash computed by a different function, or cut short by a defect, enters the vote limit unnoticed, and the same person counts as two.

## Scope

- A new version of the specification with the vote limit by calendar day and the length check of the hash of a vote without an account, the target schema, the programming interface contract and the documents of the frontend that follow it, and the record in `MVP.md` of what this initiative builds and what it hands over - first, before the revision.
- The first schema revision, which creates the whole target schema in version 12, with the idempotency key, and in the version above, with the rights of the service account.
- One shared description of the tables and of the closed lists of the target schema, used by the import and by the backend.
- The database the import and the backend share, ready to start on a team machine and on the hosted demo, with the chain of schema changes and the shared description in one package of its own.
- The tests that prove, against a real local database, that the stored data refuses by itself what the rules forbid, keeps the offset of an instant and gives the service account exactly its rights.
- The names of the created database objects in the registry of names.

## Out of scope

- Every code of the rules and every operation of the programming interface. The scenarios of AC-1 - AC-12 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` that need code of the rules go with the initiative of `MVP.md` that builds that code (FR-2): the derivation of a status, AC-1 - AC-5 and the part of AC-8 in which only the later of two votes counts - `community_facts`; the reconciliation of a fresh copy, AC-6 and AC-7 - `osm_import`; the deletion of an account, AC-9 - `accounts`; hiding and the duplicate check of AC-10 - `community_facts`, and the facts of a route of AC-10 - `route_planning`; the readings of AC-12 - `community_facts`. Decided by Kuba on 2026-10-04 (shape, Problem and Out of scope).
- The backend skeleton, which `backend_skeleton` builds.
- The version of the specification that brings the idempotency key into the target schema - `plans_finished/schema_revision/`, carried out as version 12.
- How the hash of a vote without an account is computed - what is hashed and with which secret - which `community_facts` decides within the length of FR-1.
- Applying the revision on the hosted demo - a step by hand of `docs/deployment/hosted_demo.md`, completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`.
- The import, the loading program and the sample data - `osm_import` and `sample_data`.
- Any task that clears the hash of a vote without an account - none exists since version 9 of the specification.

## Functional requirements

FR-1. A new version of `docs/product/specification.md`, approved by Kuba, states the vote limit of M4 by calendar day in the Europe/Warsaw zone: a person votes on the same fact at most once per calendar day, a second vote on the same day is refused, and a vote on the next calendar day is accepted, whatever the hours between them; of the votes of one person on a fact only the latest counts, as before. The own vote the app shows says the same: the next vote on that fact is possible from the next calendar day. The target schema of that version holds the uniqueness of the fact, the person and the calendar day of a vote, for a person with an account and for a person without one, checks that the hash of a vote without an account is 32 bytes long, and drops what only the window of a day from the instant of a vote and the clearing of the hash needed. `docs/product/api_contract.md` follows it: the refusal of a vote that comes too soon tells the person the start of the next calendar day, keeps its code and its field, and no longer promises that a vote repeated after a lost response is refused across midnight. The documents of the frontend follow it in the same change - the journey of confirming or denying a fact in `docs/product/user_journeys.md`, `docs/product/views.md`, `docs/product/interface_texts.md`, `plans/frontend_app/FRONTEND_APP_PACKAGES.md` and the mock of a voted fact in `.impeccable/briefs/views/` - and show the moment of the next vote as a day without an hour; Kuber and Adrian are told. The version takes the next free number when it is approved, 13 since version 12 was approved on 2026-10-04.

FR-2. `MVP.md` records that this initiative builds no code of the rules, which initiative runs each scenario of AC-1 - AC-12 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` that left it (section Out of scope), the version of FR-1 with the hash of 32 bytes that `community_facts` computes, and that Kuba confirmed on 2026-10-04 the rulings given in Kuba's place for D-11 of `plans_finished/mvp/MVP_PLAN.md` and for the interview of `plans_finished/schema_revision/`, and the form of the idempotency key of version 12.

FR-3. FR-1 and FR-2 are done first, as soon as the plan of this initiative is closed, without waiting for `backend_skeleton`, so that `community_facts`, `osm_import`, `accounts` and `frontend_app` start or continue their work from the new rule and from the scenarios they now carry.

FR-4. The first schema revision creates, on an empty local database, the whole target schema of `docs/product/schema.md` in version 12, with the idempotency key, and in the version of FR-1, and matches it line by line, as AC-13 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` asks. A way back below the first revision is refused with a message saying that the database is recreated instead.

FR-5. The revision gives the service account exactly the rights of `docs/product/schema.md`, section Rights of the service account, and no right to create, alter or drop anything. The name of that account is supplied when the revision is applied and never stands in the repository.

FR-6. One shared description of the seven tables and of the closed lists of the target schema is used by the import and by the backend, neither of which describes them on its own, and it matches the stored data, which a test checks.

FR-7. The stored data refuses by itself the states of FR-15 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` - a second vote of one person on one fact on the same calendar day, a fact type outside the closed list, a geozone radius outside the list, two accounts with pseudonyms differing only in letter case, two facts with the same OpenStreetMap identity, converted and outdated ones included - a second fact with an idempotency key already saved, and a hash of a vote without an account that is not 32 bytes long. Each refusal, the round trip of the offset of an instant and the rights of FR-5 are proven by a test against a real local database.

FR-8. The checks of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 are delivered here: the spatial extension exists after the revision is applied, the service account is refused creating a table and dropping or altering an object of the revision, the database lowers Polish letters and compares text by bytes, and the routing extension is available without being created.

FR-9. The names of the database objects the revision creates are entered in `docs/standards/naming_registry.md`.

FR-10. One package of its own holds the shared description and the chain of schema changes, and the import and the backend install it. It starts the database of `plans_finished/local_database/` on a team machine, which keeps its data only while it runs, and the database of the hosted demo, which keeps its data across restarts; the schema changes are applied to either only by a separate step, to the hosted demo only with the consent given at the call, and the tests run on a container against the local database.

## Acceptance criteria

AC-1 (FR-1). The new version is approved by Kuba and in force. Its M4 gives this run, hours in Europe/Warsaw, for fact F, an account A and a person without an account H: 10:00 on 4 October A confirms F - accepted; 15:00 A denies F - refused, and the refusal names 00:00 on 5 October as the start of the next vote; 00:05 on 5 October A denies F - accepted, and only the denial counts for A; 23:50 on 4 October H confirms F and 00:10 on 5 October H denies F - both accepted, and only the denial counts for H. After the vote of 10:00 the app shows A that the next vote on F is possible from 5 October, with no hour, and the documents of the frontend of FR-1 say the same. The target schema of that version holds nothing that served only the clearing of the hash or the window of a day from the instant of a vote, and refuses a hash of a vote without an account that is not 32 bytes long.

AC-2 (FR-2, FR-3). Before `backend_skeleton` is finished, `MVP.md` names, for each of AC-1 - AC-12 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`, the initiative that runs it, says that this initiative builds no code of the rules, points to the version of FR-1 and to the hash of 32 bytes `community_facts` computes, and no longer lists Kuba among the rulings still to be confirmed for D-11, for `plans_finished/schema_revision/` and for the form of the idempotency key of version 12.

AC-3 (FR-4). On an empty local database the revision is applied once by the schema owner and the stored data matches the target schema line by line: every extension, domain, table, constraint and index, and nothing else. A request to go below the first revision changes nothing and answers that the database is recreated instead.

AC-4 (FR-5, FR-8). After the revision, the service account reads and writes each table with exactly the rights the target schema lists for it, a write the target schema does not allow is refused, a new table in the public schema is refused, and dropping or altering a table of the revision is refused; the spatial extension exists.

AC-5 (FR-6). The import and the backend take every table and closed list from the one shared description. A closed list whose values differ between that description and the stored data makes a test fail.

AC-6 (FR-7). Each of these is refused by the stored data alone, with no other code in between: a geozone with a radius of 30 m; a fact of a type outside the closed list; a second fact with the OpenStreetMap identity of a fact already stored, converted or outdated; an account "kuba" next to an account "Kuba"; a second fact with an idempotency key already saved; a second vote of one person on one fact on the same calendar day, while a vote of that person on that fact on the next calendar day is kept; a vote without an account with a hash of 20 bytes, while one with a hash of 32 bytes is kept. An instant written with the offset +02:00 is read back with +02:00.

AC-7 (FR-9). `docs/standards/naming_registry.md` lists every database object the revision creates, under the name it has in the stored data.

AC-8 (FR-10). On a team machine with only Docker, one step starts the local database, one applies the chain and one runs every test on a container; stopping and starting the local database gives an empty one. The database of the hosted demo keeps the applied chain across a restart and refuses to apply it without the consent given at the call. An environment entry left unfilled stops the start with its name.

## Domain rules

- The rules are those of `docs/product/specification.md` and of `docs/product/schema.md`, which is part of it, in version 12, with the idempotency key, and in the version of FR-1. A change of the target schema is a new version of the specification approved by the user (`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-21).
- The vote limit counts calendar days in Europe/Warsaw, the zone of every date the app shows (M10). It replaces the window of a day from the instant of the previous vote of M4 in version 12, the same window in the own vote version 11 added, and the domain rule of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` that the day runs from the instant of the vote; the limit stops being a configuration value. Decided by Kuba on 2026-10-04.
- The hash of a vote without an account is 32 bytes long, and the stored data refuses any other length. It replaces the hash without a length check of `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-8; what is hashed and with which secret stays with `community_facts`. Decided by Kuba on 2026-10-04.
- A vote repeated because its response was lost is refused within the same calendar day. Across midnight it is accepted as a second vote, which adds no weight, because only the latest vote of a person counts.
- Every instant is kept with the offset it was written with, and the calendar day of a vote is the day of its instant in Europe/Warsaw, whatever that offset (`docs/standards/standard_time.md`).
- The database holds no status and no domain decision, only integrity constraints; the rules of M4 are applied by code to the stored votes (`docs/product/schema.md`, section Conventions).
- The hash of a vote without an account is pseudonymized personal data, kept until the demo is deleted (M9). The tests use made-up hashes, never one computed from a real address.
- When the target schema, the revision and the shared description disagree, the target schema prevails: the revision matches it, and the shared description follows the stored data.

## Dependencies and impact on other modules

- `backend_skeleton` installs the package of FR-10 and uses its local database; nothing of this initiative waits for it.
- `plans_finished/schema_revision/` wrote the version of the specification with the idempotency key, approved on 2026-10-04 as version 12; nothing of this initiative waits for it any more.
- `community_facts` builds voting by the rule of FR-1, computes the hash of a vote without an account with a 32-byte output, and runs AC-1 - AC-5, AC-8 in part, AC-10 in part and AC-12 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`; `osm_import` runs AC-6 and AC-7; `accounts` runs AC-9; `route_planning` runs the part of AC-10 about the facts of a route. Each of them, and `sample_data`, writes the stored data through the shared description of FR-6.
- `frontend_app` shows the refusal of a vote that comes too soon and the own vote with the moment of the next vote. The code and the field of the refusal do not change, only the instant it names; the moment the frontend keeps on the device becomes the start of the next calendar day, and the documents Kuber and Adrian build from are rewritten by the version of FR-1.
- The task `DEPLOYMENT_CONFIG` of `plans/deployment_config/` completes the step that applies the revisions on the hosted demo; the same revision runs there.
- `plans/osm_importer/` on the branches `md/fast-setup` and `mw-osm-import` asks in its blocking Q-2 which revision and which shared fixtures the owners of the schema deliver; this initiative answers the revision and the shared description, and the overlap with `osm_import` stays in `docs/standards/decision_registry.md`, entry Initiatives outside MVP.md that overlap its initiatives.

## Risks and notes

- Time: five initiatives wait for the revision. Changed on 2026-10-04 by Kuba during the implementation (questions 10 - 13): the revision no longer starts only after `backend_skeleton`.
- The target schema has never run with its spatial parts or its rights. A defect found while the revision is written needs another version of the specification approved by Kuba before the revision can match it. Running the target schema on a database with the spatial extension before the revision is written would find such a defect early, so that it enters the version of FR-1 instead.
- Until FR-2 is written, the shapes of `community_facts`, `osm_import` and `accounts` can still read the old split and the old vote limit in `MVP.md` and in D-11 of `plans_finished/mvp/MVP_PLAN.md`; FR-3 puts it first for that reason, and telling Marek and Mateusz at once costs nothing.
- Until FR-1 is written, `frontend_app` can build the own vote, its texts and the moment kept on the device on the window of a day; the version of FR-1 rewrites documents Kuber and Adrian wrote, so telling them at once costs nothing either.
- The length check binds the function `community_facts` chooses for the hash. A function with another output is refused at the first vote without an account, which shows in the tests of `community_facts`, not in the data.
- Whether an item of a list names its street is deferred until Marek tests the programming interface (`docs/standards/decision_registry.md`, entry Street name of an item of a list). If the name enters the target schema after the first revision, a second revision adds it to the stored ways.
- With the limit by calendar day a person votes twice within minutes across midnight; neither vote adds weight, but both stay as rows.
- Kuba named the key of a vote as the fact, the hash and the date. A vote with an account has no hash, so the uniqueness for such a vote stands on the account; the form of that uniqueness is a technical decision of the plan.
- The scenarios of AC-1 - AC-12 now run in four initiatives instead of one, so a gap in the target schema that only a run of the rules would show surfaces in the initiative that runs that scenario, after this revision.
- Changed on 2026-10-04 after the merge of `dev` `2dcccce`, which brought versions 11 and 12 of the specification: the version with the idempotency key is version 12 and approved, so nothing here waits for it and the version of FR-1 takes the number 13; FR-1 adds the own vote of version 11, the documents of the frontend and the length check of the hash of a vote without an account, FR-2 the confirmation of the form of the key, and FR-7, AC-1, AC-2 and AC-6 follow them. Decided by Kuba on 2026-10-04 (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_SHAPE.md`, questions 7 - 9).
- Changed on 2026-10-04 by Kuba during the implementation (questions 10 - 13): the shared description and the chain of schema changes are one package of their own with the local database and the database of the hosted demo (FR-10, AC-8), every check of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 is delivered here (FR-8), and nothing of this initiative waits for `backend_skeleton` any more (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_SHAPE.md`, questions 10 - 13).
