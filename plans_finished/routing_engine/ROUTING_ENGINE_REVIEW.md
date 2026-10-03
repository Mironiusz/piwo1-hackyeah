# Review: Choice of the routing engine for the MVP

Document state: 2026-10-03, implementation finished, review ready for the whole initiative, moved to `plans_finished/`

## Implementation run of 2026-10-03

### Check before implementation

- The plan was committed at 20:27 as `b5f03be`, with a clean tree. `ROUTING_ENGINE_SHAPE.md` has a closed interview, regulator C:40, no open question and no `Block: yes`; the plan has no open question and no TODO.
- Facts: the lines cited by F-2 - F-14, F-18 - F-21 and F-29 - F-36 carried the cited content at `b5f03be`, and every fragment that steps 1 - 9 replace or follow stood verbatim in its file. F-15 - F-17 and F-22 - F-28 were not repeated: they are runs and reads of outside documentation of the same day, and no step writes a file that depends on them beyond quoting F-26.
- Free numbers: the last decision of `plans/mvp/MVP_PLAN.md` at `b5f03be` was D-7, and Q-1 stood under its Open questions.
- The specification has carried "None at version N." under Open questions since version 2, and every version raised it (`git log -G "None at version" -- docs/product/specification.md`), while step 1 does not name that line. See O-1.

### Merges during the run

- First merge of `dev` (`0652dd5`, committed by a human as `6f45949`): it brought `plans/fact_schema/FACT_SCHEMA_PLAN.md`, a closed plan of the task `FACT_SCHEMA` that also writes version 5 of the specification, inserts D-8 into `plans/mvp/MVP_PLAN.md` and removes every item there that begins with "Q-10". Its D-6 stores the nodes of every stored way in order (`osm_way_node`) and every node with its point (`osm_node`), in the one transaction of its D-2. See O-2 and O-3. Its conflict in `plans/fact_schema/FACT_SCHEMA_PRD.md` was resolved by the session "Merge konflikty i decyzje architektoniczne", which keeps the name `SCHEMA_REVISION` for the second task of that initiative.
- Second merge of `dev` (`4bc77ee`), in progress while this run continued: it changes `docs/product/specification.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md` and `plans/api_contract/API_CONTRACT_SHAPE.md`, the targets of steps 1, 2.2, 2.3, 3 and 7, and leaves the targets of steps 2.1, 4, 5, 6 and 9 alone. See O-4.

### Deviations from the plan

O-1. Step 1 gets an eighth change: under Open questions of the specification, "None at version 4." becomes "None at version 5.". The user approved it on 2026-10-03 together with the text of steps 1.1 - 1.7, against leaving the line as it was.

O-2. Version 5 of the specification and the next free decision number of `plans/mvp/MVP_PLAN.md` are taken by this initiative, and `plans/fact_schema/FACT_SCHEMA_PLAN.md` moves to version 6 and the number after it. Decided by the user on 2026-10-03, against this initiative waiting for the task `FACT_SCHEMA` and becoming version 6, and against one shared version 5. The decision was sent to the sessions "Merge konflikty i decyzje architektoniczne" and "Rozwiązanie konfliktów merge"; this run does not edit `FACT_SCHEMA_PLAN.md`, the contract of another initiative.

O-3. Steps 3.3 and 8 are skipped, because `plans/fact_schema/FACT_SCHEMA_PLAN.md` D-6 already stores what D-11 of this plan asks for, and its step 3.4 removes every item of the MVP plan that begins with "Q-10". Decided by the user on 2026-10-03, against carrying both steps out and against step 3.3 as a pointer to that D-6 without step 8. The item of the Definition of Done "the Q-10 input of step 3.3 is listed" is therefore not met by decision. F-11 of the plan was false after the first merge and was rewritten with the plan of `plans/fact_schema/` and its D-6; F-9 and F-10 kept their claims and got the lines the merges moved them to.

O-4. With the second merge in progress, the work on one tree was split with the session "Rozwiązanie konfliktów merge" on 2026-10-03: that session finishes the specification, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md` and `plans/api_contract/API_CONTRACT_SHAPE.md` first and gives the decision number its own merge leaves free, and this run meanwhile edits only `PRODUCT.md`, the registry, the two files of `plans/demo_environment/` and `agent_docs/memory/_cross_cutting.md`. Steps 2.1, 5.1 and 6 were therefore carried out before step 1, against the Rollout order. Agent decision at C:40, without asking: the user asked to continue while the merge is resolved in parallel, and none of the three steps depends on the text of step 1 or on the decision number.

O-5. The state line of the plan does not show the progress of the run, as `plan-implement` asks, because the plan format allows exactly two markers, read by `tests/architecture/test_plan_document_contract.py`. The progress is recorded in this file.

O-6. The sentence of step 1.2 follows a sentence the second merge added after the anchor of that step: "After the approval of version 4, the rules of passwords and their recovery, the 24-hour session and the end of moderator access on the next request after the role is removed were added to it from `plans/account_sessions/`." Agent decision at C:40, without asking, agreed with the session "Rozwiązanie konfliktów merge": placed at the anchor, the account sentence would read as coming after version 5. Step 1.1 replaced the whole state line as planned, so its ending on the account rules added after the approval of version 4 is gone from the state line; the version paragraph and the item Version 4 of Decision provenance still record them.

O-7. The decision number of step 3 is D-9: the second merge brought the decision on account sessions as a second D-7, which the session "Rozwiązanie konfliktów merge" renumbered D-8, so D-9 was the next free number when step 3 was carried out. The session "Demo environment implementation" takes the number after it for Q-7, and `plans/fact_schema/` the next free one when it closes Q-10.

### What was done

- Step 1: `docs/product/specification.md` is version 5 with the text of steps 1.1 - 1.7 approved by the user on 2026-10-03 and the line of O-1, written on the version 4 text that the session "Rozwiązanie konfliktów merge" restored after the second merge.
- Step 2: `PRODUCT.md`, `plans/mvp/MVP_PLAN.md` line 7 and `plans/mvp/MVP_PRD.md` Scope and the first sentence of Domain rules name version 5; "still carries rules that version 4 replaced" stays, and the item "Changed after the gate on 2026-10-03, to follow version 4" got the sentence of step 2.3.
- Step 3: `plans/mvp/MVP_PLAN.md` has D-9 after D-8, no item Q-1, Q-11 depending on D-9, the fragments of step 3.5 replaced in the Risks item on the dependencies of the open questions, and the plan of this initiative as the last item of Supplementary files. Removing "unless the server carries every variant Q-1 still considers" with its pointer also removed the comma before it, so the sentence still reads. Step 3.3 was skipped (O-3).
- Step 4: `docs/standards/decision_registry.md`, entry Technical directions of the MVP plan, says that `plans/routing_engine/` is decided (`plans/mvp/MVP_PLAN.md` D-9). The entry stays open.
- Step 5: `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, Q-1, names the decided routing engine and what it needs from the server in place of the two variants, and the first item of its Risks says that the engine is decided.
- Step 6: `plans/demo_environment/DEPLOYMENT_SHAPE.md` got the routing engine and what makes it stop answering as the last item of Current state.
- Step 7: `plans/api_contract/API_CONTRACT_SHAPE.md` got the segments of a route, the stretches to the network with their unknown stairs and the single alternative as the last item of Current state.
- Step 8 was skipped (O-3).
- Step 9: `agent_docs/memory/_cross_cutting.md` has the entry Route graph in the memory of the backend, with a Decisions field that settles the risk note of the entry Personal data in requests to outside services; the older entry is unchanged.
- The edits of steps 5 and 6 were handed to the session "Demo environment implementation", and those of steps 1 - 3 and 7 were made only after the session "Rozwiązanie konfliktów merge" released the four files. This run added nothing to the index; during the run most of the tree, the specification, `PRODUCT.md` and `plans/mvp/MVP_PLAN.md` with their changes of this run included, was staged outside the agent sessions, so the index holds part of these changes.

### Lines of other owners left as they are

- `plans/mvp/MVP_PLAN.md` still names Q-1 outside the fragments of step 3.5: D-4 ("the routing engine of Q-1") and D-7 ("a choice of pgRouting in Q-1"), which record their own day; the Risks item ("Q-9 depends on Q-10 and Q-6 and not on Q-1"); Q-9 ("It does not depend on Q-1"); Q-10 ("and not on Q-1, which depends on it instead"); and the last item of Open questions, which quotes a former condition. The plan names only the fragments it replaces, and the open questions belong to their own initiatives.
- `docs/standards/decision_registry.md`, the same state sentence, still counts `plans/account_sessions/` among the initiatives in their interviews, although the second merge settled it as D-8 of the MVP plan; that fragment is not part of step 4.
- `plans/fact_schema/FACT_SCHEMA_PLAN.md` still names D-8 for its decision in step 3 and edits `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` in step 6.2; it is the contract of another initiative and is being changed by its own session.

### Checks of the Definition of Done

- `npx --no-install prettier --check` passes on the eleven files this run changed or created: the specification, `PRODUCT.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md`, the registry, the two files of `plans/demo_environment/`, `plans/api_contract/API_CONTRACT_SHAPE.md`, `agent_docs/memory/_cross_cutting.md` and the plan and review of this initiative.
- `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> 4 failed, 110 passed. The four are `test_every_paired_skill_is_at_parity`, `test_every_paired_agent_role_is_at_parity`, `test_repository_has_no_forbidden_characters` and `test_repository_has_no_bold_in_prose`, every reported path a file of `.claude/skills/impeccable/`, `.agents/skills/impeccable/` or `.claude/agents/impeccable-*.md`, the four the Definition of Done of the plan names as failing before this change. `test_plan_document_contract.py` passes with the corrected facts. While the second merge still had conflict markers, `test_repository_has_no_conflict_markers` failed on `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` and `plans/api_contract/API_CONTRACT_SHAPE.md`; it passes now.
- No OpenStreetMap data and no measurement script entered the tree: the run created only `plans/routing_engine/ROUTING_ENGINE_REVIEW.md`.
- AC-5: Q-1 is gone from the open questions of `plans/mvp/MVP_PLAN.md`, D-9 points to this initiative with the constraints of FR-5 of the PRD, and the registry says the initiative is decided. AC-6: Q-1 of `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` names the chosen engine with what it needs from the server and the check of the 5 seconds after the first deployment, and its decisions are unchanged. AC-1 - AC-4 are held by the decisions of the plan, as mapped there.

### Review of 2026-10-03

The review by `implementation-dod-review` covered the whole initiative, which has one task: the changes of steps 1 - 7 and 9, the deviations O-1 - O-7, the corrected facts F-9 - F-11, the memory entry and this file. Only the fragments this run wrote were judged; the other changes in the same files come from the merges of `dev` and from other sessions. Every fragment was checked to be still in its file after those sessions finished.

Blockers: none.

Risks:

- R-1. The merge of `4bc77ee` is not committed, and the index holds part of the changes of this run together with the merge resolution and the work of other sessions. Whoever commits decides whether the version 5 of the specification and D-9 enter the merge commit or a commit of their own.
- R-2. `plans/fact_schema/FACT_SCHEMA_PLAN.md`, a closed plan, still names D-8 for the decision that closes Q-10, while D-8 is now the account sessions and D-9 the routing engine, and its step 6.2 inserts an item into `plans/routing_engine/ROUTING_ENGINE_SHAPE.md`. Its own session is changing it (O-2); until it does, its steps stop on passages that no longer match.
- R-3. `plans/mvp/MVP_PLAN.md` still names Q-1 in the Risks item on the dependencies, in Q-9 and in Q-10 (Lines of other owners left as they are). A reader of those lines meets a question that is no longer open.
- R-4. D-9 and D-11 rest on answers the user gave for the backend person and the db person, whose rulings are still to be confirmed (plan, D-17).
- R-5. The time of reading the stored network from the database and building the graph is not measured; it is checked only on the server after the first deployment (plan, Risks).
- R-6. 4 of the 114 architecture tests fail, every one on the files of the design skill `impeccable`, as before this change.

Improvements:

- I-1. M6 of the specification shows no attribute named in the list for stairs, because a way is never unknown on stairs, while M8 of version 5 names the steps for the stretch to the network. The two do not contradict each other, since the stretch is not a way, but a note in the row of M6 would spare the reader the doubt. A change of the specification needs the approval of the user, so it is left to the next version.
- I-2. `plans/fact_schema/SCHEMA_REVISION_SHAPE.md` says that its rules are those of version 4 of the specification. Version 5 changes none of the rules that task builds, so the pointer is not wrong, but it is for the owner of that task to bring it to the current version.

Verification, every standard of the map:

- `standard_agentic_workflow.md` - checked automatically: `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> 61 passed, 2 failed, both on the design skill (R-6). The checks of ch. 4.7 were made before every edit: `git status`, the files read again and the split of the files agreed with the sessions working on the same tree.
- `standard_agent_docs.md` - checked automatically: `pytest tests/architecture/test_plan_document_contract.py` -> 25 passed, the closed plan of this initiative with its corrected facts included. This file and the memory entry were read against the REVIEW format and the memory entry template, with the optional field Decisions for the settled risk note.
- `standard_review.md` - checked manually: this list goes through all nineteen rows of the tool map.
- `standard_documentation.md` - checked manually: the change creates no code unit; the written text is English, follows the approved text of step 1 and the decisions of the plan, and the deviations are named in this file.
- `standard_formatting.md` - checked automatically: `ruff format --check .` -> 13 files already formatted; `npx --no-install prettier --check "**/*.md"` -> all matched files use Prettier code style; `pytest tests/architecture/test_prose_style.py` -> 2 failed, 16 passed, with no violation in a file of this change (R-6).
- `standard_git.md` - checked automatically: `pytest tests/architecture/test_conflict_markers.py` -> 8 passed. The agent ran no `git add`, commit, push or merge (R-1).
- `standard_config.md` - checked manually: no address, host, account or password of any environment is written; the server of the demo is named only by what it has to carry.
- `standard_database.md` - checked manually: no query and no schema object is written; D-10 and D-12 of the plan, carried into D-9 of the MVP plan, keep the values of a query as parameters. `bandit` B608 has nothing to check.
- `standard_tests.md` - checked automatically: `pytest tests/architecture` -> 110 passed, 4 failed (R-6). The change adds no test; the tests of D-16 come with the route work package of `plans/mvp/`.
- `standard_architecture.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md`, `standard_time.md` and `standard_worker.md` - not applicable: the change holds no Python code, no dependency and no periodic task; numpy and scipy enter `pyproject.toml` only with the route work package (D-14 of the plan).
- `standard_frontend.md` - not applicable: the change holds no frontend code.

Final verdict: ready, for the whole initiative `plans/routing_engine/`. R-1 - R-5 stay with people and sessions outside this run.

### Archive

The final verdict covers the whole initiative, so the directory qualifies for `plans_finished/` under `docs/standards/standard_agentic_workflow.md` ch. 4.6. The agent first proposed to wait, because the merge of `4bc77ee` is not committed and the index already holds files of this directory, because step 6.2 of `plans/fact_schema/FACT_SCHEMA_PLAN.md` inserts an item into `ROUTING_ENGINE_SHAPE.md` of this directory, and because other sessions are editing files that name its path. The user decided on 2026-10-03 to move it now, against waiting for the commit of the merge and against not archiving it at all.

The directory was moved with a native move to `plans_finished/routing_engine/`, after checking that the target did not exist, that `git status` showed in it only the changes of this run, and that it held no link; the five files kept their checksums. The editable references to its path were changed to the new location in the specification, `PRODUCT.md`, the registry, the shapes, PRDs and plans of the initiatives in `plans/` and `plans_finished/`, the design brief `.impeccable/briefs/route-result.md` and the plan and PRD of this initiative. The seeds, the existing review entries, among them the entries above and the reviews of `plans/dependency_check/` and `plans/demo_environment/`, and the entries of `agent_docs/memory/` keep the old path as a historical record. No code or tool reads the files of this initiative. The index still holds the old path of this directory, which the person who commits resolves.
