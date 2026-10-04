# EnableMe - architecture of the HarmonyOS client

The client is a native OpenHarmony application in ArkTS and ArkUI (Stage model, API 20) in `accessway/`. It is a
second client of the programming interface of the project, `docs/product/api_contract.md` in the root of the
repository, next to the web app; it embeds nothing of the web app. Without a service it runs on bundled sample
data, so every screen can be shown on an emulator alone.

## Layers

| Layer       | Folder                                                                                                                | Depends on                                        |
| ----------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Screens     | `entry/src/main/ets/pages`                                                                                            | components, `AppModel`, `Repository` types        |
| UI parts    | `entry/src/main/ets/components`                                                                                       | theme tokens, model, `TileStore` (map only)       |
| App state   | `data/AppModel.ets`                                                                                                   | `Repository` interface only                       |
| Data access | `data/Repository.ets` (interfaces), `data/LocalRepository.ets`, `data/ApiRepository.ets`                              | domain, API client                                |
| API client  | `data/ApiClient.ets`, `data/ApiTypes.ets`, `data/ApiMapping.ets`, `data/ApiConfig.ets`                                | platform HTTP                                     |
| Map tiles   | `data/Tiles.ets`, `data/Pmtiles.ets`, `data/Inflate.ets`, `data/Mvt.ets`, `data/TileWorker.ets`, `data/TileTypes.ets` | platform HTTP and `taskpool`                      |
| Domain      | `entry/src/main/ets/domain`                                                                                           | model only, no platform APIs, unit-tested on Node |

Screens never call the network or read files. Everything goes through the repository interfaces
(`FactsRepository`, `RoutingRepository`, `GeocodingRepository`, `AccountRepository`, `ModerationRepository`),
whose methods are asynchronous and fail with `RepoError` and a code (`unavailable`, `session_expired`,
`authentication_required`, `vote_too_soon`, `taken`, `invalid_request`, ...). Each code has one plain message
in Polish and English, so a screen shows what went wrong without knowing where the data came from.

## Two implementations of the data layer

`rawfile/config/api.json` chooses the implementation at start:

- `base_url` empty: `LocalRepository` computes everything on the device from `rawfile/data/osm_sample.json` and
  the demo reports of `data/DemoSeed.ets` - the walking network, routes, segment states, statuses from votes,
  accounts and moderation - with the same rules as the service.
- `base_url` set: `ApiRepository` calls the sixteen operations of the contract. Nothing falls back to local data
  when the service is set; an operation the service refuses shows the message of its error code.

`ApiClient` sends JSON with an optional `Authorization: Bearer` token, keeps the renewed token from the
`Session-Token` response header in `api_session_token.txt` in the app sandbox, applies one timeout
(`timeout_ms`, default 15 s) to connecting and reading, and maps the error body `{error: {code}}` and transport
failures to `RepoError`. `ApiMapping` converts the snake_case objects of the contract into the domain types
(`[lon, lat]` lines into points, days into dates, route segments with their state, missing attributes and the
three lists of the route). Two things the contract does not return are kept on the device: the own votes of the
last day (`api_my_votes.json`) and the alternative route of the last plan, so that "Show the alternative" does
not send a second request. The idempotency key of a report is generated once, when the person approves the
summary, and sent unchanged with every retry, so a lost response cannot create a duplicate.

## Map

The base map comes from one PMTiles archive of Kraków, the same archive the web app reads, at the address
`tiles_url`. The client reads it in HTTP byte ranges, with no tile endpoint of its own:

1. `TileStore.init` reads the first 16 KB: the header and the gzip-compressed root directory.
2. For each visible tile it computes the Hilbert tile id, follows a leaf directory when there is one (cached),
   and reads the bytes of the tile with one range request; at most four requests run at once.
3. `TileWorker` runs on a `taskpool` worker thread: `Inflate` unpacks gzip (a DEFLATE decoder written for the
   client, so it also runs in unit tests) and `Mvt` decodes the vector tile, keeps green areas, water, buildings
   from zoom 14 and streets in three ranks with their names, and simplifies the geometry to about one screen
   pixel.
4. Decoded tiles stay in memory (96 tiles); a missing tile is replaced by its parent while it loads.

`MapCanvas` draws on Canvas, because the emulator has no GPU. The base map is drawn once into an offscreen
bitmap 40% larger than the screen on each side; panning and pinching only move and scale that bitmap, and it is
redrawn after leaving the margin, a change of scale by more than 25% or a batch of new tiles. Over it the canvas
draws the route segments with the patterns of the legend, the fact markers, the points A and B and the crosshair
for picking a point. Without `tiles_url`, or when the archive does not answer within 3 s, the map draws the
bundled sample map instead.

## Platform capabilities

- Location: `data/Location.ets` asks for `ohos.permission.APPROXIMATELY_LOCATION` and `ohos.permission.LOCATION`
  at the moment the person presses "My location" and reads one position with `geoLocationManager`; it becomes
  the start of a route or the place of a report and is not stored.
- Network: `@kit.NetworkKit` HTTP for the contract and the byte ranges of the archive
  (`ohos.permission.INTERNET`); `network_config.json` allows plain HTTP, which the hosted demo uses.
- Concurrency: `taskpool` with a `@Concurrent` function for decoding map tiles off the UI thread.
- Accessibility: every map has a text alternative, buttons and rows carry accessibility texts and roles, the
  crosshair moves with the arrow keys, and the list under the map carries the same information as the colors.
- Storage: files in the app sandbox through `@kit.CoreFileKit`; nothing leaves the device except the requests of
  the contract.

## Screens and navigation

`pages/Index.ets` is the shell: navy header with the product name and the menu, a stack of screens driven by
`Nav`, and the bottom bar Map / Report / Needs. The shell is rebuilt after data changes with a keyed `ForEach`,
because the language and the needs change many screens at once; the parts of `components/Ui.ets` take their
values as `@Prop`, so a part also updates inside a screen that is not rebuilt. Screens, following the
artboards V-2 to V-14 of the team mock-ups: needs, map with the fact list, plan and address search, route result
with the diagram, map and three lists, fact with votes, report in five steps with the duplicate check, account,
privacy, data and moderation pages.

## Storage

`LocalRepository` keeps reports, OSM fact votes, local accounts (salted SHA-256 password hashes) and the session
(24 h since last use) in `local_repository.json` in the app sandbox. `AppModel` keeps the language and the needs
in `ui_prefs.json`; needs never leave the device and are not part of an account. `make uninstall` clears all of it.

## Tests and verification

- `make test` runs the unit tests on Node with the TypeScript compiler of the SDK: `Domain.test.ets` (needs,
  statuses from votes, OSM facts, the four segment states, conflicts and duplicates, route plans, labels),
  `ApiMapping.test.ets` (mapping of the contract objects and route responses) and `Tiles.test.ets` (Hilbert ids,
  DEFLATE blocks, the PMTiles header and directory, tile decoding on the sample archive).
- The tile decoder was compared with a reference implementation in Python on 57 tiles of the Kraków archive and
  gave byte-identical output.
- `tools/mock_backend/` is a mock of the host of the project for development: the sixteen operations under `/api`
  with their errors, sessions and rules, and the archive with byte ranges, from one port.
  `tools/mock_backend/contract_check.py` checks a running service against the contract (50 checks).
- The whole flow was run on the Oniro emulator (QEMU) against the mock on 2026-10-04: needs, map, address
  search, route, fact and vote with its daily limit, report, account and moderation.

## Known limits

- The client has run against the mock of the service only; the service of the project was not running yet.
- With `base_url` empty, routes and facts lie on the schematic sample network, which does not match the streets
  of the real Kraków map.
- The emulator has no GPS, so "My location" shows an error message there; the address search and "Point on the
  map" replace it.
