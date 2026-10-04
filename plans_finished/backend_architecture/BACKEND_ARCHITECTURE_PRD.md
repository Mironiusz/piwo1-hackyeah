# PRD: Backend architecture with the worker, Q-11 of the MVP plan

Document state: 2026-10-04

## Business goal

Close Q-11, the last open question of `plans_finished/mvp/MVP_PLAN.md`, so that the MVP plan can be closed and its work packages can start building the app before the Kraków submission closes at 11:00 on 4 October 2026. Every work package of the backend then knows where its code goes and how it is started, and the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/` knows which parts of the demo run on the server.

## Problem and its consequences

- While Q-11 is open, the MVP plan has no work packages, so nobody builds the backend skeleton, the first schema revision cannot be applied in it, and the deployment configuration cannot be written (`plans_finished/mvp/MVP_PLAN.md`, section Risks; `plans_finished/deployment/DEPLOYMENT_PLAN.md`, the new text of D-10). Every hour Q-11 stays open is taken from the time left before the deadline.
- The finished initiatives left to Q-11 what they could not decide without guessing the backend architecture: how the one backend process starts, the form and the place of the import and refresh run, how the backend follows the copy the routing service serves, where each part of the demo runs on the server, the names of the modules of the address search and of the tag rule, and the structure that implements the operations of `docs/product/api_contract.md` (shape, section Smallest meaningful scope).
- The specification requires the hash of a vote without an account to be deleted 30 days after the vote, which needs a periodic task, while the demo and all its data are deleted on 4 October 2026, one day after the first vote can be cast. Building that task costs time before the deadline for an effect the demo never shows (shape, section Challenging own assumptions).

## Scope

- The decisions of Q-11, recorded in the plan of this initiative:
  1. how the one backend process is started;
  2. the form of the trigger of the import and refresh run and the machine it runs on;
  3. how the backend learns which copy the routing data served by the routing service was built from, how the routing service moves to the routing data of a fresh copy, and how the backend process holds the graph of the route with the fewest barriers;
  4. where the backend process, the worker, the database, the static frontend and the routing service run on the server of the demo;
  5. the names of the modules and functions of the address search and of the tag rule;
  6. the structure that implements the operations of `docs/product/api_contract.md`.
- Closing Q-11 in the MVP plan and handing the implementation of the operations to its work packages.
- The rule that the hash of a vote without an account is kept until the demo is deleted, written into the specification and into the documents that follow it.

## Out of scope

- Any code, the backend skeleton included. The work packages of `plans_finished/mvp/` build it, the skeleton with the local setup in the work package of D-7 there. Decided by the user on 2026-10-03 in the shape, question 1.
- The implementation of the operations of `docs/product/api_contract.md`. It goes to the work packages of `plans_finished/mvp/`, not to Q-11 as `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-1 said. Decided by the user on 2026-10-03 in the shape, question 1.
- A periodic task that clears the hash of a vote without an account. Decided by the user on 2026-10-04 in the shape, question 5.
- Rewriting D-10 of `plans_finished/mvp/MVP_PLAN.md` to the server of the user. The task `DEPLOYMENT` of `plans_finished/deployment/` does it, and this initiative only refers to it. Decided by the user on 2026-10-04 in the shape, after a conflict with question 6.
- Whatever the stored data holds only to find the hashes to clear. `plans_finished/schema_revision/` builds the first schema revision and decides it once this initiative tells it of the change (FR-6).
- The choice of the routing engine and the content of a route request, decided in `plans_finished/valhalla_routing/`.
- The deployment configuration itself and the written instructions for the server, which belong to `plans_finished/deployment/`.

## Functional requirements

FR-1. Decisions of Q-11. The plan of this initiative decides each of the six items of the section Scope, so that the person building a work package of `plans_finished/mvp/` puts its code where the plan says and starts it as the plan says, without asking. The names follow `docs/standards/standard_naming.md`, and the structure follows the standards of the Python profile in `docs/standards/`.

FR-2. Closing Q-11. Q-11 of `plans_finished/mvp/MVP_PLAN.md` becomes a decision of that plan that names this initiative, as its other decisions name theirs, and that plan is left with no open question.

FR-3. Implementation of the operations. D-12 of `plans_finished/mvp/MVP_PLAN.md`, which says "the implementation of the operations goes with Q-11", hands the implementation of the operations to the work packages of that plan instead.

FR-4. One copy per route during a refresh. The decision of item 3 keeps every route on one copy: from the moment a fresh copy becomes the copy in use until the routing service serves the routing data of that copy, every route request ends with the error routing unavailable, and afterwards every route comes from the fresh copy, with the graph of the route with the fewest barriers rebuilt from it. No route combines the ways of one copy with the facts of another (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-3). The plan states how long that gap lasts in one refresh.

FR-5. Start before the data. The backend process starts and keeps running when no schema revision has been applied and no copy has been loaded, because on the server the start comes first and the revisions and the loading follow it by hand (`plans_finished/deployment/DEPLOYMENT_PLAN.md` D-4). Until a copy is loaded and the routing service serves its routing data, a route request ends with the error routing unavailable.

FR-6. Hash kept until the demo is deleted. A new version of `docs/product/specification.md`, after version 8, says that the hash of a vote without an account is kept until the demo and all its data are deleted on 4 October 2026, in M9 and in the section Personal data, and drops the statement that the vote limit of a person without an account reaches back at most 30 days. `docs/product/schema.md`, AC-12 of `plans_finished/mvp/MVP_PRD.md` and Q-11 of `plans_finished/mvp/MVP_PLAN.md` follow it, so that no document in force requires the deletion after 30 days. `plans_finished/schema_revision/` is told of the change and changes its own documents.

FR-7. Fit on the server. Everything the decision of item 4 places on the server fits in its 16 GB of memory at the peak of an import and refresh run, the build of the routing data included, with the needs of the routing service of `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-14.

## Acceptance criteria

AC-1 (FR-1). For each of the six items of the section Scope the plan holds a decision with the names and the places a work package needs. A reading of the plan by the person of each work package of the backend - the import, the route, the voting, the accounts, the moderation and the address search - finds where its code goes and how it starts, without a question back to this initiative.

AC-2 (FR-2). The section Open questions of `plans_finished/mvp/MVP_PLAN.md` holds no question, and the decision that replaced Q-11 names `plans_finished/backend_architecture/`.

AC-3 (FR-3). No document in force says that the implementation of the operations goes with Q-11; D-12 of `plans_finished/mvp/MVP_PLAN.md` names the work packages of that plan.

AC-4 (FR-4). Shape scenario 2: the copy in use has the instant T1 and the routing service serves routing data of T1; a member of the team triggers a refresh. A route request between the moment T2 becomes the copy in use and the moment the routing service serves the routing data of T2 ends with routing unavailable; a route request after that moment comes from T2. The plan states the expected length of the gap.

AC-5 (FR-5). Shape scenario 3: the start runs on a server with no revision applied and no copy loaded. The backend process is still running after the start, and a route request ends with routing unavailable. After the revisions and the loading, a route request returns a route without a restart of the backend process, or the plan names the restart as a step of the loading.

AC-6 (FR-6). Shape scenario 4: a person without an account confirms a fact at 10:00 on 4 October 2026, and the hash of that vote exists until the demo is deleted. The specification, `docs/product/schema.md`, `plans_finished/mvp/MVP_PRD.md` and `plans_finished/mvp/MVP_PLAN.md` hold no rule that deletes or clears the hash 30 days after the vote; the archived documents of `plans_finished/` keep their wording as history. `plans_finished/schema_revision/` has received the change.

AC-7 (FR-7). The plan sums the memory of every part the decision of item 4 places on the server at the peak of an import and refresh run, the build of the routing data included, and the sum is at most 16 GB.

## Domain rules

- The backend that answers requests runs as exactly one process (`plans_finished/geocoding/GEOCODING_PLAN.md` D-15).
- The import and refresh run is an administrative run started by a member of the team, never by request handling and never on a schedule, and a second trigger while a run holds its lock ends at once as a skipped run (`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-11).
- The demo runs on the server of the user in a data centre, with 16 GB of memory and 16 cores; what else runs on it is not known, so the demo uses only its own services, database and logs (shape, section Domain rules; `CLAUDE.md`, section Target environment).
- The hash of a vote without an account is never cleared by the app; it disappears with every other piece of data when the demo is deleted on 4 October 2026, and the vote limit and the latest votes of five persons of M4 tell persons without an account apart over the whole life of the demo. Decided by the user on 2026-10-04 in the shape, questions 5 and 7.
- The answers of the shape were given by the user for the backend person, the owner of Q-11, and the change of the hash also for the db person, the owner of the schema; their rulings are still to be confirmed.

## Dependencies and impact on other modules

- `plans_finished/mvp/MVP_PLAN.md`: Q-11 closes, D-12 changes; D-10 is rewritten by `plans_finished/deployment/`, not here. The work package of D-7 there and the work packages of the import, the route, the voting, the accounts, the moderation and the address search build in the structure of FR-1.
- `plans_finished/valhalla_routing/`: its D-3, D-7 and D-14 are the needs of items 3 and 4; its implementation runs in parallel and edits the MVP plan and the specification at the same time.
- `plans/deployment_config/`: the task `DEPLOYMENT_CONFIG` waits for Q-11 and the skeleton, and takes the placement of item 4 and the start of item 1 into its configuration.
- `plans_finished/schema_revision/`: its PRD names the periodic task three times, and the first revision builds what the stored data holds only for the clearing; it changes both after FR-6.
- `docs/product/specification.md`, `docs/product/schema.md` and `plans_finished/mvp/MVP_PRD.md`: changed by FR-6.
- `plans_finished/geocoding/`, `plans_finished/osm_barrier_mapping/` and `plans_finished/osm_data_source/`: their open names and the form of the import trigger are decided here; the archived documents are not changed.

## Risks and notes

- Time. The MVP plan, its work packages, the skeleton and the deployment configuration all wait for this initiative, and the deadline is 11:00 on 4 October 2026.
- Parallel editing. Other sessions edit `plans_finished/mvp/MVP_PLAN.md` and the specification at the same time; every edit is checked against `git status` and the modification time of the file right before it (`docs/standards/standard_agentic_workflow.md` ch. 4.7).
- Personal data. The hash is personal data. Kept until the demo is deleted, it lives at most one day; if the demo lives longer than 4 October 2026, the hash lives with it without a limit, and the specification then has to be changed again.
- The worker. Without the periodic task the worker has no task the specification describes, so the plan may find that the demo runs no worker process at all; Q-11 is still named "with the worker", and the plan says what is left of it.
- Gap during a refresh. Routes are unavailable for the length of the gap of FR-4. A refresh is triggered only by hand and rarely, so the gap is accepted, but a refresh during the live demo would show it.
- Unconfirmed rulings. The backend person and the db person have not confirmed the answers given for them.
