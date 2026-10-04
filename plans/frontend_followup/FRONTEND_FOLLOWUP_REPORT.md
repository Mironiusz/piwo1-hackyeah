# Report: What the web frontend still needs after the work of Kuba and Adrian

Document state: 2026-10-04, written by the agent for Adrian at the request of Rafał; a frozen record of the review, input to the `plan-shape` interview of this initiative

This report is not a shape, a PRD or a plan and decides nothing. Where it names product behavior it points to `docs/product/specification.md`, which prevails, and to `docs/product/api_contract.md`. It records the review asked for in `FRONTEND_FOLLOWUP_SEED.md`: what Kuba and Adrian delivered, and what the web frontend still lacks on that basis.

The reviewed state is `73a40b4` on `rm/requirements-preparation`, which contains `origin/dev` at `9b2b2ef`. At the time of the review no remote branch of Adrian or Kuba held a commit outside `origin/dev`.

## 1. What Adrian delivered

- `plans/frontend_app/` and `plans/map_tiles/`, in the commit `148e76d` merged as pull request 31.
- The single-page application of D-6 of `MVP.md` in `frontend/`: the needs, the map of facts with the fact detail, the votes and the flag, route planning with the address search and the point on the map, the route result with the legend and the list, reporting a point and an area, the account, moderation, the privacy information, the page about the data, and the Polish and English interface.
- The client of the sixteen operations of the contract in `frontend/src/api/client.ts`, with the renewal of the session token and the end of a session.
- The map drawn from the tile archive, the style and the fonts served by the project; check 6.4 of `FINAL_CHECKLIST.md` is ticked.
- A mock server in `frontend/mock-server/` and, by the review of the initiative, 573 unit tests and the four gates passing.
- Every acceptance criterion was checked on the mock server only, never on the service (`plans/frontend_app/FRONTEND_APP_REVIEW.md`, O-17). O9 was not built (O-16). The review still reads "implementation run in progress".

## 2. What Kuba delivered

- `plans/schema_first_revision/`: the package `db/` with the first revision of the target schema and its critical tests; check 2.2 is ticked.
- `plans/accounts/`: steps S-1 and S-3 only (`plans/accounts/ACCOUNTS_REVIEW.md`, the state line). S-1 narrowed the pseudonym rule of `docs/product/api_contract.md`, section `create_account`. S-3 wrote `service/account_rules.py`, `service/passwords.py` and `service/session_tokens.py` with their scenario tests. S-2 and S-4 - S-7, the operations themselves, wait for the code of `plans/backend_skeleton/`.
- `plans/community_facts/`: the shape only. Kuba cut its scope to the data layer of the nine operations and the status evaluator; the API and service layers have no executor (`docs/standards/decision_registry.md`, entry Executor of the API and service layers of the community facts).
- The accounts work and the community facts shape reached `dev` in pull request 32.

## 3. The service the frontend talks to

Function `build_app` of `api/app.py` registers no route, so no operation of the contract answers on the service yet. Checks 6.1 - 6.3 of `FINAL_CHECKLIST.md` are verified in the browser against the running service, so none of them can be ticked before the operations exist, whatever the frontend does.

## 4. Findings for the frontend

R-1 and R-2 are gaps the review found that `plans/frontend_app/` does not list. R-3 - R-7 are already open in `plans/frontend_app/` or depend on other initiatives, and are repeated here so that Adrian has one list.

### R-1. The pseudonym rule of the form is wider than the contract and the service

- Evidence: constant `PSEUDONYM_PATTERN` of `frontend/src/views/accountForm.ts` is `/^[\p{L}\p{N}_-]{3,30}$/u`, which accepts any Unicode letter and any Unicode number. `docs/product/api_contract.md`, section `create_account`, and D-3 of `plans/accounts/ACCOUNTS_PLAN.md` accept only the 26 Latin letters and the nine Polish letters `ąćęłńóśźż` in both cases, the digits `0` - `9`, `_` and `-`; constant `PSEUDONYM_CHARACTERS` of `service/account_rules.py` checks exactly that set.
- Effect: a pseudonym such as `Ünal`, or one written in Cyrillic, passes the form and is refused by the service with `invalid_request` on `pseudonym`. The form then shows the text `account.pseudonym.rule`, which says only "letters", so the person does not learn why.
- Related: function `trimPseudonym` uses `String.prototype.trim`, which removes every whitespace character, a tab and a no-break space included, while the contract and D-3 remove only the space U+0020 (function `resolve_pseudonym`). The form sends the trimmed name, so the only effect is that the client accepts what the service would refuse untrimmed.
- Related: function `isPasswordValid` checks only the minimum of 5 characters, while the contract allows 5 to 128 (constant `PASSWORD_MAX_LENGTH` of `service/account_rules.py`). A longer password is refused by the service with `invalid_request` on `password`, and the text `account.password.rule` names no maximum.
- Texts to follow the rule: `account.pseudonym.rule` and `account.password.rule` in `frontend/src/i18n/pl.ts`, `frontend/src/i18n/en.ts` and `docs/product/interface_texts.md`, section Account, V-11.
- Mock: the handler of `create_account` in `frontend/mock-server/server.mjs` still accepts any pseudonym without a control character, the rule from before version 11 of the specification, so a run on the mock does not show R-1.
- Login: the login form checks the same two rules as the registration form (`plans/frontend_app/FRONTEND_APP_REVIEW.md`, O-19), while `log_in` of the service checks only the shape and answers `invalid_credentials` (D-5 of `plans/accounts/ACCOUNTS_PLAN.md`). No account can hold a pseudonym outside the rule, so the difference changes only which message is shown.
- Confirmation: the change of the contract made by S-1 of `accounts` waits for the confirmation of Adrian (`MVP.md`, section Open decisions and confirmations; `docs/product/api_contract.md`, the state line). M9 of the specification still says only "letters, the Polish ones included"; Improvement 2 of `plans/accounts/ACCOUNTS_REVIEW.md` leaves carrying the set into the specification to Kuba, and that review finds no conflict between the two documents.

### R-2. The own vote is counted on the clock of the device, not in Europe/Warsaw

- Evidence: functions `toDeviceDay` and `startOfNextDay` of `frontend/src/state/ownVotes.ts` compute the day of a vote and the start of the next day in the time zone of the device. They are called after a vote by component `FactDetailPanel` of `frontend/src/views/FactDetailPanel.tsx` and by function `rememberConfirmation` of `frontend/src/views/report/reportSteps.ts`, and `startOfNextDay` is the fallback of the text `vote.too_soon` when a refusal carries no `repeat_allowed_at`.
- Rule: M4 of the specification counts the vote limit by calendar day in the Europe/Warsaw zone, also for the own vote the app shows (version 13, in the introduction of the specification). `docs/product/api_contract.md`, section Conventions, says that a day is computed by the service and that the client converts no time zone. The response `201` of `cast_vote` carries no instant of the next vote, so the client has to compute it, and the rule says in which zone.
- Effect: none on a device set to the Polish zone. On a device in another zone, for example a laptop set to UTC, the vote controls unlock at the wrong hour and the day of the own vote shown by `vote.own.saved` can differ from the day of the service. A vote sent too early is refused with `vote_too_soon`, which the frontend already shows, so no wrong data is stored.
- Origin: the clock of the device was an agent decision recorded as O-25 of `plans/frontend_app/FRONTEND_APP_REVIEW.md`; D-12 of `plans/frontend_app/FRONTEND_APP_PLAN.md` still describes the kept value as an instant.
- One possible way, not decided here: compute both values with `Intl.DateTimeFormat` and `timeZone: "Europe/Warsaw"`.

### R-3. The run against the service

Step 12 of `plans/frontend_app/FRONTEND_APP_PLAN.md` was not run (O-17 of its review): the development server with `VITE_API_PROXY_TARGET` set to the address of a running service, and the main scenario checked on it. It waits for section 3 of this report and is what ticks checks 6.1 - 6.3.

### R-4. Open points already listed for Adrian

`plans/frontend_app/FRONTEND_APP_REVIEW.md`, section Open points for Adrian: the rule for the labels of the stops on the summary line (O-10), whether the account says anything about the needs (O-19), the 62 texts added during the build in `docs/product/interface_texts.md`, section Texts added while the views were built, and the loading step of `map_tiles` that check 3.4 of `FINAL_CHECKLIST.md` still names.

### R-5. O9, routes with public transport

Step 11 of `plans/frontend_app/FRONTEND_APP_PLAN.md` was skipped (O-16): `docs/product/api_contract.md` holds no interface of O9 yet. It waits for `plans/public_transport_routing/` and is optional (check 4.2 of `FINAL_CHECKLIST.md`).

### R-6. The check with a screen reader on a phone

AC-14 of `plans/frontend_app/FRONTEND_APP_PRD.md` is open for the part an agent cannot check: the main scenario with a screen reader on a phone, a step of a human.

### R-7. A coming change of the check for existing facts

Requirements 3 and 9 of `plans/community_facts/COMMUNITY_FACTS_SHAPE.md` leave a fact removed in OpenStreetMap out of `find_nearby_facts`, through a new version of the specification and a change of the contract that joins the confirmation of Kuber and Adrian still outstanding for D-12 of `MVP.md`. The views show what the service returns, so they need no change; the handler of `find_nearby_facts` in `frontend/mock-server/server.mjs` would follow. Nothing is to be built before the specification changes.

## 5. Outside the frontend, but blocking it

- B-1. No operation of the contract answers on the service (section 3). The operations of `accounts` wait for `plans/backend_skeleton/`, owned by Marek.
- B-2. The API and service layers of the nine operations of the community facts have no executor; Rafał and Marek name one before check 5.1 starts (`docs/standards/decision_registry.md`, entry Executor of the API and service layers of the community facts).
- B-3. The server of the demo has to answer every path that is not a file and does not start with `/api/` with the page of the application, and to serve `/tiles/krakow.pmtiles` with byte ranges and the map style and fonts under `/map/` (`MVP.md`, section Open decisions and confirmations, the item on the addresses of the views of the web frontend). This belongs to `plans/deployment_config/`, owned by Rafał, and is not confirmed yet; without it a reload of any view other than the map of facts fails on the hosted demo.
- B-4. The machine that builds the frontend needs Node.js 22.22.0 or newer, which `react-router` asks for (`plans/frontend_app/FRONTEND_APP_REVIEW.md`, O-2).

## 6. What the review did not check

- No test or gate of the frontend was run: `frontend/node_modules` was absent. The number of tests in section 1 comes from the review of `frontend_app`.
- The application was not run in a browser.
- Not every view was read. The review read the places where the work of Kuba meets the frontend: the account form, the own votes, moderation, the client of the contract and the types of the closed lists. In those places it found no other gap: the fact types, sources and verdicts of `frontend/src/api/types.ts` match `db/accessibility_db/closed_lists.py`; function `splitFlaggedFacts` of `frontend/src/views/moderationLists.ts` keeps the order of the service, which requirement 7 of the community facts shape sets; and the client keeps a renewed token also from a refused request, which D-8 of `plans/accounts/ACCOUNTS_PLAN.md` sends.
- Whether R-3 - R-7 move into this initiative or stay with `plans/frontend_app/` is not decided here.
