# Review: Domain model and database schema of facts and votes for the MVP

Document state: 2026-10-03, initiative closed: the task `FACT_SCHEMA` is ready, and the task `SCHEMA_REVISION` was moved to the initiative `plans/schema_revision/` by a decision of the user

## Implementation run of 2026-10-03

### Check before implementation

- The tree was clean at `032373e` on the branch `rm/requirements-preparation`, and `b5f03be` and `fff8e88` are its ancestors, so step 1 of Rollout order passed (D-20). `FACT_SCHEMA_SHAPE.md` has a closed interview, regulator C:40, and no `Block: yes`; the plan has no open question and no TODO.
- The task `SCHEMA_REVISION` has its interview in progress and waits for the backend skeleton, which does not exist (F-2), so this run settles only the task `FACT_SCHEMA`, and the initiative stays in `plans/`.
- Facts: `git diff --stat b5f03be HEAD` lists 53 changed files, among them every target of steps 2 - 6. F-21, F-22, F-24 and F-25 no longer held and were rewritten with a new check date; F-28 - F-30 were added. F-1 - F-20, F-23, F-26 and F-27 kept their claims: the ones read from `fff8e88` describe that commit, and the lines of F-26 and F-27 still carry the cited content.
- Quoted passages: steps 2.1 - 2.5, 3.3 - 3.6, 5 and 6.1 and 6.3 found their anchors verbatim. Step 3.1 named D-8, which the account sessions hold, step 3.2 quoted a Risks item that `plans/dependency_check/` and the account sessions had rewritten, step 4 quoted the registry clause without its words on `SCHEMA_REVISION`, and steps 3.1, 3.5 and 4 still named the second task `FACT_SCHEMA_REVISION`.

### Deviations from the plan

O-1. The plan was corrected before any step was carried out, in the paragraph after its Goal, F-21, F-22, F-24, F-25, F-28 - F-30, D-1, D-11, D-14, D-22, the new D-23, the Scope of changes, Rollout order, Definition of Done, Risks and Supplementary files: the decision number is D-N, the next free one read right before step 3.1, because D-8 and D-9 of the MVP plan are taken; the second task is `SCHEMA_REVISION` in every step; steps 3.2 and 4 quote the passages as they stand at `032373e`; steps 3.8 and 3.9 and the new parts of steps 3.6 and 3.7 replace the "Q-10" that D-4, D-9, the last item of Open questions and two Supplementary files of the MVP plan still name, which the Definition of Done of this plan asks and D-22 announced for D-9 without a step; the text of step 6.3 no longer says that the rules of question 4 of `plans/account_sessions/` and the format of the hash are left to that initiative, because the rules stand in M9 and that initiative closed without choosing the format (F-28). Agent decision at C:40, without asking.

O-2. Step 6.2 is dropped: it inserted findings into `plans_finished/routing_engine/ROUTING_ENGINE_SHAPE.md`, the shape of an archived initiative, which the archive keeps unchanged apart from the location of references (F-30), while the Definition of Done of this plan keeps `plans_finished/` unchanged and D-6 already gives the routing engine the ordered nodes it asked for (D-22). Agent decision at C:40, without asking.

O-3. D-1 and the PRD, Scope, say that the seed of phase B, `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, was removed from the tree, while it never was (F-29). The user decided on 2026-10-03 to remove it now, as the new step 7, against keeping it and correcting D-1 and the PRD. The PRD stays unchanged, because after the removal it is true.

### Parallel work during the run

- While steps 1 and 2 were written, other sessions on the same tree moved `plans/dependency_check/` to `plans_finished/dependency_check/` and changed the references to it, in this plan, its PRD and both shapes included, and the session "Demo environment setup" appended D-10 to `plans/mvp/MVP_PLAN.md` for the former Q-7, rewrote Q-11 and one clause of the Risks item, and reported it with a message. The edits of this run survived, every file was read again right before its step, and only the passages the steps quote were edited, as `docs/standards/standard_agentic_workflow.md` ch. 4.7 asks.

O-4. D-N of the Scope of changes is D-11: D-10 arrived from the demo environment before step 3.1, so D-11 was the next free number when step 3.1 was carried out, and the plan, which reads the number right before that step, needed no change (D-22).

O-5. In step 3.2 "The critical paths are Q-10 -> Q-6 -> Q-9 and Q-7 -> Q-11, and" became "The critical path is Q-11, and" instead of "The critical path is Q-7 -> Q-11, and", because D-10 settled Q-7 after the plan was corrected and the same item now says that Q-11 depends on D-9, D-4 and D-10, all settled. The session of the demo environment left the sentence for this run so as not to break the quoted passage. Agent decision at C:40, without asking. The text of step 3.2 in the plan stays as it was corrected before implementation, because the plan does not grow during the run.

O-6. Prettier realigned the table of the section Rights of the service account in `docs/product/schema.md`, so the file differs from the block of step 1 in the padding of that table only, as Rollout order step 5 asks. Step 3.2 of the plan was rewritten from a bulleted list into one paragraph with the same replacements before the check, because prettier read the steps after the list as part of it.

### What was done

- Step 1: `docs/product/schema.md` exists with the content of step 1, dated 2026-10-03.
- Step 2: `docs/product/specification.md` is version 6 with the changes of steps 2.1 - 2.4, approved by the user on 2026-10-03 after seeing `docs/product/schema.md` and the diff of the specification; `PRODUCT.md`, `plans/mvp/MVP_PLAN.md` Goal and `plans/mvp/MVP_PRD.md` Scope and Domain rules name version 6, and the item of `MVP_PRD.md` on version 4 got the sentence of step 2.5.
- Step 3: `plans/mvp/MVP_PLAN.md` has D-11 after D-10, no item that begins with Q-10, the replacements of steps 3.2, 3.3, 3.5 - 3.9 with the deviation O-5, and the plan of this initiative as the last item of Supplementary files. The only remaining mentions of Q-10 read "the former Q-10".
- Step 4: the registry entry Technical directions of the MVP plan says that `plans/fact_schema/` decided the model and the target schema (D-11 there) and that its task `SCHEMA_REVISION` builds the first revision.
- Step 5: `docs/standards/README.md` names `docs/product/schema.md` in Project documents and in the row on tables, with the table realigned by prettier.
- Step 6: `plans/api_contract/API_CONTRACT_SHAPE.md` and `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` carry the items of steps 6.1 and 6.3; step 6.2 is dropped (O-2).
- Step 7: `plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`, unchanged since `657d8da`, is removed with a native removal, and Supplementary files of the plan point to that commit.
- Checks: `npx --no-install prettier --check` passes on every changed or created markdown file and on `plans/fact_schema/`; none of the changed or created files carries a character forbidden by `docs/standards/standard_formatting.md` or bold; `venv/Scripts/python.exe -m pytest tests/architecture -o addopts=-ra -q` reports `120 passed`.
- Not run: nothing of the DDL, which needs PostgreSQL 18 with PostGIS and runs in the task `SCHEMA_REVISION` (plan, Risks).
- Memory: an entry on the target schema was appended to `agent_docs/memory/_cross_cutting.md`, because it is an architectural decision that every later revision, the import and the backend build on.

### Review

The review of `implementation-dod-review` found no blocker. The commands of the map of `docs/standards/standard_review.md` that apply ran green: the parity, session context, dangerous commands, plan document contract, prose style and conflict marker tests (`115 passed`), `ruff format --check .`, `npx --no-install prettier --check "**/*.md"` and the whole of `tests/architecture` (`120 passed`); the standards of the Python and frontend profiles do not apply, because the change holds no code.

Risks recorded for the user:

- R-1. `plans/api_contract/API_CONTRACT_PLAN.md` still waits for "Q-10" of the MVP plan in F-2, D-3, its steps 2 and 3 and its blocking Q-5, while that decision is now D-11 there; its owner can answer Q-5 now. This plan hands its result to that initiative only through its shape (D-19).
- R-2. The DDL of `docs/product/schema.md` has not run in this task; the task `SCHEMA_REVISION` runs it first.
- R-3. With step 6.2 dropped (O-2), the archived shape of the routing engine carries no item on the stored copy; D-6 of this plan, `docs/product/schema.md` and the memory entry of the routing engine name `osm_way_node`.

Improvements: the item of step 6.3 cites D-11 of this plan, while D-11 of the MVP plan is a different decision; `SCHEMA_REVISION_SHAPE.md` still says its rules are those of version 4 of the specification, which versions 5 and 6 do not change.

Verdict: ready, for the task `FACT_SCHEMA` only, one of the two tasks of this initiative. The task `SCHEMA_REVISION` has its interview in progress and waits for the backend skeleton, so the initiative is not finished under `docs/standards/standard_agentic_workflow.md` ch. 4.6 and its directory stays in `plans/`.

## Initiative closed on 2026-10-03

The user asked to move the task `SCHEMA_REVISION` into an initiative of its own and to archive this one, changing the decision recorded in `FACT_SCHEMA_PLAN.md` D-1 that both tasks stay in this initiative. `SCHEMA_REVISION_SEED.md` and `SCHEMA_REVISION_SHAPE.md` moved to `plans/schema_revision/`, with the same names and checksums confirmed after the move. The seed is unchanged; the shape got only the new locations of its references and one sentence on the move at the end of its section Problem, and its interview stays in progress there.

Without the task `SCHEMA_REVISION` the verdict of the review above - ready for the task `FACT_SCHEMA` - covers the whole initiative, so the directory moves to `plans_finished/fact_schema/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6). R-2 goes with the task `SCHEMA_REVISION`, and R-1 and R-3 stay with their owners; none of them blocks the closure, and the archive confirms none of them.

References. In the plan, the shape and the PRD of this initiative only the location of references changed: `SCHEMA_REVISION_SEED.md` and `SCHEMA_REVISION_SHAPE.md` point to `plans/schema_revision/`, and `plans/fact_schema/` to `plans_finished/fact_schema/`. The same two rules apply to `docs/product/specification.md`, `docs/standards/decision_registry.md`, `plans/mvp/`, the plans, PRDs and shapes of `plans/account_sessions/` and `plans/api_contract/`, and the plans, PRDs and shapes of `plans_finished/local_database/` and `plans_finished/routing_engine/`, with the task `SCHEMA_REVISION` and the first schema revision named by `plans/schema_revision/` wherever they were named by this directory. Kept as a historical record: the paths inside commands bound to a commit or to the tree of their day, the path of `FACT_SCHEMA_REVISION_SEED.md`, which exists only in commit `657d8da`, F-26 of the plan and the passages that steps 3.2 and 4 of the plan replaced, because they quote the earlier wording of another document, and the sentences that say this initiative holds both tasks - D-1 of the plan, the shape and the PRD - as the record of their day. Seeds, review entries, including those of other initiatives, and memory entries keep the old path.

Agent decision at C:40, without asking: in `docs/standards/decision_registry.md` the state sentence of the entry that lists the initiatives of the MVP plan was rewritten to the state after the move, not only relocated, because a registry has to state the current state, and `plans/schema_revision/` (db) was added to its list of initiatives and owners, before `plans_finished/fact_schema/`, so that "The last one" still names this initiative.
