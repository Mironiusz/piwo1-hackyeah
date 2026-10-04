# Plan: Map tiles of the MVP

Document state: 2026-10-04, plan closed

## Goal

Meet FR-1 - FR-6 of `plans/map_tiles/MAP_TILES_PRD.md`: record the tile archive of Kraków so that a copy can be checked, put the nine map fonts and the style of the base map, as two generated files, into the repository, write the instructions for a machine of the team and for handing the archive over, and correct the documents that still give this initiative the step of the loading program. The look of the map and the requests of the browser are checked in the application that `plans/frontend_app/` builds (D-2).

## Facts

F-1. The tree has no `frontend/` directory, so every file this plan puts under it is new. | cmd:`git ls-tree -d --name-only HEAD` -> `.agents .cache .claude .codex .github .impeccable .vscode agent_docs docs plans plans_finished tests valhalla` | 2026-10-04
F-2. The archive Adrian holds has 34 785 215 bytes, covers longitude 19.792236 to 20.217346 and latitude 49.967667 to 50.126134 at zoom 0 to 15 in 1295 tiles, and carries the OpenStreetMap state of 2026-10-03 04:00 UTC. | cmd:`pmtiles show krakow.pmtiles` -> `bounds: (long: 19.792236, lat: 49.967667) (long: 20.217346, lat: 50.126134)`, `min zoom: 0`, `max zoom: 15`, `addressed tiles count: 1295`, `planetiler:osm:osmosisreplicationtime 2026-10-03T04:00:00Z`; cmd:`ls -la krakow.pmtiles` -> `34785215` | 2026-10-04
F-3. The SHA-256 value of that archive is `21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1`. | cmd:`sha256sum krakow.pmtiles` -> `21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1` | 2026-10-04
F-4. The archive stores the attribution `<a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>`. | cmd:`pmtiles show krakow.pmtiles` -> `attribution <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap</a>` | 2026-10-04
F-5. The full set of map fonts and sprites has 776 files of 11 182 999 bytes, and the ranges `0-255`, `256-511` and `8192-8447` of the three Noto Sans weights are nine files of 805 565 bytes. | cmd:`find basemaps-assets -type f` counted -> `776`; cmd:`du -sb basemaps-assets` -> `11182999`; cmd:`stat -c %s` of the nine files -> `76044 127726 64220`, `77628 129635 65101`, `79344 132976 52891` | 2026-10-04
F-6. The style package builds its layers with `layers(source, flavor, {lang})`, and a flavor is a plain object of colors that can spread a named one. | cmd:`GET https://docs.protomaps.com/basemaps/maplibre` -> `layers("protomaps",namedFlavor("light"),{lang:"en"})`; cmd:`GET https://docs.protomaps.com/basemaps/flavors` -> `let flavor = {...namedFlavor("light"),buildings:"red"}` | 2026-10-04
F-7. In the source of the style package four layers draw an image of the sprite - `roads_oneway`, `roads_shields`, `places_locality` and `pois` - the layer `pois` exists only when the flavor has the key `pois`, and the fonts default to `Noto Sans Regular`, `Noto Sans Medium` and `Noto Sans Italic`. | cmd:`GET https://raw.githubusercontent.com/protomaps/basemaps/main/styles/src/base_layers.ts` -> `"icon-image"` in the four layers, `t.pois ? [...] : []`, `t.regular || "Noto Sans Regular"`, `t.bold || "Noto Sans Medium"`, `t.italic || "Noto Sans Italic"` | 2026-10-04
F-8. The flavor of the style package has 72 required color keys, from `background` to `address_label_halo`, and the optional keys `regular`, `bold`, `italic`, `pois` and `landcover`, the last with the keys `barren`, `farmland`, `forest`, `glacier`, `grassland`, `scrub` and `urban_area`. | cmd:`GET https://raw.githubusercontent.com/protomaps/basemaps/main/styles/src/flavors.ts` -> the interface `Flavor` with these keys | 2026-10-04
F-9. The mocks draw the base map with the ground `#ECECE3`, the blocks `#DDDDD2`, the parks `#D3E1CB` and the streets `#FFFFFF`, and its labels in `#4B5058`. | code:`.impeccable/briefs/views/app.css:6`; code:`.impeccable/briefs/views/app.css:62`; code:`.impeccable/briefs/views/app.css:2` | 2026-10-04
F-10. The label color `#4B5058` has a contrast ratio of 6.83 on the ground, 8.12 on white, 5.95 on the color of the parks, 5.93 on the color of the blocks and 5.43 on `#C5D6DF`. | cmd:WCAG relative luminance computed in Python for the five pairs -> `6.83`, `8.12`, `5.95`, `5.93`, `5.43` | 2026-10-04
F-11. Git ignores `build`, `dist` and `node_modules` at every depth and has no entry for a directory of tiles. | code:`.gitignore:17`; code:`.gitignore:18`; code:`.gitignore:19` | 2026-10-04
F-12. On the server a reverse proxy serves the frontend build and the tile archive, answering byte ranges, and the archive lies on a volume the proxy reads. | doc:`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` line 74, line 80 | 2026-10-04
F-13. The frontend standard leaves to this initiative whether the copies of the fonts and sprites are committed or fetched by a script. | doc:`docs/standards/standard_frontend.md` line 41 | 2026-10-04
F-14. `MVP.md` gives this initiative the step of the loading program, asks that a change making one of its items untrue updates it in the same change, and lists the rulings still to be confirmed. | doc:`MVP.md` line 62, line 11, line 113 | 2026-10-04
F-15. The loading program does not exist: `plans/osm_import/` holds only its seed. | cmd:`ls plans/osm_import` -> `OSM_IMPORT_SEED.md` | 2026-10-04
F-16. Node.js 22.20.0 and npm 11.21.0 run on the machine of Adrian, the npm registry answers, and the style package is at 5.7.2. | cmd:`node --version` -> `v22.20.0`; cmd:`npm --version` -> `11.21.0`; cmd:`npm ping` -> `PONG 393ms`; cmd:`npm view @protomaps/basemaps version` -> `5.7.2` | 2026-10-04
F-17. `docs/setup/` exists and holds one guide. | cmd:`ls docs/setup` -> `EMULATOR_SETUP.md` | 2026-10-04
F-18. The forbidden characters check will scan `.json` files under `frontend/` once `plans/frontend_app/` extends it, and frontend files are formatted by prettier with the configuration of the repository. | doc:`docs/standards/standard_frontend.md` line 90, line 75 | 2026-10-04
F-19. MapLibre GL JS accepts in a style an address that starts with a slash and resolves it against the address of the page. | ASSUMPTION: not checked here, because no application exists yet to load the style. `plans/frontend_app/` checks it when it builds the map and resolves the three addresses of D-5 itself if it does not hold | 2026-10-04

## Decisions

D-1. The step of the loading program is not built by this task. Adrian decided on 2026-10-04, in phase B, in his words: "I will give the archive to the backend guys; until then we make our own temporary mock, then we switch over when it is ready; the point is to test it." The archive is handed to the backend persons as a file, with the record by which it is checked, and they load it on the server; until the server serves it, the frontend takes the archive from the place of D-5 on the machine it runs on. Chosen against a separate task of this initiative for the step, against planning the step on a contract of the loading program that nobody decided (F-15), and against leaving this plan open until that program exists. The backend persons have not confirmed it.

D-2. Nothing temporary is built to look at the map. Adrian answered on 2026-10-04, when asked how the style is checked before the application exists: "but we are getting close to building the frontend, after all we are planning its implementation right now." This plan therefore checks what can be checked on the files themselves - the text of the two style files, the fonts and the record of the archive - and the criteria that need a drawn map are checked by `plans/frontend_app/` when it builds its foundation: AC-2, the half of AC-3 about the requests of the browser, AC-5 and the half of AC-6 about the working map. The review of this initiative lists them as waiting until then. Read by the agent from that answer; the two variants offered were a test page outside the repository and this initiative setting up the frontend project.

D-3. The fonts are committed, and only the ranges Kraków needs: `0-255`, `256-511` and `8192-8447` of `Noto Sans Regular`, `Noto Sans Medium` and `Noto Sans Italic`, nine files of 805 565 bytes (F-5). Decided by Adrian on 2026-10-04, against committing all 776 files and against a script that fetches them, which every fresh copy of the repository and the build on the server would need an outside connection for. A label in another script, should the archive hold one, is not drawn.

D-4. The style is two generated files committed to the repository, one with Polish labels and one with English ones, and the application loads the one of the current language. Decided by Adrian on 2026-10-04, against a module that builds the style in the browser from the style package.

D-5. Places and addresses, the contract with `plans/frontend_app/` and with the server. The browser asks for the archive at `/tiles/krakow.pmtiles`, for the styles at `/map/style-pl.json` and `/map/style-en.json`, and for the fonts at `/map/fonts/{fontstack}/{range}.pbf`. In the repository the styles and the fonts lie under `frontend/public/map/`, and on a machine of the team the archive lies at `frontend/public/tiles/krakow.pmtiles`, a directory git ignores. Agent decision at C:60, without asking: `frontend/public/` is the directory the Vite template serves as it is, and the three addresses name what they hold; the archive stays apart from `map/` so that one ignore entry covers it.

D-6. What a style file holds. `version` 8; the source `protomaps` of the type `vector` with `url` `pmtiles:///tiles/krakow.pmtiles` and the attribution of F-4; `glyphs` `/map/fonts/{fontstack}/{range}.pbf`; no `sprite`; and the layers that `layers("protomaps", flavor, {lang})` returns for `pl` or `en`, changed in three ways so that no layer needs a sprite (F-7): the flavor has no key `pois`, the layers `roads_oneway` and `roads_shields` are removed, and the layer `places_locality` loses its layout properties that start with `icon-`. Agent decision at C:60, without asking: it follows from FR-2, which has no icons of points of interest, and from D-3, which commits fonts only; arrows of one-way streets and road shields serve drivers, not a person on foot.

D-7. The colors of the flavor, on top of the named flavor `light` of the package. Agent decision at C:60, without asking: every value is a token of the mocks (F-9) or one of four values next to them, and every label color meets the contrast of F-10.

| Keys of the flavor                                                                                                                       | Value     |
| ---------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `background`, `earth`, and `barren`, `farmland`, `glacier`, `urban_area` of `landcover`                                                  | `#ECECE3` |
| `park_a`, `park_b`, `wood_a`, `wood_b`, `scrub_a`, `scrub_b`, `zoo`, and `forest`, `grassland`, `scrub` of `landcover`                   | `#D3E1CB` |
| `hospital`, `industrial`, `school`, `pedestrian`, `glacier`, `sand`, `beach`, `aerodrome`, `runway`, `military`, `pier`                  | `#E6E6DC` |
| `water`                                                                                                                                  | `#C5D6DF` |
| `buildings`                                                                                                                              | `#DDDDD2` |
| `other`, `minor_service`, `minor_a`, `minor_b`, `link`, `major`, `highway`, and the five keys `bridges_*` without `_casing`              | `#FFFFFF` |
| the five keys `tunnel_*` without `_casing`                                                                                               | `#F4F5F2` |
| every key that ends in `_casing`, `_casing_early` or `_casing_late`                                                                      | `#D5D8DC` |
| `railway`, `boundaries`                                                                                                                  | `#B9BDC4` |
| `roads_label_minor`, `roads_label_major`, `ocean_label`, `subplace_label`, `city_label`, `state_label`, `country_label`, `address_label` | `#4B5058` |
| `roads_label_minor_halo`, `roads_label_major_halo`, `address_label_halo`                                                                 | `#FFFFFF` |
| `subplace_label_halo`, `city_label_halo`, `state_label_halo`                                                                             | `#ECECE3` |

The keys `regular`, `bold` and `italic` are left out, so the fonts are the three of D-3.

D-8. The generator is `frontend/scripts/generate_base_map_style.mjs`, run with `node`. It writes the two files of D-5, formatted with the prettier of the repository so that they stay unchanged under its check (F-18), and with the argument `--check` it writes nothing and ends with an error when a committed file differs from what it generates or breaks a rule of D-6. Agent decision at C:60, without asking: a plain script needs no build step, and the check keeps the committed files from drifting from the colors of D-7.

D-9. The style package for the run. Until `plans/frontend_app/` creates the project and lists the package as a development dependency, the generator runs after `npm install --prefix frontend --no-save --no-package-lock @protomaps/basemaps@5.7.2`, which creates only `frontend/node_modules`, a directory git ignores (F-11). Agent decision at C:60, without asking: it leaves no project file behind that the Vite template would have to be merged with.

D-10. The instructions and the record of the archive are one document, `docs/setup/MAP_SETUP.md`, next to the guide `docs/setup/` already holds (F-17). Agent decision at C:60, without asking.

D-11. The documents that become untrue are corrected in the same change: the sentence of `docs/standards/standard_frontend.md` that leaves the choice of D-3 open, and in `MVP.md` the row of this initiative, the item of the order that names its tile step, and the list of what is still to be confirmed (F-13, F-14).

## Scope of changes

1. `.gitignore`: after the line `node_modules` add the line `frontend/public/tiles/`.

2. The fonts, nine new files copied byte for byte from the copy of the Protomaps assets that Adrian holds: `frontend/public/map/fonts/Noto Sans Regular/0-255.pbf`, `256-511.pbf` and `8192-8447.pbf`, and the same three files under `frontend/public/map/fonts/Noto Sans Medium/` and `frontend/public/map/fonts/Noto Sans Italic/`.

3. `frontend/scripts/generate_base_map_style.mjs`, new file, without line comments, with a documentation comment above each function:
   - `buildFlavor()` returns the flavor of D-7: the named flavor `light` of the package with the values of the table, the key `landcover` with its seven keys, and without the key `pois`.
   - `buildStyle(language)` takes `"pl"` or `"en"` and returns the style object of D-6.
   - `findStyleViolations(style)` returns a list of texts, empty for a style that keeps D-6: a key `sprite`; a layer with a layout property that starts with `icon-`; a `text-font` outside the three fonts of D-3; a `glyphs` or a source `url` other than those of D-6; an address with `://` outside the `url` of the source and the attribution; a forbidden character of `docs/standards/standard_formatting.md`.
   - `main(argv)` writes `frontend/public/map/style-pl.json` and `frontend/public/map/style-en.json` formatted with prettier, or with `--check` compares them with what it generates, prints every violation and difference, and returns 0 or 1.

4. `frontend/public/map/style-pl.json` and `frontend/public/map/style-en.json`, new files, written by the generator after the install of D-9.

5. The archive on the machine of Adrian: copy the file of F-2 to `frontend/public/tiles/krakow.pmtiles`.

6. `docs/setup/MAP_SETUP.md`, new file, with these sections:
   - What the map needs: the four addresses of D-5 and which of the files are in the repository.
   - The tile archive: the build `20261003`, the command of D-5 of `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` that cut it, its size, bounds, zoom range, number of tiles and OpenStreetMap state (F-2), its SHA-256 value (F-3), and that it is never committed.
   - A machine of the team: get the archive from Adrian or cut it with that command, check it with the SHA-256 value, put it at `frontend/public/tiles/krakow.pmtiles`.
   - Handing the archive to the server: the file, the value by which it is checked, the address `/tiles/krakow.pmtiles` under which the frontend asks for it and the byte ranges the server has to answer; that the backend persons load it and that no address or login of the server enters the repository.
   - The fonts: the nine files, their origin in the Protomaps assets, their licence and the SHA-256 value of each.
   - The style: how to run the generator and its check, where the colors come from (D-7), and that a change of a color is made in the script, never in a generated file.
   - Licences: the OpenStreetMap data under the ODbL, the style package under BSD-3-Clause, the fonts under the SIL Open Font License.

7. `docs/standards/standard_frontend.md`, section Technology: replace the paragraph that starts with "The style of the base map comes from the Protomaps style package" with: "The style of the base map comes from the Protomaps style package, with the colors set to the design direction and the labels in the language of the interface. A script generates it into two committed files, one for each language of the interface, and the application loads the one of the current language. The fonts the style needs are nine committed files, the Latin ranges of three weights of Noto Sans, and the style uses no sprite. No address of a file the browser loads names an outside host. Decided on 2026-10-04 by the initiative `map_tiles` of `MVP.md` (`plans/map_tiles/MAP_TILES_PLAN.md` D-3, D-4, D-6); the instructions are in `docs/setup/MAP_SETUP.md`."

8. `MVP.md`:
   - In the table Initiatives, the row of `plans/map_tiles/`: the cell Builds becomes "The tile archive with its record, the style of the base map as two generated files and the map fonts served by the project of D-6 (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-5, D-6), with the fonts committed (`plans/map_tiles/MAP_TILES_PLAN.md` D-3). The archive file is handed to the backend persons, who load it on the server; this initiative builds no step of the loading program (D-1 there).", and the cell Waits for becomes "Nothing."
   - In Order and critical path, item 4: "After `osm_import`: `route_planning`, `sample_data` and the tile step of `map_tiles` in the loading program." becomes "After `osm_import`: `route_planning` and `sample_data`."
   - In Open decisions and confirmations, a new item at the end: "- The loading of the tile archive on the server. Adrian hands the file to the backend persons, who load it (`plans/map_tiles/MAP_TILES_PLAN.md` D-1); they have not confirmed it, and the row of `osm_import` above still says that `map_tiles` adds a step to the loading program."

## Rollout order

1. Steps 1 and 2 of Scope of changes.
2. Step 3, then the install of D-9, then step 4 by running `node frontend/scripts/generate_base_map_style.mjs`.
3. Step 5.
4. Steps 6, 7 and 8, then `npx --no-install prettier --write` on every changed or created markdown file.
5. The checks of Definition of Done.
6. The review `plans/map_tiles/MAP_TILES_REVIEW.md` and the entry in `agent_docs/memory/frontend/_shared.md`, as `plan-implement` writes them.

Steps for a human: hand the archive file with `docs/setup/MAP_SETUP.md` to the backend persons and obtain their confirmation of D-1; the commit, the push and the pull request.

## Definition of Done

- `node frontend/scripts/generate_base_map_style.mjs --check` ends with 0: both style files equal what the generator writes, and `findStyleViolations` returns nothing for either (AC-3, the half about the text of the style).
- `sha256sum frontend/public/tiles/krakow.pmtiles` gives the value of F-3, the same value stands in `docs/setup/MAP_SETUP.md` with the build `20261003`, and `git status` does not list the archive (AC-1).
- The nine font files exist, and `sha256sum` of each equals the value recorded in `docs/setup/MAP_SETUP.md` (AC-3, AC-4).
- The repository holds no script that fetches fonts, and `docs/standards/standard_frontend.md` records the choice (AC-4).
- `docs/setup/MAP_SETUP.md` holds the six parts of step 6 (AC-6, the half about the handing over).
- `npx --no-install prettier --check` passes on every changed or created markdown file and on the two style files, and `python -m pytest tests/architecture` passes.
- The review lists AC-2, the half of AC-3 about the requests of the browser, AC-5 and the half of AC-6 about the working map as waiting for `plans/frontend_app/` (D-2).

## Risks

- The layers and the keys of the flavor were read from the main branch of the style package, not from the release 5.7.2 the generator installs (F-7, F-8). A key or a layer named differently there shows in the first run: `findStyleViolations` reports a layer that still needs a sprite, and a key of D-7 that the package does not know changes nothing in the output. The table of D-7 is then corrected in this plan before the files are committed.
- The colors were chosen without seeing them on a map (D-2). The first look comes with the foundation of `plans/frontend_app/`, and a change of a color then means a new run of the generator.
- F-19 is an assumption. If it does not hold, `plans/frontend_app/` resolves the three addresses of D-5 against the address of the page when it loads a style, and the files of this plan stay as they are.
- Three ranges of fonts are committed (D-3). A label with a letter outside them is not drawn; the browser then asks for a range file that does not exist and gets no answer for it.
- The backend persons have not confirmed that they load the archive (D-1). Until they do, the hosted demo has no map.
- The archive exists as one file on one machine. The record of step 6 lets a second copy be checked, and the command in it cuts the file again as long as the build `20261003` is offered.

## Open questions

None. The four questions of phase B - the step of the loading program, how the style is checked before the application exists, the fonts and the form of the style - were answered by Adrian and are recorded in D-1 - D-4.

## Supplementary files

- `plans/map_tiles/MAP_TILES_PRD.md`, the contract this plan implements, with `plans/map_tiles/MAP_TILES_SHAPE.md` and its seed.
- `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`, D-5 - D-7, and `docs/standards/standard_frontend.md`.
- `.impeccable/briefs/views/app.css`, the tokens of the mocks, and `.impeccable/briefs/views.md`.
- `plans/frontend_app/FRONTEND_APP_PLAN.md`, the plan that waits for this one, and `MVP.md`.
