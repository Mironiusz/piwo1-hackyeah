# Plan: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-04, plan closed

## Goal

Deliver `DEPLOYMENT_PRD.md` in two parts. FR-1 - FR-4 become written instructions for standing the hosted demo up, in a new document `docs/deployment/hosted_demo.md`. The task `DEPLOYMENT_CONFIG` of this initiative completes their exact commands once its files exist. FR-5 rewrites the records of the hosting and the rules of the agent to the server of the user in a data centre. No code, no configuration file and no archived document is changed.

## Facts

F-1. No product code and no deployment file exist: the tree holds no `api/`, `service/`, `data/`, `worker/`, `frontend/` or Compose file; the only new directory is `valhalla/`, with the image definition of the routing service and its two patches. | cmd:`git ls-tree -d --name-only HEAD` -> `.agents .cache .claude .codex .impeccable .vscode agent_docs docs plans plans_finished tests valhalla`; cmd:`ls valhalla` -> `Dockerfile multimodal-exclusions.patch README.md stop-accessibility.patch` | 2026-10-04
F-2. `CLAUDE.md`, section Target environment, describes "a virtual private server of a member of the team, decided in `plans_finished/demo_environment/`", which "also runs other services of its owner". | doc:`CLAUDE.md` line 58 | 2026-10-04
F-3. `AGENTS.md` carries the same paragraph, and the parity test requires both files to be identical except for the tool name. | doc:`AGENTS.md` line 58; code:`tests/architecture/test_agent_docs_parity.py:165` | 2026-10-04
F-4. The resolved entry Target environment for the demo of the decision registry says the demo is "reached at its IP address over a secure connection" and points to D-8 and D-10. | doc:`docs/standards/decision_registry.md` line 78 | 2026-10-04
F-5. D-10 of the MVP plan names the virtual private server of the db person, "over a secure connection", and says "the secure connection and the unreachable routing of the live demo are built by the task `DEPLOYMENT`". | doc:`plans/mvp/MVP_PLAN.md` line 43 | 2026-10-04
F-6. D-8 of the archived demo environment plan chooses the virtual private server of the db person. | doc:`plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` line 42 | 2026-10-04
F-7. The `_PLAN.md` of an archived initiative changes only in the location of references, never in the content of its findings. | doc:`docs/standards/standard_agentic_workflow.md` ch. 4.6, paragraph Protecting history | 2026-10-04
F-8. `AI_WORKFLOW.md` keeps a dated log under `## Log`. Each entry is a `###` heading with the date and a title, followed by the items Tools, Request, What was done, Why and an optional Note. The entry of 2026-10-03 on the agent permissions describes the old server. | doc:`AI_WORKFLOW.md` lines 59, 95-101 | 2026-10-04
F-9. The memory entry of 2026-10-03 on the hosted demo describes the old server and the open question of ports 80 and 443. Memory entries are not rewritten. | doc:`agent_docs/memory/_cross_cutting.md` lines 39-44; doc:`docs/standards/standard_agentic_workflow.md` ch. 4.6, paragraph Protecting history | 2026-10-04
F-10. The standards map lists project documents outside the standards and says the project adds its own documents, such as operational knowledge about the environment, to the table What to open before a task. | doc:`docs/standards/README.md` lines 50-56, 98 | 2026-10-04
F-11. The environment entries live in three templates. The target environment gets one set of variables. No entry exists yet. | doc:`docs/standards/standard_config.md` lines 32, 40, 50 | 2026-10-04
F-12. Consent to apply a revision to the database of the target environment is given at call time and has no environment entry. | doc:`docs/standards/standard_config.md` line 52 | 2026-10-04
F-13. No address, host, login or secret of the target environment enters the repository in any form. | doc:`docs/standards/standard_config.md` line 67; doc:`CLAUDE.md` line 66 | 2026-10-04
F-14. After the first deployment one address search from the hosted service is checked to return a list. When the outside service does not answer, the app shows a search unavailable message that differs from the nothing found message. | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` D-16; doc:`plans_finished/geocoding/GEOCODING_PRD.md` line 45 | 2026-10-04
F-15. The prose check forbids typographic dashes, quotation marks, arrows and bold in prose in every `.md` file, `plans_finished/` included. Prettier checks markdown outside `plans_finished/`. | code:`tests/architecture/test_prose_style.py:38`; doc:`.prettierignore` line 1; doc:`makefile` target `lint-docs` | 2026-10-04
F-16. Neither pytest nor the local prettier is installed on the machine of this session, so the checks of F-15 and F-3 cannot run here. | cmd:`python3 -m pytest` -> `No module named pytest`; cmd:`ls node_modules/.bin/prettier` -> `No such file or directory` | 2026-10-04
F-17. `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md` and `plans_finished/valhalla_routing/` already describe the server of the user with 16 GB and 16 cores, and the former leaves the rewrite of D-10 to this task; both are edited by other sessions, and this task does not touch them. | doc:`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md` lines 25, 50; doc:`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md` line 139 | 2026-10-04
F-18. The routing data of Valhalla is built by the import run together with the copy, and a fresh copy is served only after the routing service has been restarted on its routing data; until then every route request ends with `routing_unavailable`. How the service is pointed at new data is for item 3 of `plans_finished/backend_architecture/`, and this task runs the service with its data. | doc:`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-2, D-3, D-13, D-14 | 2026-10-04

## Decisions

D-1. The instructions live in a new document, `docs/deployment/hosted_demo.md`. It gets an item in the list Project documents outside the standards and a row in the table What to open before a task of `docs/standards/README.md` (F-10). The task `DEPLOYMENT_CONFIG` edits the same document. Agent decision at C:40, without asking: the instructions are permanent documentation of the project, not an artifact of the initiative, and the map already provides for such documents.

D-2. Every step whose exact command, file name, port or version depends on the files of the configuration ends with one sentence: "Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`." The instructions guess no command, file name or port. Agent decision at C:40, without asking: it follows from FR-1 and AC-1 of the PRD and from the ban on guessing a contract.

D-3. The instructions name no branch or commit. They speak of "the version of the repository the team chose to deploy". Decided by the user on 2026-10-04: the choice is not the agent's.

D-4. Applying the schema revisions is a step of its own, between the start and the loading of the data. It is run by hand, with the consent given at call time, and the start command never applies revisions (F-12). Agent decision at C:40, without asking: the standard already requires consent at call time for the target environment, so folding the revisions into the start would bypass that gate.

D-5. The archived `plans_finished/demo_environment/` is not changed. D-10 of `plans/mvp/MVP_PLAN.md`, the decision registry and `CLAUDE.md` with `AGENTS.md` say that D-8 there is superseded (F-7). Decided by the user on 2026-10-04 in phase B.

D-6. The existing entries of `AI_WORKFLOW.md` and `agent_docs/memory/_cross_cutting.md` stay as they are. Each file gets a new entry that names the entry of 2026-10-03 it supersedes (F-8, F-9). Agent decision at C:40, without asking: both files are dated logs, and rewriting an old entry would erase the history they exist to keep.

D-7. `CLAUDE.md` and `AGENTS.md` change only in the first paragraph of the section Target environment. The three permission levels, the paragraph on access outside the demo and the paragraph on the ban of addresses stay word for word (AC-5). Agent decision at C:40, without asking: FR-5 says the permission levels do not change.

D-8. Other sessions edit `plans/mvp/MVP_PLAN.md`, `plans_finished/backend_architecture/` and `plans_finished/valhalla_routing/` in parallel (F-17). Before each edit, step 2 of Rollout order checks `git status` and the modification time of the file, according to `docs/standards/standard_agentic_workflow.md` ch. 4.7. Only D-10 of the MVP plan is changed. The other two initiatives are not touched. Agent decision at C:40, without asking: on 2026-10-04 the user decided that this task rewrites D-10 and that `plans_finished/backend_architecture/` only refers to it.

## Scope of changes

1. `CLAUDE.md` and `AGENTS.md`, section Target environment, first paragraph (F-2, F-3, D-7). The paragraph becomes, identical in both files:

   "The target environment is the hosted demo of the MVP on a server of a member of the team in a data centre, decided in `plans_finished/deployment/`, which supersedes `plans_finished/demo_environment/` D-8. The demo is served over plain HTTP at the address of the server. What else runs on that server is not known, so the hosted demo environment is only the services and the database of the demo on it, and their logs. The owner of the repository deletes the demo and all its data on 4 October 2026, after the results are announced. The permission levels of the agent:"

2. `docs/standards/decision_registry.md`, section Target environment for the demo (F-4). The entry becomes:

   "Resolved on 2026-10-03 by the user, answering for the db person, and changed on 2026-10-04 by the user in `plans_finished/deployment/`. The demo runs on a server of the user in a data centre, reached at its IP address over plain HTTP, and is deleted with all its data on 4 October 2026. The virtual private server of the db person, chosen in `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8, is superseded. The choice lives in `plans_finished/deployment/DEPLOYMENT_PRD.md` FR-5 and `plans/mvp/MVP_PLAN.md` D-10, the permission levels of the agent in `CLAUDE.md` and `AGENTS.md`, section Target environment."

3. `plans/mvp/MVP_PLAN.md`, D-10 only (F-5, D-8). The item becomes:

   "D-10. Where the demo runs, settling the former Q-7. The demo runs on a server of the user in a data centre, with 16 GB of memory and 16 cores, reached at its IP address over plain HTTP. Everything of the demo on the server runs in Docker containers orchestrated by Docker Compose and is started with one command and an environment file kept on the server (`plans_finished/deployment/DEPLOYMENT_SHAPE.md`, sections Current state and Domain rules). It supersedes the virtual private server of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8.

   Constraints for the rest of this plan:
   - Q-11 places on that server the backend process, the worker, PostgreSQL with PostGIS in an instance of its own, the static frontend and the Valhalla routing service of `plans_finished/valhalla_routing/`, and decides whether the import runs there or on a team machine.
   - What else runs on the server is not known, so the demo uses only its own services, database and logs (`CLAUDE.md`, section Target environment).
   - The demo has no secure connection, so the start from the current location of FR-2 of `plans/mvp/MVP_PRD.md` does not work on the hosted link. Nor does the hosted demo provide a way to take routing down (`plans_finished/deployment/DEPLOYMENT_SHAPE.md`, section Out of scope).
   - The deployment configuration is built by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/` once Q-11 and the backend skeleton exist. The written instructions are written by the task `DEPLOYMENT` of `plans_finished/deployment/`.

   Decided by the user, answering for the db person, on 2026-10-03 in `plans_finished/demo_environment/`, and changed by the user on 2026-10-03 and 2026-10-04 in `plans_finished/deployment/`."

4. `AI_WORKFLOW.md`, a new entry at the end of `## Log` (F-8, D-6):

   ```text
   ### 2026-10-04 - Agent permissions on the new demo server

   - Tools: Claude Code with Claude Opus 5.5 in the main session, the `plan-shape`, `plan-prd` and `plan-implement` skills, no subagents.
   - Request, summarized from Polish: move the hosted demo to a server of the user in a data centre and write the instructions for deploying it.
   - What was done: `CLAUDE.md` and `AGENTS.md`, section Target environment, now describe a server of a member of the team in a data centre, served over plain HTTP, of which nothing but the demo is known. The three permission levels of the agent are unchanged. The decision registry and D-10 of `plans/mvp/MVP_PLAN.md` follow it.
   - Why: the user moved the demo off the virtual private server of the db person on 2026-10-03, so the rules described a machine the demo no longer runs on. The levels still fit, because they are narrow enough to be right whatever else runs on the server.
   - Note: supersedes the entry of 2026-10-03, Agent permissions in the hosted demo, which stays as a historical record.
   ```

5. `docs/deployment/hosted_demo.md`, a new document (FR-1 - FR-4, D-1 - D-4). Its title is "# Hosted demo deployment", followed by a state line in the form `Document state: 2026-10-04`. The sections come in this order:
   1. `## What this document covers`. It says who runs the steps (the owner of the server) and that the demo and all its data are deleted on 4 October 2026, after the results, by the owner of the repository. It says that no address, host, login or secret of the server is written here or anywhere in the repository (F-13), and that the agent's permissions are in `CLAUDE.md`, section Target environment.
   2. `## Before the first start`. The server needs Docker Engine with the Compose plugin, and the port of the public link open to the internet, a setting of the host the owner makes. The minimum version and the port are completed by the configuration task (D-2).
   3. `## Getting the repository`. The version of the repository the team chose to deploy (D-3).
   4. `## Environment file`. One file on the server only, never committed. It holds every entry of the templates `.env.example` and `.env.local.example`, whose meaning is in `docs/standards/standard_config.md`, section Environment entries (F-11). The file name and how the start command reads it are completed by the configuration task (D-2).
   5. `## Starting the demo`. The one command (D-2). It starts every service of the demo. It never applies a schema revision and never loads, replaces or deletes data.
   6. `## Applying the schema revisions`. A step of its own, run by hand, with the consent given at call time, after the first start and after every update that brings a new revision (D-4, F-12). The command is completed by the configuration task (D-2).
   7. `## Loading the data`. The separate loading program loads the OpenStreetMap copy, the tile archive and the sample reports. It is run by hand after the revisions and never by the start. It has finished when the program ends without an error and the map of Kraków shows at the public link. It is not repeated after a restart. The command is completed by the configuration task (D-2).
   8. `## Restarting after a fix`. The same start command keeps every report, vote, account and loaded copy. The revisions step is run again only if the fix brings a new revision, and the loading step is not run again.
   9. `## Emptying the database`. A separate step, run on purpose, which destroys every report, vote, account and the loaded copy. Afterwards the revisions and the loading steps are run again. The start command never runs it. The command is completed by the configuration task (D-2).
   10. `## Check before the link goes into the submission`, the last section. It holds four points: the link opens on a phone, the map shows, a walking route is planned between two addresses, and one address search returns a list (F-14). When the search shows the search unavailable message instead, the public address search is refused from the server. Start and destination can still be picked on the map, and the team decides what to say in the submission before 10:00.
   11. `## Known limits of the hosted demo`, after the check as a reference list. The page is served over plain HTTP, so the browser marks it as not secure and gives it no current location, so the start is picked from an address or the map. Passwords and session tokens travel unencrypted. Routing is not taken down during the live demo.

6. `docs/standards/README.md` (F-10, D-1). In the list Project documents outside the standards, a new item after `docs/hackathon/`: "`docs/deployment/` - `hosted_demo.md`, the written instructions for standing the hosted demo up on the server, written on 2026-10-04 by `plans_finished/deployment/`, with the commands completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`." In the table What to open before a task, a new last row: task type "Deploying, restarting or checking the hosted demo", documents "`docs/deployment/hosted_demo.md` and `CLAUDE.md`, section Target environment". The table is realigned by prettier.

7. `agent_docs/memory/_cross_cutting.md`, a new entry at the end, in the template of `docs/standards/standard_agent_docs.md`, section agent_docs/memory entry format. Title: "2026-10-04 - Hosted demo moved to a server of the user, plain HTTP (plans/deployment)". It names the entry of 2026-10-03, Hosted demo on a shared server without a domain, as superseded in its server, its secure connection and its open question of ports, and keeps that entry untouched (D-6).

## Rollout order

1. Check that the facts still hold: `git log --since=2026-10-04 --name-only` intersected with the files cited in Facts, and the content under every hit.
2. Before each edit of `CLAUDE.md`, `AGENTS.md` and `plans/mvp/MVP_PLAN.md`, check `git status` and the modification time of the file (D-8).
3. Steps 1 - 4 of Scope of changes (FR-5). `CLAUDE.md` and `AGENTS.md` are edited in one step, so the parity test never sees them apart.
4. Steps 5 and 6 of Scope of changes (FR-1 - FR-4).
5. Step 7 of Scope of changes, at the end of `plan-implement`.
6. Checks:
   - the forbidden-character and bold scan of every changed file, run with the code points of `tests/architecture/test_prose_style.py`;
   - `git diff --name-only` shows nothing under `plans_finished/`;
   - a search of the changed files for an IPv4 or IPv6 address, a host name or a login finds none;
   - a comparison of `CLAUDE.md` and `AGENTS.md` after replacing the tool names shows only the expected difference.

Steps for a human:

- Run `make check` on a machine with the development dependencies installed (F-16): the parity test, the prose test and prettier.
- Commit, push and the Merge Request.

## Definition of Done

- AC-1 - AC-4 of `DEPLOYMENT_PRD.md`:
  - `docs/deployment/hosted_demo.md` has the sections of step 5 in that order;
  - every step that waits for the configuration ends with the sentence of D-2;
  - no command, file name, port or version is guessed.
- AC-5 of `DEPLOYMENT_PRD.md`:
  - the texts of steps 1 - 4 stand in their files;
  - the permission levels are unchanged;
  - nothing under `plans_finished/` changed.
- `make check` passes, run by a human per F-16. Until then the checks of step 6 of Rollout order stand in for it, and the review records that.
- `docs/standards/standard_review.md`, Definition of Done, for documentation changes.

## Risks

- The instructions are written before the files they drive. If the configuration task makes a different start sequence, for example folding the revisions into the start, it changes this document and D-4 together, not around them.
- `CLAUDE.md` is read by every session at its start. A session already running keeps the old paragraph until it restarts.
- Other sessions edit `plans/mvp/MVP_PLAN.md` in parallel. A conflicting edit of D-10 is resolved by D-8 and the user's decision of 2026-10-04, not by overwriting.
- The checks of F-15 cannot run on this machine (F-16). A formatting error is found only by `make check` on another machine.

## Open questions

None.

## Supplementary files

None.
