# Review: Backend architecture with the worker, Q-11 of the MVP plan

Document state: 2026-10-04, ready for the whole initiative, initiative closed

## Implementation run of 2026-10-04

### Check before implementation

- HEAD at the start was `6f709f4`, with the plan committed in it by a human, and the working tree was clean. `BACKEND_ARCHITECTURE_SHAPE.md` has a closed interview, regulator C:40, and no `Block: yes`; the plan is closed, with no open question and no TODO.
- The facts were checked between 00:45 and 01:05 on 2026-10-04. The commits after that, `630d228` and `6f709f4`, changed only `BACKEND_ARCHITECTURE_PRD.md` and `BACKEND_ARCHITECTURE_PLAN.md`, so no cited file changed. `plans/mvp/MVP_PLAN.md`, `docs/product/specification.md`, `docs/product/schema.md`, `plans/mvp/MVP_PRD.md` and `docs/standards/decision_registry.md` were read again and checked against `git status` and their modification time right before each edit (`docs/standards/standard_agentic_workflow.md` ch. 4.7); none had a change in progress.

### Steps done

- S-2 and S-3: `docs/product/specification.md` is version 9, with M4, M9, the section Personal data, the paragraph of the versions and the Decision provenance item of version 9; `docs/product/schema.md` changes the account of a vote without a person and the section Who writes what.
- S-4: FR-13 and AC-12 of `plans/mvp/MVP_PRD.md` keep the hash until the demo is deleted, with a note at the end of its Risks and notes.
- S-1: D-12 of `plans/mvp/MVP_PLAN.md` hands the implementation of the operations to the work packages, D-13 settles Q-11, Risks and Open questions follow, and Supplementary files name this plan.
- S-5: the entry Technical directions of the MVP plan of `docs/standards/decision_registry.md` names this initiative.

### Deviations from the plan

O-1. The header of `docs/product/schema.md` said "part of `docs/product/specification.md` version 6", and S-3 changed the document without naming its header. It now says "Document state: 2026-10-04, part of `docs/product/specification.md` version 9". Agent decision at C:40, without asking: a document changed by version 9 cannot keep stating the version it was last part of.

O-2. D-2 of `plans/mvp/MVP_PLAN.md` listed "D-3 - D-12, and the one still open, Q-11, under Open questions", which S-1 did not name and which became false when Q-11 closed. It now says "D-3 - D-13". The other mentions of Q-11 in D-4, D-9, D-10 and D-11 there name what Q-11 decides and stay as they are, because D-13 settles "the former Q-11" as the other decisions settle theirs. Agent decision at C:40, without asking: the same consequence of S-1 as its Risks and Open questions.

### Checks

- `git diff --name-only` -> `docs/product/schema.md`, `docs/product/specification.md`, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md`; nothing under `plans_finished/`.
- A search of `docs/product/`, `docs/standards/`, `plans/mvp/MVP_PLAN.md` and `plans/mvp/MVP_PRD.md` for "30 days" next to a hash, an identifier or a vote finds only the paragraph of the versions and the Decision provenance item of version 9, which describe the replacement.
- A search of `docs/`, `plans/mvp/`, `plans/deployment/`, `plans/schema_revision/`, `plans/valhalla_routing/`, `CLAUDE.md` and `AGENTS.md` for "goes with Q-11" finds nothing.
- `fetch_prose_style_summary` of `tests/architecture/test_prose_style.py` over the whole repository, run with Python because pytest is not installed on this machine -> 0 forbidden characters, 0 bold in prose.
- `resolve_fact_violations` and `resolve_open_question_violations` of `tests/architecture/test_plan_document_contract.py` over the 13 closed plans, this one included -> 0 and 0.
- `make check` with pytest and prettier was not run: neither is installed on this machine. It stays a step for a human.

### Left for a human

- Tell the db person, the owner of `plans/schema_revision/`, that the periodic task is gone and that `IX_vote_cast_at_with_voter_hash` serves nothing now; `SCHEMA_REVISION_PRD.md` lines 29, 40 and 78 still name the task.
- Ask the backend person and the db person to confirm the rulings given for them (plan D-16).
- Run `make check`, then commit, push and the Merge Request.

## Review of 2026-10-04 (implementation-dod-review)

Scope: the whole initiative `backend_architecture` - the plan, the PRD, the shape and the five documents changed by S-1 - S-5, with the memory entry of `agent_docs/memory/_cross_cutting.md`.

- B-1. `npx --no-install prettier --check` warned on `BACKEND_ARCHITECTURE_PLAN.md`: no blank line after the indented paragraph of D-13 in S-1 step 2. Fixed after the review by adding that line; the content of the plan did not change. Prettier on the ten changed files then reported "All matched files use Prettier code style!". Prettier over every markdown file of the repository warns only on `.agents/skills/impeccable/reference/critique.md` and `.claude/skills/impeccable/reference/critique.md`, vendored files this initiative did not touch.
- R-1. AC-6 of the PRD asks that `plans/schema_revision/` receive the change; it is a step for a human, and `SCHEMA_REVISION_PRD.md` lines 29, 40 and 78 still name the periodic task until the db person changes them.
- R-2. The rulings given by the user for the backend person and the db person are still to be confirmed (plan D-16).
- R-3. D-4, D-9, D-10 and D-11 of `plans/mvp/MVP_PLAN.md` still say what "Q-11" decides; D-13 settles the former Q-11, as the plan settles its other former questions.
- Verification: `test_agent_docs_parity.py` 4 of 4 and `test_conflict_markers.py` passed, the prose scan found 0 and 0, the plan contract found 0 and 0 over 13 closed plans, all run with Python through their functions because pytest is not installed here; prettier passed after B-1; the standards of the Python and frontend profiles do not apply, because no code changed.

Verdict after the fix of B-1: ready, for the whole initiative `backend_architecture`. R-1 and R-2 are steps left to the user after the closure, which ch. 4.6 of `docs/standards/standard_agentic_workflow.md` lets the archive go ahead of. The initiative qualifies for `plans_finished/backend_architecture/`.
