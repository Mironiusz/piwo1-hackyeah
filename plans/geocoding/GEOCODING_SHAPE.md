# Shape: Choice of the address search for the MVP

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) lets a user give the start and the destination of a route, and the point of a geozone, by an address. How an address typed by the user is turned into a point on the map was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the external API person of the team; the import person is consulted, because OpenStreetMap carries address tags. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-5, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- On 2026-10-03, from the machine of the agent's session, the public Nominatim instance answered a search for an address in Kraków with HTTP 200. Its usage policy is not checked yet.
- `docs/standards/standard_architecture.md`, section Calls to external systems: a read from an external system on the request path is allowed only as an explicit exception with a timeout, without retries and with a cache that does not remember a failure.
- The source of the OpenStreetMap data is undecided (`plans/osm_data_source/`); OpenStreetMap carries address tags, so the choice may depend on it.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: a decision on how the MVP searches addresses, taken by the right people. Whether this initiative also builds the search is open (question 1).

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/account_sessions/`.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-2 - the start and the destination of a route given as an address within Kraków.
2. FR-8 and AC-7 - the point of a geozone given by an address, with the keyboard alone.
3. FR-16 - the address search usable with a keyboard and a screen reader.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Is an address a piece of personal data here? Possibly: the destination a person searches for can reveal where they go, and the specification keeps even the current location out of storage and logs (`docs/product/specification.md`, M2). Whether a typed address may leave the project is a product question (question 2).
- Does the search have to cover places by name, for example "Tauron Arena", or only street addresses? The demo takes place at the Tauron Arena, so a search by name may matter (question 3).

## Domain rules or explicit TODO

- Routes work only within Kraków (`docs/product/specification.md`, Area, device and language).

## Notes on data, performance and security

- The current location is not stored, not logged and not linked to the account (`docs/product/specification.md`, M2); the same question stands for a typed address.

## Open questions

1. Does the initiative end with the recorded decision handed to `plans/mvp/MVP_PLAN.md` Q-5, or does it also build the search? `Block: no`
2. May an address typed by the user be sent to a service outside the project, and is it stored or logged anywhere in the project? `Block: yes` (category: personal data)
3. Does the search have to find places by name, or street addresses only? `Block: no`
4. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
