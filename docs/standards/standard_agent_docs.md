# Agent documentation standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

This standard is the single source of truth for the format of the five artifacts of the agentic chain (SEED, SHAPE, PRD, PLAN, REVIEW) and for the format of an `agent_docs/memory` entry. It closes a problem that this file itself recorded in its skeleton version: the agent memory convention had four addresses - this file, `standard_agentic_workflow.md` ch. 5.2, `agent_docs/README.md` and `agent_docs/memory/README.md`. From now on the other three places point here instead of repeating the same content.

## Scope and boundaries

Inside: the format of each of the five chain artifacts and the format of an `agent_docs/memory` entry, together with the rationale - what breaks when a given rule is not followed.

What is not here:

- the chain mechanism itself, the order of phases, the checkpoints and the description of the skills that handle it - that is in `standard_agentic_workflow.md`;
- the full description of the ten blocking risk categories - that is in `standard_agentic_workflow.md` ch. 3.3, here only a reference;
- the Claude Code/Codex duality and the skill parity test - that is also `standard_agentic_workflow.md`;
- when an initiative moves to the `plans_finished/` archive and how it comes back - that is `standard_agentic_workflow.md` ch. 4.6; here there is only how to record in REVIEW the scope of the verdict, the closure and the resumption;
- prose formatting in these artifacts: forbidden characters, quotation marks and the ban on inline bold - that is in `standard_formatting.md`. The rule on emphasis applies to all five chain artifacts and to memory entries, even though they are written by the agent, not by a human.

## Deviation rule

The deviation rule shared by all standards (`docs/standards/README.md`) applies in its strict version: the standard describes the target state and applies in full from the first commit, because a project created from the template has no legacy state that would require a transition period. Relaxing this rule is to be, some day, an explicit decision recorded in the standards map, not a state that comes into force on its own.

Narrowing specific to this standard: the unit of deviation is the task (`plans/<INITIATIVE>/<TASK>_*`), not a code module - the general rule speaks of a module touched by a change to production code, which has no counterpart in the `plans/` documents.

## SEED format

SEED is a verbatim record of the request, with an explicit source of origin: a conversation with the user, a pasted email, a meeting note, a branch description, a report from a team member. It cannot be modified once saved - a change of scope always goes to SHAPE, never to SEED. If the seed is too thin for anything to follow from it, it is still saved verbatim, and the gaps are addressed with questions in the shape phase - the seed is not corrected by guesswork, because then it stops being a record of what was actually said.

The user may create the seed file themselves, pasting a ready note instead of dictating it in the conversation - in that case `plan-shape` never overwrites it, it only reads it. The only hard requirement for a manually created file: it must contain some content, because an empty seed cannot be processed.

Without this rule the seed would stop being a reliable point of reference - if it could be corrected as work progresses, no future person could check what was actually requested at the start, as distinct from what was understood later.

SEED may carry the detail regulator parameter, canonically written as `C:N` (full definition: `standard_agentic_workflow.md` ch. 3.5). This does not break the inviolability of the seed, because the parameter is part of the verbatim content of the request and applies from the SHAPE header, not from here - a change of the value during the task goes to SHAPE and never comes back to this file.

## SHAPE format

SHAPE has eleven sections: Problem, Recipient and trigger, Current state, Smallest meaningful scope, Out of scope, Functional requirements, Scenarios, Challenging own assumptions, Domain rules or explicit TODO, Notes on data/performance/security, Open questions. "Recipient and trigger" asks about the recipient of the change and its trigger: a person in a specific role, a consumer of the programming interface, a periodic task of the worker, another system. When the project has no user interface, the recipient is a system, and the question about a persona has no answer.

The interview is conducted one question at a time: `AskUserQuestion` for closed decisions, plain text for open ones. After each answer a minimal note is added to the appropriate section, the corresponding entry is removed from "Open questions" and the file is saved - thanks to this the interview can be interrupted at any moment without losing progress.

The SHAPE header carries two lines: the document state with a date and `Regulator: C:N` with the value of the detail regulator in force for this task (full definition: `standard_agentic_workflow.md` ch. 3.5). This is the place from which all three chain skills read the value - not from the seed. The value may be changed during the task, but then the document gets one line saying from which point the new one applies, because without it the document cannot be read backwards. An item decided by the agent instead of by asking carries the phrase "Agent decision at C:N, without asking", in the place of that item, not in a collective section at the end.

The "Challenging own assumptions" section must not stay empty. If nothing in it raises doubts, that is a sign that the problem has not been understood yet, not that it is exceptionally clear.

Every question touching one of the ten blocking risk categories (full list and verification method: `standard_agentic_workflow.md` ch. 3.3) is marked `Block: yes` together with the name of the category. The phase ends only when all sections are filled in and no item in "Open questions" has `Block: yes` - this is a safeguard against moving to the PRD with an unresolved question that touches the API contract, the database schema or another real risk.

## PRD format

PRD has nine sections: Business goal, Problem and its consequences, Scope, Out of scope, Functional requirements, Acceptance criteria, Domain rules, Dependencies and impact on other modules, Risks and notes. It answers only "what and why", never "how".

Blacklist of content forbidden in a PRD: data models, column lists, migrations, code file paths, function names, library decisions, deployment details, secrets and credentials. If while writing the PRD there is an urge to record a technical solution, that material belongs to PLAN, not to PRD - mixing the two leads to premature freezing of technical decisions before anyone has confirmed that the problem itself and the scope are agreed.

PRD ends with a confirmation gate with the user before PLAN is created. This is the only checkpoint between "what" and "how" in the whole chain - it is never passed silently.

## PLAN format

PLAN has nine sections: Goal, Facts, Decisions, Scope of changes, Rollout order, Definition of Done, Risks, Open questions, Supplementary files. It answers "how", based on facts verified in the code, the database and the documentation - never on assumptions taken on faith.

Every step in "Scope of changes" has concrete names of files, functions and data contracts - never a description in the style of "something like". A technical decision taken independently instead of by asking carries in the "Decisions" section the same phrase as in SHAPE: "Agent decision at C:N, without asking".

### Plan state marker

The document state line carries a date and a state marker, in one of exactly two wordings: "plan in progress" or "plan closed". The marker is the same convention that SHAPE already carries (interview in progress, interview closed), and it introduces no new concept.

```text
Document state: 2026-08-17, plan closed
```

The list of wordings is closed, because inclusion of the document in the check described below depends on the marker, and the second part of the state line used to be an ordinary descriptive sentence - without a closed list the marker cannot be told apart from such a sentence.

The marker decides about inclusion in the check first, the date only second: the check covers a closed plan dated no earlier than the date the rule came into force, stored in the `RULE_EFFECTIVE_DATE` constant of the test from the Enforcement section. A plan in progress is not subject to it at all. The reason is practical: a plan written in installments is not supposed to block unrelated work on the same tree, and closing is the right moment for the check, because only then is the plan handed over to the implementation phase. A known price, accepted deliberately: a plan abandoned in the in-progress state will never come under the check.

### Format of a finding in the Facts section

The "Facts" section contains only finding items, one per line, without an introductory sentence and without content of any other kind. The introductory sentence, if needed, stands before the section heading.

An item carries four things: an identifier, a claim, evidence and a check date. They are written in three fields separated by the vertical bar character: the identifier together with the claim, the evidence, the check date in the format YYYY-MM-DD. The identifier has the shape `F-N.` with a period, just like the identifiers in the other sections. Several pieces of evidence for one finding are separated by a semicolon.

```text
F-1. The database reachability probe reads the address from the configuration, not from an environment variable. | code:`data/engine.py:31`; doc:`docs/standards/standard_config.md` para. Three configuration layers and four storage places | 2026-08-17
```

Evidence belongs to one of five kinds, recognizable by the very beginning of the entry alone, without interpreting the content:

- `code:` - reading code with an indication of the file and line,
- `cmd:` - a run together with its result. The kind is broad: it covers a shell command, a code snippet and reading the state of an environment, that is, everything that was run and whose effect is visible in the result,
- `db:` - a database query together with its result,
- `doc:` - a reference to a document with an indication of the paragraph or line,
- `ASSUMPTION:` - content accepted without verification, explicitly marked.

A finding derived from several sources carries several pieces of evidence in one item. There is no separate kind of evidence for inference and there is not supposed to be one - such a kind would be a loophole precisely for unsupported claims, which this format protects against.

Both separators work only outside text in backticks: a vertical bar and a semicolon quoted inside backticks belong to the quotation, not to the structure of the item. Without this exception the format would force rewriting a command that was actually run - a regex with a vertical bar or a query with a semicolon could no longer be quoted verbatim, and verbatim quotation matters more here than the simplicity of splitting.

The boundary of the check, named here explicitly so that a green gate is not read as proof that the findings are true: what is checked is the form of the evidence, never its truth. A made-up finding written in the correct form will pass. The format raises the cost of making things up and makes it detectable in a manual check; it does not make it impossible. The most convenient loophole here is the `ASSUMPTION:` kind, because it lets you fill in the form without any verification - using it for something that could have been checked breaks this rule, even though the automatic check will not notice it.

### Empty open questions section

A closed plan has an empty "Open questions" section. The section is empty when it contains not a single list item, and its first paragraph is a statement of absence starting with the word "None". A sentence stating that there are no questions is therefore the record of an empty section, not an item.

### Enforcement

The rules on the finding format, the state marker and the empty open questions section are enforced by `tests/architecture/test_plan_document_contract.py`, for plans marked as closed and not older than the date the rule came into force (the `RULE_EFFECTIVE_DATE` constant in that test). A project created from the template comes into being after that date, so the check covers every closed plan of the project. The check runs together with the rest of the architecture tests, so it fires on its own during implementation and during review.

If verification while writing the plan disproves an assumption from the PRD, the plan goes back to the PRD phase instead of quietly working around it - the PRD is a contract, not a draft open to arbitrary correction. PLAN is finished only when it meets the same completeness criteria that `plan-implement` will require anyway: zero TODOs, zero items in "Open questions", every step with an unambiguous input and output.

## REVIEW format

REVIEW is a log of the implementation run, not durable memory - it describes the state of a specific task, not universal knowledge about the repository. It records what was skipped, what the agent ran into during the work, what decisions were made while writing code and what requires coming back to in the future.

The difference from an `agent_docs/memory` entry is crucial: REVIEW describes the run of this one task and loses its meaning when the task closes; a memory entry records a durable pattern or decision, useful in future, unrelated tasks concerning the same module. Confusing these two places leads to a situation in which durable knowledge disappears together with the closed task, or the other way round - `agent_docs/memory` fills up with one-off trivia.

A plan gap filled in independently during implementation, instead of with a question to the user, is recorded in REVIEW with the same phrase as in the other artifacts: "Agent decision at C:N, without asking".

REVIEW is appended to by `plan-implement`, during implementation (when it runs into something the plan did not foresee) and at the end, as a summary. `implementation-dod-review`/`dod-reviewer` may supplement REVIEW, but is not its owner.

REVIEW is also the only place from which the end of an initiative is read (`standard_agentic_workflow.md`, ch. 4.6). The review verdict recorded in REVIEW states explicitly what scope it covers: the whole initiative, one task out of several, the plan alone or part of the code - without this sentence the reader will not tell the final `ready` of the whole matter apart from the `ready` of one stage, and only the former qualifies the directory for the archive. In a multi-task initiative, settling one task is a verdict for that task, not for the directory. A closure without a `ready` verdict - settling by review alone, cancellation - is recorded explicitly in the document state line ("initiative closed", "initiative cancelled") together with the reason, in the same file, not in a separate status file. The review state line has no closed list of wordings and is not subject to automatic checking - unlike the plan marker described above, which speaks of the plan's readiness for implementation, never of the end of the initiative.

The resumption of an archived initiative is appended to REVIEW as a further entry, with the date, the reason and the scope of the resumed work. The existing entries, including the closure record, stay untouched - REVIEW is a journal in which the history of closure and resumption stand side by side in the order of events. An initiative closed without a REVIEW gets this file upon resumption, with the resumption entry as the first one.

## agent_docs/memory entry format

`agent_docs/memory/` is durable memory of decisions per module - something different from Claude's global auto-memory (`~/.claude/projects/.../memory/`), which keeps the preferences and context of a specific user between sessions. `agent_docs/memory/` keeps knowledge about the repository itself, available to every tool - Claude Code and Codex alike. If something concerns only the way of working with a specific user, it goes to Claude's auto-memory, not here.

Structure and choice of path. One file per code unit, in a group folder matching the repository structure. In the Python profile the code unit is a layer from `standard_architecture.md`, so the group for service code matches the layer: `api/`, `service/`, `data/`, `worker/`. Infrastructure directories next to the service code, for example `config/` or `alembic/`, have their own groups with the same name as the directory. A project outside the Python profile defines its code unit in `standard_documentation.md` and applies the same principle. The overriding rule stays unchanged: the path of the memory file follows directly from the path of the described code, it is never guessed, and a group is created together with its first entry, not up front. A separate `tests/` group is provided from the start - it keeps patterns of the test infrastructure that cut across many test files, so it has only `_shared.md`, without per-unit files.

Knowledge concerning several modules. A file per module does not handle cross-cutting knowledge, so there are two explicit places: `_shared.md` in the group folder (a decision concerning several modules of the same group) and `_cross_cutting.md` in `memory/` (a decision cutting across groups). Both, just like module files, are created only when there is something to record in them - they are not created up front.

Entry template. Every entry has the same shape:

```text
## YYYY-MM-DD - Short title (TICKET-ID or short task description)

- What changed:
- Why:
- Reusable pattern:
- Risk / notes:
```

A fifth, optional field `- Decisions:` is added when the entry resolves a previously open question from another entry. Memory files link to each other through a wiki-link `[[file-name]]` (without the extension) - a lighter convention than the full paths in backticks used elsewhere in the repo, reserved exclusively for this layer. Entries are appended, never overwritten - this is an append-only log.

Orientation line. A module that has `<MODULE>_ALGORITHM.md` gets a memory file right away, but it contains only one orientation line before the first entry:

```text
What the module does: see `<path>/<MODULE>_ALGORITHM.md`, sections "Algorithm goal" and "General process map".
```

This is a pointer, not a copy, so it never goes out of date. The decision log itself is created only with the first real decision. Modules without `ALGORITHM.md` get neither this line nor a file up front - for them the file is created together with the first entry.

When to write an entry. A decision is recorded durably when one of these signals is visible: a recurring task pattern in the module, a recurring finding from code review, a non-obvious workflow that the next agent would discover from scratch, an easy-to-forget domain rule, or a new architectural decision affecting future changes.

What not to do. Do not document one-off trivia as a durable rule. Do not write generic advice that fits any module - the entry is to be concrete, grounded in what actually happened. Do not record the state of the current task here - that belongs to REVIEW. Do not treat this as a changelog.

Who writes. The entry is appended by `plan-implement` at the end of the task, as the last step after implementation and the summary - only then is it known what turned out to be a durable pattern and what a one-off circumstance. Review (`implementation-dod-review`, `dod-reviewer`) may supplement the entry, but is not its owner.

## Checklist

- SEED has an explicit source of origin and is unchanged since it was saved.
- SHAPE has all eleven sections filled in, zero open `Block: yes`, a non-empty "Challenging own assumptions" section.
- SHAPE carries the regulator value in its header, and items decided without asking carry the phrase about the agent decision.
- PRD contains nothing from the blacklist: data models, columns, migrations, code paths, function names, libraries, deployment, secrets.
- PLAN has concrete names of files, functions and data contracts in every "Scope of changes" step, zero TODOs, zero open questions.
- PLAN carries in its state line a marker in one of the two allowed wordings: plan in progress or plan closed.
- The "Facts" section of a closed plan has only finding items, one per line, each with an identifier, a claim, evidence of one of the five kinds and a check date, in three fields separated by a vertical bar.
- The `ASSUMPTION:` evidence kind stands only next to content that really could not be checked - it is not a bag for what one did not feel like verifying.
- The "Open questions" section of a closed plan has not a single list item and opens with a statement of absence.
- The `agent_docs/memory` entry (if one was created) has the full set of fields, is appended - not overwritten - and landed under the correct path `memory/<group>/<module>.md`.
- REVIEW states what scope the verdict covers, and a closure without `ready` or a cancellation stands explicitly in the state line; a resumption is an appended entry, not a correction of the closure.
- None of the artifacts has bold in prose or bold labels opening a paragraph or a list item - see `standard_formatting.md`. The identifiers of facts, decisions and deviations (F-1, D-1, O-1) remain plain text, because they serve for cross-referencing, not for emphasis.
