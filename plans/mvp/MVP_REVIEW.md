# Review: MVP of the accessibility app

Document state: 2026-10-04, implementation finished, review ready after minor fixes for the whole initiative, fixes applied after it, staying in `plans/`

## Implementation run of 2026-10-04

### Check before implementation

- HEAD at the start was `7935bd5`, the tree was clean, and `git fetch --all` showed `origin/dev` and `origin/main` already merged into the working branch. `MVP_SHAPE.md` has a closed interview and the regulator C:60; the plan is marked closed and has no open question and no TODO.
- The user gave two instructions for this run on 2026-10-04: an initiative that is not finished does not stop the implementation, and adds its content to `MVP.md` later; no question is asked in this initiative, and what stays unresolved goes to the registry of open decisions, `docs/standards/decision_registry.md`.
- F-12 - F-17 and F-19 - F-28 hold as written. F-18 cited line 122 of `docs/standards/README.md`, which moved to line 123 when `dev` brought the item of `TEAM.md`; the fact was corrected in the plan with the check date 2026-10-04, and step 5 of Scope of changes is applied to the quoted sentence, not to the line number.
- Initiatives not finished at the start, implemented around as the user instructed: `plans/schema_revision/`, whose plan is closed and not carried out, so the version of the specification with the idempotency key does not exist yet; `plans/valhalla_routing/`, implemented with a review that is not ready, staying in `plans/`; `plans/deployment_config/`, which holds only its seed.

### What was done relative to the plan

- Step 1: `MVP.md` in the repository root with the twelve sections of D-16, the eleven rows of D-15 in the table Initiatives, and the twenty rows of FR-1 - FR-20 with the two rows of `plans/valhalla_routing/VALHALLA_ROUTING_PRD.md` in the table Requirements and initiatives.
- Step 2: the eleven seeds of D-15, generated from the block of step 2 of the plan, dedented and otherwise unchanged, and from the row of each initiative as `MVP.md` held it when the seed was saved. Each directory holds only its seed.
- Steps 3 - 9: applied as written, each fragment replaced only where it occurred exactly once.
- Step 10: the four notes of the plan, and a fifth one described below.

### Decisions taken during implementation

- Agent decision at C:60, without asking: the owners in `MVP.md`, and so in the rows the seeds quote, are named by first name with the role in brackets, for example Marek (backend), not by the role alone as D-15 writes them. `CLAUDE.md` asks a member of the team to be named by first name, and `TEAM.md` applies it to every document written from 2026-10-04 on and names both Kuber and Adrian for a matter of the frontend.
- Agent decision at C:60, without asking: the section Technical decisions of `MVP.md` keeps the numbers of the plan, D-1 - D-12 and D-14, so that the rows of the table Initiatives can name a decision by its number inside `MVP.md`.
- Agent decision at C:60, without asking: `plans/schema_revision/SCHEMA_REVISION_PLAN.md` came from `dev` at the merge of 01:16 and names work packages of `plans/mvp/`, but step 10 does not list it, so the DoD search would fail on it. D-18 covers every plan of another initiative in progress and leaves the place of a note to the agent, so it got the note at the end of its D-9. The names follow `MVP.md`: `schema_first_revision` for the revision, `community_facts` for the save of `create_fact` and the comparison its D-3 and D-5 describe, because `MVP.md` gives that operation to `community_facts`, and `frontend_app` for the frontend work package of its Risks. The note also records the instruction of the user of 2026-10-04 that the changes its S-3 and S-4 make to files of `plans/mvp/` go into `MVP.md`.
- The instruction of the user that an initiative not finished adds its content to `MVP.md` later is written into `MVP.md`, section Why this document exists, and into the reusable pattern of the memory entry of step 8.
- Two entries were added to the open decisions of `docs/standards/decision_registry.md`, outside the steps of the plan, because the user asked that what stays unresolved goes there instead of a question: Initiatives outside MVP.md that overlap its initiatives - `plans/osm_importer/` on the branch `md/fast-setup` and `plans/bus_station_api_integration/` on the branch `mw`, both with plans in progress and not merged - and When the initiative of O9 starts its code, because the specification builds O9 first and in parallel with the mandatory features while D-15 has it wait for `route_planning` and `osm_import`. `MVP.md`, section Open decisions and confirmations, points to both.
- The item of `MVP.md` in the standards map stands right after the item of `AI_WORKFLOW.md`, as step 5 says, so before the item of `TEAM.md` that `dev` added after the plan was written.
- The rows of the table Initiatives follow D-15 in content, with small changes of wording: the row of `schema_first_revision` names what D-11 gives to the builder of the revision, the rows of `osm_import`, `frontend_app` and `public_transport_routing` drop the references F-24, D-6 and the section Dependencies of `plans/valhalla_routing/VALHALLA_ROUTING_PRD.md`, which point into the plan rather than to a document a reader of `MVP.md` opens, and the row of `sample_data` names `docs/product/schema.md` in place of F-25.
- `prettier --write` was run on `MVP.md`, on this file and on `plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, where it added only the blank line after the note inside functional requirement 2.

### Findings

- `make lint-docs` fails on `docs/setup/EMULATOR_SETUP.md` alone, a file this run did not touch, merged with pull request 16 in commit `7541bb4`; every file this run changed or created passes prettier. The file was left as it is, because the plan changes no other file.
- FR-20 of `plans/mvp/MVP_PRD.md` still calls the identifier of a vote without an account a 30-day one, while version 9 of the specification, section Personal data, keeps it until the demo is deleted, and FR-13 and AC-12 of the PRD already say so. D-13 keeps the PRD unchanged and the specification prevails, so `frontend_app` writes the privacy page by the specification; reported to the user.
- Marek owns five of the eleven initiatives, `backend_skeleton` on the critical path among them; reported to the user as a risk to the deadline of 11:00.
- `plans/schema_revision/SCHEMA_REVISION_PLAN.md` numbers its version of the specification 10, which is taken, so it becomes version 11 when carried out (its D-7); `MVP.md` quotes that numbering rule instead of a number.

### Review against the Definition of Done

The skill `implementation-dod-review` ran through the subagent `dod-reviewer` on the uncommitted changes of the whole initiative. Verdict: ready after minor fixes, for the whole initiative `plans/mvp/`. No blocker. The 120 architecture tests pass, the seeds match the block of step 2 and their rows of `MVP.md` byte for byte, the DoD search for work packages returns only the allowed lines, and only `.md` files changed.

- R-1, not fixed: `make lint-docs` fails on `docs/setup/EMULATOR_SETUP.md` alone, outside the scope of the change. The plan changes no other file, so the fix is left to a separate task, offered to the user. Until the file is formatted or the user accepts this item of the Definition of Done, the final verdict cannot be ready.
- R-2, fixed: `MVP.md`, below the table Requirements and initiatives, says that FR-20 of the PRD still names a 30-day identifier and that version 9 of the specification, which keeps it until the demo is deleted, prevails.
- R-3, reported to the user: the order of `public_transport_routing` contradicts the specification, which builds O9 first and in parallel with the mandatory features; recorded in the decision registry, entry When the initiative of O9 starts its code.
- R-4, reported to the user: the note in `plans/schema_revision/SCHEMA_REVISION_PLAN.md` D-9 does more than map names, so Kuba should read it before carrying out that plan.
- U-1, fixed: the note in `plans/schema_revision/SCHEMA_REVISION_PLAN.md` D-9 now sends the changes of S-3 and S-4 to `MVP.md` without the condition of the archive, as `MVP.md`, section Why this document exists, says.
- U-2, fixed: the wording of the rows of the table Initiatives against D-15 is recorded above.
- U-3, fixed: this verdict with its scope.

After the fixes `venv/Scripts/python.exe -m pytest` passes and every changed file passes prettier. `plans/mvp/` does not qualify for `plans_finished/` while R-1 is open (`docs/standards/standard_agentic_workflow.md` ch. 4.6), so it stays in `plans/`. Once `docs/setup/EMULATOR_SETUP.md` passes prettier, a review that ends with ready for the whole initiative qualifies it, and the move updates the editable references to `plans/mvp/`, `MVP.md` and the documents of D-17 and of step 10 included.
