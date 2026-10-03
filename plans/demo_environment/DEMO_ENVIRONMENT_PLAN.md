# Plan: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03, plan in progress

## Goal

Implement FR-1 - FR-4 and AC-1 - AC-4 of `plans/demo_environment/DEMO_ENVIRONMENT_PRD.md`: record the choice of the hosting for the MVP demo, write the three permission levels of the agent into the rules of the repository, move the registry entry to the resolved section and close Q-7 of the MVP plan, and extend FR-20 and AC-19 of the MVP PRD with the deletion of the demo.

## Facts

F-1. The section Target environment of both agent rule files says the environment is not chosen yet and leaves two permission levels as "defined together with the target environment". | doc:`CLAUDE.md` lines 56-64; doc:`AGENTS.md` lines 56-64 | 2026-10-03
F-2. `CLAUDE.md` and `AGENTS.md` must stay identical apart from the tool name, and an architecture test enforces it. | code:`tests/architecture/test_agent_docs_parity.py:169`; code:`tests/architecture/test_agent_docs_parity.py:21` | 2026-10-03
F-3. The registry entry Target environment for the demo is open, and an entry leaves the open list only when the decision has landed where people look for it, moving to the resolved section with one sentence. | doc:`docs/standards/decision_registry.md` lines 17 and 58-63; doc:`docs/standards/decision_registry.md` line 65 | 2026-10-03
F-4. Q-7 of the MVP plan waits for this initiative, and Q-11, the backend architecture with the worker, depends on Q-1, Q-2 and Q-7. | doc:`plans/mvp/MVP_PLAN.md` lines 49 and 57 | 2026-10-03
F-5. The MVP PRD states FR-20 and AC-19 without the deletion of the demo, and its dependencies still call the target environment an open entry. | doc:`plans/mvp/MVP_PRD.md` lines 67, 107 and 125 | 2026-10-03
F-6. The README says the target environment waits for the stack decision. | doc:`README.md` line 41 | 2026-10-03
F-7. A change to the rules of the repository is recorded in the log of `AI_WORKFLOW.md`, newest entry last. | doc:`CLAUDE.md` line 119; doc:`AI_WORKFLOW.md` lines 7 and 58 | 2026-10-03
F-8. The initiatives of the routing engine and of the frontend are still in the interview, each with an open blocking question. | cmd:`Select-String -Path plans/*/*_SHAPE.md -Pattern '^Document state'` -> `interview in progress` for `ROUTING_ENGINE_SHAPE.md` and `FRONTEND_STACK_SHAPE.md`; doc:`plans/routing_engine/ROUTING_ENGINE_SHAPE.md` line 64; doc:`plans/frontend_stack/FRONTEND_STACK_SHAPE.md` line 66 | 2026-10-03
F-9. No product code exists; the only tests are the architecture tests. | cmd:`Get-ChildItem tests -Recurse -File` -> only `tests/architecture/` and two `__init__.py`; doc:`plans/mvp/MVP_PLAN.md` line 13 | 2026-10-03
F-10. The hook for dangerous commands blocks destructive local commands and `git commit` and `git push`, and has no rule for any hosting provider. | code:`.claude/hooks/block_dangerous_commands.py:7`; code:`.claude/hooks/block_dangerous_commands.py:14` | 2026-10-03
F-11. The architecture tests pass on the tree before this change. | cmd:`venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `112 passed, 2 skipped` | 2026-10-03

## Decisions

D-1. The task is split: the deployment configuration with instructions, the secure connection and the unavailable source in the live demo moved to the task `DEPLOYMENT` of this initiative. Decided by the user on 2026-10-03 in phase B, against moving them to `plans/mvp/` and against one plan waiting for Q-10 of the MVP plan.

D-2. The demo runs on a virtual private server a member of the team already has. Stated by the user on 2026-10-03, in answer to what the team already has to run the demo on.

D-3. The server also runs other services of its owner. The hosted demo environment of the permission levels is therefore only the services and the database of the demo on that server, and their logs; every other service, file and log on the server is forbidden to the agent unconditionally, even on explicit request. Deleting the hosted service and its database means removing the services and the database of the demo, never the server. Decided by the user on 2026-10-03.

D-4. The server belongs to the db person of the team, who already pays for it, so the demo adds no hosting cost. The owner of the repository, who deletes the demo on 4 October 2026 (`DEMO_ENVIRONMENT_PRD.md`, section Domain rules), gets access to that server enough to remove the services and the database of the demo when the environment is stood up. Stated by the user on 2026-10-03.

## Scope of changes

## Rollout order

## Definition of Done

## Risks

- The deadline of 22:00 on 3 October 2026 for the choice holds only if the routing engine and the frontend are decided earlier that evening, or the hosting is chosen in a form that carries every variant they still consider (F-8).
- This initiative and other sessions work on one tree at the same time: on 2026-10-03 the shapes of `plans/account_sessions/` and `plans/geocoding/` were changed by other sessions. The files this plan changes outside `plans/demo_environment/` - `CLAUDE.md`, `AGENTS.md`, `README.md`, `AI_WORKFLOW.md`, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md` - are shared, so each is read again right before it is edited.

## Open questions

- Q-1. Whether the server of D-2 carries every variant the routing engine and the frontend still consider (F-8), and allows a secure connection. Asked of the user on 2026-10-03, waiting for the db person: how much free memory and free disk space the server has after the other services of its owner, and whether a domain or subdomain can point at it (yes or no only, because no address or host enters the repository). The variants to carry: a pedestrian graph of Kraków in the memory of the backend, pgRouting in the PostGIS database of the demo, or an external Valhalla instance; a static frontend or one rendered on the server; PostgreSQL with PostGIS, the worker, and the OpenStreetMap extract of Małopolska. For the OpenStreetMap copy, `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` measured on 2026-10-03 on the machine of the agent's session a download of 202 232 967 bytes in 57 seconds, all passes of the import over it in 297 - 377 seconds with a peak working set of 980 MB, and a cut copy of 26 803 150 bytes (F-4, F-10, F-11 there); the downloaded file is deleted after each run (D-14 there), and the server, or the team machine Q-11 chooses, needs to reach `download.geofabrik.de` over HTTPS.

## Supplementary files

- `plans/demo_environment/DEMO_ENVIRONMENT_PRD.md`, the contract this plan implements.
- `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, the decisions of the interview.
- `plans/demo_environment/DEPLOYMENT_SEED.md` and `plans/demo_environment/DEPLOYMENT_SHAPE.md`, the task split out of this one.
