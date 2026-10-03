# Plan: MVP account sessions and actor resolution

Document state: 2026-10-03, plan closed

## Goal

Record the agreed technical decisions for MVP account sessions, request actor resolution and the storage of passwords, then hand them to `plans/mvp/MVP_PLAN.md` Q-6 and the API contract owner. This initiative decides and documents the behavior; it does not implement accounts or session handling.

## Facts

F-1. No backend or frontend product implementation exists in the repository; the tracked Python files are repository architecture checks. | cmd:`rg --files -g '*.py' -g '*.ts' -g '*.tsx' -g '*.js'` -> only `tests/` files; doc:`plans/mvp/MVP_PLAN.md` F-3 | 2026-10-03
F-2. No migration, SQL file or schema dump is present in the repository; the target schema is `docs/product/schema.md`, part of the specification since version 6. The local database setup is decided as D-7 and the place of the demo as D-10 of `plans/mvp/MVP_PLAN.md`. Refreshed on 2026-10-03 for I-3 of `ACCOUNT_SESSIONS_REVIEW.md`. | cmd:`git ls-files --others --cached --exclude-standard` filtered for `.sql`, `migration`, `alembic` and `dump` -> only `dump_context.py` of the skill `load-context`; doc:`docs/product/schema.md` line 3; doc:`plans/mvp/MVP_PLAN.md` line 37 D-7, line 43 D-10 | 2026-10-03
F-3. The backend stack is Python 3.13 with FastAPI and PostgreSQL with PostGIS; backend module boundaries and the backend architecture with the worker remain open in the MVP plan. | doc:`plans/mvp/MVP_PLAN.md` D-1 and Q-11 | 2026-10-03
F-4. The product requires a persistent browser session with a 24-hour rolling inactivity period renewed by every active-session request, including read-only requests, except a route request and an address search, which carry no account. A request with an expired session is refused, never handled as a contribution without an account. Moderator access is denied on the next request after role removal. Refreshed on 2026-10-03 for the decisions of F-9. | doc:`docs/product/specification.md` M9 third paragraph and M11; doc:`plans_finished/account_sessions/ACCOUNT_SESSIONS_PRD.md` FR-1 and FR-2 | 2026-10-03
F-5. The user selected a signed token for account sessions on 2026-10-03; it settles the former Q-6 of the MVP plan as D-8, and the API contract carries the credential and actor-resolution behavior and owns the transport of the token. Refreshed on 2026-10-03 for I-3 of `ACCOUNT_SESSIONS_REVIEW.md`. | doc:`plans/mvp/MVP_PLAN.md` line 39 D-8; doc:`plans_finished/api_contract/API_CONTRACT_PLAN.md` line 18 F-8, line 45 D-4 | 2026-10-03
F-6. The fact-schema initiative includes account and vote data. Its rule that a person votes on the same fact again once x days have passed, with x = 1 day, is the rule of `docs/product/specification.md` version 4, M4; version 4 has no rule of one vote per account per fact. Corrected on 2026-10-03, when this initiative was merged: the earlier text called the x-day rule incompatible with such a rule of the specification. | doc:`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-7, FR-9 and FR-10; doc:`plans_finished/fact_schema/FACT_SCHEMA_SHAPE.md` sections Out of scope and Domain rules; doc:`docs/product/specification.md` M4; doc:`plans_finished/account_sessions/ACCOUNT_SESSIONS_PRD.md` FR-4 | 2026-10-03
F-7. Any secret required by the selected session mechanism must stay outside the repository and logs; secrets in settings use the type required by the configuration standard. | doc:`docs/standards/standard_config.md` section Secrets; doc:`docs/standards/standard_logging.md` section Data in the entry content | 2026-10-03
F-8. Permission behavior requires tests for all roles, separately for list and detail views, in both allowed and denied directions. | doc:`docs/standards/standard_tests.md` section Mandatory tests | 2026-10-03
F-9. The API contract sets the input of an account: a pseudonym has 3 to 30 characters after leading and trailing spaces are removed and no character of the Unicode category Cc, and a password has 5 to 128 characters, all accepted, counted as Unicode code points. A malformed, wrongly signed or expired token and the token of a deleted account are refused with `401 session_expired` and never handled as a request without an account, and a route request and an address search take no token and renew no session. The user decided the pseudonym, the refusal and the requests without a token. | doc:`plans_finished/api_contract/API_CONTRACT_PLAN.md` line 47 D-5, line 49 D-6, line 53 D-8 | 2026-10-03
F-10. The target schema stores an account as `pseudonym` and `password_hash`, both `text` with no length or format limit, with the pseudonym unique through `UX_account_pseudonym_lower`; the schema fixes no format of the hash, and the limits of the input are checked where it is accepted. | doc:`docs/product/schema.md` lines 165-175; doc:`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` line 70 D-11, line 76 D-14 | 2026-10-03
F-11. The OWASP Password Storage Cheat Sheet recommends Argon2id first, with a minimum configuration of 19 MiB of memory, an iteration count of 2 and 1 degree of parallelism. | doc:[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) section Password Hashing Algorithms, subsection Argon2id | 2026-10-03

## Decisions

D-1. The deliverable is a technical decision record and handoff, not account or session implementation. This is the user-selected scope recorded in `plans_finished/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`.

D-2. Withdrawn on 2026-10-03. It kept a vote unique per account and fact and deduplicated account and anonymous votes by the same 30-day hash. The user rejected it on 2026-10-03, when this initiative was merged into `rm/requirements-preparation`, because it contradicts `docs/product/specification.md` version 4, which stays in force: a person votes on the same fact again once a day has passed and only the latest vote of a person counts (M4, `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-7), and a vote without an account keeps its hash for 30 days and is never tied to an account, so one person who votes once without an account and once logged in counts as two persons (M9, U-4 of `plans_finished/consistency_check/`). The number is kept so that references to it stay valid.

D-3. Account sessions use a signed token. The browser retains the active token across browser closure. A valid account token expires 24 hours after the latest authenticated request; every authenticated request, including a read-only request, returns a renewed token with a new 24-hour inactivity period. Logout removes the active token from that browser, so later requests from it have no account actor. An expired token is unauthenticated. Deleting an account makes its token unable to resolve to an account. Moderator authorization uses the account's current role on every moderator request, so removing the role denies the next such request even while the token remains valid. A request with no authenticated account is an anonymous contribution; a valid account token resolves to an account contribution, with moderator access additionally requiring the current moderator role. The user selected the signed-token mechanism on 2026-10-03. The API contract initiative owns token transport and request and response shapes. Changed on 2026-10-03 by `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-5 and D-6, decided by the user (F-9): a request with a malformed, wrongly signed or expired token, or with the token of a deleted account, is refused and never handled as an anonymous contribution, so only a request without a token is one, and a route request and an address search take no token, so they resolve no account and renew no session.

D-4. Passwords are stored as Argon2id hashes with parameters no weaker than the OWASP minimum of 19 MiB of memory, 2 iterations and 1 degree of parallelism (F-11), each written into `password_hash` in the encoded form of Argon2, `$argon2id$v=19$m=<memory>,t=<iterations>,p=<parallelism>$<salt>$<hash>`, so the parameters travel with every hash and can be raised later without a schema change (F-10). Decided by the user on 2026-10-03 for B-2 of `ACCOUNT_SESSIONS_REVIEW.md`, against handing the format on to `plans/mvp/`. Agent decision at C:40, without asking, for the encoded form and the floor of the parameters; the library is chosen by the implementation. This initiative sets no input limits of its own: the pseudonym and the password are checked where the input is accepted, before hashing, by the rules of `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-8 (F-9), which the user confirmed for this initiative on 2026-10-03.

## Scope of changes

1. Record the selected session mechanism and request actor-resolution contract in this plan's `## Decisions` section. The recorded contract must meet `ACCOUNT_SESSIONS_PRD.md` FR-1 and FR-2 and specify persistence across browser closure, the 24-hour inactivity expiry, renewal by read-only and other requests, logout, account deletion, moderator-role removal, and the distinction between account and anonymous actors. The user selected signed tokens on 2026-10-03.
2. Update `plans/mvp/MVP_PLAN.md` Q-6 and its `## Decisions` section with the selected mechanism and a reference to this plan. The result must state which requirements Q-6 settles without changing unrelated MVP decisions.
3. Update `plans_finished/api_contract/API_CONTRACT_PLAN.md` Q-3 and its linked facts with the agreed credential and actor-resolution behavior. Do not define endpoint paths or request and response shapes here; the API contract initiative owns those details.
4. Withdrawn on 2026-10-03 with D-2; the compatibility notes it added to `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-7 and `plans_finished/fact_schema/FACT_SCHEMA_SHAPE.md` Domain rules were removed when this initiative was merged.
5. Added on 2026-10-03 for B-2 of `ACCOUNT_SESSIONS_REVIEW.md`: record D-4 here and name it in `plans/mvp/MVP_PLAN.md` D-8 next to the reference to D-3, and align D-3, `ACCOUNT_SESSIONS_PRD.md` FR-1, FR-2, AC-1 and Domain rules and `plans/mvp/MVP_PLAN.md` D-8 with D-5 and D-6 of `plans_finished/api_contract/API_CONTRACT_PLAN.md` (F-9), marking each change with its date. Do not change `docs/product/specification.md`: the pseudonym and the refusal of an expired session enter it from `plans_finished/api_contract/`, and the password maximum of 128 meets the "at least 64 characters" of M9.

## Rollout order

1. The user selected signed tokens on 2026-10-03; the API contract initiative records the browser-facing credential transport with the frontend consumer.
2. Add the agreed mechanism and actor-resolution contract to this plan, including how a role removal affects the next moderator request and how logout ends the browser's active session.
3. Update Q-6 in `plans/mvp/MVP_PLAN.md` and Q-3 in `plans_finished/api_contract/API_CONTRACT_PLAN.md` to point to the settled decision. Keep the API operation shapes in the API contract initiative.
4. Withdrawn on 2026-10-03 with D-2.
5. Check the completed plan against `ACCOUNT_SESSIONS_PRD.md`, `docs/standards/standard_agent_docs.md` and `docs/standards/standard_formatting.md`. Close this plan when its decisions and handoffs are recorded and it has no open questions.
6. Added on 2026-10-03 for B-2 of the review: carry out step 5 of Scope of changes, then repeat the check of step 5 of this order.

Human steps: the backend owner chooses the technical mechanism and consults the frontend consumer; the reconciliation of the vote window by the fact-schema owner was withdrawn with D-2. No product code or database operation is part of this initiative.

## Definition of Done

- The signed-token mechanism and request actor-resolution behavior are recorded here.
- This plan states the chosen credential and actor-resolution behavior, including rolling expiry, renewal on read-only requests, logout, account deletion and next-request moderator-role revocation.
- `plans/mvp/MVP_PLAN.md` Q-6 and `plans_finished/api_contract/API_CONTRACT_PLAN.md` Q-3 reference the same settled decision.
- Withdrawn on 2026-10-03 with D-2: the two items on the vote uniqueness of an account, the cross-mode hash and the action for the fact-schema owner.
- Added on 2026-10-03 for B-2 of the review: D-4 is recorded here and named in `plans/mvp/MVP_PLAN.md` D-8, and D-3, FR-1, FR-2, AC-1 and Domain rules of the PRD and D-8 there follow D-5 and D-6 of `plans_finished/api_contract/API_CONTRACT_PLAN.md`.
- The plan has no TODOs or open questions and all applicable document checks pass.
- No account or session code is implemented by this initiative.

## Risks

- Logout removes the token from the active browser. A signed token copied elsewhere and used at least once every 24 hours renews itself without end, because every authenticated request returns a renewed token; only deleting the account stops it, since the specification has no password change. The product requirements do not require server-side per-token revocation, and the user accepted this risk on 2026-10-03 (R-3 of `ACCOUNT_SESSIONS_REVIEW.md`); the hosted demo is deleted on 4 October 2026.
- Every Argon2id hash of D-4 takes at least 19 MiB of memory while it runs, on a demo server that also runs other services of its owner, so many logins at the same moment take memory from them.
- The frontend-facing token transport remains for the API contract initiative to agree with the frontend consumer; this plan does not define endpoint paths or message shapes.
- Every authenticated request renews the session, including reads. With the signed token of D-3 a renewal signs a new token and stores nothing, while every such request reads whether its account still exists and, for a moderator request, the current role. Refreshed on 2026-10-03 for I-B of the review.
- Withdrawn on 2026-10-03 with D-2: the two risks of the vote window conflict and of the hash kept on the votes of an account.
- A 5-character password minimum and no common or breached-password rejection make password guessing easier than the NIST SP 800-63B-4 policy recorded in the PRD.

## Open questions

None. The user selected signed tokens on 2026-10-03. The API contract initiative owns the remaining browser-facing transport and message shapes.

## Supplementary files

- `plans_finished/account_sessions/ACCOUNT_SESSIONS_SEED.md`, the original delegation and initiative ownership.
- `plans_finished/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, the closed behavior interview and recorded user decisions.
- `plans_finished/account_sessions/ACCOUNT_SESSIONS_PRD.md`, the product requirements and acceptance criteria this plan must satisfy.
- `docs/product/specification.md`, the source of truth for account, session, moderator and vote behavior.
- `plans/mvp/MVP_PLAN.md`, backend stack and D-8, the former Q-6.
- `plans_finished/api_contract/API_CONTRACT_PRD.md` and `plans_finished/api_contract/API_CONTRACT_PLAN.md`, the consumer contract, the transport of the token, the refusal of an expired session and the input of an account (D-4 - D-6, D-8 there).
- `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` and `plans_finished/fact_schema/FACT_SCHEMA_SHAPE.md`, the account and vote data rules.
- `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-11 and D-14 and `docs/product/schema.md`, the stored form of an account behind D-4.
- `plans_finished/local_database/LOCAL_DATABASE_SHAPE.md`, the local database setup, decided as D-7 of `plans/mvp/MVP_PLAN.md`.
- `docs/standards/standard_config.md`, secret handling for the selected mechanism.
- `docs/standards/standard_logging.md`, exclusions for secrets and personal identifiers in logs.
- `docs/standards/standard_tests.md`, permission and visibility test requirements.
