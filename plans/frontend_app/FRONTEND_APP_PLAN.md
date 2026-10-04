# Plan: Web frontend of the MVP

Document state: 2026-10-04, plan closed

## Goal

Build the web frontend that `plans/frontend_app/FRONTEND_APP_PRD.md` requires (FR-1 - FR-16, AC-1 - AC-16): the application of `MVP.md` D-6 in `frontend/`, named EnableMe, with its four gates and the pair of documents of the code unit, and every view of `docs/product/views.md` on the operations of `docs/product/api_contract.md`. The plan was stopped by D-1 until `plans/map_tiles/` delivered its files, and was written to the end after that, on 2026-10-04, at C:60.

## Facts

F-1. The tree has a `frontend/` directory with twelve untracked files of `plans/map_tiles/` - nine fonts, two style files and one script - and no project file of an application. | cmd:`git status --short -uall frontend` counted -> `12`; cmd:`ls frontend` -> `node_modules/ public/ scripts/`; cmd:`git ls-files frontend` counted -> `0` | 2026-10-04
F-2. Node.js 22.20.0 and npm 11.21.0 run on the machine of Adrian, and the npm registry answers. | cmd:`node --version` -> `v22.20.0`; cmd:`npm --version` -> `11.21.0`; cmd:`npm ping` -> `PONG 393ms` | 2026-10-04
F-3. The official Vite template for React with TypeScript pins React 19.3, Vite 8.3, TypeScript 6.0 and the linter oxlint, runs the type check before the build and lints with oxlint. | doc:`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` line 14 | 2026-10-04
F-4. The newest releases of the packages this plan adds are MapLibre GL JS 6.12.0, `pmtiles` 4.5.0, React Router 8.4.0, Tailwind CSS 4.3.3 with its Vite plugin 4.3.3, i18next 26.4.2, react-i18next 17.0.15, Vitest 5.0.3, both Barlow typefaces 5.3.0 and the style package 5.7.2. | cmd:`npm view <package> version` for `maplibre-gl`, `pmtiles`, `react-router`, `tailwindcss`, `@tailwindcss/vite`, `i18next`, `react-i18next`, `vitest`, `@fontsource/barlow-semi-condensed`, `@fontsource/barlow-condensed`, `@protomaps/basemaps` -> the versions named | 2026-10-04
F-5. On the server of the demo a reverse proxy serves the files of the frontend build and the tile archive, answering byte ranges, and passes `/api/` to the backend; its configuration is not written yet. | doc:`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` line 74; cmd:`ls plans/deployment_config` -> `DEPLOYMENT_CONFIG_SEED.md` | 2026-10-04
F-6. Every operation of the contract has the path prefix `/api`, the session token travels in the header `Authorization` and comes back renewed in `Session-Token`, four operations take no token, and the contract has sixteen operations. | doc:`docs/product/api_contract.md` line 13, line 27, line 32; cmd:`grep -c "^### [a-z_]*$" docs/product/api_contract.md` -> `16` | 2026-10-04
F-7. A saved report carries an idempotency key the client generates once, and the facts of an area are at most 1000 with the mark `is_truncated`. | doc:`docs/product/api_contract.md` line 313, line 264 | 2026-10-04
F-8. Git ignores `build`, `dist` and `node_modules` at every depth, `frontend/public/tiles/`, and every `.env.*` file. | code:`.gitignore:17`; code:`.gitignore:18`; code:`.gitignore:19`; code:`.gitignore:20`; code:`.gitignore:21` | 2026-10-04
F-9. No recipe of the makefile may hold shell syntax, and its target `check` joins the other targets. | code:`makefile:3`; code:`makefile:66` | 2026-10-04
F-10. The forbidden characters check scans only `.py` and `.md` files, picks them in `fetch_scanned_files`, skips `build`, `dist` and `node_modules`, and checks bold only in `.md` files. | code:`tests/architecture/test_prose_style.py:26`; code:`tests/architecture/test_prose_style.py:169`; code:`tests/architecture/test_prose_style.py:28`; code:`tests/architecture/test_prose_style.py:265` | 2026-10-04
F-11. The frontend standard asks for four gates set up by this initiative, for unit tests of logic outside components, for no line comments and for the reason of every new run time dependency. | doc:`docs/standards/standard_frontend.md` line 85, line 92, line 81, line 71, line 47 | 2026-10-04
F-12. The standards map records as a debt that the four gates do not run until this initiative sets them up. | doc:`docs/standards/README.md` line 125 | 2026-10-04
F-13. The hosted demo is served over plain HTTP, so the start from the current location does not work on the hosted link. | doc:`MVP.md` line 125 | 2026-10-04
F-14. `MVP.md` lets `frontend_app` start without waiting for another initiative and lists the confirmation of the contract by Kuber and Adrian as still to be obtained. | doc:`MVP.md` line 103, line 113 | 2026-10-04
F-15. `plans/map_tiles/` delivered the nine fonts under `frontend/public/map/fonts/`, the styles `frontend/public/map/style-pl.json` and `frontend/public/map/style-en.json`, the generator `frontend/scripts/generate_base_map_style.mjs` and the archive at `frontend/public/tiles/krakow.pmtiles`, and left four of its acceptance criteria to this initiative. | cmd:`node frontend/scripts/generate_base_map_style.mjs --check` -> `Both style files are up to date and keep every rule.`; doc:`plans/map_tiles/MAP_TILES_REVIEW.md` section Acceptance criteria | 2026-10-04
F-16. The addresses in the two style files start with a slash, and whether MapLibre GL JS resolves them against the page was not checked. | doc:`plans/map_tiles/MAP_TILES_PLAN.md` F-19 | 2026-10-04
F-17. The tokens of the mocks stand in lines 2 to 6 of their stylesheet: seven base colors, four colors of actions that repeat two of them, five colors of segment states and statuses, four colors of the drawn map, two typefaces and two radii. | code:`.impeccable/briefs/views/app.css:2`; code:`.impeccable/briefs/views/app.css:3`; code:`.impeccable/briefs/views/app.css:4`; code:`.impeccable/briefs/views/app.css:5`; code:`.impeccable/briefs/views/app.css:6` | 2026-10-04
F-18. The catalogue of texts writes a placeholder in single braces, gives Polish three plural forms and English two, and names the product EnableMe. | doc:`docs/product/interface_texts.md` line 27, line 28, line 90 | 2026-10-04
F-19. The views carry the decisions this plan builds on: every state without a mock is built, the street name is deferred, the own vote is kept on the device, the demo runs only on the service, and the navigation uses React Router. | doc:`docs/product/views.md` line 457, line 460, line 461, line 463, line 464 | 2026-10-04
F-20. The HarmonyOS client of Kuber gives the local moderator role to an account named `moderator`. | doc:`docs/setup/EMULATOR_SETUP.md` line 187 | 2026-10-04

## Decisions

D-1. This plan waited for `plans/map_tiles/`. Adrian decided on 2026-10-04, in phase B, that the chain of that initiative runs first, and narrowed it in its shape interview: this plan waits for the archive, the style and the fonts, not for the step of the loading program, and until what the frontend needs from a server exists it works on a temporary mock. Chosen against this plan fixing the addresses of the map files itself and against the style moving into this plan. The files were delivered on 2026-10-04 (F-15), and the plan was resumed.

D-2. The product is called EnableMe, the same in both languages. Decided by the team, as Adrian reported on 2026-10-04, after the agent proposed ten Polish and ten English names. The header shows the text `app.name` of `docs/product/interface_texts.md`.

D-3. The addresses of the views are paths, handled by React Router. Decided by Adrian on 2026-10-04, against addresses after a hash sign, which need nothing from the server. The server of the demo therefore has to answer every path that is not a file and does not start with `/api/` with the page of the application; this is a requirement for `plans/deployment_config/` (F-5). The table of paths:

| Path                                                                                                       | View                                                 |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `/`                                                                                                        | V-3, the map of facts                                |
| `/fact/:factId`                                                                                            | V-6, the fact detail over the map of facts           |
| `/needs`                                                                                                   | V-2, the needs                                       |
| `/route`                                                                                                   | V-4, route planning                                  |
| `/route/search/:end`                                                                                       | V-8, the address search for `start` or `destination` |
| `/route/pick/:end`                                                                                         | V-4, picking the point on the map                    |
| `/route/result`                                                                                            | V-5, the route result                                |
| `/route/result/fact/:factId`                                                                               | V-6, the fact detail over the route                  |
| `/report`, then `/report/place`, `/report/details`, `/report/existing`, `/report/summary`, `/report/saved` | V-7, one path for each step                          |
| `/account`                                                                                                 | V-11                                                 |
| `/privacy`                                                                                                 | V-12                                                 |
| `/about-data`                                                                                              | V-13                                                 |
| `/moderation`                                                                                              | V-14                                                 |
| every other path                                                                                           | a message with the way back to the map               |

The menu, V-10, is a layer of the shell and has no path. No path carries a text a person typed or a coordinate (`docs/product/views.md`, V-8).

D-4. The temporary mock is a small local server. Decided by Adrian on 2026-10-04, against a second implementation of the client over data kept in the frontend and against a mock of the network inside the browser. `frontend/mock-server/server.mjs` is a Node.js program without a dependency that answers the sixteen operations of the contract under `/api` on `127.0.0.1:8787`, from the files of `frontend/mock-server/data/` and from a state kept in its memory. The development server passes `/api` to the address in the variable `VITE_API_PROXY_TARGET`, by default the mock; pointing it at a backend on the same machine is the switch Adrian named. The build of the application has no proxy and no file of the mock, so the demo runs only on the service (`docs/product/views.md`, decision 16). What the mock answers:

- `plan_route`: a destination within 300 m of the sample place "Ogród Doświadczeń" gives the usual route with one alternative; within 300 m of "Park Lotników" a route with `barrier_free_route_exists` false; a start or a destination within 300 m of "Rondo Mogilskie" the error `routing_unavailable`; every other pair the usual route.
- `search_address`: the matches of `data/addresses.json` whose label contains the text, an empty list for a text that matches none, and `address_search_unavailable` for the text `unavailable`.
- The facts: the sample facts of `data/facts.json`, each with `is_sample` true; `cast_vote` answers a second vote of the same client on a fact within a day with `vote_too_soon`; `create_fact` adds an unverified fact and answers a repeated key with the first one.
- The accounts: kept in memory; an account named `moderator` has the moderator role (F-20); the token `expired` is answered with `session_expired`.
- The mock applies no rule of the specification beyond what a screen needs to be drawn, and its statuses after a vote are not those of the product.

D-5. The state of the page and the requests are kept with React alone: contexts, hooks and one small hook for a request. Decided by Adrian on 2026-10-04, against TanStack Query and against Zustand.

D-6. The styles are written with Tailwind CSS 4, through its Vite plugin. Decided by Adrian on 2026-10-04, against the stylesheet of the mocks taken over as it is and against style modules for each component. The tokens of the mocks (F-17) become the theme in `frontend/src/styles/index.css`, and the classes of the mocks are rewritten as utility classes inside the components. Tailwind works at build time and adds nothing the browser loads from another host.

D-7. The two languages are handled by i18next with react-i18next. Decided by Adrian on 2026-10-04, against a module of the frontend and against react-intl. The texts stay in `frontend/src/i18n/pl.ts` and `frontend/src/i18n/en.ts`, with the keys of `docs/product/interface_texts.md`. A placeholder keeps the single braces of the catalogue, set as the prefix and the suffix of the interpolation; a text with a number takes the value `count` and has the forms `_one`, `_few`, `_many` and `_other` in Polish and `_one` and `_other` in English. The language of the first opening is read from the settings of the browser by the frontend itself, without a detector package.

D-8. The frontend trusts the types written from the contract and checks no answer at run time. Decided by Adrian on 2026-10-04, against schemas for every answer and against hand-written checks of chosen fields. The safety net is one error boundary around the views and one error type for every failed request: an answer the code cannot use ends in the text `state.failed` instead of an empty page.

D-9. Run time dependencies and their reasons, as `docs/standards/standard_frontend.md` asks (F-11): `react-router`, for the addresses of the views and the back button of the browser (D-3); `i18next` and `react-i18next`, for the texts in two languages with their plural forms (D-7); `maplibre-gl` and `pmtiles`, decided in `plans_finished/frontend_stack/`; the two Barlow typefaces, decided there as well. `tailwindcss`, `@tailwindcss/vite`, `vitest` and `@protomaps/basemaps` are development dependencies. Each release is the one of F-4, and TypeScript stays on the 6.0 of the template.

D-10. The project is created from the official Vite template in a directory outside the repository and copied into `frontend/`, because the template refuses a directory that is not empty and `frontend/` holds the files of F-15. Nothing under `frontend/public/map/`, `frontend/public/tiles/` and `frontend/scripts/` is replaced. Agent decision at C:60, without asking: it is the one way to keep both the template of `MVP.md` D-6 and the files already delivered.

D-11. The gates. `frontend/package.json` gets the scripts `typecheck` (`tsc -b`), `lint` (`oxlint`), `test` (`vitest run`), `mock`, `map-style` and `map-style:check`. The makefile gets the targets `frontend-typecheck`, `frontend-lint`, `frontend-test`, `frontend-format-check` and `frontend-check`, each calling `npm --prefix frontend run` or `npx --no-install prettier`, which is no shell syntax (F-9), and `check` gets `frontend-check`. `tests/architecture/test_prose_style.py` scans, under `frontend/` only, also the files `.ts`, `.tsx`, `.css`, `.html` and `.json`. Agent decision at C:60, without asking: it is what the standard prescribes (F-11), and the names of the targets follow the ones the makefile has.

D-12. What the device keeps, each under its own key of the local storage of the browser, read through one module that drops a value it cannot read:

| Key                    | Value                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| `enableme.needs.v1`    | `{ "avoid": [fact types], "need": [fact types], "isSeen": true or false }`                        |
| `enableme.language.v1` | `"pl"` or `"en"`                                                                                  |
| `enableme.session.v1`  | the session token, a text                                                                         |
| `enableme.ownVotes.v1` | `{ "<fact id>": { "verdict": "confirm" or "deny", "votedOn": day, "repeatAllowedAt": instant } }` |

Agent decision at C:60, without asking: the contract fixes the token in the storage of the browser (F-6), and the three other values are the ones the specification keeps on the device.

D-13. The map. One `MapView` lives in the layout of the map views and stays while the panels over it change. It loads the style file of the current language, turns its two addresses into full addresses of the page before it hands the style to MapLibre GL JS, which makes the assumption of F-16 irrelevant, and loads the other style when the language changes. The attribution control is always open. The markers are buttons with a text name. A route is drawn by one line layer for each segment state with its own dash pattern, and by one neutral layer when the needs have no barrier. The map of facts asks for facts 0.3 seconds after the map stops and not below zoom 14. Agent decision at C:60, without asking, for the zoom level: at zoom 14 a phone screen shows about a part of a district, which is the limit Adrian set in the shape interview.

D-14. A route for needs without a barrier is drawn in the neutral style whatever state its segments carry, and the view says that the stretches are not assessed. The contract has no field for it, so the view decides it from the needs it sent. Agent decision at C:60, without asking: it is M7 of the specification, version 11, applied to the request of the frontend itself.

D-15. A point outside Kraków is found by the frontend before the request, against the bounds of the tile archive, longitude 19.7922355 to 20.2173455 and latitude 49.9676668 to 50.1261338, and a route request refused with `invalid_request` for `start` or `destination` gets the same text. The rule of a pseudonym of the specification is stated and checked in the form before the request. A list row shows a place line only when a fact carries a street name, which no answer does yet. Agent decision at C:60, without asking: each follows from a decision of `docs/product/views.md` (12, 13) and from its section on the contract.

D-16. Tests. Logic outside components has unit tests run by Vitest in Node.js, without a browser and without the network: the formats, the i18next setup with the plural forms, the client of the contract against a stand-in of `fetch`, the mapping of error codes to texts, the storage module, the needs, the own votes, the bounds of Kraków, the layers of a route and the rules of the style generator, which the review of `plans/map_tiles/` left to this initiative. Components have no tests of their own. Agent decision at C:60, without asking: it is the scope the standard names (F-11).

D-17. The pair of documents of the code unit, `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md`, is created with the route result, the first screen that applies the display rules of M7, M8 and M10. The list of what works and what does not is `docs/product/accessibility_status.md`. Agent decision at C:60, without asking: the first follows `docs/standards/standard_frontend.md`, and the second stands next to the documents it reports on.

D-18. The order is the one of the PRD, and nothing is cut ahead: the foundation, then steps 2 to 11 of Scope of changes. When the time runs out, Adrian decides what is dropped, and every part that was not built is written into `docs/product/accessibility_status.md` as not working.

## Scope of changes

Every file is new unless the step says otherwise. Every component file exports one component of the same name. No file has a line comment.

1. The foundation.

   1.1. The project. Create the Vite template `react-ts` with `npm create vite@9.2.1` in a directory outside the repository and copy its files into `frontend/` (D-10): `package.json`, `index.html`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `src/main.tsx`, `src/App.tsx`, `src/vite-env.d.ts`. The sample styles, images and the icon of the template are not copied. In `frontend/package.json`: the name `enableme-frontend`; the dependencies and the development dependencies of D-9; the scripts of D-11 next to `dev`, `build` and `preview` of the template. `frontend/package-lock.json` is written by `npm install`. `frontend/index.html` gets the title EnableMe and the language `pl`, which the application replaces at start.

   1.2. `frontend/vite.config.ts`: the plugins of React and of Tailwind; `server.proxy` passing `/api` to `VITE_API_PROXY_TARGET`, by default `http://127.0.0.1:8787`; the `test` section of Vitest with the environment `node` and the files `src/**/*.test.ts` and `scripts/**/*.test.ts`.

   1.3. The gates (D-11): `frontend/.oxlintrc.json` with the plugins `react`, `jsx-a11y` and `typescript` and every rule of `jsx-a11y` as an error. In `makefile`: the five targets, `frontend-format-check` as `npx --no-install prettier --check "frontend/**/*.{ts,tsx,css,html,json,mjs}"`, the same pattern with `--write` added to `format`, the new names in `.PHONY`, `frontend-format-check` added to `lint` and `frontend-check` to `check`. In `tests/architecture/test_prose_style.py`: the constants `FRONTEND_DIRECTORY_NAME = "frontend"` and `FRONTEND_SCANNED_FILE_SUFFIXES` with the five suffixes; `fetch_scanned_files` also returns a file under `root / FRONTEND_DIRECTORY_NAME` whose suffix is one of them; its documentation comment says so; a new test `test_fetch_scanned_files_finds_frontend_files_only_under_frontend` checks a `.ts` file under `frontend/src`, the same file outside `frontend/`, and files under `frontend/node_modules` and `frontend/dist`.

   1.4. `frontend/src/styles/index.css`: the import of Tailwind, the theme with the tokens of F-17 as the colors `shell`, `yellow`, `bg`, `surface`, `ink`, `muted`, `line`, `clear`, `barrier`, `partial`, `nodata` and `disputed`, the fonts `ui` and `num` and the radii `control` and `panel`; the imports of the weights 400, 500, 600 and 700 of Barlow Semi Condensed and 600 and 700 of Barlow Condensed from their packages; the import of the stylesheet of MapLibre GL JS.

   1.5. The texts. `frontend/src/i18n/pl.ts` and `frontend/src/i18n/en.ts` export the dictionary of one language with every key of `docs/product/interface_texts.md`. `frontend/src/i18n/index.ts` exports `detectLanguage()`, which returns the stored language or else `"pl"` when the first language of the browser starts with `pl` and `"en"` otherwise; `initI18n(language)`, which sets i18next up as D-7 says; and `changeLanguage(language)`, which switches, stores the choice and sets the language of the page. `frontend/src/format/format.ts` exports `formatDay(day, language)`, `formatDistance(metres, language)` and `formatMoment(instant, language)` with the formats of the catalogue; it converts no time zone and takes the hour from the text of the instant.

   1.6. The client of the contract. `frontend/src/api/types.ts` exports the types of `docs/product/api_contract.md`: `FactType`, `FactStatus`, `FactSource`, `Point`, `Fact`, `RouteFact`, `SegmentState`, `Segment`, `Route`, `RouteAlternative`, `PlanRouteRequest`, `PlanRouteResponse`, `AddressMatch`, `Account`, `FlaggedFact`, `Verdict` and `ApiErrorCode`. `frontend/src/api/errors.ts` exports the class `ApiError` with `code`, `fields` and `repeatAllowedAt`, and `errorTextKey(code)`, which returns the key of the text for a code and `state.failed` for a code without one. `frontend/src/api/client.ts` exports one function for each operation - `planRoute`, `searchAddress`, `readOsmCopy`, `listFactsInArea`, `readFact`, `findNearbyFacts`, `createFact`, `castVote`, `flagFact`, `createAccount`, `logIn`, `readOwnAccount`, `deleteOwnAccount`, `listFlaggedFacts`, `hideFact`, `restoreFact` - over one private `request`, which calls the origin of the page under `/api`, sends the token only where the contract takes one, stores the token of `Session-Token`, throws `ApiError`, and on `session_expired` clears the session.

   1.7. The state. `frontend/src/state/storage.ts` exports `readStored(key, isValid)`, `writeStored(key, value)` and `removeStored(key)` for the keys of D-12; a value that is missing, is not JSON or fails `isValid` reads as absent and is removed. `frontend/src/state/needs.tsx` exports `NeedsProvider`, `useNeeds()` and the three presets as the specification lists them. `frontend/src/state/session.tsx` exports `SessionProvider` and `useSession()` with the account, `logIn`, `logOut` and the notice of an ended session. `frontend/src/state/ownVotes.ts` exports `readOwnVote(factId)`, `saveOwnVote(factId, verdict, votedOn, repeatAllowedAt)` and `canVoteNow(factId, now)`. `frontend/src/state/plannedRoute.tsx` exports `PlannedRouteProvider` and `usePlannedRoute()` with the two points, the answer of `planRoute`, which of its routes is shown, and `planAgain()`. `frontend/src/hooks/useRequest.ts` exports `useRequest(run, dependencies)`, which returns the state `loading`, `ready` or `failed`, the data, the error and `retry`.

   1.8. The shell. `frontend/src/main.tsx` starts i18next and renders `App`. `frontend/src/App.tsx` holds the providers and the router with the paths of D-3. `frontend/src/shell/Shell.tsx`, `Header.tsx`, `BottomBar.tsx`, `Menu.tsx`, `MapLayout.tsx`, `PageLayout.tsx`, `ErrorBoundary.tsx` and `NotFound.tsx`: the header with the name and the menu button, the bottom bar with Map, Report and Needs, the menu with the account, the language switch, the privacy information, the page about the data and, for a moderator, moderation; the layout with the map for the paths of the map views and the layout without it for the pages; the error boundary of D-8.

   1.9. The shared parts, each as the system sheet `.impeccable/briefs/views/Main.dc.html` draws it: `frontend/src/parts/Icon.tsx`, `Button.tsx`, `Field.tsx`, `Switch.tsx`, `Note.tsx`, `Panel.tsx`, `StatusMark.tsx`, `SourceDate.tsx`, `SampleMark.tsx`, `FactRow.tsx` and `Legend.tsx`.

   1.10. The map (D-13). `frontend/src/map/krakowBounds.ts` exports `KRAKOW_BOUNDS` and `isInsideKrakow(point)`. `frontend/src/map/loadBaseMapStyle.ts` exports `loadBaseMapStyle(language)`. `frontend/src/map/routeLayers.ts` exports `buildRouteLayers(route, isAssessed)`, the sources and layers of a route. `frontend/src/map/MapView.tsx` takes the markers, the route, the picking mode and the callbacks for a pressed marker and for the map at rest.

   1.11. The mock server (D-4): `frontend/mock-server/server.mjs`, with a handler for each operation, and `frontend/mock-server/data/facts.json`, `routes.json` and `addresses.json`.

   1.12. The tests of D-16: `frontend/src/format/format.test.ts`, `src/i18n/index.test.ts`, `src/api/client.test.ts`, `src/api/errors.test.ts`, `src/state/storage.test.ts`, `src/state/needs.test.ts`, `src/state/ownVotes.test.ts`, `src/map/krakowBounds.test.ts`, `src/map/routeLayers.test.ts` and `scripts/generate_base_map_style.test.ts`.

   Done when the application opens at a width of 360 px with the shell, the map of Kraków drawn from the archive and both languages, every request goes to the origin of the page, and the four gates pass. The four criteria of `plans/map_tiles/` are checked here (step 13).

2. The needs: `frontend/src/views/NeedsView.tsx` at `/needs`. The first opening leads here, with the way to skip; a preset sets the items and does not stay chosen; no barrier marked shows its note. Mock: `Needs`.

3. The map of facts and the fact detail: `frontend/src/views/FactsMapView.tsx` at `/` and `frontend/src/views/FactDetailPanel.tsx` at `/fact/:factId`. Operations: `listFactsInArea`, `readFact`, `castVote`, `flagFact`, `readOsmCopy`. States beyond the mocks: no fact in the area; more facts than an answer holds; the map zoomed out too far; needs without any item, with the switch inactive; an outdated fact with its status, its muted marker and both votes; a fact that is gone; a vote refused as too soon; no flag action for a fact that cannot be flagged. Mocks: `MapFacts`, `FactDetail`, `FactVoted`, `FactContradiction`.

4. Route planning and the address search: `frontend/src/views/RoutePlanningView.tsx` at `/route`, `AddressSearchView.tsx` at `/route/search/:end` and `PointPickView.tsx` at `/route/pick/:end`. Operations: `searchAddress`, `planRoute`. States beyond the mocks: the search not answering; the text refused; a point outside Kraków (D-15); the location refused or not found; the route being planned. Mocks: `RoutePlanning`, `RouteSearch`, `RouteSearchNone`, `RouteUnavailable`.

5. The route result: `frontend/src/views/RouteResultView.tsx` at `/route/result`, with `frontend/src/parts/RouteSummaryLine.tsx` and `RouteTiles.tsx`, and the fact detail at `/route/result/fact/:factId`. It shows the summary line with its text description, the three tiles, the route on the map, the legend, the note about missing data, the three groups, the proposed alternative with the way back, the route with the fewest barriers and the neutral route (D-14). The route is planned again once after the needs change and after a vote or a report is saved. This step creates `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md` (D-17). Mocks: `RouteResult`, `RouteNeutral`, `RouteNoRoute`.

6. Reporting a point: `frontend/src/views/report/ReportFlow.tsx` with `ReportKindStep.tsx`, `ReportPlaceStep.tsx`, `ReportDetailsStep.tsx`, `ReportExistingStep.tsx`, `ReportSummaryStep.tsx` and `ReportSavedStep.tsx`, and `frontend/src/state/reportDraft.tsx` exporting `ReportDraftProvider` and `useReportDraft()`. Operations: `findNearbyFacts`, `castVote` for the answer that it is the same fact, `createFact` with a key from `crypto.randomUUID()` made when the summary is approved and kept until the save succeeds. States beyond the mocks: no existing fact, which skips that step; a save that failed and is tried again. Mocks: `ReportKind`, `ReportPoint`, `ReportDetails`, `ReportExisting`, `ReportSummary`, `ReportSaved`.

7. The privacy information and the page about the data: `frontend/src/views/PrivacyView.tsx` at `/privacy` and `frontend/src/views/AboutDataView.tsx` at `/about-data`, the second with `readOsmCopy`. Mocks: `Privacy`, `AboutData`.

8. The account: `frontend/src/views/AccountView.tsx` at `/account`: logging in, creating an account followed by `logIn`, the logged in state, logging out, and deleting with one confirmation. Operations: `createAccount`, `logIn`, `readOwnAccount`, `deleteOwnAccount`. States beyond the mocks: the session that ended; the account deleted. Mocks: `AccountLogin`, `AccountCreate`, `AccountIn`, `AccountDelete`.

9. Moderation: `frontend/src/views/ModerationView.tsx` at `/moderation`. Operations: `listFlaggedFacts`, `hideFact`, `restoreFact`. States beyond the mock: nothing flagged; the view denied for an account without the role. Mock: `Moderation`.

10. Reporting an area: in the files of step 6, the kind area with its four steps, the radius from the list, the barrier type, the optional description and the summary of an area; the point also given by the address search. Mock: `AreaDetails`.

11. O9. When this step is reached and `docs/product/api_contract.md` holds the interface of O9: the switch in `RoutePlanningView.tsx`, the public transport segment in `routeLayers.ts` and in `RouteSummaryLine.tsx`, and the statement of `RouteResultView.tsx`, with their texts added to both dictionaries and to `docs/product/interface_texts.md`. When the contract does not hold it, the step is skipped and recorded in the review.

12. The service. Start the development server with `VITE_API_PROXY_TARGET` at a running backend and go through every operation that answers; a difference between the contract and an answer is reported to the backend persons and written into the review, and the types change only after the contract does.

13. The checks and the documents.
    - The acceptance criteria of `plans/map_tiles/` that waited for a drawn map are checked and written into `plans/map_tiles/MAP_TILES_REVIEW.md`: its AC-2, the half of its AC-3 about the requests of the browser, its AC-5 and the half of its AC-6 about the working map.
    - `docs/product/accessibility_status.md`: what works and what does not, with the start from the current location named as not working on the hosted link (F-13), and every part of this plan that was not built.
    - `docs/standards/standard_frontend.md`: in the section Technology a paragraph on React Router, i18next and Tailwind CSS with their reasons (D-9) and on the mock server (D-4); in the section Gates the sentence that the gates are set up by this initiative becomes the names of the targets of D-11.
    - `docs/standards/README.md`: the debt of F-12 is removed.
    - `MVP.md`, Open decisions and confirmations: a new item that the addresses of the views are paths, so the server of the demo answers every path that is not a file and does not start with `/api/` with the page of the application (D-3).
    - `agent_docs/memory/frontend/_shared.md`: the entry of this task, as `plan-implement` writes it.

## Rollout order

1. Step 1 of Scope of changes, in the order of its parts, then the gates and the check of the four criteria of `plans/map_tiles/` from step 13.
2. Steps 2 to 10, one after another. After each step the four gates pass and the view is opened in a browser at a width of 360 px on the mock server, in both languages.
3. Step 11, only under its condition.
4. Step 12, for every operation the service answers at that moment; it is repeated when the service gains an operation.
5. Step 13.

Steps for a human: the commit, the push and the pull request, after the foundation and then after every step; telling the owner of `plans/deployment_config/` the requirement of D-3 and the addresses `/tiles/krakow.pmtiles` and `/map/`; the check of the main scenario with a screen reader on a phone, which AC-14 asks for and no tool of the agent can do; the confirmation of the contract by Kuber (F-14).

## Definition of Done

- `make frontend-check`, or its three `npm --prefix frontend run` commands where `make` is missing, passes: the type check, the lint and the tests (AC-1).
- `python -m pytest tests/architecture` passes with the extended prose test, and `npx --no-install prettier --check` passes on the frontend files and on every changed markdown file (AC-1).
- `node frontend/scripts/generate_base_map_style.mjs --check` ends with 0.
- `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md` exist (AC-1).
- In the network panel of the browser every request of the main scenario goes to the origin of the page (AC-2).
- Each of AC-3 - AC-13 and AC-15 of the PRD is checked by a run in a browser on the mock server, and again on the service for every operation the service answers, and the result of each is written into the review.
- The main scenario is completed with a keyboard alone in a browser, the contrast of the texts and of the segment styles is computed, the four segment states are told apart in a grayscale screenshot, and `docs/product/accessibility_status.md` is written. The check with a screen reader on a phone is the step of a human (AC-14).
- AC-16 is checked when step 11 was built, and recorded as not built otherwise.
- The four waiting criteria of `plans/map_tiles/` are recorded in its review.

## Risks

- The time. The scope is larger than the hours left, one person builds it, and nothing is cut ahead (D-18). The order protects the main scenario.
- The classes of the mocks are rewritten as Tailwind utilities (D-6). A rewritten view can drift from its mock, so each view is compared with its mock at 360 px.
- The addresses are paths (D-3). Until `plans/deployment_config/` answers unknown paths with the page, a reload or a link to a view other than the map fails on the hosted demo.
- The demo runs only on the service (`docs/product/views.md`, decision 16). A view whose operation does not answer by the deadline cannot be shown.
- The mock server answers by simple rules (D-4). A view that works on it can still fail on the service, which is what step 12 is for.
- The contract may change while the frontend is built, and no answer is checked at run time (D-8), so a difference shows as a wrong screen or as the text `state.failed`.
- i18next reads the plural forms from the value `count`, while the catalogue writes `{n}` (D-7). A text copied without that change shows no number.
- The prose test starts to scan `.json` under `frontend/`, the lock file included. A forbidden character in a file written by a tool would fail the gate of every initiative.
- Kuber has not confirmed the contract or the shape (F-14).

## Open questions

None. The seven questions of phase B - the name of the product, the addresses of the views, the form of the temporary mock, the state and the requests, the styles, the dictionaries and the checking of answers - were answered by Adrian and are recorded in D-2 - D-8.

## Supplementary files

- `plans/frontend_app/FRONTEND_APP_PRD.md`, the contract this plan implements, with `plans/frontend_app/FRONTEND_APP_SHAPE.md` and its seed.
- `plans/frontend_app/FRONTEND_APP_PACKAGES.md`, the draft of work packages by Adrian. Where it differs from this plan - one implementation of the client over data in the frontend, the plain stylesheet, a dictionary module of the frontend - this plan applies.
- `docs/product/specification.md`, `docs/product/user_journeys.md`, `docs/product/views.md`, `docs/product/interface_texts.md` and `docs/product/api_contract.md`.
- `docs/standards/standard_frontend.md` and `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`.
- `.impeccable/briefs/views.md` with the mocks of `.impeccable/briefs/views/`, and `.impeccable/briefs/route-result.md`.
- `plans/map_tiles/MAP_TILES_PLAN.md`, `plans/map_tiles/MAP_TILES_REVIEW.md` and `docs/setup/MAP_SETUP.md`.
- `MVP.md` and `TEAM.md`.
