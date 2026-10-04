# Shape: Deployment configuration of the MVP demo

Document state: 2026-10-04, interview in progress
Regulator: C:40

The seed carries no regulator value, so the default C:40 applies.

## Problem

`docs/deployment/hosted_demo.md` describes the steps for standing the hosted demo up on the server of the user, but every step whose exact command, file name, port or version depends on the deployment configuration ends with "Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`". The configuration itself does not exist, so the instructions cannot be run as they stand and the public link of the Kraków submission has nothing behind it. The user split the configuration out of the task `DEPLOYMENT` on 2026-10-04, at the gate of phase B of `plan-prd`, keeping in `DEPLOYMENT` only the documentation (seed, answer "FR-7 + instrukcja"); `DEPLOYMENT` was finished and archived in `plans_finished/deployment/` the same day.

## Recipient and trigger

- The recipient is the user, Rafał, the owner of the server in a data centre, who stands the demo up on it by following `docs/deployment/hosted_demo.md` with one command and an environment file kept outside the repository (`plans_finished/deployment/DEPLOYMENT_SHAPE.md`, section Recipient and trigger).
- The owner of this task is Rafał (`MVP.md`, section Initiatives, the paragraph after the table).
- Deadline: the demo answers at the public link by 10:00 on 4 October 2026, one hour before the Kraków submission closes at 11:00 (`plans_finished/deployment/DEPLOYMENT_PRD.md`, Business goal).
- Trigger: stage 5 of `FINAL_CHECKLIST.md`, section Stages. The work starts at once on documents; check 7.1 can be verified only after checks 2.1, 3.2, 3.3, 3.4 and 6.1.

## Current state

Checked on 2026-10-04 at 06:06, on the branch `rm/requirements-preparation`, with `origin/dev` at `9b2b2ef`.

- `docs/deployment/hosted_demo.md` leaves six things to this task: the minimum version of Docker Engine and the port of the public link (section Before the first start), the name of the environment file and how the start command reads it (Environment file), the start command (Starting the demo), the revisions command (Applying the schema revisions), the command of the loading program and the command that restarts the routing service (Loading the data), and the command that empties the database (Emptying the database).
- The placement on the server is decided in `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-10: four long-running services - `proxy`, the only one that publishes a port of the host, the HTTP port, serving the frontend build and the tile archive with byte ranges and passing `/api/` to `backend`; `backend`, one process of `python -m api`; `database`, an instance of its own on the volume `database_data`; `routing`, the Valhalla service reading the volume `routing_data` - and the import as a one-off container of the backend image writing to `routing_data`, with no long-running worker. The same D-10 leaves to this task the software of the proxy, the way Python 3.13 enters the backend image, the file names of the Compose project and the commands. The base image of the backend, the image of `valhalla/Dockerfile`, was decided by the user in place of Marek and is still to be confirmed by him (`MVP.md`, section Open decisions and confirmations).
- No backend image exists. The only image definitions in the tree are `valhalla/Dockerfile`, `db/image/Dockerfile`, `db/image/Dockerfile.tools` and `database/Dockerfile`. The Valhalla build took 11 min 33 s, a cost this task carries (`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md`, Risks).
- The Valhalla image can also be published to the GitHub container registry by the manual workflow `.github/workflows/valhalla-image.yml`, which runs only from `main`; a private package needs a one-time login on the server with a token that reads packages (`valhalla/README.md`, section Publishing the image). Whether the demo pulls or builds the image was handed to this task by `plans_finished/deployment/DEPLOYMENT_REVIEW.md` O-4.
- The database of the demo is already defined by Kuba in `db/compose.deploy.yaml`: the service `database` on the named volume `database_data`, with no port of the host and `restart: unless-stopped`, and the profile `migrate`, which applies the revisions only with `DB_REVISION_CONSENT=apply` given at the call. It shares no network with other services; `db/README.md`, section Hosted demo, leaves joining it to the other services to this task.
- The backend skeleton exists on this branch and not on `origin/dev`: `api/__main__.py` starts uvicorn with `workers=1`, and `config/settings.py` reads `APP_ENVIRONMENT`, `API_BIND_HOST`, `API_PORT`, `BUSINESS_TIMEZONE`, `LOG_LEVEL`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_SERVICE_ACCOUNT_NAME`, `DB_SERVICE_ACCOUNT_PASSWORD` and `IMPORT_WORKSPACE_ROOT`. `plans/backend_skeleton/BACKEND_SKELETON_PLAN.md` is in the state "implementation delivered for review, image and platform acceptance pending".
- The import is started with `python -m worker.osm_import` in a one-off container of the backend image on the server (`MVP.md` D-14; `plans/osm_importer/OSM_IMPORTER_PLAN.md` D-14). The command `python -m worker import-osm` of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-5 is superseded by it. The one loading program belongs to `plans/osm_import/` (`plans_finished/mvp/MVP_PLAN.md`, the paragraph under D-15), which, like `plans/sample_data/`, has only its seed.
- The routing service, at its start, reads the pointer `current` in `routing_data` and serves the copy it names, waiting while it does not exist (`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-6); `plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-9 extends the rule to the public transport data. `valhalla/Dockerfile` has no start command that reads the pointer, and `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-13 says this task runs the service with its data.
- `plans/frontend_app/FRONTEND_APP_PLAN.md` D-3, decided by Adrian, requires the server of the demo to answer every path that is not a file and does not start with `/api/` with the page of the application, to serve the tile archive at `/tiles/krakow.pmtiles` with byte ranges, and the map style and fonts under `/map/`. Rafał has not confirmed it (`MVP.md`, section Open decisions and confirmations; `plans/frontend_followup/FRONTEND_FOLLOWUP_REPORT.md` B-3). The frontend build needs Node.js 22.22.0 or newer (same report, B-4).
- How the tile archive reaches the server is stated two ways. `plans/map_tiles/MAP_TILES_PLAN.md` D-1 and `MAP_TILES_PRD.md`, section Dependencies: Adrian hands the archive file over and it is loaded on the server by hand, with no step of the loading program. Check 3.4 of `FINAL_CHECKLIST.md`, the row of `osm_import` in `MVP.md`, section Initiatives, and `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-10: a step of the loading program writes the archive to a volume the proxy reads. `MVP.md`, section Open decisions and confirmations, records it as unconfirmed.
- The environment templates in the working copy hold only the database entries: `.env.example` the three passwords, `.env.local.example` `DB_NAME`, `DB_BOOTSTRAP_NAME`, `DB_SCHEMA_OWNER_NAME`, `DB_SERVICE_ACCOUNT_NAME` and `DB_HOST_PORT`. The backend entries of `config/settings.py` are not in them, and neither is `SESSION_SIGNING_KEY`, which `plans/accounts/ACCOUNTS_PLAN.md`, Steps for a human, puts into the environment file of the demo. `docs/standards/standard_config.md` and `docs/setup/backend.md` have uncommitted changes of another session at the time of the check, so the templates and their records are changing.
- A vote without an account stores a hash of the IP address of the person combined with browser characteristics (`docs/product/specification.md`, section Personal data). Behind the proxy of D-10 the backend sees the address of the proxy unless the proxy hands the address of the person on. `plans/community_facts/COMMUNITY_FACTS_SHAPE.md` counts how that address reaches the service as part of the code that writes a vote, and nothing decides the proxy side of it.
- The log entry of the service carries no IP address (`docs/product/api_contract.md`, the rules before the operations). Nothing decides what the proxy logs. The privacy information of the app states each kept item with its purpose and retention (`docs/product/specification.md`, section Personal data), and an IP address in a log is not among them.
- The server has 16 GB of memory and 16 cores; the peak of all services during an import with public transport is at most 10.1 GB (`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-11).
- Two local database setups exist side by side: `compose.local.yml` with `database/` (`plans/backend_skeleton/BACKEND_SKELETON_PLAN.md` D-9) and `db/compose.yaml` (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_PLAN.md` D-14). Both are local and outside this task.

## Smallest meaningful scope

Following from the seed and from `plans_finished/deployment/DEPLOYMENT_PRD.md`, section Out of scope, which lists what this task took over:

- the configuration started with one command and an environment file;
- every part of the demo on the server, with the page, the programming interface and the map tiles served from one host, and the backend as exactly one process;
- a database instance of its own;
- restarts that keep the data;
- completing the commands and names that `docs/deployment/hosted_demo.md` leaves to it.

## Out of scope

- The written instructions and the records of the hosting, done by the task `DEPLOYMENT` (`plans_finished/deployment/`). This task only completes the commands of the instructions.
- A secure connection of the public link, and making routing stop answering during the live demo, both cut by the user on 2026-10-03 (`plans_finished/deployment/DEPLOYMENT_SHAPE.md`, section Out of scope).
- The loading program itself: the import, the sample reports and the tile archive are built by `plans/osm_importer/`, `plans/osm_import/`, `plans/sample_data/` and `plans/map_tiles/`; this task only starts it in the hosted environment.
- Standing the demo up and deleting it, which are steps of the user and of the owner of the repository.

## Functional requirements

To be filled in during the interview.

## Scenarios: input, flow, expected state after the run

To be filled in during the interview.

## Challenging own assumptions

To be filled in during the interview.

## Domain rules or explicit TODO

- Everything of the demo on the server runs in Docker containers orchestrated by Docker Compose (`MVP.md` D-10).
- The demo is served over plain HTTP, without a certificate (`MVP.md` D-10).
- The backend runs as exactly one process (`MVP.md` D-14, `plans_finished/geocoding/GEOCODING_PLAN.md` D-15).
- No address, host, login or secret of the server enters the repository (`docs/standards/standard_config.md`, section Secrets; `CLAUDE.md`, section Target environment).

## Notes on data, performance and security

To be filled in during the interview.

## Open questions

1. What the proxy writes to its log about a visit of the demo, given that an IP address in a log is personal data the privacy information does not state. `Block: yes` (category: personal data)
2. Whether the paths, the tile archive address and the map files of `plans/frontend_app/FRONTEND_APP_PLAN.md` D-3 are a requirement of this task. `Block: no`
3. How the tile archive reaches the server: copied by hand, or written by a step of the loading program. `Block: no`
4. When this task is done, and what is deployed when not every part of the app is ready before the deadline. `Block: no`
5. Whether this task completes the environment templates with the entries the services of the demo read and the templates lack. `Block: no`

Left to phase B of `plan-prd`, because they choose a solution, not the scope: building or pulling the Valhalla image, the software of the proxy, the port of the public link and the minimum version of Docker Engine, and the header by which the proxy hands the address of the person to the backend, agreed with Kuba, who writes the code of the votes.
