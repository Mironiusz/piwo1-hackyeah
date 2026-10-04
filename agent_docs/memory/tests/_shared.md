## 2026-10-04 - Logs, temporary paths and committed critical data in tests (OSM_IMPORTER)

- What changed: the importer tests capture the application logger, write invented OpenStreetMap files under an ASCII base directory and run committed import scenarios on a freshly migrated local database.
- Why: `config.logging.fetch_logger` sets `propagate = False` on the application logger, so pytest's `caplog` on the root logger sees nothing; on Windows the osmium reader cannot open a path with a non-ASCII character, and pytest's default temporary directory contains the user name; the service account may not delete `osm_copy` rows or facts, so committed test data cannot be cleaned up.
- Reusable pattern: attach `caplog.handler` to the logger `piwo1-hackyeah` in a fixture and restore its level afterwards (`tests/worker/test_osm_import_cases.py`); run osmium tests with `--basetemp` on an ASCII path; write committed critical scenarios as one ordered sequence with increasing source instants that refuses to start when a copy already exists (`tests/service/test_osm_import_critical.py`), and recreate the database of `db/compose.yaml` before each run. Shared invented sources live in `tests/common_osm_source.py`.
- Risk / notes: osmium's writer refuses an existing output file, so every invented source needs its own directory.

## 2026-10-04 - The ASCII base directory must also be short (public_transport_routing, S-9)

- What changed: the whole suite runs green on Windows with `--basetemp .cache/pt`, a short ASCII path inside the ignored `.cache/`.
- Why: a base directory in the scratch directory of an agent session is ASCII in its short form but expands to a long one, and the workspace of an import nests a run UUID and `work/transit_feeds/<feed>` under it, which passed the 260-character limit of Windows paths and made `tests/service/test_gtfs_import_integration.py` fail with `WinError 206`.
- Reusable pattern: `python -m pytest -m "not critical" --basetemp .cache/pt`; the osmium tests need ASCII and the import workspace tests need a short path.
- Risk / notes: pytest empties the base directory at the start of a run, so never point it at a directory with anything else in it.

## 2026-10-04 - Rolled-back critical reads and a script run outside the layers (route_planning)

- What changed: `tests/data/conftest.py` gives `service_transaction`, a connection of the service account inside a transaction rolled back after the test, used by the critical tests of the route reads; `tests/service/test_routing_service_config_cases.py` loads `valhalla/start_routing_service.py` by its path.
- Why: the route reads need seeded rows of `osm_way`, `osm_node`, `fact` and `vote`, which the service account may insert but never delete; the start script runs in the routing image, not as a module of a layer.
- Reusable pattern: seed invented rows with identities far above real ones (`9100000001`) inside `service_transaction`, so the test sees them together with whatever the local database holds and leaves nothing behind. A script outside the layers is loaded with `importlib.util.spec_from_file_location`, and its process replacement and image tools are replaced on the loaded module.
- Risk / notes: a committed scenario, as the importer runs, leaves rows in the local database for good; the end-to-end check of the route committed an invented copy into the local database of the Compose project `route-planning-db`, which therefore has to be recreated before the critical import scenario can run on it.
