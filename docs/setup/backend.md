# Backend foundation

The skeleton provides configuration, logging, an API process, database engine factories and a shared import publication boundary. It exposes no product endpoint and ships no product revision. The local database, the database of the hosted demo and the chain of schema revisions are the package `db/` of `plans_finished/schema_first_revision/` (`db/README.md`), not part of the skeleton. `python -m api` validates configuration and starts without connecting to a database, running migrations or importing OSM.

## Install

Use Python 3.13 x64, Node/npm for the pinned Markdown formatter, GNU make, and Docker Engine 28 or later with Compose v2. On Windows x64 use Docker Desktop with WSL 2 and Linux containers. Run commands from the repository root.

Linux:

```bash
python3.13 -m venv venv
venv/bin/python -m pip install ./db
venv/bin/python -m pip install -e ".[dev]"
source venv/bin/activate
npm ci
```

Windows PowerShell:

```powershell
py -3.13 -m venv venv
venv/Scripts/python -m pip install ./db
venv/Scripts/python -m pip install -e ".[dev]"
venv/Scripts/Activate.ps1
npm ci
```

The package `db/` is installed first, because the root dependency `accessibility-db` is that local package and is not published on PyPI.

## Configuration

A human copies `.env.example` and `.env.local.example` to `.env` and `.env.local` and fills every empty marker before launch; the meaning of each entry is in `docs/standards/standard_config.md`, section Environment entries. `.env` holds the secrets and `.env.local` the machine settings. `.env.local` overrides `.env`; process environment variables override both. Runtime configuration never reads `.env.priv`. Files accept literal `KEY=value` assignments, optional matching outer quotes and full-line comments, without shell expansion. Duplicate keys within a file are refused.

The backend connects as the service account of `db/`: it builds the address from `DB_SERVICE_ACCOUNT_NAME`, `DB_SERVICE_ACCOUNT_PASSWORD` and `DB_NAME` of the templates and from `DB_HOST` and `DB_PORT`, which no template carries. They are given at the launch of the backend, as the Compose files of `db/` give them to their own containers: on a developer machine `DB_HOST=127.0.0.1` and `DB_PORT` equal to `DB_HOST_PORT`, on the hosted demo by the Compose file of the backend that `plans/deployment_config/` completes. The backend reads no account of the schema owner and no bootstrap account.

In `.env.local` set `APP_ENVIRONMENT=local`, `BUSINESS_TIMEZONE=Europe/Warsaw`, `API_BIND_HOST=127.0.0.1` and a free `API_PORT`. An empty `LOG_LEVEL` means `INFO`, and an empty `IMPORT_WORKSPACE_ROOT` means that no import is configured on the machine. Keep actual credentials and every hosted-demo address outside the repository. Configuration failures name the key and its file, or the launch environment for `DB_HOST` and `DB_PORT`, without printing the value.

`IMPORT_WORKSPACE_ROOT` is optional for the API and must be an absolute path when supplied. Administrative import callers must pass that path explicitly to `apply_import_exclusion` and end the run as failed with a named exception when the facade exposes `None`. It is one persistent local filesystem directory for one database, shared by every import on the same execution machine, including replacement containers. Do not remove or replace `admission.lock`, place two databases in one root, use a network filesystem, or permit imports from a second machine. Containers must mount the same persistent root. Consumer container configuration is outside this foundation.

## Local database and API

Start the local database and apply the chain of revisions with the commands of `db/README.md`, section Local database; the image, the accounts, the revisions and their critical tests belong to `db/`, and the backend applies no revision. Then start the API with `DB_HOST` and `DB_PORT` set as described above:

```text
make backend
```

## Shared interfaces

- `config.config` is the sole runtime environment reader. `config.settings` and `config.env_file` remain pure and independently testable.
- `common_time` provides aware UTC/business timestamps and absolute monotonic deadlines. A publication uses the earlier of the run deadline and 120 seconds from publication entry, without refreshing it between statements.
- `config.logging` configures stdout once, carries a sanitized `request_id`, suppresses foreign-library logs and renders exception diagnostics without exception messages, chained payloads or source lines. API completion logs contain only method, route operation, status, duration and correlation.
- `api` calls `service`, `service` calls `data`, and `worker` calls `service`. Shared configuration and time are available to every layer. The worker has no task or schedule yet.
- `service.administrative.apply_administrative_run(operation, action)` wraps one explicit synchronous administrative action with the same configuration and logs.
- `data.engine` builds the service-account address of `db/` from the `DB_` entries with `build_database_url()` and constructs every service engine; it constructs no schema-owner engine, because the revisions of `db/` run in their own container. Dedicated import engines use `NullPool`, UTC, finite connection and statement waits and hidden SQL parameters. Pass milliseconds explicitly.
- `data.locks.apply_import_exclusion(engine, workspace_root)` yields an `ImportLease`. Keep this context open through every mutation and all caller cleanup. Contenders fail without waiting. A lost original guard cannot be reacquired for publication.
- `data.import_process.apply_import_process(workspace_lease, arguments, deadline)` runs an absolute executable in the run's private directory with no shell and suppressed output. Linux tools and their descendants must preserve both inherited lock descriptors and remain in the supervised process group. Validate each actual tool before integrating it. Windows uses a named non-breakaway, kill-on-close Job Object, assigned while the child is suspended.
- `data.publication.apply_publication(lease, run_deadline, write)` accepts a synchronous callback with a dedicated SQLAlchemy connection. The callback must use that connection for every statement and must not manage transactions, obtain raw driver connections, alter timeout settings or schedule detached work. An acknowledged commit returns `PublicationResult`; confirmed failure before commit raises `PublicationRolledBack`; lost commit acknowledgement raises `PublicationOutcomeUnknown`. Never retry an unknown outcome as if rollback were proven. Backend completion monitoring retains exclusion while completion cannot be established.

The private workspace journal contains only strict infrastructure identities, a commit-attempt flag and the run-owned Windows job name. The next manually launched import checks surviving work and removes only registered private files before admitting fresh acquisition. Corrupt or unrecognized metadata refuses admission. Recovery does not decide the outcome of an uncertain publication, reactivate a routing pointer or reconcile consumer-owned artifacts; Mateusz's importer must settle those contracts.

## Verification and remaining handoffs

```text
make check-unit
make test-critical PYTEST_ARGS=--scratch-database-url=<local-schema-owner-url>
```

Critical collection refuses `APP_ENVIRONMENT=target` with exit code 4 before fixtures, including collect-only. Database acceptance runs against the local database of `db/` with the chain applied and also requires an explicit URL of its schema owner, `DB_SCHEMA_OWNER_NAME`, for the scratch table only:

```text
python -m pytest -m critical --scratch-database-url=<local-schema-owner-url>
```

The fixture refuses an existing `public.backend_skeleton_scratch`, registers exact cleanup before creation and grants scratch DML to `DB_SERVICE_ACCOUNT_NAME`. Use only an isolated local database. The production-ceiling case takes about 120 seconds. The locale, the extensions and the rights of the accounts are checked by the critical tests of `db/tests/`, not here. `make check` retains the repository's full test semantics; `check-unit` excludes real dependencies. `psycopg` is the PostgreSQL driver selected by SQLAlchemy, and tzdata is loaded by the standard-library zoneinfo module on systems without IANA data; the unused-import exception of tzdata is explicit in `pyproject.toml`.

The implementation review records actual runs separately from unavailable acceptance. Replacement-container persistence of the import workspace belongs to the container configuration of its consumer. The skeleton does not implement the HTTP source clients, product revision and grants, accounts, vote evaluator or locking, OSM importer, routing graph or product endpoints. Those remain the initiatives and owners in `MVP.md`.
