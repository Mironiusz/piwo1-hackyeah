# Community facts implementation run and review

Document state: 2026-10-04, code, tests and documents delivered and reviewed; not ready for the whole initiative until the critical tests run on the local database

## 2026-10-04 - Implementation run

The user asked for the implementation of the plan, and `plan-implement` ran it. The plan was complete (no open questions, shape closed at C:40 with no open block). At the start the user was asked whether the agent may build the local environment, a Python 3.13 environment, the local `.env` files and the local database, and declined: only the code, the tests and the documents were to be written. The agent built none of it. Late in the run the session of `community_facts_api` created a `venv` in the repository root, and the agent used its installed tools, which install and change nothing; the local database and the `.env` files do not exist, so nothing that needs the database was run.

### Fact check before the code

- The merge of `main` into the branch on 2026-10-04 made F-16 and F-17 untrue: `schema_owner_engine` already exists in `tests/data/conftest.py`, delivered by `sample_data` D-10, and `scratch_database` already takes its owner from it. The two facts were corrected in the plan with the same check date, and D-10, S-1 and S-5 carry a note.
- Agent decision at C:40, without asking: S-1 is not implemented. A second definition in `tests/conftest.py` would duplicate a shared helper, and moving the delivered one would change a file another initiative delivered under its own plan. Every critical test of this plan sits in `tests/data/` and reaches the fixture; `database_cleanup_registry` resolves it from there. The consequence is that the fixture is not visible to tests outside `tests/data/`, which none of this plan's tests needs.
- Agent decision at C:40, without asking: the two parts of S-5 that concern `schema_owner_engine`, its entry in `docs/standards/naming_registry.md` and the note in `docs/setup/backend.md`, are left to `sample_data`, the owner of the fixture. The registry entry already names `tests/data/conftest.py` after the merge.
- After the later merge of `main` (HEAD 2ccb636) the facts F-4, F-5, F-16, F-17, F-23 and F-24 were checked again against the files it changed and still hold. `docs/product/schema.md` gained the note that negative fact identifiers belong to the sample data and that the operations of `community_facts` must accept them; the module takes any identifier, and the critical tests use a large positive identifier as the missing one, never -1.

### Implementation against the plan

- S-1: not implemented, see above.
- S-2 and S-3: `data/community_facts.py` delivers the records, the four reads, the two locks and the writes of D-2 - D-8 with the signatures of the plan. Four helpers and four constants beyond the plan names were added and are in the naming registry: `fetch_taken_vote_day`, `apply_vote_row`, `build_optional_stored_community_fact`, `build_vote_voter_columns`, `WGS84_SRID`, `VOTE_ACCOUNT_CONSTRAINT_NAME`, `VOTE_ACCOUNT_MISSING_MESSAGE` and the query constants of the plan.
- Agent decision at C:40, without asking: `apply_vote_row` holds the insert and the translation of the foreign key failure, and both `apply_vote_insert` and `apply_fact_insert` call it. The first vote of a new fact cannot meet an earlier vote, so `VoteDayTaken` has no meaning there; the impossible case raises `RuntimeError` instead of an unreachable branch.
- Agent decision at C:40, without asking: `VoteAccountMissingError` is raised `from None`. The message of the driver names the key and so the account identifier, and the diagnostics of the project render no chained payloads.
- S-4: `tests/data/test_community_facts_cases.py` has 10 cases without a database, and `tests/data/test_community_facts_critical.py` has 18 critical tests, 19 cases with the two kinds of person of the daily limit. Every test named in the plan is there. Two tests beyond the plan were added: `test_vote_waits_for_a_moderation_of_the_same_fact`, because D-5 claims that a vote waits for a moderation, and `test_area_rectangle_includes_its_edges_and_a_point_on_its_southern_parallel`, because D-3 and D-4 claim the edge is included and the parallel is compared as geometry. Agent decision at C:40, without asking: the facts of the tests lie around an origin at 49.2 N, 20.0 E, far from Krakow, so facts loaded into a developer's local database cannot enter a rectangle or a radius the tests assert exactly.
- S-5: delivered the section Community facts in `data/DATA.md` and `data/DATA_ALGORITHM.md`, the section Community fact names in `docs/standards/naming_registry.md`, the consent of Kuba in the row of `plans_finished/route_planning/` and in Open decisions and confirmations of `MVP.md`, the entry Backend handoff for vote locking during OSM publication moved to Resolved decisions of `docs/standards/decision_registry.md`, and an entry in `agent_docs/memory/data/_shared.md` for D-4, D-5 and D-7. The registry entry says that Mateusz has not confirmed the rule in writing; nothing in the repository shows his confirmation.
- Rollout step 1, the handing of D-2 - D-8 to Marek as the answer to Q-4 of `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md`, and the commit, push and Merge Request are steps for a human and were not done. The contract is now written in code and in `data/DATA.md`.

### Evidence and what was not run

- Run with the tools of that `venv` (Python 3.13.16, ruff 0.16.2, mypy 2.3.0, vulture 2.16, bandit 1.9.4, deptry 0.25.1, pytest 9.1.1): `ruff check` and `ruff format --check` on the four new Python files, clean after two fixes the tools asked for (a Yoda condition in the cases file, one statement `ruff format` joined); `mypy`, 87 files, no issues; both `bandit` passes of `data`, no findings; the 10 cases of `tests/data/test_community_facts_cases.py`, which also compile the statements for PostgreSQL; `tests/architecture`, where the layer boundary, prose style and plan contract tests pass; and the whole suite without critical tests, 1128 passed. The local prettier passes `--check` on every changed Markdown file. The compiled SQL of the reads, the locks and the writes was read statement by statement for PostgreSQL validity.
- Red in the same runs and not caused by this change: `tests/architecture/test_environment_contract.py` fails on `VOTER_HASH_KEY` of `.env.example`, which the session of `community_facts_api` adds and has not yet recorded in `docs/standards/standard_config.md`; `ruff check` finds a Yoda condition in `tests/config/test_settings_cases.py`; `vulture` reports `runtime_settings` in three files of `tests/service/`; `deptry` reports four imports in `mobile_app/`. So `make check-unit` as a whole is red on the tree, while every file of this initiative is clean in every tool above.
- Not run: the 18 critical tests, 19 cases, because the local database and the `.env` files do not exist, so none of AC-1 - AC-9 is shown by a run; AC-3 on two real connections is written and not run. `pip-audit` was not run, because no dependency was added. AC-10 waits for Marek: his plan already closes Q-4 with this contract (D-20, F-36 - F-39 of `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md`) and lists the confirmation of the code by a run as its own step.
- The first run on the database is the first evidence that the statements work, and these are the places most likely to need a fix: the insert of a fact that sets the point with an expression in `values()` while its parameters come at execution, the set-based seed statements of `test_area_read_stops_at_its_limit` and `test_votes_of_many_facts_come_in_one_read` with their `%` and `generate_series`, and the spy `Mock(wraps=connection)` of the second.

### Remaining for other people

- Run, with the local database up and its revision applied: `make check-unit`, then `make test-critical PYTEST_ARGS=--scratch-database-url=<local-schema-owner-url>` and the critical tests of `tests/data/test_accounts_critical.py`, `tests/data/test_route_facts_critical.py` and `tests/data/test_publication_critical.py`.
- Kuba hands the contract to Marek; Marek confirms AC-10; Mateusz confirms the lock of the registry entry.

## 2026-10-04 - Implementation DoD review

Scope: the whole initiative `community_facts`, that is the code, the tests, the documents and the records of this plan, assessed on the tree as it stood after the merge of `main` (HEAD 2ccb636) and the commit of the plan. The review read the standards of the map of `docs/standards/standard_review.md` and ran every tool the map names for them, in the `venv` described above.

### Blockers

- B-1. The critical tests have not run on a database. `plans/community_facts/COMMUNITY_FACTS_PLAN.md`, Definition of Done, requires AC-3 on two real connections against the local database and the critical suites passing; `docs/standards/standard_tests.md` says that code that reads or writes the database has a critical test against a real database, and a test that has never run shows nothing. The code is therefore unproven on the point of the lock, the daily limit and the conflict handling, which are its reason to exist.
- B-2. AC-10 is open: Marek has not confirmed that the written contract answers Q-4, and Mateusz has not confirmed the lock that the registry entry now records as resolved.

### Risks

- R-1. `fetch_stored_fact_for_vote` can wait up to the 120 seconds of the publication, while the engine of the API cuts a statement at 5000 ms. The module sets no limit by design (D-5); a service that forgets to raise the limit before the lock turns a publication wait into a cancelled statement after 5 seconds. The duty is written in `data/DATA.md` and in D-12 of the plan of `community_facts_api`.
- R-2. The area read compares the rectangle as geometry and so scans every fact; the volume is estimated at thousands and nothing was measured. `test_area_read_stops_at_its_limit` bounds it at one second for 1001 facts, and R-2 of the plan names the prefilter on `IX_fact_geog` as the change to make if it fails.
- R-3. `schema_owner_engine` is visible only to tests under `tests/data/`, while `database_cleanup_registry` that consumes it lives in `tests/conftest.py`; a critical test elsewhere that asks for the registry would fail on a missing fixture. Nothing uses it elsewhere today.
- R-4. The statement text assertions of the cases file prove the text of the statements and break on a harmless reformulation; they exist to hold D-3, D-4 and D-5 until the critical tests have run.

### Improvements

- I-1. Once the critical tests pass, the cases that assert statement text could be reduced to the lock modes, which the critical tests do not show directly.

### Verification

- `standard_agentic_workflow.md`: not applicable, no skill, hook, agent role or rule was changed.
- `standard_agent_docs.md`: checked automatically, `tests/architecture/test_plan_document_contract.py` passes on the corrected plan; the REVIEW and the memory entry follow the format by reading.
- `standard_review.md`: checked manually, this report follows its order.
- `standard_documentation.md`: checked manually, the sections Community facts of `data/DATA.md` and `data/DATA_ALGORITHM.md` follow the pattern of the other features of the layer.
- `standard_formatting.md`: checked automatically, `ruff format --check` on the new Python files, `prettier --check` on every changed Markdown file and `tests/architecture/test_prose_style.py` all pass.
- `standard_git.md`: checked automatically, `test_conflict_markers.py` passes; the agent made no commit and ran no `git add`.
- `standard_architecture.md`: checked automatically, `test_layer_boundaries.py` passes; the two visibility predicates live in one module each and are tested on both sides.
- `standard_config.md`: checked automatically, `test_environment_contract.py` fails on `VOTER_HASH_KEY` of another initiative; this change adds no entry.
- `standard_database.md`: checked automatically, both `bandit` passes, B608 included, find nothing; every value is a bound parameter, every query lists its columns, and the domain operations stay in the transaction of the caller.
- `standard_errors.md`: checked manually, one named error with a constant message, no retry, and the wait limit left to the caller, see R-1.
- `standard_idempotency.md`: checked manually, the save is one `INSERT ... ON CONFLICT DO NOTHING RETURNING` on the unique index of the key, with the read after a conflict that the contract needs; its tests are written, not run.
- `standard_code_quality.md`: checked automatically, `ruff check`, `mypy`, `vulture` and `deptry` find nothing in the files of this change; the red results of the same runs belong to other work, listed above.
- `standard_logging.md`: checked manually and by `ruff check`, rule G; the module logs nothing and its records and error keep the person out of their text.
- `standard_naming.md`: checked automatically, `ruff check` rule N passes; the prefixes and the `<VERB>_<WHAT>_SQL` names follow the standard and are in the registry.
- `standard_security.md`: checked automatically, `bandit` finds nothing; `pip-audit` not applicable, no dependency changed.
- `standard_tests.md`: checked automatically and manually, the cases and the architecture test pass; the critical tests are not checked by a run, see B-1.
- `standard_time.md`: checked manually, every instant travels as the pair `OffsetInstant`, the order and the comparisons use the instant alone, and the day of a vote is the generated column of the database; the offset round trip is in two critical tests, not run.
- `standard_worker.md`: not applicable, no periodic task.
- `standard_frontend.md`: not applicable, no frontend file changed.

### Verdict

Not ready, for the whole initiative `community_facts`, because of B-1 and B-2. By reading and by every tool that runs without a database the change has no defect; what remains is a run on the local database and two confirmations. The initiative does not qualify for the archive `plans_finished/` and stays in `plans/`.
