# Review: Tile-archive step of the common demo-loading program

Document state: 2026-10-04, implementation finished and reviewed as ready for the whole initiative, see Review of 2026-10-04, second round; initiative closed by the user on 2026-10-04, see Closure, moved to `plans_finished/`

## Implementation run of 2026-10-04

### Check before implementation

- The facts F-1 - F-25 of `TILE_LOADING_PLAN.md` were checked at 09:22 on the branch `rm/requirements-preparation`, `HEAD` `abe1377`. `common_time.py` had been changed by another session at 09:19 (`build_business_datetime`); the functions and records F-10 cites are unchanged. The code of F-3, F-4, F-11 - F-14 and F-17 - F-19 still holds the cited content.
- Every sentence S-14 - S-21 replaces was found verbatim before the edit, and each file was read again right before its edit.
- `TILE_LOADING_SHAPE.md` has no question marked `Block: yes`; its regulator is C:40, and the plan has no open question.
- Other work on the tree: uncommitted changes of `mobile_app/`, `sample_data`, `osm_import` and several documents, and two unmerged files, `docs/setup/EMULATOR_SETUP.md` and `mobile_app/AI_WORKFLOW.md`, none of them touched by this run.

### Parallel work met during the run

- `HEAD` moved during the run to `fd66a90` and later to `2c9bd6e` through three commits named Moved on with plans, made by a human. They took the files of this initiative as they stood then, among them `data/tile_archive.py`, `service/tile_archive.py` and the data test file; the later edits of this run stay uncommitted. The commits changed no code the facts cite beyond the files of this run.
- Another session rewrote `service/SERVICE.md` at 09:39 with its own changes of the section Sample data and removed the section Tile archive step of S-12. The section was written again on top of that version, without reverting the other edit.
- Another session appended to the item Tiles of `plans/osm_import/OSM_IMPORT_HANDOFF.md`, section Continuation state of 2026-10-04, at 09:35 a sentence that sends the reader to the plan and review of this initiative instead of that paragraph. S-18 replaced the whole item, as that sentence asks; the other edits of that session in the same file stay.
- The full fast run `pytest tests -m "not critical"` gives six failures in `tests/data/test_osm_source_cases.py` and `tests/service/test_osm_routing_preparation_integration.py`: the osmium reader cannot open a temporary path with the letter ł of the user profile. With `--basetemp=.cache/pytest-osm` all 22 tests of those two files pass, so the failures belong to the machine, as `agent_docs/memory/tests/_shared.md` already records, not to this change.

### Deviations from the plan

O-1. The file under the served name gets the mode 0644. `tempfile.NamedTemporaryFile` creates the copy as 0600 whatever the umask, and `os.replace` keeps that mode, so a proxy running as another user would refuse to serve the archive; the plan did not foresee it. Asked during implementation, the user chose 0644 before the replacement on 2026-10-04, against keeping 0600 as a requirement for `plans/deployment_config/` and against a mode taken from the umask. `data/tile_archive.py` has the constant `TILE_FILE_MODE` and calls `os.fchmod` on the open copy before `os.fsync`; the test `test_the_copy_is_readable_by_everyone_and_writable_only_by_its_owner` checks it on Linux, and the documents of S-12, S-14, S-15 and S-19 say that the placed file is readable by everyone.

O-2. S-4 was written in step 1 of Rollout order instead of step 3, because `tests/architecture/test_environment_contract.py` refuses a template entry without its record in `docs/standards/standard_config.md`, and step 1 runs that test.

O-3. `DeadlineExpiredError` is a `TimeoutError` and so an `OSError`. `fetch_tile_file_digest` re-raises it before its `except OSError`, and `apply_tile_file_copy` tells the two apart in one handler, so an expired deadline never becomes `TileFileError`; S-5 asks for exactly that behavior, and `agent_docs/memory/_cross_cutting.md` records the trap.

O-4. Three names the plan does not list. `build_required_paths` of `worker/tile_archive.py` names every missing path entry and its file once for both builders of S-7. `apply_tile_failure_reason` of `service/tile_archive.py` is the one place that turns `TileFileError` into the reason of a step and `DeadlineExpiredError` into `deadline_expired`, chaining the original. `apply_tile_temporary_cleanup` of `data/tile_archive.py` removes a copy that was not placed and, when that removal itself fails, logs a warning with the redacted traceback instead of hiding the failure of the run behind a removal failure; the next run removes the copy as a leftover. Both `apply_tile_file_copy` and the service use it, after finding R-2 of the review below. Agent decision at C:40, without asking: DRY, and the plan fixes the behavior, not these helpers. The three names stand in `docs/standards/naming_registry.md`, section Tile archive names.

O-5. A failed read of the written copy, step 7 of D-7, ends as `copy_failed`; D-7 names only `copy_mismatch` for a copy of another value. Agent decision at C:40, without asking: a copy that cannot be read back is a failed copy, and both reasons leave the served name as it was.

O-6. A failed sync of the directory on Linux after `os.replace` ends as `copy_failed` with the complete checked archive already under the served name. S-15 says that each reason leaves the served file as it was; the written contract, `docs/setup/MAP_SETUP.md` and `service/SERVICE_ALGORITHM.md` state this one exception, and the next run reports `unchanged`. Agent decision at C:40, without asking: the contract has to describe what the step does, and the earlier state cannot come back after the replacement.

O-7. `apply_tile_leftover_removal` skips a link that carries the prefix and turns a failed listing of the directory into `TileFileError("Cannot remove tile archive file")`, the message of a failed removal. Agent decision at C:40, without asking: the step never follows a link (D-10), and the listing failure maps to `copy_failed` either way.

O-8. The item of S-19 in `plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md`, section Current state, got one more sentence, that the placed file is readable by everyone, so the proxy may read it as another user; a consequence of O-1 that Kuba needs for the proxy.

O-9. The check of AC-9 in the Definition of Done searches all of `plans/osm_import/`. It also found the sentence of `OSM_IMPORT_PLAN.md`, section Scope of changes, that asked to finalize the contract before `map_tiles` and `sample_data` implement their integrations, which S-17 does not list; it now names only `sample_data` and says that `tile_loading` delivered its contract. Agent decision at C:40, without asking: FR-7 covers the plan of `plans/osm_import/`. The check also finds `OSM_IMPORT_SEED.md`, a verbatim record that is never edited, and `OSM_IMPORT_SHAPE.md`, the closed interview of that initiative, which FR-7 does not list; both keep `map_tiles` as they were written.

### What was done

- S-1 - S-3: `config/settings.py`, `config/config.py` and `.env.local.example` carry `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR` as optional absolute paths; S-11 added the two invalid relative values and `test_optional_tile_places_do_not_block_api_configuration`.
- S-4: two rows and one paragraph in `docs/standards/standard_config.md`, section Environment entries.
- S-5 and S-8: `data/tile_archive.py` and `tests/data/test_tile_archive_cases.py`, twelve tests.
- S-6 and S-9: `service/tile_archive.py` and `tests/service/test_tile_archive_integration.py`, fourteen tests under the `integration` marker.
- S-7 and S-10: `worker/tile_archive.py`, the command `python -m worker.tile_archive`, and `tests/worker/test_tile_archive_cases.py`, eight tests.
- S-12 and S-13: the sections Tile archive step of `service/SERVICE.md` and `service/SERVICE_ALGORITHM.md`, Tile archive of `data/DATA.md` and `data/DATA_ALGORITHM.md`, and Tile archive names of `docs/standards/naming_registry.md`.
- S-14 - S-22: `docs/setup/MAP_SETUP.md`, `docs/deployment/loading_program.md` with the new section Tile-provider handoff, the PRD, plan and handoff of `plans/osm_import/`, `plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md`, `MVP.md`, `FINAL_CHECKLIST.md` and `plans/tile_loading/STAGE.md` with stage 4.

### Checks of the Definition of Done

- `pytest -o addopts=-ra tests/data/test_tile_archive_cases.py tests/service/test_tile_archive_integration.py tests/worker/test_tile_archive_cases.py tests/config tests/architecture -m "not critical"`: 244 passed, 5 skipped after the fixes of the review below. The skips are the link and the mode tests on Windows and the three local environment files that do not exist on this machine.
- The Linux paths of `data/tile_archive.py` ran in a container of the local image `python:3.13-slim` with the umask 077: the copy and the placed file have the mode 0644, a link has no digest, a link under the served name is replaced without touching its target, the sync of the directory succeeds, and the leftover removal skips a link with the prefix.
- `ruff check` and `ruff format --check` pass on the nine Python files, `mypy` reports no error on the three modules, also with `--platform linux`, and `bandit -q` reports no issue.
- `npx --no-install prettier --check` passes on every changed or created markdown file.
- The new Python files hold no line comment and none of the forbidden characters.
- AC-9: `map_tiles` stays in `MVP.md`, `FINAL_CHECKLIST.md`, `docs/deployment/loading_program.md`, `plans/osm_import/` and `plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md` only as the producer of the archive, in the history of D-21 and in the files of O-9.

### Acceptance criteria

- AC-1, AC-3, AC-4: met by the tests of `tests/service/test_tile_archive_integration.py` on an invented archive of 2 000 000 bytes whose value replaces the recorded one. The file of Adrian with its real value has not been run, because it is not on this machine (F-16).
- AC-2: met by the copy that fails at its sync and the copy stopped by the deadline, both leaving the earlier file and no temporary file.
- AC-5: met for the four inputs, each with its reason, the served directory as before and no path in the message.
- AC-6: met by the tests of `tests/worker/test_tile_archive_cases.py` for the outcome line, the exit codes and the failure line.
- AC-7: the side of the command is met by the stand-in exclusion that refuses and the one that admits. The side of the common program waits for `plans/osm_import/`, which composes the step.
- AC-8: met by the section Tile-provider handoff of `docs/deployment/loading_program.md` and the test with an expired deadline.
- AC-9: met, see the check above.

### Still open

- The first run on the real file and its SHA-256 value, on the server, once `plans/deployment_config/` gives the one-off container the two places; a wrong constant would end every run with `source_mismatch`.
- The confirmations of Mateusz, Kuba and Adrian named in `MVP.md`, section Open decisions and confirmations.
- `docs/deployment/loading_program.md`, section Proposed common result contract, still says that the proposal settles the representation without claiming finalized importer or tile callables; the sentence stays true of the proposal and was left for `plans/osm_import/`.

## Review of 2026-10-04, first round

`implementation-dod-review`, run by the agent `dod-reviewer` on the working tree, scope: the implementation of the whole initiative. Verdict: ready after minor fixes, without blockers. Its own runs: the fast suite with `--basetemp=.cache/pt`, 981 passed, 11 skipped; `ruff`, `mypy`, `vulture`, `deptry` and `bandit` clean on the scope, the findings of `ruff` and `deptry` outside it belonging to `mobile_app/`; the Linux paths again in a container of `python:3.13-slim`.

Z-1. The docstring of `apply_tile_archive_run` said that every failure leaves the served name as it was, against O-6 and the written contract. Fixed: it states the exception of `copy_failed` after the replacement and that an unexpected exception passes on.

Z-2. A failed removal of the partial file inside `apply_tile_file_copy` replaced the original failure, so an expired deadline could end as `copy_failed`. Fixed: `apply_tile_temporary_cleanup` moved to `data/tile_archive.py`, the copy and the service both use it, and the test `test_a_partial_file_that_cannot_be_removed_does_not_hide_an_expired_deadline` checks it.

Z-3. The repeat paragraph of the contract said that a run with the archive in place writes nothing, while step 3 of D-7 removes leftovers first. Fixed: `docs/deployment/loading_program.md`, `service/SERVICE_ALGORITHM.md` and `docs/setup/MAP_SETUP.md` say that nothing is written under the served name.

Z-4. The contract did not say where the settings builder may be called from. Fixed: the section Tile-provider handoff says that the worker entry point of the common program builds the settings and passes them down, because `service/` may not import `worker/`.

Z-5. `build_required_paths` of `worker/tile_archive.py` repeats the message of `build_osm_import_settings` of `worker/osm_import.py`, and `config/settings.py` builds the same prefix a third time. Left as it is: moving one helper next to `ConfigurationError` changes `worker/osm_import.py` of another initiative, so it is a follow-up for its owner, not part of this change.

Z-6. The real file of Adrian and its SHA-256 value have not run (AC-1, AC-4), and the side of AC-7 in which the common program refuses waits for `plans/osm_import/`. Not a code finding; it stands in Still open above.

After the fixes: the Definition of Done run gives 244 passed, 5 skipped; `ruff check`, `ruff format --check`, `mypy` on both platforms and `bandit` pass on the scope, `prettier --check` passes on the changed documents, and the Linux paths ran again in the container with the same result.

## Review of 2026-10-04, second round

`implementation-dod-review`, run again by the agent `dod-reviewer` on `HEAD` `2c9bd6e` and the working tree, on the changes of Z-1 - Z-4. Scope: the code and documents of the whole initiative `plans/tile_loading/`. Verdict: ready.

- Z-1 and Z-2 are fixed: the docstring of `apply_tile_archive_run` agrees with the written contract, and an expired deadline survives a failed removal of the partial file, checked by the new test and again on Linux in a container of `python:3.13-slim`.
- Z-3 and Z-4 are fixed in `docs/deployment/loading_program.md`, `service/SERVICE_ALGORITHM.md` and `docs/setup/MAP_SETUP.md`.
- Z-5 stays a follow-up for the owner of `worker/osm_import.py`.
- Its runs: the fast suite with `--basetemp=.cache/pt`, 982 passed, 11 skipped; `ruff`, `mypy` on both platforms, `vulture` and `bandit` clean on the scope; `prettier --check` clean on the changed documents.
- What the verdict does not cover, Z-6: the first run on the real file of Adrian and its SHA-256 value on the server, a step for a human in the plan, and the side of AC-7 in which the common program refuses, which `plans/osm_import/` builds.

## Closure

On 2026-10-04 the user decided to move the initiative to `plans_finished/` after the final verdict ready of the second round, without waiting for the items of Still open. The first run on the real file on the server stays a step for a human of the plan, and the side of AC-7 in which the common program refuses stays with `plans/osm_import/`; the move confirms neither of them.
