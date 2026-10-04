# Naming registry

Document state: 2026-10-03

## What this file is

A registry of names actually used in the repository. It describes the actual state, not the target one - unlike `standard_naming.md`, which sets the rules. When the registry and the standard diverge, the standard says what should be and the registry says what is; the divergence between them is information, not an error of either of them.

The deviation rule applies here differently than to the standards: the registry describes the actual state by definition, so it is impossible to be non-compliant with it. It can only be outdated - and that is the only way this file can be wrong.

## How to use it

Before you invent a name for a new file, function or constant, check whether the pattern is already here. If it is, use it. If it is not, and the name is likely to repeat, add it here together with its first place of use. This way a second person will not invent a different name for the same thing.

## Current state

- Layer packages: `api`, `service`, `data`, `worker`; shared configuration is `config` and time is `common_time`.
- Factories and actions: `build_app`, `build_engine`, `build_import_engine`, `build_migration_engine`, `apply_import_exclusion`, `apply_publication`, `apply_import_process`.
- SQL constants use `FETCH_..._SQL` or `APPLY_..._SQL` in `data/locks.py`; import admission and publication fence have separate keys.
- Planned public failure names such as `ImportAlreadyRunning` and `PublicationOutcomeUnknown` are aliases of exception classes ending in `Error`, satisfying the naming gate while preserving the shared contract.
- Launch targets: `backend`, `db-build`, `db-up`, `db-down`, `migration-heads`, `migration-history`, `test-critical`, `check-unit`.
