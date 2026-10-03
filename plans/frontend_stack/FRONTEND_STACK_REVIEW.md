# Review: Choice of the frontend technology for the MVP and of the standards for frontend code

Document state: 2026-10-03, implementation finished, the archive move postponed by the user

## Implementation run of 2026-10-03

### Check before implementation

- The facts of `plans/frontend_stack/FRONTEND_STACK_PLAN.md` were checked again between 18:50 and 19:00. The branch has no commit since the plan was written: `HEAD` is the merge of 18:11, the plan was saved at 18:44.
- Line references: the lines cited by F-15, F-21 - F-30, F-33 and F-34 still carry the cited content in the working tree.
- Runs repeated with the same result: F-2 (`git ls-files -- frontend` -> 0 files), F-3 (Node.js v22.20.0, npm 11.21.0), the `npm view` commands of F-5 - F-11, F-18 and F-20, the template of F-4, the list of builds and the `HEAD` request of F-13, and the character count of F-31. The newest Vite is 8.3.2 now, inside the range `^8.3.1` of the template.
- Not repeated: F-12, F-14, F-16, F-17, F-19 and F-32. They are reads of outside documentation and measurements of the same day, and this run only quotes their numbers.
- `PRODUCT.md` and `.impeccable/briefs/route-result.md` carry uncommitted changes older than this run. F-20 was checked against the changed brief: the section Selected direction still names the two typefaces.
- `origin/dev` moved by three commits after the last merge into this branch, up to `8e8dc8f`. They add `plans/fact_schema/` and change one line in `docs/standards/decision_registry.md` (entry Technical directions of the MVP plan) and one in `plans/mvp/MVP_PLAN.md` (item Q-10). Neither line is edited or cited by this plan, so `dev` was not merged during this run.
- No sign of another session on the tree: `git status` showed only the files of this initiative and the two design files above, and no shared file was modified after the start of this run.
- Baseline of the checks: `tests/architecture/test_plan_document_contract.py` passes, 25 tests. `tests/architecture/test_prose_style.py` fails only on the files of the design skill under `.claude/skills/impeccable/` and `.agents/skills/impeccable/`, as the Risks of the plan say. The pinned prettier reports one file of the set this plan covers: `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, see O-1.
- Tools: `node_modules` was missing, so `npm ci` in the repository root installed the pinned prettier 3.7.4, as the Definition of Done foresees. No virtual environment exists on this machine; the tests run on the system Python 3.13.14 with pytest 9.0.1.

### Deviations from the plan

O-1. `plans/frontend_stack/FRONTEND_STACK_SHAPE.md` got the missing newline at the end of the file. The Scope of changes does not list the file, while the Definition of Done asks prettier to pass on it. Agent decision at C:40, without asking: the change has one variant and touches no content of the shape.

O-2. The root `README.md`, section What is inside, got "one standard of the frontend profile" in the item on `docs/standards/`. The plan did not list the file; without the change the item would count the standards wrongly after step 2. Agent decision at C:40, without asking: it follows from D-12, and the sentence has one correct wording.

O-3. Steps 3 and 6 add a table row whose Group cell, "frontend profile", is wider than every earlier one, so prettier padded the Group column of both tables again. Every row of the two tables therefore shows in the diff, with whitespace as the only difference outside the planned rows; `git diff -w` shows the planned lines alone.

O-4. `plans/mvp/MVP_PLAN.md`, section Risks, still names Q-3 among the open questions that depend on no other. The plan removes only the item under Open questions and keeps the other identifiers, so the line was left as it is. It is reported to the user as a line for the owner of that plan.

### What was done

- Step 1: `docs/standards/standard_frontend.md` was created with the core sections and the sections of D-11.
- Steps 2 - 5: `docs/standards/README.md` names three groups, has the item and the table row of the frontend profile, the row in the table of task types and the two debts.
- Step 6: `docs/standards/standard_review.md` has the row of the frontend standard and the two changed sentences around the table.
- Step 7: `docs/standards/standard_documentation.md` records the code unit of frontend code.
- Step 8: `docs/standards/decision_registry.md`, entry Technology stack and the Python profile of the standards, carries the two replaced sentences.
- Steps 9 - 11: `plans/api_contract/API_CONTRACT_SHAPE.md`, `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md` and `plans/demo_environment/DEPLOYMENT_SHAPE.md` each got their item under Current state. `git status` was read right before these edits and showed no work of another session in those directories.
- Steps 12 - 14: `plans/mvp/MVP_PLAN.md` got D-4, lost the item Q-3 under Open questions and got the plan of this initiative under Supplementary files.
- Step 15: `agent_docs/memory/frontend/_shared.md` was created with the one entry.

### Checks of the Definition of Done

- `git diff -w` of the four documents of steps 2 - 8 shows only the planned lines. `git diff --numstat` of the sibling files: 1 added in each of the three shapes, 3 added and 1 removed in `plans/mvp/MVP_PLAN.md`.
- No file exists under `frontend/`: `git ls-files -- frontend` -> 0 files, and the directory does not exist.
- `npx --no-install prettier --check` on the eleven markdown files this run created or changed and on the files of `plans/frontend_stack/` -> all matched files use Prettier code style.
- `python -m pytest tests/architecture/test_plan_document_contract.py` -> 25 passed, the check of this closed plan included.
- `python -m pytest tests/architecture/test_prose_style.py` -> the two repository-wide checks fail, and every reported path belongs to the design skill: `.claude/skills/impeccable/`, `.agents/skills/impeccable/` and `.claude/agents/impeccable-*.md`. No file this run created or changed is reported.
- `python -m pytest tests/architecture` -> 110 passed, 4 failed out of 114. Besides the two checks above, the two parity checks of `tests/architecture/test_agent_docs_parity.py` fail on the same design skill and its four agent roles, which exist only on the Claude Code side. The two prose checks were red in the baseline run; the two parity checks were not part of the baseline, and they fail only on files this run did not touch. All four lie outside this initiative.

### Review of 2026-10-03

The review by `implementation-dod-review` covered the whole initiative: the changes of steps 1 - 15, the deviations O-1 - O-4, the memory entry and the artifacts of `plans/frontend_stack/`.

Blockers: none.

Risks:

- R-1. The Python tools of the tool map - ruff, mypy, vulture, deptry, bandit and pip-audit - are not installed on this machine, so their commands were not run. The change holds no Python file, so nothing of it falls under them.
- R-2. The gates of the branch are red for a reason outside this change: 4 of the 114 architecture tests fail and `npx --no-install prettier --check "**/*.md"` reports 62 files, every one of them a file of the design skill added by commit `9578638`, which `dev` already contains. No file of this change is reported by either. The merge request of this branch carries the same red until the owner of that skill settles it.
- R-3. `origin/dev` is three commits ahead of the last merge into this branch. The lines it changed in `docs/standards/decision_registry.md` and `plans/mvp/MVP_PLAN.md` are not the lines of this change, so the merge is expected to be clean; it is left to the human who prepares the merge request.
- R-4. Two lines of other owners became stale and were left as the plan asks: `plans/mvp/MVP_PLAN.md`, section Risks, still counts Q-3 among the open questions (O-4), and `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, section Current state, still says that neither the routing engine nor the frontend is decided, right above the new item.
- R-5. The branch `origin/js/frontend-shape` is not merged into this branch and carries its own version of `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, the parallel interview the shape names. It bears on the archive, see the closing entry.

Improvements:

- I-1. `docs/standards/standard_frontend.md`, section What this standard does not cover, gave a reason that traces to no decision of the plan or of the shape. Fixed: the section now names the decision against a full frontend profile.
- I-2. `AI_WORKFLOW.md` has no log entry for this change. The plan does not list the file, and a standard for frontend code is not a change to a skill, a hook, an agent role or the rules of the core. Left to the user.

Verification, every standard of the map:

- `standard_agentic_workflow.md` - checked automatically: `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> 61 passed, 2 failed, both on the design skill (R-2).
- `standard_agent_docs.md` - checked automatically: `pytest tests/architecture/test_plan_document_contract.py` -> 25 passed. The memory entry and this file were read against the formats of the standard.
- `standard_review.md` - checked manually: the tool map has the row of the new standard, and this list goes through all nineteen rows.
- `standard_documentation.md` - checked manually: the code unit is recorded, and its pair of documents is not created up front, with the condition in the memory of the unit.
- `standard_formatting.md` - checked automatically: `npx --no-install prettier --check` passes on every file of this change, the repository-wide run reports only the design skill (R-2); `pytest tests/architecture/test_prose_style.py` reports no file of this change (R-2). `ruff format --check .` was not run (R-1).
- `standard_git.md` - checked automatically: `pytest tests/architecture/test_conflict_markers.py` -> 8 passed. The agent ran no `git add`, commit, push or merge.
- `standard_architecture.md`, `standard_config.md`, `standard_database.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md`, `standard_time.md` and `standard_worker.md` - not applicable: the change holds no Python code, no configuration, no schema object and no periodic task.
- `standard_tests.md` - not applicable to the content of the change, which adds no test; `pytest tests/architecture` -> 110 passed, 4 failed (R-2).
- `standard_frontend.md` - checked manually: its gates are not set up and no frontend code exists. The standard itself was read against D-11 of the plan, section by section.

First verdict: ready after minor fixes, for the whole initiative, with no blocker.

After the fix of I-1, `npx --no-install prettier --check` on the files of this change, `pytest tests/architecture/test_plan_document_contract.py` and the prose check of the changed files passed again.

Final verdict: ready, for the whole initiative `plans/frontend_stack/`. R-2 - R-4 stay as steps left to people outside this run.

### Archive

The verdict covers the whole initiative, so the directory qualifies for `plans_finished/` under `docs/standards/standard_agentic_workflow.md` ch. 4.6. The move was not made in this run, and the question went to the user, for three reasons the chapter does not list among its checks:

- `origin/js/frontend-shape` is not merged and changes `plans/frontend_stack/FRONTEND_STACK_SHAPE.md` in place (R-5). Merged after a move, it meets a file that is no longer there, and the same initiative can end up in both locations at once.
- The move rewrites the location of the reference in the editable documents that name `plans/frontend_stack/`: twenty files outside this directory besides seeds, earlier review entries and memory, most of them artifacts of other owners. One of those lines, in the entry Technical directions of the MVP plan of `docs/standards/decision_registry.md`, was changed on `origin/dev` after the last merge (R-3), so the rewrite would turn a clean merge into a conflict.
- The files of this change are not committed yet, and steps 2 - 14 put the path `plans/frontend_stack/` into them in the wording the plan fixed.

Decided by the user on 2026-10-03: the directory stays in `plans/` until the merge request of this branch is merged into `dev` and the branch `origin/js/frontend-shape` is settled. The move is then made on the user's instruction, with the checks of ch. 4.6. The verdict above is not changed by this: the work of the initiative is finished, and only its location waits.

## Merge of dev into the branch on 2026-10-03

`dev` at `49aa204` was merged into the branch at the user's request. R-3 expected a clean merge; `dev` moved further after that entry, and two files this initiative changed conflicted.

- `plans/mvp/MVP_PLAN.md`, section Decisions: `dev` had taken D-4 for the source of the OpenStreetMap data and D-5 for the mapping of OpenStreetMap tags. The frontend decision that step 12 added as D-4 is D-6 after the merge, with its text unchanged, and the item of step 14 under Supplementary files names D-6. Agent decision at C:40, without asking: D-4 and D-5 of `dev` are referred to by `agent_docs/memory/_cross_cutting.md`, by `plans/fact_schema/FACT_SCHEMA_SHAPE.md` and `plans/fact_schema/FACT_SCHEMA_PRD.md`, and by the Risks and the items Q-10 and Q-11 of the plan itself, while the frontend decision was referred to by its number only in the artifacts of this initiative.
- Wherever `plans/frontend_stack/FRONTEND_STACK_PLAN.md` (steps 12 and 14, Definition of Done) and the entry on steps 12 - 14 above say D-4 of `plans/mvp/MVP_PLAN.md`, the decision meant is D-6. The plan is a contract and was not edited.
- `plans/mvp/MVP_PLAN.md`, section Open questions: neither Q-2, settled on `dev` as D-4, nor Q-3, settled by this initiative, is listed any more.
- `plans/api_contract/API_CONTRACT_SHAPE.md`, section Current state: both new items are kept, the item of step 9 right after the item of `plans/geocoding/`, as the step asks, and the item of `plans/osm_data_source/` from `dev` after it.
- `plans/frontend_stack/FRONTEND_STACK_SHAPE.md` and `docs/standards/decision_registry.md` were changed on both sides and merged without a conflict: `dev` added one item to Current state of the shape and changed the entry Technical directions of the MVP plan of the registry, which this initiative does not touch.
- O-4 still holds: the Risks of `plans/mvp/MVP_PLAN.md`, in the wording of `dev`, name Q-3 among the open questions that depend on no other.
- Checks after the merge: `python -m pytest tests/architecture/test_conflict_markers.py tests/architecture/test_plan_document_contract.py` -> 33 passed; `python -m pytest tests/architecture` -> 110 passed, 4 failed out of 114, the same four checks as in R-2, every reported path a file of the design skill; `npx --no-install prettier --check` on the four files named above -> all matched files use Prettier code style.
- The agent ran no `git add` and no commit: marking the two files as resolved and concluding the merge is left to a human.
