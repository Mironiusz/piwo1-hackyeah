# Review: Choice of the local PostgreSQL environment with PostGIS for the MVP

Document state: 2026-10-04, implementation finished, moved to `plans_finished/` on 2026-10-03 by the session that moved the sibling initiatives

## Implementation run of 2026-10-03

### Check before implementation

- The plan was saved at 19:28, after `HEAD` `72682d6`, the merge of `dev` at 19:14. `git fetch --all` at 19:30: neither `origin/dev` nor `origin/rm/requirements-preparation` is ahead of `HEAD`. `git status` showed only the plan of this initiative as untracked, and the three target files were last written by that merge, so no other session was working on them.
- References: the places cited by F-1 (`plans/mvp/MVP_PLAN.md` D-6, the Risks item and Q-4), F-2 (`docs/standards/decision_registry.md` entry Technical directions of the MVP plan), F-3 (`plans/demo_environment/DEPLOYMENT_SHAPE.md` sections Current state and Open questions) and F-18 - F-24 still carry the cited content. The text that steps 2, 3 and 5 replace or remove stood verbatim in the files.
- F-4: D-2 and D-3 of `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` carry the virtual private server and the other services of its owner, but not that the server belongs to the db person, which D-4 there says. See O-1.
- Not repeated: F-5 - F-17 and F-25. They are runs and reads of outside documentation and package indexes of the same day, no step of this plan writes a file that depends on them, and the plan uses them only as the basis of its decisions.
- Free numbers: the last decision of `plans/mvp/MVP_PLAN.md` was D-6, so D-7 was free, and Q-4 still stood under Open questions.
- `LOCAL_DATABASE_SHAPE.md` has a closed interview, no open question and no `Block: yes`. The plan has no open question and no TODO.
- Baseline of the checks: `npx --no-install prettier --check` passes on the seven files of the Definition of Done; `tests/architecture/test_plan_document_contract.py` -> 25 passed; `tests/architecture/test_prose_style.py` -> 2 of 18 failed, every reported path a file of the design skill under `.claude/skills/impeccable/`, `.agents/skills/impeccable/` or `.claude/agents/impeccable-*.md`.
- Tools: `venv` and `node_modules` exist, so `npm ci` was not needed.

### Deviations from the plan

O-1. F-4 of the plan got a third piece of evidence, `doc:` `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-4, the decision saying that the server belongs to the db person. The claim and the check date are unchanged. Agent decision at C:40, without asking: the claim was true, one of its three parts had no cited evidence, and the correction has one variant.

O-2. The state line of the plan was not used to show the progress of the run, as `plan-implement` asks: the plan format allows exactly two markers, and `tests/architecture/test_plan_document_contract.py` reads them. The progress is recorded in this file.

### What was done

- Steps 1 - 4: `plans/mvp/MVP_PLAN.md` got D-7 after D-6, the risk sentence that names only Q-6 and Q-7 among the open questions that depend on no other, no item Q-4 under Open questions, and the plan of this initiative under Supplementary files.
- Step 5: `docs/standards/decision_registry.md`, entry Technical directions of the MVP plan, item Blocks, carries the replaced sentence. The entry stays among the open decisions.
- Step 6: `plans/demo_environment/DEPLOYMENT_SHAPE.md` got the consequence for the hosted database as the last item of Current state. Its decisions and its open question are unchanged.
- The decision is recorded in the working tree before the deadline of 22:00 on 3 October 2026 set in `LOCAL_DATABASE_SHAPE.md`; the commit is left to a human.

### Lines of other owners left as they are

- `plans/fact_schema/FACT_SCHEMA_SHAPE.md` sections Current state and Smallest meaningful scope and `plans/fact_schema/FACT_SCHEMA_PRD.md` sections Dependencies and impact on other modules and Risks and notes still say that the local database is open and wait for Q-4. D-10 of the plan keeps the shapes of `plans/fact_schema/` and `plans/routing_engine/` out of this change, and the plan names this under Risks, so they were not edited.

### Checks of the Definition of Done

- `git diff --numstat`: `plans/mvp/MVP_PLAN.md` 4 added and 2 removed, `docs/standards/decision_registry.md` 1 and 1, `plans/demo_environment/DEPLOYMENT_SHAPE.md` 1 and 0. `git diff --word-diff=plain` shows only the words of steps 1 - 6.
- No setup file exists: `git ls-files --others --exclude-standard` lists only the files of this initiative, and the tree outside `node_modules`, `venv` and `.git` holds no `Dockerfile`, no Compose file, no `.env` file and no `alembic.ini`.
- `npx --no-install prettier --check` on the files of `plans/local_database/`, this review included, `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md`, `plans/demo_environment/DEPLOYMENT_SHAPE.md` and `agent_docs/memory/_cross_cutting.md` -> all matched files use Prettier code style.
- `venv\Scripts\python.exe -m pytest tests/architecture/test_plan_document_contract.py -o addopts=-ra` -> 25 passed, the check of this closed plan included.
- `venv\Scripts\python.exe -m pytest tests/architecture/test_prose_style.py -o addopts=-ra` -> 2 failed, 16 passed, the same two checks as in the baseline. The assertion message cuts the list of violations short, so the scan of the test, `fetch_prose_style_summary`, was run directly and filtered to the files of this change: 0 of 257 forbidden character violations and 0 of 1842 bold violations, every reported path under `.claude/skills/`, `.agents/skills/` or `.claude/agents/`.
- The steps for a human of the Rollout order stay with people: the commit and the Merge Request, the confirmation of the db person, and telling the db person and the backend person about `CREATE EXTENSION postgis` in the first revision and about pgRouting 4.0.1.

### Review of 2026-10-03

The review by `implementation-dod-review` covered the whole initiative: the changes of steps 1 - 6, the deviations O-1 and O-2, the memory entry and the artifacts of `plans/local_database/`.

Blockers: none.

Risks:

- R-1. 4 of the 114 architecture tests fail: the two parity checks of `tests/architecture/test_agent_docs_parity.py` on the design skill `impeccable` and its agent roles, and the two prose checks on the files of the same skill. The prose checks were red in the baseline of this run, and no file of this change is reported by any of the four. `npx --no-install prettier --check "**/*.md"` passes on the whole repository.
- R-2. The four lines of `plans/fact_schema/` named under Lines of other owners left as they are still show Q-4 as open. D-10 of the plan keeps them out of this change, so a reader of those artifacts sees the old state until their owner updates them.
- R-3. The decisions were given by the user on behalf of the db person, whose ruling is still to be confirmed (plan, Risks).
- R-4. No run of the environment exists: the image, the Compose file and the script are built only by the work package of `plans/mvp/`, so D-3 - D-6 rest on the published contents of the images, the packages and the documentation (F-7 - F-14, F-25). Their first build is the first run.

Improvements:

- I-1. The memory entry in `agent_docs/memory/_cross_cutting.md` tied the permission error of a forgotten grant to the missing CREATE on the public schema, while the reason is that the service account owns nothing. Fixed: the two causes now stand in two separate clauses.
- I-2. The prettier item of the Checks of the Definition of Done above named the four files of `plans/local_database/` without this review and without the memory file. Fixed.

Verification, every standard of the map:

- `standard_agentic_workflow.md` - checked automatically: `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> 61 passed, 2 failed, both on the design skill (R-1). The checks of ch. 4.7 were made before the edits: `git status`, the modification times of the target files and `git fetch`.
- `standard_agent_docs.md` - checked automatically: `pytest tests/architecture/test_plan_document_contract.py` -> 25 passed, the closed plan of this initiative included. This file and the memory entry were read against the REVIEW format and the memory entry template.
- `standard_review.md` - checked manually: this list goes through all nineteen rows of the tool map.
- `standard_documentation.md` - checked manually: the change creates no code unit, and the prose of the changed documents keeps to the facts and decisions of the plan.
- `standard_formatting.md` - checked automatically: `ruff format --check .` -> 13 files already formatted; `npx --no-install prettier --check "**/*.md"` -> all matched files use Prettier code style; `pytest tests/architecture/test_prose_style.py` -> 2 failed, 16 passed, with no violation in a file of this change (R-1).
- `standard_git.md` - checked automatically: `pytest tests/architecture/test_conflict_markers.py` -> 8 passed. The agent ran no `git add`, commit, push or merge.
- `standard_config.md` - checked manually: no address, account name or password of any environment is written, and the entries of the environment templates with their records are left to the work package of `plans/mvp/` (D-8 of the plan). The contract test of the map does not exist yet.
- `standard_database.md` - checked manually: the decisions keep every extension, schema object and grant in revisions and keep the builtin provider with `C.UTF-8`. No query is written, so `bandit` B608 has nothing to check.
- `standard_tests.md` - checked automatically: `pytest tests/architecture` -> 110 passed, 4 failed (R-1). The change adds no test; the critical tests of D-8 come with the work package of `plans/mvp/`.
- `standard_architecture.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md`, `standard_time.md` and `standard_worker.md` - not applicable: the change holds no Python code, no dependency and no periodic task.
- `standard_frontend.md` - not applicable: the change holds no frontend code.

First verdict: ready after minor fixes, for the whole initiative, with no blocker.

After the fixes of I-1 and I-2, `npx --no-install prettier --check` on the files of this change, `pytest tests/architecture/test_plan_document_contract.py` and the prose scan of the changed files passed again.

Final verdict: ready, for the whole initiative `plans/local_database/`. R-1 - R-4 stay with people outside this run.

### Archive

The final verdict covers the whole initiative, so the directory qualifies for `plans_finished/` under `docs/standards/standard_agentic_workflow.md` ch. 4.6. The move was not made in this run. A second agent session was working on the same tree at the same time: at the user's request it moves `plans/geocoding/`, `plans/osm_data_source/`, `plans/osm_barrier_mapping/` and `plans/frontend_stack/` to `plans_finished/` and rewrites the editable references in the same files this run changed. Two sessions rewriting references in the same files would get in each other's way (ch. 4.7).

Decided by the user on 2026-10-03: that session moves `plans/local_database/` together with the other four, with the checks of ch. 4.6. This run leaves the directory as it is after this entry.

## 2026-10-04 - Archiving recorded after the fact

The directory was moved to `plans_finished/local_database/` on 2026-10-03 by the session of `plans/consistency_check/`, as this review handed it over (`plans_finished/consistency_check/CONSISTENCY_CHECK_REVIEW.md`, section What was done); git first holds it there in commit `feee392` of 2026-10-03. This review recorded the verdict that qualifies the initiative for the archive under `docs/standards/standard_agentic_workflow.md` ch. 4.6, but not the move itself, so `plans/repository_consistency/` appended this entry on 2026-10-04 at the request of the user. That session records its checks of ch. 4.6 for this move in the same section.
