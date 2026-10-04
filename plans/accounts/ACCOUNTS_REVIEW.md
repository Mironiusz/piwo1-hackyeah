# Review: MVP accounts and shared actor resolution

Document state: 2026-10-04, S-1 and S-3 implemented and reviewed, ready after minor fixes with the fixes done; S-2 and S-4 - S-7 waiting for the code of `plans/backend_skeleton/`

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
