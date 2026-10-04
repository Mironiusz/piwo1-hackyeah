# Standards map

Document state: 2026-10-04

This directory is the set of all standards in force in the repository. This file is the entry point to the set - do not open a standard while skipping this map, because the status of a document and its group are recorded here.

The source of truth for every rule is the standard, not `CLAUDE.md` or `AGENTS.md`. In case of a discrepancy between the repository core and a standard, the standard prevails - the core deliberately keeps only hard bans applicable without context, while justifications, exceptions and edge cases live here. Above everything stands the product specification named in `CLAUDE.md`, section What we are building: in case of a discrepancy between a standard and the specification, the specification prevails.

## Standards

The set is divided into three groups:

- Workflow core - six standards describing work with agents, documentation, formatting, review and git. They apply in every project created from the template.
- Python profile - twelve standards for a Python service with a PostgreSQL database, Alembic migrations and a separate worker process. A project that is not such a service removes their files, their rows from this map and from the map in `standard_review.md`, and replaces references to them in the core with its own standards or removes them. The stack was chosen in `plans_finished/mvp/` and is now carried by the backend foundation. The backend foundation now implements Python/FastAPI/PostgreSQL and keeps this profile in force.
- Frontend profile - one standard for the web frontend in `frontend/`: its technology, its code unit, the rules it takes from the product and its automatic gates. Added on 2026-10-03 by `plans_finished/frontend_stack/`. Frontend code is held to this standard and to the six of the workflow core; the Python profile does not apply to it.

Meaning of the statuses: ready - the document has the full content of its rules. partial - the document has content, but at least one of its rules is waiting for a decision or a measurement; the reason is in the standard itself. skeleton - the document has only the core sections with one-sentence descriptions of what is to be written there.

| File                           | Group            | Status | Responsible for                                                                    |
| ------------------------------ | ---------------- | ------ | ---------------------------------------------------------------------------------- |
| `standard_agentic_workflow.md` | core             | ready  | the seed -> plan -> review chain, hooks, subagents, Claude Code and Codex parity   |
| `standard_agent_docs.md`       | core             | ready  | the format of SEED, SHAPE, PRD, PLAN, REVIEW and `agent_docs/memory` entries       |
| `standard_review.md`           | core             | ready  | the review process, the standard - tool map, Definition of Done                    |
| `standard_documentation.md`    | core             | ready  | documentation of code units and the tone of prose                                  |
| `standard_formatting.md`       | core             | ready  | code and markdown formatting, forbidden characters, no bold, references by section |
| `standard_git.md`              | core             | ready  | agent permissions for git, branch roles, merge directions                          |
| `standard_architecture.md`     | Python profile   | ready  | layer boundary, one place for cross-cutting rules, external calls                  |
| `standard_config.md`           | Python profile   | ready  | three configuration layers, environment files, validation, secrets                 |
| `standard_database.md`         | Python profile   | ready  | form of schema changes, database privacy, data access, queries                     |
| `standard_errors.md`           | Python profile   | ready  | error handling, retries, timeouts                                                  |
| `standard_idempotency.md`      | Python profile   | ready  | idempotency key, reconciliation, deduplication                                     |
| `standard_code_quality.md`     | Python profile   | ready  | static analysis, complexity, comments, performance                                 |
| `standard_logging.md`          | Python profile   | ready  | log entry format, levels, personal data in logs                                    |
| `standard_naming.md`           | Python profile   | ready  | names of files, functions and constants                                            |
| `standard_security.md`         | Python profile   | ready  | static security analysis, dependency vulnerabilities, data in local environments   |
| `standard_tests.md`            | Python profile   | ready  | test layers, critical tests, mandatory tests                                       |
| `standard_time.md`             | Python profile   | ready  | time model, time zones, time windows in data                                       |
| `standard_worker.md`           | Python profile   | ready  | the worker process, the periodic task contract, locks                              |
| `standard_frontend.md`         | frontend profile | ready  | technology, code unit, product rules and gates of frontend code                    |

The boundaries between the standards are described in the Scope and boundaries section of each of them.

## Registries next to the standards

Two files in this directory are not standards and have no core sections:

- `naming_registry.md` - an expandable registry of names actually used in the repository, describing the actual state, not the target one. `standard_naming.md` refers to it directly. It is empty for now.
- `decision_registry.md` - decisions deliberately postponed, with the reason for the deferral and the condition for resolving them. It looks to the future, unlike the section on boundaries and debts at the end of this file, which looks to the past.

## Project documents outside the standards

The project adds its own directories next to `docs/standards/`, each with its provenance:

- `docs/product/` - the product specification, `docs/product/specification.md`, written by the team, with the target database schema in `docs/product/schema.md`, part of the specification since version 6. It is the source of truth for the product, named in `CLAUDE.md`, section What we are building. Its first version, written on 2026-10-03, settles the target group and the MVP scope. Next to it, `docs/product/api_contract.md` is the contract of the programming interface between the clients and the service, decided in `plans_finished/api_contract/`; it is not part of the specification, which prevails over it. Three more documents stand there, written by the frontend person on 2026-10-03 and 2026-10-04 for version 11 of the specification: `docs/product/user_journeys.md`, the steps of a person through every mandatory feature, `docs/product/views.md`, the list of views of the web frontend derived from those journeys, with what each view needs from the programming interface, and `docs/product/interface_texts.md`, the texts of the interface in Polish and English. The specification prevails over all three.
- `docs/hackathon/` - `challenge_requirements.md`, a working summary of the rules and task descriptions of the two HackYeah 2026 challenges the project is submitted to, written on 2026-10-03 from the organizers' PDFs. The PDFs remain the authority and are not stored in the repository.
- `docs/deployment/` - `hosted_demo.md`, the written instructions for standing the hosted demo up on the server, written on 2026-10-04 by `plans_finished/deployment/`, with the commands completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`.
- `docs/setup/backend.md` - local Linux/Windows installation, database/API launch, shared publication interfaces and consumer prerequisites of the implemented backend foundation.
- `docs/setup/` - `EMULATOR_SETUP.md`, the instructions for installing the OpenHarmony toolchain and emulator and running a HarmonyOS client on it, merged on 2026-10-04 with pull request 16 from the branch `js/emulator-setup`. The client `accessway/`, `scripts/env.sh` and the `make` targets it runs, such as `make setup` and `make aw-run`, are not in the repository, and whether a HarmonyOS client is built is still open in `decision_registry.md`, entry HarmonyOS port and the Huawei submission.
- `AI_WORKFLOW.md` in the repository root - the description of how AI tools are used here, required by the Huawei challenge.
- `MVP.md` in the repository root - the summary of the MVP: its scope, its technical decisions, the initiatives that build it with their owners and order, and the requirements each of them meets, written on 2026-10-04 by `plans_finished/mvp/`. The product specification prevails over it.
- `TEAM.md` in the repository root - the members of the team and the role each one holds, set by Rafał on 2026-10-04, so that documents name people instead of roles (`CLAUDE.md`, section Language and communication style).

## Deviation rule

Common to all standards, in the strict version for a repository without legacy code:

A standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with a standard blocks review regardless of who wrote it and when.

When the repository has legacy code - for example after the first production release - relaxing this rule to the soft version is to be an explicit decision recorded in this file together with the date and the reason. In the soft version non-compliant code does not block review as long as nobody modifies it, and the obligation to adapt arises in the module touched by the change, that is, in the code unit from `standard_documentation.md` in which the change modifies at least one file. The soft version is not a state that comes into force by itself.

Each standard repeats this rule in its `Deviation rule` section, possibly narrowed in a way specific to its topic. Exception: `naming_registry.md` describes the actual state by definition, so the rule applies to it differently - this is written directly in the registry itself.

## What to open before a task

| Task type                                                                   | Documents to open before the work                                                                                                    |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Anything about product behavior                                             | the product specification named in `CLAUDE.md` - it is the source of truth, not a reference point                                    |
| Scope, deliverables, deadlines, judging or the rules of the challenges      | `docs/hackathon/challenge_requirements.md`                                                                                           |
| A new task of undetermined shape                                            | `agent_docs/ai_workflows/shape_prd_workflow.md` and the `plan-shape` skill, before any code is written                               |
| Closing, cancelling or resuming an initiative in `plans/`                   | `standard_agentic_workflow.md` ch. 4.6                                                                                               |
| Assessing whether a change is ready to merge                                | the `implementation-dod-review` skill and `standard_review.md` with the other standards from the map                                 |
| Work on something that somebody has already changed before                  | `agent_docs/memory/`, if an entry exists                                                                                             |
| Anything about git, branches or a Merge Request                             | `standard_git.md`                                                                                                                    |
| Using AI tools in a new way, or changing a skill, hook, agent role or rule  | `AI_WORKFLOW.md` - the Huawei challenge requires it to stay current                                                                  |
| Writing or updating code documentation                                      | `standard_documentation.md`                                                                                                          |
| Code and markdown formatting                                                | `standard_formatting.md`                                                                                                             |
| A new code unit or a change to the structure of an existing one             | `standard_architecture.md` and `standard_naming.md`, section File names                                                              |
| Code quality, comments, complexity, performance                             | `standard_code_quality.md`                                                                                                           |
| Code security, static analysis, dependency vulnerabilities                  | `standard_security.md`                                                                                                               |
| Tests                                                                       | `standard_tests.md`                                                                                                                  |
| Naming of files and functions                                               | `standard_naming.md` and `naming_registry.md`                                                                                        |
| Configuration and secrets                                                   | `standard_config.md`                                                                                                                 |
| Logging                                                                     | `standard_logging.md`                                                                                                                |
| Error handling, retries, timeouts                                           | `standard_errors.md`                                                                                                                 |
| Idempotency, reconciliation, deduplication                                  | `standard_idempotency.md`                                                                                                            |
| Time, time zones, time windows in data                                      | `standard_time.md`                                                                                                                   |
| Anything that touches a table, column, view or schema                       | `standard_database.md`, the schema dump for the actual state, the product specification with `docs/product/schema.md` for the target |
| A periodic worker task, a lock, a time window, a frequency                  | `standard_worker.md`                                                                                                                 |
| Permissions, read visibility                                                | `standard_architecture.md`, section One place for cross-cutting rules                                                                |
| Frontend code, the map, interface texts                                     | `standard_frontend.md` and the product specification                                                                                 |
| A request, a response, a path or an error code of the programming interface | `docs/product/api_contract.md` and the product specification                                                                         |
| Deploying, restarting or checking the hosted demo                           | `docs/deployment/hosted_demo.md` and `CLAUDE.md`, section Target environment                                                         |

The project adds its own documents to this table, for example operational knowledge about the environment or a database schema dump, together with their provenance.

If after reading the indicated documents the contract is still not unambiguous, it is a question for the user, not a place for a fallback - see the hierarchy for resolving conflicts in `CLAUDE.md` and `AGENTS.md`. Check `decision_registry.md` at the same time: a missing rule may be a recorded deferral, not a gap.

## Unresolved boundaries and debts

This section is a log of decisions already made and debt already present. It grows by an entry every time an initiative leaves behind a finding deliberately left unfixed - the `REVIEW.md` artifact of a given initiative records them at the scale of one task, and what goes beyond that scope ends up here.

Debts the template starts with:

- The set has no standard describing the internal architecture of a single layer, that is, the split of responsibilities between files in its directory. A split rule written before the code exists would be guessing. Condition for writing it: a layer has so many files that their split starts raising questions in review.
- `standard_documentation.md` has no Scope and boundaries section and no checklist.
- The Python profile gates that check code (layer boundaries, environment contract, consistency of the periodic task registry) are not part of the template, because the template has no code. The project sets them up together with the first code of a given layer.

Decisions recorded on 2026-10-03, when the project was set up from the template:

- The whole repository is written in English, including the standards, skills and architecture tests translated from the Polish template; the conversation with the user stays in Polish. Reason: the Huawei challenge requires English project documentation. The rule lives in `CLAUDE.md` and `AGENTS.md`, section Language and communication style. Its exceptions are the Kraków submission in Polish and the original of a request quoted in a seed next to its translation (`standard_agent_docs.md`, section SEED format), the latter added on the same day after the first seed of the project.
- The ten blocking risk categories of the template (`standard_agentic_workflow.md` ch. 3.3) are kept unchanged, although they were chosen for a service with a database and an API. A decision of the user, not a gap.

Decisions recorded on 2026-10-03 by `plans_finished/frontend_stack/`:

- Frontend code is held to the workflow core and to `standard_frontend.md` only. A full frontend profile mirroring the Python one was decided against, so the frontend has no standard for the names of its files and for its split into directories. Condition for writing it: the split starts raising questions in review.
- The four gates of `standard_frontend.md` do not run until the initiative `frontend_app` of `MVP.md` writes the first frontend code and sets them up. Until then the standard is checked by review alone.

Decision recorded on 2026-10-03, outside an initiative, on the request of the user to stop the gates failing on the `impeccable` skill:

- A third-party skill installed by its own installer, today `impeccable` with its four agent roles, is exempt from the content parity of the Claude Code and Codex variants and from the prose gate. Reason: the installer generates each variant for its tool differently on purpose, and an edit made by hand would be lost with the next update of the skill. The other options were rewriting about two thousand lines of someone else's text in both copies, or removing a skill the team uses for the design direction. The list is in `tests/architecture/common_vendored_content.py`, the rule in `standard_agentic_workflow.md` ch. 6.1.
