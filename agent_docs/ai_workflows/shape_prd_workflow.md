# Workflow: seed -> shape -> PRD -> plan

This document describes the methodology of the chain carried out by the `plan-shape`, `plan-prd` and `plan-implement` skills. Use it together with `AGENTS.md` / `CLAUDE.md` - it does not replace the repository rules, it only supplements them with the process that leads from a raw request to an implemented change.

The pattern has ten blocking risk categories chosen for a service with a database and a programming interface, the recipient of the change instead of a persona, and the seed as a separate, immutable artifact instead of a section inside the notes. A project with a different risk profile changes the list of categories simultaneously in three places: here, in the `plan-shape` skill and in `docs/standards/standard_agentic_workflow.md` ch. 3.3.

## Sequence

```
plan-shape   <task description or a pointer to a ready seed file>
plan-prd     <TASK>_SHAPE.md
plan-implement  <TASK>_PLAN.md
```

Every call is manual. A skill finishes its work, says plainly what was produced and what can be called next, but does not start the next skill on its own - every phase boundary is a checkpoint at which you can see the result and turn back.

## Artifacts

One generic chain of skills handles any task through a parameter - the task name prefix and the initiative name (a directory in `plans/`). We do not create a separate skill per task.

Five files, each with one allowed kind of content - the full section templates are written directly into the `plan-shape` and `plan-prd` skills. By default flat in `plans/<INITIATIVE>/`; when an initiative carries more than one task, a subdirectory per task is allowed, `plans/<INITIATIVE>/<TASK>/` - details and an example in `docs/standards/standard_agentic_workflow.md`, section 3.2:

- `<TASK>_SEED.md` - the raw request, immutable once saved.
- `<TASK>_SHAPE.md` - a loose plan with the clarifying interview.
- `<TASK>_PRD.md` - what is to happen and why.
- `<TASK>_PLAN.md` - how to do it technically.
- `<TASK>_REVIEW.md` - the state and run of the task, not durable memory.

## Archiving and resumption

`plans/` holds only initiatives in progress. An initiative that is explicitly finished or explicitly cancelled moves as a whole, under the same name and with its task subdirectories, to `plans_finished/<INITIATIVE>/`. The evidence is a final `ready` verdict covering the whole scope of the initiative or another explicit closure recorded in its review - a complete set of files, a closed interview, a closed plan, settling one task out of several, a verdict for part of the work or the age of the directory are not evidence. With unambiguous evidence the agent moves the directory on its own (in the chain this is done by `plan-implement` after returning from the review); with a contradictory or ambiguous state it asks the user and leaves the directory in place. The move does not change seeds, old review and memory entries or frozen materials - it updates only editable references and makes sure that the tools reading the files of the initiative keep working.

Resuming the same work means returning the directory from `plans_finished/` to `plans/` with a resumption entry added to the review; merely reading the archive resumes nothing, and a new scope gets a new initiative. Before you create a new directory, check both locations - a name present in the archive means resumption, not a second seed. The full rule together with the rationale: `docs/standards/standard_agentic_workflow.md` ch. 4.6.

## Seed

Always record the verbatim content of the request and the explicit source: conversation with the user, pasted email, meeting note, branch description, report from a team member. The user may create the seed file themselves instead of dictating it in the conversation - `plan-shape` never overwrites an existing seed, it only loads it.

If the seed is too thin for anything to follow from it, record it verbatim anyway, and address the gaps with questions in the shape phase. The seed is not a place for the agent's guesses - it is a record of what was actually said, nothing more.

## Blocking risk categories

A question in the shape phase that touches one of these categories must be marked `Block: yes` and holds back the transition to the PRD until it is resolved:

1. Access token and permission scope contract - whether the token contents, the way it is resolved to an actor and the permission scopes are agreed with the token issuer and with the interface consumers, rather than assumed.
2. Stability of the programming interface (API) contract - whether the change touches the shape of a request, a response, a path or the semantics of a field used by a consumer outside this repository.
3. Database schema - whether the table, column, view or type exists. Verification: the schema dump for the actual state, the product specification for the target state.
4. Form of a schema change - the block applies to every schema change. Verification: whether the change follows the form described in `docs/standards/standard_database.md`, that is, an Alembic revision with raw SQL.
5. Source of truth for data - when the same information is in several places and it is not known which one is authoritative. Always a question to the user, not something to resolve by reading the code.
6. Time semantics and zone offset - whether writing or reading a time value can change its offset.
7. Idempotency and deduplication - whether the change can produce a double write or lose a record on retry, or whether it touches the reconciliation key.
8. Read visibility and permissions - whether the change touches who can read or do what.
9. Personal data - first and last names, contact data, and any information about the actions or the assessment of a specific person. This also applies to logs and reports.
10. Query volume and cost - when the number of rows cannot be estimated or the change lies on the path of a read performed at every display of a list.

## Detail regulator

A request may carry a parameter that controls the number and depth of questions: a number from 0 to 100, written in reference form as `C:N`. Any form of label is recognized, provided that it is directly followed by a number from that range - otherwise a Windows disk path would be read as the parameter. Two different occurrences in one seed stop the agent on a question about which value to adopt, asked before the first interview question.

The value is given in the seed, and it applies from the header of `<TASK>_SHAPE.md`, where `plan-shape` writes it as the line `Regulator: C:N`. The other skills read it only from there. No parameter means 40. The value may be changed during the task - the header then carries the new value, and the document one line about the moment of the change.

Five thresholds, each containing everything the lower one does:

1. 0-19 - only blocking questions, the agent resolves everything else.
2. 20-39 - additionally, choices whose reversal would require rewriting work already done.
3. 40-59 - additionally, every choice with different consequences for the scope or for future tasks. The default level.
4. 60-79 - additionally, what would be derived as a consequence at lower thresholds, and scope boundaries not named explicitly in the request.
5. 80-100 - a question about every decision that has more than one reasonable variant.

Blocks are untouchable across the whole scale: the ten categories above and the ban on guessing the contract apply the same way at 0 as at 100. Technical questions are asked only in phase B of `plan-prd`, regardless of the value.

Before every question the agent checks whether the answer is already in the repository - an obligation independent of the regulator, applying also at 100. A question about something that was found is asked only on one of four signals and states plainly which signal it is:

1. Two sources say different things about the same thing, including a difference between the actual and the target state.
2. The topic is covered by an open entry in `docs/standards/decision_registry.md` or described in a standard with partial status.
3. The answer is only in an artifact of a closed task in `plans/`, without confirmation in the code, a standard or the product specification.
4. A document not updated after an explicitly identified event that may have invalidated it. Requires a specific reference event, does not work as a general expiry date.

An item resolved by the agent instead of by asking carries the phrase "Agent decision at C:N, without asking".

Full definition of the mechanism: `docs/standards/standard_agentic_workflow.md` ch. 3.5.

## PRD content blacklist

A PRD answers "what and why", never "how". Forbidden: data models, column lists, migrations, code file paths, function names, library decisions, deployment details, secrets and credentials. If while writing the PRD there is an urge to record a technical solution, that material belongs to the implementation plan, not to the PRD.

## Challenging own assumptions

The shape phase requires a section in which the agent records the questions it asked itself about its own understanding of the problem, together with what came out of them. This section must not be empty - if nothing raises doubts, the problem has not been understood yet.

## Recipient instead of a persona

Instead of asking about a persona and its access, the shape phase asks about the recipient of the change and its trigger: a person in a specific role, a request from a programming interface consumer, a periodic task, another system reading the result. When the project has no user interface, the recipient is a system, and the question about a persona has no answer.
