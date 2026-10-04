# Review: Map tiles of the MVP

Document state: 2026-10-04, implementation finished and reviewed as ready for the scope of the plan; the four acceptance criteria that waited for a drawn map were checked by `frontend_app` on the same day; initiative closed by the user without the confirmation of the backend persons, see the entry Closure, moved to `plans_finished/`

## Implementation run of 2026-10-04

### Check before implementation

- The facts of `plans/map_tiles/MAP_TILES_PLAN.md` were checked again at 02:55. `HEAD` was `a6255ed`, equal to `origin/dev`, and no commit touched a file the facts cite since the plan was written.
- Line references: the lines cited by F-9, F-11, F-12, F-13, F-14 and F-18 still carry the cited content in the working tree.
- Runs repeated with the same result: F-1 (`git ls-tree -d --name-only HEAD` has no `frontend`), F-15 (`ls plans/osm_import` -> `OSM_IMPORT_SEED.md`) and F-17 (`ls docs/setup` -> `EMULATOR_SETUP.md`).
- Not repeated: F-2 - F-5, F-10 and F-16, measured in the same night on the same files, and F-6, a read of outside documentation.
- F-7 and F-8 were read from the main branch of the style package, which the Risks of the plan name. After the install of D-9 they were checked on the release 5.7.2: `grep "icon-image" src/base_layers.ts` finds the same four layers, `roads_oneway`, `roads_shields`, `pois` and `places_locality`, and the interface `Flavor` in `src/flavors.ts` has the same 72 required keys and the five optional ones. The table of D-7 needed no correction.
- `plans/map_tiles/MAP_TILES_SHAPE.md` has no question marked `Block: yes`; its regulator is C:60.
- No sign of another session on the tree: `git status` showed only the files of `plans/frontend_app/` and `plans/map_tiles/`.
- Baseline of the checks: `python -m pytest tests/architecture` passes, 120 tests.

### Deviations from the plan

O-1. `frontend/scripts/generate_base_map_style.mjs` has three functions the plan does not name, all private to the file: `collectFontNames` and `collectLiteralFontNames`, which read the font names out of a `text-font` value that is a list or an expression, and `renderStyleFile`, which formats a style with prettier. The four functions of step 3 keep the contracts the plan gives them. Agent decision at C:60, without asking: they are parts of `findStyleViolations` and `main`, and no other file calls them.

O-2. `main` runs only when the file is started with `node`, not when another file imports its functions. Without it a test that imports `buildStyle` would start a run with the arguments of the test tool. Agent decision at C:60, without asking: the behavior of the plan, a run from the command line, is unchanged.

O-3. `buildFlavor` stops with an error when the style package does not know a key of D-7. The plan names this case in its Risks and says a wrong key would change nothing in the output; the error makes it visible in the first run instead. Agent decision at C:60, without asking.

O-4. `findStyleViolations` also reports a style with a source other than the tile archive. The plan lists the address of the source and not their number. Agent decision at C:60, without asking: a second source would be a second address of a file the browser loads, which FR-3 forbids.

O-5. The Definition of Done says the instructions hold six parts, while step 6 of Scope of changes lists seven. All seven were written; the count in the Definition of Done is a slip of the plan.

O-6. `docs/standards/standard_frontend.md`, section Technology, got a second changed sentence: the one that lists what is served from one host named "the map fonts and sprites" and now names "the map style and fonts". The plan lists only the paragraph on the style; this sentence became untrue with D-6, which leaves the style without a sprite. Agent decision at C:60, without asking: it follows from D-11, and the sentence has one correct wording. Found in the review below.

### What was done

- Step 1: `.gitignore` has the line `frontend/public/tiles/` after `node_modules`.
- Step 2: the nine font files lie under `frontend/public/map/fonts/`, copied byte for byte from the copy Adrian holds.
- Step 3: `frontend/scripts/generate_base_map_style.mjs` was written, without line comments, with a documentation comment above each function.
- Step 4: after `npm install --prefix frontend --no-save --no-package-lock @protomaps/basemaps@5.7.2`, the generator wrote `frontend/public/map/style-pl.json` and `frontend/public/map/style-en.json`, 68 layers and 86 179 bytes each. The install created only `frontend/node_modules`, which git ignores.
- Step 5: the archive was copied to `frontend/public/tiles/krakow.pmtiles` on the machine of Adrian.
- Step 6: `docs/setup/MAP_SETUP.md` was created with its seven sections.
- Step 7: the paragraph on the style in `docs/standards/standard_frontend.md`, section Technology, was replaced with the text of the plan.
- Step 8: `MVP.md` has the new cells in the row of `plans/map_tiles/`, the shortened item 4 of Order and critical path, and the new last item of Open decisions and confirmations.

### Checks of the Definition of Done

- `node frontend/scripts/generate_base_map_style.mjs --check` -> `Both style files are up to date and keep every rule.`, exit 0.
- The two style files read as text: the keys `version`, `sources`, `glyphs` and `layers`; no `sprite`; no layer with a layout property that starts with `icon-`; the only colors are the ten of D-7; the only addresses are `pmtiles:///tiles/krakow.pmtiles` and the link of the attribution; ten label layers differ between the two languages.
- `sha256sum frontend/public/tiles/krakow.pmtiles` -> `21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1`, the value of F-3, which stands in `docs/setup/MAP_SETUP.md` together with the build `20261003`. `git check-ignore -v frontend/public/tiles/krakow.pmtiles` -> `.gitignore:20:frontend/public/tiles/`, and `git status` does not list the archive.
- The nine font files: the size and the SHA-256 value of each equal the row of `docs/setup/MAP_SETUP.md`, 9 of 9, 805 565 bytes together.
- No file under `frontend/scripts/` fetches fonts, and `docs/standards/standard_frontend.md` records the choice.
- `git status --short -uall frontend` lists twelve files: the nine fonts, the two styles and the script.
- `npx --no-install prettier --check` passes on `MVP.md`, `docs/standards/standard_frontend.md`, `docs/setup/MAP_SETUP.md`, the files of `plans/map_tiles/`, the two style files and the script.
- `python -m pytest tests/architecture` passes, 120 tests.

### Acceptance criteria

- AC-1: met by the record of the archive and the check of its SHA-256 value.
- AC-3: the half about the text of the style is met by the check of the generator. The half about the requests of the browser waits for `plans/frontend_app/` (D-2 of the plan).
- AC-4: met. The fonts are committed, no script fetches them, and the standard records the choice.
- AC-6: the half about handing the archive over is met by `docs/setup/MAP_SETUP.md`. The half about a working map on a machine of the team waits for `plans/frontend_app/`.
- AC-2 and AC-5 wait for `plans/frontend_app/`: the colors, the names of the streets, the labels in both languages and the attribution need a drawn map.

### Steps of a human still open

- Handing the archive file with `docs/setup/MAP_SETUP.md` to the backend persons and obtaining their confirmation of D-1.
- The commit, the push and the pull request.

### Review of 2026-10-04

Scope: the changes of this run - `.gitignore`, `MVP.md`, `docs/standards/standard_frontend.md`, `docs/setup/MAP_SETUP.md`, the twelve files under `frontend/`, the entry in `agent_docs/memory/frontend/_shared.md` and the files of `plans/map_tiles/`. The review was made by the agent that implemented the plan, not by a separate reviewer.

Blockers: none.

Fixed during the review:

- Z-1. The script decided whether it was started with `node` by comparing the address of the file with the path given to `node` as texts. Started through a linked directory the two differ, the generator would do nothing, and its check would end with 0 without checking anything. `isStartedDirectly` now compares both paths after links are resolved. Checked by a run: `--check` ends with 0 and prints its line, and an import of the file runs nothing.
- Z-2. The sentence of the standard described in O-6.

Risks:

- R-1. The generator has no unit tests, while `docs/standards/standard_frontend.md`, section Tests of logic, asks for tests of logic outside components. The test tool is set up by `plans/frontend_app/`. Until then the run with `--check` is the only check of the rules. Tests to add there: `findStyleViolations` for a sprite, an icon, a font outside the three and an outside address, and `buildStyle` for both languages.
- R-2. The release of the style package is pinned only by the command in `docs/setup/MAP_SETUP.md`. No lock file holds it until the frontend project lists the package.
- R-3. Four acceptance criteria wait for a drawn map (D-2 of the plan): the colors were chosen without being seen.
- R-4. The backend persons have not confirmed D-1, and the row of `osm_import` in `MVP.md` still says that `map_tiles` adds a step to the loading program. It was left to its owner and listed under Open decisions and confirmations.
- R-5. The layer `places_locality` keeps the properties `text-variable-anchor` and `text-radial-offset`, which placed its text next to the icon the style no longer draws. Whether the names of localities sit well is seen on the drawn map.

Improvements: none beyond the risks above.

Verification:

- `standard_agentic_workflow.md`: checked automatically. `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> 63 passed.
- `standard_agent_docs.md`: checked automatically. `pytest tests/architecture/test_plan_document_contract.py` -> 25 passed, the closed plan of this initiative included. The memory entry and this review were read against their formats.
- `standard_review.md`: checked manually. This record follows its order and names the scope of the verdict.
- `standard_documentation.md`: checked manually. `docs/setup/MAP_SETUP.md` says why it exists and carries its state line. The pair of documents of the frontend code unit is not due: `plans/frontend_app/` creates it with the first screen that applies a display rule.
- `standard_formatting.md`: checked automatically. `npx --no-install prettier --check "**/*.md"` passes, and `pytest tests/architecture/test_prose_style.py` -> 19 passed. `ruff format --check .` was not run: ruff is not installed on this machine, and no Python file changed. The script and the two style files, which the prose test does not scan yet, were checked with its function `resolve_forbidden_character_violations`: 0 violations, the longest line 196 characters.
- `standard_git.md`: checked automatically and manually. `pytest tests/architecture/test_conflict_markers.py` -> 8 passed. The agent made no commit and no push; the branch was moved forward to `dev` before the plan was written, without a merge commit.
- `standard_architecture.md`, `standard_config.md`, `standard_database.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md`, `standard_tests.md`, `standard_time.md` and `standard_worker.md`: not applicable. The change holds no Python code, no database object, no environment entry and no Python dependency.
- `standard_frontend.md`: checked manually, because its gates are not set up yet and no project exists to run them in. No address of a file the browser loads names an outside host, which the check of the generator verifies; the one new package is a development tool of the generator and no run time dependency; the code, the names and the documentation comments are in English; the script has no line comment; the script and the two style files pass prettier with the configuration of the repository; they hold no forbidden character. Tests of logic are missing (R-1).

Verdict: ready, for the scope of `plans/map_tiles/MAP_TILES_PLAN.md`, that is FR-1 - FR-6 as far as files can show them. It is not a verdict for the whole initiative: AC-2, AC-5 and the halves of AC-3 and AC-6 that need a drawn map are not checked, so the initiative does not qualify for the archive and its directory stays in `plans/`.

## Acceptance criteria checked on the drawn map, 2026-10-04

Checked by the agent that built `plans/frontend_app/`, in a browser at a width of 360 px, on the development server and on the built application of `frontend/`, on the machine of Adrian, with the archive at `frontend/public/tiles/krakow.pmtiles`. No review separate from that agent was made.

- AC-2: met. On the map of Czyżyny at zoom 15 the streets are white, the parks green, the water blue and the buildings a darker ground, and they are told apart; the names "Stanisława Lema" and "Aleja Pokoju" are readable; no icon of a point of interest is drawn. The colors are the ones of D-7 of the plan, read from the style. The names of the streets, `#4B5058`, have a contrast of 6.83 to 1 against the ground `#ECECE3` and 5.95 to 1 against a park `#D3E1CB`, above the 4.5 to 1 of level AA. With the interface in English the label of the city reads "Krakow", and the streets keep their local names.
- AC-3, the half about the requests: met for the run that was made. The map was moved with fifty presses of the arrow keys and zoomed in and out more than twenty times, and the list of the requests of the page named one host, the one of the page: the style, the fonts, the archive in byte ranges and the worker script of the map library. The run was shorter than the minute the criterion names.
- AC-5: met. The attribution `© OpenStreetMap` stands in the lower right corner of the map without any action. The map component lifts it above the edge of the panel that lies over the map, which had hidden it at first.
- AC-6, the half about the working map: met on one machine. The steps of `docs/setup/MAP_SETUP.md` were followed on the machine the archive was produced on; no second member of the team has followed them on a clean copy yet.

What this closes of the review above: R-1, the generator has unit tests now, `frontend/scripts/generate_base_map_style.test.ts`, run by the gate of the frontend; R-2, `frontend/package-lock.json` pins the style package 5.7.2 as a development dependency; R-3, the colors were seen on the drawn map; R-5, the label of the city sits at its place without the icon. F-19 of the plan was settled: the map component turns the two addresses of the style into full addresses of the page before it hands the style to MapLibre GL JS.

Still open: R-4, the backend persons have not confirmed D-1, and a second member of the team has not followed the instructions. Both are steps of a human, so the initiative stays in `plans/`.

## Closure

The user chose on 2026-10-04, while cleaning up `plans/`, to close the initiative without waiting for the two steps of a human the entry above leaves open: the confirmation of D-1 by the backend persons (R-4) and the steps of `docs/setup/MAP_SETUP.md` followed by a second member of the team on a clean copy. AC-1 - AC-6 are checked, AC-3 with a run shorter than the minute it names and AC-6 on one machine only, and check 6.4 of `FINAL_CHECKLIST.md` is ticked. The archive reaching the server is not carried by this initiative: D-1 hands it over as a file, and its loading is the matter of `plans/tile_loading/` and of check 3.4 of `FINAL_CHECKLIST.md`. This closure does not confirm that the archive is loaded on the server. The directory moves to `plans_finished/map_tiles/`.
