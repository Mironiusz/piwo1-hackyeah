# PRD: Walking routes of the MVP

Document state: 2026-10-04

## Business goal

The main scenario of `docs/product/specification.md` is a walking route in Kraków matched to the barriers and amenities a person sets, with what is known about every segment and a list of the barriers on it (Main scenario, steps 2 - 4). The Kraków submission closes at 11:00 on 4 October 2026, and its demo, video and presentation are built on that route, as is the HarmonyOS client of the Huawei submission (`MVP.md`, Goal and deadline). This initiative delivers the route on the service of the project, so that both clients can show it and check 4.1 of `FINAL_CHECKLIST.md` can pass.

The rulings behind this PRD were given by Rafał in place of Marek, the owner of the initiative, on 2026-10-04, and are still to be confirmed by him; the changes of the programming interface contract are also still to be confirmed by Kuber and Adrian (shape, Problem).

## Problem and its consequences

- Every decision about the route is made - the routing engine of the project (`MVP.md` D-9) and the rules of M2, M7 and M8 - and the operation `plan_route` is described in `docs/product/api_contract.md`, but nothing computes a route. Until something does, the route screens of both clients have nothing to show, check 4.1 cannot pass, the demo has no main scenario, and routes with public transport (O9) cannot start their code (`MVP.md`, Order and critical path).
- With a profile that names no barrier, the contract can only answer one of the four states of M7, so a route could come back green everywhere. That presents missing assessment as accessibility, which the briefs and M7 forbid (`docs/standards/decision_registry.md`, entry Route without assessment in the contract).
- The contract has no way to refuse a start or a destination outside Kraków, and the clients have no boundary to check it against, so the rule of M2 that such a point is refused cannot be met (`docs/standards/decision_registry.md`, entry Refusal of a point outside Kraków in the contract).

## Scope

1. The operation `plan_route` on the service of the project: walking routes in Kraków computed by the routing engine of the project, with every behavior M2, M7, M8 and M10 of the specification give a route.
2. The setting of the routing engine of the project for walking routes: what it is allowed to answer and what it is allowed to log.
3. Two changes of the programming interface contract, decided in the shape: the state not assessed of a route of a profile without barriers, and the refusal of a point outside Kraków; written into `docs/product/api_contract.md` and `docs/product/views.md`, with both entries of `docs/standards/decision_registry.md` moved to Resolved decisions.
4. A new version of the specification that records in M2 how long a point outside Kraków stays set (shape, requirement 13).
5. The need handed to `osm_importer`: the boundary of Kraków of every copy is kept with that copy.
6. The tests that show the requirements below.

## Out of scope

- The import side of the routes: the tag mapping, the network and the data of the routing engine prepared from each copy, with their publication (`osm_importer`), and the loading program of the demo (`osm_import`).
- Running the routing engine with its data in the hosted demo (`plans/deployment_config/`).
- Routes with public transport, O9 (`public_transport_routing`).
- The route screens of the clients (`frontend_app`, `stage5_harmonyos_port`), the address search (`address_search`), and how a client presents the missing attributes of a segment, which M8 decides for the client.
- The rule that derives the status of a fact from its votes, which a route calls and never rewrites (`schema_first_revision`, `community_facts`).
- The name of a way in the place of an item of the list, deferred until Marek has tested the programming interface (`docs/standards/decision_registry.md`, entry Street name of an item of a list).

## Functional requirements

FR-1. Route matched to the profile (M2). For a start and a destination in Kraków and the barriers and amenities of a profile, the service answers a walking route that uses only the pedestrian network of M2, never the access rules of the engine itself. The route avoids the barriers of the profile known from OpenStreetMap, the user barriers of the profile that prevail, and the geozones of a type of the profile that are unverified, confirmed or disputed. An outdated or hidden fact changes no route, and a rest place never changes its course (`plans_finished/mvp/MVP_PRD.md` FR-2; `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` FR-1).

FR-2. Alternative around unverified barriers (M2). When the route keeps an unverified or disputed barrier of the profile that OpenStreetMap does not contradict, the response carries one alternative that avoids it, when its path differs, naming each avoided barrier with its status (`plans_finished/mvp/MVP_PRD.md` FR-3).

FR-3. No route without barriers (M2). When every way to the destination crosses a barrier of the profile or a matching geozone, the service answers the route with the fewest such barriers, says that no route without barriers exists, and names where the barriers are (`plans_finished/mvp/MVP_PRD.md` FR-4).

FR-4. Segment states (M7). Every segment of a route of a profile with at least one barrier is in one of the four states of M7, decided by the service. A segment without complete data is never in the state no barrier, and neither is a segment of a way OpenStreetMap marks as not accessible for wheelchairs, whose marking the response carries. The stretch between a chosen point and the pedestrian network is a straight segment in the state no data, with its stairs unknown. A user report that OpenStreetMap contradicts and that has not reached the threshold of M4 is marked as such, and its segment follows OpenStreetMap (`plans_finished/mvp/MVP_PRD.md` FR-10).

FR-5. Route without assessment (M1, M7). When the profile names no barrier, every segment of the route and of its alternative, the stretches to the network included, is in the state not assessed, which is none of the four states of M7 and appears in no other case. Such a route is never presented as free of barriers (shape, requirement 11).

FR-6. List for the route (M8). The response carries the three groups of M8 in order along the route: the barriers of the profile on the route, the barriers outside the profile on the route, and the amenities of the profile within 50 m of the route. Every item has its type, its distance from the start along the route, its source, its date and its status. With a profile without barriers every barrier on the route is in the second group. For every segment in the state partial data or no data the response names the attributes behind the barriers of the profile that are not known; whether a client shows them is decided by M8 for the client (shape, requirement 14; `plans_finished/mvp/MVP_PRD.md` FR-11 as `MVP.md`, section Requirements and initiatives, reads it since version 11 of the specification).

FR-7. Point outside Kraków (M2). A start or a destination outside the administrative boundary of Kraków of the copy in use is refused with an outcome of its own that says which of the two points lies outside, and no route is computed. The client also checks a point against the bounds of the map of Kraków when it is set, and on the refusal removes the point and gives the message of M2 (shape, requirement 12).

FR-8. One copy. The ways, the facts, the segment states and the date of a route come from the copy in use and never combine one copy with another. While the routing engine does not yet serve the data of the copy in use, a route request ends as routing not answering. A new vote, report or geozone counts in the next route without a restart and without an import (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` FR-3).

FR-9. No route shown as compliant when it is not (M10). A route that crosses a barrier or a geozone it had to avoid, other than those of the route with the fewest barriers of FR-3, is never shown; when it cannot be corrected, the request ends as routing not answering (shape, functional requirement 8).

FR-10. Routing not answering (M10). When the routing engine does not answer, does not answer in time or fails, the service answers that a route cannot be planned right now, with no route and nothing guessed, and nothing of the request is sent to a routing service outside the project (`plans_finished/mvp/MVP_PRD.md` FR-17; `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` FR-10).

FR-11. Nothing of a route request is kept (M2). The current location, the start, the destination and the profile are not stored, not logged beyond the name of the operation, its status, its duration and its request identifier, not linked to an account and not sent outside the project, and nothing the routing engine keeps or logs holds a location of a request. A route request carries no identity of an account (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` FR-2; `docs/product/api_contract.md`, sections Sessions and actors and Request logs and failures).

FR-12. Response time. A walking route across Kraków, with its alternative or its route with the fewest barriers, is answered within 5 seconds on the server of the demo (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` FR-4).

FR-13. The contract and the views. FR-5 and FR-7 are written into `docs/product/api_contract.md`, section plan_route, and into `docs/product/views.md`, and the entries Route without assessment in the contract and Refusal of a point outside Kraków in the contract of `docs/standards/decision_registry.md` move to Resolved decisions, each with how it turned out.

FR-14. The specification. A new version of `docs/product/specification.md` records in M2 that a point between the bounds of the map of Kraków and its boundary stays set until the route request refuses it (shape, requirement 13). The user approved on 2026-10-04, at the gate of this PRD, this text, added at the end of the paragraph of M2 on a point outside Kraków: "The app checks a point against the bounds of the map of Kraków when it is set. A point inside those bounds but outside the boundary stays set until the route is requested, and is then refused and removed with the same message."

FR-15. The boundary of Kraków for the import. The need that the import keeps the boundary of Kraków of every copy together with that copy is handed to `osm_importer` and recorded in its plan.

## Acceptance criteria

The criteria are checked on the response of `plan_route`. Those that need the copy of Kraków wait for check 3.1 of `FINAL_CHECKLIST.md`, and AC-14 waits for the hosted demo; until then the tests show each rule on small networks built in the test.

AC-1 (FR-1). Profile "I use a wheelchair", start Rondo Mogilskie, destination Tauron Arena, a confirmed user report of stairs on the shortest way: the route goes around the stairs, its segments carry the states of M7 and the response carries the three groups. With stairs from OpenStreetMap on the shortest way instead, the route goes around them too (`plans_finished/mvp/MVP_PRD.md` AC-2; `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-1).

AC-2 (FR-1). A geozone of type poor surface on the way is avoided for the wheelchair profile and not avoided for a profile without poor surface (`plans_finished/mvp/MVP_PRD.md` AC-2).

AC-3 (FR-1). A way M2 admits but the engine on its own would refuse, a way `highway=bridleway` or one with `smoothness=impassable`, is used when it is the shortest way, and a way M2 keeps out but the engine on its own would admit, `access=private` without a permission for pedestrians or `foot=use_sidepath`, is never part of a route (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-4).

AC-4 (FR-2, FR-4). An anonymous report of stairs on a stretch OpenStreetMap says nothing about: for the wheelchair profile the route goes through it, its segment is in the state barrier, and the alternative avoids it, naming the stairs with the status unverified (`plans_finished/mvp/MVP_PRD.md` AC-3; `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-3).

AC-5 (FR-3). A profile that avoids stairs and a destination reachable only by ways with 1, 2 and 4 known stairs: the route crosses the stairs of 1, the response says that no route without barriers exists, and the group of the barriers of the profile names where they are (`plans_finished/mvp/MVP_PRD.md` AC-4; `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-2).

AC-6 (FR-4). In the run of scenario 4 of `plans_finished/mvp/MVP_SHAPE.md`, the segment through the crossing X follows OpenStreetMap and the report of X is marked as contradicted by OpenStreetMap; after the next anonymous confirmation the segment is in the state barrier and a new route avoids X. On every route no segment with an unknown attribute of the profile is in the state no barrier, no segment of a way marked `wheelchair=no` is in the state no barrier, and both stretches to the network are in the state no data (`plans_finished/mvp/MVP_PRD.md` AC-9, the part of the service).

AC-7 (FR-5). A profile without barriers and the need of a rest place: every segment of the route, both stretches to the network included, is in the state not assessed, none is in one of the four states of M7, and every barrier on the route is in the group of the barriers outside the profile.

AC-8 (FR-6). For the segment of scenario 9 of `plans_finished/mvp/MVP_SHAPE.md`, read as meeting a carriageway, and the preset "I use a wheelchair", the segment is in the state partial data and the response names the incline, the kerbs and the width as unknown. Every item of the three groups has its type, distance from the start, source, date and status, and an amenity of the profile 60 m from the route is not in the third group while one 40 m from it is (`plans_finished/mvp/MVP_PRD.md` AC-10 as `MVP.md` reads it).

AC-9 (FR-7). A start on the map in Wieliczka, 1 km outside the boundary of Kraków and inside the bounds of the map, with the Rynek Główny as the destination, is refused with the outcome of FR-7 naming the start, and no route is computed; a destination outside names the destination, and both outside name both. A point inside the boundary 50 m from it gets a route.

AC-10 (FR-8). A confirmed report of stairs saved on the shortest way changes the next route without a restart and without an import. After a fresh copy of OpenStreetMap replaces the copy in use, a route request ends as routing not answering until the engine serves the data of the new copy, and afterwards every way of a route belongs to the new copy and the route shows its date (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-6).

AC-11 (FR-9). When the engine answers a route that crosses a barrier the request excluded, and answers it again after the barrier is excluded once more, the request ends as routing not answering and no route is shown (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-13).

AC-12 (FR-10). With the engine down, and with the engine answering after its time limit, a route request ends as routing not answering with no route, and no service outside the project received any part of it (`plans_finished/mvp/MVP_PRD.md` AC-16; `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-12).

AC-13 (FR-11). After a route request whose start is a known current location, no service outside the project received any part of it, and neither the logs of the service nor what the engine keeps or logs hold that location (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-5).

AC-14 (FR-12). A walking route from Tyniec to Wyciąże, with the barriers and geozones of the demo data, is answered within 5 seconds on the server of the demo, and so is the case of AC-5 (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` AC-7).

AC-15 (FR-13). `docs/product/api_contract.md`, section plan_route, and `docs/product/views.md` describe the state not assessed and the refusal of a point outside Kraków, and both entries stand in Resolved decisions of `docs/standards/decision_registry.md`.

AC-16 (FR-14). The specification carries a new version whose M2 says how long a point between the bounds of the map and the boundary of Kraków stays set, with the text the user approved.

AC-17 (FR-15). The plan of `osm_importer` names the keeping of the boundary of Kraków of every copy as a need of this initiative.

## Domain rules

- The pedestrian network, the avoided barriers, the contradiction of a report by OpenStreetMap, the 15 m of a report from a stretch, the 5 m of a kerb contradiction and the cover of a geozone are those of M2.
- The four states of M7 and the attribute behind each barrier are those of M7 with the tag rules of M6; a way not tagged as steps counts as known to have no stairs, and on its own does not make a segment partial data.
- A fact from OpenStreetMap that nobody has voted on is unverified and counts on the route until it is outdated; it prevails over a contradicting user report until the confirmations of that report reach the sum of 2 (M4).
- A geozone that holds the start or the destination cannot be avoided; the route crosses it, and the response says that no route without barriers exists (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-5 and D-9).
- The date of the copy in a response is the calendar day of the copy in Europe/Warsaw (M6, M10).
- A route of a profile without barriers is never presented as free of barriers (M7), and missing information is never presented as a confirmation of accessibility (M10).
- A start or a destination is in Kraków when it lies inside the administrative boundary of Kraków of the copy in use (M2).

## Dependencies and impact on other modules

- `backend_skeleton` provides the layers and the entry points the operation lives in, and the local setup; the code of this initiative cannot land before them.
- `schema_first_revision` provides the first schema revision the route reads; on 2026-10-04 it exists only on the unmerged branch of Kuba.
- The rule that derives the status of a fact, from `schema_first_revision` and `community_facts`; no branch held it on 2026-10-04, and without it a route has no statuses.
- `osm_importer` provides the data of the routing engine for each copy with their publication, and receives the need of FR-15. If that need is not delivered, FR-7 cannot work.
- `plans/deployment_config/` runs the routing engine in the hosted demo, which AC-14 needs.
- `frontend_app` and `stage5_harmonyos_port` follow the changes of FR-13. The HarmonyOS client on `dev` derives whether a route is assessed from its own request, treats a route without assessment as free of barriers, and names the missing attributes in its list, which M8 does not allow; that is for Kuber, raised in the shape.
- `public_transport_routing` starts its code after this initiative (`MVP.md`, Order and critical path).
- Documents changed by this initiative: `docs/product/api_contract.md`, `docs/product/views.md`, `docs/standards/decision_registry.md`, `docs/product/specification.md`, and the plan of `osm_importer`.

## Risks and notes

- The deadline: the work starts at about 04:40 on 4 October 2026, and the Kraków submission closes at 11:00 the same day, while `backend_skeleton`, `schema_first_revision`, the status rule and `osm_importer` are each not merged or not written.
- Every ruling of this PRD was given in place of Marek, and the contract changes in place of Kuber and Adrian; a different ruling of theirs changes FR-5, FR-6 or FR-7.
- The branch of Kuba carries a version 13 of the specification different from the version 13 of `dev`, so the version of FR-14 gets its number only when the two are merged.
- The route of the engine and the route with the fewest barriers are computed by different programs on the same copy, so an unusual piece of the network can end as routing not answering instead of a route (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md`, Risks).
- The time of a route with every barrier of a whole route across Kraków was not measured; FR-12 is checked only on the server of the demo.
- How the service tells which copy the routing engine serves is not settled in the documents; it is a question of the plan, not of this PRD.
