# Naming registry

Document state: 2026-10-04

## What this file is

A registry of names actually used in the repository. It describes the actual state, not the target one - unlike `standard_naming.md`, which sets the rules. When the registry and the standard diverge, the standard says what should be and the registry says what is; the divergence between them is information, not an error of either of them.

The deviation rule applies here differently than to the standards: the registry describes the actual state by definition, so it is impossible to be non-compliant with it. It can only be outdated - and that is the only way this file can be wrong.

## How to use it

Before you invent a name for a new file, function or constant, check whether the pattern is already here. If it is, use it. If it is not, and the name is likely to repeat, add it here together with its first place of use. This way a second person will not invent a different name for the same thing.

## Current state

The first entries came on 2026-10-04 with the package `db/` of `plans/schema_first_revision/`, the first code of the project. The names the template brought with it - the `makefile` targets and the architecture tests - have not been entered. The target rule is in `standard_naming.md`; the actual state goes here.

## Names in the database

Every object the first revision `db/accessibility_db/migrations/versions/0001_target_schema.py` creates, which is also its first place of use. PostgreSQL stores an unquoted name in lower case, so the stored name is the name of `docs/product/schema.md` in lower case; a column is named only in `docs/product/schema.md`.

| Name in `docs/product/schema.md`           | Stored name                                | Kind                   | Table or domain      |
| ------------------------------------------ | ------------------------------------------ | ---------------------- | -------------------- |
| `postgis`                                  | `postgis`                                  | extension              | -                    |
| `utc_offset_minutes`                       | `utc_offset_minutes`                       | domain                 | -                    |
| `CK_utc_offset_minutes_range`              | `ck_utc_offset_minutes_range`              | check of a domain      | `utc_offset_minutes` |
| `fact_type`                                | `fact_type`                                | domain                 | -                    |
| `CK_fact_type_closed_list`                 | `ck_fact_type_closed_list`                 | check of a domain      | `fact_type`          |
| `fact_source`                              | `fact_source`                              | domain                 | -                    |
| `CK_fact_source_closed_list`               | `ck_fact_source_closed_list`               | check of a domain      | `fact_source`        |
| `osm_element_type`                         | `osm_element_type`                         | domain                 | -                    |
| `CK_osm_element_type_closed_list`          | `ck_osm_element_type_closed_list`          | check of a domain      | `osm_element_type`   |
| `way_barrier_state`                        | `way_barrier_state`                        | domain                 | -                    |
| `CK_way_barrier_state_closed_list`         | `ck_way_barrier_state_closed_list`         | check of a domain      | `way_barrier_state`  |
| `kerb_point_state`                         | `kerb_point_state`                         | domain                 | -                    |
| `CK_kerb_point_state_closed_list`          | `ck_kerb_point_state_closed_list`          | check of a domain      | `kerb_point_state`   |
| `vote_verdict`                             | `vote_verdict`                             | domain                 | -                    |
| `CK_vote_verdict_closed_list`              | `ck_vote_verdict_closed_list`              | check of a domain      | `vote_verdict`       |
| `osm_copy`                                 | `osm_copy`                                 | table                  | -                    |
| `PK_osm_copy`                              | `pk_osm_copy`                              | primary key            | `osm_copy`           |
| `UX_osm_copy_state_at`                     | `ux_osm_copy_state_at`                     | unique constraint      | `osm_copy`           |
| `osm_way`                                  | `osm_way`                                  | table                  | -                    |
| `PK_osm_way`                               | `pk_osm_way`                               | primary key            | `osm_way`            |
| `CK_osm_way_stairs_state`                  | `ck_osm_way_stairs_state`                  | check                  | `osm_way`            |
| `CK_osm_way_absent_by_default_only_stairs` | `ck_osm_way_absent_by_default_only_stairs` | check                  | `osm_way`            |
| `IX_osm_way_geog`                          | `ix_osm_way_geog`                          | index                  | `osm_way`            |
| `osm_node`                                 | `osm_node`                                 | table                  | -                    |
| `PK_osm_node`                              | `pk_osm_node`                              | primary key            | `osm_node`           |
| `osm_way_node`                             | `osm_way_node`                             | table                  | -                    |
| `PK_osm_way_node`                          | `pk_osm_way_node`                          | primary key            | `osm_way_node`       |
| `FK_osm_way_node_way`                      | `fk_osm_way_node_way`                      | foreign key            | `osm_way_node`       |
| `FK_osm_way_node_node`                     | `fk_osm_way_node_node`                     | foreign key            | `osm_way_node`       |
| `CK_osm_way_node_sequence_index`           | `ck_osm_way_node_sequence_index`           | check                  | `osm_way_node`       |
| `IX_osm_way_node_node_id`                  | `ix_osm_way_node_node_id`                  | index                  | `osm_way_node`       |
| `fact`                                     | `fact`                                     | table                  | -                    |
| `PK_fact`                                  | `pk_fact`                                  | primary key            | `fact`               |
| `UX_fact_osm_identity`                     | `ux_fact_osm_identity`                     | unique constraint      | `fact`               |
| `UX_fact_idempotency_key`                  | `ux_fact_idempotency_key`                  | unique constraint      | `fact`               |
| `CK_fact_osm_identity_complete`            | `ck_fact_osm_identity_complete`            | check                  | `fact`               |
| `CK_fact_osm_edited_on_with_identity`      | `ck_fact_osm_edited_on_with_identity`      | check                  | `fact`               |
| `CK_fact_openstreetmap_has_identity`       | `ck_fact_openstreetmap_has_identity`       | check                  | `fact`               |
| `CK_fact_removed_only_openstreetmap`       | `ck_fact_removed_only_openstreetmap`       | check                  | `fact`               |
| `CK_fact_user_content_without_identity`    | `ck_fact_user_content_without_identity`    | check                  | `fact`               |
| `CK_fact_saved_report_has_idempotency_key` | `ck_fact_saved_report_has_idempotency_key` | check                  | `fact`               |
| `CK_fact_idempotency_key_sha256`           | `ck_fact_idempotency_key_sha256`           | check                  | `fact`               |
| `CK_fact_geozone`                          | `ck_fact_geozone`                          | check                  | `fact`               |
| `CK_fact_step_count`                       | `ck_fact_step_count`                       | check                  | `fact`               |
| `CK_fact_offset_pairs`                     | `ck_fact_offset_pairs`                     | check                  | `fact`               |
| `CK_fact_hidden_only_flagged`              | `ck_fact_hidden_only_flagged`              | check                  | `fact`               |
| `IX_fact_geog`                             | `ix_fact_geog`                             | index                  | `fact`               |
| `IX_fact_flagged_at`                       | `ix_fact_flagged_at`                       | index                  | `fact`               |
| `account`                                  | `account`                                  | table                  | -                    |
| `PK_account`                               | `pk_account`                               | primary key            | `account`            |
| `UX_account_pseudonym_lower`               | `ux_account_pseudonym_lower`               | unique index           | `account`            |
| `vote`                                     | `vote`                                     | table                  | -                    |
| `PK_vote`                                  | `pk_vote`                                  | primary key            | `vote`               |
| `FK_vote_fact`                             | `fk_vote_fact`                             | foreign key            | `vote`               |
| `FK_vote_account`                          | `fk_vote_account`                          | foreign key            | `vote`               |
| `UX_vote_account_day`                      | `ux_vote_account_day`                      | unique constraint      | `vote`               |
| `UX_vote_hash_day`                         | `ux_vote_hash_day`                         | unique constraint      | `vote`               |
| `CK_vote_account_only_with_account`        | `ck_vote_account_only_with_account`        | check                  | `vote`               |
| `CK_vote_hash_only_without_account`        | `ck_vote_hash_only_without_account`        | check                  | `vote`               |
| `CK_vote_voter_hash_sha256`                | `ck_vote_voter_hash_sha256`                | check                  | `vote`               |
| `IX_vote_fact_id_cast_at`                  | `ix_vote_fact_id_cast_at`                  | index                  | `vote`               |
| `IX_vote_account_id`                       | `ix_vote_account_id`                       | index                  | `vote`               |
| `accessibility_db.service_account_name`    | `accessibility_db.service_account_name`    | setting of the session | -                    |

## File names

- `db/accessibility_db/migrations/versions/<four-digit order>_<subject>.py` - a schema revision; the order of the chain is the order of the file names, first `0001_target_schema.py`.
- `db/accessibility_db/<responsibility>.py` - a module of the shared model, first `closed_lists.py` and `tables.py`.
- `db/tests/common_<topic>.py` - a helper shared by the tests of `db/tests/`, first `common_target_schema.py`, `common_stored_rows.py` and `common_critical_guard.py`.
- `db/compose.yaml` and `db/compose.deploy.yaml` - the Compose files of the local database and of the database of the hosted demo.

## Function names

- `fetch_environment_value` - reads one required entry from the environment outside the configuration facade, first in `db/accessibility_db/migrations/env.py` and `db/tests/conftest.py`.
- `build_offset_instant`, `build_local_datetime` - build the pair of an instant and its wall-clock time, in `db/accessibility_db/tables.py`.
- `build_instant_pair`, `build_closed_list_type`, `build_closed_list_values`, `resolve_null_pair` - build the mapping of a pair and of a closed list, in `db/accessibility_db/tables.py`.
- `apply_schema_revisions`, `resolve_application_allowed`, `build_schema_owner_url` - apply the chain and decide whether it may run, in `db/accessibility_db/migrations/env.py`.

## Names of query constants

- `CREATE_TARGET_SCHEMA_SQL`, `SET_SERVICE_ACCOUNT_NAME_SQL`, `GRANT_SERVICE_ACCOUNT_SQL` - the statements of the first revision.
- `INSERT_<ROW>_SQL` and `SELECT_<WHAT>_SQL` - the statements of the critical tests in `db/tests/`, for example `INSERT_HASH_VOTE_SQL` and `SELECT_TABLE_COLUMNS_SQL`.

## Names in tests

- `test_<what it checks>` in a file `db/tests/test_<subject>.py`; a file that touches the database carries `pytestmark = pytest.mark.critical`.
- `service_engine`, `service_connection`, `stored_fact_id` - the fixtures of `db/tests/conftest.py`.
- `schema_owner_engine` - the backend-owned local owner fixture required by `tests/conftest.py`; its delivery contract is `plans/sample_data/SAMPLE_DATA_BACKEND_HANDOFF.md`.
- `database_cleanup_registry` - the shared exact-key cleanup fixture in `tests/conftest.py`.
- `sample_critical_dataset` - the invented sample-network fixture in `tests/data/conftest.py`.

## Sample-loading interface

`service.sample_data.apply_sample_data` is the no-argument administrative provider. Its shared records live in `common_sample_data.py`. `SampleDataFailure` is the public alias of `SampleDataError`; the alias preserves the approved provider contract while the class follows exception naming conventions.

The sample definitions reserve `fact.id` -1 through -4. Ordinary facts keep generated identifiers, and sample retries never reallocate or overwrite these identifiers. This convention is documented in `docs/data/sample_data.md`.
