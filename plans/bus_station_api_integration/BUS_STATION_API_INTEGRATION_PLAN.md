# Plan: Imported MSIP bus and tram stops

Document state: 2026-10-03, plan in progress

The user approved the PRD on 2026-10-03. This draft records verified prerequisites; it is not ready for implementation.

## Goal

Implement the approved PRD's periodic import of Kraków stops and public database-only reads, including startup recovery and the agreed retry schedules.

## Facts

F-1. The PRD is approved and excludes calculations, network import, user-vote integration and frontend exposure of the import date. | doc:`plans/bus_station_api_integration/BUS_STATION_API_INTEGRATION_PRD.md` sections Out of scope and Functional requirements; cmd:`user message on 2026-10-03: looks good` | 2026-10-03
F-2. The current working tree has no backend application, persistence layer or migration code. | cmd:`rg --files -g '*.py'` -> Python code only in repository architecture tests, with no product implementation | 2026-10-03
F-3. Backend architecture and worker decisions remain an open question of the MVP plan. | doc:`plans/mvp/MVP_PLAN.md:63` | 2026-10-03
F-4. The MSIP dataset 1490 catalogue's online-data link resolves to the bus-stop ArcGIS layer 0, rather than a verified WFS endpoint covering both stop types. | cmd:`web open https://msip.krakow.pl/dataset/1490 and click online-data link` -> https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0, named Przystanki autobusowe | 2026-10-03
F-5. The verified bus layer exposes objectid, stop_id, stop_name, stop_lat, stop_lon, shape, aktualnosc and linie; it exposes no bench or shelter fields. | cmd:`web read https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0` -> Fields lists the eight named fields | 2026-10-03
F-6. The verified bus layer limits responses to 2000 records and supports pagination. | cmd:`web read https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0` -> MaxRecordCount 2000 and Supports Pagination true | 2026-10-03

## Decisions

D-1. Preserve the approved PRD as the implementation contract. Do not silently reduce bus-and-tram coverage to the verified bus layer.

D-2. Do not create a parallel backend skeleton while the existing project's architecture remains undecided. Resolve the integration dependency before assigning implementation files, entry points or shared configuration contracts. Agent decision at C:40, without asking: the current PRD depends on project architecture and does not authorize replacing it.

## Scope of changes

Not yet specified. Concrete code files, function names, storage objects and endpoint contracts depend on the backend architecture and must be verified before this section is completed.

The affected responsibilities are the upstream adapter, geographic filtering, complete-dataset reconciliation, storage, import status, scheduling and startup catch-up, public reads, configuration, logging, documentation and their relevant verification gates. Existing reports and votes must not be affected.

## Rollout order

1. Resolve whether the backend prerequisites will be supplied by the existing MVP work or require a separately agreed change in scope.
2. Verify the bus and tram services, source identifiers, completeness signals, available attributes, reuse terms and administrative-boundary source.
3. Verify shared backend contracts and schema, then specify concrete changes and checks before closing this plan.
4. Implement and validate only from the completed plan.

## Definition of Done

All PRD acceptance criteria AC-1 through AC-10 are demonstrated by relevant runs. Repository standards and review gates pass. The implementation plan has verified concrete contracts and no unresolved questions before implementation starts.

## Risks

- Building the backend skeleton here would extend the approved integration scope and overlap the MVP architecture work.
- The catalogue link alone does not establish complete bus and tram coverage or equipment availability.
- Partial retrieval must not be treated as a complete source snapshot that deletes missing records.
- A source outage must preserve the previously imported dataset.
- Repository formatting tooling is currently unavailable because `npx` is not installed.

## Open questions

1. Should this integration wait for the project's backend architecture and skeleton, or should the user explicitly authorize a separate prerequisite scope to provide them?

Source verification tasks remain in the rollout order and are not replaced by user guesses.

## Supplementary files

- `SEED.md`: the user-edited request, left unchanged.
- `BUS_STATION_API_INTEGRATION_SHAPE.md`: confirmed scope and behavior.
- `BUS_STATION_API_INTEGRATION_PRD.md`: approved product requirements and acceptance criteria.
- `../mvp/MVP_PLAN.md`: pending backend architecture decision Q-11.
