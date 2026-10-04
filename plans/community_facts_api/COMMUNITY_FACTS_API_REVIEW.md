# Community facts API implementation run and review

Document state: 2026-10-04, code, tests and documents delivered and run on the local database; reviewed ready after minor fixes for the whole initiative, the fixes applied; not archived while Marek's confirmation is outstanding

## 2026-10-04 - Implementation run

The user, Kuba, asked in the conversation of 2026-10-04 whether this initiative could be run together with `plans/community_facts/`, and `plan-implement` ran it in the same working tree while Kuba's session finished the data layer. Two questions were asked before any code. The first closed Q-4: the user answered that Q-4 is closed with the data contract of `plans/community_facts/` and that the implementation starts, which the plan records as D-20; Marek, the owner of the initiative, was not asked and has not confirmed the delivery. The second chose the environment: the user agreed that the agent builds a Python 3.13 virtual environment and the local database of `db/`, with local `.env` files of generated test values that never enter the repository or the conversation.

### Fact check before the code

- F-18 and F-24 were untrue at the start and were corrected in the plan with the same check date: Kuba's data layer had a closed plan and code in the working tree, and this machine is Linux without the Windows environment F-24 described.
- F-36 - F-40 were added for the data contract, the shared statement-limit helper, the critical fixtures and the existing grouping of votes; Q-4 was removed from Open questions and the plan was marked closed. The plan document contract test passes on it.
- The tree changed under the run three times: Kuba committed parts of this work (`89417fa`, `09eae4b`, `ecad79e`), and another session merged `origin/main` (`3381488`). After each, the changed files were checked against the facts that cite them. The merge changed `tests/conftest.py`, `tests/service/conftest.py` and `docs/standards/standard_config.md`; none of them changed a fact of this plan.

### Implementation against the plan

- S-0: closed by D-20. The local database of `db/compose.yaml` was started on `127.0.0.1:55432`, revision `0001` was applied and read back from `alembic_version`, and Kuba's critical tests of `tests/data/test_community_facts_critical.py` passed on it, 19 cases, before the service was built on the module.
- S-1: `service/fact_rules.py` and `service/anonymous_voters.py` with the symbols of D-4, D-9, D-11 and D-15, and their two scenario files.
- S-2: `VOTER_HASH_KEY` and `API_TRUSTED_PROXY_ADDRESSES` in the settings, the facade, both templates, the configuration standard and the invented settings; `api/__main__.py` passes `proxy_headers=True` and the list to uvicorn; `api/fact_identity.py` with its integration test, which runs uvicorn's own proxy handling.
- S-3 - S-5: `service/community_facts.py` with the four reads, the save, the vote, the flag, the hiding and the restoration, and `build_fact_views` in `service/fact_status.py`.
- S-6: `api/point_body.py`, `api/fact_models.py`, `api/facts.py`, `api/moderation.py`, `api/fact_errors.py`, the bodies in `api/fact_body.py`, `repeat_allowed_at` in `build_error_response` and the registration in `build_app`.
- S-7: `api/API.md`, `api/API_ALGORITHM.md`, `service/SERVICE.md`, `service/SERVICE_ALGORITHM.md`, `docs/standards/naming_registry.md`, `docs/setup/backend.md`, `MVP.md`, the registry entry Executor of the API and service layers of the community facts, which stays open for Marek's confirmation, and entries in `agent_docs/memory/api/_shared.md`, `agent_docs/memory/service/_shared.md` and `agent_docs/memory/tests/_shared.md`.

Decisions made while writing the code:

- Agent decision at C:40, without asking: `FactCreationInput` of D-4 is the request as the programming interface layer passes it, and `resolve_fact_creation_input` returns `FactContent` of the data layer, so one record carries the unchecked request across the layer boundary and the data record carries the normalized content, instead of two records of the same role.
- Agent decision at C:40, without asking: a description loses only the spaces U+0020 at both ends, the reading the contract word "spaces" got for a pseudonym in `plans_finished/accounts/ACCOUNTS_PLAN.md` D-3, and a description with a NUL character or a lone surrogate is refused as `invalid_request` with `description`, because PostgreSQL cannot store it and it would otherwise end in `internal_error`.
- Agent decision at C:40, without asking: an amenity geozone is refused with the field `type`, a radius off the list with `geozone_radius_m`, and unordered corners with both coordinates at fault, for example `north_east.lat` and `south_west.lat`. The corners must be strictly south and west, the literal reading of the contract.
- Agent decision at C:40, without asking: `idempotency_key` is accepted only as 8-4-4-4-12 hexadecimal digits with hyphens, in either letter case; the hash always uses the canonical lowercase form, so both cases give one key.
- Agent decision at C:40, without asking: the identifier of a path is limited to the range of `bigint` and refused outside it as `invalid_request` with `id`; zero and negative identifiers reach the service, because the sample facts have negative identifiers (`docs/product/schema.md`).
- Agent decision at C:40, without asking: `type` of a request is read into `FactType` with `strict=False` on that field alone, because a union of the two `Literal` aliases of `api/route.py` made Pydantic report paths such as `type.literal['stairs', ...]`.
- Agent decision at C:40, without asking: an operation that does not use the resolved actor declares its session dependency in `dependencies`, which keeps the refusal of a bad token and the renewal, and keeps vulture clean.
- Agent decision at C:40, without asking: the service functions keep the names of S-5 (`apply_fact_flag`, `apply_fact_hiding`, `apply_fact_restoration`), which equal the names of the data functions, so the data ones are imported as `apply_stored_fact_flag`, `apply_stored_fact_hiding` and `apply_stored_fact_restoration`.
- Agent decision at C:40, without asking: D-12 names `APPLY_STATEMENT_TIMEOUT_SQL`; the code calls the shared helper `apply_statement_timeout` that wraps it (F-38), as the shared-helper rule requires.
- Agent decision at C:40, without asking: `build_fact_views` lives in `service/fact_status.py`, the one place of the status rule. The first version left the inline grouping of `fetch_placed_facts` in `service/route_planning.py` untouched; after the review below named the second copy, `fetch_placed_facts` calls `build_fact_views` too, a change of three lines covered by the scenario tests of the route.
- Agent decision at C:40, without asking: a distance of the nearby check is rounded with `round`, the idiom of the route (F-40).
- Decided by the user on 2026-10-04 in this run: `schema_owner_engine` and `SCRATCH_OWNER_STATEMENT_TIMEOUT_MS` moved from `tests/data/conftest.py` to `tests/conftest.py`, so the critical tests of `tests/service/` reach the exact owner cleanup. The plan foresaw the cleanup fixture in Q-4 and F-39 but missed that `database_cleanup_registry` reached it only from `tests/data/`; the user chose the move over a rolled-back transaction only and over critical tests of the service in `tests/data/`. The root `conftest.py` imports `data` inside the fixture, so a unit run needs no configuration.

### Evidence

Every run used `venv/bin/python`, Python 3.13.16, with the pinned tools.

- Scenario and integration tests of this initiative: `tests/service/test_fact_rules_cases.py` and `test_anonymous_voters_cases.py`, 100 cases; `test_community_fact_reads_cases.py`, 12; `test_community_fact_writes_cases.py`, 21; `test_fact_moderation_cases.py`, 13; `tests/api/test_facts_api_integration.py`, 54; `tests/api/test_moderation_api_integration.py`, 21; `tests/api/test_fact_identity_integration.py`, `tests/config/` and the new case of `tests/api/test_errors_integration.py` all pass.
- Critical tests on the local database: `tests/service/test_community_fact_writes_critical.py`, 12 cases, `test_community_fact_reads_critical.py`, 1, and `test_fact_moderation_critical.py`, 2, pass, and the database holds no fact, vote or account after them. They prove on stored data the offsets of a summer and a winter save, the exact point compared on a retry, a changed content refused, a hidden fact missing on a retry, a deleted account answered as an expired session with nothing stored, one fact and one vote of four concurrent saves with one key, the daily limit across midnight with `2026-10-05T00:00:00.000+02:00` and across the autumn clock change with `2026-10-26T00:00:00.000+01:00`, one person of one address and User-Agent, one vote of four concurrent votes of one person, a vote that waits for a publication locking its fact with the importer's own statements and counts its commit as outdated and its rollback as disputed, the weight kept by votes of a deleted account, the visibility matrix of the area, the detail, the nearby check and the moderator list, and the flag, hide and restore cycle with the first flag day kept.
- The whole critical suite of `tests/data/` and `tests/service/`, after the fixture move: 81 passed, 4 skipped, none failed, in 133 s.
- A smoke run of `python -m api` against the local database: a save answered 201, its retry 200, a changed content 409 `idempotency_key_reused`, the area, the detail and the nearby check 200, a second vote of the author on the same day 409 `vote_too_soon` with the next midnight, a vote of another User-Agent 201 with the status disputed, a flag 204, the moderator list without a token 401, a bad token 401 `session_expired`, unordered corners 422 with both latitudes. The request log held the operation, the status and the duration only. The fact of the run was deleted afterwards by its exact key, which also confirmed that the key the code computes equals the definition of `docs/product/schema.md`.
- Gates: `mypy` on 93 files, both `bandit` passes of every layer, `vulture`, `ruff check` and `ruff format --check` of every changed Python file, `prettier --check` of every changed Markdown file, `tests/architecture`, 157 passed, the whole suite without critical tests, 1257 passed and 1 skipped after the last two fixes of this run (an empty `DEMO_HTTP_PORT` added to the local `.env.local` for the template entry another session added, and a wording of a memory entry the bold check read as bold), and `pip-audit`, no known vulnerability.
- Red on the tree and not caused by this initiative: `ruff check` reports 67 findings and `ruff format --check` several files in `mobile_app/tools/mock_backend/`, `deptry` four imports there, and `prettier --check` `docs/setup/EMULATOR_SETUP.md` and `mobile_app/accessway/README.md`. So `make check-unit` as a whole is red on the tree, while every file of this initiative is clean.

### Remaining for other people

- Marek confirms the delivery of his initiative and D-20, which closes AC-10 of `plans/community_facts/` and lets the registry entry Executor of the API and service layers of the community facts move to Resolved decisions in check 1.4.
- A human sets `VOTER_HASH_KEY` in `.env` and `API_TRUSTED_PROXY_ADDRESSES` in `.env.local` on every machine and on the hosted demo, never changing `VOTER_HASH_KEY` during the demo; without them `python -m api` stops with their names. `plans/deployment_config/` gives the proxy the producer side of D-16, and the hosted demo is checked with two different addresses before the demo (R-4).
- Kuber and Adrian connect the clients; R-10, the 15-second timeout of the HarmonyOS client against a vote that may wait 120 seconds, needs a clear message there.
- `tests/service/test_osm_import_critical.py` leaves its import in the local database, so the next full critical run on the same database fails there until it is recreated with `docker compose ... down` and `up`.
- Commit, push and the Merge Request are steps for a human.

## 2026-10-04 - Implementation DoD review

`implementation-dod-review` ran on the whole initiative, committed and uncommitted, through an independent reviewer agent in read-only mode, which ran every mapped gate itself.

### Blockers

None.

### Risks

- R-A. `tests/data/test_sample_data_critical.py` stopped at its setup guard in the reviewer's run, because the database still held the import `tests/service/test_osm_import_critical.py` leaves behind; the run was inconclusive for the move of `schema_owner_engine`.
- R-B. Marek has not confirmed the delivery or D-20, so the registry entry Executor of the API and service layers of the community facts stays open.
- R-C. The anonymous identity on the hosted demo depends on the proxy of `plans/deployment_config/` appending X-Forwarded-For and allowing a read of 120 seconds, and on `API_TRUSTED_PROXY_ADDRESSES` and `VOTER_HASH_KEY` set on the server; the check with two addresses is not done.
- R-D. `build_fact_views` repeated the grouping of votes still inline in `fetch_placed_facts` of `service/route_planning.py`.
- R-E. `make check-unit` is red on the branch only outside this initiative: `ruff check`, `ruff format --check` and `deptry` in `mobile_app/tools/mock_backend/`, and `prettier --check` of `docs/setup/EMULATOR_SETUP.md` and `mobile_app/accessway/README.md`.
- R-F. The 15-second timeout of the HarmonyOS client against a vote that may wait 120 seconds (R-10 of the plan).

### Improvements

- I-1. `GET /api/facts/in-area` and `GET /api/facts/nearby` match the template of `read_fact` and answer 422 `invalid_request` with `id` instead of 404 `not_found`.
- I-2. `apply_invalid_fact_input` and `apply_vote_too_soon` of `api/fact_errors.py` answered an unexpected exception type with an incomplete envelope instead of `internal_error`, the pattern of `api/errors.py`.
- I-3. This record had no verdict yet.

### Verification

Every standard of the map was checked: `standard_agentic_workflow.md`, `standard_agent_docs.md`, `standard_formatting.md`, `standard_git.md`, `standard_architecture.md`, `standard_config.md`, `standard_database.md`, `standard_code_quality.md`, `standard_logging.md`, `standard_naming.md`, `standard_security.md` and `standard_tests.md` automatically, with the mapped commands; `standard_review.md`, `standard_documentation.md`, `standard_errors.md`, `standard_idempotency.md` and `standard_time.md` manually; `standard_worker.md` and `standard_frontend.md` not applicable, with no periodic task and no frontend code. The reviewer's runs: `mypy` clean on 93 files, `vulture` clean, both `bandit` passes clean, `ruff` and `prettier` clean on every file in scope, `tests/architecture` green, the suite without critical tests 1257 passed, and the critical files of the community facts and of the publication green on the local database.

### Verdict

Ready after minor fixes, for the whole initiative `plans/community_facts_api/`. Not a final ready, so the directory does not qualify for `plans_finished/` by this verdict.

### After the review

- R-A: the local database was recreated with `docker compose ... down` and `up` and the revision applied again; the whole critical suite of `tests/data/` and `tests/service/` then passed, 81 passed and 4 skipped, the four needing native Windows Job Objects, `tests/data/test_sample_data_critical.py` included.
- R-D: `fetch_placed_facts` of `service/route_planning.py` calls `build_fact_views`, so the grouping has one place; the scenario tests of the route and every API test pass, 202 cases, and the critical tests of the route passed in the run above.
- I-2: both handlers answer an unexpected exception type with `internal_error`.
- I-1: Agent decision at C:40, without asking: kept. Every segment that is not an integer under `/api/facts/` is refused as an invalid `id`, which a client of the contract never sends by GET; a custom path convertor for signed integers would turn `/api/facts/abc` into `not_found` and change the refusal the tests and this record describe, for no client gain.
- I-3: this section.
- R-B, R-C, R-E and R-F stay with the people named in Remaining for other people. Since 10:34 a worktree of another session in `.claude/worktrees/` makes `tests/architecture/test_prose_style.py` fail on its own copy of the skills; no file of the repository itself breaks that test.

The directory stays in `plans/`: the verdict is not a final ready and Marek's confirmation of the delivery is outstanding. A later review after his confirmation decides the archive.
