# Shape: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03, interview closed
Regulator: C:40

The value C:40 was confirmed by the user in answer 2 of the seed.

## Problem

The MVP (`plans/mvp/`) is split into work packages that several people build in parallel (`plans/mvp/MVP_PRD.md`, Risks and notes). The frontend and the backend can be built at the same time only when the programming interface between them is agreed first: which requests exist, what they carry and what they return, including errors. The contract is not defined anywhere yet; the user asked for an initiative on it for the backend person.

## Recipient and trigger

- The owner of the contract is the backend person of the team; the frontend person is consulted as its first consumer. The ownership was given by the user in the seed (agent question 2 and user answer 2).
- `plans/mvp/MVP_PLAN.md`, open question Q-9, which waits for this contract. Trigger: the user's request of 2026-10-03 in phase B of `plans/mvp/`.
- The user decided in this interview that the API contract may be settled in parallel with `plans/routing_engine/` and `plans/account_sessions/`; details depending on those decisions are to be coordinated with their owners. Endpoint implementation waits for Q-10 and Q-11 decisions in `plans/mvp/MVP_PLAN.md`.

## Current state

- No product code and no programming interface exist. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- `CLAUDE.md`, section What we are building: a web app first, ported to HarmonyOS if time allows; `plans/mvp/MVP_PRD.md`, Dependencies: the solution must not prevent a second client from using the same data and rules. In this interview, the user decided that the system and its API must be ready for both Web and HarmonyOS from the start. This does not decide whether a native HarmonyOS app is built or submitted.
- The user decided in this interview that the API does not need backward compatibility for independently updated clients; the backend and both clients may evolve through coordinated changes.
- The user decided in this interview that API contract work may proceed before Q-10, but endpoint implementation waits until Q-10 settles the domain model, database schema and identifier of a vote without an account, and Q-11 settles the backend architecture with the worker.
- Several decisions the contract depends on are delegated to their own initiatives: `plans/routing_engine/` (what a route is made of), `plans/account_sessions/` (how a request is resolved to an actor), `plans/frontend_stack/` (the first consumer), `plans/geocoding/` (whether address search goes through the backend).
- `plans/geocoding/` decided on 2026-10-03 (`plans/geocoding/GEOCODING_PLAN.md` D-3, D-4, D-7, D-11) that the address search goes through the backend. The search text travels only in the body of a POST request, never in a URL. The answer is a list of matches with a label, a latitude and a longitude, an empty list when nothing is found, a response distinct from both when the search is unavailable, and a caller error for a text longer than 200 characters as received or empty after normalization.
- `plans/osm_data_source/` decided on 2026-10-03 (`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-4, D-8) that the date of the OpenStreetMap copy in use is the calendar day in Europe/Warsaw of the state of OpenStreetMap the copy reflects, never the day it was downloaded, and that the date of an OpenStreetMap fact is the calendar day in Europe/Warsaw of the last OpenStreetMap edit of its element.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans/osm_barrier_mapping/` decided on 2026-10-03 (`docs/product/specification.md` version 3, M6 - M8) that the route response names the missing attributes of a segment with partial data or no data as kerbs, surface, incline and width, says for a way marked `wheelchair=no` that OpenStreetMap marks it as not accessible for wheelchairs, and carries the number of steps of stairs when OpenStreetMap gives it, next to the source and the calendar date of the last OpenStreetMap edit of every OpenStreetMap fact.

## Smallest meaningful scope

Following from the seed and the user's answers in this interview: define the contract of the programming interface between the frontend and the backend of the MVP, then implement its endpoints after Q-10 settles the domain model, database schema and identifier of a vote without an account, and Q-11 settles the backend architecture with the worker in `plans/mvp/MVP_PLAN.md`. The backend person owns the work; the frontend person is consulted.

## Out of scope

The technical decisions delegated in the same conversation have their own initiatives: `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`. The domain model and database schema, the backend architecture with the worker, and the identifier of a vote without an account were offered as topics of this initiative and not chosen; they stayed with `plans/mvp/`. Later on 2026-10-03 the domain model and database schema, with the identifier of a vote without an account, moved at the user's request to `plans/fact_schema/` (Q-10 of `plans/mvp/MVP_PLAN.md`), and the backend architecture with the worker stays with `plans/mvp/` as its Q-11.

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
11. The user decided in this interview that the API normally returns stable codes for the clients to translate; it returns text in a selected language only when that is the only way to implement a feature.

## Scenarios: input, flow, expected state after the run

1. A person selects a start, a destination and barrier and amenity preferences, then requests a route. The service returns a route with its segment states, missing attributes, relevant barriers and amenities, and any proposed alternative and reason. If routing is unavailable, it returns a distinct unavailable result and no guessed route. Both clients can display the same result and translate stable codes.
2. A person submits a report. The service returns existing facts of the same type within about 15 m for comparison. If the person confirms it is the same fact, the service records a confirmation; otherwise it accepts a new report only after the person approves its summary. No report is merged automatically or saved without approval.
3. A person without an account and a logged-in person read visible content, submit reports and vote. Only a logged-in person can flag content. A moderator sees flagged reports and geozones in the moderation view and can hide them; hidden content no longer appears in ordinary lists or details. A person cannot cast a second vote on the same fact.
4. A person switches the interface language while a route is planned. The route remains available and the selected client displays the same stable API codes in the chosen language.

## Challenging own assumptions

- Can the contract be shaped before routing and sessions are decided? The user chose parallel work; route and actor details depending on those initiatives are coordinated with their owners rather than guessed here.
- Does the API return texts in a language, or codes the client translates? The user decided in this interview that stable codes are the default and clients translate them; localized text is allowed only when required to implement a feature.
- Is the frontend the only consumer? The user decided in this interview that the system must be ready for both Web and HarmonyOS. The separate decision whether to build or submit a native HarmonyOS app remains open in `docs/standards/decision_registry.md`.

## Domain rules or explicit TODO

- Nothing about the author of a report, vote or geozone - neither a pseudonym nor whether the author was logged in - reaches other users (`docs/product/specification.md`, M9); the responses must not carry it.
- The current location travels only in the route request: it is not stored, not logged and not linked to the account (`docs/product/specification.md`, M2).
- The user confirmed in this interview that anonymous and logged-in people have the same read access to visible content in lists and details; both can report and vote. Only logged-in people can flag. A moderator additionally sees flagged content in the moderation view and can hide it; hidden content is absent from ordinary lists and details.

## Notes on data, performance and security

- The route request carries the preferences of the profile, which practically reveal health information (`docs/product/specification.md`, M1).
- The user decided in this interview that API request logs contain only the operation name, outcome/status, duration and request identifier. They contain no request or response body, headers, pseudonym, account identifier, location, preferences, IP address or browser characteristics.
- If an API request fails, a separate diagnostic log may include the full traceback required by `docs/standards/standard_logging.md`; the user approved this in the interview. This does not change the four-field limit for API request logs.
- A response body never contains an exception, a query fragment, a database object name or a connection string (`docs/standards/standard_errors.md`, Reaction while handling a request).
- `plans/mvp/MVP_PLAN.md` Q-10 follows Q-1 through Q-9, and the mandatory MVP must work in the demo before the Kraków submission deadline. Agent decision at C:40, without asking: settle this API contract before Q-10 can proceed and complete the endpoint implementation after Q-10 and Q-11 by the demo deadline at 11:00 on 4 October 2026.
- The repository does not estimate how long Q-1 through Q-11 and the endpoint implementation will take, so whether the endpoint scope fits before the demo deadline cannot yet be established.

## Open questions

None. The contract is settled before Q-10 in `plans/mvp/MVP_PLAN.md`; endpoint implementation follows Q-10 and Q-11 and is due by the Kraków demo deadline. The available time for that sequence has no estimate in the repository.
