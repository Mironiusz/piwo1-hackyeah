# Shape: Choice of the frontend technology for the MVP and of the standards for frontend code

Document state: 2026-10-03, interview closed
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

## Smallest meaningful scope

Following from the seed: a decision on the frontend technology and on how frontend code is held to the standards, taken by the right people. The initiative ends with the recorded decision: the answer handed to `plans/mvp/MVP_PLAN.md` Q-3 and the entry for frontend code in the standards (answer of the user to question 1, 2026-10-03). It does not set up the frontend project.

## Out of scope

- Setting up the frontend project (scaffolding, the map with the attribution, the language switch, the gates running on code) and the screens of the main scenario. The user answered question 1 on 2026-10-03 that the initiative ends with the decision; setting up the frontend belongs to the implementation of `plans/mvp/`, which receives the decision through Q-3. The seed item, the decision taken by the right people, keeps its executor: the frontend person.
- The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-16 and AC-15 - the main scenario with a keyboard alone and with a screen reader on a phone, WCAG 2.2 AA contrast, every piece of map information also as text.
2. FR-10 and AC-9 - four segment states told apart in a grayscale screenshot, with a legend.
3. FR-19 and AC-18 - Polish and English, default from the browser, a switch that keeps the planned route; usable at 360 px width and not broken on a desktop browser.
4. FR-8 and AC-7 - a geozone created from the first focus to the saved state with the keyboard alone.
5. FR-1 - the profile kept only on the device.
6. FR-9 and AC-8 - the OpenStreetMap attribution visible on the map.

## Scenarios: input, flow, expected state after the run

1. Input: the six requirements listed in Functional requirements, the two-client rule of the programming interface from Domain rules, the backend fixed in `plans/mvp/MVP_PLAN.md` D-1, and the terms and limits of the candidate map tile services. Flow: the frontend person compares the candidate technologies against these inputs, consults the external API person on the tile service, and chooses. Expected state: the chosen technology, the map library, the tile service and the rejected variants with the reason for each are recorded in this initiative; `plans/mvp/MVP_PLAN.md` Q-3 points to that record and is no longer open.
2. Input: the chosen technology and the standards of the repository, which cover only Python code. Flow: the frontend person names the frontend code unit, the formatter and linter, the test runner and the gates that check frontend code. Expected state: frontend code has a recorded code unit in `docs/standards/standard_documentation.md`, as that standard asks of a project outside the Python profile, and the standards map names which standards and gates apply to frontend code; no frontend file exists yet.

## Challenging own assumptions

- Is the frontend only a technology choice? No: the repository has no standards for non-Python code, so the choice also decides which gates check it, and that changes the standards map (question 2).
- Does the HarmonyOS port constrain the choice? Yes, but not through the frontend code: the user answered on 2026-10-03 that the port is a second client of the same programming interface (a native ArkTS/ArkUI client or React Native for OpenHarmony), not an ArkTS application embedding the web app. The web frontend therefore does not have to run inside a HarmonyOS WebView; what it shares with the port is the programming interface, which has to be planned for two clients from the start.

## Domain rules or explicit TODO

- The programming interface between the frontend and the backend has two clients from the start: the web frontend and the HarmonyOS port (a native ArkTS/ArkUI client or React Native for OpenHarmony). Nothing the web frontend needs may be available only through a channel the port cannot use, such as server-rendered HTML fragments or state kept only in the web page. Answer of the user, 2026-10-03, to question 3 (category: stability of the programming interface (API) contract). The user is the repository owner; the decision owner named in Recipient and trigger is the frontend person, so this answer removes the question from the list without replacing that person's ruling. The contract itself is settled in `plans/api_contract/`, which receives this as an input.
- Whether the Huawei submission happens at all stays an open entry of `docs/standards/decision_registry.md` (HarmonyOS port and the Huawei submission); the answer above fixes only that, if it happens, it is a second client and not an embedding of the web app.
- Missing information is never shown as accessible, and color is never the only carrier of a segment state (`docs/product/specification.md`, M7 and M10).
- Nothing about the author of a report, vote or geozone is shown to other users (`docs/product/specification.md`, M9).
- Agent decision at C:40, without asking: the standards map is extended in the same change as the decision, not in a later one (former question 2). `docs/standards/standard_documentation.md` already asks a project outside the Python profile to record its own code unit there, so recording the decision without that entry would leave frontend code outside every standard at the moment the first frontend file is written. Which standards and gates are named is part of the decision itself and stays with the frontend person.
- Agent decision at C:40, without asking: the decision is due before the first frontend file of `plans/mvp/` is written (former question 4). Q-3 blocks the frontend part of the MVP, and the Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts), so any later point would mean rewriting frontend code already written. A clock time is not set here, because it depends on the team's split of work, which the repository does not record.

## Notes on data, performance and security

- The profile and the current location never reach the account (`docs/product/specification.md`, M1 and M2); the frontend is where the profile lives.
- The map display relies on an external tile service whose terms and limits are checked together with the choice.

## Open questions

None. Questions 1 and 3 were answered by the user; questions 2 and 4 were settled as agent decisions recorded in Domain rules or explicit TODO.
