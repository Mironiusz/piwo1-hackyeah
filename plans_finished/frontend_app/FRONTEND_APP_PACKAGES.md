# Frontend work packages: draft for the plans of the frontend initiatives

Document state: 2026-10-04, draft of Adrian for `plans_finished/frontend_app/` and `plans_finished/map_tiles/`, part of neither plan until Kuber and Adrian take it over

## Why this file exists

`MVP.md` gives the web frontend to two initiatives owned by Kuber and Adrian: `plans_finished/frontend_app/`, the application in `frontend/` with every screen, the four gates and the pair of documents of the code unit, and `plans_finished/map_tiles/`, the tile archive, the map style, the fonts and sprites and the step of the loading program that loads the archive. Both wait for nothing to start, and `frontend_app` builds against `docs/product/api_contract.md`.

This file was written on 2026-10-03 and 2026-10-04, before these initiatives existed, as what the frontend could prepare while the backend architecture was open. It is the input of Adrian to their shapes and plans: the text of the work packages, ready to move into the sections Scope of changes and Rollout order. It rests on D-6, the frontend stack, and D-12, the contract of the programming interface, of `MVP.md`. It is a supplementary file and decides nothing: the names of files below are proposals of the agent, written from the list of views, and the owners of the two plans change them freely.

## Inputs

- `docs/product/specification.md`, the source of truth, with `docs/product/user_journeys.md` for the steps of a person.
- `docs/product/views.md`: the fourteen views with their states, the decisions behind them and the section that reads them against the contract.
- `docs/product/interface_texts.md`: every text of the interface in Polish and English, with the rules of the wording decided on 2026-10-04.
- `docs/product/api_contract.md`: the operations the frontend calls.
- `docs/standards/standard_frontend.md` and `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`, D-1 - D-13: the technology, the gates and the rules of frontend code.
- `.impeccable/briefs/views.md` with the mocks in `.impeccable/briefs/views/`, and `.impeccable/briefs/route-result.md`: the look of every view, with the tokens in `app.css`.
- `MVP.md`: the initiatives, their owners and their order.
- Two sets of files Adrian produced on 2026-10-03 and keeps outside the repository, as D-5 and D-6 of the frontend stack plan ask: the tile archive of Kraków, 34.8 MB, cut from the Protomaps build `20261003`, zoom 0 to 15; and the map fonts and sprites, 776 files of 11.18 MB.

## Rules every package keeps

- The four gates of `docs/standards/standard_frontend.md` pass before a package is done: the type check, the lint, the tests and the forbidden characters check.
- The frontend holds no product rule. It shows the segment states, the groups of the list, the status of a fact and every day as received.
- The frontend reaches the service only through one module, the client of the contract. A view never builds a request on its own.
- Every text comes from the two dictionaries. A view holds no text of its own.
- Every state of a view listed in `docs/product/views.md` is built, the states without a mock included (`docs/product/views.md`, decision 10).
- A view is built to the mock at a width of 360 to 430 px and must not break on a desktop browser.
- No line comments; a documentation comment in the block form where an explanation is needed.

## Package F: foundation

One person builds it first. Every other package starts from it.

Scope:

- `frontend/` created from the official Vite template for React with TypeScript, with its `package.json` and lock file, and the run time packages the frontend stack plan names: MapLibre GL JS, `pmtiles`, the Protomaps style package and the two typefaces of the direction. One more run time package is added, React Router, decided by Adrian on 2026-10-04 (`docs/product/views.md`, decision 17); its reason, the addresses of the views and the back button of the browser, is stated in the merge request.
- The gates: `frontend/.oxlintrc.json` with the rule groups `react`, `jsx-a11y` and `typescript`, the `make` targets of the three gates run from `frontend/`, and the extension of `tests/architecture/test_prose_style.py` to the files `.ts`, `.tsx`, `.css`, `.html` and `.json` under `frontend/`.
- `frontend/src/styles/tokens.css`: the tokens of `.impeccable/briefs/views/app.css`, and the styles of the shared parts taken over from the same file.
- `frontend/src/i18n/pl.ts`, `frontend/src/i18n/en.ts` and `frontend/src/i18n/index.ts`: the two dictionaries of `docs/product/interface_texts.md`, the language taken from the settings of the browser, the switch, the choice remembered on the device, and the plural forms of both languages.
- `frontend/src/format/`: the formats of a day, a distance and the day of the next vote.
- `frontend/src/api/types.ts`: the types of the contract, written by hand from `docs/product/api_contract.md` until the backend code exists and its OpenAPI description can generate them.
- `frontend/src/api/client.ts`: one function for each operation of the contract, named after it: `planRoute`, `searchAddress`, `readOsmCopy`, `listFactsInArea`, `readFact`, `findNearbyFacts`, `createFact`, `castVote`, `flagFact`, `createAccount`, `logIn`, `readOwnAccount`, `deleteOwnAccount`, `listFlaggedFacts`, `hideFact`, `restoreFact`.
- `frontend/src/api/http.ts`: the implementation over the service, on the origin of the page with the prefix `/api`, with the session token in the header, the renewed token of every answer and the error codes of the contract turned into one error type.
- `frontend/src/api/fixtures.ts` with `frontend/src/api/fixtures/`: the implementation over sample data of the district of the Tauron Arena, in the shapes of the contract, used only by the tests and by a development run before the service exists. Every fact in it is marked as sample data, and it is never part of the build of the demo (`docs/product/views.md`, decision 16).
- `frontend/src/state/session.ts`: the token in the storage of the browser, logging out, and the refusal `session_expired`, which logs the person out with a message.
- `frontend/src/state/needs.ts`: the needs kept on the device, the three presets as actions, the first opening.
- `frontend/src/state/ownVotes.ts`: the own vote of a person on a fact and the day from which the next vote is possible, the next calendar day in Europe/Warsaw, kept on the device.
- `frontend/src/shell/`: the header, the bottom bar with Map, Report and Needs, the menu, and the navigation between the views with React Router, through the address of the page, so that the back button of the browser works.
- `frontend/src/parts/`: the shared parts of the system sheet - the list row, the status mark, the source with its date, the sample data mark, the note, the button, the field, the switch, the panel over the map and the legend.
- `frontend/src/map/MapView.tsx` with `style.ts` and `layers.ts`: the one map, the tile archive read through the protocol of `pmtiles`, the style of the Protomaps package with the colors of the direction and the labels in the language of the interface, the attribution always open, the keyboard focus able to leave the map, the markers as buttons and one line layer with its own dash pattern for each segment state.
- The map files served by the development run and by the build - the tile archive, the fonts and the sprites - and the style of the base map belong to `plans_finished/map_tiles/`, which also decides whether the copies of the fonts and sprites are committed or fetched by a script. Proposed here: fetched by a script and never committed.

Tests: the plural forms and the formats, the mapping of error codes to texts, the needs, the own votes and the session.

Done when: the app opens at 360 px with the shell, the map of Kraków drawn from the archive and both languages, every request goes to the origin of the page, and the four gates pass.

## Packages of the first person: the map and the route

Package A1, the map of facts and the fact detail (V-3, V-6, V-9):

- Views: `frontend/src/views/FactsMap.tsx` with the list of the visible area and the switch between the facts of the needs and all facts; `frontend/src/views/FactDetail.tsx` as a panel over the map.
- Operations: `listFactsInArea`, `readFact`, `castVote`, `flagFact`, `readOsmCopy`.
- States beyond the mocks: no fact in the area; more facts than the service returns, with the request to zoom in; the needs without any item, with the switch inactive; an outdated fact, with its status, its muted marker and both votes; a fact that is no longer available; a vote refused because the person already voted on the same day; the flag unavailable for a fact from map data.
- Mocks: `MapFacts`, `FactDetail`, `FactVoted`, `FactContradiction`.

Package A2, route planning and the address search (V-4, V-8):

- Views: `frontend/src/views/RoutePlanning.tsx`, `frontend/src/views/AddressSearch.tsx`, and the mode of the map that picks a point.
- Operations: `searchAddress`, `planRoute`.
- States beyond the mocks: the search unavailable; the text of a search refused; a point outside Kraków, checked against the bounds of the map before the request; the location refused by the browser or not found; the route being planned.
- Mocks: `RoutePlanning`, `RouteSearch`, `RouteSearchNone`, `RouteUnavailable`.

Package A3, the route result (V-5, V-9):

- Views: `frontend/src/views/RouteResult.tsx` with the summary line, the three tiles, the map of the route, the legend, the note about missing data and the list in three groups.
- Operations: `planRoute`, planned again when the needs change and when a vote or a report of the person is saved.
- States beyond the mocks: the alternative shown as the route, with the way back; the route planned again; a group without items.
- This package creates the pair of documents of the code unit, `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md`, because the route result is the first screen that applies the display rules of M7, M8 and M10.
- Mocks: `RouteResult`, `RouteNeutral`, `RouteNoRoute`.

## Packages of the second person: the forms and the pages

Package B1, the needs (V-2):

- Views: `frontend/src/views/Needs.tsx`, shown on the first opening with the way to skip it, and from the bottom bar afterwards.
- No operation: the needs stay on the device.
- States: no barrier marked, with its note; a preset that sets the items and does not stay chosen.
- Mock: `Needs`.

Package B2, reporting (V-7):

- Views: `frontend/src/views/report/` with one file for each step - the kind, the point, the details, the existing facts, the summary, the saved report - and the details of an area.
- Operations: `findNearbyFacts`, `castVote` when the person says it is the same fact, `createFact` with a key generated once, when the person approves the summary, and repeated with every attempt of the same save.
- States beyond the mocks: the summary of an area; a save that failed and is tried again; no existing fact nearby, which skips that step.
- Mocks: `ReportKind`, `ReportPoint`, `ReportDetails`, `ReportExisting`, `ReportSummary`, `ReportSaved`, `AreaDetails`.

Package B3, the menu, the account and the pages (V-10 - V-13):

- Views: `frontend/src/views/Account.tsx` for logging in, creating an account, the logged in state and the confirmation of deleting; `frontend/src/views/Privacy.tsx`; `frontend/src/views/AboutData.tsx`.
- Operations: `createAccount` followed by `logIn`, `logIn`, `readOwnAccount`, `deleteOwnAccount`, `readOsmCopy`.
- States beyond the mocks: the session that ended; the account deleted.
- Mocks: `Menu`, `AccountLogin`, `AccountCreate`, `AccountIn`, `AccountDelete`, `Privacy`, `AboutData`.

Package B4, moderation (V-14):

- Views: `frontend/src/views/Moderation.tsx`, reached from an entry of the menu that only an account with the moderator role sees.
- Operations: `listFlaggedFacts`, `hideFact`, `restoreFact`.
- States beyond the mock: nothing flagged; the view denied for an account without the role.
- Mock: `Moderation`.

## Joint packages

Package J1, the service:

- The build uses `frontend/src/api/http.ts`. Every operation is checked against the running service, and the types are generated from its OpenAPI description, so that a difference between the contract and the code shows in the type check.
- It waits for each operation of the service, built by the backend initiatives of `MVP.md`.

Package J2, the checks before the demo:

- The path of the accessibility check of `docs/product/user_journeys.md`, J-14: the keyboard, a screen reader, the contrast, the four segment states told apart without color, the width of 360 px, and the language switched without losing the route.
- The list of what already works and what still needs work, which the Kraków brief asks for.
- The built files handed to the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`, and the tile archive loaded by the step that `plans_finished/map_tiles/` adds to the loading program of `plans/osm_import/`.

## Order

1. Package F.
2. A1 and B1 in parallel.
3. A2 and B2 in parallel.
4. A3 and B3 in parallel.
5. B4.
6. J1, as far as the service exists, and J2.

The order follows the path of the demo for the Kraków jury (`docs/product/user_journeys.md`, section on the demo): the needs, a route, the facts with their source, date and status, contradictory data, incomplete data, an unavailable source. The account and moderation come last, because the path of the demo does not need them.

## Open points for the owners of the plans

- The demo runs only on the service: on 2026-10-04 Adrian decided against showing the scenario on sample data of the frontend when the service is not ready (`docs/product/views.md`, decision 16). The team has the last word, and the consequence is that the frontend has nothing to show of a route, a fact or a vote until the operations behind them answer.
- The street name of a list row and the narrower rule of a pseudonym, which wait for the owners of the contract (`docs/product/views.md`, decisions 12 and 13).
- The switch, the public transport segment and the statement of the optional feature O9 belong to `plans_finished/frontend_app/` once `plans/public_transport_routing/` has written its interface into the contract (`MVP.md`). No package here, no view and no mock covers them.
