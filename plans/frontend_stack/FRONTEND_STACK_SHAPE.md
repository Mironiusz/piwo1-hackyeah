# Shape: Choice of the frontend technology for the MVP and of the standards for frontend code

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) is a phone-first web app whose whole main scenario has to work with a keyboard and a screen reader. Which technology the user interface is built in, and how its code is held to the standards of the repository, was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it. The standards of the repository cover only Python code: the Python profile describes a Python service, and frontend code falls outside it.

## Recipient and trigger

- The owner of the decision is the frontend person of the team; the external API person is consulted about the map tile service. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-3, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- The repository has Node.js v24.18.0 and npm 11.16.0 on the machine of the agent's session, and `package.json` pins only prettier 3.7.4, used for markdown (`docs/standards/standard_formatting.md`, section Markdown formatting).
- `docs/standards/standard_documentation.md` asks a project outside the Python profile to record its own code unit there; nothing is recorded for frontend code.
- `tests/architecture/test_prose_style.py` checks forbidden characters and bold in `.md` and `.py` files only (`docs/standards/standard_formatting.md`, section Emphasis in prose).
- The HarmonyOS port is an open entry in `docs/standards/decision_registry.md`; one of its variants is an ArkTS application embedding the web app.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans/geocoding/` decided on 2026-10-03 (`plans/geocoding/GEOCODING_PRD.md` FR-1 - FR-5, `plans/geocoding/GEOCODING_PLAN.md` D-3) that the search runs only on submission, shows a list the user always picks from with a keyboard and a screen reader, has two distinct messages for nothing found and search unavailable, and never puts the search text into the address of the page. It also recorded a risk for this initiative: map tiles loaded by the browser straight from `tile.openstreetmap.org` reveal the IP address of the person and the area they look at to that service.
- `plans/osm_data_source/` decided on 2026-10-03 (`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-18) that the map shows the attribution `© OpenStreetMap contributors` as a link to `https://www.openstreetmap.org/copyright`, visible without any interaction on every view with the map, as the attribution guidelines of the OpenStreetMap Foundation require.

## Smallest meaningful scope

Following from the seed: a decision on the frontend technology and on how frontend code is held to the standards, taken by the right people. Whether this initiative also sets up the frontend is open (question 1).

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-16 and AC-15 - the main scenario with a keyboard alone and with a screen reader on a phone, WCAG 2.2 AA contrast, every piece of map information also as text.
2. FR-10 and AC-9 - four segment states told apart in a grayscale screenshot, with a legend.
3. FR-19 and AC-18 - Polish and English, default from the browser, a switch that keeps the planned route; usable at 360 px width and not broken on a desktop browser.
4. FR-8 and AC-7 - a geozone created from the first focus to the saved state with the keyboard alone.
5. FR-1 - the profile kept only on the device.
6. FR-9 and AC-8 - the OpenStreetMap attribution visible on the map.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Is the frontend only a technology choice? No: the repository has no standards for non-Python code, so the choice also decides which gates check it, and that changes the standards map (question 2).
- Does the HarmonyOS port constrain the choice? Possibly, if the port embeds the web app; the port itself is undecided (question 3).

## Domain rules or explicit TODO

- Missing information is never shown as accessible, and color is never the only carrier of a segment state (`docs/product/specification.md`, M7 and M10).
- Nothing about the author of a report, vote or geozone is shown to other users (`docs/product/specification.md`, M9).

## Notes on data, performance and security

- The profile and the current location never reach the account (`docs/product/specification.md`, M1 and M2); the frontend is where the profile lives.
- The map display relies on an external tile service whose terms and limits are checked together with the choice.

## Open questions

1. Does the initiative end with the recorded decision handed to `plans/mvp/MVP_PLAN.md` Q-3, or does it also set up the frontend? `Block: no`
2. Which standards and gates apply to frontend code, and is the standards map extended in the same change? `Block: no`
3. Does the frontend have to be reusable by the HarmonyOS port, and does a second client of the same programming interface have to be planned from the start? `Block: yes` (category: stability of the programming interface (API) contract)
4. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
