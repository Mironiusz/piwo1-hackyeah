# Design brief: route result

Document state: 2026-10-03, direction chosen by the user and the team, brief waiting for the user's confirmation

Product truth is in `PRODUCT.md` and `docs/product/specification.md`, and this brief does not repeat it. The approved look is in `.impeccable/briefs/route-result/`: `approved.png` (first viewport), `approved-full.png` (the whole screen) and `mock.html` (the same screen as HTML and CSS, with the exact values).

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
- Fidelity: a production-ready screen on sample data taken from the scenarios in `plans/mvp/MVP_SHAPE.md`, without a backend. The technology is decided in `plans/frontend_stack/`; the working choice of the frontend person is React + Vite + TypeScript.
- Not in this pass: choosing the start and the destination, editing the profile, the report flow, accounts and moderation. They inherit this visual world later.
- The result is wrong, even if polished, when it reads as a clone of Google Maps, as a medical or charity app, or as an official form.

## States and ranges

The ranges are assumptions of the agent, not measurements.

- Route length from 0.3 to 5 km. Barriers from the profile from 0 to 8, usually 1 to 3. Additional barriers and amenities from 0 to 10 each. The share of the route without data from none to all of it; in Kraków it is often large.
- States of the screen: the usual result; an unverified or disputed barrier with a proposed alternative route; no route without barriers; the routing service not answering, with a plain message and no guessed route; a stale copy of OpenStreetMap data, with its date; a route that is mostly without data; loading.
- An empty group never reads as accessible. It says that no barriers are known and repeats how much of the route is unknown.
- States of a fact: unverified, confirmed, disputed, outdated, a fact from OpenStreetMap, and an unverified report that contradicts OpenStreetMap.

## Interaction and layout

- Header, top to bottom: the profile as a yellow pill and the action that changes the route; the line diagram in a white panel with the place names under its ends; three tiles with the facts.
- Tiles: barriers from the profile in a yellow frame, the distance without data in a dashed frame, the whole route in a plain frame. The frame repeats the meaning of the number.
- Map: the route in the four states, markers for the barriers and amenities from the profile, the sample data mark, the OpenStreetMap attribution.
- Sheet: it overlaps the bottom of the map and has a handle. It holds the legend and the list in three groups: from the profile, additional barriers, amenities on the route.
- List row: the same fields in the same places - icon, type, distance from the start aligned to the right, place, then the status with its icon and word, the source and the date.
- The proposal of an alternative route stands directly under the barrier that causes it and names the reason.
- Fact detail: source, date of the last confirmation, status, and two equal buttons, "Nadal jest" and "Już nie ma".
- Bottom bar: the route, the primary action "Zgłoś barierę" in yellow, the profile.
- Proposed, not yet confirmed: tapping a stop on the diagram scrolls the list to its row and highlights its marker on the map.
- The screen is designed for a width of 360 to 430 px. On a desktop browser it must not break.

## Constraints and open decisions

- WCAG 2.2 level AA: keyboard, screen reader, contrast. The list is the text alternative for the map, and the four states have to be told apart without color.
- The interface is in Polish and English. The Polish labels in the mock are working copy, not final wording.
- Open: labels on the diagram collide when there are many barriers or when they are close together. Numbered stops were shown as a variant and not chosen. The builder asks the user for the rule instead of inventing one.
- Open: the yellow accent is close to the amber of the partial data state. The line pattern stays the carrier of that state, and the result is checked in grayscale.
- Decided by the user on 2026-10-03: the map shows OpenStreetMap data, with the attribution visible.
- Decided in `plans/frontend_stack/` on 2026-10-03: the browser talks only to the server of the project, so the map tiles and the fonts are served by the project; the frontend is chosen for the browser, and the HarmonyOS port, if built, is a second client of the same programming interface, so this screen holds no product rule the port would need; this screen is built as a work package of `plans/mvp/`.
- Open: the library that renders the map and the way the project serves its map tiles, both decided in phase B of `plan-prd` of `plans/frontend_stack/`. The earlier recommendation of Leaflet rested on the web view of a HarmonyOS client, which no longer constrains the choice. The routing engine is decided in `plans/routing_engine/`.
- Build path: code-led, because no image generation is available. The decision page recorded the value `comp` only because that was the way to show the previews; nothing is recorded in `.impeccable/config.json`. The mock is the reference for composition and values, built by the agent as HTML, not a generated image.

## Decision trail

1. Round 1: five visual worlds on the same screen. The team took the header layout of the line diagram direction and the lower layout of the category standard.
2. Round 2: five palettes and typefaces on that layout. The team took the first one for the typeface and for the whole lower part.
3. Round 3: five headers. The team took the diagram in the header.
4. Round 4: five final variants. The team took the facts in tiles.
