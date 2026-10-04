# Review: First schema revision of the domain model of facts and votes - the documents its implementation needs

Document state: 2026-10-04, implementation finished, version renumbered to 12 at the merge of `dev`, review ready for the whole initiative

## Implementation run of 2026-10-04

The plan `plans/schema_revision/SCHEMA_REVISION_PLAN.md` was carried out by `plan-implement` at C:40, on the branch `rm/requirements-preparation` at `e018faa`, with the uncommitted changes of the session that carried out `plans/mvp/` in `MVP.md`, `plans/mvp/MVP_REVIEW.md`, `AI_WORKFLOW.md` and D-9 of the plan taken as the current state.

### Version approved

The user approved version 11 of `docs/product/specification.md` on 2026-10-04, shown as the change of S-1 and S-2, before anything of S-3 - S-5 was written.

### Facts checked again

Three merges of `dev` reached the branch after the plan was written. Before the first write F-2, F-3, F-4, F-13, F-14, F-15 and F-20 were corrected in the plan with the check date 2026-10-04: the specification in force was version 10, of `plans_finished/deployment/`; `docs/product/schema.md` named version 9; `plans_finished/backend_architecture/` had brought version 9 and was archived; `MVP.md` and the decision registry named the initiative `schema_first_revision` as the builder of the first revision. The plan format check passes after the correction.

### Deviations from the plan and decisions

- D-7 applied: version 10 was taken, so the version is numbered 11, and every `10` and `version 9` of S-1 - S-5 moved to `11` and `version 10`. The number was checked against the state line of the specification right before S-2 and right before the approval.
- The changes of S-3 and of S-4 to files of `plans/mvp/` went into `MVP.md`, as the note at the end of D-9 says; `plans/mvp/MVP_PLAN.md` and `plans/mvp/MVP_PRD.md` are unchanged.
- Agent decision at C:40, without asking: the places of `MVP.md` that follow version 11. Scope names version 11, in place of the Goal of `plans/mvp/MVP_PLAN.md` and `plans/mvp/MVP_PRD.md` lines 17 and 111; D-11 names the column and its three constraints and points to D-1 - D-4 of the plan, in place of D-11 and D-12 of `plans/mvp/MVP_PLAN.md`; the row of `schema_first_revision` waits only for `backend_skeleton`, and item 2 of Order and critical path no longer waits for the version; the item of the initiatives in progress says the version was written; the item of Open decisions and confirmations on the version is removed, and the rulings still to be confirmed by Kuba include the form of the key; Sources names the plan, in place of the Supplementary files of `plans/mvp/MVP_PLAN.md`. `MVP.md`, section Why this document exists, asks that a change that makes an item of the file untrue updates it in the same change, and the plan gives no text for `MVP.md`. `MVP.md` line 128 keeps version 10 as the version that dropped a scene of the demo, by D-8.
- Agent decision at C:40, without asking: AC-3 of the Definition of Done is read on `MVP.md`. Its search for "until that version is approved", "does not hold yet" and "that the task still writes" still matches D-11, D-12 and the Supplementary files of `plans/mvp/MVP_PLAN.md`, which by the note at the end of D-9 this task does not write. The same search for the wordings of `MVP.md` that said the version was still to be written gives no match.
- Agent decision at C:40, without asking: the item of version 11 in the Decision provenance of the specification and the memory entry name Kuba where S-2 and S-6 say "the db person", because `TEAM.md` asks a document written from 2026-10-04 on to name a member of the team by first name.
- Agent decision at C:40, without asking: S-5 rewrites the current wording of the decision registry, which the session of `plans/mvp/` had changed after the plan was written: "has its PRD written and builds no code: it writes the new version of the specification with the idempotency key, and the initiative `schema_first_revision` builds the first revision" became "builds no code and wrote version 11 of the specification with the idempotency key, and the initiative `schema_first_revision` builds the first revision".
- S-6 names the initiative `schema_first_revision` in place of the work package of D-11, as the note at the end of D-9 says, and adds to Risk / notes the index `IX_vote_cast_at_with_voter_hash` and the rulings still to be confirmed.
- `prettier --write` was run on `MVP.md`, which re-padded the table Initiatives after the row of `schema_first_revision` got shorter.

### Checks

- AC-1: read against scenario 1 of `plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, the target schema leaves one fact, unverified with 0.5 of confirmations: the repetitions at 10:00:06 and 25 hours later are refused by `UX_fact_idempotency_key`, and the same key with another content is refused by the same constraint and answered `409 idempotency_key_reused` by the code of D-5.
- `venv/Scripts/python.exe -m pytest`: 120 passed, the prose style and plan format checks among them.
- `npx --no-install prettier --check` on every changed file: passes.
- The search of step 3 for the forbidden characters and bold in the changed files: no match outside `plans/schema_revision/SCHEMA_REVISION_SEED.md`, whose bold is the verbatim request.
- AC-2: `git grep -n "idempotency_key" docs/product/schema.md` shows the column, the three constraints and the item of the section Facts, and nothing in the rights.
- AC-4: `git grep -n -E "schema_revision|SCHEMA_REVISION" -- docs CLAUDE.md AGENTS.md PRODUCT.md AI_WORKFLOW.md plans/mvp MVP.md` gives no line that names this task as the builder of the first revision or says it waits for Q-11 or for the backend skeleton.
- The constraints of S-1 have not run: no PostgreSQL runs on this machine (F-17).

### Lines of other initiatives left by D-10

- `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md` lines 56 and 82, `BACKEND_ARCHITECTURE_PRD.md` lines 33 and 82 and `BACKEND_ARCHITECTURE_REVIEW.md` lines 36 and 45 still expect this task to build the revision, to decide the index `IX_vote_cast_at_with_voter_hash` and to change lines 29, 40 and 78 of `plans/schema_revision/SCHEMA_REVISION_PRD.md`, which still name the periodic task that version 9 removed. The archive is history, and the PRD of this task is not in the scope of the plan.
- `plans/valhalla_routing/VALHALLA_ROUTING_PRD.md` line 36 still says that this task builds the database schema.
- `plans/mvp/MVP_PLAN.md` D-11, D-12, item 2 and the last paragraph of D-15, step 10 of Scope of changes and the Supplementary files still say that the version with the key is still to be written, left by the note at the end of D-9.

### Findings

- Since version 9 no task clears `voter_hash`, so `IX_vote_cast_at_with_voter_hash` serves nothing, and FR-1 of the PRD forbids this task any other change of the target schema; reported to the user.
- `voter_hash` has no check of its length while `idempotency_key` has one (D-4); reported to the user.
- The rulings on the stored key, its form and the builder of the revision were given by the user in place of Kuba and are still to be confirmed.

### Review against the Definition of Done

The skill `implementation-dod-review` ran through the subagent `dod-reviewer` on the uncommitted changes of the whole initiative `plans/schema_revision/`, which has one task. Verdict: ready after minor fixes, for the whole initiative. No blocker; the 120 tests pass, and `prettier --check "**/*.md"` fails only on `docs/setup/EMULATOR_SETUP.md`, outside this change.

- R-1, settled by the user: AC-3 of the plan fails as written on `plans/mvp/MVP_PLAN.md` D-11, D-12 and the Supplementary files. On 2026-10-04 the user confirmed that AC-3 is read on `MVP.md`, and that `plans/mvp/` stays unchanged, as `MVP.md`, section Why this document exists, and the note at the end of D-9 say.
- R-2, open: while the review ran, the session that archived `plans/valhalla_routing/` changed the references to it in the specification, the decision registry, `MVP.md` and the shape, PRD and plan of this initiative, so the checks have to run again on the final tree.
- R-3 - R-5, reported to the user: the constraints have not run on PostgreSQL, the rulings given for Kuba are not confirmed, and the gaps of the Findings above stay.
- I-1: D-7 of the plan still says "numbered 10, the number after version 9 in force", D-8 and S-4 name `PRODUCT.md` line 101, and F-17 says pytest is not installed, while the corrected F-3 and F-15 and this run say otherwise. The plan is the contract and does not grow, and this log records how D-7 was applied, so the plan stays as it is.
- I-2, fixed: the reading of AC-1 is in Checks.
- I-3, reported to the user: lines 40, 55 and 78 of `plans/schema_revision/SCHEMA_REVISION_PRD.md` still name the periodic task that version 9 removed and version 7 as the version in force, and go into the archive as they are.
- I-4: the plan names "the db person" in the Steps of a human and the Risks, lines this run did not change. The plan and `TEAM.md` reached this branch in the same merge of `dev`, `540b4e8`, so whether the plan was written before that rule is not known, and the plan stays as it is.

### Version 11 on dev

After the review the session that keeps the repository consistent after the MVP reported that `origin/dev` holds an approved version 11 of its own, the user journeys of PR #22, so by D-7 the version of this initiative becomes version 12 at the merge of `dev`. On 2026-10-04 the user decided that the session merges `dev` and renumbers the documents in force, and that this initiative then checks the final tree, runs the review again and is archived only after it.

That session fast-forwarded the branch to `193471b` with the uncommitted changes kept on top, and renumbered the version to 12 in the specification - the state line, the sentence of Why this document exists, Open questions and the item of Decision provenance, which ends with "Written as version 11, it was numbered 12 on 2026-10-04 at the merge of `dev` that brought version 11 of `docs/product/user_journeys.md`" - in the state line of `docs/product/schema.md`, in `MVP.md` lines 19, 46, 68 and 117, in `PRODUCT.md` lines 45 and 100 and in line 48 of the decision registry. The artifacts of this initiative keep version 11 as the record of the run. The user approved the text, not the number, so the renumbering needs no new approval (D-7).

The fact check after the merge: of the files the plan cites, the merge changed only the specification, `MVP.md` and `PRODUCT.md`, and the change of S-1 and S-2 survived in them line by line. Version 11 of the user journeys changes no rule and no part of the target schema this version rests on; `docs/product/interface_texts.md` line 398 tells the person that a repeated save of a report saves nothing twice, which the key of this version makes possible. F-3 and F-15 describe the state before this run, which the run and the merge changed by design, so the plan stays as it is.

### Second review against the Definition of Done

The subagent `dod-reviewer` ran the review again on the final tree at `193471b` with the uncommitted work on top. Verdict: ready after minor fixes, for the whole initiative. The renumbering matches S-1 and S-2 with D-7 applied in every document in force; the 120 tests pass and `prettier --check "**/*.md"` is clean on the whole repository.

- R-A, fixed: the memory entry of S-6 named version 11 for the key, which the specification now gives to the user journeys. Agent decision at C:40, without asking: the entry, appended in this run and not committed, names version 12 and adds that it was written as version 11, so that an agent that reads memory cites the version the specification gives the key; no earlier entry changed.
- I-A, fixed: R-2 of the first review is closed. The session that archived `plans/valhalla_routing/` finished, and its edits inside this initiative only replace `plans/valhalla_routing/` with `plans_finished/valhalla_routing/`: three in the PRD, five in the shape and those of the plan.
- R-3 - R-5 and I-1, I-3, I-4 stay as recorded above.

After the second review the session that keeps the repository consistent corrected the end of the item of version 12 in the Decision provenance to "at the merge of `dev` that brought version 11 of this specification, written with `docs/product/user_journeys.md`", and the memory entry follows that wording. Its review also found that the item of `MVP.md` on the rulings still to be confirmed names the form of the key as a ruling given for Kuba, while the item of version 12 in the Decision provenance says only that the user decided it; the item of `MVP.md` now points to the steps of a human of the plan, which ask Kuba to confirm the stored key and its form. The approved text of the specification did not change.

### Final verdict

The subagent `dod-reviewer` checked again R-A, I-A and the two edits of the paragraph above on the current tree: the memory diff against `HEAD` only adds lines, the citation of `MVP.md` matches the steps of a human of the plan, the 120 tests pass and the touched files pass prettier. Verdict: ready, for the whole initiative `plans/schema_revision/`, which has one task. R-3 - R-5 stay as accepted risks reported to the user; Kuba confirming the rulings and the commit, push and Merge Request are steps of a human. The initiative qualifies for `plans_finished/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6).
