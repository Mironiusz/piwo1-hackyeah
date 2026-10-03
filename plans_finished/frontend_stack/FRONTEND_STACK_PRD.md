# PRD: Choice of the frontend technology for the MVP and of the standards for frontend code

Document state: 2026-10-03

## Business goal

The frontend is where a person meets the MVP: a phone-first web app in which the whole main scenario has to work with a keyboard and a screen reader (`plans/mvp/MVP_PRD.md` FR-16), in two languages, on a screen 360 px wide. What the frontend is built in decides how cheaply those requirements are met in the hours left, so the choice is made once, early, by the person who builds it.

The initiative delivers that decision together with the rules frontend code is held to. It closes `plans/mvp/MVP_PLAN.md` Q-3, so that the MVP plan can be closed and the frontend work packages can be planned against a named technology and a named standard before the deadline at 11:00 on 4 October 2026. It also tells `plans_finished/demo_environment/` what the hosting has to carry, which that initiative needs on the evening of 3 October 2026.

## Problem and its consequences

Without a recorded decision three other pieces of work stand still: the MVP plan cannot be closed (`plans/mvp/MVP_PLAN.md`, Q-3 and Risks), the choice of the hosting cannot rely on what the frontend needs (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`, Dependencies), and the contract of the programming interface does not know its first consumer (`plans_finished/api_contract/`).

The standards of the repository cover only Python code, and they apply in the strict version, from the first commit (`CLAUDE.md`, section Full compliance with the standards). Frontend code written before a standard exists for it has nothing a review can pass or fail it against, so the first frontend merge request either stalls or goes in unchecked.

A map is the one part of the interface that usually talks to a service outside the project. If the browser loads map tiles or fonts straight from an outside host, that host learns the IP address of the person and, for tiles, the area they look at. `plans_finished/geocoding/` already keeps the typed search text away from outside services for the same reason; a map that gives the same information away would undo it. The live demo would also depend on a public tile service that limits heavy use by IP address, while the whole venue shares a few addresses.

A frontend that keeps product rules or data outside the programming interface would have to be rewritten for the HarmonyOS port, which is a second client of that interface, against the dependency of `plans/mvp/MVP_PRD.md` that the solution must not prevent a second client from using the same data and rules.

A technology that cannot deliver keyboard and screen reader use, four segment states readable without color, two languages with the route kept, and a geozone created with the keyboard alone fails acceptance criteria of the MVP (AC-7, AC-9, AC-15 and AC-18 of `plans/mvp/MVP_PRD.md`) at a point when there is no time left to change it.

## Scope

- The choice of the frontend technology for the MVP, with the rejected variants and the reason for each.
- The choice of how the map is displayed, and of the source and the way in which the project serves its own map tiles of Kraków.
- The rules frontend code is held to: the workflow core standards, one short frontend standard with its row in the standards map, the code unit of frontend code, and the automatic gates the standard names.
- The record of the decision where people look for it: `plans/mvp/MVP_PLAN.md` Q-3, the entry Technology stack and the Python profile of the standards in `docs/standards/decision_registry.md`, and the inputs the decision gives to `plans_finished/demo_environment/` and `plans_finished/api_contract/`.

## Out of scope

- Setting up the frontend project (scaffolding, the map with the attribution, the language switch, the gates running on code) and building the screens of the main scenario. All of it belongs to the implementation of `plans/mvp/`, which receives the decision through Q-3. Decided by the frontend person in the shape interview; the parallel interview recorded the same answer.
- Producing the map tiles of Kraków and putting them on the hosting. This initiative decides their source and the way they are served; the work itself is part of setting up the map, and its executor is named when `plans/mvp/` plans its work packages. Agent decision at C:40, without asking: it follows from the initiative ending with the decision; confirmed by the frontend person at the gate of this PRD on 2026-10-03.
- The contract of the programming interface, including whether it returns texts or codes, which is part of `plans_finished/api_contract/`. This initiative gives it two inputs: two clients from the start, and an interface in two languages.
- Whether the HarmonyOS port is built at all, an open entry in `docs/standards/decision_registry.md`.
- The wording of the privacy information (`plans/mvp/MVP_PRD.md` FR-20), owned by `plans/mvp/`.
- The visual design of the screens. The design direction of the route result screen, shaped by the frontend person on 2026-10-03 (`PRODUCT.md`, `.impeccable/briefs/route-result.md`), is an input the technology has to be able to build, not something this initiative decides.
- A full frontend profile of standards mirroring the Python profile. Decided against by the frontend person in the shape interview.
- The other technical decisions delegated in the same conversation, each with its own initiative: `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans_finished/account_sessions/`.

## Functional requirements

The initiative writes no frontend code, so the requirements say what the decision has to make true of the frontend that `plans/mvp/` builds (FR-1 - FR-8), and what the initiative itself records (FR-9 - FR-11).

FR-1. Keyboard and screen reader. The chosen technology and map display let the whole main scenario - setting the profile, planning a route, reading the result, reporting a barrier, voting - be done with a keyboard alone and with a screen reader on a phone (`plans/mvp/MVP_PRD.md` FR-16). The map never holds the keyboard focus without a way out and is never the only carrier of a piece of information.

FR-2. Geozone with the keyboard alone. A geozone - a point, a radius from a list, a barrier type - can be created from the first focus to the saved state with the keyboard alone (`plans/mvp/MVP_PRD.md` FR-8).

FR-3. Segment states without color. The map display draws the four segment states with a color and a line pattern or icon each, with a legend, so that they can be told apart in grayscale (`plans/mvp/MVP_PRD.md` FR-10).

FR-4. Two languages and the kept route. The interface exists in Polish and in English, takes its default from the browser, and has a switch that changes the language without losing the planned route. It works on a phone screen 360 px wide and stays usable on a desktop browser (`plans/mvp/MVP_PRD.md` FR-19).

FR-5. Profile on the device. The technology keeps the profile only on the device, across reloads, and never sends it anywhere to be stored (`plans/mvp/MVP_PRD.md` FR-1).

FR-6. Only the server of the project. The browser of the person loads the page, its scripts, its fonts, the map tiles and every other file from the server of the project, and makes no request to any other host.

FR-7. Own map of Kraków. The project serves the map tiles of the whole of Kraków itself, from a source whose licence and terms allow it, with the OpenStreetMap attribution visible on the map (`plans/mvp/MVP_PRD.md` FR-9).

FR-8. One programming interface, two clients. Everything the web frontend shows about a route and about facts comes through the programming interface, which a second client can use in the same way. The frontend does not rely on fragments of pages rendered by the server, and holds no product rule that exists only in the web page.

FR-9. What the hosting has to carry. The decision states what the frontend needs from the hosting: whether its files are static or rendered on the server, and how much storage the map tiles take.

FR-10. Standards for frontend code. Frontend code is held to the six workflow core standards as they stand, and to one short frontend standard added to the standards map. The standard names the code unit of frontend code and the automatic gates: a type check, a lint with accessibility rules, tests of logic, and the forbidden characters rule extended to frontend files. The Python profile stays in force for the backend.

FR-11. The record. The decision names the chosen technology, the map display, the source of the map tiles and the way they are served, and each rejected variant with the reason. `plans/mvp/MVP_PLAN.md` Q-3 is closed with a pointer to it, and the entry Technology stack and the Python profile of the standards in `docs/standards/decision_registry.md` says how frontend code is held to the standards.

## Acceptance criteria

AC-1 - AC-7 describe the frontend the decision leads to. They are checked when `plans/mvp/` builds it, and phase B of this initiative shows for each of them why the chosen technology can meet it. AC-8 - AC-10 are checked when this initiative is carried out.

AC-1 (FR-1, FR-2). On a phone with a screen reader, and with a keyboard alone, a user sets a preset, plans a route, reads the result, reports a barrier, votes and creates a geozone without a pointer. The focus enters the map and leaves it with the keyboard, and everything the map shows is also read from the list.

AC-2 (FR-3). A grayscale screenshot of a route that has all four segment states lets each state be told apart, and the legend names all four.

AC-3 (FR-4). With a browser set to English the interface starts in English, with a browser set to Polish in Polish. With a route on the screen, the switch changes the language and the same route stays on the screen. At 360 px width no part of the main scenario is cut off, and on a desktop browser no element is cut off or overlapping.

AC-4 (FR-5). After a preset is picked and one item is changed, reloading the app on the same device shows the same profile, and the profile appears in no request other than the request for a route.

AC-5 (FR-6). From opening the app at the public link to a displayed route, with the map moved to another district, the browser makes requests to exactly one host, the server of the project.

AC-6 (FR-7). With the public OpenStreetMap tile service unreachable from the device, the map shows any district of Kraków, and the OpenStreetMap attribution is visible on it.

AC-7 (FR-8). For the route result, the segment states, the three groups of the list and the source, date and status of every fact are present in the response of the programming interface; none of them is worked out by a rule that exists only in the web page.

AC-8 (FR-9). The decision states static or rendered on the server, and the storage of the map tiles as a number, and `plans_finished/demo_environment/` carries both as an input.

AC-9 (FR-10). The standards map has a row for the frontend standard. The standard names the code unit of frontend code and the four gates, and `docs/standards/standard_documentation.md` records that code unit. Once the gates run on code in `plans/mvp/`, a frontend change with a type error, with a forbidden character or with an image without a text alternative fails a named gate.

AC-10 (FR-11). The decision names the chosen technology, the map display, the source of the map tiles and the way they are served, and at least one rejected variant for each with its reason. `plans/mvp/MVP_PLAN.md` no longer lists Q-3 as open and points to the decision, and the registry entry says how frontend code is held to the standards.

## Domain rules

The rules are those of the section Domain rules or explicit TODO of `plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`. In short, for reading the acceptance criteria:

- Missing information is never shown as accessible, and color is never the only carrier of a segment state.
- Nothing about the author of a report, vote or geozone is shown to other users.
- The programming interface has two clients from the start: the web frontend and the HarmonyOS port, which, if it is built, is a separate client and not an application embedding the web app. The web frontend is chosen for the browser.
- The browser of the person talks only to the server of the project: map tiles, fonts, scripts and every other file come from it.
- Frontend code follows the six workflow core standards and one short frontend standard that names its gates; the gates themselves are set up with the first frontend code in `plans/mvp/`.
- The initiative ends with the decision and the frontend standard; it writes no frontend code.

## Dependencies and impact on other modules

- No product code exists, so nothing in the code is changed indirectly. The decision feeds `plans/mvp/`: it closes `plans/mvp/MVP_PLAN.md` Q-3, and the frontend becomes work packages of that plan, held to FR-1, FR-8, FR-9, FR-10, FR-16 and FR-19 of `plans/mvp/MVP_PRD.md`.
- `plans_finished/demo_environment/` waits for what the hosting has to carry (FR-9). Its plan keeps 22:00 on 3 October 2026 as the deadline for the choice of the hosting only if the frontend is decided earlier that evening, and its open question about the free disk space of the server now also covers the map tiles.
- `plans_finished/api_contract/` gets two inputs: the programming interface has two clients from the start, and the interface exists in two languages, which bears on its open question whether the interface returns texts or codes. The frontend person is consulted there as the first consumer.
- `plans_finished/geocoding/` decided the behavior of the address search that the frontend builds: a search on submission, a list the user always picks from, two distinct messages, and the search text never in the address of the page.
- `plans_finished/osm_data_source/` decides the copy of OpenStreetMap data behind the routes. The base map may come from a copy of another date; whether it needs a date of its own is settled in phase B.
- `docs/standards/`: the standards map gets a row, `standard_documentation.md` gets the code unit of frontend code, and the registry entry Technology stack and the Python profile of the standards is updated. The Python profile is not touched.
- The automatic check of forbidden characters covers only two kinds of files today. Extending it to frontend files changes a check that runs for the whole repository; it is done together with the first frontend code in `plans/mvp/`.
- The design direction of the route result screen (`PRODUCT.md`, `.impeccable/briefs/route-result.md`) is an input: the chosen technology has to be able to build it, including typefaces served by the project.
- The HarmonyOS port, an open entry in `docs/standards/decision_registry.md`, uses the same programming interface as a second client; nothing in this PRD decides whether it is built.

## Risks and notes

- Time: the decision is needed before 22:00 on 3 October 2026 for `plans_finished/demo_environment/`, and it blocks the closing of the MVP plan; every hour it stays open is taken from implementation before 11:00 on 4 October 2026.
- Serving the map tiles from the project is the costly half of FR-6. It needs a source whose licence and terms allow it, storage on a server whose free disk space is not known yet (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` Q-1), and work to produce the tiles. If phase B finds that this cannot be done in the time left, the rule goes back to the frontend person; it is not replaced silently by an outside tile service.
- The external API person, who is consulted about the map tiles, has not been heard yet; phase B consults that person before the source of the tiles is fixed.
- A standard written in a hurry can name a gate the chosen tools cannot carry. Phase B names a gate only after checking that the chosen technology has a tool for it.
- The base map and the data behind the routes may show different states of the same street. `plans/mvp/MVP_PRD.md` FR-9 shows the date of the copy the routes use; a person may still see on the map a path the route does not know, or the other way round.
- Volume, an estimate by the agent from the shape: at most a few dozen people use the public link, and one map view on a phone needs about twenty tiles, so the server answers a few thousand tile requests over the demo, each a read of a stored file.
- The skill the frontend person used for the design direction is a change to how AI tools are used in the repository, and `AI_WORKFLOW.md` has to say so for the Huawei jury. That record is outside this initiative and is named here so that it is not lost.
