# OpenStreetMap importer

Document state: 2026-10-04

## What the import does

One manual run makes a complete OpenStreetMap copy of Kraków current, or leaves the previous copy as it was. It does the following:

1. Downloads the latest dated Geofabrik extract of Małopolska and validates its redirect, MD5 and source instant.
2. Selects the pedestrian network of M2 within administrative relation 449696.
3. Derives the present barrier and amenity facts of M6.
4. Builds the matching Valhalla walking data.
5. Publishes the network, the facts and the copy date in one database transaction, then points the routing data at the new copy.

Votes, independent user reports and moderation decisions are never changed. Nothing schedules the import and no app request starts it.

## Prerequisites

- The database of `db/` with its revision chain applied. Locally this is `db/compose.yaml` (`db/README.md`, section Local database); the hosted demo is wired by `plans/deployment_config/`.
- A Python 3.13 environment with `python -m pip install ./db` followed by `python -m pip install .`.
- The Valhalla 3.9.0 tools `valhalla_build_tiles` and `valhalla_build_extract`. They exist in the image of `valhalla/Dockerfile`, on which `plans/deployment_config/` builds the backend image the import runs in. There are no native Windows builds, so on Windows every step except the tile build can run, but a complete import cannot.
- A Valhalla configuration template produced by `valhalla_build_config` of the same image. The import overrides `mjolnir.tile_dir`, `mjolnir.tile_extract`, `include_platforms`, `keep_osm_node_ids` and `keep_all_osm_node_ids`, and removes the transit inputs.
- The shared libraries of osmium in the image, including `libexpat.so.1`, which `python:3.13-slim` lacks.

The configuration needs the backend entries of `docs/standards/standard_config.md` and four paths, all absolute:

| Entry                      | Meaning                                                                                                                             |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `IMPORT_WORKSPACE_ROOT`    | One persistent workspace per database on a local filesystem; the import exclusion and crash recovery keep their private files there |
| `ROUTING_DATA_DIR`         | The directory the routing service reads: `copies/<name>/` of every copy and the pointer `current`                                   |
| `VALHALLA_TOOL_DIR`        | The directory holding the Valhalla build tools                                                                                      |
| `VALHALLA_CONFIG_TEMPLATE` | The Valhalla JSON configuration described above                                                                                     |

On Windows the workspace and routing paths must contain only ASCII characters, because the osmium reader cannot open a path with another character.

## Running the first import and a refresh

From the repository root, with `DB_HOST` and `DB_PORT` given at launch:

```bash
python -m worker.osm_import
```

The same command performs the first import and every later refresh. In the hosted demo it runs as a one-off container of the backend image; the exact container command belongs to `plans/deployment_config/`. Any run against the hosted demo needs an explicit human decision. The whole run has a 60-minute deadline, and the final database transaction has at most 120 seconds of it. A missing or invalid configuration entry ends the run with exit code 1 and names the entry and its file.

## Outcomes

The run ends with one log line `OSM import outcome=<outcome>` carrying the source instant, the duration and the counts of nodes, ways, memberships and facts written.

| Outcome              | Exit code | Meaning                                                                                                                            | What is current afterwards                                                                                                         |
| -------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `updated`            | 0         | A new copy was committed and the pointer names it                                                                                  | The new copy; restart the routing service so that it loads it                                                                      |
| `unchanged`          | 0         | The source instant equals the copy in use                                                                                          | The previous copy, untouched                                                                                                       |
| `skipped`            | 2         | Another import, or the unfinished work of an interrupted one, holds the import exclusion                                           | Whatever was current; run again later                                                                                              |
| `routing_incomplete` | 1         | The database copy was committed, but the pointer could not be written                                                              | The new database copy; the routing service still serves the old data and refuses routes until the next run republishes the pointer |
| `commit_unknown`     | 1         | The commit confirmation was lost and could not be settled                                                                          | Unknown; the pointer is unchanged, and the next run settles it                                                                     |
| `failed`             | 1         | A named failure, such as source validation, an older source instant, reading, geometry, tools, routing files, deadline or rollback | The previous copy and pointer, untouched                                                                                           |

A failure before the commit never leaves a partial copy: on a first import there is no copy, and on a refresh the previous network, facts, votes and copy date stay as they were.

## Recovery on the next run

Each run first removes leftover preparation directories of interrupted runs. It then compares the pointer with the latest committed copy:

- a missing pointer, or one naming an older copy, is republished after that copy's manifest verifies its files and source instant;
- missing or damaged files of the committed copy stop the run as an integrity failure, leaving the database and the pointer unchanged and downloading nothing;
- a pointer naming a newer copy than the database stops the run in the same way.

Rebuilding the files of a committed copy is not automated; it needs a human decision.

## Checking the copy in use

The copy in use is the latest row of `osm_copy`:

```sql
SELECT state_at, state_at_utc_offset_minutes, file_name, made_current_at
FROM osm_copy
ORDER BY state_at DESC
LIMIT 1;
```

Three dates must not be confused:

- `state_at` is the source instant, and its calendar day in Europe/Warsaw is the copy date the app shows;
- `file_name` carries the extract's dated name;
- `made_current_at` is when the copy was published, not how fresh the data is.

The pointer `ROUTING_DATA_DIR/current` names the selected routing data, the source instant in whole seconds since the epoch. `copies/<name>/manifest.json` records that instant with the size and SHA-256 hash of `network.osm.pbf`, `valhalla_tiles.tar` and `krakow_boundary.wkb`, the boundary of Kraków as WKB in longitude and latitude that the route reads to refuse a point outside Kraków. The copy the routing service actually loaded is checked by the routing consumer, which refuses routes while it differs from the copy in use. The import never restarts the routing service.

## Disappearing and returning facts

When a refresh no longer holds an OpenStreetMap fact, the publication decides it by M4 with the shared vote evaluator, `resolve_fact_status` of `service/fact_status.py` (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-52):

- confirmations greater than denials, both summed over the latest votes of five persons, make it a user report that keeps all its votes;
- no votes, only denials or a tie leave it an OpenStreetMap fact marked as removed, which disappears from the map and the routes and keeps its votes.

While the publication decides, the fact and its votes are locked, so a vote on that fact waits until the commit or the rollback. A converted or removed fact that stays absent is not decided again. When a later copy holds the same fact type on the same element again, the fact returns as an OpenStreetMap fact with all its votes.

## Source, freshness and attribution

OpenStreetMap contributors provide the data, under the [Open Database License](https://www.openstreetmap.org/copyright); the app keeps the visible OpenStreetMap attribution the specification requires. The extract comes from Geofabrik over HTTPS, and only its dated redirect, published MD5 and header instant are trusted. Freshness is the header instant, never the download time. Accessibility tags can be incomplete, inconsistent or outdated, and missing or contradictory information never confirms accessibility.

## Verification

The quick checks need no database and no network:

```bash
python -m pytest -m "not critical" tests/service tests/data tests/worker tests/architecture/test_osm_import_boundaries.py
```

The critical checks need a freshly migrated local database of `db/compose.yaml` without any OpenStreetMap copy. Publication commits, and the service account may not delete copies, so recreate the database with `down` and `up` and apply the chain before each run. Run them with `APP_ENVIRONMENT=local`, the backend entries and the database entries pointing at that database:

```bash
python -m pytest -m critical tests/service/test_osm_import_critical.py
```

They run whole imports of invented sources with a stand-in for the Valhalla tools, including the conversion, the removal and the return of disappearing facts with their votes and the locks held while they are decided. A real tile build was verified separately in a temporary Linux container built from the Valhalla 3.9.0 image. No real extract or slice of one enters the repository.

## Known limits

- The boundary and network passes keep every way and every node of the whole Małopolska extract in memory, so peak memory grows with the extract, not with Kraków. A real run has not been measured yet; measure one before the demo depends on it.
- A non-area relation of the copy whose tags make an amenity present, or an area without a usable interior point, fails the whole import rather than guessing a location.
