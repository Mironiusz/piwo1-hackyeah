# Review: Consistency check of all initiatives and of the MVP plan, and its fixes

Document state: 2026-10-03, fixes finished, review ready for the whole initiative, moved to `plans_finished/`

## Check of 2026-10-03

### Scope

The agent read `docs/product/specification.md` version 3, `docs/standards/decision_registry.md`, `agent_docs/memory/`, and the artifacts of every initiative in `plans/`: `mvp`, `geocoding`, `osm_data_source`, `osm_barrier_mapping`, `frontend_stack`, `fact_schema`, `local_database`, `demo_environment` with its task `DEPLOYMENT`, `api_contract`, `account_sessions` and `routing_engine`. Seeds were read only for `mvp` and `fact_schema`, because a seed is a verbatim record and decides nothing; the PRDs of the closed initiatives were checked through their plans and reviews. The initiative has no shape, PRD or plan: the request was a check and its fixes, and this file records both.

### Findings

The findings name the paths as they were at the time of the check. `geocoding`, `osm_data_source`, `osm_barrier_mapping`, `frontend_stack` and `local_database` moved to `plans_finished/` later the same day (U-8, section What was done).

C-1. The disputed status. `docs/product/specification.md` version 3, M4, gives confirmed at the fourth step of scenario 3 of `plans/mvp/MVP_SHAPE.md` (confirmations 2.0, one denial), while `plans/mvp/MVP_PRD.md` AC-6 expects disputed, and the Domain rules of the same PRD restate the wording of the specification. The user settled it for `plans/fact_schema/` in question 8 of its shape, but the specification, which prevails, still says confirmed.

C-2. The rule of voting. The specification, M4, has "One person has one vote per fact", and M9 says the hashed identifier serves only that rule, while `plans/fact_schema/FACT_SCHEMA_SHAPE.md` replaced it with a vote limit of x days, a window of the latest votes of k persons and only the latest vote of a person counting (x = 1 day and k = 5 in `plans/fact_schema/FACT_SCHEMA_PRD.md`). The old rule is repeated in `plans/mvp/MVP_PRD.md` AC-6, in `plans/api_contract/API_CONTRACT_SHAPE.md` Functional requirements 4 and in `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` Functional requirements 3. The specification also does not state D-21 of the plan of `osm_data_source`, the weight a vote keeps after its identifier is deleted.

C-3. The dependencies of the open questions. `plans/mvp/MVP_PLAN.md` says that Q-9 does not depend on Q-1, while `plans/api_contract/API_CONTRACT_SHAPE.md`, section Challenging own assumptions and open question 3, says the route response depends on `plans/routing_engine/`. Its Risks counted Q-7 among the questions that depend on no other, while `plans/demo_environment/DEMO_ENVIRONMENT_PRD.md` FR-1 and AC-1 ask the choice of the hosting to say how it carries the routing chosen in `plans/routing_engine/`, and they still counted Q-3, settled as D-6, among the open questions.

C-4. The entry HarmonyOS port and the Huawei submission of `docs/standards/decision_registry.md` lists an ArkTS application embedding the web app as a variant, which `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, section Domain rules, excludes by a decision of the repository owner accepted by the frontend person.

C-5. D-15 (the backend runs as exactly one process) and D-16 (one search from the hosted service after the first deployment) of the plan of `geocoding` never reached `plans/demo_environment/`: step 6 of that plan was skipped (O-1 of its review), and no document of `plans/demo_environment/` names either constraint.

C-6. The specification, M10, asks every fact to show its reliability status, while M4 defines the statuses of a user fact only; an OpenStreetMap fact only prevails or becomes outdated. M4 makes an OpenStreetMap fact outdated once denials reach the sum of 2, whatever its confirmations, while `plans/fact_schema/FACT_SCHEMA_PRD.md` FR-8 states both that rule and an order of statuses in which denials also have to outweigh the confirmations.

C-7. The specification, M2, makes routes avoid the geozones whose type is in the profile, and scenario 7 of `plans/mvp/MVP_SHAPE.md` avoids an unverified one, but nothing says what happens with a disputed or an outdated geozone.

C-8. `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md`, section Challenging own assumptions, records that one person can vote on one fact once without an account and once logged in, "to be raised with the user"; it was never raised.

C-9. Product rules approved by the user that live only in a PRD or a plan, not in the specification: the 50 m of amenities near the route (`plans/mvp/MVP_PRD.md`, Domain rules), D-21 of `osm_data_source`, the rules of `plans/fact_schema/` on votes, statuses, flags, hiding, geozone radii and pseudonyms, the behavior of the address search of `geocoding`, and the rule of `frontend_stack` that the browser talks only to the server of the project.

C-10. Stale lines: the item Q-10 of `plans/mvp/MVP_PLAN.md` still names Q-2 instead of D-4 and lists the segment states among what is stored, which `plans/fact_schema/FACT_SCHEMA_PRD.md` FR-5 decided against; `plans/mvp/MVP_PRD.md` calls the technology stack open and the district of the Tauron Arena unchecked, which `plans/mvp/MVP_PLAN.md` D-1 and F-2 of the plan of `geocoding` settled; `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` points to an open question 3 of `plans/demo_environment/` that was answered when its shape was closed; `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md` says the frontend is not decided and that `plans/mvp/MVP_PLAN.md` decides the start of the service in Q-10 instead of Q-11; `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, F-4, F-8 and Q-1, still considers a frontend rendered on the server; `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` doubts that the routing can be decided before the source of the OpenStreetMap data, which is decided; `plans/api_contract/API_CONTRACT_SHAPE.md` names neither `plans/fact_schema/` among its dependencies nor its PRD in its current state; the review of `geocoding` carries the state line "implementation in progress" under a final ready verdict.

C-11. `plans/fact_schema/FACT_SCHEMA_PRD.md` AC-3 does not exercise the window of k persons: counting every latest vote gives the same outdated on 10 October, and the fact is outdated already on 9 October.

C-12. No document says explicitly which results of the tag mapping are OpenStreetMap facts that can be voted on. The scenarios of `plans/osm_data_source/OSM_DATA_SOURCE_SHAPE.md` imply that only a barrier or an amenity the tag rules make present is such a fact, while an absent or unknown item is an attribute of the way.

C-13. `plans/local_database/LOCAL_DATABASE_PRD.md` FR-4, the consequence for the hosted database, had not reached the task `DEPLOYMENT` yet.

C-14. `geocoding`, `osm_data_source`, `osm_barrier_mapping` and `frontend_stack` carry a final ready verdict for the whole initiative and still lie in `plans/`.

C-15. `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` lists F-34 and F-35 between F-25 and F-26. The plan is closed and is a contract, so the order stays.

### Decisions of the user

The agent asked the questions in Polish in two rounds on 2026-10-03, after message 2 of the seed; each answer below is the option the user chose, the recommended one where not stated otherwise.

U-1 (C-6). An OpenStreetMap fact has the same four statuses as a user fact, derived from its votes by the same rules, so an OpenStreetMap fact without votes is unverified. The status says how far people confirmed the fact; whether the fact counts on the route still follows the rules of the source, so an OpenStreetMap fact prevails until it is outdated. Against an OpenStreetMap fact confirmed by its source until denied, and against a fifth status for OpenStreetMap data without votes.

U-2 (C-6). An OpenStreetMap fact becomes outdated by the same rule as a user fact: the denials reach at least 2 and outweigh the confirmations. Against the wording of version 3, under which denials of 2 are enough whatever the confirmations.

U-3 (C-7). Routes avoid the geozones whose type is in the profile when they are unverified, confirmed or disputed, and do not avoid outdated or hidden ones; scenario 7 of `plans/mvp/MVP_SHAPE.md` stands. Against treating a disputed geozone like a point report, and against avoiding only confirmed geozones.

U-4 (C-8). One person voting on one fact once without an account and once logged in is accepted as a risk, named in the presentation next to the person with two accounts. Against computing the hashed identifier for logged-in votes too, which would tie an account to the IP address and the browser characteristics.

U-5 (C-3). The contract of the programming interface does not depend on the routing engine: the route response describes the data of the product - the segments with their geometry and states, the list, the alternative and the messages - and the engine adapts to it. Given by the user answering for the backend person, who owns `plans/api_contract/`. Against waiting with the route part of the contract for `plans/routing_engine/`.

U-6 (C-9). Version 4 of the specification takes, besides the rules that contradict version 3 (C-1, C-2, U-1 - U-3), the 50 m of amenities near the route, the behavior of the address search and the rule that the browser talks only to the server of the project. The privacy rules of the address search were offered and not chosen, so they stay in the PRD and the plan of `geocoding`.

U-7 (C-11). AC-3 of `plans/fact_schema/FACT_SCHEMA_PRD.md` stays as it is; the window is checked by the tests of the plan of `fact_schema`. Not the recommended option, which added a scenario where the window changes the status.

U-8 (C-14). All four initiatives move to `plans_finished/`, `frontend_stack` included; the branch `origin/js/frontend-shape`, whose single commit is an older version of `FRONTEND_STACK_SHAPE.md` already merged into the current one, counts as absorbed and is for the user to delete. Not the recommended option, which kept `frontend_stack` in `plans/` until that branch is settled.

U-9 (C-12). Only the barriers and amenities the tag rules make present are facts from OpenStreetMap that get votes; an absent or unknown item is an attribute of the way. Proposed by the agent in the draft of version 4 and accepted by the user when approving it, against the offered option of approving version 4 without this rule and leaving it to the plan of `plans/fact_schema/`.

U-10. Three rules decided by the user in the shape interview of `plans/routing_engine/` (questions 2, 5 and 6 there) enter version 4 by the decision of question 7 there, relayed by the session of that initiative: nothing of a route request leaves the project, the pedestrian network takes only the ways a pedestrian may use, and the stretch between a chosen point and the network is a segment in the state no data. Together with them, the purpose of the hash in M9 names both uses it has under version 4, after improvement 5 of the review below. Approved by the user on 2026-10-03 after the first approval of version 4.

U-11. The item of Personal data that keeps every part of a route request inside the project also says that the text of an address search is a separate request, which the project hands to an address search service outside it from its own server, without anything that identifies the person. Decided by the user on 2026-10-03 after risk 1 of the second pass of the review below, against only narrowing the wording and against leaving it, so that the privacy information built from version 4 does not promise more than the address search of `plans_finished/geocoding/` keeps. This brings into version 4 the part of the privacy rules of the address search that U-6 had left out.

## Fixes of 2026-10-03

### Parallel work on the same files

At 19:33, after the questions, `git status` showed a session implementing `plans/local_database/` on the same tree: `LOCAL_DATABASE_PLAN.md` and `LOCAL_DATABASE_REVIEW.md` were new, and `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md` and `plans/demo_environment/DEPLOYMENT_SHAPE.md` were changed between 19:30 and 19:32. Its review recorded the implementation as finished, without a review verdict yet. Its changes settle C-13 and the part of C-3 about Q-3. Under `docs/standards/standard_agentic_workflow.md` ch. 4.7, the files of that session and the archiving of U-8, which rewrites references in them, wait until that session is wrapped up; the other fixes go first.

### What was done

- C-3, C-8, C-10: `plans/account_sessions/ACCOUNT_SESSIONS_SHAPE.md` - the pointer to the answered question of `plans/demo_environment/` replaced by its answer, an item with the decisions of `plans/fact_schema/` on accounts and votes, functional requirement 3 on the vote limit, the double vote recorded as raised and accepted (U-4), and `plans/fact_schema/` named in Out of scope.
- C-2, C-3, C-10: `plans/api_contract/API_CONTRACT_SHAPE.md` - `plans/fact_schema/` among the dependencies, an item with what the contract exposes from its PRD, an item with U-1, U-2 and U-5, functional requirement 4 on the vote limit and the window, the assumption on routing marked as decided otherwise, and open question 3 narrowed to `plans/account_sessions/`.
- C-10: `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` - items with FR-5 and FR-11 of the PRD of `plans/fact_schema/`, with D-7 of the MVP plan, and with U-2, U-3 and U-5; the doubt about the source of the OpenStreetMap data marked as settled; a note pointing to the memory entry on personal data in requests to outside services.
- C-5, C-10: `plans/demo_environment/DEMO_ENVIRONMENT_SHAPE.md` - the state of the routing engine and the frontend, Q-11 in place of Q-10 with the reason, and the item of step 6 of the plan of `geocoding`. `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` - F-4, F-8, the first risk and Q-1 brought to the decided frontend and to D-15 and D-16 of `geocoding`, edited in place so that no line moves, because the review of `local_database` cites its lines 27 - 31. `plans/demo_environment/DEPLOYMENT_SHAPE.md` - an item with D-15 and D-16 of `geocoding` after the item of `local_database`.
- C-3, C-10: `plans/mvp/MVP_PLAN.md` - the Risks item on dependencies (Q-7 depends on Q-1 unless the server carries every variant, the second critical path, the former Q-2 as D-4), Q-9 with U-5, Q-10 with the state of `plans/fact_schema/`, the way states in place of the segment states and D-6 in place of Q-3, the Goal and the Q-10 caveats with version 4, and this review among the Supplementary files. The D-7 of `local_database`, its removal of Q-4 and its Risks sentence were kept and only extended.
- C-10: `plans/mvp/MVP_PRD.md` - Dependencies on the technology stack and the target environment, and the note on the district of the Tauron Arena.
- C-10: `plans/fact_schema/FACT_SCHEMA_SHAPE.md` and `plans/fact_schema/FACT_SCHEMA_PRD.md` - the four lines that still waited for Q-4 (R-2 of the review of `local_database`) now point to D-7 of the MVP plan.
- C-4: `docs/standards/decision_registry.md` - the embedding variant removed from the entry HarmonyOS port and the Huawei submission with the reason, the state of every initiative added to Technical directions of the MVP plan, and the entry Target environment for the demo brought to D-2 of the plan of `plans/demo_environment/`.
- C-14, U-8: `geocoding`, `osm_data_source`, `osm_barrier_mapping`, `frontend_stack` and, at the request of the session of `local_database` relaying its user's decision recorded in `LOCAL_DATABASE_REVIEW.md`, section Archive, `local_database` moved to `plans_finished/`. Checks of ch. 4.6: no target existed, no source had uncommitted changes besides the files of `local_database`, whose checksums matched those its session handed over, no links; the 25 files had identical SHA-256 sums before and after the move. The reviews of the first four got an archiving entry, and the state lines of `geocoding`, `osm_data_source` and `frontend_stack` were brought in line with it. A script rewrote 411 editable references in 32 files from `plans/<name>/` to `plans_finished/<name>/`: `docs/`, the shapes, PRDs and plans of every initiative, `PRODUCT.md` and `.impeccable/briefs/route-result.md`. Seeds, earlier review entries and `agent_docs/memory/` keep the old paths as historical records.
- C-1, C-2, C-6, C-7, C-9, C-12, U-1 - U-4, U-6: `docs/product/specification.md` version 4, approved by the user on 2026-10-03 after being shown the changes section by section: M2 with the geozones on the route and the subsection Address search, M4 with the statuses of every fact, the facts from OpenStreetMap as present items only, the vote limit, the window, the order of statuses, the weight after deletion and the outdating of OpenStreetMap facts, M5 with the closed list of radii, M8 with the 50 m, M9 with pseudonyms, the vote limit and the accepted double vote, M11 with flags, hiding and restoring, Personal data with the rule that the browser talks only to the server of the project, and the Decision provenance entry. The target schema `docs/product/schema.md` is not part of it: `plans/fact_schema/` still writes it.
- Version 4 carried into the documents that follow it: `plans/mvp/MVP_PRD.md` (Scope, FR-2, FR-6, FR-7, FR-14, AC-6 and the Domain rules, marked as changed after the gate), `plans/fact_schema/FACT_SCHEMA_PRD.md` (FR-8 with U-2, marked as changed after the gate, and its Dependencies), `plans/fact_schema/FACT_SCHEMA_SHAPE.md` (an item in Current state), `plans/mvp/MVP_PLAN.md` and `PRODUCT.md` (the version of the specification, the vote limit and the flags).
- Not changed: C-11 by U-7, and C-15, because a closed plan is a contract. `plans/mvp/MVP_SHAPE.md` stays the record of its interview, as `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-4 decided.

### Movement of `HEAD`

At 19:42 the user committed `feee392`, which took in the work of this session up to the rewrite of the references. The fixes after it are uncommitted. The state of the tree was read again after the commit, and nothing of the commit had to be redone.

### Review of 2026-10-03

The review by the `dod-reviewer` agent covered the whole initiative: version 4 against the decisions it cites, the PRDs that follow it, the scenario runs quoted in acceptance criteria, the archive moves under ch. 4.6, the dependencies in `plans/mvp/MVP_PLAN.md`, formatting and the repository rules. `npx --no-install prettier --check` passed on 18 changed files; `pytest tests/architecture` gave 110 passed and 4 failed, the four failures on the files of the impeccable skill that existed before this initiative, and the prose scan found no violation in a file this initiative changed. The scenario runs of `plans/mvp/MVP_SHAPE.md` 3, 4 and 5, of `plans/fact_schema/FACT_SCHEMA_SHAPE.md` 1 - 3 and of `plans_finished/osm_data_source/OSM_DATA_SOURCE_SHAPE.md` 1 - 3 keep their stated results under version 4.

First verdict: not ready, for the whole initiative.

- B-1. `plans/mvp/MVP_PRD.md` FR-13 still gave the identifier of a vote without an account the purpose "to allow one vote per fact". Fixed: it now tells one person without an account from another for the vote limit and the latest votes of five persons, the vote keeping its weight, and FR-13 is among the requirements marked as changed after the gate.
- R-1. `plans/mvp/MVP_PRD.md`, section Domain rules, named the rules of `plans/mvp/MVP_SHAPE.md` next to version 4, while that shape keeps rules version 4 replaced. Fixed: the section says the specification prevails where the two differ.
- R-2. No decision recorded the acceptance of C-12. Fixed: U-9.
- R-3. `plans/mvp/MVP_PLAN.md`, section Risks, said Q-6 depends on no other open question, while it takes the accounts from Q-10. Fixed: Q-6 takes the rules of accounts from the confirmed PRD of Q-10 and their stored form from its plan.
- I-1. M9 of the specification named only the vote limit as the purpose of the hash, while M4 also uses it to tell the latest votes of five persons apart. Fixed in version 4 with the approval of U-10.
- I-2. The findings above use the paths from before the move. Fixed: a note at the head of section Findings.
- I-3. The state line of `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_REVIEW.md` did not mention the move. Fixed.

While these fixes were made, the session of `plans/routing_engine/` relayed the decision of question 7 of its interview, U-10, and version 4 took its three rules after the user approved them. At 19:51 the user committed `fff8e88`, which took in the work up to the first approval of version 4 and its follow-up changes; the fixes of this review and U-10 are uncommitted.

Second pass of the same review, after the fixes above and U-10: no blocker, every earlier finding fixed, the three rules of U-10 stated as decided in `plans/routing_engine/`, and the items of this initiative in the shapes and in `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, which the first pass could not read in full, consistent. Verdict: ready after minor fixes, for the whole initiative.

- R-4. Personal data in version 4 promised that nothing of a route request leaves the project, the start and the destination included, while the address search hands the typed text to an outside service. Fixed by U-11.
- R-5. `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, F-8 and Q-1, still counted an external Valhalla instance among the variants and the routing engine as being in its interview. Fixed in place, without moving a line: F-8 states the closed interview and the exclusion of an engine outside the project by version 4, M2, and Q-1 no longer lists the external instance.
- R-6. An item this initiative wrote in `plans/routing_engine/ROUTING_ENGINE_SHAPE.md` says an OpenStreetMap fact stops counting on the route "only" when it is outdated, leaving out the contradicting report that replaces it at the sum of 2. That shape is being edited by the session of `plans/routing_engine/`, so the fix with its wording was handed to that session on 2026-10-03, under ch. 4.7. That session applied it the same day, with a pointer to M4 of version 4.
- I-4. A missing comma in the state line of the specification. Fixed.
- I-5. M7 defines no data apart from the default of no stairs, which belongs to a way, and the stretch between a chosen point and the network is not a way, so version 4 does not say whether stairs count as unknown on it. This is product behavior for the user; it was handed to the session of `plans/routing_engine/`, which owns the rule and puts the question to the user in phase B of its plan, not decided here.

After these fixes `npx --no-install prettier --check` passed on the changed files under `docs/` and `plans/`, and `pytest tests/architecture` gave 110 passed and 4 failed, the same four failures on the files of the impeccable skill.

Final verdict: ready, for the whole initiative `plans/consistency_check/`. I-5 stays with the session of `plans/routing_engine/`, and the commit of the uncommitted changes stays with a human.

## Archiving of 2026-10-03

The final ready verdict covers the whole initiative, so the session that ran it moved `plans/consistency_check/` to `plans_finished/` the same day under `docs/standards/standard_agentic_workflow.md` ch. 4.6 and rewrote the editable references to it. The references in `plans/routing_engine/ROUTING_ENGINE_SHAPE.md`, `ROUTING_ENGINE_PRD.md` and the plan that session is writing were left to the session of `plans/routing_engine/`, which edits those files through phase B and agreed to rewrite them itself.
