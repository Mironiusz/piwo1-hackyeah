# Review and Definition of Done standard

Document state: 2026-10-04

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

"Review" in this repository currently names two different things under very similar names: the `<TASK>_REVIEW.md` artifact in the agentic chain (the run log of one task) and the process of assessing whether a change is ready to merge (what `dod-reviewer` does). Without one place describing the second of them, the readiness criteria and the report order live only scattered across the skill and agent files, in two independently maintained copies (Claude Code and Codex) - and that is exactly the cost of duplication that `standard_architecture.md` warns against.

This standard settles three questions: what distinguishes review from the artifact of the same name in the agentic chain, what the mechanism and the report order of review in this repository are, and which points define a change as ready to merge.

## Scope and boundaries

This standard is responsible for the review process of a change and for the Definition of Done of the repository: the mechanism by which review is performed, the report order, the criteria for what to report and what not, and the final checklist.

What is not here:

- The mechanism of the agentic chain leading to review itself (seed -> shape -> PRD -> plan -> implementation -> review) - that is `standard_agentic_workflow.md`.
- The `<TASK>_REVIEW.md` artifact - the run log of a specific task (what was skipped, what the agent ran into, which decisions were made in the code). It is a document describing the history of one task and it loses its meaning after the task is closed; this standard describes a repeatable assessment process, valid for every change. The deciding sentence: `_REVIEW.md` is an event log, this standard is an assessment criterion.
- A Definition of Done for the internal architecture of a single layer does not exist as a separate checklist, because the set currently has no standard describing that architecture - see `docs/standards/README.md`, the unresolved boundaries and debts section. The checklist of this standard always applies, to every change.
- The rules that review checks (code quality, architecture, documentation, formatting, security and so on) - each of them lives in its proper standard. This document says how and in what order to check them, not what exactly each of them requires.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

A clarification specific to this standard: the duty to go through this process applies to every change of production code within a task, regardless of its size - the definition of a "module touched by the change" from `docs/standards/README.md` narrows which standards the duty to align applies to, it does not narrow whether review takes place at all. Adopting this standard does not force a retroactive review of changes already merged.

## Review mechanism in this repository

Review is performed by the `implementation-dod-review` skill, called directly or through the `dod-reviewer` subagent. The skill has a canonical pair covered by the parity test (`standard_agentic_workflow.md`, ch. 6.2): `.claude/skills/implementation-dod-review/SKILL.md` for Claude Code and `.agents/skills/implementation-dod-review/SKILL.md` for Codex, identical down to the character except for the differences explicitly allowed by that test.

The `dod-reviewer` subagent (`.claude/agents/dod-reviewer.md`) exists only in Claude Code - subagents in this sense are a Claude-only mechanism, with no counterpart in `.agents/` (`standard_agentic_workflow.md`, ch. 6.4). `.codex/agents/dod-reviewer.toml` is the counterpart on the Codex side in a different mechanism (a native Codex role, not a subagent) - consistent in content with the Claude version and covered by the role pair parity check in `tests/architecture/test_agent_docs_parity.py`. The check compares the instructions read from both variants and allows exactly one explicitly named difference between them: the name of the command runner, because Codex does not know tools named `Bash` and `PowerShell`. A divergence in anything else stops the tests, instead of waiting to be caught by eye.

The `dod-reviewer` subagent has no access to `Edit` or `Write` and runs in `permissionMode: plan` - it cannot introduce a fix, only describe it. This is enforced at the permission level, not only by instructions: review assesses the readiness of a change, it does not fix it for the author.

Review is invoked automatically at the end of `plan-implement` (`standard_agentic_workflow.md`, ch. 4.3, step 8) and manually, at any moment, at the user's request - on the current diff, if git context is available, or on the files indicated by the user, when it is not.

## Standard - verifying tool map

The table below maps each standard to the command that checks its rule automatically - where such a command exists. The Group column says whether the standard belongs to the workflow core, to the Python profile or to the frontend profile. A project outside the Python profile removes the profile rows together with the standard files, according to `docs/standards/README.md`. None of these commands covers the whole checklist of its standard: it checks the mechanical, repeatable part (syntax, format, a known pattern), not a domain rule or an architectural decision. The review of a standard's checklist against the change always takes place, regardless of whether a command exists for it.

| Standard                       | Group            | Automatic verification                                                                                                                                   |
| ------------------------------ | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard_agentic_workflow.md` | core             | `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` |
| `standard_agent_docs.md`       | core             | `pytest tests/architecture/test_plan_document_contract.py`                                                                                               |
| `standard_review.md`           | core             | no tool - manual review (this document)                                                                                                                  |
| `standard_documentation.md`    | core             | no tool - manual review                                                                                                                                  |
| `standard_formatting.md`       | core             | `ruff format --check .`, `npx --no-install prettier --check "**/*.md"`, `pytest tests/architecture/test_prose_style.py`                                  |
| `standard_git.md`              | core             | `pytest tests/architecture/test_conflict_markers.py`                                                                                                     |
| `standard_architecture.md`     | Python profile   | no tool - manual review                                                                                                                                  |
| `standard_config.md`           | Python profile   | `pytest tests/architecture/test_environment_contract.py`, created on 2026-10-04 with the first environment entries                                       |
| `standard_database.md`         | Python profile   | `bandit` (rule B608, building a query by concatenating strings)                                                                                          |
| `standard_errors.md`           | Python profile   | no tool - manual review                                                                                                                                  |
| `standard_idempotency.md`      | Python profile   | no tool - manual review                                                                                                                                  |
| `standard_code_quality.md`     | Python profile   | `ruff check .`, `mypy`, `vulture`, `deptry .`                                                                                                            |
| `standard_logging.md`          | Python profile   | `ruff check .` (rule G, lazy placeholders instead of an f-string)                                                                                        |
| `standard_naming.md`           | Python profile   | `ruff check .` (rule N)                                                                                                                                  |
| `standard_security.md`         | Python profile   | `bandit`, `pip-audit` (only for a new or upgraded dependency)                                                                                            |
| `standard_tests.md`            | Python profile   | `pytest`                                                                                                                                                 |
| `standard_time.md`             | Python profile   | no tool - manual review                                                                                                                                  |
| `standard_worker.md`           | Python profile   | not in the template - the task registry consistency test is created with the first periodic task                                                         |
| `standard_frontend.md`         | frontend profile | `npx tsc -b`, `npx oxlint`, `npx vitest run`, `pytest tests/architecture/test_prose_style.py` - set up with the first frontend code                      |

The command runs from the repository root, in an environment with the `dev` dependency group installed. The three `npx` commands of the frontend profile run from `frontend/`. The table points to the tool itself, not to the target name in the `makefile` - targets may be renamed, while the tool behind a standard's rule does not change with such a change.

## Report order and verdict

A review report always has five sections, in this order:

1. Blockers - problems which mean that the change is not ready.
2. Risks - problems that may be acceptable, but require a conscious decision, not an oversight.
3. Improvements - optional cleanups and quality suggestions, not required for readiness.
4. Verification - a pass over all the standards from the map above, each with one of four states: not applicable (the change does not touch the area of this standard, with a short reason), checked automatically (the standard has a mapped command, the command was run, and the result or its summary is in the report), checked manually (the standard has no mapped command, so the verification is only a review of the checklist), not checked (the reviewer did not get to it before the call limit; the item needs to be completed before the verdict covers this standard). A violation found along the way goes to Blockers or Risks, it does not stay here.
5. Verdict - one of three: `ready`, `ready after minor fixes`, `not ready`.

This order is not accidental: blockers and risks must be visible before the reader reaches the minor improvements, otherwise a real threat gets lost in the noise of stylistic remarks. The verdict is always last, because it is a conclusion from the sections above, not a starting point for justifying them.

Going through the whole map, not only through the standards that the reviewer, after reading the diff, deems relevant, is an intended requirement. A choice of the relevant standards left solely to the reviewer's judgment is invisible from the outside - omitting a standard that the change actually touches looks identical in the report to its conscious and justified exclusion. An explicit list of all the standards from the map, with one of the states next to each, turns this into something the reader of the report can verify themselves, without reconstructing the reviewer's train of thought.

`ready after minor fixes` is reserved for a situation in which the only problems found are in the Risks or Improvements section, not in Blockers - the presence of even one blocker rules out this verdict.

A run weighs more than review. Where the environment can be brought up and a run performed, reading the code and the documents does not replace the run. A known failure of a run within the scope of the change (tests, the chain on the environment, e2e tests) rules out the `ready` verdict, even when the letter of the acceptance criterion is met. Before the verdict, the reviewer checks whether a run later than the assessment of the criterion contradicts the assessed scope, and assesses the code of the target branch, not which initiative was supposed to close a given thing.

The verdict names its scope: the whole initiative, one task out of several, the plan alone or the indicated files. What happens to the initiative directory after review depends on this sentence: a final `ready` for the whole initiative qualifies it for the `plans_finished/` archive, `ready` for one task, a plan or a part of the code does not (`standard_agentic_workflow.md`, ch. 4.6). Review reports this qualification but does not perform the move - it stays in read-only mode, and the move is done by `plan-implement` after returning from review or by an agent that the user explicitly told to tidy up. Review invoked on an initiative that is already explicitly closed says so in the report instead of assessing it anew.

## What to report and what not to report

Review backs every finding with a specific file path, the place in it named by a section, an item or a code symbol (`standard_formatting.md`, section References to a place in a file), and a reason - a general remark without pointing to a place gives the author of the change nothing to fix. Review does not guess a contract that it does not find in the code or in the standards - a missing file, standard, module boundary, test or document is reported explicitly as missing, not assumed.

Review does not report:

- speculative rewrites that the change does not require,
- stylistic preferences without a specific, named risk,
- pre-existing problems, outside the scope of the current change, unless they make it harder to understand the change itself.

Rationale: a review that assesses a change against everything that has ever been imperfect in the repository stops being useful - the author of the change cannot fix the whole history of the code in one PR, and spreading attention over pre-existing problems draws it away from the problems that this specific change actually introduced.

## Checklist

A task can be considered finished when:

- the changes follow the DRY, SOLID and KISS principles,
- the code is simple, readable and contains no unnecessary fallbacks,
- fallbacks come from a real need for code safety, not from not knowing the contract,
- unclear places have been clearly pointed out instead of guessed,
- potential bugs or risks have been described to the user,
- the code contains no line comments,
- functions that need explanation have docstrings describing in plain language what they do,
- the code formatting follows the rules from this file,
- if the implementation was larger or changed a module, the whole must, after the change, comply with all the standards from /docs/standards
- the final reply clearly describes what was changed,
- the final reply explains why the changes were made,
- the final reply describes the decisions made,
- the final reply points out potential problems,
- the final reply says directly what could not be determined, if something was unclear,
- the Verification section goes through all the standards from the map, not only through a subset deemed relevant, and for a standard with a mapped command that command was actually run, not only judged by eye,
- the acceptance criteria were settled by a run wherever a run was possible, and no known run contradicts the verdict.
