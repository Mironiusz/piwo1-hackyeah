# Shape: Address search of the MVP

Document state: 2026-10-04, interview closed
Regulator: C:40

The seed carries no detail regulator, so the shape starts at C:40 (`plans_finished/mvp/MVP_PLAN.md` D-19). The owner of this initiative is Mateusz (`MVP.md`, section Initiatives). The interview is conducted with Rafał, the repository owner; an answer Rafał gives in place of Mateusz removes the question from the list and does not replace Mateusz's ruling.

## Problem

The MVP needs the search of an address or a place to give the start and the destination of a route (M2) and the point of a geozone (M5 of `docs/product/specification.md`). Everything above the code is settled: the product rules in M2, section Address search, the operation `search_address` in `docs/product/api_contract.md`, and the technical decision D-3 of `MVP.md`, which points to `plans_finished/geocoding/GEOCODING_PLAN.md` D-1 - D-16, with D-7 corrected by `plans_finished/nominatim_client/`. No code of the operation exists, while both clients already call it. This initiative builds the operation in the backend.

## Recipient and trigger

- A person using the web client or the HarmonyOS client submits a search text with the Enter key or a search button while setting the start or the destination of a route or the point of a geozone. The trigger is a request `POST /api/address-search` without a token.
- The clients that consume the response: the web frontend of `frontend_app` (Adrian) and the HarmonyOS port (Kuber).
- The outside system that receives the effect: the public Nominatim instance of the OpenStreetMap Foundation, which receives at most one request per 1.1 seconds from the server of the project.
- The person who verifies check 2.4 of `FINAL_CHECKLIST.md`.

## Current state

- `plans/address_search/` holds only the seed and `STAGE.md` (stage 2). No initiative named `address_search` exists in `plans_finished/`. The related closed initiatives have another scope: `plans_finished/geocoding/` decided the search and `plans_finished/nominatim_client/` checked the live instance against that decision; neither wrote product code.
- `docs/product/specification.md`, version 14, M2, section Address search: the search runs only on submission, returns only places within Kraków, carries no identity of an account, always gives a list the person picks from with the full address of each item, works with a keyboard alone and a screen reader, and has two different plain messages for nothing found and for an unavailable search. Section Personal data: the project hands the text to an address search service outside the project from its own server, without anything that identifies the person. The section names no cache of the text.
- `docs/product/api_contract.md`, section Address search: `POST /api/address-search`, no token, body `{ "text": ... }`; response `200` with `matches`, each with `label` and `point`, an empty array when nothing is found; `422` `invalid_search_text` for more than 200 characters as received or an empty text after trimming, collapsing spaces and removing the words "ul." and "ulica"; `503` `address_search_unavailable`. Section Sessions and actors: the service ignores the header `Authorization` here and renews nothing. Section Request logs and failures: the request log entry carries only the operation name, the status, the duration and the request identifier.
- `MVP.md` D-3 and `plans_finished/mvp/MVP_PLAN.md` D-3: the public Nominatim instance, called only by the server, with the rules, parameters and tests of `plans_finished/geocoding/GEOCODING_PLAN.md` D-1 - D-16; D-7 there changed on 2026-10-04 by the ruling recorded in `plans_finished/nominatim_client/attachments/nominatim_check_2026-10-04.md`, section Contradictions: in place of a missing `address.road` the label takes `address.neighbourhood` with the house number, and a result whose label repeats an earlier label of the same list is dropped. That ruling was given by Rafał in place of Mateusz, whose own ruling is still to be confirmed.
- `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-13 names the modules: `api/address_search.py`, `service/address_search.py` and `data/nominatim.py`, with the named exception `AddressSearchUnavailable`; D-2 there makes every endpoint a plain `def` run in the thread pool of FastAPI.
- Code: none of the three modules exists. The API foundation of `backend_skeleton` exists in the working tree - `build_app` in `api/app.py`, the error envelope in `api/errors.py`, the request log in `api/request_context.py`, and `config/logging.py`, which already sets the level of the logger `httpx` - and no endpoint is registered yet. The `backend_skeleton` review ends "not ready" on platform and image blockers (B-1 - B-3 of `plans_finished/backend_skeleton/BACKEND_SKELETON_REVIEW.md`), check 2.1 of `FINAL_CHECKLIST.md` is not ticked, and the same review records that `python -m api` answers local HTTP while its database is unavailable.
- `httpx==0.28.1` is already a pinned runtime dependency in `pyproject.toml`, used by the importer in `data/osm_source.py`.
- The web frontend calls the operation in `frontend/src/api/client.ts` and handles both error codes in `frontend/src/views/AddressSearchView.tsx` and `frontend/src/views/report/ReportPlaceStep.tsx`, today against `frontend/mock-server/server.mjs`; the HarmonyOS client calls it in `mobile_app/accessway/entry/src/main/ets/data/ApiRepository.ets`.
- The recorded responses of the live instance are in `plans_finished/nominatim_client/attachments/nominatim_check_2026-10-04.json`, named in `plans_finished/mvp/MVP_PLAN.md`, section Supplementary files, as material for the tests with a fake transport; `plans_finished/nominatim_client/NOMINATIM_CLIENT_PLAN.md`, section Risks, says the tests copy what they need instead of reading from the archive.
- The manual check of `plans_finished/geocoding/GEOCODING_PLAN.md` D-16 after the first deployment is item 4 of `docs/deployment/hosted_demo.md`, section Check before the link goes into the submission. The one backend process required by D-15 there is carried by D-14 of `MVP.md`.
- `FINAL_CHECKLIST.md`, check 2.4: done when an address in Kraków is found through the service and an unavailable search gives its plain message, the address part of MVP AC-2; it waits for check 2.1. `MVP.md`, section Requirements and initiatives, lists this initiative for FR-2 (AC-2) after `route_planning` and for FR-8 (AC-7) after `community_facts`, with `frontend_app` in both rows.
- `docs/standards/decision_registry.md` has no open entry on the address search.

## Smallest meaningful scope

The operation `search_address` in the three layers named by D-13 of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md`, behaving as the contract, M2 and `plans_finished/geocoding/GEOCODING_PLAN.md` D-2 - D-13 with the corrected D-7 say, registered in the application of `backend_skeleton`, with the automated tests of D-16 there, and verified on a locally running service for check 2.4.

## Out of scope

- The search field, the list, the two messages and their texts: `frontend_app` and the HarmonyOS port, both already built against the contract. This initiative delivers the distinct `503` response; the plain message on the screen belongs to the client. Agent decision at C:40, without asking: `MVP.md` lists `frontend_app` next to this initiative for AC-2 and AC-7, and the contract leaves the message to the client.
- The check from the hosted server that one search returns a list: item 4 of `docs/deployment/hosted_demo.md`, section Check before the link goes into the submission.
- Any other search service, an own Nominatim instance, suggestions while typing and the reverse direction of the search, rejected or left out by `plans_finished/geocoding/`.
- A change of the contract of `search_address`.
- Filling the cache in advance with the texts of the demo, or any other answer when the public instance is down. D-3 accepts that risk (`plans_finished/geocoding/GEOCODING_PLAN.md`, section Risks), and `docs/deployment/hosted_demo.md` leaves the team to decide before 10:00 what the submission says when the search is unavailable. Agent decision at C:40, without asking: it is not in D-3 and the seed orders only D-3.
- Naming the public Nominatim instance among the data sources of the Kraków submission, and the privacy information of FR-20 of `plans_finished/mvp/MVP_PRD.md`, which belong to the materials and to `frontend_app`.

## Functional requirements

1. The operation `search_address` answers `POST /api/address-search` as `docs/product/api_contract.md`, section Address search, says, takes no token, ignores the header `Authorization` and renews no session.
2. A text longer than 200 characters as received, or empty after the normalization of requirement 3, is refused with `invalid_search_text`; a body outside the contract is refused with `invalid_request`. Neither sends anything outside the project.
3. Before the cache lookup and the outgoing request the text is trimmed, every run of whitespace becomes one space, and the standalone words "ul." and "ulica" are removed in any letter case; nothing else is rewritten (`plans_finished/geocoding/GEOCODING_PLAN.md` D-4).
4. The outgoing request goes only to the public Nominatim instance, with the parameters and the User-Agent of D-5 there, and carries nothing that identifies the person: no cookie, no forwarded header, no account.
5. Only places whose address names Kraków as the city are returned (D-6 there).
6. Every match carries the label of D-7 there as corrected on 2026-10-04 and its point, in the order of the service, and a match whose label repeats an earlier label of the same list is dropped.
7. Answers, an empty list included, are kept in the cache of D-8 there; a failed search is never kept.
8. At most one outgoing request starts per 1.1 seconds for the whole process, and a search that gets no turn within 3 seconds is unavailable (D-9 there).
9. The outgoing request times out after 5 seconds and is not retried (D-10 there).
10. A timeout, a connection error, a status other than 200, a body that is not the expected JSON and no turn at the gate end as `503` `address_search_unavailable`, distinct from an empty list (D-11 there).
11. No log entry anywhere in the path of the request holds the text, the normalized text, the URL of the outgoing request, the response body or the point of a match, tracebacks included (D-12 there).
12. The automated tests of D-16 there exist and use no network; the material they take from the recorded responses is copied into the tests.
13. On a locally running service a person finds an address in Kraków and gets `address_search_unavailable` when the public instance cannot be reached, for check 2.4 of `FINAL_CHECKLIST.md`.

## Scenarios: input, flow, expected state after the run

1. A place by name. Input: "Tauron Arena" with an empty cache. Flow: the server normalizes the text, finds nothing in the cache, waits for its turn at the gate, asks the public instance, keeps the places in Kraków, labels them and drops repeated labels. State after: `200` with the arena first as "Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków"; the cache holds the key "tauron arena" with that list, without who asked or when; no log entry holds the text or a point.
2. The same text in other letters. Input: "TAURON ARENA" one minute later, in the same process. Flow: the case-folded key hits the cache. State after: the same list as in scenario 1; the public instance got no second request.
3. A street prefix and a house number unknown to the service. Input: "ul. Lipska 5". Flow: the normalization sends "Lipska 5"; the service returns 9 segments of the street without a number. State after: the list holds only distinct labels such as "Lipska, Płaszów, 30-721 Kraków", the first of each repeated label kept in the order of the service.
4. A place outside Kraków. Input: "Rynek Górny, Wieliczka". Flow: both results name the town Wieliczka and are dropped. State after: `200` with an empty `matches`, kept in the cache as an answer.
5. A caller error. Input: a text of 201 characters, and separately the text " ul. ". Flow: the first is refused before normalization, the second is empty after it. State after: `422` `invalid_search_text` for both; nothing was sent outside the project and nothing entered the cache.
6. A burst on a cold cache. Input: five different texts arrive at 10:00:00.000. Flow: the gate lets requests start at 10:00:00.000, 10:00:01.100 and 10:00:02.200; the fourth turn would come at 10:00:03.300, more than 3 seconds after arrival. State after: three searches answered with lists, two with `503` `address_search_unavailable`, none of the two kept in the cache; the public instance saw three requests in 2.2 seconds.
7. The public instance does not answer. Input: any text while the instance times out. Flow: after 5 seconds the call ends without a retry. State after: `503` `address_search_unavailable`; nothing kept in the cache, so the next search for the same text asks the instance again; one error entry with the cause and the elapsed time, without the text or the URL.
8. A request with a token. Input: the client sends `Authorization: Bearer` with a valid token by mistake. Flow: the service ignores the header. State after: the normal answer, without the header `Session-Token`; the session is not renewed.
9. A restart. Input: the backend process restarts during the demo. Flow: the cache starts empty. State after: the next search for any text asks the public instance again; nothing about earlier searches survived.

## Challenging own assumptions

- Is this a resumption of `plans_finished/geocoding/` or `plans_finished/nominatim_client/`? No. Those decided and checked the search, this one builds it, under a different name that `plans_finished/mvp/` set up with its own seed.
- Should this shape reopen the decisions D-4 - D-16 of `plans_finished/geocoding/GEOCODING_PLAN.md`? No. They were decided by the user with Mateusz on 2026-10-03 and checked against the live instance on 2026-10-04, which confirmed all of them apart from D-7, already corrected. The shape takes them as given; the technical form of each is phase B of `plan-prd`. The one point raised again was the cache of the search text, because it is personal data and stood only in an archived plan; Rafał kept it unchanged (Notes on data, performance and security).
- Does the search need the database or a finished `backend_skeleton`? It reads and writes no table, the API foundation it plugs into already exists, and `python -m api` answers without a database. So it can be built and checked locally before check 2.1 is ticked; whether check 2.4 may be ticked before 2.1 is for the person who ticks it, and this shape does not change `FINAL_CHECKLIST.md`.
- Is the plain message of check 2.4 part of this initiative? Only its cause, the distinct `503`; the message itself is shown by the clients, which already handle the code (Out of scope).
- Can a match the search labels as Kraków lie outside the boundary that refuses a start or a destination? At the edge of the city it can; `route_planning` then refuses the point with the message of M2, so nothing here changes.
- Can the request log or a traceback leak the text? The request log of `api/request_context.py` carries no body, but a traceback of an uncaught exception from the HTTP client could carry the URL with the text; requirement 11 and the log test of D-16 cover it.
- Does the backend reach the public instance from the server of the demo? The search needs outgoing HTTPS from the backend container, while D-9 of `MVP.md` puts Valhalla on an internal network of the demo; no deployment document names that need yet (Notes on data, performance and security).

## Domain rules or explicit TODO

- `docs/product/specification.md`, M2, section Address search, and section Personal data, prevail.
- `docs/product/api_contract.md`, section Address search, with Conventions, Sessions and actors, Request logs and failures and Errors, is the contract.
- `plans_finished/geocoding/GEOCODING_PLAN.md` D-2 - D-16, with D-7 as corrected in `plans_finished/mvp/MVP_PLAN.md` D-3, are the technical decisions; the names of the modules are those of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md` D-13.
- TODO for Mateusz: confirm the ruling on D-7 of 2026-10-04 and the answer on the cache of the search text, both given by Rafał in Mateusz's place (Open questions, item 1).

## Notes on data, performance and security

- Personal data: the text can reveal where a person goes and, for a hospital, something about their health (`agent_docs/memory/_cross_cutting.md`, entry Personal data in requests to outside services). It travels only in the body of a POST request, is never logged and never stored in the database, and reaches the public instance without anything that identifies the person.
- The cache of the search text stays as `plans_finished/geocoding/GEOCODING_PRD.md` FR-7 and `GEOCODING_PLAN.md` D-8 decided: in the memory of the one backend process, keyed by the normalized text alone, without who asked or when, at most 24 hours and at most 1000 entries, lost on a restart, never on disk and never in a log. `docs/product/specification.md`, section Personal data, does not change: the cache ties no text to a person, so it is not a kept item, as `plans_finished/geocoding/GEOCODING_SHAPE.md`, section Notes on data, performance and security, already reasoned, and the privacy information of FR-20 of `plans_finished/mvp/MVP_PRD.md` gets no new item. Decided by Rafał on 2026-10-04 in place of Mateusz (question 1, asked on signal 3 because the rule stood only in an archived plan).
- Query volume: at most one outgoing request per 1.1 seconds; the estimate of `plans_finished/geocoding/GEOCODING_SHAPE.md` - a few dozen people of the team and the jury, a few searches each - stays below that limit, and a burst above it ends as unavailable, never as a wrong point.
- Outgoing network: the backend container needs outgoing HTTPS to the public instance. This is a need of `plans/deployment_config/`, whose owner places the services as D-14 of `MVP.md` decides; it is handed over in the PRD, not decided here.
- The address of the server may be blocked by the public instance; item 4 of `docs/deployment/hosted_demo.md`, section Check before the link goes into the submission, finds it before the link goes into the submission.
- No secret is involved: the User-Agent names the repository, and no address of the target environment enters the code.

## Open questions

1. Mateusz's confirmation of the D-7 ruling of 2026-10-04 and of the answer to the question on the cache of the search text, both given by Rafał in Mateusz's place. `Block: no`
