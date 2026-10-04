# Plan: Demo scenario and its verification

Document state: 2026-10-04, plan closed

## Goal

Implement the approved `STAGE7_DEMO_SCENARIO_PRD.md`: write the scenario and sample-data handover, give the team an executable verification procedure, and record the actual readiness and results of local and hosted checks. The user approved the PRD and explicitly requested execution in the same reply. The plan is complete even when its runtime steps await the application and data of other initiatives; those prerequisites do not count as successful checks.

## Facts

F-1. The shape is closed at C:40 and has no blocking open question; the PRD has the user's approval and twelve requirements with sixteen acceptance criteria. | doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SHAPE.md` state line, Functional requirements and Open questions; doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_PRD.md` state line, Functional requirements and Acceptance criteria | 2026-10-04
F-2. The shape requires a wheelchair-profile route from the Tauron Arena to Ogród Doświadczeń, with a destination change only when the real contradiction crossing or the alternative around S-2 is missing. | doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SHAPE.md` Domain rules or explicit TODO, the items on the preset and route; doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_PRD.md` FR-3 and AC-3 | 2026-10-04
F-3. S-5 starts at confirmation weight 1.5 and is confirmed by one anonymous vote of weight 0.5; hosted rehearsal ends before that vote and local rehearsal uses separate data. | doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SHAPE.md` Domain rules or explicit TODO, the items on S-5 and rehearsal; doc:`docs/product/specification.md` M4 and M9 | 2026-10-04
F-4. The bundled demo defines eight sample reports and areas, S-5 with only one confirmation of weight 1, flagged S-6 and S-7 and hidden S-8; their coordinates describe a schematic network. | code:`mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets` function `demoReports` and helper `sample`; doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_DRAFT.md` section 5 | 2026-10-04
F-5. The current app registers address search, walking routes and accounts, but no community-fact or copy-read router. | code:`api/app.py` function `build_app`; cmd:`rg --files api` -> account, session, address and route modules, no community-fact or copy-read module | 2026-10-04
F-6. Checks 3.3, 6.1, 6.2 and 7.1, required before the hosted verification, are unchecked. | doc:`FINAL_CHECKLIST.md` checks 3.3, 6.1, 6.2 and 7.1 | 2026-10-04
F-7. The sample-data initiative contains only its seed and stage; no worker loads sample facts, and deployment configuration has a shape and seed but no delivered full-demo Compose file. | cmd:`rg --files plans/sample_data plans/deployment_config worker` -> seeds, stages, deployment shape, OSM and GTFS workers; cmd:`rg --files -g '*compose*'` -> only the local and deployment database Compose files | 2026-10-04
F-8. No local Docker container is running at the readiness measurement. | cmd:`docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'` -> no rows | 2026-10-04
F-9. The frontend development proxy defaults to the project's mock service, while a build uses same-origin API requests. A mock run cannot verify the hosted application. | code:`frontend/vite.config.ts` constant `apiProxy` and server and preview settings; doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_PRD.md` AC-16 | 2026-10-04
F-10. The contract names the scenario's address search, copy date, area facts, fact detail, route and vote operations; a confirmation is a POST and is a durable contribution. | doc:`docs/product/api_contract.md` sections search_address, read_osm_copy, list_facts_in_area, read_fact, plan_route and cast_vote | 2026-10-04
F-11. The views and interface texts define the wheelchair preset, four assessed route states, sample marks, contradiction text, replanning, incomplete-data note and unavailable-routing message. | doc:`docs/product/views.md` V-2, V-5, V-6, V-8, V-9 and V-13; doc:`docs/product/interface_texts.md` keys needs.preset.wheelchair, sample.mark, fact.contradiction, route.replanning, route.no_data_note and plan.unavailable.title | 2026-10-04
F-12. The current Python and repository venv lack pytest and the API dependencies; the available Anaconda pytest runs under Python 3.8 and cannot collect the parity gate because tomllib is missing. Prettier 3.7.4 is installed at the repository root. | cmd:`python --version` -> Python 3.14.2; cmd:`python -c 'import importlib.util; print({name: importlib.util.find_spec(name) is not None for name in ("pytest", "fastapi", "httpx")})'` -> all False; cmd:`/home/marek/anaconda3/bin/python -m pytest -o addopts=-ra tests/architecture/test_plan_document_contract.py tests/architecture/test_prose_style.py tests/architecture/test_conflict_markers.py tests/architecture/test_agent_docs_parity.py tests/architecture/test_vendored_content.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` -> collection fails on missing tomllib in Python 3.8; cmd:`node_modules/.bin/prettier --version` -> 3.7.4 | 2026-10-04
F-13. The draft is a proposal, not the final scenario, and there is no existing final scenario document in docs. | doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_DRAFT.md` introduction; cmd:`rg --files docs -g '*scenario*'` -> no match | 2026-10-04
F-14. Hosted rehearsal may not cast the demonstration vote; the agent may not reset hosted data or stop hosted routing. Target addresses and secrets must remain outside every repository artifact. | doc:`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_PRD.md` FR-5, FR-7, FR-8 and Domain rules; doc:`AGENTS.md` Target environment; doc:`docs/deployment/hosted_demo.md` Known limits of the hosted demo | 2026-10-04

## Decisions

D-1. Write one canonical runbook, `docs/demo/scenario.md`, containing the timed scenes, sample-data requirements, map-data verification register, rehearsal rules, local unavailable-routing check and handover. Keep the draft and seed unchanged. Agent decision at C:40, without asking: the approved scope is a scenario and its verification, not new service code or another implementation of facts and routes.

D-2. Record the execution and per-criterion status in `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_REVIEW.md`. Distinguish the written procedure from observed behavior. A documented scene can be ready as documentation while its runtime criterion remains unperformed. Agent decision at C:40, without asking: this follows the REVIEW format and PRD AC-15 and AC-16.

D-3. Keep all generated changes inside this initiative and `docs/demo/scenario.md`. The blast radius is limited to references from the new runbook to the product documents, contract and initiative artifacts. No endpoint, database object, configuration key, frontend code, loading operation or checklist tick changes. Handover consists of prepared material, with acceptance pending; no message is sent to team members.

D-4. Before runtime verification, repeat the prerequisite and application checks from F-5 - F-9. Obtain the runtime address outside the repository and distinguish local from hosted. Confirm that the frontend talks to the real backend, that the copy and sample facts are available, and that S-5 is still eligible for the demonstration vote. If a prerequisite is absent, record the affected scenes as blocked rather than starting another initiative's implementation.

D-5. The main hosted rehearsal covers scenes 1 - 6 only. The full hosted demonstration, including the accepted confirmation, is at the pitch as the shape requires. Local rehearsal covers the confirmation and unavailable-routing exercises in separate local data. Only stop and restart a positively identified local routing container through the owner's delivered local setup commands; never infer a container name or stop hosted routing. No cleanup or reset is added by this initiative.

D-6. Runtime evidence records the application revision, environment kind, measured duration, visible result and criterion status, without runtime addresses, raw IP, User-Agent, identity hashes, headers or secrets. Screenshots and clips are sanitized before being attached. An inaccessible or unspecified environment is a prerequisite to resume verification, not permission to guess its address or fabricate a run.

D-7. Use the installed Prettier on the touched Markdown files. Run the workflow, artifact, prose and conflict-marker architecture gates with the pinned pytest in a temporary environment under `/tmp/enableme-stage7-tools` when the project Python lacks it. No project dependency changes are needed for this documentation work. Agent decision at C:40, without asking: the old Anaconda interpreter cannot run the existing gates, and a separate temporary environment preserves other sessions' setup.

D-8. Complete the documentation steps and their review even when runtime verification is unavailable. The whole initiative stays in `plans/` until the runtime criteria actually pass and review covers the whole scope. No memory entry is needed merely to repeat this scenario's rehearsal rule: it is a task-specific condition retained by the canonical runbook and the review.

## Scope of changes

S-1. Input: the user's approval and execution request. Update only the state line of `STAGE7_DEMO_SCENARIO_PRD.md` to record approval and authorized execution. Output: the PRD body stays the accepted contract.

S-2. Input: PRD FR-1 - FR-10, the closed shape, the supporting draft, F-4 and F-11. Create `docs/demo/scenario.md` with: document state; authorities and reading instructions; prerequisite checklist; nine timed scenes numbered 1 - 9; sample facts S-1 - S-8; map-data requirements O-1 - O-4 with unverified states; safe hosted rehearsal; local confirmation rehearsal; local unavailable-routing exercise; early-vote recovery by the server owner; limitations; handover; and a result-record format. Output: one runbook whose scene durations total 160 seconds, whose S-5 starts at 1.5 and whose sample content and placement requirements match the approved shape. S-6 - S-8 add no timed scene. PRD AC-1, AC-5 and the documentary parts of AC-6, AC-11 and AC-14 can be settled from this artifact.

S-3. Input: the current working tree and local environment, F-5 - F-12 and PRD FR-11. Record the readiness measurement in `STAGE7_DEMO_SCENARIO_REVIEW.md`, including the delivered routers, missing operations and loaders, prerequisite checks, local containers, available test tools and missing runtime address. Output: an explicit record of which scene checks are unavailable and why, without claiming a failure of a separately hosted deployment. Recheck if the user supplies a ready environment or another session delivers the required code during the work.

S-4. Input: the runbook and a positively identified environment satisfying D-4. On hosted, run scenes 1 - 6 without a vote and record their observed outcomes; the hosted contribution remains for the pitch. On local, run the remaining read-only scene, the confirmation exercise and the unavailable-routing exercise, restoring only local routing afterwards. Output: actual observations against PRD AC-2 - AC-4, AC-6 - AC-10 and AC-12, with sanitized evidence; unperformed checks stay explicitly unperformed. AC-13 is conditional on an early hosted write and belongs to human restoration. AC-16 remains open until the real hosted contribution and full demonstration occur.

S-5. Input: the runbook, actual outcomes and PRD FR-9 and FR-12. In `STAGE7_DEMO_SCENARIO_REVIEW.md`, map all sixteen acceptance criteria to documentary evidence, runtime evidence or unmet dependencies; record the prepared handover and each recipient's acceptance as pending unless actually received. Output: Rafał can assess checks 7.2 and 7.3 from a truthful result record; no checklist box is checked by this initiative merely because the documentation exists.

S-6. Input: all touched Markdown files. Run D-7's checks and the `implementation-dod-review` skill. Append the report to `STAGE7_DEMO_SCENARIO_REVIEW.md` with every mapped standard assigned a verification status, the actual command outcomes and a verdict naming its scope. Output: documentation quality is assessed, remaining runtime work is visible, and the initiative remains active until its full acceptance criteria pass.

## Rollout order

1. Recheck the shape, approved PRD, current revision and cited product rules. S-1 records the already-given approval.
2. S-2, then S-3. These steps do not wait for runtime delivery by other initiatives.
3. S-4 only for environments meeting D-4. Missing inputs leave the relevant runtime steps pending while documentation work continues.
4. S-5 and S-6. Re-read changed files and the app factory before closing the current run record.

Human steps: provide a ready local or hosted runtime address outside the repository; Mateusz verifies real placements and delivers sample data; the delivered application environment supplies its local routing stop/start commands; the presenter casts the hosted demonstration vote at the pitch; the server owner alone restores hosted data if an early vote changed it; Rafał confirms the checklist results. Video and deck choices and any HarmonyOS alignment stay with Adrian and Kuber. Commits and publication are human work.

## Definition of Done

- The canonical scenario and handover meet the approved PRD, preserve the original seed and draft, and introduce no product rule.
- The touched Markdown passes Prettier and the mapped documentation gates, or unrelated baseline failures are reported separately with their paths.
- Every PRD acceptance criterion has a result and evidence, or an explicit unmet prerequisite. A missing runtime result does not count as a pass.
- The whole initiative is complete only when the required hosted run, its contribution and the separate local unavailable-routing exercise have actually been verified and the review gives a ready verdict for that whole scope.
- No target address, credential or identifying request data enters repository artifacts, no hosted rehearsal vote is cast by the agent, and no hosted data or routing is reset or stopped.

## Risks

- Missing community-fact operations, sample data and full-demo configuration prevent the current local end-to-end run. A separate deployment may differ and requires its own check.
- Unverified map-data items can invalidate the default destination and sample placements. Only Mateusz's verified copy can settle them.
- A shared IP and User-Agent or an early vote can consume the demonstration identity's daily limit. A fresh browser alone is not proof of a new backend identity.
- The local routing-unavailable exercise cannot start safely without a positively identified local container and delivered stop/start commands.
- The default frontend development proxy serves mock answers, which cannot prove runtime acceptance.
- Parallel sessions can change the application or documentation during the work. Re-read the evidence files before recording a verdict.

## Open questions

None. Runtime addresses, loaded data, verified placements, local routing commands and recipient acceptance are execution prerequisites with explicit pending outcomes, not unresolved product or implementation contracts. No step invents them.

## Supplementary files

- `STAGE7_DEMO_SCENARIO_SHAPE.md`, `STAGE7_DEMO_SCENARIO_PRD.md` and the supporting `STAGE7_DEMO_SCENARIO_DRAFT.md`.
- `docs/product/specification.md`, M1, M2, M4 and M6 - M10; `docs/product/views.md`, V-2 - V-6, V-8, V-9 and V-13; `docs/product/interface_texts.md`, the scene text keys.
- `docs/product/api_contract.md`, the operations named by F-10; `mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets`, the sample content.
- `FINAL_CHECKLIST.md`, checks 3.3, 6.1, 6.2, 6.5 and 7.1 - 7.3; `plans_finished/mvp/MVP_PRD.md`, the mapped MVP criteria; `docs/hackathon/challenge_requirements.md`, Validation during the presentation.
- `docs/deployment/hosted_demo.md`, Loading the data and Known limits of the hosted demo; `AGENTS.md`, Target environment.
- `docs/standards/standard_agent_docs.md`, artifact formats; `docs/standards/standard_formatting.md`; `docs/standards/standard_review.md`; `docs/standards/standard_tests.md`; `docs/standards/standard_agentic_workflow.md`, ch. 4.6 and 4.7.
