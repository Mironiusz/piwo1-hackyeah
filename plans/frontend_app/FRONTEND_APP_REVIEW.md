# Review: Web frontend of the MVP

Document state: 2026-10-04, implementation run closed and reviewed as not ready for the whole initiative: one blocker waits for a decision of Adrian, the run against the service was not made and AC-16 is not built; the initiative stays in `plans/`

## Implementation run of 2026-10-04

### Check before implementation

- The facts of `plans/frontend_app/FRONTEND_APP_PLAN.md` were checked again at 03:30. `HEAD` was `a6255ed`, equal to `origin/dev`, and no commit touched a file the facts cite since the plan was written, so the line references of F-5 - F-14 and F-17 - F-20 stand.
- Runs repeated with the same result: F-1 (`git status --short -uall frontend` lists the twelve files of `plans/map_tiles/`), F-2 (`node --version` -> `v22.20.0`, `npm --version` -> `11.21.0`) and F-15 (`node frontend/scripts/generate_base_map_style.mjs --check` ends with 0).
- F-3 holds after the install: the template `react-ts` of `npm create vite@9.2.1` gives the ranges React `^19.2.8`, Vite `^8.3.0`, TypeScript `~6.0.2` and oxlint `^1.81.0`, and `npm ls` shows them resolved to React 19.3.0, Vite 8.3.2, TypeScript 6.0.3 and oxlint 1.86.0, pinned by `frontend/package-lock.json`.
- F-16 was settled by the run: the map component turns the two addresses of the style into full addresses of the page, and the map draws from the archive.
- `plans/frontend_app/FRONTEND_APP_SHAPE.md` has no question marked `Block: yes`; its regulator is C:60.
- No sign of another session on the tree: `git status` showed only the files of the two initiatives of the frontend.
- Baseline of the checks: `python -m pytest tests/architecture -q -o addopts=""` passes, 120 tests.

### How the work was split

The foundation, the needs, the map of facts with the fact detail, route planning with the address search and the point on the map, and the route result were written by the lead agent. Three more agents worked in parallel on files of their own, each on the model Opus: one on the account, moderation, the privacy information and the page about the data (steps 7 - 9), one on reporting a point and an area (steps 6 and 10), and one on the unit tests and the gates (steps 1.3 and 1.12). The lead agent checked every view in a browser. After the run a reviewer separate from the builders, the agent `dod-reviewer` on the model Opus, read the change; its findings stand under Review.

### Deviations from the plan

O-1. The template of step 1.1 has no `src/vite-env.d.ts`: it declares the types of Vite in `tsconfig.app.json`. The file was not created. The template also ships its own `.oxlintrc.json`, which was taken over and extended, and its three `tsconfig` files had line comments, which were removed because the repository allows none.

O-2. `npm install` warns that `react-router` 8.4.0 asks for Node.js 22.22.0 or newer, while the machine has 22.20.0 (F-2). The install succeeds and the application runs. A machine that builds the frontend should have Node.js 22.22.0 or newer.

O-3. `frontend/vite.config.ts` passes `/api` to the proxy target also in `preview`, which the plan names only for the development server. Without it the built application could not be checked on the mock. Agent decision at C:60, without asking: the build itself still has no proxy.

O-4. Files the plan does not name, all without a second owner: `src/map/mapScene.ts` (the scene a view puts on the map, and the hooks `useMapScene` and `useMap`), `src/parts/iconPaths.ts`, `src/parts/factText.ts`, `src/parts/styles.ts`, `src/parts/routeSummary.ts`, `src/state/lastMapPath.ts`, `src/views/factDetail.ts` and `src/views/routeText.ts`. Exports the plan does not name: `onSessionEnd` of the client, by which the session provider learns that the service ended a session; `toApiError`; `useLanguage`; `toDeviceDay`, `toDeviceInstant` and `oneDayAfter` next to the own votes; `findRouteBounds`; `INITIAL_MAP_VIEW` and `FACTS_MIN_ZOOM` next to the bounds of Kraków. Agent decision at C:60, without asking: each is a part of a file the plan names, split off so that a component file exports one component.

O-5. The error codes of the frontend have one code the contract does not: `network_error`, for a request that got no answer at all. It maps to the text `state.offline`. Agent decision at C:60, without asking: the catalogue of texts has this message, and no code of the contract fits it.

O-6. The map has two zoom buttons, which no mock draws. Without them zooming needs a pinch or a double tap, and WCAG 2.2 asks for a way with a single pointer and without a path. Their names are in both dictionaries. Agent decision at C:60, without asking: AC-14 asks for level AA.

O-7. The markers of the map are buttons with a text name, as D-13 says, and are left out of the order of the Tab key. `docs/product/views.md` asks that the map is one stop the keyboard can leave and that everything the map shows is in the panel as text; the list under the map holds the same facts as links. Agent decision at C:60, without asking. The review reads this as a deviation from `docs/standards/standard_frontend.md` and not only from the plan: B-1 under Review.

O-8. The map has one of three fixed heights instead of growing with the screen, as every mock draws it: 262 px, 190 px for the address search and 380 px while a point is picked, each capped by a share of the height of the screen. A map that changed its size with the length of the list under it would rest again and ask for facts again, which FR-15 forbids.

O-9. A Polish day keeps the two digits of its month and drops the leading zero of its day, `3.10.2026` and `12.05.2025`, because the mocks and the catalogue of texts show both forms.

O-10. The labels of the stops on the summary line of the route: `docs/product/views.md` leaves the rule for many or close barriers open and asks the builder to put it to the user. A label is left out when it would run into the label before it; the stop stays, and the text of the stretches and the list name every barrier. Agent decision at C:60, without asking: Adrian was not asked during the night run, the rule changes nothing a person can learn from the view, and it is one function, `placeSummaryStops`. It is listed for Adrian in the summary of the run.

O-11. On the first opening the view of the needs keeps the bottom bar and the menu, which its mock does not draw, and shows the language switch in the header, which its mock does draw. AC-3 asks that both are reachable from every view.

O-12. The detail of a fact shows every day the service gave: the day of the last edit of the map data and the day of the last confirmation. The mock shows one day. The contract says the client shows every day that is not null.

O-13. The mock server holds three rules the plan does not list: a fact created through it is no sample data, so both forms of a row can be seen; a rectangle that holds the place "Rynek Główny" is answered as cut off, so the state of too many facts can be reached; and the facts of a route are put at their places on the route that was asked for, with the identifiers 9001 - 9006, so the detail and the votes work on them.

O-14. The part `Note` takes `announce` instead of the attribute `role`, and a status message outside it is the element `output`: the linter, with every rule of `jsx-a11y` an error, refuses a literal role where an element exists.

O-15. The texts the build needed beyond the catalogue were added to both dictionaries and to `docs/product/interface_texts.md`, section Texts added while the views were built. They were not approved one by one.

O-16. Step 11 was skipped: `docs/product/api_contract.md` holds no interface of O9 (`grep -c "transit\|public_transport" docs/product/api_contract.md` -> `0`). AC-16 is recorded as not built.

O-17. Step 12 was not run: no backend runs on this machine, and none was reachable during the run. Every check below was made on the mock server. The types change only after the contract does.

O-18. The pages - the account, the privacy information, the page about the data and moderation - start with a back control above their heading, as their mocks draw it. It goes one step back in the history of the browser, or to the map view a person left when the page is the first address of the visit.

O-19. The account. The view of deleting an account does not show the line that the needs stay on the device (`account.delete.stays.needs`), which its mock shows, while the logged in state shows the sentence that the needs are not part of the account (`account.needs`), as its mock does. `docs/product/views.md`, V-11, says the view says nothing about the needs; the mocks and the catalogue of texts, which Adrian reviewed later, say otherwise. Two sources differ, so this is listed for Adrian in the summary of the run. The form for logging in checks the same two rules as the form for creating an account.

O-20. Moderation uses buttons of the full height instead of the small ones of its mock, and puts the day of the flag on a row of its own, because in Polish the source with its day and the day of the flag read alike side by side. A page of moderation that is denied to a person without a session offers the way to log in.

O-21. Reporting. The key of a save is made with `crypto.randomUUID()` where the browser has it and from `crypto.getRandomValues` otherwise, because a page served over plain HTTP, as the hosted demo is, has no `randomUUID`; without it every save on the demo would fail. The key is dropped also when the service answers `idempotency_key_reused`, because no further attempt with it could succeed. The kind starts on the barrier, as its mock shows. The number of steps is a text field with the numeric keyboard, so a wrong text gets its message instead of being read as empty. The place step has a control that moves the focus to the map, because the step opens with the focus on its heading, which stands after the map. The detail of a fact cannot be opened from the existing facts of step 4; each of them shows what a row shows and its description. The answer that the report is the same fact is not held back by the vote the device remembers: the service decides, and its refusal is shown as the plain message.

O-22. The session. The state of the session gained two things the plan does not name, after the agent of the pages found them missing: whether the kept token is still being checked, so the account page does not show the form for logging in to a person who is logged in, and a way to read the account again, used when the service refuses a moderator action for the role, so the menu loses the entry.

O-23. The client of the contract. A renewed token is kept, and an answer that the session expired ends the session, only while the token the request carried is still the kept one. The first half was a defect the tests found: the answer to a request that left before a logout logged the person in again. Both are in `frontend/src/api/client.ts` with their tests.

O-24. The tests and the gates. `frontend/tsconfig.node.json` includes `scripts`, so the test of the style generator is type checked, with a declaration file next to the generator. The tests share `frontend/src/testing/memoryStorage.ts`. The agents wrote tests also for the helpers of their views, which D-16 does not list. `tests/architecture/test_prose_style.py` got a second new test, for every suffix and for a binary file.

O-25. After the merge with `dev` at 05:16 the frontend follows version 13 of the specification and the changed contract: a person has one vote on a fact in a calendar day, and the refusal carries the start of the next day. The device remembers the start of the next calendar day on its own clock in place of the moment 24 hours later, the two texts `vote.own.saved` and `vote.too_soon` are the ones the catalogue has now, the message names a day and not a day with an hour, and the function that wrote a day with an hour is removed with its tests, because no text uses it. The mock server refuses a second vote on the same calendar day. D-12 of the plan still describes the kept value: an instant.

O-26. After the review the code changed in three places the plan describes otherwise, each answering a finding listed under Review. The device keeps the voter with an own vote, the pseudonym of the account of the session or nobody, and shows the vote only to that voter (D-12 names the verdict, the day and the instant). The state of the session keeps the error of a check of the kept token that got no answer. `frontend/src/map/focusMap.ts` is a file the plan does not name: the control that moves the focus to the map, which the place step of a report had, is now shared with the view that picks an end of a route. A saved report is also remembered on the device as the own vote of its author, because specification M4 says that a report carries the confirmation of its author and that the application shows a person their own latest vote; before, the detail of a fresh report offered both votes and the service refused the vote. Agent decision at C:60, without asking, for all four: each follows the specification or a rule of the standard, and none changes a contract.

O-27. After the second merge with `dev` at 05:46 the form of the account checks the pseudonym against the letters the contract now names: the 26 Latin letters and the nine Polish letters in both cases, the digits 0 to 9, the underscore and the hyphen. Before, the form accepted a letter or a digit of any alphabet, which the service refuses. The contract says itself that this change waits for the confirmation of Adrian; the form follows the contract as it stands on `dev`.

### Merge with dev, 2026-10-04 05:16

- On the request of Adrian the latest `origin/dev`, `afe5bc1`, was brought into the branch while the review ran. The branch had no commit of its own, so it was moved forward, and the uncommitted work was carried over with `git stash` and `git stash pop`, without a conflict left in the tree. One file needed a decision: in `MVP.md` the team had rewritten the table of initiatives, so the row of `map_tiles` was written again into the new table, and the list of the order, which the team replaced, was left as the team wrote it.
- The fact check was repeated for the files the merge changed. Every claim of F-5 - F-20 holds. The line references moved for F-9, F-13, F-14 and F-19, `plans/deployment_config/` of F-5 holds a second file, and F-12 names the debt this run removed. One change is of substance: the vote rule of O-25. The pseudonym rule of the contract now equals the one the frontend checks (D-15), and `plans/mvp/` is `plans_finished/mvp/`, which the PRD and the shape of this initiative now name.
- After the merge `python -m pytest tests/architecture -q -o addopts=""` fails in two tests of the prose style, on files that came with `dev`: bold in prose in four documents under `mobile_app/`, and forbidden characters in a document of a package under `mobile_app/accessway/oh_modules/`. No file of this run is among them; they belong to the owner of `mobile_app/` and were left as they are. For the same reason `npx --no-install prettier --check "**/*.md"` now names eight files, all under `mobile_app/`; every other document passes.
- At 05:25 Adrian committed the run as `148e76d`, and at 05:26 it was merged into `dev` through pull request 31 as `31ab1cb`, before the review was closed. The branch was moved forward to `31ab1cb`, which holds the same tree. What changed after the review is not committed.
- At 05:46 `dev` had moved again, to `9b2b2ef`, with the accounts of the service. The branch was moved forward to it; no file it changed was changed in the working tree. The fact check was repeated for the three files of it this initiative cites: `docs/product/api_contract.md` makes the letters of a pseudonym explicit and refuses a lone surrogate (O-27), `makefile` gained two lines of the security target and keeps the frontend targets, and `MVP.md` keeps the row of `map_tiles` and the requirement for the server of the demo.

### What was done

- Step 1, the foundation: the project from the Vite template with the packages of D-9, the proxy of the development server, the four gates with their `make` targets and the extended forbidden characters check, the theme with the tokens of the mocks, the two dictionaries with the formats, the types and the client of the sixteen operations, the state on the device and across views, the shell with its menu, the shared parts, the one map with its scene, the mock server with its data, and the unit tests.
- Step 2: the needs, with the first opening and the way to skip.
- Step 3: the map of facts with its list, its switch and its states, and the detail of a fact with the votes, the own vote and the flag.
- Step 4: route planning, the address search and the point on the map.
- Step 5: the route result with the summary line, the tiles, the legend, the note, the three groups, the alternative, the route with the fewest barriers and the neutral route, and the pair `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md`.
- Steps 6 and 10: reporting a barrier, an amenity and an area.
- Step 7: the privacy information and the page about the data. Step 8: the account. Step 9: moderation.
- Step 11: skipped (O-16). Step 12: not run (O-17).
- Step 13: the four criteria of `plans/map_tiles/` are recorded in its review; `docs/product/accessibility_status.md` is written; `docs/standards/standard_frontend.md` names the three packages, the mock and the targets of the gates; the debt on the gates is removed from `docs/standards/README.md`; `docs/setup/MAP_SETUP.md` tells how to run the frontend on the archive; `MVP.md` names the requirement for the server of the demo; the 62 texts added during the build stand in `docs/product/interface_texts.md`; the memory entry stands in `agent_docs/memory/frontend/_shared.md`.

### Checks of the Definition of Done

- Last run, after the merge with `dev` and after the changes that followed the review: `npm --prefix frontend run typecheck` -> exit 0. `npm --prefix frontend run lint` -> exit 0, no finding. `npm --prefix frontend run test` -> 17 files, 580 tests passed. `npm --prefix frontend run build` -> exit 0. `make` is not installed on this machine, so the targets were checked by running their commands.
- `python -m pytest tests/architecture -q -o addopts=""` -> 122 passed before the merge, with the prose test extended to the frontend files; after the merge 127 passed, 3 skipped and 2 failed, both on files under `mobile_app/` that came with `dev` (see Merge with dev). `npx --no-install prettier --check "frontend/**/*.{ts,tsx,css,html,json,mjs}"` and `npx --no-install prettier --check "**/*.md"` -> all files pass.
- `node frontend/scripts/generate_base_map_style.mjs --check` -> `Both style files are up to date and keep every rule.`
- `npm --prefix frontend run build` -> exit 0. The built files hold no address of the mock and no text of its data (`grep -c` for the port and for a sample address -> 0), and the built application drew the map and its first opening when served by `vite preview`.
- `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md` exist.
- The list of the requests of the page, read in the browser after the main scenario on the development server and on the built application, names one host, the one of the page.

### Acceptance criteria

Every criterion was checked by the lead agent in a browser at a width of 360 px on the mock server; none was checked on the service (O-17).

- AC-1: met. The four gates pass, and the pair of documents exists.
- AC-2: met on the mock. After the needs, a route, its list, a report and a vote the page had sent requests to one host.
- AC-3: met. The bottom bar and the menu stand in every view; the menu shows Moderation for the account `moderator` and not for an account without the role or for a person without an account.
- AC-4: met. A device without kept needs opens on the needs, with the way to skip; the preset for a baby stroller sets stairs, high kerb, poor surface and narrow passage to avoid and elevator, ramp and lowered kerb as needed, and nothing else; stairs unticked with the Space key stay unticked in the storage of the device, which the application reads at its start; needs without a barrier show the note.
- AC-5: met. The map of facts shows the facts of the needs, and every fact after the switch, and the list holds the same facts; a row shows the status, the source with its day and the sample data mark; after a vote the detail shows the status, the own vote and both votes inactive; a vote repeated on another empty device is answered with the message that names the day from which the next vote is possible; an outdated fact has a muted marker, its status and both votes; a fact from the map data has no flag action. After the review: a vote cast without an account is not shown to an account that opens the same fact, which can vote, and a saved report shows its author the own vote on the new fact.
- AC-6: met, with one part not reachable in the test. The start was given by an address and by a point on the map, the destination by an address; the location of the device was refused by the test browser and gave its message. One match of the search is a list, and nothing is set until it is picked; nothing found and the search not answering give different messages; routing that does not answer gives the plain message and no route. A point outside Kraków is checked in the code and in the unit tests of the bounds, and was not reached in the browser, because the map does not move outside its bounds.
- AC-7: met. The four states are told apart in a grayscale screenshot of the legend, the summary line and the map; the list has the three groups with the type, the source, the day and the status of every item; a route with a stretch without data shows the one note; an unverified barrier of the needs gives one proposal with the barrier and its status, the alternative is shown without a new request and the way back restores the first route; a route without a way free of barriers says so and lists the barrier; needs without a barrier give the hollow line and the statement; a barrier outside the needs has no marker.
- AC-8: met. A report of stairs at the place of existing stairs shows the existing fact and asks; the answer that it is the same sent one vote and no report; nothing but the check for existing facts was sent before the summary was approved; the saved state offers only a new report and the way to the map. An area was created from the first focus to the saved state with the keyboard alone, the place given by the address search. The repeated save with the same key is covered by the unit tests of the flow and was not provoked in the browser.
- AC-9: met. Creating an account shows both rules and the statement on the password; a taken pseudonym, a broken rule and a failed login give their messages; a token the service refuses shows once that the session ended, with the way to log in; deleting takes one confirmation and no password; the needs in the storage stayed the same through logging in and out. After the review: with the mock stopped, the account page of a device that keeps a token shows the message that something went wrong with the way to try again, and no form for logging in.
- AC-10: met. A flagged report appeared in moderation, was gone from the map of facts after hiding and back after restoring; an account without the role and a person without an account see that the view is for a moderator.
- AC-11: met. The privacy information lists the two kept items with purpose and retention, the four items that are not kept, and the deletion on 4 October 2026, in both languages; the page about the data shows the day of the copy; the name OpenStreetMap stands in two texts of the page about the data and in the attribution on the map, and nowhere else in the dictionaries.
- AC-12: met for the states that could be reached on the mock. Not reached in the browser: more facts than an answer holds, a point outside Kraków, a fact hidden while its detail is open, a save that failed. Their code and texts exist. A map that cannot be drawn was reached after the review, with the tile archive moved aside: the message stands in place of the map, and the list shows the facts around the place the map would have opened on.
- AC-13: met. A browser set to English started the built application in English; the start in Polish for a browser set to Polish is covered by the unit test of the detection, and the stored choice of Polish started the application in Polish; the switch changed the language of a shown route without a route request; the main scenario ran at 360 px; at 1280 px the application is one centered column without a horizontal scroll.
- AC-14: met for what an agent can check, open for the rest. The main scenario and the report of an area were completed with the keyboard alone, the contrast was computed, the grayscale screenshot was read, and `docs/product/accessibility_status.md` names the start from the current location as not working on the hosted link. The check with a screen reader on a phone is a step of a human and was not made.
- AC-15: met. Fifty presses of the arrow keys on the map sent no request while the map moved and one after it stopped, and two zoom steps sent one each; zoomed out, the map sent none and asked to zoom in; typing in the search field sent nothing until the text was submitted; five changed items of the needs and the return to the shown route sent one route request.
- AC-16: not built (O-16).

### Review

The change was reviewed by the agent `dod-reviewer` on the model Opus, in read-only mode, between 04:56 and 05:23, on the tree as it stood before the merge with `dev`. Its coverage is partial: it stopped at its call limit. It read the client and the types against the contract, the map component, the state on the device, the session, and the views of the facts, of the account and of the place of a report. It did not read `src/shell`, `src/parts`, `src/hooks`, `src/format`, the texts of the dictionaries, the mock server, most of the summary step of a report, the tests, or the pair of documents against the code.

Blocker:

- B-1. The markers of the map cannot be reached with the keyboard: `frontend/src/map/MapView.tsx` gives every marker button `tabIndex` -1, while `docs/standards/standard_frontend.md`, in its accessibility rules and in its checklist, asks that every interactive element is reachable with the keyboard. The demo is not hurt, because the list under the map opens the same facts, and `docs/product/views.md` asks that the map is one stop the keyboard can leave. Two sources differ, so this is a decision of Adrian: the exception is written into the standard, or the markers enter the order of the Tab key. Open.

Risks:

- R-1. Nothing ran against the service (O-17), and the branch was behind `dev`. The reviewer read all sixteen operations of the client against the contract and found them equal in path, method, token use, error body and every field. The merge is done (see Merge with dev); the run against the service stays open.
- R-2. A tile archive that cannot be read gave a blank map without a message. Fixed after the review: the map component listens for the errors of the map and tells that the map failed when the base map source cannot be read.
- R-3. The device remembered a vote for a fact and not for a person, so a second person on the same device could not vote although the service would accept the vote. Fixed after the review (O-26). The limit itself is a rule of specification M4, which says that the application keeps the controls inactive until the next calendar day; the device counts that day on its own clock, which differs from the Europe/Warsaw day of the service on a device in another time zone.
- R-4. When the check of the kept token got no answer, the account page showed the form for logging in while the token still travelled with every request. Fixed after the review (O-26).
- R-5. Decisions taken without Adrian: O-10, O-15 and O-19. They stand under Open points for Adrian.
- R-6. Five changed files lay outside the scope the reviewer was given and were not reviewed: `.gitignore`, `.impeccable/briefs/views.md`, `PRODUCT.md`, `docs/product/user_journeys.md` and `docs/product/views.md`. They were changed in the working tree before this run, and went into the commit of Adrian with it.

Improvements, all three made after the review:

- The list of the map of facts said that no fact is known for the moment before the map rested for the first time. It now says that it is loading.
- The detail of a fact wrote the unit of the radius as a literal. It now uses the distance format, as the report does.
- The view that picks an end of a route had no control that moves the focus to the map. It now has the one of the place step of a report.

Verification, as the reviewer reported it, before the merge with `dev`:

- `standard_agentic_workflow`, `standard_agent_docs`, `standard_git`: checked automatically, their tests are among the 122 that passed.
- `standard_review`: checked manually.
- `standard_documentation`: not checked.
- `standard_formatting`: checked automatically, both prettier checks and the prose test pass; `ruff format` did not run, because `ruff` is not installed.
- `standard_frontend`: checked automatically, the four gates pass; its checklist manually, in part.
- `standard_tests`: checked automatically, `tests/architecture` only.
- `standard_code_quality`, `standard_naming`: not checked, because `ruff` and `mypy` are not installed; they apply to `tests/architecture/test_prose_style.py`.
- `standard_architecture`, `standard_config`, `standard_database`, `standard_errors`, `standard_idempotency`, `standard_logging`, `standard_security`, `standard_time`, `standard_worker`: not applicable, the change holds no backend code.
- Also checked by the reviewer: no line comment in the frontend files, no function without a documentation comment, no address of another host in `frontend/src` or `index.html`, no dictionary key missing in either language, the name OpenStreetMap only in the two texts of the page about the data, and two contrast ratios of `docs/product/accessibility_status.md` recomputed.

Verdict of the review: not ready. Scope: the whole initiative `frontend_app`. B-1 blocks under the strict deviation rule, step 12 was never run, AC-16 is not built and the steps of a human are open. In the files it read the reviewer found no defect that breaks the demo, and every gate passed; once B-1 is decided, that part needs only minor fixes. The initiative does not qualify for `plans_finished/` and stays in `plans/`.

What changed after the review was checked by the lead agent and not by the reviewer: the four gates pass, and each change was seen in a browser at 360 px on the mock. The map of facts starts with the loading text and never with the text that no fact is known; the view that picks an end of a route moves the focus to the map and keeps both actions on a screen of 360 by 640 px; a vote cast without an account leaves both votes active for an account on the same fact, and the vote of the account is kept with its pseudonym; with the mock stopped the account page shows the message with the way to try again, and after the mock started again the retry ended in the notice of an ended session; a pseudonym with letters of another alphabet is refused by the form with its rule and no request; with the tile archive moved aside the message stands in place of the map and the list shows the facts; with the archive back the map draws; a saved report shows its author the own vote on the new fact with both votes inactive.

### Open points for Adrian

- B-1 of the review: the exception for the markers of the map in `docs/standards/standard_frontend.md`, or the markers in the order of the Tab key.
- The rule for the labels of the stops on the summary line (O-10).
- Whether the account says anything about the needs (O-19).
- The 62 texts added during the build, in `docs/product/interface_texts.md`, section Texts added while the views were built.
- `FINAL_CHECKLIST.md`, which came with `dev`, still names a loading step of `map_tiles` in its check 3.4, while D-1 of `plans/map_tiles/MAP_TILES_PLAN.md` hands the archive to the backend persons as a file. `MVP.md` lists it under Open decisions and confirmations.

### Steps of a human still open

- The commit and the push of what changed after the review, and the pull request to `dev`. The run itself is committed and merged (`148e76d`, pull request 31).
- Telling the owner of `plans/deployment_config/` that the server answers every path that is not a file and does not start with `/api/` with the page, and serves `/tiles/krakow.pmtiles` with byte ranges and `/map/`.
- Step 12: the run against the service, once one runs: `VITE_API_PROXY_TARGET` set to its address for `npm --prefix frontend run dev`.
- The check of the main scenario with a screen reader on a phone.
- The confirmation of the contract and of the shape by Kuber.
