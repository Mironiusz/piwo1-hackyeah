# Review: Final checklist whose completion means the project is finished

Document state: 2026-10-04, ready for the whole initiative, initiative closed

## Implementation run of 2026-10-04

### Check before implementation

- HEAD at the start was `f8fc67d` on the branch `rm/requirements-preparation`, and the tree was clean. `FINAL_CHECKLIST_SHAPE.md` has a closed interview, the regulator C:40 and no `Block: yes` question; its one TODO, in the section Domain rules or explicit TODO, asks for the registry entry HarmonyOS port and the Huawei submission to drop the variant without a Huawei submission, which scope step 7 of the plan does. The plan is marked closed and has no open question.
- The user asked on 2026-10-04 to close the initiative. All nine steps of Scope of changes were already in the tree, committed by a human in `f7f1391` at 04:18 together with the work of `plans/repository_consistency/`, and the session that wrote them left no review. This run resumed from that state as `docs/standards/standard_agentic_workflow.md` ch. 4.5 describes: it read the state and compared it with the plan instead of writing the changes again.
- Since the plan was written only the merge of `js/mobile_app_init`, pull request 27 with the commit `99c4049`, changed the tree, and every file it changed lies under `mobile_app/`. No file a fact of the plan cites changed. Two facts describe the world outside the cited files and no longer hold as written: F-22, because `git fetch` at the time of this run shows `jmi/odklejka_v1` 5 commits ahead of HEAD instead of 2, and F-23, because `mobile_app/` now holds `accessway/`, a `Makefile`, `scripts/env.sh` and its own `docs/EMULATOR_SETUP.md`, while `docs/setup/EMULATOR_SETUP.md` still names them at the root. The plan was not amended: both facts were true when the changes were written, and what follows from them belongs to checks 1.3 and 8.3 of the list, not to this initiative.

### What was done relative to the plan

- Scope step 1 and 2: twenty `STAGE.md` files exist, one in every initiative of `plans/`, each in the form of D-3, and each number equals the table of PRD FR-6 (rollout step 7, compared file by file). The five new initiatives hold only their seed and their `STAGE.md`, and the prefix of each name matches its stage.
- Scope step 3: `FINAL_CHECKLIST.md` has the title, the state line, the sections How to read this list and Stages, and the ten sets with 42 checks in the wording of PRD FR-5; check 9.5 asks whether the PDFs already tracked by git stay in the public repository, as D-8 says.
- Scope step 4: `MVP.md` says the Huawei submission is mandatory, points to `FINAL_CHECKLIST.md` in the sections How the MVP is built and Sources, has the row of `osm_importer`, the column Starts from with the documents of the plan, the owners of shape requirement 22, the sentence on the deployment configuration, the section Order and critical path by stage and the division of the work as the first item of the section Open decisions and confirmations.
- Scope step 5: `TEAM.md`, column Works on, holds the division of the plan, with the sentence under the table.
- Scope step 6: `docs/hackathon/challenge_requirements.md` points to `docs/official/` in the section Provenance, puts the whole Kraków solution in Polish, says the Huawei jury may invite teams to present, and the row Presentation says so for Huawei.
- Scope step 7: the registry entry HarmonyOS port and the Huawei submission keeps the two clients, drops the variant without a Huawei submission and names check 8.1 as its condition.
- Scope steps 8 and 9: `docs/standards/standard_agentic_workflow.md` has the glossary item Stage and the paragraph at the end of section 3.2, and `AI_WORKFLOW.md`, section Log, has the entry Final checklist, stages of the initiatives and division of the work.
- Rollout step 6: `npx --no-install prettier --check` passes on every file of scope steps 1 - 9. `python -m pytest tests/architecture` fails in two tests of `tests/architecture/test_prose_style.py`, and every violation they report lies under `mobile_app/`; no file of this initiative is named. See Findings.

### Decisions taken during this run

- Agent decision at C:40, without asking: the changes found in `f7f1391` are taken as the implementation of this plan once each scope step was compared with the plan; nothing was written again.
- Agent decision at C:40, without asking: no entry in `agent_docs/memory/`. The only durable rule of this initiative, what `STAGE.md` holds and when it changes, is written in `docs/standards/standard_agentic_workflow.md` section 3.2, and a memory entry would repeat it.

### Findings

- The red architecture tests come from the merge of `js/mobile_app_init`: bold in prose in `mobile_app/AGENTS.md`, `mobile_app/CLAUDE.md`, `mobile_app/README.md` and `mobile_app/AI_WORKFLOW.md`, forbidden characters in a vendored README under `mobile_app/accessway/oh_modules/`, and prettier warnings in eight markdown files under `mobile_app/`. They were left as they are: the work is someone else's and outside this plan (`docs/standards/standard_agentic_workflow.md` ch. 4.7); they belong to check 1.6 of the list.
- The same merge tracks the dependency directory `mobile_app/accessway/oh_modules/` (83 files), the build cache `mobile_app/accessway/.hvigor/` (12 files) and a tile archive `mobile_app/tiles/krakow.pmtiles` of about 33 MB, and `mobile_app/` carries its own `CLAUDE.md`, `AGENTS.md` and `AI_WORKFLOW.md` and the product name AccessWay, which `CLAUDE.md` of the root says is not chosen yet. These touch checks 1.6, 8.3, 9.4 and 9.5 and are reported to the user.
- `mobile_app/` is a native ArkTS/ArkUI client, one of the two variants the registry entry HarmonyOS port and the Huawei submission keeps open; the entry stays open until check 8.1 settles it.

### Review against the Definition of Done

The review ran with the skill `implementation-dod-review` on the files of this initiative: `FINAL_CHECKLIST.md`, the twenty `STAGE.md` files, the five new seeds, `MVP.md`, `TEAM.md`, `docs/hackathon/challenge_requirements.md`, the registry entry HarmonyOS port and the Huawei submission, the item Stage and the end of section 3.2 of `docs/standards/standard_agentic_workflow.md`, the last entry of `AI_WORKFLOW.md`, section Log, and this file.

Blockers: none.

Risks:

- Z-1. At HEAD `f8fc67d` the repository-wide runs are red: two tests of `tests/architecture/test_prose_style.py`, `ruff format --check .` on five scripts under `mobile_app/tools/` and `npx --no-install prettier --check "**/*.md"` on eight files under `mobile_app/`. Every violation lies under `mobile_app/`, which the merge of `js/mobile_app_init` brought after this plan was carried out, and none in a file of this initiative, so the item of the plan Definition of Done that asks for the architecture tests and the prettier check to pass holds for this scope and not for the tree. The fix belongs to the owner of `mobile_app/` or to check 1.6 of the list.
- Z-2. `FINAL_CHECKLIST.md` stays a living document after this initiative is archived: it is ticked and its waits may change. That needs no open initiative, because `docs/standards/standard_agentic_workflow.md` section 3.2 makes the list the source of every `STAGE.md` and asks a change of a wait to update them in the same change, whoever makes it.
- Z-3. Other sessions write in initiatives this one set up, at the same time: `plans/stage1_clarifications/STAGE1_CLARIFICATIONS_SHAPE.md` and `plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_SHAPE.md` are untracked files that appeared during this run. They were not touched, and AC-5, which says a new initiative holds only its seed and `STAGE.md`, describes the state this initiative left, not the later work of their owners.

Improvements:

- U-1. Check 10.5 of the list names the shape of this initiative by its path, requirement 12, where PRD FR-5 says shape requirement 12. The plan does not record it, but inside the list a bare "shape" would point nowhere, so the path is the only readable form; the change keeps the meaning.
- U-2. Check 1.3 names the time 03:56 of 2026-10-04, while AC-2 allows no time other than the deadlines. It is the time of the observation FR-5 quotes word for word, not a deadline of the work, so the intent of FR-3 holds.
- U-3. Check 8.3, Before that, still says the files `docs/setup/EMULATOR_SETUP.md` names are missing; since the merge of `js/mobile_app_init` they exist under `mobile_app/`, next to a second `mobile_app/docs/EMULATOR_SETUP.md`. Which of the two documents stays is for set 8 and check 1.6 to decide.

Acceptance criteria, settled by a run where one is possible:

- AC-1: a script compared the 42 checks of the list with the table of PRD FR-5 part by part; they match except check 9.5, changed by D-8 of the plan, and check 10.5 of U-1. The ten sets stand in the order of FR-1.
- AC-2: a search of the list for the six first names of `TEAM.md`, times, addresses, hosts and secrets found only the deadline 11:00 twice and the time of U-2; only check 4.2 is marked optional.
- AC-3 and AC-4: a script built the waits between the initiatives from the checks of the list, computed every stage by the rule of FR-6 and compared it with the twenty `STAGE.md` files: no mismatch, no cycle, and no initiative of `plans/` missing from the list.
- AC-5: the five new directories held only their seed and `STAGE.md` when this initiative left them (Z-3), each prefix matches its stage, and the five seeds are identical below their opening paragraph, quoting the message of the user and the four closed questions with their answers.
- AC-6 and AC-7: read against FR-9 - FR-13 and scope steps 4 - 9 of the plan; every item holds.
- AC-8: check 4.1 says the code is written from `plans_finished/valhalla_routing/` and the contract while check 3.1 is not met, and check 1.1 names set 8, checks 9.4, 10.3 and 10.4 and the Huawei part of 10.5.
- AC-9: `npx --no-install prettier --check` passes on every file of this initiative, and `tests/architecture/test_prose_style.py` reports nothing outside `mobile_app/`.

Verification against the map of `docs/standards/standard_review.md`, section Standard - verifying tool map:

- `standard_agentic_workflow.md`: checked automatically, `pytest` on its four mapped tests passed, together with the tests of `standard_agent_docs.md` and `standard_git.md` (101 passed); the item Stage and section 3.2 were also read.
- `standard_agent_docs.md`: checked automatically, `tests/architecture/test_plan_document_contract.py` passed; the five seeds and this file were read against the sections SEED format and REVIEW format.
- `standard_review.md`: checked manually, this review follows its order and its Definition of Done.
- `standard_documentation.md`: checked manually, every changed document is in English and points to the documents that decide, not to line numbers.
- `standard_formatting.md`: checked automatically, see Z-1 and AC-9; no violation in the files of this initiative.
- `standard_git.md`: checked automatically, `tests/architecture/test_conflict_markers.py` passed; the agent made no commit.
- `standard_architecture.md`, `standard_config.md`, `standard_database.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md`, `standard_tests.md`, `standard_time.md` and `standard_worker.md`: not applicable, the initiative changes no Python code, configuration or database; the rule of `CLAUDE.md` that no address, host, login or secret enters the repository was checked by the search of AC-2.
- `standard_frontend.md`: not applicable, no frontend code changed.

Verdict: ready, for the whole initiative `final_checklist`. The initiative qualifies for `plans_finished/` under `docs/standards/standard_agentic_workflow.md` ch. 4.6.

### Archiving

- On 2026-10-04 the directory was moved whole from `plans/final_checklist/` to `plans_finished/final_checklist/` by a native move, after checking that the target did not exist, that `git status` showed no change in the directory other than this file and that it held no link. The SHA-256 sums of its six files are the same before and after the move. The git index and the commit are left to a human.
- Editable references were updated to the new path: three in `FINAL_CHECKLIST.md`, three in `MVP.md`, one in `TEAM.md`, one in `docs/standards/decision_registry.md`, entry HarmonyOS port and the Huawei submission, one in `FINAL_CHECKLIST_SHAPE.md` and thirteen in `FINAL_CHECKLIST_PLAN.md` of this initiative, which changed nothing else.
- Agent decision at C:40, without asking: D-5 of the plan keeps `plans/final_checklist/`, because it describes the words of the opening paragraph of the five seeds, and the seeds keep the old path as a historical record.
- Left unchanged as historical records: the five seeds of the `stage` initiatives, `plans/repository_consistency/REPOSITORY_CONSISTENCY_REVIEW.md` and the entries of `AI_WORKFLOW.md`, section Log. No code or tool reads the files of this initiative; `tests/architecture/test_plan_document_contract.py` reads plans in `plans_finished/` as well.
