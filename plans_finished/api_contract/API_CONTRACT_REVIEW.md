# Review: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03, implementation of the whole plan carried out, review ready for the whole initiative, archived in `plans_finished/api_contract/`

## Implementation run of 2026-10-03

### Check before implementation

- `API_CONTRACT_SHAPE.md` has a closed interview, regulator C:40, and no `Block: yes`; the plan is closed, has no open question and no TODO.
- The tree at `032373e` on the branch `rm/requirements-preparation` carries uncommitted changes of other sessions, as F-24 foresaw. The files of the session that closed the demo environment were written up to a minute before this run started, so the rules of `docs/standards/standard_agentic_workflow.md` ch. 4.7 apply: every file is read again right before its step.
- Facts: F-1 - F-25 still hold. The lines they cite carry the cited content; no tracked file lies under a directory of a code layer or of the frontend (F-2); D-12 is still free in `plans/mvp/MVP_PLAN.md`; the tools of F-25 answer with the same versions.
- Quoted passages: every passage quoted by steps 2 - 9 was found verbatim in its file. The registry entry of step 7 gained `plans/deployment/` and `plans_finished/demo_environment/` from another session, outside the passage step 7.1 replaces.

### Parallel work during the run

- At 21:46 the session that closed the demo environment reported that it moved `plans/demo_environment/` to `plans_finished/demo_environment/`, moved its task `DEPLOYMENT` to `plans/deployment/`, and changed one path in the list of sibling initiatives of `API_CONTRACT_SHAPE.md`. No step of this plan quotes that path.
- At 21:49 the session of `plans/fact_schema/` reported that, at the user's request, it moves the task `SCHEMA_REVISION` to the new initiative `plans/schema_revision/`, archives the rest as `plans_finished/fact_schema/`, and updates the paths in `docs/product/specification.md`, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md` and the plan, PRD and shape of this initiative, the anchors and texts of steps 3.x and 9.1 included, without changing their content. This run agreed with that session to hold its edits of those files until it was done; the steps on other files went on in the meantime.
- At about 21:53 that session reported it was done. Every held file was read again: the anchors of steps 3.1 - 3.5, 7.1, 7.2, 9.1 and 9.2 were still found verbatim, the anchor of step 3.5 and the texts of steps 3.1 and 9.1 now with the paths `plans_finished/fact_schema/` and `plans/schema_revision/`, and the heading of step 9 names `plans/schema_revision/SCHEMA_REVISION_SHAPE.md`. Steps 2.10, 3, 7 and 9 were carried out on that state.
- After the relocation the evidence of F-24, the state line of `plans_finished/fact_schema/FACT_SCHEMA_REVIEW.md`, reads that the initiative is closed with the task `FACT_SCHEMA` ready and the task `SCHEMA_REVISION` moved to `plans/schema_revision/`. The claim of F-24 - another session implemented `FACT_SCHEMA` on the same tree while this plan was written - still holds, so the fact was left as it is; the plan does not grow during the run.
- The `git status` of `plans_finished/` lists changes of the other sessions, the path updates of their archiving; this run changed nothing under `plans_finished/`.

### Deviations from the plan

None in content. Prettier changed only the padding of the tables of `docs/product/api_contract.md` and of the table of `docs/standards/README.md`, as Rollout order step 5 and step 6.2 ask; a comparison that ignores the padding found the contract identical to the block of step 1.

### What was done

- Step 1: `docs/product/api_contract.md` exists with the content of step 1 and the state line dated 2026-10-03.
- Step 3 of Rollout order: the user saw the contract and the changes of the specification and approved both on 2026-10-03, the contract in place of the frontend person (D-10) and version 7 (D-3). The date went into the state line of the contract and into steps 2.1 and 2.9.
- Steps 2.1 - 2.9: `docs/product/specification.md` is version 7 with the six additions of M2, M4 and M9, the paragraph on version 7, "None at version 7." and the item Version 7 of Decision provenance.
- Step 2.10: `PRODUCT.md` names version 7 in both places, the Goal of `plans/mvp/MVP_PLAN.md` names version 7, and `plans/mvp/MVP_PRD.md` names version 7 in Scope and Domain rules, with the sentence of step 2.10 appended to its item on version 4.
- Step 3: `plans/mvp/MVP_PLAN.md` has D-12 after D-11, the replaced clause of the Risks item, no item that begins with Q-9, the item Q-11 of step 3.4 and the plan of this initiative as the last item of Supplementary files.
- Steps 4 and 5: `docs/standards/standard_errors.md` and `docs/standards/standard_naming.md` send the response codes, bodies and paths to the contract.
- Step 6: `docs/standards/README.md` names the contract in Project documents and has the new row in What to open before a task.
- Step 7: the registry entry Technical directions of the MVP plan says that `plans/account_sessions/` and `plans/api_contract/` are decided and that Q-11 moved to a separate initiative, and its Condition ends with that initiative.
- Step 8: `PRODUCT.md` has the replaced item under Undecided and the new item of Evidence on Hand.
- Step 9: `plans/schema_revision/SCHEMA_REVISION_SHAPE.md` has the item on the idempotency key in Current state and the blocking question 2.
- Checks: `npx --no-install prettier --check` passes on every changed or created markdown file and on the files of `plans/api_contract/`; none of the changed or created files carries a character forbidden by `docs/standards/standard_formatting.md`, bold or a CRLF line ending; `venv/Scripts/python.exe -m pytest tests/architecture -o addopts=-ra -q` reports `120 passed`.
- Memory: an entry on the contract was appended to `agent_docs/memory/_cross_cutting.md`, because it is an architectural decision that the implementation of the operations, the frontend and a possible HarmonyOS client build on.

### Observations for the user

- After step 3.4 the rest of the item Q-11 of `plans/mvp/MVP_PLAN.md` still says that the task `SCHEMA_REVISION` waits for the backend skeleton "decided here", while the same item now says that Q-11 is decided in a separate initiative. The plan replaces only the first sentence of that item, so the rest was left as it is.
- Two cells of the error tables of the contract, `invalid_search_text` of `search_address` and `vote_too_soon` of `cast_vote`, hold a full sentence, while the section Table width in documentation of `docs/standards/standard_formatting.md` asks for a short phrase. They are kept as step 1 gives them, because the contract is the approved text.

### Review

The review of `implementation-dod-review` found no blocker. The commands of the map of `docs/standards/standard_review.md` that apply ran green on the tree after step 9: the parity, session context, dangerous commands, plan document contract, prose style and conflict marker tests (`115 passed`), `ruff format --check .` (`15 files already formatted`), `npx --no-install prettier --check "**/*.md"` and the whole of `tests/architecture` (`120 passed`).

Verification against the map:

- `standard_agentic_workflow.md`: checked automatically, the parity, session context and dangerous commands tests passed; the parallel work on the tree followed ch. 4.7, recorded above.
- `standard_agent_docs.md`: checked automatically, `test_plan_document_contract.py` passed; this review and the memory entry follow the formats of the REVIEW and memory sections by manual reading.
- `standard_review.md`: checked manually, the Definition of Done of the plan holds item by item.
- `standard_documentation.md`: checked manually, the contract and the changed passages are in the dry declarative tone of Prose tone; the rest of the standard covers module documents, which the change does not hold.
- `standard_formatting.md`: checked automatically, prettier, ruff format and the prose style test passed, and a scan of the changed files found no forbidden character, no bold and no CRLF line ending.
- `standard_git.md`: checked automatically, the conflict marker test passed; nothing was committed or staged.
- `standard_architecture.md`, `standard_config.md`, `standard_database.md`, `standard_code_quality.md`, `standard_security.md`, `standard_tests.md`, `standard_worker.md`: not applicable as commands, because the change holds no Python code; manually, the contract carries no address, host, login or secret of an environment, and the risk of a token in the storage of the browser stands in the Risks of the plan.
- `standard_errors.md`, `standard_idempotency.md`, `standard_logging.md`, `standard_naming.md`, `standard_time.md`: checked manually against the contract, which they now point at: one error body with a code and nothing of an exception or the infrastructure, an idempotency key for `create_fact` and repeated flags, hides and restores answering the same way, `X-Request-Id` under the rule of the logging standard and a request log of four fields, snake case names, instants with milliseconds and the offset of Europe/Warsaw and days computed by the service.
- `standard_frontend.md`: not applicable as commands, because no frontend code exists; manually, the contract gives the frontend every closed list as a code and every day as computed by the service, so it applies no product rule.

Risks recorded for the user:

- R-1. The frontend person has not confirmed the contract yet; the user approved it in that person's place (D-10), and a later change changes whatever is built on it.
- R-2. The repetition of `create_fact` cannot be implemented until question 2 of `plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, `Block: yes`, is answered.
- R-3. No initiative of Q-11 exists yet, so nobody is scheduled to implement the operations before the Kraków deadline at 11:00 on 4 October 2026.
- R-4. The files of this change also carry uncommitted changes of other sessions, `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md` and `docs/product/specification.md` among them, so a commit of this change alone has to pick its hunks.

Improvements: the two observations above, the rest of the item Q-11 and the two long table cells of the contract.

Verdict: ready, for the whole initiative `plans/api_contract/`, whose one task is this plan. The steps left to a human - the confirmation of the frontend person, the initiative of Q-11, question 2 of the shape of `SCHEMA_REVISION` and the commit - are post-closure steps, so the initiative qualifies for `plans_finished/` under `docs/standards/standard_agentic_workflow.md` ch. 4.6.

### Archiving

- After the verdict a human committed the tree as `54dd6f6`, with every file of this run in it, so the evidence of the review was compared again: the files of the initiative and of the change equal `HEAD`, and `tests/architecture` reports `120 passed` on it.
- Moved on 2026-10-03 from `plans/api_contract/` to `plans_finished/api_contract/` with a native move, under `docs/standards/standard_agentic_workflow.md` ch. 4.6: the target did not exist, the directory had no change after the verdict, it holds no link, and the SHA-256 sums of its five files are the same before and after the move. The session closing `plans/account_sessions/` held its edits of the shared files while the references were updated.
- The editable references - `docs/product/api_contract.md`, `docs/product/specification.md`, `docs/standards/README.md`, `docs/standards/decision_registry.md`, `docs/standards/standard_frontend.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md`, `plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, the shape, PRD and plan of `plans/account_sessions/`, the plan of this initiative and the shapes, PRDs and plans of the archived initiatives - name `plans_finished/api_contract/`. The seed, every review entry, this file included, and `agent_docs/memory/` keep `plans/api_contract/` as historical records. No code or tool reads the files of this initiative.
