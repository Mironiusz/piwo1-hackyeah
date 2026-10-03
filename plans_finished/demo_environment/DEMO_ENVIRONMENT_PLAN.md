# Plan: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03, plan closed

## Goal

Implement FR-1 - FR-4 and AC-1 - AC-4 of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`: record the choice of the hosting for the MVP demo, write the three permission levels of the agent into the rules of the repository, move the registry entry to the resolved section and close Q-7 of the MVP plan, and extend FR-20 and AC-19 of the MVP PRD with the deletion of the demo.

## Facts

F-1. Until step 1 of this plan the section Target environment of both agent rule files said the environment is not chosen yet and left two permission levels as "defined together with the target environment". | doc:`CLAUDE.md` lines 56-66; doc:`AGENTS.md` lines 56-66 | 2026-10-03
F-2. `CLAUDE.md` and `AGENTS.md` must stay identical apart from the tool name, and an architecture test enforces it. | code:`tests/architecture/test_agent_docs_parity.py:169`; code:`tests/architecture/test_agent_docs_parity.py:21` | 2026-10-03
F-3. The registry entry Target environment for the demo is open, and an entry leaves the open list only when the decision has landed where people look for it, moving to the resolved section with one sentence. | doc:`docs/standards/decision_registry.md` lines 17 and 58-63; doc:`docs/standards/decision_registry.md` line 65 | 2026-10-03
F-4. Q-7 of the MVP plan waits for this initiative, Q-11, the backend architecture with the worker, depends on D-9 (the former Q-1, the routing engine), D-4 (the former Q-2, the source of the OpenStreetMap data) and Q-7, and Q-7 is also named in Q-10 and in the item of Risks on the order of the open questions. | doc:`plans/mvp/MVP_PLAN.md` section Open questions, items Q-7, Q-10 and Q-11; doc:`plans/mvp/MVP_PLAN.md` section Risks, item The open questions depend on each other | 2026-10-03
F-5. The MVP PRD stated FR-20 and AC-19 without the deletion of the demo until step 5 of this plan, and its dependencies still call the target environment an open entry. | doc:`plans/mvp/MVP_PRD.md` lines 67, 107 and 129 | 2026-10-03
F-6. Until step 2 of this plan the README said the target environment waits for the stack decision. | doc:`README.md` line 41 | 2026-10-03
F-7. A change to the rules of the repository is recorded in the log of `AI_WORKFLOW.md`, newest entry last. | doc:`CLAUDE.md` line 121; doc:`AI_WORKFLOW.md` lines 7 and 59 | 2026-10-03
F-8. The routing engine was decided on 2026-10-03: a graph of the pedestrian network in the memory of the one backend process, with no routing service of its own and none outside the project, at a measured peak working set of 255 MB; the frontend was decided on 2026-10-03: static files, about 50 MB with a tile archive read in byte ranges, served from the same host as the programming interface. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` line 3 `plan closed`, D-1, D-13 and F-26; doc:`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-3 and D-13 | 2026-10-03
F-9. No product code exists; the only tests are the architecture tests. | cmd:`Get-ChildItem tests -Recurse -File` -> only `tests/architecture/` and two `__init__.py`; doc:`plans/mvp/MVP_PLAN.md` line 13 | 2026-10-03
F-10. The hook for dangerous commands blocks destructive local commands and `git commit` and `git push`, and has no rule for any hosting provider. | code:`.claude/hooks/block_dangerous_commands.py:7`; code:`.claude/hooks/block_dangerous_commands.py:14` | 2026-10-03
F-11. The architecture tests pass on the tree before this change. | cmd:`venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `112 passed, 2 skipped` | 2026-10-03
F-12. Let's Encrypt issues certificates for IPv4 and IPv6 addresses, generally available since 2026-01-15, only in the shortlived profile, valid for 160 hours, and validated only with the http-01 or tls-alpn-01 challenge, never dns-01. | cmd:`WebFetch https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability` -> `Short-lived and IP address certificates are now generally available`, `valid for 160 hours`, `Let's Encrypt supports both IPv4 and IPv6`; cmd:`WebFetch https://letsencrypt.org/2025/07/01/issuing-our-first-ip-address-certificate.html` -> `only the http-01 and tls-alpn-01 methods can be used`, `request the shortlived profile` | 2026-10-03
F-13. The http-01 challenge is answered on TCP port 80 and the tls-alpn-01 challenge on TCP port 443 of the validated address. | doc:`RFC 8555` section 8.3; doc:`RFC 8737` section 3 | 2026-10-03
F-14. The import of the OpenStreetMap copy peaked at a working set of 980 MB on the machine of the agent's session, its downloaded file of 202 232 967 bytes is deleted after each run, and the cut copy has 26 803 150 bytes. | doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` F-10, F-11 and D-14 | 2026-10-03

## Decisions

D-1. The task is split: the deployment configuration with instructions, the secure connection and the unavailable source in the live demo moved to the task `DEPLOYMENT` of this initiative. Decided by the user on 2026-10-03 in phase B, against moving them to `plans/mvp/` and against one plan waiting for Q-11 of the MVP plan.

D-2. The demo runs on a virtual private server a member of the team already has. Stated by the user on 2026-10-03, in answer to what the team already has to run the demo on.

D-3. The server also runs other services of its owner. The hosted demo environment of the permission levels is therefore only the services and the database of the demo on that server, and their logs; every other service, file and log on the server is forbidden to the agent unconditionally, even on explicit request. Deleting the hosted service and its database means removing the services and the database of the demo, never the server. Decided by the user on 2026-10-03.

D-4. The server belongs to the db person of the team, who already pays for it, so the demo adds no hosting cost. The owner of the repository, who deletes the demo on 4 October 2026 (`DEMO_ENVIRONMENT_PRD.md`, section Domain rules), gets access to that server enough to remove the services and the database of the demo when the environment is stood up. Stated by the user on 2026-10-03.

D-5. The three permission levels are enforced only by the rules of the repository; the hook for dangerous commands (F-10) gets no rule for the hosted demo environment. Decided by the user on 2026-10-03 in the implementation phase, against also blocking the forbidden actions in the hook.

D-6. The user confirmed on 2026-10-03, in the implementation phase, the extension of FR-20 and AC-19 of `plans/mvp/MVP_PRD.md` with the statement that the demo and all its data are deleted on 4 October 2026, as FR-4 of `DEMO_ENVIRONMENT_PRD.md` requires.

D-7. The rollout is split while Q-1 is open: FR-2 and FR-4 are implemented now, FR-1 and FR-3 after the db person answers Q-1, and the initiative stays in `plans/` until then. Decided by the user on 2026-10-03 in the implementation phase, against recording the choice with minimum requirements checked only at the first deployment.

D-8. The hosting of the demo, settling Q-1. The demo runs on the virtual private server of D-2, reached at the IP address of the server; the team may buy a domain for it later. Stated by the user on 2026-10-03 for the db person: after the other services of its owner the server has 4 GB of free memory, 64 GB of free disk and 4 cores, and no domain or subdomain points at it.

- Reason: the team already has the server, and its free resources carry the demo. The one backend process with the route graph peaked at 255 MB and the static frontend takes about 50 MB of disk (F-8); the import of the OpenStreetMap copy peaked at 980 MB, and its download of about 200 MB is deleted after each run (F-14). With the import on this server the two leave about 2.8 GB of memory for PostgreSQL with PostGIS, which was not measured, and the demo needs a few GB of the 64 GB of disk.
- Cost: none added, the db person already pays for the server (D-4).
- Secure connection: without a domain the public link is served over HTTPS with a Let's Encrypt certificate for the IP address of the server (F-12), valid for 160 hours, longer than the demo lives, and validated through port 80 or 443 of the server (F-13). Whether these ports are free of the other services of the owner is not known, so the task `DEPLOYMENT` chooses between the demo answering on them itself and a proxy of the owner that only the db person configures (D-3). A domain bought later takes an ordinary certificate instead.
- Unreachable routing: the services and the database of the demo on this server are under the control of the team, so during the live demo the team can cause one of the failures after which routing stops answering (`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-3, D-13) and undo it; which one and how is requirement 3 of `plans/deployment/DEPLOYMENT_SHAPE.md`.
- Checks left to the first deployment, as the plans that set them decided: one route across Kraków in at most 5 seconds (`plans_finished/routing_engine/`), one address search from the server (`plans_finished/geocoding/GEOCODING_PLAN.md` D-15, D-16), and reaching `download.geofabrik.de` over HTTPS unless Q-11 of `plans/mvp/MVP_PLAN.md` runs the import on a team machine.

Decided by the user on 2026-10-03 in the implementation phase. The choice between the ports of the server and a proxy of the owner was left to the task `DEPLOYMENT` by the user on the same day, because the db person does not know whether the ports are free.

## Scope of changes

1. `CLAUDE.md` and `AGENTS.md`, section Target environment (FR-2, AC-2, F-1, F-2): the first paragraph and the three items are replaced with the same text in both files. It names the target environment as the hosted demo on the server of D-2, limited to the services and the database of the demo and their logs (D-3), deleted on 4 October 2026 by the owner of the repository, and gives the three levels of the section Domain rules of the PRD, with every other service, file and log on that server added to the forbidden level (D-3). Outside the hosted demo environment the agent keeps no access to any target environment, and challenge submissions stay with a human. The last paragraph, on addresses, hosts, logins and secrets, stays unchanged.
2. `README.md` line 41 (F-6): the clause saying that the target environment waits for the stack decision is replaced with one saying that the permission levels for the target environment were filled in on 2026-10-03 from `plans_finished/demo_environment/`.
3. `AI_WORKFLOW.md`, section Log (F-7): one entry at the end, recording the change of the rules for the agent and its reason.
4. `docs/standards/decision_registry.md`, entry Target environment for the demo, item Blocks: the routing engine is no longer named as a blocker (F-8), the permission levels are recorded as filled in ahead of the choice by D-7, and Q-1 stays the only blocker. The entry stays open until step 6.
5. `plans/mvp/MVP_PRD.md` (FR-4, AC-4, F-5, D-6): FR-20 and AC-19 require, in the hosted demo, the statement in Polish and English that the demo and all its data are deleted on 4 October 2026, after the results are announced, and a new item at the end of the section Domain rules records that the change comes from this initiative and was confirmed by the user on 2026-10-03.
6. After Q-1 (FR-1, FR-3, AC-1, AC-3): a decision of this plan records the choice of the hosting with its reason, its cost, how it carries the routing engine and the frontend (F-8), and how it allows a secure connection and an unreachable routing; the registry entry moves to the resolved section with one sentence; Q-7 of `plans/mvp/MVP_PLAN.md` is closed by a decision with the next free number that points to this initiative, and the items that name Q-7 as open (F-4) are adapted; the item of the section Dependencies of `plans/mvp/MVP_PRD.md` on the target environment (F-5) says it is decided.

## Rollout order

1. Steps 1 - 4, each file read again right before it is edited (section Risks).
2. Step 5 once the merge session releases `plans/mvp/MVP_PRD.md`.
3. The architecture tests, with an unexpected red checked against the work of other sessions (`docs/standards/standard_agentic_workflow.md` ch. 4.7).
4. Step 6 once Q-1 is answered, and in `plans/mvp/MVP_PLAN.md` only after the routing engine session has added its decision there; then the architecture tests again.

## Definition of Done

- AC-2: both rule files carry the same three levels, the parity test passes, and neither contains the phrase "defined together with the target environment".
- AC-4: FR-20 and AC-19 of `plans/mvp/MVP_PRD.md` require the statement about the deletion in both languages, and the PRD records the origin of the change and the confirmation of the user.
- AC-1 and AC-3, after Q-1: the decision of step 6 covers every point of AC-1, the registry entry is only in the resolved section, and Q-7 points to this initiative as decided.
- No changed file names an address, host, login or secret of the hosting.
- The architecture tests pass, or a red is shown to come from the work in progress of another session.

## Risks

- The deadline of 22:00 on 3 October 2026 for the choice holds only if the routing engine is decided earlier that evening, or the hosting is chosen in a form that carries every variant it still considers; the frontend is already decided (F-8). The routing engine was decided on 2026-10-03 in `plans_finished/routing_engine/` (`plans/mvp/MVP_PLAN.md` D-9).
- This initiative and other sessions work on one tree at the same time: on 2026-10-03 the shapes of `plans/account_sessions/` and `plans_finished/geocoding/` were changed by other sessions. The files this plan changes outside `plans_finished/demo_environment/` - `CLAUDE.md`, `AGENTS.md`, `README.md`, `AI_WORKFLOW.md`, `docs/standards/decision_registry.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md` - are shared, so each is read again right before it is edited.

## Open questions

None. Q-1 was settled on 2026-10-03 as D-8.

## Supplementary files

- `plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`, the contract this plan implements.
- `plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, the decisions of the interview.
- `plans/deployment/DEPLOYMENT_SEED.md` and `plans/deployment/DEPLOYMENT_SHAPE.md`, the task split out of this one.
