# Review: Backend skeleton and local database of the MVP

Document state: 2026-10-04, planning in progress

## 2026-10-04 - Phase B resumed from the approved PRD

Scope: preparation of `BACKEND_SKELETON_PLAN.md`, not implementation or a readiness verdict for the backend.

The existing initiative has a closed shape and an approved PRD but no implementation plan. Resumed `plan-prd` phase B, preserving the seed, shape, PRD, importer ownership and archived decisions. Created a plan in progress covering the application foundation, environment entries, local database, Alembic handoff, shared logging, administrative wrapper, protected critical tests and the publication/exclusion proposal.

Checked the current MVP allocation, backend architecture, local database decisions, importer amendments and standards. Verified the PostgreSQL image manifest and public dependency metadata. Neither an image build, a backend launch nor a database publication has been performed in this phase. No hosted environment was accessed.

Q-1 remains pending: the user was asked whether PostgreSQL transaction_timeout plus a separate exclusion session should be the implementation direction. No answer was inferred from elapsed time. Q-2 records the outstanding proof of connection-loss fencing and safe cleanup; a separate advisory-lock holder alone does not establish that a publisher stops when that holder disappears. The proposed interface paragraphs are explicitly conditional. The plan cannot yet be marked closed or used to implement these contracts.

Validation:

- Python 3.13.11 with the repository-pinned pytest 9.1.1 ran the plan-contract, prose-style and conflict-marker suites: 51 passed, 1 failed in 6.83 seconds.
- The sole failure points to bold prose in `.pytest_cache/README.md:6`, outside the initiative. Its modification time was 2026-10-03 20:17:34 +0200, before this turn; it was not modified or removed.
- Direct use of the existing fact/prose validators on the draft plan found zero violations. This check covers an in-progress draft that the closed-plan gate intentionally skips; it does not verify the truth of every fact or approve the proposed contract.
- The pinned Prettier 3.7.4 formatted the plan. The final targeted formatting check covers both new artifacts.
- `git diff --check` passed; both new artifacts remain untracked and were not staged.

Another session created `plans/accounts/ACCOUNTS_SHAPE.md` during this work. Its file was not changed. Only the two backend-skeleton planning artifacts were added to repository content by this task; temporary verification environments and downloaded formatting tools are untracked tool artifacts.

Verdict: planning incomplete, pending Q-1 and Q-2. No implementation readiness or completion is claimed, no durable implementation memory is added, and the initiative remains in `plans/backend_skeleton/`.

## 2026-10-04 - Timeout direction approved and database primitives checked

Scope: recording the user's Yes to Q-1 and resolving the engineering portion of Q-2. This entry supersedes the earlier pending-Q-1 status; it does not rewrite that historical entry or approve a new PRD boundary.

The user approved PostgreSQL transaction_timeout, an independent exclusion-holder connection and a distinct uncertain-commit outcome. Updated the plan immediately, then checked the underlying database primitives in a disposable local `postgres:18.6-trixie` container with no network, no published port and a tmpfs database. No product backend, product revision, actual import or hosted action was performed.

The probe used invented scratch data and a restricted service role. Its output was:

```json
{
  "admission_after_all_backend_locks_end": true,
  "busy_refused_ms": 0.38,
  "publisher_fence_survives_guard_loss": true,
  "rollback_confirmed_and_guard_retained": true,
  "server_version": "18.6 (Debian 18.6-1.pgdg13+2)",
  "timeout_elapsed_ms": 404.56
}
```

A session-held admission lock preserved exclusion while a separate publication session timed out and its insert rolled back. A second key, shared by the publication session and probed exclusively by each contender, prevented new admission after the guard session was deliberately terminated. After the publication session also timed out and disappeared, admission succeeded and the scratch insert remained absent. This verifies server primitives with shortened budgets, not the final SQLAlchemy implementation, exact 120-second performance, file cleanup, commit uncertainty or complete-import behavior.

Recorded the fixed two-key protocol, typed backend identities, stale-guard attachment refusal, fresh autocommit cleanup checks and no-reconnect policy in D-11 - D-14. Agent decision at C:40, without asking: these engineering details implement the approved direction without changing product objects or granting maintenance privileges. PostgreSQL documents the same-role activity visibility and try-lock semantics; the probe exercised the service-role path. The task-owned container was stopped and its temporary database removed by its `--rm` lifecycle; no existing container was stopped.

One contractual question remains. If both sessions disappear, advisory locks cannot preserve exclusion until the old Python process finishes its private file cleanup. The user has been asked whether to accept new admission after database completion on that abnormal failure path, with the old run forbidden to republish, or retain FR-8's stronger cleanup requirement. No answer has been inferred. An affirmative answer must land in the shape and PRD before the plan closes; a negative answer requires redesign without inventing a persistent schema object.

Other sessions changed `MVP.md`, `docs/product/api_contract.md` and `docs/product/schema.md`. Inspected the diffs: account pseudonym alignment and account documentation, with no skeleton error-envelope or database DDL change. Preserved those edits and refreshed the corresponding planning fact.

Targeted fact-format and prose validation and Prettier cover the updated plan and review. The prior repository-wide prose failure remains the pre-existing `.pytest_cache/README.md` finding. No implementation verdict, archive move or durable implementation memory is claimed.

Verdict: planning incomplete, Q-1 resolved; Q-2 awaits the abnormal-loss cleanup decision. The initiative remains in `plans/backend_skeleton/`.

## 2026-10-04 - Q-2 answered: retain exclusion through file cleanup

Scope: record the user's requirement that a new import must wait until file cleanup finishes, including after both database lock sessions are lost. Updated the shape, PRD FR-8 and AC-8, and the technical plan. The earlier pending-Q-2 record remains historical.

The answer rejects admission based solely on database completion. D-11 - D-14 cannot satisfy the full requirement with session-bound locks alone. No production code, persistent schema lease, shared-filesystem assumption or automatic recovery policy was introduced. Technical-plan Q-3 now asks how to finish cleanup and authorize admission after the old process crashes.

Verdict: planning incomplete. Q-2 is answered; Q-3 and the durable exclusion redesign remain blocking. The initiative remains in `plans/backend_skeleton/`.

## 2026-10-04 - Q-3 answered: automatic crash recovery

Scope: record the user's selection of automatic cleanup and admission release after the old process crashes. Updated the shape, PRD FR-8 and Out of scope, and the plan. No manual recovery policy was adopted and no implementation was started.

The current MVP and backend architecture allow manually launched imports and specify no long-running worker. Automatic cleanup on a later manual launch may preserve that architecture; cleanup without another launch needs an independent recovery owner. Q-4 asks the observable timing rather than assuming either behavior. No importer-owned file or archived architecture artifact was changed.

Verdict: planning incomplete. Q-3 is answered; Q-4 and the durable exclusion redesign remain blocking.

## 2026-10-04 - Q-4 answered: recover on the next manual import

Scope: record the user's choice of recovery during the next manual launch. Updated the shape, PRD FR-8, AC-8 and Out of scope, and the plan. Recovery precedes new acquisition; no periodic import or independent cleanup service is introduced.

Checked importer D-14: hosted imports run on the server and local imports use local development databases; this does not authorize a team computer accessing the hosted database. That allocation does not explicitly guarantee one execution machine and a persistent workspace for all runs against one database. Q-5 asks this boundary before selecting cross-platform process exclusion and recovery. A timeout or missing database session remains insufficient evidence that old local work has stopped.

Verdict: planning incomplete. Q-4 is answered; Q-5 and the concrete exclusion/recovery redesign remain blocking. No importer-owned files, product schema, production code or hosted environment were changed.

## 2026-10-04 - Q-5 answered: shared persistent workspace on one machine

Scope: record the user's confirmation of one execution machine and one persistent workspace for every import into a given database, also across replacement containers. Updated the shape, PRD FR-8 and the plan. The seed, importer-owned files, archived architecture and hosted environment are unchanged.

Q-2 - Q-5 now settle observable recovery behavior: wait through file cleanup despite database session loss, recover automatically during the next manual launch, and access the old workspace from the same execution machine. These answers remove the need to infer distributed cleanup or add an independent recovery service. The concrete local process/child-work exclusion, crash journal and database-completion verification remain technical design work.

Verdict: planning incomplete, user behavior questions Q-2 - Q-5 answered. The plan remains in progress until the revised recovery protocol is concrete and verified; no implementation readiness is claimed.

## 2026-10-04 - Current environment rechecked and local recovery primitive probed

Rechecked the execution environment rather than reusing the earlier machine's evidence. Docker CLI 29.1.3 and Compose 2.40.3 are installed, but local socket access fails inside and outside the sandbox. An approved sudo check requires interactive authentication. Python is 3.14.4; Python 3.13 and the backend runtime dependencies are absent. Updated plan F-17; earlier database probes remain historical evidence, not current acceptance runs.

An isolated probe outside the repository verified Linux nonblocking owner exclusion, durable pending-workspace state after owner termination, and exclusion during exact-workspace recovery. It used only invented files and a task-owned subprocess, cleaned its temporary directory, and touched no database or hosted service. Recorded its limited scope in F-26. No process-tree, Windows, container or PostgreSQL guarantee is inferred.

Outstanding engineering work: define and verify durable workspace exclusion together with external child-process containment, crash recovery and registered database completion. Simply acquiring a file lock after the owner dies does not prove that its external tools have stopped. Windows and cross-container recovery cannot be claimed from the Linux owner-only probe.

Validation: the 52 plan-document, prose-style and conflict-marker tests passed after recording Q-5; the post-evidence validation is recorded by the completing session. Local PostgreSQL verification is unavailable because of Docker permissions. No production implementation, plan closure, archive move, staging, commit or push was performed.

## 2026-10-04 - Recovery design closed and foundation implemented

Scope: S-1 - S-8 of the closed backend skeleton plan, on `mw-backend-skeleton` after the resolved dev merge. The earlier incomplete-planning verdicts are historical: Q-1 - Q-5 are now answered, and D-17 - D-18 provide the concrete recovery protocol. The initiative remains in progress until implementation acceptance covers every required platform and the actual image.

Agent decision at C:40, without asking: add Starlette 1.7.0 as a direct dependency because the adapters directly import its ASGI types, exceptions and response class. The jointly installed runtime resolves against the pins in `pyproject.toml`; HTTPX 0.28.1 remains the approved test dependency. The current Starlette TestClient emits a deprecation warning for HTTPX, without failing the checks. Exception implementations end in `Error` to satisfy N818 and expose aliases matching the planned public names.

Agent decision at C:40, without asking: a second inherited Linux activity descriptor proves every compliant descendant has stopped before normal cleanup, while the permanent admission descriptor retains cross-crash exclusion. The supervisor runs absolute executables without a shell and suppresses raw output. A failed recovery journal validation or unexpected private-directory entry preserves evidence and refuses admission. Empty UUID directories or an initial journal.pending alone are recovered before any workspace could have been admitted. This closes crash windows around initial journal creation and final directory removal without guessing ownership of actual work.

Implemented configuration, common time, logging, the API foundation, administrative wrapper, engine factories, the two database lock keys, journal recovery, publication outcomes and Linux/Windows process supervision. Added the local image/bootstrap/Compose and an empty Alembic runner. No product revision, extension activation, product grant, endpoint, importer-owned file, routing pointer or hosted service was changed. The consumer handoff and actual-tool descriptor requirement are in `docs/setup/backend.md`.

### Executed evidence

- Joint runtime installation succeeded in a task-owned temporary directory on Python 3.14.4. Python 3.13 is not installed on this executor.
- The final complete suite excluding the separately rehearsed production-ceiling case: 181 passed, one native Windows case skipped, one 120-second case deselected. The run uses `APP_ENVIRONMENT=local`, a restricted service account and explicit maintenance credentials only for registered scratch setup. Scratch cleanup names the exact registered table.
- A real PostgreSQL 18.6 rehearsal of the 80-second wait plus 50-second statement stopped at the shared 120-second ceiling and left the scratch write invisible. The same initial run found a stale-guard exception classification failure; the subsequent corrected short critical suite passed. Deadline enforcement was unchanged by that correction.
- Real database checks cover UTC, Polish case conversion and UTF-8 round trip, restricted role capabilities, no-wait admission, stale guard refusal, atomically visible committed writes, shortened server timeout, repeated short statements sharing one budget, commit-phase timeout and a deliberately lost acknowledgement after an actual successful scratch COMMIT. The latter returns unknown while another connection observes the committed row.
- A real owner-process crash with a live orphan writer preserved local exclusion after owner/session loss. The next manual launch was refused while the child lived, then recovered its private files before admitting new work. A separate fork test waits for a descendant after its immediate parent exits.
- A real `python -m api` process responded to local HTTP with the exact 404 envelope and correlation header while its invented database URL pointed to an unavailable database. Invalid port configuration exited 1 without printing the invalid value. No migration or import ran.
- Target critical selection is refused with exit 4 before write fixtures, both in a normal run and during collect-only. Architecture, template-entry parity and existing repository gates passed.
- `alembic heads` and `alembic history` returned an empty revision chain. `sh -n database/bootstrap.sh` passed. Compose configuration passed against task-owned copies of the example files; it creates no service and is not a database-image acceptance run.
- Ruff lint/format, mypy over 26 production/hook/runner files, Vulture, deptry, scoped Bandit including the separate B608 pass, and pinned Prettier passed. The dependency vulnerability audit of the complete newly installed runtime reported no known vulnerabilities. Bandit suppressions are narrow and justified next to their makefile invocations: environment filenames reported as credentials, the trusted absolute non-shell supervisor, and Windows argv encoding.
- Sandbox restrictions on local sockets and dependency downloads required explicit escalated runs. The isolated database, runtime tools, Node and formatter were prepared under `/tmp`; no system package was installed and no hosted environment was accessed.

### Blockers

B-1. `database/Dockerfile` and `compose.local.yml`: actual image build, fresh/repeated volume startup, extension-file availability and replacement-container workspace persistence are unverified. Docker socket access is denied even outside the sandbox, and sudo requires interactive authentication. Native PostgreSQL checks do not replace image acceptance.

B-2. `data/windows_job.py` and `tests/data/test_windows_job_critical.py`: native Windows x64, Docker Desktop setup and the crash/descendant containment acceptance must run on Windows. A Linux skip is not evidence. Python 3.13 confirmation also remains outstanding; this executor runs 3.14.4.

B-3. `docs/setup/backend.md`, shared interfaces: Mateusz must verify that each actual mutating import tool preserves the Linux descriptors and containment contract, and provide the persistent container workspace mount. The invented cooperative tools prove the foundation protocol only. No actual importer or pointer-recovery readiness is claimed.

### Risks

R-1. Loss of database connectivity can keep completion monitoring and exclusion active indefinitely. Every individual connection/query wait is bounded; refusing fresh work without authoritative completion is deliberate. It does not retry publication or claim a rollback.

R-2. The callback is a trusted synchronous interface. It must use the provided connection and cannot alter transaction/timeout settings, use raw driver operations or launch detached work. Consumer implementation needs to obey that boundary.

R-3. Starlette warns that its HTTPX TestClient integration is deprecated. This is test-only and currently passes; changing the agreed test dependency is not part of this delivery.

### Improvements

No optional rewrite is required for the verified Linux foundation. Native platform and image runs must precede a ready verdict.

### Verification

| Standard         | State and evidence                                                                                                                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agentic workflow | Checked automatically: parity, hook and dangerous-command tests passed; reviewed append-only artifacts and ownership manually.                                                         |
| Agent docs       | Checked automatically: plan contract tests passed; memory records preserve durable boundaries rather than task status.                                                                 |
| Review           | Checked manually against the full checklist and the plan acceptance criteria.                                                                                                          |
| Documentation    | Checked manually: runbook describes shared interfaces and prerequisites; layer memories explicitly defer module document pairs until a domain rule exists.                             |
| Formatting       | Checked automatically: Ruff, pinned Prettier and prose gates passed.                                                                                                                   |
| Git              | Checked automatically: no conflict markers; checked manually: no commit, push, rebase or new staging. The resolved merge still awaits a human commit.                                  |
| Architecture     | Checked manually and with new layer/engine-construction gates.                                                                                                                         |
| Configuration    | Checked automatically: pure cases, template contract, real safe startup and target guard.                                                                                              |
| Database         | Checked automatically: B608 and local critical queries; manually reviewed account separation and absence of product schema changes. Image-specific acceptance is incomplete under B-1. |
| Errors           | Checked manually and with API, rollback, uncertain-commit and cleanup scenarios.                                                                                                       |
| Idempotency      | Checked manually: no product idempotency rule is introduced; try-lock admission and exact recovery identity are tested.                                                                |
| Code quality     | Checked automatically: Ruff, mypy, Vulture and deptry passed.                                                                                                                          |
| Logging          | Checked automatically with Ruff G and redaction/correlation tests; reviewed the request-field allowlist manually.                                                                      |
| Naming           | Checked automatically with Ruff N; public aliases and registry reviewed manually.                                                                                                      |
| Security         | Checked automatically: scoped Bandit and new-runtime pip-audit passed. No actual hosted address, credential or personal data was introduced.                                           |
| Tests            | Checked automatically: local suite, refusal guard and actual database scenarios; native Windows and image acceptance remain incomplete.                                                |
| Time             | Checked manually and with aware-time/deadline cases, UTC sessions and the real 120-second rehearsal. No product time storage model was introduced.                                     |
| Worker           | Not applicable to periodic execution: the package has no task, registry or schedule. Its dependency boundary is tested.                                                                |
| Frontend         | Not applicable: no frontend code or interface was changed.                                                                                                                             |

### Verdict

Not ready for the whole backend skeleton initiative: B-1 - B-3 remain. The implemented Linux foundation has executable evidence, but that partial scope does not qualify the initiative for archive. Keep `plans/backend_skeleton/` in place. A human creates the merge commit and any implementation commits; no unsolicited staging or history changes are authorized.

## 2026-10-04 - Final review fixes and evidence refresh

Fixed malformed environment-file startup to exit through the safe configuration boundary, preserving the filename without values or a raw traceback. Added a process-level regression. Exception paths now record redacted diagnostics, and the shared logger installs a NullHandler until the entry point configures it, preventing logging.lastResort from rendering an unredacted exception. The Linux supervisor terminates and waits for its contained writer group on deadline or interruption; strict journal models reject coercion of recovery metadata. The targeted workspace/process regression passed all eight cases after those changes.

Agent decision at C:40, without asking: declare tzdata 2026.5, verified from the package index, because the accepted Windows target cannot assume an installed IANA timezone database. [Python's zoneinfo data-source documentation](https://docs.python.org/3.13/library/zoneinfo.html#data-sources) explicitly recommends this dependency for cross-platform applications. It supplies the user's configured business timezone and introduces no guessed default. The standard library loads it implicitly; deptry's narrow unused-import exception is recorded beside the CLI-only Alembic dependency.

The refreshed full short suite passed 182 tests with one native Windows skip and the separately verified production-ceiling case deselected. Mypy, Ruff, Vulture, deptry, Bandit and pinned Prettier were rerun after the relevant fixes. No platform blocker is removed by these runs. The verdict remains not ready for the whole initiative, with B-1 - B-3 unchanged; no archive move, commit, push or new staging follows.

Added native-only Windows success, whole-descendant deadline and owner-crash recovery cases for the required executor handoff. They remain unexecuted here. A forced empty system timezone search confirmed package-provided `Europe/Warsaw`; the refreshed runtime vulnerability audit, including tzdata, found no known vulnerabilities. Exact scratch cleanup was confirmed, the test-only service role was removed and the task-owned native PostgreSQL server was stopped. No existing service was stopped.

`tests/data/test_database_setup_critical.py` supplies the image-specific extension-file and encoding/byte-order assertions for the real Compose acceptance run. They were not counted in the native PostgreSQL suite: the temporary bare server has no project extension packages and cannot establish B-1. This additional handoff does not change the verdict.

## 2026-10-04 - Alignment with the database package of db/ at the merge of mw-osm-import

The merge of `mw-osm-import` brought the skeleton next to the package `db/` of `plans/schema_first_revision/`, giving two local databases, two Alembic configurations and two sets of database entries: the clash `plans/accounts/ACCOUNTS_PLAN.md` F-13 recorded. The user settled it in favor of Kuba's `SCHEMA_FIRST_REVISION_PLAN.md` D-14 and D-15 and chose that the backend builds its address from the `DB_` entries. The plan records the change on D-2, D-4, D-9, D-10, D-15, S-4 and S-7.

Changed: `config/settings.py` and `config/config.py` read `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_SERVICE_ACCOUNT_NAME` and `DB_SERVICE_ACCOUNT_PASSWORD` in place of `DATABASE_URL`; `data/engine.py` builds the address with `build_database_url()` and no longer has `build_migration_engine`; the scratch fixture of `tests/data/conftest.py` builds the schema-owner engine itself; `tests/data/test_engine_critical.py` keeps only the session checks of the backend engine; the targets `db-build`, `db-up`, `db-down`, `migration-heads` and `migration-history`, the Bandit scans of `alembic`, the root dependency `alembic` and its deptry exception are removed; `docs/setup/backend.md`, `README.md`, `docs/standards/standard_config.md` and `docs/standards/naming_registry.md` follow.

Not done: `database/`, `alembic/`, `alembic.ini`, `compose.local.yml` and `tests/data/test_database_setup_critical.py` are still in the tree, because their deletion was refused to the agent by the permission mode; a human removes them. The backend entries `APP_ENVIRONMENT`, `API_BIND_HOST`, `API_PORT`, `BUSINESS_TIMEZONE`, `LOG_LEVEL` and `IMPORT_WORKSPACE_ROOT` still have no template line and no record in `docs/standards/standard_config.md`, as D-4 required.

Verification on Windows with Python 3.13: Ruff check and format pass; the tests of `tests/config/`, `tests/api/`, the administrative wrapper, the critical guard, the layer boundaries, the environment contract and the plan contract give 73 passed and 3 skipped; Bandit passes on `config`, `api`, `data`, `worker` and `common_time.py`; deptry reports only `mobile_app`. Mypy reports 12 errors, all in `data/import_process.py` and `data/osm_valhalla.py`, which use Linux-only APIs. The full non-critical run fails outside this change: the prose gates on `mobile_app/`, the pyosmium cases on a temporary path with a non-ASCII user name and the Linux process cases of Valhalla. No critical test ran, because no local database of `db/` was up.

### Verdict

The clash with `db/` is removed from the code and the documents of the skeleton, except the files a human still deletes. The verdict of the initiative is unchanged: B-1 - B-3 remain, and `plans/backend_skeleton/` stays in place.

## 2026-10-04 - Windows acceptance with the database of db/ and the template gap closed

Scope: B-1 and B-2 of the entry "Recovery design closed and foundation implemented" after the alignment with `db/`, the template gap the previous entry left, the classification of B-3, and the Windows gates of the skeleton files. Executor: Windows 11 x64 with Python 3.13.14 in an isolated virtual environment of the session and Docker 29.6.1 (plan F-30). The stale `database/`, `alembic/`, `alembic.ini`, `compose.local.yml` and `tests/data/test_database_setup_critical.py` were removed by the user's commit `e1d621c` before this work.

The user answered two proposals of this session on 2026-10-04 with "pozwalam ci to zrobić, zrób co możesz, dopinajmy to" (English: "I allow you to do it, do what you can, let's wrap it up"): an empty `LOG_LEVEL` marker means the default `INFO`, and B-3 is a handoff to the consumer, not a blocker of the skeleton. The plan records the first on D-4.

Changed:

- `.env.local.example` holds `APP_ENVIRONMENT`, `API_BIND_HOST`, `API_PORT`, `BUSINESS_TIMEZONE`, `LOG_LEVEL` and `IMPORT_WORKSPACE_ROOT` as empty markers, and `docs/standards/standard_config.md`, section Environment entries, records each with its requiredness and its behavior when missing. `docs/setup/backend.md` no longer says that these entries are added by hand.
- `config/settings.py` reads an empty `LOG_LEVEL` as `DEFAULT_LOG_LEVEL` through `build_log_level`, the same way `build_workspace_path` reads an empty `IMPORT_WORKSPACE_ROOT` as unconfigured. `tests/config/test_settings_cases.py` checks that every required backend entry left empty is refused by name and that an empty log level gives `INFO`.
- `data/import_process.py`: `fetch_activity_completion` and `apply_linux_process` refuse a platform other than Linux with `ImportWorkspaceUnconfirmed`, in the form mypy narrows, the idiom `fetch_kernel_api` of `data/windows_job.py` already uses. Before this, mypy on Windows reported 10 errors in this file.
- `tests/data/test_import_exclusion_critical.py`: `test_next_manual_launch_recovers_after_owner_crash` failed on Windows, because it encodes the Linux semantics in which a contained writer outlives its killed owner. The shared helper `apply_owner_crash` now starts and kills the owner; the Linux test keeps its expectations, and the new `test_next_manual_launch_recovers_after_windows_owner_crash` checks with the real database that a child meant to run for 30 seconds ends with its owner and that the next launch is admitted within 10 seconds after recovering the private files.
- The plan: the state line, F-30, and the change notes on D-3 and D-4.

Agent decision at C:40, without asking: the owner-crash test was split instead of skipped on Windows. D-18 decides that a Windows job with kill-on-close ends the whole tree with its last handle, so on Windows an orphan writer cannot exist and the observable requirement of AC-8 is the immediate recovery on the next launch; the Windows variant proves it on the database path that the workspace-only `test_windows_owner_crash_is_recovered_on_next_manual_launch` does not cover.

### Executed evidence

- The local database of `db/compose.yaml` built and started healthy under a task-owned Compose project with generated local test values kept in the session scratch directory; no environment file of the repository was created or read.
- Before any revision: the critical suite of the skeleton gave 12 passed and 1 skipped (the Linux orphan variant), with the 120-second case deselected; this includes the three native Windows Job Object cases and the Windows owner-crash case with the database. The production-ceiling case passed separately in 120.09 seconds.
- `python -m api`, with the `DB_` entries given at launch and empty `LOG_LEVEL` and `IMPORT_WORKSPACE_ROOT`, answered an unknown GET path and `DELETE /` with 404 and `{"error":{"code":"not_found"}}`, kept a supplied `X-Request-Id` and generated a missing one, and logged one line per request with method, operation, status, duration and request identifier only. The process was stopped after the check.
- The profile `migrate` applied the chain: `alembic_version` is `0001`, read as the schema owner; the service account is refused reading it, as its rights intend. The profile `test` ran `db/tests`: 26 passed.
- After the revision the critical suite of the skeleton again gave 12 passed and 1 skipped, and no `public.backend_skeleton_scratch` was left.
- The non-critical suite passes for every skeleton test. Its 7 failures are outside the skeleton: the prose gates on `mobile_app/`, three pyosmium cases of `osm_importer` that cannot open a temporary path with a non-ASCII user name, and two Linux process cases of `data/osm_valhalla.py`.
- Mypy: no error in the skeleton files on Windows and with `--platform linux`; two errors remain in `data/osm_valhalla.py`, which calls `os.killpg` and `signal.SIGKILL` without a platform guard. Ruff check and format, vulture and every Bandit pass of the target `security` for the skeleton paths are clean; Ruff and deptry report only `mobile_app/`. pip-audit found no known vulnerability in the project dependencies; it reported only `pip` of the tool environment (PYSEC-2026-3721) and could not audit the local `accessibility-db`. Pinned Prettier formatted the changed documents.
- Linux run of the changed Linux-only code: a `python:3.13-slim` container with Python 3.13.16, the repository mounted read-only and the network of the same database of `db/` gave 9 passed and 4 skipped (the Windows-only cases) for the critical files of the skeleton, the refactored `test_next_manual_launch_recovers_after_owner_crash` included, and 8 passed for `tests/data/test_import_process_integration.py` and `tests/data/test_import_workspace_cases.py`.
- The task-owned Compose containers, network and the images built for the checks were removed; the pulled base image `python:3.13-slim` stays, as it is also the base of `db/image/Dockerfile.tools`. No hosted environment was accessed and no existing container was stopped.

### Blockers

None for the skeleton. B-1 is closed: the database image is the one of `db/`, which built and served the whole acceptance here; the persistence of the import workspace across replacement containers belongs to the container configuration of its consumer (`docs/setup/backend.md`, section Configuration). B-2 is closed by the native Windows runs above with Python 3.13. B-3 is a handoff to Mateusz by the user's decision: D-18 makes the verification of each actual mutating tool a condition of importer readiness.

### Risks

R-1. `make typecheck` and the full `make check` still fail on Windows because of `data/osm_valhalla.py` of `osm_importer` and of `mobile_app/`; their owners fix them.

R-2. `import osmium` fails in `python:3.13-slim` with a missing `libexpat.so.1`, so six test modules of `osm_importer` do not even collect there. It does not touch the skeleton, but every Linux image that runs the import, the backend image of D-14 included, needs that system library; it is a handoff to Mateusz and to `plans/deployment_config/`.

R-3. `plans/accounts/ACCOUNTS_PLAN.md` F-13 and `plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md` still describe two local database setups; both are work in progress of other sessions and were not edited.

R-4. A developer whose `.env.local` predates this change fails the environment contract test until the six new entries are added to it.

### Improvements

None required. The skeleton tests could be collected without the modules of `osm_importer` on a machine without `libexpat`, but that is a property of those modules, not of the foundation.

### Verification

| Standard         | State and evidence                                                                                                                                                                                                                      |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agentic workflow | Checked automatically: the parity, vendored content, session-context hook and dangerous-command tests passed; the handoff with the parallel session followed ch. 4.7.                                                                   |
| Agent docs       | Checked automatically: the plan contract test passed with F-30; the memory entry is a durable platform pattern, not a task status.                                                                                                      |
| Review           | Checked manually against the checklist of `standard_review.md` and AC-1 - AC-15 of the PRD.                                                                                                                                             |
| Documentation    | Checked manually: `docs/setup/backend.md` and the section Environment entries describe the actual template; every new function has a docstring.                                                                                         |
| Formatting       | Checked automatically: Ruff format and Prettier pass on the changed files; the prose gate fails only on `mobile_app/`, outside this change. No line comment and no forbidden character in the changed code.                             |
| Git              | Checked automatically: no conflict markers. No commit, push, staging or rebase by the agent; the user committed the work as `e1d621c` and `ea782db`.                                                                                    |
| Architecture     | Checked automatically: the layer boundary test passed.                                                                                                                                                                                  |
| Configuration    | Checked automatically: the environment contract test and the critical environment guard passed; the contract against a local `.env.local` was skipped, as no such file exists on this executor.                                         |
| Database         | Checked automatically: Bandit B608 clean; the service account is refused `alembic_version`, and the scratch fixture leaves nothing behind.                                                                                              |
| Errors           | Checked manually and by the live 404 envelope and the rollback, timeout and unknown-commit cases on Windows and Linux.                                                                                                                  |
| Idempotency      | Not applicable: the change introduces no repeatable product operation.                                                                                                                                                                  |
| Code quality     | Checked automatically: Ruff, vulture and deptry clean for the skeleton; mypy clean for the skeleton on Windows and with `--platform linux`, with two errors left in `data/osm_valhalla.py` of `osm_importer` (R-1).                     |
| Logging          | Checked automatically with Ruff G; the live request log carries only the allowlisted fields.                                                                                                                                            |
| Naming           | Checked automatically with Ruff N; `DEFAULT_LOG_LEVEL`, `build_log_level` and `apply_owner_crash` follow `standard_naming.md`.                                                                                                          |
| Security         | Checked automatically: every Bandit pass of the skeleton paths clean; pip-audit found no known vulnerability in the project dependencies. Test credentials were generated, kept outside the repository and destroyed with the database. |
| Tests            | Checked automatically: the skeleton suites on Windows, the critical suite on Windows and Linux against the database of `db/`, the 120-second ceiling and `db/tests`.                                                                    |
| Time             | Checked manually: no change of time handling; the deadline cases pass on both platforms.                                                                                                                                                |
| Worker           | Not applicable: no periodic task exists.                                                                                                                                                                                                |
| Frontend         | Not applicable: no frontend file changed.                                                                                                                                                                                               |

### Verdict

Ready, for the whole backend skeleton initiative. Every acceptance criterion of the PRD has a passing run on the agreed systems: Windows x64 natively in this entry, Linux x64 in the entry "Recovery design closed and foundation implemented" and in the container run above, with the local database of `db/` that replaced the skeleton's own setup. B-1 and B-2 are closed by runs and B-3 is a consumer handoff by the user's decision. R-1 - R-4 belong to other initiatives or to each developer's local file and do not undermine the completion. The initiative qualifies for `plans_finished/backend_skeleton/`; check 2.1 of `FINAL_CHECKLIST.md` is ticked by a person.
