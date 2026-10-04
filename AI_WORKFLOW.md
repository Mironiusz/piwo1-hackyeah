# AI workflow

Document state: 2026-10-04

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
- A third-party design skill, Impeccable 4.5.0 (Apache 2.0), in `.claude/skills/impeccable/` and `.agents/skills/impeccable/`, with four agent roles of its own (`.claude/agents/impeccable-*.md`). The design direction of the route result screen was shaped with it, and the brief and the mocks of the views of `docs/product/views.md` follow that direction in the same place (`PRODUCT.md`, `.impeccable/briefs/`). It is installed and updated by its own installer, so the team does not edit it, and the parity and prose gates skip it.
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

### 2026-10-03 - MVP scope in the product specification

- Tools: Claude Code with Claude Opus 5.5 in the main session, no subagents.
- Request, summarized from Polish: the team listed the candidate features of the MVP (preference profiles, routes matched to needs, reports of barriers, confirmations, geozones, voice, open data, route colors, barrier notifications, Good Samaritan points with a ranking, anonymous reports) and asked to split them into mandatory and optional.
- How it went: the agent read the challenge requirements and the deferred decisions, then went through the features one by one, giving for each a recommendation tied to a concrete requirement or judging criterion of the challenges, and named the mandatory items the list was missing (source, date and reliability status of every fact, a text alternative for the map, a case of contradictory data in the demo). Four choices that change the scope were asked as closed questions: the target group, the scope of geozones, accounts, and points with the ranking.
- What was done: `docs/product/specification.md` was created with the target group, the mandatory and optional features and the out-of-scope list; the decision registry entry on the specification moved to the resolved section; the files that said the specification does not exist yet were updated.
- Validation: the user accepted the split and the descriptions in the conversation before the file was written; the specification records which decisions the user made and which details the agent proposed.
- Note: the specification was written directly from the conversation, not through the seed -> shape chain, because it settles the product scope that the chain's initiatives will refer to.

### 2026-10-03 - MVP initiative and its shape interview

- Tools: Claude Code with Claude Opus 5.5 in the main session, the `plan-shape` skill, no subagents.
- Request, summarized from Polish: put the MVP planning into an initiative in `plans/` and continue it through the chain, with the detail regulator raised to C:60.
- How it went: the agent proposed the initiative name and layout (`plans/mvp/`, prefix `MVP`, one flat task) and waited for confirmation. Saving the seed revealed a conflict between two rules - the seed has to be verbatim, and the repository has to be in English - which the agent put to the user instead of choosing; the seed keeps the Polish original with an English translation next to it. The interview went one question at a time, each closed question asked on a concrete run with times and states, and eleven questions touching blocking risk categories (source of truth, deduplication, read visibility and permissions, personal data, time semantics) were answered before closing. The user added rules during the interview (a photo adds weight to a vote, the profile moves between devices with a QR code), which raised follow-up questions about scope and personal data.
- What was done: `plans/mvp/MVP_SEED.md` and `plans/mvp/MVP_SHAPE.md` with the interview closed; `docs/product/specification.md` raised to version 2 with the rules of every MVP feature, a new mandatory feature (flagging and moderation), a new first optional feature (QR transfer) and a section on personal data.
- Validation: every decision in the shape and the specification is attributed to the user; the gates of the repository (prose style, prettier) pass.
- Lesson: at C:60 the consequences of earlier answers produced as many questions as the initial list - three of the final rules (unverified barriers, denials of OpenStreetMap facts, moderation in the core) came from follow-ups, not from the seed.

### 2026-10-03 - Rule for seeds written in another language

- Tools: Claude Code with Claude Opus 5.5 in the main session.
- Request, summarized from Polish: turn the decision taken for the first seed into a rule, so the same conflict is not raised again with every seed.
- What was done: `docs/standards/standard_agent_docs.md`, section SEED format, now says that a request in a language other than English is quoted verbatim in that language, with an English translation by the agent next to it, marked as not part of the verbatim record. The `plan-shape` skill (in both `.claude/` and `.agents/`), `CLAUDE.md`, `AGENTS.md`, `agent_docs/ai_workflows/shape_prd_workflow.md` and the standards map point to it.
- Why: two rules collided - the repository is written in English, and a seed is a verbatim record. A translation alone would no longer be a record of what was said; the original alone could not be read by the Huawei jury.

### 2026-10-03 - Agent permissions in the hosted demo

- Tools: Claude Code with Claude Opus 5.5 in the main session, the `plan-implement` skill, no subagents; other Claude Code sessions worked on the same tree at the same time and were coordinated by messages between sessions.
- Request, summarized from Polish: implement `plans/demo_environment/` without getting in the way of the parallel sessions.
- What was done: `CLAUDE.md` and `AGENTS.md`, section Target environment, now carry the three permission levels of the agent for the hosted demo on a virtual private server of a member of the team, limited to the services, the database and the logs of the demo, because the server also runs other services of its owner. Reading those logs needs no request, anything else in that environment needs an explicit request, and deleting the demo or its database, changing the secrets of the hosting and touching anything else on the server are forbidden even on request.
- Why: during the night before the submission the agent can read an error or deploy a fix on request, while the deletion of the demo and its personal data on 4 October 2026 stays with the owner of the repository. The levels are enforced by the rules only, not by the hook for dangerous commands, by the decision of the user.
- Note: the levels were written before the choice of the hosting was recorded, because the free memory and disk of the server are still to be confirmed (`plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` Q-1 and D-7).

### 2026-10-03 - Third-party skill outside the repository gates

- Tools: Claude Code with Claude Opus 5.5 in the main session, no skills, no subagents.
- Request, summarized from Polish: fix the failing tests caused by the Impeccable skill.
- What was done: the parity and prose gates in `tests/architecture/` skip the third-party skill `impeccable` and its four agent roles, named one by one in `tests/architecture/common_vendored_content.py`; `tests/architecture/test_vendored_content.py` fails when an entry points to something no longer installed. `standard_agentic_workflow.md` ch. 6.1, 6.2 and 6.4, `standard_formatting.md`, `standard_tests.md` and the standards map describe the exemption.
- Why: since the skill was installed, four architecture tests failed on about two thousand lines of its text, so a red `make test` no longer pointed at the change being checked. The installer generates the Claude Code and Codex variants differently on purpose, and an edit made by hand would be lost with its next update.

### 2026-10-04 - Decisions of parallel initiatives carried into the MVP plan

- Tools: Claude Code with Claude Opus 5.5 in the main session, no skills, no subagents.
- Request, summarized from Polish: check whether the branch of another member of the team holds decisions that refine the MVP, and then carry them in.
- How it went: the agent read the branch and found only planning documents of four initiatives - Valhalla in place of the own router with optional public transport routes from static GTFS, the deployment, the first schema revision and the backend architecture. It split their decisions into those that only bring the MVP plan up to date and those that conflict with the Kraków brief or with the specification, and put both lists to the user, who had the first carried in at once. The second was first recorded as open questions of the MVP plan; the user then sided with the decisions of the branch, and the agent recorded them together with the departures from the brief they cause.
- What was done: the branch was merged by fast-forward, twice, as it grew during the session. In `plans/mvp/MVP_PLAN.md`, D-9 now names Valhalla and records the accepted green public transport segment of the optional feature, D-10 the server in a data centre with every part of the demo in Docker containers, served over plain HTTP and without the scene of unavailable routing, D-11 the first schema revision as a work package of the MVP plan with everything it has to meet, and D-12 the implementation of the operations in the work packages; Q-11, pointing to `plans/backend_architecture/`, is its only open question. `docs/product/specification.md` version 8 drops the scene of unavailable routing from M10 and keeps the plain message, and `plans/mvp/MVP_PRD.md`, `PRODUCT.md` and `docs/hackathon/challenge_requirements.md` follow, the last with the two departures from the brief listed for the submission. `CLAUDE.md` and `AGENTS.md`, section Target environment, describe the new server with unchanged permission levels, and `docs/standards/decision_registry.md` and `agent_docs/memory/_cross_cutting.md` follow.
- Why: the agent rule on the target environment described a server the demo no longer runs on (`plans/deployment/DEPLOYMENT_SHAPE.md`, functional requirement 5), and the MVP plan named a routing engine and a builder of the first revision that had changed.
- Validation: the 120 architecture tests pass, the parity of `CLAUDE.md` and `AGENTS.md` and the prose gate included, prettier finds every changed file formatted, and no added line carries a character the formatting rules forbid.
- Note: a conflict with a challenge requirement goes to the user and is never resolved silently (`CLAUDE.md`, section What we are building), so the green public transport segment without accessibility data and the plain HTTP were carried in only after the user decided them, and the exception in `CLAUDE.md` for the first is left to `plans/valhalla_routing/`, which writes it with its version of the specification. The superseding note on D-8 of `plans_finished/demo_environment/` that functional requirement 5 of the deployment shape asks for was not written, because an archived plan keeps its findings unchanged (`docs/standards/standard_agentic_workflow.md` ch. 4.6); `plans/mvp/MVP_PLAN.md` D-10 records the change instead.

### 2026-10-04 - Exception to a rule from the briefs for public transport

- Tools: Claude Code with Claude Opus 5.5 in the main session, the skills `plan-prd`, `plan-implement` and `implementation-dod-review`, the `dod-reviewer` subagent for the review; a Valhalla spike run by the user with an agent outside the repository gave the measurements; other sessions worked on `plans/deployment/` and `plans/backend_architecture/` on the same tree at the same time.
- Request, summarized from Polish: replace the own router with Valhalla run by the project and add routes with public transport of ZTP Kraków from its static GTFS, going ahead after the spike.
- What was done: `CLAUDE.md` and `AGENTS.md`, section What we are building, now name one deliberate exception to the constraint that missing information is never presented as a confirmation of accessibility: a public transport segment of ZTP Kraków without accessibility data in its GTFS counts as accessible. Version 8 of `docs/product/specification.md` carries it as the optional feature O9 and next to M7 and M10, and `plans/valhalla_routing/VALHALLA_ROUTING_PLAN.md` records the technical decision that replaces D-9 of `plans/mvp/MVP_PLAN.md`.
- Why: the user decided the exception in the seed and the shape interview of `plans/valhalla_routing/` on 2026-10-03, after the agent stated that it conflicts with the rule of the Kraków brief and that the feeds carry no accessibility information at all. A constraint of the repository core that the specification departs from has to say so, or the core and the specification disagree.
- Note: the risk to the person and to the criterion "Data reliability, presentation and updates" stays and is recorded in the risks of `plans/valhalla_routing/VALHALLA_ROUTING_PRD.md`.

### 2026-10-04 - Agent permissions on the new demo server

- Tools: Claude Code with Claude Opus 5.5 in the main session, the `plan-shape`, `plan-prd` and `plan-implement` skills, no subagents; other Claude Code sessions worked on the same tree at the same time and were coordinated by messages between sessions.
- Request, summarized from Polish: move the hosted demo to a server of the user in a data centre and write the instructions for deploying it.
- What was done: `CLAUDE.md` and `AGENTS.md`, section Target environment, now describe a server of a member of the team in a data centre, served over plain HTTP, of which nothing but the demo is known. The three permission levels of the agent are unchanged. The decision registry and D-10 of `plans/mvp/MVP_PLAN.md` follow it.
- Why: the user moved the demo off the virtual private server of the db person on 2026-10-03, so the rules described a machine the demo no longer runs on. The levels still fit, because they are narrow enough to be right whatever else runs on the server.
- Note: supersedes the entry of 2026-10-03, Agent permissions in the hosted demo, which stays as a historical record.

### 2026-10-04 - Merge of dev into the branch of the MVP plan

- Tools: Claude Code with Claude Opus 5.5 in the main session, no skills, no subagents.
- Request, summarized from Polish: resolve the merge conflicts with `dev` and the behavioral and architectural conflicts between the two lines, taking the changes of `dev` wherever they collide, because the user had agreed them with their author.
- What was done: both lines wrote a version 8 of `docs/product/specification.md` on 2026-10-04. Version 8 of `dev`, routes with public transport as the optional feature O9 with its exception, stays version 8, and the change of this branch, which drops from M10 the scene of routing that does not answer, became version 9 with its text unchanged; `PRODUCT.md`, `plans/mvp/MVP_PLAN.md` and `plans/mvp/MVP_PRD.md` name version 9. `CLAUDE.md`, `AGENTS.md`, D-9 and D-10 of `plans/mvp/MVP_PLAN.md` and the entry Target environment for the demo of `docs/standards/decision_registry.md` take the wording of `dev`. What only this branch changed - Q-11 with `plans/backend_architecture/`, the first schema revision as a work package of D-11, the correction of D-3 by `plans_finished/nominatim_client/`, AC-15 of `plans/mvp/MVP_PRD.md` and item 10 of the conflicts in `docs/hackathon/challenge_requirements.md` - stays, brought up to date with `dev`: the interview of `plans/backend_architecture/` is closed, the deployment configuration is written by the task `DEPLOYMENT_CONFIG` of `plans/deployment/`, the Valhalla spike is done, and the green public transport segment is a rule of the specification, no longer of D-9. The entries of this log and of `agent_docs/memory/_cross_cutting.md` are kept from both lines, in the order of their commits.
- Why: two parallel lines decided the same documents on the same day, and the version numbers of the specification follow the order in which its versions enter the shared line.
- Note: the entry of this branch in `agent_docs/memory/_cross_cutting.md` says the numpy and scipy of the route graph no longer apply; the later entry of `dev` keeps them for the graph of the route with the fewest barriers, and the later entry is the one in force.

### 2026-10-04 - Team members named instead of roles

- Tools: Claude Code with Claude Opus 5.5 in the main session, no skills, no subagents.
- Request, summarized from Polish: assign the people of the team to their roles and write it down, so that documents name people instead of saying "the db person".
- What was done: `TEAM.md` in the repository root lists the six members of the team with the role names the repository already used - Rafał as the lead, Kuber and Adrian on the frontend and the HarmonyOS port, Kuba on the database, Marek on the backend, Mateusz on the import and the external API. `CLAUDE.md` and `AGENTS.md`, section Language and communication style, now tell the agent to name a member of the team by first name, and the standards map lists the new file.
- Why: the chain artifacts said "the db person" or "the backend person" because the user had named only roles on 2026-10-03; with the people known, a role in place of a name only makes the reader look up who it is.
- Note: documents written before 2026-10-04 keep their role names, by the decision of the user; `TEAM.md` is how they are read.

### 2026-10-04 - Second merge of dev into the branch of the MVP plan

- Tools: Claude Code with Claude Opus 5.5 in the main session, no skills, no subagents.
- Request, summarized from Polish: resolve the merge conflicts with `dev`, taking the additions of `dev` and keeping the new layout of the MVP plan of this branch.
- What was done: both lines wrote a version 9 of `docs/product/specification.md` on 2026-10-04. Version 9 of `dev`, the hash of a vote without an account kept until the demo is deleted, stays version 9, and the change of this branch, which drops from M10 the scene of routing that does not answer, became version 10 with its text unchanged; `PRODUCT.md`, `plans/mvp/MVP_PLAN.md` and `plans/mvp/MVP_PRD.md` name version 10. `plans/mvp/MVP_PLAN.md` keeps the layout of this branch, in which the initiative implements nothing and hands the MVP to the initiatives of its D-15, and takes the decision of `dev` that settles Q-11 as D-14, with the work packages it named replaced by those initiatives; the decisions, the scope of changes and the risks that still treated Q-11 as open follow it. Both archivals are kept, `plans_finished/backend_architecture/` of `dev` and `plans_finished/deployment/` with `plans/deployment_config/` of this branch, and the editable references of both point to the new places.
- Why: the version numbers of the specification follow the order in which its versions enter the shared line, as at the first merge, and a plan that settles Q-11 and still waits for it could not be carried out.
- Note: `plans/schema_revision/SCHEMA_REVISION_PLAN.md` numbers its own version 10 and says it takes the next free number when another version is approved first (D-7 there), so it becomes version 11 when it is carried out; its facts on `plans/backend_architecture/` are of their day.

### 2026-10-04 - MVP plan reduced to a summary and the seeds of its initiatives

- Tools: Claude Code with Claude Opus 5.5 in the main session, the skills `plan-prd`, `plan-implement` and `implementation-dod-review`, the `dod-reviewer` subagent for the review; another session archived `plans/deployment/` on the same tree at the same time and the two were coordinated by messages between sessions.
- Request, summarized from Polish: the MVP plan is to implement nothing and only create the MVP file and set up the initiatives that implement it.
- What was done: `MVP.md` in the repository root summarizes the MVP - its scope, the technical decisions of `plans/mvp/MVP_PLAN.md`, the eleven initiatives that build it with their owners named by first name and the order of their waits, and the initiatives that meet each requirement of `plans/mvp/MVP_PRD.md`. Eleven seeds, from `plans/backend_skeleton/` to `plans/public_transport_routing/`, quote the conversation and the row of their initiative. The decision registry, `docs/standards/standard_frontend.md`, the standards map, `PRODUCT.md`, `CLAUDE.md`, `AGENTS.md` and `agent_docs/memory/` name those initiatives instead of the work packages of the MVP plan, and the shape, PRDs and plans in progress of `plans/valhalla_routing/` and `plans/schema_revision/` got dated notes.
- Why: so that the pieces of the MVP are built in parallel by their owners, each through its own chain, ordered so that the main scenario works first (`plans/mvp/MVP_PLAN.md` D-13, D-15).
- Note: the user told the implementation run to ask no questions and not to wait for the initiatives not finished yet, which add their content to `MVP.md` later. Two initiatives on branches not merged yet overlap those of `MVP.md`, the import and the stops of public transport; the agent recorded the overlap in `docs/standards/decision_registry.md` instead of deciding it.

### 2026-10-04 - Consistency pass after the MVP plan and third merge of dev

- Tools: Claude Code with Claude Opus 5.5 in the main session, the `dod-reviewer` subagent for the review; two other sessions, which closed `plans/valhalla_routing/` and carried out `plans/schema_revision/`, worked on the same tree at the same time and were coordinated by messages between sessions.
- Request, summarized from Polish: check that the repository and its documentation are current and consistent after the MVP plan was carried out, merging `dev` into the branch if needed.
- What was done: the branch was brought up to `dev` twice by a fast-forward, the second time over the uncommitted work of the other sessions, after both of them had stopped writing. Both lines wrote a version 11 of `docs/product/specification.md`: version 11 of `dev`, the rules the user journeys of `docs/product/user_journeys.md` needed, stays version 11, and the idempotency key of `plans/schema_revision/` became version 12 with its text unchanged, as D-7 of its plan says; `docs/product/schema.md`, `MVP.md`, `PRODUCT.md`, the decision registry and the brief of the views name version 12. `MVP.md` says how FR-11 and AC-10 of `plans/mvp/MVP_PRD.md` are read after version 11, names the narrower rule of a pseudonym that `docs/product/api_contract.md` does not carry yet, and lists the new documents of the frontend; the decision registry records the street name of an item of a list, deferred by version 11; `README.md` and the standards map describe what the repository holds now, `docs/setup/` included; `docs/setup/EMULATOR_SETUP.md` was formatted by prettier, the last file that failed `make lint-docs`.
- Validation: the architecture tests and prettier pass on the whole tree before and after the merge; the changes of the other sessions were compared line by line before and after the merge; `dod-reviewer` found no blocker, and its minor findings were fixed or handed to the session that owns the text.
- Note: the work on the user journeys, the views and their mocks that brought version 11 has no entry in this log yet; its author knows which tools were used. `docs/setup/EMULATOR_SETUP.md` describes a HarmonyOS client, `accessway/`, that is not in the repository, which the agent reported to the user instead of changing the file.
