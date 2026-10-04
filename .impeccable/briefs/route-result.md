# Design brief: route result

Document state: 2026-10-03, direction chosen by the user and the team, brought in line with version 11 of the specification, with the list of views and with the decisions taken with the mocks of the views

Product truth is in `PRODUCT.md` and `docs/product/specification.md`, and this brief does not repeat it. What the view shows and which states it has is in `docs/product/views.md`, V-5 for the route result, V-6 for the fact detail and V-9 for the legend. The approved look is in `.impeccable/briefs/route-result/`: `approved.png` (first viewport), `approved-full.png` (the whole screen) and `mock.html` (the same screen as HTML and CSS, with the exact values).

## Job and audience

- Who arrives: a person who uses a wheelchair, walks with a baby stroller or walks with difficulty, and has just asked for a walking route in Kraków.
- Situation: a phone held outdoors or just before leaving, in daylight. There is no turn-by-turn navigation, so the screen is for judging the route, not for being led along it.
- Need: decide on their own whether to take this route.
- Visitor mode: Operate.

## Outcome and proof

- Before any scrolling the person knows three facts: how many barriers from the profile are on the route, how much of the route has no data, and how long the route is. Facts and unknowns stand side by side, without a verdict.
- After that: where each barrier is (diagram, map, list), how far each fact can be trusted (source, date, status), and whether an alternative route exists.
- The proof the screen has to carry: the four segment states, every fact with its source, date and reliability status, missing data shown as missing, sample data marked as sample data.

## Selected direction

Chosen in four rounds on 2026-10-03. The recorded choice of the last round is the option `final-kafelki`.

- Type: Barlow Semi Condensed for interface text, Barlow Condensed 700 for numbers. Both are served by the project, never loaded from an outside host.
- Palette: navy `#12306B` for the header and for actions, yellow `#FFD400` for the profile pill, the count of barriers and the primary action, white surfaces, ink `#111418`, secondary text `#4B5058`, hairlines `#D5D8DC`, page ground `#F4F5F2`.
- State colors: barrier `#C8321E`, no barrier `#1E7A46`, partial data `#E0A100`, no data `#6F7480`. Each state also has its own line pattern.
- Density: compact, close to a timetable. Corner radius 3 px on controls, 6 px on panels, 16 px on the top corners of the sheet.
- Signature move: the route drawn as a line diagram in the header - a straightened line whose segments carry the four states, with a stop for every barrier from the profile and the names of the start and the destination at its ends.
- Sequence: header, map, white sheet with the legend and the list, fact detail, bottom bar.

## Scope and boundaries

- Target: the route result screen, shown after a route is planned.
- In this pass: the route header with the entry to the profile, the map, the legend, the list in three groups, the fact detail with the two votes, the special states listed below, the sample data mark, and a user report that contradicts OpenStreetMap.
- Fidelity: a production-ready screen on sample data taken from the scenarios in `plans/mvp/MVP_SHAPE.md`, without a backend. The technology is decided in `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`: React with TypeScript, built by Vite.
- Not in this pass: choosing the start and the destination, editing the profile, the report flow, accounts and moderation. They inherit this visual world later.
- The result is wrong, even if polished, when it reads as a clone of Google Maps, as a medical or charity app, or as an official form.

## States and ranges

The ranges are assumptions of the agent, not measurements.

- Route length from 0.3 to 5 km. Barriers from the profile from 0 to 8, usually 1 to 3. Additional barriers and amenities from 0 to 10 each. The share of the route without data from none to all of it; in Kraków it is often large.
- States of the screen: the usual result; an unverified or disputed barrier with one proposed alternative route; the alternative shown as the route, with the way back; no route without barriers; the routing service not answering, with a plain message and no guessed route; a route that is mostly without data; a profile without barriers; planning again after the profile changed or a vote or a report of the person was saved; loading.
- Every route has a stretch without data at each end, the straight line between a chosen point and the pedestrian network. The summary line therefore starts and ends in the state no data, and the distance without data is never zero.
- A way that OpenStreetMap marks as not accessible for wheelchairs is partial data where it would be no barrier, and the list says so in a sentence.
- A profile without barriers: no segment has a state. The route is drawn in a neutral style that is none of the four, the view says that the segments are not assessed, and the tile with the barriers of the profile has nothing to count. Its style is a hollow navy line, drawn in the mocks of the views and confirmed by the user on 2026-10-03 (`.impeccable/briefs/views.md`).
- An empty group never reads as accessible. It says that no barriers are known and repeats how much of the route is unknown.
- Statuses a person sees on a route: unverified, confirmed, disputed. An outdated fact does not count for a route or its list; on the map of facts it stays, with the status outdated (`.impeccable/briefs/views.md`). A fact from OpenStreetMap has the same statuses, and a report that contradicts OpenStreetMap below the threshold shows as an unverified report icon.

## Interaction and layout

- Header, top to bottom: the entry to the needs as a yellow pill and the action that changes the route; the line diagram in a white panel with the place names under its ends; three tiles with the facts.
- Tiles: barriers from the profile in a yellow frame, the distance without data in a dashed frame, the whole route in a plain frame. The frame repeats the meaning of the number.
- Map: the route in the four states, markers for the barriers and amenities from the profile, the sample data mark, the OpenStreetMap attribution.
- Sheet: it overlaps the bottom of the map and has a handle. It holds the legend and the list in three groups: from the profile, additional barriers, amenities on the route. One plain note above the list says when some stretches of the route have no data.
- List row: the same fields in the same places - icon, type, distance from the start aligned to the right, place, then the status with its icon and word, the source and the date.
- The proposal of an alternative route stands directly under the barrier that causes it and names the reason.
- Fact detail: a panel over the map with the source, the date - the last OpenStreetMap edit for a fact from OpenStreetMap, the last confirmation for a user fact - the status, the person's own latest vote, and two equal buttons, "Nadal jest" and "Już nie ma", inactive until the next calendar day after the person voted. A report, a geozone and a converted fact also have the flag action.
- Legend: the four states, the kinds of markers, the sample data mark and the date of the copy of the map data.
- Bottom bar: the map, the primary action that starts a report in yellow, the needs. The account, the language, the privacy information, the page about the data and moderation are in a menu in the header (`docs/product/views.md`, V-1 and V-10). The mock still shows the earlier labels of the bar.
- Proposed, not yet confirmed: tapping a stop on the diagram scrolls the list to its row and highlights its marker on the map.
- The screen is designed for a width of 360 to 430 px. On a desktop browser it must not break.

## Constraints and open decisions

- WCAG 2.2 level AA: keyboard, screen reader, contrast. The list is the text alternative for the map, and the four states have to be told apart without color.
- The interface is in Polish and English. The Polish labels in the mock are working copy, not final wording.
- Open: labels on the diagram collide when there are many barriers or when they are close together. Numbered stops were shown as a variant and not chosen. The builder asks the user for the rule instead of inventing one.
- Open: the yellow accent is close to the amber of the partial data state. The line pattern stays the carrier of that state, and the result is checked in grayscale.
- Decided by the user on 2026-10-03: the map shows OpenStreetMap data, with the attribution visible.
- Decided by the user on 2026-10-03 with the mocks of the views: the texts of the interface call OpenStreetMap map data, in the working Polish copy "dane mapy". The name itself stands only in the attribution on the map and once on the page about the data. `mock.html` and the two images of this brief still show the earlier wording; the mocks of `.impeccable/briefs/views/` show the current one.
- Decided by the user on 2026-10-03 with the mocks of the views: the list names no missing attributes. One plain note says that some stretches of the route have no data and that barriers on them are not known.
- Decided in `plans_finished/frontend_stack/` on 2026-10-03: the browser talks only to the server of the project, so the map tiles and the fonts are served by the project; the frontend is chosen for the browser, and the HarmonyOS port, if built, is a second client of the same programming interface, so this screen holds no product rule the port would need; this screen is built as a work package of `plans/mvp/`.
- Decided in `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` on 2026-10-03: the map is drawn by MapLibre GL JS from one archive of vector tiles of Kraków served by the project (D-4, D-5 there). The base map takes its colors from this direction and its labels from the language of the interface (D-6 there). Markers are buttons on the map, and each segment state is a line layer with its own dash pattern (D-8 there). The routing engine is decided in `plans_finished/routing_engine/`.
- Constraint from the same plan: once the gate of forbidden characters covers frontend files, interface texts cannot contain an ellipsis, a middle dot, an arrow, a multiplication sign, a typographic dash or a curly quotation mark, so separators and icons are drawn as graphics. The approved mock already complies.
- Build path: code-led, because no image generation is available. The decision page recorded the value `comp` only because that was the way to show the previews; nothing is recorded in `.impeccable/config.json`. The mock is the reference for composition and values, built by the agent as HTML, not a generated image.

## Decision trail

1. Round 1: five visual worlds on the same screen. The team took the header layout of the line diagram direction and the lower layout of the category standard.
2. Round 2: five palettes and typefaces on that layout. The team took the first one for the typeface and for the whole lower part.
3. Round 3: five headers. The team took the diagram in the header.
4. Round 4: five final variants. The team took the facts in tiles.
