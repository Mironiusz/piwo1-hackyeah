# Review: Choice of the source of OpenStreetMap data for the MVP

Document state: 2026-10-03, implementation finished, the directory stays in `plans/` until the user decides on the move

## Implementation run of 2026-10-03

### Check before implementation

- The plan was closed at 18:29. The last commit touching a file it cites is 7178497 at 17:38, and the target files of steps 1 - 11 were last written between 16:46 and 17:43, so the facts of the plan still hold. The quoted fragments of steps 3 - 6 and 8 - 11 were found verbatim, and `plans/mvp/MVP_PLAN.md` had D-1 - D-3, so D-M is D-4.
- F-25 and F-34 were checked against `plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md`, untracked and written by another session at 18:28: the cited lines 44, 100 - 112, 147, 159, 169, 193 - 199 and 249 still carry the cited content. Its steps 5 and 6 append items to `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` and `plans/api_contract/API_CONTRACT_SHAPE.md`, which steps 8 and 11 here do not touch, so the two plans still apply in either order.
- F-35 was run again before any change: the same four architecture tests fail, with no violation under `plans/`.
- `plans/osm_data_source/OSM_DATA_SOURCE_SHAPE.md` has no open question, and the plan has none either.

### Deviations from the plan

None. The state line of the plan stays `plan closed`; progress is recorded here, as in `plans/geocoding/GEOCODING_REVIEW.md`.

### What was done

- Steps 1 - 7: `plans/mvp/MVP_PLAN.md` got D-4, lost the item Q-2 under Open questions, got the replacements of steps 3 - 6 in the items Q-10, Q-11 and the Risks item, and got the item of step 7 under Supplementary files. The references to Q-2 inside the passages `plans/osm_barrier_mapping/` quotes stay, as the plan says.
- Step 8: `plans/routing_engine/ROUTING_ENGINE_SHAPE.md`, section Current state, the item on the undecided source is replaced.
- Step 9: `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, item Q-1, got the sentence with the measurements.
- Step 10: `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, section Current state, got the item on the attribution as its last item.
- Step 11: `plans/api_contract/API_CONTRACT_SHAPE.md`, section Current state, got the item on the two dates after the item of `plans/geocoding/`.
- Memory: `agent_docs/memory/_cross_cutting.md` got an entry on OpenStreetMap data in the repository and the identity of an OpenStreetMap element, because the rules of D-7 and D-16 bind the tests and the code of the tag mapping and of the routing too, and the plan of `plans/osm_barrier_mapping/` does not state them for its tests.

### Checks of the Definition of Done

- `git diff --numstat` of the files outside `plans/osm_data_source/`: 7 added and 5 removed in `plans/mvp/MVP_PLAN.md`, 1 changed line in each of `ROUTING_ENGINE_SHAPE.md` and `DEMO_ENVIRONMENT_PLAN.md`, 1 added line in each of `FRONTEND_STACK_SHAPE.md` and `API_CONTRACT_SHAPE.md`. `docs/product/specification.md` is unchanged.
- `npx --no-install prettier --check` on the five changed files and the files of `plans/osm_data_source/` -> all files use Prettier code style.
- `venv\Scripts\python.exe -m pytest tests/architecture -o addopts=-ra -q` -> 4 failed, 110 passed; the failures are the four of F-35, and `test_plan_document_contract.py` passes on this closed plan. `fetch_prose_style_summary` of `tests/architecture/test_prose_style.py` reports no forbidden character and no bold under `plans/` or `docs/`.

### Parallel work on the same files

Between 18:36 and 18:37, after steps 1 - 11 were done, the session of `plans/osm_barrier_mapping/` applied its steps 2, 4, 5 and 6 to the same tree: it added D-5 to `plans/mvp/MVP_PLAN.md`, taking the next free number after D-4 as its plan says, rewrote the Q-8 passages and the item Q-10 caveats there, appended its items to `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` and `plans/api_contract/API_CONTRACT_SHAPE.md` after the items of steps 8 and 11, appended to the Dependencies of `plans/osm_data_source/OSM_DATA_SOURCE_PRD.md` the sentence F-25 foresees, and wrote version 3 of `docs/product/specification.md`. None of it was reverted. The texts of steps 1 - 11 were checked again afterwards and each is present exactly once; `npx --no-install prettier --check` and `pytest tests/architecture` gave the same results as above.

### Review of 2026-10-03

The review by `implementation-dod-review` covered the whole initiative: steps 1 - 11, the memory entry and the artifacts of `plans/osm_data_source/`. Every mapped command was run: the agentic workflow tests, `test_plan_document_contract.py` (25 passed), `ruff format --check .`, `npx --no-install prettier --check "**/*.md"`, `test_prose_style.py`, `test_conflict_markers.py`, `ruff check .`, `mypy`, `vulture`, `deptry .`, both bandit passes of the makefile and the full `pytest`. The only failures are the four tests of F-35 and prettier on 62 files, all under `.claude/skills/impeccable/` and `.agents/skills/impeccable/`, added by commit 9578638 and outside this plan.

No blocker, two risks and one improvement.

- R-1. The changed shared files now carry the changes of two initiatives interleaved in the same sections, so the commit and the Merge Request of the human have to take them together or split them with care.
- R-2. The initiative qualifies for `plans_finished/` by its verdict, but the move is held. `plans/osm_barrier_mapping/` is still being implemented in another session, its active plan and review cite `plans/osm_data_source/` paths, and its Definition of Done checks `plans/osm_data_source/OSM_DATA_SOURCE_PRD.md` by path. Moving now would mean editing the references in that work in progress, which `docs/standards/standard_agentic_workflow.md` ch. 4.7 forbids, and would break its checks. The decision goes to the user.
- I-1. `plans/mvp/MVP_PLAN.md` still names Q-2 in the Risks item, in the item Q-10 and in the item that begins "Q-10 inputs from `plans/osm_data_source/OSM_DATA_SOURCE_SHAPE.md`", which the plan left on purpose because the other plan quoted those passages. Now that both plans have landed, they could read "the former Q-2 (D-4)". No change: it is outside the steps of this plan.

Final verdict: ready, for the whole initiative `plans/osm_data_source/`.

The user decided on 2026-10-03 to leave the directory in `plans/` for now (R-2). It moves to `plans_finished/` once the session of `plans/osm_barrier_mapping/` has finished its review, by the user or at the user's instruction.
