# Review: MVP accounts and shared actor resolution

Document state: 2026-10-04, S-1 - S-7 implemented and reviewed, verdict ready for the whole initiative in section Review of the whole initiative

## Implementation - run of 2026-10-04

Scope: S-1 and S-3 of `plans/accounts/ACCOUNTS_PLAN.md`, the two steps the Rollout order lets run before the skeleton exists, and the parts of S-7 that describe them.

Check before the run, step 1 of the Rollout order: after `git fetch` at 05:02, `origin/dev` was still `afe5bc1`, and `api/`, `service/`, `data/`, `config/` and `common_time.py` existed neither in the working tree nor on any remote branch (`git ls-tree -r` of each), so F-11 - F-13 stand with their check date. The missing skeleton parts of D-1 are `config/` with `Settings` and the facade, `common_time.py`, `config/logging.py`, `api/app.py`, `api/errors.py` and `data/engine.py`; nothing was written in their place. No file cited in the Facts changed since the plan was written. The untracked `plans/community_facts/COMMUNITY_FACTS_SHAPE.md` of another session was in the tree and was not touched (`docs/standards/standard_agentic_workflow.md` ch. 4.7).

What changed:

- S-1: `docs/product/api_contract.md`, section create_account, names the letters as the 26 Latin and the nine Polish letters in both cases and the digits as `0` - `9`, and refuses every other character; its state line records the decision of Kuba with the confirmation of Adrian pending. `MVP.md`, section Open decisions and confirmations, records the same.
- S-3: `service/account_rules.py`, `service/passwords.py` and `service/session_tokens.py` with the names of S-3, apart from the exception names below; `tests/service/__init__.py` and the three scenario files `test_account_rules_cases.py`, `test_passwords_cases.py` and `test_session_tokens_cases.py`.
- Gates and records: the root `pyproject.toml` pins `argon2-cffi==25.1.0` and adds `service` to mypy and vulture; the `makefile` adds two Bandit passes for `service`; `docs/standards/naming_registry.md` lists the new file, function, exception and test names; `agent_docs/memory/service/_shared.md` is created with its first entry and `agent_docs/memory/_cross_cutting.md` gets one.

Runs, in a container of Python 3.13 with the pinned tools of the root `pyproject.toml` and argon2-cffi 25.1.0:

- `pytest tests/service`: 99 passed.
- `pytest tests/architecture`: 125 passed, 3 skipped for the absent `.env`, `.env.local` and `.env.priv.example`, 2 failed - the two prose style tests, both only on files of `mobile_app/`.
- `ruff check` and `ruff format --check` of `service` and `tests/service`: clean. Of the whole repository: findings only in four files of `mobile_app/tools/`.
- `mypy`: no issue in 5 files. `vulture`: clean. `bandit -r service` at medium confidence and its B608 pass: clean. `pip-audit` of `argon2-cffi==25.1.0`: no known vulnerability.
- `deptry .`: two findings, both `pmtiles_mvt` imported in `mobile_app/tools/mock_backend/`; none in `service`.
- `npx --no-install prettier --check` on every changed markdown file: clean.

Decisions while implementing:

- Agent decision at C:40, without asking: the exceptions of the plan carry the suffix `Error` - `InvalidAccountInputError` and `SessionExpiredError` now, `AuthenticationRequiredError`, `ModeratorRoleRequiredError`, `PseudonymTakenError` and `InvalidCredentialsError` in S-5 - because the ruff rule N818 of the `N` set of `pyproject.toml` refuses the names of D-7, S-3 and S-5 of the plan, and the only other way is a suppression the standards do not allow without a reason of the code.
- Agent decision at C:40, without asking: `service` joined the gates now, with its first code, instead of waiting for S-1 of the skeleton that D-13 of the plan expects, because code outside the gates does not meet the Definition of Done; the same lines of the skeleton will meet these in a manual merge. For the same reason the pin of argon2-cffi of D-13 came with S-3, which imports it, instead of with S-2.
- Agent decision at C:40, without asking: `tests/service/__init__.py` is empty, like `tests/__init__.py`, so that the test modules are imported as `tests.service.*`.
- Agent decision at C:40, without asking: a token part is accepted only when its base64url re-encoding equals it, which covers padding, characters outside the alphabet and loose trailing bits with one rule, and the payload part is checked for that form before the signature, so a payload with characters outside ASCII is refused instead of failing in the encoding of the signature input.

Run into:

- On `dev` before this change `make check` was already red outside accounts: `ruff check`, `ruff format --check` and `deptry` on `mobile_app/tools/`, and the prose style tests on markdown of `mobile_app/`, all from pull request 27. A separate task was suggested for it; accounts does not fix someone else's code.

Left for later:

- S-2, S-4, S-5 and S-6 wait for the skeleton parts named above; S-7 waits for the layer documents and for the code of S-4 - S-6, and the section Moderator role of `db/README.md` is written with S-4.
- AC-1 - AC-4 are covered by the scenario tests of S-3 only on the side of the rules; their operations, the critical tests and every other acceptance criterion wait for S-4 - S-6.
- The steps of a human of the plan, and telling Marek about the suffix `Error` his plan will need too.

Review of S-1 and S-3, `implementation-dod-review` through the subagent `dod-reviewer`, every mapped command run in the tools container:

- Blockers: none. Every finding of `ruff check`, `ruff format --check`, `deptry`, `prettier` and the prose style tests is in `mobile_app/`, outside the change.
- Risk 1, fixed: a password holding a lone surrogate, which a JSON escape such as `\ud800` produces, passed `resolve_password` and then raised `UnicodeEncodeError` in Argon2. Decided by Kuba on 2026-10-04, against refusing the whole body in the programming interface layer: `resolve_password` refuses text that UTF-8 cannot encode as `password`, so the operation answers `invalid_request` with that field, and a login with such a password ends in `invalid_credentials` like any password outside the rules (plan D-5). `docs/product/api_contract.md`, section create_account, says so next to the counting of characters; the scenario tests cover a surrogate in a password and in a pseudonym.
- Risk 2, recorded: `MVP.md` and `docs/standards/decision_registry.md` in the working tree also hold changes of the session working on `plans/community_facts/` - the bullet on who builds the programming interface and service layers of `community_facts` and the entry Executor of the API and service layers of the community facts, with the agreement on the vote lock. They are not part of this run and have to be kept apart from it when the work is committed.
- Improvement 1, done. Agent decision at C:40, without asking: `build_session_token` and `resolve_session_claims` refuse a naive current instant with `ValueError` through `_build_utc_instant`, because `docs/standards/standard_time.md` forbids guessing the zone of a naive value; a scenario test covers both.
- Improvement 2, left to Kuba: M9 of the specification still says only "letters, the Polish ones included"; the contract names the set exactly. They do not conflict and the specification prevails, but the set could be carried into the next version of the specification.

Runs after the fixes: `pytest tests/service` and the plan contract test, 128 passed; `ruff check`, `ruff format --check`, `mypy`, `vulture` and both Bandit passes clean on the changed code; `prettier` clean on the changed markdown.

Verdict: ready after minor fixes, the minor fixes being Risk 1 and Improvement 1, now done. Scope: S-1 and S-3 of `plans/accounts/ACCOUNTS_PLAN.md`, part of the code of the initiative; S-2 and S-4 - S-7 are not implemented and not assessed, so the initiative does not qualify for `plans_finished/` and stays in `plans/`.

## Implementation - second run of 2026-10-04

Scope: S-2 and S-4 - S-7 of `plans/accounts/ACCOUNTS_PLAN.md`, closing the initiative on the request of the user.

Check before the run, step 2 of `plan-implement`: the skeleton of D-1 is delivered and `plans_finished/backend_skeleton/` archived, so F-10 - F-13 were out of date. They were rewritten in the plan with the check date 2026-10-04: the templates hold more than the database entries, the backend code exists, `Settings` names its fields in upper case, `build_app()` registers each product router through a call of its own, and `fetch_api_engine` is already in `data/engine.py`. The other facts were checked against the files they cite and still hold. The shape has no open question.

Parallel work, `docs/standards/standard_agentic_workflow.md` ch. 4.7: the sessions of `plans/route_planning/`, `plans/public_transport_routing/`, `plans/address_search/` and `plans/osm_importer/` were changing files of the tree during the whole run. This run touched several of the same files - `config/settings.py`, `config/config.py`, `tests/config/test_settings_cases.py`, `docs/standards/standard_config.md`, `api/app.py`, `service/SERVICE.md`, `service/SERVICE_ALGORITHM.md`, `data/DATA.md`, `api/API.md`, `api/API_ALGORITHM.md`, `docs/standards/naming_registry.md` and `agent_docs/memory/_cross_cutting.md` - only by adding its own lines next to theirs, so their hunks and these have to be kept apart when the work is committed. `api/API.md` and `api/API_ALGORITHM.md`, first created by this run, were overwritten a few minutes later by the session of `plans/route_planning/` with the documents of the whole layer; that version was kept and the account sections were added to it.

What changed:

- S-2: `SESSION_SIGNING_KEY: SecretStr` in `Settings`, required, refused below `SESSION_SIGNING_KEY_MIN_LENGTH` of 32 characters by its name and file `.env` only, exported by `config/config.py`; `SESSION_SIGNING_KEY=` in `.env.example`; its row and paragraph in `docs/standards/standard_config.md`, section Environment entries; the cases of a missing, an empty, a short and a 32-character key in `tests/config/test_settings_cases.py`; the invented key in `tests/common_runtime_settings.py` and in the settings of `tests/service/test_administrative_integration.py`, which every process that loads the facade now needs.
- S-4: `data/accounts.py` with `StoredAccount`, `apply_account_insert`, `fetch_account_by_id`, `fetch_account_by_pseudonym`, `apply_account_delete` and `build_stored_account`; the fixture `stored_account_cleanup` in `tests/conftest.py`; `tests/data/test_accounts_critical.py`.
- S-5: `service/actors.py` and `service/accounts.py`; `tests/service/test_actors_cases.py` and `tests/service/test_accounts_critical.py`.
- S-6: `api/sessions.py` and `api/accounts.py`, and the call `apply_account_routes(app)` in `build_app()` before `RequestContextMiddleware` is added; `tests/api/test_accounts_api_integration.py`.
- S-7: the section Moderator role of `db/README.md`; the section Accounts of `service/SERVICE.md`, `service/SERVICE_ALGORITHM.md`, `data/DATA.md` and `api/API.md` and the section Accounts and sessions of `api/API_ALGORITHM.md`; the section Account names of `docs/standards/naming_registry.md`; an entry in `agent_docs/memory/_cross_cutting.md` for the consumer contract of D-7 and the token of D-6.

Decisions while implementing:

- Agent decision at C:40, without asking: D-2 adds nothing. `fetch_api_engine` was delivered in `data/engine.py` before this run, so it is used as it is, and the router is registered by one call in `build_app()`, the way `apply_route_routes(app)` of `plans/route_planning/` is. This session did not confirm the agreement with Marek that D-2 asks for; the call is one line and follows the pattern his own initiative uses.
- Agent decision at C:40, without asking: the field is `SESSION_SIGNING_KEY`, not the lower-case name of S-2, because the delivered `Settings` names every field after its entry (D-1); it is mapped to `.env` in `ENVIRONMENT_ENTRY_FILES`, the file of the secrets. D-13 needed nothing more: argon2-cffi was pinned in the first run, and `accessibility-db==0.1.0` is a declared dependency of the root, so deptry needs no `known_first_party`.
- Agent decision at C:40, without asking: `create_account` passes `fetch_business_now()`, the instant of D-9 for `created_at`, and `log_in` passes `fetch_utc_now()`, the instant of D-6 for the expiry; both are the same instant.
- Agent decision at C:40, without asking: a request with more than one header `Authorization` is refused as `session_expired`, because only one header can carry the session and taking the first would ignore the other silently.
- Agent decision at C:40, without asking: the handler of `session_expired` clears the renewed token, so neither a deletion that loses a race with another deletion nor a consumer that answers a failed vote insert on `fk_vote_account` with `session_expired` gives a token the client is told to delete. `log_in` keeps its token through the same state of the request, so `SessionTokenMiddleware` is the one writer of `Session-Token`.
- Agent decision at C:40, without asking: a login whose pseudonym or password is outside the rules of registration ends in `InvalidCredentialsError` at once, without verifying a hash, because those rules are public and the duration tells nothing about an account.
- Agent decision at C:40, without asking: the layer documents keep their delivered names `SERVICE.md`, `SERVICE_ALGORITHM.md`, `DATA.md` and `API.md` instead of the generic names of S-7, and `api/API_ALGORITHM.md` is written too, because `agent_docs/memory/api/_shared.md` asks for the pair with the first product operation.
- Agent decision at C:40, without asking: the two request models share `AccountCredentialsRequest`, and the two reads share `build_stored_account`, so neither shape is written twice.
- Agent decision at C:40, without asking: the constant of the key in the state of the request is `SESSION_STATE_KEY`, because Bandit B105 reads any name holding the word token as a password; the key itself stays `session_token`.
- `tests/config/test_settings_cases.py` had CRLF endings in the working tree when this run edited it, so `ruff format --check` refused the whole file; its endings were turned into LF, which git does at the commit anyway, and no line changed.

Runs, on this machine with the virtual environment of the repository, Python 3.13.14 and the pinned tools, against a private local database of `db/compose.yaml` started as the Compose project `accounts-check` with invented values from the session scratchpad and its chain applied:

- `pytest tests/data/test_accounts_critical.py tests/service/test_accounts_critical.py`: 11 passed; the database held no account, fact or vote of the tests afterwards.
- `pytest -m "not critical"` of the whole repository: every test of accounts, of the configuration and of the programming interface passes; 8 failures, none in a file of this run - the two prose style tests on files of `mobile_app/`, and 6 OpenStreetMap tests whose temporary path holds the non-ASCII letter of the Windows user name, which osmium cannot open (`data/DATA.md`, section Architectural decisions).
- `ruff check .`: 25 findings, all in `mobile_app/`. `ruff format --check .`: 14 files, none of this run, among them files of the route planning session and `mobile_app/`.
- `mypy`: no issue in 77 files. `vulture`: clean. `deptry .`: two findings, both `pmtiles_mvt` in `mobile_app/tools/mock_backend/`. Every Bandit pass of the `makefile`: clean.
- `npx --no-install prettier --check` on every markdown file this run changed: clean.
- `python -m api` against that database: `create_account` 201, a second registration up to letter case 409, a pseudonym with a space 422 with `fields` `["pseudonym"]`, a wrong password 401 `invalid_credentials`, `log_in` with a differently cased trimmed pseudonym 200 with `Session-Token`, `read_own_account` 200 with a renewed token, without a token 401 `authentication_required`, with a malformed token 401 `session_expired`, `delete_own_account` 204 without `Session-Token`, and the old token afterwards 401 `session_expired`; a login with `łukasz_2` found the account `Łukasz_2`. The log of the process held only the operation, the status, the duration and the request identifier.
- The statement of the section Moderator role of `db/README.md` ran through `psql` as the service account and answered `UPDATE 0` for a pseudonym no account has; the critical test runs the same statement with `UPDATE 1`.

Acceptance criteria of `ACCOUNTS_PRD.md`:

- AC-1 - AC-5 and AC-13: passed by the scenario tests of S-3, the critical tests of S-4 and S-5, the integration tests of S-6 and the run of `python -m api`.
- AC-6 - AC-9: passed by the token cases of S-3, the actor matrix and the role read again of S-5, and the header tests of S-6, all with explicit instants.
- AC-10 and AC-11: passed by the deletion and reuse cases of S-4 and the scenario of S-5 on the local database.
- AC-12: the waiting, refused and rolled-back deletions of S-4 pass. The interleaving with the vote writer of `community_facts`, which does not exist yet, and with the importer is remaining integration work, not passed acceptance.
- AC-14: every row of the handoff table of `ACCOUNTS_SHAPE.md`, section Domain rules or explicit TODO, matches `db/`, and the critical tests ran on it as the service account.
- AC-15: S-1 is in the contract, with its operations and message shapes unchanged. The confirmation of the contract by Kuber and Adrian is still pending, as its state line records; for the explicit letters only the confirmation of Adrian is named there, because the set is the one the HarmonyOS client of Kuber already checks (F-14).
- AC-16: this record.

Run into:

- `apply_error_handlers` of `api/errors.py`, the skeleton, answers a body that is not UTF-8 with 500 `internal_error`: FastAPI raises `HTTPException` 400 for it, and the handler turns every status but 404 and 405 into `internal_error`, while the contract names `invalid_request` 422 for a body that is not JSON. It affects every operation with a body, not only accounts, and was seen with a body in Windows-1250 sent to `create_account`. It is outside this initiative and `api/errors.py` is being changed by another session, so it was not fixed here.
- Check 2.3 of `FINAL_CHECKLIST.md` asks for a moderator request refused on the running service. No moderator operation exists yet, so the refusal was verified only through a test-only operation in the integration tests and through the critical scenario; a person ticks the check.

Left for later, outside the code of this initiative:

- The steps of a human of the plan: a `SESSION_SIGNING_KEY` in every local `.env` and in the environment file of the demo before this code runs there, because every process that loads the facade refuses to start without it; telling Adrian and Kuber about the character set of S-1 and the consumer contract of D-7, and Rafał about the key for `DEPLOYMENT_CONFIG`; assigning the moderator role of the demo accounts; the commits and the Merge Request.
- The interleaving of AC-12 with the vote writer of `community_facts` and with the importer.

## Review of the whole initiative

Scope: S-1 - S-7 of `plans/accounts/ACCOUNTS_PLAN.md`, the account parts of every file the two runs changed. `implementation-dod-review` ran through the subagent `dod-reviewer` twice on 2026-10-04, read-only, with every mapped command run on this machine and the critical tests on the private database of the second run.

First pass, verdict ready after minor fixes:

- Blockers: none.
- Risk 1, a step of a human: the agreement of D-2 with Marek on the call `apply_account_routes(app)` in `build_app()` is not confirmed by this session.
- Risk 2, handed off: a body that is not UTF-8 is answered with 500 `internal_error` by `apply_error_handlers` of `api/errors.py`, outside this initiative; a separate task was suggested to the user for it.
- Risk 3, decided by Rafał on 2026-10-04: when both the pseudonym and the password of a registration are outside their rules, `invalid_request` keeps naming only `pseudonym`, the first field `InvalidAccountInputError` of S-3 carries, with no change of the code or of the contract, against collecting both fields; the clients check both fields before sending.
- Risk 4, remaining integration work as the Definition of Done of the plan allows: the interleaving of AC-12 with the vote writer of `community_facts` and with the importer.
- Risk 5, a step of a human: every process that loads the configuration facade, the importer included, refuses to start without `SESSION_SIGNING_KEY`, so every local `.env` and the environment file of the demo need it first.
- Improvement 1, done: the handler `apply_invalid_account_input` of `apply_account_routes` lost its unreachable branch that answered `invalid_request` with no field; it raises any other exception again.
- Improvement 2, done: the item AC-15 of the second run names the pending confirmation of Kuber and Adrian.
- Improvement 3, done: the docstring of `Settings` in `config/settings.py`, which passed 200 characters once the lines of this initiative and of `plans/public_transport_routing/` met, is a multi-line docstring.
- `pip-audit -r` of `argon2-cffi==25.1.0`: no known vulnerability.

Runs after the fixes: `pytest tests/api/test_accounts_api_integration.py tests/config tests/service/test_actors_cases.py`, 99 passed; `ruff check`, `ruff format --check` and `mypy` clean on the changed files.

Second pass, after the fixes: blockers none, no new improvement, the account sections of the layer documents, of `docs/standards/naming_registry.md`, of `db/README.md` and of `docs/standards/standard_config.md` read in full and found consistent with the code; the critical tests 11 passed, and the gates of the changed files clean.

Verdict: ready. Scope: the whole initiative `plans/accounts/`, S-1 - S-7. The steps of a human of the plan - the agreement of D-2 with Marek, `SESSION_SIGNING_KEY` in every environment, the confirmations of Kuber and Adrian, the moderator role of the demo accounts, the commits and the Merge Request - and the task for `api/errors.py` stay open after the closure; the move to `plans_finished/` proves none of them.
