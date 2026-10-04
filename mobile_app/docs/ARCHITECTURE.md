# EnableMe - architecture

## Layers

| Layer | Folder | Depends on |
|---|---|---|
| Screens | `entry/src/main/ets/pages` | components, `AppModel`, `Repository` types |
| UI parts | `entry/src/main/ets/components` | theme tokens, model |
| App state | `data/AppModel.ets` | `Repository` interface only |
| Data access | `data/Repository.ets` (interface), `data/LocalRepository.ets` (on-device implementation) | domain |
| Domain | `entry/src/main/ets/domain` | model only, no platform APIs, unit-tested on Node |

Screens never read the dataset directly. Everything goes through `Repository`, whose methods are asynchronous and fail with `RepoError` and a code (`unavailable`, `outside_area`, `vote_too_soon`, `taken`, ...). Connecting the team API means a second implementation of the interface and switching `AppModel.repo`. The map background (streets, buildings, green areas) is drawn from the bundled dataset in both cases.

## Domain

- `OsmMapping` turns an Overpass response into a walking graph, map areas, places and OSM facts (stairs with step count, kerbs, steep inclines, narrow ways, rough surfaces, ramps, elevators, accessible toilets, benches, handrails).
- `Needs` maps the "I avoid" list to route constraints (kerb above 3 cm, incline above 6 %, width below 0.9 m, rough surface, stairs).
- `EdgeRules` gives each segment one of four states. A segment is "no barriers, full data" only if every attribute relevant to the needs is known. Only confirmed reports block a segment; unverified or disputed reports are shown but the route follows OpenStreetMap until they are confirmed.
- `Routing` runs Dijkstra without blocking segments and falls back to the route with the fewest barriers when no barrier-free route exists.
- `Plan` builds what the result screen shows: segments with geometry and state, facts on the route with their distance from the start, data gaps (including the walk from the chosen point to the network), and alternative routes around unverified barriers from the needs.
- `Facts` and `Trust` build the fact list with one status from votes: confirmed (weight of "still there" reaches 2), disputed (votes both ways), outdated (weight of "gone" exceeds "still there" by 2, then hidden), otherwise unverified. Account votes weigh 1, votes without an account 0.5, one vote per fact per day. A report contradicting OSM within 15 m (high kerb vs lowered kerb) is marked as a conflict.

## Screens and navigation

`pages/Index.ets` is the shell: navy header with the product name and menu, a stack of screens, the bottom bar Mapa / Zgłoś / Potrzeby. The whole shell is rebuilt after data changes (keyed `ForEach`), because language and data live in `AppModel`, not in component state. Screens with a map use one pattern: `MapCanvas` on top and a white sheet with a handle overlapping it.

`MapCanvas` draws everything on Canvas (the emulator has no GPU): background areas, white streets with labels, route segments with the same patterns as the legend, square fact markers, A/B points and a crosshair for picking points (movable by touch or arrow keys).

## Storage

`LocalRepository` keeps reports, OSM fact votes, local accounts (salted SHA-256 password hashes) and the session (24 h since last use) in `local_repository.json` in the app sandbox. `AppModel` keeps the language and needs in `ui_prefs.json`. `make uninstall` clears both.

## Tests

`make test` runs `entry/src/test/Domain.test.ets` on Node with the SDK's TypeScript fork: needs presets, statuses from votes, OSM facts, the four segment states, conflicts and duplicates, route plans (barrier-free, unrated, alternative, no free route) and Polish labels.
