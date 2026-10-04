# Review: Choice of the address search for the MVP

Document state: 2026-10-03, implementation finished, review ready for the whole initiative, moved to `plans_finished/`

## Implementation run of 2026-10-03

### Check before implementation

- The facts of `plans/geocoding/GEOCODING_PLAN.md` were checked again at 16:31: no commit since the plan was written, and the lines cited by F-13 and F-19 - F-22 still carry the cited content. The standards cited by F-14 - F-18 are unchanged in the working tree.
- Another session works on `plans/demo_environment/` at the same time: its shape was written at 16:27 and is now in the state interview closed, and the files `DEMO_ENVIRONMENT_PRD.md`, `DEMO_ENVIRONMENT_PLAN.md` (plan in progress), `DEPLOYMENT_SEED.md` and `DEPLOYMENT_SHAPE.md` (interview in progress) appeared next to it. Its plan says it will edit `plans/mvp/MVP_PLAN.md` too and read it again right before the edit.

### Deviations from the plan

O-1. Step 6 - the item in `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md` - is skipped. The plan did not foresee another session working on that initiative at the same time, and `docs/standards/standard_agentic_workflow.md` ch. 4.7 asks not to fix someone else's work in progress. Decided by the user on 2026-10-03: the constraint reaches that initiative through D-3 in `plans/mvp/MVP_PLAN.md`, which its session reads before its own edit, and the user passes D-15 (one process) and D-16 (the check of a blocked hosting address after the first deployment) of `plans/geocoding/GEOCODING_PLAN.md` to that session.

### What was done

- Steps 1 - 3: `plans/mvp/MVP_PLAN.md` got D-3, lost the item Q-5 under Open questions, and got `plans/geocoding/GEOCODING_PLAN.md` under Supplementary files. Each shared file was read again right before its edit; none had changed since the check above.
- Step 4: `plans/api_contract/API_CONTRACT_SHAPE.md`, section Current state, got the item on the search going through the backend.
- Step 5: `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, section Current state, got the item on the search behavior and the risk of the map tiles.
- Step 6: skipped, see O-1.
- Memory: `agent_docs/memory/_cross_cutting.md` got its first entry, on personal data in requests to outside services. It is cross-cutting because the same rule binds the route request with the current location, and no code unit exists yet from whose path a module file could follow.

### Checks of the Definition of Done

- `git diff` of the three changed files outside `plans/geocoding/` shows only the planned lines: 4 added and 1 removed in `plans/mvp/MVP_PLAN.md`, 1 added in each of the two shapes.
- `npx prettier --check` on `plans/mvp/MVP_PLAN.md`, the two changed shapes and the files of `plans/geocoding/` -> all files use Prettier code style.
- `venv\Scripts\python.exe -m pytest tests/architecture -q` -> 114 passed, the plan contract check of this closed plan and the prose style check included.

### Review of 2026-10-03

The review by `implementation-dod-review` covered the whole initiative: the changes of steps 1 - 5, the skipped step 6, the memory entry and the artifacts of `plans/geocoding/`. Every mapped command was run: the agentic workflow tests, `test_plan_document_contract.py`, `ruff format --check .`, `npx --no-install prettier --check "**/*.md"`, `test_prose_style.py`, `test_conflict_markers.py`, `ruff check .`, `mypy`, `vulture`, `deptry .`, both bandit passes of the makefile and the full `pytest` - all passed. F-3 was run again during the review and still holds: 9 of the 10 results for "Biedronka" have the city Kraków and one has the town Niepołomice.

First verdict: ready after minor fixes, for the whole initiative, with no blocker, one risk and three improvements.

- R-1. The Definition of Done item on the three sibling shapes is not met for `plans/demo_environment/`, by the user decision recorded in O-1. D-3 of `plans/mvp/MVP_PLAN.md` names the single process but only refers to D-16, so the check of a blocked hosting address reaches that initiative only if the user passes it on.
- I-1. D-4 of the plan and the item in `plans/api_contract/API_CONTRACT_SHAPE.md` did not say whether the limit of 200 characters applies before or after normalization. Fixed: the limit applies to the text as received, checked before normalization. Agent decision at C:40, without asking: the input layer validates the length before the rules layer processes the text, and either reading met the PRD.
- I-2. D-2 did not name the thread pool condition of `docs/standards/standard_architecture.md`, section Calls to external systems. Fixed: D-2 now names it.
- I-3. The httpx documentation behind F-12 does not show whether the query string is logged. No change: D-12 switches the logging off regardless.

After the fixes of I-1 and I-2, and the matching text of step 4 in the plan, `npx --no-install prettier --check` on the changed files and `pytest tests/architecture` passed again.

Final verdict: ready, for the whole initiative `plans/geocoding/`. R-1 stays as a step left to the user.

## Consistency check and archiving of 2026-10-03

- The state line said "implementation in progress" under the final ready verdict above. The session of `plans/consistency_check/` corrected it to the verdict, which covers the whole initiative.
- R-1 is settled: the constraints of step 6, D-15 and D-16 of the plan, were added on 2026-10-03 by `plans/consistency_check/` to `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md` with the text of step 6, to item Q-1 of `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, and to `plans/demo_environment/DEPLOYMENT_SHAPE.md`, whose deployment configuration starts the service.
- The user decided on 2026-10-03 to move the initiative to `plans_finished/` (U-8 of `plans/consistency_check/CONSISTENCY_CHECK_REVIEW.md`). The session of `plans/consistency_check/` moved it on the same day under `docs/standards/standard_agentic_workflow.md` ch. 4.6.
