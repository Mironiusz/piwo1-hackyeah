# Target database schema

Document state: 2026-10-04, part of `docs/product/specification.md` version 13

## Why this document exists

This is the target state of the database schema of the app: the extensions, domains, tables, constraints, indexes and the rights of the service account. It is part of the product specification (`docs/product/specification.md`, section Why this document exists), and it is changed and approved like the specification, by the user, as a new version of it. Every Alembic revision is reviewed line by line against it (`docs/standards/standard_database.md`, Form of schema changes). It says what the schema is supposed to be, not what a server holds; the actual state is the schema dump, once the project keeps one.

The import of OpenStreetMap data and the backend read and write this one schema in one database. Neither has a schema or a database of its own; the section Who writes what says which of them writes which table.

## Conventions

- PostgreSQL 18, with the extension `postgis`, in the schema `public`. The first revision of the chain creates it and is applied by the schema owner account.
- A table is a singular noun in snake case. Constraints and indexes carry the prefix `PK_`, `FK_`, `UX_` (unique), `CK_` (check), `EX_` (exclusion) or `IX_`, then the table and the subject, unquoted.
- An instant is a pair of `timestamptz(3)` and `<column>_utc_offset_minutes` (`docs/standards/standard_time.md`); a calendar day is a `date`.
- A closed list is a `text` domain with a check of its values; the code maps it to an enumeration.
- Every geometry is `geography` in the reference system 4326, so distances are in metres.
- Free texts have no length limit in the database; the limits of user input are set where the input is accepted.
- The database holds no status, no sum of votes and no domain rule, only integrity constraints: the rules of `docs/product/specification.md` M4 are applied by the code to the stored votes.

## Extensions and domains

```sql
CREATE EXTENSION postgis;

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
    idempotency_key bytea NULL,
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
    CONSTRAINT UX_fact_idempotency_key UNIQUE (idempotency_key),
    CONSTRAINT CK_fact_osm_identity_complete CHECK ((osm_element_type IS NULL) = (osm_element_id IS NULL)),
    CONSTRAINT CK_fact_osm_edited_on_with_identity CHECK ((osm_element_id IS NULL) = (osm_edited_on IS NULL)),
    CONSTRAINT CK_fact_openstreetmap_has_identity CHECK (source = 'user_report' OR osm_element_id IS NOT NULL),
    CONSTRAINT CK_fact_removed_only_openstreetmap CHECK (NOT is_removed_from_osm OR source = 'openstreetmap'),
    CONSTRAINT CK_fact_user_content_without_identity CHECK (osm_element_id IS NULL OR (description IS NULL AND geozone_radius_m IS NULL AND NOT is_sample)),
    CONSTRAINT CK_fact_saved_report_has_idempotency_key CHECK ((idempotency_key IS NOT NULL) = (osm_element_id IS NULL AND NOT is_sample)),
    CONSTRAINT CK_fact_idempotency_key_sha256 CHECK (octet_length(idempotency_key) = 32),
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
- `idempotency_key` is the key of the save of a report or a geozone through `create_fact` of `docs/product/api_contract.md`: the SHA-256 hash of the text `create_fact:` followed by the `idempotency_key` of the request in its canonical form, 36 lowercase characters with hyphens, which makes it the reconciliation key of `docs/standards/standard_idempotency.md`. Every fact saved that way has one, kept for as long as the fact exists, and a fact from OpenStreetMap, a fact converted from one and sample data have none. A second fact with a key already saved is refused, so a repeated save finds the fact of the first one, which holds everything of the request its content is compared with.
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
    cast_on date GENERATED ALWAYS AS ((cast_at AT TIME ZONE 'Europe/Warsaw')::date) STORED,
    CONSTRAINT PK_vote PRIMARY KEY (id),
    CONSTRAINT FK_vote_fact FOREIGN KEY (fact_id) REFERENCES fact (id),
    CONSTRAINT FK_vote_account FOREIGN KEY (account_id) REFERENCES account (id) ON DELETE SET NULL,
    CONSTRAINT UX_vote_account_day UNIQUE (fact_id, account_id, cast_on),
    CONSTRAINT UX_vote_hash_day UNIQUE (fact_id, voter_hash, cast_on),
    CONSTRAINT CK_vote_account_only_with_account CHECK (is_cast_with_account OR account_id IS NULL),
    CONSTRAINT CK_vote_hash_only_without_account CHECK (NOT is_cast_with_account OR voter_hash IS NULL),
    CONSTRAINT CK_vote_voter_hash_sha256 CHECK (octet_length(voter_hash) = 32)
);

CREATE INDEX IX_vote_fact_id_cast_at ON vote (fact_id, cast_at);

CREATE INDEX IX_vote_account_id ON vote (account_id) WHERE account_id IS NOT NULL;
```

- An account is a pseudonym, unique without regard to letter case, a password hash and the moderator role assigned by hand (M9, M11). Deleting an account deletes its row and nothing else.
- A vote confirms or denies a fact. Its person is the account or the hashed identifier of M9, never both; `is_cast_with_account` keeps the kind of voter, from which the code takes the weight of M4. The report of a user carries the confirmation of its author as its first vote.
- `voter_hash` is 32 bytes long, the output of a 256-bit hash function; what is hashed is decided by the code that writes the vote (M9).
- `cast_on` is the calendar day of `cast_at` in Europe/Warsaw, computed by the database whatever offset the pair carries. A person votes on a fact at most once per calendar day (M4): `UX_vote_account_day` refuses a second vote of an account and `UX_vote_hash_day` a second vote of a hash on the same day. A vote of an account has no hash and a vote without an account has no account, so each uniqueness compares only its own kind of person, and a vote whose account was deleted takes part in neither.
- When the account is deleted, the vote stays with its weight and has no person any more, so it counts as a person of its own (M4, M9). The hash of a vote without an account is never cleared; it is deleted with the demo (M9). Votes are never deleted.

## Rights of the service account

The schema owner account creates and owns every object, and the service account of the running app, the import included, owns nothing (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-5). The revisions grant the service account exactly these rights and no right to create, alter or drop an object:

| Table                                 | Rights                         |
| ------------------------------------- | ------------------------------ |
| `osm_copy`                            | select, insert                 |
| `osm_way`, `osm_node`, `osm_way_node` | select, insert, update, delete |
| `fact`, `vote`                        | select, insert, update         |
| `account`                             | select, insert, update, delete |

The name of the service account is an entry of the local environment files, so the `GRANT` statements stand in the revisions with that name supplied when they are applied, never in this document.

## What the schema does not hold

- The status of a fact, its sums and the date of its last confirmation, derived from the votes (M4).
- The state of a route segment, derived for each route from the copy, the profile in the route request and the facts (M7).
- The preference profile, the current location and the routes, which are never stored (M1, M2).
- The sessions of logged-in users, decided in `plans_finished/account_sessions/`.
- The database itself and its accounts, created by the local setup and not by a revision.

## Who writes what

- The import writes `osm_copy`, `osm_way`, `osm_node`, `osm_way_node` and the facts with an OpenStreetMap identity: a fresh copy, the reconciliation of its facts and its row in `osm_copy` in one transaction, which upserts the ways, nodes and facts of the copy and deletes the ways and nodes it no longer holds.
- The backend writes the facts without an OpenStreetMap identity - reports and geozones, each with the idempotency key of its save, never changed afterwards - the votes on every fact, the accounts, and `flagged_at` and `hidden_at`.
- No task clears `voter_hash`; it is deleted with every other piece of data when the demo is deleted (M9).
- No one deletes a fact or a vote.
