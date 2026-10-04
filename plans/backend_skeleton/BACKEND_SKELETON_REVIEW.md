# Review: Backend skeleton and local database of the MVP

Document state: 2026-10-04, planning in progress

## 2026-10-04 - Phase B resumed from the approved PRD

Scope: preparation of `BACKEND_SKELETON_PLAN.md`, not implementation or a readiness verdict for the backend.

The existing initiative has a closed shape and an approved PRD but no implementation plan. Resumed `plan-prd` phase B, preserving the seed, shape, PRD, importer ownership and archived decisions. Created a plan in progress covering the application foundation, environment entries, local database, Alembic handoff, shared logging, administrative wrapper, protected critical tests and the publication/exclusion proposal.

Checked the current MVP allocation, backend architecture, local database decisions, importer amendments and standards. Verified the PostgreSQL image manifest and public dependency metadata. Neither an image build, a backend launch nor a database publication has been performed in this phase. No hosted environment was accessed.

Q-1 remains pending: the user was asked whether PostgreSQL transaction_timeout plus a separate exclusion session should be the implementation direction. No answer was inferred from elapsed time. Q-2 records the outstanding proof of connection-loss fencing and safe cleanup; a separate advisory-lock holder alone does not establish that a publisher stops when that holder disappears. The proposed interface paragraphs are explicitly conditional. The plan cannot yet be marked closed or used to implement these contracts.

Validation:

- Python 3.13.11 with the repository-pinned pytest 9.1.1 ran the plan-contract, prose-style and conflict-marker suites: 51 passed, 1 failed in 6.83 seconds.
- The sole failure points to bold prose in `.pytest_cache/README.md:6`, outside the initiative. Its modification time was 2026-10-03 20:17:34 +0200, before this turn; it was not modified or removed.
- Direct use of the existing fact/prose validators on the draft plan found zero violations. This check covers an in-progress draft that the closed-plan gate intentionally skips; it does not verify the truth of every fact or approve the proposed contract.
- The pinned Prettier 3.7.4 formatted the plan. The final targeted formatting check covers both new artifacts.
- `git diff --check` passed; both new artifacts remain untracked and were not staged.

Another session created `plans/accounts/ACCOUNTS_SHAPE.md` during this work. Its file was not changed. Only the two backend-skeleton planning artifacts were added to repository content by this task; temporary verification environments and downloaded formatting tools are untracked tool artifacts.

Verdict: planning incomplete, pending Q-1 and Q-2. No implementation readiness or completion is claimed, no durable implementation memory is added, and the initiative remains in `plans/backend_skeleton/`.

## 2026-10-04 - Timeout direction approved and database primitives checked

Scope: recording the user's Yes to Q-1 and resolving the engineering portion of Q-2. This entry supersedes the earlier pending-Q-1 status; it does not rewrite that historical entry or approve a new PRD boundary.

The user approved PostgreSQL transaction_timeout, an independent exclusion-holder connection and a distinct uncertain-commit outcome. Updated the plan immediately, then checked the underlying database primitives in a disposable local `postgres:18.6-trixie` container with no network, no published port and a tmpfs database. No product backend, product revision, actual import or hosted action was performed.

The probe used invented scratch data and a restricted service role. Its output was:

```json
{
  "admission_after_all_backend_locks_end": true,
  "busy_refused_ms": 0.38,
  "publisher_fence_survives_guard_loss": true,
  "rollback_confirmed_and_guard_retained": true,
  "server_version": "18.6 (Debian 18.6-1.pgdg13+2)",
  "timeout_elapsed_ms": 404.56
}
```

A session-held admission lock preserved exclusion while a separate publication session timed out and its insert rolled back. A second key, shared by the publication session and probed exclusively by each contender, prevented new admission after the guard session was deliberately terminated. After the publication session also timed out and disappeared, admission succeeded and the scratch insert remained absent. This verifies server primitives with shortened budgets, not the final SQLAlchemy implementation, exact 120-second performance, file cleanup, commit uncertainty or complete-import behavior.

Recorded the fixed two-key protocol, typed backend identities, stale-guard attachment refusal, fresh autocommit cleanup checks and no-reconnect policy in D-11 - D-14. Agent decision at C:40, without asking: these engineering details implement the approved direction without changing product objects or granting maintenance privileges. PostgreSQL documents the same-role activity visibility and try-lock semantics; the probe exercised the service-role path. The task-owned container was stopped and its temporary database removed by its `--rm` lifecycle; no existing container was stopped.

One contractual question remains. If both sessions disappear, advisory locks cannot preserve exclusion until the old Python process finishes its private file cleanup. The user has been asked whether to accept new admission after database completion on that abnormal failure path, with the old run forbidden to republish, or retain FR-8's stronger cleanup requirement. No answer has been inferred. An affirmative answer must land in the shape and PRD before the plan closes; a negative answer requires redesign without inventing a persistent schema object.

Other sessions changed `MVP.md`, `docs/product/api_contract.md` and `docs/product/schema.md`. Inspected the diffs: account pseudonym alignment and account documentation, with no skeleton error-envelope or database DDL change. Preserved those edits and refreshed the corresponding planning fact.

Targeted fact-format and prose validation and Prettier cover the updated plan and review. The prior repository-wide prose failure remains the pre-existing `.pytest_cache/README.md` finding. No implementation verdict, archive move or durable implementation memory is claimed.

Verdict: planning incomplete, Q-1 resolved; Q-2 awaits the abnormal-loss cleanup decision. The initiative remains in `plans/backend_skeleton/`.
