# piwo1-hackyeah

A HackYeah 2026 project (3-4 October 2026, Kraków): a community app about the accessibility of places in Kraków. It combines open data (OpenStreetMap, open city data) with reports from people, including photos, shows where every piece of information comes from, how fresh and how reliable it is, and plans routes matched to the needs of people with different disabilities. Web first, with a HarmonyOS port if time allows.

The project is submitted to two partner challenges: "Kraków bez barier" (City of Kraków) and "Imagine What's Next" (Huawei). Their requirements, deliverables and judging criteria are summarized in `docs/hackathon/challenge_requirements.md`. The product specification will live in `docs/product/specification.md`; it is still being written.

There is no product code yet. Build, installation and launch instructions for the app will be added here together with the first code.

## Origin of the workflow

The repository was created on 2026-10-03 from a pre-existing project template, "agentic-workflow": an agentic workflow for Claude Code and Codex together with a set of standards for a Python service. The template contains no product code. It was translated from Polish to English and filled in for this project during the hackathon. How AI tools are used here is described in `AI_WORKFLOW.md`.

## What is inside

- `.claude/`, `.agents/`, `.codex/` - the chain skills (`plan-shape`, `plan-prd`, `plan-implement`, `implementation-dod-review`, `load-context`), the subagents `repo-researcher` and `dod-reviewer` with their Codex variants, the `local_docs_context.py` hook with the session start context, the `block_dangerous_commands.py` hook blocking destructive commands as well as `git commit` and `git push`, and settings that block reading secret files.
- `agent_docs/` - the project description for the hook, the methodology of the chain and the durable memory convention.
- `docs/standards/` - the standards map, six standards of the workflow core, twelve standards of the Python profile and two registries.
- `docs/hackathon/` - the summary of the challenge rules; `docs/product/` - the place for the product specification.
- `tests/architecture/` - the core gates: Claude Code and Codex parity, hooks, prose style, plan document contract, conflict markers.
- `plans/` and `plans_finished/` - the place for initiatives in progress and their archive.
- `pyproject.toml`, `makefile`, `package.json`, `.prettierrc` - quality and formatting tools.

The full description of the system is in `docs/standards/standard_agentic_workflow.md`, and the entry point to the standards is `docs/standards/README.md`.

## Requirements

The machine needs `make`, `python` 3.13 and `node` with `npm` for prettier, which formats markdown. The Python tools go into a virtual environment, prettier into `node_modules` in the version pinned in `package.json`.

```bash
python -m venv venv
venv/Scripts/python -m pip install -e ".[dev]"
npm ci
make check
```

## Setup from the template

The template's setup steps and their state in this repository:

1. Copy the template files into a new repository, without the template's `.git` directory. Done in the initial commit.
2. Fill in the places marked `<...>` in `CLAUDE.md`, `AGENTS.md` and `agent_docs/session_context.md`: the project description, the product specification, the team and the agent's permissions for the target environment. `CLAUDE.md` and `AGENTS.md` must be identical except for the tool name - the parity test checks it. Done on 2026-10-03; the team section was removed because there is nothing to record yet, and the target environment waits for the stack decision (`docs/standards/decision_registry.md`).
3. Enter the project name in `pyproject.toml`, `package.json` and `package-lock.json`. Done: `piwo1-hackyeah`.
4. A Python profile project adds its layer directories to `[tool.mypy]` and `[tool.vulture]` in `pyproject.toml` and to the `security` target in `makefile` together with the first code, and sets up the profile gates (layer boundaries, environment contract, consistency of the periodic task registry) together with the first code of a given layer. Waiting for the first code.
5. A project outside the Python profile removes the profile standards listed in `docs/standards/README.md`, their rows in the maps in `docs/standards/README.md` and `docs/standards/standard_review.md`, and the Python tools it does not use. The core gates stay, because they are Python tests and need `pytest`. Deferred until the stack is chosen (`docs/standards/decision_registry.md`).
6. The list of ten blocking risk categories is chosen for a service with a database and an API. A project with a different risk profile changes it in the three places listed in `docs/standards/standard_agentic_workflow.md` ch. 3.3. Kept unchanged by decision of the user.
7. Run `make check`.

## Personal skills versus project skills

When `~/.claude/skills` holds a skill with the name of a project skill, Claude Code loads the personal copy instead of the project one, without any message. The SessionStart hook warns about such a collision at the start of a session, and the rule is described in `docs/standards/standard_agentic_workflow.md` ch. 6.5.

## Carrying fixes back to the template

The template is used only for the start: projects created from it do not receive its later changes by themselves, and the template does not receive fixes from projects. A workflow fix made in a project is carried over to the template by hand:

- a core file (skill, subagent, hook, gate, core or profile standard) is carried over as a whole, after removing project-specific content: product and system names, references to the specification, decisions and initiatives of the project,
- a file of the project part (`CLAUDE.md`, `AGENTS.md`, `agent_docs/session_context.md`, the standards map, the registries) is carried over only in its general part.

After carrying a fix over, `make check` has to pass in the template, and a grep for the name of the source project must return no hits. The template itself is written in Polish, so a fix from this repository has to be translated back.
