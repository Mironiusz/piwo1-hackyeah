# Review: Demo scenario and its verification

Document state: 2026-10-04, documentation implemented; runtime verification pending; initiative remains active

## Implementation run

The user approved `STAGE7_DEMO_SCENARIO_PRD.md` and authorized execution in the same reply. The plan was written from the current tree before implementing its steps. S-1, S-2, S-3 and S-5 are implemented: approval is recorded, the canonical scenario and handover are prepared, the current readiness is measured and every acceptance criterion has a state. S-4 awaits the runtime prerequisites. S-6's documentation review is recorded below.

`docs/demo/scenario.md` is the canonical runbook. It contains nine scenes with estimated durations totalling 160 seconds, requirements for S-1 - S-8, unverified real-data requirements O-1 - O-4, the hosted rehearsal boundary, local confirmation and unavailable-routing exercises, human recovery after an early hosted vote, limitations and prepared handover. The seed and supporting draft were not edited.

The blast radius is four Markdown files: the PRD state line, the new plan and review, and the canonical runbook. No product code, database, runtime configuration, loader, frontend, checklist tick or target environment was changed. No team member was contacted. The handover is prepared, not acknowledged by its recipients.

### Current readiness measurement

Measured on the local working tree at revision `10bf3f5`, on 2026-10-04. This is a local measurement, not a test of a separate hosted deployment.

- `api/app.py`, function `build_app`, now registers addresses, walking routes and accounts. This supersedes the earlier session's observation that it registered no product operation.
- The app factory registers no community-fact router and no copy-read router. The route module and fact serialization alone do not supply area reads, fact detail and voting endpoints.
- `plans/sample_data/` has a seed and stage, without a delivered sample loader. `worker/` has OSM and GTFS import commands, without a sample-data command.
- `plans/deployment_config/` has its seed and shape, without delivered full-demo configuration. The available Compose files run the database, not the complete demo.
- Checks 3.3, 6.1, 6.2 and 7.1 are unchecked in `FINAL_CHECKLIST.md`.
- `docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'` returned no local containers. Neither local routing nor a local full-demo environment could be identified for the stopping exercise.
- No runtime address was supplied during this execution. The user was asked outside the repository whether a ready local or hosted application is available. No address was invented or stored.
- The current Python and repository venv lack the API dependencies and pytest. The old Anaconda environment has pytest but cannot collect the parity gate on Python 3.8 because tomllib is missing. For documentation gates only, pytest 9.1.1 was installed into `/tmp/enableme-stage7-tools`; project dependency files were not edited.
- The default frontend development proxy points to the project's mock backend. No mock run was substituted for the real service required by the PRD.

No runtime scene was attempted against an unidentified or incomplete environment. Real map-data existence and placements remain unverified. No demonstration vote, hosted write, database read of personal vote data, routing stop or database reset was performed.

### Acceptance criteria

| Criterion | State                                  | Evidence or remaining input                                             |
| --------- | -------------------------------------- | ----------------------------------------------------------------------- |
| AC-1      | Documentary pass                       | Nine timed scenes total 160 seconds.                                    |
| AC-2      | Runtime unperformed                    | Profile, map, copy date and result need the real application.           |
| AC-3      | Runtime unperformed                    | Two real address matches remain unverified.                             |
| AC-4      | Runtime unperformed                    | S-2, S-3 and S-4 need verified placements and sample data.              |
| AC-5      | Documentary pass                       | Eight sample requirements preserve the bundled content.                 |
| AC-6      | Procedure written; runtime unperformed | O-1 - O-4 are explicitly unverified.                                    |
| AC-7      | Runtime unperformed                    | Actual report and map-fact detail need live reads.                      |
| AC-8      | Runtime unperformed                    | Initial S-5 and accepted local and hosted contributions are unverified. |
| AC-9      | Runtime unperformed                    | Real connectors and a partial-data stretch need a route.                |
| AC-10     | Runtime unperformed                    | Identified local routing and its commands are missing.                  |
| AC-11     | Documentary pass                       | Limitations and separate accessibility evidence are explicit.           |
| AC-12     | Runtime unperformed                    | No real hosted or local rehearsal took place.                           |
| AC-13     | Conditional; not triggered             | No early hosted vote or human restoration was observed.                 |
| AC-14     | Documentary pass; acceptance pending   | Handover is prepared for Mateusz, Adrian, Kuber and Rafał.              |
| AC-15     | Record pass                            | Current prerequisites and unperformed scenes are explicit.              |
| AC-16     | Runtime unperformed                    | Full hosted run and its pitch contribution remain pending.              |

Documentary passes establish the written material only. They do not settle the observed behavior required by the runtime criteria or mark checks 7.2 and 7.3 complete.

### Memory assessment

No durable memory entry was added. This change creates no new code-unit pattern or reusable architectural decision; its rehearsal boundary and prepared data are specific to the demo and already have the canonical runbook as their maintained source.

## Blockers

B-1. The whole initiative lacks the runtime evidence required by PRD AC-2 - AC-4, AC-6 - AC-10, AC-12 and AC-16. The current tree lacks required community-fact operations, copy-read operation, sample-data loading and full-demo configuration; no ready runtime address was supplied. The canonical procedure does not replace these dependencies.

B-2. The hosted contradiction scene must retain its contribution for the pitch. Even a complete local rehearsal would not qualify the hosted run as passed. The actual hosted pitch contribution and resulting route change remain necessary before the whole initiative can close.

## Risks

R-1. The current checkout and a separate deployed revision can differ. The local readiness record is not evidence that any separately hosted application is unavailable.

R-2. Real map data can invalidate the default destination or the assumed demonstration crossings. `docs/demo/scenario.md`, Real map-data requirements, keeps them unverified and assigns verification and permitted destination choice to Mateusz.

R-3. A prior contribution from the same IP and User-Agent can consume the daily vote even with a new browser session. The local and hosted data must remain separate, and an earlier hosted vote requires human restoration.

R-4. The repository-wide prose gate has baseline violations outside this change: typographic quotation marks in the downloaded HarmonyOS testing package, and bold prose in existing mobile documentation and `.pytest_cache/README.md`. No violation in the changed Markdown was reported by that run. These unrelated files were not rewritten.

R-5. The repository-wide Prettier check reports nine existing files outside this change: `.pytest_cache/README.md`, four README or changelog files of the downloaded HarmonyOS test packages, and `mobile_app/accessway/README.md`, `mobile_app/AI_WORKFLOW.md`, `mobile_app/docs/ARCHITECTURE.md` and `mobile_app/docs/EMULATOR_SETUP.md`. The four changed Markdown files pass their separate formatting check. No global formatting rewrite was performed.

## Improvements

None required for the documented procedure. Once the real application and placements are delivered, replace estimated timing with measured durations in the result record and record the destination and sanitized runtime evidence.

## Verification

### Commands and outcomes

- The first attempt with the old Anaconda interpreter failed during collection on missing tomllib. This was an unsuitable test environment, not an application or document regression.
- The seven-file core run with `/tmp/enableme-stage7-tools/bin/python -m pytest -o addopts=-ra tests/architecture/test_plan_document_contract.py tests/architecture/test_prose_style.py tests/architecture/test_conflict_markers.py tests/architecture/test_agent_docs_parity.py tests/architecture/test_vendored_content.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` collected 122 tests: 120 passed and the two repository-wide prose assertions failed on the unrelated paths described in R-4.
- After the scenario and result record were written, `/tmp/enableme-stage7-tools/bin/python -m pytest -o addopts=-ra tests/architecture/test_plan_document_contract.py tests/architecture/test_prose_style.py tests/architecture/test_conflict_markers.py` collected 54 tests: 52 passed and the same two global prose assertions failed only on R-4's baseline paths.
- `npx --no-install prettier --check "**/*.md"` failed on the nine unrelated files of R-5. The same check naming only `docs/demo/scenario.md` and this initiative's PLAN, PRD and REVIEW passed for all four files.
- A scoped run of the existing prose validators found no violation in those four Markdown files; the existing fact and open-question validators accepted the new closed plan. A structural check confirmed nine contiguous timed scenes totalling 160 seconds, S-1 - S-8, O-1 - O-4 and all sixteen criteria in the result table. These are document checks, not application tests.

### Standard map

| Standard                     | Verification state    | Scope and outcome                                                              |
| ---------------------------- | --------------------- | ------------------------------------------------------------------------------ |
| standard_agentic_workflow.md | Checked automatically | The parity, vendor and hook gates passed.                                      |
| standard_agent_docs.md       | Checked automatically | The closed-plan contract gate passed.                                          |
| standard_review.md           | Checked manually      | Scope, blockers and verdict remain explicit.                                   |
| standard_documentation.md    | Checked manually      | The runbook describes actions and evidence; no code unit changed.              |
| standard_formatting.md       | Checked automatically | Prettier and prose checks run; baseline prose failures are separated.          |
| standard_git.md              | Checked automatically | Conflict-marker gate passed; no index or history mutation.                     |
| standard_architecture.md     | Not applicable        | No code layer or imports changed.                                              |
| standard_config.md           | Not applicable        | No environment key or configuration changed.                                   |
| standard_database.md         | Not applicable        | No schema, query, data access or reset changed.                                |
| standard_errors.md           | Not applicable        | No error handling or retry behavior changed.                                   |
| standard_idempotency.md      | Not applicable        | No loading or write mechanism changed.                                         |
| standard_code_quality.md     | Not applicable        | No executable code changed.                                                    |
| standard_logging.md          | Not applicable        | No logger changed; evidence excludes identifying request data.                 |
| standard_naming.md           | Not applicable        | No function or code-file names introduced.                                     |
| standard_security.md         | Not applicable        | No project dependency or executable behavior changed.                          |
| standard_tests.md            | Checked automatically | Existing document gates ran; no implementation-mirroring tests added.          |
| standard_time.md             | Not applicable        | No clock or storage behavior changed; the runbook uses M4's existing day rule. |
| standard_worker.md           | Not applicable        | No worker or periodic task changed.                                            |
| standard_frontend.md         | Not applicable        | No frontend implementation changed.                                            |

## Verdict

Not ready for the whole initiative: the scenario and handover are implemented, but required local and hosted runtime verification remains unperformed. This verdict covers the documented work and its recorded prerequisites, and does not certify the application. The initiative stays in `plans/stage7_demo_scenario/`; it is not qualified for `plans_finished/` and checks 7.2 and 7.3 remain unchecked.
