# Plan: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03, plan in progress

## Goal

Define and implement the API operations required by `plans/api_contract/API_CONTRACT_PRD.md` for the Web client and a possible HarmonyOS client. Keep the contract and implementation consistent with the agreed product behavior, the routing and account-session decisions, and the backend architecture settled in `plans/mvp/MVP_PLAN.md`.

## Facts

F-1. The PRD requires requests, responses and failure outcomes for all mandatory MVP behavior crossing the client-service boundary, shared by Web and a possible HarmonyOS client. | doc:`plans/api_contract/API_CONTRACT_PRD.md` section Scope, lines 13-19; section Functional requirements, lines 29-45 | 2026-10-03
F-2. Endpoint implementation waits for the domain model, database schema, backend architecture and anonymous vote identifier to be settled in `plans/mvp/MVP_PLAN.md` Q-10. | doc:`plans/api_contract/API_CONTRACT_PRD.md` section Dependencies and impact on other modules, lines 76-81; doc:`plans/mvp/MVP_PLAN.md` section Open questions, lines 42-52 | 2026-10-03
F-3. The backend stack is Python 3.13 with FastAPI and PostgreSQL with PostGIS, while backend module boundaries remain delegated to Q-10. | doc:`plans/mvp/MVP_PLAN.md` section Decisions, lines 23-29; section Open questions, lines 51-52 | 2026-10-03
F-4. Address search is a backend operation; its input is sent in a POST request body and it distinguishes matches, no matches, unavailability and invalid caller input. The exact path and JSON request and response shape belong to this initiative. | doc:`plans/geocoding/GEOCODING_PLAN.md` D-3, D-4, D-7 and D-11, lines 40-56; doc:`plans/api_contract/API_CONTRACT_PRD.md` AC-6, line 59 | 2026-10-03
F-5. Route composition and account actor resolution are not settled in this initiative's inputs yet. Their contract details must follow the respective initiatives and be agreed with the frontend consumer. | doc:`plans/api_contract/API_CONTRACT_PRD.md` section Dependencies and impact on other modules, lines 76-81; doc:`plans/account_sessions/ACCOUNT_SESSIONS_PRD.md` section Risks and notes, line 84 | 2026-10-03
F-6. The repository has no backend or API implementation files; the matching files under `src/`, `app/` and `backend/` are absent. | cmd:`rg --files` filtered for `src/`, `app/`, `backend/`, `openapi` and `schema` -> no matching files; only architecture tests are present under `tests/` | 2026-10-03

## Decisions

D-1. Address search uses POST and keeps search text out of the URL. The response distinguishes a list of matches, an empty list, an unavailable search outcome and invalid input, as specified in `plans/geocoding/GEOCODING_PLAN.md`. This is a settled input constraint, not a new API shape decision.

D-2. Stable client-facing codes are the default; clients translate them to Polish or English. Localized response text is included only where the PRD requires it. | `plans/api_contract/API_CONTRACT_PRD.md`, domain rules

D-3. The plan remains in progress until the frontend consultation, dependent initiative decisions and Q-10 provide enough information to name concrete API and backend artifacts without guessing their contracts or architecture.

## Scope of changes

1. Record the shared client-service contract in the agreed contract artifact, covering route planning, route findings, nearby-fact comparison, reports, votes, geozones, OpenStreetMap freshness, account operations, moderation, address search, request failures, stable codes and privacy constraints from FR-1 through FR-8. The artifact format and path remain open until the frontend consumer confirms what it can use.
2. After the frontend review, `plans/routing_engine/` and `plans/account_sessions/` settle their decisions, and `plans/mvp/MVP_PLAN.md` Q-10 settles the backend architecture and domain model, name the exact backend files and operations needed to implement the agreed contract. Add those concrete paths to this section before closing the plan.
3. Implement the agreed API operations in the backend files selected by Q-10, including address search under the constraints in `plans/geocoding/GEOCODING_PLAN.md` D-3, D-4, D-7 and D-11. Preserve the PRD's authorization, privacy, reliability and logging rules.
4. Add tests for the API behavior and contract errors in the test files selected by the backend architecture and `docs/standards/standard_tests.md`. Cover the PRD acceptance criteria, including anonymous and moderator access, duplicate voting, unavailable routing and search, and exclusion of private fields from responses and request logs.

## Rollout order

1. Consult the frontend owner on the contract artifact format, operation set, request and response shapes, and error outcomes. Record agreed details here and in the contract artifact.
2. Incorporate the results of `plans/routing_engine/` and `plans/account_sessions/`; do not invent route result fields or request actor behavior before those decisions are recorded.
3. Wait for Q-10 in `plans/mvp/MVP_PLAN.md`. Then replace the pending implementation references in `Scope of changes` with exact module, function, contract and test names derived from the selected architecture.
4. Implement the service operations and tests in dependency order, keeping the OpenAPI or other agreed contract artifact synchronized with the implementation.
5. Verify every PRD acceptance criterion and the applicable repository standards. Update this plan with the verification results before closing it.

Human steps: the backend owner makes the technical decisions in this initiative and consults the frontend owner as the contract's first consumer. Any shared database operation, target-environment action or publication remains governed by the applicable repository rules.

## Definition of Done

- The frontend owner has reviewed and agreed to the contract artifact.
- The exact operations, paths, request and response shapes, authorization outcomes and stable error codes are written in the agreed artifact and meet `API_CONTRACT_PRD.md` FR-1 through FR-8 and AC-1 through AC-8.
- The backend files and tests are named explicitly in this plan after Q-10 and implement the agreed contract.
- Both clients can consume the same contract; route, account and moderation behavior matches the decisions in their owning initiatives.
- Address search preserves the POST-body privacy constraint and its four distinct input and service outcomes.
- No response exposes contribution identity, account state of a contributor, contribution weights, internal exception details or infrastructure details. Request logs meet AC-8.
- All applicable checks required by `docs/standards/standard_review.md` pass.

## Risks

- The routing engine and account-session initiatives have not yet supplied decisions for route response fields and actor resolution. Guessing them can make the clients incompatible.
- Q-10 is not yet settled, so concrete backend implementation paths and function names cannot be verified. Selecting them now would guess the backend architecture.
- The PRD records that time to finish Q-1 through Q-10 and implementation has not been estimated; feasibility before the 11:00 4 October 2026 submission deadline is unknown.
- Route requests carry preferences that can practically reveal health information. Logging, persistence and account linkage must continue to exclude them.
- The repository records no frontend consumer approval yet. The API contract is a blocking stability risk until that consumer agreement is recorded.

## Open questions

- Q-1. Which contract artifact format and path does the frontend owner agree to consume, and have they reviewed and approved the operation set and request, response and error shapes? `Block: yes` (category: stability of the programming interface (API) contract)
- Q-2. What routing result fields and failure outcomes are committed by `plans/routing_engine/`? `Block: yes` (category: stability of the programming interface (API) contract)
- Q-3. What request credential and actor-resolution behavior is committed by `plans/account_sessions/` and accepted by the frontend consumer? `Block: yes` (category: access token and permission scope contract)
- Q-4. What concrete backend modules and function boundaries does `plans/mvp/MVP_PLAN.md` Q-10 establish for implementing this contract? `Block: no`
- Q-5. What exact schema and error details are needed for fact reporting, voting, geozones and moderation after Q-10 establishes their domain model? `Block: yes` (category: stability of the programming interface (API) contract)

## Supplementary files

- `plans/api_contract/API_CONTRACT_SEED.md`, the original request and initiative ownership.
- `plans/api_contract/API_CONTRACT_SHAPE.md`, the agreed product scope and scenarios.
- `plans/api_contract/API_CONTRACT_PRD.md`, the requirements this plan implements.
- `plans/mvp/MVP_PLAN.md`, including Q-10 and the backend stack decision.
- `plans/routing_engine/ROUTING_ENGINE_SHAPE.md`, the pending route behavior decision.
- `plans/account_sessions/ACCOUNT_SESSIONS_PRD.md`, the account and actor behavior requirements.
- `plans/geocoding/GEOCODING_PLAN.md`, the settled address-search constraints.
