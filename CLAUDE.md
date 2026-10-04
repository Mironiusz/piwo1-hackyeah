# CLAUDE.md

## Purpose of this file

This file describes the permanent rules for working in this repository. Claude Code is to apply them while analyzing, writing code, refactoring, documenting and explaining changes.

## What we are building

EnableMe (in the repository piwo1-hackyeah) is a community app about the accessibility of places in Kraków, built at HackYeah 2026 (3-4 October 2026) for two partner challenges at once: "Kraków bez barier" (City of Kraków) and "Imagine What's Next" (Huawei, HarmonyOS). It combines information from open sources (OpenStreetMap, open city data) with reports from people, including photos, about places with good and with limited accessibility, and plans routes matched to the needs of people with different disabilities. We build a web app first and port it to HarmonyOS if time allows.

Constraints that come from the challenge briefs, not from product decisions: the app does not rely on internal systems of the Kraków City Hall (UMK) or municipal units (MJO), never presents missing or unverified information as a confirmation of accessibility, with one deliberate exception of the specification - a public transport segment of ZTP Kraków without accessibility data in its GTFS counts as accessible (O9) - and does not require users to disclose a disability when barrier and amenity preferences are enough to match results. What else the product deliberately does not do is decided by the specification.

The source of truth for the product is `docs/product/specification.md`: what the product does, for whom, the scope of the prototype and what stays out of it. Since 2026-10-03 it settles the target group and the scope of the MVP; product behavior it does not describe is still undecided, and every question about it goes to the user. In case of a discrepancy between the specification and anything else in the repository, the specification prevails. The challenge requirements and judging criteria are summarized in `docs/hackathon/challenge_requirements.md` - they are external constraints the specification has to satisfy, so a conflict between the specification and a challenge requirement is raised with the user, never resolved silently. The same description in two sentences is in `agent_docs/session_context.md`, from which the SessionStart hook inserts it at the beginning of every session.

How the MVP is built - the initiatives that implement it, their owners and order, and the requirements of the MVP each of them meets - is summarized in `MVP.md` in the repository root. It decides nothing of its own, and the specification prevails over it.

## Language and communication style

- Talk to the user in Polish, always with Polish diacritics.
- Use a casual, conversational, student-like tone, but keep professional terminology.
- Everything that goes into the repository is written in English: code, docstrings, documentation, standards, chain artifacts in `plans/` and `plans_finished/`, `agent_docs/`, and commit or Merge Request descriptions drafted by the agent. The reason is the Huawei challenge, which requires the whole project documentation in English (`docs/hackathon/challenge_requirements.md`). Polish proper names keep their spelling.
- There are two exceptions. Material a challenge explicitly requires in Polish - the Kraków submission on HackTribe - is marked as Polish where it is stored. A request quoted in a seed keeps its original language next to an English translation (`docs/standards/standard_agent_docs.md`, section SEED format).
- Talk to the user normally and explain your decisions.
- When something is unclear, say so directly instead of guessing.
- When you see a potential bug in the code, report it.
- Name a member of the team by first name, never by role: Kuba, not the db person. Who holds which role is in `TEAM.md` in the repository root.

## Rules for working with code

- Follow DRY, SOLID and KISS.
- Avoid fallbacks when you do not know the context. In that case it is better to create nothing and ask or search than to build a fallback for a potential contract that does not really exist.
- Use only necessary fallbacks that come from good practices of writing safe code, not from lack of knowledge.
- When the correctness of the data is not certain, ask whether it can be guaranteed.
- Always explain the decisions you made.
- Always say clearly what was changed.

## Hierarchy for resolving rule conflicts

When two rules from this file or from the standards in docs/standards collide, resolve them in this order:

1. Correctness and integrity of data.
2. No guessing of contracts - better to ask than to add a fallback.
3. Compliance with docs/standards.
4. Readability.
5. Performance.
6. DRY and avoiding needless cleverness.

This order follows directly from the rules above: the ban on fallbacks without context and asking instead of guessing are emphasized most strongly here, so they rank highest.

## Working with git

- Do not create commits and do not push anything to the remote repository. `git commit` and `git push` are forbidden unconditionally, also on the user's explicit request - commits are created by a human.
- Run `git add` and `git rebase` only on the user's explicit request, never on your own initiative.
- Run the remaining operations without asking: reading, `git fetch`, `git pull`, `git stash`, switching and creating branches, local `git merge`, `git worktree`.
- An operation outside these lists is decided by one criterion: does it touch history. If it creates, rewrites or publishes history, do not do it yourself.
- Changes enter main and dev only through a Merge Request. In the other direction, onto a working branch, they come down with a regular merge.
- Justifications, branch roles and edge cases are in docs/standards/standard_git.md.

## Target environment

The target environment is the hosted demo of the MVP on a server of a member of the team in a data centre, decided in `plans_finished/deployment/`, which supersedes `plans_finished/demo_environment/` D-8. The demo is served over plain HTTP at the address of the server. What else runs on that server is not known, so the hosted demo environment is only the services and the database of the demo on it, and their logs. The owner of the repository deletes the demo and all its data on 4 October 2026, after the results are announced. The permission levels of the agent:

- without asking: reading the repository, running local tools and tests, and reading the logs of the services of the hosted demo,
- only on the user's explicit request: anything else in the hosted demo environment, reading personal data from the demo database included,
- forbidden unconditionally, even on explicit request: deleting the services of the hosted demo or its database, changing the secrets of the hosting, and touching anything on that server outside the hosted demo environment - every other service, file and log.

Outside the hosted demo environment the agent has no access to any target environment, and challenge submissions are done by a human.

Regardless of the project: no address, host, login or secret of the target environment enters the repository in any form - not in code, not in documentation, not in initiative artifacts. The rule is described in docs/standards/standard_config.md.

## Comments and code documentation

- Do not write line comments in code.
- Use docstrings instead of line comments.
- Docstrings describe in plain human language what a function does.
- The ban on line comments does not mean no communication with the user.
- In the conversation, explain decisions, risks and changes normally.
- For more about documentation, see docs/standards/standard_documentation.md

## Code formatting

- Pass parameters to functions separated by spaces until the line exceeds 200 characters.
- After exceeding 200 characters, break the parameters into multiple lines.
- Do not use these characters in code: —, –, −.
- Use the plain character instead: -.
- Do not use these characters in code: “, ”.
- Use the plain character instead: ".
- Do not use these characters in code: →, ←, ↔.
- Use instead: ->, <-, <->.
- Do not use emojis.
- Do not overuse quotation marks.
- Use quotation marks only when they are needed, for example for a literal quote, a field name or a code fragment in text.

## Reply after finishing a task

After every change describe:

- what was changed,
- why it was changed,
- which decisions were made,
- which potential problems were noticed,
- what could not be determined, if something was unclear.

## Definition of Done

The full Definition of Done checklist is in `docs/standards/standard_review.md`.

## Full compliance with the standards

This repository has no legacy code, so the standards apply in the strict version: full compliance from the first commit, without a transition period. The soft deviation rule, which tolerates non-compliant code as long as nobody modifies it, does not apply here. When the repository has legacy code, relaxing this rule is to be an explicit decision recorded in the standards map, not an inherited state.

## Database schema

If the project keeps a schema dump, its location is recorded in the standards map. The dump is a picture of the actual state of the server, not the source of truth about the schema - editing the dump file does not change the database.

## Deferred decisions

Some decisions are deliberately postponed, with a recorded reason and a condition for resolving them - the list is in `docs/standards/decision_registry.md`. Before you treat a missing rule as a gap, check whether it is recorded there as a deferral. Do not resolve such an entry by guessing.

## Task cycle and the agentic system

The repository has an agent_docs/ layer next to the permanent docs/ and the chain plan-shape -> plan-prd -> plan-implement, which takes a task from the report through five artifacts in plans/<INITIATIVE>/ (SEED, SHAPE, PRD, PLAN, REVIEW) to an implemented change and durable memory in agent_docs/memory/. The full description of the whole system - task artifacts, blocking risk categories, the personal/project skill name collision, parallel work on one tree, the boundary between \_REVIEW.md and agent_docs/memory/, the duality of Claude Code and Codex - is in docs/standards/standard_agentic_workflow.md. An initiative explicitly finished or cancelled moves as a whole to plans_finished/<INITIATIVE>/, and a resumed one returns to plans/ - the criterion, protection of history and handling of references are in ch. 4.6 of that standard; plans/ holds only work in progress.

How AI tools are used in this repository is documented for the Huawei jury in `AI_WORKFLOW.md`. A change to the workflow itself - a skill, a hook, an agent role, these rules - is recorded there as well.

## Mapping: what to open before a task

The full table mapping a task type to the documents to open before the work, including when to reach for agent_docs/ and for docs/, is in docs/standards/README.md.
