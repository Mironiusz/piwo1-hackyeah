# Plan: Check of the public Nominatim instance against the decisions of the address search

Document state: 2026-10-04, plan closed

## Goal

Carry out `plans_finished/nominatim_client/NOMINATIM_CLIENT_PRD.md` (FR-1 - FR-6, AC-1 - AC-6): a script kept as an attachment of this initiative checks the live public Nominatim instance once, within the limits of FR-2, records every response, and a dated report states for each fact of `plans_finished/geocoding/GEOCODING_PLAN.md` F-1 - F-8, F-10, F-11 and for each new case whether it confirms or contradicts a decision of D-4 - D-10 there. `plans_finished/mvp/MVP_PLAN.md` points to the report and the recording, and its D-3 changes only by a ruling on a contradiction. No code of the product is written.

## Facts

F-1. Of the facts of the address search decision, F-1 - F-7 describe answers of the public instance, F-8 their times, F-9 the public Photon instance, and F-10 and F-11 readings of the usage policy and the privacy policy. | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-1; doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-8; doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-9; doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-10; doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-11 | 2026-10-04
F-2. The texts behind F-1 - F-7 are "Kraków", "Tauron Arena", "Biedronka", "Rynek Górny, Wieliczka", "Rynek Glowny", "Florianska 1", "Lema 7", "ul. Lema 7", "ulica Lema 7", "ul. Lipska 5", "Lipska 5", "al. Pokoju 7", "os. Strusia 23", "Szpital Uniwersytecki, Jakubowskiego 2", "Szpital Uniwersytecki" and "Jakubowskiego 2". | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-1 - F-7 | 2026-10-04
F-3. The search request is a GET of `https://nominatim.openstreetmap.org/search` with `q`, `format=jsonv2`, `addressdetails=1`, `limit=10`, `countrycodes=pl`, `viewbox=19.7922355,50.1261338,20.2173455,49.9676668`, `bounded=1`, `accept-language=pl` and the header `User-Agent: piwo1-hackyeah (HackYeah 2026 accessibility prototype)`. | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` D-1; doc:`plans_finished/geocoding/GEOCODING_PLAN.md` D-5 | 2026-10-04
F-4. The decisions checked are the normalization D-4, the request D-5, the filter to Kraków D-6, the label D-7, the cache D-8 with an empty list kept as an answer and a case-folded key, the gate D-9 and the timeout D-10. | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` D-4 - D-10 | 2026-10-04
F-5. The usage policy was read at `https://operations.osmfoundation.org/policies/nominatim/` and the privacy policy at `https://osmfoundation.org/wiki/Privacy_Policy`. | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-10; doc:`plans_finished/geocoding/GEOCODING_PLAN.md` F-11 | 2026-10-04
F-6. The name of a stop in the stops layer of MSIP carries the number of the platform after the name, for example "Rondo Mogilskie 01", so a person types the name without it. | cmd:`curl ".../K04_KOMUNIKACJA/MapServer/0/query?where=stop_name+LIKE+'Rondo+Mogilskie%'&outFields=stop_id,stop_name,linie&f=json"` -> `Rondo Mogilskie 01`, `Rondo Mogilskie 02`, `Rondo Mogilskie Opera 02` | 2026-10-03
F-7. The project Python is 3.13.14 and the project declares no runtime dependency. | cmd:`venv/Scripts/python.exe --version` -> `Python 3.13.14`; code:`pyproject.toml` key `dependencies` of table `[project]` | 2026-10-04
F-8. The standard library `urllib.request.urlopen` takes a timeout, and its `HTTPError` is a kind of `URLError`, while `TimeoutError` is a kind of `OSError`. | cmd:`venv/Scripts/python.exe -c "...inspect.signature(urllib.request.urlopen)..."` -> `(url, data=None, timeout=<object ...>, *, context=None)`, `True True` | 2026-10-04
F-9. `ruff check .` and `ruff format --check .` cover every Python file of the tree apart from the tool directories, so a script under `plans/` is linted and format-checked. | code:`makefile` target `lint-python`; code:`pyproject.toml` key `exclude` of table `[tool.ruff]`; code:`pyproject.toml` key `extend-exclude` of table `[tool.ruff]` | 2026-10-04
F-10. mypy checks only `.claude/hooks`, vulture only `.claude/hooks` and `tests`, bandit only `.claude/hooks`, and pytest collects only `tests`. | code:`pyproject.toml` key `files` of table `[tool.mypy]`; code:`pyproject.toml` key `paths` of table `[tool.vulture]`; code:`makefile` target `security`; code:`pyproject.toml` key `testpaths` of table `[tool.pytest.ini_options]` | 2026-10-04
F-11. The prose style gate scans every `.py` and `.md` file outside the tool directories for forbidden characters and bold, so the script and the report fall under it and a `.json` recording does not. | code:`tests/architecture/test_prose_style.py` constant `SCANNED_FILE_SUFFIXES`; code:`tests/architecture/test_prose_style.py` constant `EXCLUDED_DIRECTORY_NAMES` | 2026-10-04
F-12. Prettier checks only `**/*.md` and skips `plans_finished/`. | code:`makefile` target `lint-docs`; code:`.prettierignore` entry `plans_finished/` | 2026-10-04
F-13. A copy of someone else's document in `plans/<INITIATIVE>/attachments/` comes under the gate, and on a hit the user chooses how it is handled. | doc:`docs/standards/standard_formatting.md` section Emphasis in prose | 2026-10-04
F-14. A function name starts with `fetch_` for reading from a source, `build_` for assembling a value, `resolve_` for a decision and `apply_` for executing one. | doc:`docs/standards/standard_naming.md` section Function names: a verb that states the responsibility | 2026-10-04
F-15. Code has no line comments, and its logic is documented in docstrings. | doc:`docs/standards/standard_code_quality.md` section Comments in code | 2026-10-04
F-16. An existing script of the repository uses `main` as its entry point. | code:`.claude/hooks/block_dangerous_commands.py` function `main` | 2026-10-04
F-17. A technical timestamp is an aware instant in UTC. | doc:`docs/standards/standard_time.md` section The time "now": on the database side and on the Python side | 2026-10-04
F-18. An attachment of an archived initiative is frozen as to its data, queries and logic, and only the run instruction in the docstring of an attachment script is updated with the new path. | doc:`docs/standards/standard_agentic_workflow.md` ch. 4.6 | 2026-10-04
F-19. Line endings in the repository are LF, and on Windows `Path.write_text` without `newline="\n"` wrote CRLF, which prettier rejected. | code:`.gitattributes` entry `* text=auto eol=lf`; cmd:`npx prettier --check plans/nominatim_client/*.md` after a write without `newline` -> `Code style issues found`, after `newline="\n"` -> `All matched files use Prettier code style!` | 2026-10-04
F-20. `plans_finished/mvp/MVP_PLAN.md` carries the search decision in D-3 and lists `plans_finished/geocoding/GEOCODING_PLAN.md` as the decision behind D-3 under Supplementary files. | doc:`plans_finished/mvp/MVP_PLAN.md` D-3; doc:`plans_finished/mvp/MVP_PLAN.md` section Supplementary files | 2026-10-04
F-21. The agent runs local tools and tests without asking. | doc:`CLAUDE.md` section Target environment | 2026-10-04
F-22. The Kraków solution is submitted no later than 11:00 on 4 October 2026. | doc:`docs/hackathon/challenge_requirements.md` section Shared facts | 2026-10-04

## Decisions

D-1. The check is one Python script, `plans_finished/nominatim_client/attachments/nominatim_check.py`, using only the standard library: `urllib.request` for the request, `json` for the body and the recording, `time.monotonic` for the pace and `datetime` for the instants (F-7, F-8). No dependency is added, so `pyproject.toml` does not change. Agent decision at C:40, without asking: the project has no HTTP client among its dependencies, and adding one for a script outside the product would put it on the list of the product.

D-2. The script holds the list of the check as the constant `CHECK_ITEMS`, a tuple of pairs of a label and a text, in this order: `("F-1", "Kraków")`, `("F-2", "Tauron Arena")`, `("F-3, F-7", "Biedronka")`, `("F-3", "Rynek Górny, Wieliczka")`, `("F-4", "Rynek Glowny")`, `("F-4", "Florianska 1")`, `("F-5", "Lema 7")`, `("F-5", "ul. Lema 7")`, `("F-5", "ulica Lema 7")`, `("F-5", "ul. Lipska 5")`, `("F-5, F-7", "Lipska 5")`, `("F-5", "al. Pokoju 7")`, `("F-5", "os. Strusia 23")`, `("F-6", "Szpital Uniwersytecki, Jakubowskiego 2")`, `("F-6", "Szpital Uniwersytecki")`, `("F-6", "Jakubowskiego 2")`, `("stop", "Rondo Mogilskie")`, `("stop", "Czerwone Maki P+R")`, `("letter case", "tauron arena")`, `("letter case", "TAURON ARENA")`, `("postcode", "Stanisława Lema 7, 31-571")`, `("postcode", "31-571 Kraków")`, `("no match", "Qwxzvbn")`, `("typo", "Tauron Arnea")`, `("typo", "Florjanska 1")`. That is 25 texts, each once, below the 40 of PRD FR-2; the constant `MAXIMUM_TEXTS = 40` is checked against the length of the list before anything is sent. Agent decision at C:40, without asking: the texts of F-2 of this plan check F-1 - F-7 of `plans_finished/geocoding/GEOCODING_PLAN.md` again with the same input, the stops follow F-6 of this plan, and every text is a public place or a public building (PRD FR-6).

D-3. Every request is the request of F-3 of this plan, with `q` set to the text exactly as listed, without the normalization of D-4 there, because the check has to see whether that normalization is still needed. The constants `SEARCH_URL`, `USER_AGENT` and `FIXED_PARAMETERS` hold the values of F-3. Agent decision at C:40, without asking: it follows from PRD FR-2, which identifies the application as the search does.

D-4. A new request starts no earlier than 1.1 seconds after the start of the previous one, measured with `time.monotonic` (`MINIMUM_INTERVAL_SECONDS = 1.1`), and waits at most 5 seconds for each blocking operation (`TIMEOUT_SECONDS = 5.0`, passed to `urlopen` and covering the connection and every read). Agent decision at C:40, without asking: the values are those of PRD FR-2.

D-5. A request has one of five outcomes, written in the field `error` of its entry: `null` for status 200 with a body that is valid JSON; `http_status` for `HTTPError`, with its code in `status`; `timeout` for `TimeoutError`, also when it arrives wrapped in a `URLError`; `connection_error` for any other `URLError` or `OSError`; `invalid_json` for status 200 with a body that is not valid UTF-8 JSON. Any outcome other than `null` stops the run at once: nothing is retried and no further text is sent. Agent decision at C:40, without asking: PRD FR-2 names 403, 429 and no answer within 5 seconds; stopping on every other failure as well is stricter and cannot exceed the limits of the instance.

D-6. A run writes one recording, a UTF-8 JSON file with LF line endings, `ensure_ascii=False` and an indent of 2 (F-19), with the object `{"service_url", "user_agent", "parameters", "started_at", "finished_at", "stopped_early", "entries"}`. Each entry is `{"check_item", "text", "sent_at", "elapsed_seconds", "status", "error", "body"}`, where `sent_at` is an aware UTC instant written by `datetime.isoformat` with milliseconds (F-17), `elapsed_seconds` is rounded to three decimals, and `body` is the parsed JSON of the response, with the field `licence` of every result kept as the instance sent it (PRD FR-3), or `null` when there is no valid body. Agent decision at C:40, without asking: one file per run keeps the order and the times needed for AC-2, and the parsed body lets the tests of `plans_finished/mvp/` build a fake response with one serialization.

D-7. The script takes exactly one argument, the path of the recording. It refuses to start, before sending anything, when the argument is missing, when the file already exists or when its directory does not exist, and it opens the file in the mode `x`, so that a recording is never overwritten (F-18). The recording is written in a `finally` block, so a run stopped by a failure or by Ctrl+C still keeps the entries already received. The exit code is 0 for a full run, 1 for a stopped run and 2 for a refused start. Each sent request prints one line to the standard output with its number, label, status or error and time. Agent decision at C:40, without asking: an argument instead of a fixed path lets a run after archiving write outside the frozen archive.

D-8. The functions of the script, following F-14 and F-16: `build_search_url(text: str) -> str`; `fetch_search_entry(check_item: str, text: str) -> RecordedEntry`, which sends one request and returns its entry, `RecordedEntry` being a `TypedDict` of the fields of D-6; `resolve_run_must_stop(entry: RecordedEntry) -> bool`; `build_recording(started_at: str, finished_at: str, entries: list[RecordedEntry]) -> dict[str, object]`; `apply_recording(path: Path, recording: dict[str, object]) -> None`; and `main(argv: list[str]) -> int`, called under `if __name__ == "__main__"` with `sys.exit(main(sys.argv))`. Every function and the module carry a docstring and no line comment (F-15); the module docstring holds the run instruction of D-12 (F-18). Agent decision at C:40, without asking.

D-9. The script is held to `ruff check`, `ruff format --check` and the prose style gate, which already cover it (F-9, F-11), and is checked once in the implementation with `mypy --strict` on its file alone; no configuration of a tool changes. Agent decision at C:40, without asking: mypy does not cover `plans/` (F-10), and adding it to the configuration for one attachment would extend a gate of the product to a tool outside it.

D-10. Before the live run, the stop rule and the pace are verified against a stand-in for the instance on `127.0.0.1`, started by a one-off snippet in the scratchpad of the session that imports the script and replaces `SEARCH_URL`: once answering 200 with `[]` for every request, and once answering 429 to the twelfth request. Nothing of it is kept in the repository; its commands and results are recorded in the report of D-13. Agent decision at C:40, without asking: the live instance cannot be made to refuse on purpose, and the tests of the repository must not use the network (PRD FR-4).

D-11. The live run is made once, by the agent during `plan-implement`, from the machine of the session (F-21), with the recording `plans_finished/nominatim_client/attachments/nominatim_check_<day>.json`, where `<day>` is the calendar day of the start of the run in Europe/Warsaw. Calling `plan-implement` is the decision of a person that PRD FR-2 requires for a run. Agent decision at C:40, without asking.

D-12. The module docstring holds the instruction for a repeated run: the command `venv\Scripts\python.exe plans_finished\nominatim_client\attachments\nominatim_check.py plans_finished\nominatim_client\attachments\nominatim_check_<day>.json`, the rule that a run is started only by the decision of a person and never by a test or an automatic check, the meaning of the exit codes, and the URLs of the two policies of F-5 to read again by hand (PRD FR-1, FR-4). Agent decision at C:40, without asking.

D-13. The result is the report `plans_finished/nominatim_client/attachments/nominatim_check_<day>.md`, with the day of D-11, in four sections: Verification of the script, with the commands and results of D-9 and D-10; Run, with the command, the instants, the number of requests and whether the run stopped; Results, one item `R-N.` per fact F-1 - F-8, F-10, F-11 of `plans_finished/geocoding/GEOCODING_PLAN.md` and per new case, in the form `R-N. <claim>. Verdict: confirms D-x | <evidence> | <day>` or `Verdict: contradicts D-x`, with evidence of the kind `cmd:` pointing to the number of the entry in the recording, or to a reading of a policy page; and Contradictions, listing every item that contradicts a decision with the ruling on it, or "None.". F-8 is judged from the slowest `elapsed_seconds` of the run against the 5 seconds of D-10, and F-10 and F-11 from a new reading of the pages of F-5 (PRD FR-1). Agent decision at C:40, without asking: the facts format of `docs/standards/standard_agent_docs.md` gives the report the same evidence discipline as a plan.

D-14. After the run, the recording is scanned for the characters forbidden by `docs/standards/standard_formatting.md` and the report is checked by the prose style gate (F-11, F-13). A forbidden character in the recording stops the implementation with a question to the user, as the shape promised, although no gate scans `.json`. Agent decision at C:40, without asking.

D-15. A contradiction stops the implementation after the report: the agent shows each contradicting item to the user, asks for the ruling of the user and the external API person, and records it in the section Contradictions of the report of D-13. Only after a ruling to change a decision does the agent append to `plans_finished/mvp/MVP_PLAN.md` D-3 one sentence per changed decision, of the form "Corrected on <day> by `plans_finished/nominatim_client/`: `plans_finished/geocoding/GEOCODING_PLAN.md` D-x <new rule>, see `plans_finished/nominatim_client/attachments/nominatim_check_<day>.md` R-N.", and nothing in `plans_finished/geocoding/` changes (PRD FR-5). Agent decision at C:40, without asking.

## Scope of changes

1. Create `plans_finished/nominatim_client/attachments/nominatim_check.py` with the constants `SEARCH_URL`, `USER_AGENT`, `FIXED_PARAMETERS`, `MINIMUM_INTERVAL_SECONDS`, `TIMEOUT_SECONDS`, `MAXIMUM_TEXTS` and `CHECK_ITEMS` (D-2, D-3, D-4), the `TypedDict` `RecordedEntry` and the functions of D-8, behaving as D-5, D-6 and D-7 say, with the module docstring of D-12.
2. Verify the script without the network: `venv/Scripts/ruff.exe check plans_finished/nominatim_client/attachments/nominatim_check.py`, `venv/Scripts/ruff.exe format --check plans_finished/nominatim_client/attachments/nominatim_check.py`, `venv/Scripts/mypy.exe --strict plans_finished/nominatim_client/attachments/nominatim_check.py`, and the two runs against the stand-in of D-10; their commands and results go into the report in step 6.
3. Make the live run of D-11, producing `plans_finished/nominatim_client/attachments/nominatim_check_<day>.json`.
4. Scan the recording for forbidden characters (D-14).
5. Read again the two policy pages of F-5.
6. Write `plans_finished/nominatim_client/attachments/nominatim_check_<day>.md` as D-13 says.
7. Only when the report lists a contradiction: follow D-15.
8. In `plans_finished/mvp/MVP_PLAN.md`, section Supplementary files, after the item "`plans_finished/geocoding/GEOCODING_PLAN.md`, the decision behind D-3." add the item "`plans_finished/nominatim_client/attachments/nominatim_check_<day>.md`, the check of the public Nominatim instance behind D-3, and `plans_finished/nominatim_client/attachments/nominatim_check_<day>.json`, its recorded responses, material for the tests of the search with a fake transport."

## Rollout order

1. Step 1, then step 2; a failing check returns to step 1.
2. Step 3 only after step 2 passes, so that a defect of the stop rule cannot reach the live instance.
3. Steps 4 - 6.
4. Step 7, when it applies; the implementation waits for the ruling.
5. Step 8.
6. Checks of the Definition of Done.

Steps for a human: the ruling of the external API person on every contradiction of step 7 and the confirmation of the answers of the shape interview; the commit and the Merge Request of the new and changed files.

## Definition of Done

- The stand-in run answering 200 sends 25 requests with no two starts less than 1.1 seconds apart, records 25 entries and exits with 0; the stand-in run refusing the twelfth request receives exactly 12 requests, records 11 entries with status 200 and one with status 429 and `error` `http_status`, sets `stopped_early` to true and exits with 1 (AC-2).
- `CHECK_ITEMS` holds exactly the 25 pairs of D-2, each text a public place or a public building (AC-6).
- The live recording exists, holds at most 25 entries, and every entry with results keeps the field `licence` of each result (AC-3).
- The report has an item for each of F-1 - F-8, F-10, F-11 and for each of the five new cases, each naming a decision of D-4 - D-10 and a verdict, and a Contradictions section (AC-1).
- Every contradiction has a recorded ruling before `plans_finished/mvp/MVP_PLAN.md` D-3 changes, and `git status` shows no change under `plans_finished/geocoding/` (AC-5).
- `plans_finished/mvp/MVP_PLAN.md` carries the item of step 8.
- `venv/Scripts/ruff.exe check .` and `venv/Scripts/ruff.exe format --check .` pass, and `venv/Scripts/mypy.exe --strict` passes on the script.
- `npx --no-install prettier --check "**/*.md"` passes, and `venv/Scripts/python.exe -m pytest tests/architecture` passes, the prose style gate and the check of this closed plan included.
- No file under `tests/` and no configuration of a tool refers to the script (AC-4).

## Risks

- The submission closes at 11:00 on 4 October 2026 (F-22), the day of this plan; a contradiction found after the search work package of `plans_finished/mvp/` has started lands in code already written.
- The live run may get the machine of the session blocked by the instance; the stop of D-5 limits it to one refused request, but the same machine is used for development.
- The stop rule is proven against a stand-in, not against the live instance, which cannot be made to refuse on purpose.
- The live run checks the instance from the machine of the session, not from the server of the demo; whether the server is blocked stays with `plans_finished/geocoding/GEOCODING_PLAN.md` D-16.
- The recording is not covered by any formatting gate (F-11, F-12); D-14 covers it by hand for this run only, and a repeated run needs the same scan.
- The recording is OpenStreetMap data under the ODbL in a public repository, which touches the open entry on the licence of the repository in `docs/standards/decision_registry.md`.
- When the initiative is archived, the paths in `plans_finished/mvp/MVP_PLAN.md` are updated as editable references (F-18); the tests of the search should copy what they need instead of reading from `plans/`.
- The answers of the shape interview were given by the user; the ruling of the external API person on them is still to be confirmed.

## Open questions

None.

## Supplementary files

- `plans_finished/nominatim_client/NOMINATIM_CLIENT_PRD.md`, the contract this plan implements.
- `plans_finished/nominatim_client/NOMINATIM_CLIENT_SHAPE.md`, the scenarios and the domain rules behind the PRD.
- `plans_finished/nominatim_client/NOMINATIM_CLIENT_SEED.md`, the verbatim request.
- `plans_finished/geocoding/GEOCODING_PLAN.md`, the facts and the decisions this check verifies.
