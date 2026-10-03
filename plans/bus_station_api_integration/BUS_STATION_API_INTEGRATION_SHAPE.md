# Shape: Periodic MSIP import and database-backed reads

Document state: 2026-10-03, interview closed
Regulator: C:40

This shape follows the user-edited `SEED.md` read on 2026-10-03. It replaces the earlier request-time proxy scope. The seed is left unchanged.

## Problem

The frontend needs data from MSIP without contacting MSIP during a frontend request. The backend periodically obtains the source data and stores it in the application's database; frontend requests read only that database.

## Recipient and trigger

The frontend consumes the stored data through the backend. Regular refreshes run daily at 03:00 in Europe/Warsaw, following the user's choice of a fixed nighttime refresh on 2026-10-03. On the same date the user confirmed that application startup automatically triggers the initial import when no successfully imported dataset exists, without waiting for frontend requests or the regular refresh schedule.

## Current state

No backend implementation was found in the working tree during the preceding investigation. Backend architecture and schema decisions are still tracked by `plans/mvp/` and `plans/fact_schema/`; their current implementation state must be rechecked before a technical plan.

The user names MSIP dataset 1490 for bus and tram stops and their equipment, and dataset 2961 or an OpenStreetMap-based engine for pedestrian network analysis and isochrones.

The official catalogue at https://msip.krakow.pl/dataset/1490 describes bus and tram stop locations and EPSG:2178, and refers reuse to the MSIP terms. Its description does not confirm shelter or bench attributes. Neither dataset 2961 nor its service contract has been verified yet.

`docs/product/specification.md`, O4, permits useful open city datasets after checking their reuse terms. M2 requires route inputs and preferences to stay within project infrastructure. Isochrones are not specified as an existing product feature.

## Smallest meaningful scope

Periodically import bus and tram stops from MSIP dataset 1490 within the administrative boundary of Kraków into the application database and expose stored data to the frontend through the backend. On 2026-10-03 the user confirmed that this initiative imports data only, performs no calculations, includes stops only and restricts their location to the administrative boundary of Kraków.

## Out of scope

Request-time calls to MSIP are excluded by the revised seed. Pedestrian network analysis, isochrone calculation and integration with an external calculation engine are excluded by the user's answer of 2026-10-03. The user subsequently excluded importing the transport network dataset 2961 and retained only the stop dataset 1490. Network analysis and calculation requirements from the seed therefore have no implementation deliverable in this initiative, by the user's explicit scope decision.

## Functional requirements

1. Obtain bus and tram stop data from MSIP dataset 1490, retaining only stops within the administrative boundary of Kraków, as confirmed by the user on 2026-10-03.
2. Include stop geometry and equipment such as shelters and benches when the source actually provides those attributes; source availability must be checked, never assumed.
3. Refresh source data daily at 03:00 in Europe/Warsaw, rather than every 24 hours after the previous import. The user requested a fixed daily time and gave 03:00 as the example on 2026-10-03. Agent decision at C:40, without asking: Europe/Warsaw follows the local time of Kraków. Implementation must respect daylight saving changes rather than use a fixed UTC offset.
4. Store imported data in the application's database.
5. Answer frontend reads exclusively from the application's database, without triggering upstream requests.
6. If a refresh fails, retain the previously imported data and continue serving it. Keep the last-successful-import date as backend-only metadata; do not expose it to the frontend. The user's later clarification on 2026-10-03 supersedes the earlier agreement to include this date in frontend responses.
7. Before the first successful import, return an explicit data-unavailable result rather than treating the absence of an import as an empty source dataset. The user accepted this on 2026-10-03 and additionally required missing data to be fetched as soon as possible, without waiting for the next regular refresh.
8. Automatically trigger the initial import at application startup when no successfully imported dataset exists, independently of frontend requests and the regular refresh schedule, as confirmed by the user on 2026-10-03. A successfully imported empty dataset is distinct from an import that has never succeeded.
9. For the MVP, if the initial import fails, retry every 5 minutes until an import succeeds. While no successful import exists, frontend reads return the data-unavailable result. The user accepted this MVP behavior on 2026-10-03; it does not establish the policy for a later production service.
10. If the daily refresh fails while a successfully imported dataset exists, retry approximately once an hour until a refresh succeeds. Continue serving the previous data and retain its last-successful-import date internally, without returning the date to the frontend. The user chose hourly retries on 2026-10-03; the 5-minute retry policy remains limited to the initial import without an existing dataset. A successful retry does not shift the regular daily 03:00 schedule.
11. If application downtime prevents the scheduled 03:00 refresh, trigger the overdue import immediately on application startup, even when previous data exists. The user confirmed this on 2026-10-03. If this refresh fails while previous data exists, apply the hourly retry policy; the regular daily schedule remains unchanged.
12. Reading imported stop data through the backend is public and requires no login, as confirmed by the user on 2026-10-03. This decision applies to reading the data, not to exposing an administrative import trigger.
13. Keep imported stops as a separate MSIP dataset, without linking or merging them with user reports or votes. Each successful import updates the dataset to reflect the source, including removing stops the source no longer contains. The user confirmed this on 2026-10-03. A failed import retains the previous dataset under requirement 6.
14. Expose the stop name, identifier, location, bus/tram type, lines, source attribution and equipment when provided by MSIP, as confirmed by the user on 2026-10-03. Do not expose the last-successful-import date. Verify source availability and field semantics before defining the technical contract; do not infer missing equipment or accessibility information.

## Scenarios: input, flow, expected state after the run

1. A periodic run fetches source data and stores it. A later frontend request reads the stored data without contacting MSIP.
2. Day 1: an import succeeds and stores data. Day 2: MSIP is unavailable during a refresh. The previously imported data remains unchanged. A subsequent frontend request returns that data without contacting MSIP or including the import date. Backend metadata still records day 1 as the last successful import. This reflects the user's later clarification on 2026-10-03 that import dates stay internal.
3. The application starts without a successfully imported stop dataset and automatically triggers the initial import without waiting for a frontend request or the regular refresh schedule. If the import fails, the MVP retries every 5 minutes until an import succeeds. Until then, the backend reports that stop data is not yet available. Once it succeeds, frontend reads return the stored data. The user confirmed startup behavior and the MVP retry policy on 2026-10-03.
4. A later successful import changes a stop and no longer contains another stop. The separate MSIP dataset reflects the updated stop and removes the missing one. User reports and votes are not linked to these imported stops and remain unchanged. If the import fails, the previous MSIP dataset remains unchanged.
5. At 03:00 a daily refresh fails while previous data exists. Approximately one hour later the application retries; after another failure it retries again approximately one hour later. Frontend reads continue returning the previous data without the import date; backend metadata retains the original last-successful-import date. Once a retry succeeds, the new data becomes available and hourly retries stop. The next regular refresh remains scheduled for 03:00 Europe/Warsaw.
6. At 02:00 the application stops while previous data exists. At 03:00 it is still stopped, so the daily refresh does not run. At 04:00 the application starts and immediately triggers the overdue import. Frontend reads use the previous data until the import succeeds; a failed catch-up refresh follows the hourly retry policy.

## Challenging own assumptions

- Is this still a proxy integration? No. The revised seed explicitly requests periodic persistence and database-only reads.
- Does the catalogue establish bench and shelter availability? No. The verified description establishes stop locations only; service fields need investigation.
- Does mentioning an isochrone API authorize sending user locations outside the project? No. That would conflict with the current M2 rule when derived from route inputs.
- Does a daily MSIP import change the agreed manual OpenStreetMap refresh? No such change was requested. The two sources must be distinguished.
- Does importing network data require implementing isochrones? No. On 2026-10-03 the user explicitly restricted this initiative to importing data without calculations, then restricted the imported data to stops only. Neither network import nor isochrone calculation remains in scope.

## Domain rules or explicit TODO

The geographic filter follows the administrative boundary of Kraków, not a bounding rectangle. The boundary source and geometric handling are to be verified and specified in the technical plan; this shape does not choose a new boundary contract.

Missing or unverified source attributes do not establish accessibility (`docs/product/specification.md`, M10). Imported stops form a separate MSIP dataset and are not linked or merged with user reports or votes, as confirmed by the user on 2026-10-03. No merging with OpenStreetMap objects is specified. The product specification remains authoritative for route-data privacy.

## Notes on data, performance and security

The upstream schema, reuse terms, dataset sizes and available equipment fields require verification. No migration or endpoint contract is defined yet. Source reconciliation reflects the complete successful import in a separate MSIP dataset, with the source identity and implementation to be verified in the technical plan. The daily schedule is 03:00 Europe/Warsaw, with an immediate catch-up import on startup after a missed run. The frontend read path must remain independent of upstream availability, as explicitly requested in the seed.

## Open questions

None. The user confirmed the proposed frontend information on 2026-10-03, with the import date excluded.

Source-service verification and reuse-term checks are research tasks, not questions to substitute for that research. Technical schema, scheduler and endpoint decisions belong to the subsequent implementation plan.
