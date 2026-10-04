# PRD: Address search of the MVP

Document state: 2026-10-04

## Business goal

A person gives the start and the destination of a route and the point of a geozone by typing an address or the name of a place in Kraków, as M2 and M5 of `docs/product/specification.md` describe. This is the address part of MVP AC-2 and a way to set the point of MVP AC-7 (`plans_finished/mvp/MVP_PRD.md`), and the effect of check 2.4 of `FINAL_CHECKLIST.md`: an address in Kraków is found through the service, and an unavailable search gives its own answer.

## Problem and its consequences

The web client and the HarmonyOS client already send the search to the service as `docs/product/api_contract.md`, section Address search, defines it, but the service has no such operation. Today every search on the real service ends as an unknown operation, so a person can set a point only on the map. The main scenario of the demo plans a walking route between two addresses, and the check of the hosted demo before the link goes into the submission (`docs/deployment/hosted_demo.md`) expects one address search to return a list; both fail until the operation exists.

## Scope

- The operation `search_address` on the side of the service, with the request, the responses and the errors of the contract, behaving as M2, section Address search, and D-3 of `MVP.md` decide.
- Its automated tests, without the network.
- A check on a locally running service that serves check 2.4.

## Out of scope

- The search field, the list, the picking and the two plain messages on the screen, with their texts: `frontend_app` and the HarmonyOS port, both already built against the contract. This initiative delivers the distinct answer the messages are chosen by.
- The check from the hosted server that one search returns a list, which is item 4 of `docs/deployment/hosted_demo.md`, section Check before the link goes into the submission.
- Any other search service, suggestions while typing and turning a point into an address, rejected or left out by `plans_finished/geocoding/`.
- A change of the contract of the operation.
- An answer prepared in advance for the case when the outside search service is down, for example searches of the demo kept ready before it starts. D-3 accepts that risk, and the team decides before 10:00 on 4 October 2026 what the submission says when the search is unavailable.
- The privacy information of FR-20 of `plans_finished/mvp/MVP_PRD.md`, which gets no new item from the search, and the description of the data sources in the Kraków submission.

## Functional requirements

FR-1. The operation. The service answers the address search of `docs/product/api_contract.md`, section Address search. The search takes no session: it never uses a token sent with it and never renews a session.

FR-2. Caller errors. A text longer than 200 characters as received, or empty once FR-3 is applied, is refused as an invalid search text. A request whose body does not follow the contract is refused as an invalid request. Neither refusal sends anything outside the project or is remembered.

FR-3. Preparing the text. Before anything else the text is trimmed, every run of spaces becomes one space, and the standalone words "ul." and "ulica" are removed in any letter case, because the outside search service finds nothing with them. Nothing else in the text is changed.

FR-4. Matches. The search returns only places within Kraków, in the order the outside search service gives them. Each match carries its point and its full label as D-3 of `MVP.md` defines it: the name of the place when it differs from the street, the street with the house number or, without a street, the estate with the house number, the district, and the postcode with Kraków. A match whose label repeats the label of an earlier match of the same list is left out, so that the list never shows two items that cannot be told apart.

FR-5. Privacy toward the outside search service. The text reaches the outside search service only from the server of the project, together with the fixed identification of the application that the terms of the service require and nothing that identifies the person: no address of the person, no account, nothing taken from the request of the person.

FR-6. Privacy inside the project. The text, the prepared text, the request sent to the outside search service, its answer and the points found are never written to a log or to the database, an error report included. The only place a text and its matches may be kept is the memory of the one running service, keyed by the prepared text alone, without who asked or when, for at most 24 hours, and lost when the service restarts. This keeping is not tied to a person, so it adds nothing to the data the specification lists as kept.

FR-7. Repeated searches. A search for a text already answered by the running service, in any letter case, is answered without asking the outside search service again, also when the answer was that nothing was found. A failed search is not remembered: the next search for the same text asks the outside search service again.

FR-8. Terms of the outside search service. The whole service never sends more than one request per second to the outside search service, whatever the number of people searching. A search that cannot get its turn within a short wait ends as unavailable instead of waiting longer.

FR-9. Search unavailable. When the outside search service does not answer in time, cannot be reached, refuses, or answers with something other than the expected list, or when the search gets no turn under FR-8, the person gets the unavailable answer of the contract, distinct from an empty list. No point is guessed, and the search is not repeated on behalf of the person.

FR-10. Tests. Every outcome of FR-2 - FR-9 is covered by automated tests that use no network and no real outside search service, and one test proves FR-6 for the logs of every outcome.

## Acceptance criteria

AC-1 (FR-1, FR-4). On a locally running service with access to the internet, a search for "Tauron Arena" returns a list whose first match is labelled "Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków", every match lies in Kraków, and no two matches have the same label.

AC-2 (FR-4). A search for "Rynek Górny, Wieliczka", whose places all lie outside Kraków, returns an empty list. Recorded answers in which two street segments share one label give a list in which that label appears once, at the position of the first of them.

AC-3 (FR-2). A text of 201 characters and the text " ul. " are refused as an invalid search text; a body without the text and a body with the text as a number are refused as an invalid request. In all four cases the outside search service receives no request.

AC-4 (FR-3, FR-7). "ul. Lipska 5" sends the text "Lipska 5" to the outside search service. A search for "TAURON ARENA" right after "Tauron Arena" causes no second request to it, and neither does a second search for "Qwxzvbn", which found nothing the first time.

AC-5 (FR-1). A search sent with a session token, valid or not, gets the same answer as without it, and the answer carries no renewed token.

AC-6 (FR-5). The request the outside search service receives carries the text, the fixed parameters and the identification of D-3 of `MVP.md`, and no cookie, no header taken from the request of the person and no account.

AC-7 (FR-7, FR-9). With the outside search service not answering in time, unreachable, answering with a refusal and answering with a body that is not the expected list, each search ends with the unavailable answer; after each of them the next search for the same text sends a new request.

AC-8 (FR-8, FR-9). Five different searches arriving at the same instant on a service that remembers nothing yet cause requests to the outside search service at least one second apart, and every search that does not get its turn within the wait of D-3 ends with the unavailable answer.

AC-9 (FR-6). For each outcome of AC-1 - AC-8, and for an unexpected failure inside the search, no log record, at the most detailed level and with formatted error reports included, holds the searched text, the prepared text, the address of the request to the outside search service, its answer or the point of a match.

AC-10 (FR-6). After a restart of the running service, a search for a text searched before the restart asks the outside search service again.

AC-11 (FR-9). On a locally running service cut off from the internet, a search ends with the unavailable answer, which the clients already turn into their plain message; this and AC-1 serve check 2.4.

AC-12 (FR-10). The automated tests of the search pass with the network switched off.

## Domain rules

The rules are those of `plans_finished/address_search/ADDRESS_SEARCH_SHAPE.md`, section Domain rules or explicit TODO, and of `docs/product/specification.md`, M2, section Address search, which prevails. In short, for reading the acceptance criteria:

- The search returns only places within Kraków, as a list the person always picks from; the service never picks a match on its own.
- The text leaves the project only from the server, without anything that identifies the person.
- The text and its matches are never logged and never stored in the database; only the memory of the running service keeps them, keyed by the text alone, for at most 24 hours, lost on restart (decided by Rafał in place of Mateusz on 2026-10-04, shape, section Notes on data, performance and security).
- Nothing found and search unavailable are two different answers; no point is ever guessed.
- The terms of the outside search service, one request per second at most and its required identification, are never broken, also at the cost of an unavailable answer.

## Dependencies and impact on other modules

- `backend_skeleton`: the search plugs into the application foundation it built - the error answers, the request log and the logging setup - which exists while that initiative is not finished. Check 2.4 waits for check 2.1 in `FINAL_CHECKLIST.md`; the search itself needs no database.
- `frontend_app` and the HarmonyOS port: they consume the operation unchanged and own the messages; nothing of them changes.
- `community_facts`: the point of a geozone given by an address uses the same operation; no work there.
- `route_planning`: refuses a start or a destination outside the boundary of Kraków with its own message, also for a match the search found at the edge of the city.
- `plans/deployment_config/`: the service of the demo needs outgoing access to the outside search service and runs as exactly one process (D-14 of `MVP.md`), because the memory of FR-6 and the limit of FR-8 hold only within one process. The outgoing access is not yet named in any deployment document and is handed over by this initiative.
- The shared logging of the service: FR-6 rules out the address of an outgoing request in a log, which may change what other parts of the service log about their own outgoing requests.

## Risks and notes

- The public outside search service may refuse requests from the address of the demo server. The search then ends as unavailable for the whole demo, and only the map is left for giving a place; item 4 of the check in `docs/deployment/hosted_demo.md` finds it before the link goes into the submission.
- The outside search service is a single dependency of the live demo at 11:00 on 4 October 2026 and may be slow or down.
- AC-1 depends on the live outside search service, whose answers can differ from one minute to the next (`plans_finished/nominatim_client/attachments/nominatim_check_2026-10-04.md`, R-12); the automated tests rest on recorded answers instead.
- A name combined with an address, such as "Szpital Uniwersytecki, Jakubowskiego 2", finds nothing, and a typo is not corrected; the demo searches for one of the two parts.
- Mateusz, the owner of this initiative, has not yet confirmed the ruling on the label of 2026-10-04 nor the answer on the memory of FR-6, both given by Rafał in Mateusz's place.
- Time: the Kraków submission closes at 11:00 on 4 October 2026, the day of this document.
