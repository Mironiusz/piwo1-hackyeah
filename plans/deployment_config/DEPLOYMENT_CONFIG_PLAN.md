# Plan: Deployment configuration of the MVP demo

Document state: 2026-10-04, plan closed

## Goal

Build the configuration of the hosted demo that `DEPLOYMENT_CONFIG_PRD.md` asks for: one Compose project in `deploy/` that starts the proxy, the backend, the database and the routing service with one command and one environment file, runs the schema revisions, the import, the public transport import and the tile step as one-off containers, and keeps the data across restarts; and complete `docs/deployment/hosted_demo.md` with the exact commands, so that Rafał stands the demo up on his server by following it.

## Facts

F-1. The database of the demo is already defined: the service `database` built from `db/image`, on the named volume `database_data`, with `restart: unless-stopped`, a healthcheck and no port of the host, and the service `migrate` under the profile `migrate`, which runs `alembic upgrade head` as the schema owner with `DB_HOST: database` and `DB_PORT: "5432"`. | code:`db/compose.deploy.yaml` services `database` and `migrate`; doc:`db/README.md` section Hosted demo | 2026-10-04
F-2. A Compose file can take both services of `db/compose.deploy.yaml` with `extends` and add a network of its own: the build contexts stay resolved against `db/`, and the volume, the healthcheck, `depends_on` and the profile are kept. | cmd:`docker compose -f deploy/compose.yaml --profile migrate config` on a scratch copy with `extends` of `database` and `migrate` and `networks: [internal]` -> contexts `.../db/image` and `.../db`, `source: database_data`, `condition: service_healthy`, `profiles`, network `enableme_internal` with `internal: true` | 2026-10-04
F-3. The routing image `ghcr.io/mironiusz/valhalla-a11y:3.9.0-a11y.1` is published and public: an anonymous pull token is granted, the manifest resolves without any login to ghcr.io, and the image was pulled on the machine of this session. | cmd:`curl https://ghcr.io/token?scope=repository:mironiusz/valhalla-a11y:pull` -> 200; cmd:`docker manifest inspect ghcr.io/mironiusz/valhalla-a11y:3.9.0-a11y.1` -> resolves with no ghcr.io entry in `~/.docker/config.json`; doc:`valhalla/README.md` section What a run publishes | 2026-10-04
F-4. The routing image starts the service by itself with `python3 /opt/enableme/start_routing_service.py /data`, needs only the routing data mounted read-only at `/data` and listens on 8002; it waits for the pointer `current`, reading it every 5 seconds, and stops with a non-zero code when `current` names no copy with `valhalla_tiles.tar`. | code:`valhalla/Dockerfile` instruction `CMD`; code:`valhalla/start_routing_service.py` functions `fetch_current_copy_name` and `main`; doc:`valhalla/README.md` section Starting the service | 2026-10-04
F-5. The routing image is Ubuntu 24.04.5 with Python 3.12.3, runs as root, holds the Valhalla tools in `/usr/local/bin`, among them `valhalla_build_tiles`, `valhalla_build_extract`, `valhalla_build_config`, `valhalla_build_timezones`, `valhalla_ingest_transit` and `valhalla_convert_transit`, and has `libexpat`. | cmd:`docker run --rm --entrypoint sh valhalla-patched:3.9.0-a11y -c "cat /etc/os-release; python3 --version; ls /usr/local/bin; id"` -> Ubuntu 24.04.5, Python 3.12.3, the tools listed, uid 0; cmd:`docker run --rm --entrypoint sh ghcr.io/mironiusz/valhalla-a11y:3.9.0-a11y.1 -c "ls /usr/lib/x86_64-linux-gnu"` filtered by expat -> 4 entries | 2026-10-04
F-6. The backend needs Python 3.13, installs the local package `./db` before the root project because `accessibility-db` is not on PyPI, and is not packaged: the root project has `py-modules = []`, the code reaches a container by COPY, and the metadata go to `.cache`, whose `.cache/.gitkeep` is versioned. | code:`pyproject.toml` keys `requires-python`, `dependencies`, `tool.setuptools.py-modules` and `tool.distutils.egg_info.egg-base`; doc:`docs/setup/backend.md` section Install | 2026-10-04
F-7. The backend image is to be built on the routing image with Python 3.13 added; the way Python 3.13 enters it, the software of the proxy, the file names of the Compose project and the commands are left to this task. | doc:`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-10 | 2026-10-04
F-8. The image `ghcr.io/astral-sh/uv:0.11.0`, `nginx:1.30.0-alpine` and `node:22.22.0-alpine` exist in their registries. | cmd:`docker manifest inspect` of each of the three -> resolves | 2026-10-04
F-9. `python -m api` starts one uvicorn process from `API_BIND_HOST` and `API_PORT`, with no access log, `proxy_headers=True` and `forwarded_allow_ips` set to `API_TRUSTED_PROXY_ADDRESSES`. | code:`api/__main__.py` function `main` | 2026-10-04
F-10. uvicorn 0.54.0 takes the client address from X-Forwarded-For by walking the entries from the right and returning the first one that is not a trusted host, so an entry a person forges on the left is ignored when the proxy appends the peer address; only a trusted `*` returns the leftmost entry, and the settings refuse `*`. | code:`venv/lib/python3.13/site-packages/uvicorn/middleware/proxy_headers.py` method `_TrustedHosts.get_trusted_client_address`; code:`config/settings.py` method `Settings.apply_trusted_proxy_validation` | 2026-10-04
F-11. The configuration facade reads `.env` and `.env.local` from the working directory when they exist and lets the process environment override them; `API_TRUSTED_PROXY_ADDRESSES` is required as a key and may be empty, `VOTER_HASH_KEY` and `SESSION_SIGNING_KEY` are required secrets of at least 32 characters, and `DB_HOST` and `DB_PORT` come from the launch environment. | code:`config/config.py` module body; code:`config/settings.py` constant `ENVIRONMENT_ENTRY_FILES` and class `Settings` | 2026-10-04
F-12. The templates hold `.env.example`: `DB_BOOTSTRAP_PASSWORD`, `DB_SCHEMA_OWNER_PASSWORD`, `DB_SERVICE_ACCOUNT_PASSWORD`, `SESSION_SIGNING_KEY`, `VOTER_HASH_KEY`; `.env.local.example`: the database names, `DB_HOST_PORT`, the backend entries, `API_TRUSTED_PROXY_ADDRESSES`, the routing entries, `PUBLIC_TRANSPORT_ENABLED`, `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR`. | cmd:`grep -oE "^[A-Z_]+=" .env.example .env.local.example` -> the names listed | 2026-10-04
F-13. Every entry of a template must have a record in `docs/standards/standard_config.md`, section Environment entries, every template holds only empty markers, and every entry of a template must be present in the local file of the same kind where that file exists; nothing ties the templates to `ENVIRONMENT_ENTRY_FILES`. | code:`tests/architecture/test_environment_contract.py` functions `test_every_template_entry_has_a_record_in_the_configuration_standard`, `test_every_template_holds_only_empty_markers` and `test_every_template_entry_is_present_in_its_local_file`; cmd:`grep -rln ENVIRONMENT_ENTRY_FILES tests config` -> only `config/settings.py` | 2026-10-04
F-14. `.gitignore` ignores `.env` and `.env.*` except `.env.example` and `.env.*.example`, and the repository has no `.dockerignore`. | code:`.gitignore` patterns `.env`, `.env.*`, `!.env.example`, `!.env.*.example`; cmd:`ls -a` filtered by docker -> nothing | 2026-10-04
F-15. Every operation of the programming interface is routed under `/api/` by the backend itself, so the proxy passes the path unchanged; the backend has no health endpoint. | code:`api/accounts.py` router `ACCOUNTS_ROUTER`; code:`api/route.py` function `plan_route`; code:`api/address_search.py` route `/api/address-search` | 2026-10-04
F-16. The frontend is built with `npm run build`, that is `tsc -b && vite build`, into `frontend/dist`; the build has no proxy and calls the host it was loaded from; `frontend/public/map/` holds the two styles and the fonts, which the build copies under `/map/`; the tile archive is not in the repository and is ignored under `frontend/public/tiles/`. | code:`frontend/package.json` script `build`; code:`frontend/vite.config.ts` default export; cmd:`ls frontend/public/map` -> `fonts`, `style-en.json`, `style-pl.json`; code:`.gitignore` pattern `frontend/public/tiles/` | 2026-10-04
F-17. The views of the frontend are paths, so the server must answer every path that is not a file and does not start with `/api/` with the page, serve `/tiles/krakow.pmtiles` with byte ranges and the style and fonts under `/map/`; the frontend build needs Node.js 22.22.0 or newer. | doc:`plans_finished/frontend_app/FRONTEND_APP_PLAN.md` D-3; doc:`plans_finished/frontend_followup/FRONTEND_FOLLOWUP_REPORT.md` B-4 | 2026-10-04
F-18. The import is `python -m worker.osm_import` and needs `IMPORT_WORKSPACE_ROOT`, `ROUTING_DATA_DIR`, `VALHALLA_TOOL_DIR` and `VALHALLA_CONFIG_TEMPLATE`, the last one a configuration produced by `valhalla_build_config` of the same image; it downloads the Geofabrik extract, has a 60-minute deadline and ends with the exit codes of its outcome table. | code:`worker/osm_import.py` settings builder; doc:`docs/import/osm_importer.md` sections Prerequisites, Running the first import and a refresh and Outcomes | 2026-10-04
F-19. The public transport import is `python -m worker.gtfs_import`, run after the import in the same kind of one-off container, with the same four paths; it needs the feeds of ZTP Kraków and the timezone boundaries the routing tools download. | code:`worker/gtfs_import.py` settings builder; doc:`docs/deployment/hosted_demo.md` section Loading the data | 2026-10-04
F-20. The tile step is `python -m worker.tile_archive`; it reads the file at `TILE_ARCHIVE_SOURCE`, which must be a regular file and not a link, outside `TILE_ARCHIVE_DIR`, copies it into `TILE_ARCHIVE_DIR` with an atomic replacement, needs `IMPORT_WORKSPACE_ROOT` and the database for the import exclusion, and exits 0 for `loaded` and `unchanged`, 2 for `skipped` and 1 for a failure. | code:`worker/tile_archive.py` constant `TILE_ARCHIVE_EXIT_CODES`; doc:`docs/setup/MAP_SETUP.md` section Handing the archive to the server; doc:`docs/deployment/loading_program.md` section Tile-provider handoff | 2026-10-04
F-21. The backend reads `ROUTING_DATA_DIR` for the boundary of Kraków of the copy in use and calls the routing service at `ROUTING_SERVICE_URL`. | doc:`docs/standards/standard_config.md` section Environment entries, rows `ROUTING_SERVICE_URL` and `ROUTING_DATA_DIR`; code:`data/valhalla.py` client built from `ROUTING_SERVICE_URL` | 2026-10-04
F-22. The import workspace is one persistent local directory per database, shared by every import on the machine including replacement containers, and must never hold the files of two databases. | doc:`docs/setup/backend.md` section Configuration, paragraph on `IMPORT_WORKSPACE_ROOT` | 2026-10-04
F-23. The memory peak of all services during an import with public transport is at most 10.1 GB of the 16 GB of the server. | doc:`plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-11 | 2026-10-04
F-24. The machine of this session has Docker 27.2.1 with Compose 2.29.2; `docs/setup/backend.md` asks developers for Docker Engine 28 or later. | cmd:`docker --version` -> 27.2.1; cmd:`docker compose version` -> v2.29.2; doc:`docs/setup/backend.md` section Install | 2026-10-04
F-25. `docs/deployment/hosted_demo.md` leaves to this task the minimum Docker version and the port, the name of the environment file and how the start reads it, the start command, the revisions command, the commands of the loading step and of the routing restart, and the command that empties the database. | doc:`docs/deployment/hosted_demo.md` sections Before the first start, Environment file, Starting the demo, Applying the schema revisions, Loading the data and Emptying the database | 2026-10-04
F-26. Three documents still say that the owner of this task has not confirmed a requirement for it: the addresses of the frontend, the outgoing HTTPS to Nominatim and the two places of the tile step; and three documents point to this task for the joining of the database, the backend Compose file and the container command of the import. | doc:`MVP.md` section Open decisions and confirmations; doc:`db/README.md` section Hosted demo; doc:`docs/setup/backend.md` section Configuration; doc:`docs/import/osm_importer.md` section Running the first import and a refresh | 2026-10-04
F-27. The naming registry lists the Compose files of `db/` among the file names. | doc:`docs/standards/naming_registry.md` section File names | 2026-10-04

## Decisions

D-1. The routing image is pulled, not built: `routing` uses `ghcr.io/mironiusz/valhalla-a11y:3.9.0-a11y.1`, and the backend image is built `FROM` the same tag. Decided by Kuba on 2026-10-04 in phase B, against building `valhalla/Dockerfile` on the server (F-3). A change of a patch or of `valhalla/Dockerfile` needs a run of `.github/workflows/valhalla-image.yml` and a raised tag in `deploy/compose.yaml` and `deploy/backend.Dockerfile` (`valhalla/README.md`, section When to run it).

D-2. The configuration lives in a new directory `deploy/`: `deploy/compose.yaml`, `deploy/backend.Dockerfile`, `deploy/proxy.Dockerfile` and `deploy/nginx.conf`; a new `.dockerignore` in the repository root keeps `.env`, `.env.*` except the templates, `venv`, `.venv`, `node_modules`, `frontend/node_modules`, `frontend/dist`, `.cache` except `.cache/.gitkeep`, `.git` and `logs` out of the build context, because both images are built from the repository root (F-14). Agent decision at C:40, without asking: one place for the whole demo, next to `db/` and `valhalla/`, which stay as they are.

D-3. The Compose project is named `enableme`. `database` and `migrate` are taken from `db/compose.deploy.yaml` with `extends` and only get the network of D-4, so the database stays defined in one place (F-1, F-2). The volume is therefore `enableme_database_data`, not `accessibility-db_database_data`. Agent decision at C:40, without asking: the name of the product; a database started earlier with `db/compose.deploy.yaml` alone is not taken over (Risks).

D-4. Two networks. `internal`, with `internal: true`, joins `database`, `migrate`, `routing`, `backend` and `loader`; `edge`, an ordinary bridge, joins `proxy`, `backend` and `loader`. Only `proxy` publishes a port, `${DEMO_HTTP_PORT}:80`. So `database` and `routing` have no outgoing access (PRD FR-10), `backend` reaches Nominatim and `loader` the Geofabrik extract, the GTFS feeds and the timezone boundaries through `edge` (F-18, F-19), and nothing but the proxy is reachable from outside the machine (PRD FR-1). Agent decision at C:40, without asking: the only layout that meets FR-2 and FR-10 together.

D-5. Python 3.13 enters the backend image through uv: `deploy/backend.Dockerfile` copies `/uv` from `ghcr.io/astral-sh/uv:0.11.0`, installs CPython 3.13 with `uv python install 3.13` into `/opt/python`, creates `/opt/venv` with it, installs `./db` and then the root project with `uv pip install`, copies `api`, `config`, `data`, `service`, `worker`, `common_time.py` and `common_sample_data.py` into `/app`, writes `valhalla_build_config > /opt/enableme/valhalla_config_template.json`, and starts `python -m api` from `/app`. Agent decision at C:40, without asking: a standalone CPython runs on Ubuntu 24.04 without a third-party package archive, the patch is fixed by the pinned uv version, and copying the Debian build of `python:3.13-slim` would depend on the shared libraries of another distribution (F-5, F-6, F-8).

D-6. Values that follow from the configuration itself are set in `environment:` of `backend` and `loader`, which overrides the environment file: `APP_ENVIRONMENT=target`, `API_BIND_HOST=0.0.0.0`, `API_PORT=8000`, `DB_HOST=database`, `DB_PORT=5432`, `ROUTING_SERVICE_URL=http://routing:8002`, `ROUTING_DATA_DIR=/srv/routing`, `VALHALLA_TOOL_DIR=/usr/local/bin`, `VALHALLA_CONFIG_TEMPLATE=/opt/enableme/valhalla_config_template.json`, `IMPORT_WORKSPACE_ROOT=/srv/import`, `TILE_ARCHIVE_DIR=/srv/tiles` and `TILE_ARCHIVE_SOURCE=/srv/tile_source/krakow.pmtiles`. Every other entry comes from the environment file through `env_file`. `docs/deployment/hosted_demo.md` names these twelve entries as set by the configuration, so their values in the environment file of the server are not read (PRD FR-11). Agent decision at C:40, without asking: they are paths and addresses inside the containers, which only the Compose file knows (F-11, F-21).

D-7. Four named volumes: `database_data` from F-1; `routing_data`, read-write at `/srv/routing` in `loader`, read-only at `/srv/routing` in `backend` and at `/data` in `routing`; `import_workspace`, read-write at `/srv/import` in `loader`; `tile_archive`, read-write at `/srv/tiles` in `loader` and read-only at `/srv/tiles` in `proxy`. Agent decision at C:40, without asking: D-6 and D-10 of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md`, F-20, F-21 and F-22.

D-8. The one-off runs are the service `loader` under the profile `load`: the backend image, `restart: "no"`, `depends_on` `database` healthy, started with `docker compose ... run --rm loader python -m worker.osm_import`, `python -m worker.gtfs_import` or `python -m worker.tile_archive`. The tile file is bound only for the tile run, at the call: `-v <path of the file on the server>:/srv/tile_source/krakow.pmtiles:ro`, so the source place needs no environment entry and lies outside `TILE_ARCHIVE_DIR` (F-20). When the common program of `plans/osm_import/` exists, it runs in the same service. Agent decision at C:40, without asking: D-5 of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` and D-14 of `MVP.md`, and the commands that exist today (F-18 - F-20).

D-9. The proxy is nginx `1.30.0-alpine`, built by `deploy/proxy.Dockerfile` in two stages: `node:22.22.0-alpine` runs `npm ci` and `npm run build` in `frontend/`, and the nginx stage copies `frontend/dist` to `/usr/share/nginx/html` and `deploy/nginx.conf` to `/etc/nginx/nginx.conf`. `deploy/nginx.conf`:

- `error_log /dev/stderr emerg;`, so nginx writes only the failures that stop it, which carry no request, and never an error line with the address of a client;
- `log_format enableme '$time_iso8601 $request_method $uri $status';` and `access_log /dev/stdout enableme;`, with `$uri` and not `$request_uri`, so no query string, address or browser identification is logged (PRD FR-6);
- `server_tokens off;` and `listen 80;`;
- `location /api/` with `proxy_pass http://backend:8000;`, `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`, `proxy_set_header Host $host;` and `proxy_read_timeout 130s;`, above the 120 seconds of D-12 of `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` (PRD FR-9);
- `location = /tiles/krakow.pmtiles` with `alias /srv/tiles/krakow.pmtiles;`, served by nginx as a static file with byte ranges, and opened on every request because `open_file_cache` stays off, so the atomic replacement of the tile step is seen at once (PRD FR-7, FR-8);
- `location /` with `try_files $uri $uri/ /index.html;`, which serves the build, `/map/` included, and answers every other path with the page (PRD FR-7).

Agent decision at C:40, without asking: nginx serves byte ranges, the fallback to the page and an access log of chosen fields with no module, and its error log can be held to failures that carry no request.

D-10. `proxy`, `backend` and `routing` have `restart: unless-stopped`, as `database` has from F-1, so every long-running part comes back after a reboot (PRD FR-3). `proxy` depends on `backend` and `backend` on `database` healthy and on `routing` started. Agent decision at C:40, without asking: the policy `db/` already uses.

D-11. The environment file of the demo is `.env.demo` in the repository root, ignored by `.env.*` (F-14). Every command runs from the repository root as `docker compose --env-file .env.demo -f deploy/compose.yaml ...`; the same file is read by `env_file: ../.env.demo` of `backend` and `loader` and by the interpolation of `db/compose.deploy.yaml`. Agent decision at C:40, without asking: one file of both templates, as `docs/deployment/hosted_demo.md`, section Environment file, already says.

D-12. The port of the public link is a new entry `DEMO_HTTP_PORT` of `.env.local.example`, read only by the interpolation of `deploy/compose.yaml` as `${DEMO_HTTP_PORT:?Set DEMO_HTTP_PORT}`, with its record in `docs/standards/standard_config.md`; it has no counterpart in `config/settings.py`, because no service process reads it. Agent decision at C:40, without asking: what else listens on the server is not known (`CLAUDE.md`, section Target environment), so the port must change without a change of the repository (`docs/standards/standard_config.md`, section Rule for assigning a value to a layer).

D-13. The minimum is Docker Engine 27 with the Compose plugin 2.29, the versions the configuration is verified with on the machine of this session (F-24). Agent decision at C:40, without asking: the features used - `extends` with a build, profiles, `depends_on` with a condition, `--wait` and internal networks - all work there.

D-14. Emptying the database removes the volumes `enableme_database_data` and `enableme_import_workspace` after `docker compose ... down`, and keeps `enableme_routing_data` and `enableme_tile_archive`. Agent decision at C:40, without asking: the workspace belongs to one database (F-22); the routing data and the archive hold no report, vote or account, and the next import writes a new copy and pointer.

D-15. `API_TRUSTED_PROXY_ADDRESSES` on the server is the subnet of the network `enableme_edge`, read after the first start with `docker network inspect enableme_edge --format '{{(index .IPAM.Config 0).Subnet}}'` and written into `.env.demo`, after which `backend` is recreated; the value never enters the repository (D-16 of `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md`). Until it is set, the entry is empty and every vote without an account seems to come from the proxy. Agent decision at C:40, without asking: the subnet is chosen by Docker on the server, and fixing one in the repository could collide with a network already there.

D-16. The documents are completed in the same change: `docs/deployment/hosted_demo.md` gets every command of F-25, the list of D-6 and the step of D-15, and loses every pointer to this task; `db/README.md`, section Hosted demo, `docs/setup/backend.md`, section Configuration, and `docs/import/osm_importer.md`, section Running the first import and a refresh, point to `deploy/compose.yaml` and `docs/deployment/hosted_demo.md` instead of to this task; `MVP.md`, section Open decisions and confirmations, closes the three items of F-26 as confirmed by Kuba on 2026-10-04 in `DEPLOYMENT_CONFIG_SHAPE.md`, requirements 7, 8 and 11, and records in section Initiatives or under D-10 what this task settled, as its paragraph on unfinished initiatives asks; `docs/standards/naming_registry.md`, section File names, gets `deploy/compose.yaml`, `deploy/backend.Dockerfile`, `deploy/proxy.Dockerfile` and `deploy/nginx.conf`; `docs/standards/README.md` names `deploy/` next to `docs/deployment/`. Agent decision at C:40, without asking: PRD FR-5 and FR-11, and the rule of `MVP.md` that a change making one of its items untrue updates it.

D-17. Verification runs on the machine of this session with a throwaway `.env.demo` of generated test values, never on the server: the images are built, the project is started, and the checks of the Definition of Done are run with `curl` and `docker compose`; the file is removed afterwards. The full import is run once if the download allows it; the tile step with the real archive and the check on a phone stay with Rafał on the server, because the archive is not on this machine (F-16). Agent decision at C:40, without asking: `CLAUDE.md`, section Target environment, allows local tools and forbids changes on the server without an explicit request.

## Scope of changes

S-1. `.dockerignore` (new): the patterns of D-2, one per line.

S-2. `deploy/backend.Dockerfile` (new):

```text
FROM ghcr.io/astral-sh/uv:0.11.0 AS uv
FROM ghcr.io/mironiusz/valhalla-a11y:3.9.0-a11y.1
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_INSTALL_DIR=/opt/python UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH
RUN uv python install 3.13 && uv venv --python 3.13 /opt/venv
WORKDIR /app
COPY db/pyproject.toml db/alembic.ini ./db/
COPY db/accessibility_db ./db/accessibility_db
RUN uv pip install ./db
COPY pyproject.toml ./
COPY .cache/.gitkeep ./.cache/.gitkeep
RUN uv pip install .
RUN valhalla_build_config > /opt/enableme/valhalla_config_template.json
COPY api ./api
COPY config ./config
COPY data ./data
COPY service ./service
COPY worker ./worker
COPY common_time.py common_sample_data.py ./
CMD ["python", "-m", "api"]
```

The image has no line comment and no secret; `/app` holds no `.env` file (S-1), so the facade reads only the process environment.

S-3. `deploy/proxy.Dockerfile` (new): stage `frontend` `FROM node:22.22.0-alpine`, `WORKDIR /frontend`, `COPY frontend/package.json frontend/package-lock.json ./`, `RUN npm ci`, `COPY frontend ./`, `RUN npm run build`; stage `FROM nginx:1.30.0-alpine`, `COPY deploy/nginx.conf /etc/nginx/nginx.conf`, `COPY --from=frontend /frontend/dist /usr/share/nginx/html`.

S-4. `deploy/nginx.conf` (new): `worker_processes auto;`, `error_log /dev/stderr emerg;`, `events {}`, and `http` with `include /etc/nginx/mime.types;`, `default_type application/octet-stream;`, the log format, access log, `server_tokens off;` and the `server` of D-9.

S-5. `deploy/compose.yaml` (new), `name: enableme`:

- `proxy`: `build: {context: .., dockerfile: deploy/proxy.Dockerfile}`, `image: enableme-proxy:local`, `ports: ["${DEMO_HTTP_PORT:?Set DEMO_HTTP_PORT}:80"]`, `volumes: [tile_archive:/srv/tiles:ro]`, `networks: [edge]`, `depends_on: [backend]`, `restart: unless-stopped`;
- `backend`: `build: {context: .., dockerfile: deploy/backend.Dockerfile}`, `image: enableme-backend:local`, `env_file: ../.env.demo`, `environment:` the twelve values of D-6, `volumes: [routing_data:/srv/routing:ro]`, `networks: [internal, edge]`, `depends_on: {database: {condition: service_healthy}, routing: {condition: service_started}}`, `restart: unless-stopped`;
- `routing`: `image: ghcr.io/mironiusz/valhalla-a11y:3.9.0-a11y.1`, `volumes: [routing_data:/data:ro]`, `networks: [internal]`, `restart: unless-stopped`;
- `database` and `migrate`: `extends` of `../db/compose.deploy.yaml`, `networks: [internal]`;
- `loader`: `image: enableme-backend:local`, `profiles: [load]`, `env_file: ../.env.demo`, `environment:` the twelve values of D-6, `volumes: [routing_data:/srv/routing, import_workspace:/srv/import, tile_archive:/srv/tiles]`, `networks: [internal, edge]`, `depends_on: {database: {condition: service_healthy}}`, `restart: "no"`;
- `networks`: `internal: {internal: true}`, `edge: {}`;
- `volumes`: `database_data`, `routing_data`, `import_workspace`, `tile_archive`.

The twelve values of D-6 are written once as a YAML anchor `x-container-paths` and merged into `backend` and `loader`.

S-6. `.env.local.example`: the line `DEMO_HTTP_PORT=`. `docs/standards/standard_config.md`, section Environment entries: its row - the port of the host at which the proxy of `deploy/compose.yaml` publishes the hosted demo, read only by the interpolation of that file - and one paragraph: it came on 2026-10-04 with `plans/deployment_config/`, is required by `deploy/compose.yaml` and stops it with its name when empty, has no counterpart in `config/settings.py`, and on a developer machine any free port; and that `deploy/compose.yaml` sets the twelve entries of D-6 itself for `backend` and `loader`, as the Compose files of `db/` set `DB_HOST` and `DB_PORT`.

S-7. `docs/deployment/hosted_demo.md`: in Before the first start, Docker Engine 27 with the Compose plugin 2.29 or newer, and the port of `DEMO_HTTP_PORT`; in Environment file, `.env.demo` in the repository root, filled from both templates, read by `--env-file` and by the services, with the twelve entries of D-6 listed as set by the configuration, and `API_TRUSTED_PROXY_ADDRESSES` left empty until the step of D-15; in Starting the demo, `docker compose --env-file .env.demo -f deploy/compose.yaml up -d --build --wait proxy backend routing database`, then the step of D-15; in Applying the schema revisions, `docker compose --env-file .env.demo -f deploy/compose.yaml --profile migrate run --rm -e DB_REVISION_CONSENT=apply migrate`; in Loading the data, the three `run --rm loader` commands of D-8 in the order `worker.osm_import`, `worker.gtfs_import`, `worker.tile_archive` with the bind of the file, and `docker compose --env-file .env.demo -f deploy/compose.yaml restart routing`; in Restarting after a fix, the start command; in Emptying the database, `docker compose --env-file .env.demo -f deploy/compose.yaml down` and `docker volume rm enableme_database_data enableme_import_workspace`; the sentence of What this document covers that steps end with a pointer to the task is removed, and so is every pointer "Completed by the task `DEPLOYMENT_CONFIG`".

S-8. `db/README.md`, section Hosted demo; `docs/setup/backend.md`, section Configuration; `docs/import/osm_importer.md`, section Running the first import and a refresh: the sentence that points to this task points to `deploy/compose.yaml` and `docs/deployment/hosted_demo.md`.

S-9. `MVP.md`: the three items of F-26 in section Open decisions and confirmations are closed with the requirement of `DEPLOYMENT_CONFIG_SHAPE.md` that confirms each; the row or paragraph of this task records `deploy/compose.yaml`, the pulled routing image of D-1 and nginx of D-9.

S-10. `docs/standards/naming_registry.md`, section File names, and `docs/standards/README.md`, the item on `docs/deployment/`: the names of D-16.

## Rollout order

1. S-1 - S-5, then `docker compose --env-file .env.demo -f deploy/compose.yaml config` with a throwaway `.env.demo` of generated test values.
2. `docker compose ... build`, then `up -d --wait proxy backend routing database`, the revisions run of S-7, and the checks AC-1, AC-5, AC-6, AC-8 and AC-9 of the Definition of Done; `routing` waits for the pointer meanwhile, which checks scenario 2 of the shape.
3. The import and the public transport import with `run --rm loader`, `restart routing` and a walking route through `/api/routes` (AC-3); then a reboot of the project with `down` and `up -d --wait` and the same route without a loading run (AC-2).
4. S-6 - S-10, then `make lint-docs` and `python -m pytest tests/architecture`.
5. `docker compose ... down`, removal of the throwaway volumes and of `.env.demo` on this machine.

Steps for a human:

- Commit and push, and the Merge Request.
- Add `DEMO_HTTP_PORT` with any free port to the local `.env.local` of each developer machine, which the environment contract test asks for (F-13).
- On the server, Rafał: fill `.env.demo` from both templates with values of the server, follow `docs/deployment/hosted_demo.md` from Before the first start to the check, put the archive of Adrian on the server and run the tile step, and tick check 7.1 of `FINAL_CHECKLIST.md` when the map of Kraków shows at the public link.

## Definition of Done

- `docker compose --env-file .env.demo -f deploy/compose.yaml config` ends with code 0, and with an empty `DEMO_HTTP_PORT` it stops naming it.
- After `up -d --wait`, `docker compose ps` shows `proxy`, `backend`, `routing` and `database` running; `docker compose exec backend sh -c "ps -e"` shows one `python -m api` process; `docker compose port` names a port only for `proxy` (AC-1).
- `curl -sI http://127.0.0.1:$DEMO_HTTP_PORT/` and `curl -sI http://127.0.0.1:$DEMO_HTTP_PORT/routes/any-view` both return 200 with `text/html`; `/map/style-pl.json` returns the style; `curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:$DEMO_HTTP_PORT/api/routes` reaches the backend and returns its answer, not the page (AC-6).
- With a file put into the volume `tile_archive` under `krakow.pmtiles`, `curl -s -H "Range: bytes=0-15" -D - http://127.0.0.1:$DEMO_HTTP_PORT/tiles/krakow.pmtiles` returns 206 with 16 bytes (AC-6); the tile step itself is verified by Rafał with the real archive (AC-7).
- After a page, a tile, a request to `/api/` and a request to a missing path, `docker compose logs proxy` holds lines of only time, method, path and status, and no IP address and no browser identification (AC-5).
- `docker compose exec routing python3 -c "import socket; socket.create_connection(('1.1.1.1', 443), 3)"` and the same from `database` with `bash -c "exec 3<>/dev/tcp/1.1.1.1/443"` fail, and the same from `backend` succeeds (AC-9).
- With `API_TRUSTED_PROXY_ADDRESSES` set as in D-15, a request through the proxy with a forged `X-Forwarded-For: 203.0.113.9` is seen by the backend with the address of the client and not with the forged one, checked by a temporary log of `request.client.host` run in a throwaway container from the same image and never committed, or by two votes without an account once `plans/community_facts_api/` exposes them (AC-8).
- The import, the public transport import and `restart routing` end with exit code 0 and a planned walking route; after `down` and `up -d --wait` the same route is planned without a loading run (AC-2, AC-3).
- `docs/deployment/hosted_demo.md` holds no "Completed by the task `DEPLOYMENT_CONFIG`" (AC-4); a search of the change finds no address, host, login or secret of the server.
- `python -m pytest tests/architecture` and `make lint-docs` pass.
- The review of `docs/standards/standard_review.md` is run on the change.

## Risks

- A database started on the server earlier with `db/compose.deploy.yaml` alone lives in the volume `accessibility-db_database_data` and is not used by the project `enableme` (D-3); the instructions start from an empty database anyway, and such a container is stopped with `docker compose -f db/compose.deploy.yaml down` before the first start.
- The full import downloads the extract of Małopolska and runs up to 60 minutes; if it does not fit the time of this task on this machine, AC-2 and AC-3 are verified by Rafał on the server.
- Until `plans/community_facts_api/` exposes a vote, AC-8 is checked only with a throwaway container (Definition of Done).
- The default request body limit of nginx is 1 MB; no endpoint of the backend accepts a file at the time of this plan, and an endpoint of photos (O2) needs `client_max_body_size` raised in `deploy/nginx.conf`.
- The containers run as root, as the routing image does (F-5); the demo exists for one day and publishes only the proxy.
- The free disk of the server was not stated; the routing data, the import workspace, the database, the two images and the archive share it.
- `docs/setup/backend.md` asks developers for Docker Engine 28, while the demo asks for 27 (D-13); the two serve different machines and do not contradict each other.

## Open questions

None. Every decision of this plan is recorded in Decisions.

## Supplementary files

None.
