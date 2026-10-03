# PRD: Choice of the address search for the MVP

Document state: 2026-10-03

## Business goal

A user of the MVP gives the start and the destination of a route, and the point of a geozone, by typing an address or the name of a place, not only by finding the point on the map. This is the natural way to say where one goes on a phone, and the practical one for a person using a keyboard or a screen reader, which the Kraków brief requires for the main scenario. The search serves the judging criterion of usefulness and ease of use directly, and the demo at the Tauron Arena starts from it.

The initiative delivers the decision on how the MVP searches, closing `plans/mvp/MVP_PLAN.md` Q-5, so that the MVP plan can be closed and its implementation can start before the deadline at 11:00 on 4 October 2026.

## Problem and its consequences

Without a search, the only way to give a destination is to pan and zoom the map until the place is found. On a phone that is slow, and with a keyboard alone or a screen reader it is close to impossible, which breaks the accessibility requirement of the MVP (`plans/mvp/MVP_PRD.md` FR-16) and the keyboard-only geozone (AC-7 of the same document).

At the same time the text a person searches for says where they are going. A destination such as a hospital can reveal information about health, and the specification already keeps even the current location out of storage and logs (`docs/product/specification.md`, M2). A search built carelessly would hand this text, together with the IP address of the person, to a third party, or leave it in the logs of the project, where it can be tied to a person and a time.

A search that silently takes the first match would send a route to a wrong place without anyone noticing, which is the same kind of harm as a guessed route that the specification forbids (M10).

## Scope

- The behavior of the search of addresses and places used for the start and the destination of a route (`plans/mvp/MVP_PRD.md` FR-2) and for the point of a geozone (FR-8 of the same document).
- The privacy rules of the search: who may learn the typed text, and where it may be kept.
- The technical choice of the service that answers the search and of the way it is connected to the project, made in phase B of this initiative, recorded so that it closes `plans/mvp/MVP_PLAN.md` Q-5.

## Out of scope

- Building the search. The code is written as a work package of `plans/mvp/`, together with the rest of the backend, because the backend architecture is decided there (`plans/mvp/MVP_PLAN.md` Q-11). Decided by the user with the external API person in the shape interview.
- The shape of the search request and response between the frontend and the backend, which is part of `plans_finished/api_contract/`.
- The map tiles and what their source learns about the person, which is part of `plans_finished/frontend_stack/`.
- The wording of the privacy information (`plans/mvp/MVP_PRD.md` FR-20), owned by `plans/mvp/`.
- Suggestions while the user types. Decided against by the user with the external API person in the shape interview.
- Places outside Kraków, because routes work only within Kraków.
- Turning a point chosen on the map into an address. Agent decision at C:40, without asking: neither the specification nor `plans/mvp/MVP_PRD.md` asks for it, and the shape covers only the direction from a typed text to a point; confirmed by the user with the external API person at the gate of this PRD on 2026-10-03.

## Functional requirements

FR-1. Searching by text. The user types a street address, with or without a house number, or the name of a place, for example "Tauron Arena" or "Rynek Główny", and submits it with the Enter key or a search button. Nothing is searched while the user types.

FR-2. Results within Kraków. The search returns only places within Kraków.

FR-3. Picking from a list. The result of a search is always a list for the user to pick from, also when it has a single item. Each item shows the full address, so places with the same name can be told apart. The app never takes a match on its own; the start, the destination or the geozone point is set only when the user picks an item.

FR-4. Accessibility. The search field, the submission, the list and the picking work with a keyboard alone and with a screen reader; the screen reader announces how many results there are. This holds for the start and the destination of a route and for the point of a geozone.

FR-5. Nothing found and search unavailable. When nothing is found in Kraków, the user gets a plain message saying so. When the outside service does not answer, refuses, or cannot be asked without exceeding its limits, the user gets a different plain message saying that the search is unavailable right now. In both cases no point is guessed, and choosing a point on the map stays available. Both messages exist in the two languages of the interface (`plans/mvp/MVP_PRD.md` FR-19).

FR-6. Privacy toward outside services. The typed text may reach a service outside the project only from the server of the project. The browser never sends it to an outside service, and nothing that identifies the person - their IP address, their account - travels with the text to that service.

FR-7. Privacy inside the project. The typed text and the point found for it are never written to a log anywhere in the path of the request - the log of the app, of the HTTP server or of the hosting - nor to the database, and are never linked to an account or to an IP address. The only place they may be kept is a cache in the memory of the server process, keyed by the text alone, without who asked or when, and lost when the process restarts.

FR-8. Repeated searches. A search for a text that was already answered during the life of the server process is answered without asking the outside service again. A failed search is not remembered: the next search for the same text asks the outside service again.

FR-9. Terms of the outside service. The outside service is used within its published terms of use: its request limits are never exceeded, and the identification and the attribution it requires are given. The attribution is visible to the user.

## Acceptance criteria

AC-1 (FR-1, FR-3). Typing "Tauron Arena" in the destination field sends no request to the outside service until the user presses Enter. After Enter, a list with at least one item in Kraków with its full address appears, and the destination stays empty until the user picks an item.

AC-2 (FR-2, FR-5). A search for "Rynek Górny, Wieliczka", a place outside Kraków, ends with the message that nothing was found in Kraków, and no point is set.

AC-3 (FR-3). A search for "Biedronka" shows several items, each with a different full address, and nothing is set until the user picks one. A search with a single match shows a list of one item, and nothing is set until the user picks it.

AC-4 (FR-4). On a phone with a screen reader and with a keyboard alone, a user goes from the destination field to a set destination, and from the search field of the geozone form to a set geozone point, without a pointer; the screen reader announces the number of results.

AC-5 (FR-5). A search for a text that matches nothing shows the nothing found message. With the outside service unreachable, a search shows the search unavailable message, which differs from the nothing found message. In both cases no point is set, choosing a point on the map works, and both messages appear in Polish and in English.

AC-6 (FR-6). During a search, the browser sends the typed text to no host other than the server of the project. The requests the outside service receives carry no IP address of the person and no identifier of an account.

AC-7 (FR-7). After searches for "Szpital Uniwersytecki, Jakubowskiego 2", neither the logs of the app, of the HTTP server and of the hosting, nor the database contain that text or the point found for it. After a restart of the server process nothing about these searches remains.

AC-8 (FR-8). Two searches for the same text in a row cause one request to the outside service. After a search that failed because the outside service did not answer, the next search for the same text causes a new request to it.

AC-9 (FR-9). Searches submitted faster than the limit of the outside service allows never cause more requests than the limit; a search that cannot be answered within the limit ends with the search unavailable message. The attribution required by the outside service is visible in the app.

## Domain rules

The rules are those of the section Domain rules of `plans_finished/geocoding/GEOCODING_SHAPE.md`. In short, for reading the acceptance criteria:

- Routes, and so search results, are only within Kraków.
- The typed text leaves the project only from the server, never with anything that identifies the person.
- The typed text and its point are treated like the current location: never logged, never in the database, never linked to a person; only an in-memory cache keyed by the text alone, lost on restart.
- The user always picks the result; the app never picks on its own, not even a single match.
- The search runs only on submission; nothing is suggested while typing.
- Nothing found and search unavailable are two different plain messages; no point is ever guessed, and the map stays available.

## Dependencies and impact on other modules

- No product code exists, so nothing in the repository is changed indirectly. The decision feeds `plans/mvp/`: it closes `plans/mvp/MVP_PLAN.md` Q-5, and the search becomes a work package of that plan, used by `plans/mvp/MVP_PRD.md` FR-2 and FR-8 and held to FR-16 and FR-19.
- `plans_finished/api_contract/` waits for this initiative to know whether the search goes through the backend: it does, so the search is part of the contract between the frontend and the backend.
- `plans_finished/frontend_stack/` builds the list and the messages; the risk of the map tiles revealing the IP address of the person is recorded for it.
- `plans_finished/demo_environment/` decided a hosted service at a public link; where the hosting sends outgoing requests from matters for the outside service.
- `plans_finished/osm_data_source/` matters only if phase B picks an own search instance built from OpenStreetMap data.
- The HarmonyOS port, an open entry in `docs/standards/decision_registry.md`, would use the same search through the server; the rules of this PRD hold for any client.
- A read from an external system while handling a request is allowed in this repository only as an explicit, limited exception (`docs/standards/standard_architecture.md`, Calls to external systems); the search is such a read, so phase B records it as that exception.

## Risks and notes

- The outside service may refuse requests from the hosting: hosting services often send outgoing requests from an IP address shared with other customers, which a public service may already block. To be checked in phase B against the environment of `plans_finished/demo_environment/`.
- The outside service is a single dependency of the live demo; when it fails, only the map remains for giving a place.
- Query volume, an estimate by the agent from the shape: the team and the jury, at most a few dozen people, each making a few searches over several minutes, stay below 60 searches per minute, and the cache lowers the number further. A burst above the limit of the outside service ends in the search unavailable message, never in a wrong point.
- People typing on a phone often leave out Polish diacritics or the prefix "ul.", for example "Rynek Glowny" or "Lipska 5". If the chosen service does not match such text, the search fails exactly where the demo uses it; phase B checks it.
- The privacy policy of the operator of the most likely outside service gives no retention period for search requests. Because the text reaches it without anything identifying the person (FR-6), this is accepted, but it stays unknown.
- The list of barriers for a route (`plans/mvp/MVP_PRD.md` FR-11) shows the place of every item. If `plans/mvp/` decides to show that place as a street address, it needs the opposite direction - a point turned into an address - for every item of the list, which this PRD leaves out and which multiplies requests to the outside service. That needs its own decision.
- Time: the decision blocks the closing of the MVP plan, and every hour it stays open is taken from implementation before 11:00 on 4 October 2026.
