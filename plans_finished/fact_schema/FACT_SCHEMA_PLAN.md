# Plan: Domain model and database schema of facts and votes for the MVP

Document state: 2026-10-03, plan closed

## Goal

Carry out the task `FACT_SCHEMA` of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`: write the target schema that holds FR-1 - FR-13 as `docs/product/schema.md`, and make it part of the product specification in version 6 of `docs/product/specification.md`, the part of FR-14 that version 4 left to this initiative; meet AC-13 without its part about the stored data. Close Q-10 of `plans_finished/mvp/MVP_PLAN.md` with a decision entry that states the constraints the schema puts on the rest of the MVP, record that in the registry of deferred decisions (FR-16, AC-14), and hand the sibling initiatives what they read from the schema. No code and no revision are written here: the stored data of FR-15, AC-1 - AC-12 and the part of AC-13 about the stored data are the task `SCHEMA_REVISION` of this initiative (D-1).

The plan is written for the tree in which the branch `rm/requirements-preparation` up to its commit `b5f03be` is merged and the plan of `plans_finished/routing_engine/` is implemented (D-20, D-22): `fff8e88` archives the decided initiatives in `plans_finished/`, closes Q-4 as D-7 of the MVP plan and writes version 4 of the specification, `b5f03be` adds the changes of `plans_finished/dependency_check/` after the gate of the PRD, and the routing engine takes version 5 of the specification and D-8 of the MVP plan.

Changed on 2026-10-03, after the plan was closed, when `dev` was merged into `rm/requirements-preparation`: the second task is named `SCHEMA_REVISION`, the plan meets FR-16 and AC-14 added to the PRD after its gate, it writes version 6 of the specification and D-9 of the MVP plan, and the Scope of changes quotes the files as they stand after that merge and after the routing engine (F-1, F-24 - F-27, D-1, D-18, D-20, D-22).

Corrected on 2026-10-03 by `plan-implement`, before any step was carried out, for the tree at `032373e`: the decision on account sessions took D-8 of the MVP plan and the routing engine D-9, so this plan writes the next free decision, D-N in the Scope of changes; the steps name the second task `SCHEMA_REVISION` throughout; steps 3.2 and 4 quote the passages as they stand now; steps 3.8 and 3.9 replace the two decision entries that still name Q-10; step 6.2 is dropped and step 7 removes the seed of phase B (F-21, F-22, F-24, F-25, F-28 - F-30, D-1, D-11, D-14, D-22, D-23).

## Facts

F-1. The PRD of this initiative passed its gate on 2026-10-03 with x = 1 day and k = 5 approved by the user in place of the db person, and after the gate it splits the initiative into the tasks `FACT_SCHEMA` and `SCHEMA_REVISION`, hands the stored data, AC-1 - AC-12, the part of AC-13 about the stored data and the code of the rules they need to the second task, gives this task FR-16 and AC-14, and asks one target schema for the import and the backend. | doc:`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` lines 20, 21 and 25, line 65 FR-16, line 69, line 97 AC-14, lines 103 and 104 `- x = 1 day:` and `- k = 5:` | 2026-10-03
F-2. No product code exists: the tracked Python files are only the architecture tests and the agent hooks, and there is no Alembic directory, no layer directory and no configuration module. | cmd:`git ls-files` -> Python files only under `tests/architecture/`, `.claude/hooks/`, `.codex/hooks/` and `.agents/skills/load-context/scripts/`, and no path under `alembic/`, `api/`, `service/`, `data/`, `worker/` or `config/` | 2026-10-03
F-3. Q-4 is closed as D-7 of the MVP plan: every member runs PostgreSQL 18.6 with PostGIS 3.6.4 in a project image, a work package of the MVP plan builds the local setup and the Alembic configuration, the schema owner is a superuser that applies the revisions, the service account owns nothing and gets its rights only from grants in revisions, and the first revision creates PostGIS. | cmd:`git show fff8e88:plans_finished/mvp/MVP_PLAN.md` -> line 37 `D-7. Local database environment, settling the former Q-4.`; cmd:`git show fff8e88:plans_finished/local_database/LOCAL_DATABASE_PLAN.md` -> line 47 D-5, line 51 D-7, line 53 D-8 | 2026-10-03
F-4. Version 4 of the specification, approved by the user on 2026-10-03 and written by `plans_finished/consistency_check/`, states the statuses of every fact, OpenStreetMap facts included, the OpenStreetMap facts as present items only, the vote limit, the window of five persons, the order of statuses, the weight of a vote whose person is no longer known, the closed list of radii, the pseudonym rule, flags, hiding and restoring, and leaves the target schema out. | cmd:`git show fff8e88:docs/product/specification.md` -> lines 3, 104, 105, 107 - 109, 121, 181 and 202; cmd:`git show fff8e88:plans/consistency_check/CONSISTENCY_CHECK_REVIEW.md` -> line 80, which says the target schema is not part of version 4 | 2026-10-03
F-5. Version 4 still says that the specification settles no technical solution, has "None at version 4." under Open questions and ends its Decision provenance with the entry of version 4. | cmd:`git show fff8e88:docs/product/specification.md` -> line 9 `This document does not settle the technology stack or any technical solution`, line 266 `None at version 4.`, line 275 `- Version 4:` | 2026-10-03
F-6. The user decided in `plans_finished/consistency_check/` that an OpenStreetMap fact has the four statuses of a user fact and becomes outdated by the same rule, that routes avoid geozones unless outdated or hidden, and that the window of k persons is checked by the tests of this initiative rather than by AC-3. | cmd:`git show fff8e88:plans/consistency_check/CONSISTENCY_CHECK_REVIEW.md` -> lines 47, 49, 51 and 59, U-1, U-2, U-3 and U-7 | 2026-10-03
F-7. The MVP PRD, `PRODUCT.md`, FR-8 of the PRD of this initiative and the shapes of the contract, the routing engine and the sessions already follow version 4 or carry the PRD of this initiative. | cmd:`git show fff8e88:plans_finished/mvp/MVP_PRD.md` -> lines 39, 55 and 81; cmd:`git show fff8e88:PRODUCT.md` -> lines 56 and 59; cmd:`git show fff8e88:plans/fact_schema/FACT_SCHEMA_PRD.md` -> line 47; cmd:`git show fff8e88:plans_finished/api_contract/API_CONTRACT_SHAPE.md` -> lines 27 and 28; cmd:`git show fff8e88:plans_finished/routing_engine/ROUTING_ENGINE_SHAPE.md` -> lines 25 and 27; cmd:`git show fff8e88:plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` -> line 25 | 2026-10-03
F-8. In the MVP plan of that commit D-7 is the last decision, Q-10 is open with three items of inputs and one of caveats, and Q-10 is named in the Risks, in Q-9 and in the closing note on Q-11. | cmd:`git show fff8e88:plans_finished/mvp/MVP_PLAN.md` -> line 37 D-7, line 48 Risks, line 55 Q-9, lines 56 - 60 Q-10 and its items, line 61 Q-11, line 62 the closing note, lines 72 - 73 the last Supplementary files | 2026-10-03
F-9. In that commit the registry of deferred decisions says that this initiative has its PRD confirmed and its plan still to be written, and the standards map names the product specification alone as the target of anything that touches a table. | cmd:`git show fff8e88:docs/standards/decision_registry.md` -> line 48, which says this initiative has its PRD confirmed and its plan still to be written; cmd:`git show fff8e88:docs/standards/README.md` -> lines 54 and 92 | 2026-10-03
F-10. The rules for a pseudonym and a password are a blocking question 4 of the interview of `plans_finished/account_sessions/`. | cmd:`git show fff8e88:plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` -> line 69, question 4 with `Block: yes` | 2026-10-03
F-11. The closed plan of the tag mapping leaves the names of the modules and constants of the backend to Q-11 of the MVP plan. | cmd:`git show fff8e88:plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` -> line 68 D-14, line 72 D-16 | 2026-10-03
F-12. Every schema change is an Alembic revision of raw SQL reviewed line by line against the DDL of the product specification, permissions are granted in revisions, integrity constraints are required while triggers and domain decisions in the database are not allowed, a one-to-one relation is a column on the existing row, and a text column has a documented length limit or deliberately none. | doc:`docs/standards/standard_database.md:46`; doc:`docs/standards/standard_database.md:50`; doc:`docs/standards/standard_database.md:62`; doc:`docs/standards/standard_database.md:78`; doc:`docs/standards/standard_database.md:82`; doc:`docs/standards/standard_database.md:130` | 2026-10-03
F-13. An instant is stored as `timestamptz(3)` with a `utc_offset_minutes` column of the shared domain, the condition `CK_<table>_offset_pairs` rejects a half pair, a server-stamped value takes the offset of the business zone, and a day is a `date`. | doc:`docs/standards/standard_time.md:48`; doc:`docs/standards/standard_time.md:54`; doc:`docs/standards/standard_time.md:70`; doc:`docs/standards/standard_time.md:72` | 2026-10-03
F-14. A duplicate that may legitimately repeat after a window must not be guarded by a hard unique constraint, and a conflict is resolved by `INSERT ... ON CONFLICT` rather than by a caught exception. | doc:`docs/standards/standard_idempotency.md:54`; doc:`docs/standards/standard_idempotency.md:60` | 2026-10-03
F-15. The identity of an OpenStreetMap fact is the element type, the element identifier and the fact type without matching by geometry, a fresh copy with its reconciliation and its date becomes visible in one commit with the way of storing it left to Q-10, the reconciliation ends with a unique constraint on that identity for converted and outdated facts too, and a vote keeps its weight after its 30-day identifier is deleted. | cmd:`git show fff8e88:plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` -> line 61 D-7, line 65 D-9, lines 67 - 75 D-10, line 107 D-21 | 2026-10-03
F-16. The tag mapping gives every way of the pedestrian network four barrier states, the `wheelchair=no` marking and its kerb, crossing and motor traffic context, every node its point facts and kerb point, every amenity a point, and every fact the calendar day of the last edit of its element. | cmd:`git show fff8e88:plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` -> line 52 D-6, line 54 D-7, line 56 D-8, line 66 D-13, line 70 D-15 | 2026-10-03
F-17. The shape of this initiative left to phase B whether a status is derived on read or kept up to date on write. | cmd:`git show fff8e88:plans/fact_schema/FACT_SCHEMA_SHAPE.md` -> line 86 | 2026-10-03
F-18. On PostgreSQL 15 with `btree_gist`, two partial exclusion constraints over the fact, the person and `tstzrange(cast_at, repeat_allowed_at)` make `INSERT ... ON CONFLICT DO NOTHING RETURNING id` return no row for a second vote of the same account or hash within the day, return a row for a vote exactly one day later, let votes without any identity coexist, and raise an error without `ON CONFLICT`; `tstzrange` is immutable while `timestamptz + interval` is only stable. | cmd:`docker run postgres:15` with `psql` running the scratchpad script `check.sql` -> `first_account_vote` 1, `second_within_day` 0 rows, `exactly_one_day_later` 3, `first_hash_vote` 4, `second_hash_within_day` 0 rows, `two_without_identity` 6 and 7, `ERROR: conflicting key value violates exclusion constraint "ex_vote_account_limit"`, `timestamptz_pl_interval` volatility `s`, `tstzrange` volatility `i` | 2026-10-03
F-19. On the same server a unique index on `lower(pseudonym)` refuses `wózek_krk` after `Wózek_KRK` and `żaba` after `ŻABA`, a unique constraint on the OpenStreetMap identity admits two facts with a null identity and refuses a second fact on `way` 42 with the same type, and unquoted constraint names are stored in lower case. | cmd:the same `check.sql` -> `ERROR: duplicate key value violates unique constraint "ux_account_pseudonym_lower"`, `zaba_upper` 3, `zaba_lower` 0 rows, `duplicate_osm_identity` 0 rows, `facts` 3 | 2026-10-03
F-20. `btree_gist` ships in the server package of the official PostgreSQL image, not in a separate one, and is a trusted extension. | cmd:`docker run postgres:15` with `psql -c "select name, version, trusted from pg_available_extension_versions where name = 'btree_gist'"` -> `btree_gist|1.7|t`; cmd:`dpkg -S /usr/share/postgresql/15/extension/btree_gist.control` -> `postgresql-15` | 2026-10-03
F-21. The machine of the implementing session has Python 3.13.14 with pytest 9.1.1 in `venv/`, Node.js 24.18.0 with the installed prettier of `package.json`, and no running Docker engine, and the project requires Python 3.13. | cmd:`venv/Scripts/python.exe --version` -> `Python 3.13.14`; cmd:`venv/Scripts/python.exe -m pytest --version` -> `pytest 9.1.1`; cmd:`ls node_modules/.bin/` filtered by `prettier` -> `prettier`; cmd:`node --version` -> `v24.18.0`; cmd:`docker info --format '{{.ServerVersion}}'` -> `failed to connect to the docker API`; code:`pyproject.toml:12` | 2026-10-03
F-22. The architecture tests check a closed plan dated on or after 2026-08-17, and on the tree at `032373e`, before this plan changed anything, all of them pass. | code:`tests/architecture/test_plan_document_contract.py:38`; cmd:`venv/Scripts/python.exe -m pytest tests/architecture -o addopts=-ra -q` -> `120 passed` | 2026-10-03
F-23. The naming registry is empty, and the naming standard gives no rule for the names of database objects beyond the example `CK_<table>_offset_pairs`. | doc:`docs/standards/naming_registry.md` section Current state; doc:`docs/standards/standard_naming.md` section Names of query constants; doc:`docs/standards/standard_time.md:70` | 2026-10-03
F-24. The closed plan of `plans_finished/routing_engine/` writes version 5 of the specification, with the state line replaced, a sentence on version 5 inserted right before "This document does not settle" and an item "- Version 5:" in the Decision provenance, inserts its decision entry as the next free decision of the MVP plan with the words "with the ordered nodes and coordinates of Q-10", moves the pointers to the specification to version 5, and needs, for every way of the pedestrian network, the ordered list of its nodes with the OpenStreetMap identifier and the coordinates of each node, stored and named by the task `FACT_SCHEMA`; that plan is implemented and the specification stands at version 5. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` line 70 D-11, lines 95 - 109 Step 1, lines 111 - 117 Step 2, line 121 step 3.1; doc:`docs/product/specification.md` line 3 `version 5`, line 9, line 279 `None at version 5.`, line 289 `- Version 5:` | 2026-10-03
F-25. At `032373e` the MVP plan has D-8 for the account sessions and D-9 for the routing engine as its last decision, and names Q-10 in D-4, in D-9, in the Risks item rewritten by `plans_finished/dependency_check/` and extended after D-8, in Q-9, in the five items of Q-10, in the closing note of Open questions and in two of its Supplementary files; the item of Supplementary files on the routing engine is the last one. | doc:`plans_finished/mvp/MVP_PLAN.md` line 31 D-4 `Q-10 stores the copy under that constraint`, line 39 `D-8. Account sessions`, line 41 D-9 `with the ordered nodes and coordinates of Q-10`, line 52 Risks, line 57 Q-9, lines 58 - 62, line 64, lines 75 and 76, line 77 | 2026-10-03
F-26. After `b5f03be` the registry entry Technical directions of the MVP plan says that `plans/fact_schema/` has its PRD confirmed and its plan still to be written, and its task `SCHEMA_REVISION` an interview in progress. | doc:`docs/standards/decision_registry.md` line 48 | 2026-10-03
F-27. After `b5f03be` the shape of the routing engine names `plans_finished/consistency_check/` in its item on version 4, and the task `SCHEMA_REVISION` has its seed and a shape with the interview in progress, which already names its trigger, the critical tests that run after it and PostGIS in the first revision. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_SHAPE.md` line 27; doc:`plans_finished/schema_revision/SCHEMA_REVISION_SEED.md`; doc:`plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md` line 3 and sections Recipient and trigger and Functional requirements | 2026-10-03
F-28. Since `c0b7bae` the password rules stand in M9 of the specification, the only rule of a pseudonym is uniqueness without regard to letter case, and the closed plan of `plans_finished/account_sessions/` decides a signed token and chooses no format of the password hash. | doc:`docs/product/specification.md` line 189, line 191; doc:`plans_finished/account_sessions/ACCOUNT_SESSIONS_PLAN.md` line 3 `plan closed`, line 26 D-3; doc:`plans_finished/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` line 76 `Password storage and the technical session mechanism are implementation decisions` | 2026-10-03
F-29. The seed of phase B, `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, which D-1 and the PRD describe as removed from the tree, is still in the tree, unchanged since it was added, and no branch ever removed it; commit `657d8da` holds it. | cmd:`git log --all --oneline --diff-filter=D -- plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md` -> no commit; cmd:`git diff 5a1d78e HEAD --stat -- plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md` -> no change; cmd:`git cat-file -e 657d8da:plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md` -> exists; doc:`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` line 21 | 2026-10-03
F-30. `plans_finished/routing_engine/` is archived with a final verdict for the whole initiative, and the archive keeps the findings of the shape of an archived initiative unchanged, only the location of its references may change. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_REVIEW.md` line 3, line 99; doc:`docs/standards/standard_agentic_workflow.md` line 192 | 2026-10-03

## Decisions

D-1. The initiative has two tasks. This task, `FACT_SCHEMA`, writes `docs/product/schema.md`, version 6 of the specification and the changes of the Scope of changes, and meets FR-16, AC-14 and AC-13 without its part about the stored data. The task `SCHEMA_REVISION`, whose seed is `plans_finished/schema_revision/SCHEMA_REVISION_SEED.md` and whose shape is `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md`, builds the first Alembic revision of that schema, the code of the rules that FR-15 and AC-1 - AC-12 need and their tests, and checks the part of AC-13 about the stored data, once the work package of D-7 of the MVP plan has built the local setup and the Alembic configuration and Q-11 the backend skeleton (F-2, F-3, F-11, F-27). The importer and the backend share one schema in one database: `docs/product/schema.md` describes it whole and says which of the two writes which table, and the revisions of the second task are the only chain both use. Decided by the user on 2026-10-03 in phase B, against this plan building the skeleton itself and against one plan waiting with open questions; the shared schema is the user's condition attached to that answer. The same day U-1 of `plans_finished/dependency_check/` made the same split independently and named the second task `SCHEMA_REVISION`, while phase B named it `FACT_SCHEMA_REVISION`; when the two lines met, the user kept the name `SCHEMA_REVISION`, and the seed of phase B, quoted verbatim in commit `657d8da` as `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, was removed from the tree because a task has one seed, with what it adds carried into the PRD and the shape of that task (F-1). The file was in fact still in the tree when this plan was implemented (F-29); the user decided on 2026-10-03 that step 7 removes it, against keeping it and correcting this entry and the PRD.

D-2. A fresh OpenStreetMap copy is stored in one transaction: the import upserts the ways and nodes of the copy with `INSERT ... ON CONFLICT`, deletes those the copy no longer holds, reconciles the facts by `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-10 and inserts the row of the copy into `osm_copy`, all in one commit. The tables of the copy carry no copy version. Decided by the user on 2026-10-03 in phase B, against a versioned copy switched in a last short transaction. It settles the storage left to Q-10 by D-9 there (F-15).

D-3. `docs/product/schema.md` is written in full by step 1 below: the DDL of the target state in `sql` blocks, one subsection per table with the meaning of every column, the rights of the service account, what the schema deliberately does not hold, and who writes what. Version 6 of the specification makes it part of the specification, and the standards map names it next to the specification as the target of a schema change. Decided by the user in the shape (question 2); the structure of the file is an agent decision at C:40, without asking.

D-4. The status of a fact, its sums and the date of its last confirmation are not stored: the rules layer derives them on every read from the votes of the fact, the window of k persons and the thresholds of `docs/product/specification.md` M4, the same for every fact (F-4, F-6), and the segment state is derived for every route. The schema stores only what votes cannot give: the source, the OpenStreetMap identity and the removal from OpenStreetMap. Agent decision at C:40, without asking: the shape left the choice to phase B with a measurement on the first import (F-17), which cannot exist before the stored data; a stored status would also have to be recomputed for every fact whenever k, x or a threshold changes, which a derived one never needs; the facts with votes are few in the MVP. A stored status can be added later by a normal revision if a measurement asks for it.

D-5. Every fact - a point report, a geozone, an OpenStreetMap fact and a fact converted from one - is one row of the table `fact`. A geozone is a fact with a radius, a column rather than a side table, because the relation is one-to-one (F-12). The lifecycle of M4 is held by three things: `source`, the OpenStreetMap identity kept after a conversion, and `is_removed_from_osm` for a fact outdated because OpenStreetMap removed it; a conversion sets `source` to `user_report` and keeps the identity, a return sets it back to `openstreetmap`. Only a barrier or an amenity the tag rules make present is an OpenStreetMap fact (F-4). A fact keeps no author: the author of a report is only the person of its first vote. Agent decision at C:40, without asking: one table lets votes, flags, the duplicate check and the window apply to every fact through one foreign key, as M4 and M5 require.

D-6. The OpenStreetMap copy is stored as three tables keyed by the OpenStreetMap identifiers: `osm_way` with the line of the way, the four barrier states of D-6 of the tag mapping, the `wheelchair=no` marking and whether the way is for motor traffic or a crossing; `osm_node` with its point, its kerb point and whether it is a crossing or on a way for motor traffic; and `osm_way_node` with the nodes of each way in order, which the segment combination of D-7 there needs (F-16). Only the elements of the pedestrian network are stored; which elements that is stays with `plans_finished/routing_engine/` and the import. The state `present` of a way stands next to the OpenStreetMap fact of that barrier on that way, which carries the votes and the number of steps; the import writes both in the transaction of D-2. An amenity of an element outside the network is a fact without a row in these tables, so `fact` has no foreign key to them. Raw tags are not stored, because a change of the tag rules is followed by a fresh import (D-14 of the tag mapping). Agent decision at C:40, without asking. `osm_way_node` and the point of `osm_node` also hold the ordered nodes with their OpenStreetMap identifiers and coordinates that the route graph of `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-11 needs (F-24), so that need asks nothing beyond this schema.

D-7. Every fact sits at a point, `geography(Point, 4326)`: for a way fact a point of the way chosen by the import, for an area the point of D-13 of the tag mapping. Ways and nodes use `geography` of the same reference system, and distances such as the 15 m of the duplicate check are given in metres through `ST_DWithin` on a GiST index. A query that needs the whole of a way fact reads the line of `osm_way` through the identity. Agent decision at C:40, without asking: metres without a projection, and one type for every geometry of the schema.

D-8. A vote is one row of `vote`, never updated except for clearing its hash, kept as history. Its person is `account_id` or `voter_hash`, never both, and after the account is deleted (`ON DELETE SET NULL`) or the hash is cleared after 30 days the vote has no person and counts as a person of its own (`docs/product/specification.md` M4, M9). `is_cast_with_account` records the kind of voter, from which the rules layer computes the weight of M4, so a deleted account keeps its weight of 1 and O2 can add a photo column later. The hash is `bytea` without a length check, because how it is computed belongs to the voting work package (PRD, Out of scope). Agent decision at C:40, without asking: the weights stay a rule in code, and the kind is the fact about the vote that survives both deletions.

D-9. The vote limit of M4 is refused by the database itself through two partial exclusion constraints, `EX_vote_account_limit` and `EX_vote_hash_limit`, over the fact, the person and the interval from `cast_at` to `repeat_allowed_at`. The rules layer writes `repeat_allowed_at` as `cast_at` plus x at the moment of the vote, so x stays configuration and a change of x applies to new votes only; the bound is a stored instant because `timestamptz + interval` cannot stand in a constraint expression (F-18). A vote is written with `INSERT ... ON CONFLICT DO NOTHING RETURNING id`, and no returned row means the vote was refused. Agent decision at C:40, without asking: the backstop lives in the database (F-12), unlike a hard unique constraint it lets a vote through once x has passed (F-14), and it needs no explicit lock; both behaviors were run on PostgreSQL (F-18).

D-10. A flag is the column pair `flagged_at` of the fact, written by the first flag, not a table: a flag keeps nothing about who flagged (M11), so further flags add nothing to keep. Hiding is the pair `hidden_at`, written by the moderator and cleared by a restore; only flagged content can be hidden. That an OpenStreetMap fact cannot be flagged and that a hidden fact cannot be voted on are rules of the rules layer, because they compare rows and the database holds no triggers (F-12). M11 names no way to dismiss a flag, so none is stored. Agent decision at C:40, without asking.

D-11. An account is a pseudonym, a password hash and a moderator flag set by hand. The pseudonym is unique without regard to letter case through `UX_account_pseudonym_lower` on `lower(pseudonym)` (F-19, M9), and neither text column has a length or format limit in the database, because the rules for both were question 4 of `plans_finished/account_sessions/` (F-10); that initiative enforces them at the input and chooses the hash format. Deleting an account deletes its row. Agent decision at C:40, without asking. Since `c0b7bae` the password rules stand in M9 and the pseudonym has no rule of length or format, while `plans_finished/account_sessions/` closed without choosing the format of the hash (F-28); the decision stands, the rules of M9 are checked where the input is accepted, and the schema fixes no format of the hash.

D-12. Closed lists are `text` domains with a check of the list - `fact_type`, `fact_source`, `osm_element_type`, `way_barrier_state`, `kerb_point_state`, `vote_verdict` - with English codes in snake case, and the code maps them to enumerations (`docs/standards/standard_database.md`, Queries in code). A new value is a revision that replaces the check of the domain. The radius list of a geozone and the barrier types allowed for it are checks of `fact`. Whether the programming interface reuses these codes is decided by `plans_finished/api_contract/`. Agent decision at C:40, without asking: a domain check is easier to change than an enum type and keeps the list in one place.

D-13. Instants follow F-13: every one is a pair, server-stamped ones take the offset of the Europe/Warsaw zone at the moment of writing, and `CK_fact_offset_pairs` guards the two nullable pairs; the pairs declared `NOT NULL` on both columns cannot be half written. `osm_copy.state_at` is the header instant of `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-4 with the offset it came with, 0 for a value in UTC. The date of the last OpenStreetMap edit is a `date`, `osm_edited_on`, the calendar day in Europe/Warsaw of D-15 of the tag mapping, computed by the import. Agent decision at C:40, without asking.

D-14. The free texts - `description`, `pseudonym`, `password_hash`, `file_name` - have deliberately no length limit in the database: the limits of user input are set where the input is accepted, by `plans_finished/api_contract/` for the description and `plans_finished/account_sessions/` for the account, and `file_name` comes from the checked name of D-3 of `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md`. Agent decision at C:40, without asking, to avoid guessing a contract owned elsewhere. Since `c0b7bae` the limits of the account are the rules of M9, checked where the input is accepted (F-28).

D-15. Database objects live in the schema `public`. Tables are singular nouns in snake case, and constraints and indexes carry the prefixes `PK_`, `FK_`, `UX_`, `CK_`, `EX_` and `IX_` followed by the table and the subject, unquoted, so PostgreSQL stores them in lower case (F-19, F-23). `naming_registry.md` gets these names from the task `SCHEMA_REVISION`, when the objects exist, because the registry records the actual state. Agent decision at C:40, without asking.

D-16. The schema needs the extensions `postgis` and `btree_gist`, the second for the constraints of D-9. Both are created by the first revision of the chain, applied by the schema owner of D-7 of the MVP plan (F-3); `btree_gist` comes with the server package of the image of that decision and is trusted, so the environment needs nothing more (F-20). Agent decision at C:40, without asking.

D-17. `docs/product/schema.md` states the rights of the service account table by table, derived from who writes what: read and insert on `osm_copy`; read, insert, update and delete on `osm_way`, `osm_node`, `osm_way_node` and `account`; read, insert and update on `fact` and `vote`; nothing else, and no right to create, alter or drop. The `GRANT` statements themselves are written by the revision of `SCHEMA_REVISION`, because the name of the account is an entry of the local environment files and never stands in the repository (F-3). Agent decision at C:40, without asking: permissions are part of the target state the revisions are reviewed against (F-12), and the import and the backend both run as the service account of D-7 of the MVP plan.

D-18. Version 6 of the specification only adds to version 5: it declares `docs/product/schema.md` part of the specification and the target of every schema revision, makes that the one exception to the sentence that the specification settles no technical solution, and records its provenance. No rule of version 4 or 5 changes, so everything built on them stays valid, and the pointers that name the version of the specification move to version 6 as they moved to version 5. Decided by the user on 2026-10-03 in phase B: version 4 was written by `plans_finished/consistency_check/` with the rules of this initiative (F-4), and a change needed here is a new version compatible with the one before. Numbered 6 instead of 5, and the pointers added, on 2026-10-03 by D-22.

D-19. `plans_finished/mvp/MVP_SHAPE.md` stays unchanged as the record of its interview, and the archived `plans_finished/local_database/` is not edited; the constraints on extensions and rights reach the MVP through D-9 of the MVP plan. The shapes of the contract, the routing engine and the sessions already carry the PRD of this initiative (F-7), so each gets one item with what the schema adds to it. Agent decision at C:40, without asking.

D-20. This plan is written for the tree after the branch `rm/requirements-preparation` up to `fff8e88` is merged, and it does not merge it. `plan-implement` starts only when that commit is an ancestor of the working branch; until then the quoted passages of the Scope of changes do not exist in the working tree. Decided by the user on 2026-10-03 in phase B, against merging that branch into the branch of this task now and against a plan written for the tree without it. On 2026-10-03 `dev` was merged into `rm/requirements-preparation`, whose commit `b5f03be` carries the changes after the gate that this plan now quotes (F-25 - F-27), so the commit that has to be an ancestor is `b5f03be`, which has `fff8e88` as its own.

D-21. The task `SCHEMA_REVISION` continues the interview of its shape and reads this plan and `docs/product/schema.md` as its inputs. It turns AC-1 - AC-12 into tests under `docs/standards/standard_tests.md` - critical tests for every refusal of FR-15, for the round trip of an offset and for the rights of D-17, and scenario tests for the status runs, among them a run where the window of k persons changes the status, as U-7 of `plans_finished/consistency_check/` asks (F-6). It may change `docs/product/schema.md` only through a new version of the specification approved by the user. Agent decision at C:40, without asking.

D-22. This plan and the plan of `plans_finished/routing_engine/` both wrote version 5 of the specification and the next decision of the MVP plan (F-24). The routing engine takes version 5 and D-8, and this plan writes version 6 and D-9 and is implemented after the routing engine, so its steps quote the files as that implementation leaves them. The routing engine skips its step 3.3, the Q-10 input of its D-11, and its step 8, the sentence in the Dependencies of the PRD of this initiative, because D-6 already stores what D-11 there needs; step 3 below still removes the five items of Q-10 and replaces the "Q-10" that the decision entry D-8 of the routing engine names. Decided by the user on 2026-10-03 in the session that implements `plans_finished/routing_engine/`, which reported it to the session that merged `dev`. The account sessions then took D-8 and the routing engine D-9 (F-25), so this plan writes the next free decision number of the MVP plan, read right before step 3.1, as D-N, and step 3.9 replaces the "Q-10" of D-9.

D-23. Corrections made before implementation for the tree at `032373e`, where the quoted passages of steps 3.2 and 4 no longer matched: step 3.2 replaces the fragments of the Risks item that name Q-10 as it stands now, and step 4 the whole clause on this initiative in the registry; steps 3.8 and 3.9 replace the "Q-10" of D-4 and D-9 of the MVP plan, and step 3.7 the two Supplementary files that name it, which the Definition of Done asks and F-25 lists; step 6.2 is dropped, because the shape it edits is archived and the archive keeps its findings (F-30), the Definition of Done keeps `plans_finished/` unchanged, and D-6 already gives the routing engine what it asked (D-22); the text of step 6.3 follows F-28. Agent decision at C:40, without asking. Step 7, which removes the seed of phase B (F-29), was decided by the user on 2026-10-03 (D-1).

## Scope of changes

Texts to insert are given in fenced blocks and are inserted without the fence. Every existing file is read again right before it is edited; when a quoted passage no longer matches the file, the step stops and the difference goes to the user. YYYY-MM-DD is the day of the edit; in steps 2.4 and 2.5 it is the day of the user's approval. D-N is the next free decision number of `plans_finished/mvp/MVP_PLAN.md`, read right before step 3.1 and the same in every step (D-22).

### Step 1. `docs/product/schema.md`, new file

Create the file with this content:

````text
# Target database schema

Document state: YYYY-MM-DD, part of `docs/product/specification.md` version 6

## Why this document exists

This is the target state of the database schema of the app: the extensions, domains, tables, constraints, indexes and the rights of the service account. It is part of the product specification (`docs/product/specification.md`, section Why this document exists), and it is changed and approved like the specification, by the user, as a new version of it. Every Alembic revision is reviewed line by line against it (`docs/standards/standard_database.md`, Form of schema changes). It says what the schema is supposed to be, not what a server holds; the actual state is the schema dump, once the project keeps one.

The import of OpenStreetMap data and the backend read and write this one schema in one database. Neither has a schema or a database of its own; the section Who writes what says which of them writes which table.

## Conventions

- PostgreSQL 18, with the extensions `postgis` and `btree_gist`, in the schema `public`. The first revision of the chain creates both extensions and is applied by the schema owner account.
- A table is a singular noun in snake case. Constraints and indexes carry the prefix `PK_`, `FK_`, `UX_` (unique), `CK_` (check), `EX_` (exclusion) or `IX_`, then the table and the subject, unquoted.
- An instant is a pair of `timestamptz(3)` and `<column>_utc_offset_minutes` (`docs/standards/standard_time.md`); a calendar day is a `date`.
- A closed list is a `text` domain with a check of its values; the code maps it to an enumeration.
- Every geometry is `geography` in the reference system 4326, so distances are in metres.
- Free texts have no length limit in the database; the limits of user input are set where the input is accepted.
- The database holds no status, no sum of votes and no domain rule, only integrity constraints: the rules of `docs/product/specification.md` M4 are applied by the code to the stored votes.

## Extensions and domains

```sql
CREATE EXTENSION postgis;

CREATE EXTENSION btree_gist;

CREATE DOMAIN utc_offset_minutes AS smallint
    CONSTRAINT CK_utc_offset_minutes_range CHECK (VALUE BETWEEN -840 AND 840);

CREATE DOMAIN fact_type AS text
    CONSTRAINT CK_fact_type_closed_list CHECK (VALUE IN ('stairs', 'high_kerb', 'poor_surface', 'steep_incline', 'narrow_passage', 'ramp', 'elevator', 'lowered_kerb', 'accessible_toilet', 'rest_place', 'handrail_at_stairs'));

CREATE DOMAIN fact_source AS text
    CONSTRAINT CK_fact_source_closed_list CHECK (VALUE IN ('openstreetmap', 'user_report'));

CREATE DOMAIN osm_element_type AS text
    CONSTRAINT CK_osm_element_type_closed_list CHECK (VALUE IN ('node', 'way', 'relation'));

CREATE DOMAIN way_barrier_state AS text
    CONSTRAINT CK_way_barrier_state_closed_list CHECK (VALUE IN ('present', 'absent', 'absent_by_default', 'unknown'));

CREATE DOMAIN kerb_point_state AS text
    CONSTRAINT CK_kerb_point_state_closed_list CHECK (VALUE IN ('high', 'lowered', 'unknown'));

CREATE DOMAIN vote_verdict AS text
    CONSTRAINT CK_vote_verdict_closed_list CHECK (VALUE IN ('confirm', 'deny'));
```

- `fact_type` is the closed list of M3: the barriers stairs, high kerb, poor surface, steep incline and narrow passage, and the amenities ramp, elevator, lowered kerb, accessible toilet, rest place and handrail at stairs.
- `fact_source` is the source a fact shows (M10). A fact converted from OpenStreetMap shows `user_report` (M4).
- `way_barrier_state` is the state the tag rules of M6 give a barrier on a way; `absent_by_default` exists only for stairs.
- `kerb_point_state` is the kerb at a node, high, lowered or unknown.
- `vote_verdict` is a confirmation that a fact is still there or a denial that it is.

## OpenStreetMap copy

```sql
CREATE TABLE osm_copy (
    id bigint GENERATED ALWAYS AS IDENTITY,
    state_at timestamptz(3) NOT NULL,
    state_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    file_name text NOT NULL,
    made_current_at timestamptz(3) NOT NULL,
    made_current_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    CONSTRAINT PK_osm_copy PRIMARY KEY (id),
    CONSTRAINT UX_osm_copy_state_at UNIQUE (state_at)
);

CREATE TABLE osm_way (
    id bigint NOT NULL,
    geog geography(LineString, 4326) NOT NULL,
    stairs_state way_barrier_state NOT NULL,
    poor_surface_state way_barrier_state NOT NULL,
    steep_incline_state way_barrier_state NOT NULL,
    narrow_passage_state way_barrier_state NOT NULL,
    is_marked_wheelchair_no boolean NOT NULL,
    is_motor_traffic boolean NOT NULL,
    is_crossing boolean NOT NULL,
    CONSTRAINT PK_osm_way PRIMARY KEY (id),
    CONSTRAINT CK_osm_way_stairs_state CHECK (stairs_state IN ('present', 'absent_by_default')),
    CONSTRAINT CK_osm_way_absent_by_default_only_stairs CHECK (poor_surface_state <> 'absent_by_default' AND steep_incline_state <> 'absent_by_default' AND narrow_passage_state <> 'absent_by_default')
);

CREATE INDEX IX_osm_way_geog ON osm_way USING gist (geog);

CREATE TABLE osm_node (
    id bigint NOT NULL,
    geog geography(Point, 4326) NOT NULL,
    kerb_point kerb_point_state NULL,
    is_crossing boolean NOT NULL,
    is_on_motor_traffic_way boolean NOT NULL,
    CONSTRAINT PK_osm_node PRIMARY KEY (id)
);

CREATE TABLE osm_way_node (
    way_id bigint NOT NULL,
    sequence_index integer NOT NULL,
    node_id bigint NOT NULL,
    CONSTRAINT PK_osm_way_node PRIMARY KEY (way_id, sequence_index),
    CONSTRAINT FK_osm_way_node_way FOREIGN KEY (way_id) REFERENCES osm_way (id) ON DELETE CASCADE,
    CONSTRAINT FK_osm_way_node_node FOREIGN KEY (node_id) REFERENCES osm_node (id),
    CONSTRAINT CK_osm_way_node_sequence_index CHECK (sequence_index >= 0)
);

CREATE INDEX IX_osm_way_node_node_id ON osm_way_node (node_id);
```

- `osm_copy` has one row for every copy made current, never changed afterwards. The copy in use is the row with the latest `state_at`, the instant of the OpenStreetMap state the copy reflects, with the offset it came with; the app shows its calendar day in Europe/Warsaw (M6). `file_name` is the dated name of the downloaded file.
- `osm_way` holds every way of the pedestrian network of the copy in use, keyed by its OpenStreetMap identifier, with its line and the state of each of stairs, poor surface, steep incline and narrow passage by the tag rules of M6. `is_marked_wheelchair_no` is the marking of M7, `is_motor_traffic` says the way is for motor traffic by M6, and `is_crossing` says it is tagged as a crossing. A state `present` stands next to the OpenStreetMap fact of the same barrier on the same way in `fact`, which carries its votes and its number of steps; an absent, absent by default or unknown state is an attribute of the way, not a fact (M4).
- `osm_node` holds every node of those ways, with its point, its kerb point or null when it is not one, whether it is tagged as a crossing and whether it also belongs to a way for motor traffic.
- `osm_way_node` holds the nodes of each way in their order, from 0.

## Facts

```sql
CREATE TABLE fact (
    id bigint GENERATED ALWAYS AS IDENTITY,
    fact_type fact_type NOT NULL,
    source fact_source NOT NULL,
    geog geography(Point, 4326) NOT NULL,
    geozone_radius_m smallint NULL,
    description text NULL,
    step_count smallint NULL,
    is_sample boolean NOT NULL,
    osm_element_type osm_element_type NULL,
    osm_element_id bigint NULL,
    osm_edited_on date NULL,
    is_removed_from_osm boolean NOT NULL,
    created_at timestamptz(3) NOT NULL,
    created_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    flagged_at timestamptz(3) NULL,
    flagged_at_utc_offset_minutes utc_offset_minutes NULL,
    hidden_at timestamptz(3) NULL,
    hidden_at_utc_offset_minutes utc_offset_minutes NULL,
    CONSTRAINT PK_fact PRIMARY KEY (id),
    CONSTRAINT UX_fact_osm_identity UNIQUE (osm_element_type, osm_element_id, fact_type),
    CONSTRAINT CK_fact_osm_identity_complete CHECK ((osm_element_type IS NULL) = (osm_element_id IS NULL)),
    CONSTRAINT CK_fact_osm_edited_on_with_identity CHECK ((osm_element_id IS NULL) = (osm_edited_on IS NULL)),
    CONSTRAINT CK_fact_openstreetmap_has_identity CHECK (source = 'user_report' OR osm_element_id IS NOT NULL),
    CONSTRAINT CK_fact_removed_only_openstreetmap CHECK (NOT is_removed_from_osm OR source = 'openstreetmap'),
    CONSTRAINT CK_fact_user_content_without_identity CHECK (osm_element_id IS NULL OR (description IS NULL AND geozone_radius_m IS NULL AND NOT is_sample)),
    CONSTRAINT CK_fact_geozone CHECK (geozone_radius_m IS NULL OR (geozone_radius_m IN (10, 25, 50, 100) AND fact_type IN ('stairs', 'high_kerb', 'poor_surface', 'steep_incline', 'narrow_passage'))),
    CONSTRAINT CK_fact_step_count CHECK (step_count IS NULL OR (step_count > 0 AND fact_type = 'stairs')),
    CONSTRAINT CK_fact_offset_pairs CHECK ((flagged_at IS NULL) = (flagged_at_utc_offset_minutes IS NULL) AND (hidden_at IS NULL) = (hidden_at_utc_offset_minutes IS NULL)),
    CONSTRAINT CK_fact_hidden_only_flagged CHECK (hidden_at IS NULL OR flagged_at IS NOT NULL)
);

CREATE INDEX IX_fact_geog ON fact USING gist (geog);

CREATE INDEX IX_fact_flagged_at ON fact (flagged_at) WHERE flagged_at IS NOT NULL;
```

- A fact is a barrier or an amenity of `fact_type` at the point `geog`: a point report, a geozone, a fact from OpenStreetMap or a fact converted from one (M3 - M6). A fact from OpenStreetMap is an item the tag rules of M6 make present. For a fact of a way the point lies on the way, and the line of the way is in `osm_way`.
- A geozone is a fact with `geozone_radius_m` of 10, 25, 50 or 100 m and a barrier type (M5).
- `description` and `step_count` are the optional description and number of steps of M3; `step_count` also holds the number of steps OpenStreetMap gives. `is_sample` marks sample data (M10). A saved fact is never edited by a user (M3, M5).
- `osm_element_type`, `osm_element_id` and `fact_type` are the identity of a fact from OpenStreetMap, unique for every fact that came from OpenStreetMap, converted and outdated ones included; a fact reported by a user has none. `osm_edited_on` is the calendar day in Europe/Warsaw of the last edit of that element (M4).
- `source` is `openstreetmap` for a fact of the copy and `user_report` otherwise. A fact a fresh copy no longer holds either becomes `user_report` with its identity kept, or keeps `openstreetmap` with `is_removed_from_osm`, which makes it outdated with the reason that it was removed in OpenStreetMap; a fact that returns becomes `openstreetmap` again without that mark (M4).
- `flagged_at` is the first flag of the fact; a flag keeps nothing about who flagged (M11). `hidden_at` is set when a moderator hides flagged content and cleared when they restore it.
- The status of a fact, its sums and the date of its last confirmation are not columns: the code derives them from `vote` by M4, the same for every fact.

## Accounts and votes

```sql
CREATE TABLE account (
    id bigint GENERATED ALWAYS AS IDENTITY,
    pseudonym text NOT NULL,
    password_hash text NOT NULL,
    is_moderator boolean NOT NULL,
    created_at timestamptz(3) NOT NULL,
    created_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    CONSTRAINT PK_account PRIMARY KEY (id)
);

CREATE UNIQUE INDEX UX_account_pseudonym_lower ON account (lower(pseudonym));

CREATE TABLE vote (
    id bigint GENERATED ALWAYS AS IDENTITY,
    fact_id bigint NOT NULL,
    verdict vote_verdict NOT NULL,
    is_cast_with_account boolean NOT NULL,
    account_id bigint NULL,
    voter_hash bytea NULL,
    cast_at timestamptz(3) NOT NULL,
    cast_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    repeat_allowed_at timestamptz(3) NOT NULL,
    repeat_allowed_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    CONSTRAINT PK_vote PRIMARY KEY (id),
    CONSTRAINT FK_vote_fact FOREIGN KEY (fact_id) REFERENCES fact (id),
    CONSTRAINT FK_vote_account FOREIGN KEY (account_id) REFERENCES account (id) ON DELETE SET NULL,
    CONSTRAINT CK_vote_account_only_with_account CHECK (is_cast_with_account OR account_id IS NULL),
    CONSTRAINT CK_vote_hash_only_without_account CHECK (NOT is_cast_with_account OR voter_hash IS NULL),
    CONSTRAINT CK_vote_repeat_after_cast CHECK (repeat_allowed_at > cast_at),
    CONSTRAINT EX_vote_account_limit EXCLUDE USING gist (fact_id WITH =, account_id WITH =, tstzrange(cast_at, repeat_allowed_at) WITH &&) WHERE (account_id IS NOT NULL),
    CONSTRAINT EX_vote_hash_limit EXCLUDE USING gist (fact_id WITH =, voter_hash WITH =, tstzrange(cast_at, repeat_allowed_at) WITH &&) WHERE (voter_hash IS NOT NULL)
);

CREATE INDEX IX_vote_fact_id_cast_at ON vote (fact_id, cast_at);

CREATE INDEX IX_vote_account_id ON vote (account_id) WHERE account_id IS NOT NULL;

CREATE INDEX IX_vote_cast_at_with_voter_hash ON vote (cast_at) WHERE voter_hash IS NOT NULL;
```

- An account is a pseudonym, unique without regard to letter case, a password hash and the moderator role assigned by hand (M9, M11). Deleting an account deletes its row and nothing else.
- A vote confirms or denies a fact. Its person is the account or the hashed identifier of M9, never both; `is_cast_with_account` keeps the kind of voter, from which the code takes the weight of M4. The report of a user carries the confirmation of its author as its first vote.
- `repeat_allowed_at` is the instant from which the same person may vote on the same fact again, written as `cast_at` plus the waiting time of M4. The two exclusion constraints refuse a vote of the same person on the same fact before that instant.
- When the account is deleted or the hash is cleared 30 days after `cast_at`, the vote stays with its weight and has no person any more, so it counts as a person of its own (M4, M9). Votes are never deleted.

## Rights of the service account

The schema owner account creates and owns every object, and the service account of the running app, the import included, owns nothing (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-5). The revisions grant the service account exactly these rights and no right to create, alter or drop an object:

| Table                                        | Rights                         |
| -------------------------------------------- | ------------------------------ |
| `osm_copy`                                   | select, insert                 |
| `osm_way`, `osm_node`, `osm_way_node`        | select, insert, update, delete |
| `fact`, `vote`                               | select, insert, update         |
| `account`                                    | select, insert, update, delete |

The name of the service account is an entry of the local environment files, so the `GRANT` statements stand in the revisions with that name supplied when they are applied, never in this document.

## What the schema does not hold

- The status of a fact, its sums and the date of its last confirmation, derived from the votes (M4).
- The state of a route segment, derived for each route from the copy, the profile in the route request and the facts (M7).
- The preference profile, the current location and the routes, which are never stored (M1, M2).
- The sessions of logged-in users, decided in `plans_finished/account_sessions/`.
- The database itself and its accounts, created by the local setup and not by a revision.

## Who writes what

- The import writes `osm_copy`, `osm_way`, `osm_node`, `osm_way_node` and the facts with an OpenStreetMap identity: a fresh copy, the reconciliation of its facts and its row in `osm_copy` in one transaction, which upserts the ways, nodes and facts of the copy and deletes the ways and nodes it no longer holds.
- The backend writes the facts without an OpenStreetMap identity - reports and geozones - the votes on every fact, the accounts, and `flagged_at` and `hidden_at`.
- The periodic task of the worker clears `voter_hash` 30 days after `cast_at`.
- No one deletes a fact or a vote.
````

### Step 2. `docs/product/specification.md`, version 6

2.1. Replace the whole state line, which starts "Document state:" and names version 5 of `plans_finished/routing_engine/`, with:

```text
Document state: YYYY-MM-DD, version 6 - the target database schema in `docs/product/schema.md`, decided in `plans_finished/fact_schema/`, made part of this specification
```

2.2. In the section Why this document exists, replace the sentence "This document does not settle the technology stack or any technical solution - those are chosen in phase B of `plan-prd`." with:

```text
Version 6 makes the target database schema in `docs/product/schema.md`, decided in `plans_finished/fact_schema/`, part of this specification, without changing any rule of version 5. This document does not settle the technology stack or any technical solution - those are chosen in phase B of `plan-prd` - with one exception: the target database schema in `docs/product/schema.md` is part of this specification, is changed and approved like it, and is the target every schema revision is reviewed against.
```

2.3. In the section Open questions, replace the sentence that begins "None at version" with "None at version 6."

2.4. In the section Decision provenance, after the bullet that starts "- Version 5:", insert the bullet:

```text
- Version 6: the target database schema in `docs/product/schema.md` was decided in phase B of `plans_finished/fact_schema/`. That it is part of this specification, in a separate file, was decided by the user in the shape interview of that initiative; one schema for the import and the backend, the split of the initiative into the schema and its first revision, the storage of a fresh copy of OpenStreetMap in one transaction and a new version that changes no rule of the one before were decided by the user in its phase B; the tables, columns, constraints and rights were proposed by the agent. The user approved this version on YYYY-MM-DD.
```

2.5. The pointers to the version of the specification follow, as step 2 of `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` moved them to version 5 (D-18): in `PRODUCT.md`, "`docs/product/specification.md`, version 5" becomes "`docs/product/specification.md`, version 6" in both places; in `plans_finished/mvp/MVP_PLAN.md`, Goal, "`docs/product/specification.md`, version 5," becomes "`docs/product/specification.md`, version 6,"; in `plans_finished/mvp/MVP_PRD.md`, "of the specification, version 5," in Scope and "The rules are those of the specification, version 5," in Domain rules name version 6, while "still carries rules that version 4 replaced" stays as it is, and the item of its section Domain rules that begins "Changed after the gate on 2026-10-03, to follow version 4" gets the sentence "Scope and the first sentence of this section name version 6 since YYYY-MM-DD, which adds the target database schema of `plans_finished/fact_schema/` and changes none of this PRD." appended.

### Step 3. `plans_finished/mvp/MVP_PLAN.md`

3.1. In Decisions, after the last decision entry, append:

```text
D-N. Domain model and database schema of facts and votes, settling the former Q-10. The target schema is `docs/product/schema.md`, part of `docs/product/specification.md` since version 6, with the rules of votes, statuses, flags and hiding of version 4, as `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-1 - D-21 decide. Constraints for the rest of this plan: the import and the backend write one shared schema, the import the OpenStreetMap tables and the facts with an OpenStreetMap identity, the backend the reports, geozones, votes, accounts, flags and hiding (D-1 there); a fresh copy is written in one transaction together with its reconciliation and its date (D-2 there); the status of a fact and the date of its last confirmation are derived from the votes on every read and never stored, and the segment state is derived for every route (D-4 there); a vote is written with `INSERT ... ON CONFLICT DO NOTHING`, where no returned row means the vote limit refused it (D-9 there); the database itself refuses the states of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-15; the first revision creates `postgis` and `btree_gist` and grants the service account of D-7 only the rights listed in the schema (D-16, D-17 there). The schema is built by the task `SCHEMA_REVISION` of `plans_finished/schema_revision/` once the local setup and the Alembic configuration of D-7 and the backend skeleton of Q-11 exist, and the work packages of the import, the voting, the accounts, the moderation and the route build on that revision. Decided on 2026-10-03 in `plans_finished/fact_schema/`: the rules by the user in place of the db person, whose ruling is still to be confirmed, the split into two tasks and the storage of a fresh copy by the user, the rest by the agent at C:40.
```

3.2. In Risks, in the item that begins "The open questions depend on each other", replace "Q-10 depends only on the rules of D-5 and on one question of the former Q-2, now D-4, both settled on 2026-10-03, and closes with the task `FACT_SCHEMA` of `plans/fact_schema/`, not with its schema revision" with "the former Q-10 is settled as D-N by the task `FACT_SCHEMA` of `plans_finished/fact_schema/`, not by its schema revision"; replace "and adapts to the ways and points Q-10 stores" with "and adapts to the ways and points D-N stores"; replace "from the PRD of Q-10," with "from the PRD of the former Q-10," and "from the target schema of Q-10," with "from the target schema of D-N,"; replace "Q-9 depends on Q-10 and Q-6 and not on Q-1" with "Q-9 depends on D-N and Q-6 and not on Q-1"; replace "The critical paths are Q-10 -> Q-6 -> Q-9 and Q-7 -> Q-11, and" with "The critical path is Q-7 -> Q-11, and"; and replace "which stays with Q-10, so the path Q-10 -> Q-9 remains." with "which D-N settles in the target schema."

3.3. In Open questions, item Q-9, replace "Depends on Q-10 for the resources and statuses it exposes" with "Depends on D-N for the resources and statuses it exposes", and replace "the route response carries the segment states of Q-10," with "the route response carries the segment states derived from the data of D-N,".

3.4. In Open questions, remove the five items that begin "- Q-10. The domain model and database schema of facts and votes", "- Q-10 inputs from `plans_finished/osm_data_source/OSM_DATA_SOURCE_SHAPE.md`", "- Q-10 inputs from `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6", "- Q-10 inputs from `plans_finished/osm_data_source/`, settling" and "- Q-10 caveats:".

3.5. In Open questions, at the end of item Q-11, append: " The task `SCHEMA_REVISION` of `plans_finished/schema_revision/` waits for the backend skeleton decided here, next to the Alembic configuration of D-7, to build the schema of D-N."

3.6. In the last item of Open questions, replace "Q-10 was narrowed to the domain model" with "The former Q-10 was narrowed to the domain model", replace "because the former condition of Q-10 " with "because its former condition ", and replace "The owners of Q-10 and Q-11 were proposed by the agent." with "The owners of the former Q-10 and of Q-11 were proposed by the agent."

3.7. In Supplementary files, after the last item, which begins "- `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md`", append the item "- `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md`, the decision behind D-N."; in the item that begins "- `plans_finished/consistency_check/CONSISTENCY_CHECK_REVIEW.md`", replace "the changes to Q-9, Q-10 and the Risks" with "the changes to Q-9, the former Q-10 and the Risks"; in the item that begins "- `plans_finished/dependency_check/DEPENDENCY_CHECK_REVIEW.md`", replace "the closing of Q-10" with "the closing of the former Q-10".

3.8. In D-4, replace "and Q-10 stores the copy under that constraint" with "and D-N stores the copy under that constraint".

3.9. In D-9, replace "with the ordered nodes and coordinates of Q-10" with "with the ordered nodes and coordinates of D-N".

### Step 4. `docs/standards/decision_registry.md`

In the entry Technical directions of the MVP plan, item Blocks, replace "`plans/fact_schema/` has its PRD confirmed and its plan still to be written, and its task `SCHEMA_REVISION` an interview in progress;" with "`plans_finished/fact_schema/` decided the model and the target schema `docs/product/schema.md` in its task `FACT_SCHEMA` (`plans_finished/mvp/MVP_PLAN.md` D-N), and its task `SCHEMA_REVISION`, with its interview in progress, builds the first revision once the local setup, the Alembic configuration and the backend skeleton exist;".

### Step 5. `docs/standards/README.md`

5.1. In the section Project documents outside the standards, replace "- `docs/product/` - the product specification, `docs/product/specification.md`, written by the team." with "- `docs/product/` - the product specification, `docs/product/specification.md`, written by the team, with the target database schema in `docs/product/schema.md`, part of the specification since version 6."

5.2. In the table What to open before a task, in the row "Anything that touches a table, column, view or schema", replace "the product specification for the target" with "the product specification with `docs/product/schema.md` for the target", and realign the table with prettier.

### Step 6. Shapes of the sibling initiatives

6.1. `plans_finished/api_contract/API_CONTRACT_SHAPE.md`, section Current state: after the item that begins "- The user decided on 2026-10-03 in `plans_finished/consistency_check/` (U-1 and U-2 of its review)", insert:

```text
- `plans_finished/fact_schema/` decided on 2026-10-03 the target schema behind the resources of this contract (`docs/product/schema.md`; `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-4, D-9, D-12): the closed lists are stored as English codes in snake case, which the contract may reuse or map; the status of a fact and the date of its last confirmation are derived on every read, never stored; and a vote refused by the vote limit is a normal outcome of the write, not an error, so the contract needs an answer for it.
```

6.2. Dropped on 2026-10-03 before implementation (D-23): it inserted an item into `plans_finished/routing_engine/ROUTING_ENGINE_SHAPE.md`, the shape of an archived initiative.

6.3. `plans_finished/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, section Current state: after the item that begins "- `plans_finished/fact_schema/` decided on 2026-10-03 the stored data of accounts and votes", insert:

```text
- `plans_finished/fact_schema/` decided on 2026-10-03 the target schema of accounts (`docs/product/schema.md`; `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-11): a pseudonym unique through `lower(pseudonym)`, a password hash and a moderator flag set by hand, with no length or format limit on either text in the database, so the password rules of `docs/product/specification.md` M9 are checked where the input is accepted, and the schema fixes no format of the hash.
```

### Step 7. `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, removed

Remove the file with the native file removal command, not `git rm`, after checking that it is unchanged since commit `657d8da`, which keeps it in the history (F-29, D-1). Then, in Supplementary files of this plan, replace the item that begins "- `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`" with "- `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md` at `657d8da`, the verbatim request of phase B that split the task `SCHEMA_REVISION` out of this one, removed from the tree on YYYY-MM-DD (D-1)."

## Rollout order

1. Check that `b5f03be` is an ancestor of the working branch with `git merge-base --is-ancestor b5f03be HEAD`. If it is not, stop and tell the user that the branch `rm/requirements-preparation` has to reach this branch first (D-20).
2. Step 1, then step 2 without the approval date of 2.4.
3. Show the user `docs/product/schema.md` and the diff of `docs/product/specification.md` and ask for the approval of version 6. On approval, write its date into 2.4 and continue; on any requested change, stop and change this plan first, because the schema is the contract of steps 3 - 6 and of the task `SCHEMA_REVISION`.
4. Steps 3 - 7 in any order, each file read again right before its edit, with the stop on a passage that no longer matches.
5. `npx --no-install prettier --write` on every changed or created markdown file, after `npm ci` when prettier is not installed, then the checks of the Definition of Done.

Steps for a human: bringing `rm/requirements-preparation` into this branch, through `dev` or directly, before step 1; the approval of version 6 of the specification with `docs/product/schema.md` in step 3; the commit and the Merge Request of the changed files, the removal of step 7 included.

## Definition of Done

- `docs/product/schema.md` exists with the content of step 1, and `docs/product/specification.md` carries exactly the changes of step 2, with the date of the user's approval in 2.4; no rule of version 4 or 5 is changed.
- `plans_finished/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md`, `docs/standards/README.md` and the two shapes of steps 6.1 and 6.3 carry exactly the changes of steps 3 - 6; `plans_finished/mvp/MVP_SHAPE.md` and `plans_finished/` are unchanged.
- `plans_finished/mvp/MVP_PLAN.md` has D-N, no item that begins with Q-10 under Open questions, and no reference to Q-10 outside "the former Q-10".
- `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md` is no longer in the tree, and the Supplementary files of this plan carry the item of step 7.
- `npx --no-install prettier --check` passes on every changed or created markdown file and on the files of `plans_finished/fact_schema/`.
- The changed and created files contain none of the characters forbidden by `docs/standards/standard_formatting.md` and no bold in prose.
- `python -m pytest tests/architecture -o addopts=-ra` in a Python 3.13 environment reports no violation in a file this plan changes or creates or in `plans_finished/fact_schema/`, the check of this closed plan by `tests/architecture/test_plan_document_contract.py` included. Violations outside them that the tree already has (F-22) are not part of this plan.
- The review of `plan-implement` finds no blocking issue.

## Risks

- The plan cannot start before `rm/requirements-preparation` reaches this branch (D-20). If that branch changes again before it is merged, a quoted passage may stop a step.
- The rules were decided by the user in place of the db person, and the OpenStreetMap rules for the import person; either ruling can still change the specification and the schema (PRD, Risks and notes).
- The DDL of `docs/product/schema.md` has run only in its parts without PostGIS, on PostgreSQL 15 (F-18, F-19). The `geography` columns, their GiST indexes and the rights run first in the task `SCHEMA_REVISION` on PostgreSQL 18, and an error found there is a new version of the specification.
- The stored data waits for the local setup and the Alembic configuration of D-7 of the MVP plan and for the backend skeleton of Q-11. Every hour of that wait is taken from the import, voting and route work packages that build on the revision, before the Kraków deadline at 11:00 on 4 October 2026.
- The state `present` of a way and the OpenStreetMap fact of that barrier are kept in step only by the import transaction, not by a constraint, because the database holds no cross-table rule (D-6).
- The status is derived on every read (D-4); its cost has not been measured. If a route over many voted facts is slow, a revision adds a stored status and the rules layer keeps it up to date.
- Not decided anywhere, and to be asked by the task or work package that meets it: whether a hidden or flagged converted fact that returns in a fresh copy as an OpenStreetMap fact stays hidden; the schema allows either.
- M11 names no way to dismiss a flag, so the moderator view keeps every flagged fact for ever (D-10). In the demo that is a short list.
- Other sessions edit `plans_finished/mvp/MVP_PLAN.md`, the registry and the sibling shapes; a quoted passage that changed stops its step (Scope of changes).
- The machine of the implementing session has no running Docker engine (F-21), so nothing of the DDL runs in this task; that stays with the task `SCHEMA_REVISION`, as the risk on the DDL above says.

## Open questions

None.

## Supplementary files

- `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`, the contract of both tasks of this initiative.
- `plans_finished/fact_schema/FACT_SCHEMA_SHAPE.md`, the domain rules and scenarios behind the PRD.
- `plans_finished/fact_schema/FACT_SCHEMA_SEED.md`, the verbatim request of this task.
- `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md` at `657d8da`, the verbatim request of phase B that split the task `SCHEMA_REVISION` out of this one, removed from the tree on 2026-10-03 (D-1).
- `plans_finished/schema_revision/SCHEMA_REVISION_SEED.md` and `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md`, the seed and the shape of the task `SCHEMA_REVISION`.
- `plans/consistency_check/CONSISTENCY_CHECK_REVIEW.md` at `fff8e88`, the decisions U-1 - U-8 behind version 4 of the specification.
