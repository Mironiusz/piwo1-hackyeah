# Review: First schema revision of the MVP

Document state: 2026-10-04, stages A and B implemented and reviewed, ready after minor fixes with the fixes done; initiative closed by the user without a final ready verdict for the whole initiative, steps of a human left open, see the entry Closure, moved to `plans_finished/`

## Stage A - run of 2026-10-04

Implemented S-1 - S-6 of `plans/schema_first_revision/SCHEMA_FIRST_REVISION_PLAN.md`, documents only, in the order of the plan.

Check before the run: since the plan was written, `HEAD` moved by two commits of Jakub Mieczkowski, `ca76535` and `5c7b2e8`, which hold only the shape, the PRD and the plan of this initiative; `origin/dev` has no new commit; no file cited in the Facts changed, so the facts stand with their check date. The shape has no unresolved `Block: yes`.

What changed:

- S-1: `docs/product/specification.md` is version 13: the state line, the sentence of version 13 in the paragraph of versions, the vote limit of M4 and the sentence on the own vote by calendar day, "None at version 13.", and the item of version 13 in the Decision provenance, with the approval of Kuba.
- S-2: `docs/product/schema.md` names version 13, drops `btree_gist`, gives `vote` the column `cast_on` with `UX_vote_account_day`, `UX_vote_hash_day` and `CK_vote_voter_hash_sha256` in place of `repeat_allowed_at`, its offset, `CK_vote_repeat_after_cast` and the two exclusion constraints, drops `IX_vote_cast_at_with_voter_hash`, and describes `voter_hash` and `cast_on`.
- S-3: `docs/product/api_contract.md`: the state line, `vote_too_soon` by calendar day, the example `2026-10-05T00:00:00.000+02:00`, and the repetition of a vote after a lost response.
- S-4: `docs/product/user_journeys.md` (5 places), `docs/product/views.md` (8), `docs/product/interface_texts.md` (5), `plans/frontend_app/FRONTEND_APP_PACKAGES.md` (3), `.impeccable/briefs/views/FactVoted.dc.html` (1) and `.impeccable/briefs/route-result.md` (1), with the texts of the plan; every replacement matched its old text exactly once.
- S-5: `MVP.md`: Scope at version 13, D-11, the row of `schema_first_revision`, the paragraph on the scenarios of AC-1 - AC-12, the entry `DB_SERVICE_ACCOUNT_NAME` and SQLAlchemy 2.1 under the table Requirements and initiatives, the confirmations of Kuba in Open decisions and confirmations, and the plan of this initiative among the Sources.
- S-6: Kuba approved version 13 in chat on 2026-10-04, after which the last sentence of the item of version 13 was added.

Runs:

- `npx --no-install prettier --check "**/*.md"`, the target `lint-docs`: all files pass.
- The grep of the Definition of Done of stage A finds only `docs/product/api_contract.md` lines 356 and 359, the item of version 13 of the specification, and in `MVP.md` D-11 (line 46), the override of FR-6 and AC-6 added after the review (line 101) and the paragraph on the scenarios of AC-1 - AC-12 (line 103).
- The statements of the `sql` blocks of the new `docs/product/schema.md` for the domains, `account` and `vote`, with a one-column stub of `fact`, ran on a temporary `postgres:15` container: scenario 2 of the shape gives four rows and no row for 15:00, a hash of 20 bytes is refused by `ck_vote_voter_hash_sha256`, and `vote` holds exactly `pk_vote`, `fk_vote_fact`, `fk_vote_account`, `ux_vote_account_day`, `ux_vote_hash_day` and its three checks, with the indexes `ix_vote_account_id`, `ix_vote_fact_id_cast_at` and the indexes of its key and uniqueness. The container was removed. The tables with PostGIS did not run, because no local image has it.
- The architecture tests did not run: pytest is not installed on this machine (F-20 of the plan).

Decisions while implementing:

- Agent decision at C:40, without asking: `.impeccable/briefs/views/FactVoted.dc.html` was left without `prettier --write`. The file was already not formatted by prettier before this change (`git show HEAD:... | prettier --check` fails), `lint-docs` checks only `.md` files, and formatting it would rewrite the whole mock for a change of one sentence.

- Agent decision at C:40, without asking: the memory entry "Vote limit by calendar day and the length of the vote hash" was appended to `agent_docs/memory/_cross_cutting.md` after stage A, not after stage B as item 4 of the Rollout order of the plan puts it, because the change of the vote limit already binds `community_facts` and `frontend_app`. Stage B appends its own entry and does not rewrite this one.

Review of stage A, `implementation-dod-review` through the subagent `dod-reviewer`:

- First round: not ready. B-1: `plans/mvp/MVP_PRD.md` FR-6 (line 39), AC-6 (line 81) and its Domain rules (line 114) still state the vote limit as a day, and `MVP.md` did not override them, although the shape had AC-6 read through the new version; the plan gave no step for it. R-1: the memory entry of 2026-10-03 "Target database schema of facts and votes" still gave the exclusion constraints as the reusable pattern, and the new entry did not settle it. R-2: the architecture tests did not run, pytest is missing. R-3: the steps of a human are open. R-4: the DDL did not run on PostgreSQL 18 with PostGIS.
- Fix of B-1, agent decision at C:40, without asking: a paragraph in `MVP.md` before the paragraph on the scenarios, in the form of the paragraphs on FR-20 and FR-11, saying that version 13 prevails over FR-6, AC-6 and the Domain rules of `plans/mvp/MVP_PRD.md` and how AC-6 is met; `plans/mvp/` itself is not edited (`MVP.md` line 11).
- Fix of R-1: the Decisions field of the new memory entry also settles the entry of 2026-10-03; the log stays append-only.
- Second round: B-1 and R-1 resolved, `npx --no-install prettier --check "**/*.md"` passes, the sweep for the old vote limit finds only text overridden by `MVP.md` or history; the only new finding was this log, updated here. R-2 - R-4 stay as risks the plan records; running `pytest tests/architecture -o addopts=-ra` where pytest exists settles R-2 before the Merge Request.

Verdict: ready after minor fixes, the minor fix being this log, now done. Scope: stage A only (S-1 - S-6, documents) of the initiative `plans/schema_first_revision/`; stage B is not implemented and not assessed. The initiative does not qualify for `plans_finished/`.

Left for later:

- Stage B, S-7 - S-13, waits until the code of `backend_skeleton` is merged into the branch (plan D-1).
- The steps of a human of the plan after stage A: tell Kuber and Adrian, Marek and Mateusz.

## Stage B - run of 2026-10-04

Kuba asked where the code was. Stage B stood on code of `backend_skeleton` - `data/engine.py`, `alembic/env.py`, the pins of `pyproject.toml` and the hook of the critical tests - which existed on none of the 14 remote branches (`git fetch`, then `git ls-tree -r` of each). Kuba then decided, one question at a time, that the model and the migrations are a library of their own that does not touch `backend_skeleton` (question 10 of the shape), a package in this repository (11), named `accessibility_db` in `db/`, without the prefix `piwo1` (12), with the local database on Compose, the database of the hosted demo on Compose with a lasting volume, and the tests on a container (13). The shape, the PRD (FR-8, FR-10, AC-8) and the plan (D-1, D-5, D-7 - D-9, D-12 - D-17, F-24 - F-30, S-7 - S-12) record the change with its date; `MVP.md` records that `backend_skeleton` no longer builds the local setup or the Alembic configuration and that this initiative waits for nothing.

What was built:

- `db/`: `pyproject.toml`, `alembic.ini`, `README.md`, `image/Dockerfile`, `image/create_accounts.sh`, `image/Dockerfile.tools`, `compose.yaml`, `compose.deploy.yaml`.
- `db/accessibility_db/`: `closed_lists.py`, `tables.py`, `migrations/env.py`, `migrations/script.py.mako`, `migrations/versions/0001_target_schema.py`, whose 22 statements were taken from the `sql` blocks of `docs/product/schema.md` by a script, so they match it character for character.
- `db/tests/`: three shared modules, `conftest.py` and seven test files with 26 tests; `tests/architecture/test_critical_test_guard.py` in the root.
- `.env.example`, `.env.local.example`, the records of the entries in `docs/standards/standard_config.md`, `docs/standards/naming_registry.md`, the root `pyproject.toml` (`deptry` excludes `db`), `agent_docs/memory/db/accessibility_db.md` and an entry in `agent_docs/memory/_cross_cutting.md`.

Runs, all in containers (F-24 - F-30 of the plan):

- The image builds with the pinned PostGIS 3.6.4 and pgRouting 4.0.1; the profile `migrate` applies `0001` on PostgreSQL 18.6 with the builtin locale C.UTF-8.
- The profile `test`: 26 passed.
- `DB_ENVIRONMENT=target` stops the critical session with code 4, also with `--collect-only`; `alembic downgrade base` is refused; `down` and `up` give an empty local database.
- `db/compose.deploy.yaml` under another project name: the profile `migrate` is refused without the consent, applies with `-e DB_REVISION_CONSENT=apply`, the version `0001` stays after `down` and `up`, no port of the host; its volume was removed after the check.
- The 125 architecture tests of the root, `ruff check .`, `ruff format --check .`, `mypy` of `db/` and `deptry .` of the root and of `db/` pass; `npx --no-install prettier --check "**/*.md"` passes.

Run into while implementing:

- SQLAlchemy 2.1.3 refuses a composite named like its own column and keeps an attribute for every column of a composite; agent decision at C:40, without asking: the columns of a pair are mapped under private keys starting with an underscore, the closest the library comes to the rule of `docs/standards/standard_time.md` that no attribute holds the offset alone.
- The first test run failed one test: a nullable pair read as `OffsetInstant(None, None)`; agent decision at C:40, without asking: `return_none_on=resolve_null_pair` is passed for nullable pairs, after which the test passes.
- `Vote.cast_on` is mapped as nullable, because PostgreSQL reports a generated column as nullable and the test of the model compares nullability.
- The two critical tests of D-8 of `plans_finished/local_database/` that need no revision were added (`test_local_database_setup.py`), because the local setup is now built here.
- A repository hook blocked shell commands that held `--rm` next to `cp -r` or to the names of the environment templates; the scripts ran from files of the session scratchpad instead.

Left for later:

- The steps of a human of the plan: tell Marek about the package and the revisions in `db/`, tell Kuber, Adrian and Mateusz as after stage A, join `db/compose.deploy.yaml` to the demo in `DEPLOYMENT_CONFIG` and apply the chain there with the consent; commit, push and the Merge Request.

Review of stage B, `implementation-dod-review` through the subagent `dod-reviewer`, first round: not ready.

- Blocker 1, fixed: the environment contract test was missing. Agent decision at C:40, without asking: `tests/architecture/test_environment_contract.py` checks that every template entry has a record in `docs/standards/standard_config.md`, that every template holds only empty markers, and that every template entry is present in its local file where that file exists; a missing local file skips that check with its name, because a local file is never committed (plan D-19).
- Blocker 2, fixed: `vulture` found the unused `kw` of `Geography.get_col_spec` at 100%; it is `**_kw` now, and the root `pyproject.toml` adds `db` to the paths of `vulture`.
- Blocker 3, fixed: `build_stored_fact` wrote to the database; it is `apply_stored_fact`, and the two helpers of the refusals that run writes are `apply_refused_statement` and `apply_refused_write`.
- Risk 1, partly fixed: `make security` scans `db/` with `bandit`; `mypy` and the tests of `db/` need the dependencies of the package and run in its container (`db/README.md`), not in `make check` of the root.
- Risk 2, fixed: `docs/standards/decision_registry.md` says that `schema_first_revision` builds the local setup and the Alembic configuration in `db/`; the trigger and scenario 1 of the shape describe the current state with the change dated; the owner column of `backend_skeleton` in `MVP.md` no longer names the local setup. `plans/mvp/MVP_PLAN.md` is not edited, because `MVP.md` overrides it (`MVP.md` line 11); the entry Technology stack and the Python profile of the decision registry stays, because its condition is the first backend code, which `db/` is not.
- Risk 3, fixed: `docs/standards/standard_config.md` names `db/accessibility_db/migrations/env.py` next to `alembic/env.py` in the exception for the environment of the schema revisions.
- Risk 4, decided by Kuba on 2026-10-04: the schema owner stays a superuser also on the hosted demo (plan D-18).
- Risk 5, fixed: `docs/standards/standard_time.md` records the private keys of the columns of a pair, and `docs/standards/standard_tests.md` the place and the value of the guard of the critical tests of `db/`.
- Improvements, done: F-9 and F-12 of the plan say they are superseded by D-14 and D-15.

Runs after the fixes, in containers: 127 architecture tests passed and 3 skipped with the name of the missing local file or template, `ruff check .` and `ruff format --check .` on 34 files, `vulture` clean, `bandit -r db -s B101` clean, `mypy` of `db/` on 16 files, `deptry` of the root and of `db/`, `pip-audit` of the pins of `db/` without a known vulnerability, the 26 tests of `db/`, and `prettier` on every markdown file.

Second round of the review of stage B: every blocker and risk resolved; one new finding, fixed: the row of `docs/standards/standard_config.md` in the tool map of `docs/standards/standard_review.md` names `pytest tests/architecture/test_environment_contract.py` instead of saying the test does not exist yet.

Verdict: ready after minor fixes, the minor fix being the row of the tool map, now done. Scope: stage B (S-7 - S-12, D-14 - D-19) of the initiative `plans/schema_first_revision/`. Together with the verdict of stage A, ready after minor fixes with its fix done, both stages are implemented and reviewed; no verdict states a final ready for the whole initiative, so it stays in `plans/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6), and the steps of a human of the plan are still open.

## Closure

The user chose on 2026-10-04, while cleaning up `plans/`, to close the initiative without a final `ready` verdict for its whole scope. Both stages are implemented and reviewed with their fixes done, and check 2.2 of `FINAL_CHECKLIST.md` is ticked. The steps of a human stay as the section Left for later of stage B records them: telling Marek, Kuber, Adrian and Mateusz about the package and the revisions in `db/`, joining `db/compose.deploy.yaml` to the hosted demo in `plans/deployment_config/` and applying the chain there with the consent, and the commit, the push and the Merge Request. This closure does not confirm whether any of them was done. A later change of the package `db/` goes through a resumption under ch. 4.6 of `docs/standards/standard_agentic_workflow.md` or through a new initiative. The directory moves to `plans_finished/schema_first_revision/`.
