"""
Creates the whole target schema of `docs/product/schema.md`, version 13 of the specification, and grants the service account its rights.

The revision creates the extension `postgis`, the seven domains and the seven tables with their constraints and
indexes, each statement exactly as the target schema writes it, and grants the service account exactly the rights of
the section Rights of the service account. It is the first revision of the chain, because every later revision changes
the objects it creates. The name of the service account comes from `migrations/env.py` and reaches the database only as
a parameter of `set_config`, and each grant quotes it as an identifier with `format('%I', ...)`. The grants name each
table and set no default privileges, so the version table of Alembic and every later table get no right from here.
The revision has no downgrade: the supported way back is recreating the database (`docs/standards/standard_database.md`).
"""

import sqlalchemy as sa
from alembic import context, op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

CREATE_TARGET_SCHEMA_SQL: tuple[str, ...] = (
    "CREATE EXTENSION postgis",
    """CREATE DOMAIN utc_offset_minutes AS smallint
    CONSTRAINT CK_utc_offset_minutes_range CHECK (VALUE BETWEEN -840 AND 840)""",
    """CREATE DOMAIN fact_type AS text
    CONSTRAINT CK_fact_type_closed_list CHECK (VALUE IN ('stairs', 'high_kerb', 'poor_surface', 'steep_incline', 'narrow_passage', 'ramp', 'elevator', 'lowered_kerb', 'accessible_toilet', 'rest_place', 'handrail_at_stairs'))""",
    """CREATE DOMAIN fact_source AS text
    CONSTRAINT CK_fact_source_closed_list CHECK (VALUE IN ('openstreetmap', 'user_report'))""",
    """CREATE DOMAIN osm_element_type AS text
    CONSTRAINT CK_osm_element_type_closed_list CHECK (VALUE IN ('node', 'way', 'relation'))""",
    """CREATE DOMAIN way_barrier_state AS text
    CONSTRAINT CK_way_barrier_state_closed_list CHECK (VALUE IN ('present', 'absent', 'absent_by_default', 'unknown'))""",
    """CREATE DOMAIN kerb_point_state AS text
    CONSTRAINT CK_kerb_point_state_closed_list CHECK (VALUE IN ('high', 'lowered', 'unknown'))""",
    """CREATE DOMAIN vote_verdict AS text
    CONSTRAINT CK_vote_verdict_closed_list CHECK (VALUE IN ('confirm', 'deny'))""",
    """CREATE TABLE osm_copy (
    id bigint GENERATED ALWAYS AS IDENTITY,
    state_at timestamptz(3) NOT NULL,
    state_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    file_name text NOT NULL,
    made_current_at timestamptz(3) NOT NULL,
    made_current_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    CONSTRAINT PK_osm_copy PRIMARY KEY (id),
    CONSTRAINT UX_osm_copy_state_at UNIQUE (state_at)
)""",
    """CREATE TABLE osm_way (
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
)""",
    "CREATE INDEX IX_osm_way_geog ON osm_way USING gist (geog)",
    """CREATE TABLE osm_node (
    id bigint NOT NULL,
    geog geography(Point, 4326) NOT NULL,
    kerb_point kerb_point_state NULL,
    is_crossing boolean NOT NULL,
    is_on_motor_traffic_way boolean NOT NULL,
    CONSTRAINT PK_osm_node PRIMARY KEY (id)
)""",
    """CREATE TABLE osm_way_node (
    way_id bigint NOT NULL,
    sequence_index integer NOT NULL,
    node_id bigint NOT NULL,
    CONSTRAINT PK_osm_way_node PRIMARY KEY (way_id, sequence_index),
    CONSTRAINT FK_osm_way_node_way FOREIGN KEY (way_id) REFERENCES osm_way (id) ON DELETE CASCADE,
    CONSTRAINT FK_osm_way_node_node FOREIGN KEY (node_id) REFERENCES osm_node (id),
    CONSTRAINT CK_osm_way_node_sequence_index CHECK (sequence_index >= 0)
)""",
    "CREATE INDEX IX_osm_way_node_node_id ON osm_way_node (node_id)",
    """CREATE TABLE fact (
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
)""",
    "CREATE INDEX IX_fact_geog ON fact USING gist (geog)",
    "CREATE INDEX IX_fact_flagged_at ON fact (flagged_at) WHERE flagged_at IS NOT NULL",
    """CREATE TABLE account (
    id bigint GENERATED ALWAYS AS IDENTITY,
    pseudonym text NOT NULL,
    password_hash text NOT NULL,
    is_moderator boolean NOT NULL,
    created_at timestamptz(3) NOT NULL,
    created_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    CONSTRAINT PK_account PRIMARY KEY (id)
)""",
    "CREATE UNIQUE INDEX UX_account_pseudonym_lower ON account (lower(pseudonym))",
    """CREATE TABLE vote (
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
)""",
    "CREATE INDEX IX_vote_fact_id_cast_at ON vote (fact_id, cast_at)",
    "CREATE INDEX IX_vote_account_id ON vote (account_id) WHERE account_id IS NOT NULL",
)

SET_SERVICE_ACCOUNT_NAME_SQL = "SELECT set_config('accessibility_db.service_account_name', :service_account_name, true)"

GRANT_SERVICE_ACCOUNT_SQL: tuple[str, ...] = (
    "DO $$ BEGIN EXECUTE format('GRANT SELECT, INSERT ON osm_copy TO %I', current_setting('accessibility_db.service_account_name')); END $$",
    "DO $$ BEGIN EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON osm_way, osm_node, osm_way_node TO %I', current_setting('accessibility_db.service_account_name')); END $$",
    "DO $$ BEGIN EXECUTE format('GRANT SELECT, INSERT, UPDATE ON fact, vote TO %I', current_setting('accessibility_db.service_account_name')); END $$",
    "DO $$ BEGIN EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON account TO %I', current_setting('accessibility_db.service_account_name')); END $$",
)


def upgrade() -> None:
    """Creates every object of the target schema and grants the service account named by `migrations/env.py` its rights."""
    service_account_name = context.config.attributes.get("service_account_name")
    if not service_account_name:
        raise RuntimeError("migrations/env.py did not supply the name of the service account from DB_SERVICE_ACCOUNT_NAME.")
    for statement in CREATE_TARGET_SCHEMA_SQL:
        op.execute(statement)
    op.execute(sa.text(SET_SERVICE_ACCOUNT_NAME_SQL).bindparams(service_account_name=service_account_name))
    for statement in GRANT_SERVICE_ACCOUNT_SQL:
        op.execute(statement)


def downgrade() -> None:
    """Refuses to go below the first revision, because the supported way back is recreating the database."""
    raise NotImplementedError("The first revision has no downgrade. Recreate the local database: docker compose down, then up again.")
