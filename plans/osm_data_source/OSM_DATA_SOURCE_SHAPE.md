# Shape: Choice of the source of OpenStreetMap data for the MVP

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 4). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) relies on OpenStreetMap accessibility data for Kraków from the first use, and has to keep working on the last fetched copy, showing its date, when fresh data cannot be fetched. Where the data comes from and how it is refreshed was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the import person of the team; the db person is consulted, because the fetched copy is stored in the database. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-2, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- On 2026-10-03, from the machine of the agent's session: two public Overpass API instances did not answer within 40 s; the Geofabrik extract `malopolskie-latest.osm.pbf` was reachable with a size of 202 232 967 bytes; the `osmium` package (pyosmium) 4.3.1 had a ready wheel for Python 3.13 on Windows.
- The Kraków brief names OpenStreetMap as a map and routing base whose licence terms and attribution have to be respected, and asks for every source to state its origin, terms of use, freshness and verification method (`docs/hackathon/challenge_requirements.md`, Data sources named in the brief).
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: a decision on where the MVP takes OpenStreetMap data from and how it is refreshed, taken by the right people. Whether this initiative also builds the import is open (question 1).

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`. Which OpenStreetMap tags count as which barrier is `plans/osm_barrier_mapping/`, not this initiative.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-9 - OpenStreetMap data for Kraków available from the first use, with the attribution visible; when fresh data cannot be fetched, the app works on the last fetched copy and shows its date.
2. FR-5 and FR-6 - OpenStreetMap facts take part in the duplicate check of a report within about 15 m and can be confirmed or denied like user facts.
3. FR-15 and AC-14 - an OpenStreetMap fact shows the date of its last OpenStreetMap edit.
4. FR-2 and FR-10 - the routes and the segment states are computed on this data.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Is the date of the last OpenStreetMap edit of each fact available from every candidate source? It has to be, for AC-14; this is to be checked for each variant in phase B, not assumed.
- How fresh does the data have to be for a demo on 4 October? Possibly one copy fetched before the demo is enough, and a regular refresh matters only for the presentation of the "prototype to service" plan (question 3).

## Domain rules or explicit TODO

- Dates are calendar days in the Europe/Warsaw zone; OpenStreetMap edit times given in UTC are converted the same way (`plans/mvp/MVP_SHAPE.md`, section Domain rules).
- The app never pretends its data is current: stale OpenStreetMap data is shown with its date (`plans/mvp/MVP_SHAPE.md`, section Domain rules).

## Notes on data, performance and security

- OpenStreetMap data is under the ODbL: attribution is required, and a database combining OpenStreetMap data with our own may fall under its share-alike terms (`plans/mvp/MVP_PRD.md`, Risks and notes). Nothing here is legal advice.
- The brief warns that information published online is not automatically free to fetch automatically or use commercially (`docs/hackathon/challenge_requirements.md`, Data sources named in the brief).

## Open questions

1. Does the initiative end with the recorded decision handed to `plans/mvp/MVP_PLAN.md` Q-2, or does it also build the import? `Block: no`
2. Which copy is authoritative when a fresh fetch and the last stored copy differ for the same fact, and what happens to user votes on an OpenStreetMap fact that disappears in a fresh copy? `Block: yes` (category: source of truth for data)
3. How often does the data have to be refreshed during the hackathon and in the "prototype to service" story? `Block: no`
4. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
