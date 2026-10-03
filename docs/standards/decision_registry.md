# Deferred decisions registry

Document state: 2026-10-03

## Why this document exists

This file collects decisions that are known to be needed but have been deliberately postponed - because a measurement is missing, because they depend on a contract with someone outside, or because their moment has not come yet. Without such a place, a decision deferred in a conversation disappears together with the conversation and comes back only as a surprise during implementation, when it is already the most expensive.

This is not a standard and it has no core sections. It is a registry, like `naming_registry.md` - it describes the actual state of the decision process, not the target state of the repository.

Boundary with the neighbors: `docs/standards/README.md`, in the section on boundaries and debts, describes decisions already made and debt already present in closed initiatives - it looks to the past. This file looks to the future. The `<TASK>_REVIEW.md` artifact in `plans/` records what the agent ran into during one task; if such a finding leads to a decision that goes beyond that task, its place is here.

## How to use it

An entry is created at the moment someone states that the decision cannot responsibly be made today. It always contains four things: what the decision affects, what the variants are, what blocks resolving it, and how we will know it can be made.

An entry leaves the list of open decisions only when the decision has landed where people look for it - in the right standard, in the product specification or in the code. It then moves to the resolved section with one sentence about how it turned out and where it lives now. The entry here is never the source of truth for a rule - it is only a record that the rule does not exist yet.

A deferral needs a reason. "We did not want to think about it" is not a reason; "we have no measurement on the target driver" is.

## Open decisions

### Product specification and the scope of the prototype

- Affects: everything about product behavior - the target user group, which barriers and amenities are shown, how routes are matched to needs, the reliability statuses of data, what users can report and how. `CLAUDE.md` names `docs/product/specification.md` as the source of truth for the product.
- Variants: the Kraków brief asks to narrow the prototype to a chosen group (its example: wheelchair users and parents with baby strollers), and Huawei prefers a working narrow solution; the team's idea mentions routes for people with different disabilities. Route profiles can be named after needs and built from barrier preferences, or named after disabilities - the brief advises against requiring a disability to be disclosed (`docs/hackathon/challenge_requirements.md`, Conflicts and open points 6 and 7).
- Blocks: the team is still writing the specification.
- Condition: `docs/product/specification.md` exists and names the target group. Until then no product behavior is decided by an agent - every such question goes to the user.

### Technology stack and the Python profile of the standards

- Affects: whether the twelve Python profile standards stay in force (`docs/standards/README.md`), the tools in `pyproject.toml` and `makefile`, the gates that check code, and the shape of every plan.
- Variants: a backend in Python with PostgreSQL (possibly with PostGIS), which keeps the profile as it is; another backend, which removes the profile following the steps in `README.md`; no own backend, which also removes the profile.
- Blocks: the specification is not written yet, and the stack follows from what the product has to do.
- Condition: phase B of `plan-prd` for the first product initiative chooses the stack. The profile is kept or removed in the same change, never left in force by inertia.

### HarmonyOS port and the Huawei submission

- Affects: whether the project is submitted to the Huawei challenge at all, the architecture of the clients, the time left for the Kraków deliverables.
- Variants: a native ArkTS/ArkUI client using the same backend as the web app; a React Native for OpenHarmony client; an ArkTS application that embeds the web app and adds native platform capabilities, which is fast but likely scores lower on the use of platform capabilities; no Huawei submission. A web build alone is explicitly not a valid Huawei submission.
- Blocks: the progress of the web app, which comes first.
- Condition: the team sets a go/no-go time for the port. A `.hap` package, its build instructions, a recorded demo and `AI_WORKFLOW.md` need several hours before the deadline, so the decision has to come early enough to leave them.

### Intellectual property between the two challenges and the repository licence

- Affects: whether both prizes can be accepted, and which licence, if any, the public repository carries.
- Variants: no licence file (the repository is public, all rights reserved); an open-source licence (which grants licences to everyone, while the Kraków transfer agreement has the authors declare that they have granted none); submitting to one challenge only.
- Blocks: it needs an answer from the organizers - the City of Kraków challenge mentors and Huawei - on how the copyright transfer for the Kraków prize relates to the Huawei licence and to a public repository (`docs/hackathon/challenge_requirements.md`, Conflicts and open points 2 and 3). An agent does not decide this, and nothing written here is legal advice.
- Condition: the organizers have answered, before a licence file is added to the repository.

### Target environment for the demo

- Affects: `CLAUDE.md` and `AGENTS.md`, section Target environment - the three levels of agent permissions; the hosting part of the Kraków "prototype to service" plan; configuration and secrets.
- Variants: not known before the stack is chosen.
- Blocks: the technology stack decision above.
- Condition: the stack is chosen and the team picks where the demo runs; the three permission levels are filled in together with it.

## Resolved decisions

### Language of the repository

Resolved on 2026-10-03 by the user: everything in the repository is written in English, the conversation with the user stays in Polish. It lives in `CLAUDE.md` and `AGENTS.md`, section Language and communication style.

### Location of the product specification

Resolved on 2026-10-03 by the user: the specification lives in the repository, in `docs/product/`. It lives in `CLAUDE.md`, section What we are building. The content of the specification is still open - see the open entry above.

### Blocking risk categories

Resolved on 2026-10-03 by the user: the ten categories of the template stay unchanged. It lives in `docs/standards/standard_agentic_workflow.md` ch. 3.3.
