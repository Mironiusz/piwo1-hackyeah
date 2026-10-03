# Shape: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03, interview in progress
Regulator: C:40

The value C:40 was confirmed by the user in answer 2 of the seed.

## Problem

The MVP (`plans/mvp/`) is split into work packages that several people build in parallel (`plans/mvp/MVP_PRD.md`, Risks and notes). The frontend and the backend can be built at the same time only when the programming interface between them is agreed first: which requests exist, what they carry and what they return, including errors. The contract is not defined anywhere yet; the user asked for an initiative on it for the backend person.

## Recipient and trigger

- The owner of the contract is the backend person of the team; the frontend person is consulted as its first consumer. The ownership was given by the user in the seed (agent question 2 and user answer 2).
- `plans/mvp/MVP_PLAN.md`, open question Q-9, which waits for this contract. Trigger: the user's request of 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code and no programming interface exist. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- `CLAUDE.md`, section What we are building: a web app first, ported to HarmonyOS if time allows; `plans/mvp/MVP_PRD.md`, Dependencies: the solution must not prevent a second client from using the same data and rules.
- Several decisions the contract depends on are delegated to their own initiatives: `plans/routing_engine/` (what a route is made of), `plans/account_sessions/` (how a request is resolved to an actor), `plans/frontend_stack/` (the first consumer), `plans/geocoding/` (whether address search goes through the backend).
- `plans/geocoding/` decided on 2026-10-03 (`plans/geocoding/GEOCODING_PLAN.md` D-3, D-4, D-7, D-11) that the address search goes through the backend. The search text travels only in the body of a POST request, never in a URL. The answer is a list of matches with a label, a latitude and a longitude, an empty list when nothing is found, a response distinct from both when the search is unavailable, and a caller error for a text longer than 200 characters as received or empty after normalization.
- `plans/osm_data_source/` decided on 2026-10-03 (`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-4, D-8) that the date of the OpenStreetMap copy in use is the calendar day in Europe/Warsaw of the state of OpenStreetMap the copy reflects, never the day it was downloaded, and that the date of an OpenStreetMap fact is the calendar day in Europe/Warsaw of the last OpenStreetMap edit of its element.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans/osm_barrier_mapping/` decided on 2026-10-03 (`docs/product/specification.md` version 3, M6 - M8) that the route response names the missing attributes of a segment with partial data or no data as kerbs, surface, incline and width, says for a way marked `wheelchair=no` that OpenStreetMap marks it as not accessible for wheelchairs, and carries the number of steps of stairs when OpenStreetMap gives it, next to the source and the calendar date of the last OpenStreetMap edit of every OpenStreetMap fact.

## Smallest meaningful scope

Following from the seed: the contract of the programming interface between the frontend and the backend of the MVP, owned by the backend person. Whether this initiative also builds the endpoints, or only fixes the contract that the MVP packages then build, is open (question 1).

## Out of scope

The technical decisions delegated in the same conversation have their own initiatives: `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`. The domain model and database schema, the backend architecture with the worker, and the identifier of a vote without an account were offered as topics of this initiative and not chosen; they stay with `plans/mvp/`.

## Functional requirements

The contract has to carry these requirements of `plans/mvp/MVP_PRD.md` between the frontend and the backend:

1. FR-1 and FR-2 - a route request with the start, the destination and the barrier and amenity preferences of the profile, not linked to the account.
2. FR-2, FR-3, FR-4, FR-10, FR-11 and FR-17 - a route response with segments and their states, the missing attributes, the three groups of the list, the proposed alternative with its reason, the statement that no route without barriers exists, and a distinct answer when routing does not answer.
3. FR-5 - a report with the check for existing facts of the same type within about 15 m before saving, and saving only after the approved summary.
4. FR-6 and FR-7 - confirming and denying any fact, OpenStreetMap facts included, with one vote per person per fact.
5. FR-8 - creating a geozone and voting on it.
6. FR-9 - the date of the OpenStreetMap copy in use.
7. FR-12 and FR-13 - accounts, and contributions without an account.
8. FR-14 - flagging, the moderator view, hiding.
9. FR-15 and FR-18 - every fact with its source, date and status, and the sample data mark, without anything about its author or the weights.
10. FR-19 - switching the language without losing the planned route.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Can the contract be fixed before routing and sessions are decided? Only partly: the shape of a route response depends on `plans/routing_engine/`, and how a request identifies an actor depends on `plans/account_sessions/`. Fixing those parts first would be guessing a contract (question 3).
- Does the API return texts in a language, or codes the client translates? FR-19 keeps the planned route across a language switch, and a second client would have to translate the same codes; this changes the contract, not only the frontend (question 4).
- Is the frontend the only consumer? Today yes; a HarmonyOS client is possible but undecided, which changes how stable the contract has to be (question 2).

## Domain rules or explicit TODO

- Nothing about the author of a report, vote or geozone - neither a pseudonym nor whether the author was logged in - reaches other users (`docs/product/specification.md`, M9); the responses must not carry it.
- The current location travels only in the route request: it is not stored, not logged and not linked to the account (`docs/product/specification.md`, M2).

## Notes on data, performance and security

- The route request carries the preferences of the profile, which practically reveal health information (`docs/product/specification.md`, M1).
- A response body never contains an exception, a query fragment, a database object name or a connection string (`docs/standards/standard_errors.md`, Reaction while handling a request).

## Open questions

1. Does the initiative end with the agreed contract handed to `plans/mvp/MVP_PLAN.md` Q-9, or does it also build the endpoints? `Block: no`
2. Who consumes the interface - the web frontend only, or also a HarmonyOS client - and how stable must it be? `Block: yes` (category: stability of the programming interface (API) contract)
3. In which order are the contract, `plans/routing_engine/` and `plans/account_sessions/` settled, so that no part of the contract is guessed? `Block: no`
4. Does the interface return texts in a language or codes that the client translates? `Block: no`
5. What may each role - a person without an account, a logged-in person, a moderator - read and do through the interface, separately for lists and for single items? `Block: yes` (category: read visibility and permissions)
6. Which parts of a request may be logged, given that the location and the preferences may not? `Block: yes` (category: personal data)
7. By when must the contract be agreed, given the deadline at 11:00 on 4 October 2026? `Block: no`
