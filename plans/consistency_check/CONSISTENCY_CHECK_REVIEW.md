# Review: Consistency check of all initiatives and of the MVP plan, and its fixes

Document state: 2026-10-03, fixes in progress

## Check of 2026-10-03

### Scope

The agent read `docs/product/specification.md` version 3, `docs/standards/decision_registry.md`, `agent_docs/memory/`, and the artifacts of every initiative in `plans/`: `mvp`, `geocoding`, `osm_data_source`, `osm_barrier_mapping`, `frontend_stack`, `fact_schema`, `local_database`, `demo_environment` with its task `DEPLOYMENT`, `api_contract`, `account_sessions` and `routing_engine`. Seeds were read only for `mvp` and `fact_schema`, because a seed is a verbatim record and decides nothing; the PRDs of the closed initiatives were checked through their plans and reviews. The initiative has no shape, PRD or plan: the request was a check and its fixes, and this file records both.

### Findings

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

## Fixes of 2026-10-03

### Parallel work on the same files

At 19:33, after the questions, `git status` showed a session implementing `plans/local_database/` on the same tree: `LOCAL_DATABASE_PLAN.md` and `LOCAL_DATABASE_REVIEW.md` were new, and `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md` and `plans/demo_environment/DEPLOYMENT_SHAPE.md` were changed between 19:30 and 19:32. Its review recorded the implementation as finished, without a review verdict yet. Its changes settle C-13 and the part of C-3 about Q-3. Under `docs/standards/standard_agentic_workflow.md` ch. 4.7, the files of that session and the archiving of U-8, which rewrites references in them, wait until that session is wrapped up; the other fixes go first.

### What was done
