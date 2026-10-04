# EnableMe (AccessWay) - Kraków bez barier (HarmonyOS app)

An app for the "Kraków bez barier" challenge (HackYeah 2026). For now it runs entirely on the device: the pedestrian network, routes, segment assessment, reports, votes and accounts are all computed locally, and the data layer is ready to be connected to the team's API.

## Running on the emulator (from `mobile_app/`)

Installing the emulator and tools from scratch (Linux and Windows): `docs/setup/EMULATOR_SETUP.md` in the root of the repository.

```bash
make emulator-fast        # or make emulator, if the emulator is not running yet
make osm                  # optional: real OSM data for central Kraków (requires internet)
make run                  # build + sign + install + launch
make logs                 # app logs for 60 s
make uninstall           # uninstall (clears saved reports and settings)
make test                 # domain logic tests on Node
```

Without `make osm` the app uses a schematic sample of the area around Tauron Arena (`tools/accessway_sample.py`), marked in the app as sample data.

## What is in the app

The screens follow the team's mockups "Widoki MVP: makiety" (MVP views: mockups; artboards System and V-2 to V-14):

- V-2 Needs: three ready-made presets, the lists "I avoid" ("Unikam") and "I need" ("Potrzebuję"), the buttons Skip ("Pomiń") and Done ("Gotowe"); needs stay on the device only.
- V-3 Fact map: destination search, the switch "From my needs / All" ("Z moich potrzeb / Wszystkie"), facts in the visible area with status, source and date.
- V-4 and V-8 Route planning and address search: start and destination from the search (only after Enter or the button), from the map or from the current location; a routing service error shows no guessed route.
- V-5 Route result: route diagram, tiles, a map with four segment states, the groups "From your needs" ("Z Twoich potrzeb"), "Other barriers" ("Dodatkowe bariery"), "Amenities on the route" ("Udogodnienia na trasie"), "What we do not know" ("Czego nie wiemy"), an alternative route for an unverified barrier; variants without assessment and without a barrier-free route.
- V-6 Fact details: a vote "Still there" ("Nadal jest") or "Gone" ("Już nie ma") once per day, a conflict with the state in OpenStreetMap, a report to moderation.
- V-7 Reporting a barrier, an amenity or an area step by step, with a check for facts of the same kind within a 15 m radius.
- V-10 to V-14: menu, account with pseudonym and password, privacy information, about the data, moderation.

The product name is "EnableMe": the header and the start screen take it from the constant `PRODUCT_NAME` in `data/AppModel.ets`, and the icon label from the `string.json` resources.

## Data and API connection

The screens use only the `Repository` interface (`entry/src/main/ets/data/Repository.ets`). There are two implementations:

- `LocalRepository`: everything on the device, from data bundled with the app (default);
- `ApiRepository`: the team's API according to `docs/product/api_contract.md` in the piwo1-hackyeah repository.

The choice depends on a single file: `entry/src/main/resources/rawfile/config/api.json`.

```json
{ "base_url": "http://203.0.113.10", "timeout_ms": 15000 }
```

- `base_url` empty: works without a server.
- `base_url` with an address: the server address without `/api` and without a trailing slash; the app appends the operation paths.
- Server on the computer where the emulator runs: `http://10.0.2.2:<port>` (the host address as seen from QEMU).
- After changing the file: `make run` (the file is built into the package).

What is where:

| File | Role |
|---|---|
| `data/ApiConfig.ets` | reads `config/api.json` |
| `data/ApiClient.ets` | HTTP, the `Authorization: Bearer` header, renewed token from `Session-Token`, error codes to messages |
| `data/ApiTypes.ets` | JSON shapes from the contract, one to one |
| `data/ApiMapping.ets` | translates the contract into app types (tests in `entry/src/test/ApiMapping.test.ets`) |
| `data/ApiRepository.ets` | contract operations, each described by name and path |

Contract operations and where they are used in the app: `plan_route` (route result), `search_address` (search), `read_osm_copy` (data date), `list_facts_in_area` (fact map, fetched again after the map is moved), `read_fact`, `cast_vote`, `flag_fact` (fact details), `find_nearby_facts`, `create_fact` (reporting), `create_account`, `log_in`, `read_own_account`, `delete_own_account` (account), `list_flagged_facts`, `hide_fact`, `restore_fact` (moderation).

Differences between the contract and the mockups, resolved in the app:

- The contract does not return the user's own vote, so the app remembers the votes cast from this device in the last 24 hours (`api_my_votes.json`).
- The contract has no reverse geocoding and does not give a fact's street, so fact rows from the API have no street name, and a point from the map is called "Point picked on the map" ("Punkt wskazany na mapie").
- `list_facts_in_area` also returns outdated facts; the System mockup says an outdated fact is not shown anywhere, so the app skips them.
- The alternative route comes from the `alternative` field of the same response; "Show" ("Pokaż") does not send a second request.
- The base map comes from the PMTiles archive given in the `tiles_url` field (section below); without it, from the data in the app.

The server runs over plain HTTP, so `resources/base/profile/network_config.json` allows traffic without TLS.

In the local version the moderator role goes to the account with the pseudonym `moderator`; with the API the server assigns the role. Accounts, votes and reports of the local version are stored only on the device; `make uninstall` clears them.

### Mock of the project server (API and map)

`make mock` runs `tools/mock_backend/server.py`: a single host as in the demo, with the API under `/api` and the map archive next to it. The mock keeps everything in memory (`tools/mock_backend/api_mock.py`) and implements all 16 contract operations with their errors, sessions (`Authorization`, renewed `Session-Token`), `X-Request-Id` and the specification rules: M4 statuses from the latest votes of five people with weights 1 and 0.5, the once-per-day vote limit, idempotent reports, M11 flagging and moderation, M2 routes with the four M7 segment states and the three M8 lists, and an alternative route around an unverified barrier.

What the mock makes up (marked in the code):

- the pedestrian network is built from the `roads` layer of the archive at zoom level 15, so routes follow the real streets of Kraków; on the first start building takes about 40 s, after that the network sits in the cache `tiles/krakow.pmtiles.network.pickle`;
- the OSM attributes of segments (kerbs, surface, incline, width, steps) are drawn randomly from a seed for each street block, so segment states are stable between runs;
- 6000 sample facts (`--facts`), most within a 1.5 km radius of well-known places, with votes chosen so that every status occurs;
- address search knows a dozen or so places in Kraków and the named streets of the network;
- the OSM copy date is the build date of the archive (`tiles/krakow.pmtiles.build`).

Account with the moderator role: pseudonym `moderator`, password from `--moderator-password` (default `moderator`, for the local mock only). Every restart begins with a clean state.

`api.json` for the emulator: `base_url` `http://10.0.2.2:8090`, `tiles_url` `http://10.0.2.2:8090/krakow.pmtiles` (the mock prints both at startup). `python3 tools/mock_backend/contract_check.py` checks a running server against the contract (50 checks: every operation, its errors and conventions, token renewal also on errors, the M7 state rules). The mock also passed an independent review against the contract; fixed: token in error responses, default "no steps" ("bez schodów") on roads (M7), `wheelchair=no` never green, reports overruled by OSM (`is_overruled_by_osm`), newest flag first, JSON 404 for unknown methods, strict validation of the idempotency key, the geofence radius and the pseudonym.

Known gap in the contract: for needs without any barrier (M7: segments "without assessment" ("bez oceny")) the contract has no separate state, so the mock returns `no_barrier`, and the app draws such a route neutrally based on its own flag.

Tested on the QEMU emulator with the mock (4 October 2026): needs from a ready-made preset, the map with archive tiles and facts from the API, address search, the route Rynek Główny - Tauron Arena with states and lists, the fact card, voting and the daily limit, a report (with duplicate detection), creating an account, logging out, logging in as moderator, hiding and restoring a fact. Fixes from the test: the idempotency key is created once for the confirmed summary, outdated facts stay on the map (M4), component buttons and fields refresh after a state change (previously, for example, "Sign in" ("Zaloguj się") stayed greyed out).

## Map from vector tiles

The map background comes from a single PMTiles archive of Kraków, just as in the web app: the archive sits on the project host next to the API and every client reads it with byte ranges (piwo1-hackyeah, `plans_finished/frontend_stack/` D-3 and D-5, `docs/standards/standard_frontend.md`). The app needs no additional endpoint. Until the project host is available, the mock serves the archive:

```bash
make tiles          # downloads the Kraków map to tiles/krakow.pmtiles (about 35 MB, requires internet)
make tiles-sample   # or a small map of the schematic sample, without internet
make mock           # API and archive on port 8090 (Range for the archive)
make run            # the app; the emulator sees the computer at 10.0.2.2
```

The full archive address is the `tiles_url` field in `entry/src/main/resources/rawfile/config/api.json` (default `http://10.0.2.2:8090/krakow.pmtiles`; the mock prints the correct address at startup, for the sample `.../sample.pmtiles`). When the archive does not respond or the field is empty, the map draws the background from the data in the app.

The mock (`tools/mock_backend/server.py`, Python standard library only) serves the archive at `GET /<archive name>` with `Range` support (206), next to the API from the section above and `GET /health`.

How the app reads the archive (`data/Tiles.ets`, `data/Pmtiles.ets`, `data/Inflate.ets`, `data/Mvt.ets`):

- once: the first 16 KB of the archive, that is the header and the root directory (decompressed from gzip);
- for each visible tile: the Hilbert ID, a leaf directory if needed (cached), then one request for the tile bytes;
- gzip decompression and MVT decoding in a separate thread (`taskpool`), without blocking the UI; from the Protomaps layers it keeps greenery, water, buildings (from zoom 14) and streets in three ranks (paths from 14, residential streets from 13) with names, simplified to about one screen point;
- at most 4 downloads at once, a cache of 96 tiles, a missing tile is replaced by its parent.

The ArkTS decoder gives results identical to the Python reference implementation on 57 tiles of the Kraków archive; unit tests (`make test`) check it on the sample archive.

Performance: a tile is 512-1024 points on screen, so there are fewer of them when zoomed out. The background is drawn once into a bitmap 40% larger than the screen on each side; panning and pinching only move and scale this bitmap, and it is redrawn only after going beyond the margin, after a zoom change of more than 25% (twice that during pinching) or after new tiles arrive (collected in batches every 90 ms).

Note: the local route and sample facts lie on the schematic sample network, which does not match the real streets. On the real Kraków map (`make tiles`) the route from `LocalRepository` is therefore offset from the streets; with the API, routes come from the real network and match the tiles. For a demo without the API, `make tiles-sample` is the right fit.

## Demo scenario (sample of the Tauron Arena area)

1. Needs: "I use a wheelchair" ("Poruszam się na wózku"), Done.
2. Map: "Where are you going?" ("Dokąd idziesz?"), type "ogród", Search ("Szukaj"), choose Ogród Doświadczeń. Start: Address ("Adres"), "tauron", Search, choose Tauron Arena Kraków. Plan the route ("Wyznacz trasę").
3. Result: a confirmed high kerb on ul. Stanisława Lema and unverified steps at al. Pokoju with an alternative route; "What we do not know" shows segments without data.
4. Destination "Park Lotników Polskich": the only way leads through steps from OpenStreetMap, so the app says there is no barrier-free route.
5. Needs without any barrier: a route without segment assessment.
6. The fact "High kerb" ("Wysoki krawężnik") at ul. Medweckiego: OpenStreetMap reports a lowered kerb here.

## Sources and licences

- Map data: OpenStreetMap, ODbL licence, (c) OpenStreetMap contributors, fetched via the Overpass API.
- Typeface: Barlow Semi Condensed (Regular, SemiBold, Bold) and Barlow Condensed Bold, SIL Open Font License (`rawfile/fonts/OFL-Barlow.txt`).
- Icons: Material Symbols, Apache License 2.0 (`rawfile/icons/LICENSE.txt`), and simple outline icons drawn for this app.
