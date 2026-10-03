# AI workflow

Document state: 2026-10-03

## Why this document exists

The Huawei challenge "Imagine What's Next" requires every team that uses AI tools to publish this file (`docs/hackathon/challenge_requirements.md`, section Use of AI). It describes which AI tools build this project, which reusable instructions steer them, how the work flows from an idea to code, and how generated output is reviewed. It is updated while the work goes on: the general sections describe the current setup, the log at the end records what happened, newest entry last.

The product has no AI feature so far. If one is added, it gets its own section here: the model or service, the inference flow, data handling, limitations, validation and privacy.

## Tools

| Tool                                     | Role                                                                                                                                     |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code (Anthropic), Claude Opus 5.5 | the main coding agent; used in the desktop app                                                                                           |
| Claude Code subagents                    | parallel work on disjoint sets of files, and the read-only roles `repo-researcher` and `dod-reviewer` defined in `.claude/agents/`       |
| Codex (OpenAI)                           | supported as a second agentic tool through `AGENTS.md`, `.agents/skills/` and `.codex/`; whether the team uses it is recorded in the log |
| MCP servers                              | none used for building the project so far                                                                                                |

Each log entry names the tools and models actually used in that piece of work.

## Reusable instructions and configuration

- `CLAUDE.md` and `AGENTS.md` - the permanent rules, identical for both tools: the repository is written in English and the conversation with the user in Polish, no guessing of contracts (ask instead of adding a fallback), no line comments in code, the agent never commits or pushes, and the hierarchy for resolving rule conflicts.
- `docs/standards/` - the standards the agents follow, with the standards map as the entry point. The source of truth above them is the product specification in `docs/product/`.
- Skills in `.claude/skills/` and `.agents/skills/`, identical in both tools: `plan-shape` (turns a raw request into a shaped plan through an interview), `plan-prd` (turns the shape into a PRD and then into an implementation plan, with a confirmation gate in between), `plan-implement` (implements a closed plan and calls the review), `implementation-dod-review` (review against the Definition of Done), `load-context` (dumps a folder into one file for analysis).
- Hooks: `local_docs_context.py` inserts the project description and pointers to the standards at the start of every session; `block_dangerous_commands.py` blocks destructive commands as well as `git commit` and `git push`.
- `.claude/settings.json` - denies reading and writing secret files.

The full description of the system, with the reasons behind each rule, is in `docs/standards/standard_agentic_workflow.md`.

## From an idea to code

Every task goes through the chain seed -> shape -> PRD -> plan -> implementation -> review, with artifacts in `plans/<INITIATIVE>/`:

1. Seed - the request written down verbatim, with its source. It is never edited afterwards, so the original prompt stays visible.
2. Shape - an interview, one question at a time; questions touching a blocking risk category (for example personal data or the database schema) must be answered by a human before going further. Decisions the agent took without asking are marked in place.
3. PRD - what and why, without technical decisions; a human confirms it before the plan is written.
4. Plan - how, with every fact backed by evidence (code, command, database or document) and a check date.
5. Implementation - exactly what the plan says; anything unforeseen stops the agent with a question, and the course of the work is logged in the task's review file.
6. Review - against the Definition of Done in `docs/standards/standard_review.md`.

Every transition between phases is manual, so a human sees each result and can turn back.

## How generated output is reviewed and validated

- A human checkpoint at every phase boundary of the chain.
- Automated gates run by `make check`: the architecture tests in `tests/architecture/` (Claude Code and Codex parity, hooks, prose style, plan document contract, conflict markers), ruff, mypy, vulture, deptry, bandit, pip-audit, and prettier for markdown.
- The review skill and the `dod-reviewer` role check changes against the Definition of Done and do not fix anything themselves.
- The agent never commits or pushes. A human reads the diff and creates every commit, so the commit history shows the progress a human accepted.

## Known limitations

- The format gate for plans checks the form of the evidence behind a fact, never its truth.
- Nothing automatic checks how many interview questions were asked or whether they were justified; the in-place marks of agent decisions are the only material for checking it.
- The template was written for a Python service with a database; parts of it may not fit until the technology stack is chosen.

## Log

### 2026-10-03 - Repository setup and translation to English

- Tools: Claude Code with Claude Opus 5.5 in the main session; seven Claude Code subagents with the same model for the translation.
- Request, summarized from Polish: the team chose the challenges "Kraków bez barier" and Huawei "Imagine What's Next" and combined them into one community app about accessible places and routes, web first with a HarmonyOS port if time allows. The agent was asked to fill in the agentic workflow for it without writing any code, because the specification is still being written, and then to translate the whole repository into English.
- Questions the agent asked, and the answers: where the specification lives (in the repository, `docs/product/`); what to do with the Python profile of the standards (defer until the stack is chosen); whether to replace the blocking risk categories (keep them); how to split languages between the two challenges (the whole repository in English).
- What was done: the template placeholders were filled in; the rules of both challenges were summarized from the organizers' PDFs in `docs/hackathon/challenge_requirements.md`, including the conflicts between them; the deferred decisions were recorded in `docs/standards/decision_registry.md`; the whole repository was translated by subagents working in parallel on disjoint lists of files, with a shared glossary fixing the exact renderings of headings and of the markers parsed by the tests, while the main session wrote the project files and ran the gates.
- Validation: `make check` passes - ruff, mypy, vulture, deptry, bandit, pip-audit and 112 architecture tests, with the 2 repository-wide plan checks skipped because no closed plan exists yet. Those two checks were exercised on a temporary closed plan built from the translated `plan-prd` template: it passed, and the same plan with an item under `## Open questions` was rejected; the temporary plan was deleted afterwards. A grep for Polish characters and Polish words found only proper names and the characters quoted on purpose by the formatting rules. Phrases that translators rendered differently were unified by hand.
- Lesson: a parallel translation needs the strings parsed by code (for example "plan closed" or "## Facts") fixed in a glossary before the work starts; one gap in the glossary, the angle-bracket placeholders, was found during the run and sent to the translators as an addendum.
