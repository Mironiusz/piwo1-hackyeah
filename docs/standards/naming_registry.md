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
- `service/<responsibility>.py` - a module of the rules layer, first `account_rules.py`, `passwords.py` and `session_tokens.py` of `plans_finished/accounts/`.
- `tests/common_<topic>.py` - data or a helper shared by the tests of `tests/`, for example `common_osm_source.py`, `common_runtime_settings.py` and `common_nominatim_answers.py`.

## Function names

- `fetch_environment_value` - reads one required entry from the environment outside the configuration facade, first in `db/accessibility_db/migrations/env.py` and `db/tests/conftest.py`.
- `build_offset_instant`, `build_local_datetime` - build the pair of an instant and its wall-clock time, in `db/accessibility_db/tables.py`.
- `build_instant_pair`, `build_closed_list_type`, `build_closed_list_values`, `resolve_null_pair` - build the mapping of a pair and of a closed list, in `db/accessibility_db/tables.py`.
- `apply_schema_revisions`, `resolve_application_allowed`, `build_schema_owner_url` - apply the chain and decide whether it may run, in `db/accessibility_db/migrations/env.py`.
- `resolve_pseudonym`, `resolve_password` - decide whether an input of a registration meets M9 and return the accepted value, in `service/account_rules.py`.
- `build_password_hash`, `resolve_password_match` - hash a password and decide whether a password matches a stored hash, in `service/passwords.py`.
- `build_session_token`, `resolve_session_claims` - issue a signed session token and decide whether one is valid, in `service/session_tokens.py`.

## Exception names

- `<What went wrong>Error` - every exception class ends in `Error`, because the ruff rule N818 of the `N` set of `pyproject.toml` refuses any other name; first `InvalidAccountInputError` in `service/account_rules.py` and `SessionExpiredError` in `service/session_tokens.py`.

## Names of query constants

- `CREATE_TARGET_SCHEMA_SQL`, `SET_SERVICE_ACCOUNT_NAME_SQL`, `GRANT_SERVICE_ACCOUNT_SQL` - the statements of the first revision.
- `INSERT_<ROW>_SQL` and `SELECT_<WHAT>_SQL` - the statements of the critical tests in `db/tests/`, for example `INSERT_HASH_VOTE_SQL` and `SELECT_TABLE_COLUMNS_SQL`.

## Names in tests

- `test_<what it checks>` in a file `db/tests/test_<subject>.py`; a file that touches the database carries `pytestmark = pytest.mark.critical`.
- `service_engine`, `service_connection`, `stored_fact_id` - the fixtures of `db/tests/conftest.py`.
- `test_<what it checks>` in a file `tests/service/test_<subject>_cases.py` - the scenario tests of the rules layer, first `test_account_rules_cases.py`, `test_passwords_cases.py` and `test_session_tokens_cases.py`.

## Names of the backend foundation

The names of `plans_finished/backend_skeleton/`, merged on 2026-10-04 from the branch `mw-backend-skeleton`.

- Layer packages: `api`, `service`, `data`, `worker`; shared configuration is `config` and time is `common_time`.
- Factories and actions: `build_app`, `build_engine`, `build_import_engine`, `build_database_url`, `apply_import_exclusion`, `apply_publication`, `apply_import_process`.
- SQL constants use `FETCH_..._SQL` or `APPLY_..._SQL` in `data/locks.py`; import admission and publication fence have separate keys.
- Planned public failure names such as `ImportAlreadyRunning` and `PublicationOutcomeUnknown` are aliases of exception classes ending in `Error`, satisfying the naming gate while preserving the shared contract.
- Launch targets: `backend`, `test-critical`, `check-unit`. The targets of the local database and of the revision runner left on 2026-10-04 with the local setup of the skeleton; the local database is started by the commands of `db/README.md`.

## Importer service names

- `service/osm_source_validation.py`: `resolve_osm_source_location`, `resolve_osm_checksum`, `resolve_osm_source_state`, `resolve_osm_source_is_newer` and `OsmSourceError` validate source metadata without I/O.
- `service/osm_tag_rule.py`: `resolve_is_pedestrian_network_way` is the shared predicate for stored network and routing PBF selection, following the backend architecture contract.
- `service/osm_tag_thresholds.py`: closed tag-value lists use the suffix `_VALUES`.

- `service/osm_tag_values.py`: `resolve_osm_length_m`, `resolve_osm_incline_percent` and `resolve_osm_step_count` parse numeric tag values; `OsmTagError` rejects unrepresentable step counts.
- `service/osm_geometry.py`: `resolve_osm_fact_location`, `resolve_osm_element_coverage` and `OsmGeometryError` implement geometry rules.
- `service/osm_routing_tags.py`: `build_osm_routing_node_tags` and `build_osm_routing_way_tags` create routing tag mappings.
- `data/osm_reader.py`: `OsmElementSnapshot`, `fetch_osm_elements`, `fetch_osm_header_timestamp` and `OsmReadError` describe local source reading.
- `data/osm_network_file.py`: `apply_osm_network_pbf` and `OsmNetworkFileError` describe prepared PBF writing.
- `data/routing_data.py`: `RoutingFileDigest`, `RoutingManifest`, `RoutingDataError`, `apply_osm_routing_manifest` and `fetch_osm_routing_manifest` describe completeness metadata; `build_routing_copy_name`, `fetch_routing_pointer`, `apply_routing_pointer`, `fetch_routing_preparations`, `apply_routing_preparation_directory`, `apply_routing_copy_placement` and `apply_routing_directory_removal` keep `copies/<name>/`, the `.prepare-` directories (`ROUTING_PREPARATION_PREFIX`) and the pointer `current` (`ROUTING_POINTER_NAME`) under `ROUTING_DATA_DIR`.

- `data/osm_source.py`: `build_osm_http_client`, `fetch_osm_latest_location`, `fetch_osm_checksum_text`, `apply_osm_download` and `OsmDownloadError` own HTTP transport.
- `service/osm_acquisition.py`: `OsmExtract` and `fetch_osm_extract` describe validated temporary source acquisition.
- `service/osm_preparation.py`: `OsmPreparedNetwork`, `build_osm_boundary`, `build_osm_boundary_rings`, `build_osm_network` and `build_osm_routing_network` describe selection and normalized copies.
- `service/osm_routing_preparation.py`: `OsmPreparedCopy`, `fetch_osm_prepared_copy`, `build_osm_valhalla_config` and `apply_osm_routing_preparation` read a source into a prepared copy and place its routing directory.
- `data/osm_valhalla.py`: `OsmTileBuildError`, `fetch_osm_valhalla_template`, `apply_osm_valhalla_config` and `apply_osm_valhalla_tiles` run the Valhalla tools through `apply_import_process`.

- `data/osm_copy.py`: `OsmFactIdentity`, typed source rows, `apply_osm_network`, `apply_osm_present_facts`, `fetch_osm_facts` (without row locks), `fetch_osm_facts_for_update`, `fetch_osm_fact_history` and `apply_osm_fact_changes` use the delivered database models.
- `service/osm_database_rows.py`: `build_osm_database_network` maps original network snapshots to database rows.
- `service/osm_facts.py`: `OsmFactData`, `OsmFactCandidate`, `OsmSourceScan` and `build_osm_fact_data` derive the present facts of a copy.
- `service/osm_reconciliation.py`: `resolve_osm_disappearing_facts` and `resolve_osm_fact_changes` find the facts that disappear for the first time and decide what each of them becomes.
- `service/osm_publication.py`: `OsmPublicationCounts`, `apply_osm_copy_publication`, `apply_osm_disappearance` and `fetch_osm_commit_outcome` form the publication callback, the decision on disappearing facts and the commit-outcome checks.
- `service/osm_routing_recovery.py`: `resolve_osm_routing_recovery`, `apply_osm_routing_recovery` and `OsmRoutingIntegrityError` recover the routing pointer.
- `service/osm_import.py`: `OsmImportSettings`, `OsmImportResult`, `OsmImportError`, `OSM_IMPORT_NAMED_ERRORS`, `apply_osm_import`, `apply_osm_import_command` and `build_osm_stamp` run one import; its outcomes are `updated`, `unchanged`, `skipped`, `routing_incomplete` and `commit_unknown`.
- `worker/osm_import.py`: the manual entry point `python -m worker.osm_import`, with `build_osm_import_settings`, `apply_osm_import_action`, `apply_osm_import_report` and `OSM_IMPORT_EXIT_CODES`.

## Address search names

The names of `plans_finished/address_search/`, the operation `search_address`.

- `api/address_search.py`: `SearchAddressRequest` with the field validator `resolve_utf8_text`, `fetch_address_matches`, `build_address_search_response` and `apply_address_search_routes`, which registers the route named `search_address`.
- `service/address_search.py`: `AddressSuggestion`, `InvalidSearchTextError`, `AddressSearchUnavailableError`, `resolve_search_text`, `build_address_label`, `build_address_suggestions`, `SearchCache` with `fetch_suggestions` and `apply_suggestions`, `SearchGate` with `resolve_wait_seconds`, the process instances `SEARCH_CACHE` and `SEARCH_GATE`, the coroutine `fetch_address_suggestions`, and the constants `SEARCH_TEXT_MAX_LENGTH`, `REMOVED_STREET_WORDS`, `KRAKOW_CITY`, `CACHE_TIME_TO_LIVE_SECONDS`, `CACHE_MAX_ENTRIES`, `GATE_INTERVAL_SECONDS` and `GATE_MAX_WAIT_SECONDS`.
- `data/nominatim.py`: `NominatimPlace`, `NominatimRequestError`, `build_nominatim_client`, `build_nominatim_places`, the coroutine `fetch_nominatim_places`, and the constants `NOMINATIM_SEARCH_URL`, `NOMINATIM_USER_AGENT`, `NOMINATIM_SEARCH_PARAMETERS` and `NOMINATIM_TIMEOUT_SECONDS`.
- `tests/common_nominatim_answers.py`: `RECORDED_ANSWERS`, the recorded answers keyed by the searched text.

## Public transport names

The names of `plans/public_transport_routing/`, the GTFS step of the routing data with public transport of O9.

- `data/gtfs_source.py`: `GtfsSourceError`, `build_gtfs_http_client`, `build_gtfs_published_day`, `fetch_gtfs_feed` and the constants `GTFS_FEED_URLS`, `GTFS_FEEDS` and `GTFS_REQUEST_TIMEOUT_SECONDS`.
- `data/gtfs_copy.py`: `GtfsCopy`, `GtfsCopyError`, `apply_gtfs_preparation`, `fetch_gtfs_preparations`, `apply_gtfs_feed_validation`, `apply_gtfs_copy`, `fetch_gtfs_copy`, `build_gtfs_feed_path` and the constants `GTFS_DIRECTORY_NAME`, `GTFS_DAYS_NAME`, `GTFS_COPY_NAME_PATTERN` and `GTFS_REQUIRED_MEMBERS`.
- `data/transit_build.py`: `TransitBuildError`, `build_transit_name`, `resolve_transit_copy_name`, `build_transit_directory`, `apply_transit_preparation`, `fetch_transit_preparations`, `apply_timezone_validation`, `apply_transit_build`, `fetch_transit_pointer`, `apply_transit_pointer` and the constants `TRANSIT_DIRECTORY_NAME`, `TRANSIT_ARCHIVE_NAME`, `TRANSIT_NAME_PATTERN` and `TRANSIT_SHELL`.
- `data/routing_directories.py`: `fetch_preparation_directories`, `apply_preparation_directory`, `apply_directory_placement`, `fetch_directory_pointer`, `apply_directory_pointer` and the constants `PREPARATION_PREFIX` and `POINTER_NAME`, the immutable directories and pointer of any parent directory.
- `service/gtfs_feeds.py`: `GtfsFeedError`, `GtfsRow`, `resolve_gtfs_accessibility`, `build_gtfs_stop_rows`, `build_gtfs_trip_rows`, `build_gtfs_route_rows`, `apply_gtfs_table`, `apply_gtfs_feed_preparation` and the closed lists `GTFS_TABLE_RULES`, `GTFS_REQUIRED_COLUMNS` and `GTFS_ADDED_COLUMNS`.
- `service/gtfs_import.py`: `GtfsImportSettings`, `GtfsImportResult`, `GTFS_IMPORT_NAMED_ERRORS`, `apply_gtfs_import_command`, `apply_gtfs_import`, `apply_gtfs_import_run`, `apply_gtfs_fetch`, `apply_gtfs_feed_check`, `apply_preparation_cleanup`, `build_transit_valhalla_config`, `apply_transit_data` and `fetch_transit_serves_copy_in_use`; its outcomes are `built`, `reused`, `skipped`, `no_gtfs_copy` and `no_osm_copy`, and those of the fetch `fetched`, `failed` and `not_run`.
- `worker/gtfs_import.py`: the manual entry point `python -m worker.gtfs_import`, with `build_gtfs_import_settings`, `apply_gtfs_import_action` and `apply_gtfs_import_report`.
- `tests/common_gtfs_feed.py`: `INVENTED_GTFS_TABLES` and `apply_invented_gtfs_feed`, the invented feeds of the tests.
- `PUBLIC_TRANSPORT_ENABLED`: the environment entry of the switch of public transport in `config/settings.py`.

## Walking route names

The names of `plans_finished/route_planning/`, the operation `plan_route` and the status rule of M4.

- `service/fact_status.py`: `FactStatus`, `FactVoteRecord`, `FactStatusResult`, `FactView`, `resolve_fact_status`, `resolve_status_from_sums`, `build_vote_person`, `build_vote_weight` and the constants `ACCOUNT_VOTE_WEIGHT`, `ANONYMOUS_VOTE_WEIGHT`, `STATUS_PERSON_COUNT` and `STATUS_WEIGHT_THRESHOLD`.
- `common_time.py`: `build_business_day`, the calendar day of an instant in the business zone.
- `data/engine.py`: `fetch_api_engine`, `fetch_read_only_snapshot`, `apply_statement_timeout`, `API_STATEMENT_TIMEOUT_MS` and the query constant `APPLY_STATEMENT_TIMEOUT_SQL`.
- `data/route_network.py`: `RouteNetworkArrays`, `fetch_route_network`, the query constants `FETCH_ROUTE_WAYS_SQL`, `FETCH_ROUTE_WAY_NODES_SQL` and `FETCH_ROUTE_NODES_SQL`, and `NETWORK_PARTITION_ROWS`, `WAY_BARRIER_STATES`, `WAY_BARRIER_COLUMNS`, `KERB_POINT_STATES` and `NO_KERB_POINT`.
- `data/route_facts.py`: `StoredFact`, `StoredRouteFact`, `StoredVote`, `fetch_route_facts`, `fetch_fact_votes`, `fetch_geozone_ways`, `VISIBLE_FACT_CONDITION`, the query constants `FETCH_ROUTE_FACTS_SQL`, `FETCH_COPY_ROUTE_FACTS_SQL`, `FETCH_FACT_VOTES_SQL` and `FETCH_GEOZONE_WAYS_SQL`, and `REPORT_STRETCH_DISTANCE_M` and `FACT_ID_BATCH_SIZE`.
- `data/valhalla.py`: `RoutingServiceError`, `RoutingServiceNoRouteError`, `RoutingServiceTraceError`, `RoutingServiceUnavailableError`, `ValhallaRoute`, `ValhallaEdge`, `ValhallaTrace`, `build_valhalla_client`, `fetch_valhalla_answer`, `fetch_served_copy_instant`, `fetch_valhalla_route`, `fetch_valhalla_trace` and the constants `VALHALLA_CALL_TIMEOUT_SECONDS`, `VALHALLA_NO_ROUTE_ERROR_CODE` and `VALHALLA_TRACE_ERROR_CODE`.
- `data/routing_data.py`: `ROUTING_BOUNDARY_NAME`, now one of `ROUTING_FILE_NAMES`, `apply_osm_boundary_file`, `build_routing_copy_directory` and `fetch_osm_boundary`.
- `service/route_graph.py`: `RoutePoint`, `RouteGraph`, `FewestBarriersPath`, `RouteGraphCache`, `ROUTE_GRAPH_CACHE`, `build_route_graph`, `fetch_route_graph`, `build_route_graph_at_start`, `resolve_fewest_barriers_path`, the helpers `build_*` of rows, stretches and coordinates, and `GRAPH_BUILD_STATEMENT_TIMEOUT_MS` and `BARRIER_STRETCH_WEIGHT`.
- `service/route_requests.py`: `ExcludedLocation`, `RouteExclusions`, `build_polyline_points`, `build_corridor_wkt`, `build_geozone_polygon`, `build_route_exclusions`, `build_route_body`, `build_trace_body`, `resolve_avoided_barriers`, `resolve_geozone_holds_point` and the constants `PEDESTRIAN_COSTING_OPTIONS`, `CORRIDOR_MIN_HALF_WIDTH_M`, `GEOZONE_POLYGON_VERTICES`, `SHAPE_MATCH_EDGE_WALK` and `SHAPE_MATCH_WALK_OR_SNAP`.
- `service/route_segments.py`: `RoutingUnavailableError`, `SegmentState`, `MissingAttribute`, `TracedSegment`, `PlacedFact`, `RouteFacts`, `SegmentAssessment`, `RouteFactView`, `RouteLists`, `build_route_facts`, `build_route_segments`, `resolve_segment_state`, `resolve_route_lists`, `resolve_crossed_barriers`, `resolve_fact_on_segment` and the constants `KERB_CONTRADICTION_DISTANCE_M`, `AMENITY_DISTANCE_M` and `REPORT_REPLACEMENT_CONFIRMATIONS`.
- `service/route_boundary.py`: `RouteBoundaryCache`, `ROUTE_BOUNDARY_CACHE`, `fetch_krakow_boundary` and `resolve_points_outside_krakow`.
- `service/route_planning.py`: `PointOutsideKrakowError`, `RouteAnswer`, `PlannedRoute`, `PlannedAlternative`, `RouteSegment`, `RouteRequest`, `CheckedRoute` and `resolve_route`.
- `api/route.py`: `PointBody`, `RouteRequestBody` with the validator `apply_unique_type_validation`, `plan_route`, the route named `plan_route`, `apply_route_routes` and `apply_route_lifespan`; `api/fact_body.py`: `build_fact_body`.
- `valhalla/start_routing_service.py`: `build_merged_config`, `build_routing_service_config`, `fetch_default_config`, `fetch_overrides`, `fetch_current_copy_name` and `main`; `valhalla/valhalla_overrides.json` holds the settings of the routing service the project sets.
- `tests/common_route_network.py` builds the invented networks of the route tests, `tests/common_runtime_settings.py` holds the invented settings shared by the tests that load the facade, and the fixture `service_transaction` of `tests/data/conftest.py` gives a rolled-back connection of the service account.

## Account names

The names of `plans_finished/accounts/`, the four account operations and the one actor resolution; the files, functions and exceptions of its first step are listed in the sections above.

- `api/accounts.py`: `ACCOUNTS_ROUTER` with the routes named `create_account`, `log_in`, `read_own_account` and `delete_own_account`, `AccountCredentialsRequest`, `CreateAccountRequest`, `LogInRequest`, `build_account_body` and `apply_account_routes`.
- `api/sessions.py`: `fetch_request_session`, `fetch_account_actor`, `fetch_moderator_actor`, `apply_session_token`, `SessionTokenMiddleware`, `apply_session_error_handlers` and the constants `SESSION_TOKEN_HEADER` and `SESSION_STATE_KEY`.
- `service/actors.py`: `AccountActor`, `SessionResolution`, `AuthenticationRequiredError`, `ModeratorRoleRequiredError`, `resolve_request_actor`, `resolve_bearer_token`, `resolve_account_actor`, `resolve_moderator_actor`, `fetch_session_signing_key` and the constant `BEARER_SCHEME`.
- `service/accounts.py`: `AccountView`, `LoginResult`, `PseudonymTakenError`, `InvalidCredentialsError`, `apply_account_creation`, `resolve_login` and `apply_account_deletion`.
- `data/accounts.py`: `StoredAccount`, `apply_account_insert`, `fetch_account_by_id`, `fetch_account_by_pseudonym`, `apply_account_delete`, `build_stored_account` and the statements `APPLY_ACCOUNT_INSERT_SQL`, `FETCH_ACCOUNT_SQL`, `FETCH_ACCOUNT_BY_ID_SQL`, `FETCH_ACCOUNT_BY_PSEUDONYM_SQL` and `APPLY_ACCOUNT_DELETE_SQL`.
- `tests/conftest.py`: the fixture `stored_account_cleanup`, which deletes the accounts a critical test registered before committing them.
- `SESSION_SIGNING_KEY`: the environment entry of the key that signs session tokens, with `SESSION_SIGNING_KEY_MIN_LENGTH` in `config/settings.py`.
