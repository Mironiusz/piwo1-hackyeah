# PRD: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03

## Business goal

Agree on one programming interface that lets the Web client and a possible HarmonyOS client use the same MVP data and behavior, so that the frontend and the backend can be built in parallel against it. The interface must cover the mandatory MVP demo in Kraków by 11:00 on 4 October 2026.

## Problem and its consequences

The frontend and backend are separate work packages, but there is no agreed interface between them. Without a shared contract for requests, responses and errors, the teams can build incompatible behavior, delay integration and leave required MVP scenarios unavailable in the demo. A contract that exposes incomplete accessibility information as certainty, or reveals private profile and contribution details, could also mislead or harm the people the app serves.

## Scope

- Define the requests, responses and failure outcomes needed for all mandatory MVP features that cross the client and service boundary.
- Make the same contract usable by Web and HarmonyOS clients from the start. The clients and service may evolve through coordinated changes; independently updated client backward compatibility is not required.
- Return stable codes for client translation by default. Return localized text only where a feature requires it.
- Include address search through the service, with its input and result behavior described in Domain rules.

## Out of scope

- Implementing the service operations of the contract, and choosing the backend architecture with the worker. The user decided on 2026-10-03, in phase B, that the backend architecture of Q-11 of the MVP plan goes to a separate initiative set up later and that the implementation of the operations goes with it, so the contract does not wait for either.
- Choosing or implementing the domain model, database schema, worker behavior or anonymous vote identifier; these are handled in their own initiatives.
- Choosing the routing algorithm, session and actor resolution, frontend technology, OpenStreetMap import, map data mapping, local database, demo environment or other decisions assigned to their own initiatives.
- Building or submitting a native HarmonyOS client. The interface is prepared for that client, while whether to build or submit it remains a separate decision.
- Backward compatibility for clients released independently from the service, since the clients and service are developed and released in coordination.
- Optional MVP features and behavior outside the product specification.

## Functional requirements

FR-1. Route requests carry the selected start and destination and the current barrier and amenity preferences. A route request carries no identity of an account, so the preferences are never linked to one.

FR-2. Route results communicate route segments and their states, missing accessibility attributes, barriers matching the profile, additional barriers, relevant amenities, any proposed alternative and its reason, and when no route without barriers exists. A routing service failure is distinguishable from a valid route result and never produces a guessed route.

FR-3. A report flow returns existing facts of the same type within about 15 m, including OpenStreetMap facts, for the user to compare. A matching fact can be confirmed. A new report is saved only after the user approves its summary. A repeated submission of the same approved report or geozone, for example after a lost response, does not create a second fact.

FR-4. A person with or without an account can read visible content, report facts, confirm facts and deny facts. A person votes on the same fact again only once a day has passed since their previous vote on it, and only the latest vote of a person counts (`docs/product/specification.md` M4). The service supports creation and voting on geozones. Visible content in an area of the map includes outdated facts, except a fact outdated because it was removed from OpenStreetMap, and never includes hidden content.

FR-5. The service communicates the date of the OpenStreetMap copy in use and exposes each fact's source, date and status. Sample facts are marked as sample data wherever presented.

FR-6. The service supports account creation, login, logout and deletion, and supports contributions without an account. A pseudonym has 3 to 30 characters after leading and trailing spaces are removed, and no control characters. A request made with an expired session, or with the session of a deleted account, is refused with its own outcome and is never handled as a contribution without an account. Anyone can flag content (`docs/product/specification.md` M11). Moderators can view flagged reports and geozones and hide them; hidden content is absent from ordinary lists and details.

FR-7. The service supports the app's Polish and English clients without losing a planned route when the client changes language.

FR-8. The contract specifies the request and response behavior, including errors, for every operation required by FR-1 through FR-7. Responses use stable codes for client translation by default and do not expose exception details, query fragments, database object names or connection strings.

## Acceptance criteria

AC-1. The contract defines one route request with a start, a destination and a preference set, and one route response with the route meaning, segment states, missing attributes, grouped findings and alternative-route information that both clients read the same way. The route request carries no identity of an account, and the contract states that a current location is not retained after the request.

AC-2. The contract defines a routing-unavailable outcome distinct from every route result, which carries no route.

AC-3. The contract defines a check that returns same-type facts within about 15 m, OpenStreetMap facts included, a confirmation of a matching fact, and a save of a new fact sent only after the summary is approved. No operation merges reports. A repeated save of the same submission returns the fact of the first save instead of creating a second one.

AC-4. The contract lets anonymous and logged-in people read visible facts, report and vote, and defines the refusal of a second vote by the same person on the same fact within a day of the first. Anyone can flag content. Moderator operations list flagged content and hide and restore it, hidden content is absent from every other operation, and a moderator operation is refused without the current moderator role. A request with an expired session gets its own refusal.

AC-5. Every fact in every response carries the source, date and status needed for users to judge the information, and the sample data mark. No response carries a contribution's author, whether its author was logged in, or contribution weights.

AC-6. The contract defines address search that accepts search text in a POST request body, returns matches with a label and coordinates, returns an empty result when there are no matches, and distinguishes that result from search unavailability. Text longer than 200 characters as received, or empty after normalization, is rejected as caller input. An address search request carries no identity of an account.

AC-7. Every value from a closed list in every response is a stable code that a client translates into the selected interface language, and the route response carries no localized text, so a client switches language without requesting the route again.

AC-8. The contract states that request logs contain only the operation name, outcome or status, duration and request identifier, and no request or response body, headers, pseudonym, account identifier, location, preferences, IP address or browser characteristics, and that a failed response contains no internal exception or infrastructure details.

## Domain rules

- A current location is sent only with a route request. It is not stored, logged or linked to an account.
- Profile preferences travel with a route request but are not linked to an account or retained as account data. A route request and an address search request carry no identity of an account, so neither of them renews a session.
- Nothing identifying the author of a report, vote or geozone, including whether the author was logged in, is visible to other users.
- Anonymous and logged-in people have the same read access to visible content, and both may report and vote. Anyone may flag content; moderators additionally see flagged content and may hide it.
- Visible content in an area of the map includes outdated facts, except a fact outdated because it was removed from OpenStreetMap, which disappears from the map (`docs/product/specification.md` M4). Hidden content is never visible outside the moderator view.
- A pseudonym has 3 to 30 characters after leading and trailing spaces are removed, and contains no control characters.
- A request made with an expired session, or with the session of a deleted account, is refused with its own outcome, so that nobody contributes without an account and with the lower weight while believing they are logged in.
- Stable codes are the default for client-facing content. Localized text is returned only when needed to implement a feature.
- Address search text is sent only in a POST request body, never in a URL. A search result contains a list of matches, each with a label, latitude and longitude. No matches produce an empty list; unavailable search is a distinct outcome. Input longer than 200 characters as received, or empty after normalization, is invalid.
- Request logs are limited to operation name, outcome or status, duration and request identifier. They exclude request and response bodies, headers, pseudonym, account identifier, location, preferences, IP address and browser characteristics. A separate failure diagnostic may contain the traceback needed for diagnosis.
- A response body does not contain exception details, query fragments, database object names or connection strings.

## Dependencies and impact on other modules

- The implementation of the operations follows the backend architecture, which the user moved on 2026-10-03 from Q-11 of the MVP plan to a separate initiative set up later; this contract is an input of that initiative.
- The resources, statuses and closed lists the contract exposes follow the target schema of `plans_finished/fact_schema/`, part of `docs/product/specification.md` since version 6. A repeated save that returns the first fact needs the stored data to recognize the repetition, which that schema does not hold yet; how it is stored is for that initiative to decide.
- Actor resolution follows `plans_finished/account_sessions/`, settled before this contract (U-3 of `plans_finished/dependency_check/`, `plans/mvp/MVP_PLAN.md` D-8). The route response describes the data of the product, and the routing engine adapts to it (U-5 of `plans_finished/consistency_check/`).
- The frontend initiative is the first consumer and is consulted on the contract. The user approves the contract in place of the frontend person, whose confirmation is still to be obtained. The geocoding initiative has already decided that address search goes through the service.
- The interface enables parallel frontend and backend work and is intended to be shared by Web and a possible HarmonyOS client.

## Risks and notes

- The contract is ready before any operation is implemented. The time the implementation needs once the backend architecture is decided is not estimated, so whether it fits before the Kraków demo deadline cannot yet be established.
- Actor resolution is decided in `plans_finished/account_sessions/` and the route response follows the data of the product (Dependencies); a need of the contract beyond them is raised with the owner of that initiative rather than assumed.
- A change of the target schema is a new version of the specification, and it can change the contract too.
- The four rules of FR-1, FR-4 and FR-6 on a route request without an account, outdated facts in an area of the map, the pseudonym and an expired session were decided by the user on 2026-10-03 in phase B of this initiative, as product behavior the specification does not describe.
- Changed after the gate on 2026-10-03, when this initiative was merged into `rm/requirements-preparation`: FR-4, FR-6, AC-4, the flag item of Domain rules, the Dependencies and the item above follow the user's decision that, where this initiative contradicted them, `docs/product/specification.md` version 4, M4 and M11, U-3 of `plans_finished/dependency_check/` and U-5 of `plans_finished/consistency_check/` stay in force.
- Changed after the gate on 2026-10-03, in phase B, at the user's decisions recorded in `API_CONTRACT_PLAN.md`: the implementation of the operations left Scope for Out of scope together with the backend architecture; FR-1, FR-3, FR-4 and FR-6 and the Domain rules gained the rules above and the repeated save; the acceptance criteria check the contract instead of a running service; the Dependencies and the first and third items of this section changed with them.
- Route requests include preferences that can practically reveal health information, so the contract and its handling must preserve the privacy rules above.
