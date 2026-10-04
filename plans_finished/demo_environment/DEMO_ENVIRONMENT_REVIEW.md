# Review: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03, initiative closed: the task `DEMO_ENVIRONMENT` is ready (FR-1 - FR-4), and the task `DEPLOYMENT` was moved to the initiative `plans/deployment/` by a decision of the user

## 2026-10-03 - Implementation run, phase one

The plan came to implementation in the state plan in progress, with the sections Scope of changes, Rollout order and Definition of Done empty and Q-1 open. Before any change the facts were checked against the tree: F-5 pointed at lines of `plans/mvp/MVP_PRD.md` that had moved to 64, 103 and 122, and F-8 still called the routing engine undecided, while `plans/routing_engine/ROUTING_ENGINE_PLAN.md` was closed with D-1 on the same day. Both facts were corrected in the plan. The other facts held.

The user answered three questions in this phase: the permission levels are enforced by the rules only, not by the hook for dangerous commands (D-5); the extension of FR-20 and AC-19 of the MVP PRD is confirmed (D-6); and the rollout is split, FR-2 and FR-4 now and FR-1 and FR-3 after Q-1 (D-7). Q-1 itself stays open: the free memory and disk of the server and whether a domain can point at it are still to come from the db person.

Agent decision at C:40, without asking: the sections Scope of changes, Rollout order and Definition of Done were written by the agent from FR-1 - FR-4 of the PRD and the files named in the section Risks, because each step follows directly from a requirement and its acceptance criterion and has one reasonable form.

Agent decision at C:40, without asking: the new text of the section Target environment keeps, for everything outside the hosted demo environment, the rule in force before the change - no access to any target environment, and challenge submissions done by a human. The PRD sets levels only for the hosted demo environment, and dropping the old sentence would have left the rest undefined.

Agent decision at C:40, without asking: in `docs/standards/decision_registry.md` the item Condition of the entry Target environment for the demo was also changed, not only the item Blocks named in step 4 of the plan, because its clause that the permission levels are filled in together with the choice stopped being true with D-7.

Other sessions worked on the same tree during this phase, and the work was coordinated with them by messages. The session resolving the merge of `dev` holds `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md`, `docs/product/specification.md`, `plans/api_contract/` and `plans/account_sessions/` until it reports done, and step 5 waits for it. The routing engine session edited Q-1 of this plan and `DEPLOYMENT_SHAPE.md` before this run started, has one sentence still to add to the first item of Risks of this plan, and adds its decision to `plans/mvp/MVP_PLAN.md` before step 6 closes Q-7 there with the next free number.

Done: steps 1 - 4 of the plan. `CLAUDE.md` and `AGENTS.md` carry the same new section Target environment, `README.md`, step 2 of section Setup from the template, and the log of `AI_WORKFLOW.md` follow it, and the registry entry names Q-1 as its only blocker.

Architecture tests after steps 1 - 4: `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `5 failed, 109 passed`. The parity test of `CLAUDE.md` and `AGENTS.md` passes. None of the five failures points at a file changed in this run: the parity of the skill `impeccable` and of the four `impeccable-*` agent roles without a Codex pair, and forbidden characters and bold in prose inside `.claude/skills/impeccable/` and `.agents/skills/impeccable/`, all present in `HEAD` since commit `090f5a9`; and conflict markers in `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` and `plans/api_contract/API_CONTRACT_SHAPE.md`, the work in progress of the merge session. Neither is fixed here.

Step 5 followed once the merge session and then the routing engine session released `plans/mvp/MVP_PRD.md`, the file read again right before the edit. FR-20 and AC-19 now require, in the hosted demo, the statement in Polish and English that the demo and all its data are deleted on 4 October 2026, after the results are announced, and a third item "Changed after the gate on 2026-10-03" at the end of the section Domain rules records that the change comes from this initiative and was confirmed by the user (D-6). The routing engine session also added its sentence to the first item of Risks of this plan and settled Q-1 of the MVP plan as D-9 there, so the decision that closes Q-7 in step 6 takes D-10, unless another decision lands first.

During this phase someone staged most of the changed files, those of this run included, while the merge of `dev` was being resolved by hand; this run ran no `git add`. The later edit of `plans/mvp/MVP_PRD.md` is not staged.

Checks after step 5: `npx prettier --check` on the eight files changed in this run -> `All matched files use Prettier code style!`; `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `4 failed, 110 passed`, the four failures being those of `impeccable` named above, and the conflict markers gone with the resolved merge.

## 2026-10-03 - Definition of Done review, phase one

Scope: phase one of the task `DEMO_ENVIRONMENT` - FR-2 and FR-4, steps 1 - 5 of the plan - in `CLAUDE.md`, `AGENTS.md`, `README.md`, `AI_WORKFLOW.md`, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PRD.md`, `DEMO_ENVIRONMENT_PLAN.md` and this file. Changes of the parallel sessions in the same tree are outside it.

### Blockers

None.

### Risks

- R-1. The rules for the agent name the server of D-2 as the target environment while the registry entry stays open and Q-1 may still show that the server does not carry the demo. The user accepted this order in D-7; if Q-1 rules the server out, the section Target environment of `CLAUDE.md` and `AGENTS.md` changes together with the new choice.
- R-2. The deadline of 22:00 on 3 October 2026 for the choice of the hosting now hangs on Q-1 alone, not on the routing engine as the first item of Risks of the plan still reads.
- R-3. The repository-wide gates are red outside this scope: the parity of the skill `impeccable` and of four `impeccable-*` agent roles without a Codex pair, and forbidden characters and bold in prose in `.claude/skills/impeccable/` and `.agents/skills/impeccable/`, present in `HEAD` since commit `090f5a9`. The tests that cover this change pass, but a full green run is impossible until that is fixed elsewhere.

### Improvements

None.

### Verification

- `standard_agentic_workflow.md`: checked automatically; `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> `2 failed, 61 passed`, the two failures those of R-3; `test_agents_and_claude_core_files_are_at_parity` passes. The rules of ch. 4.7 on parallel work were followed: shared files read again before each edit, other sessions' edits kept, no `git add`.
- `standard_agent_docs.md`: checked automatically; `pytest tests/architecture/test_plan_document_contract.py` passes. Checked manually: the plan keeps the marker plan in progress, gaps filled without asking carry the phrase of the agent decision, and this file has no bold in prose.
- `standard_review.md`: checked manually; the report follows the order and names its scope.
- `standard_documentation.md`: checked manually; no code unit changed, and the entry of `AI_WORKFLOW.md` follows the shape of the earlier entries.
- `standard_formatting.md`: checked automatically; `ruff format --check .` -> `13 files already formatted`, `npx --no-install prettier --check "**/*.md"` -> `All matched files use Prettier code style!`, `pytest tests/architecture/test_prose_style.py` -> `2 failed, 16 passed`, every violation inside `impeccable` (R-3), none in a file of this scope.
- `standard_git.md`: checked automatically; `pytest tests/architecture/test_conflict_markers.py` passes. No history or index operation was run by this task.
- `standard_architecture.md`: not applicable; no service code.
- `standard_config.md`: checked manually; the changed files name no address, host, login or secret of the hosting, confirmed by a search of the added lines for addresses, links and logins.
- `standard_database.md`: not applicable; no schema or query.
- `standard_errors.md`: not applicable; no code.
- `standard_idempotency.md`: not applicable; no code.
- `standard_code_quality.md`: not applicable; no Python code changed.
- `standard_logging.md`: not applicable; no code.
- `standard_naming.md`: not applicable; no code.
- `standard_security.md`: not applicable; no code or dependency. The permission levels themselves are the rules of the user (D-5).
- `standard_tests.md`: not applicable; no product code to test, the architecture tests are reported above.
- `standard_time.md`: not applicable; no time values in code.
- `standard_worker.md`: not applicable; no periodic task.
- `standard_frontend.md`: not applicable; no frontend code.

### Verdict

Ready, for phase one of the task `DEMO_ENVIRONMENT` only (FR-2 and FR-4). FR-1 and FR-3 wait for Q-1 (D-7), the task `DEPLOYMENT` has its interview in progress, so the initiative is not finished and stays in `plans/`.

## 2026-10-03 - After the review

Two changes of other sessions landed after the review. The routing engine session archived its initiative and replaced the path `plans/routing_engine` with `plans_finished/routing_engine` in the plan, the PRD and both shapes of this initiative and in `plans/mvp/`; the edits of this run in those files are intact. Another session excluded the third-party skill `impeccable` from the gates by name (`AI_WORKFLOW.md`, entry "Third-party skill outside the repository gates"), so R-3 no longer holds: `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `120 passed`.

## 2026-10-03 - Implementation run, phase two

The user asked to finish the initiative. The review above leaves it in `plans/` for two reasons, Q-1 and the task `DEPLOYMENT`, so the user was asked about both before any change. Q-1 was answered for the db person: after the other services of its owner the server has 4 GB of free memory, 64 GB of free disk and 4 cores, and no domain points at it; the demo runs at the IP address of the server, and a domain may be bought later. The user confirmed that the 4 GB and 64 GB are free, not the size of the whole server, and does not know whether ports 80 and 443 are free, so the choice between them and a proxy of the owner goes to the task `DEPLOYMENT`. The task `DEPLOYMENT` stays in this initiative by a decision of the user, so the initiative stays in `plans/`.

Before step 6 the facts were checked against the tree. F-4 named Q-1 of the MVP plan, settled as D-9 there, and F-5 pointed at lines that had moved to 67, 107 and 129, so both were corrected; F-3 and F-8 held. F-12 - F-14 were added for the certificate for an IP address, the ports of its validation and the measurements of the import, Q-1 was settled as D-8, and the plan was closed.

Agent decision at C:40, without asking: in `DEPLOYMENT_SHAPE.md`, section Current state, the item saying that the hosting is not chosen was replaced with one pointing to D-8 and giving what the task `DEPLOYMENT` needs from it, because D-8 made it untrue and the interview of that task would start from a wrong state.

Agent decision at C:40, without asking: in `plans/mvp/MVP_PLAN.md` the sentence "The critical paths are Q-10 -> Q-6 -> Q-9 and Q-7 -> Q-11, and" of the item of Risks and the list of Supplementary files were left unchanged, so the sentence still names the settled Q-7 and no supplementary item points to D-10 yet. `plans/fact_schema/FACT_SCHEMA_PLAN.md`, implemented in parallel, quotes that sentence in step 3.2 and anchors step 3.7 on the last supplementary item, and stops on a passage that no longer matches. The session of `plans/fact_schema/` was told by message what was changed in the MVP plan and that the next free decision there is D-11.

Other sessions worked on the same tree during this run. At 21:28 one of them archived `plans/dependency_check/` and changed its reference in `plans/mvp/MVP_PLAN.md`, so the file was read again before the edit; the session of `plans/fact_schema/` changed `docs/product/specification.md`, `plans/mvp/MVP_PRD.md` and its own files. Their changes were kept, and this run touched none of them.

Done: step 6 of the plan. D-8 records the choice, the registry entry Target environment for the demo is in the resolved section, Q-7 of `plans/mvp/MVP_PLAN.md` is closed as D-10, with Q-10, Q-11 and the clause on Q-7 in Risks adapted, and the item of `plans/mvp/MVP_PRD.md` on the target environment says it is decided. A memory entry was appended to `agent_docs/memory/_cross_cutting.md`.

Checks after step 6: `npx --no-install prettier --check` on the six files changed in this run -> `All matched files use Prettier code style!`; `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `120 passed`.

## 2026-10-03 - Definition of Done review, phase two

Scope: phase two of the task `DEMO_ENVIRONMENT` - FR-1 and FR-3, step 6 of the plan - in `DEMO_ENVIRONMENT_PLAN.md`, `DEPLOYMENT_SHAPE.md`, this file, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PLAN.md`, the item on the target environment of `plans/mvp/MVP_PRD.md` and `agent_docs/memory/_cross_cutting.md`, together with a check that AC-2 and AC-4 of phase one still hold. Changes of the parallel sessions in the same tree are outside it.

### Blockers

None.

### Risks

- R-4. In `plans/mvp/MVP_PLAN.md` the sentence "The critical paths are Q-10 -> Q-6 -> Q-9 and Q-7 -> Q-11" still names the settled Q-7, and no supplementary item points to D-10, both left so as not to break the quotes of `plans/fact_schema/FACT_SCHEMA_PLAN.md` steps 3.2 and 3.7. Whoever edits that plan after those steps adapts them.
- R-5. Whether ports 80 and 443 of the server are free is not known. If neither they nor a proxy of the owner can answer the validation of F-13, the public link has no secure connection, and the current location of FR-2 of `plans/mvp/MVP_PRD.md` does not work in the browser. The task `DEPLOYMENT` decides it, and it waits for Q-11 and the backend skeleton before 11:00 on 4 October 2026.
- R-6. The free memory and disk of D-8 are a statement of the user for the db person; the agent cannot check them, because the server outside the hosted demo environment is forbidden to it. The memory of PostgreSQL with PostGIS was not measured, and the peaks of the backend and the import come from the Windows machine of the agent's session.
- R-7. The repository-wide `npx --no-install prettier --check "**/*.md"` is red on `docs/product/schema.md`, `docs/standards/README.md` and `plans/fact_schema/FACT_SCHEMA_PLAN.md`, the work in progress of the session of `plans/fact_schema/`, whose rollout formats them at its end. No file of this scope is among them.

### Improvements

- I-1. F-1, F-6 and F-7 of the closed plan describe the tree before steps 1 - 3: both rule files and `README.md` no longer say what F-1 and F-6 quote, and the passages F-7 cites now stand in `CLAUDE.md` section Task cycle and the agentic system and `AI_WORKFLOW.md` section Log. Rewording them as the state before the step that changed them, as F-5 already is, keeps the closed plan true.

### Verification

- `standard_agentic_workflow.md`: checked automatically; `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> `63 passed`. The rules of ch. 4.7 were followed: shared files read again right before each edit, the change of `plans/mvp/MVP_PLAN.md` by another session at 21:28 kept, the session of `plans/fact_schema/` told by message, no `git add`. The initiative was checked against ch. 4.6 below.
- `standard_agent_docs.md`: checked automatically; `pytest tests/architecture/test_plan_document_contract.py` -> `25 passed`, with the plan closed and its Open questions opening with "None". Checked manually: gaps filled without asking carry the phrase of the agent decision, the memory entry has the four fields and the title of the template, and none of the changed files has bold in prose.
- `standard_review.md`: checked manually; this report follows the order and names its scope.
- `standard_documentation.md`: checked manually; no code unit changed, and the memory entry is appended to `_cross_cutting.md`, because the decision cuts across the backend, the database and the frontend.
- `standard_formatting.md`: checked automatically; `ruff format --check .` -> `15 files already formatted`; `npx --no-install prettier --check "**/*.md"` -> three files of R-7, none of this scope, and the seven files of this scope pass on their own; `pytest tests/architecture/test_prose_style.py` -> `19 passed`.
- `standard_git.md`: checked automatically; `pytest tests/architecture/test_conflict_markers.py` -> `8 passed`. No history or index operation was run.
- `standard_architecture.md`: not applicable; no service code.
- `standard_config.md`: checked manually; a search of the added lines finds no IPv4 address, no login and no secret, and the only hosts named are `letsencrypt.org` as the source of F-12 and `download.geofabrik.de`, both outside the hosting.
- `standard_database.md`: not applicable; no schema or query.
- `standard_errors.md`: not applicable; no code.
- `standard_idempotency.md`: not applicable; no code.
- `standard_code_quality.md`: not applicable; no Python code changed.
- `standard_logging.md`: not applicable; no code.
- `standard_naming.md`: not applicable; no code.
- `standard_security.md`: not applicable; no code or dependency. The secure connection is a requirement of the task `DEPLOYMENT` (R-5).
- `standard_tests.md`: not applicable; no product code to test, the architecture tests pass, `120 passed` after step 6.
- `standard_time.md`: not applicable; no time values in code.
- `standard_worker.md`: not applicable; no periodic task.
- `standard_frontend.md`: not applicable; no frontend code.

Acceptance criteria: AC-1 - D-8 names the hosting, its reason, its cost, how it carries the routing engine and the frontend, and how it allows a secure connection and an unreachable routing, with no address, host or login; AC-2 - neither rule file contains "defined together with the target environment", and the parity test passes; AC-3 - the registry entry stands only in the resolved section, and D-10 of the MVP plan points to this initiative; AC-4 - FR-20 and AC-19 of `plans/mvp/MVP_PRD.md` still carry the deletion of the demo.

### Verdict

Ready, for the whole task `DEMO_ENVIRONMENT` (FR-1 - FR-4). It does not cover the initiative: the task `DEPLOYMENT` has its interview in progress and stays in this initiative by a decision of the user on 2026-10-03, so `plans/demo_environment/` does not qualify for `plans_finished/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6) and stays in `plans/`.

## 2026-10-03 - After the review, phase two

I-1 was applied: F-1 and F-6 now say what both rule files and `README.md` said until steps 1 and 2 of the plan, and F-7 points at `CLAUDE.md` section Task cycle and the agentic system and `AI_WORKFLOW.md` section Log; no other content of the plan changed. R-4 - R-7 stay open for their owners: R-4 for whoever edits `plans/mvp/MVP_PLAN.md` after steps 3.2 and 3.7 of `plans/fact_schema/FACT_SCHEMA_PLAN.md`, R-5 for the task `DEPLOYMENT`, R-6 for the first deployment, and R-7 for the session of `plans/fact_schema/`.

R-4 was settled later on 2026-10-03. The session of `plans/fact_schema/` finished its edits of `plans/mvp/MVP_PLAN.md`: the sentence of the item of Risks now reads "The critical path is Q-11", and its D-11 follows D-10. The item "- `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, the decision behind D-10." was then inserted in the Supplementary files of that plan, between the items of D-9 and D-11.

## 2026-10-03 - Initiative closed

The user asked to move the task `DEPLOYMENT` into an initiative of its own and to archive this one, changing the decision recorded in the implementation run, phase two, that the task stays here. `DEPLOYMENT_SEED.md` and `DEPLOYMENT_SHAPE.md` moved to `plans/deployment/`, with the same names and checksums confirmed after the move. The seed is unchanged; the shape got only the new locations of its references and one sentence on the move at the end of its section Problem, and its interview stays in progress there.

Without the task `DEPLOYMENT` the verdict of the Definition of Done review, phase two - ready for the whole task `DEMO_ENVIRONMENT` (FR-1 - FR-4) - covers the whole initiative, so the directory moves to `plans_finished/demo_environment/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6). R-5 goes with the task `DEPLOYMENT`, and R-6 stays for the first deployment; neither blocks the closure, and the archive confirms neither.

References. In the plan, the shape and the PRD of this initiative only the location of references changed: `DEPLOYMENT_SEED.md` and `DEPLOYMENT_SHAPE.md` point to `plans/deployment/`, `plans/demo_environment/` to `plans_finished/demo_environment/`. The same two rules apply to `CLAUDE.md`, `AGENTS.md`, `README.md`, `PRODUCT.md`, `docs/standards/decision_registry.md`, `plans/mvp/`, the shapes of `plans/account_sessions/` and `plans/api_contract/`, and the shapes, PRDs and plans of `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/geocoding/`, `plans_finished/frontend_stack/`, `plans_finished/local_database/` and `plans_finished/osm_barrier_mapping/`, with the task `DEPLOYMENT` named by `plans/deployment/` wherever it was named by this directory. The sentences that say this initiative still holds the task `DEPLOYMENT` - D-1 of the plan, the shape and the PRD of this initiative - stay as the record of their day. Seeds, review entries, memory entries and the log of `AI_WORKFLOW.md` keep the old path as a historical record.

Agent decision at C:40, without asking: in `docs/standards/decision_registry.md` the state sentence of the entry that lists the initiatives of the MVP plan, "`plans/demo_environment/` has a plan in progress and its task `DEPLOYMENT` an interview in progress", was rewritten to the state after the move, not only relocated, because a registry has to state the current state, and `plans/deployment/` (db) was added to its list of initiatives and owners.
