# Importer data layer

Document state: 2026-10-04

## Module role

The layer reads the source over HTTPS and from local files, runs the Valhalla tools, keeps the routing directories and the pointer, and exposes database operations on a caller-supplied SQLAlchemy connection. It constructs no database engine, manages no publication transaction and decides no product rule; selection, mapping and reconciliation belong to the service layer.

## Public interface

| Module                | Operations                                                                                                                                                                                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `osm_source.py`       | `build_osm_http_client`, `fetch_osm_latest_location`, `fetch_osm_checksum_text`, `apply_osm_download`                                                                                                                                                                           |
| `osm_reader.py`       | `fetch_osm_header_timestamp`, `fetch_osm_elements(path, deadline, invalid_areas)`                                                                                                                                                                                               |
| `osm_network_file.py` | `apply_osm_network_pbf`                                                                                                                                                                                                                                                         |
| `osm_valhalla.py`     | `fetch_osm_valhalla_template`, `apply_osm_valhalla_config`, `apply_osm_valhalla_tiles`                                                                                                                                                                                          |
| `routing_data.py`     | `apply_osm_routing_manifest`, `fetch_osm_routing_manifest`, `build_routing_copy_name`, `fetch_routing_pointer`, `apply_routing_pointer`, `fetch_routing_preparations`, `apply_routing_preparation_directory`, `apply_routing_copy_placement`, `apply_routing_directory_removal` |
| `osm_copy.py`         | `apply_osm_network`, `apply_osm_present_facts`, `apply_osm_fact_changes`, `apply_osm_copy_metadata`, `fetch_current_osm_copy`, `fetch_osm_copy_history`, `fetch_osm_facts`, `fetch_osm_facts_for_update`, `fetch_osm_fact_history`                                              |

The named failures are:

- `OsmDownloadError`;
- `OsmReadError`;
- `OsmNetworkFileError`;
- `OsmTileBuildError`;
- `RoutingDataError`.

A spent run deadline propagates as the shared `DeadlineExpiredError`.

## Technical inputs and outputs

`fetch_osm_elements` yields immutable `OsmElementSnapshot` values copied from pyosmium objects, including node references, relation members and assembled area WKB. It checks the run deadline before every element. Missing coordinates or source timestamps fail with `OsmReadError`. An area that native assembly left without an outer ring, from a broken multipolygon or a broken closed way of the source, is skipped and counted in the optional `OsmInvalidAreaTally`; its way or relation is still yielded, so for the layers above the area is simply missing. Every other failure to read or to build a geometry fails with `OsmReadError`.

`apply_osm_network_pbf` writes prepared snapshots and validates duplicate identities and node references. It preserves ordered references and records the source instant in the PBF header. Inputs are materialized to validate references before writing, so memory scales with the selected network.

`apply_osm_valhalla_tiles` runs `valhalla_build_tiles` and `valhalla_build_extract` from the supplied tool directory with the supplied configuration. Both run through the shared `apply_import_process` of `import_process.py`, which runs them without a shell in the run workspace and discards their output. On a spent deadline it ends the whole process group or Windows job before raising, and every writer is finished before the import releases exclusion. A nonzero exit becomes `OsmTileBuildError`. The archive must exist and be nonempty, and its modification time is then set to the source instant.

Under `ROUTING_DATA_DIR` the layer keeps the following:

- `copies/<name>/` with `network.osm.pbf`, `valhalla_tiles.tar`, `krakow_boundary.wkb` and `manifest.json`, where the name is the source instant in whole seconds since the epoch;
- `copies/.prepare-*` preparation directories, never published;
- the pointer `current`, which holds a copy name followed by a newline and is replaced through a synced temporary file and `os.replace`.

The manifest records the source instant, byte sizes and SHA-256 hashes of the three files of `ROUTING_FILE_NAMES`. `fetch_osm_routing_manifest` validates its exact schema and recomputes every digest, so a copy prepared before the boundary was kept is refused. `apply_osm_boundary_file` writes the boundary of Kraków, WKB in longitude and latitude, into a preparation directory before its manifest, never over an existing file.

## File responsibilities

`osm_source.py` owns the HTTPX client and every source request. TLS verification stays enabled, redirects are not followed and HTTP environment configuration is disabled. Transport errors become `OsmDownloadError`, and no request is retried inside a run. `httpx==0.28.1` is the selected transport pin.

`osm_copy.py` imports the actual `accessibility_db` tables and closed lists:

- it upserts selected network rows, replaces ordered membership and removes obsolete network rows;
- it identifies present facts by element type, element identity and fact type and updates only the source-owned fields, so identifiers, moderation, creation time and user content survive;
- it writes copy metadata and disappearance changes on the same supplied connection.

No function in `osm_copy.py` commits or opens a connection.

## Main records and contracts

`fetch_osm_facts` reads source-identified facts in ascending identity order without row locks. `fetch_osm_facts_for_update` locks only the given facts, in ascending identity order and in batches, and returns them as they are once locked. `fetch_osm_fact_history` then locks their vote rows in ascending fact and vote identity order and keeps person identifiers out of the snapshot representation. `apply_osm_fact_changes` writes the source and removal mark the service layer decided with the shared vote evaluator. Every lock lasts until the caller's transaction ends (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-15 and D-52).

## Architectural decisions

No image name, environment configuration or database connection factory is defined here. The caller supplies the tool directory, the configuration template and the routing root from the settings, and holds the shared import exclusion across preparation and publication. A manifest proves file completeness, not database commit state.

On Windows the osmium reader cannot open a path containing a non-ASCII character, so the workspace and routing paths must be ASCII there.

Tests use invented XML and PBF files and temporary directories. A real tile build from an invented source was verified on 2026-10-04 in a temporary Linux container built from the Valhalla 3.9.0 image. Database operations are exercised by the importer's critical tests against the local database of `db/compose.yaml`.

## Address search

`nominatim.py` is the one call site of the public Nominatim instance, used by `service/address_search.py` for the operation `search_address`.

| Name                          | Role                                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `fetch_nominatim_places`      | Coroutine: one search for a prepared text, giving `list[NominatimPlace]` in the order of the service                                        |
| `build_nominatim_client`      | A fresh `httpx.AsyncClient` per search, with an optional transport that only tests pass                                                     |
| `build_nominatim_places`      | Reads the body of an answer into places or refuses it                                                                                       |
| `NominatimPlace`              | Frozen record of `name`, `road`, `house_number`, `neighbourhood`, `quarter`, `suburb`, `city_district`, `postcode`, `city`, `lat` and `lon` |
| `NominatimRequestError`       | The named failure, with the attributes `cause` and `status`                                                                                 |
| `NOMINATIM_SEARCH_URL`        | `https://nominatim.openstreetmap.org/search`                                                                                                |
| `NOMINATIM_USER_AGENT`        | The identification of the application the terms of the service require                                                                      |
| `NOMINATIM_SEARCH_PARAMETERS` | The seven fixed query parameters of `plans_finished/geocoding/GEOCODING_PLAN.md` D-5                                                        |
| `NOMINATIM_TIMEOUT_SECONDS`   | 5 seconds for the whole call                                                                                                                |

The client sends only the User-Agent header besides the ones HTTPX adds itself, reads no proxy from the environment, follows no redirect and, being new for every search, keeps no cookie. The constants are not configuration, because they are the same in every environment and are no secret. The message of `NominatimRequestError` holds only the cause and the status, never the text or the address of the request, and `raise_for_status` of HTTPX is not used, because its message holds that address. Tests replace `build_nominatim_client` with the same function bound to an `httpx.MockTransport`, so the real headers and parameters are checked without a network.

## GTFS step

Four modules serve the GTFS step of `service/gtfs_import.py`, the routing data with public transport of O9.

| Module                   | Operations                                                                                                                                                                                                       |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gtfs_source.py`         | `build_gtfs_http_client`, `fetch_gtfs_feed(client, feed, target, deadline)`, `build_gtfs_published_day`, `GTFS_FEED_URLS`, `GTFS_FEEDS`                                                                          |
| `gtfs_copy.py`           | `apply_gtfs_preparation`, `fetch_gtfs_preparations`, `apply_gtfs_feed_validation`, `apply_gtfs_copy(root, feeds, preparation)`, `fetch_gtfs_copy(root)`, `build_gtfs_feed_path`, `GtfsCopy`                      |
| `transit_build.py`       | `apply_transit_preparation`, `fetch_transit_preparations`, `apply_transit_build`, `build_transit_name`, `resolve_transit_copy_name`, `build_transit_directory`, `fetch_transit_pointer`, `apply_transit_pointer` |
| `routing_directories.py` | `fetch_preparation_directories`, `apply_preparation_directory`, `apply_directory_placement`, `fetch_directory_pointer`, `apply_directory_pointer`                                                                |

The named failures are `GtfsSourceError`, `GtfsCopyError` and `TransitBuildError`; the directory operations of `routing_directories.py` raise the `RoutingDataError` of `routing_data.py`.

`gtfs_source.py` is the one call site of the GTFS of ZTP Kraków. `GTFS_FEED_URLS` holds the three public addresses of the city's data, `GTFS_KRK_T`, `GTFS_KRK_A` and `GTFS_KRK_M`; they are constants, not configuration, because they are the same in every environment and no secret. The client verifies certificates, has 30-second connection and read-inactivity limits, follows no redirect and reads no proxy from the environment. A fetch accepts only status 200 with a `Last-Modified` header in a zone and a nonempty body of its declared length, checks the run deadline before the request and between chunks, and turns every transport and file failure into `GtfsSourceError`; nothing is retried, because the next manual run is the retry. The day a feed was published is the calendar day of `Last-Modified` in the business zone, read through `build_business_day`.

Under `ROUTING_DATA_DIR` the step keeps the following, next to `copies/` and `current` of the importer:

- `gtfs/<name>/` with `GTFS_KRK_T.zip`, `GTFS_KRK_A.zip`, `GTFS_KRK_M.zip` and `feeds.json`, the day each feed was published, where the name is the instant the copy is made, right after its fetch, in whole seconds since the epoch;
- `gtfs/current`, the GTFS copy in use;
- `transit/<copy name>-<GTFS name>/valhalla_tiles.tar`, the archive with public transport built from the OpenStreetMap copy and the GTFS copy of its name;
- `transit/current`, the data with public transport in use;
- `gtfs/.prepare-*` and `transit/.prepare-*` preparations, never pointed to.

A directory is placed by a rename of its complete preparation and never changes afterwards, and a pointer is replaced through a synced temporary file and `os.replace`, the same way as `current` of the importer. `routing_directories.py` holds that mechanism for any parent directory and a pattern of names; `routing_data.py` keeps its own copy for `copies/`, because another initiative was changing that file when this one was written.

`apply_transit_build` runs `valhalla_build_timezones` through `/bin/sh -c`, the one tool whose output is the file it makes, then `valhalla_ingest_transit` and `valhalla_convert_transit` with the build configuration, all through `apply_import_process`, and then `apply_osm_valhalla_tiles` of `osm_valhalla.py`, which builds the tiles and the archive and stamps it with the instant of the OpenStreetMap copy. An empty timezone database or a failed tool gives `TransitBuildError`. The configuration itself is built by the service, because the specialization of the template lives there.

Tests use invented zips, `httpx.MockTransport` and the process supervisor replaced at its seam. On 2026-10-04 the fetch, the copy and the preparation of `service/gtfs_feeds.py` ran on the three real feeds in a scratch directory outside the repository, and the names of the configuration keys and the options of the transit tools were read from the image `valhalla-patched:3.9.0-a11y`; a build of the tiles with public transport has not been run from this code yet.

## Accounts

`accounts.py` reads and writes the table `account` for `service/accounts.py` and `service/actors.py`, always on a connection the service opened on `fetch_api_engine()` of `engine.py`, inside its transaction.

| Name                         | Role                                                                                                                        |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `apply_account_insert`       | Inserts an ordinary account with `is_moderator` false and the pair `created_at`; gives its identifier, or `None` when taken |
| `fetch_account_by_id`        | Reads the account of an identifier, or `None`                                                                               |
| `fetch_account_by_pseudonym` | Reads the account whose pseudonym is equal without regard to letter case, or `None`                                         |
| `apply_account_delete`       | Deletes the row of an account and says whether one was deleted                                                              |
| `StoredAccount`              | Frozen record of `account_id`, `pseudonym`, `password_hash`, left out of its text, and `is_moderator`                       |

The statements are SQLAlchemy Core on the columns of `accessibility_db.tables.Account`. The insert is `ON CONFLICT (lower(pseudonym)) DO NOTHING RETURNING id`, so the index `UX_account_pseudonym_lower` decides between two concurrent registrations and the second waits for the first transaction; the lookup compares `lower(pseudonym)` with `lower(:pseudonym)`, the expression of that index, so letter case follows the database. The deletion is one `DELETE ... RETURNING id`; `FK_vote_account` detaches the votes of the account in the same statement, and a vote insert holding its key-share lock on the row makes the deletion wait. The critical tests of `tests/data/test_accounts_critical.py` prove each of these on the local database of `db/compose.yaml`; facts and votes are written there only inside transactions rolled back after the test, because the service account cannot delete them.

## Community facts

`community_facts.py` reads and writes the tables `fact` and `vote` for the nine operations of the community facts that `service/` and `api/` build (`plans/community_facts/COMMUNITY_FACTS_PLAN.md` D-1 - D-9). It works on a connection the service opened on `fetch_api_engine()` of `engine.py`, inside the transaction of the caller, and it never commits, opens a connection, sets a statement limit or logs. It decides nothing: a lock gives the service layer the state it decides on, and a write does what it is told. The votes of the facts of any read come from `fetch_fact_votes` of `route_facts.py`, in one call for all of them.

| Record                                | Content                                                                                                                                                                          |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `StoredCommunityFact`                 | A `StoredFact` of `route_facts.py` with `flagged_at`, the pair of the first flag as one `OffsetInstant` or `None`, and `is_hidden`; no author, no account and no idempotency key |
| `StoredNearbyFact`                    | `fact` and `distance_m`, the exact geodesic distance in metres; the rounding to whole metres is the service layer's                                                              |
| `FactContent`                         | `fact_type`, `lat`, `lon`, `description`, `step_count` and `geozone_radius_m`, normalized by the caller                                                                          |
| `AccountVoter` and `AnonymousVoter`   | The two kinds of `Voter`: an `account_id`, or the 32 bytes `voter_hash` of a person without an account, left out of the text of the record                                       |
| `FactInsertOutcome`                   | The `fact` of a save and `is_created`, false for a repeated save                                                                                                                 |
| `StoredVoteInsert` and `VoteDayTaken` | The two kinds of `VoteInsertOutcome`: the `vote_id` and `cast_on` of the stored vote, or the `cast_on` of the stored vote that refused the new one                               |
| `VoteAccountMissingError`             | A vote named an account that no longer exists; the message is constant and carries no identifier                                                                                 |

| Operation                      | Role                                                                                                                                                                                              |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fetch_stored_facts_in_area`   | The visible facts whose point lies in a rectangle, the edge included, by identity and at most `limit`; the caller passes one above the cap of the contract to learn that the rectangle holds more |
| `fetch_stored_fact`            | One fact by identifier in any status, a fact removed in OpenStreetMap included, or `None` for a hidden or a missing one                                                                           |
| `fetch_stored_nearby_facts`    | The visible facts of one type within a distance of a point, the distance included, nearest first, with the exact distance                                                                         |
| `fetch_stored_flagged_facts`   | Every flagged fact, the hidden ones included, the most recently flagged first                                                                                                                     |
| `fetch_stored_fact_for_vote`   | Locks a fact for a vote and reads it as it is once locked, hidden or removed or not, or `None`                                                                                                    |
| `fetch_stored_fact_for_change` | Locks a fact for a flag, a hiding or a restoration and reads it as it is once locked, or `None`                                                                                                   |
| `apply_fact_insert`            | Saves a report or a geozone with the confirmation of its author as its first vote, once per idempotency key                                                                                       |
| `apply_vote_insert`            | Stores a vote at the instant the caller gives, or says which day refused it                                                                                                                       |
| `apply_fact_flag`              | Marks a fact flagged and keeps the first instant                                                                                                                                                  |
| `apply_fact_hiding`            | Hides a fact and keeps the first instant                                                                                                                                                          |
| `apply_fact_restoration`       | Clears the hidden mark and keeps the flag and the votes                                                                                                                                           |

Two visibility rules of the contract differ on purpose and each lives in one place. The map and the check for existing facts use `VISIBLE_FACT_CONDITION` of `route_facts.py`, which leaves out hidden facts and facts removed in OpenStreetMap; the reading by identifier uses `UNHIDDEN_FACT_CONDITION`, which leaves out only the hidden ones. A rectangle is compared as geometry, because the edges of a geography rectangle are geodesic and bulge north of the parallels, so it does not use the index `IX_fact_geog` and scans the facts; a geozone counts by its point. A fact with a negative identifier of the sample data is read and written like any other.

The moderation writes check neither the source, nor the flag, nor the hidden mark; the service layer decides on the state the lock gave back, and `CK_fact_hidden_only_flagged` stays the last guard of the database. The two locks are the lock of the vote, `FOR SHARE`, and the lock of the change, `FOR NO KEY UPDATE`. The first conflicts with the `FOR UPDATE` the publication of a fresh copy takes on the facts it reconciles (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-15) and with the lock of the change, so a vote waits for both, while two votes on one fact do not wait for each other; a vote holds only its own fact, so it adds no cycle to the ascending order of the publication.

What the service layer has to keep to use these operations correctly:

- One request is one transaction on its connection. It uses the isolation READ COMMITTED of the engine default: `apply_fact_insert` waits on the unique index of the idempotency key and, after a conflict, reads the fact the other transaction committed, which a REPEATABLE READ transaction would not see.
- The lock comes before the decision and before every write on the same fact. The caller raises the statement limit to 120000 ms before `fetch_stored_fact_for_vote` with `apply_statement_timeout` and restores 5000 ms after it; this module sets no limit.
- The caller takes the instant of a vote from `fetch_business_now` after the lock, so the day of the vote is the day of the write and not of the arrival.
- A vote of an account that no longer exists raises `VoteAccountMissingError` after an integrity failure of the database, and so does the confirmation of an author whose account no longer exists inside `apply_fact_insert`. The transaction is then aborted and the caller rolls it back, so a failed save leaves neither the fact nor the vote. `VoteDayTaken` is an answer and leaves the transaction usable.
- A repeated save returns the stored fact, hidden or not, and stores nothing; the comparison of its content with the request and the answer for a hidden fact are the service layer's.

The critical tests of `tests/data/test_community_facts_critical.py` cover each of these on the local database of `db/compose.yaml`, the vote against a publication on two real connections included; `tests/data/test_community_facts_cases.py` fixes the lock modes, the visibility predicates and the columns of the statements without a database.

## Walking route

Five modules serve the walking route of `service/route_planning.py`.

| Module             | Names                                                                                                                                                                                                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `engine.py`        | `fetch_api_engine`, the one pooled engine of the API process with a statement limit of 5 seconds; `fetch_read_only_snapshot`; `apply_statement_timeout`                                                                                                                                             |
| `route_network.py` | `RouteNetworkArrays` and `fetch_route_network`, the ways, their ordered nodes and the nodes of the copy as numpy arrays, read in partitions of 100 000 rows                                                                                                                                         |
| `route_facts.py`   | `StoredFact`, `StoredRouteFact`, `StoredVote`, `fetch_route_facts`, `fetch_fact_votes`, `fetch_geozone_ways`, `VISIBLE_FACT_CONDITION` and the query constants `FETCH_*_SQL`                                                                                                                        |
| `valhalla.py`      | `build_valhalla_client`, `fetch_served_copy_instant`, `fetch_valhalla_route`, `fetch_valhalla_trace`, the records `ValhallaRoute`, `ValhallaTrace` and `ValhallaEdge`, and `RoutingServiceError` with `RoutingServiceNoRouteError`, `RoutingServiceTraceError` and `RoutingServiceUnavailableError` |
| `routing_data.py`  | `ROUTING_BOUNDARY_NAME`, `apply_osm_boundary_file`, `build_routing_copy_directory` and `fetch_osm_boundary`                                                                                                                                                                                         |

`fetch_read_only_snapshot` opens one `REPEATABLE READ READ ONLY` transaction and rolls it back at the end; `apply_statement_timeout` sets the limit of the current transaction only, with the value as a bound parameter. Every read of the route runs on the connection of its caller. `VISIBLE_FACT_CONDITION`, a fact neither hidden nor removed in OpenStreetMap, is the one visibility predicate of the facts, which `community_facts` reuses. `valhalla.py` is the one call site of the routing service (`docs/standards/standard_architecture.md`, Calls to external systems): one cached `httpx.Client` bound to `ROUTING_SERVICE_URL`, with a timeout of 2 seconds, no proxy from the environment and no redirect; it caches no answer and retries nothing. `fetch_osm_boundary` reads the boundary of a copy only through its manifest. The tests of `valhalla.py` use `httpx.MockTransport`, the boundary file is checked in temporary directories, and `engine.py`, `route_network.py` and `route_facts.py` are checked by critical tests against the local database of `db/`, each inside a transaction rolled back after the test.

## Tile archive

`tile_archive.py` holds the file operations of the tile step of `service/tile_archive.py`. It reads and writes files only and touches no database.

| Name                            | Role                                                                                                                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fetch_tile_directory_presence` | Whether a path is a directory that is not a link                                                                                                                         |
| `fetch_tile_file_digest`        | The SHA-256 hex digest of a regular file read in chunks under the run deadline, or `None` for a missing path, a directory and a link                                     |
| `apply_tile_file_copy`          | A copy of the source in a new `.tile-archive-*` file of the served directory, written in chunks under the run deadline, mode 0644, synced                                |
| `apply_tile_file_placement`     | The temporary file put under the served name with one `os.replace`, and on Linux a sync of the directory                                                                 |
| `apply_tile_file_removal`       | The removal of one file if it is still there                                                                                                                             |
| `apply_tile_temporary_cleanup`  | The removal of a temporary copy that was not placed; a failed removal is logged as a warning and left to the next run, so it never hides the failure that ended the copy |
| `apply_tile_leftover_removal`   | The removal of every regular `.tile-archive-*` file of a directory, with the count removed                                                                               |
| `TILE_FILE_CHUNK_BYTES`         | 1 048 576, the size of one chunk of every read and write                                                                                                                 |
| `TILE_TEMPORARY_PREFIX`         | `.tile-archive-`, the prefix of the temporary copies                                                                                                                     |
| `TILE_FILE_MODE`                | 0644, the mode of the copy, so a proxy running as another user can read the public archive                                                                               |

A failed read, copy, placement or removal raises `TileFileError` with one of four constant messages that name no path; the service turns it into the reason of its step. An exhausted run deadline passes on as the `DeadlineExpiredError` of `common_time.py`, which is a `TimeoutError` and so an `OSError`, so every function handles it before an `OSError`. The atomic replacement follows `apply_routing_pointer` of `routing_data.py` and the sync of the directory `apply_journal_write` of `import_workspace.py`. The tests run on temporary directories; on 2026-10-04 the Linux paths - the mode of the copy, a link at the served name and the sync of the directory - also ran in a Linux container of the image `python:3.13-slim`.

## Sample data

`sample_data.py` holds the storage of the sample step of `service/sample_data.py`. It opens its own connection and runs every statement in one Repeatable Read transaction.

| Name                                                  | Role                                                                                                                                                                                                               |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fetch_sample_prerequisites`                          | For each definition: whether a copy exists, whether its reference way exists, the two nearest ways within 15 m with their distances and the distance of the reference way                                          |
| `fetch_stored_samples`                                | The immutable content and creation pair of the facts on the reserved identifiers, without moderation fields                                                                                                        |
| `fetch_sample_votes`                                  | Every vote on a sample fact cast under one of its defined fictional voter identities, with its verdict, account fields and pair                                                                                    |
| `apply_sample_inserts`                                | The missing facts with their creation, flag and hide pairs in one batch, then the votes of exactly the facts returned as new in another; a vote batch that returns another count fails with `initial_vote_invalid` |
| `apply_sample_transaction`                            | One connection of `build_engine(5000)` in Repeatable Read, the action of the service and a commit whose acknowledgement alone means success                                                                        |
| `apply_sample_connection` and `apply_sample_rollback` | The completion classification: an acknowledged rollback, an unknown commit and a serialization failure at commit                                                                                                   |

Facts are inserted with `OVERRIDING SYSTEM VALUE` and `ON CONFLICT (id) DO NOTHING RETURNING id`, so a reserved identifier another row holds is never overwritten. Each batch travels as one bound JSON parameter, and distances are PostGIS geography distances in metres. The module writes no update, delete or DDL. The transaction and insert cases use connection substitutes; the critical tests seed an invented network as the local schema owner and run the real provider as the service account.

## Relation to DATA_ALGORITHM.md

`DATA_ALGORITHM.md` describes the order of reading, writing and verification these files follow.
