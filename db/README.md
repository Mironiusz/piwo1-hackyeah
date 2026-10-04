# accessibility-db

The shared model of the accessibility database and the chain of its schema revisions, with the database image and the Compose files that run it locally and on the hosted demo. The OpenStreetMap import and the backend install this package and import the tables and closed lists from `accessibility_db` instead of describing them on their own. The target schema is `docs/product/schema.md`; this package creates it and checks that it matches.

## What is here

- `accessibility_db/closed_lists.py` - the six closed lists of the target schema as enumerations.
- `accessibility_db/tables.py` - the seven tables as SQLAlchemy declarative classes; every instant is one `OffsetInstant` attribute, a pair of the instant and its offset.
- `accessibility_db/migrations/` - the Alembic environment and the revisions, applied by the schema owner account; `0001_target_schema` creates the whole target schema and grants the service account its rights.
- `image/Dockerfile` - PostgreSQL 18.6 with PostGIS 3.6.4 and pgRouting 4.0.1, and the script that creates the database, the schema owner and the service account at the first start (`plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-3 - D-6).
- `image/Dockerfile.tools` - Python 3.13 with this package and pytest, for applying the revisions and running the tests.
- `compose.yaml` - the local database, without a lasting volume, on `127.0.0.1` at the port `DB_HOST_PORT`, with the profiles `migrate` and `test`.
- `compose.deploy.yaml` - the database of the hosted demo, with a named volume and no port of the host, with the profile `migrate`.
- `tests/` - a test without a database that compares the first revision with the target schema, and the critical tests against the local database.

## Before the first start

- Docker Engine 28.0.0 or newer with the Compose plugin, or Docker Desktop with the WSL 2 backend on Windows.
- Copy `.env.example` to `.env` and `.env.local.example` to `.env.local` in the repository root and fill in every entry; the meaning of each is in `docs/standards/standard_config.md`, section Environment entries. An empty entry stops Compose with its name.

## Local database

The commands run from the repository root.

```bash
docker compose --env-file .env --env-file .env.local -f db/compose.yaml up -d --wait database
docker compose --env-file .env --env-file .env.local -f db/compose.yaml --profile migrate run --rm migrate
docker compose --env-file .env --env-file .env.local -f db/compose.yaml --profile test run --rm test
docker compose --env-file .env --env-file .env.local -f db/compose.yaml down
```

The first command starts the database and waits until it answers. The second applies the chain of revisions; nothing applies it at the start. The third runs every test of `db/tests/`, the critical ones included, against that database as the service account; each test rolls back its writes. The local database keeps its data only while its container runs, so `down` and `up` give an empty database again, which is also the supported way back after an applied revision was edited.

## Hosted demo

The database of the demo keeps its data in the named volume `database_data`. The step of applying the revisions runs by hand, with the consent given at the call and never written in a file:

```bash
docker compose --env-file <environment file of the demo> -f db/compose.deploy.yaml up -d --wait database
docker compose --env-file <environment file of the demo> -f db/compose.deploy.yaml --profile migrate run --rm -e DB_REVISION_CONSENT=apply migrate
```

Without `DB_REVISION_CONSENT=apply` the step refuses to change the database. How the demo joins this database to its other services is completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/` (`docs/deployment/hosted_demo.md`).
