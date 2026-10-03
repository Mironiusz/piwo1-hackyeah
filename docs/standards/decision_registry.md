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

### Technology stack and the Python profile of the standards

- Affects: whether the twelve Python profile standards stay in force (`docs/standards/README.md`), the tools in `pyproject.toml` and `makefile`, the gates that check code, and the shape of every plan.
- Variants: a backend in Python with PostgreSQL (possibly with PostGIS), which keeps the profile as it is; another backend, which removes the profile following the steps in `README.md`; no own backend, which also removes the profile.
- Blocks: the stack follows from what the product has to do; the MVP scope it has to serve is in `docs/product/specification.md` since 2026-10-03. On 2026-10-03, in phase B of `plans/mvp/`, the user chose the backend - Python 3.13 with FastAPI, on PostgreSQL with PostGIS - and with it kept the Python profile (`plans/mvp/MVP_PLAN.md` D-1). That decision lives only in a plan in progress so far. On 2026-10-03 `plans/frontend_stack/` decided the frontend technology and recorded how frontend code is held to the standards: the workflow core and `standard_frontend.md` in the standards map (`plans/frontend_stack/FRONTEND_STACK_PLAN.md`).
- Condition: the backend decision lands in the first backend code and in the standards map. The frontend half of this entry is met. The profile is kept or removed in the same change, never left in force by inertia.

### HarmonyOS port and the Huawei submission

- Affects: whether the project is submitted to the Huawei challenge at all, the architecture of the clients, the time left for the Kraków deliverables.
- Variants: a native ArkTS/ArkUI client using the same backend as the web app; a React Native for OpenHarmony client; an ArkTS application that embeds the web app and adds native platform capabilities, which is fast but likely scores lower on the use of platform capabilities; no Huawei submission. A web build alone is explicitly not a valid Huawei submission.
- Blocks: the progress of the web app, which comes first.
- Condition: the team sets a go/no-go time for the port. A `.hap` package, its build instructions, a recorded demo and `AI_WORKFLOW.md` need several hours before the deadline, so the decision has to come early enough to leave them.

### Optional features of the MVP

- Affects: the optional queue O1-O8 of `docs/product/specification.md` - QR transfer of the profile, photos, points and ranking, open city data, geozone corrections, place cards, live alerts, voice. Three of them come straight from the seed of `plans/mvp/`: points with the ranking, geozone corrections and voice.
- Variants: a pass of `plan-prd` for O1-O3 only, which the team can still reach before the deadline; a pass for the whole queue; leaving them as ideas for the presentation.
- Blocks: the specification describes them only in sketches, and the team decided on 2026-10-03 to plan and build the mandatory core M1-M11 first.
- Condition: M1-M11 meet the acceptance criteria of `plans/mvp/MVP_PRD.md`. Then the optional features get their own pass of `plan-prd`, starting with O1.

### Technical directions of the MVP plan

- Affects: `plans/mvp/MVP_PLAN.md`, which cannot be closed, and therefore cannot be implemented, until these directions are decided.
- Variants: the variants the agent offered for each direction are quoted in the seed of its initiative.
- Blocks: on 2026-10-03 the user decided that every technical direction of the MVP plan is decided by the team role responsible for it, in its own initiative, not in phase B of `plans/mvp/`. The initiatives and their owners: `plans/routing_engine/` (backend), `plans/osm_data_source/` (import), `plans/frontend_stack/` (frontend), `plans/demo_environment/` (db), `plans/osm_barrier_mapping/` (import, approved as a product rule by the owner of the specification), `plans/local_database/` (db), `plans/geocoding/` (external API), `plans/account_sessions/` (backend), `plans/api_contract/` (backend), `plans/fact_schema/` (db). The last one decides the domain model and database schema of facts and votes, together with the identifier of a vote without an account, and also builds the first schema revision (user decision of 2026-10-03, `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, question 1). That revision waits for the local database with PostGIS of `plans/local_database/` and for a backend skeleton holding the Alembic configuration, which no plan has built yet; the decision on the model does not wait for either.
- Condition: each initiative records its decision; the matching open question of `plans/mvp/MVP_PLAN.md` is then closed, and phase B of `plans/mvp/` resumes with the backend architecture.

### Intellectual property between the two challenges and the repository licence

- Affects: whether both prizes can be accepted, and which licence, if any, the public repository carries.
- Variants: no licence file (the repository is public, all rights reserved); an open-source licence (which grants licences to everyone, while the Kraków transfer agreement has the authors declare that they have granted none); submitting to one challenge only.
- Blocks: it needs an answer from the organizers - the City of Kraków challenge mentors and Huawei - on how the copyright transfer for the Kraków prize relates to the Huawei licence and to a public repository (`docs/hackathon/challenge_requirements.md`, Conflicts and open points 2 and 3). An agent does not decide this, and nothing written here is legal advice.
- Condition: the organizers have answered, before a licence file is added to the repository.

### Target environment for the demo

- Affects: `CLAUDE.md` and `AGENTS.md`, section Target environment - the three levels of agent permissions; the hosting part of the Kraków "prototype to service" plan; configuration and secrets.
- Variants: not known before the stack is chosen.
- Blocks: the technology stack decision above. On 2026-10-03 the choice of where the demo runs was delegated to `plans/demo_environment/`, owned by the db person of the team.
- Condition: the stack is chosen and `plans/demo_environment/` records where the demo runs; the three permission levels are filled in together with it.

## Resolved decisions

### Language of the repository

Resolved on 2026-10-03 by the user: everything in the repository is written in English, the conversation with the user stays in Polish. It lives in `CLAUDE.md` and `AGENTS.md`, section Language and communication style.

### Location of the product specification

Resolved on 2026-10-03 by the user: the specification lives in the repository, in `docs/product/`. It lives in `CLAUDE.md`, section What we are building.

### Product specification and the scope of the prototype

Resolved on 2026-10-03 by the user: the prototype is narrowed to wheelchair users, parents with baby strollers and people with walking difficulties, matched through barrier and amenity preferences rather than a disability, and the MVP is split into mandatory and optional features. It lives in `docs/product/specification.md`; product behavior not described there still goes to the user.

### Blocking risk categories

Resolved on 2026-10-03 by the user: the ten categories of the template stay unchanged. It lives in `docs/standards/standard_agentic_workflow.md` ch. 3.3.
