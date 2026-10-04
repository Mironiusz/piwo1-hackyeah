# Shape: HarmonyOS port

Document state: 2026-10-04, interview closed
Regulator: C:40

## Problem

The Huawei submission is mandatory since 2026-10-04 (`plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7) and needs a HarmonyOS client of the same programming interface as the web app, delivered as a `.hap` package with build instructions. `FINAL_CHECKLIST.md`, set 8, names four checks: the choice of the client (8.1), the client planning a route against the running service (8.2), the package on an emulator (8.3) and instructions that reproduce the package from the README alone (8.4). The entry HarmonyOS port and the Huawei submission of `docs/standards/decision_registry.md` waits for this shape to choose the client.

## Recipient and trigger

The jury of the Huawei challenge "Imagine What's Next", who install and run the package from the public repository and its README, and a person with a disability who plans a walking route on a HarmonyOS phone. The trigger is the deadline of the submission at 11:00 on 4 October 2026 (`FINAL_CHECKLIST.md`, set 1, the deadline of the Huawei challenge is still a fact to verify there).

## Current state

Found in the repository on 2026-10-04, before the interview:

- A native ArkTS/ArkUI client exists in `mobile_app/` (commit "Mobile app initial commit" on `dev`, merged through pull request 27). It is an OpenHarmony project for API 20, Stage model, in `mobile_app/accessway/`, built from the team mock-ups "Widoki MVP: makiety" with all screens V-2 to V-14.
- Its data layer has two implementations behind one interface: `LocalRepository`, which computes everything on the device from bundled sample data, and `ApiRepository`, which calls `docs/product/api_contract.md`. The choice is the field `base_url` in `mobile_app/accessway/entry/src/main/resources/rawfile/config/api.json`; empty means local data.
- `ApiRepository` maps all sixteen operations of the contract: `plan_route`, `search_address`, `read_osm_copy`, `list_facts_in_area`, `read_fact`, `find_nearby_facts`, `create_fact`, `cast_vote`, `flag_fact`, `create_account`, `log_in`, `read_own_account`, `delete_own_account`, `list_flagged_facts`, `hide_fact`, `restore_fact`. It has not run against a live service yet, because check 4.1 is not ticked.
- A platform capability is used: the device location through `geoLocationManager` (`mobile_app/accessway/entry/src/main/ets/data/Location.ets`), as the start point of a route and the place of a report.
- The base map is drawn on Canvas, because the emulator has no GPU. It draws vector tiles of Kraków from a separate tile server when the field `tiles_url` of the same file is set, and the bundled sample map otherwise. The tile server is a mock in `mobile_app/tools/mock_backend/server.py`; the operation it serves, `GET /tiles/{z}/{x}/{y}.json`, is not in `docs/product/api_contract.md`.
- Unit tests of the domain and of the API mapping run on Node (`make aw-test` in `mobile_app/`).
- `docs/setup/EMULATOR_SETUP.md` is an older copy of `mobile_app/docs/EMULATOR_SETUP.md`: it assumes the commands run from the root of the former standalone repository and mentions a project `app/` that is not in this repository.
- Tracked by git under `mobile_app/` but not source: `accessway/.hvigor/` (build caches and reports), `accessway/oh_modules/` (installed packages), `accessway/local.properties` (a local SDK path), `accessway/signatures/` with the debug signing keys whose encrypted passwords are in `accessway/build-profile.json5`, and `tiles/krakow.pmtiles`, an archive of about 35 MB.
- The docstrings of most source files under `mobile_app/accessway/entry/src/` and the file `mobile_app/accessway/README.md` are in Polish, while `CLAUDE.md`, section Language and communication style, requires everything in the repository in English. A defect of the same class as the scope (the files of the client); recommended for the PRD at the cost of translating the docstrings of about forty files and one README. Agent decision at C:40, without asking: recorded, not yet in the requirements.
- During the interview, on 2026-10-04, the correction ordered with question 3 was made in the standalone working copy of the client from which `mobile_app/` was copied: the client reads the archive in byte ranges (`data/Pmtiles.ets`, `data/Inflate.ets`, `data/Mvt.ets`, `data/Tiles.ets`) and the mock serves only the archive. The decoder gave byte-identical output to the reference implementation in Python on 57 tiles of the Kraków archive, and four unit tests cover it. `mobile_app/` does not hold the correction yet.
- The application is named "EnableMe" on screen since 2026-10-04 by a request of Kuber in another conversation; `CLAUDE.md` and `PRODUCT.md` still say the product name is not chosen.

## Smallest meaningful scope

- The client is the native ArkTS/ArkUI client in `mobile_app/` (answer of Kuber to question 1 on 2026-10-04). React Native for OpenHarmony is not built. This settles the variant of the registry entry HarmonyOS port and the Huawei submission for check 8.1.
- The client calls all sixteen operations of `docs/product/api_contract.md` (answer of Kuber to question 2 on 2026-10-04). An operation the running service does not answer yet shows the error message of the contract on its screen; nothing falls back to local data when `base_url` is set.
- The base map comes from the project the way the repository already decides it for the web app: one PMTiles archive of Kraków, served by the host of the project next to the programming interface and read in byte ranges (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-3 and D-5, `docs/standards/standard_frontend.md`). The port reads that same archive. The JSON tile endpoint of the mock in `mobile_app/tools/mock_backend/` is not in any of these documents, so it is removed and the port decodes the archive itself; the mock keeps serving the archive in byte ranges (answer of Kuber to question 3 on 2026-10-04, who ordered the correction at once, during the interview). The documents do not fix the path of the archive on the host, so the port takes the full address of the archive from its configuration instead of assuming a path.

## Out of scope

- A React Native for OpenHarmony client (question 1).
- A JSON tile endpoint or any tile operation added to `docs/product/api_contract.md`; the archive is a static file of the host, as for the web app (question 3).
- Rewriting the git history to drop the archive and the keys from past commits; it is left to a person (question 4).
- The product name "EnableMe" in `CLAUDE.md`, `PRODUCT.md` and the specification. The port shows it on screen; whether it becomes the name of the product is a decision of the owner of the specification, outside this initiative. Agent decision at C:40, without asking.
- The style of the web base map (fonts, sprites, Protomaps style package); the port draws its own Canvas style from the same archive.

## Functional requirements

1. The client in `mobile_app/` is the HarmonyOS client of the submission, native ArkTS/ArkUI, API 20 (8.1).
2. With `base_url` set, every one of the sixteen operations of the contract goes to the service; the error codes of the contract are shown as their messages (8.1, 8.2).
3. A route is planned for a profile against the running service, starting at the location of the device when the person allows it (8.2).
4. The base map is read from the PMTiles archive of the project in byte ranges, at the address given in the configuration; with no address or no answer the bundled sample map is drawn (8.2).
5. The mock in `mobile_app/tools/mock_backend/` serves only what the documents decide: the archive in byte ranges. It serves it from the same host as a stand-in for the host of the project during development.
6. The non-source files of question 4 are ignored and listed for untracking.
7. `docs/setup/EMULATOR_SETUP.md` sets up the toolchain and the emulator from this repository, with every command run where it says and every file it names present (8.3).
8. `mobile_app/README.md` names the versions of the toolchain, the SDK and the emulator and reproduces the package from a clean clone (8.4).

## Scenarios: input, flow, expected state after the run

1. Development without the service. `base_url` empty, `tiles_url` the address of the archive on the mock. The app starts on the emulator, reads the header and the root directory of the archive in two range requests, then each visible tile in one range request; the map of Kraków is drawn and routes come from the bundled sample.
2. The hosted demo. `base_url` and `tiles_url` point at the host of the project, set at build time and never committed. A person picks the needs, start and destination, and plans a route; the route with its segment states is drawn over the base map from the same archive as the web app (8.2).
3. The service does not answer an operation. The screen shows the message of the contract error; nothing is computed locally instead.
4. A clean clone. A person follows `mobile_app/README.md` and `docs/setup/EMULATOR_SETUP.md`, generates the signing material and the archive, builds the `.hap`, installs it on the emulator and launches it (8.3, 8.4).

## Challenging own assumptions

- Is the client in `mobile_app/` the client of this initiative, or a prototype the shape may discard? It was built before this seed and outside the chain; the shape treats it as the current state, and the choice of 8.1 decides whether it stays.
- Does "the same programming interface" exclude the tile endpoint? The web app reads one PMTiles archive with byte ranges (`plans_finished/frontend_stack/`, D-5 and D-3), the port reads JSON tiles from another endpoint. Both read the same archive, but the second endpoint is outside the contract, so it is a question, not a finding.
- Is the debug signing material a secret under `docs/standards/standard_config.md`? It signs only debug builds for an emulator, but the repository becomes public, so it was asked; it leaves the repository (question 4).
- Can the port read PMTiles on a CPU-only emulator fast enough? The archive keeps its tiles compressed with gzip and the port has to inflate and decode each one; the cost moves from the mock to the device. The tiles are decoded once, kept in memory, and the base map stays a cached bitmap, so panning does not depend on it; the first view of an area is slower.
- Does the mock decide anything? It was written outside the chain on 2026-10-04 and its JSON endpoint was an invention; after question 3 it only serves the archive, as the host of the project will.

## Domain rules or explicit TODO

- The port is a second client of the same programming interface, not an embedding of the web app (`plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`, Domain rules; `PRODUCT.md`).
- No address, host, login or secret of the hosted demo enters the repository (`CLAUDE.md`, Target environment), so the address of the service in `api.json` is set at build time and is not committed.

## Notes on data, performance and security

- The client keeps a session token and the own votes of the last day in files of the application sandbox; it keeps no other personal data.
- The emulator draws without a GPU; the tile pipeline was optimised on 2026-10-04 (simplified tiles, a cached bitmap of the base map).

## Open questions

None. The blocking questions 2, 3 and 4 were answered on 2026-10-04.
