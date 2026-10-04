# PRD: Web frontend of the MVP

Document state: 2026-10-04

## Business goal

By 11:00 on 4 October 2026 a person, and with them the Kraków jury, goes through the main scenario of `docs/product/specification.md` on a phone: sets the needs, plans a walking route in Kraków, reads its barriers and amenities with their source, date and status, reports a barrier and votes on a fact. The web frontend is the only place where the mandatory features M1 - M11 become visible, so the demo, the video and the presentation of the Kraków submission are built on it (`MVP.md`, Goal and deadline).

It serves three judging criteria of the Kraków task directly - usefulness for the chosen group and ease of use, quality and completeness of the prototype, and the reliability, presentation and updates of the data - and it shows the community model that the business and scaling part of the presentation rests on (`plans_finished/mvp/MVP_PRD.md`, Business goal).

## Problem and its consequences

- No frontend exists. Whatever the backend initiatives of `MVP.md` build during the night, nobody can see it or check it without a screen.
- Nineteen of the twenty requirements of `plans_finished/mvp/MVP_PRD.md` name this initiative among those that meet them (`MVP.md`, Requirements and initiatives). Without it their acceptance criteria cannot be checked, and the submission has no prototype to show.
- The behavior of every view is already written down in `docs/product/user_journeys.md`, `docs/product/views.md` and `docs/product/interface_texts.md`, and its look in the mocks of `.impeccable/briefs/views/`. What is missing is the application that carries them.
- The time is short: when the shape was closed, at 2:10 on 4 October 2026, eight hours and fifty minutes were left, and one person builds the whole frontend.

## Scope

- The web application that `MVP.md` D-6 decides, with the automatic gates of `docs/standards/standard_frontend.md` and the pair of documents of the code unit.
- Every view of `docs/product/views.md`, V-1 - V-14, with every state it lists, in Polish and in English, with the texts of `docs/product/interface_texts.md` and the look of the mocks.
- The main scenario usable with a keyboard alone and with a screen reader, and the recorded list of what works and what does not, which the Kraków brief asks for.
- The parts of the optional feature O9 - the switch, the public transport segment and the statement that public transport was unavailable - once its interface is written into `docs/product/api_contract.md`.
- The whole scope is built in one order, with nothing cut ahead: the foundation, which is the shell, the map, the two dictionaries and the client of the contract; the needs; the map of facts with the fact detail and the votes; route planning with the address search; the route result; reporting a point; the privacy information and the page about the data; the account; moderation; reporting an area; the parts of O9. What is dropped is decided when the time runs out (`plans/frontend_app/FRONTEND_APP_SHAPE.md`, Smallest meaningful scope).

## Out of scope

- Every operation of the service. They are built by the backend initiatives of `MVP.md`.
- The tile archive, the style of the base map, the map fonts and sprites and the loading of the archive on the server. They belong to `plans/map_tiles/`; this initiative draws the map from what that one provides.
- The sample reports and geozones of the demo district. They belong to `plans/sample_data/`; the frontend only marks what the service marks as sample data.
- A demo shown on sample data kept in the frontend. Adrian decided on 2026-10-04 that the demo runs only on the service (`docs/product/views.md`, decision 16).
- The deployment of the hosted demo, which belongs to `plans/deployment_config/`.
- The HarmonyOS client, a second client of the same contract, built by Kuber outside this initiative.
- The optional features O1 - O8.
- A layout tuned for a desktop browser.
- Any product rule the specification does not have. A behavior that turns out to be missing goes to Adrian and into the specification first.

## Functional requirements

FR-1. The application and its checks. The web frontend exists as `MVP.md` D-6 decides. The four automatic gates of `docs/standards/standard_frontend.md` are set up and pass, and the pair of documents of the code unit exists from the first screen that applies a display rule of the specification.

FR-2. One host. The application talks only to the service of the project, through the operations of `docs/product/api_contract.md`, on the host the page comes from. The page, its typefaces, the map and every other file come from that host.

FR-3. Shell and menu (V-1, V-10). Every view has the header and the bottom bar with Map, Report and Needs. The menu leads to the account, the language, the privacy information and the page about the data, and for an account with the moderator role to moderation.

FR-4. Needs (V-2). A person marks the barriers to avoid and the amenities needed, starts from one of the three presets, and sees the needs on the first opening with a way to skip them. The needs stay on the device.

FR-5. Map of facts and fact detail (V-3, V-6). The app opens on a map of Kraków with the facts of the needs, with a switch to every fact and a list as the text form of the map. A fact shows its type, source, date, status and the sample data mark, can be confirmed or reported as gone, shows the own vote of the person, and can be flagged where the service allows it.

FR-6. Route planning and address search (V-4, V-8). A person gives the start by the current location, an address or a point on the map, and the destination by an address or a point, and asks for a route. The search shows a list of matches to pick from.

FR-7. Route result and legend (V-5, V-9). The route is shown as a summary line, on the map and as a list in three groups, with the four segment states told apart without color, the note about missing data, the proposed alternative, the route with the fewest barriers when none is free of them, and the route without assessed segments for needs without a barrier.

FR-8. Reporting (V-7). A person reports a barrier, an amenity or an area through one entry: the kind, the place, the details, the check for existing facts of a point report, the summary and the saved report.

FR-9. Account (V-11). A person creates an account, logs in, logs out and deletes the account with one confirmation.

FR-10. Moderation (V-14). An account with the moderator role sees the flagged content, hides it and restores it.

FR-11. Privacy information and the page about the data (V-12, V-13). The app states what it keeps and what it does not, and explains where the facts come from, what the statuses and the segment states mean and from which day the map data are.

FR-12. States and messages. Every state that `docs/product/views.md` lists for a view is built, the states without a mock included, and every message says what happened and what the person can do next.

FR-13. Languages and screens. The interface is in Polish and in English, with the default taken from the browser and a switch in the app. It is designed for a phone and stays usable on a desktop browser.

FR-14. Accessibility of the main scenario. Setting the needs, planning a route, reading the result, reporting a barrier and voting work with a keyboard alone and with a screen reader, every piece of information on the map is also available as text, and the list of what works and what does not is recorded.

FR-15. Requests to the service. The application asks the service only when a person's action needs it: for the facts of the map when the map has stood still, for an address when the person submits the text, and for a route when the person asks for it or comes back to a shown route after a change.

FR-16. Public transport, O9. Once the interface of O9 is in `docs/product/api_contract.md`: a switch between a walking route and a route with public transport, the public transport segment in the route result, and the statement that public transport was unavailable.

## Acceptance criteria

AC-1 (FR-1). The four gates of `docs/standards/standard_frontend.md` pass on the finished application, and the pair of documents of the code unit exists.

AC-2 (FR-2). During the main scenario - the needs, a route, its list, a report and a vote - the browser sends requests to exactly one host.

AC-3 (FR-3). The bottom bar and the menu are reachable from every view. A person without the moderator role sees no entry to moderation; an account with that role sees it.

AC-4 (FR-4). On a phone that never opened the app the needs are shown first and can be skipped. Picking "I walk with a baby stroller" marks stairs, high kerb, poor surface and narrow passage to avoid and elevator, ramp and lowered kerb as needed, and nothing else. After unticking stairs and reloading the page, stairs stay unticked. Needs without any barrier are accepted, with the note that the route will not be assessed (`plans_finished/mvp/MVP_PRD.md`, AC-1).

AC-5 (FR-5). The map of facts shows only the facts of the needs, and after the switch every fact; the list holds the same facts as the map. A fact shows its source, its day as the service gave it, and its status, and a sample fact carries the sample data mark on the map and in the list. After a vote the status is shown together with the own vote, and both votes are inactive; a vote repeated within a day is answered with the message that names the moment of the next vote. An outdated fact is shown with its status and can be confirmed again. A fact from the map data has no flag action (`plans_finished/mvp/MVP_PRD.md`, AC-14 and AC-17).

AC-6 (FR-6). A route can be asked for with each of the three ways to give the start and each of the two ways to give the destination. One match of the search is still shown as a list, and nothing is set until the person picks it. Nothing found and the search not answering give two different messages. A point outside Kraków is refused with its message. When no route can be planned, the plain message is shown and no route (`plans_finished/mvp/MVP_PRD.md`, AC-16). On the hosted demo the start from the current location ends in the message that the location is not available.

AC-7 (FR-7). In a grayscale screenshot the four segment states can be told apart, and the legend names all four. The list has the three groups, and every item shows its type, source, date and status. A route with a stretch without data shows the one note about missing data and names no missing attribute. An unverified barrier of the needs on the route gives one proposed alternative with the barrier and its status as the reason. When no route is free of barriers, the app says so and lists them. Needs without a barrier give a route drawn in the neutral style with the statement that its stretches are not assessed. A barrier outside the needs does not appear on the map (`plans_finished/mvp/MVP_PRD.md`, AC-3, AC-4, AC-9, and AC-10 as version 11 of the specification changes it).

AC-8 (FR-8). A report of a high kerb next to an existing high kerb shows the existing fact and asks whether it is already reported; the answer yes adds a confirmation and saves no report. Nothing is saved before the summary is approved, and a saved report offers no way to change it. A save repeated after its answer was lost leaves one report. An area is created from the first focus to the saved state with a keyboard alone (`plans_finished/mvp/MVP_PRD.md`, AC-5 and AC-7).

AC-9 (FR-9). Creating an account shows the rules of the pseudonym and the password and the statement that a forgotten password cannot be recovered; a taken pseudonym and a broken rule give their messages. A failed login gives one message for both causes. A request refused because the session ended tells the person they are logged out and lets them repeat the action. Deleting the account takes one confirmation and asks for no password. The needs are the same before and after logging in.

AC-10 (FR-10). A flagged report appears in moderation; after it is hidden it is gone from the map of facts; after it is restored it is back. A person without the moderator role who opens the address of moderation sees the message that the view is only for a moderator (`plans_finished/mvp/MVP_PRD.md`, AC-13).

AC-11 (FR-11). The privacy information lists every kept item with its purpose and its retention and the items that are not kept, in both languages, and states that the demo and all its data are deleted on 4 October 2026. The page about the data shows the day of the copy of the map data. The name OpenStreetMap appears only in the attribution on the map and on the page about the data (`plans_finished/mvp/MVP_PRD.md`, AC-19).

AC-12 (FR-12). Every state listed in `docs/product/views.md` can be reached and shows a text of `docs/product/interface_texts.md`. No state leaves an empty area or shows a code of the service in place of a text.

AC-13 (FR-13). With a browser set to English the interface starts in English, with a browser set to Polish in Polish. The switch changes the language without losing a planned route and without a new route request. The main scenario works on a phone screen 360 px wide, and on a desktop browser no element is cut off or overlapping. Every text exists in both languages (`plans_finished/mvp/MVP_PRD.md`, AC-18).

AC-14 (FR-14). The main scenario is completed with a keyboard alone and with a screen reader on a phone, and the texts and the segment styles meet the contrast ratios of WCAG 2.2 level AA. The list of what works and what does not is recorded and names the start from the current location as not working on the hosted link (`plans_finished/mvp/MVP_PRD.md`, AC-15).

AC-15 (FR-15). A person moves the map of facts for three seconds and then zooms in twice: the application asks the service for facts three times, never while the map moves. With the map zoomed out to the whole city it does not ask and asks the person to zoom in. Typing in the search field sends nothing until the text is submitted. Changing five items of the needs and coming back to a shown route sends one route request.

AC-16 (FR-16). With the interface of O9 in the contract, the route form has the switch with walking as the default, a route with public transport shows its public transport segment as the specification says, and a route answered without public transport says that public transport was unavailable. Without that interface no switch is shown.

## Domain rules

- `docs/product/specification.md`, version 12 when this document was written, prevails over every other document. Where `plans_finished/mvp/MVP_PRD.md` differs from it - FR-11 and AC-10 on the missing attributes, FR-20 on the 30 days of the identifier of a vote - the frontend follows the specification.
- The decisions of `docs/product/views.md`, 1 - 17, of `docs/product/user_journeys.md` and of `docs/product/interface_texts.md` are rules of this initiative, and the texts of the interface are the ones of that catalogue.
- The frontend holds no product rule. The segment states, the groups of the list, the status of a fact and every day are shown as the service gives them (`docs/standards/standard_frontend.md`).
- The interface calls OpenStreetMap map data. The name itself stands only in the attribution on the map and on the page about the data (specification, M10).
- The needs, the chosen language, the own votes of the person and the session stay on the device. The own vote of a person is therefore known only on the device it was cast on.
- The map of facts asks for facts when the map has stood still for 0.3 seconds and never while it moves, and it does not ask when the map is zoomed out beyond a part of a district. Decided by Adrian in the shape interview.
- A shown route is planned again once, when the person comes back to it after changing the needs, and after a vote or a report of the person is saved.
- A pseudonym has 3 to 30 characters of letters, digits, the underscore and the hyphen. The frontend states and checks this rule of the specification, although the contract accepts more.
- An item of a list shows the name of its street only when the service gives one. The contract has no such field yet.
- A text written by a person is shown as plain text.
- The demo runs only on the service. Data in the shapes of the contract kept in the frontend serve its tests and its development run and never reach the demo.
- Data kept on the device that the application cannot read after a change of its form is dropped, and the application starts as on the first opening.

## Dependencies and impact on other modules

- `plans/map_tiles/` provides the tile archive, the style of the base map and the map fonts and sprites. Without them the map cannot be drawn. Both initiatives have the same owners, and Adrian holds the files produced on 2026-10-03.
- The operations of the service come from the backend initiatives of `MVP.md`: the address search, the facts with the votes, the flags and moderation, the accounts, the route, the day of the copy of the map data, and the interface of O9. This initiative starts without waiting for them, and a screen is finished only when the operation it calls answers (`MVP.md`, Initiatives).
- `docs/product/api_contract.md` is the contract both sides build against. Two differences with the specification wait for its owners: the characters of a pseudonym and the street name of a fact. A change of an operation is agreed with the frontend first, as that document says.
- `plans/sample_data/` provides the sample reports and geozones the frontend marks.
- `plans/deployment_config/` serves the application on the host of the service. The hosted demo is served without a secure connection, so a browser gives it no location (`MVP.md`, Known departures from the Kraków brief).
- The forbidden characters check of the repository is extended to the files of the frontend, which changes a check that every initiative runs.
- `MVP.md` asks that a change making one of its items untrue updates it in the same change. This initiative updates it when it finishes or drops a part.
- The HarmonyOS client uses the same contract. Nothing this initiative builds is needed by it, and no product rule lives only in the web application.

## Risks and notes

- The time. The agent estimated the whole scope at eight to nine hours of work for two people, one person builds it, and less than nine hours were left when the shape was closed. Adrian chose to build everything without a list of cuts, so the order of the section Scope protects the main scenario and the parts at its end are the ones that fall off. Each part that is not built goes into the list of what does not work.
- The service. The demo runs only on the service, and the route is the last operation in the order of `MVP.md`. A view whose operation does not answer by the deadline cannot be shown, however complete it is.
- The contract is built in parallel and may still change, which changes what was already built on it.
- Kuber, the second owner in `MVP.md`, has confirmed neither the shape nor the contract. The answer that Adrian builds the whole web frontend was given by Adrian alone.
- The accessibility check with a screen reader on a phone needs time at the end that the building may use up.
- The texts of `docs/product/interface_texts.md` are working copy: Adrian decided the rules of the wording and did not approve the texts one by one.
- O9 has no view and no mock. Its parts are built from the specification and from the interface that `plans/public_transport_routing/` writes, if that interface exists in time.
