# Review: Check of the public Nominatim instance against the decisions of the address search

Document state: 2026-10-04, implementation of the whole plan carried out, the contradiction R-7 ruled, review ready for the whole initiative, the bandit finding B310 accepted by the user, archived in `plans_finished/nominatim_client/`

## Implementation run of 2026-10-04

### Check before implementation

- `NOMINATIM_CLIENT_SHAPE.md` has a closed interview, regulator C:40, and no `Block: yes`; the plan is closed, has no open question and no TODO.
- The tree at `abad82d` on the branch `rm/requirements-preparation` has no commit after the check date of the facts, and `git status` lists only `plans/nominatim_client/` as untracked, so no file cited by the facts changed since they were checked. The lines cited by F-9 - F-22 carry the cited content.
- F-7 and F-8 were run again: `venv/Scripts/python.exe --version` -> `Python 3.13.14`, and the signature of `urllib.request.urlopen` and the two subclass checks give the values of F-8.
- The system clock read 00:14 on 2026-10-04 in Europe/Warsaw before the run, so `<day>` of D-11 is 2026-10-04. `zoneinfo` of the project Python finds no `Europe/Warsaw`, because the package `tzdata` is not installed; the script needs only UTC, so this does not touch it.

### Decisions taken while writing code

- Agent decision at C:40, without asking: an `http.client.HTTPException`, raised for example by a broken status line or a body cut short, is classified as `connection_error`. D-5 names only `URLError` and `OSError`, and without this an exception of the HTTP layer would end the run with a traceback and without the entry of the request already sent, against PRD AC-3.
- Agent decision at C:40, without asking: a response that `urlopen` returns without raising but with a status other than 200 is classified as `http_status`. D-5 gives `null` only for status 200, and every other outcome stops the run.
- Agent decision at C:40, without asking: Ctrl+C is caught in `main`, which prints one line to the standard error and returns the exit code 1 of a stopped run, after the `finally` block wrote the recording. D-7 gives 1 to a stopped run and names Ctrl+C as one.
- Agent decision at C:40, without asking: a list `CHECK_ITEMS` longer than `MAXIMUM_TEXTS` is a refused start with the exit code 2, because D-2 checks it before anything is sent and D-7 gives 2 to a start refused before sending.
- Agent decision at C:40, without asking: the exit codes are the constants `EXIT_FULL_RUN`, `EXIT_STOPPED_RUN` and `EXIT_REFUSED_START`, next to the constants of step 1, so that `main` carries no bare number.
- `stopped_early` is computed by `build_recording` from the entries alone, as fewer entries than texts or any failed entry, because the signature of D-8 gives it no other input.
- The module docstring is a raw string, because the Windows command of D-12 holds backslash sequences that a plain string would turn into control characters.

### What was done

- Step 1: `plans/nominatim_client/attachments/nominatim_check.py` exists with the constants, the `TypedDict` `RecordedEntry` and the functions of D-8.
- Step 2: ruff, ruff format and `mypy --strict` pass on the script, and both stand-in runs of D-10 behave as the Definition of Done says, with the refused starts checked as well. The commands and results are in the section Verification of the script of the report.
- Step 3: the live run sent 25 requests, all answered with status 200, and wrote `plans/nominatim_client/attachments/nominatim_check_2026-10-04.json`; exit code 0.
- Step 4: the recording holds no forbidden character and no CRLF line ending.
- Step 5: both policy pages were read again with WebFetch.
- Step 6: `plans/nominatim_client/attachments/nominatim_check_2026-10-04.md` holds R-1 - R-15, fourteen confirming and R-7 contradicting D-7.
- Step 7: the implementation stopped after the report and asked for the ruling on R-7. The user ruled on 2026-10-04, answering for the external API person, that D-7 changes in both points: `address.neighbourhood` with the house number in place of a missing `address.road`, and a result whose label repeats an earlier label of the same list is dropped, keeping the first. The ruling is in the section Contradictions of the report, and one sentence carries it into `plans/mvp/MVP_PLAN.md` D-3, one per changed decision as D-15 says, although the question offered to the user spoke of one sentence per change. `plans_finished/geocoding/` has no change.
- Step 8: `plans/mvp/MVP_PLAN.md`, section Supplementary files, has the item of step 8 after the item on `plans_finished/geocoding/GEOCODING_PLAN.md`.
- Checks of the Definition of Done: `venv/Scripts/ruff.exe check .` -> `All checks passed!`; `venv/Scripts/ruff.exe format --check .` -> `16 files already formatted`; `mypy --strict` on the script -> `Success: no issues found in 1 source file`; `venv/Scripts/python.exe -m pytest tests/architecture -o addopts=""` -> `120 passed`; no file under `tests/` and none of `pyproject.toml`, `makefile`, `.prettierignore`, `.gitattributes` and `.claude/settings.json` holds `nominatim`; `git status --short plans_finished/geocoding` is empty. `npx --no-install prettier --check "**/*.md"` fails on one file, `plans/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md`, from the commit `3582925` of another person, which this run did not touch; prettier passes on every file of `plans/nominatim_client/` and on `plans/mvp/MVP_PLAN.md`.
- Memory: no entry. The only durable outcome, the corrected label, binds the work package of the search through `plans/mvp/MVP_PLAN.md` D-3, which points to the report; no code unit of the search exists yet to hold a memory file, and a cross-cutting entry would repeat D-3.

### Parallel work during the run

- Another session works on the same tree. Before step 7, `git status` listed uncommitted changes of `AGENTS.md`, `AI_WORKFLOW.md`, `CLAUDE.md`, `agent_docs/memory/_cross_cutting.md`, `docs/standards/decision_registry.md` and `plans/mvp/MVP_PLAN.md`, the last written at 00:19:31, after this run started. Its changes of `plans/mvp/MVP_PLAN.md` touch D-9, D-10, Risks, Open questions and Supplementary files, not D-3 and not the item on `plans_finished/geocoding/GEOCODING_PLAN.md`; following `docs/standards/standard_agentic_workflow.md` ch. 4.7 they were taken as the current state, and only the passages of D-15 and step 8 were edited.
- `HEAD` moved during the run from `abad82d` to `be0977f`, and during the review to `d009868`. The commits between them change only files under `plans/backend_architecture/`, `plans/deployment/`, `plans/schema_revision/` and `plans/valhalla_routing/`, none of them cited by the facts of the plan, so the check before implementation and the verdict below still hold. The file that fails prettier was last changed by `d009868`.

### Review

The review of `implementation-dod-review` covers the whole initiative: the script, the recording, the report, this review and the two passages of `plans/mvp/MVP_PLAN.md` written by this run. The other uncommitted changes of the tree belong to the parallel session and are outside it.

Blockers: none.

Risks:

- `venv/Scripts/bandit.exe plans/nominatim_client/attachments/nominatim_check.py --confidence-level medium` reports B310, severity medium, confidence high, at the call of `urllib.request.urlopen`, because bandit cannot see that the scheme of the request is the constant `https` of `SEARCH_URL`. `docs/standards/standard_security.md` scopes static analysis to production code, the script is a tool of the check that nothing of the product imports, the passes of bandit in the `makefile` cover only `.claude/hooks`, and D-9 of the plan lists the gates of the script without bandit, so the finding blocks nothing by the letter of the standards; it needs a decision of the user whether it is accepted.
- `npx --no-install prettier --check "**/*.md"` fails on `plans/backend_architecture/BACKEND_ARCHITECTURE_SHAPE.md`, a file of another person last changed by the commit `d009868`. The item of the Definition of Done on prettier holds for every file of this initiative and for `plans/mvp/MVP_PLAN.md`, but not for the whole tree until that file is formatted by its owner.
- The recording is OpenStreetMap data under the ODbL in a public repository, which touches the open entry on the licence of the repository in `docs/standards/decision_registry.md`; this belongs to the human who commits it.
- The ruling on R-7 was given by the user for the external API person, whose own ruling is still to be confirmed, as are the answers of the shape interview.

Improvements: none needed for the scope of the plan.

Verification against the map of `docs/standards/standard_review.md`:

- `standard_agentic_workflow.md`: checked automatically, the parity, session context and dangerous commands tests pass within `tests/architecture` (`120 passed`); the parallel work followed ch. 4.7, recorded above.
- `standard_agent_docs.md`: checked automatically, `test_plan_document_contract.py` passes; this review follows the REVIEW format by manual reading, and the report gives its results in the form of the facts format.
- `standard_review.md`: checked manually, the Definition of Done of the plan holds item by item, with the prettier item limited as in Risks.
- `standard_documentation.md`: checked manually, the module, the constants, the `TypedDict` and every function of the script carry a docstring in plain language, the module docstring holds the run instruction of D-12, and the report is in the dry declarative tone of the standard.
- `standard_formatting.md`: checked automatically, `ruff format --check .` -> `16 files already formatted`, the prose style test passes, prettier passes on every file of this run and fails only on the file named in Risks; the recording was scanned by hand as D-14 says.
- `standard_git.md`: checked automatically, the conflict marker test passes; nothing was staged or committed.
- `standard_architecture.md`: not applicable, the script is no layer of the product and nothing imports it.
- `standard_config.md`: checked manually, the address of the public instance, the User-Agent and the limits are constants next to the code, used in one place, none a secret, and nothing of the target environment is in the change.
- `standard_database.md`: checked automatically, `bandit -t B608` on the script finds nothing; the script touches no database.
- `standard_errors.md`: checked manually, the call to the instance has an explicit timeout of 5 seconds chosen by D-4 and is never retried, and every failure stops the run.
- `standard_idempotency.md`: not applicable, the script only reads with GET and repeats nothing.
- `standard_code_quality.md`: checked automatically, `ruff check .` -> `All checks passed!`, `mypy` as configured -> `Success: no issues found in 2 source files`, `mypy --strict` on the script -> `Success: no issues found in 1 source file`, `vulture` as configured and on the script -> no finding, `deptry .` -> `Success! No dependency issues found.`
- `standard_logging.md`: checked automatically, `ruff check .` covers rule G; the script logs nothing, and its printed lines carry the label, not the searched text.
- `standard_naming.md`: checked automatically, `ruff check .` covers rule N; the prefixes `build_`, `fetch_`, `resolve_` and `apply_` match the responsibility of each function.
- `standard_security.md`: checked automatically, the passes of the `makefile` on `.claude/hooks` find nothing; bandit on the script reports B310, recorded in Risks; `pip-audit` not applicable, no dependency was added.
- `standard_tests.md`: checked automatically, `pytest` -> `120 passed`; the script has no test by PRD FR-4 and D-10, and its stop rule and pace were proven against the stand-in instead.
- `standard_time.md`: checked manually, every instant is an aware UTC value with milliseconds from `datetime.now(UTC)`, never a bare `datetime.now()`; there is no shared time module to use, because no product code exists.
- `standard_worker.md`: not applicable, no periodic task.
- `standard_frontend.md`: not applicable, no frontend code.

Verdict: ready, for the whole initiative. It qualifies the initiative for `plans_finished/` once the user decides on the B310 risk, because a decision awaited from the user stops the move (`docs/standards/standard_agentic_workflow.md` ch. 4.6).

### Closure

- The user decided on 2026-10-04 to accept the bandit finding B310 as a risk: the script and the configuration of the tools stay unchanged, against rewriting the request on `http.client` and against a pass of bandit for the attachment in the `makefile`.
- With the verdict ready for the whole initiative and no decision left open, the initiative is finished. The ruling of the external API person on R-7 and on the answers of the shape interview, and the commit and the Merge Request, are steps for a human after the closure.
- Archived on 2026-10-04 by a native move of `plans/nominatim_client/` to `plans_finished/nominatim_client/`, following `docs/standards/standard_agentic_workflow.md` ch. 4.6: the target did not exist, the directory had no link, and the SHA-256 of all 8 files was the same before and after the move.
- Editable references now point to `plans_finished/nominatim_client/`: the last sentence of D-3 and the item of step 8 in `plans/mvp/MVP_PLAN.md`, the locations in `NOMINATIM_CLIENT_PLAN.md` and `NOMINATIM_CLIENT_PRD.md`, and the run instruction in the docstring of `attachments/nominatim_check.py`. Reverting only those locations gives back the SHA-256 of the files before the move, and the tokens of the script outside its module docstring are unchanged.
- Left as historical records: the seed, the entries of this review above, the dated report `attachments/nominatim_check_2026-10-04.md`, the recording, and the evidence of F-19 in the plan, a command that was run.
- The script still works from the archive: `venv/Scripts/python.exe plans_finished/nominatim_client/attachments/nominatim_check.py` without an argument refuses to start with the exit code 2 and sends nothing. Its run instruction now writes a new recording next to the archived one, which the user may prefer to point elsewhere, as D-7 allows with the argument.
- While the closure was being written, the commit `c95d935` of a human took the archived directory and the changed `plans/mvp/MVP_PLAN.md` with the updated references; `git grep "plans/nominatim_client"` finds no reference outside the archive in it. The same commit changed `docs/hackathon/challenge_requirements.md`, and the deadline behind F-22 still stands at line 24.

### Observations for the user

- The stand-in showed that the gate of `plans_finished/geocoding/GEOCODING_PLAN.md` D-9 spaces the starts of requests, not their arrivals: with starts 1.100 s apart the stand-in saw arrivals 1.076 s apart. Locally the margin of 0.1 s absorbed this; over the network the part of a request before it reaches the instance cannot be measured from the client. No fact contradicts D-9, so the report gives no verdict on it.
- The instance answered two requests a few seconds apart from databases in different states (R-12). The tests of the search in `plans/mvp/` should not assume that a recorded response is what the instance answers today.
- A postcode result carries no `osm_type` and `osm_id` (R-2), which a fake response in the tests should keep.
- The usage policy now names a limit of 4 requests per minute for scripts running longer than a day or at regular intervals (R-9). Neither the search nor this check is such a script, but a scheduled repetition of the check would be.
