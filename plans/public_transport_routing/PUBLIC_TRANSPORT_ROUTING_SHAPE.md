# Shape: Routes with public transport, the optional feature O9

Document state: 2026-10-04, interview in progress
Regulator: C:40

## Problem

Version 13 of `docs/product/specification.md` makes routes with the public transport of ZTP Kraków the optional feature O9, built first and in parallel with the mandatory features, within a time box of 4.5 hours of work of the people of the team. `plans_finished/valhalla_routing/` decided how such a route is computed (`VALHALLA_ROUTING_PLAN.md` D-12) and handed the build to a separate initiative (D-13 there). `MVP.md`, section Initiatives, names this initiative for it. Nothing of O9 exists yet: the route operation of `docs/product/api_contract.md` knows only walking routes, no copy of the GTFS is fetched by anything, and no code of the backend exists.

The task prefix is `PUBLIC_TRANSPORT_ROUTING`, from the seed the user saved under the name of the initiative given in `MVP.md`.

## Recipient and trigger

- A person planning a route in Kraków who sets the switch of the route form to public transport. The request reaches the service through `plan_route` of `docs/product/api_contract.md` from the web frontend of `plans/frontend_app/`, and possibly from the HarmonyOS client of `plans/stage5_harmonyos_port/`.
- The frontend of `plans/frontend_app/`, which builds the switch, the public transport segment and the statement of O9 only once this initiative has written its interface into `docs/product/api_contract.md` (`MVP.md`, section Initiatives).
- A member of the team who fetches the copy of the GTFS before the demo and refreshes it by hand; nothing refreshes it on a schedule (specification, O9).

## Current state

State read on 2026-10-04 at 04:32, Europe/Warsaw.

- The specification, version 13, section O9, holds the rules of the feature: the switch with walking as the default, departure now in Europe/Warsaw, the walking legs under M2, M7 and M8, the public transport segment green when the GTFS gives no accessibility information, a stop or a trip marked not accessible never used for boarding or alighting, the walking route with a plain statement when public transport cannot be answered, the copy of the GTFS as a whole or not at all, and the time box. M7 and M10 carry the exception of O9.
- `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-12 is the input of this initiative: the routing data with public transport built by the tools of the image of D-1 from the network file of D-2 and the three feeds after the rewrite of F-14; the request with `costing` `multimodal`, the pedestrian options of D-4, the exclusions of D-5 and `transit.wheelchair` true; every walking leg through D-8 and D-9; the walking route of D-4 - D-10 when the multimodal request answers no route; a public transport leg drawn between its boarding and alighting stops. Only the fallback and the executor were decided by the user; the rest is an agent decision at C:40 of that plan.
- `VALHALLA_ROUTING_PRD.md` FR-5 - FR-9 and FR-11, with AC-8 - AC-11 and AC-13, are the requirements this initiative meets (`MVP.md`, section Requirements and initiatives, last row: `public_transport_routing`, `frontend_app`).
- `valhalla/` builds the image of the engine with the two patches that make the walking legs of a multimodal route honour exclusions and the accessibility of stops and trips (`valhalla/README.md`, section The patches).
- `docs/product/api_contract.md`, section Route, operation `plan_route`: the request carries `start`, `destination`, `avoid` and `need`, and a field it does not name is refused with `invalid_request`; the response has no kind of route, no public transport segment and no statement that public transport was unavailable. A change of an operation is a change of that document first, agreed by the backend person and the frontend person (its section Why this document exists).
- `plans/osm_importer/OSM_IMPORTER_PLAN.md` D-20 leaves public transport ingestion, the routing image, the service startup, the served-copy check and the fewest-barriers graph with the initiatives of Marek. `plans/osm_importer/OSM_IMPORTER_PRD.md` AC-12: public transport feeds are not produced by the import run.
- `docs/deployment/hosted_demo.md` does not mention the GTFS, and `MVP.md` names `map_tiles` and `sample_data`, not this initiative, as adding steps to the loading program of `osm_import`.
- No product code exists: the repository root holds no `api/`, `service/`, `data/` or `worker/`. `plans/route_planning/`, which builds the walking route D-12 reuses, and `plans/backend_skeleton/` hold only a seed and `STAGE.md`.
- `FINAL_CHECKLIST.md`, check 4.2: `public_transport_routing` is optional, waits for 4.1, 3.1 and 1.5, and does not condition the end of the project. `STAGE.md` of this initiative says stage 5.
- `docs/standards/decision_registry.md` holds two open entries whose condition falls on this shape: When the initiative of O9 starts its code, and Wording of the public transport segment of O9. Both name Rafał and Marek.
- The Kraków submission closes at 11:00 on 4 October 2026 (`MVP.md`, section Goal and deadline).

## Smallest meaningful scope

From the seed, before the interview:

1. The interface of a route with public transport written into `docs/product/api_contract.md` first.
2. A route with public transport as D-12 decides, for FR-5 - FR-9 of `VALHALLA_ROUTING_PRD.md`.
3. The time box of FR-11 of `VALHALLA_ROUTING_PRD.md`: 4.5 hours of work of the people of the team.
4. The registry entry When the initiative of O9 starts its code moves to Resolved decisions, and `MVP.md`, sections Initiatives, Order and critical path and Open decisions and confirmations, follows the parallel start of question 1, in the same change, as the condition of that entry asks.

## Out of scope

- The switch, the public transport segment and the statement in the views: `plans/frontend_app/` builds them once the interface is in the contract (`MVP.md`, section Initiatives).
- The walking route and everything D-12 reuses from D-1 - D-11 of `VALHALLA_ROUTING_PLAN.md`: `plans/route_planning/` (`MVP.md`, section Initiatives).
- The importer, the network file of D-2 and the walking data of the engine: `plans/osm_importer/` (`OSM_IMPORTER_PLAN.md` D-20).
- Real-time public transport data (specification, section Out of scope).

## Functional requirements

To be filled in during the interview.

## Scenarios: input, flow, expected state after the run

To be filled in during the interview.

## Challenging own assumptions

To be filled in during the interview.

## Domain rules or explicit TODO

- The code of this initiative starts at once, in parallel with `route_planning` and `osm_importer`, as the section Optional features of the specification says of O9. What does not need the code of `route_planning` goes first: the interface in the contract, the copy of the GTFS, the routing data with public transport and the multimodal request; the walking legs of D-8 and D-9 and the walking route of the fallback are joined to the code of `route_planning` once it exists, and the parts the two share are agreed by their owner, Marek. Decided by Rafał on 2026-10-04 in this interview, question 1, against waiting for `route_planning` and `osm_importer` as `plans_finished/mvp/MVP_PLAN.md` D-15 and D-20 record. The registry names Rafał and Marek, so Marek's ruling is still to be confirmed.

## Notes on data, performance and security

To be filled in during the interview.

## Open questions

1. Does the exception of M7 also name a segment the GTFS marks as accessible and the alighting at the stop, in a new version of the specification, or does the text stay as it is? `Block: no` - resolved in this shape by the condition of the registry entry Wording of the public transport segment of O9.
2. What does a public transport leg show the person besides its green state and its source: the line, the boarding and alighting stops, the departure time - and what of it is the text form of M8 and M10? `Block: yes` (category: time semantics and zone offset, if a departure time is shown)
3. Who agrees the change of `plan_route` in `docs/product/api_contract.md`: Marek and Adrian, Kuber for the HarmonyOS client, or Rafał in their place with a caveat? `Block: yes` (category: stability of the programming interface (API) contract)
4. Who fetches the copy of the GTFS and builds the routing data with public transport: a step of this initiative in the loading program of `osm_import`, or something else? `Block: no`
5. Where does the day each feed was published, stated in the description of the data sources (M10), come from: written into the page by hand, or read from the service? `Block: no`
6. When did the 4.5 hours start, and who keeps the record of them? `Block: no`
