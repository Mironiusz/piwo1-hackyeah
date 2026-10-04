# PRD: Deployment configuration of the MVP demo

Document state: 2026-10-04

## Business goal

The whole MVP demo answers at the public link of the Kraków submission, which closes at 11:00 on 4 October 2026, and stays up until the results are announced, so the jury opens it on their phones and the live demo runs from the same place. The demo is stood up on the server of Rafał by following `docs/deployment/hosted_demo.md` with one start command and one environment file kept outside the repository. The goal of 10:00 set by `plans_finished/deployment/DEPLOYMENT_PRD.md`, Business goal, stays a goal, not a condition of done (`DEPLOYMENT_CONFIG_SHAPE.md`, requirement 12).

## Problem and its consequences

`docs/deployment/hosted_demo.md` describes the steps of the hosted demo, but every step whose exact command, file name, port or version depends on the configuration points to this task, and the configuration does not exist. As long as it does not:

- The instructions cannot be run, and the public link of the submission has nothing behind it.
- The frontend addresses its views by paths, so without a server that answers unknown paths with the page of the application, a reload or a link to any view other than the map of facts fails (`MVP.md`, section Open decisions and confirmations).
- Without the address of the person handed on by the server in front of the backend, every vote without an account looks like it comes from the same address, so all anonymous voters share one daily vote limit (`docs/product/specification.md`, M4 and M9).
- Without outgoing access of the backend, every address search on the demo ends as unavailable.
- The tile step and the loading program have nowhere to write on the server, and the routing service has no data to serve.

## Scope

- The configuration of every part of the hosted demo, started with one command and one environment file.
- The page, the programming interface and the map tiles served from one host over plain HTTP.
- The backend as exactly one process, and the database as an instance of its own.
- Restarts that keep the data.
- The one-off runs of the hosted environment: the schema revisions, the loading program and its steps.
- What the server in front of the backend logs and what it hands on to the backend.
- Completing the commands, names, port and version that `docs/deployment/hosted_demo.md` leaves to this task, and the environment templates for the entries the demo reads.

## Out of scope

- The written instructions and the records of the hosting, done by `plans_finished/deployment/`. This task only completes the commands of the instructions and adjusts them where its own decisions differ from what they say.
- A secure connection of the public link, and making routing stop answering during the live demo, both cut by the user on 2026-10-03 (`plans_finished/deployment/DEPLOYMENT_SHAPE.md`, section Out of scope).
- The loading program itself: the import, the public transport data, the sample reports and the tile step are built by `plans_finished/osm_importer/`, `plans/osm_import/`, `plans/public_transport_routing/`, `plans/sample_data/`, `plans_finished/map_tiles/` and `plans_finished/tile_loading/`. This task only runs them in the hosted environment.
- The backend side of the address of a person, decided and built by `plans/community_facts_api/` (D-16 there).
- Standing the demo up and deleting it, which are steps of Rafał and of the owner of the repository.

## Functional requirements

FR-1. One start. Every long-running part of the demo - the server in front, the backend, the database and the routing service - starts with one command that reads one environment file kept only on the server. The page, the programming interface and the map tiles are served from one host over plain HTTP. The start never applies a schema revision and never loads, replaces or deletes data.

FR-2. One backend process and an own database. The backend runs as exactly one process. The database of the demo is an instance of its own, reachable only by the parts of the demo that use it.

FR-3. Restarts keep the data. Running the start command again, restarting one part or rebooting the server keeps every report, vote, account, loaded copy, routing data and the tile archive, and every part comes back on its own.

FR-4. One-off runs. The schema revisions, the loading program and each of its steps run as one-off runs in the hosted environment, separate from the start, and reach the database and the places they write. After a loading run, a restart of the routing service makes it serve the routing data the run prepared; until such data exist the routing service waits, and a route request gets the plain message of M10.

FR-5. Completed instructions. Every command, file name, port and version that `docs/deployment/hosted_demo.md` leaves to this task is written there: the minimum version of the container runtime, the port of the public link, the name of the environment file and how the start reads it, the start command, the revisions command, the command of the loading program and of its steps, the command that restarts the routing service and the command that empties the database.

FR-6. No address of a person in the log of the server in front. The server in front logs the requests and its own errors - at most the method, the path, the status and the time - and never the IP address or the browser identification of a person (`DEPLOYMENT_CONFIG_SHAPE.md`, requirement 6).

FR-7. Addresses of the frontend. The server answers every path that is not a file and does not start with `/api/` with the page of the application, serves the tile archive at `/tiles/krakow.pmtiles` with byte ranges, and serves the map style and fonts under `/map/` (`plans_finished/frontend_app/FRONTEND_APP_PLAN.md` D-3).

FR-8. Places of the tile archive. The tile step reads the archive from a source place where a person put the file on the server and writes it into the place the server serves at the address of FR-7. The configuration gives the one-off run both places, together with the import workspace and the database the step needs, and keeps the served place across restarts (`plans_finished/tile_loading/TILE_LOADING_PLAN.md`; `docs/deployment/loading_program.md`, section Tile-provider handoff).

FR-9. Address of a person to the backend. The server in front hands the address of the person to the backend on every request it passes, and allows the longest backend operation to finish, as `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-16 decides; the backend trusts the address only from the server in front, configured on the server and never in the repository.

FR-10. Outgoing access. The backend reaches the public Nominatim instance over HTTPS, and the one-off loading runs reach the sources they download. The routing service and the database have no outgoing access, so nothing of a route request leaves the project (`docs/product/specification.md`, M2 and Personal data).

FR-11. Environment templates. Every entry the parts of the demo read from the environment file is in the templates with its record in `docs/standards/standard_config.md`. An entry another initiative adds before the implementation of this task is not added twice. Values the configuration sets for itself, such as how the backend reaches the database, are not entries of the environment file of the server.

FR-12. Partial deployment and done. Until the whole demo works, the parts that already work may be deployed at the public link so the link is not empty. The task is done when the page, the map tiles, the backend, the database and the routing service with its data answer at the public link, started with one command and kept across restarts.

## Acceptance criteria

AC-1 (FR-1, FR-2). On a machine with the container runtime and a filled environment file, the start command brings up the four parts; the page answers at the port of the public link, `/api/` reaches the backend, and exactly one backend process runs. No part other than the server in front is reachable from outside the machine. After the start, the database holds no data the start wrote.

AC-2 (FR-3). After the demo is loaded, a reboot of the machine and a repeated start command each leave the same reports, votes, accounts, routing data and tile archive, without a loading run.

AC-3 (FR-4). The revisions command applies the revisions only with the consent given at the call. The loading program and the tile step run as one-off runs and end with their documented outcomes. After a loading run and the restart command, a walking route is planned; before them, a route request gets the plain message of M10.

AC-4 (FR-5). `docs/deployment/hosted_demo.md` holds no pointer "Completed by the task `DEPLOYMENT_CONFIG`" any more, and every command it names exists in the configuration. A search of the repository finds no address, host, login or secret of the server.

AC-5 (FR-6). After a page load, a tile request, a vote without an account and a failed request, the log of the server in front holds no IP address and no browser identification.

AC-6 (FR-7). A reload of every view path of `plans_finished/frontend_app/FRONTEND_APP_PLAN.md` D-3 returns the page; a byte range request for `/tiles/krakow.pmtiles` returns only the requested bytes; the map style and fonts answer under `/map/`; an unknown path under `/api/` reaches the backend, not the page.

AC-7 (FR-8). With the archive file at the source place, the standalone tile step ends with the outcome `loaded`, the served file has the recorded SHA-256 value and answers at `/tiles/krakow.pmtiles`; a second run ends with `unchanged`; after a restart the archive is still served.

AC-8 (FR-9). Two votes without an account, sent from two different addresses through the server in front, are stored with two different hashes; a request that carries its own forged address entry is not counted under the forged address.

AC-9 (FR-10). An address search on the demo returns a list. From inside the routing service and the database no connection outside the machine can be opened.

AC-10 (FR-11). Every entry the demo reads from the environment file appears in a template and in `docs/standards/standard_config.md`, exactly once.

AC-11 (FR-12). Check 7.1 of `FINAL_CHECKLIST.md` holds: the demo stands up from its configuration, the loading program loads the data, and the map of Kraków shows at the public link; the check of `docs/deployment/hosted_demo.md`, section Check before the link goes into the submission, passes on a phone.

## Domain rules

- Everything of the demo on the server runs in containers orchestrated together, served over plain HTTP without a certificate (`MVP.md` D-10).
- The backend runs as exactly one process (`MVP.md` D-14).
- No address, host, login or secret of the server enters the repository (`docs/standards/standard_config.md`, section Secrets; `CLAUDE.md`, section Target environment).
- The only item of a person kept in a log of the demo is the points of a route request in the log of the routing service, until the demo is deleted on 4 October 2026 (`docs/product/specification.md`, M2 and Personal data).
- The browser talks only to the server of the project; no file of the page comes from outside it (`docs/product/specification.md`, Personal data).

## Dependencies and impact on other modules

- `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-6, D-10 and D-11: the placement of the parts, the pointer the routing service reads and the memory budget.
- `db/README.md`, section Hosted demo: the database of the demo and its revisions, which this task joins to the other parts.
- `valhalla/` and `docs/import/osm_importer.md`: the image of the routing tools, on which the image the import runs in is built.
- `plans/osm_import/`, `plans/public_transport_routing/`, `plans/sample_data/` and `plans_finished/tile_loading/`: the loading program and its steps, which this task runs.
- `plans/community_facts_api/` D-16: the backend side of the address of a person and its two environment entries.
- `plans_finished/frontend_app/` D-3 and `frontend/`: the frontend build the server in front serves.
- `docs/deployment/hosted_demo.md`, the environment templates, `docs/standards/standard_config.md` and `MVP.md`, section Open decisions and confirmations, where the entries that the owner of this task has not confirmed the requirements of FR-7, FR-8 and FR-10 are closed.
- Check 7.1 of `FINAL_CHECKLIST.md`, which waits for checks 2.1, 3.2, 3.3, 3.4 and 6.1.

## Risks and notes

- At 09:50 on 4 October 2026 no part of the configuration existed, and the build of the routing image alone took 11 min 33 s, so the goal of 10:00 is missed; the submission closes at 11:00. A partial deployment (FR-12) keeps the link from being empty meanwhile.
- The common loading program of `plans/osm_import/` did not exist at the time of this PRD; its steps run as separate commands until it does, and FR-5 then names the common command.
- Whether a forged address entry sent by a person can change the hash of a vote depends on how the backend picks the address among those handed on (AC-8); if it can, the issue goes to Marek before the server in front is configured.
- Whether the server in front sees the tile archive replaced by the tile step at once depends on the server chosen in the plan (`plans_finished/tile_loading/TILE_LOADING_SHAPE.md`, Challenging own assumptions).
- The public Nominatim instance may block or limit the address of the server; the check of the instructions finds it, and the app then shows the search unavailable message.
- The free disk of the server was not stated; the routing data, the import workspace, the database and the tile archive share it.
