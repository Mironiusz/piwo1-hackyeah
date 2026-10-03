# Review: Valhalla as the routing engine and public transport routes from static GTFS

Document state: 2026-10-04, implementation finished, review not ready for the whole initiative, fixes applied after it, staying in `plans/`

## Implementation run of 2026-10-04

### Check before implementation

- HEAD at the start was `2135a90`, with the plan committed in it by a human. `VALHALLA_ROUTING_SHAPE.md` has a closed interview, regulator C:40, no open question and no `Block: yes`; the plan has no open question and no TODO.
- Three commits made after the facts were checked, `e6d9a67`, `100e801` and `2135a90`, changed `plans/deployment/DEPLOYMENT_PRD.md`, the files of this initiative and added `valhalla/`. F-1 and F-20 were corrected in the plan and F-26 was added, all with the check date 2026-10-04; the other facts cite files those commits did not change.
- `plans/deployment/DEPLOYMENT_PLAN.md` is untracked and was written at 00:31 by another session working on `plans/deployment/`. It changes D-10 of `plans/mvp/MVP_PLAN.md` only and leaves this initiative to its owner (its D-8), so the two runs touch different decisions of the same file; S-5 checks the file right before each edit (`docs/standards/standard_agentic_workflow.md` ch. 4.7).

### Deviations from the plan

O-1. `valhalla/` was added in `e6d9a67` with `valhalla/Dockerfile`, `valhalla/README.md` and the two patches, byte for byte those copied by S-1 into `plans/valhalla_routing/spike/`. The two copies in `plans/valhalla_routing/spike/` were removed, and D-1, D-15, F-12, S-1 and the section Supplementary files of the plan point to `valhalla/` instead. Agent decision at C:40, without asking: two copies of the same patch can diverge, and the build definition already lives in `valhalla/`.

O-2. `PRODUCT.md` lists the optional features O1 - O8 and public transport routes as out of scope altogether (lines 86 - 87), and no step of the plan names it. It is changed together with S-2 so that it follows version 8 of the specification. Agent decision at C:40, without asking: the specification prevails over every other document (`CLAUDE.md`, section What we are building), and `plans_finished/routing_engine/` changed `PRODUCT.md` the same way when it changed the specification.

O-3. S-2 gets two more changes of the specification it does not name: under Open questions "None at version 7." becomes "None at version 8.", and the first sentence of section Decision provenance names 2026-10-04 next to 2026-10-03. Agent decision at C:40, without asking: every version raised that line (`plans_finished/routing_engine/ROUTING_ENGINE_REVIEW.md` O-1), and the entry of version 8 records decisions of 2026-10-04.

O-4. Step 7 of `plan-implement` added the entry "Valhalla run by the project replaces the route graph" to `agent_docs/memory/_cross_cutting.md`, next to the entry of `plans/routing_engine/` it partly supersedes; the earlier entry stays as history.

O-5. S-7 was carried out at 00:37 and then overtaken by the session working on `plans/backend_architecture/`, which rewrote the same file at 00:40 and 00:42 (`docs/standards/standard_agentic_workflow.md` ch. 4.7): its question 2 is gone from Open questions, and its section Smallest meaningful scope, item 3, and the paragraph after the list now carry the decision of this initiative in its own words. The note S-7 prescribes is therefore not in the file, and line 22 still says the route graph is "in force as D-9 of `plans/mvp/MVP_PLAN.md`", false since S-5. That file belongs to its own session, so this run does not edit it again; the line is reported to the user.

O-6. After the review, M7 of the specification read both that a public transport segment "is green whenever its GTFS gives no accessibility information" and, in the next paragraph, "A segment without complete data is never green." The second sentence now begins "Apart from the exception of O9 above,". Agent decision at C:40, without asking: S-2 meant the exception, and its literal text left M7 contradicting itself; the user approves the text of version 8 anyway.

O-7. After the review, D-9 of `plans/mvp/MVP_PLAN.md` also keeps D-2 and D-17 of `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md`, which S-5 listed neither as replaced nor as kept, and says that under the kept D-2 every call to Valhalla has one call site in the data layer and one seam in the rules layer (`docs/standards/standard_architecture.md`, section Calls to external systems). Agent decision at C:40, without asking: D-2 still holds once the call to Valhalla is a read of the data layer, and D-17 still covers the confirmation of D-11, which is kept. The other requirements of that section of the standard for a read during request handling - its own named exceptions, the documented strategy of no retry with the 2 seconds of D-10, the call through a thread pool and the cache - are for the route work package; whether a cache of routes makes sense at all is a question for it and Q-11.

O-8. After the review, `PRODUCT.md` line 74 names the exception of O9 next to the rule that missing information is never presented as a confirmation of accessibility, and the tools of the entry of `AI_WORKFLOW.md` name the `dod-reviewer` subagent instead of "no subagents". Agent decision at C:40, without asking: both followed from O-2 and from this run.

### Steps carried out

- S-1 in phase B; S-2 with O-3; O-2; S-3; S-4; S-5; S-6; S-7; S-8, in this order. Before S-5, S-7 and S-8 the files were checked with `git status`, `git log` and their modification time: none had a change after the last commit, and HEAD moved only by the human commit `cfe0adc` of `plans/deployment/DEPLOYMENT_PLAN.md` during the run.
- Gates: pytest is not installed for the Python of this machine, and installing it needs a download, so `make test` was not run. The checks of `tests/architecture/test_plan_document_contract.py`, `tests/architecture/test_prose_style.py` and the parity of `AGENTS.md` and `CLAUDE.md` of `tests/architecture/test_agent_docs_parity.py` were run through their helper functions with a stand-in for the `pytest` module in the scratchpad of the session: no violation in any gated plan, none in the prose of the whole repository, parity holds. `npx prettier --check` passes on every file this run changed except the two of Z-2.

### Findings outside the scope of this run

Z-1. `valhalla/Dockerfile` carries three line comments (`# ENABLE_SERVICES must stay ON ...` and the two after it), while `CLAUDE.md`, section Comments and code documentation, says "Do not write line comments in code." `valhalla/README.md` exempts the C++ diffs of the patches, not the Dockerfile. The file was added by a human in `e6d9a67` and is not changed by this run; it is reported to the user.

Z-2. At the end of the run `npx prettier --check` failed on `plans/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md`, where it would renumber the open questions the interview cites by number, and on `plans/deployment/DEPLOYMENT_PRD.md`, where a continuation paragraph broke a nested list at line 34. Both failures stood at HEAD `cfe0adc` before this run. The sessions owning both files rewrote them during the review, and at 00:45 prettier passes on both and on every file this run changed.

Z-3. The git index held a partial version of this run while it was still working: the specification, the plan, this file and the two removed patches were staged before O-3 - O-8 were written, so committing the index as it stands would ship version 8 with "None at version 7.". This run ran no `git add`. Whoever commits restages from the working tree.

### Review of 2026-10-04

- The `implementation-dod-review` skill through the `dod-reviewer` subagent, on the uncommitted changes at about 00:41, for the whole initiative `plans/valhalla_routing/`: not ready. Blocker B-1, the failing prettier run on `plans/deployment/DEPLOYMENT_PRD.md`, is settled by Z-2. Risks R-1, R-2 and R-5 are settled by O-6, O-5 and O-7, R-3 is Z-3, and improvements I-1 and I-3 by O-8.
- Left open after the fixes: `make test` has never run, because pytest is not installed on this machine (R-4); the user has not approved the text of version 8 of the specification and of the exception in `CLAUDE.md` and `AGENTS.md`, and the backend person has not confirmed D-16 (R-6); the wording of the public transport segment that the GTFS marks as accessible, and of alighting next to "the ride and the boarding at the stop", is for the user (I-2). No second review was run after the fixes.
- The verdict does not qualify the initiative for `plans_finished/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6), so the directory stays in `plans/`.
