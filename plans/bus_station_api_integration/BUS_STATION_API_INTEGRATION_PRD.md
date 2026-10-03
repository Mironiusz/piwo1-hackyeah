# PRD: Imported MSIP bus and tram stops

Document state: 2026-10-03

## Business goal

Provide publicly readable bus and tram stop information for Kraków without making frontend reads depend on the availability of MSIP. Keep a periodically refreshed local copy so the application can continue serving the last successfully obtained data during source outages.

## Problem and its consequences

Calling MSIP for each frontend request makes source outages affect every reader and repeats external requests for the same information. A periodic import separates source availability from reading the application data. Before the first successful import, the application must distinguish unavailable data from a valid empty result.

## Scope

Import bus and tram stops from MSIP dataset 1490 within the administrative boundary of Kraków and make the imported information publicly readable through the backend. Include stop identity, name, location, bus/tram type, lines, source attribution and equipment when the source provides it. Refresh daily at a fixed local time, obtain the initial copy promptly and recover from failed or missed imports.

## Out of scope

- Importing the transport network dataset 2961, excluded by the user after revising the seed.
- Pedestrian network analysis, route calculation, isochrones and external calculation engines, excluded by the user's import-only decision.
- Calling MSIP during frontend reads.
- Linking or merging imported stops with user reports, votes or OpenStreetMap objects.
- Exposing the last-successful-import date to the frontend.
- Frontend interface implementation: this initiative provides data for the frontend to consume.

## Functional requirements

FR-1. Import bus and tram stops from MSIP dataset 1490 whose locations are within the administrative boundary of Kraków. A bounding rectangle is not a substitute for that boundary.

FR-2. Make the stop name, identifier, location, bus/tram type, lines, source attribution and source-provided equipment available to consumers. Equipment such as shelters and benches is included only when actually supplied by the source. Missing attributes must not be inferred.

FR-3. Serve stop data exclusively from the application's stored copy. Reading data does not contact MSIP or trigger an import, and requires no login.

FR-4. Refresh daily at 03:00 in Europe/Warsaw, following local time across daylight saving changes. A successful retry does not move the next regular refresh to 24 hours after that retry.

FR-5. When the application starts without a successfully imported dataset, begin the initial import immediately without waiting for a consumer request or the daily schedule.

FR-6. For the MVP, retry a failed initial import every 5 minutes until an import succeeds. Until then, return an explicit data-unavailable result. Distinguish this state from a successfully imported dataset containing no matching stops.

FR-7. A failed refresh leaves the previous dataset available and unchanged. Retain the last-successful-import date internally without returning it to the frontend.

FR-8. After a failed refresh while previous data exists, retry approximately once an hour until a refresh succeeds. Stop hourly retries after success and retain the regular 03:00 schedule.

FR-9. If downtime prevents the scheduled daily refresh, start the overdue import immediately when the application starts again. Continue serving existing data during this import; a failed attempt follows FR-8.

FR-10. Keep imported stops as a separate MSIP dataset. A complete successful import updates changed stops and removes stops the source no longer contains, without affecting user reports or votes. A failed import must not leave a partially replaced dataset available.

## Acceptance criteria

AC-1. Given source stops inside and outside the administrative boundary of Kraków, the imported dataset contains only the stops inside the agreed boundary (FR-1).

AC-2. Consumers receive the agreed stop information and MSIP attribution, including equipment only when provided by the source. Unknown equipment is not reported as absent or as proof of accessibility (FR-2).

AC-3. A reader without an account can obtain imported stops. Repeated reads make zero requests to MSIP and initiate zero imports (FR-3).

AC-4. Regular refreshes are scheduled for 03:00 Europe/Warsaw across winter and summer time. A retry succeeding at 06:00 does not change the next regular refresh from 03:00 to 06:00 (FR-4, FR-8).

AC-5. Starting without an imported dataset initiates an import without any frontend request. Failed initial attempts are retried every 5 minutes; reads return data unavailable until success (FR-5, FR-6).

AC-6. A successfully imported empty dataset produces a valid empty result, distinct from the unavailable result before the first successful import (FR-6).

AC-7. With previous data available, a failed daily refresh leaves that data unchanged and triggers approximately hourly retries. A successful retry makes the new dataset available and ends those retries (FR-7, FR-8).

AC-8. If the application is stopped from 02:00 until 04:00, it initiates the missed 03:00 import on startup at 04:00. Existing data remains readable; an unsuccessful catch-up attempt uses hourly retries (FR-9).

AC-9. A complete successful import updates a changed stop and removes a stop no longer present in the source. A failed or incomplete import preserves the previous dataset. User reports and votes remain unchanged (FR-10).

AC-10. Stop responses contain no last-successful-import date. The backend retains that information for import management, and a failed attempt does not advance it (FR-7).

## Domain rules

MSIP is the source of the imported stop dataset. Its records do not establish a stop's accessibility. Missing or unverified attributes remain unknown; neither a stop nor equipment is converted into an accessibility confirmation.

Imported stops remain separate from community reports and votes. Source removals change only the imported dataset. The administrative boundary of Kraków defines the geographic scope.

The import date is operational backend information. It is distinct from any source-provided date describing the underlying data and is not presented to frontend consumers.

## Dependencies and impact on other modules

The implementation depends on the project's backend, persistence and background-task architecture decisions. Their current state must be verified before the implementation plan is written; this PRD does not choose those solutions.

The frontend gains a public source of stored stop information, with an explicit unavailable state before the initial import succeeds. No frontend screen change is required in this initiative.

The existing community contribution and OpenStreetMap flows remain independent. Their refresh policies and voting rules are unaffected.

## Risks and notes

- The verified MSIP catalogue description confirms stop locations, but not shelter or bench attributes. Available attributes and their meaning must be checked before promising them in the consumer contract.
- The source's reuse terms must be checked before implementation, as required for open city data by the product specification.
- The source's identifiers, full-dataset retrieval and completeness signals require verification so incomplete retrieval cannot be mistaken for removed stops.
- Long source outages preserve availability of older data. By the user's decision, frontend consumers do not receive the import date.
- The 5-minute initial retry policy is accepted for the MVP and does not decide the policy of a later production service.
- Technical verification may reveal unavailable required source information or architectural prerequisites. Resolve such findings explicitly before implementation rather than inventing missing data or contracts.
