# Plan: MVP account sessions and actor resolution

Document state: 2026-10-03, plan closed

## Goal

Record the agreed technical decision for MVP account sessions and request actor resolution, then hand it to `plans/mvp/MVP_PLAN.md` Q-6 and the API contract owner. This initiative decides and documents the behavior; it does not implement accounts or session handling.

## Facts

F-1. No backend or frontend product implementation exists in the repository; the tracked Python files are repository architecture checks. | cmd:`rg --files -g '*.py' -g '*.ts' -g '*.tsx' -g '*.js'` -> only `tests/` files; doc:`plans/mvp/MVP_PLAN.md` F-3 | 2026-10-03
F-2. No database schema, migration or schema dump is present in the repository. The local database setup is still an open initiative, and the target environment is not selected or accessible to the agent. | cmd:`rg --files -g '*.sql' -g '*schema*' -g '*dump*' -g '*migration*'` -> no matches; doc:`plans/fact_schema/FACT_SCHEMA_SHAPE.md` section Current state; doc:`plans/local_database/LOCAL_DATABASE_SHAPE.md` section Current state; doc:`docs/standards/decision_registry.md` section Technology stack and the Python profile of the standards | 2026-10-03
F-3. The backend stack is Python 3.13 with FastAPI and PostgreSQL with PostGIS; backend module boundaries and the backend architecture with the worker remain open in the MVP plan. | doc:`plans/mvp/MVP_PLAN.md` D-1 and Q-11 | 2026-10-03
F-4. The product requires a persistent browser session with a 24-hour rolling inactivity period renewed by every active-session request, including read-only requests. Moderator access is denied on the next request after role removal. | doc:`docs/product/specification.md` M9 and M11; doc:`plans/account_sessions/ACCOUNT_SESSIONS_PRD.md` FR-1 and FR-2 | 2026-10-03
F-5. The user selected a signed token for account sessions on 2026-10-03, resolving MVP plan Q-6; the API contract records the credential and actor-resolution behavior without defining endpoint or message shapes. | doc:`plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` section Recipient and trigger; doc:`plans/mvp/MVP_PLAN.md` Q-6 and D-7; doc:`plans/api_contract/API_CONTRACT_PLAN.md` Q-3 | 2026-10-03
F-6. The fact-schema initiative includes account and vote data. Its x-day repeat-vote rule remains incompatible with the account-level uniqueness rule of the product specification and this initiative. | doc:`plans/fact_schema/FACT_SCHEMA_PRD.md` FR-7, FR-9 and FR-10; doc:`plans/fact_schema/FACT_SCHEMA_SHAPE.md` sections Out of scope and Domain rules; doc:`docs/product/specification.md` M4; doc:`plans/account_sessions/ACCOUNT_SESSIONS_PRD.md` FR-4 | 2026-10-03
F-7. Any secret required by the selected session mechanism must stay outside the repository and logs; secrets in settings use the type required by the configuration standard. | doc:`docs/standards/standard_config.md` section Secrets; doc:`docs/standards/standard_logging.md` section Data in the entry content | 2026-10-03
F-8. Permission behavior requires tests for all roles, separately for list and detail views, in both allowed and denied directions. | doc:`docs/standards/standard_tests.md` section Mandatory tests | 2026-10-03

## Decisions

D-1. The deliverable is a technical decision record and handoff, not account or session implementation. This is the user-selected scope recorded in `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`.

D-2. A vote remains unique per account and fact independently of the 30-day hash. The same hash deduplicates account and anonymous votes only while it exists; after expiry a later anonymous vote may be accepted. The user decided this in `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` and `plans/account_sessions/ACCOUNT_SESSIONS_PRD.md`.

D-3. Account sessions use a signed token. The browser retains the active token across browser closure. A valid account token expires 24 hours after the latest authenticated request; every authenticated request, including a read-only request, returns a renewed token with a new 24-hour inactivity period. Logout removes the active token from that browser, so later requests from it have no account actor. An expired token is unauthenticated. Deleting an account makes its token unable to resolve to an account. Moderator authorization uses the account's current role on every moderator request, so removing the role denies the next such request even while the token remains valid. A request with no authenticated account is an anonymous contribution; a valid account token resolves to an account contribution, with moderator access additionally requiring the current moderator role. The user selected the signed-token mechanism on 2026-10-03. The API contract initiative owns token transport and request and response shapes.

## Scope of changes

1. Record the selected session mechanism and request actor-resolution contract in this plan's `## Decisions` section. The recorded contract must meet `ACCOUNT_SESSIONS_PRD.md` FR-1 and FR-2 and specify persistence across browser closure, the 24-hour inactivity expiry, renewal by read-only and other requests, logout, account deletion, moderator-role removal, and the distinction between account and anonymous actors. The user selected signed tokens on 2026-10-03.
2. Update `plans/mvp/MVP_PLAN.md` Q-6 and its `## Decisions` section with the selected mechanism and a reference to this plan. The result must state which requirements Q-6 settles without changing unrelated MVP decisions.
3. Update `plans/api_contract/API_CONTRACT_PLAN.md` Q-3 and its linked facts with the agreed credential and actor-resolution behavior. Do not define endpoint paths or request and response shapes here; the API contract initiative owns those details.
4. Record the account-vote uniqueness rule as a compatibility constraint for `plans/fact_schema/FACT_SCHEMA_PRD.md` FR-7 and `plans/fact_schema/FACT_SCHEMA_SHAPE.md` Domain rules. Request that the fact-schema owner reconcile the current x-day repeat-vote proposal with the product specification before schema implementation; do not edit that initiative's decision on the owner's behalf.

## Rollout order

1. The user selected signed tokens on 2026-10-03; the API contract initiative records the browser-facing credential transport with the frontend consumer.
2. Add the agreed mechanism and actor-resolution contract to this plan, including how a role removal affects the next moderator request and how logout ends the browser's active session.
3. Update Q-6 in `plans/mvp/MVP_PLAN.md` and Q-3 in `plans/api_contract/API_CONTRACT_PLAN.md` to point to the settled decision. Keep the API operation shapes in the API contract initiative.
4. Notify the fact-schema owner that `FACT_SCHEMA_PRD.md` FR-7 and `FACT_SCHEMA_SHAPE.md` Domain rules conflict with the account-level vote uniqueness in the product specification. The owner records the resolution in their initiative before implementation of the fact schema.
5. Check the completed plan against `ACCOUNT_SESSIONS_PRD.md`, `docs/standards/standard_agent_docs.md` and `docs/standards/standard_formatting.md`. Close this plan when its decisions and handoffs are recorded and it has no open questions.

Human steps: the backend owner chooses the technical mechanism and consults the frontend consumer; the fact-schema owner reconciles the vote-window conflict in their initiative. No product code or database operation is part of this initiative.

## Definition of Done

- The signed-token mechanism and request actor-resolution behavior are recorded here.
- This plan states the chosen credential and actor-resolution behavior, including rolling expiry, renewal on read-only requests, logout, account deletion and next-request moderator-role revocation.
- `plans/mvp/MVP_PLAN.md` Q-6 and `plans/api_contract/API_CONTRACT_PLAN.md` Q-3 reference the same settled decision.
- The account-level vote uniqueness rule and the 30-day cross-mode hash rule remain distinct and consistent with the product specification.
- The fact-schema owner has a recorded action to reconcile the x-day repeat-vote proposal with the current product specification before schema implementation.
- The plan has no TODOs or open questions and all applicable document checks pass.
- No account or session code is implemented by this initiative.

## Risks

- Logout removes the token from the active browser. A signed token copied elsewhere may remain valid until its 24-hour inactivity expiry; the product requirements do not require server-side per-token revocation.
- The frontend-facing token transport remains for the API contract initiative to agree with the frontend consumer; this plan does not define endpoint paths or message shapes.
- The fact-schema initiative currently proposes a repeat vote after x days, conflicting with the current product specification and this PRD's one-vote-per-account rule. Implementing either interpretation before reconciliation can make the stored vote behavior disagree with product behavior.
- Every active request renews the session, including reads. Depending on the selected mechanism, this may add persistence work to ordinary read requests.
- Retaining the same hash for account and anonymous votes links account vote activity to network and browser characteristics for up to 30 days. The hash is pseudonymized personal data.
- A 5-character password minimum and no common or breached-password rejection make password guessing easier than the NIST SP 800-63B-4 policy recorded in the PRD.

## Open questions

None. The user selected signed tokens on 2026-10-03. The API contract initiative owns the remaining browser-facing transport and message shapes.

## Supplementary files

- `plans/account_sessions/ACCOUNT_SESSIONS_SEED.md`, the original delegation and initiative ownership.
- `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, the closed behavior interview and recorded user decisions.
- `plans/account_sessions/ACCOUNT_SESSIONS_PRD.md`, the product requirements and acceptance criteria this plan must satisfy.
- `docs/product/specification.md`, the source of truth for account, session, moderator and vote behavior.
- `plans/mvp/MVP_PLAN.md`, backend stack, Q-6 and the dependent API contract decision Q-9.
- `plans/api_contract/API_CONTRACT_PRD.md` and `plans/api_contract/API_CONTRACT_PLAN.md`, the consumer contract and its blocking actor-resolution question.
- `plans/fact_schema/FACT_SCHEMA_PRD.md` and `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, the account and vote data rules and the vote-window conflict.
- `plans/local_database/LOCAL_DATABASE_SHAPE.md`, the unresolved local database setup.
- `docs/standards/standard_config.md`, secret handling for the selected mechanism.
- `docs/standards/standard_logging.md`, exclusions for secrets and personal identifiers in logs.
- `docs/standards/standard_tests.md`, permission and visibility test requirements.
