# Shape: Choice of the source of OpenStreetMap data for the MVP

Document state: 2026-10-03, interview closed
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

Following from the seed: a decision on where the MVP takes OpenStreetMap data from and how it is refreshed, taken by the right people. The initiative ends with this decision handed to `plans/mvp/MVP_PLAN.md` as a decision closing Q-2; the import and the refresh are built in a work package of `plans/mvp/` together with the backend architecture of Q-11 there, as `plans_finished/geocoding/` did for the address search. Decided by the user on 2026-10-03 (question 1), against building the import in this initiative before Q-11 is settled.

The rules of questions 2, 5 and 6 - an OpenStreetMap fact that disappears or returns in a fresh copy - are product behavior the specification does not describe, so they enter `docs/product/specification.md` in sections M4 and M6 and in Decision provenance, in the same version 3 that takes the rules of `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, as one change approved by the user. Decided by the user on 2026-10-03 (question 7), against a separate version 4 and against keeping the rules only in this shape.

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans_finished/api_contract/`, `plans_finished/routing_engine/`, `plans_finished/frontend_stack/`, `plans_finished/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans_finished/account_sessions/`. Which OpenStreetMap tags count as which barrier is `plans_finished/osm_barrier_mapping/`, not this initiative.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-9 - OpenStreetMap data for Kraków available from the first use, with the attribution visible; when fresh data cannot be fetched, the app works on the last fetched copy and shows its date.
2. FR-5 and FR-6 - OpenStreetMap facts take part in the duplicate check of a report within about 15 m and can be confirmed or denied like user facts.
3. FR-15 and AC-14 - an OpenStreetMap fact shows the date of its last OpenStreetMap edit.
4. FR-2 and FR-10 - the routes and the segment states are computed on this data.

## Scenarios: input, flow, expected state after the run

1. An OpenStreetMap fact with votes disappears in a fresh copy. Input: on 1 October at 20:00 the import finds way W tagged `highway=steps`, which gives the OpenStreetMap fact stairs with the last OpenStreetMap edit on 14 March 2022. Flow: 3 October 09:00 a logged-in confirmation (1); 09:40 an anonymous confirmation (0.5); 12:00 a fresh import in which W is `highway=footway` without steps; 12:30 a user with the preset "I use a wheelchair" plans a route through W. Expected state at 12:30: stairs on W is a user fact carrying the 1.5 of confirmations, with the status unverified; the missing steps tag does not contradict it (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, section Domain rules), so the segment is red, the route keeps W and an alternative avoiding it is proposed. Decided by the user on 2026-10-03 (question 2).
2. An OpenStreetMap fact without a majority of confirmations disappears. Input: on 1 October the import finds way V tagged `surface=sett`, which gives the OpenStreetMap fact poor surface. Flow: 2 October an anonymous denial (0.5); 3 October 12:00 a fresh import in which V is `surface=asphalt`; 12:30 a user with the preset "I walk with a baby stroller" plans a route through V. Expected state at 12:30: the OpenStreetMap fact poor surface on V is outdated with the reason that it was removed in OpenStreetMap, it is on neither the map nor the route, and the denial stays in its history. The same holds without any vote and at a tie. Decided by the user on 2026-10-03 (question 5).
3. A converted fact returns. Input: stairs on W converted to a user fact as in scenario 1. Flow: 3 October 13:00 an anonymous confirmation (0.5), the sum reaches 2.0 and the fact is confirmed; 4 October 06:00 a fresh import in which the OpenStreetMap edit was reverted and W is `highway=steps` again; 08:00 a user with the preset "I use a wheelchair" plans a route. Expected state at 08:00: there is one stairs fact on W, an OpenStreetMap fact with the date of its last OpenStreetMap edit and its 2.0 of confirmations, and the route avoids W. Decided by the user on 2026-10-03 (question 6).

## Challenging own assumptions

- Is the date of the last OpenStreetMap edit of each fact available from every candidate source? It has to be, for AC-14; this is to be checked for each variant in phase B, not assumed.
- How fresh does the data have to be for a demo on 4 October? One copy fetched before the demo is enough, with a refresh by hand; a regular refresh matters only for the plan from prototype to service (question 3). The cost is the 15% criterion "Data reliability, presentation and updates" (`docs/hackathon/challenge_requirements.md`, line 90), which the MVP meets with the visible date of the copy and the description, not with a running schedule.
- Does the conversion of question 2 contradict `docs/product/specification.md` M4, which says an OpenStreetMap fact "becomes outdated" once denials reach the sum of 2? No: M4 describes denials, not a fact removed from OpenStreetMap, which M4 does not mention at all. The conversion is a new rule for a case the specification does not describe, which is why it was asked rather than derived.
- Does the conversion break "Missing information is never presented as a confirmation of accessibility" (M10)? In scenario 2 the outdated stairs or poor surface disappears and the segment may turn green, but only because the fresh copy says so explicitly or, for stairs, by the rule of `plans_finished/osm_barrier_mapping/` that a way not tagged as steps is a known "no stairs". The green state comes from data, not from its absence.
- What if a bad edit or vandalism in OpenStreetMap removes many facts at once? Facts without a majority of confirmations then become outdated in one refresh. In the MVP a refresh runs only by hand, so the team sees the result before the demo; for the service this is a risk of the regular refresh, to be described in the plan from prototype to service.
- Does a converted fact need its anonymous votes to keep their weight after the 30-day identifier is deleted (`docs/product/specification.md`, M9)? Yes: the conversion counts the stored weights, so a vote has to outlive its identifier. M9 already says that votes stay and keep their weight after an account is deleted; the same for the deleted identifier is a point for Q-10, not decided here.

## Domain rules or explicit TODO

- Dates are calendar days in the Europe/Warsaw zone; OpenStreetMap edit times given in UTC are converted the same way (`plans/mvp/MVP_SHAPE.md`, section Domain rules).
- The app never pretends its data is current: stale OpenStreetMap data is shown with its date (`plans/mvp/MVP_SHAPE.md`, section Domain rules).
- For OpenStreetMap facts a successful fresh copy is authoritative and replaces the stored one; the stored copy is only the fallback used while a fresh one cannot be fetched. Source: `docs/product/specification.md`, M6 ("When fresh data cannot be fetched, the app works on the last fetched copy"), and the app does not edit OpenStreetMap data. Recorded without asking as the answer found in the specification to the first half of question 2.
- An OpenStreetMap fact that is missing from a fresh copy becomes a user fact that keeps its votes, and from then on its status follows the rules of a user fact (`docs/product/specification.md`, M4). Decided by the user on 2026-10-03 (question 2), answering for the import person who owns this decision; the ruling of the import person is still to be confirmed.
- This conversion happens only when the sum of the confirmations of the fact is greater than the sum of its denials. Otherwise - no votes, denials only, or a tie - the OpenStreetMap fact becomes outdated with the reason that it was removed in OpenStreetMap, disappears from the map and the route, and its votes stay in its history. Decided by the user on 2026-10-03 (question 5), against converting at a single confirmation and against converting always, with the same caveat about the import person.
- A fact that returns in a later copy on the same OpenStreetMap element with the same type is the same fact again: a converted user fact or an outdated OpenStreetMap fact becomes an OpenStreetMap fact once more, with the source OpenStreetMap, the date of its last OpenStreetMap edit and all its votes. Decided by the user on 2026-10-03 (question 6), against keeping two separate facts and against keeping the user fact, with the same caveat about the import person. This is a match by identity, not by distance, so it does not conflict with "Nothing is merged automatically" of `docs/product/specification.md` M3, which concerns a new report and the facts within about 15 m; the agent pointed this reading out before the answer.
- An OpenStreetMap fact that appears in a fresh copy where a user fact of the same type already lies is a separate fact; the two are not merged. Source: `docs/product/specification.md`, M3 ("Nothing is merged automatically"), since a user fact is a point that can be tied to an OpenStreetMap element only by distance. Recorded without asking as an answer found in the specification.
- In the MVP the data is fetched once before the demo, and the team can trigger a fresh copy by hand; nothing refreshes on a schedule. A regular refresh, for example once a day, is described in the plan from prototype to service and in the description of the data sources (`docs/hackathon/challenge_requirements.md`, lines 49, 62 and 68), not built. Decided by the user on 2026-10-03 (question 3), against a scheduled refresh in the MVP and against a single copy without any refresh path. The rules of questions 2, 5 and 6 therefore run on every refresh triggered by hand.
- The decision of this initiative, including the choice of the source in phase B, is needed before the first import of the MVP on 3 October 2026, so that the demo recorded on the morning of 4 October runs on it, ahead of the Kraków deadline at 11:00 on 4 October 2026. Agent decision at C:40, without asking: a consequence of question 3 (one fetch before the demo) and of Q-10 of `plans/mvp/MVP_PLAN.md` waiting for question 2.
- TODO for phase B and for Q-10 of `plans/mvp/MVP_PLAN.md`: what counts as the same OpenStreetMap element when OpenStreetMap splits, joins or recreates a way, which changes the identifiers of its parts. The rules above assume an identity that survives such edits only as far as OpenStreetMap keeps the identifier.
- The converted fact keeps all its votes, confirmations and denials alike, and shows the source "user report" with the date of its last confirmation, because OpenStreetMap no longer supports it (`docs/product/specification.md`, M10). Agent decision at C:40, without asking: a consequence of the answer to question 2.
- Whether a fresh OpenStreetMap copy contradicts the converted fact follows the contradiction rule of `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`: a missing tag never contradicts it, an explicit tag value on the passable side does (for example a poor surface fact converted after the way became `surface=asphalt`), and then the color follows OpenStreetMap until the votes reach the sum of 2.

## Notes on data, performance and security

- OpenStreetMap data is under the ODbL: attribution is required, and a database combining OpenStreetMap data with our own may fall under its share-alike terms (`plans/mvp/MVP_PRD.md`, Risks and notes). Nothing here is legal advice.
- The brief warns that information published online is not automatically free to fetch automatically or use commercially (`docs/hackathon/challenge_requirements.md`, Data sources named in the brief).

## Open questions

None. Questions 1 to 7 were answered on 2026-10-03; the numbering of the answers above follows the original list, and questions 5 to 7 were added during the interview.
