# Review: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-04, task DEPLOYMENT reviewed

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
