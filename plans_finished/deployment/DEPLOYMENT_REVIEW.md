# Review: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-04, initiative closed: the task `DEPLOYMENT` is ready, and the task `DEPLOYMENT_CONFIG` was moved to the initiative `plans/deployment_config/` by a decision of the user

## 2026-10-04 - Implementation of DEPLOYMENT_PLAN.md

### Facts corrected before the start

- F-1, F-17 and F-18 were corrected before any change: since the plan was written, `plans/valhalla_routing/` got its plan and its `valhalla/` directory, and the other sessions already moved `plans/backend_architecture/` and `plans/valhalla_routing/` to the server of the user.

### Run into during implementation

- Z-1. The plan did not foresee that the routing service has to be restarted on the routing data built by the loading step before routes work (F-18, from `plans/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-3). Section Loading the data of `docs/deployment/hosted_demo.md` gets that sentence, with its command completed by the configuration task as D-2 requires, and the check gains nothing new because its route point already fails without it. Agent decision at C:40, without asking: a decided contract of another initiative, not a guess, and leaving it out would make the instructions produce a demo whose every route ends with the routing unavailable message.
- Z-2. Another session, implementing `plans/valhalla_routing/`, edited `CLAUDE.md`, `AGENTS.md`, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PLAN.md`, `AI_WORKFLOW.md`, `agent_docs/memory/_cross_cutting.md` and `DEPLOYMENT_PRD.md` minutes before this implementation, in other sections than this plan. The edits of this plan were announced by messages to the three sessions working on Valhalla, naming the sections each side touches, according to `docs/standards/standard_agentic_workflow.md` ch. 4.7. Two answered that the edits were not theirs, the third did not answer; the shared files had not changed for more than two minutes, so the edits of this plan were made as exact replacements in their own sections, and every edit of the other session stays as it was.

### Done relative to the plan

- Steps 1 - 7 of Scope of changes are done as written, with the one addition of Z-1. Nothing under `plans_finished/` changed.

### Review against the Definition of Done

Blockers: none.

Risks:

- O-1. `npx --no-install prettier --check` could not run in this session: `node_modules` is not installed on this machine (F-16). The session implementing `plans/valhalla_routing/` ran `npx prettier --check plans/deployment/*.md docs/deployment/hosted_demo.md docs/standards/README.md` after both sessions finished their edits, with the result "All matched files use Prettier code style!", after a loose paragraph in section Out of scope of `DEPLOYMENT_PRD.md` was turned into a list item. `CLAUDE.md`, `AGENTS.md`, `AI_WORKFLOW.md`, `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md` and `agent_docs/memory/_cross_cutting.md` were not in that run, so `make check` on a machine with the development dependencies is still to be run before the merge.
- O-2. The task `DEPLOYMENT_CONFIG` has only its seed. The requirements handed to it - one command, one host, one backend process, a database instance of its own, restarts that keep the data - stand in section Out of scope of `DEPLOYMENT_PRD.md` and in `plans/mvp/MVP_PLAN.md` D-10, and its shape has to take them from there; until it exists, `docs/deployment/hosted_demo.md` points to a task with no plan.
- O-3. The specification M10 and AC-15 of `plans/mvp/MVP_PRD.md` still disagree with the cuts of this initiative; a separate task was suggested to the user for them.
- O-4. Handed over to the task `DEPLOYMENT_CONFIG`, not decided here: on 2026-10-04 the session working on `plans/valhalla_routing/` announced a manual-only workflow, `.github/workflows/valhalla-image.yml`, that publishes the patched Valhalla image to the GitHub container registry under a fixed version tag with no `latest`, so that the server pulls that tag instead of building the image of `plans/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-1. If the package is private, the server first needs a one-time login with a token that reads packages - a secret that lives only on the server. The workflow can be run only once it is on the default branch. Whether the demo pulls or builds the image is for `DEPLOYMENT_CONFIG` to decide; `docs/deployment/hosted_demo.md` is not changed for it.

Improvements: none.

Verification:

- `standard_agentic_workflow.md`: checked automatically - the parity tests of `tests/architecture/test_agent_docs_parity.py` pass, run through a local stand-in for pytest because pytest is not installed (F-16); the hook tests need `pytest.mark` and were not run, and the change touches no hook.
- `standard_agent_docs.md`: checked automatically - `tests/architecture/test_plan_document_contract.py` passes with `DEPLOYMENT_PLAN.md` closed.
- `standard_review.md`: checked manually - this record.
- `standard_documentation.md`: checked manually - plain English, no bold, references by path and section.
- `standard_formatting.md`: checked automatically for `tests/architecture/test_prose_style.py`, which passes on the whole repository; prettier passed on the deployment documents and the standards map, run by another session, and not checked on the other changed files (O-1); `ruff format` not applicable, no Python changed.
- `standard_git.md`: checked automatically - `tests/architecture/test_conflict_markers.py` passes; no commit was made.
- `standard_architecture.md`, `standard_database.md`, `standard_errors.md`, `standard_idempotency.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md`, `standard_tests.md`, `standard_time.md`, `standard_worker.md`: not applicable - no code, schema, query, log, test, time rule or periodic task changed.
- `standard_config.md`: checked manually - no address, host, login or secret in any changed file, by a search for IPv4 and IPv6 forms; the environment file is described only by the names of the templates.
- `standard_frontend.md`: not applicable - no frontend code.

Verdict: ready after minor fixes, for the task `DEPLOYMENT` only. The minor fix is running `make check` (O-1). The initiative `plans/deployment/` also holds the task `DEPLOYMENT_CONFIG`, which has only a seed, so it stays in `plans/` and does not qualify for the archive.

## 2026-10-04 - Initiative closed

The user asked to move the task `DEPLOYMENT_CONFIG` into an initiative of its own and to archive this one. `DEPLOYMENT_CONFIG_SEED.md` moved to `plans/deployment_config/` with the same name and the checksum confirmed after the move, and its content is unchanged. That initiative has only its seed; its shape takes the requirements of O-2 from section Out of scope of `DEPLOYMENT_PRD.md` and from `plans/mvp/MVP_PLAN.md` D-10.

O-1 was settled after the merge of `dev` into this branch, commit `50a50cd`. `make check` was run with the development dependencies of `venv`: ruff, mypy, vulture, deptry, bandit, pip-audit and pytest, 120 passed, pass. Prettier failed on two files. In `DEPLOYMENT_PLAN.md` one blank line between item 5 of Scope of changes and its nested list was removed by `prettier --write`, the only change of the plan, with no change of content. `docs/setup/EMULATOR_SETUP.md` came from `dev` with the emulator setup and is not part of this initiative, so it stays as it is. After the fix `npx --no-install prettier --check` passes on the files of this initiative and on every file it changed outside it: `docs/deployment/hosted_demo.md`, `docs/standards/README.md`, `CLAUDE.md`, `AGENTS.md`, `AI_WORKFLOW.md`, `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md` and `agent_docs/memory/_cross_cutting.md`.

Verdict: ready, for the task `DEPLOYMENT`. Without the task `DEPLOYMENT_CONFIG` it covers the whole initiative, so the directory moves to `plans_finished/deployment/` (`docs/standards/standard_agentic_workflow.md` ch. 4.6). O-2 goes with the task `DEPLOYMENT_CONFIG`, and O-3 stays with the separate task suggested to the user; neither blocks the closure, and the archive confirms neither.

References. In the shape, the PRD and the plan of this initiative only the location of references changed: the task `DEPLOYMENT_CONFIG` named by `plans/deployment/` is named by `plans/deployment_config/`, its seed points there, and every other `plans/deployment/` points to `plans_finished/deployment/`. The same rules apply to `CLAUDE.md`, `AGENTS.md`, `docs/deployment/hosted_demo.md`, `docs/standards/README.md`, `docs/standards/decision_registry.md`, `docs/product/specification.md`, `plans/mvp/`, the shape of `plans/backend_architecture/`, the PRD of `plans/schema_revision/`, the PRD and the plan of `plans/valhalla_routing/`, and the shapes, PRDs and plans of `plans_finished/demo_environment/`, `plans_finished/frontend_stack/`, `plans_finished/local_database/` and `plans_finished/routing_engine/`. The sentences that say this initiative still holds the task `DEPLOYMENT_CONFIG` - the summary and D-1 of the plan and section Out of scope of the shape - stay as the record of their day. Seeds, review entries, memory entries and the log of `AI_WORKFLOW.md` keep the old path as a historical record.

Agent decision at C:40, without asking: two sentences of `plans/valhalla_routing/` name `plans/deployment/` as the executor of work still to be done - building the deployment configuration in section Out of scope of `VALHALLA_ROUTING_PRD.md`, and running the service of D-1 in D-13 of `VALHALLA_ROUTING_PLAN.md`. They point to `plans/deployment_config/`, because the archive does no more work and that work is the task `DEPLOYMENT_CONFIG`.

Agent decision at C:40, without asking: in `docs/standards/decision_registry.md` the state sentence of the entry that lists the initiatives of the MVP plan was rewritten to the state after the move, not only relocated, because a registry has to state the current state. `plans/deployment_config/` was added to its list of initiatives and owners with the owner of `plans/deployment/`, the initiative it was split from.
