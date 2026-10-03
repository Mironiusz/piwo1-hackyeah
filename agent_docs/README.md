# agent_docs

Index of the agentic layer of the repository. This layer is editable by the agent - unlike `docs/`, which is the fixed source of standards and of machine-generated knowledge. Never mix the two: if you are writing a new standard or correcting the description of a code unit, it goes to `docs/`; if you are recording a decision or a pattern from a real task, it goes here.

## What is here

- `session_context.md` - two sentences about the project and a pointer to the product specification. The SessionStart hook inserts them at the beginning of every session, so the file is to stay short.
- `ai_workflows/shape_prd_workflow.md` - a description of the seed -> shape -> PRD -> plan chain, served by the `plan-shape` and `plan-prd` skills, together with the rule for archiving a finished initiative to `plans_finished/` and for resuming it. Open it for every new task whose shape is not yet settled and before closing or resuming an initiative.
- `memory/` - durable decisions per code unit, one file per unit, in the folder of the group that matches the repository structure. Entry convention, code unit and choice of file: see `docs/standards/standard_agent_docs.md`.

## How to choose a file in memory

See `docs/standards/standard_agent_docs.md`, section "agent_docs/memory entry format".

## Index of docs/

`docs/` is fixed and the agent does not edit it outside a task that is explicitly about it (`docs/standards/standard_agentic_workflow.md`, ch. 5.1).

- `docs/standards/` - fixed standards written by a human. The full list, the readiness status and the boundaries of each standard are in `docs/standards/README.md` - that file is the entry point to this directory, not this list. Open a specific standard according to the mapping in that file, not upfront.
- Directories that the project adds itself, for example a machine-generated database schema dump or operational knowledge about the environment, are entered by the project in the map in `docs/standards/README.md` together with their provenance. The schema dump is a picture of the actual state of the server, not the source of truth about the schema - editing such a file does not change the database.

Outside `docs/` there is one more source, superior to all of them: the product specification indicated in `CLAUDE.md`, section What we are building. In case of a discrepancy with anything else, the product specification prevails.

The full task type -> document to open mapping, including when to reach for `agent_docs/` and when for `docs/`, is in `docs/standards/README.md`.
