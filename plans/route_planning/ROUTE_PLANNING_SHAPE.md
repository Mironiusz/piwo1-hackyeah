# Shape: Walking routes of the MVP

Document state: 2026-10-04, interview closed
Regulator: C:40

## Problem

The main scenario of the MVP rests on a walking route matched to the profile (M2 of `docs/product/specification.md`), with the states of its segments (M7), the list for the route (M8) and a plain message when routing does not answer (M10). Every technical decision behind it is made - Valhalla run by the project, D-9 of `MVP.md` with `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-1 - D-16 and the decisions of `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` it keeps - and the operation `plan_route` stands in `docs/product/api_contract.md`, section Route, but no code computes a route. This initiative builds the route side of D-5 and D-9 of `MVP.md` and the operation `plan_route` (seed, the quoted row of the table Initiatives).

The interview is answered by Rafał in place of Marek, the owner of the initiative, on 2026-10-04 (Rafał: "robię to za niego, bo marek śpi", I am doing it for him, because Marek is asleep). Every ruling below is a ruling given by the user in place of Marek and is still to be confirmed by him. A ruling that also needs Kuber and Adrian says so.

## Recipient and trigger

- A person who plans a walking route in the web client or in the HarmonyOS client, through `plan_route` (`POST /api/routes`) with a start, a destination and the barriers and amenities of the profile; the client plans a shown route again when the profile changes or a vote or a report of the person is saved (M1, M2).
- Adrian and Kuber, who build the route screens of `frontend_app` and `stage5_harmonyos_port` against the response of `plan_route`.
- `public_transport_routing`, owned by Marek too, which builds O9 on the walking route (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-12) and starts its code after this initiative (`MVP.md`, Order and critical path).
- Mateusz, whose `osm_importer` keeps the boundary of Kraków of every copy for the refusal of requirement 12, and Kuba, if phase B keeps it in the database.
- Check 4.1 of `FINAL_CHECKLIST.md` and `stage7_demo_scenario`, which verify the route on the running service.
- Inside the service the trigger is every route request; the graph of the route with the fewest barriers is built when the backend process starts and rebuilt when the instant of the copy in use changes (`VALHALLA_ROUTING_PLAN.md` D-7).

## Current state

Checked on 2026-10-04 on the branch `rm/requirements-preparation`, equal to `origin/dev`, and on the branches of the remote.

- `plans/route_planning/` holds only its seed and `STAGE.md` with stage 4, on every branch of the remote. `plans_finished/` holds no initiative of this name.
- No backend code exists: the repository root has no `api/`, `service/`, `data/` or `worker/`. `plans/backend_skeleton/`, which creates them, has a plan in progress, and its review ends with Q-2 still awaiting a decision.
- The image of D-1 of `VALHALLA_ROUTING_PLAN.md` already exists: `valhalla/Dockerfile` with the two patches (F-26 there). What D-13 there leaves to this initiative of D-1 is the configuration of the service.
- The import side of D-9 of `MVP.md` - the network file, the walking data of Valhalla and the publication of the pointer to them - is built by `plans/osm_importer/`, whose plan is in progress and which has no code.
- On this branch `plans/schema_first_revision/` has only its seed. The branch `origin/jmi/odklejka_v1` of Kuba holds its shape, PRD, plan, review and the first revision in `db/`, not merged on 2026-10-04. Neither that branch nor any other holds code that derives the status of a fact from its votes; `MVP.md` gives that code to `schema_first_revision` and `community_facts`.
- The target schema `docs/product/schema.md` holds the copy in `osm_copy`, `osm_way`, `osm_node` and `osm_way_node` and the facts in `fact`. It keeps no boundary of Kraków and no name of a way.
- `plan_route` in `docs/product/api_contract.md`, section Route: the request carries `start`, `destination`, `avoid` and `need`; the response carries `osm_copy_date`, `barrier_free_route_exists`, `route` and `alternative`; a segment carries `state`, always one of the four states of M7, `missing_attributes` and `is_marked_wheelchair_no`; the route carries the three groups of M8; the one error is `routing_unavailable` with status 503.
- Three open entries of `docs/standards/decision_registry.md` touch the operation: Route without assessment in the contract and Refusal of a point outside Kraków in the contract, both to be decided by Marek with Kuber and Adrian before `plan_route` is built, and Street name of an item of a list, deferred until Marek has tested the programming interface.
- `docs/product/views.md`, section The views read against the contract of the team, records that a segment carries its missing attributes and that the frontend does not show them (decision 8), because version 11 of the specification replaced the named missing attributes with one plain note (M8; `MVP.md`, section Requirements and initiatives).
- The HarmonyOS client merged into `dev` on 2026-10-04 (`mobile_app/accessway/entry/src/main/ets/data/ApiMapping.ets`, function `planFromApi`) derives whether a route is assessed from the barriers of its own request, sets a route without assessment as free of barriers in its field `barrierFree`, and names the attributes of `missing_attributes` in its gaps of the route, which M8 has not named since version 11 of the specification. None of this is code of this initiative.
- The importer assembles the administrative boundary of Kraków, relation 449696, in every run (`plans/osm_importer/OSM_IMPORTER_PLAN.md`, Step 2, `build_osm_boundary`) and stores it nowhere, and no OpenStreetMap data, the boundary included, may enter the repository (`agent_docs/memory/_cross_cutting.md`, entry OpenStreetMap data in the repository). The bounds of the map of Kraków also hold parts of Wieliczka and Niepołomice (`plans_finished/geocoding/GEOCODING_PLAN.md` D-6).
- This branch and the branch of Kuba each carry a different version 13 of the specification: here "two notes on the account in the target schema", there "the vote limit by calendar day and the length of the hash of a vote without an account". Neither changes a rule of a route; the numbering is for whoever merges the branches.

## Smallest meaningful scope

`plan_route` on the running service answers a walking route in Kraków for a profile, computed by the Valhalla service of the project with the decisions of D-9 of `MVP.md`, with the segment states, the alternative around unverified barriers, the route with the fewest barriers when none avoids them, the list for the route and `routing_unavailable` when routing does not answer: AC-2 - AC-4, AC-9, AC-10 and AC-16 of `plans_finished/mvp/MVP_PRD.md` and AC-1 - AC-7 and AC-12 of `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` (`FINAL_CHECKLIST.md`, check 4.1).

## Out of scope

- The import side of D-5 and D-9 of `MVP.md`: the tag mapping, the network file and the walking data of Valhalla with the publication of their pointer (`osm_importer`), and the loading program of the demo (`osm_import`).
- Running the Valhalla service with its data in the hosted demo (`plans/deployment_config/`, `VALHALLA_ROUTING_PLAN.md` D-13).
- Routes with public transport, O9 and D-12 of `VALHALLA_ROUTING_PLAN.md` (`public_transport_routing`).
- The route screens of the clients (`frontend_app`, `stage5_harmonyos_port`) and the address search (`address_search`).
- The code of the status rule of M4, which this initiative calls and never rewrites (`ROUTING_ENGINE_PLAN.md` D-12; `MVP.md`, rows of `schema_first_revision` and `community_facts`).
- The name of a way in the list of a route, deferred by `docs/standards/decision_registry.md`, entry Street name of an item of a list, until Marek has tested the programming interface, which this initiative first makes possible. Agent decision at C:40, without asking: the condition of the entry cannot be met before `plan_route` works.

## Functional requirements

The list follows from the seed and from the decisions it names; it changes with the answers of the open questions.

1. `plan_route` as `docs/product/api_contract.md`, section Route, describes it, without a token, logging only the entry of section Request logs and failures there, and sending nothing of the request outside the project (M2).
2. The copy in use and the walking data the service serves are compared on every request, and a difference ends it with `routing_unavailable` (`VALHALLA_ROUTING_PLAN.md` D-3).
3. The walking request to Valhalla with the costing options of D-4 and the exclusions of D-5 there, with the corridor, the geozone polygons and the limits of the service.
4. The configuration of the Valhalla service: the limits of D-5 and logging that holds no coordinate of a request, shown by a test (D-11 there).
5. The alternative around unverified or disputed barriers of the profile that OpenStreetMap does not contradict (D-6 there).
6. The route with the fewest barriers on the graph of the stretches of the copy in use, with `barrier_free_route_exists` false (D-7 there).
7. The tie of every route to the stored stretches through the trace, and from it the segment states of M7, the three groups of the list of M8 and the amenities within 50 m (D-8 there; `ROUTING_ENGINE_PLAN.md` D-5, D-8 - D-10, D-12).
8. The check of a route against every barrier and geozone it had to avoid before it is shown (D-9 there).
9. `routing_unavailable` in every case of D-10 there, with no route guessed and no call outside the project.
10. The tests of D-13 there: the cases of `ROUTING_ENGINE_PLAN.md` D-16 that still hold and a test in which Valhalla answers a route crossing an excluded barrier and the request ends with `routing_unavailable`.
11. A route of a profile without barriers: when `avoid` is empty, every segment of `route` and of `alternative` has the state `not_assessed`, a fifth value of `state` outside the four states of M7, with an empty `missing_attributes`; `not_assessed` appears in no other case (question 1). This initiative writes the value into `docs/product/api_contract.md`, section plan_route, and `docs/product/views.md`, and moves the entry Route without assessment in the contract of `docs/standards/decision_registry.md` to Resolved decisions.
12. A start or a destination outside the administrative boundary of Kraków of the copy in use is refused by `plan_route` with an error code of its own that names which of the two points lies outside, and no route is computed (question 2). The client checks a point against the bounds of the map of Kraków when it is set, as `docs/product/views.md` proposes, and on the refusal removes the point and gives the message of M2. The import keeps the boundary of every copy with that copy; where and in what form, and the name and status of the error code, are decided in phase B. This initiative writes the refusal into `docs/product/api_contract.md`, section plan_route, and `docs/product/views.md`, hands the keeping of the boundary to `osm_importer`, and moves the entry Refusal of a point outside Kraków in the contract of `docs/standards/decision_registry.md` to Resolved decisions.
13. A point between the bounds of the map and the boundary of Kraków stays set until the route request refuses it, which departs from "the point is not set" of M2. This initiative writes that into M2 through a new version of `docs/product/specification.md`, whose text the user approves at the gate of the PRD (question 2).
14. `missing_attributes` stays in the contract and the service fills it for every segment in `partial_data` or `no_data` as the contract describes (question 3). Whether a client shows it is decided by M8 of the specification for the client, not by this initiative.

## Scenarios: input, flow, expected state after the run

1. Route without barriers. Input: the preset "I use a wheelchair", a start at the Tauron Arena and a destination 1.5 km away, no barrier of the profile on the shortest way. Flow: the copy is checked, Valhalla is asked with the barriers and geozones of the corridor excluded, the route is traced and checked. State after: `barrier_free_route_exists` true, every segment in one of the four states, the list in three groups, `alternative` null, nothing of the request stored or logged.
2. Unverified barrier on the route. Input: as 1, with an unverified user report of stairs on the shortest way that OpenStreetMap does not contradict. Flow: the report is not excluded, its segment is `barrier`; a second request excludes it. State after: `route` keeps the stairs, `alternative` avoids them and names them with the status unverified in `avoided_barriers`.
3. No route without barriers. Input: a destination that every way reaches only over stairs. Flow: Valhalla answers 442 with every barrier excluded, the graph finds the path with the fewest barriers, one more request excludes all others. State after: `barrier_free_route_exists` false, `profile_barriers` names where the stairs are.
4. Routing does not answer. Input: the Valhalla service is down, or answers after 2 seconds. State after: 503 `routing_unavailable`, no route, nothing sent outside the project.
5. Fresh copy not yet served. Input: a fresh OpenStreetMap copy is current in the database and the service still serves the walking data of the previous one. State after: 503 `routing_unavailable` until the service serves the data of the copy in use.
6. Exclusions silently dropped. Input: Valhalla drops the excluded locations without an error (F-9 of `VALHALLA_ROUTING_PLAN.md`) and answers a route crossing a barrier of the profile. Flow: the check of D-9 finds the crossing, the request is repeated once with it excluded, and crosses it again. State after: 503 `routing_unavailable`, one entry at ERROR without coordinates.
7. Profile without barriers. Input: `avoid` empty and `need` of `rest_place`, a start at the Tauron Arena and a destination 1.5 km away. Flow: no barrier and no geozone is excluded, the route is traced and checked as in 1. State after: every segment, the two straight stretches at the ends included, has the state `not_assessed`; every barrier on the route is in `additional_barriers` (M8); `barrier_free_route_exists` is true, because no barrier of the profile exists to cross; `is_marked_wheelchair_no` is filled as for any other profile.
8. Point outside Kraków. Input: a point on the map in Wieliczka, 1 km outside the boundary of Kraków and inside the bounds of the map, as the start, and the Rynek Główny as the destination. Flow: the client sets the start, the destination is set, the client sends `plan_route`; the service finds the start outside the boundary of the copy in use. State after: the refusal names the start, no route is computed and nothing of the request is stored or logged; the client removes the start and says that routes work only in Kraków. A start outside the bounds of the map is refused by the client alone, before it is set.
9. Missing attributes. Input: the preset "I use a wheelchair" and a stretch of pavement with `surface=asphalt` and no `incline` or `width`. State after: the segment is `partial_data` with `missing_attributes` of `incline` and `width`, and the list says in one plain note that some stretches have no data (M8).

## Challenging own assumptions

- Does this initiative still build the image of D-1? No: `valhalla/Dockerfile` exists and is byte for byte the image of the spike (F-26 of `VALHALLA_ROUTING_PLAN.md`), so the work of D-1 shrinks to the configuration of the service.
- Can the effect be verified before `osm_importer` delivers the walking data? Only on small networks the tests build themselves from invented elements; the route on the copy of Kraków waits for check 3.1 of `FINAL_CHECKLIST.md`, as stage 4 says.
- Can a status be shown without the code of the status rule? No: a route reads the statuses through that rule (`ROUTING_ENGINE_PLAN.md` D-12), and no branch holds it on 2026-10-04, so the statuses of a route wait for `schema_first_revision` or `community_facts`.
- Is the instant of the routing data comparable with the instant of the copy as D-3 asks? `plans_finished/backend_architecture/` D-14 reads `tileset_last_modified` from `/status` of the service, while the copy in use is the latest `state_at` of `osm_copy`; how the one maps to the other is for the pointer `osm_importer` publishes and for phase B, not for this shape.
- After questions 1 - 3, does every item of the seed still have an executor? Yes: nothing was cut; the answers added the boundary of Kraków, handed to `osm_importer`, and changes of the contract, the views and the specification, done by this initiative.
- Is the refusal of a point outside Kraków a rule of the route or of the client? Both: M2 says the point is not set, which only the client can do, and the client has no boundary, so the service refuses and the client follows the refusal (question 2).
- Is the deadline reachable? The code of this initiative needs the layers of `backend_skeleton`, the first revision of `schema_first_revision` and, to be verified on Kraków, the walking data of `osm_importer`; none of them is merged at 04:30 on 2026-10-04, and the Kraków submission closes at 11:00 the same day.

## Domain rules or explicit TODO

- The rules of M1, M2, M7, M8 and M10 of `docs/product/specification.md`, read through D-1 - D-11 of `VALHALLA_ROUTING_PLAN.md` and D-4, D-5, D-8 - D-12 and D-14 - D-16 of `ROUTING_ENGINE_PLAN.md`.
- A route avoids the barriers of the profile known from OpenStreetMap, the confirmed barriers of the profile and the geozones of a type in the profile that are unverified, confirmed or disputed; an outdated or hidden fact changes no route (M2, M11).
- A segment without complete data is never green, and a way marked `wheelchair=no` is never green (M7).
- A route of a profile without barriers has every segment in the state `not_assessed` and is never presented as free of barriers (M1, M7). Decided by the user on 2026-10-04 in question 1, in place of Marek, against a field of the route next to a state of null and against the client deriving it from its own `avoid`; to be confirmed by Marek, and as a change of the contract also by Kuber and Adrian. `is_marked_wheelchair_no` stays as it is for such a route, because M8 names a way marked `wheelchair=no` whatever the profile. Agent decision at C:40, without asking, for `is_marked_wheelchair_no`.
- `plan_route` refuses a start or a destination outside the administrative boundary of Kraków of the copy in use, and the client also checks the bounds of the map when a point is set. Decided by the user on 2026-10-04 in question 2, in place of Marek, against also serving the boundary to the clients and against a check of the bounds of the map alone, which would have needed M2 changed; to be confirmed by Marek, and as a change of the contract also by Kuber and Adrian. The user chose it knowing that a point between the bounds of the map and the boundary stays set until the route request refuses it (requirement 13).
- `missing_attributes` stays in the contract and is filled by the service. Decided by the user on 2026-10-04 in question 3, in place of Marek, against removing it from the contract; asked despite the answer of the repository because the contract, the HarmonyOS client and decision 8 of `docs/product/views.md` with M8 say different things (signal 1). The service decides those attributes anyway to choose between the states of M7.
- For the clients, outside this initiative: the HarmonyOS client reads the state `not_assessed` instead of deriving it from its own request, does not name missing attributes in the list (M8), and does not present a route without assessment as free of barriers (M7). Raised with the user on 2026-10-04 for Kuber.

## Notes on data, performance and security

- Personal data: the current location, the start, the destination and the profile are never stored, logged or sent outside the project, the request carries no identity of an account, and the Valhalla service logs no coordinate of a request (M2; `docs/product/api_contract.md`, sections Sessions and actors and Request logs and failures; `VALHALLA_ROUTING_PLAN.md` D-11). Answered in the repository.
- Query volume and cost: a route within 5 seconds (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` FR-4), the corridor of D-5, the graph of D-7 of about 630 MB in the backend process and the service within 2.5 GB, all within the 16 GB of the server (D-14 there). Answered in the repository.
- Source of truth for data: the ways, the facts and the date of one route come from one copy, the copy in use (D-3 there; `ROUTING_ENGINE_PLAN.md` D-3). Answered in the repository.
- Read visibility: hidden and outdated facts are left out, and a fact from OpenStreetMap without votes is unverified and counts until outdated (M2, M4, M11; `ROUTING_ENGINE_PLAN.md` D-12). Answered in the repository.
- Time: `osm_copy_date` is the calendar day of the copy in Europe/Warsaw (`docs/product/api_contract.md`, Conventions). Answered in the repository.
- Idempotency: `plan_route` writes nothing.
- Database schema: the route only reads the schema. Keeping the boundary of Kraków of every copy (requirement 12) is a change of the schema if phase B keeps it in the database, and then a ruling of Kuba and a revision of `schema_first_revision` or a later one; phase B decides between that and a file kept with the walking data.
- Stability of the programming interface contract: the state `not_assessed` (question 1) and the refusal of a point outside Kraków (question 2) change `plan_route` in `docs/product/api_contract.md`; both are still to be confirmed by Kuber and Adrian.

## Open questions

None blocking. Every question of the interview was answered by the user in place of Marek on 2026-10-04 and waits for his confirmation, and questions 1 and 2 also for the confirmation of Kuber and Adrian.
