# Backend foundation

The skeleton provides configuration, logging, an API process, database engine factories, the local database image and a shared import publication boundary. It exposes no product endpoint and ships no product revision. `python -m api` validates configuration and starts without connecting to a database, running migrations or importing OSM.

## Install

Use Python 3.13 x64, Node/npm for the pinned Markdown formatter, GNU make, and Docker Engine 28 or later with Compose v2. On Windows x64 use Docker Desktop with WSL 2 and Linux containers. Run commands from the repository root.

Linux:

```bash
python3.13 -m venv venv
venv/bin/python -m pip install -e ".[dev]"
source venv/bin/activate
npm ci
```

Windows PowerShell:

```powershell
py -3.13 -m venv venv
venv/Scripts/python -m pip install -e ".[dev]"
venv/Scripts/Activate.ps1
npm ci
```

## Configuration

A human copies `.env.example`, `.env.local.example` and `.env.priv.example` to `.env`, `.env.local` and `.env.priv`. Fill every placeholder before launch. `.env` contains credentials and connection strings, `.env.local` contains machine and local database settings, and `.env.priv` is reserved for private process state; runtime configuration never reads it. `.env.local` overrides `.env`; process environment variables override both. Files accept literal `KEY=value` assignments, optional matching outer quotes and full-line comments, without shell expansion. Duplicate keys within a file are refused.

Set `APP_ENVIRONMENT=local`, `BUSINESS_TIMEZONE=Europe/Warsaw`, `API_BIND_HOST=127.0.0.1` and a free `API_PORT`. `LOG_LEVEL` defaults to `INFO`. Service and migration URLs must use `postgresql+psycopg`, an explicit account and database. `DATABASE_URL` uses `DATABASE_SERVICE_USER` and its password; `MIGRATION_DATABASE_URL` uses the separate owner. Keep actual credentials and every hosted-demo address outside the repository. Configuration failures name the key and file without printing its value.

`IMPORT_WORKSPACE_ROOT` is optional for the API and must be an absolute path when supplied. Administrative import callers must pass that path explicitly to `apply_import_exclusion`. It is one persistent local filesystem directory for one database, shared by every import on the same execution machine, including replacement containers. Do not remove or replace `admission.lock`, place two databases in one root, use a network filesystem, or permit imports from a second machine. Containers must mount the same persistent root. Consumer container configuration is outside this foundation.

## Local database and API

```text
make db-build
make db-up
make backend
```

Compose binds the database port only to loopback. Its named volume survives `make db-down`. Initialization creates the database and accounts only on a fresh volume. Changing environment passwords on an existing volume does not update accounts. The bootstrap owner is privileged for extensions and revisions; the runtime service account has no role/database creation or replication privilege. The database uses PostgreSQL 18, UTF-8 and builtin `C.UTF-8` for Polish case conversion and byte comparison. The image supplies pinned PostGIS and pgRouting packages but does not enable them. Kuba's product revision supplies extensions, schema and product grants.

```text
make migration-heads
make migration-history
```

Both currently return an empty revision chain. Alembic alone reads `MIGRATION_DATABASE_URL` through the shared literal file parser; runtime configuration never exposes that credential. It also passes `DATABASE_SERVICE_USER` through `config.attributes["service_role_name"]` for the revision owner. Do not infer product readiness from an empty successful runner.

## Shared interfaces

- `config.config` is the sole runtime environment reader. `config.settings` and `config.env_file` remain pure and independently testable.
- `common_time` provides aware UTC/business timestamps and absolute monotonic deadlines. A publication uses the earlier of the run deadline and 120 seconds from publication entry, without refreshing it between statements.
- `config.logging` configures stdout once, carries a sanitized `request_id`, suppresses foreign-library logs and renders exception diagnostics without exception messages, chained payloads or source lines. API completion logs contain only method, route operation, status, duration and correlation.
- `api` calls `service`, `service` calls `data`, and `worker` calls `service`. Shared configuration and time are available to every layer. The worker has no task or schedule yet.
- `service.administrative.apply_administrative_run(operation, action)` wraps one explicit synchronous administrative action with the same configuration and logs.
- `data.engine` constructs all service and migration engines. Dedicated import engines use `NullPool`, UTC, finite connection and statement waits and hidden SQL parameters. Pass milliseconds explicitly.
- `data.locks.apply_import_exclusion(engine, workspace_root)` yields an `ImportLease`. Keep this context open through every mutation and all caller cleanup. Contenders fail without waiting. A lost original guard cannot be reacquired for publication.
- `data.import_process.apply_import_process(workspace_lease, arguments, deadline)` runs an absolute executable in the run's private directory with no shell and suppressed output. Linux tools and their descendants must preserve both inherited lock descriptors and remain in the supervised process group. Validate each actual tool before integrating it. Windows uses a named non-breakaway, kill-on-close Job Object, assigned while the child is suspended.
- `data.publication.apply_publication(lease, run_deadline, write)` accepts a synchronous callback with a dedicated SQLAlchemy connection. The callback must use that connection for every statement and must not manage transactions, obtain raw driver connections, alter timeout settings or schedule detached work. An acknowledged commit returns `PublicationResult`; confirmed failure before commit raises `PublicationRolledBack`; lost commit acknowledgement raises `PublicationOutcomeUnknown`. Never retry an unknown outcome as if rollback were proven. Backend completion monitoring retains exclusion while completion cannot be established.

The private workspace journal contains only strict infrastructure identities, a commit-attempt flag and the run-owned Windows job name. The next manually launched import checks surviving work and removes only registered private files before admitting fresh acquisition. Corrupt or unrecognized metadata refuses admission. Recovery does not decide the outcome of an uncertain publication, reactivate a routing pointer or reconcile consumer-owned artifacts; Mateusz's importer must settle those contracts.

## Verification and remaining handoffs

```text
make check-unit
make test-critical PYTEST_ARGS=--scratch-database-url=<local-owner-url>
```

Critical collection refuses `APP_ENVIRONMENT=target` with exit code 4 before fixtures, including collect-only. Database acceptance also requires an explicit local maintenance URL:

```text
python -m pytest -m critical --scratch-database-url=<local-owner-url>
```

The fixture refuses an existing `public.backend_skeleton_scratch`, registers exact cleanup before creation and grants scratch DML to the configured service role. Use only an isolated local database. The production-ceiling case takes about 120 seconds. `make check` retains the repository's full test semantics; `check-unit` excludes real dependencies. `psycopg` is the PostgreSQL driver selected by SQLAlchemy; Alembic is a CLI dependency, and tzdata is loaded by the standard-library zoneinfo module on systems without IANA data; both unused-import exceptions are explicit in `pyproject.toml`.

The implementation review records actual runs separately from unavailable acceptance. Linux execution cannot prove native Windows behavior, Docker Desktop setup or replacement-container persistence. The skeleton does not implement the HTTP source clients, product revision and grants, accounts, vote evaluator or locking, OSM importer, routing graph or product endpoints. Those remain the initiatives and owners in `MVP.md`.
