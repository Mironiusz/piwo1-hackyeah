# Service layer

Document state: 2026-10-04

## Module role

The layer implements product decisions independently of an administrative command or an API request. For the OpenStreetMap importer, it does the following:

- validates the source;
- selects the pedestrian network;
- maps barriers and amenities and locates facts;
- decides disappearing facts and recovers the routing pointer;
- prepares routing tags;
- orchestrates one complete import, from exclusion to the routing pointer.

The shared administrative wrapper `apply_administrative_run` in `administrative.py` belongs to the backend foundation and is consumed, not changed, by the importer.

## Public interface

| Function                                  | Input                                                       | Output                                                                      |
| ----------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| `apply_osm_import_command`                | `OsmImportSettings`                                         | `OsmImportResult`, after running one import with the importer's HTTP client |
| `apply_osm_import`                        | `OsmImportSettings`, HTTPX asynchronous client              | `OsmImportResult` with outcome, source instant and counts                   |
| `resolve_osm_source_location`             | Absolute redirect location                                  | Validated source URL                                                        |
| `resolve_osm_checksum`                    | Published checksum text, selected filename, computed digest | Matching lowercase MD5                                                      |
| `resolve_osm_source_state`                | Source header timestamp                                     | Aware `datetime` preserving the offset                                      |
| `resolve_osm_source_is_newer`             | Source and optional current instants                        | Whether processing a newer copy is allowed                                  |
| `resolve_is_pedestrian_network_way`       | Read-only tag mapping                                       | Network eligibility                                                         |
| `resolve_way_facts`, `resolve_node_facts` | Tags, and for a node its motor-traffic membership           | Immutable attributes and fact types                                         |
| `resolve_osm_fact_location`               | Point, line or area in EPSG:4326                            | The fact's point                                                            |
| `resolve_osm_element_coverage`            | Validated boundary, point or line                           | Whether the element belongs to the copy                                     |
| `build_osm_fact_data`                     | Source snapshots, boundary, selected network, business zone | `OsmFactData`: present facts and motor-traffic node ids                     |
| `resolve_osm_disappearing_facts`          | Stored facts, fresh identities                              | Stored facts that disappear for the first time                              |
| `resolve_osm_fact_changes`                | Disappearing facts and their votes                          | A user report or a removal mark for each fact, by M4                        |
| `resolve_osm_routing_recovery`            | Committed and pointer copy names                            | `none`, `publish` or `integrity_failure`                                    |

The outcomes of `OsmImportResult` are:

- `updated`;
- `unchanged`;
- `skipped`;
- `routing_incomplete`, for a committed copy whose pointer could not be published;
- `commit_unknown`.

Every other ending is a named exception. `OSM_IMPORT_NAMED_ERRORS` lists the importer exceptions whose messages are constant texts and may be reported to the operator.

## Technical inputs and outputs

`OsmImportSettings` carries the following absolute paths, read from the settings by `worker/osm_import.py`, together with the business zone:

- the import workspace root;
- `ROUTING_DATA_DIR`;
- the Valhalla tool directory;
- the Valhalla configuration template.

The run reads the Geofabrik extract through `data/osm_source.py` and the database through the delivered engine, exclusion and publication. It writes, in this order:

1. The network, present facts and one `osm_copy` row inside one publication transaction.
2. `copies/<name>/` under `ROUTING_DATA_DIR` before that transaction.
3. The pointer `current` after a confirmed commit.

## Operating modes

There is one mode: a manual run of `python -m worker.osm_import`. It covers the first import and every refresh, on a team member's machine or in a one-off container of the backend image. Nothing schedules it and no API request starts it.

## File structure

```text
service/
  osm_import.py              orchestration of one run and its outcomes
  osm_acquisition.py         validated source acquisition
  osm_source_validation.py   source metadata rules
  osm_preparation.py         boundary, network selection, routing normalization
  osm_facts.py               present facts of the copy
  osm_geometry.py            fact locations and copy coverage
  osm_tag_rule.py            network predicate and tag mapping
  osm_tag_thresholds.py      closed tag lists and thresholds
  osm_tag_values.py          numeric tag forms
  osm_routing_tags.py        routing tag normalization
  osm_database_rows.py       network rows for the database
  osm_reconciliation.py      disappearing facts
  osm_publication.py         publication callback and commit-outcome checks
  osm_routing_preparation.py prepared copy and routing directory
  osm_routing_recovery.py    routing pointer recovery
```

## File responsibilities

`osm_import.py` holds exclusion, the 60-minute run deadline, the order of steps, the named refusal passed out of a rolled-back publication and the mapping of results to outcomes. The publication callback needs a server stamp of whole milliseconds, because the schema stores `timestamptz(3)`; `build_osm_stamp` cuts `fetch_business_now` to it.

`osm_acquisition.py` exposes the asynchronous context manager `fetch_osm_extract(client, directory, deadline)`. It works in a temporary directory inside the run workspace and removes the downloaded bytes when the context closes. The deadline is the run deadline's `expires_at`, valid for asyncio because its loop clock is `time.monotonic`.

`osm_preparation.py` assembles the Kraków boundary, checks every member ring and selects whole permitted ways with their ordered node references and original tags. `osm_facts.py` derives the facts of the copy in one source pass. `osm_routing_preparation.py` exposes `fetch_osm_prepared_copy`, which reads the source in three passes, and `apply_osm_routing_preparation`. The latter returns a verified `copies/<name>/`: it reuses a complete one, replaces an incomplete one never committed, and keeps a committed one while stopping the run.

`osm_publication.py` holds `apply_osm_copy_publication`, the callback of the shared transaction, `apply_osm_disappearance`, which locks and decides the facts that disappear for the first time, and `fetch_osm_commit_outcome`, the bounded checks after a lost commit confirmation. `osm_routing_recovery.py` holds the pointer decision and `apply_osm_routing_recovery`.

## Main records and contracts

- `OsmPreparedCopy`: original network, motor-traffic node ids, present facts and the boundary of Kraków, which `apply_osm_routing_preparation` writes into the copy directory.
- `OsmPublicationCounts`: nodes, ways, memberships and facts written.
- `OsmImportResult`: outcome, source instant and counts, which are absent unless a publication confirmed them.

A copy directory is named by the source instant in whole seconds since the epoch, and the pointer holds that name followed by a newline.

## Architectural decisions

The importer reuses the delivered engine, exclusion, publication, process supervisor, clock and logger, and adds no substitute. It has no vote rule of its own: a fact that disappears for the first time is decided with `resolve_fact_status` of `fact_status.py`, the evaluator every caller shares (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-52).

Geometry is computed in EPSG:2180 and stored in EPSG:4326 with the pinned Shapely and pyproj. The pure rules perform no filesystem, HTTP or database operation and create no timestamps from the clock. Their failures are named:

- `OsmSourceError` for source metadata;
- `OsmGeometryError` for unusable geometry;
- `OsmTagError` for a step count beyond the schema's smallint range.

Tests in `tests/service/` use invented values only and never touch the hosted database.

Source validation is in the rules layer because it decides which metadata may be accepted. Inputs are not mutated. The source header's offset and precision survive parsing. The synchronous source passes check the run deadline before each element, because a synchronous pyosmium pass cannot be interrupted by asyncio. Every Valhalla tool runs through `apply_import_process`, which ends the whole process group or Windows job before returning.

## Summary

One manual run admits itself under exclusion, recovers the pointer of the last committed copy, and acquires and validates the source. It then prepares the copy and its routing data, publishes the database copy in one transaction of at most 120 seconds and publishes the pointer after a confirmed commit. Every failure before commit leaves the previous copy and pointer unchanged.

## Address search

`address_search.py` holds the rules of the operation `search_address` of `docs/product/api_contract.md`, built by `plans_finished/address_search/`.

| Function                    | Input                       | Output                                                                       |
| --------------------------- | --------------------------- | ---------------------------------------------------------------------------- |
| `fetch_address_suggestions` | Search text as received     | `tuple[AddressSuggestion, ...]`, a coroutine; the one entry of the API layer |
| `resolve_search_text`       | Search text as received     | The prepared text sent out                                                   |
| `build_address_label`       | `NominatimPlace`            | The full label of the place                                                  |
| `build_address_suggestions` | Places in the service order | The suggestions in Kraków, one per label                                     |

`AddressSuggestion` is a frozen record of `label`, `lat` and `lon`; the tuple keeps a remembered answer unchangeable by a caller. The two named failures are `InvalidSearchTextError`, which the API layer answers as `invalid_search_text`, and `AddressSearchUnavailableError`, answered as `address_search_unavailable`. The failure of the data layer, `NominatimRequestError`, never leaves this module, because the API layer may not import the data layer.

The process holds two instances: `SEARCH_CACHE`, a `SearchCache` of at most `CACHE_MAX_ENTRIES` answers kept for `CACHE_TIME_TO_LIVE_SECONDS`, and `SEARCH_GATE`, a `SearchGate` with `GATE_INTERVAL_SECONDS` and `GATE_MAX_WAIT_SECONDS`. Both live in the event loop of the one API process and need no lock, because no `await` stands between reading and updating them. This is why the search, unlike the other operations, is asynchronous: the call to the public instance does not block the loop, and one limit of 5 seconds bounds the whole call (`plans_finished/address_search/ADDRESS_SEARCH_PLAN.md` D-1). The limit of one request per 1.1 seconds and the memory hold only while the service runs as exactly one process. Nothing of a search reaches the database or the disk.

## GTFS step

`gtfs_import.py` and `gtfs_feeds.py` hold the step of the loading program of `plans/public_transport_routing/`, the routing data with public transport of O9. It is a manual run of `python -m worker.gtfs_import`, after `python -m worker.osm_import` in the same one-off container; nothing schedules it and no API request starts it.

| Function                           | Input                                             | Output                                                                                         |
| ---------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `apply_gtfs_import_command`        | `GtfsImportSettings`                              | `GtfsImportResult`, after one run with the client of `data/gtfs_source.py` and a 30-minute run |
| `apply_gtfs_import`                | `GtfsImportSettings`, HTTPX client, run deadline  | `GtfsImportResult`, under the exclusion of the importer                                        |
| `fetch_transit_serves_copy_in_use` | `ROUTING_DATA_DIR`                                | Whether `transit/current` was built from the OpenStreetMap copy `current` names                |
| `build_transit_valhalla_config`    | Template, run workspace, archive path             | The configuration of the walking build with the GTFS input, the ingest output and the timezone |
| `apply_gtfs_feed_preparation`      | Feed zip, new directory of the ingest input       | The feed unpacked, with stops, trips and routes rewritten by the rules below                   |
| `build_gtfs_stop_rows`             | Rows of `stops.txt`                               | The rows with `wheelchair_boarding` decided by `resolve_gtfs_accessibility`                    |
| `build_gtfs_trip_rows`             | Rows of `trips.txt`                               | The rows with `wheelchair_accessible` decided by `resolve_gtfs_accessibility`                  |
| `build_gtfs_route_rows`            | Rows of `routes.txt`                              | The rows with `route_type` 900 turned into 0                                                   |
| `resolve_gtfs_accessibility`       | A value of the feed, an inherited value or `None` | 1 or 2 kept, an empty value or 0 turned into the inherited 1 or 2, or into 1                   |

`GtfsImportSettings` carries the import workspace root, `ROUTING_DATA_DIR`, the Valhalla tool directory and the configuration template; `worker/gtfs_import.py` reads them through `build_osm_import_settings` of `worker/osm_import.py`, so a missing path is named exactly as the import names it. `GtfsImportResult` holds the outcome - `built`, `reused`, `skipped`, `no_gtfs_copy` or `no_osm_copy` -, what became of the fresh fetch - `fetched`, `failed` or `not_run` - and the name of the data pointed to. Every other ending is a named exception; `GTFS_IMPORT_NAMED_ERRORS` lists those whose messages are constant texts. `GtfsFeedError` is the failure of `gtfs_feeds.py`.

The step takes the exclusion of the importer, because only that exclusion admits a workspace and so that it never overlaps an import that moves the pointer `current`. A failed or incomplete fetch, or one whose feeds `apply_gtfs_feed_check` cannot prepare, is not a failure of the run: the earlier GTFS copy stays in use and the build runs from it. A copy that cannot be stored ends the run. The worker exits 0 only when the run did not fail and `fetch_transit_serves_copy_in_use` holds. `gtfs_feeds.py` reads and writes the files of a feed itself, since unpacking is the whole of its rule; its rules, the `build_gtfs_*_rows` functions, take and return rows only.

## Accounts

Five files hold the accounts of `plans_finished/accounts/`: the operations `create_account`, `log_in`, `read_own_account` and `delete_own_account` of `docs/product/api_contract.md`, and the one resolution of the actor and of the moderator role every other operation uses.

| File                | Responsibility                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| `account_rules.py`  | The input rules of a pseudonym and a password, `resolve_pseudonym` and `resolve_password`              |
| `passwords.py`      | The Argon2id hash, `build_password_hash`, `resolve_password_match` and `UNKNOWN_ACCOUNT_PASSWORD_HASH` |
| `session_tokens.py` | The signed token, `build_session_token` and `resolve_session_claims`, and `SessionExpiredError`        |
| `actors.py`         | `resolve_request_actor`, `resolve_account_actor`, `resolve_moderator_actor` and the key of the facade  |
| `accounts.py`       | `apply_account_creation`, `resolve_login` and `apply_account_deletion`                                 |

| Function                  | Input                                                            | Output                                                                                          |
| ------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `resolve_request_actor`   | The header `Authorization` or `None`, an aware instant           | `SessionResolution`: `AccountActor` and the renewed token, or neither                           |
| `resolve_account_actor`   | `SessionResolution`                                              | `AccountActor`, or `AuthenticationRequiredError`                                                |
| `resolve_moderator_actor` | `SessionResolution`                                              | `AccountActor` holding the role, or `AuthenticationRequiredError`, `ModeratorRoleRequiredError` |
| `apply_account_creation`  | Pseudonym and password as received, instant in the business zone | `AccountView`, or `InvalidAccountInputError`, `PseudonymTakenError`                             |
| `resolve_login`           | Pseudonym and password as received, aware instant                | `LoginResult` with the token, or `InvalidCredentialsError`                                      |
| `apply_account_deletion`  | `AccountActor`                                                   | Nothing, or `SessionExpiredError` when the account was deleted first                            |

`AccountActor` is the frozen record of `account_id`, `pseudonym` and `is_moderator`, read again on every request; `SessionResolution` pairs it with `renewed_token`; `AccountView` is the shared object Account of the contract and `LoginResult` adds `session_token`. A token and a hash are left out of the text of every record. The named failures are answered by the programming interface layer: `InvalidAccountInputError` with its `field` as `invalid_request`, `PseudonymTakenError` as `pseudonym_taken`, `InvalidCredentialsError` as `invalid_credentials`, `SessionExpiredError` as `session_expired`, `AuthenticationRequiredError` as `authentication_required` and `ModeratorRoleRequiredError` as `moderator_role_required`. `actors.py` re-exports `SessionExpiredError` of `session_tokens.py`, so a consumer imports the session refusals from one module.

Every operation that reaches the database opens one short transaction of its own on `fetch_api_engine()` and passes its connection to `data/accounts.py`; the password is hashed and verified outside it. `actors.py` reads `SESSION_SIGNING_KEY` from the configuration facade inside `fetch_session_signing_key`, so importing the module needs no configuration. The three pure files perform no database, file or network operation and read no clock: the caller passes the instant. Their tests are scenario tests with explicit instants, the actor matrix replaces the data layer, and the critical test `tests/service/test_accounts_critical.py` walks one account through the local database.

## Walking route and the status of a fact

Six files hold the walking route of `plans_finished/route_planning/`, the operation `plan_route` of `docs/product/api_contract.md`, and the one status rule of M4 that the route, the importer and `community_facts` share.

| File                | Responsibility                                                                                                                            |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `fact_status.py`    | `FactStatus`, `FactVoteRecord`, `FactStatusResult`, `FactView` and `resolve_fact_status`, the status rule of M4                           |
| `route_planning.py` | `resolve_route`, the order of one route request, `PointOutsideKrakowError` and the records of the answer                                  |
| `route_graph.py`    | `RoutePoint`, the graph of the copy kept by the process and the path with the fewest barriers                                             |
| `route_requests.py` | The bodies of the walking request and of the trace, the corridor, the polygons of geozones and what a route avoids                        |
| `route_segments.py` | The tie of a traced route to the stretches, the place of every fact, the state of a segment, the list of M8 and `RoutingUnavailableError` |
| `route_boundary.py` | The boundary of Kraków of the copy kept by the process and the points outside it                                                          |

| Function                        | Input                                                                      | Output                                                                                       |
| ------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `resolve_route`                 | Start, destination, the barrier types and the amenity types of the profile | `RouteAnswer`, or `PointOutsideKrakowError`, `RoutingUnavailableError`                       |
| `resolve_fact_status`           | Every vote of a fact, whether it was removed in OpenStreetMap              | `FactStatusResult`: the status, the two weighted sums and the day of the latest confirmation |
| `build_route_graph_at_start`    | Nothing                                                                    | Nothing; the graph of the copy in use, built in the lifespan of the API process              |
| `fetch_route_graph`             | Connection of the snapshot, instant of the copy                            | `RouteGraph` of that copy, rebuilt only when the instant changes                             |
| `resolve_fewest_barriers_path`  | Graph, two points, the count of barriers per stretch                       | `FewestBarriersPath`, the stretches of the path with the fewest barriers                     |
| `resolve_points_outside_krakow` | Instant of the copy, two points                                            | `start`, `destination`, both in this order, or nothing                                       |
| `resolve_avoided_barriers`      | The placed facts of an area, the barrier types of the profile              | The barriers and geozones a route avoids                                                     |
| `build_route_segments`          | Graph, trace, two points                                                   | One `TracedSegment` per part of a stretch, with the two straight stretches to the network    |
| `resolve_segment_state`         | Segment, graph, placed facts, barrier types of the profile                 | `SegmentAssessment`: the state, the missing attributes and the marking `wheelchair=no`       |
| `resolve_route_lists`           | Segments, graph, placed facts, the profile                                 | `RouteLists`, the three groups of M8 in order along the route                                |

`RouteAnswer` holds `osm_copy_date`, `barrier_free_route_exists`, `route` and `alternative`; `PlannedRoute` the length, the segments and the three groups of its list; `PlannedAlternative` a route and `avoided_barriers`; `RouteSegment` a line, a length, a state, the missing attributes and the marking; `RouteFactView` a `FactView` with `distance_from_start_m` and `is_overruled_by_osm`. `SegmentState` has the four states of M7 and `not_assessed`. The two named failures are answered by the programming interface layer: `PointOutsideKrakowError` with its `points` as `point_outside_krakow` and `RoutingUnavailableError` as `routing_unavailable`. `RoutePoint` lives in `route_graph.py` and `RoutingUnavailableError` in `route_segments.py`, because the graph and the segments need them and `route_planning.py` imports both.

Every route request reads in one `REPEATABLE READ READ ONLY` snapshot on `fetch_api_engine()`, so every read sees one state of the database. The graph and the boundary are caches of the process keyed by the instant of the copy; each is rebuilt under a `threading.Lock` when that instant changes, and a failed build or read leaves nothing behind. The graph is rebuilt inside the snapshot of the request with a statement limit of 60 seconds, so a route always uses one copy. The routing service is reached only through `data/valhalla.py`, which retries nothing; the two repetitions are rules of this layer: a trace once more with `walk_or_snap` after error 443, and a route once more with the crossed barriers excluded. A database error or a failure of the routing service becomes `RoutingUnavailableError`, logged at ERROR with its kind and never with a coordinate. The tests are scenario tests on small invented networks, with the functions of the data layer replaced at their seam; the reads themselves are covered by the critical tests of `tests/data/`.

## Sample data

`sample_data.py` holds the sample step of `plans/sample_data/`: it validates four fictional demonstration facts and reconciles them without resetting contributions. The fixed dataset and the loading contract are in `docs/data/sample_data.md`.

`apply_sample_data() -> SampleDataResult` takes no arguments. It returns only after an acknowledged commit or raises the failure described in `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`. The result carries `outcome`, `created_count`, `unchanged_count`, `initial_votes_created_count` and the four stable identifiers.

The operation reads typed network, fact and fictional-author snapshots through `data/sample_data.py`, prepares the missing facts and receives an acknowledged transaction result. The database package supplies the closed lists and the offset pairs; the clock and the logger of the backend foundation are bound when the provider is called, so importing its pure decisions neither reads configuration nor configures logging. These runtime dependencies are required, with no private replacement.

The step is a synchronous administrative step of the common loading program, which owns its adapter and command. No endpoint, separate command, automatic retry or periodic task is supplied here. `sample_data.py` holds the fixed dataset, the pure network, content and history decisions and the transactional orchestration. `common_sample_data.py` in the repository root holds the immutable definitions, measured prerequisites, reconciliation snapshots and results. `SampleDataFailure` is the public alias of `SampleDataError`, keeping the handoff contract while satisfying the exception naming rule. Database access stays behind the data layer.

## Relation to SERVICE_ALGORITHM.md

`SERVICE_ALGORITHM.md` describes the domain rules and the run order these files implement.
