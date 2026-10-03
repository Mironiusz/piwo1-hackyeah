# Review: Mapping of OpenStreetMap tags to the closed list of barriers and amenities

Document state: 2026-10-03, implementation finished, review ready for the whole initiative

## Implementation run of 2026-10-03

### Check before implementation

- No commit since the plan was written at 18:28; the last commit is `5a67a24` of 17:41. The lines cited by F-1 - F-4, F-6 - F-8 and F-10 - F-12 still carry the cited content. F-13 - F-26 are measurements of OpenStreetMap and of the OpenStreetMap wiki and were not run again: no step of the plan depends on their exact numbers, which the plan uses only for decisions and risks.
- Another session implements `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` at the same time. At 18:32 it had written D-4 into `plans/mvp/MVP_PLAN.md`, removed Q-2 there and rewritten the passages its plan names, and by 18:36 it had also changed `plans/routing_engine/ROUTING_ENGINE_SHAPE.md`, `plans/api_contract/API_CONTRACT_SHAPE.md`, `plans/frontend_stack/FRONTEND_STACK_SHAPE.md` and `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`. F-5 was corrected before the start to say that the MVP plan has D-1 - D-4, so D-N of step 2 is D-5, as the plan foresees. The line numbers of F-28 were shifted by one in `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md`, edited after this plan, and were corrected too.
- `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `4 failed, 110 passed`, the four tests of F-27, every reported path a file of the impeccable skill under `.claude/` or `.agents/`. `npx prettier --check` on the files of the Scope of changes -> all files use Prettier code style.

### Deviations from the plan

O-1. Step 2.6 got a longer text than the plan quotes. The plan replaces the Q-10 caveat with "the rules above are in `docs/product/specification.md` version 3, written by `plans/osm_barrier_mapping/` and approved by the user.", but the implementation of `plans/osm_data_source/` had meanwhile put above that caveat the item with the weight of a vote after its 30-day identifier is deleted, which version 3 deliberately leaves out (D-2 here, D-21 there). The literal text would have said that this rule, too, is in the specification. Decided by the user on 2026-10-03, against the literal text: the caveat ends with ", except the weight of a vote after its 30-day identifier is deleted, which lives in `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-21."

### What was done

- Steps 1.1 - 1.9: `docs/product/specification.md` raised to version 3. The part of the section Domain rules of the PRD from "Barriers:" to "The thresholds in short: ..." was copied into M6 by a script that took the lines of the PRD as they are and removed only " (FR-12)", so the tables are verbatim.
- Step 1.10: the user was shown the changes of steps 1.1 - 1.9 section by section and approved version 3 on 2026-10-03 without changes; the sentence "The user approved this version on 2026-10-03." closes the version 3 entry of Decision provenance.
- Step 2: `plans/mvp/MVP_PLAN.md` got D-5, the next free number after D-4 of `plans/osm_data_source/`, lost the item Q-8 under Open questions, and got the replacements of steps 2.1 and 2.4 - 2.8, step 2.6 as in O-1. The file was read again right before the edit; every passage quoted by steps 2.4 and 2.7 was still there after the edits of the parallel session.
- Step 3: `plans/mvp/MVP_PRD.md` got the four replacements. `plans/mvp/MVP_SHAPE.md` is unchanged.
- Steps 4 - 6: `plans/osm_data_source/OSM_DATA_SOURCE_PRD.md`, `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` and `plans/api_contract/API_CONTRACT_SHAPE.md` got their items. The two shapes had been changed by the parallel session at 18:33; they were read again before the edit, and the new items stand after the last item of Current state, after the items of `plans/osm_data_source/`.
- Memory: `agent_docs/memory/_cross_cutting.md` got an entry on the thresholds living both in the specification and next to the rule, and on the two kinds of absence. It is cross-cutting because it ties the specification to the import and the route, and no code unit exists yet from whose path a module file could follow.

### Checks of the Definition of Done

- `git diff` of the changed files outside `plans/osm_barrier_mapping/` shows only the lines of steps 1 - 6 next to the lines of the parallel session: 44 lines added and 5 replaced in the specification, 1 decision added, 1 item removed, 1 supplementary file added and 6 passages replaced in the MVP plan, 4 lines replaced in the MVP PRD, 1 sentence appended in the data source PRD and 1 item added in each of the two shapes.
- `npx prettier --check` on the six changed files and the five files of `plans/osm_barrier_mapping/` -> all files use Prettier code style.
- `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `4 failed, 110 passed`, the same four tests as F-27, every reported path a file of the impeccable skill; `test_plan_document_contract.py` passes on this closed plan.

### Review of 2026-10-03

The review by `implementation-dod-review` covered the whole initiative: steps 1 - 6 with O-1, the corrected facts F-5 and F-28, the memory entry and the artifacts of `plans/osm_barrier_mapping/`. The lines written by the parallel implementation of `plans/osm_data_source/` in the same files were outside it. Every mapped command was run: the agentic workflow tests, `test_plan_document_contract.py` (25 passed), `ruff format --check .`, `npx --no-install prettier --check "**/*.md"`, `test_prose_style.py`, `test_conflict_markers.py`, `ruff check .`, `mypy`, `vulture`, `deptry .`, both bandit passes of the makefile and the full `pytest`. The only failures are the four tests of F-27, and prettier reports 62 files, all of them files of the impeccable skill, outside this change. A script compared the tag rules in M6 of the specification with the section Domain rules of the PRD: identical except the removed " (FR-12)". `plans/mvp/MVP_SHAPE.md` and `AI_WORKFLOW.md` are unchanged.

No blocker and no risk. Two improvements, both left without a change:

- I-1. AC-15 of the PRD names sections M2, M4 and M7 for the thresholds being common to all profiles, while version 3 states it in M6, in the opening paragraph of the tag rules, where step 1.5 of the plan put it. The rule is in the specification, and the specification was approved in this wording; no change.
- I-2. In the item Q-10 of `plans/mvp/MVP_PLAN.md` the words "both interviews closed on 2026-10-03" now follow a reference to the specification and one to a shape, because step 2.4 replaced only the reference to the shape of this initiative. Both interviews were in fact closed, so the sentence stays true; no change.

Verdict: ready, for the whole initiative `plans/osm_barrier_mapping/`. Steps left to people: the import person confirms or changes the thresholds before the demo is recorded, and a human makes the commit and the Merge Request.

### Archiving

The verdict qualifies the initiative for `plans_finished/`, but the directory stays in `plans/`. Moving it means rewriting the editable references to `plans/osm_barrier_mapping/` in 24 files outside it, among them `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` and `OSM_DATA_SOURCE_PRD.md`, while the session implementing `plans/osm_data_source/` was still at work on the same tree, and during this review about sixty files of the impeccable skill under `.claude/` and `.agents/` were being changed by someone else. Decided by the user on 2026-10-03, against moving now: the move is left to an agent asked to clean up `plans/` once the parallel work is wrapped up.

## Archiving of 2026-10-03

The parallel work named above is wrapped up: `plans_finished/osm_data_source/` has its final ready verdict. The user decided on 2026-10-03 to move this initiative to `plans_finished/` (U-8 of `plans/consistency_check/CONSISTENCY_CHECK_REVIEW.md`), and the session of `plans/consistency_check/`, asked to clean up `plans/`, moved it on the same day under `docs/standards/standard_agentic_workflow.md` ch. 4.6.
