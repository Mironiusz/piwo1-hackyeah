# Demonstration samples

Document state: 2026-10-04, provider code implemented; critical storage and joint acceptance remain incomplete

The sample provider prepares four fictional user reports near Tauron Arena Kraków. Public OSM geometry supplies locations, while the reported barriers and amenity are invented. Each description begins with `Sample data:` and each fact has `is_sample=true`.

## Fixed dataset

| Identifier | Content                                         | Latitude    | Longitude   | Reference way |
| ---------- | ----------------------------------------------- | ----------- | ----------- | ------------- |
| -1         | Poor surface contradicting explicit OSM absence | 50.06741305 | 19.9947175  | 926589691     |
| -2         | Stairs with three fictional steps               | 50.0677843  | 19.9934245  | 360933256     |
| -3         | Fictional rest place                            | 50.06737    | 19.99468    | 926589691     |
| -4         | Poor-surface geozone with a 25 m radius         | 50.0681175  | 19.99363775 | 28837556      |

These identifiers are reserved. Ordinary generated identifiers and sequences are not changed. Samples have no report-save key or OSM identity, as the current schema requires. Site evidence and limitations are in `plans/sample_data/SAMPLE_DATA_OSM_EVIDENCE.md`.

## Loading and retry

The common loader owned by `osm_import` calls `service.sample_data.apply_sample_data()` as its third effect, after OSM and tiles, through `python -m worker.load_demo`. The common command and its adapter are delivery dependencies; this provider creates no replacement command. Its exact result and failure contract is `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`.

One Repeatable Read transaction checks the current network and reconciles the samples. Existing content and author history must match; changed definitions or occupied unrelated identifiers fail without overwrite. Community votes, flags and hiding are preserved. A manually triggered full-flow retry repeats validation using the same identifiers.

Every new sample receives one entirely fictional confirmation without an account and starts unverified with confirmation weight 0.5. The author identity is SHA-256 of `sample-data:initial-author:v1:` plus the negative decimal identifier, encoded as UTF-8. It contains no real account, IP address or browser input. Its vote instant and offset equal the sample's creation pair. Repeat loading neither refreshes that history nor adds another daily confirmation.

## Prerequisites and failure

Install the pinned `accessibility-db` package from `./db` together with the root development dependencies. Prepare the database using the separate commands in `db/README.md`; the provider performs no migration or network download. Runtime requires the delivered `data.engine.build_engine`, `common_time.fetch_business_now` and `config.logging.fetch_logger`. Their backend delivery remains outstanding.

The shared engine supplies 5000 ms statement limits and bounded connection/pool waits. The provider refuses missing copy, invalid sites, lost explicit absence, identity collision, changed content or invalid initial history. `database_failed` reports storage failure; `commit_unknown` preserves uncertainty after a lost commit acknowledgement. A disconnected connection or attempted rollback alone is not proof of completed rollback.

The provider returns success only after acknowledged commit. It does not retry automatically, refresh source data, move sample points or erase preceding common-loader effects. Runtime service permissions require no deletion or DDL.

## Verification and remaining acceptance

Run the independent cases with `python -m pytest tests/service/test_sample_data_cases.py tests/service/test_sample_data_integration.py tests/data/test_sample_data_transaction_cases.py`. They replace only the layer's immediate dependencies and do not establish real-database behavior.

Critical tests need the shared local configuration guard, restricted runtime engine, owner engine and exact cleanup registry. Those backend contracts must be delivered before durable fixture writes. Real PostGIS queries, concurrent attempts, preserved moderation and votes, a failed write between batches and actual source-copy/site checks remain mandatory. Final acceptance also checks the actual demo route, negative identifiers through fact operations, sample marks in the clients and the common program's adapter. Current evidence and blockers are recorded in `plans/sample_data/SAMPLE_DATA_REVIEW.md`.
