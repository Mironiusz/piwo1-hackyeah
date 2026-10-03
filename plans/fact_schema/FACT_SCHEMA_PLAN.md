# Plan: Domain model and database schema of facts and votes for the MVP

Document state: 2026-10-03, plan closed

## Goal

Carry out the task `FACT_SCHEMA` of `plans/fact_schema/FACT_SCHEMA_PRD.md`: write the target schema that holds FR-1 - FR-13 as `docs/product/schema.md`, part of the product specification, together with version 4 of `docs/product/specification.md` and the changes to `plans/mvp/MVP_PRD.md` that the rules require (FR-14), and meet AC-13. Close Q-10 of `plans/mvp/MVP_PLAN.md` with the constraints the schema puts on the rest of the MVP, and hand the sibling initiatives what they read from it. No code and no revision are written here: the stored data of FR-15 and AC-1 - AC-12 are the task `FACT_SCHEMA_REVISION` of this initiative (D-1).

## Facts

F-1. The PRD of this initiative passed its gate on 2026-10-03 with x = 1 day and k = 5 approved by the user in place of the db person, and since phase B of this task it splits the initiative into the tasks `FACT_SCHEMA` and `FACT_SCHEMA_REVISION`. | doc:`plans/fact_schema/FACT_SCHEMA_PRD.md` section Scope, line 21; doc:`plans/fact_schema/FACT_SCHEMA_PRD.md` section Domain rules, lines 96 - 97 | 2026-10-03
F-2. No product code exists: the tracked Python files are only the architecture tests and the agent hooks, and there is no Alembic directory, no layer directory and no configuration module. | cmd:`git ls-files` -> Python files only under `tests/architecture/`, `.claude/hooks/`, `.codex/hooks/` and `.agents/skills/load-context/scripts/`, and no path under `alembic/`, `api/`, `service/`, `data/`, `worker/` or `config/` | 2026-10-03
F-3. The choice of the local database is an interview in progress whose question 3, which account creates the PostGIS extension in the first revision, is blocking. | doc:`plans/local_database/LOCAL_DATABASE_SHAPE.md` line 3; doc:`plans/local_database/LOCAL_DATABASE_SHAPE.md` line 59 | 2026-10-03
F-4. The rules for a pseudonym and a password are a blocking question 4 of the interview of `plans/account_sessions/`. | doc:`plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` line 68 | 2026-10-03
F-5. The closed plan of the tag mapping leaves the names of the modules and constants of the backend to Q-11 of the MVP plan. | doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` line 68 D-14; doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-16 | 2026-10-03
F-6. Every schema change is an Alembic revision of raw SQL reviewed line by line against the DDL of the product specification, integrity constraints are required while triggers and domain decisions in the database are not allowed, a one-to-one relation is a column on the existing row, and a text column has a documented length limit or deliberately none. | doc:`docs/standards/standard_database.md:46`; doc:`docs/standards/standard_database.md:62`; doc:`docs/standards/standard_database.md:78`; doc:`docs/standards/standard_database.md:82`; doc:`docs/standards/standard_database.md:130` | 2026-10-03
F-7. An instant is stored as `timestamptz(3)` with a `utc_offset_minutes` column of the shared domain, the condition `CK_<table>_offset_pairs` rejects a half pair, a server-stamped value takes the offset of the business zone, and a day is a `date`. | doc:`docs/standards/standard_time.md:48`; doc:`docs/standards/standard_time.md:54`; doc:`docs/standards/standard_time.md:70`; doc:`docs/standards/standard_time.md:72` | 2026-10-03
F-8. A duplicate that may legitimately repeat after a window must not be guarded by a hard unique constraint, and a conflict is resolved by `INSERT ... ON CONFLICT` rather than by a caught exception. | doc:`docs/standards/standard_idempotency.md:54`; doc:`docs/standards/standard_idempotency.md:60` | 2026-10-03
F-9. The identity of an OpenStreetMap fact is the element type, the element identifier and the fact type without matching by geometry, a fresh copy with its reconciliation and its date becomes visible in one commit with the way of storing it left to Q-10, the reconciliation ends with a unique constraint on that identity for converted and outdated facts too, and a vote keeps its weight after its 30-day identifier is deleted. | doc:`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` line 61 D-7; doc:`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` line 65 D-9; doc:`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` lines 67 - 75 D-10; doc:`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` line 107 D-21 | 2026-10-03
F-10. The tag mapping gives every way of the pedestrian network four barrier states, the `wheelchair=no` marking and its kerb, crossing and motor traffic context, every node its point facts and kerb point, every amenity a point, and every fact the calendar day of the last edit of its element. | doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` line 52 D-6; doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` line 54 D-7; doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` line 56 D-8; doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` line 66 D-13; doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` line 70 D-15 | 2026-10-03
F-11. Version 3 of the specification says it settles no technical solution, keeps one vote per fact and the disputed wording that scenario 3 of the MVP contradicts, gives the radii of a geozone only as an example, gives the hash the sole purpose of one vote per fact, lets a moderator hide but not restore, has eleven fact types, and makes stairs never absent or unknown. | doc:`docs/product/specification.md` line 9; doc:`docs/product/specification.md` lines 83 - 84, 96, 102, 109, 125, 171 and 188 | 2026-10-03
F-12. The MVP PRD names version 3 twice, keeps one vote per fact in FR-6 and FR-13, lets a moderator only hide in FR-14, refuses a second confirmation of an account for ever in AC-6, and keeps the disputed wording in its Domain rules. | doc:`plans/mvp/MVP_PRD.md` lines 17, 39, 53, 55, 81, 111 and 114 | 2026-10-03
F-13. `PRODUCT.md` repeats one vote per fact and a moderator who can only hide. | doc:`PRODUCT.md` lines 56 and 59 | 2026-10-03
F-14. The MVP plan names version 3 in its Goal, has the decisions D-1 - D-6, holds Q-10 with three items of inputs and one of caveats, refers to Q-10 from Q-9, its Risks and the closing note on Q-11, and says nothing of a backend skeleton in Q-11. | doc:`plans/mvp/MVP_PLAN.md` lines 7, 35, 46, 54 - 61 | 2026-10-03
F-15. The registry of deferred decisions says the revision waits for the local database and a backend skeleton, and the standards map names the product specification alone as the target of anything that touches a table. | doc:`docs/standards/decision_registry.md` line 48; doc:`docs/standards/README.md` lines 54 and 92 | 2026-10-03
F-16. The shape of the contract needs the resources and statuses of Q-10, and asks whether the interface returns codes that the client translates. | doc:`plans/api_contract/API_CONTRACT_SHAPE.md` lines 33, 56 and 74 | 2026-10-03
F-17. The shape of this initiative left to phase B whether a status is derived on read or kept up to date on write. | doc:`plans/fact_schema/FACT_SCHEMA_SHAPE.md` line 85 | 2026-10-03
F-18. On PostgreSQL 15 with `btree_gist`, two partial exclusion constraints over the fact, the person and `tstzrange(cast_at, repeat_allowed_at)` make `INSERT ... ON CONFLICT DO NOTHING RETURNING id` return no row for a second vote of the same account or hash within the day, return a row for a vote exactly one day later, let votes without any identity coexist, and raise an error without `ON CONFLICT`; `tstzrange` is immutable while `timestamptz + interval` is only stable. | cmd:`docker run postgres:15` with `psql` running the scratchpad script `check.sql` -> `first_account_vote` 1, `second_within_day` 0 rows, `exactly_one_day_later` 3, `first_hash_vote` 4, `second_hash_within_day` 0 rows, `two_without_identity` 6 and 7, `ERROR: conflicting key value violates exclusion constraint "ex_vote_account_limit"`, `timestamptz_pl_interval` volatility `s`, `tstzrange` volatility `i` | 2026-10-03
F-19. On the same server a unique index on `lower(pseudonym)` refuses `wózek_krk` after `Wózek_KRK` and `żaba` after `ŻABA`, a unique constraint on the OpenStreetMap identity admits two facts with a null identity and refuses a second fact on `way` 42 with the same type, and unquoted constraint names are stored in lower case. | cmd:the same `check.sql` -> `ERROR: duplicate key value violates unique constraint "ux_account_pseudonym_lower"`, `zaba_upper` 3, `zaba_lower` 0 rows, `duplicate_osm_identity` 0 rows, `facts` 3 | 2026-10-03
F-20. The machine of this session has Python 3.12.3 without pytest, Node.js 22.17.0 without the installed prettier of `package.json`, a running Docker engine 27.2.1 and a local `postgres:15` image without PostGIS, while the project requires Python 3.13. | cmd:`python3 --version` -> `Python 3.12.3`; cmd:`python3 -m pytest --version` -> `No module named pytest`; cmd:`ls node_modules/.bin/prettier` -> no such file; cmd:`node --version` -> `v22.17.0`; cmd:`docker info --format '{{.ServerVersion}}'` -> `27.2.1`; cmd:`docker images` filtered by `postgres` -> `postgres:15`; code:`pyproject.toml:12` | 2026-10-03
F-21. The architecture tests check a closed plan dated on or after 2026-08-17, and before the plan of the tag mapping changed anything they failed only in the files of the impeccable skill. | code:`tests/architecture/test_plan_document_contract.py:38`; doc:`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` F-27 | 2026-10-03
F-22. The naming registry is empty, and the naming standard gives no rule for the names of database objects beyond the example `CK_<table>_offset_pairs`. | doc:`docs/standards/naming_registry.md` section Current state; doc:`docs/standards/standard_naming.md` section Names of query constants; doc:`docs/standards/standard_time.md:70` | 2026-10-03

## Decisions

D-1. The initiative has two tasks. This task, `FACT_SCHEMA`, writes `docs/product/schema.md`, version 4 of the specification and the changes of the Scope of changes, and meets AC-13 of the PRD. The task `FACT_SCHEMA_REVISION`, whose seed is `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, builds the first Alembic revision of that schema, the code of the rules that FR-15 and AC-1 - AC-12 need and their tests, once `plans/local_database/` (Q-4) is closed and Q-11 of the MVP plan has built the backend skeleton with the Alembic configuration (F-2, F-3, F-5). The importer and the backend share one schema in one database: `docs/product/schema.md` describes it whole and says which of the two writes which table, and the revision of the second task is the only chain of revisions both use. Decided by the user on 2026-10-03 in phase B, against this plan building the skeleton itself and against one plan waiting with open questions; the shared schema is the user's condition attached to that answer.

D-2. A fresh OpenStreetMap copy is stored in one transaction: the import upserts the ways and nodes of the copy with `INSERT ... ON CONFLICT`, deletes those the copy no longer holds, reconciles the facts by `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-10 and inserts the row of the copy into `osm_copy`, all in one commit. The tables of the copy carry no copy version. Decided by the user on 2026-10-03 in phase B, against a versioned copy switched in a last short transaction. It settles the storage left to Q-10 by D-9 there (F-9).

D-3. `docs/product/schema.md` is written in full by step 1 below: the DDL of the target state in `sql` blocks, one subsection per table with the meaning of every column, what the schema deliberately does not hold, and who writes what. It is part of the specification from version 4, and the standards map names it next to the specification as the target of a schema change. Decided by the user in the shape (question 2); the structure of the file is an agent decision at C:40, without asking.

D-4. The status of a fact, its sums and the date of its last confirmation are not stored: the rules layer derives them on every read from the votes of the fact, the window of k persons and the thresholds of M4, and the segment state is derived for every route. The schema stores only what votes cannot give: the source, the OpenStreetMap identity and the removal from OpenStreetMap. Agent decision at C:40, without asking: the shape left the choice to phase B with a measurement on the first import (F-17), which cannot exist before the stored data; a stored status would also have to be recomputed for every fact whenever k, x or a threshold changes, which a derived one never needs; the facts with votes are few in the MVP. A stored status can be added later by a normal revision if a measurement asks for it.

D-5. Every fact - a point report, a geozone, an OpenStreetMap fact and a fact converted from one - is one row of the table `fact`. A geozone is a fact with a radius, a column rather than a side table, because the relation is one-to-one (F-6). The lifecycle of M4 is held by three things: `source`, the OpenStreetMap identity kept after a conversion, and `is_removed_from_osm` for a fact outdated because OpenStreetMap removed it; a conversion sets `source` to `user_report` and keeps the identity, a return sets it back to `openstreetmap`. A fact keeps no author: the author of a report is only the person of its first vote. Agent decision at C:40, without asking: one table lets votes, flags, the duplicate check and the window apply to every fact through one foreign key, as M4 and M5 require.

D-6. The OpenStreetMap copy is stored as three tables keyed by the OpenStreetMap identifiers: `osm_way` with the line of the way, the four barrier states of D-6 of the tag mapping, the `wheelchair=no` marking and whether the way is for motor traffic or a crossing; `osm_node` with its point, its kerb point and whether it is a crossing or on a way for motor traffic; and `osm_way_node` with the nodes of each way in order, which the segment combination of D-7 there needs (F-10). Only the elements of the pedestrian network are stored; which elements that is stays with `plans/routing_engine/` and the import. The state `present` of a way stands next to the OpenStreetMap fact of that barrier on that way, which carries the votes and the number of steps; the import writes both in the transaction of D-2. An amenity of an element outside the network is a fact without a row in these tables, so `fact` has no foreign key to them. Raw tags are not stored, because a change of the tag rules is followed by a fresh import (D-14 of the tag mapping). Agent decision at C:40, without asking.

D-7. Every fact sits at a point, `geography(Point, 4326)`: for a way fact a point of the way chosen by the import, for an area the point of D-13 of the tag mapping. Ways and nodes use `geography` of the same reference system, and distances such as the 15 m of the duplicate check are given in metres through `ST_DWithin` on a GiST index. A query that needs the whole of a way fact reads the line of `osm_way` through the identity. Agent decision at C:40, without asking: metres without a projection, and one type for every geometry of the schema.

D-8. A vote is one row of `vote`, never updated, kept as history. Its person is `account_id` or `voter_hash`, never both, and after the account is deleted (`ON DELETE SET NULL`) or the hash is cleared after 30 days the vote has no person and counts as a person of its own (FR-9, FR-10). `is_cast_with_account` records the kind of voter, from which the rules layer computes the weight of M4, so a deleted account keeps its weight of 1 and O2 can add a photo column later. The hash is `bytea` without a length check, because how it is computed belongs to the voting work package (PRD, Out of scope). Agent decision at C:40, without asking: the weights stay a rule in code, and the kind is the fact about the vote that survives both deletions.

D-9. The vote limit of FR-7 is refused by the database itself through two partial exclusion constraints, `EX_vote_account_limit` and `EX_vote_hash_limit`, over the fact, the person and the interval from `cast_at` to `repeat_allowed_at`. The rules layer writes `repeat_allowed_at` as `cast_at` plus x at the moment of the vote, so x stays configuration and a change of x applies to new votes only; the bound is a stored instant because `timestamptz + interval` cannot stand in a constraint expression (F-18). A vote is written with `INSERT ... ON CONFLICT DO NOTHING RETURNING id`, and no returned row means the vote was refused. Agent decision at C:40, without asking: the backstop lives in the database (F-6), unlike a hard unique constraint it lets a vote through once x has passed (F-8), and it needs no explicit lock; both behaviors were run on PostgreSQL (F-18).

D-10. A flag is the column pair `flagged_at` of the fact, written by the first flag, not a table: a flag stores nothing about who flagged, so further flags add nothing to keep. Hiding is the pair `hidden_at`, written by the moderator and cleared by a restore; only flagged content can be hidden. That an OpenStreetMap fact cannot be flagged and that a hidden fact cannot be voted on are rules of the rules layer, because they compare rows and the database holds no triggers (F-6). M11 names no way to dismiss a flag, so none is stored. Agent decision at C:40, without asking.

D-11. An account is a pseudonym, a password hash and a moderator flag set by hand. The pseudonym is unique without regard to letter case through `UX_account_pseudonym_lower` on `lower(pseudonym)` (F-19), and neither text column has a length or format limit in the database, because the rules for both are question 4 of `plans/account_sessions/` (F-4); that initiative enforces them at the input and chooses the hash format. Deleting an account deletes its row. Agent decision at C:40, without asking.

D-12. Closed lists are `text` domains with a check of the list - `fact_type`, `fact_source`, `osm_element_type`, `way_barrier_state`, `kerb_point_state`, `vote_verdict` - with English codes in snake case, and the code maps them to enumerations (`docs/standards/standard_database.md`, Queries in code). A new value is a revision that replaces the check of the domain. The radius list of a geozone and the barrier types allowed for it are checks of `fact`. Whether the programming interface reuses these codes is decided by `plans/api_contract/` (F-16). Agent decision at C:40, without asking: a domain check is easier to change than an enum type and keeps the list in one place.

D-13. Instants follow F-7: every one is a pair, server-stamped ones take the offset of the Europe/Warsaw zone at the moment of writing, and `CK_fact_offset_pairs` guards the two nullable pairs; the pairs declared `NOT NULL` on both columns cannot be half written. `osm_copy.state_at` is the header instant of `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-4 with the offset it came with, 0 for a value in UTC. The date of the last OpenStreetMap edit is a `date`, `osm_edited_on`, the calendar day in Europe/Warsaw of D-15 of the tag mapping, computed by the import. Agent decision at C:40, without asking.

D-14. The free texts - `description`, `pseudonym`, `password_hash`, `file_name` - have deliberately no length limit in the database: the limits of user input are set where the input is accepted, by `plans/api_contract/` for the description and `plans/account_sessions/` for the account, and `file_name` comes from the checked name of D-3 of `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md`. Agent decision at C:40, without asking, to avoid guessing a contract owned elsewhere.

D-15. Database objects live in the schema `public`. Tables are singular nouns in snake case, and constraints and indexes carry the prefixes `PK_`, `FK_`, `UX_`, `CK_`, `EX_` and `IX_` followed by the table and the subject, unquoted, so PostgreSQL stores them in lower case (F-19, F-22). `naming_registry.md` gets these names from the task `FACT_SCHEMA_REVISION`, when the objects exist, because the registry records the actual state. Agent decision at C:40, without asking.

D-16. The schema needs the extensions `postgis` and `btree_gist`, the second for the constraints of D-9. Which account creates them, and the grants to the accounts of the service, are question 3 of `plans/local_database/` (F-3) and the revision of `FACT_SCHEMA_REVISION`; `docs/product/schema.md` names the extensions and no account. Agent decision at C:40, without asking.

D-17. Version 4 of the specification states the values of x and k - one day and five persons - and says that a change of either is a new version, as version 3 does for the thresholds of M6; in code they stay configuration values. Agent decision at C:40, without asking: the PRD keeps them configuration so that a change does not alter the rules, and the specification has to show the values the product runs on; the user approves the wording with version 4.

D-18. `plans/mvp/MVP_SHAPE.md` stays unchanged as the record of its interview, as `plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-4 kept it. The shapes of the sibling initiatives get one item each in Current state, the way the closed plans of `plans/osm_data_source/` and `plans/osm_barrier_mapping/` handed them their decisions. Agent decision at C:40, without asking.

D-19. The task `FACT_SCHEMA_REVISION` starts with its own shape from its seed and reads this plan and `docs/product/schema.md` as its inputs. It turns AC-1 - AC-12 into tests under `docs/standards/standard_tests.md` - critical tests for every refusal of FR-15 and for the round trip of an offset, scenario tests for the status runs - and it may change `docs/product/schema.md` only through a new version of the specification approved by the user. Agent decision at C:40, without asking.

## Scope of changes

Texts to insert are given in fenced blocks and are inserted without the fence. Every existing file is read again right before it is edited; when a quoted passage no longer matches the file, the step stops and the difference goes to the user. YYYY-MM-DD is the day of the edit; in step 2.10 it is the day of the user's approval.

### Step 1. `docs/product/schema.md`, new file

Create the file with this content:

````text
# Target database schema

Document state: YYYY-MM-DD, part of `docs/product/specification.md` version 4

## Why this document exists

This is the target state of the database schema of the app: the extensions, domains, tables, constraints and indexes, written as DDL. It is part of the product specification (`docs/product/specification.md`, section Why this document exists), and it is changed and approved like the specification, by the user, as a new version of it. Every Alembic revision is reviewed line by line against it (`docs/standards/standard_database.md`, Form of schema changes). It says what the schema is supposed to be, not what a server holds; the actual state is the schema dump, once the project keeps one.

The import of OpenStreetMap data and the backend read and write this one schema in one database. Neither has a schema or a database of its own; the section Who writes what says which of them writes which table.

## Conventions

- PostgreSQL 17 or newer, with the extensions `postgis` and `btree_gist`, in the schema `public`.
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
- `osm_way` holds every way of the pedestrian network of the copy in use, keyed by its OpenStreetMap identifier, with its line and the state of each of stairs, poor surface, steep incline and narrow passage by the tag rules of M6. `is_marked_wheelchair_no` is the marking of M7, `is_motor_traffic` says the way is for motor traffic by M6, and `is_crossing` says it is tagged as a crossing. A state `present` stands next to the OpenStreetMap fact of the same barrier on the same way in `fact`, which carries its votes and its number of steps.
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

- A fact is a barrier or an amenity of `fact_type` at the point `geog`: a point report, a geozone, a fact from OpenStreetMap or a fact converted from one (M3 - M6). For a fact of a way the point lies on the way, and the line of the way is in `osm_way`.
- A geozone is a fact with `geozone_radius_m` of 10, 25, 50 or 100 m and a barrier type (M5).
- `description` and `step_count` are the optional description and number of steps of M3; `step_count` also holds the number of steps OpenStreetMap gives. `is_sample` marks sample data (M10). A saved fact is never edited by a user (M3, M5).
- `osm_element_type`, `osm_element_id` and `fact_type` are the identity of a fact from OpenStreetMap, unique for every fact that came from OpenStreetMap, converted and outdated ones included; a fact reported by a user has none. `osm_edited_on` is the calendar day in Europe/Warsaw of the last edit of that element (M4).
- `source` is `openstreetmap` for a fact of the copy and `user_report` otherwise. A fact a fresh copy no longer holds either becomes `user_report` with its identity kept, or keeps `openstreetmap` with `is_removed_from_osm`, which makes it outdated with the reason that it was removed in OpenStreetMap; a fact that returns becomes `openstreetmap` again without that mark (M4).
- `flagged_at` is the first flag of the fact; a flag stores nothing about who flagged (M11). `hidden_at` is set when a moderator hides flagged content and cleared when they restore it.
- The status of a fact, its sums and the date of its last confirmation are not columns: the code derives them from `vote` (M4).

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
- When the account is deleted or the hash is cleared 30 days after `cast_at`, the vote stays with its weight and has no person any more, so it counts as a person of its own (M4, M9). Votes are never updated or deleted.

## What the schema does not hold

- The status of a fact, its sums and the date of its last confirmation, derived from the votes (M4).
- The state of a route segment, derived for each route from the copy, the profile in the route request and the facts (M7).
- The preference profile, the current location and the routes, which are never stored (M1, M2).
- The sessions of logged-in users, decided in `plans/account_sessions/`.
- The accounts of the database and their grants, created with the first revision.

## Who writes what

- The import writes `osm_copy`, `osm_way`, `osm_node`, `osm_way_node` and the facts with an OpenStreetMap identity: a fresh copy, the reconciliation of its facts and its row in `osm_copy` in one transaction, which upserts the ways, nodes and facts of the copy and deletes the ways and nodes it no longer holds.
- The backend writes the facts without an OpenStreetMap identity - reports and geozones - the votes on every fact, the accounts, and `flagged_at` and `hidden_at`.
- The periodic task of the worker clears `voter_hash` 30 days after `cast_at`.
- No one deletes a fact or a vote.
````

### Step 2. `docs/product/specification.md`, version 4

2.1. Replace the whole state line, which starts "Document state: 2026-10-03, version 3 - the OpenStreetMap tag rules", with:

```text
Document state: YYYY-MM-DD, version 4 - the limit on repeated votes, the window of the latest votes and the order of statuses, the weight of a vote whose person is no longer known, flags and restoring hidden content, decided in `plans/fact_schema/`, and the target database schema in `docs/product/schema.md`
```

2.2. In the section Why this document exists, replace the sentence "This document does not settle the technology stack or any technical solution - those are chosen in phase B of `plan-prd`." with:

```text
Version 4 adds the limit on repeated votes of one person, the window of the latest votes that a status counts, the order in which a status is derived, the weight of a vote whose person is no longer known, the rules of flags and restoring hidden content, decided in `plans/fact_schema/`, together with the target database schema. This document does not settle the technology stack or any technical solution - those are chosen in phase B of `plan-prd` - with one exception: the target database schema in `docs/product/schema.md` is part of this specification, is changed and approved like it, and is the target every schema revision is reviewed against.
```

2.3. In M4, replace the bullet "- A user fact becomes confirmed when the sum of its confirmations reaches 2. It becomes outdated when the denials reach at least 2 and outweigh the confirmations. It is disputed when it has both confirmations and denials and neither rule applies." with:

```text
- A status counts only the latest vote of each of the five persons who voted on the fact most recently; older votes stay in the history of the fact and do not count. This holds for every fact, facts from OpenStreetMap and geozones included, and every sum of confirmations or denials in this section is counted over these votes.
- Over these votes a user fact is outdated when the denials reach at least 2 and outweigh the confirmations; otherwise disputed when it has both confirmations and denials; otherwise confirmed when the confirmations reach 2; otherwise unverified. A single denial therefore makes a confirmed fact disputed.
```

2.4. In M4, replace the bullet "- One person has one vote per fact: per account for logged-in users, per hashed identifier for others (M9)." with:

```text
- A person is an account for logged-in users and a hashed identifier for others (M9). A person votes on the same fact again only once one day has passed since their previous vote on it; an earlier vote is refused. Of the votes of one person on a fact only the latest counts, so a person can change their mind or renew a confirmation but never adds weight. A vote is not withdrawn, only replaced by a later one. The author of a report is a person like any other: the report carries their confirmation.
- A vote keeps its weight for as long as the fact exists, also after its account is deleted or its hashed identifier is deleted after 30 days (M9). Such a vote no longer belongs to any person and counts as the vote of a person of its own.
- The five persons and the one day are configuration values of the prototype; a change of either is a new version of this document.
```

2.5. In M5, replace "with a radius chosen from a list (for example 10, 25, 50 or 100 m)" with "with a radius chosen from the list 10, 25, 50 and 100 m".

2.6. In M9, replace "The hash serves only to allow one vote per fact, and it is deleted after 30 days." with "The hash serves only the limit on repeated votes of M4, and it is deleted 30 days after the vote was cast, while the vote keeps its weight (M4)."

2.7. In M9, replace "Other users never see who made a report, a confirmation or a geozone - neither a pseudonym nor whether the author was logged in." with "Other users never see who made a report, a confirmation or a geozone - neither a pseudonym nor whether the author was logged in - and a moderator does not see it either." and after the paragraph that starts "Deleting an account removes the account, the pseudonym and the points." insert the paragraph:

```text
A pseudonym is unique without regard to letter case. The pseudonym of a deleted account is free to be taken again.
```

2.8. In M11, replace the paragraph "Anyone can flag a report, a geozone or a photo. A moderator - a member of the team whose role is assigned by hand - sees the flagged content in a simple view and can hide it; hidden content disappears for everyone." with:

```text
Anyone can flag a report, a geozone or a photo. A fact from OpenStreetMap cannot be flagged, while a fact that a fresh copy turned into a user fact (M4) counts as a report. A flag stores nothing about who flagged. A moderator - a member of the team whose role is assigned by hand - sees the flagged content in a simple view and can hide it. Hidden content disappears for everyone: it is not on the map or the lists, does not affect routes or segment colors, is not offered as an existing fact before a report (M3) and cannot be voted on. The moderator can restore hidden content, which then counts again with the votes it has.
```

2.9. In the section Open questions, replace "None at version 3." with "None at version 4."

2.10. In the section Decision provenance, after the bullet that starts "- Version 3:", insert the bullet:

```text
- Version 4: the rules of M4 (the limit on repeated votes, the window of the latest votes, the order of statuses, the weight of a vote whose person is no longer known), M5 (the closed list of radii), M9 (the purpose of the hash, the pseudonym, a moderator not seeing authors) and M11 (flags, restoring hidden content), and the target schema in `docs/product/schema.md`, were decided in the shape interview, at the PRD gate and in phase B of `plans/fact_schema/`, which record the scenarios each rule was decided on. The one day and the five persons were proposed by the agent and approved by the user on 2026-10-03 in place of the db person of the team, whose ruling is still to be confirmed. The weight of a vote after its hashed identifier is deleted was decided in phase B of `plans/osm_data_source/`. The closed list of radii, the pseudonym rule, the ban on flagging OpenStreetMap facts, a flag without its author and a vote without a person counting as a person of its own were proposed by the agent. The user approved this version on YYYY-MM-DD.
```

### Step 3. `plans/mvp/MVP_PRD.md`

3.1. In Scope, replace "The mandatory features M1-M11 of the specification, version 3," with "The mandatory features M1-M11 of the specification, version 4,".

3.2. In FR-6, replace "One person has one vote per fact." with "A person votes on the same fact again only once one day has passed since their previous vote on it, and only their latest vote counts."

3.3. In FR-13, replace "To allow one vote per fact, such a vote keeps" with "For the limit on repeated votes of FR-6, such a vote keeps", and replace "never the raw values, deleted after 30 days." with "never the raw values, deleted 30 days after the vote, while the vote keeps its weight."

3.4. In FR-14, replace "can hide it; hidden content disappears for everyone." with "can hide it and restore it; hidden content disappears for everyone until it is restored."

3.5. In AC-6, replace "A second confirmation of the same fact by the same account is refused." with "A second confirmation of the same fact by the same account within one day is refused."

3.6. In Domain rules, replace "The rules are those of the specification, version 3," with "The rules are those of the specification, version 4,", and replace the bullet "- A user fact is confirmed when its confirmations sum to 2; outdated when its denials reach at least 2 and outweigh the confirmations; disputed when it has both confirmations and denials and neither rule applies; unverified otherwise." with:

```text
- A status counts the latest vote of each of the five persons who voted on the fact most recently. Over them a user fact is outdated when its denials reach at least 2 and outweigh the confirmations; otherwise disputed when it has both confirmations and denials; otherwise confirmed when its confirmations sum to 2; otherwise unverified.
```

### Step 4. `PRODUCT.md`

4.1. In the item "- Confirmations and denials.", replace "One person has one vote per fact." with "A person votes on the same fact again only after a day, and only their latest vote counts."

4.2. In the item "- Flagging and moderation.", replace "and can hide it." with "and can hide it and restore it."

### Step 5. `plans/mvp/MVP_PLAN.md`

5.1. In Goal, replace "of `docs/product/specification.md`, version 3," with "of `docs/product/specification.md`, version 4,".

5.2. In Decisions, after D-6, append:

```text
D-7. Domain model and database schema of facts and votes, settling the former Q-10. The target schema is `docs/product/schema.md`, part of `docs/product/specification.md` version 4, with the rules of votes, statuses, flags and hiding of M4, M5, M9 and M11 there, as `plans/fact_schema/FACT_SCHEMA_PLAN.md` D-1 - D-19 decide. Constraints for the rest of this plan: the import and the backend write one shared schema, the import the OpenStreetMap tables and the facts with an OpenStreetMap identity, the backend the reports, geozones, votes, accounts, flags and hiding (D-1 there); a fresh copy is written in one transaction together with its reconciliation and its date (D-2 there); the status of a fact and the date of its last confirmation are derived from the votes on every read and never stored, and the segment state is derived for every route (D-4 there); a vote is written with `INSERT ... ON CONFLICT DO NOTHING`, where no returned row means the limit on repeated votes refused it (D-9 there); the database itself refuses the states of `plans/fact_schema/FACT_SCHEMA_PRD.md` FR-15. The schema is built by the task `FACT_SCHEMA_REVISION` of `plans/fact_schema/` once Q-4 and the backend skeleton of Q-11 exist, and the work packages of the import, the voting, the accounts, the moderation and the route build on that revision. Decided on 2026-10-03 in `plans/fact_schema/`: the rules by the user in place of the db person, whose ruling is still to be confirmed, the split into two tasks and the storage of a fresh copy by the user, the rest by the agent at C:40.
```

5.3. In Risks, in the item that begins "The open questions depend on each other", replace "Q-10 depends on the rules of D-5 and on one question of Q-2, both settled on 2026-10-03; Q-9 depends on Q-10 and Q-6;" with "Q-9 depends on D-7 and Q-6;", and replace "The critical path is Q-10 -> Q-9." with "The critical path is Q-9, and the stored data of D-7 also waits for Q-4 and Q-11."

5.4. In Open questions, item Q-9, replace "Depends on Q-10 for the resources and statuses it exposes" with "Depends on D-7 for the resources and statuses it exposes", and replace "the route response carries the segment states of Q-10," with "the route response carries the segment states derived from the data of D-7,".

5.5. In Open questions, remove the five items that begin "- Q-10. The domain model and database schema of facts and votes", "- Q-10 inputs from `plans/osm_data_source/OSM_DATA_SOURCE_SHAPE.md`", "- Q-10 inputs from `plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6", "- Q-10 inputs from `plans/osm_data_source/`, settling" and "- Q-10 caveats:".

5.6. In Open questions, at the end of item Q-11, append: " It also builds the backend skeleton - the layer directories, the configuration and the Alembic setup - that the task `FACT_SCHEMA_REVISION` of `plans/fact_schema/` waits for to build the schema of D-7."

5.7. In the last item of Open questions, replace "Q-10 was narrowed to the domain model" with "The former Q-10 was narrowed to the domain model", and replace "The owners of Q-10 and Q-11 were proposed by the agent." with "The owners of the former Q-10 and of Q-11 were proposed by the agent."

5.8. In Supplementary files, append the item "- `plans/fact_schema/FACT_SCHEMA_PLAN.md`, the decision behind D-7."

### Step 6. `docs/standards/decision_registry.md`

In the entry Technical directions of the MVP plan, item Blocks, replace "That revision waits for the local database with PostGIS of `plans/local_database/` and for a backend skeleton holding the Alembic configuration, which no plan has built yet; the decision on the model does not wait for either." with "On 2026-10-03 the user split that initiative into two tasks: `FACT_SCHEMA` decides the model and writes the target schema in `docs/product/schema.md`, and `FACT_SCHEMA_REVISION` builds the revision, which waits for the local database with PostGIS of `plans/local_database/` and for a backend skeleton holding the Alembic configuration, which no plan has built yet."

### Step 7. `docs/standards/README.md`

7.1. In the section Project documents outside the standards, replace "- `docs/product/` - the product specification, `docs/product/specification.md`, written by the team." with "- `docs/product/` - the product specification, `docs/product/specification.md`, written by the team, with the target database schema in `docs/product/schema.md`, part of the specification since version 4."

7.2. In the table What to open before a task, in the row "Anything that touches a table, column, view or schema", replace "the product specification for the target" with "the product specification with `docs/product/schema.md` for the target", and realign the table with prettier.

### Step 8. Shapes of the sibling initiatives

8.1. `plans/api_contract/API_CONTRACT_SHAPE.md`, section Current state: after the item that begins "- `plans/osm_barrier_mapping/` decided on 2026-10-03 (`docs/product/specification.md` version 3, M6 - M8)", insert:

```text
- `plans/fact_schema/` decided on 2026-10-03 (`plans/fact_schema/FACT_SCHEMA_PLAN.md`; `docs/product/schema.md`, part of `docs/product/specification.md` version 4) the resources the contract exposes and their states: a fact of a type from the closed list, with the source OpenStreetMap or user report, a point, for a geozone a radius of 10, 25, 50 or 100 m, an optional description and number of steps, the sample data mark, the calendar day of its last OpenStreetMap edit for an OpenStreetMap fact, and a status derived from the latest votes of the five persons who voted most recently, never stored; a vote that confirms or denies, refused when the same person voted on the same fact less than a day before, so a refusal is an answer the contract has to carry; accounts with a pseudonym unique without regard to letter case and a moderator role; flagging, hiding and restoring. The closed lists are stored as English codes in snake case, which the contract may reuse or map. No response carries the author of a report, a vote or a geozone, nor the weights, to anyone, a moderator included.
```

8.2. `plans/routing_engine/ROUTING_ENGINE_SHAPE.md`, section Current state: after the item that begins "- `plans/osm_barrier_mapping/` decided on 2026-10-03 (`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6, D-7, D-11)", insert:

```text
- `plans/fact_schema/` decided on 2026-10-03 (`plans/fact_schema/FACT_SCHEMA_PLAN.md` D-2, D-4, D-6, D-7; `docs/product/schema.md`) how the copy is stored for the route: every way of the pedestrian network with its line, its four barrier states, the `wheelchair=no` marking and whether it is for motor traffic or a crossing; its nodes in order; every node with its point, its kerb point and whether it is a crossing or on a way for motor traffic; every fact at a point, a way fact identified by its way. A fresh copy is written in one transaction. The segment state and the status of a fact are derived for each route, never stored. Which ways belong to the pedestrian network and how a route is related to the stored ways stay with this initiative.
```

8.3. `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, section Current state: after the item that begins "- On 2026-10-03 the repository was checked for answers to the open questions of this shape", insert:

```text
- `plans/fact_schema/` decided on 2026-10-03 (`plans/fact_schema/FACT_SCHEMA_PLAN.md` D-8, D-11; `docs/product/schema.md`) that an account is stored as a pseudonym unique without regard to letter case, a password hash and a moderator flag set by hand, with no length or format limit on either text in the database, which leaves the rules of question 4 of this shape, and the format of the hash, to this initiative. A vote of an account is refused when the same account voted on the same fact less than a day before (`docs/product/specification.md` version 4, M4), which replaces one vote per fact per account in item 3 of Functional requirements.
```

8.4. `plans/local_database/LOCAL_DATABASE_SHAPE.md`, section Current state: after the item "- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).", insert:

```text
- `plans/fact_schema/` decided on 2026-10-03 (`docs/product/schema.md`; `plans/fact_schema/FACT_SCHEMA_PLAN.md` D-16) that the schema needs the extensions `postgis` and `btree_gist`, the second for the exclusion constraints of the limit on repeated votes, so question 3 of this shape concerns both. The first revision is built by the task `FACT_SCHEMA_REVISION` of `plans/fact_schema/` once this initiative and the backend skeleton exist. The parts of the schema that need no PostGIS were run on PostgreSQL 15 on 2026-10-03 (F-18 and F-19 there).
```

## Rollout order

1. Step 1, then step 2 without the approval date of 2.10.
2. Show the user `docs/product/schema.md` and the diff of `docs/product/specification.md` and ask for the approval of version 4. On approval, write its date into 2.10 and continue; on any requested change, stop and change this plan first, because the specification is the contract of steps 3 - 8.
3. Steps 3 - 8 in any order, each file read again right before its edit, with the stop on a passage that no longer matches.
4. `npm ci`, then `npx --no-install prettier --write` on every changed or created markdown file, then the checks of the Definition of Done.

Steps for a human: the approval of version 4 of the specification with `docs/product/schema.md` in step 2; a Python 3.13 environment with the dev dependencies of `pyproject.toml` for the architecture tests, which the machine of this session lacks (F-20); the commit and the Merge Request of the changed files.

## Definition of Done

- `docs/product/schema.md` exists with the content of step 1, and `docs/product/specification.md` carries exactly the changes of step 2, with the date of the user's approval in 2.10.
- `plans/mvp/MVP_PRD.md`, `PRODUCT.md`, `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md`, `docs/standards/README.md` and the four shapes of step 8 carry exactly the changes of steps 3 - 8; `plans/mvp/MVP_SHAPE.md` is unchanged.
- `plans/mvp/MVP_PLAN.md` has D-7, no item that begins with Q-10 under Open questions, and no reference to Q-10 outside "the former Q-10".
- `npx --no-install prettier --check` passes on every changed or created markdown file and on the files of `plans/fact_schema/`.
- The changed and created files contain none of the characters forbidden by `docs/standards/standard_formatting.md` and no bold in prose.
- `python -m pytest tests/architecture -o addopts=-ra` in a Python 3.13 environment reports no violation in a file this plan changes or creates or in `plans/fact_schema/`, the check of this closed plan by `tests/architecture/test_plan_document_contract.py` included. Violations outside them that the tree already has (F-21) are not part of this plan.
- The review of `plan-implement` finds no blocking issue.

## Risks

- The rules were decided by the user in place of the db person, and the OpenStreetMap rules for the import person; either ruling can still change version 4 and the schema (PRD, Risks and notes).
- The DDL of `docs/product/schema.md` has run only in its parts without PostGIS (F-18, F-19). The `geography` columns and their GiST indexes run first in the task `FACT_SCHEMA_REVISION`, and an error found there is a new version of the specification.
- The stored data waits for Q-4, whose question 3 on the extension account is blocking (F-3), and for the backend skeleton of Q-11. Every hour of that wait is taken from the import, voting and route work packages that build on the revision, before the Kraków deadline at 11:00 on 4 October 2026.
- The state `present` of a way and the OpenStreetMap fact of that barrier are kept in step only by the import transaction, not by a constraint, because the database holds no cross-table rule (D-6).
- The status is derived on every read (D-4); its cost has not been measured. If a route over many voted facts is slow, a revision adds a stored status and the rules layer keeps it up to date.
- Not decided anywhere, and to be asked by the task or work package that meets it: whether a hidden or flagged converted fact that returns in a fresh copy as an OpenStreetMap fact stays hidden; the schema allows either.
- M11 names no way to dismiss a flag, so the moderator view keeps every flagged fact for ever (D-10). In the demo that is a short list.
- The specification names no status for an OpenStreetMap fact other than outdated; FR-8 of the PRD derives one in the same order as for a user fact. `plans/api_contract/` has to show it without presenting missing information as a confirmation (M10).
- Other sessions edit `plans/mvp/MVP_PLAN.md` and the sibling shapes on the same tree; a quoted passage that changed stops its step (Scope of changes).
- The machine of this session has neither Python 3.13 nor the installed prettier (F-20), so the checks of the Definition of Done need the human step of Rollout order or another machine.

## Open questions

None.

## Supplementary files

- `plans/fact_schema/FACT_SCHEMA_PRD.md`, the contract of both tasks of this initiative.
- `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, the domain rules and scenarios behind the PRD.
- `plans/fact_schema/FACT_SCHEMA_SEED.md`, the verbatim request of this task.
- `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, the verbatim request that split the task `FACT_SCHEMA_REVISION` out of this one.
