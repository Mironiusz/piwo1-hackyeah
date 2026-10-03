# Review: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03, implementation in progress - FR-2 and FR-4 done, FR-1 and FR-3 wait for Q-1

## 2026-10-03 - Implementation run, phase one

The plan came to implementation in the state plan in progress, with the sections Scope of changes, Rollout order and Definition of Done empty and Q-1 open. Before any change the facts were checked against the tree: F-5 pointed at lines of `plans/mvp/MVP_PRD.md` that had moved to 64, 103 and 122, and F-8 still called the routing engine undecided, while `plans/routing_engine/ROUTING_ENGINE_PLAN.md` was closed with D-1 on the same day. Both facts were corrected in the plan. The other facts held.

The user answered three questions in this phase: the permission levels are enforced by the rules only, not by the hook for dangerous commands (D-5); the extension of FR-20 and AC-19 of the MVP PRD is confirmed (D-6); and the rollout is split, FR-2 and FR-4 now and FR-1 and FR-3 after Q-1 (D-7). Q-1 itself stays open: the free memory and disk of the server and whether a domain can point at it are still to come from the db person.

Agent decision at C:40, without asking: the sections Scope of changes, Rollout order and Definition of Done were written by the agent from FR-1 - FR-4 of the PRD and the files named in the section Risks, because each step follows directly from a requirement and its acceptance criterion and has one reasonable form.

Agent decision at C:40, without asking: the new text of the section Target environment keeps, for everything outside the hosted demo environment, the rule in force before the change - no access to any target environment, and challenge submissions done by a human. The PRD sets levels only for the hosted demo environment, and dropping the old sentence would have left the rest undefined.

Agent decision at C:40, without asking: in `docs/standards/decision_registry.md` the item Condition of the entry Target environment for the demo was also changed, not only the item Blocks named in step 4 of the plan, because its clause that the permission levels are filled in together with the choice stopped being true with D-7.

Other sessions worked on the same tree during this phase, and the work was coordinated with them by messages. The session resolving the merge of `dev` holds `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md`, `docs/product/specification.md`, `plans/api_contract/` and `plans/account_sessions/` until it reports done, and step 5 waits for it. The routing engine session edited Q-1 of this plan and `DEPLOYMENT_SHAPE.md` before this run started, has one sentence still to add to the first item of Risks of this plan, and adds its decision to `plans/mvp/MVP_PLAN.md` before step 6 closes Q-7 there with the next free number.

Done: steps 1 - 4 of the plan. `CLAUDE.md` and `AGENTS.md` carry the same new section Target environment, `README.md` line 41 and the log of `AI_WORKFLOW.md` follow it, and the registry entry names Q-1 as its only blocker.

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
