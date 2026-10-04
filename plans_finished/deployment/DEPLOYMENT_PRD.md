# PRD: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-04

## Business goal

By 10:00 on 4 October 2026 the repository holds written instructions for standing the MVP demo of `plans/mvp/` up on the user's own server in a data centre. The public link in the Kraków submission, which closes at 11:00, then works on the phones of the jury, and the live demo runs from the same place (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`, Business goal). The deadline leaves one hour before the submission closes to check the link and fix what the check finds.

The instructions describe the steps, their order and what each step leaves behind. The deployment configuration they drive is built by a separate task, decided by the user on 2026-10-04. That task completes the commands of the instructions once its files exist.

This task also brings the rules of the agent and the records of the hosting in line with the server the demo actually runs on. Without that, the permission levels of the agent describe a machine the demo no longer uses.

## Problem and its consequences

The hosted demo has no written instructions. The choice of the hosting was also overturned late on 3 October 2026, when the user moved the demo from the server of the db person to a server of their own. As long as nothing changes:

- Nobody but the author of the configuration knows in which order to start the demo, load its data and check it. The night up to 10:00 is the whole window for the skeleton of the app, the configuration, the first start and the check of the link, and a wrong order costs hours.
- `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8, `plans/mvp/MVP_PLAN.md` D-10 and `CLAUDE.md`, section Target environment, describe the server of the db person, so the agent reads its permissions against the wrong machine. The resolved entry of `docs/standards/decision_registry.md` says the demo is reached over a secure connection, which the user cut.
- If the instructions did not say that a restart keeps the data and that emptying the database is a separate step, a member of the team fixing something at 04:00 could wipe the reports, votes and accounts entered during the check, and the data of the demo would have to be loaded again before 10:00.

## Scope

- Written instructions for standing the demo up on the server, in the order of the steps: what the server needs, the environment file, the start, loading the data by hand, the check, restarts and emptying the database.
- Updating the records of the hosting and the rules of the agent to the server of the user.

## Out of scope

- The deployment configuration itself, moved on 2026-10-04 by the user to a separate task. That task now holds the requirements this PRD carried until then:
  - the configuration started with one command and an environment file;
  - every part of the demo on the server, with the page, the programming interface and the map tiles served from one host, and the backend as exactly one process;
  - a database instance of its own;
  - restarts that keep the data;
  - completing the commands and names that these instructions leave to it.
- A secure connection for the public link. The user cut it on 2026-10-03: the demo is served over plain HTTP, and the user accepted the consequences listed in the shape (`DEPLOYMENT_SHAPE.md`, section Out of scope).
- Making routing stop answering during the live demo. The user cut it on 2026-10-03. The behaviour of the app when routing does not answer, FR-17 of `plans/mvp/MVP_PRD.md`, stays, but it is not shown on the hosted link.
- Changing `docs/product/specification.md` M10 to match that cut, and adding the start from the current location, which does not work over HTTP, to the list of what works and what does not of AC-15 of `plans/mvp/MVP_PRD.md`. Both belong to the specification and to `plans/mvp/`, not to this task.
- The program that loads the data, that is, the import of the OpenStreetMap copy, the tile archive and the sample reports. They are work packages of `plans/mvp/MVP_PLAN.md` (D-4, D-6 there, FR-18 of `plans/mvp/MVP_PRD.md`). The instructions only say when and how to start it.
- The routing service itself and how its data is prepared. Both are decided by `plans_finished/valhalla_routing/` and built by the import and route work packages of `plans/mvp/MVP_PLAN.md` (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-13).
- Standing the demo up and deleting it on 4 October 2026, which are steps of the user and of the owner of the repository, and written instructions for the deletion, which the user cut on 2026-10-03.
- What happens if the skeleton of the app is not ready by 10:00. The user did not state it (Risks and notes).

## Functional requirements

FR-1. Written instructions. The repository holds written instructions with which a member of the team who did not write them stands the whole demo up on the server and opens it at the public link on a phone. The instructions cover four things. First, what the server needs before the first start: the container runtime, and the HTTP port open to the internet, a setting of the host that the user makes as its owner. Second, that the environment file lives only on the server, and where the repository names its entries. Third, the one command that starts the demo. Fourth, what that command does and never does. No address, host, login or secret of the server is in the instructions.

FR-2. Loading the data by hand. The instructions name the step that loads the OpenStreetMap copy, the tile archive and the sample reports with the separate loading program. The user runs that step by hand after the demo is up, never as part of the start. The instructions also say how to tell that the step finished and that it is not repeated after a restart.

FR-3. Restarts and emptying the database. The instructions say that running the start command again, after a fix or after a restart of the server, keeps every report, vote, account and loaded copy. They describe emptying the database as a separate step, run on purpose, together with what it destroys.

FR-4. Check after the first start. The instructions end with a check the team runs before the link goes into the submission: the demo opens at the public link on a phone, the map shows, a walking route is planned between two addresses, and one address search returns a list (`plans_finished/geocoding/GEOCODING_PLAN.md` D-16). They also say what a failed address search means and that the map still works then (`plans_finished/geocoding/GEOCODING_PRD.md` FR-5).

FR-5. Records of the hosting. The records that name the server of the demo describe the server of the user in a data centre, served over plain HTTP:

- D-10 of `plans/mvp/MVP_PLAN.md`, the section Target environment of `CLAUDE.md` and `AGENTS.md`, and the resolved entry of `docs/standards/decision_registry.md` describe the new server, say that D-8 of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` is superseded, and point to this task.
- The archived `plans_finished/demo_environment/` is not changed: its D-8 stays as a historical record (`docs/standards/standard_agentic_workflow.md` ch. 4.6, section Protecting history). Decided by the user on 2026-10-04 in phase B, against a superseding note written into the archived plan.
- The change of a workflow rule is recorded in `AI_WORKFLOW.md`.

None of them names an address, a host or a login. The permission levels of the agent do not change.

## Acceptance criteria

AC-1 (FR-1). The instructions list the prerequisites of the server, the environment file and the start in that order. A search of the repository finds no address, host, login or secret of the server. Every step whose exact command depends on the files of the configuration task names that task as the place where the command is completed. When that task finishes, a member of the team who did not write the instructions follows only them, and the demo opens at the public link on a phone. That walk-through is an acceptance criterion of the configuration task, which owns the files it runs.

AC-2 (FR-2). The loading step comes after the start in the instructions. It says it is run by hand, says how its end is recognized, and says that the start never repeats it.

AC-3 (FR-3). The instructions state that a restart keeps the data, and they describe emptying the database as a separate step that names what is lost.

AC-4 (FR-4). The check is the last section of the instructions. It covers the four points of FR-4 and what to do when the address search fails.

AC-5 (FR-5):

- D-10 of `plans/mvp/MVP_PLAN.md`, the section Target environment of `CLAUDE.md` and `AGENTS.md`, and the resolved entry of `docs/standards/decision_registry.md` describe the server of the user over plain HTTP, name D-8 of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` as superseded and point to this task.
- `git diff` shows no change under `plans_finished/demo_environment/`.
- `AI_WORKFLOW.md` records the change.
- The three permission levels in `CLAUDE.md` and `AGENTS.md` read the same as before, and the two files stay identical except for the tool name.
- None of these files contains an address, a host or a login.

## Domain rules

- The demo is served over plain HTTP at the address of the server, without a certificate. The browser marks the page as not secure and does not give the page the current location, so the start is picked from an address or the map. Passwords and session tokens travel unencrypted. The user accepted all of this on 2026-10-03.
- The hosted demo environment of the agent is only the services, the database and the logs of the demo. Every other service, file and log on the server is forbidden to the agent unconditionally, because what else runs there is not known (`CLAUDE.md`, section Target environment).
- Personal data kept by the demo, its deletion on 4 October 2026 after the results and the person responsible for it are those of `plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, section Domain rules. This task does not change them.
- Secrets and details of the target environment never enter the repository (`docs/standards/standard_config.md`, section Secrets).

## Dependencies and impact on other modules

- The separate configuration task, decided by the user on 2026-10-04. Its files are what the instructions drive, and it completes their exact commands. It needs Q-11 of `plans/mvp/MVP_PLAN.md`, the backend architecture with the worker, and the skeleton of the app.
- `plans_finished/valhalla_routing/` decides the routing service the demo runs. At the time of this PRD it had a PRD and no plan; on 2026-10-04 its plan replaced D-9 of `plans/mvp/MVP_PLAN.md` with one Valhalla service run by the project. What the service needs from the server and what makes it stop answering are D-1 and D-14 of `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md`: the image built by `valhalla/Dockerfile`, on the internal network with no port of the host; at most 2.5 GB of memory; about 60 MB of routing data for walking and about 700 MB with public transport; a build that needs about 2.1 GB and 3.9 GB of memory with public transport; and no answer when the service is down, when its data is of another copy than the copy in use, or after 2 seconds for one call.
- The work packages of `plans/mvp/MVP_PLAN.md` for the import (D-4), the tile archive (D-6) and the sample data (FR-18 of `plans/mvp/MVP_PRD.md`) together make the loading program of FR-2.
- `plans_finished/geocoding/` D-16: the check of an address search after the first deployment.
- `docs/product/specification.md` M10 and AC-15 of `plans/mvp/MVP_PRD.md` have to follow the cuts of this task. That work is outside this task.
- FR-5 changes `CLAUDE.md`, `AGENTS.md`, `AI_WORKFLOW.md`, `docs/standards/decision_registry.md` and `plans/mvp/MVP_PLAN.md`. It does not change the archived `plans_finished/demo_environment/`.
- `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md`, item 3 of its scope, also planned to rewrite D-10 of `plans/mvp/MVP_PLAN.md`. On 2026-10-04 the user decided that this task rewrites D-10 under FR-5, so that initiative only refers to it.

## Risks and notes

- No product code existed at the review of the shape, after 22:00 on 3 October 2026, and Q-11 was open. The instructions are written before the files they drive, so until the configuration task completes their commands they describe the steps but cannot be run as they stand. The deadline of 10:00 holds only if the skeleton of the app, the routing service and the configuration are ready early enough in the night. The user did not state what happens if they are not.
- The server has 16 GB of memory and 16 cores, confirmed by the user on 2026-10-04. Its free disk was not stated, and its owner judges it sufficient. `plans_finished/valhalla_routing/` sized the routing service against the 4 GB of the old server in its shape, and its plan sizes it within these 16 GB (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-14).
- The public Nominatim instance may block or limit the address of the server. The check of FR-4 finds it before the submission, and the app then shows the search unavailable message (`plans_finished/geocoding/GEOCODING_PRD.md` FR-5).
- Until the specification is changed, M10 requires the demo to show an unavailable routing, and this PRD does not show it. The specification prevails until then.
- The Kraków brief lists secure connections among the basic data protection and security rules (`docs/hackathon/challenge_requirements.md`). The demo does not meet that point, by a decision of the user.
