# PRD: Valhalla as the routing engine and public transport routes from static GTFS

Document state: 2026-10-04

## Business goal

By 11:00 on 4 October 2026 the MVP of `plans/mvp/` plans walking routes in Kraków matched to the barrier preferences of a person (`docs/product/specification.md` version 7, M2, M7, M8), computed by a routing engine run by the project instead of a graph the project writes itself. The user judged writing an own router the wrong call, all the more so because routes are also meant to use public transport (seed, message 1), and chose Valhalla, run by the project on its own infrastructure, in the shape. As an optional feature, a route can use the public transport of ZTP Kraków from its static GTFS, if that can be integrated quickly (seed, message 2).

This task also unblocks the two initiatives waiting for it: items 3 and 4 of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md`, on which Q-11 and the whole of `plans/mvp/MVP_PLAN.md` wait, and `plans/deployment/`, which already deploys Valhalla on the answer of the user of 2026-10-04 while D-9 of the MVP plan still names the own graph.

## Problem and its consequences

- D-9 of `plans/mvp/MVP_PLAN.md` names a graph of the pedestrian network in the memory of the backend process, written by the project. The user rejected it on 2026-10-03 (seed, message 1). Until this task replaces D-9, two documents of the repository say different things about how routes are computed, and Q-11 cannot decide how the route computation is fed or where it runs.
- No product code exists yet, so the change costs documents only; every hour the decision stays open is taken from the work packages of `plans/mvp/`, which all wait for Q-11.
- Valhalla does not apply the rules of the specification on its own. It has its own rules of which ways a pedestrian may use, decides some barriers by itself, has no route with the fewest barriers, and in its published version the walking legs of a public transport route ignore the places a request asks to avoid (the spike of 2026-10-03, run by the user outside the project). Left alone, it could lead a wheelchair user over steps on the way to a tram stop, which is exactly what M10 forbids: "Missing information is never presented as a confirmation of accessibility."
- Public transport routes are out of scope in version 7 of the specification ("Turn-by-turn navigation and public transport routes."), so the optional feature needs a new version of it first.

## Scope

1. Valhalla, run by the project on its own infrastructure, computes the walking routes of M2 in place of the own graph of `plans_finished/routing_engine/`, with the behavior of M2, M7 and M8 unchanged (shape, Smallest meaningful scope, item 1).
2. Routes with public transport from the static GTFS of ZTP Kraków as an optional feature, built first among the optional features and, unlike them, in parallel with the mandatory features from the start, within a time box of 4.5 hours of work of the people of the team, after which it is dropped (shape, Smallest meaningful scope, item 2; the parallel start and the measure of the time box decided by the user at the gate of this PRD on 2026-10-04).
3. A new version of the specification, of `CLAUDE.md` and of `AI_WORKFLOW.md` that records the optional feature and the exception for public transport without accessibility data (shape, functional requirement 8).
4. Replacing D-9 of `plans/mvp/MVP_PLAN.md` with the decision of this initiative, together with the constraints D-9 hands to the rest of that plan (shape, functional requirement 9).
5. Handing over to `plans_finished/backend_architecture/` and to `plans/deployment/` what the engine needs from the backend and from the server of the demo, and what makes it not answer. Agent decision at C:40, without asking: both shapes wait for this initiative by name (`BACKEND_ARCHITECTURE_SHAPE.md`, question 2; `DEPLOYMENT_SHAPE.md`, section Current state), as `plans_finished/routing_engine/` handed its needs to the demo environment.
6. The technical decision the work packages build on: how the engine is fed with the copy in use, how a request carries the profile, the facts and the geozones, how the route with the fewest barriers and the alternative are computed, how a route is tied to the stored stretches and checked before it is shown, and what makes routing unavailable. Decided by the user in phase B on 2026-10-04: this initiative delivers documents only, against building the engine and its data here and against building everything here.

## Out of scope

- Building the engine, its data and the route on it: the image of the engine, the network file and the routing data the import produces, the requests, the route with the fewest barriers, the alternative, the tie of a route to the stored stretches and its check. Work packages of `plans/mvp/` build them under the decision of this initiative, which replaces D-9 there. Decided by the user in phase B on 2026-10-04 (Scope, item 6).
- Building the routes with public transport of O9. A separate initiative, set up by the user, takes FR-5 - FR-9 and FR-11 of this PRD and the decision of this initiative as its input, and its time box runs from its start. Decided by the user in phase B on 2026-10-04, against a work package of `plans/mvp/`.
- GTFS-RT and any real-time public transport data (seed, message 2).
- A departure or arrival time chosen by the person; a public transport route always departs now (section Domain rules).
- A date of the timetable in the interface; the freshness of the GTFS goes into the description of the data sources (section Domain rules).
- Turn-by-turn navigation, which stays out of scope as the specification says.
- Any routing service outside the project, a public Valhalla instance included (M2).
- Building the backend skeleton, the database schema and the deployment configuration, which `plans_finished/backend_architecture/`, `plans/schema_revision/` and `plans/deployment/` do; this task hands them its needs (Scope, item 5).
- Taking routing down on the hosted demo during the live demo, cut by the user on 2026-10-03 in `plans/deployment/` (`DEPLOYMENT_SHAPE.md`, section Out of scope). The behavior of the app when the engine does not answer stays (FR-10).
- Changing the tag rules and thresholds of M6, the segment rules of M7 and the list of M8, which this task applies as they stand.

## Functional requirements

FR-1. Walking routes by the engine of the project. A walking route of M2 is computed by Valhalla run by the project on its own infrastructure. The behavior of M2, M7 and M8 does not change: the route uses only the pedestrian network of M2, never the access rules of the engine; it avoids the barriers from the profile and the matching geozones; it keeps an unverified or disputed barrier on a red segment and proposes the alternative that avoids it; it falls back to the route with the fewest barriers when every way crosses one; it shows the stretch to the network in the state no data; and every segment gets its state of M7 and its items in the list of M8 (shape, functional requirement 1; `plans/mvp/MVP_PRD.md` FR-2, FR-3, FR-4, FR-10, FR-11).

FR-2. Nothing of a route request leaves the project. The request to the engine stays on the infrastructure of the project, and nothing the engine keeps or logs about a request holds the current location, which M2 says is "not stored, not logged and not linked to the account" (shape, functional requirement 2 and section Notes on data, performance and security).

FR-3. The copy in use and new facts. A route takes its ways, its facts, its segment states and the date of the copy from one copy of OpenStreetMap, the copy in use (M6), and never combines the ways of one copy with the facts or the date of another. A new vote, report or geozone counts in the next route, without a restart of a service and without a new import. Taken over from `plans_finished/routing_engine/ROUTING_ENGINE_PRD.md` FR-1, which the replaced engine had to meet. Agent decision at C:40, without asking: the shape keeps the behavior of M2, M6 and M7 unchanged, and these are the conditions under which that behavior holds.

FR-4. Response time. A walking route across Kraków, with everything FR-2, FR-3, FR-4 and FR-11 of `plans/mvp/MVP_PRD.md` show after planning, is answered within 5 seconds on the server of the demo, the route with the fewest barriers and the alternative included (`plans_finished/routing_engine/ROUTING_ENGINE_PRD.md` FR-1).

FR-5. Kind of route. The route form has a switch between a walking route and a route with public transport. Walking is the default, and one route is computed at a time (shape, functional requirement 3).

FR-6. Route with public transport. A route with public transport uses the static GTFS of ZTP Kraków - the feeds `GTFS_KRK_T`, `GTFS_KRK_A` and `GTFS_KRK_M` - and always departs now, in the Europe/Warsaw zone. Its walking legs follow every rule of FR-1 and FR-3 (shape, functional requirement 4). It never boards or alights at a stop the GTFS marks as not accessible and never uses a trip the GTFS marks as not accessible; riding through such a stop on the same vehicle is allowed (section Domain rules).

FR-7. Public transport segment. A public transport segment - the ride and the boarding at the stop - is green whenever the GTFS gives no accessibility information for it, with the source GTFS of ZTP Kraków and no date. It is not a fact: it has no status and cannot be voted on or flagged (shape, functional requirement 5).

FR-8. Public transport unavailable. When the route with public transport cannot be answered while walking routes can, the app computes the walking route on its own and shows it together with a plain statement that public transport was unavailable (shape, functional requirement 6).

FR-9. Copy of the GTFS. The copy of the GTFS is fetched before the demo as a whole or not at all, refreshed only by hand, and the last complete copy stays in use when a fresh one fails (shape, functional requirement 7).

FR-10. Engine not answering. When the engine does not answer or does not answer in time, the app shows the plain message of M10 and no route, walking or otherwise, and sends nothing to a routing service outside the project (shape, scenario 5; `plans/mvp/MVP_PRD.md` FR-17).

FR-11. Time box. When public transport routes do not give a working route with a tram in Kraków within 4.5 hours of work of the people of the team, the feature is dropped; the work of agents does not count toward the 4.5 hours, and the time box runs from the start of the work, which goes in parallel with the mandatory features (section Domain rules). When it is dropped: the switch of FR-5 is not shown, walking routes of FR-1 stay, and the work moves on to O1 (shape, Smallest meaningful scope, item 2, and scenario 6).

FR-12. Specification and rules. The specification gets a new version: public transport routes leave the section Out of scope and become the optional feature O9, built first, before O1, and, as the only optional feature, in parallel with the mandatory features, with the time box of FR-11; the exception for the public transport of ZTP Kraków departs from M7 and M10 and is written next to them. `CLAUDE.md` names the exception next to the rule from the briefs, and `AI_WORKFLOW.md` records that change (shape, functional requirement 8).

FR-13. Decision recorded and handed over. D-9 of `plans/mvp/MVP_PLAN.md` is replaced by the decision of this initiative, with the constraints it hands to the rest of that plan, and the entry Technical directions of the MVP plan of `docs/standards/decision_registry.md` follows it. `plans_finished/backend_architecture/` gets, for its items 3 and 4, how the route computation is fed with the copy in use and what runs where; `plans/deployment/` gets what the engine needs from the server of the demo - memory, disk, processor, its own service and the data it is built from - and what makes it not answer (Scope, item 5).

## Acceptance criteria

AC-1 - AC-13 are checked by the work packages of `plans/mvp/` and by the initiative of O9 that build them (section Out of scope). This initiative checks AC-14 - AC-16.

AC-1 (FR-1). Shape scenario 1: profile "I use a wheelchair", start Rondo Mogilskie, destination Tauron Arena, a confirmed user report of stairs on the shortest way, switch on walking. The route goes around the stairs, its segments carry the states of M7, and the list of M8 is shown.

AC-2 (FR-1). Shape scenario 2: a profile that avoids stairs and a destination reachable only by ways with 1, 2 and 4 known stairs. The app shows the route with 1 barrier, the plain statement that no route without barriers exists, and the place of that barrier in the list.

AC-3 (FR-1). An anonymous report of stairs on a stretch OpenStreetMap says nothing about: for a wheelchair profile the route goes through it, the segment is red, and an alternative route avoiding it is proposed with the reason naming the stairs and the status unverified (`plans/mvp/MVP_PRD.md` AC-3).

AC-4 (FR-1). A way M2 admits but the engine on its own would refuse - for example a way with `highway=bridleway`, or one with `smoothness=impassable` - is used by a route when it is the shortest way, and a way M2 keeps out but the engine on its own would admit - for example `access=private` without a permission for pedestrians, or `foot=use_sidepath` - is never part of a route.

AC-5 (FR-2). After a route request from the current location, no service outside the project received any part of it, and nothing the engine keeps or logs holds that location.

AC-6 (FR-3). A confirmed report of stairs saved on the shortest way changes the next route, without a restart and without an import. After a fresh copy of OpenStreetMap replaces the copy in use, every way of a route belongs to the new copy and the route shows the date of the new copy.

AC-7 (FR-4). A walking route from Tyniec to Wyciąże, with the barriers and geozones of the demo data, is answered within 5 seconds on the server of the demo, and so is the case of AC-2.

AC-8 (FR-5, FR-6, FR-7). Shape scenario 3: profile "I walk with a baby stroller", Rondo Mogilskie to Tauron Arena, switch on public transport. The route departs now in Europe/Warsaw, its walking legs carry their states of M7 and their barriers in the list of M8, and a barrier from the profile on the shortest walking way to the stop is avoided. The tram segment is green with the source GTFS of ZTP Kraków and no date, and it offers no vote and no flag. With the switch untouched, the route is a walking route.

AC-9 (FR-6). With a copy of the GTFS in which the stop where the route of AC-8 boards is marked not accessible, the route boards at another stop; a trip marked not accessible is not used; a route may ride through a stop marked not accessible on the same vehicle.

AC-10 (FR-8). Shape scenario 4: at 02:30 with no departure soon, or with a GTFS copy that failed to load, switch on public transport. The app shows the walking route with its states and list, and a plain statement that public transport was unavailable.

AC-11 (FR-9). A fresh fetch of the GTFS that fails or is incomplete leaves the last complete copy in use, and routes with public transport keep working on it.

AC-12 (FR-10). Shape scenario 5: with the engine down, a route request in either position of the switch ends with the plain message of M10 and no route.

AC-13 (FR-11). Shape scenario 6: when 4.5 hours of work of the people of the team on public transport routes end without a working route with a tram in Kraków, the switch is not shown, walking routes work, and the next optional feature started is O1.

AC-14 (FR-12). The new version of the specification lists O9 before O1 with the time box and its parallel start, has no public transport routes in Out of scope, and states the exception next to M7 and M10; `CLAUDE.md` and `AI_WORKFLOW.md` name it.

AC-15 (FR-13). D-9 of `plans/mvp/MVP_PLAN.md` points to this initiative; `plans_finished/backend_architecture/` and `plans/deployment/` cite the needs handed to them.

AC-16 (FR-13). The decision names, for each of FR-1 - FR-4 and FR-10, what the import and route work packages of `plans/mvp/` build and with which settings of the engine, so that they build it without a choice of their own, and for FR-5 - FR-9 and FR-11 what the initiative of O9 takes over.

## Domain rules

- The pedestrian network of M2, version 5, stays the rule: the engine routes only on the ways that rule admits, and the specification does not take the access rules of the engine. Decided by the user on 2026-10-03 (shape, section Domain rules).
- A segment of public transport organized by ZTP Kraków - trams and buses, the feeds `GTFS_KRK_T`, `GTFS_KRK_A` and `GTFS_KRK_M` - is treated as accessible whenever the GTFS gives no information on its accessibility. Decided by the user on 2026-10-03 as an exception "introduced on purpose" (seed, message 2), knowing that it conflicts with the rule of the Kraków brief and of M10 that missing information is never presented as a confirmation of accessibility. It covers public transport only, never walking segments.
- A stop or a trip the GTFS explicitly marks as not accessible is not accessible (shape, section Domain rules, agent decision at C:40). A route never boards or alights at such a stop and never uses such a trip; riding through such a stop on the same vehicle is allowed. Decided by the user at the gate of this PRD on 2026-10-04, settling the TODO of the shape, against leaving it out of scope and against showing it as a barrier the route does not avoid.
- A public transport segment - the ride and the boarding at the stop - is shown exactly like a green walking segment, with no additional description, with the source GTFS of ZTP Kraków and without a date; the freshness of the GTFS, the day each feed was published, goes into the description of the data sources and the presentation (shape, section Domain rules).
- A public transport route always departs now, at the moment of the request in the Europe/Warsaw zone (shape, section Domain rules).
- The person chooses the kind of route with the switch of FR-5; walking is the default and one route is computed at a time (shape, section Domain rules).
- When every way to the destination crosses a barrier from the profile or a matching geozone, the route stays the route with the fewest such barriers of M2, unchanged (shape, section Domain rules). A start or a destination inside a geozone is such a case whenever every stretch next to it is covered by the geozone, because a geozone covers stretches, never a chosen point (M2). Agent decision at C:40, without asking: a reading of M2, which the spike made relevant by showing that the engine answers no route at all when an avoided area holds the start or the destination.
- When no route with public transport avoids every barrier and geozone its walking legs have to avoid, the route with public transport cannot be answered and FR-8 applies: the app computes the walking route, the route with the fewest barriers when needed, and states that public transport was unavailable. Decided by the user in phase B on 2026-10-04, against a route with public transport with the fewest barriers on its walking legs.
- The copy of the GTFS follows the copy of OpenStreetMap of M6: fetched before the demo, used as a whole or not at all, refreshed by hand, never on a schedule, and the last complete copy stays when a fresh one fails (shape, section Domain rules).
- When the route with public transport cannot be answered while walking routes can, the app computes the walking route on its own and states that public transport was unavailable (shape, section Domain rules).
- The static GTFS of ZTP Kraków is a public data source of the city, not an internal system of UMK or MJO (shape, section Domain rules).
- The new optional feature takes the number O9 and is built first, before O1 (shape, section Domain rules). Unlike the other optional features, which are built only after all mandatory features work, it is built in parallel with the mandatory features from the start, and its time box counts only the hours of work of the people of the team, not the work of agents. Decided by the user at the gate of this PRD on 2026-10-04, against starting it after M1 - M11 work and against counting the time on the clock.

## Dependencies and impact on other modules

- `plans/mvp/`: D-9 of its plan is replaced (FR-13); FR-2, FR-3, FR-4, FR-10, FR-11 and FR-17 of its PRD are met by the engine of this task.
- `plans_finished/backend_architecture/`: its items 3 and 4 wait for this task by the decision of the user (`BACKEND_ARCHITECTURE_SHAPE.md`, question 2), and Q-11 of the MVP plan closes only after them.
- `plans/deployment/`: deploys the engine as one service of its own in a container, from an image of the project that serves both kinds of route, with its data and, if the optional feature is built, the public transport data (`DEPLOYMENT_SHAPE.md`, section Current state, answer of the user of 2026-10-04; one service decided by the user in phase B on 2026-10-04, against a second service for public transport).
- The initiative of O9, set up by the user (section Out of scope).
- `plans/schema_revision/` and `docs/product/schema.md`: the route takes its facts and geozones from the stored data; whether the engine needs anything stored beyond it is for phase B, and a need beyond it is raised with the db person, never assumed (`plans_finished/routing_engine/ROUTING_ENGINE_PRD.md` FR-3).
- `plans_finished/osm_data_source/`: the copy of OpenStreetMap lives in the database and the downloaded file is deleted after each run (D-14 there), while the engine builds its own data from a file; reconciling the two, without breaking FR-3, is for phase B, and a change to a decision of that finished initiative is raised with the user.
- `docs/product/api_contract.md`: the switch of FR-5, the public transport segments of FR-7 and the statement of FR-8 change the route operation, and a change of an operation is a change of that document first (`plans/mvp/MVP_PLAN.md` D-12).
- `plans_finished/frontend_stack/` and the frontend work package of `plans/mvp/`: the switch, the public transport segment and the statement are shown by the frontend.
- `docs/product/specification.md`, `CLAUDE.md` and `AI_WORKFLOW.md` (FR-12).

## Risks and notes

- Time. The Kraków submission closes at 11:00 on 4 October 2026 and no product code exists. This task sits on the critical path of the MVP plan through Q-11, so a delay here delays every work package.
- The engine as published does not keep the rules of FR-1 on the walking legs of a public transport route. The spike made it do so with two small changes to the engine, so the optional feature means the project builds and keeps its own build of the engine until the changes are accepted upstream. Without that build FR-6 cannot be met and the time box of FR-11 decides.
- The route with the fewest barriers is not a feature of the engine: it needs logic of the project next to it, which the spike prototyped. The old D-1 rejected Valhalla partly for this reason, and the user accepted it as a cost of the change (shape, section Challenging own assumptions).
- The spike found that the engine can silently ignore every place a request asks to avoid when one of them fails to load. A route computed that way looks like a compliant route. Phase B has to make sure such a route is never shown as avoiding the barriers, because that would present a barrier as absent.
- A green public transport segment is not safe by data: the feeds of 2026-10-03 carry no accessibility information at all, and older high-floor vehicles may serve a route. The risk to the person and to the criterion "Data reliability, presentation and updates" (15% of the Kraków task description) is accepted by the user (shape, section Challenging own assumptions).
- The engine keeps a timetable of about 60 days from the day its data is built, and from then on answers no public transport route at all. For the demo this is covered by the walking fallback of FR-8.
- Server of the demo. The user confirmed in phase B on 2026-10-04 the 16 GB of memory and 16 cores of the server of the user in a data centre that `plans_finished/backend_architecture/` and `plans/deployment/` record; a figure of 32 GB and 44 processors given earlier in the same conversation does not hold. It is above what the spike measured for the engine with public transport.
- One service serves both kinds of route, so walking routes, which are mandatory, run on the build of the engine the project makes for the optional feature. Accepted by the user in phase B on 2026-10-04.
- The terms of use of the GTFS of ZTP Kraków were not checked; the brief asks the team to state them for every source (shape, section Notes on data, performance and security).
- The parallel start of O9 takes time of the people of the team - questions, reviews, commits and Merge Requests, which only a human makes - from the mandatory features before 11:00, while no product code exists yet. Accepted by the user at the gate of this PRD on 2026-10-04.
- The spike was run outside the project; its scripts, measurements and the two changes to the engine are not in the repository yet. Phase B decides what of them enters the repository and on what evidence its facts rest.
