# PRD: Routes with public transport, the optional feature O9

Document state: 2026-10-04

## Business goal

A person with a wheelchair, a baby stroller or difficulty walking can plan a route in Kraków that uses the trams and buses of ZTP Kraków, with walking legs that keep every rule of a walking route, and can read in words which line to take, where to board, where to alight and when it departs. This is the optional feature O9 of `docs/product/specification.md`, built first and in parallel with the mandatory features, within a time box of 4.5 hours of work of the people of the team (specification, O9). It strengthens the route matched to the needs of a person, the core of the Kraków submission, and the base of the Huawei submission, which uses the same programming interface (`MVP.md`, section Goal and deadline).

Success is a route with a tram in Kraków on the running service, shown to the person, before the time box ends. If it does not come, the feature disappears from the app without a trace, and walking routes work as before (shape, Smallest meaningful scope).

## Problem and its consequences

- The route operation of `docs/product/api_contract.md` knows only walking routes, and a field it does not name is refused. Until the interface of O9 is written there, neither the web frontend nor the service can build anything of the feature, and `MVP.md` lets `plans/frontend_app/` start its views of O9 only after that (shape, Current state).
- No copy of the GTFS is fetched by anything: `plans_finished/osm_importer/` leaves public transport out (`plans_finished/osm_importer/OSM_IMPORTER_PRD.md`, Out of scope), and the loading program of the demo loads three other things (`docs/deployment/hosted_demo.md`, section Loading the data). Without it, every route with public transport ends in the walking route.
- M7 of the specification names only "the ride and the boarding at the stop" of a segment whose GTFS gives no accessibility information, so the state of the alighting and of a segment the GTFS marks as accessible does not follow from its text (`docs/standards/decision_registry.md`, entry Wording of the public transport segment of O9).
- The specification says nothing of what a public transport segment shows besides its state and its source. A ride without a line, stops and a time gives the person no route they can follow, and no text form, which M8 and M10 require of everything on the map.
- Two open entries of the registry hold check 1.5 of `FINAL_CHECKLIST.md`, and check 4.2 of O9 waits for it.
- The Kraków submission closes at 11:00 on 4 October 2026, and at 04:32 no code of the backend existed (shape, Current state).

## Scope

1. The interface of a route with public transport in `docs/product/api_contract.md`, written before any code that serves it: the kind of route, the public transport segment, the statement that public transport was unavailable, and the day each feed of the GTFS copy in use was published.
2. A route with public transport of O9, as `plans_finished/valhalla_routing/` decided it for this initiative (`VALHALLA_ROUTING_PLAN.md` D-12), meeting FR-5 - FR-9 of `VALHALLA_ROUTING_PRD.md` as this PRD refines them.
3. The copy of the GTFS of ZTP Kraków, fetched and turned into the data of routes with public transport in the same loading run as the copy of OpenStreetMap.
4. The day each feed of the copy in use was published, given by the service for the page about the data V-13.
5. The time box of 4.5 hours of work of the people of the team, with its record.
6. A new version of the specification - 14 at the time of the shape, or the next free number when it is written -, the two entries of the registry moved to its resolved decisions, and `MVP.md` and `docs/deployment/hosted_demo.md` following this initiative.

## Out of scope

- The switch, the public transport segment, the statement, the days of the feeds and the exception of O9 on the page about the data in the views of the web frontend: `plans/frontend_app/` builds them from the interface of item 1 (`MVP.md`, section Initiatives).
- The views of O9 in the HarmonyOS client: `plans/stage5_harmonyos_port/` decides them, and the interface serves that client as it serves the web frontend (shape, Out of scope, agent decision at C:40).
- The walking route and what a route with public transport reuses of it - the walking legs, the alternative, the route with the fewest barriers and the plain message when routing does not answer: `plans_finished/route_planning/` (`MVP.md`, section Initiatives).
- The importer, the network of the pedestrian ways and the walking data of the routing engine: `plans_finished/osm_importer/` (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-20).
- The stops of buses and trams from the MSIP service of Kraków: the registry entry Initiatives outside MVP.md that overlap its initiatives stays open under its own condition (shape, Out of scope, agent decision at C:40).
- Real-time public transport data (specification, section Out of scope); an arrival time, a choice of the departure or arrival time, and a date of the timetable (specification, O9; shape, question 3).

## Functional requirements

FR-1. Kind of route. The interface carries the choice between a walking route and a route with public transport for the switch of the route form; walking is the default, and one route is computed at a time (`VALHALLA_ROUTING_PRD.md` FR-5).

FR-2. Route with public transport. It uses the three feeds `GTFS_KRK_T`, `GTFS_KRK_A` and `GTFS_KRK_M` and departs now, at the moment of the request in the Europe/Warsaw zone. Its walking legs follow every rule of a walking route of M2, M7 and M8: they avoid the barriers and geozones of the profile, keep the segment states and the list, and nothing of the request leaves the project. It never boards or alights at a stop and never uses a trip the GTFS marks as not accessible; riding through such a stop on the same vehicle is allowed (`VALHALLA_ROUTING_PRD.md` FR-6; specification, O9).

FR-3. Public transport segment. The boarding at the stop, the ride and the alighting at the stop are green, whether the GTFS marks them as accessible or gives no accessibility information for them, with the source GTFS of ZTP Kraków and no date. The segment is not a fact: it has no status and cannot be voted on or flagged. It shows the kind of vehicle - tram or bus -, the line, the name of the boarding stop and of the alighting stop, and the departure time from the boarding stop in hours and minutes in the Europe/Warsaw zone, and the list of M8 holds it as an item in the order of the route, its text form (`VALHALLA_ROUTING_PRD.md` FR-7; shape, questions 2 and 3). With a profile that has no barrier to avoid, the segment has no state, like every other segment of such a route (M1, M7), and still shows the vehicle, the line, the stops and the time. Decided by Rafał on 2026-10-04 in phase B, against the segment green by the exception of O9.

FR-4. Public transport unavailable. When the route with public transport cannot be answered while walking routes can - no departure in time, the data of public transport unavailable, or no route with public transport whose walking legs avoid every barrier and geozone they have to avoid - the service answers the walking route, the route with the fewest barriers of M2 when needed, together with a plain statement that public transport was unavailable. When walking routes cannot be answered either, the answer is the plain message of M10 and no route, walking or otherwise (`VALHALLA_ROUTING_PRD.md` FR-8 and FR-10; specification, O9 and M10).

FR-5. Copy of the GTFS. The copy of the three feeds is fetched before the demo and on a refresh by hand, never on a schedule, in the same loading run as the copy of OpenStreetMap, so that a route with public transport and a walking route always come from the same copy of OpenStreetMap. It is used as a whole or not at all, and the last complete copy stays in use when a fresh one fails (`VALHALLA_ROUTING_PRD.md` FR-9; shape, question 5).

FR-6. Days of the feeds. The service gives the day each feed of the copy in use was published, a calendar day in the Europe/Warsaw zone, so that the page about the data V-13 states it next to the date of the OpenStreetMap copy. After a refresh it is the day of the new copy, after a failed refresh that of the copy kept, without anyone editing a text. The day a feed was published is never replaced by the day it was downloaded (specification, M6 and M10; shape, question 6).

FR-7. Interface first. Everything of FR-1, FR-3, FR-4 and FR-6 that crosses between a client and the service is written into `docs/product/api_contract.md` before the code that serves it. Rafał approves it in place of Marek and Adrian, whom the contract names for a change of an operation; Kuber is told of it as the owner of the HarmonyOS client, and their confirmation joins check 1.4 of `FINAL_CHECKLIST.md` (seed; shape, question 4).

FR-8. Switch only where it works. The switch is shown only where a route with a tram in Kraków works; until then the app plans walking routes only, also while the time box runs (shape, question 8).

FR-9. Time box. 4.5 hours of work of the people of the team on this feature, the work of agents not counted, added up over the people and counted from 04:32 on 2026-10-04, the start of the shape interview. Each piece of work is recorded with the person, the time from and to, and what was done. When the sum reaches 4.5 hours without a working route with a tram in Kraków, the feature is dropped: the switch is not shown, walking routes stay, and the work moves on to O1 (`VALHALLA_ROUTING_PRD.md` FR-11; shape, question 7).

FR-10. Response time. A route with public transport is answered within the 5 seconds a walking route has; when it ends in the walking route of FR-4, the attempt with public transport may add at most 2 seconds (`VALHALLA_ROUTING_PRD.md` FR-4; shape, section Notes on data, performance and security, agent decision at C:40).

FR-11. Documents. A new version of the specification, the one of Scope, item 6, carries FR-3 with its profile without barriers, FR-8 and the wording of the exception in M7, M10 and O9, approved by Rafał. The registry entries When the initiative of O9 starts its code and Wording of the public transport segment of O9 move to its resolved decisions. `MVP.md` follows the parallel start and the step of the loading run, and `docs/deployment/hosted_demo.md`, section Loading the data, names the copy of the GTFS among what that run loads (shape, questions 1, 2 and 5).

## Acceptance criteria

AC-1, AC-2, AC-3, AC-6 and AC-11 below are AC-8, AC-9, AC-10, AC-11 and AC-13 of `VALHALLA_ROUTING_PRD.md`, which `MVP.md` gives to this initiative, as the shape refined them.

AC-1 (FR-1, FR-2, FR-3). Profile "I walk with a baby stroller", start Rondo Mogilskie, destination Tauron Arena, switch on public transport. The route departs now in Europe/Warsaw; its walking legs carry their states of M7 and their barriers in the list of M8, and a barrier from the profile on the shortest walking way to the stop is avoided. The tram segment is green, with the source GTFS of ZTP Kraków, no date, the kind of vehicle, the line, the two stops and the departure time, it appears in the list in the order of the route, and it offers no vote and no flag. With the switch untouched, the same request gives a walking route.

AC-2 (FR-2). With a copy of the GTFS in which the stop where the route of AC-1 boards is marked not accessible, the route boards at another stop; a trip marked not accessible is not used; a route may ride through a stop marked not accessible on the same vehicle.

AC-3 (FR-4). At 02:30 with no departure soon, or with a copy of the GTFS that failed to load, switch on public transport: the app shows the walking route with its states and list, the route with the fewest barriers when no route avoids them, and a plain statement that public transport was unavailable.

AC-4 (FR-4). When every route with public transport would cross a barrier or a geozone of the profile on a walking leg, the answer is that of AC-3, never a route with public transport that crosses it.

AC-5 (FR-4). With the routing service down, a request with the switch on public transport ends with the plain message of M10 and no route.

AC-6 (FR-5). A fresh fetch of the GTFS in which one feed fails or is incomplete leaves the last complete copy of all three feeds in use, and routes with public transport keep working on it.

AC-7 (FR-5). After a refresh by hand of the copy of OpenStreetMap, a route with public transport and a walking route between the same points come from the new copy, and show its date.

AC-8 (FR-6). After a load with feeds published on given days, the service gives those days; after a failed refresh it gives the days of the copy kept. No day given is the day of a download.

AC-9 (FR-7). `docs/product/api_contract.md` carries the interface of FR-1, FR-3, FR-4 and FR-6, with the approval of Rafał in place of Marek and Adrian in its state line, before the first code of this initiative that serves it; check 1.4 of `FINAL_CHECKLIST.md` lists the confirmation of Marek, Adrian and Kuber.

AC-10 (FR-8). In an environment where a route with a tram does not work yet, the route form shows no switch, and a route request gives a walking route. Once a route with a tram works there, the switch is shown.

AC-11 (FR-9). The record of the time box shows every piece of work of the people of the team on this feature from 04:32 on 2026-10-04, with its sum. When the sum reaches 4.5 hours without a working route with a tram in Kraków, the switch is not shown anywhere, walking routes work, and the next optional feature started is O1.

AC-12 (FR-10). The route of AC-1 is answered within 5 seconds on the server of the demo, and the walking route of AC-3 within 7 seconds.

AC-13 (FR-11). The specification is at a new version with FR-3, FR-8 and the wording of the exception, approved by Rafał; both registry entries stand among its resolved decisions; `MVP.md` no longer says that `public_transport_routing` waits for `route_planning` and `osm_importer`, and names its step of the loading run; `docs/deployment/hosted_demo.md` names the copy of the GTFS among what the loading run loads.

AC-14 (FR-3). With a profile that avoids no barrier, the route of AC-1 shows the tram segment without a state, like its walking segments, with the vehicle, the line, the two stops and the departure time.

## Domain rules

- A segment of public transport organized by ZTP Kraków is treated as accessible whenever the GTFS marks it as accessible or gives no information on its accessibility. This is the one deliberate exception to the rule of the Kraków brief and of M10 that missing information is never presented as a confirmation of accessibility, chosen by the user knowingly (`VALHALLA_ROUTING_PRD.md`, Domain rules; `docs/hackathon/challenge_requirements.md`, Conflicts and open points, item 10). It covers public transport only, never a walking segment.
- A stop or a trip the GTFS explicitly marks as not accessible is not accessible: never a place to board or alight, never a trip to ride; riding through such a stop on the same vehicle is allowed (specification, O9).
- A route with public transport always departs now; the person chooses no time, and the interface shows no date of the timetable. The departure time of a ride is a time of day, not a date of the timetable (specification, O9; shape, question 3).
- When no route with public transport keeps every barrier and geozone off its walking legs, public transport counts as unavailable, and the walking route is shown, never a route with public transport with the fewest barriers on its walking legs (`VALHALLA_ROUTING_PRD.md`, Domain rules).
- The copy of the GTFS follows the copy of OpenStreetMap of M6: fetched before the demo, used as a whole or not at all, refreshed by hand, never on a schedule, and the last complete copy stays when a fresh one fails. The day of a feed is the day it was published, not the day it was fetched (specification, M6 and O9).
- The static GTFS of ZTP Kraków is a public data source of the city, not an internal system of UMK or MJO (`VALHALLA_ROUTING_PRD.md`, Domain rules).
- The code of this initiative starts at once, in parallel with `route_planning` and `osm_importer`; what does not need their code goes first. Decided by Rafał on 2026-10-04 (shape, question 1); Marek's ruling is still to be confirmed.
- The time box counts the hours of people, added up, from 04:32 on 2026-10-04, and never the work of agents (specification, O9; shape, question 7).

## Dependencies and impact on other modules

- `plans_finished/route_planning/`, owned by Marek: the walking legs, the walking route of FR-4, the route with the fewest barriers and the plain message when routing does not answer are its code; this initiative joins them once they exist, and the parts the two share are agreed by Marek (shape, question 1).
- `plans_finished/osm_importer/` and `plans/osm_import/`, owned by Mateusz: the data of routes with public transport is built from the same copy of OpenStreetMap as the walking data of `osm_importer`, and the step of FR-5 joins the one loading run of `osm_import` in the form of a step it writes down, as `plans/map_tiles/` and `plans/sample_data/` do (`MVP.md`, section Initiatives).
- `plans/frontend_app/`, owned by Adrian: the switch, the segment, the statement and the days of the feeds in the views, the exception of O9 on the page about the data next to its sentence that missing data is never shown as accessible, and the texts of the interface for them (`docs/product/views.md`, section V-13 and the item on O9 under what no view covers).
- `plans/stage5_harmonyos_port/`, owned by Kuber: told of the interface of FR-7.
- `plans/deployment_config/`, owned by Rafał: the hosted demo runs the loading run with the step of FR-5 and restarts the routing service after it (`docs/deployment/hosted_demo.md`, section Loading the data).
- `FINAL_CHECKLIST.md`: check 1.4 gets the confirmations of FR-7 and of the rulings for Marek, check 1.5 is met for the two entries of O9, and check 4.2 is the check of this initiative.
- `docs/product/specification.md`, `docs/product/api_contract.md`, `docs/standards/decision_registry.md`, `MVP.md` and `docs/deployment/hosted_demo.md` (FR-7, FR-11).
- `plans_finished/valhalla_routing/`: its decision D-12 is the input of this initiative, and its image of the routing engine already carries the changes a route with public transport needs (`valhalla/README.md`, section The patches).

## Risks and notes

- Time. The Kraków submission closes at 11:00, the time box started at 04:32, and a route with a tram whose walking legs keep M2 needs the code of `route_planning`, which did not exist at 04:32. The deadline can come before the 4.5 hours end; FR-8 keeps the demo from showing a switch that does not work.
- Rulings still to be confirmed: Marek for the parallel start and the wording of the exception, as the registry names him; Marek, Adrian and Kuber for the interface of FR-7. A change they make later changes the service and the frontend both.
- A green public transport segment is not safe by data: the feeds of 2026-10-03 carried no accessibility information at all, so every segment is green by the exception, and AC-2 can be shown only on a copy changed for the test. That rests on `VALHALLA_ROUTING_PRD.md`, Risks and notes, and is checked again on the copy fetched. The risk was accepted by the user.
- It is not known which part of a feed of ZTP Kraków gives the day it was published. If no part does, FR-6 cannot be met as written, and the question goes to the user.
- The terms of use of the GTFS of ZTP Kraków were not checked, while the Kraków brief asks the team to state the terms of every source.
- Collision with `route_planning`. Its session reported at 05:00 on 2026-10-04 that it will also change the operation of the route in `docs/product/api_contract.md`, `docs/product/views.md`, the registry and the specification, with a new version for M2, in the same tree and on the same branch. Version 13 was already written on two branches at once and joined at a merge. The order of the two changes is decided by Rafał; the number of the new version is checked right before it is written, and the change of the route operation is written on top of whatever `route_planning` wrote first, never over it.
- The routing engine keeps a timetable of about 60 days from the day its data is built; the demo is deleted on 4 October 2026, so this does not reach the demo.
