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
