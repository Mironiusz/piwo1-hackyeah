# Shape: Web frontend of the MVP

Document state: 2026-10-04, interview closed
Regulator: C:60

The seed carries no regulator value, so the interview ran at the default C:40 (`plans_finished/mvp/MVP_PLAN.md` D-19). Adrian raised the value to C:60 at the gate of the PRD on 2026-10-04; it applies from phase B of `plan-prd`.

## Problem

No product code of the frontend exists, and a person sees every mandatory feature M1 - M11 only through it. By 11:00 on 4 October 2026 the Kraków jury is shown the main scenario on a phone (`MVP.md`, Goal and deadline), and `MVP.md` hands the web frontend to this initiative: the application in `frontend/`, the four gates of `docs/standards/standard_frontend.md`, the pair of documents of the code unit, every screen of `plans_finished/mvp/MVP_PRD.md` with the map drawn from the archive of `plans_finished/map_tiles/`, and the parts of the optional feature O9 once its interface is in the contract (seed, the quoted row of `MVP.md`).

Without it the backend initiatives of `MVP.md` have nothing that shows their work, and nineteen of the twenty requirements of `plans_finished/mvp/MVP_PRD.md` name `frontend_app` among the initiatives that meet them (`MVP.md`, Requirements and initiatives).

## Recipient and trigger

- A person planning a route, a contributor and a moderator, as `PRODUCT.md` describes them, on a phone; and the Kraków jury at the demo. The trigger is opening the link of the demo, and then every action in a view.
- The service of the project: the frontend is a client of the sixteen operations of `docs/product/api_contract.md` and of nothing else.
- The owners are Kuber and Adrian (`MVP.md`, `TEAM.md`). This shape was written with Adrian, who builds the whole web frontend (Domain rules).

## Current state

- There is no `frontend/` directory and no frontend code on any branch (`git ls-tree` of every remote branch on 2026-10-04, `dev` at `193471b`).
- The stack is decided: TypeScript with React, built by Vite, the map drawn by MapLibre GL JS from one archive of vector tiles (`MVP.md` D-6; `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`). `docs/standards/standard_frontend.md` names four gates, none of them set up yet.
- The contract is `docs/product/api_contract.md`, approved in place of the frontend persons, whose confirmation `MVP.md` lists as still to be obtained. Adrian confirmed it as the base of the frontend in the conversations of 2026-10-03 and 2026-10-04, with one change asked for, the characters of a pseudonym, and one item deferred, the street name of a fact (`docs/product/views.md`, decisions 11 - 14 and section The views read against the contract of the team). The confirmation of Kuber is not recorded.
- What a person does and sees is written down: `docs/product/user_journeys.md` has fourteen journeys, `docs/product/views.md` fourteen views with their states and seventeen decisions, `docs/product/interface_texts.md` every text in Polish and English, and `.impeccable/briefs/views.md` twenty-eight mocks in `.impeccable/briefs/views/` with the tokens of the look.
- `plans_finished/frontend_app/FRONTEND_APP_PACKAGES.md` is a draft of work packages by Adrian, an input to the plan and not part of it.
- No operation of the service exists yet. `MVP.md` lets this initiative start without waiting and build against the contract; each screen is finished once the operation it calls answers (`MVP.md`, Initiatives and Order and critical path).
- The hosted demo is served over plain HTTP, so a browser gives it no location (`MVP.md`, Known departures from the Kraków brief). Since version 10 of the specification the demo does not show routing that does not answer.
- Four differences between documents meet in the frontend. In each the specification prevails (`MVP.md`, Why this document exists):
  - FR-11 and AC-10 of `plans_finished/mvp/MVP_PRD.md` have the list name the missing attributes of a segment; version 11 of the specification, M8, has one plain note. The frontend shows the note.
  - FR-20 of the same document names a 30-day identifier of a vote without an account; version 9 of the specification keeps it until the demo is deleted. The privacy information follows the specification.
  - The contract accepts every character of a pseudonym that is not a control character; version 11 of the specification, M9, allows letters, digits, the underscore and the hyphen. The frontend states and checks the rule of the specification.
  - The specification, M8, gives an item of a list the name of its street when it has one; the contract has no field for it. The frontend shows no place line until the contract carries the name.

## Smallest meaningful scope

The path of the demo of `docs/product/user_journeys.md` on the operations of the service: the needs with a preset, a route with its list and its segment states, a fact with its source, date and status, a vote, and a report that contradicts OpenStreetMap. The whole scope is built, in this order: the foundation - the shell, the map, the two dictionaries and the client of the contract; the needs; the map of facts with the fact detail and the votes; route planning with the address search; the route result; reporting a point; the privacy information and the page about the data; the account; moderation; reporting an area; and the parts of O9. Decided by Adrian on 2026-10-04: no part is cut ahead and no hour ends the building, and what is dropped is decided when the time runs out. Chosen against the same order with a fixed list of what is dropped first and the building ended at 8:30, and against the order in which the operations of the service arrive, which puts the route result last.

## Out of scope

- Every operation of the service: the backend initiatives of `MVP.md`.
- The tile archive, the style of the base map, the map fonts and sprites and the step of the loading program: `plans_finished/map_tiles/`. This initiative draws the map from what that one provides.
- The sample reports and geozones of the demo district: `plans/sample_data/`. The frontend only marks what the service marks as sample data.
- A demo on sample data kept in the frontend. Adrian decided on 2026-10-04 that the demo runs only on the service (`docs/product/views.md`, decision 16).
- The deployment configuration of the hosted demo: `plans/deployment_config/`.
- The HarmonyOS client, a second client of the same contract (`docs/standards/decision_registry.md`, entry HarmonyOS port and the Huawei submission).
- The optional features O1 - O8.
- A layout tuned for a desktop browser, and any product rule the specification does not have.

## Functional requirements

1. The application exists in `frontend/` as `MVP.md` D-6 decides. The four gates of `docs/standards/standard_frontend.md` are set up and pass, and the pair of documents of the code unit is created with the first screen that applies a display rule of the specification.
2. The application reaches the service only through the operations of `docs/product/api_contract.md`, on the host the page comes from, and talks to no other host.
3. The shell and the menu (`docs/product/views.md`, V-1 and V-10): the header, the bottom bar with Map, Report and Needs, and the menu with the account, the language, the privacy information, the page about the data and, for a moderator, moderation.
4. The needs (V-2), with the three presets, shown on the first opening with a way to skip them (FR-1, AC-1 of `plans_finished/mvp/MVP_PRD.md`).
5. The map of facts (V-3) and the fact detail (V-6): the facts of the needs or all facts, the list as the text form of the map, the source, the date and the status of a fact, the two votes with the own vote of the person, the flag, and the sample data mark (FR-6, FR-7, FR-15, FR-18).
6. Route planning and the address search (V-4, V-8): the start from the current location, an address or a point on the map, the destination from an address or a point, and the plain message when no route can be planned (FR-2, FR-17).
7. The route result and the legend (V-5, V-9): the four segment states told apart without color, the three groups of the list, the note about missing data, the proposed alternative, the route with the fewest barriers and the route without assessed segments (FR-3, FR-4, FR-10, FR-11 as version 11 of the specification changes it, FR-15).
8. Reporting a barrier, an amenity or an area (V-7), with the check for existing facts, the summary and the area created with a keyboard alone (FR-5, FR-8).
9. The account (V-11): creating, logging in, logging out and deleting (FR-12).
10. Moderation (V-14), for an account with the moderator role (FR-14).
11. The privacy information and the page about the data (V-12, V-13), with the date of the copy of the map data (FR-20, FR-9).
12. Every state of every view of `docs/product/views.md` is built, the states without a mock included.
13. The interface is in Polish and English with the texts of `docs/product/interface_texts.md`; it is designed for a phone of 360 px and does not break on a desktop browser; switching the language does not lose a planned route (FR-19).
14. The main scenario - the needs, a route, its list, a report and a vote - works with a keyboard alone and with a screen reader, and the list of what works and what does not, which the brief asks for, is recorded (FR-16, AC-15).
15. Once `plans/public_transport_routing/` has written the interface of O9 into the contract: the switch between a walking route and a route with public transport, the public transport segment and the statement that public transport was unavailable (seed; `docs/product/specification.md`, O9).

## Scenarios: input, flow, expected state after the run

1. First opening. Input: a phone that never opened the app, the browser in Polish. Flow: the needs are shown; the person picks "Chodzę z wózkiem dziecięcym", unticks stairs, confirms and reloads the page. State after: the map of facts in Polish; stairs stay unticked; nothing of the needs was sent to the service (AC-1).
2. A route with an unverified barrier. Input: needs that avoid stairs, a start and a destination in Czyżyny, an unverified report of stairs on the way. Flow: the person plans the route. State after: the segment with the stairs is in the state barrier, the list names the stairs with source, date and status, and one alternative is proposed with the stairs and their status as the reason (AC-3).
3. No route without barriers. Input: needs that avoid stairs, a destination reached only through stairs. State after: the route with the fewest barriers, the plain statement that no route without barriers exists, and the stairs in the list (AC-4).
4. A report next to an existing fact. Input: a report of a high kerb 8 m from an existing one. Flow: the app shows the existing fact and asks whether it is already reported; the person says yes. State after: a confirmation of the existing fact and no new report (AC-5).
5. A vote and a second vote. Input: a fact without a vote of this person. Flow: the person confirms it at 9:12 and opens it again at 15:00. State after: the status of the fact after the vote; at 15:00 the own vote is shown and the two votes are inactive until 9:12 of the next day.
6. The language switch. Input: a planned route in Polish. Flow: the person switches to English. State after: the same route and list in English, without a new request to the service (AC-18).
7. The session ends during a report. Input: a logged in person whose session expired, with an approved summary. Flow: the save is refused with the expired session. State after: the person is told they are logged out, nothing was saved as a report without an account, and the report can be saved again after logging in or without an account.
8. Routing does not answer. Input: a route request the service cannot answer. State after: the plain message and no route (AC-16).
9. The location on the hosted demo. Input: the hosted link over plain HTTP, the start from the current location. State after: the message that the location is not available, and the start can be given by an address or a point on the map.

## Challenging own assumptions

- Is the frontend blocked while the service does not exist? No. `MVP.md` has it build against the contract, and decision 16 of `docs/product/views.md` only keeps sample data of the frontend out of the demo. Until an operation answers, the screen that calls it is built and tested on data in the shapes of the contract kept for tests and for a development run.
- Does every screen of `plans_finished/mvp/MVP_PRD.md` mean the fourteen views? That document names requirements, not screens. The views were derived from the journeys, which cover FR-1 - FR-20, and `MVP.md` maps each requirement to this initiative, so the views are taken as the list of screens.
- Are the views still right after versions 8 - 10 of the specification? Checked at the merge of 2026-10-04: the privacy information and the path of the demo were brought in line, and the views of O9 are missing (requirement 15).
- Is the packages draft a decision? No. Its names of files and its split are proposals for phase B.
- Does the whole scope fit before 11:00? Not verified, and unlikely: on 2026-10-04 the agent estimated eight to nine hours of work for two people, one person builds it, and at the end of this interview, at 2:10, eight hours and fifty minutes were left, with the PRD and the plan still to write. Adrian chose to build everything without a list of cuts, so the order of Smallest meaningful scope is what protects the main scenario: the parts at its end are the ones that fall off.
- Is a rule for two owners decided by one of them? Everything here was decided with Adrian, who builds the whole web frontend. Kuber, the other owner in `MVP.md`, has confirmed neither this shape nor the contract; the answer about his work was given by Adrian and does not replace his own.
- Do the blocking risk categories apply to a frontend? The session token, the stability of the contract, the idempotency key, the time semantics and the moderator view are answered by `docs/product/api_contract.md`: the token and its renewal, the rule that an operation changes in that document first, the key generated once for an approved summary, days and instants computed by the service, and the role checked by the service on every moderator request. No database schema is touched. Personal data is answered in the notes below. Query volume was decided by Adrian in the interview (Domain rules).

## Domain rules or explicit TODO

- The specification, version 12 at the merge of `dev` of 2026-10-04, prevails over every other document. The decisions of `docs/product/views.md`, 1 - 17, of `docs/product/user_journeys.md` and of `docs/product/interface_texts.md` are rules of this initiative.
- The frontend holds no product rule: the segment states, the groups of the list, the status of a fact and every day are shown as received (`docs/standards/standard_frontend.md`).
- The interface never says OpenStreetMap outside the attribution on the map and the page about the data (specification, M10).
- Kept on the device and nowhere else: the needs, the chosen language, the own votes of the person and the session token.
- A shown route is planned again once, when the person comes back to it after changing the needs, and after a vote or a report of the person is saved. Agent decision at C:40, without asking: the needs are edited on a page without the route, so a request for every single change would show nothing.
- The map of facts asks the service for the facts of the visible area when the map has stood still for 0.3 seconds, never while it moves; until the answer comes it keeps showing the facts it had. When the map is zoomed out beyond a part of a district, it does not ask at all and asks the person to zoom in. Decided by Adrian on 2026-10-04, against asking also during the movement, at most every 0.5 seconds, and against asking only when the person presses a button. In the run of the question - three seconds of moving the map, then two steps of zooming in - it gives 3 requests where asking during the movement gives about 8. The zoom level of the limit is for phase B.
- Adrian builds the whole web frontend, and Kuber stays with the HarmonyOS port. Decided by Adrian on 2026-10-04, against two splits of the views between the two of them and against leaving the split open. The parts are therefore built one after another, not in parallel. The answer concerns also the work of Kuber and was given by Adrian alone.
- The name of the product, which the header shows, is EnableMe, the same in both languages. Decided by the team, as Adrian reported on 2026-10-04, in phase B; the mocks show a placeholder.
- TODO: the street name of a fact, deferred by Adrian until the backend is tested (`docs/product/views.md`, decision 13).

## Notes on data, performance and security

- Personal data. The needs travel only inside a route request, which carries no identity of an account; the current location travels only there as well and is kept nowhere; the page loads nothing from another host, so no outside service learns the address of the person or the area they look at (specification, Personal data).
- The session token is kept in the storage of the browser, as the contract says, where a script of the page can read it. The page runs no script from another host, and a description written by a person is shown as plain text, never as markup.
- Query volume. The address search asks the service only when the person submits the text. A route request may take up to 5 seconds (`plans_finished/mvp/MVP_PRD.md`), so the view shows that the route is being planned. The map of facts asks for facts only when the map has stood still, and not at all when it is zoomed out far (Domain rules); an answer holds at most 1000 facts, and the map asks the person to zoom in when the area holds more (`docs/product/api_contract.md`, `list_facts_in_area`).
- Stored data of the device that the application cannot read, after a change of its form during the night, is dropped, and the application starts as on the first opening. Agent decision at C:40, without asking.

## Open questions

None. The three questions of the interview - how often the map of facts asks the service, who builds which part, and the order with what is dropped first - are answered in Domain rules and in Smallest meaningful scope. Two things wait for others and block nothing here: the confirmation of this shape and of the contract by Kuber, and the two differences between the specification and the contract, the characters of a pseudonym and the street name of a fact.
