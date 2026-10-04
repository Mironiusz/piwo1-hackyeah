# Plan: Tile-archive step of the common demo-loading program

Document state: 2026-10-04, plan closed; implemented and reviewed as ready, see `TILE_LOADING_REVIEW.md`

## Goal

Meet FR-1 - FR-7 of `plans_finished/tile_loading/TILE_LOADING_PRD.md`: a tile step in three layers - file operations in `data/tile_archive.py`, the decisions and the exclusion in `service/tile_archive.py`, and the command `python -m worker.tile_archive` in `worker/tile_archive.py` - with two administrative environment entries, its tests, the contract written into `docs/deployment/loading_program.md` for `plans/osm_import/` to compose, and the corrections of every document of FR-7.

## Facts

F-1. No code loads the archive: `worker/` holds only `__init__.py`, `gtfs_import.py` and `osm_import.py`, and neither `service/` nor `data/` has a module with tile in its name. | cmd:`ls worker` -> `__init__.py gtfs_import.py osm_import.py`; cmd:`ls service data` -> no file named with tile | 2026-10-04
F-2. The archive of the hosted demo is `krakow.pmtiles`, 34 785 215 bytes, SHA-256 `21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1`, asked for by the browser at `/tiles/krakow.pmtiles`. | doc:`docs/setup/MAP_SETUP.md` sections What the map needs and The tile archive | 2026-10-04
F-3. The GTFS step takes the exclusion of the importer through `build_import_engine(GTFS_IMPORT_GUARD_STATEMENT_TIMEOUT_MS)` with the value 5000 and `apply_import_exclusion(engine, settings.workspace_root)`, returns its outcome `skipped` on `ImportAlreadyRunning`, and disposes the engine on every path. | code:`service/gtfs_import.py` function `apply_gtfs_import` and constant `GTFS_IMPORT_GUARD_STATEMENT_TIMEOUT_MS` | 2026-10-04
F-4. `apply_import_exclusion(engine, workspace_root)` takes the local admission lock of the workspace and two PostgreSQL advisory keys without waiting, raises `ImportAlreadyRunning` when another holder has them, and can raise `ImportWorkspaceUnconfirmed` when its context closes. | code:`data/locks.py` function `apply_import_exclusion`; code:`data/local_lock.py` class `ImportAlreadyRunning`; code:`data/import_workspace.py` class `ImportWorkspaceUnconfirmed` | 2026-10-04
F-5. The common loading program holds the import exclusion through all three steps, and it and standalone imports refuse each other at once. | doc:`plans/osm_import/OSM_IMPORT_PLAN.md` D-10, D-11 and D-14 | 2026-10-04
F-6. Every provider step has its own finite whole-step budget, and the tile value and its enforcement are still open in the loading contract. | doc:`plans/osm_import/OSM_IMPORT_PLAN.md` D-13; doc:`docs/deployment/loading_program.md` sections Approved execution budgets and Remaining integration requirements | 2026-10-04
F-7. The summary of the common program shows no path, exception text or connection value. | doc:`plans/osm_import/OSM_IMPORT_PLAN.md` D-17 | 2026-10-04
F-8. The proposed common records name the effect `tile_archive`, a filesystem-only effect without commit state, and the proposal is not approved. | doc:`docs/deployment/loading_program.md` section Proposed common result contract; doc:`plans/osm_import/OSM_IMPORT_PLAN.md` D-18 | 2026-10-04
F-9. The sample provider is a synchronous service callable that takes no lease, returns its own result record, raises a named failure with fixed reason codes and adds no worker command. | doc:`plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md` sections Callable and records and Failure contract | 2026-10-04
F-10. `common_time.py` has `build_deadline(seconds, now)`, `fetch_monotonic_seconds()`, the record `Deadline(expires_at)` and `resolve_remaining_milliseconds(deadline, now)`, which raises `DeadlineExpiredError` when less than a millisecond is left. | code:`common_time.py` functions `build_deadline`, `fetch_monotonic_seconds`, `resolve_remaining_milliseconds`, classes `Deadline` and `DeadlineExpiredError` | 2026-10-04
F-11. The repository replaces a file atomically through `tempfile.NamedTemporaryFile(dir=..., prefix=..., delete=False)`, `flush`, `os.fsync`, `os.replace` and an unlink of the temporary file on failure, and syncs the directory only when `sys.platform == "linux"`. | code:`data/routing_data.py` function `apply_routing_pointer`; code:`data/import_workspace.py` function `apply_journal_write` | 2026-10-04
F-12. The repository hashes a file with `hashlib.file_digest(stream, "sha256")` and refuses a link with `path.is_symlink()`. | code:`data/routing_data.py` function `fetch_routing_file_digest` | 2026-10-04
F-13. A worker entry point reads its entries from `config.config` inside a builder, names every missing one with `ConfigurationError` and the file of `ENVIRONMENT_ENTRY_FILES`, writes one outcome line through `fetch_logger`, maps outcomes to exit codes with `skipped` as 2, logs a named failure with its constant message and passes any other failure on to `apply_administrative_run`, which logs it and exits 1. | code:`worker/osm_import.py` functions `build_osm_import_settings`, `apply_osm_import_report`, `apply_osm_import_action` and constant `OSM_IMPORT_EXIT_CODES`; code:`service/administrative.py` function `apply_administrative_run` | 2026-10-04
F-14. An administrative path entry is `Path | None` with the default `None`, an empty value becomes `None`, a relative path stops the facade with its name, and the facade exposes each entry as a constant. | code:`config/settings.py` class `Settings`, validators `build_path_entry` and `apply_absolute_path_validation`, constant `ENVIRONMENT_ENTRY_FILES`; code:`config/config.py` | 2026-10-04
F-15. Every entry of a template has a record in the section Environment entries of the configuration standard, every template holds only empty markers, and `.env.local.example` ends with `PUBLIC_TRANSPORT_ENABLED=`. | code:`tests/architecture/test_environment_contract.py` functions `test_every_template_entry_has_a_record_in_the_configuration_standard` and `test_every_template_holds_only_empty_markers`; cmd:`cat .env.local.example` -> 16 entries, the last `PUBLIC_TRANSPORT_ENABLED=` | 2026-10-04
F-16. This machine has no `.env` or `.env.local` and no copy of the archive, so the local-file contract test skips and no run on the real file is possible here. | cmd:Glob `.env*` -> `.env.example .env.local.example`; cmd:`ls frontend/public/tiles/` -> `No such file or directory` | 2026-10-04
F-17. The worker layer may not import `data`, and the service layer may not import `worker`. | code:`tests/architecture/test_layer_boundaries.py` constant `FORBIDDEN` | 2026-10-04
F-18. Worker tests stand in for the facade with a module put into `sys.modules` and capture the logger `piwo1-hackyeah`; service tests of a busy exclusion replace `apply_import_exclusion` in the service module under the `integration` marker on `tmp_path`; data tests on `tmp_path` carry the `_cases` suffix. | code:`tests/worker/test_gtfs_import_cases.py` function `apply_invented_config` and fixture `report`; code:`tests/service/test_gtfs_import_integration.py` function `test_another_run_holding_the_exclusion_gives_skipped` and `pytestmark`; cmd:`grep -ln tmp_path tests/data/*_cases.py` -> `test_import_workspace_cases.py test_osm_source_cases.py test_routing_data_cases.py` | 2026-10-04
F-19. The settings tests list invalid relative paths of the administrative entries in `test_invalid_entries_do_not_leak_values` and check empty ones in `test_optional_valhalla_paths_do_not_block_api_configuration`. | code:`tests/config/test_settings_cases.py` functions `test_invalid_entries_do_not_leak_values` and `test_optional_valhalla_paths_do_not_block_api_configuration` | 2026-10-04
F-20. The virtual environment runs Python 3.13.14 with `hashlib.file_digest`, and has `ruff`, `mypy` and `bandit`. | cmd:`venv/Scripts/python.exe -c "import sys,hashlib;print(sys.version.split()[0], hasattr(hashlib,'file_digest'))"` -> `3.13.14 True`; cmd:`ls venv/Scripts` -> `ruff.exe`, `mypy.exe`, `bandit.exe` | 2026-10-04
F-21. The code unit documents of the service and data layers carry one section per loading step, for example `## GTFS step`, and the naming registry one section of names per initiative, for example `## Public transport names`. | cmd:`grep -n "^#" service/SERVICE.md service/SERVICE_ALGORITHM.md data/DATA.md data/DATA_ALGORITHM.md` -> `## GTFS step` in each; doc:`docs/standards/naming_registry.md` section Public transport names | 2026-10-04
F-22. No configuration of the proxy or of the application services exists, and the deployment configuration still holds the question how the archive reaches the server. | cmd:`git ls-files` filtered by compose -> `db/compose.deploy.yaml db/compose.yaml`; doc:`plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md` section Open questions, item 3 | 2026-10-04
F-23. `MVP.md` asks that a change making one of its items untrue updates it in the same change; its row of `plans/osm_import/` says that `map_tiles` adds a step, and its section Open decisions and confirmations records the loading of the archive as unconfirmed. | doc:`MVP.md` sections Why this document exists, Initiatives and Open decisions and confirmations | 2026-10-04
F-24. Check 3.4 of `FINAL_CHECKLIST.md` is named `map_tiles`, the loading step, and waits for check 3.2; the stage of an initiative is one more than the highest stage it waits for; check 7.1 waits for 3.4. | doc:`FINAL_CHECKLIST.md` sections Stages, Set 3 and Set 7 | 2026-10-04
F-25. `plans/map_tiles/` was moved to `plans_finished/map_tiles/` by another session on 2026-10-04, which also repointed the references in `MVP.md`, `docs/setup/MAP_SETUP.md`, `plans/osm_import/` and `plans/deployment_config/`. | cmd:`git status --short plans` -> `D plans/map_tiles/MAP_TILES_PLAN.md` and the other files of that directory; cmd:`ls plans_finished/map_tiles` -> `MAP_TILES_PLAN.md MAP_TILES_PRD.md MAP_TILES_REVIEW.md MAP_TILES_SEED.md MAP_TILES_SHAPE.md STAGE.md` | 2026-10-04

## Decisions

D-1. Three layers and the command. `data/tile_archive.py` reads, copies and places files; `service/tile_archive.py` decides what a run does and takes the exclusion; `worker/tile_archive.py` is the command `python -m worker.tile_archive`. Agent decision at C:40, without asking: the same split as the GTFS step (F-3, F-13), and the only one the layer boundaries allow (F-17).

D-2. The accepted archive is two constants of `service/tile_archive.py`: `TILE_ARCHIVE_NAME = "krakow.pmtiles"` and `TILE_ARCHIVE_SHA256 = "21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1"` (F-2). Agent decision at C:40, without asking: a value constant across environments and used in one place belongs to the third layer of `docs/standards/standard_config.md`, section Rule for assigning a value to a layer, and the domain rule of the PRD accepts no other file.

D-3. Two administrative environment entries in `.env.local.example`: `TILE_ARCHIVE_SOURCE`, the absolute path of the file a person put on the server, and `TILE_ARCHIVE_DIR`, the absolute path of the directory the proxy serves; the served file is `TILE_ARCHIVE_DIR/krakow.pmtiles`. Like `IMPORT_WORKSPACE_ROOT`, each is `Path | None`, empty means unset, a relative path stops the facade, and the API never needs them (F-14). Agent decision at C:40, without asking: the values depend on the machine and are no secret, so they belong to the local values file, and only an administrative run reads them (`docs/standards/standard_config.md`, section Validating values from the environment).

D-4. The command takes the exclusion of the importer exactly as the GTFS step does: `build_import_engine(TILE_ARCHIVE_GUARD_STATEMENT_TIMEOUT_MS)` with 5000, `apply_import_exclusion(engine, workspace_root)` with `IMPORT_WORKSPACE_ROOT`, the outcome `skipped` when it is busy, and the engine disposed on every path (F-3, F-4). A consequence: the command needs the database and the workspace, and it also refuses while a standalone OpenStreetMap import or GTFS step runs, and they refuse while it runs. Agent decision at C:40, without asking: the common program holds this exclusion through the tile step (F-5), so only this one gives FR-5, and a second lock for the same purpose is forbidden by `docs/standards/standard_architecture.md`, section Shared helpers.

D-5. The step the common program composes is `apply_tile_archive_run(settings, deadline)`. It takes no lease and acquires no exclusion; the common program holds the exclusion around it, and the validation of a lease across provider steps stays with question Q-5 of `plans/osm_import/OSM_IMPORT_PLAN.md`. Agent decision at C:40, without asking: the precedent of the sample provider (F-9), and the step writes no database.

D-6. The whole-step budget is `TILE_ARCHIVE_RUN_SECONDS = 120`. It is enforced by `resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())` before every chunk of `TILE_FILE_CHUNK_BYTES = 1048576` bytes of each read and write, and once more before the placement; an expired budget removes the temporary file and ends the step with the reason `deadline_expired`. A system call that blocks inside one chunk is not interrupted. Agent decision at C:40, without asking: three reads and one write of 34.8 MB take seconds on a local disk, and 120 seconds leaves room for a slow disk while staying finite, as `plans/osm_import/OSM_IMPORT_PLAN.md` D-13 asks.

D-7. The order of a run of `apply_tile_archive_run`, which implements FR-1 - FR-3:

1. Refuse a source path inside the served directory: `places_overlap`.
2. Refuse a missing served directory: `served_directory_missing`.
3. Remove the temporary files an earlier run left in the served directory: a failure gives `copy_failed`.
4. Read the digest of the served file. Equal to `TILE_ARCHIVE_SHA256`: return `unchanged` without touching the source. A read failure: `served_unreadable`.
5. Read the digest of the source: no file gives `source_missing`, a read failure `source_unreadable`, another value `source_mismatch`.
6. Copy the source into a new temporary file in the served directory: a failure gives `copy_failed`.
7. Read the digest of the temporary file: another value gives `copy_mismatch`.
8. Check the budget, then put the temporary file under the served name with one `os.replace` and sync the directory on Linux: a failure gives `copy_failed`.
9. On every path that ends before step 8 succeeds, remove the temporary file.

Return `loaded`. Agent decision at C:40, without asking: the order follows FR-1 - FR-3, and the temporary file lies in the served directory so that `os.replace` stays on one file system (F-11).

D-8. Records and failures. `TileArchiveResult(outcome)` with `TileArchiveOutcome` = `loaded`, `unchanged` or `skipped`; `TileArchiveError(reason)` with `TileArchiveFailureReason` = `places_overlap`, `served_directory_missing`, `served_unreadable`, `source_missing`, `source_unreadable`, `source_mismatch`, `copy_failed`, `copy_mismatch` or `deadline_expired`, and the constant message `Tile archive step failed: <reason>`, which names no path. `TILE_ARCHIVE_NAMED_ERRORS = (TileArchiveError, ImportWorkspaceUnconfirmed)` lists the failures whose messages the operator may see. The file operations raise `TileFileError` with constant messages, and the service turns it into the reason of its step. Agent decision at C:40, without asking: the shape of the sample and GTFS failures (F-9, F-13), and FR-6 asks for fixed codes without a location.

D-9. The command exits 0 for `loaded` and `unchanged`, 2 for `skipped`, and 1 for a named failure or, through `apply_administrative_run`, for any other exception. It writes one line, `Tile archive outcome=<outcome> duration_s=<seconds>` at INFO, or `Tile archive outcome=failed cause=<type>: <message> duration_s=<seconds>` at ERROR, without a path. Agent decision at C:40, without asking: the codes and lines of `worker/osm_import.py` (F-13); a skipped run is information, as `docs/standards/standard_worker.md`, section Locks, asks.

D-10. A link at either place counts as no file: a source that is a link gives `source_missing`, and a link under the served name is replaced by the archive. Agent decision at C:40, without asking: the step writes into a directory served to everyone, and following a link could read or overwrite a file outside the two places (F-12).

D-11. Tests without a critical test. `tests/data/test_tile_archive_cases.py` checks the file operations on `tmp_path`; `tests/service/test_tile_archive_integration.py` checks AC-1 - AC-5, AC-7 and AC-8 on `tmp_path` with an invented archive of 2 000 000 bytes whose digest replaces `TILE_ARCHIVE_SHA256` through `monkeypatch`, and a stand-in exclusion; `tests/worker/test_tile_archive_cases.py` checks AC-6 with an invented facade; `tests/config/test_settings_cases.py` gets the two entries. Agent decision at C:40, without asking: the step itself reads and writes no database, the exclusion it reuses has its own critical test in `tests/data/test_import_exclusion_critical.py`, and the GTFS step is tested the same way (F-18).

D-12. The contract of FR-6 is one new section of `docs/deployment/loading_program.md`, Tile-provider handoff, not a separate handoff file. Agent decision at C:40, without asking: one place for the contract the common program reads, and FR-7 already corrects that document.

D-13. This initiative stands at stage 4 of `FINAL_CHECKLIST.md`: its check 3.4 waits for check 3.2 of `osm_import`, at stage 3 (F-24). Its row in `MVP.md` names Rafał as the owner (`TILE_LOADING_SHAPE.md`, Recipient and trigger), and the naming registry gets its names. Agent decision at C:40, without asking: consequences of the stage rule and of `MVP.md`, section Why this document exists.

## Scope of changes

S-1. `config/settings.py`:

- in `ENVIRONMENT_ENTRY_FILES`, after `"PUBLIC_TRANSPORT_ENABLED": ".env.local",`, add `"TILE_ARCHIVE_SOURCE": ".env.local",` and `"TILE_ARCHIVE_DIR": ".env.local",`;
- in `Settings`, after `PUBLIC_TRANSPORT_ENABLED: bool = False`, add `TILE_ARCHIVE_SOURCE: Path | None = None` and `TILE_ARCHIVE_DIR: Path | None = None`;
- add `"TILE_ARCHIVE_SOURCE", "TILE_ARCHIVE_DIR"` to the field lists of the validators `build_path_entry` and `apply_absolute_path_validation`;
- in the docstring of `Settings`, replace "the optional import path and the switch of public transport" with "the optional import path, the switch of public transport and the two optional places of the tile archive".

S-2. `config/config.py`: after `PUBLIC_TRANSPORT_ENABLED = _settings.PUBLIC_TRANSPORT_ENABLED`, add `TILE_ARCHIVE_SOURCE = _settings.TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR = _settings.TILE_ARCHIVE_DIR`.

S-3. `.env.local.example`: after the line `PUBLIC_TRANSPORT_ENABLED=`, add the lines `TILE_ARCHIVE_SOURCE=` and `TILE_ARCHIVE_DIR=`.

S-4. `docs/standards/standard_config.md`, section Environment entries:

- after the row of `PUBLIC_TRANSPORT_ENABLED`, add the rows `TILE_ARCHIVE_SOURCE` with template `.env.local.example` and meaning "The absolute path of the map tile archive a person put on the machine, read only by `python -m worker.tile_archive`, which copies it into `TILE_ARCHIVE_DIR`; it lies outside that directory." and `TILE_ARCHIVE_DIR` with template `.env.local.example` and meaning "The absolute path of the directory from which the proxy serves the map tile archive at `/tiles/krakow.pmtiles`, written only by `python -m worker.tile_archive`.";
- after the paragraph that starts with "`PUBLIC_TRANSPORT_ENABLED` came on 2026-10-04", add the paragraph: "The tile entries came on 2026-10-04 with `plans/tile_loading/`. `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR` are administrative entries like `IMPORT_WORKSPACE_ROOT`: empty or missing, they do not stop the API and the facade exposes them as `None`, a relative path stops the facade with its name, and `python -m worker.tile_archive` ends as failed with a named configuration failure when one of them or `IMPORT_WORKSPACE_ROOT` is missing (`plans/tile_loading/TILE_LOADING_PLAN.md` D-3)."

S-5. `data/tile_archive.py`, new file with the module docstring "Read, copy and place the map tile archive in the directory the proxy serves, in chunks bounded by a run deadline.", without line comments, with a docstring on every function:

- constants `TILE_FILE_CHUNK_BYTES = 1048576` and `TILE_TEMPORARY_PREFIX = ".tile-archive-"`;
- `class TileFileError(RuntimeError)`, a failed read or write of a tile file with a constant message;
- `fetch_tile_directory_presence(directory: Path) -> bool`: whether the path is a directory that is not a link;
- `fetch_tile_file_digest(path: Path, deadline: Deadline) -> str | None`: `None` when the path is not a regular file or is a link; otherwise the SHA-256 hex digest read in chunks of `TILE_FILE_CHUNK_BYTES` with the budget checked before each chunk; `OSError` becomes `TileFileError("Cannot read tile archive file")`; `DeadlineExpiredError` passes on;
- `apply_tile_file_copy(source: Path, directory: Path, deadline: Deadline) -> Path`: a new file of `tempfile.NamedTemporaryFile(mode="wb", dir=directory, prefix=TILE_TEMPORARY_PREFIX, delete=False)`, written in chunks with the budget checked before each chunk, flushed and synced with `os.fsync`; returns its path; on `OSError` and on `DeadlineExpiredError` it removes the partial file, then raises the first as `TileFileError("Cannot copy tile archive file")` and lets the second pass on;
- `apply_tile_file_placement(temporary: Path, target: Path) -> None`: `os.replace(temporary, target)`, then on `sys.platform == "linux"` an `os.fsync` of the directory opened with `os.O_RDONLY | os.O_DIRECTORY`, as `data/import_workspace.py` `apply_journal_write` does; `OSError` becomes `TileFileError("Cannot place tile archive file")`;
- `apply_tile_file_removal(path: Path) -> None`: `path.unlink(missing_ok=True)`; `OSError` becomes `TileFileError("Cannot remove tile archive file")`;
- `apply_tile_leftover_removal(directory: Path) -> int`: removes every regular file of `directory` whose name starts with `TILE_TEMPORARY_PREFIX` through `apply_tile_file_removal` and returns how many it removed.

S-6. `service/tile_archive.py`, new file with the module docstring "Run the tile step of the loading program: put the recorded map tile archive into the directory the proxy serves.", without line comments, with a docstring on every function and record:

- constants `TILE_ARCHIVE_NAME`, `TILE_ARCHIVE_SHA256` of D-2, `TILE_ARCHIVE_RUN_SECONDS = 120` and `TILE_ARCHIVE_GUARD_STATEMENT_TIMEOUT_MS = 5000`;
- `type TileArchiveOutcome` and `type TileArchiveFailureReason` with the values of D-8;
- `@dataclass(frozen=True) class TileArchiveSettings` with `source_path: Path` and `served_directory: Path`;
- `@dataclass(frozen=True) class TileArchiveResult` with `outcome: TileArchiveOutcome`;
- `class TileArchiveError(RuntimeError)`, whose `__init__(self, reason: TileArchiveFailureReason)` sets the message of D-8 and the attribute `reason`;
- `TILE_ARCHIVE_NAMED_ERRORS: tuple[type[Exception], ...] = (TileArchiveError, ImportWorkspaceUnconfirmed)`;
- `resolve_tile_places_overlap(settings: TileArchiveSettings) -> bool`: whether `settings.source_path.is_relative_to(settings.served_directory)`, compared without reading the file system;
- `apply_tile_archive_command(settings: TileArchiveSettings, workspace_root: Path) -> TileArchiveResult`: `apply_tile_archive(settings, workspace_root, build_deadline(TILE_ARCHIVE_RUN_SECONDS, fetch_monotonic_seconds()))`;
- `apply_tile_archive(settings: TileArchiveSettings, workspace_root: Path, deadline: Deadline) -> TileArchiveResult`: D-4, with `ExitStack` as `service/gtfs_import.py` `apply_gtfs_import` uses it, `TileArchiveResult("skipped")` on `ImportAlreadyRunning`, and `apply_tile_archive_run(settings, deadline)` inside;
- `apply_tile_archive_run(settings: TileArchiveSettings, deadline: Deadline) -> TileArchiveResult`: the order of D-7 over the functions of S-5, turning each `TileFileError` into the reason D-7 names and `DeadlineExpiredError` into `deadline_expired`, chaining the original with `from`; when step 4 found a file of another value, one INFO line `Tile archive replaces a served file of another value` through `fetch_logger(__name__)` before returning `loaded`.

S-7. `worker/tile_archive.py`, new file with the module docstring "Start the tile step of the loading program on its own: python -m worker.tile_archive.", without line comments:

- `TILE_ARCHIVE_EXIT_CODES = {"loaded": 0, "unchanged": 0, "skipped": 2}`;
- `build_tile_archive_settings() -> TileArchiveSettings`: reads `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR` from `config.config` inside the function, as `build_osm_import_settings` does, and raises `ConfigurationError("Missing or invalid configuration: " + ...)` naming each missing entry with its file from `ENVIRONMENT_ENTRY_FILES`; the common program of `plans/osm_import/` reuses it;
- `build_tile_archive_workspace_root() -> Path`: the same for `IMPORT_WORKSPACE_ROOT`;
- `apply_tile_archive_report(result: TileArchiveResult, duration_seconds: float) -> int`: the INFO line of D-9 and the code of `TILE_ARCHIVE_EXIT_CODES`;
- `apply_tile_archive_action() -> int`: builds both inputs, calls `apply_tile_archive_command`, logs a failure of `TILE_ARCHIVE_NAMED_ERRORS` with the ERROR line of D-9 and returns 1, logs any other exception by its type and raises it again, as `apply_osm_import_action` does;
- `if __name__ == "__main__": sys.exit(apply_administrative_run("tile_archive", apply_tile_archive_action))`.

S-8. `tests/data/test_tile_archive_cases.py`, new file, each test with a docstring:

- `fetch_tile_file_digest` returns the digest `hashlib` computes for a regular file, `None` for a missing path, a directory and a link (skipped with `pytest.skip` when the machine refuses to create a link), and raises `DeadlineExpiredError` for `Deadline(fetch_monotonic_seconds() - 1)`;
- `apply_tile_file_copy` writes the same bytes into a file of `TILE_TEMPORARY_PREFIX` in the directory; with a stand-in `data.tile_archive.fetch_monotonic_seconds` that passes the first chunk and expires before the second, on a file of three chunks, it raises `DeadlineExpiredError` and leaves no temporary file; with a missing source it raises `TileFileError` and leaves no temporary file;
- `apply_tile_file_placement` replaces an existing target with the bytes of the temporary file, and the temporary file is gone;
- `apply_tile_leftover_removal` removes two files of `TILE_TEMPORARY_PREFIX`, keeps `krakow.pmtiles` and another file, and returns 2;
- `fetch_tile_directory_presence` gives `True` for a directory and `False` for a missing path and a file.

S-9. `tests/service/test_tile_archive_integration.py`, new file with `pytestmark = pytest.mark.integration`, a fixture that writes an invented archive of 2 000 000 bytes into a source directory, creates an empty served directory and replaces `service.tile_archive.TILE_ARCHIVE_SHA256` with its digest through `monkeypatch`, and these tests, each with a docstring:

- AC-1: a run gives `loaded`, the served file has the digest, and the served directory holds only `krakow.pmtiles`;
- AC-2: with an earlier file under the served name, a stand-in `os.fsync` in `data.tile_archive` that raises `OSError` gives `copy_failed`, and a stand-in `service.tile_archive.apply_tile_file_copy` that raises `DeadlineExpiredError` gives `deadline_expired`; in both the served file keeps its earlier bytes and no temporary file remains;
- AC-3: with the archive under the served name and the source removed, a run gives `unchanged`, and `st_mtime_ns` and `st_ino` of the served file are unchanged;
- AC-4: with a file of another value under the served name, a run gives `loaded` and the served file has the digest;
- AC-5, parametrized: no source file gives `source_missing`; a source cut short to 1 000 000 bytes and a source with one changed byte give `source_mismatch`; a stand-in `service.tile_archive.apply_tile_file_copy` that writes other bytes into a temporary file gives `copy_mismatch`; in each the served directory is as before, no temporary file remains, and `str(tmp_path)` is not in the message of the failure;
- `places_overlap` for a source inside the served directory, and `served_directory_missing` for a missing served directory;
- AC-7: with a stand-in `service.tile_archive.build_import_engine` whose result records `dispose` and a stand-in `service.tile_archive.apply_import_exclusion` that raises `ImportAlreadyRunning`, `apply_tile_archive` gives `skipped`, nothing is written, and the engine was disposed; with a stand-in exclusion that admits, it gives `loaded`;
- AC-8: `Deadline(fetch_monotonic_seconds() - 1)` gives `deadline_expired` and the served directory is as before.

S-10. `tests/worker/test_tile_archive_cases.py`, new file, with the invented facade and log capture of F-18, each test with a docstring:

- `build_tile_archive_settings` names `TILE_ARCHIVE_SOURCE (.env.local)` and `TILE_ARCHIVE_DIR (.env.local)` when they are `None`, and `build_tile_archive_workspace_root` names `IMPORT_WORKSPACE_ROOT (.env.local)`;
- `apply_tile_archive_report` returns 0 for `loaded` and `unchanged` and 2 for `skipped`, and its line holds the outcome and no path;
- AC-6: with a stand-in `worker.tile_archive.apply_tile_archive_command` that raises `TileArchiveError("source_mismatch")`, `apply_tile_archive_action` returns 1 and logs `outcome=failed` with `source_mismatch`; with one that raises `RuntimeError`, it raises it again after logging its type.

S-11. `tests/config/test_settings_cases.py`: add `("TILE_ARCHIVE_SOURCE", "relative/krakow.pmtiles")` and `("TILE_ARCHIVE_DIR", "relative")` to the parameters of `test_invalid_entries_do_not_leak_values`, and a test `test_optional_tile_places_do_not_block_api_configuration` that builds `Settings(**VALID, TILE_ARCHIVE_SOURCE="", TILE_ARCHIVE_DIR="")` and finds both `None`.

S-12. Code unit documents:

- `service/SERVICE.md`: a new section `## Tile archive step` before `## Relation to SERVICE_ALGORITHM.md`, with a table of `apply_tile_archive_command`, `apply_tile_archive`, `apply_tile_archive_run` and `resolve_tile_places_overlap` with their inputs and outputs, the records of D-8, the exclusion of D-4, the budget of D-6 and the exit codes of D-9;
- `service/SERVICE_ALGORITHM.md`: a new section `## Tile archive step` at the end, after the section Sample data and its subsections, with the order of D-7 and the repeat rule of FR-2;
- `data/DATA.md`: a new section `## Tile archive` before `## Relation to DATA_ALGORITHM.md`, with the functions and constants of S-5 and `TileFileError`;
- `data/DATA_ALGORITHM.md`: a new section `## Tile archive` at the end, after the section Walking route, with the chunked reads under the budget, the temporary file in the served directory and the placement of D-7 steps 6 - 8.

S-13. `docs/standards/naming_registry.md`: a new section `## Tile archive names` after the section Public transport names, listing the names of S-5, S-6 and S-7 in the form of the entries of that section, and the environment entries `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR`.

S-14. `docs/setup/MAP_SETUP.md`:

- in the section Why this document exists, replace "and how the tile archive is handed to the persons who load it on the server" with "and how the tile archive is put on the server";
- replace the body of the section Handing the archive to the server with: the archive reaches the server as a file Adrian hands over; the person who stands the demo up puts the file itself, not a link, at the path of `TILE_ARCHIVE_SOURCE`, outside the directory of `TILE_ARCHIVE_DIR`; the tile step of the loading program, or on its own `python -m worker.tile_archive`, checks the file against the SHA-256 value of the table, copies it into `TILE_ARCHIVE_DIR` and puts it under `krakow.pmtiles` only after a second check (`plans/tile_loading/TILE_LOADING_PLAN.md` D-7); the outcomes `loaded`, `unchanged` and `skipped` with the exit codes 0, 0 and 2, and the nine failure reasons of D-8 with what a person does for each, exit code 1; a repeated run with the archive in place writes nothing and needs no source file; what the server has to provide - the address `/tiles/krakow.pmtiles` on the host of the page, byte ranges, served from `TILE_ARCHIVE_DIR` - stays as the list it is; and that no address, login or secret of the server is written into the repository.

S-15. `docs/deployment/loading_program.md`:

- in Status and ownership, replace "Adrian supplies the tile provider through `map_tiles`." with "Rafał supplies the tile provider through `tile_loading`; `map_tiles` supplied only the archive file and its record.";
- in Approved execution budgets, replace "Tile and sample whole-step values and enforcement still require their provider contracts" with "The tile step has 120 seconds, enforced by its provider (section Tile-provider handoff); the sample whole-step value and enforcement still require its provider contract";
- in Approved outcomes and terminal output, replace "This example does not define an as-yet-unagreed tile reason." with "The tile reasons are those of section Tile-provider handoff.";
- after the section Approved sample-provider handoff, add the section `## Tile-provider handoff`: the callable `service.tile_archive.apply_tile_archive_run(settings: TileArchiveSettings, deadline: Deadline) -> TileArchiveResult`, called synchronously while the common program holds the exclusion, with `worker.tile_archive.build_tile_archive_settings()` for the settings and `build_deadline(TILE_ARCHIVE_RUN_SECONDS, fetch_monotonic_seconds())` started when the step starts; `loaded` and `unchanged` both complete the `tile_archive` effect, which has no commit state; `TileArchiveError.reason` with the nine codes of D-8, each leaving the served file as it was; an expired budget is `deadline_expired`; an unexpected exception is an unsuccessful step, with the served file either as before or the complete checked archive; the step takes no lease (D-5); the repeat rule of FR-2; the standalone command `python -m worker.tile_archive` takes the same exclusion and gives `skipped` while the common program runs;
- in Remaining integration requirements, replace "- Finalize the tile callable, outcome and failure records, repeat safety and execution budget with Adrian." with "- Map the outcomes and reasons of section Tile-provider handoff to the common records.".

S-16. `plans/osm_import/OSM_IMPORT_PRD.md`:

- append to the state line "; on 2026-10-04 the user moved the tile step from `map_tiles` to `tile_loading` (`plans/tile_loading/TILE_LOADING_PRD.md` FR-7)";
- in FR-4, replace "Adrian adds the tile step through `map_tiles`" with "Rafał adds the tile step through `tile_loading`";
- in Out of scope, replace "; `map_tiles` and `sample_data` own those steps." with "; `map_tiles` produced the archive, and `tile_loading` and `sample_data` own the loading steps.";
- in Dependencies and impact on other modules, replace "- `map_tiles`, owned by Adrian, and `sample_data`, owned by Mateusz, supply their loading steps and consume the common step contract." with "- `tile_loading`, owned by Rafał, and `sample_data`, owned by Mateusz, supply their loading steps and consume the common step contract; `map_tiles`, owned by Adrian, supplied the archive file the tile step loads.".

S-17. `plans/osm_import/OSM_IMPORT_PLAN.md`:

- replace F-16 with "F-16. The tile step is delivered by `tile_loading` as `service.tile_archive.apply_tile_archive_run`, with its contract in the loading contract. | code:`service/tile_archive.py` function `apply_tile_archive_run`; doc:`docs/deployment/loading_program.md` section Tile-provider handoff | 2026-10-04";
- append to D-21: "On 2026-10-04 `plans/tile_loading/` delivered the step with its own command and its contract (`docs/deployment/loading_program.md`, section Tile-provider handoff), and the PRD of this initiative names it in FR-4; the hold of this decision ends with that delivery.";
- in Q-3, replace "common result records and tile-provider signature with their owners" with "common result records with their owners; the tile-provider signature is delivered by `tile_loading` (D-21)";
- in Q-5, replace "finite tile and sample whole-step budgets and enforcement under D-13, and tile-provider repeat safety" with "the finite sample whole-step budget and enforcement under D-13; the tile budget, its enforcement and its repeat safety are delivered by `tile_loading` (D-21)";
- in R-8, replace "tiles have no technical contract" with "the tile contract is delivered by `tile_loading`";
- in Supplementary files, replace "`plans_finished/map_tiles/MAP_TILES_SEED.md`, whose owners supply the additional steps" with "`plans/tile_loading/TILE_LOADING_PLAN.md`, whose owners supply the additional steps".

S-18. `plans/osm_import/OSM_IMPORT_HANDOFF.md`:

- in the state line, replace "the initiative is held by the user until `plans/tile_loading/` settles the tile step" with "`plans/tile_loading/` delivered the tile step on 2026-10-04, which ends the hold of plan D-21";
- in Continuation state of 2026-10-04, replace the item that starts with "- Tiles: no callable, command or compose service loads the archive." with "- Tiles: `plans/tile_loading/` delivered `service/tile_archive.py` `apply_tile_archive_run(settings, deadline) -> TileArchiveResult` and the command `python -m worker.tile_archive`; the contract is in `docs/deployment/loading_program.md`, section Tile-provider handoff. The repository still has no proxy configuration that serves the archive.";
- in Scope and ownership, replace "Adrian supplies the tile-loading step through `map_tiles`." with "Rafał supplies the tile-loading step through `tile_loading`.";
- in the table of Decisions already settled, row Budgets, replace "Tile/sample values and enforcement remain open." with "Tiles have 120 seconds under `tile_loading`; the sample value and enforcement remain open.";
- in Proposal still awaiting approval, replace "not the missing importer/tile callables" with "not the missing importer callable";
- in Blocking integration work, row Q-3, replace "bind the administrative wrapper and tile interface" with "bind the administrative wrapper and the delivered tile interface", and row Q-5, replace "supply finite tile/sample whole-step budgets and safe enforcement; confirm tile repeat safety" with "supply the finite sample whole-step budget and safe enforcement";
- in How to resume, replace step 1 with "1. `plans/tile_loading/` delivered the tile step (plan D-21); read `docs/deployment/loading_program.md`, section Tile-provider handoff. Then read this handoff, starting with Continuation state of 2026-10-04, and the linked plan and loading contract; retain the approved SHAPE and PRD.".

S-19. `plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md`:

- in Current state, replace the item that starts with "- How the tile archive reaches the server is stated two ways." with "- How the tile archive reaches the server is settled by `plans/tile_loading/` on 2026-10-04, decided by Rafał: a person puts the file at the path of `TILE_ARCHIVE_SOURCE`, and the tile step, run by the loading program or by `python -m worker.tile_archive` in the one-off container, copies it into the directory of `TILE_ARCHIVE_DIR`, which the proxy serves at `/tiles/krakow.pmtiles`. The one-off container therefore needs the source file to read, `TILE_ARCHIVE_DIR` to write and the import workspace and database it already needs (`docs/deployment/loading_program.md`, section Tile-provider handoff). Kuba has not confirmed it.";
- in Out of scope, replace " and `plans_finished/map_tiles/`" with ", `plans_finished/map_tiles/` and `plans/tile_loading/`", because `map_tiles` built the archive and `tile_loading` loads it;
- in Open questions, remove item 3 and renumber items 4 and 5 to 3 and 4.

S-20. `MVP.md`:

- in the row of `plans/osm_import/`, replace "into which `map_tiles`, `sample_data` and `public_transport_routing` add their steps" with "into which `tile_loading`, `sample_data` and `public_transport_routing` add their steps";
- after the row of `plans_finished/map_tiles/`, add the row `plans/tile_loading/` | Rafał (lead) | "The tile step of the loading program: it copies the archive of `map_tiles` from the place a person put it on the server into the place the proxy serves, accepting only the recorded file, with its own command `python -m worker.tile_archive` and its contract for `osm_import` (`plans/tile_loading/TILE_LOADING_PLAN.md`)." | "`docs/setup/MAP_SETUP.md`, section The tile archive, and FR-3 and FR-4 of `plans/osm_import/OSM_IMPORT_PRD.md`.";
- in Order and critical path, item 4, add `tile_loading` to the list;
- in Open decisions and confirmations, replace the item that starts with "- The loading of the tile archive on the server." with "- The loading of the tile archive on the server is the tile step of `tile_loading`, decided by Rafał on 2026-10-04 (`plans/tile_loading/TILE_LOADING_PRD.md`): a person puts the file of Adrian into the source place, and the step copies it into the place the proxy serves. Mateusz, who composes the step into the loading program, Kuba, who gives it its two places on the server, and Adrian, whose `docs/setup/MAP_SETUP.md` it changes, have not confirmed it."

S-21. `FINAL_CHECKLIST.md`:

- in Stages, add `tile_loading` to the initiatives of stage 4 and to the column Waits for of stage 5;
- in Set 3, replace "Initiatives: `osm_importer`, `osm_import`, `sample_data`, and the loading step of `map_tiles`." with "Initiatives: `osm_importer`, `osm_import`, `sample_data` and `tile_loading`.";
- replace the heading of check 3.4, "3.4 `map_tiles`, the loading step", with "3.4 `tile_loading`".

S-22. `plans/tile_loading/STAGE.md`, new file: `# Stage`, then `4`, then `Source: FINAL_CHECKLIST.md, section Stages.`, in the form of the other `STAGE.md` files.

## Rollout order

1. S-1 - S-3, then S-11 and `venv/Scripts/python.exe -m pytest -o addopts=-ra tests/config tests/architecture/test_environment_contract.py`.
2. S-5 and S-8, then S-6 and S-9, then S-7 and S-10, each pair run with its test file.
3. S-4, S-12 and S-13.
4. S-14 - S-22, each after a fresh read of the file, because other sessions edit `MVP.md`, `FINAL_CHECKLIST.md`, `plans/osm_import/` and `plans/deployment_config/` in parallel (F-25); a sentence to replace that is no longer there is reported instead of guessed.
5. The checks of Definition of Done.
6. The review `plans_finished/tile_loading/TILE_LOADING_REVIEW.md` and an entry in `agent_docs/memory/`, as `plan-implement` writes them.

Steps for a human:

- Hand the file `krakow.pmtiles` from Adrian to Rafał, put it at `TILE_ARCHIVE_SOURCE` on the server, set `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR` in the environment file of the server, and run `python -m worker.tile_archive` there once `plans/deployment_config/` gives the one-off container the two places; this is the first run on the real file and its real SHA-256 value (F-16).
- Add the empty entries `TILE_ARCHIVE_SOURCE=` and `TILE_ARCHIVE_DIR=` to every local `.env.local`.
- Obtain the confirmations of Mateusz, Kuba and Adrian named in S-20.
- The commit, the push and the merge request.

## Definition of Done

- `venv/Scripts/python.exe -m pytest -o addopts=-ra tests/data/test_tile_archive_cases.py tests/service/test_tile_archive_integration.py tests/worker/test_tile_archive_cases.py tests/config tests/architecture -m "not critical"` passes.
- `venv/Scripts/ruff.exe check` and `venv/Scripts/ruff.exe format --check` pass on `config/settings.py`, `config/config.py`, `data/tile_archive.py`, `service/tile_archive.py`, `worker/tile_archive.py` and the four test files.
- `venv/Scripts/mypy.exe data/tile_archive.py service/tile_archive.py worker/tile_archive.py` reports no error.
- `venv/Scripts/bandit.exe -q data/tile_archive.py service/tile_archive.py worker/tile_archive.py` reports no issue.
- `npx --no-install prettier --check` passes on every changed or created markdown file.
- `grep -rn "map_tiles" MVP.md FINAL_CHECKLIST.md docs/deployment/loading_program.md plans/osm_import plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md` finds `map_tiles` only as the producer of the archive, never as the supplier of the tile step (AC-9).
- The new Python files hold no line comment and none of the characters `docs/standards/standard_formatting.md` forbids.

## Risks

- The real SHA-256 value is checked only on the real file, which is not on this machine (F-16); a wrong constant would make every run end with `source_mismatch`. The constant is copied from `docs/setup/MAP_SETUP.md`, and the first human run of Rollout order checks it.
- The step works on the server only when `plans/deployment_config/` mounts the two places and the import workspace into the one-off container and serves `TILE_ARCHIVE_DIR`; until then it is verified on the tests alone.
- The exclusion of D-4 makes the command refuse during a standalone OpenStreetMap import, which can last up to 60 minutes; the person then waits or runs the common program.
- A system call blocked inside one chunk is not interrupted by the budget (D-6); on a local disk this is not expected.
- Other sessions edit the documents of S-16 - S-21 at the same time (F-25), so a replacement sentence may already be gone when it is applied.
- The map at the public link before 10:00 on 4 October 2026 most likely comes from a file put on the server by hand; this plan does not change that.

## Open questions

None. Every technical decision of phase B is recorded in D-1 - D-13 as an agent decision at C:40, because none of them has consequences for the scope beyond the approved PRD.

## Supplementary files

- `plans_finished/tile_loading/TILE_LOADING_PRD.md`, the contract this plan implements, with `plans_finished/tile_loading/TILE_LOADING_SHAPE.md` and its seed.
- `plans/osm_import/OSM_IMPORT_PLAN.md` D-7, D-10, D-11, D-13, D-14, D-17, D-18 and D-21, and `docs/deployment/loading_program.md`.
- `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`, the precedent of a provider contract.
- `service/gtfs_import.py`, `worker/gtfs_import.py`, `worker/osm_import.py` and `data/routing_data.py`, the patterns this plan follows.
- `docs/setup/MAP_SETUP.md` and `plans_finished/map_tiles/MAP_TILES_PLAN.md` D-1.
- `docs/standards/standard_config.md`, `standard_architecture.md`, `standard_naming.md`, `standard_errors.md`, `standard_worker.md`, `standard_tests.md` and `standard_documentation.md`.
