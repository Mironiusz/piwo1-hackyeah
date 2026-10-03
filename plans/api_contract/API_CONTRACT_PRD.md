# PRD: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03

## Business goal

Agree on one programming interface that lets the Web client and a possible HarmonyOS client use the same MVP data and behavior, while the frontend and backend are built in parallel. The interface and its working operations must support the mandatory MVP demo in Kraków by 11:00 on 4 October 2026.

## Problem and its consequences

The frontend and backend are separate work packages, but there is no agreed interface between them. Without a shared contract for requests, responses and errors, the teams can build incompatible behavior, delay integration and leave required MVP scenarios unavailable in the demo. A contract that exposes incomplete accessibility information as certainty, or reveals private profile and contribution details, could also mislead or harm the people the app serves.

## Scope

- Define the requests, responses and failure outcomes needed for all mandatory MVP features that cross the client and service boundary.
- Implement the service operations required by that contract after the domain model, database schema, backend architecture and anonymous vote identifier are settled in the MVP plan.
- Make the same contract usable by Web and HarmonyOS clients from the start. The clients and service may evolve through coordinated changes; independently updated client backward compatibility is not required.
- Return stable codes for client translation by default. Return localized text only where a feature requires it.
- Include address search through the service, with its input and result behavior described in Domain rules.

## Out of scope

- Choosing or implementing the domain model, database schema, backend architecture, worker behavior or anonymous vote identifier; these are handled in the MVP plan.
- Choosing the routing algorithm, session and actor resolution, frontend technology, OpenStreetMap import, map data mapping, local database, demo environment or other decisions assigned to their own initiatives.
- Building or submitting a native HarmonyOS client. The interface is prepared for that client, while whether to build or submit it remains a separate decision.
- Backward compatibility for clients released independently from the service, since the clients and service are developed and released in coordination.
- Optional MVP features and behavior outside the product specification.

## Functional requirements

FR-1. Route requests carry the selected start and destination and the current barrier and amenity preferences. The preferences are not linked to an account.

FR-2. Route results communicate route segments and their states, missing accessibility attributes, barriers matching the profile, additional barriers, relevant amenities, any proposed alternative and its reason, and when no route without barriers exists. A routing service failure is distinguishable from a valid route result and never produces a guessed route.

FR-3. A report flow returns existing facts of the same type within about 15 m, including OpenStreetMap facts, for the user to compare. A matching fact can be confirmed. A new report is saved only after the user approves its summary.

FR-4. A person with or without an account can read visible content, report facts, confirm facts and deny facts. One person can vote once per fact. The service supports creation and voting on geozones.

FR-5. The service communicates the date of the OpenStreetMap copy in use and exposes each fact's source, date and status. Sample facts are marked as sample data wherever presented.

FR-6. The service supports account creation, login, logout and deletion, and supports contributions without an account. Only logged-in people can flag content. Moderators can view flagged reports and geozones and hide them; hidden content is absent from ordinary lists and details.

FR-7. The service supports the app's Polish and English clients without losing a planned route when the client changes language.

FR-8. The contract specifies the request and response behavior, including errors, for every operation required by FR-1 through FR-7. Responses use stable codes for client translation by default and do not expose exception details, query fragments, database object names or connection strings.

## Acceptance criteria

AC-1. Both clients can request a route with a start, destination and preference set, and receive the same route meaning, segment states, missing attributes, grouped findings and alternative-route information. Profile preferences are not tied to an account, and a current location is not retained after the route request.

AC-2. When routing is unavailable, both clients receive a result distinct from a valid route and can show that no route can be planned at that time. No route is invented.

AC-3. Before a new fact is saved, the client can show same-type facts within about 15 m, including OpenStreetMap facts. Confirming a matching fact records a confirmation; creating a new fact requires approval of its summary. No report is merged automatically or saved before approval.

AC-4. Anonymous and logged-in people can read visible facts, report and vote. A second vote by the same person on the same fact is refused. Only logged-in people can flag content. A moderator can see flagged content and hide it, after which it is absent from ordinary lists and details.

AC-5. Route and fact results provide the source, date and status needed for users to judge the information. They do not disclose a contribution's author, whether its author was logged in, or contribution weights. Sample data remains identifiable as such.

AC-6. Address search accepts search text in a POST request body, returns matches with a label and coordinates, returns an empty result when there are no matches, and distinguishes that result from search unavailability. Text longer than 200 characters as received, or empty after normalization, is rejected as caller input.

AC-7. Both clients can translate stable response codes into the selected interface language. Switching language does not discard a planned route.

AC-8. Request logs contain only the operation name, outcome or status, duration and request identifier. They contain no request or response body, headers, pseudonym, account identifier, location, preferences, IP address or browser characteristics. A failed response contains no internal exception or infrastructure details.

## Domain rules

- A current location is sent only with a route request. It is not stored, logged or linked to an account.
- Profile preferences travel with a route request but are not linked to an account or retained as account data.
- Nothing identifying the author of a report, vote or geozone, including whether the author was logged in, is visible to other users.
- Anonymous and logged-in people have the same read access to visible content, and both may report and vote. Only logged-in people may flag content; moderators additionally see flagged content and may hide it.
- Stable codes are the default for client-facing content. Localized text is returned only when needed to implement a feature.
- Address search text is sent only in a POST request body, never in a URL. A search result contains a list of matches, each with a label, latitude and longitude. No matches produce an empty list; unavailable search is a distinct outcome. Input longer than 200 characters as received, or empty after normalization, is invalid.
- Request logs are limited to operation name, outcome or status, duration and request identifier. They exclude request and response bodies, headers, pseudonym, account identifier, location, preferences, IP address and browser characteristics. A separate failure diagnostic may contain the traceback needed for diagnosis.
- A response body does not contain exception details, query fragments, database object names or connection strings.

## Dependencies and impact on other modules

- Endpoint implementation waits for Q-10 in the MVP plan, which settles the domain model, database schema, backend architecture with the worker and anonymous vote identifier.
- Contract details that depend on route composition or actor resolution are coordinated with the routing engine and account sessions initiatives.
- The frontend initiative is the first consumer and is consulted on the contract. The geocoding initiative has already decided that address search goes through the service.
- The interface enables parallel frontend and backend work and is intended to be shared by Web and a possible HarmonyOS client.

## Risks and notes

- The repository does not estimate the time needed to settle Q-1 through Q-10 and implement the service operations, so feasibility before the Kraków demo deadline cannot yet be established.
- Route composition and actor resolution are still being decided in their respective initiatives. Contract details depending on them must be coordinated with those owners rather than assumed.
- Route requests include preferences that can practically reveal health information, so the contract and its handling must preserve the privacy rules above.
