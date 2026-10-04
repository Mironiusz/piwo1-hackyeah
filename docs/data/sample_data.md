# Demonstration samples

Document state: 2026-10-04, provider implemented for the eight facts of the demo scenario; critical storage tests pass locally, joint acceptance remains

The sample provider prepares the eight facts S-1 - S-8 of the demo scenario of `stage7_demo_scenario` near Tauron Arena Kraków. Their content - type, steps, radius and the Polish description - is that of the bundled HarmonyOS demonstration, `demoReports` of `mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets`. Their places lie on real ways of public OpenStreetMap data around the proxy route from the Tauron Arena to M1 Kraków, al. Pokoju 67. Every fact is a user report with `is_sample=true`; the content is fictional, whatever the real geometry.

## Fixed dataset

Points are given as latitude and longitude. Times are minutes before the first successful loading.

| Identifier | Content                                                                      | Point                    | Reference way | Created | Sample votes                        | Moderation              |
| ---------- | ---------------------------------------------------------------------------- | ------------------------ | ------------- | ------- | ----------------------------------- | ----------------------- |
| -1         | High kerb                                                                    | 50.0676150, 19.9888900   | 1222443126    | 288     | confirm 288, 288, 144, 144          | none                    |
| -2         | Stairs, 4 steps, `Brak poręczy po prawej stronie.`                           | 50.0663721, 19.99663575  | 926589685     | 1440    | confirm 1440, 1440                  | none                    |
| -3         | Ramp                                                                         | 50.0668, 19.99536        | 28837534      | 2880    | confirm 2880, 2880, 2160, 2160      | none                    |
| -4         | Poor surface, geozone of 25 m, `Remont chodnika, rozkopana nawierzchnia.`    | 50.06645, 19.99455       | 360935725     | 2880    | confirm 2880, 2880; deny 1440, 1440 | none                    |
| -5         | High kerb, contradicted by the lowered kerb of node 317034340                | 50.06574634, 19.99708082 | 252778084     | 432     | confirm 432, 432, 432               | none                    |
| -6         | Stairs, 3 steps, a placeholder about a neighbour and his car                 | 50.06763615, 19.9893127  | 306727457     | 144     | confirm 144, 144                    | flagged 144             |
| -7         | Narrow passage, geozone of 50 m, `Rusztowanie na całej szerokości chodnika.` | 50.07595, 20.00285       | 83093546      | 1440    | confirm 1440, 1440; deny 720, 720   | flagged 720             |
| -8         | High kerb, a placeholder with a phone number                                 | 50.06754, 19.98907       | 1222443122    | 2880    | confirm 2880, 2880                  | flagged and hidden 2880 |

The placeholders of S-6 and S-8 imitate content a moderator would hide and contain no real personal data. The exact Polish texts are in `service/sample_data.py`, `SAMPLE_DEFINITIONS`.

The identifiers -1 - -8 are reserved for sample data, as `docs/product/schema.md`, section Facts, records. Ordinary generated identifiers and sequences are not changed. Samples have no report-save key or OpenStreetMap identity, as the current schema requires. The places, their measurements and the replacement destination are in `plans/sample_data/SAMPLE_DATA_OSM_EVIDENCE.md`.

## Votes, statuses and dates

Every sample vote is a vote without an account, of weight 0.5, with its own fictional voter: each vote of weight 1 of the bundled demonstration became two such votes, and S-5 has three. The voter identity of the n-th vote of a fact is SHA-256 of `sample-data:voter:v2:` followed by the fact identifier and n in decimal, joined by `:`, in UTF-8. It contains no real account, IP address or browser input. Before anyone votes, the statuses derived under M4 are S-1 and S-3 confirmed, S-4 and S-7 disputed and the others unverified; S-5 stands at a confirmation weight of 1.5, so one presenter's confirmation without an account brings it to 2.

The loading instant is the business-zone clock truncated to whole seconds. Every creation, vote, flag and hiding lies its fixed number of minutes before it, computed in UTC and stored with the Europe/Warsaw offset in force at its own instant, so a date two days back can keep summer time when the loading happens in winter. Loading writes votes and the flag and hide pairs, never a status.

## Loading and retry

The common loader owned by `osm_import` calls `service.sample_data.apply_sample_data()` as its third effect, after OpenStreetMap and tiles, through `python -m worker.load_demo`. The common command and its adapter are delivery dependencies; this provider creates no replacement command. Its exact result and failure contract is `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`.

One Repeatable Read transaction checks the current network, reconciles the samples and inserts the missing ones. Existing content and sample vote history must match; changed definitions or occupied unrelated identifiers fail without overwrite. A retry dates the expected votes of an existing fact from its stored creation, so it needs no record of the first loading instant. Community votes, flags and hiding are preserved and never compared or reset. A manually triggered full-flow retry repeats validation using the same identifiers.

## Prerequisites and failure

Install the pinned `accessibility-db` package from `./db` together with the root development dependencies. Prepare the database using the separate commands in `db/README.md`; the provider performs no migration or network download. Runtime uses the shared `data.engine.build_engine`, `common_time.fetch_business_now` and `config.logging.fetch_logger`.

The provider checks that a copy exists and every reference way exists, that each point fact's reference way is its unique nearest way within 15 m, and that each geozone's reference way lies within its radius. For S-5 it builds the route graph of the current copy and applies route planning's own rule: a lowered kerb point on the stretch S-5 lies on, within 5 m. The graph build uses the 60 s statement limit of a build; other statements use the shared 5000 ms limit. The provider refuses a missing copy (`copy_missing`), an invalid place (`site_invalid`), a missing kerb contradiction (`contradiction_missing`), an identity collision, changed content or invalid sample vote history. `database_failed` reports storage failure; `commit_unknown` preserves uncertainty after a lost commit acknowledgement. A disconnected connection or attempted rollback alone is not proof of completed rollback.

The provider returns success only after acknowledged commit. It does not retry automatically, refresh source data, move sample points or erase preceding common-loader effects. Runtime service permissions require no deletion or DDL.

## Verification and remaining acceptance

Run the independent cases with `python -m pytest tests/service/test_sample_data_cases.py tests/service/test_sample_data_integration.py tests/data/test_sample_data_transaction_cases.py tests/data/test_sample_data_insert_cases.py tests/data/test_sample_fixture_cleanup_cases.py`. They replace only the layer's immediate dependencies and do not establish real-database behavior.

The critical tests in `tests/data/test_sample_data_critical.py` run the real provider with the restricted service account against a local database of `db/compose.yaml` with the first revision applied, and need `--scratch-database-url` with the local schema-owner address. They seed an invented network of the eight reference ways and the lowered kerb, and cover the first loading, repetitions, preserved contributions, missing prerequisites, a kerb that is not lowered or too far, wrong places, collisions, a failure between the batches and concurrent invocations.

Final acceptance also checks the imported copy and the actual demo route, negative identifiers through the fact operations, sample marks in the clients and the common program's adapter. Current evidence and open items are recorded in `plans/sample_data/SAMPLE_DATA_REVIEW.md`.
