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
- The source of the OpenStreetMap data the routes are computed on is itself undecided (`plans/osm_data_source/`).
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: a decision on how the MVP computes routes, taken by the right people. Whether this initiative also builds the routing is open (question 1).

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`.

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

- Is this a purely technical choice? Not entirely: whether the current location and the destination may leave the project for a third-party service is a privacy question for the product (question 2), and a public service with usage limits is a risk for the live demo (question 3).
- Can routing be decided before the OpenStreetMap data source? Probably not independently: both decide where the pedestrian network comes from, so the two initiatives may have to be settled together.

## Domain rules or explicit TODO

- The rules of segment states, weights, statuses and the precedence of OpenStreetMap over reports below the threshold are those of `plans/mvp/MVP_PRD.md`, section Domain rules, and `plans/mvp/MVP_SHAPE.md`, section Domain rules; this initiative does not change them.
- Missing information is never shown as accessible (`docs/product/specification.md`, M10).
- The current location travels only in the route request: it is not stored, not logged and not linked to the account (`docs/product/specification.md`, M2).

## Notes on data, performance and security

- A route request carries the barrier preferences of the profile, which the specification keeps off the account because they practically reveal health information (`docs/product/specification.md`, M1).
- `docs/standards/standard_architecture.md`, section Calls to external systems, allows a read from an external system on the request path only as an explicit exception with a timeout, without retries and with a cache that does not remember a failure.

## Open questions

1. Does the initiative end with the recorded decision handed to `plans/mvp/MVP_PLAN.md` Q-1, or does it also build the routing? `Block: no`
2. May the current location, the destination and the barrier preferences be sent to a service outside the project, and if so, what does the privacy information (FR-20) say about it? `Block: yes` (category: personal data)
3. Is a dependency on a public third-party service with usage limits acceptable for the live demo on 4 October? `Block: no`
4. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
