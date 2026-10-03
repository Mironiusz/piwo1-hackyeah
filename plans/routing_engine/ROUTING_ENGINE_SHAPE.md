# Shape: Choice of the routing engine for the MVP

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 4). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) needs walking routes in Kraków that follow rules ordinary route engines do not apply on their own: the route avoids only the barriers from the user's profile, keeps an unverified barrier but marks its segment and proposes an alternative, falls back to the route with the fewest barriers when no route without them exists, and splits the route into segments with one of four states and the list of missing attributes. How routes are computed was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the backend person of the team; the external API person is consulted, because one variant is an external routing service. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-1, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- On 2026-10-03, from the machine of the agent's session: the public Valhalla instance answered a pedestrian route request with HTTP 200; the public OSRM demo answered a foot route request with HTTP 200; two public Overpass API instances did not answer within 40 s.
- The usage policy and the logging practice of the public Valhalla instance could not be read on 2026-10-03: the root address of `valhalla1.openstreetmap.de` answers HTTP 404, and the terms of use of its operator, FOSSGIS, are behind a bot protection page. What that operator keeps from a route request, and for how long, is therefore unknown.
- `plans_finished/osm_data_source/` decided on 2026-10-03 (`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-1, D-2, D-6, D-17) that the OpenStreetMap data is the Geofabrik extract of Małopolska in PBF, cut to the administrative boundary of Kraków with every way crossing it kept whole, and refreshed only by hand. Whatever engine is chosen, the facts, the segment states and the date of the copy come from that copy. An engine built by the project reads the same copy - OSRM straight from PBF, osm2pgrouting only after a conversion to XML, a graph in the memory of the backend through pyosmium - while an external engine computes on its own data of another date and area, so its route has to be matched to the ways of the copy before a segment gets a state.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans_finished/osm_barrier_mapping/` decided on 2026-10-03 (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6, D-7, D-11) what the route reads from the import: for every way of the pedestrian network a state of stairs, poor surface, steep incline and narrow passage - present, absent, absent by default for stairs only, unknown - with the number of steps and the `wheelchair=no` marking, and point facts on the nodes of the way: stairs, a narrow passage and kerb points that are high, lowered or unknown. It also decided how a segment combines them, which segments meet a carriageway, and that only an explicit absence or an opposite kerb point contradicts a user report (`docs/product/specification.md` version 3, M2, M6, M7). Left to this initiative: which stretch of way a point report lies on, and within what distance of an opposite kerb point a kerb report counts as contradicted.
- `plans/fact_schema/` passed the gate of its PRD on 2026-10-03 (`plans/fact_schema/FACT_SCHEMA_PRD.md` FR-5, FR-11): what the import gives for every way is stored once and independently of the profile, and the state of a route segment is never stored but derived for each route from it, the profile carried by the route request and the user facts; a hidden fact does not affect the route. Its PRD leaves to this initiative how a route is related to the stretches of way it keeps. Added on 2026-10-03 by `plans/consistency_check/`.
- `plans_finished/local_database/` decided on 2026-10-03 (`plans/mvp/MVP_PLAN.md` D-7) that the local database carries the files of pgRouting 4.0.1 next to PostGIS without creating the extension, so a choice of pgRouting here needs only a new schema revision. Added on 2026-10-03 by `plans/consistency_check/`.
- The user decided on 2026-10-03 in `plans/consistency_check/`, for version 4 of `docs/product/specification.md`: routes avoid the geozones whose type is in the profile when they are unverified, confirmed or disputed, never outdated or hidden ones (U-3 of its review); an OpenStreetMap fact becomes outdated, and stops counting on the route, only when its denials reach at least 2 and outweigh its confirmations, as a user fact does (U-2); and, answering for the backend person, the contract of `plans/api_contract/` does not depend on the routing engine, so the engine adapts to the route response that contract defines (U-5).

## Smallest meaningful scope

A decision on how the MVP computes routes, taken by the right people, recorded and handed to `plans/mvp/MVP_PLAN.md` Q-1, together with the two rules `plans_finished/osm_barrier_mapping/` left to phase B of this initiative (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, Domain rules): which stretch of way a point report lies on, and within what distance of an opposite kerb point a kerb report counts as contradicted. The initiative ends with the recorded decision; the routing itself is built by a work package of `plans/mvp/`, as with `plans_finished/geocoding/`, `plans_finished/osm_data_source/` and `plans_finished/local_database/`. Decided by the user on 2026-10-03 (question 1), against this initiative also building the routing, which would have waited for the schema of `plans/fact_schema/` and the import of `plans_finished/osm_data_source/`, neither of which exists in code yet.

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans/account_sessions/`.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-2 - a walking route within Kraków that avoids barriers from the profile known from OpenStreetMap, confirmed user barriers from the profile and geozones whose type is in the profile; rest places do not change its course.
2. FR-3 - an unverified or disputed barrier from the profile not contradicted by OpenStreetMap stays on the route, its segment is red, and an alternative route avoiding it is proposed with the reason.
3. FR-4 - when every way crosses a barrier from the profile, the route with the fewest such barriers, a plain statement that no route without barriers exists, and the list of where the barriers are.
4. FR-10 and FR-11 - every segment of the route in one of four states, and the missing attributes named for a segment with partial data or no data.
5. FR-11 - amenities from the profile within 50 m of the route (PRD, section Domain rules).
6. FR-17 - when routing does not answer, a plain message and no guessed route.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Is this a purely technical choice? Not entirely: whether the current location and the destination may leave the project for a third-party service is a privacy question for the product (question 2), and a public service with usage limits is a risk for the live demo (question 3). Settled on 2026-10-03: nothing of a route request leaves the project (Domain rules), so the engine runs on the infrastructure of the project and the usage limits of a public service do not apply to routing.
- Does the answer to question 2 keep the destination inside the project? Not entirely: a destination typed as text still reaches the public Nominatim instance through the address search, from the server of the project and without the IP address of the person (`plans_finished/geocoding/GEOCODING_SHAPE.md`, Domain rules; `plans/mvp/MVP_PLAN.md` D-3). That is a separate decision about the search text; the rule here covers the route request, which carries the current location, the coordinates of the start and of the destination, and the barrier preferences.
- Can routing be decided before the OpenStreetMap data source? Probably not independently: both decide where the pedestrian network comes from, so the two initiatives may have to be settled together. Settled on 2026-10-03 by the order of events: `plans_finished/osm_data_source/` decided the source first, and its D-17 is the condition this initiative meets (Current state).

## Domain rules or explicit TODO

- The rules of segment states, weights, statuses and the precedence of OpenStreetMap over reports below the threshold are those of `plans/mvp/MVP_PRD.md`, section Domain rules, and `plans/mvp/MVP_SHAPE.md`, section Domain rules; this initiative does not change them.
- Missing information is never shown as accessible (`docs/product/specification.md`, M10).
- The current location travels only in the route request: it is not stored, not logged and not linked to the account (`docs/product/specification.md`, M2).
- Nothing of a route request leaves the project: the current location, the start, the destination and the barrier and amenity preferences, and anything derived from them such as a list of places to avoid, are used only by software of the project running on its own infrastructure, and are never sent to a routing service outside the project. Decided by the user on 2026-10-03 (question 2), against sending them to an outside service from the server of the project only, without the IP address of the person, as the address search does - a variant that would have needed version 4 of `docs/product/specification.md` to narrow "not logged" in M2 to the project and the privacy information to name the outside service. An external routing service such as the public Valhalla instance is therefore out of the variants of phase B; an engine run by the project on its own infrastructure is not.
- Routing does not depend on a public service with usage limits during the live demo. The former question 3, whether such a dependency is acceptable, closes as a consequence of the rule above. Agent decision at C:40, without asking.

## Notes on data, performance and security

- A route request carries the barrier preferences of the profile, which the specification keeps off the account because they practically reveal health information (`docs/product/specification.md`, M1).
- `docs/standards/standard_architecture.md`, section Calls to external systems, allows a read from an external system on the request path only as an explicit exception with a timeout, without retries and with a cache that does not remember a failure.
- If the route is computed by a service outside the project, the pattern of `agent_docs/memory/_cross_cutting.md`, entry Personal data in requests to outside services, applies to the current location: it travels from the browser only in the body of a POST request, and no log entry of the outgoing call carries the URL with the coordinates. Added on 2026-10-03 by `plans/consistency_check/`. Since question 2 no route request goes to an outside service, so only the first half of the pattern applies: the current location travels from the browser only in the body of a POST request. The risk note of that memory entry, which names this initiative as undecided, becomes stale once this initiative is implemented.

## Open questions

1. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
