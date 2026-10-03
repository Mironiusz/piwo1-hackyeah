# Review: Check of cyclic dependencies between the open questions of the MVP plan, and its fixes

Document state: 2026-10-03, fixes applied, review after fixes ready for the whole initiative, moved to `plans_finished/`

## Check of 2026-10-03

### Scope

The agent read the open questions Q-1, Q-6, Q-7, Q-9, Q-10 and Q-11 of `plans/mvp/MVP_PLAN.md` with its Risks and decisions D-1 - D-7, `plans/mvp/MVP_PRD.md`, and the dependencies each initiative behind those questions states in its own artifacts: `plans/routing_engine/` (shape, PRD), `plans/account_sessions/` (shape), `plans/demo_environment/` (shape, PRD, plan, and the shape of its task `DEPLOYMENT`), `plans/api_contract/` (shape) and `plans/fact_schema/` (shape, PRD), together with `docs/standards/decision_registry.md`, entry Technical directions of the MVP plan, and `plans_finished/local_database/LOCAL_DATABASE_PLAN.md`. The initiative has no shape, PRD or plan: the request was a check and its fixes, and this file records both, as in `plans_finished/consistency_check/`.

### Findings

The findings name the paths as they were at the time of the check. The first report to the user called C-1 a deadlock that appears only when Q-10 is taken to close with the implementation of `plans/fact_schema/`. While preparing the fixes the agent found D-8 of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md`, which makes the cycle real under either reading, and said so to the user in the proposal.

C-1. Q-10 and the backend skeleton. `plans/fact_schema/` decides the model and also builds the first schema revision (FR-15 of its PRD, question 1 of its shape). The revision needs a backend skeleton with the Alembic configuration, built by the work package of D-7 of the MVP plan, whose file names and locations D-8 of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` leaves to that work package because Q-11 shapes the skeleton. That work package starts only once the MVP plan is closed, and the MVP plan closes only once Q-10 is closed (`plans/mvp/MVP_PLAN.md`, Risks, first item). A plan of `plans/fact_schema/` that also builds the revision therefore cannot be completed without guessing the layout of the skeleton, Q-10 cannot close, and the loop Q-10 -> FR-15 -> skeleton of D-7 -> closing of the MVP plan -> Q-10 closes. No requirement of `plans/fact_schema/FACT_SCHEMA_PRD.md` closed Q-10, unlike FR-5 of `plans/routing_engine/ROUTING_ENGINE_PRD.md` for Q-1 and FR-3 of `plans/demo_environment/DEMO_ENVIRONMENT_PRD.md` for Q-7.

C-2. Q-1 and Q-10 depend on each other through different artifacts. `plans/routing_engine/ROUTING_ENGINE_PRD.md` FR-3 reads FR-5 of the PRD of `plans/fact_schema/` and answers what that PRD left to it, while `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, section Challenging own assumptions, and its PRD, Dependencies, ask to be checked against `plans/routing_engine/` when it closes, "not assumed". `plans/mvp/MVP_PLAN.md` said flatly that Q-10 does not depend on Q-1, and its Risks did not list the dependency of Q-1 on Q-10. Not a deadlock, because the PRD of Q-10 is confirmed, but a plan of Q-10 written before Q-1 closes could need rework.

C-3. Q-6 and Q-9 could wait for each other. Open question 3 of `plans/api_contract/API_CONTRACT_SHAPE.md` still asked in which order the contract and `plans/account_sessions/` are settled, while `plans/mvp/MVP_PLAN.md`, Risks, already ordered Q-6 before Q-9. Question 3 of `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` (what a moderator may see and do) overlapped question 5 of the contract (what each role may read and do through the interface), with no rule on which settles what. The session mechanism also depends on which clients use the interface, which question 2 of the contract still asks, while `plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md` already decided it.

C-4. `plans/mvp/MVP_PLAN.md`, Risks, named the critical path Q-10 -> Q-9, while Q-6 takes the stored form of accounts from Q-10 and Q-9 waits for Q-6, so the path is Q-10 -> Q-6 -> Q-9.

C-5. No cycle, recorded so that it is not checked again: the loop between Q-7 and Q-11 through the deployment configuration was cut by the task `DEPLOYMENT` of `plans/demo_environment/`, and FR-1 - FR-4 of `DEMO_ENVIRONMENT_PRD.md` no longer wait for Q-11; open question Q-1 of `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` mentions the machine Q-11 chooses for the import, but it checks the server for the import anyway, so Q-7 does not wait for Q-11; the 5 seconds of `plans/routing_engine/ROUTING_ENGINE_PRD.md` FR-1 on the server of the demo are measured on the machine of the agent's session and checked after the first deployment, so Q-1 does not wait for Q-7.

## Proposal and decisions of the user

After message 2 of the seed the agent proposed a fix for each finding and asked three questions: whether `plans/fact_schema/` is split (recommended) or the revision handed to a work package of `plans/mvp/`, and whether the name `SCHEMA_REVISION` fits; whether the routing engine adapts to FR-5 of the PRD of `plans/fact_schema/`; who removes the moderator role. It also asked whether the user answers for the db and backend persons, as before. The user answered with message 3, "apply all these fixes", which the agent takes as accepting every recommendation of the proposal. The user has not stated being the db or the backend person, so the rulings of those persons are still to be confirmed, as elsewhere in these initiatives. The part of the proposal about `plans/fact_schema/` is quoted verbatim in `plans/fact_schema/SCHEMA_REVISION_SEED.md`.

U-1 (C-1). `plans/fact_schema/` is split into two tasks, after the pattern of `DEMO_ENVIRONMENT` and `DEPLOYMENT` in `plans/demo_environment/`. The task `FACT_SCHEMA` keeps the rules and the target schema (FR-1 - FR-14) and gets FR-16, which closes Q-10 of the MVP plan with a decision entry; Q-10 closes when that task is implemented, which needs documents only. The new task `SCHEMA_REVISION` builds the first schema revision: it meets FR-15, AC-1 - AC-12 and the part of AC-13 about the stored data, and starts once the task `FACT_SCHEMA` is implemented and the backend skeleton of D-7 exists. This keeps the decision of question 1 of `FACT_SCHEMA_SHAPE.md` that the initiative builds the revision. Against handing the revision to a work package of `plans/mvp/`, which also cuts the loop but reverses that decision, and against pulling the skeleton ahead of the closing of the MVP plan, which D-8 of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` ties to Q-11.

U-2 (C-2). The routing engine adapts to what FR-5 of `plans/fact_schema/FACT_SCHEMA_PRD.md` stores, as it adapts to the route response of `plans/api_contract/` (U-5 of `plans_finished/consistency_check/`), and a need beyond FR-5 is raised with the db person, never assumed. `plans/fact_schema/` therefore does not wait for `plans/routing_engine/`. Against deciding Q-1 before the plan of Q-10, which lengthens the path Q-10 -> Q-6 -> Q-9.

U-3 (C-3). `plans/account_sessions/` is settled before `plans/api_contract/`. The rules of the roles, the moderator role included, are decided in `plans/account_sessions/` (its question 3), and question 5 of the contract only maps them onto its requests and responses. The session mechanism takes its clients from `plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`, section Domain rules, not from question 2 of the contract.

The third question of the proposal, who removes the moderator role, was not answered; it stays in question 3 of `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, narrowed to what version 4 of `docs/product/specification.md`, M11, does not say.

## Fixes of 2026-10-03

### Parallel work on the same files

Between the check and the fixes the user committed `724d9e8`, which moved `plans/consistency_check/` to `plans_finished/` and rewrote the references to it. The files of this initiative were read again after that commit. `plans/routing_engine/ROUTING_ENGINE_PRD.md` and `ROUTING_ENGINE_SHAPE.md` carried uncommitted changes of the session of `plans/routing_engine/`, which is writing its plan, so under `docs/standards/standard_agentic_workflow.md` ch. 4.7 the change of U-2 to that PRD was handed to that session instead of being made here. The same commit had already fixed in place the external Valhalla variant in `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, F-8 and Q-1, which the first report of this check still named as stale.

### What was done

- C-1, U-1: `plans/fact_schema/SCHEMA_REVISION_SEED.md` and `plans/fact_schema/SCHEMA_REVISION_SHAPE.md` created, the shape with the interview in progress and one open question without a block, on the deadline. `plans/fact_schema/FACT_SCHEMA_PRD.md`, marked as changed after the gate: the Business goal, Scope with the new item on recording the decision, Out of scope with the stored data and the reason, FR-15 marked as handed to the task `SCHEMA_REVISION` and kept with its number, FR-16 new, a note before the acceptance criteria that AC-1 - AC-12 and the stored data part of AC-13 bind the task `SCHEMA_REVISION`, AC-13 with that pointer, AC-14 new, Dependencies and Risks. `plans/fact_schema/FACT_SCHEMA_SHAPE.md`: Smallest meaningful scope with the split and the reason, and functional requirement 11 pointing to the new task. `docs/standards/decision_registry.md`, entry Technical directions of the MVP plan: the split, the closing of Q-10 with the task `FACT_SCHEMA`, and the state of the new task.
- C-1, C-2, C-4: `plans/mvp/MVP_PLAN.md` - Q-10 says when it closes and that it does not depend on Q-1, which depends on it; the Risks item on dependencies rewritten with U-1 - U-3, the dependency of Q-1 on Q-10, the critical path Q-10 -> Q-6 -> Q-9 and the task `SCHEMA_REVISION` next to `DEPLOYMENT`; this review among the Supplementary files.
- C-2, U-2: `plans/fact_schema/FACT_SCHEMA_PRD.md`, Dependencies, and `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, Challenging own assumptions, no longer wait for a check against `plans/routing_engine/`. The matching change to FR-3 and to the Dependencies of `plans/routing_engine/ROUTING_ENGINE_PRD.md` was sent to the session of that initiative on 2026-10-03 with its wording. That session applied it the same day, marked as changed after the gate, and the agent verified it in the file; the change is uncommitted, in the work of that session.
- C-3, U-3: `plans/api_contract/API_CONTRACT_SHAPE.md` - question 3 answered in Challenging own assumptions and removed from the open questions, with the numbering of the rest kept; question 5 narrowed to mapping the rules of `plans/account_sessions/`. `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` - an item in Current state with the clients of the interface from `plans_finished/frontend_stack/`, a note that version 4 answers most of question 3, and question 3 narrowed to what M11 does not say.
- C-4: `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, Problem, and `plans/fact_schema/FACT_SCHEMA_PRD.md`, Business goal, carry the corrected critical path.
- Not changed: `plans/mvp/MVP_PRD.md`, because none of its requirements depends on the order of the open questions; the stale consultation of the external API person in Q-1 of the MVP plan, which `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` already records as without a subject, because it does not touch the dependencies.

### Order of the open questions after the fixes

1. Now, in parallel: the task `FACT_SCHEMA` of `plans/fact_schema/` (Q-10) and phase B of `plans/routing_engine/` (Q-1).
2. Then Q-6 after Q-10, and Q-7 after Q-1.
3. Then Q-9 after Q-6 and Q-10, and Q-11 after Q-1 and Q-7.
4. Then the closing of the MVP plan, the local setup and the backend skeleton of D-7, the tasks `SCHEMA_REVISION` and `DEPLOYMENT`, and after `SCHEMA_REVISION` the critical tests of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 that check the first revision.

## Review of 2026-10-03

### First pass

The review by the `dod-reviewer` agent covered the whole initiative: the dependencies after the fixes, read from the artifacts of every initiative behind the open questions, the post-gate changes of `plans/fact_schema/FACT_SCHEMA_PRD.md` and the references to them across the repository, the formats of the new seeds and shape, the claims of this review against the diff, and formatting. `npx --no-install prettier --check` passed on the changed files, and `pytest tests/architecture` gave 110 passed and 4 failed, the four failures on the files of the impeccable skill that existed before this initiative, none on a changed file. It confirmed that the split of U-1 cuts the loop of C-1, because Q-10 closes with a task that needs no backend skeleton, and that no edge leads back from `SCHEMA_REVISION` or `DEPLOYMENT` to an open question.

Verdict: ready after minor fixes, for the whole initiative.

- R-1. `SCHEMA_REVISION` and the work package of D-7 of the MVP plan depended on each other at the level of execution: D-8 of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` gives that work package critical tests that check the first revision, while the task started only once the work package had built the skeleton. Fixed: the trigger of `plans/fact_schema/SCHEMA_REVISION_SHAPE.md` is the local setup and the skeleton with the Alembic configuration, not the whole work package, those critical tests run after the task, and the shape, the Risks of `plans/mvp/MVP_PLAN.md` and step 4 of the order above say so.
- R-2. This review said the change of U-2 to `plans/routing_engine/ROUTING_ENGINE_PRD.md` was not confirmed, while the file already carried it. Fixed: the state line and the item of What was done.
- R-3. `plans/api_contract/API_CONTRACT_SHAPE.md`, section Challenging own assumptions, still called the HarmonyOS client undecided, against its own Current state and the item added to `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`. Fixed with a note that `plans_finished/frontend_stack/` plans the interface for two clients, while whether the port is built stays in the registry and the stability of the contract stays question 2 of that interview. The answer stands in an artifact of a closed initiative, so question 2 itself was not narrowed (`.claude/skills/plan-shape/SKILL.md`, the signals that keep a found answer from closing a question).
- I-1. `SCHEMA_REVISION_SHAPE.md`, Current state, read as if the task built the rules of FR-1 - FR-14. Fixed: the rules the stored data has to hold.
- I-2. The post-gate markers of `FACT_SCHEMA_PRD.md` were not uniform. Fixed: every changed item says "after the gate".
- I-3. The seed of `SCHEMA_REVISION` declares one divergence from the verbatim original, arrows written as `->`, judged acceptable; `docs/standards/standard_agent_docs.md`, section SEED format, has no rule for a verbatim text that carries a forbidden character. A rule there would be a change of a standard, which is for the user to decide; not changed.
- I-4. `FACT_SCHEMA_SHAPE.md`, section Challenging own assumptions, keeps the sentence "To be checked against that initiative when it closes, not assumed." before the note that settles it. It stays as the record of the interview; not changed.

### Notes from the session of `plans/routing_engine/`

When it applied U-2, the session of `plans/routing_engine/` reported a need beyond FR-5 of `plans/fact_schema/FACT_SCHEMA_PRD.md`, raised under U-2 itself: the graph of the chosen engine needs, for every way of the pedestrian network, the ordered list of its nodes with their coordinates (D-11 of its plan, being written). It reports that the user accepted it for the db person on 2026-10-03, and its plan hands it over as a Q-10 input of `plans/mvp/MVP_PLAN.md` and a sentence in the Dependencies of `FACT_SCHEMA_PRD.md` in its implementation step. That is U-2 working as decided, but the input reaches `plans/fact_schema/` only when `plans/routing_engine/` is implemented, so a target schema written by the task `FACT_SCHEMA` before then has to take it from `plans/routing_engine/ROUTING_ENGINE_PLAN.md` D-11 directly. The chosen engine is a graph in the memory of the backend, not pgRouting, so no revision creates pgRouting. The same plan inserts its decision entry into `plans/mvp/MVP_PLAN.md` as D-8, while FR-16 of `FACT_SCHEMA_PRD.md` adds a decision entry without a fixed number; whichever closes first takes the next free number.

## Review after fixes of 2026-10-03

### Scope

The second pass of the `dod-reviewer` agent, run on the request of the user, covering the whole initiative on branch `rm/requirements-preparation` with a clean working tree: the seed and this review, the files named by the fixes of R-1, R-2, R-3, I-1 and I-2 of the first pass and by U-1 - U-3, and the open questions Q-7, Q-9, Q-10 and Q-11 of `plans/mvp/MVP_PLAN.md` read with decisions D-1 - D-9 as they stand now. The paths `plans/routing_engine/` and `plans/consistency_check/` in the seed and in the dated entries above are historical records (`docs/standards/standard_agentic_workflow.md` ch. 4.6, Protecting history) and are not assessed as findings.

### Blockers

None.

### Risks

- R-1. Open questions of `plans/api_contract/API_CONTRACT_SHAPE.md` says "The contract is settled before Q-10 in `plans/mvp/MVP_PLAN.md`", while Q-9 of that plan depends on Q-10 for the resources and statuses it exposes, its Risks keep the path Q-10 -> Q-9, and D-3 and Q-5 (`Block: yes`) of `plans/api_contract/API_CONTRACT_PLAN.md` keep the plan of the contract waiting for Q-10. The sentence comes from commit `4992bba`, not from the fixes of this initiative, and creates no cycle under either reading, because Q-10 does not wait for the contract: D-14 of `plans/fact_schema/FACT_SCHEMA_PLAN.md` leaves the input limits to the contract and its step 6.1 edits the contract shape, but neither waits for it. It still states the order this initiative settled the other way round. Handed to `plans/api_contract/`: the sentence should say that the shape and PRD of the contract are written before Q-10 closes, while its plan, and with it Q-9, closes after Q-10. It does not block the closure of this initiative.

### Improvements

- I-1. `plans/mvp/MVP_PLAN.md`, Risks, second item, still says "The critical paths are Q-10 -> Q-6 -> Q-9" and describes Q-6 as open; only its last sentence says Q-6 is settled as D-8 and the path Q-10 -> Q-9 remains. Read in order it is not a contradiction, since the later sentence settles the earlier one (ch. 4.6), but one current sentence would read better. For whoever next edits that item.
- I-2. Q-10 of `plans/mvp/MVP_PLAN.md` says the plan of `plans/fact_schema/` is still to be written, while `plans/fact_schema/FACT_SCHEMA_PLAN.md` is in the state plan closed. This concerns the progress of Q-10, not its dependencies, and FR-16 of `plans/fact_schema/FACT_SCHEMA_PRD.md` replaces the entry when Q-10 closes. For `plans/fact_schema/`.

### Confirmation of the fixes of the first pass

- R-1 is present: section Recipient and trigger of `plans/fact_schema/SCHEMA_REVISION_SHAPE.md` makes the trigger the implemented task `FACT_SCHEMA` plus the local setup and the backend skeleton with the Alembic configuration, "that part of the work package, not the whole of it", and the critical tests of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 run after the task. Challenging own assumptions of that shape answers the mutual wait, and Risks of `plans/mvp/MVP_PLAN.md` and step 4 of Order of the open questions after the fixes say the same.
- R-2 is present: the state line before this pass and the item C-2, U-2 of What was done say that the session of the routing engine applied the change and that it was verified, and `plans_finished/routing_engine/ROUTING_ENGINE_PRD.md` records FR-3 and its Dependencies item as changed after the gate on 2026-10-03 by U-2 of this initiative.
- R-3 is present: in `plans/api_contract/API_CONTRACT_SHAPE.md`, Challenging own assumptions, the item on whether the frontend is the only consumer has the note on the two clients planned by `plans_finished/frontend_stack/`; whether the port is built stays in the registry, and the stability of the contract stays question 2 of that interview, since closed.
- I-1 is present: Current state of `SCHEMA_REVISION_SHAPE.md` reads "the rules of FR-1 - FR-14, which the stored data has to hold".
- I-2 is present: all twelve changed items of `plans/fact_schema/FACT_SCHEMA_PRD.md` carry the marker "after the gate on 2026-10-03" with the U-number - Business goal, Scope, Out of scope, FR-15, FR-16, the note before the acceptance criteria, AC-13, AC-14, two Dependencies items and two Risks items.
- I-3 and I-4 are unchanged, as decided; the sentence of I-4 is still in Challenging own assumptions of `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, followed by the note that settles it.

### Confirmation of U-1 - U-3 and of the order of the open questions

- U-1 is present: `plans/fact_schema/SCHEMA_REVISION_SEED.md` and `plans/fact_schema/SCHEMA_REVISION_SHAPE.md` exist; FR-15 is handed over with its number kept, FR-16 and AC-14 exist; functional requirement 11 of `plans/fact_schema/FACT_SCHEMA_SHAPE.md` points to the task `SCHEMA_REVISION`; the entry Technical directions of the MVP plan in `docs/standards/decision_registry.md` names the split; Q-10 of `plans/mvp/MVP_PLAN.md` closes with the task `FACT_SCHEMA`, which needs documents only.
- U-2 is present: the Dependencies of `plans/fact_schema/FACT_SCHEMA_PRD.md` no longer wait for the routing engine, and Q-10 of the MVP plan says Q-1 depends on it, not the other way round. The need beyond FR-5 recorded in Notes from the session of `plans/routing_engine/` reached `plans/mvp/MVP_PLAN.md` D-9 as a constraint on the ordered nodes and coordinates of Q-10. `plans/fact_schema/FACT_SCHEMA_PLAN.md` D-6 stores the line of each way; whether that plan covers the need in full belongs to `plans/fact_schema/` and was not checked here. Decision numbers do not collide: D-8 went to Q-6, D-9 to Q-1, and FR-16 has no fixed number.
- U-3 is present: `plans/api_contract/API_CONTRACT_SHAPE.md` answers question 3 in Challenging own assumptions and lists no open question, question 5 maps the rules of `plans/account_sessions/`, and Current state records that the user rejected parallel work because it contradicts U-3. Current state of `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` has the item on the clients from `plans_finished/frontend_stack/` and the note on M11, and D-8 of `plans/mvp/MVP_PLAN.md` records Q-6 settled first.
- The unanswered question of who removes the moderator role is a hand-off to `plans/account_sessions/`, whose shape is now closed with the rule that removing the role revokes access on the next request, and D-8 checks the current role on every request. It belongs to another initiative and does not block this one.
- There is no cycle among the remaining open questions. Q-10 depends only on D-4 and D-5, both settled, and states that it does not depend on Q-6 (now D-8), Q-7, Q-9 or Q-1 (now D-9). Q-9 depends on Q-10 and D-8. Q-7 depends on D-9 and not on Q-11, so the cut of C-5 holds. Q-11 depends on D-9, D-4 and Q-7. The only edges between open questions are Q-10 -> Q-9 and Q-7 -> Q-11, with no edge back. At the level of execution `SCHEMA_REVISION` and `DEPLOYMENT` wait for Q-11 and the skeleton of D-7, and nothing leads from them back to an open question.

### Verification

- `standard_agentic_workflow.md`: checked automatically; `test_agent_docs_parity.py`, `test_session_context_hook.py` and `test_dangerous_commands_hook.py` passed within `tests/architecture`. Ch. 4.6 and the hand-off to the routing session under ch. 4.7 checked manually.
- `standard_agent_docs.md`: checked automatically; `test_plan_document_contract.py` passed. Checked manually: the initiative has a seed and a review only, as `plans_finished/consistency_check/`, the seed quotes each Polish message verbatim with an English translation, and the review has a state line.
- `standard_review.md`: checked manually; this report follows its order and its states.
- `standard_documentation.md`: checked manually; the artifacts are in English and refer to each other by path and section, no code documentation in scope.
- `standard_formatting.md`: checked automatically; `npx --no-install prettier --check` on the two files of the initiative and the eight files the fixes touched, and on `"**/*.md"` -> `All matched files use Prettier code style!`; `test_prose_style.py` passed; a scan of the two initiative files found no forbidden character and no bold. `ruff format --check .` not run, no Python file in scope.
- `standard_git.md`: checked automatically; `test_conflict_markers.py` passed, the working tree is clean.
- `standard_architecture.md`: not applicable; no code in scope.
- `standard_config.md`: not applicable; no environment entry. Checked manually that no host, address, login or secret appears in the seed or this review.
- `standard_database.md`: not applicable; no code.
- `standard_errors.md`: not applicable; no code.
- `standard_idempotency.md`: not applicable; no code.
- `standard_code_quality.md`: not applicable; no Python code.
- `standard_logging.md`: not applicable; no Python code.
- `standard_naming.md`: not applicable; no Python code.
- `standard_security.md`: not applicable; no code and no new dependency.
- `standard_tests.md`: not applicable to product tests, none exist. `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` on Python 3.13.14 -> `120 passed`; the four failures on the impeccable skill reported in the first pass no longer occur, so no later run contradicts this scope.
- `standard_time.md`: not applicable; no code.
- `standard_worker.md`: not applicable; no periodic task.
- `standard_frontend.md`: not applicable; no frontend code.

### Verdict

Verdict: ready, for the whole initiative `plans/dependency_check/`. R-1, I-1 and I-2 are hand-offs to `plans/api_contract/`, `plans/mvp/` and `plans/fact_schema/`; they change no fix of this initiative and no edge of the dependency order. This final `ready` covers the whole scope, so the initiative qualifies for `plans_finished/` under ch. 4.6, point 1, and nothing in its artifacts contradicts closure.

## Archiving of 2026-10-03

The final ready verdict of the review after fixes covers the whole initiative, so the session that recorded it moved `plans/dependency_check/` to `plans_finished/` the same day under `docs/standards/standard_agentic_workflow.md` ch. 4.6, on the instruction of the user, with the checksums of both files confirmed before and after the move. It rewrote the editable references to it in `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md`, `plans/fact_schema/FACT_SCHEMA_PRD.md`, `FACT_SCHEMA_SHAPE.md`, `FACT_SCHEMA_PLAN.md` and `SCHEMA_REVISION_SHAPE.md`, `plans/api_contract/API_CONTRACT_SHAPE.md` and `API_CONTRACT_PRD.md`, `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, and, only as to location, `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` and `ROUTING_ENGINE_PRD.md`, as the earlier archiving of `plans_finished/consistency_check/` did for that PRD. The anchor of the step of `plans/fact_schema/FACT_SCHEMA_PLAN.md` that edits the item of this review among the Supplementary files of `plans/mvp/MVP_PLAN.md` was rewritten together with that item, so the step still finds it. `plans/fact_schema/SCHEMA_REVISION_SEED.md` and the dated entries of `plans/account_sessions/ACCOUNT_SESSIONS_REVIEW.md`, `plans/fact_schema/FACT_SCHEMA_REVIEW.md` and `plans_finished/routing_engine/ROUTING_ENGINE_REVIEW.md` keep the old path as historical records. The move was made while another session was implementing `plans/fact_schema/FACT_SCHEMA_PLAN.md` on the same tree; the user chose to move and rewrite the references during that work.
