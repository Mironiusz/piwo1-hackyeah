# PRD: Choice of the routing engine for the MVP

Document state: 2026-10-03

## Business goal

By 11:00 on 4 October 2026 the MVP of `plans/mvp/` plans walking routes in Kraków matched to the barrier preferences of a person. The route is the core of the main scenario (`docs/product/specification.md` version 4, M2, M7, M8): it turns open data and reports into something a person can act on before leaving home. It also carries two of the things the Kraków demo has to show (M10): a contradiction between OpenStreetMap and a user report, and a plain message with no guessed route when routing does not answer.

This task makes the decision that the route work package of `plans/mvp/` needs, so that the package builds the routing without making a choice of its own. The package builds it.

## Problem and its consequences

How the MVP computes routes was not decided in phase B of `plans/mvp/`; the user handed the decision to the backend person of the team. Ordinary route engines do not apply the rules of the specification on their own: they do not avoid only the barriers from the profile, keep an unverified barrier on a red segment next to an alternative, fall back to the route with the fewest barriers, or give every segment one of four states with its missing attributes. As long as the decision is open:

- `plans/mvp/MVP_PLAN.md` cannot be closed, and `plan-implement` cannot start on it: its open question Q-1 waits for this decision, and Q-11, the backend architecture with the worker, depends on Q-1.
- `plans/demo_environment/` cannot tell whether the server of the demo carries the routing (its plan, Q-1), and its deadline of 22:00 on 3 October 2026 for the choice of the hosting moves.
- The import cannot know which ways to process: `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6 applies the tag rule "on the elements of the pedestrian network", and no initiative has said which tags make that network.
- `plans/fact_schema/` leaves open how a route is related to the stretches of way whose facts it keeps.
- The contradiction of M2 has two values nobody set: which stretch of way a point report lies on, and within what distance of an opposite kerb point of OpenStreetMap a kerb report counts as contradicted. Without them, scenario 4 of `plans/mvp/MVP_SHAPE.md`, the contradiction the Kraków demo has to show, has no defined outcome.

## Scope

- The choice of how the MVP computes routes, by software of the project on its own infrastructure, from the copy of OpenStreetMap of `plans_finished/osm_data_source/`, recorded with its reason and the alternatives it was chosen against.
- The OpenStreetMap tag values that make a way part of the pedestrian network, under the rule of the section Domain rules.
- How a route is related to the stretches of way and the points whose facts `plans/fact_schema/` keeps.
- The two values of the contradiction of M2 left by `plans_finished/osm_barrier_mapping/`.
- Recording the decision where people look for it: the MVP plan and the deferred decisions registry.
- Handing over to `plans/demo_environment/` what the chosen engine needs from the server of the demo. Agent decision at C:40, without asking: the plan of that initiative lists the routing variants its server has to carry and waits for this choice (its Q-1), as `plans_finished/local_database/` handed its consequence to the same initiative.

## Out of scope

- Building the routing: the network the engine reads, the cost per profile, the segment states, the alternative route, the route with the fewest barriers, the list and the endpoint. A work package of `plans/mvp/` builds them (`ROUTING_ENGINE_SHAPE.md`, question 1).
- Any routing service outside the project, the public Valhalla instance and the OSRM demo included (`ROUTING_ENGINE_SHAPE.md`, question 2).
- The route part of the contract of the programming interface, which `plans/api_contract/` defines and to which the engine adapts (U-5 of `plans_finished/consistency_check/`).
- Writing the three product rules of `ROUTING_ENGINE_SHAPE.md`, questions 2, 5 and 6, into the specification. `plans_finished/consistency_check/` added them to M2 and to the section Personal data of version 4 on 2026-10-03 at the user's request, and the user approved them (`ROUTING_ENGINE_SHAPE.md`, question 7).
- The tag rule and the thresholds of M6, the segment rules of M7 and the list of M8, which this decision applies as they stand.
- Turn-by-turn navigation and public transport routes (`docs/product/specification.md`, Out of scope).
- The other technical decisions delegated in the same conversation, each with its own initiative: `plans/api_contract/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans/account_sessions/`.

## Functional requirements

FR-1. Choice of the engine. The decision names how the MVP computes a walking route: which software computes it, where it runs within the project, how it reads the pedestrian network from the copy, and how it applies the profile carried by the route request together with the user facts and the geozones valid at the moment of the request. The chosen way:

- makes FR-2, FR-3, FR-4, FR-10, FR-11 and FR-17 of `plans/mvp/MVP_PRD.md` achievable, the alternative route of FR-3 and the route with the fewest barriers of FR-4 included,
- takes the facts, the segment states and the date from the copy in use, and never combines the ways of two copies, or the ways of one copy with the date of another (`ROUTING_ENGINE_SHAPE.md`, scenario 4),
- takes a new vote, report or geozone into account in the next route, without a restart of the service or a new import (`ROUTING_ENGINE_SHAPE.md`, scenario 3),
- keeps everything of the route request inside the project (section Domain rules),
- gives a route across Kraków, with everything FR-2, FR-3, FR-4 and FR-11 of the MVP PRD show after planning, within 5 seconds on the server of the demo.

The decision is recorded with its reason and with the alternatives it was chosen against.

FR-2. The pedestrian network. The decision names the OpenStreetMap tag values that make a way part of the pedestrian network and those that keep it out, under the rule of the section Domain rules, and for each value that keeps ways out, how many ways of the copy of Kraków it removes. The import applies the tag rule of `plans_finished/osm_barrier_mapping/` to exactly these ways, and a route uses only them.

FR-3. Route and stored facts. The decision states how every segment of a route is tied to the stretches of way and the points whose facts `plans/fact_schema/` keeps, so that the state of the segment (M7), its missing attributes and its barriers on the list (M8), the amenities within 50 m of the route (M8) and the contradiction of M2 come from those facts and from the user facts, while the segment itself is never stored (`plans/fact_schema/FACT_SCHEMA_PRD.md` FR-5). It also states how the stretch between a chosen point and the network becomes a segment in the state no data (section Domain rules). The tie uses what `plans/fact_schema/FACT_SCHEMA_PRD.md` FR-5 stores; a need beyond it is raised with the db person, never assumed, as the engine adapts to the route response of `plans/api_contract/` (U-5). Decided by the user on 2026-10-03 in `plans/dependency_check/` (U-2 of its review).

FR-4. Values of the contradiction. The decision names how a point report is assigned to the stretch of way it lies on, a report lying between a sidewalk and a carriageway included, and within what distance of an opposite kerb point of OpenStreetMap a report of a high or a lowered kerb counts as contradicted, each with its reason.

FR-5. The decision recorded. The open question Q-1 of `plans/mvp/MVP_PLAN.md` is closed by a decision entry that points to this initiative and states the constraints for the rest of that plan: which work package builds the routing, what it reads from the import and from the stored facts, and what Q-11 takes from it about where the route is computed. The entry Technical directions of the MVP plan of `docs/standards/decision_registry.md` records that this initiative is decided.

FR-6. Needs of the engine handed over. `plans/demo_environment/` gets, as an input of its open question about the server, what the chosen engine needs from the server of the demo - memory, disk and any service of its own - and what makes it not answer, which the task `DEPLOYMENT` needs to show an unavailable source in the live demo. Nothing is decided there by this task.

## Acceptance criteria

AC-1 (FR-1). The recorded choice names the software, where it runs within the project and how it reads the network from the copy, and says for each of FR-2, FR-3, FR-4, FR-10, FR-11 and FR-17 of the MVP PRD and for scenarios 2 - 6 of `ROUTING_ENGINE_SHAPE.md` how it meets them. It names its reason and the alternatives it was chosen against, among them the three of `ROUTING_ENGINE_SEED.md`, the external one with the reason it is excluded. Every claim about a capability, a licence, memory or time rests on a source checked in phase B: the documentation of the product, its published contents or a run. The time of a route across Kraków is measured on the copy of Kraków on the machine of the agent's session and is under 5 seconds there. The choice names no address, host, account or password.

AC-2 (FR-2). The decision lists the including and the excluding tag values, each excluding value with the number of ways of the copy of Kraków it removes, counted in phase B. Under the list a way tagged `highway=footway` and `access=private` without a permission for pedestrians is outside the network, and a way tagged `highway=residential` without a sidewalk tag is inside it.

AC-3 (FR-3). Applied by hand to scenario 6 of `ROUTING_ENGINE_SHAPE.md`, the decision gives a first segment of 4 m and a last segment of 60 m in the state no data; applied to scenario 9 of `plans/mvp/MVP_SHAPE.md`, it gives segment Y in the state partial data with the incline and the kerbs named as missing.

AC-4 (FR-4). The decision names a rule for the stretch of a point report and a distance in metres for the kerb, each with its reason. Applied by hand to scenario 4 of `plans/mvp/MVP_SHAPE.md`, they make the report of a high kerb at crossing X contradicted by the lowered kerb of OpenStreetMap, so the segment follows OpenStreetMap until the report reaches 2.0.

AC-5 (FR-5). Q-1 is no longer among the open questions of `plans/mvp/MVP_PLAN.md`. A decision entry there points to this initiative and states the constraints of FR-5. The registry entry Technical directions of the MVP plan says that `plans/routing_engine/` is decided.

AC-6 (FR-6). The open question about the server in `plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md` names the chosen engine with what it needs from the server instead of the three variants it lists today, with a pointer to this initiative, and checking the 5 seconds of FR-1 on the server of the demo is listed among the checks after the first deployment. The decisions of that plan are unchanged.

## Domain rules

- The rules of the route, the segment states, the list, the statuses and the contradiction are those of `docs/product/specification.md` version 4, M2, M4, M6, M7 and M8. This task applies them and does not change them.
- A geozone whose type is in the profile is avoided when it is unverified, confirmed or disputed; a fact or a geozone that is outdated or hidden does not change the route (M2).
- Missing information is never presented as a confirmation of accessibility (M10).
- The current location travels only in the route request: it is not stored, not logged and not linked to the account (M2). A route request carries the barrier preferences without linking them to the account (M1).
- Nothing of a route request leaves the project: the current location, the start, the destination and the preferences, and anything derived from them such as a list of places to avoid, are used only by software of the project running on its own infrastructure (M2 and section Personal data, from `ROUTING_ENGINE_SHAPE.md`, question 2).
- A route leads only along ways of the copy that a pedestrian may use according to their OpenStreetMap tags. Ways forbidden to pedestrians, ways not built yet and private ways without a permission for pedestrians are outside the pedestrian network; ways for motor traffic are inside it, as M6 reads their surface and width when they have no sidewalk (M2, from `ROUTING_ENGINE_SHAPE.md`, question 5).
- The stretch between a chosen start or destination and the point where the route joins the pedestrian network is a segment in the state no data, drawn as a straight line, at every length, and the list names its missing attributes (M2, from `ROUTING_ENGINE_SHAPE.md`, question 6).
- A route across Kraków, with everything shown after planning, is ready within 5 seconds on the server of the demo. Decided by the user on 2026-10-03 at the start of this PRD, against 2 seconds and against measuring without a limit.
- The tag values of FR-2 and the values of FR-4 are product behavior a person sees, so they are put to the user in phase B and, once decided, go to the specification. Agent decision at C:40, without asking: it follows from `ROUTING_ENGINE_SHAPE.md`, question 7, under which the product rules of this initiative enter the specification. Because `plans_finished/consistency_check/` was closed before phase B, the user decided on 2026-10-03 in phase B that a step of the plan of this initiative writes them as a new version of the specification, shown to the user for approval.
- Changed after the gate on 2026-10-03: FR-3 and the item of `plans/fact_schema/` under Dependencies and impact on other modules, by U-2 of `plans/dependency_check/`; the item above on how the values reach the specification, by the user in phase B.
- The decision has no deadline of its own; the deadline of 22:00 for the choice of the hosting moves if it comes too late for it (`ROUTING_ENGINE_SHAPE.md`, Smallest meaningful scope).

## Dependencies and impact on other modules

- `plans/mvp/MVP_PLAN.md` gets Q-1 closed (FR-5), and Q-11 can then be decided. The plan stays open while its other questions wait.
- `plans/mvp/MVP_PLAN.md` D-3 makes the backend run as exactly one process, because the cache of the address search lives in its memory. The chosen engine has to work with that.
- `plans_finished/osm_data_source/`: the condition of its D-17 is met, because the engine reads the copy of that initiative. The copy itself does not change.
- `plans_finished/osm_barrier_mapping/`: FR-2 defines the network its D-6 relies on. Its closed plan is not changed; the import work package of `plans/mvp/` applies D-6 to the network of FR-2.
- `plans/fact_schema/`: FR-3 answers what its PRD left to this initiative, within what its FR-5 stores; since U-2 of `plans/dependency_check/` that PRD no longer waits for a check against this initiative.
- `plans/api_contract/`: the route response describes the data of the product, and the engine adapts to it (U-5). The stretch to the network is an ordinary segment in the state no data.
- `plans/demo_environment/` and its task `DEPLOYMENT` receive the needs of FR-6.
- `plans_finished/local_database/`: the local database already carries pgRouting without creating it, so choosing pgRouting needs no change of the local environment (`plans/mvp/MVP_PLAN.md` D-7); another choice leaves it unused.
- `docs/product/specification.md`: version 4 states the three rules of `ROUTING_ENGINE_SHAPE.md`, questions 2, 5 and 6, in M2 and in the section Personal data; the tag values of FR-2 and the values of FR-4 go there after phase B.
- `docs/standards/decision_registry.md`: the entry Technical directions of the MVP plan changes (FR-5).
- `agent_docs/memory/_cross_cutting.md`: the risk note of the entry Personal data in requests to outside services names this initiative as undecided and becomes stale once it is implemented.

## Risks and notes

- The answers behind this PRD were given by the user, who has not stated being the backend person. The ruling of the backend person is still to be confirmed, as in `plans/fact_schema/` and `plans_finished/local_database/`.
- The 5 seconds are measured in phase B on the machine of the agent's session, not on the server of the demo, whose free memory is not known yet (`plans/demo_environment/DEMO_ENVIRONMENT_PLAN.md`, Q-1). A slower server surfaces only after the first deployment, which FR-6 asks to check.
- With no outside service, the only way routing stops answering is the engine of the project failing. Showing an unavailable source in the live demo, which M10 asks for, needs a deliberate way to make it fail, and that is for the task `DEPLOYMENT`.
- Most segments will be partial data for profiles that avoid a steep incline or a narrow passage: of the 151 882 ways of the network measured in `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` F-9, 5 798 carry `incline` and 4 849 carry `width`. On top of that almost every route starts or ends with a short segment in the state no data. That is honest, but the demo has to explain it.
- A destination inside a gated estate gets a route that ends at the nearest public way with a segment in the state no data that can be tens of metres long. That follows from leaving private ways out of the network.
- Ending with the decision alone delays the routing itself to a work package of `plans/mvp/`, which starts only once that plan is closed. The user chose this knowing the cost (`ROUTING_ENGINE_SHAPE.md`, question 1).
