# PRD: Deployment of the MVP demo to the chosen hosting

Document state: 2026-10-04

## Business goal

By 10:00 on 4 October 2026 the repository holds everything the user needs to stand the MVP demo of `plans/mvp/` up on their own server in a data centre with one command. The public link in the Kraków submission, which closes at 11:00, then works on the phones of the jury, and the live demo runs from the same place (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`, Business goal). The deadline is one hour before the submission closes, so there is time to check the link and fix what the check finds.

The same task brings the rules of the agent and the records of the hosting in line with the server the demo actually runs on. Without that, the permission levels of the agent describe a machine the demo no longer uses.

## Problem and its consequences

The hosted demo has no deployment configuration and no written instructions. The choice of the hosting was also overturned late on 3 October 2026, when the user moved the demo from the server of the db person to a server of their own. As long as nothing changes:

- Nobody can stand the demo up. The night up to 10:00 is the whole window for the skeleton of the app, the configuration, the first start and the check of the link, and every hour lost comes out of the checks and fixes.
- `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-8, `plans/mvp/MVP_PLAN.md` D-10 and `CLAUDE.md`, section Target environment, describe the server of the db person, so the agent reads its permissions against the wrong machine.
- What else runs on the server of the user is not known. The account that applies the schema revisions is a superuser (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-5). If the database of the demo shared a database instance with anything else, that account could read and drop it.
- If a restart after a fix at 04:00 lost the data, the reports, votes and accounts entered by the team during the check would be gone, and the data of the demo would have to be loaded again before 10:00.

## Scope

- The deployment configuration and written instructions with which the whole demo starts on the server of the user with one command and an environment file kept outside the repository.
- A database instance of its own for the demo.
- Restarts that keep the data, and a separate, deliberate way to empty the database.
- Starting the program that loads the data of the demo by hand, as a step of the written instructions.
- The check after the first start, so the team finds a broken link before the jury does.
- Updating the records of the hosting and the rules of the agent to the server of the user.

## Out of scope

- A secure connection for the public link. The user cut it on 2026-10-03: the demo is served over plain HTTP, and the user accepted the consequences listed in the shape (`DEPLOYMENT_SHAPE.md`, section Out of scope).
- Making routing stop answering during the live demo. The user cut it on 2026-10-03. The behaviour of the app when routing does not answer, FR-17 of `plans/mvp/MVP_PRD.md`, stays, but it is not shown on the hosted link.
- Changing `docs/product/specification.md` M10 to match that cut, and adding the start from the current location, which does not work over HTTP, to the list of what works and what does not of AC-15 of `plans/mvp/MVP_PRD.md`. Both belong to the specification and to `plans/mvp/`, not to this task.
- The program that loads the data, that is, the import of the OpenStreetMap copy, the tile archive and the sample reports. They are work packages of `plans/mvp/MVP_PLAN.md` (D-4, D-6 there, FR-18 of `plans/mvp/MVP_PRD.md`). This task only starts that program on the server.
- The routing service itself and how its data is prepared. Both belong to `plans/valhalla_routing/`. This task runs the routing service on the server.
- Standing the demo up and deleting it on 4 October 2026, which are steps of the user and of the owner of the repository, and written instructions for the deletion, which the user cut on 2026-10-03.
- What happens if the skeleton of the app is not ready by 10:00. The user did not state it (Risks and notes).

## Functional requirements

FR-1. Configuration and instructions. The repository holds the deployment configuration and written instructions with which a member of the team starts the whole demo on the server with one command and an environment file, without help from the person who wrote them, and then opens the demo at the public link on a phone. The environment file lives only on the server; the repository holds only the names of its entries. No address, host, login or secret of the server is in the repository.

FR-2. Everything of the demo runs on the server. The page, the programming interface and the map tiles are served from one host at the public link (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-3). The routing service of `plans/valhalla_routing/` and the database of the demo run on the same server and are started by the same one command. The backend runs as exactly one process and is never scaled out (`plans_finished/geocoding/GEOCODING_PLAN.md` D-15).

FR-3. A database instance of its own. The database of the demo runs in an instance that holds no other database, so the account that applies the schema revisions reaches nothing else on the server. Deleting the demo means removing that instance with its data.

FR-4. Restarts keep the data. Running the one command again, after a fix or after a restart of the server, brings the demo up with every report, vote, account and loaded copy already in its database. Emptying the database is a separate step, run on purpose, which the written instructions name as such.

FR-5. Data loaded by hand. The OpenStreetMap copy, the tile archive and the sample reports are loaded by a separate program, which the user starts by hand after the demo is up. The one command that starts the demo never loads, replaces or deletes data. The written instructions name this step, its order relative to the start, and how to tell that it finished.

FR-6. Check after the first start. The written instructions end with a check the team runs before the link goes into the submission: the demo opens at the public link on a phone, the map shows, a walking route is planned between two addresses, and one address search returns a list (`plans_finished/geocoding/GEOCODING_PLAN.md` D-16).

FR-7. Records of the hosting. The records that name the server of the demo describe the server of the user in a data centre. D-8 of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` gets a note that it is superseded, and D-10 of `plans/mvp/MVP_PLAN.md` and the section Target environment of `CLAUDE.md` point to this task. The change of a workflow rule is recorded in `AI_WORKFLOW.md`. None of them names an address, a host or a login. The permission levels of the agent do not change.

## Acceptance criteria

AC-1 (FR-1). A member of the team who did not write the instructions follows only them, on the server with the environment file filled in, and the demo opens at the public link on a phone. A search of the repository finds no address, host, login or secret of the server, and every entry the environment file needs is named in the repository.

AC-2 (FR-2). At the public link the page, the programming interface and the map tiles answer from the same host. A planned route comes from the routing service on the server, and nothing of a route request leaves the server. While the demo runs, exactly one backend process serves requests.

AC-3 (FR-3). The database instance of the demo lists only the database of the demo. After the instance is removed, no data of the demo is left on the server.

AC-4 (FR-4). The team saves a report and casts a vote, then runs the one command again. After the restart the report and the vote are still there, and no data was loaded again. The step that empties the database is described in the instructions as a separate step, and the one command never runs it.

AC-5 (FR-5). On a fresh server the one command brings the demo up with an empty database, and the map and routes have no data yet. After the user runs the loading program by hand, routes are planned and the sample reports carry the sample data mark (FR-18 of `plans/mvp/MVP_PRD.md`).

AC-6 (FR-6). The check of the instructions passes on the hosted demo before 10:00 on 4 October 2026. If the address search returns the search unavailable message instead of a list, the team knows it before the link goes into the submission.

AC-7 (FR-7). D-8 of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` carries the superseding note. D-10 of `plans/mvp/MVP_PLAN.md` and `CLAUDE.md`, section Target environment, describe the server of the user and point to this task. `AI_WORKFLOW.md` records the change. The three permission levels in `CLAUDE.md` read the same as before. None of these files contains an address, a host or a login.

## Domain rules

- The demo is served over plain HTTP at the address of the server, without a certificate. The browser marks the page as not secure. It does not give the page the current location, so the start is picked from an address or the map. Passwords and session tokens travel unencrypted. The user accepted all of this on 2026-10-03.
- The hosted demo environment of the agent is only the services, the database and the logs of the demo. Every other service, file and log on the server is forbidden to the agent unconditionally, because what else runs there is not known (`CLAUDE.md`, section Target environment).
- Personal data kept by the demo, its deletion on 4 October 2026 after the results and the person responsible for it are those of `plans_finished/demo_environment/DEMO_ENVIRONMENT_SHAPE.md`, section Domain rules. This task does not change them.
- Secrets and details of the target environment never enter the repository (`docs/standards/standard_config.md`, section Secrets).

## Dependencies and impact on other modules

- `plans/mvp/MVP_PLAN.md` Q-11, the backend architecture with the worker, and the skeleton of the app. The configuration names how they start, so it is written only after both exist. They are the trigger of the technical plan of this task.
- `plans/valhalla_routing/`. It decides the routing service this task runs and how its data is prepared. At the time of this PRD it has a closed shape only, and D-9 of `plans/mvp/MVP_PLAN.md` still names the own engine. The user confirmed on 2026-10-04 that Valhalla stays.
- The work packages of `plans/mvp/MVP_PLAN.md` for the import (D-4), the tile archive (D-6) and the sample data (FR-18 of `plans/mvp/MVP_PRD.md`), which together are the loading program of FR-5.
- `plans/schema_revision/` and `plans_finished/local_database/`. The chain of schema revisions and the accounts that the hosted database receives come from them.
- `plans_finished/geocoding/` D-15 and D-16: one backend process, and the check of an address search after the first deployment.
- `docs/product/specification.md` M10 and AC-15 of `plans/mvp/MVP_PRD.md` have to follow the cuts of this task. That work is outside this task.
- `CLAUDE.md`, `AI_WORKFLOW.md`, `plans_finished/demo_environment/` and `plans/mvp/MVP_PLAN.md` are changed by FR-7. The change to the archived initiative is a superseding note only, not its resumption.

## Risks and notes

- No product code existed at the review of the shape, after 22:00 on 3 October 2026, and Q-11 was open. The deadline of 10:00 holds only if the skeleton of the app and the routing service are ready early enough in the night. The user did not state what happens if they are not.
- The resources of the server were not stated in figures. Its owner judges them sufficient. `plans/valhalla_routing/` sized the routing service against the 4 GB of the old server, which no longer apply.
- The public Nominatim instance may block or limit the address of the server. The check of FR-6 finds it before the submission, and the app then shows the search unavailable message (`plans_finished/geocoding/GEOCODING_PRD.md` FR-5).
- Until the specification is changed, M10 requires the demo to show an unavailable routing, and this PRD does not show it. The specification prevails until then.
- The Kraków brief lists secure connections among the basic data protection and security rules (`docs/hackathon/challenge_requirements.md`). The demo does not meet that point, by a decision of the user.
