## 2026-10-04 - Separate runtime and maintenance credentials (backend skeleton)

- What changed: Runtime configuration exposes only validated application settings and the service URL; Alembic reads its owner URL outside that facade.
- Why: API and administrative runtime code must not gain maintenance credentials.
- Reusable pattern: Use the literal shared file parser with process-environment precedence and safe key-only validation errors.
- Risk / notes: Never read .env.priv at runtime or log input values. Every new entry must extend ENVIRONMENT_ENTRY_FILES and its matching example template.
