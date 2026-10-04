# Plan: API and service layers of community facts

Document state: 2026-10-04, plan in progress

## Goal

Implement the approved `COMMUNITY_FACTS_API_PRD.md` on the shared backend foundation, Kuba's community-fact data operations and the actor resolution of `accounts`. Deliver the nine HTTP operations without a second evaluator, database engine, session mechanism or environment reader. The shape's regulator is C:40.

The PRD was approved by the user on 2026-10-04. This plan records verified foundations and a concrete API/service split, but it is not ready for implementation until the questions below are resolved. An absent dependency is not an implemented contract.

## Facts

F-1. The shape is closed at C:40 and the user approved its PRD on 2026-10-04. | doc:`COMMUNITY_FACTS_API_SHAPE.md` document state and Open questions; doc:`COMMUNITY_FACTS_API_PRD.md` document state | 2026-10-04
F-2. Version 18 of the specification governs M3 - M5, M9 - M11 and privacy; anonymous identity uses IP + User-Agent only, with identical pairs sharing one identity. | doc:`docs/product/specification.md` M9 and Personal data | 2026-10-04
F-3. The API contract defines the nine operations, the shared Fact, request validation, session renewal and the safe error envelope. | doc:`docs/product/api_contract.md` Conventions, Shared objects, Sessions and actors, Facts, Moderation and Errors | 2026-10-04
F-4. Area reads return at most 1000 eligible facts; nearby reads use 15 m and exclude hidden and OSM-removed facts; direct reads allow a non-hidden removed fact. | doc:`docs/product/api_contract.md` Facts | 2026-10-04
F-5. Saving uses a UUID key; an identical normalized retry returns 200, the first save returns 201, and changed content returns 409 with `idempotency_key_reused`. | doc:`docs/product/api_contract.md` create_fact | 2026-10-04
F-6. Vote refusals use 409 with `vote_too_soon` and the next Europe/Warsaw midnight; hidden facts return 404 with `fact_not_found`. | doc:`docs/product/api_contract.md` cast_vote and Errors | 2026-10-04
F-7. `api.app.build_app` installs shared error handling and correlation and registers no product router; `api.errors.build_error_response` accepts code, status and invalid-request fields but not a next-vote instant. | code:`api/app.py` build_app; code:`api/errors.py` build_error_response and apply_error_handlers | 2026-10-04
F-8. The API entry point calls uvicorn with one worker and access logs disabled; it does not explicitly disable proxy-header processing. | code:`api/__main__.py` main | 2026-10-04
F-9. Settings are a pure Pydantic model; the facade alone reads runtime values and exposes constants. Neither voter-hash nor session-signing keys are currently declared there. | code:`config/settings.py` Settings and ENVIRONMENT_ENTRY_FILES; code:`config/config.py` module constants | 2026-10-04
F-10. The pooled API engine has UTC sessions, a 5000 ms statement timeout, bounded connection and pool waits, and hidden parameters; the read-only snapshot helper uses REPEATABLE READ and rolls back on exit. | code:`data/engine.py` apply_engine_construction, fetch_api_engine and fetch_read_only_snapshot | 2026-10-04
F-11. `StoredFact` and `StoredVote` exist and cover public fact and evaluator inputs; `StoredFact` does not include hidden/flag timestamps or the saved idempotency key needed by write orchestration. | code:`data/route_facts.py` StoredFact and StoredVote | 2026-10-04
F-12. The existing `fetch_fact_votes` reads all votes for supplied fact identifiers on the caller's connection, batching at 10000 identifiers. | code:`data/route_facts.py` fetch_fact_votes and FACT_ID_BATCH_SIZE | 2026-10-04
F-13. The route visibility condition excludes both hidden and removed facts, so it cannot be applied unchanged to the direct-detail operation. | code:`data/route_facts.py` VISIBLE_FACT_CONDITION; doc:`docs/product/api_contract.md` read_fact | 2026-10-04
F-14. `resolve_fact_status` orders votes by instant and identifier, keeps the latest vote per identity, uses the latest five identities and returns status, weighted sums and the latest-confirmation day. It computes that day over all supplied confirmations. | code:`service/fact_status.py` resolve_fact_status, FactVoteRecord and FactStatusResult | 2026-10-04
F-15. Shared aware time functions and business-day conversion already exist; the database package provides the instant/offset pair and its conversion helpers. | code:`common_time.py` fetch_business_now, fetch_utc_now and build_business_day; code:`db/accessibility_db/tables.py` OffsetInstant, build_offset_instant and build_local_datetime | 2026-10-04
F-16. The target Fact and Vote mappings and first revision contain the idempotency key, first-flag and hide pairs, daily uniqueness constraints, 32-byte hash constraints and account detachment. Status is not stored as a column. | code:`db/accessibility_db/tables.py` Fact and Vote; code:`db/accessibility_db/migrations/versions/0001_target_schema.py` upgrade statements; doc:`docs/product/schema.md` Facts and Accounts and votes | 2026-10-04
F-17. The service account cannot delete fact or vote rows; critical tests of those writes must roll back or use a separately agreed exact cleanup boundary rather than assume delete rights. | code:`db/accessibility_db/migrations/versions/0001_target_schema.py` GRANT_SERVICE_ACCOUNT_SQL; doc:`docs/standards/standard_tests.md` Critical tests | 2026-10-04
F-18. Kuba's closed shape supplies the data layer and evaluator but no community-fact implementation plan or data-operation signatures exists in this tree. | doc:`COMMUNITY_FACTS_SHAPE.md` Smallest meaningful scope; cmd:`python` path-presence probe reports `data/community_facts.py`, `data/facts.py`, `data/votes.py` and `plans/community_facts/COMMUNITY_FACTS_PLAN.md` absent | 2026-10-04
F-19. Accounts D-7 and S-5 - S-6 specify `SessionResolution`, `AccountActor` and `fetch_request_session` / `fetch_moderator_actor`; the review requires exception names ending in Error. Actor and API-session modules are not delivered in this tree. | doc:`plans/accounts/ACCOUNTS_PLAN.md` D-7 and S-5 - S-6; doc:`plans/accounts/ACCOUNTS_REVIEW.md` Decisions while implementing; cmd:`python` path-presence probe reports `service/actors.py` and `api/sessions.py` absent | 2026-10-04
F-20. A valid-session handled refusal is renewed by the accounts middleware; a foreign-key refusal after account deletion is mapped by the vote consumer to `session_expired`. | doc:`plans/accounts/ACCOUNTS_PLAN.md` D-7 and D-8 | 2026-10-04
F-21. The importer plan requires reconciled fact locks before vote history and a 120-second publication ceiling; Kuba agreed that a vote locks its fact before checking visibility. The delivered history query locks vote rows but does not establish completed reconciliation. | code:`data/osm_copy.py` FETCH_OSM_FACT_HISTORY_SQL and fetch_osm_fact_history; doc:`COMMUNITY_FACTS_SHAPE.md` requirement 5; doc:`plans/osm_importer/OSM_IMPORTER_PLAN.md` D-15 and D-16 | 2026-10-04
F-22. Deployment has no closed proxy plan; its shape leaves the header carrying the person's IP for agreement in phase B. | doc:`plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md` Current state and Open questions; cmd:`python` path-presence probe reports `plans/deployment_config/DEPLOYMENT_CONFIG_PLAN.md` absent | 2026-10-04
F-23. The frontend client has no explicit request abort timeout found in the client source search; this does not establish the timeout of the hosted proxy or HarmonyOS client. | cmd:`rg` search for AbortController, timeout and setTimeout in `frontend/src` returns location/UI timers rather than a client request timeout; doc:`plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md` Current state | 2026-10-04
F-24. Local runtime verification is unavailable: both the default Python and `venv/bin/python` are Python 3.14.2 and lack backend packages; the database probe ends before connecting on ModuleNotFoundError. Local Docker uses its default context and lists no running containers after approved read access. No applied database revision has been verified. | cmd:`python --version`, `venv/bin/python --version` and import probes; cmd:`docker context show` returns default and `docker ps --format '{{.Names}} {{.Image}}'` returns an empty list | 2026-10-04
F-25. The documented local setup installs the database package before root dependencies and starts and migrates the local database separately; runtime startup performs no migration. | doc:`docs/setup/backend.md` Install and Start; doc:`db/README.md` Local database | 2026-10-04
F-26. Tests distinguish isolated scenarios, API integration without a real dependency and critical real-database checks; critical collection refuses the target configuration. | doc:`docs/standards/standard_tests.md` Test layers and Mandatory tests; code:`tests/conftest.py` pytest_collection_finish | 2026-10-04
F-27. Environment templates contain only empty markers; every template key requires a standard record and, when its local file exists, a corresponding local key. | code:`tests/architecture/test_environment_contract.py` test_every_template_holds_only_empty_markers and test_every_template_entry_is_present_in_its_local_file; doc:`docs/standards/standard_config.md` Environment entries | 2026-10-04
F-28. Review requires complete standard checks and actual runs where possible; a plan closes only with no unresolved questions and concrete step inputs and outputs. | doc:`docs/standards/standard_review.md` Checklist; doc:`.agents/skills/plan-prd/SKILL.md` Phase B | 2026-10-04
F-29. The current importer refuses a publication with a newly disappearing OSM fact, with a message that the evaluator is not delivered, even though the evaluator now exists; it has no call to the shared evaluator in that path. Completing this integration belongs to the importer. | code:`service/osm_publication.py` apply_osm_copy_publication; code:`service/fact_status.py` resolve_fact_status | 2026-10-04

## Decisions

D-1. Keep the approved boundary: API/service implementation belongs to this task; data operations and actor resolution are delivered by their existing owners. Do not create alternative account or community-data implementations to hide missing dependencies. Agent decision at C:40, without asking: this follows the approved scope and the ban on guessing contracts.

D-2. New HTTP operations are synchronous FastAPI routes, so synchronous SQLAlchemy work runs in the framework's thread pool. `api/facts.py` owns the six public fact routes and `api/moderation.py` the three moderator routes. Their route names are the nine operation headings in the contract, independent of the Python function names. Registration is through `apply_fact_routes(app)` and `apply_moderation_routes(app)` called from `api.app.build_app`. Agent decision at C:40, without asking: all delivered database calls are synchronous and the route split follows the existing contract.

D-3. `api/fact_models.py` owns the strict request shape and response adaptation. Its models are `FactPoint`, `FactAreaRequest`, `NearbyFactsRequest`, `CreateFactRequest`, `CastVoteRequest`, `FactResponse`, `FactEnvelope`, `AreaFactsResponse`, `NearbyFactResponse`, `NearbyFactsResponse`, `FlaggedFactResponse` and `FlaggedFactsResponse`. Unknown fields are forbidden; coordinates must be finite numeric WGS 84 values and cannot be booleans or coerced strings; identifiers and step counts are integers rather than booleans. Pydantic performs shape validation, while cross-field domain rules stay in service. Agent decision at C:40, without asking: this implements the contract using the existing validation stack.

D-4. `service/fact_rules.py` owns `InvalidFactInputError`, `FactCreationInput` and `resolve_fact_creation_input`, validates the ordered area corners, the stairs-only step count, barrier-only geozones and permitted radii, and normalizes descriptions. `build_fact_idempotency_key(UUID)` computes SHA-256 of ASCII `create_fact:` plus the canonical lowercase UUID, as the target schema requires. A canonical creation input is compared to the saved content, not to its author, timestamp or current status. Agent decision at C:40, without asking: normalization and stable key semantics are already decided.

D-5. `service/community_facts.py` owns read/write orchestration and the domain failures `FactNotFoundError`, `IdempotencyKeyReusedError`, `VoteTooSoonError`, `FactNotFlaggableError` and `FactNotFlaggedError`. It builds views using the existing `FactView` and `resolve_fact_status`; the API adapter exposes no status sums or person fields. Stored votes are grouped by fact in one pass, not filtered once per returned fact. The exact data calls and result types remain Q-4 and are not invented in this draft. Agent decision at C:40, without asking: orchestration, one evaluator and omission of protected data follow the architecture and contract.

D-6. Area/detail/nearby/moderator reads use `fetch_read_only_snapshot(fetch_api_engine())` so facts and votes come from one snapshot. Writes use a caller-owned transaction from `fetch_api_engine().begin()` and construct the successful response view before leaving it; failure rolls back and no response is returned before commit. Reads take no per-fact engine or connection. Agent decision at C:40, without asking: this reuses the delivered engine and prevents mixed fact/vote states.

D-7. Request session resolution is supplied by `api.sessions.fetch_request_session`; moderator routes use `fetch_moderator_actor`. An authenticated voter supplies the account identifier through the agreed account actor; an anonymous voter supplies only the derived 32 bytes. The data layer receives no Request, IP or User-Agent. Accounts' middleware and error handlers remain the only session implementation. The Error-suffixed exceptions recorded in F-19 are used rather than the obsolete names in its original plan. Agent decision at C:40, without asking: this follows the recorded consumer contract.

D-8. `api/fact_errors.py` installs domain-to-contract handlers through `apply_fact_error_handlers(app)`. Most failures reuse `build_error_response`; `VoteTooSoonError` has an aware `repeat_allowed_at` and gets the contracted next-midnight ISO 8601 value with milliseconds. Extend the shared helper with a typed optional `repeat_allowed_at` argument permitted only for `vote_too_soon`, keeping existing callers compatible; do not introduce a second generic error envelope. Unexpected errors retain the existing sanitized diagnostic path. Agent decision at C:40, without asking: F-7 requires a narrow extension for the existing error field.

D-9. Compute the next voting boundary in `service/fact_rules.py` through `build_repeat_allowed_at(cast_on: date)`: add one calendar day as a date, combine with local midnight and the configured Europe/Warsaw ZoneInfo. This is calendar arithmetic, not addition of 24 hours to an aware instant. A conflict must supply the stored conflicting vote day, so waiting through midnight cannot produce a stale next-vote time from request-entry time. Preserve the stored offset pair through `build_offset_instant` on writes and `build_local_datetime` on reads. Agent decision at C:40, without asking: the daily limit and offset standard decide this behavior.

D-10. Retrying a save first respects public visibility, then compares normalized saved content. The operation returns the original fact on an identical retry and writes the author confirmation only for a newly inserted fact. The new-fact insertion, author confirmation and view belong to one transaction. The final conflict protection stays in the delivered data operation and database constraint, not in a preliminary service lookup. Agent decision at C:40, without asking: this follows PRD FR-2 and FR-6 and the idempotency standard.

D-11. `service/anonymous_voters.py` will own `InvalidAnonymousVoterInputError`, `AnonymousVoterInput` with protected representations, and `build_anonymous_voter_hash`. `api/fact_identity.py` extracts transport inputs without logging them and passes plain values to that rule. The hashing key, trusted address source and invalid-input response are Q-1 - Q-3; no defaults, extra browser characteristics or unchecked forwarded headers are assumed. The eventual canonical input must have unambiguous framing and canonical IP representation. The key must stay stable for the demo, so identical inputs do not silently receive a new identity.

D-12. Preserve the already agreed vote wait of at most 120 seconds (F-21). On the vote transaction, use the existing `data.engine.APPLY_STATEMENT_TIMEOUT_SQL` to set a local 120000 ms statement budget before the fact-lock query, then restore `API_STATEMENT_TIMEOUT_MS` after that query. The data handoff must identify the lock operation and must capture the vote instant after the wait, so a wait through midnight applies the day of the actual write. All other request statements keep the existing 5000 ms limit. The proxy handoff records the maximum wait rather than silently assuming it permits it. No write retries after an uncertain commit; the client reconciles a save through its same key and retries a vote through the agreed daily-limit behavior. A timeout rolls back and uses the existing safe `internal_error` contract. Agent decision at C:40, without asking: the 120-second vote agreement already exists; the narrow transaction-local setting preserves it without raising the limit for all API reads or inventing a new failure code.

D-13. There is no new schema revision, periodic job, external HTTP call, dependency or status cache. Configuration for the chosen hash/proxy method uses the existing settings/facade and empty-marker templates, with matching standard records and tests. Machine-specific or secret values never enter these artifacts. Agent decision at C:40, without asking: none of those additions is required by the approved scope.

D-14. Group tests by the existing layer boundary. API integration replaces service calls and session dependencies; service scenarios replace the agreed data seam; critical checks run the real data operations on the local database and prove offset preservation and atomic writes. Do not seed durable fact/vote rows through a service-account connection and then assume DELETE cleanup. The exact transaction-injection or local owner-cleanup fixture is part of Q-4. Agent decision at C:40, without asking: F-17 and the testing standard require this boundary.

## Scope of changes

### S-0. Verify dependencies and complete the plan

Input: F-18 - F-27, Q-1 - Q-4 and the approved PRD. Obtain the concrete community-data module names, signatures, typed outcomes, transaction ownership, visibility predicates, vote conflict metadata, foreign-key failure translation and test seam from Kuba's implementation plan or delivered code. Recheck the actor dependencies when they are delivered. Verify the applied local revision and table/constraint/index state once the documented local environment is available. Record the actual data and proxy contracts and update Facts, Decisions and S-3 - S-6 with their symbols. Recheck the existing public contract instead of modifying it through an implementation assumption.

Output: a complete contract and fact set with no unresolved question, not a substitute implementation of another initiative. This step is unfinished; the plan remains in progress until it is completed.

### S-1. Shared rules and anonymous identity

Input: D-3 - D-4, D-9, the answers to Q-1 - Q-3 and the closed data handoff of S-0. Add `service/fact_rules.py` and `service/anonymous_voters.py` with the symbols of D-4, D-9 and D-11. Add `tests/service/test_fact_rules_cases.py` and `tests/service/test_anonymous_voters_cases.py`: positive/refused radii, step counts, ordered rectangles, description boundaries, canonical keys, midnight across both clock changes, exact IP/User-Agent identity stability and accepted identical-pair collisions. Unknown or malformed identifying inputs use only the contract decided in Q-3.

Output: pure domain and identity rules with explicit inputs and no environment read outside the facade.

### S-2. Configuration and identity transport boundary

Input: Q-1 - Q-3 and F-8 - F-9, F-22 and F-27. Extend `config/settings.py`, `config/config.py`, the applicable empty-marker templates, `docs/standards/standard_config.md` Environment entries, and `tests/common_runtime_settings.py` with exactly the selected key and transport settings. Add their positive/refused cases to `tests/config/test_settings_cases.py` and `tests/config/test_facade_integration.py`. Add `api/fact_identity.py` and `tests/api/test_fact_identity_integration.py` proving header spoofing is refused or ignored according to the trusted peer boundary and that raw inputs never reach logs or failures. If the selected method depends on the raw transport peer, explicitly disable uvicorn proxy processing in `api/__main__.py`; the proxy handoff must name the producer and consumer sides without editing hosting files in this task.

Output: one validated configuration contract and a transport adapter for the selected identity method, with no target value in tracked files. Exact new entry names depend on the pending selection; this draft does not claim them as settled.

### S-3. Read orchestration

Input: S-0, the shared evaluator and D-5 - D-7. Add to `service/community_facts.py` the synchronous entry points `fetch_facts_in_area`, `fetch_fact`, `fetch_nearby_facts` and `fetch_flagged_facts`, with plain typed input and response views. Apply the distinct detail versus area/nearby visibility from F-4 and F-13. Select at most 1001 area candidates to derive truncation, evaluate only the returned at-most-1000 facts, and load their votes on the same snapshot in bulk. A nearby or moderator result gains no unapproved pagination or cap. Exact data-operation calls and result dataclasses are to be inserted from S-0 before this plan closes.

Tests: `tests/service/test_community_fact_reads_cases.py` for public area, direct detail, nearby and moderator matrices, status/source/date adaptation, removed versus ordinary outdated facts, ordering and truncation; `tests/service/test_community_fact_reads_critical.py` for actual local query and snapshot consistency, with no person data in outputs. Output: all four read entry points on the agreed data contract.

### S-4. Save and vote orchestration

Input: S-0 - S-3, D-9 - D-12 and the agreed lock/wait contract. Add `apply_fact_creation` and `apply_fact_vote` to `service/community_facts.py`. Creation uses normalized content and the canonical key, writes its initial confirmation only on the first insert and returns a `FactCreationResult` containing the public `FactView` and `is_created`. Vote conflicts raise `VoteTooSoonError` with the boundary derived from the stored conflicting day. A fact lock precedes visibility checks and a vote insert; status is read before returning from the committed write. An account deleted after recognition follows the agreed data failure signal into accounts' `SessionExpiredError`. The data calls and the failure/result types remain dependent on S-0.

Tests: `tests/service/test_community_fact_writes_cases.py` and `tests/service/test_community_fact_writes_critical.py` for identical and changed-content retries, hidden retries, author-vote atomicity, daily conflict, two concurrent same-key saves, two concurrent same-day votes, account-deletion races, publication commit/rollback races, and stored instant/offset round trips. Output: save and vote behavior meeting PRD AC-5 - AC-11 and AC-14 without a parallel data implementation.

### S-5. Flagging and moderation orchestration

Input: S-0, S-3 - S-4 and accounts' current moderator recognition. Add `apply_fact_flag`, `apply_fact_hiding` and `apply_fact_restoration` to `service/community_facts.py`. Keep flagging eligibility and flagged-only hide/restore decisions in service, enforce the data layer's matching write conditions, preserve the first flag instant and return `FlaggedFactView` with a public fact view, `flagged_on` and `is_hidden`. Exact locked reads and update outcomes are supplied by S-0.

Tests: `tests/service/test_fact_moderation_cases.py` and `tests/service/test_fact_moderation_critical.py` for visible user reports, geozones, converted facts, OSM refusals, hidden/public versus moderator matrices, repeated actions, first flag date and retained votes after restore. Output: all three state-changing entry points and the moderator representation.

### S-6. Request/response adapters and registration

Input: S-1 - S-5, D-2 - D-3, D-7 - D-8 and delivered `api/sessions.py`. Add the request/response models of D-3 and `build_fact_response(FactView)` / `build_flagged_fact_response(FlaggedFactView)` in `api/fact_models.py`, exposing exactly the contracted public fields. Add the fact/moderation routers, stable operation names, optional-session and moderator dependencies, required anonymous-identity extraction only for anonymous creation/voting, and `api/fact_errors.py`. Register routes and handlers in `api/app.py`; session registration remains with accounts. A first save returns 201 and a retry 200; a vote returns 201; a flag returns 204 without a body; moderation returns the specified 200 object.

Tests: `tests/api/test_facts_api_integration.py` and `tests/api/test_moderation_api_integration.py`, with `integration` markers, service replacements, the exact bodies/statuses/fields of all nine operations and failures, unknown fields, wrong scalar types, path IDs, valid/refused session renewal, public/moderator visibility and log redaction. Extend `tests/api/test_errors_integration.py` for next-midnight error serialization without weakening existing envelopes. Output: the nine contracted operations callable from the assembled app, with no direct data-layer import in API.

### S-7. Verification, documentation and records

Input: the delivered code, critical results and all PRD criteria. Add `api/API.md` and `api/API_ALGORITHM.md` when the first product routes are delivered, and update `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md` for the new flows without replacing accounts/import documentation. Update `docs/standards/naming_registry.md`, `docs/setup/backend.md`, MVP and the still-open identity handoff in the decision registry for the exact delivery. Append only reusable implementation decisions to `agent_docs/memory/api/_shared.md`, `agent_docs/memory/service/_shared.md` or `_cross_cutting.md`; task execution belongs to `COMMUNITY_FACTS_API_REVIEW.md`. Do not update a data-layer document for code this task does not change.

Output: all PRD criteria traced to actual runs, complete standard gates and a review of this task. A task-only ready verdict does not archive the whole community-facts initiative while Kuba's task remains unfinished.

## Rollout order

1. Complete S-0 and answer Q-1 - Q-4. Keep the plan in progress until the data signatures, transport contract, hashing choice and verification boundary are explicit.
2. Close the plan only after every step has concrete input and output and no unresolved item remains. Implementation is a separate user-invoked phase.
3. During implementation, deliver S-1 and S-2 with isolated tests; they must not mask missing account/data code.
4. Deliver S-3, then S-4, then S-5 on the agreed dependencies. Verify real database operations against the local revised database with the critical environment guard.
5. Deliver S-6, run the nine-operation API matrix and a local assembled-service smoke run, then complete S-7 and the implementation review.

Steps for a human: install the required Python/Docker applications if absent; provide local environment values and any selected hash/session key without sharing them in chat; coordinate the data/actor/proxy handoffs and team confirmations; perform commits and remote operations that are reserved for humans. This task makes no hosted-demo mutation.

## Definition of Done

- Every PRD FR-1 - FR-12 and AC-1 - AC-15 is traced to a passed run, including the real-database atomicity, concurrency, visibility and offset cases. No assumed cleanup rights or external target database is used.
- `make check-unit` passes for the changed units; the relevant critical cases pass against the local database of `db/` with the revision applied. Run the full checks required by `docs/standards/standard_review.md`, including formatting, type checks, dead code, dependency hygiene, layer/environment gates and both applicable Bandit passes. Audit dependencies only if implementation introduces or upgrades one.
- The exact JSON shapes and error codes are unchanged except a separately approved contract clarification for identifying-input failures. Internal sums, identities, raw IP/User-Agent, secrets and database details appear in neither responses nor logs.
- Review covers API, service, configuration and any actually touched shared module. Documentation and memory reflect actual delivery rather than proposals or unavailable acceptance.
- `COMMUNITY_FACTS_API_REVIEW.md` states its task scope and remaining initiative dependencies. Do not archive `plans/community_facts/` solely because this task finishes.

## Risks

R-1. The data-operation contract is missing, so the service signatures and fixture boundary cannot yet be finalized. Treat Q-4 as a real dependency, not an opportunity to invent fallback queries or alternate result types.

R-2. The live local schema and query cost are unverified. Models and revision SQL establish the target, not the state of a server; do not label S-0 or critical acceptance passed until a run proves them.

R-3. IP + User-Agent collisions and changed-pair identities are accepted prototype limitations. A changed hash key creates a different identity too, so key stability needs an explicit contract and no automatic regeneration.

R-4. Uvicorn may rewrite the client peer before an application-level trusted-peer check unless proxy processing is explicitly coordinated. An arbitrary client-supplied address header must never choose the voter IP.

R-5. Full vote-history reads have unbounded row volume even though the area result is capped. Group once, avoid N+1 queries and measure the delivered data method. If it requires a bounded status projection, agree it with Kuba and preserve the latest-confirmation date as well as the five-person window.

R-6. The agreed fact-lock wait requires a narrow extension of the current 5-second statement ceiling. The exact lock call belongs to the data handoff, and the proxy must support the recorded wait. Pool occupancy remains bounded by the existing pool settings; a pool timeout is a safe failure, not a reason to create more engines.

R-7. Account deletion and moderation can race with a vote/save. The service must use the agreed locked data outcomes and translate account detachment without treating it as anonymous or returning a partially committed view.

R-8. Kuber and Adrian's confirmation of the contract amendments and the team handoff remain outstanding. Do not resolve these by silently altering requests, permissions or identifying inputs.

R-9. Importer reconciliation is not yet connected to the delivered evaluator (F-29). The real publication race criteria need that integration and the agreed fact-first locks delivered by the importer; this task must not claim AC-14 passed with a substitute importer or repair the other initiative silently.

## Open questions

Q-1. Select HMAC-SHA256 under a separate required `VOTER_HASH_KEY`, stable throughout the demo, or reuse `SESSION_SIGNING_KEY` with domain-separated input. The selection affects configuration, hash identity stability and the human secret-setup step. `Block: yes` (category: personal data). The question has been put to the user; no answer is assumed.

Q-2. Agree the IP transport boundary with the proxy owner: the header produced by the proxy, how it overwrites client input, how the backend verifies the raw trusted peer and how direct local requests are distinguished. A trusted-proxy mode must not fall back to the proxy's own IP or an unchecked forwarded value. `Block: yes` (category: personal data).

Q-3. Set the response when an anonymous creation/vote has missing, empty, duplicated or malformed User-Agent or cannot yield a valid IP under the selected transport mode. Recommend refusing it rather than inventing a replacement identity, but the input/error contract needs the user's answer and any necessary amendment first. `Block: yes` (category: stability of the programming interface (API) contract).

Q-4. Obtain and agree the concrete community-data signatures, transaction-safe outcomes, visibility predicates, stored conflicting vote day and local critical-test fixture contract from Kuba's task. No implementation plan exists for that task in this tree. The API/service plan cannot finalize data call sites by guessing. `Block: yes` (category: read visibility and permissions).

## Supplementary files

The approved PRD and closed shape live next to this plan. References for the final handoff are `plans/accounts/ACCOUNTS_PLAN.md` D-7 - D-8, `COMMUNITY_FACTS_SHAPE.md` requirements 4 - 8, `docs/product/api_contract.md` Shared objects, Facts, Moderation and Sessions and actors, `docs/product/schema.md`, and `docs/setup/backend.md`. An exact data/proxy handoff document can be added after its producer and consumer contracts are agreed; none exists yet for this task.
