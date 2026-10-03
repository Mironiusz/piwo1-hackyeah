# PRD: First schema revision of the domain model of facts and votes - the documents its implementation needs

Document state: 2026-10-03

## Business goal

By 11:00 on 4 October 2026 the MVP of `plans/mvp/` is implemented, and every part of it that reads or writes facts and votes - the import, the route, voting, geozones, accounts and moderation - builds on one first schema revision that matches the product specification. That revision is built by a work package of the MVP plan, not by this task: on 2026-10-03 the user decided that this task writes no code and only prepares the documents the implementation of the MVP needs (`plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, Problem).

This task delivers two things that implementation is missing: a target schema that holds what the programming interface contract already asks of it - the idempotency key of a saved report or geozone - and one place in the MVP plan that says who builds the first revision and what it has to meet.

## Problem and its consequences

- The contract of `docs/product/api_contract.md` asks that a save of a report or a geozone repeated with the same key returns the first fact and creates nothing, and the target schema `docs/product/schema.md` has nowhere to keep that key. Until it does, the repetition cannot be implemented as contracted (`plans_finished/api_contract/API_CONTRACT_REVIEW.md` R-2). A person whose phone loses signal after the save and retries gets two facts of the same stairs at the same place, each unverified, with the votes of everyone after them split between the two.
- The documents in force - `plans/mvp/MVP_PLAN.md` D-11, its Risks and Q-11, and the entry Technical directions of the MVP plan in `docs/standards/decision_registry.md` - say this task builds the first revision. After the decision of the user they no longer hold, and no work package of the MVP plan has the revision. Its requirements stand only in archived artifacts of `plans_finished/` and in the shape of this task, so a work package that reads the MVP plan and the specification alone would miss them.
- If the MVP plan does not state the order - the local setup and the backend skeleton first, then the revision, then the critical tests that check it - the loop that `plans_finished/dependency_check/` cut on 2026-10-03 can come back inside that plan.

## Scope

- A new version of the product specification that brings the idempotency key of a saved report or geozone into the target schema.
- An entry in `plans/mvp/MVP_PLAN.md` that hands a work package of that plan the first schema revision with everything it has to meet.
- The documents in force that name this task as the builder of the revision follow that entry.

## Out of scope

- Any code: the first schema revision, the code of the rules its tests need and the tests themselves. They are built by a work package of the MVP plan, which also decides which of its work packages builds which code of the rules. Decided by the user on 2026-10-03, against this task building the revision or any of that code, and against cancelling this task and moving everything to the MVP plan (`plans/schema_revision/SCHEMA_REVISION_SHAPE.md`, Problem).
- When the revision is ready: the Rollout order of `plans/mvp/MVP_PLAN.md`.
- The rules of facts and votes, the target schema except the change of FR-1, and closing Q-10 of the MVP plan: the task `FACT_SCHEMA` of `plans_finished/fact_schema/`.
- The local setup, its configuration of schema changes and their critical tests: the work package of `plans/mvp/MVP_PLAN.md` D-7.
- The periodic task of the worker that deletes the identifiers of votes without an account 30 days after the vote: Q-11 of `plans/mvp/MVP_PLAN.md`.
- The import, which writes the OpenStreetMap facts by these rules: a work package of `plans/mvp/` after Q-11.
- The archived artifacts of `plans_finished/` that say this task builds the revision. They keep their wording as history (`docs/standards/standard_agentic_workflow.md` ch. 4.6, Protecting history).

## Functional requirements

FR-1. The target schema holds the idempotency key. A new version of `docs/product/specification.md`, approved by the user, makes the target schema `docs/product/schema.md` keep, for every report and geozone saved through `create_fact` of `docs/product/api_contract.md`, the key of that save for as long as the fact exists, and makes the stored data refuse, by itself, a second fact with a key already saved. A fact from OpenStreetMap, a fact converted from one and sample data have no key. How the key is stored either meets the convention of `docs/standards/standard_idempotency.md` or is recorded as a deviation from it with its reason. The version changes no other rule and nothing else of the target schema.

FR-2. The revision handed to the MVP plan. `plans/mvp/MVP_PLAN.md` states that a work package of that plan builds the first schema revision, its tests and the code of the rules those tests need, and that the revision and its tests meet:

- FR-15 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`: the stored data refuses, by itself, the states the rules forbid, the second fact with a saved key of FR-1 included;
- the scenarios of AC-1 - AC-12 there, run on the stored data in the kinds of tests that `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-21 names, with the last sentence of AC-4 met by the periodic task of the worker of Q-11;
- the match of the stored data with the target schema line by line, in the version of FR-1 (AC-13 there);
- the extensions the target schema names, created by the first revision in the chain;
- exactly the rights of the service account the target schema names, with the name of that account never written in the repository;
- the names of the database objects it creates entered in the registry of names of the repository;
- the order: after the local setup, its configuration of schema changes and the backend skeleton, and before the critical tests of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` D-8 that check the first revision.

Which work package builds which code of the rules is that plan's decision.

FR-3. The references follow. D-11, the Risks, Q-11 and the Supplementary files of `plans/mvp/MVP_PLAN.md` and the entry Technical directions of the MVP plan in `docs/standards/decision_registry.md` name the work package of FR-2 instead of this task as the builder of the first revision, and none of them says any longer that this task waits for Q-11 or for the backend skeleton.

## Acceptance criteria

AC-1 (FR-1). The specification has a new version approved by the user, whose history names this initiative and the decision of the user of 2026-10-03. Read against scenario 1 of `plans/schema_revision/SCHEMA_REVISION_SHAPE.md` - a save at 10:00:01 whose response is lost, the same save repeated at 10:00:06 and again 25 hours later, and the same key sent with another content - the target schema leaves one fact, unverified with 0.5 of confirmations, and lets the stored data refuse every second fact with that key.

AC-2 (FR-1). The target schema says which facts carry a key and which do not, and that a key is kept for as long as its fact exists. Its form either meets the convention of `docs/standards/standard_idempotency.md`, section Reconciliation key, or a deviation from it is recorded with its reason where the standards of the repository record deviations. A comparison of the new version with version 7 shows no other change of a rule or of the target schema.

AC-3 (FR-2). A person who reads only `plans/mvp/MVP_PLAN.md` and the specification finds every item of FR-2 and knows that a work package of the MVP plan builds the first revision, without opening `plans/schema_revision/` or `plans_finished/`.

AC-4 (FR-3). No document in force names this task as the builder of the first revision or says that it waits for Q-11 or for the backend skeleton; the archived artifacts of `plans_finished/` are unchanged.

## Domain rules

- The idempotency key of a report or a geozone is kept with the fact for as long as the fact exists, so a repetition of the same save counts as the same save however late it arrives - the permanent kind of duplicate of `docs/standards/standard_idempotency.md`, section Two kinds of duplicate. Decided by the user on 2026-10-03, answering for the db person, against a key cleared 24 hours after the save and against no stored key with duplicates accepted as a recorded deviation.
- The key is a random value generated once per approved summary of a save. It identifies no person and links no two saves of one person, so keeping it adds no personal data.
- The rules of votes, statuses, flags and hiding are those of version 4 of `docs/product/specification.md`, and the target schema is that of version 6, both carried into version 7 in force on 2026-10-03 (`plans/mvp/MVP_PLAN.md` D-11). This task changes none of them.
- The target schema is part of the specification. It changes only through a new version of the specification approved by the user (`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-21), and every schema revision is reviewed against it line by line (`docs/standards/standard_database.md`).
- Versions of the specification are numbered in the order the user approves them, so no document fixes the number of a version before its approval.
- This task writes no code. Decided by the user on 2026-10-03.
- The db person owns this task. Both decisions of the user in its interview were made in place of the db person, whose ruling is still to be confirmed.

## Dependencies and impact on other modules

- `plans/mvp/MVP_PLAN.md`, a plan in progress, gets the entry of FR-2 and the changes of FR-3. Its sections Scope of changes, Rollout order and Definition of Done are empty, so the work package of FR-2 is defined when that plan writes them; it has to carry the entry before it closes. Other sessions edit that plan on 2026-10-03 for `plans/valhalla_routing/` and `plans/deployment/`.
- `docs/product/specification.md` and `docs/product/schema.md` get a new version (FR-1). The documents that name the version of the specification in force follow it, and `plans/valhalla_routing/` plans a new version of its own.
- `docs/product/api_contract.md` does not change. The repetition of `create_fact` becomes implementable once FR-1 is approved.
- `docs/standards/decision_registry.md` changes in the entry Technical directions of the MVP plan (FR-3).
- `docs/standards/standard_idempotency.md` is the standard FR-1 either meets or records a deviation from.
- The initiative of Q-11 of the MVP plan, not set up yet, builds the backend skeleton the revision waits for and the periodic task of the worker that meets the last sentence of AC-4 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md`.
- The work packages of the import, the route, voting, geozones, accounts and moderation build on the revision of FR-2; the routing engine of D-9 reads the stored ways and points, and `plans/valhalla_routing/` may replace it.
- The archived artifacts of `plans_finished/fact_schema/` and `plans_finished/local_database/` keep saying that this task builds the revision.

## Risks and notes

- The db person has not confirmed either decision of the user. If that person rejects a stored key, the contract of `create_fact` changes or a deviation from the idempotency standard is recorded; if that person wants the revision back in this task, the loop of `plans_finished/dependency_check/` has to be checked again.
- The target schema has run only in its parts without the spatial extension, on an older PostgreSQL (`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md`, Risks). An error found by the work package of FR-2 needs another version of the specification approved by the user, during the night of the implementation.
- A gap in the target schema surfaces only when the work package of FR-2 runs AC-1 - AC-12 on the stored data, after Q-11 and the backend skeleton.
- The revision cannot be built before the initiative of Q-11, which is not set up yet, decides the backend skeleton. That stays the longest path to the deadline; this task does not shorten it, it only stops being on it.
- The idempotency standard has the status "ready - full content", and the repository applies the standards in their strict version (`CLAUDE.md`, section Full compliance with the standards). A deviation for the form of the key is an explicit decision recorded with its reason, not a quiet difference.
- The archived artifacts that still say this task builds the revision, among them D-7 of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md`, can mislead a reader who does not reach the MVP plan; the MVP plan is the document in force.
