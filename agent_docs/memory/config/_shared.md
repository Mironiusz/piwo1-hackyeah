## 2026-10-04 - Separate runtime and maintenance credentials (backend skeleton)

- What changed: Runtime configuration exposes only validated application settings and the service URL; Alembic reads its owner URL outside that facade.
- Why: API and administrative runtime code must not gain maintenance credentials.
- Reusable pattern: Use the literal shared file parser with process-environment precedence and safe key-only validation errors.
- Risk / notes: Never read .env.priv at runtime or log input values. Every new entry must extend ENVIRONMENT_ENTRY_FILES and its matching example template.

## 2026-10-04 - The backend connects through the `DB_` entries of `db/` (backend skeleton, merge of mw-osm-import)

- What changed: `config/config.py` exposes `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_SERVICE_ACCOUNT_NAME` and `DB_SERVICE_ACCOUNT_PASSWORD` in place of `DATABASE_URL`, and `data/engine.py` builds the service address from them with `build_database_url()`.
- Why: the user settled the clash of `plans/accounts/ACCOUNTS_PLAN.md` F-13 in favor of `plans/schema_first_revision/SCHEMA_FIRST_REVISION_PLAN.md` D-14 and D-15: the local database, the revisions and the database entries belong to `db/`, not to the skeleton.
- Reusable pattern: a new database consumer takes the address from `data/engine.py` and never declares its own database entry; `DB_HOST` and `DB_PORT` are given at launch, never in a template.
- Risk / notes: `ENVIRONMENT_ENTRY_FILES` names the launch environment for `DB_HOST` and `DB_PORT`. The other backend entries still have no template line, so `.env.local.example` does not yet describe everything the facade reads.

## 2026-10-04 - `ConfigurationError` is a `ValueError` (public_transport_routing, S-9)

- What changed: `build_gtfs_published_day` of `data/gtfs_source.py` guards only the parsing of the header, after a broad `except (TypeError, ValueError)` around `build_business_day` reported a missing configuration as a missing `Last-Modified` header.
- Why: `config.settings.ConfigurationError` subclasses `ValueError`, and `build_business_day` and `fetch_business_now` of `common_time.py` import the facade lazily, so the first call is where a missing entry surfaces. The mistake showed only on a real run, because the tests load invented settings.
- Reusable pattern: never wrap a call that may load `config.config` in an `except ValueError` that turns into a domain error; parse the input in its own `try`, then call the clock or the zone outside it. A test that replaces the zone function with one raising `ConfigurationError` keeps it so (`tests/data/test_gtfs_source_integration.py`).
- Risk / notes: other broad `except ValueError` blocks around rules that read the business zone have the same trap.
