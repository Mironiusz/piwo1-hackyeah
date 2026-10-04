# FRONTEND

Document state: 2026-10-04

## Module role

The web frontend of EnableMe: a single-page application for a phone screen from 360 px wide, in Polish and English, that shows the facts of an area, plans a walking route for the needs of a person, and lets the person vote, flag and report. It talks only to the service of the project, on the host the page came from, through the operations of `docs/product/api_contract.md`.

## Public interface

The addresses of the views, handled by React Router:

| Path                                                                                                       | View                                            |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `/`                                                                                                        | the map of facts                                |
| `/fact/:factId`                                                                                            | the detail of a fact over the map of facts      |
| `/needs`                                                                                                   | the needs                                       |
| `/route`                                                                                                   | route planning                                  |
| `/route/search/:end`                                                                                       | the address search for `start` or `destination` |
| `/route/pick/:end`                                                                                         | picking the point on the map                    |
| `/route/result`                                                                                            | the route result                                |
| `/route/result/fact/:factId`                                                                               | the detail of a fact over the route             |
| `/report`, then `/report/place`, `/report/details`, `/report/existing`, `/report/summary`, `/report/saved` | the steps of a report                           |
| `/account`, `/privacy`, `/about-data`, `/moderation`                                                       | the pages                                       |
| every other path                                                                                           | a message with the way back to the map          |

The menu is a layer of the shell and has no path. No path carries a text a person typed or a coordinate. The server has to answer every path that is not a file and does not start with `/api/` with the page of the application.

The npm scripts of `frontend/package.json`: `dev`, `build`, `preview`, `typecheck`, `lint`, `test`, `mock`, `map-style` and `map-style:check`.

## Technical inputs and outputs

- Reads and writes the service through the sixteen operations of the contract under `/api`, each as one function of `src/api/client.ts`.
- Reads from the host of the page the style of the base map, `/map/style-pl.json` or `/map/style-en.json`, its fonts under `/map/fonts/`, and the tile archive `/tiles/krakow.pmtiles` in byte ranges (`docs/setup/MAP_SETUP.md`).
- Keeps four values in the local storage of the browser, each under its own key: `enableme.needs.v1`, `enableme.language.v1`, `enableme.session.v1` and `enableme.ownVotes.v1`.
- Reads the location of the device only when the person asks for it, and sends it only as a point of a route request.

## Operating modes

- Development on the mock: `npm run mock` starts `mock-server/server.mjs` on `127.0.0.1:8787`, and `npm run dev` passes `/api` to it. The mock answers by the simple rules written at the top of its file and keeps its state in memory.
- Development on a service: the same development server with the variable `VITE_API_PROXY_TARGET` set to the address of a running backend.
- Build: `npm run build` writes the static files to `dist/`. The build holds no proxy and no file of the mock, so it runs only on the service.

## File structure

```text
frontend/
  index.html
  package.json, package-lock.json
  vite.config.ts, tsconfig*.json, .oxlintrc.json
  FRONTEND.md, FRONTEND_ALGORITHM.md
  mock-server/        server.mjs and data/
  public/map/         the two style files and the fonts of the base map
  public/tiles/       the tile archive, kept out of the repository
  scripts/            the generator of the base map style
  src/
    main.tsx, App.tsx
    api/              the types, the errors and the client of the contract
    format/           days, distances and moments in the form of a language
    hooks/            the hook of a request
    i18n/             the two dictionaries and the setup of i18next
    map/              the map component, its scene, the route layers, the bounds of Kraków
    parts/            the shared parts of the interface
    shell/            the frame of every view and the two layouts
    state/            what lives across views and on the device
    styles/           the theme and the base styles
    testing/          the stand-in of the browser storage for the tests
    views/            one file for each view, their helpers, and report/ for the steps of a report
```

## File responsibilities

- `src/main.tsx` starts i18next with the detected language and renders `App`.
- `src/App.tsx` holds the providers of the state and the table of paths.
- `src/api/types.ts` holds the types of the contract, written by hand from its document. `src/api/errors.ts` holds the one error type and the mapping of a code to a text key. `src/api/client.ts` holds one function for each operation over one request function, which sends the token only where the contract takes one, stores the renewed token and clears an ended session.
- `src/state/storage.ts` reads and writes the four kept values and drops what it cannot read. `needs.tsx` holds the needs and the three presets, `session.tsx` the account of the session, `ownVotes.ts` the own votes, `plannedRoute.tsx` the two ends of a route with the answer of the service, `reportDraft.tsx` the report being written, and `lastMapPath.ts` the map view a person left.
- `src/hooks/useRequest.ts` runs a request for a view and tells loading, ready and failed apart.
- `src/map/MapView.tsx` is the one component that uses MapLibre GL JS: it draws the base map from the archive, the route layers, the areas and the markers, and reports where the map rests. `mapScene.ts` is the contract between a view and the map: a view describes its scene and the layout hands it to the map. `routeLayers.ts` turns a route into its line layers. `loadBaseMapStyle.ts` loads the style of a language and makes its addresses full addresses of the page. `krakowBounds.ts` holds the bounds of the tile archive.
- `src/shell/Shell.tsx` is the frame: the header, the menu, the view and the bottom bar, the first opening and the focus after a change of the address. `MapLayout.tsx` keeps the one map above the panel of a map view, `PageLayout.tsx` frames a page, and `ErrorBoundary.tsx` is the safety net around the views.
- `src/parts/` holds what several views share: the button, the field, the switch, the note, the panel, the status, the source with its day, the sample data mark, the row of a fact, the legend, the summary line of a route and its tiles, the icons, and the class names of the shared text styles.
- `src/views/` holds the views. `factDetail.ts` and `routeText.ts` hold what the map views share: the markers of facts, the names of the ends of a route and the context a map view hands to the detail of a fact. `PageBack.tsx` and `LeadItem.tsx` are parts of the pages, `accountForm.ts` holds the two rules of the account form and the mapping of its refusals to messages, `moderationLists.ts` splits the flagged facts into the two lists, `textParts.ts` cuts a text for its emphasis, and `useFocusRequest.ts` moves the focus after an action removed the focused element.
- `src/views/report/` holds the flow of a report: `ReportFlow.tsx` keeps the draft for its six steps, each step is one component, `ReportStepHead.tsx` and `ReportFactLine.tsx` are the parts the steps share, `reportSteps.ts` holds the order of the steps, the guard that leads an address without its data back, the body of the save and the key of a save, and `reportMap.ts` the markers and the map moves of the flow.
- A file that ends with `.test.ts` holds the unit tests of the file of the same name next to it. `src/testing/memoryStorage.ts` is the stand-in of the storage of the browser those tests share, and `scripts/generate_base_map_style.d.mts` declares the generator of the base map style for its test.
- `mock-server/server.mjs` answers the sixteen operations during development. It is no part of the build.

## Main records and contracts

- `Fact`, `RouteFact`, `Route`, `Segment` and `PlanRouteResponse` of `src/api/types.ts` mirror the contract field for field, in snake case, because the frontend passes the answers on unchanged.
- `ApiError` carries the code of the contract, the refused fields and, for a vote that came too soon, the instant of the next one.
- `MapScene` of `src/map/mapScene.ts` is everything a view puts on the map: the markers, the areas, the route, the picking mode, the sample data badge, a request to move the map and the size of the map.
- `Needs` of `src/state/needs.tsx` is the form the needs are kept in: the barriers to avoid, the amenities needed and whether the first opening happened.

## Architectural decisions

- The state and the requests use React alone: contexts, hooks and one request hook. No answer of the service is checked at run time; the types are trusted, and the error boundary catches what they miss (`plans/frontend_app/FRONTEND_APP_PLAN.md`, D-5 and D-8).
- One map lives in the layout of the map views and stays while the panels change. A view never touches the map library: it describes a scene (D-13).
- The style of the map is put together from the base style and the layers of the view and handed to the map as a whole, which applies only the difference.
- The styles are Tailwind utility classes with the tokens of the mocks as the theme (D-6). The texts are two flat dictionaries read by i18next, with the keys of `docs/product/interface_texts.md` (D-7).
- The worker script of the map library is bundled by Vite and handed to the library by its address, because the library cannot find its worker inside a bundle.
- The temporary mock is a server of its own behind the proxy of the development server, so the client has one implementation and the build cannot contain mock data (D-4).

## Summary

One React application with one map, a thin client of the contract and no product rule of its own. What a person sees is what the service answered, shown so that it reads without color, without the map and without a pointer.

## Relation to FRONTEND_ALGORITHM.md

This document describes the construction of the frontend. Its behavior and the rules it shows answers by are described in `FRONTEND_ALGORITHM.md`.
