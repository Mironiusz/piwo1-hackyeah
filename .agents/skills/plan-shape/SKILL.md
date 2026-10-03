---
name: plan-shape
description: Turns a raw request (seed) into a refined loose plan through an interview with the user. Saves the seed verbatim in a separate, unmodifiable file, then conducts an interview recorded in the shape file, with sections on the problem, the recipient, the scope, the scenarios and challenging own assumptions, and with open questions marked with a blocking risk category. The first skill of the chain plan-shape -> plan-prd -> plan-implement. Use at the start of a new task whose shape is not yet settled.
---

# Turning a seed into a loose plan (shape)

Goal: build `<TASK>_SHAPE.md` from a raw request, conducting an interview that catches ambiguities before the PRD is created.

## Naming and resumption

Establish the name of the initiative (the directory in `plans/<INITIATIVE>/`) and the task prefix. If the user did not give them, propose both based on the content of the input and wait for confirmation - do not create anything on disk before confirmation, because the name is permanent and visible in the repo.

If `plans/<INITIATIVE>/<TASK>_SHAPE.md` already exists, this is a resumption: read the shape together with the seed and go straight to the section "Conduct the interview", skipping file creation.

## Archive

Before you create a new directory, check both locations: `plans/` and the `plans_finished/` archive. A name present in `plans_finished/` means an initiative explicitly finished or cancelled - do not create a second seed or a second task prefix for it. If the request is the same work, this is a resumption: the directory goes back to `plans/` with a resumption entry in the review according to `docs/standards/standard_agentic_workflow.md` ch. 4.6, and the interview continues the existing shape. If the request is a new scope on the same topic, propose a new name. Which of these two situations applies is decided by the user, not by the similarity of names. The same name present in both locations at once is a state to be clarified, not to be chosen from.

## Seed

Check whether `<TASK>_SEED.md` already exists - the user may have created it themselves, pasting a ready note instead of dictating the seed in the conversation. Never overwrite an existing seed, only read it.

The requirement of an explicit `Source:` applies only when `plan-shape` itself creates the file based on the conversation - there you always record where the request came from. If the file already exists because the user created it manually, the fact that they wrote it is a sufficient source - do not ask about a missing `Source:` line or about the exact heading `## Verbatim content`, if the content is somewhere in the file under a different section name. The only real requirement for a manually created file: it must contain some content. If the file is empty, ask what the user had in mind - an empty seed cannot be processed.

If the seed does not exist, save it as the first action, before the first question:

```text
# Seed: <one-sentence title>

Source: <conversation with the user | pasted email | meeting note | branch description | report from a team member>
Date: YYYY-MM-DD

## Verbatim content

<exactly what was said or pasted, without editing and without interpretation>
```

The file has no other sections and once saved it cannot be modified - a change of scope always goes to `_SHAPE.md`, never to the seed. If the seed is too thin for anything to follow from it, save it verbatim anyway, and address the gaps with questions in the shape phase.

## Detail regulator

The request may carry a parameter controlling the number and depth of questions: a number from 0 to 100, canonically written as `C:N`. Recognize any form of the label, on one condition - it is immediately followed by a number from this range. The condition is necessary, because seeds in this repository are sometimes written with disk paths starting with the same pattern.

No parameter in the seed means 40. Two different values in one seed stop you at a single question about which one to adopt, asked before the first interview question - as long as the conflict lasts, it is not even known how inquisitive the rest is supposed to be.

Write the established value into the header of `<TASK>_SHAPE.md` and from that moment read it from there, not from the seed. The user may change it at any moment - then update the header and add one line saying from which point the new value applies. When the value in the header differs from the one in the seed, the header applies and this is not a reason to ask.

Five thresholds, one per range. Each includes everything below it and adds its own:

- 0-19: only blocking questions. You decide everything else yourself. A task that touches no risk category may pass the interview without a single question.
- 20-39: additionally, choices whose reversal would require rewriting work already done.
- 40-59: additionally, every choice between variants with different consequences for the scope of the task or for future tasks. You decide yourself what is a consequence of decisions already made. This is the default level.
- 60-79: additionally, things that on lower thresholds you would derive as a consequence, and scope boundaries that the request does not name explicitly.
- 80-100: you ask about every decision that has more than one reasonable variant. You decide yourself only what has a single variant or stands explicitly in the repository.

The regulator does not reach the blocks at any threshold. The ten blocking risk categories and the ban on guessing a contract apply the same at 0 as at 100 - the value 0 gives an interview consisting only of blocking questions, not an empty interview.

Nor does the regulator change the fact that the shape is non-technical. A high value raises here the depth of questions about the problem, the scope and the rules, never about the solution - technical questions belong to phase B of `plan-prd`.

Mark an item that you decided yourself instead of asking with the phrase "Agent decision at C:N, without asking" in the document. Without it you cannot see what a human confirmed and what you assumed yourself.

Full definition of the mechanism: `docs/standards/standard_agentic_workflow.md` ch. 3.5.

## Before you ask

Before every question check whether the answer is not already in the repository. The rule applies at every regulator position, also at 100 - the regulator controls only what remains after subtracting the questions whose answer is already recorded. Record the answer you found in the shape together with an indication of the source, instead of asking the user about it.

Finding an answer does not close the topic when one of four signals occurs. Then the question is asked despite the finding and states explicitly which signal triggered it:

1. Two sources say different things about the same thing, including a difference between the actual state and the target state.
2. The topic is covered by an open entry in `docs/standards/decision_registry.md` or described in a standard with partial status - the rule is deliberately absent there.
3. The answer stands only in an artifact of a closed task in `plans/`, without confirmation in the code, a standard or the product specification pointed to in `CLAUDE.md`. A task journal describes the state at the moment of writing, not the state in force.
4. The document was not updated after an explicitly indicated event that could have invalidated it. The signal requires a concrete reference event and does not work as a general expiry date of the document.

## `_SHAPE.md` skeleton

```text
# Shape: <task title>

Document state: YYYY-MM-DD, interview in progress | interview closed
Regulator: C:N

## Problem

## Recipient and trigger

## Current state

## Smallest meaningful scope

## Out of scope

## Functional requirements

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

## Domain rules or explicit TODO

## Notes on data, performance and security

## Open questions
```

"Recipient and trigger" asks who or what receives the effect of the change and what triggers it: a person in a specific role, a request from a consumer of the programming interface, a periodic task, another system reading the result. When the project has no user interface, the recipient is a system, and the question about a persona has no answer. "Scenarios" describe the input, the flow and the state after completion, not user stories.

Create the file with the skeleton, filling in at the start only what follows directly from the seed. Do not fill sections with guesses.

## Conduct the interview

One question at a time - AskUserQuestion for closed decisions, plain text for open questions. How many questions are asked and how deep they reach is set by the regulator; the way they are asked does not depend on it - one question at a time applies across the whole scale. After each answer add a minimal note to the appropriate section, remove the corresponding entry from `## Open questions` and save the file. The interview can be interrupted at any moment - the state lives in the file, not in the conversation.

Mark every question touching one of the ten blocking risk categories with `Block: yes` together with the name of the category:

```text
1. <question> `Block: yes` (category: <name>)
2. <question> `Block: no`
```

The ten categories, with the full description and the verification method of each in `agent_docs/ai_workflows/shape_prd_workflow.md`: access token and permission scope contract, stability of the programming interface (API) contract, database schema, form of a schema change, source of truth for data, time semantics and zone offset, idempotency and deduplication, read visibility and permissions, personal data, query volume and cost. Blocking questions must be resolved before moving to the PRD.

Ask a question about behavior over time on a concrete run, not on the names of mechanisms: three to six points with times and the state after each step, and the question only below them. Give an undesired effect as a number, not an adjective. When a question refers to a repository artifact, first quote its fragment in the conversation - the path with the section name alone is not enough. An abstract question can get an answer to a question understood differently than it was asked, and that answer then lands in the shape as a decision nobody made.

Check an answer that can be verified by reading code or data before recording it, and show the result. Follow up on an ambiguous answer with variants instead of choosing a variant for the user. Record an answer given by the repository owner to a question addressed to another role with this caveat - it removes the question from the list, it does not replace the ruling of that other role.

After every answer that cuts something out of the scope, go back to the seed and check whether each ordered item still has an executor. When none does, interrupt the interview and say so plainly, instead of inventing a substitute goal for the initiative - the right result is then sometimes an entry in `docs/standards/decision_registry.md` with a condition for coming back. An item taken out of the scope disappears from the requirements list and the list is renumbered; the reason for the cut is described in the `## Out of scope` section. Work that changes the executor or the repository, but does not fall out of the scope, stays on the list.

When the interview reveals a defect of the same class as the scope (the same screen, the same rule, the same flow), recommend pulling it into the scope while naming the cost. Recommend a separate seed when the defect lies in another repository or outside the code of this project.

Fill in `## Challenging own assumptions` - a record of the questions you asked yourself about your own understanding of the problem, together with what came out of them. This section must not stay empty.

## Closing

Finish when all sections are filled in and `## Open questions` has no item with `Block: yes`. Change the document state to "interview closed" and tell the user that `plan-prd` can be called. Do not call it yourself - every phase boundary is a checkpoint at which the user is to see the result and be able to turn back.

## Rules

- Zero guessing of contracts, names, scopes - that is a question for the user, not a decision of the model.
- The regulator changes the number and depth of questions, never the inviolability of the blocks or the obligation to check the repository before asking.
- The initiative name and the task prefix require the user's confirmation before anything is created on disk.
- The document has no bold in prose or bold labels opening a paragraph or a list item - order provides the emphasis, not the typeface. See `docs/standards/standard_formatting.md`, the section on emphasis in prose.
