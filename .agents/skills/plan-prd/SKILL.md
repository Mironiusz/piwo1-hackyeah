---
name: plan-prd
description: Turns a finished loose plan (shape) into a PRD, and then into an implementation plan, in two separate phases with a confirmation gate between them. The PRD answers what and why without technical decisions, the implementation plan answers how, with facts verified in the code and the database. The second skill of the chain plan-shape -> plan-prd -> plan-implement. Use after the interview in plan-shape is closed, on the `_SHAPE.md` file.
---

# From shape to PRD and implementation plan

Goal: complete the chain `plan-shape -> plan-prd -> plan-implement`, producing `_PRD.md` and `_PLAN.md` in two clearly separated phases. The separation is necessary, because the PRD bans technical content while the implementation plan requires it - mixing both in one run leads to premature freezing of technical decisions.

## Resumption

Read the task prefix and the initiative name from the path of the file you are called on - never invent your own. If `_PRD.md` already exists but `_PLAN.md` does not, this is a resumption: go straight to phase B. If both exist, ask the user what is to change, instead of starting from scratch.

## Archive

A file under `plans_finished/` belongs to an initiative explicitly finished or cancelled. Do not write a PRD or a plan in the archive: work on such an initiative starts with its resumption, that is, the return of the whole directory to `plans/` on the user's instruction, according to `docs/standards/standard_agentic_workflow.md` ch. 4.6. Merely reading an archived shape or asking about a past result is not a resumption.

## Detail regulator

Read the regulator value from the header of `<TASK>_SHAPE.md`, never from the seed. No header with a value means 40.

In phase A the regulator changes nothing except the depth of questions about the scope and the domain rules - the PRD does not decide technical solutions anyway, and the confirmation gate before phase B applies at every position of the scale.

In phase B the regulator controls how many technical decisions you make yourself and how many you put to the user:

- 0-19: only blocking questions. You make all technical decisions yourself and record them in `## Decisions` together with the reason.
- 20-39: additionally, choices whose reversal would require rewriting work already done.
- 40-59: additionally, every choice with different consequences for the scope or for future tasks. This is the default level.
- 60-79: additionally, the direction of the solution where more than one sensible approach exists, even if one of them clearly prevails.
- 80-100: you ask about every decision that has more than one reasonable variant, including the order of steps, the boundaries of the change and the method of verification.

Blocks and the ban on guessing a contract stand outside the regulator's reach at every threshold. So does the obligation to check in the code, the database and the documentation everything the PRD assumes - the regulator does not release you from step 5, only from asking about what that step has already established.

Mark a decision taken independently instead of by asking in `## Decisions` with the phrase "Agent decision at C:N, without asking".

Full definition of the mechanism: `docs/standards/standard_agentic_workflow.md` ch. 3.5.

## Phase A: PRD

1. Read `<TASK>_SHAPE.md` and `<TASK>_SEED.md`.
2. Stop if the shape has unresolved `Block: yes` questions. Do not try to resolve them by guessing - put them to the user and add the answers to the shape, then come back.
3. Write `<TASK>_PRD.md` according to the template:

```text
# PRD: <task title>

Document state: YYYY-MM-DD

## Business goal

## Problem and its consequences

## Scope

## Out of scope

## Functional requirements

## Acceptance criteria

## Domain rules

## Dependencies and impact on other modules

## Risks and notes
```

Hard blacklist of content forbidden in a PRD: data models, column lists, migrations, code file paths, function names, library decisions, deployment details, secrets and credentials. The PRD answers "what and why", never "how". If while writing the PRD there is an urge to record a technical solution, that material belongs to `_PLAN.md`, not here.

4. Show the user what was created and ask for confirmation before moving to phase B. This is the only gate between "what" and "how", so do not pass it silently.

## Phase B: implementation plan

5. Open the documents pointed to by the task -> document mapping in `AGENTS.md` / `CLAUDE.md` for this type of task. Verify in the code, the database and the documentation everything the PRD assumes, and record the findings in the `## Facts` section in the format described in `docs/standards/standard_agent_docs.md`, section PLAN format: identifier, claim, evidence of one of the five kinds and check date. Do not repeat the pattern here - the standard is its only address, and the automatic check reads it from there.
6. Calculate the blast radius of the change before you write down the scope of changes: all call sites, database schema objects, configuration keys and automatic checks that the planned change touches indirectly. Derive this list from the reads in step 5, not from guessing. If it goes beyond the scope agreed in the PRD, stop and ask the user about splitting the plan, instead of quietly extending the scope. This stop is something different from the return from step 8: there the PRD turned out to be wrong, here the PRD may be correct, merely too narrow.
7. Write `<TASK>_PLAN.md` according to the template:

```text
# Plan: <task title>

Document state: YYYY-MM-DD, plan in progress

## Goal

## Facts

## Decisions

## Scope of changes

## Rollout order

## Definition of Done

## Risks

## Open questions

## Supplementary files
```

Every step in `## Scope of changes` must have concrete names of files, functions and data contracts, not a description in the style of "something like".

8. If the verification from step 5 disproves an assumption from the PRD, stop and go back to phase A. The PRD is a contract, so it must not be quietly worked around in the plan.
9. Finish when the plan meets the completeness criteria that `plan-implement` will require anyway: zero TODOs, zero items in `## Open questions`, every step with an unambiguous input and output. Then change the marker in the state line to `plan closed` - only that marker pulls the document under the finding format check, so a plan written in installments stays at `plan in progress` until the very end. Tell the user that `plan-implement` can be called. Do not call it yourself.

## Rules

- Zero guessing of contracts, names, scopes - that is a question for the user, not a decision of the model.
- Phase A and phase B are separated by a confirmation gate - never move from the PRD to the plan without showing the PRD to the user.
- Put questions to the user the same way as in `plan-shape`: behavior over time on a concrete run with times and the state after each step, the effect as a number, and the artifact you are asking about quoted as a fragment, not by its path alone.
- A requirement taken out of the scope disappears from the requirements list and the list is renumbered, and the reason for the cut goes to `## Out of scope`. An item marked with an "out of scope" annotation and left on the list requires deciding, at every reading, whether it counts.
- In the plan, assign to a human only the steps that the agent cannot or should not perform: installing an application, changing system settings, commit, push, Merge Request, an operation on a shared database and consents required by security rules. The agent performs the rest. Collect the human's steps in one concise list at the end of `## Rollout order`.
- Neither document has bold in prose or bold labels opening a paragraph or a list item - order provides the emphasis, not the typeface. See `docs/standards/standard_formatting.md`, the section on emphasis in prose. Identifiers of facts, decisions and requirements such as F-1, D-1, WF-1 remain plain text, because they serve for cross-referencing, not for emphasis.
