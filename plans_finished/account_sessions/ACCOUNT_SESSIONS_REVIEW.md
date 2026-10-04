# Review: MVP account sessions and actor resolution

Document state: 2026-10-03, review ready for the whole initiative

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

## 2026-10-03 - Definition of Done review after the merge

Scope: the whole initiative on branch `rm/requirements-preparation` with a clean working tree - the five artifacts of this initiative and the files it changed: `plans/mvp/MVP_PLAN.md` D-8, `plans/api_contract/API_CONTRACT_PLAN.md` D-4 and F-5, `plans/fact_schema/FACT_SCHEMA_PRD.md`, `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, and the addition after approval in `docs/product/specification.md`. The scope is documentation and hand-off only; no account or session code (`ACCOUNT_SESSIONS_PLAN.md` D-1). The review was run by the `dod-reviewer` agent on the request of the user, and the agent of the session checked B-2 and B-3 in the files before recording them.

Runs: `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` under Python 3.13.14 -> `120 passed`; `npx --no-install prettier --check` on the five artifacts and the five touched files, and on `"**/*.md"` -> all match; `ruff format --check .` -> `15 files already formatted`; `ruff check .` -> all checks passed. The earlier B-1 is resolved: the prose-style gate has a valid passing result.

Checks of the merge changes:

- The withdrawn FR-4, AC-4 - AC-6, D-2 and step 4 of Scope of changes and of Rollout order keep their numbers and are marked as withdrawn. The note in Domain rules of `ACCOUNT_SESSIONS_SHAPE.md` covers the interview record. The only unmarked leftover is the Problem section of the PRD (B-3).
- `plans/mvp/MVP_PLAN.md` D-8 matches D-3 of the plan point by point and leaves out D-2; Q-6 appears only as the former Q-6. `plans/api_contract/API_CONTRACT_PLAN.md` D-4 and F-5 match D-3 and name no vote deduplication.
- No compatibility note about vote uniqueness per account remains in `plans/fact_schema/`, so the earlier R-2 no longer holds.
- Open question 1 of the shape (`Block: no`) is answered by D-3 for the mechanism and by D-4 of `API_CONTRACT_PLAN.md` for the transport. Question 3, as narrowed by U-3 of `plans/dependency_check/DEPENDENCY_CHECK_REVIEW.md`, is settled: the team assigns and removes the role by hand (PRD FR-2, shape Domain rules, specification M11), and the removal takes effect on the next request (M11, D-3).

### Blockers

- B-2. The password storage format and the input limits of an account are handed to this initiative, which neither decides them nor hands them on. `ACCOUNT_SESSIONS_SHAPE.md`, section Notes on data, performance and security, sends password storage to phase B, while `ACCOUNT_SESSIONS_PLAN.md` decides only the session mechanism (D-3) and lists no open question. `plans/fact_schema/FACT_SCHEMA_PLAN.md`, plan closed, relies on this initiative in D-11 (it "enforces them at the input and chooses the hash format"), in D-14 (the input limits of the account are set by `plans/account_sessions/`) and in step 6.3, a pending insertion into Current state of `ACCOUNT_SESSIONS_SHAPE.md` saying the target schema leaves question 4 of this shape and the format of the hash to this initiative. FR-3 of the PRD gives only the password minimum of 5 and a maximum of at least 64, with no hash format and no pseudonym limit, and neither M9 of the specification nor D-8 of `plans/mvp/MVP_PLAN.md` covers it. Under ch. 4.6 of `docs/standards/standard_agentic_workflow.md` this is an unsettled contradiction with another initiative, and archiving first would leave step 6.3 editing an archived shape. It needs a decision of the user or the backend owner: a decision in this plan on the hash format and the pseudonym and password input limits, or an explicit hand-off to another owner agreed with the owner of `plans/fact_schema/`, with step 6.3 settled accordingly.
- B-3. The Problem section of `ACCOUNT_SESSIONS_PRD.md` still says without marking that the same 30-day vote hash also needs to apply to account votes. That is the withdrawn FR-4, against M9 of `docs/product/specification.md`, under which the hash is stored only for a vote without an account. Every other affected place of the PRD is marked. Fix: mark the sentence as withdrawn, as in the Business goal.

### Risks

- R-3 (the earlier R-1, stated more precisely). Logout only removes the token from that browser (D-3), and every authenticated request returns a renewed token, so a copied token used at least once every 24 hours renews itself without end; only deleting the account stops it, since the specification has no password change. Risks of the plan says the copy stays valid until its 24-hour inactivity expiry, which is accurate but understates a token that keeps being used. The deletion of the demo on 4 October 2026 limits the exposure. It needs a conscious acceptance or a server-side check; it does not block.

### Improvements

- I-1. Supplementary files of `ACCOUNT_SESSIONS_PLAN.md` still describe the files of `plans/fact_schema/` as holding the vote-window conflict, which no longer exists after the correction of F-6.
- I-2. Risks of `ACCOUNT_SESSIONS_PRD.md`: "A later anonymous vote may be accepted after the hash expires." comes from the withdrawn approach; under M4 a later vote from the same hash is accepted after one day anyway and replaces the earlier one.
- I-3. F-5 of the plan cites the shape section Recipient and trigger for the choice of a signed token, which that section does not contain, and Q-3 of `API_CONTRACT_PLAN.md`, now D-4. F-2 calls the local database setup an open initiative and the target environment unselected, while both are decided (`plans/mvp/MVP_PLAN.md` D-7, `plans/demo_environment/`). Dated facts of a closed plan; refresh them if the plan is touched for B-2.
- I-4. `ACCOUNT_SESSIONS_SHAPE.md`, Current state, says M11 answered most of question 3, while question 3 is no longer among the open questions and is settled in Domain rules; a pointer there would make the trail from U-3 of `plans/dependency_check/` easy to follow.
- I-5. The first part of the dependency item in Risks of `plans/mvp/MVP_PLAN.md` still treats Q-6 as open on the critical path Q-10 -> Q-6 -> Q-9; the settlement as D-8 is only added at its end.

Not checked, the call limit of the reviewer ran out: whether FR-6 and AC-6 of `plans/mvp/MVP_PRD.md` match M4 of version 4, the references to this initiative in `plans/api_contract/API_CONTRACT_PRD.md`, `plans/api_contract/API_CONTRACT_SHAPE.md` and `plans/demo_environment/`, the seed, and a direct existence check of the `plans_finished/` targets.

### Verification

- `standard_agentic_workflow.md`: checked automatically; `test_agent_docs_parity.py`, `test_session_context_hook.py` and `test_dangerous_commands_hook.py` passed within the 120. The closure rules of ch. 4.6 checked manually, which led to B-2.
- `standard_agent_docs.md`: checked automatically; `test_plan_document_contract.py` passed. Kept numbering and withdrawal markers checked manually, which led to B-3.
- `standard_review.md`: checked manually; report order, scope and verdict follow the standard.
- `standard_documentation.md`: checked manually; no code-unit documentation changed, and the addition to the specification matches the initiative.
- `standard_formatting.md`: checked automatically; `ruff format --check .` passed, Prettier passed on the ten files and on `"**/*.md"`, `test_prose_style.py` passed under Python 3.13.14.
- `standard_git.md`: checked automatically; `test_conflict_markers.py` passed, which matters after a merge with conflicts. No git operation was run by the review.
- `standard_architecture.md`: not applicable; no service code or module boundary.
- `standard_config.md`: not applicable; no configuration entry added. F-7 records the Secrets rule for the signing secret of D-3.
- `standard_database.md`: not applicable; no SQL or schema artifact belongs to this initiative.
- `standard_errors.md`: not applicable; no error-handling code.
- `standard_idempotency.md`: not applicable; with D-2 withdrawn no deduplication decision is left here, the vote limit belongs to `plans/fact_schema/`.
- `standard_code_quality.md`: not applicable; no code. `ruff check .` passed anyway.
- `standard_logging.md`: not applicable; no logging code.
- `standard_naming.md`: not applicable; no code symbols.
- `standard_security.md`: checked manually; the password policy deviation is recorded in Risks of the PRD and in M9, the token risk is R-3, the undecided hash format is B-2.
- `standard_tests.md`: not applicable to product code; the architecture suite ran with 120 passed.
- `standard_time.md`: checked manually; the 24 hours count from the latest authenticated request as elapsed time, and no stored timestamp form is decided here.
- `standard_worker.md`: not applicable; no periodic task.
- `standard_frontend.md`: not applicable; no frontend code, the token transport belongs to `plans/api_contract/`.

### Verdict

Not ready, for the whole initiative. B-1 and R-2 of the earlier review are resolved and the withdrawals of the merge are applied except B-3, but B-2 needs a decision of the user or the backend owner. This verdict does not qualify the initiative for `plans_finished/`, and B-2 is also an unsettled contradiction with `plans/fact_schema/`, which on its own stops the move under ch. 4.6. After B-2 and B-3 are fixed, a new review is needed before archiving.

## 2026-10-03 - After the review

While this review was being recorded, another session started `plan-implement` on `plans/fact_schema/`. Its correction of `plans/fact_schema/FACT_SCHEMA_PLAN.md` adds F-28, which records that this initiative closed without choosing the format of the password hash, and extends D-11 with the statement that the schema fixes no format of the hash, while the first part of D-11, D-14 and step 6.3 still leave the hash format and the input limits of the account to this initiative. B-2 therefore still holds; its resolution is not attempted here, because that plan is being implemented by the other session.

## 2026-10-03 - Fixes of B-2 and B-3

The user asked to resolve the blockers of the review after the merge. The changes are recorded in `ACCOUNT_SESSIONS_PLAN.md` as step 5 of Scope of changes and step 6 of Rollout order.

- B-3: the sentence of the Problem section of `ACCOUNT_SESSIONS_PRD.md` on the 30-day hash of account votes is replaced by a withdrawal marker, as in the Business goal.
- B-2, the hash: the user chose Argon2id on 2026-10-03, against handing the format on to `plans/mvp/`. It is D-4 of the plan, with F-10 and F-11; the encoded form in `password_hash` and the floor of the parameters at the OWASP minimum are an agent decision at C:40, without asking, and the library is left to the implementation.
- B-2, the input limits: while this was being fixed it turned out that `plans/api_contract/` had already set them in D-8 of its plan - a pseudonym of 3 to 30 characters after the trim, with no character of the Unicode category Cc, and a password of 5 to 128 characters counted as code points - and that its implementation writes the pseudonym into M9 as part of version 7 of the specification, waiting for the approval of the user. The user first chose in this session, without knowing that decision, a pseudonym of letters, digits, `_`, `-` and `.`, and then confirmed the rule of `plans/api_contract/` instead. D-4 sets no limits of its own and points to D-8 there; this initiative does not change the specification, because the password maximum of 128 meets the "at least 64 characters" of M9.
- B-2, the contradiction with `plans/fact_schema/`: that initiative was moved to `plans_finished/fact_schema/` during this work. Its D-11 and D-14 leave the format of the hash and the input of an account to the place where the input is accepted, which D-4 here and D-8 of `plans/api_contract/` now fill. Its F-28, which says that this initiative chose no format of the hash, describes the state before D-4 and stays as it is, as a record of the archive.
- New finding, fixed in the same run: D-5 and D-6 of `plans/api_contract/API_CONTRACT_PLAN.md`, decided by the user, refuse a request with an expired or invalid token instead of handling it as anonymous and take no token on a route request and an address search. That contradicted "an expired token is unauthenticated" and "a request with no authenticated account is an anonymous contribution" of D-3, FR-1, FR-2, AC-1 and Domain rules of the PRD, the rolling session of the shape and `plans/mvp/MVP_PLAN.md` D-8. Each of them got a dated change marker; F-4 and F-9 of the plan record the new state. D-8 of the MVP plan also names D-4 and the input rules.
- R-3: the user accepted the risk on 2026-10-03; Risks of the plan states it. A new risk on the memory of Argon2id on the shared demo server is added there.
- Improvements: I-1 and the stale descriptions of Supplementary files, I-2 in Risks of the PRD, I-3 in F-2 and F-5 of the plan and I-4 in Current state of the shape are fixed. I-5 is not: it is in Risks of `plans/mvp/MVP_PLAN.md`, whose sentence on Q-9 the implementation of `plans/api_contract/` replaces in its step 3.2.

Parallel work: during this run another session moved `plans/fact_schema/` to `plans_finished/fact_schema/` and changed the paths to it in the plan, the PRD and the shape of this initiative, and the session of `plans/api_contract/` implemented its plan in `docs/product/specification.md` and `plans/mvp/MVP_PLAN.md`. Their edits are taken as the current state, every file was read again right before its edit, and in the MVP plan only D-8 was changed, which no step of `plans/api_contract/` quotes. The paths in the earlier entries of this review stay as they were written.

A new review of the whole initiative is needed before archiving.

## 2026-10-03 - Definition of Done review after the fixes

Scope: the whole initiative - the five artifacts and D-8 of `plans/mvp/MVP_PLAN.md` - as left by the entry above. The scope is documentation and hand-off only; no account or session code (`ACCOUNT_SESSIONS_PLAN.md` D-1). The review was run by the `dod-reviewer` agent on the request of the user; the agent of the session checked R-C in the specification before recording it.

Runs: `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `120 passed`; `npx --no-install prettier --check plans/account_sessions/*.md plans/mvp/MVP_PLAN.md` -> all match; `plans_finished/account_sessions/` does not exist.

### Blockers

None. B-3 is fixed by the withdrawal marker in the Problem section of the PRD. B-2 is fixed by D-4 for the hash and by the pointer of D-4 to D-8 of `plans/api_contract/API_CONTRACT_PLAN.md` for the input, which `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-11 and D-14 leave to the place where the input is accepted; F-28 there stays as a record of the archive. No contradiction remains with D-4 - D-8 of the API contract, D-8 of the MVP plan, M9 and M11 of the specification, `docs/product/schema.md` or the fact-schema plan.

### Risks

- R-A. The agreement of the frontend person is not recorded in this initiative: the PRD, Dependencies, asks for it, and D-3 says only that the user selected the signed token. The user approved the contract in place of the frontend person, whose confirmation is still to be obtained (`plans/api_contract/API_CONTRACT_PLAN.md` D-10, `plans/mvp/MVP_PLAN.md` D-12). That is a human step tracked there, which does not block archiving under ch. 4.6.
- R-B. FR-12 and AC-11 of `plans/mvp/MVP_PRD.md` do not carry the additions of version 7 to M9. Their alignment belongs to the implementation of `plans/api_contract/` (its step 2.10), not to this initiative.
- R-C. Resolved before recording: `docs/product/specification.md` is version 7, approved by the user on 2026-10-03. Should the user later change D-5, D-6 or D-8 of the API contract, D-3, D-4, FR-1, FR-2, AC-1, Domain rules, the shape and D-8 of the MVP plan have to follow, by resuming this initiative.
- R-D. The editable references to this initiative lie in files the session of `plans/api_contract/` is editing, so the move waits for that session to finish its own path changes.
- Accepted and recorded: R-3, the memory of Argon2id on the shared server and the deviation from NIST SP 800-63B-4.

### Improvements

- I-A. F-8 of `plans/api_contract/API_CONTRACT_PLAN.md` cites D-3 of this plan by a line number that no longer points at D-3, since F-9 - F-11 were inserted. To be corrected together with the path of that reference at the move.
- I-B. Fixed after the report: the item of Risks of the plan on renewal now names what a signed-token renewal costs.
- I-C. Fixed after the report: the change markers of FR-1, FR-2 and Domain rules of the PRD and of the rolling session of the shape name the session of a deleted account next to the expired one, as D-3, F-9 and M9 do.
- I-D. Not applied: Human steps, Scope steps 2 and 3 and the Definition of Done of the plan describe the hand-off as it was done, under the names Q-6 and Q-3 of that time.
- I-5 of the earlier review is left to step 3.2 of `plans/api_contract/API_CONTRACT_PLAN.md`.

The fixes of I-B and I-C change only the wording of change markers and of one risk, no decision; after them prettier on the five artifacts and `tests/architecture` were run again by the agent of the session.

Not checked, the call limit of the reviewer ran out: the citations of F-1, F-3, F-6, F-7 and F-8 of the plan.

### Verification

- `standard_agentic_workflow.md`: checked automatically; the parity and hook tests passed within the 120. The closure rules of ch. 4.6 checked manually: no collision, no unsettled contradiction, no ambiguous status.
- `standard_agent_docs.md`: checked automatically; `test_plan_document_contract.py` passed. The facts F-2, F-4, F-5, F-9 and F-10 checked manually against the lines they cite, and the withdrawal and change markers against their dates.
- `standard_review.md`: checked manually; report order, scope and verdict follow the standard.
- `standard_documentation.md`: checked manually; no code-unit documentation.
- `standard_formatting.md`: checked automatically; prettier on the scope files and `test_prose_style.py` passed.
- `standard_git.md`: checked automatically; `test_conflict_markers.py` passed. No git operation was run.
- `standard_architecture.md`, `standard_config.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_tests.md`, `standard_worker.md`, `standard_frontend.md`: not applicable; no code. F-7 records the rule for the signing secret and F-8 the role matrix for the implementation.
- `standard_database.md`: checked manually; D-4 matches `password_hash text` of the target schema.
- `standard_security.md`: checked manually; the floor of D-4 matches the OWASP minimum of F-11, and the token risk and the deviation from NIST are recorded and accepted.
- `standard_time.md`: checked manually; the 24 hours are elapsed time, and no stored timestamp form is decided here.

### Verdict

Ready, for the whole initiative `plans/account_sessions/`, a decision record and hand-off without code. It qualifies for `plans_finished/` under ch. 4.6 of `docs/standards/standard_agentic_workflow.md`; the move waits for the session of `plans/api_contract/` to finish its path changes (R-D).
