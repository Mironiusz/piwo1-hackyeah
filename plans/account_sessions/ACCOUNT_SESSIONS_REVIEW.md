# Review: MVP account sessions and actor resolution

Document state: 2026-10-03, review not ready

## 2026-10-03 - Implementation run

The signed-token account-session decision and actor-resolution behavior were recorded in `ACCOUNT_SESSIONS_PLAN.md` D-3. `plans/mvp/MVP_PLAN.md` now records the decision as D-7 and no longer lists Q-6 as open. `plans/api_contract/API_CONTRACT_PLAN.md` records the credential and actor behavior in D-4 and no longer lists Q-3 as open. The fact-schema PRD and SHAPE record the conflict between per-account vote uniqueness and the x-day repeat-vote proposal, with a request for the fact-schema owner to reconcile it before schema implementation.

No account or session code was implemented, as required by the plan. No direct message was sent to the fact-schema owner; the requested reconciliation is recorded in the owner's PRD and SHAPE.

Pre-review verification: Prettier reported that all five changed Markdown files match the configured format. Automated architecture tests were not run.

## 2026-10-03 - Definition of Done review

Correction to the pre-review note: the plan-document architecture test was run and passed (25 tests). The prose-style architecture test was also attempted and failed during setup because the available `pytest` entry point uses Python 3.8. Prettier passed for all six changed Markdown files.

### Blockers

- B-1. The prose-style architecture check is incomplete. `pytest tests/architecture/test_prose_style.py` ran under Python 3.8 and failed because `pathlib.Path.walk` is unavailable there. The available Python 3.13 interpreter has no pytest installed. The repository-wide prose and forbidden-character gate therefore has no valid result for this change.

### Risks

- R-1. Logout removes the token from the active browser. A copy of that signed token may remain usable until its inactivity expiry, as recorded in `ACCOUNT_SESSIONS_PLAN.md` D-3 and Risks. The product requirements do not specify server-side revocation.
- R-2. The fact-schema owner has a documented request to reconcile the per-account vote rule before schema implementation. No direct notification was sent, and the fact-schema owner has not recorded a resolution.

### Improvements

None.

### Verification

- `standard_agentic_workflow.md`: checked manually; no workflow mechanisms were changed, and initiative closure rules were reviewed.
- `standard_agent_docs.md`: checked automatically; `pytest tests/architecture/test_plan_document_contract.py` passed, 25 tests. Plan completeness and review artifact format were checked manually.
- `standard_review.md`: checked manually; report order and scope follow the review standard.
- `standard_documentation.md`: not applicable; no code-unit documentation was changed.
- `standard_formatting.md`: Prettier check passed for all five changed Markdown files. The prose-style architecture check is incomplete for the environment reason in B-1.
- `standard_git.md`: not applicable; no branch, index or history operation was performed.
- `standard_architecture.md`: not applicable; no service code or module boundary was changed.
- `standard_config.md`: not applicable; no configuration or environment entry was added.
- `standard_database.md`: not applicable; no schema or database artifact was changed.
- `standard_errors.md`: not applicable; no error-handling code was changed.
- `standard_idempotency.md`: not applicable; no implementation of deduplication was changed. The vote compatibility conflict is recorded for the schema owner.
- `standard_code_quality.md`: not applicable; no code was changed.
- `standard_logging.md`: not applicable; no logging implementation was changed.
- `standard_naming.md`: not applicable; no code symbols or module files were added.
- `standard_security.md`: checked manually for the documented token and privacy risks; no security-sensitive code or dependency was changed.
- `standard_tests.md`: not applicable; no tests or product code were added or changed.
- `standard_time.md`: checked manually; the 24-hour inactivity period is elapsed time, and no persisted timestamp representation was specified or changed.
- `standard_worker.md`: not applicable; no periodic task or worker behavior was changed.
- `standard_frontend.md`: not applicable; no frontend code or interface text was changed.

### Verdict

Not ready for the whole account-sessions initiative because B-1 leaves the required repository prose-style gate without a valid result. The implementation scope is documentation and handoff only; no account or session code was in scope. This verdict does not qualify the initiative for `plans_finished/`.

## 2026-10-03 - Changes when merged into rm/requirements-preparation

The merge of `dev` into `rm/requirements-preparation` brought this initiative in with conflicts against decisions made there. The user decided that on every conflict those decisions win and the changes of this initiative are rejected. Withdrawn, with their numbers kept: FR-4 and AC-4 - AC-6 of `ACCOUNT_SESSIONS_PRD.md` and D-2 of `ACCOUNT_SESSIONS_PLAN.md`, with step 4 of its Scope of changes and of its Rollout order - the 30-day hash kept also for the votes of an account and one vote per account per fact, which contradict `docs/product/specification.md` version 4, M4 and M9. F-6 of the plan was corrected, because version 4 has no rule of one vote per account per fact. The compatibility notes in `plans/fact_schema/FACT_SCHEMA_PRD.md` and `plans/fact_schema/FACT_SCHEMA_SHAPE.md` were removed. `ACCOUNT_SESSIONS_SHAPE.md` keeps the interview record with a note in its Domain rules naming the rejected items. The other rules of this initiative - the passwords without recovery, the 24-hour session and the end of moderator access on the next request after the role is removed - entered version 4 of the specification as an addition after its approval, and its decision entered `plans/mvp/MVP_PLAN.md` as D-8, settling the former Q-6, because it arrived as a second D-7. The verdict above predates these changes and needs a new review.
