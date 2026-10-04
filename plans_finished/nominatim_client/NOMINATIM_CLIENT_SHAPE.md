# Shape: Check of the public Nominatim instance against the decisions of the address search

Document state: 2026-10-04, interview closed
Regulator: C:40

The seed carries no value of the regulator, so the default 40 applies.

## Problem

The address search of `docs/product/specification.md` M2 and M5 is answered by the public Nominatim instance, as `plans_finished/geocoding/` decided, but nothing of it exists yet: no code calls the instance, and its behaviour was checked only by hand from the machine of the agent's session. The user asked for an initiative that tests Nominatim and writes the interface to it; the interview narrowed it to the test, and the interface stays with `plans_finished/mvp/` (Out of scope).

## Recipient and trigger

- Trigger: the request of the user on 2026-10-03, after the agent concluded that Nominatim is needed only for the address search and that none of OpenStreetMap from Geofabrik, the stops of MSIP and Valhalla replaces it (seed).
- The owner is the external API person, the owner of `plans_finished/geocoding/` (`plans_finished/geocoding/GEOCODING_SHAPE.md`, Recipient and trigger), and the import person is consulted. Agent decision at C:40, without asking: this initiative carries out the decision of that one.
- The answers of the interview on 2026-10-03 were given by the user. They remove the questions from the list, but the ruling of the external API person on them is still to be confirmed.
- The recipients of the result: the external API person, who rules on every fact that contradicts a decision of `plans_finished/geocoding/`, and the work package of `plans_finished/mvp/` that builds the search, which takes the confirmed or corrected decisions and the recorded responses for its tests.
- The check is made before that work package starts, and at the latest before 11:00 on 4 October 2026, when the Kraków submission closes (`docs/hackathon/challenge_requirements.md`, Shared facts). Agent decision at C:40, without asking: a correction found later would land in code already written.

## Current state

- `plans_finished/geocoding/` decided on 2026-10-03 the public Nominatim instance (`GEOCODING_PLAN.md` D-1), called only by the server, with the normalization of the text (D-4), the exact request (D-5), the filter of results to Kraków (D-6), the label of a match (D-7), the cache in memory (D-8), the gate of one request per 1.1 seconds (D-9), the timeout of 5 seconds without a retry (D-10), three outcomes with one named exception (D-11), no searched text in any log (D-12), the constants of the third configuration layer (D-13), one backend process (D-15) and the tests (D-16).
- Building the search was left out of `plans_finished/geocoding/`: "The code is written as a work package of `plans_finished/mvp/`, together with the rest of the backend, because the backend architecture is decided there" (`GEOCODING_SHAPE.md`, Out of scope).
- `plans_finished/mvp/MVP_PLAN.md` D-3 carries that decision into the MVP. Its only open question, Q-11, owner backend, is decided in a separate initiative set up later, and it decides, among others, "the names of the modules and functions of the address search (`plans_finished/geocoding/GEOCODING_PLAN.md` D-2)" and "the structure that implements the operations of D-12", the address search included.
- The operation is fixed in `docs/product/api_contract.md`, section Address search: `POST /api/address-search` without a token, a body `{ "text": ... }`, a response `matches` with a label and a point, the error 422 `invalid_search_text` and the error 503 `address_search_unavailable`.
- No product code exists: `pyproject.toml` declares no runtime dependency, and `tests/` holds only `tests/architecture/`.
- The behaviour of the public instance was checked on 2026-10-03 from the machine of the agent's session (`GEOCODING_PLAN.md` F-1 - F-8), among others that "ul." and "ulica" break the search (F-5) and that the bounded viewbox still lets in Niepołomice and Wieliczka (F-3).
- Unit tests run without the network, and integration tests use neither the real network nor a real database (`GEOCODING_PLAN.md` F-18, from `docs/standards/standard_tests.md`).
- The usage policy of the public instance: an absolute limit of 1 request per second, no search as you type, an own User-Agent, results cached by the client, and a client repeating the same query may be blocked (`GEOCODING_PLAN.md` F-10).

## Smallest meaningful scope

A test of the public Nominatim instance against the decisions of `plans_finished/geocoding/`, and a correction of those decisions where the test contradicts them. No code of the search is written here. Decided by the user on 2026-10-03, against writing the client now with the names of its modules decided here, and against going through the chain now with the implementation waiting for Q-11 of `plans_finished/mvp/MVP_PLAN.md`.

## Out of scope

- Writing the interface to Nominatim, ordered by the seed. It keeps its executor: a work package of `plans_finished/mvp/`, with the names of the modules and the structure of the operations decided by Q-11 of `plans_finished/mvp/MVP_PLAN.md`, as `plans_finished/geocoding/GEOCODING_SHAPE.md`, Out of scope, recorded. Decided by the user on 2026-10-03, because writing it here would decide a part of Q-11 before its initiative exists.
- The choice of the address search service and the product rules of the search: settled by `plans_finished/geocoding/` and `docs/product/specification.md` M2, Address search.
- A check from the server of the demo whether its address is blocked by the public instance. It stays the manual check after the first deployment of `plans_finished/geocoding/GEOCODING_PLAN.md` D-16; the agent acts in the hosted demo environment only on an explicit request (`CLAUDE.md`, Target environment). Decided by the user on 2026-10-03.
- Changing the archived artifacts of `plans_finished/geocoding/`. A correction of its decisions is recorded in this initiative and carried into `plans_finished/mvp/MVP_PLAN.md` D-3, because an archived plan keeps its contract (`docs/standards/standard_agentic_workflow.md` ch. 4.6). Decided by the user on 2026-10-03 with the name of the initiative, whose option said that the archive stays untouched.

## Functional requirements

1. A check of the live public Nominatim instance from a machine of the team: the facts of `plans_finished/geocoding/GEOCODING_PLAN.md` about the answers of the instance, F-1 - F-8, are checked again, together with new cases, and each searched text is sent once. The pages of the usage policy and of the privacy policy behind F-10 and F-11 are read again outside the run, and F-9, about the public Photon instance, is not checked. The result is a list of facts, each confirming or contradicting a decision of D-4 - D-10 there. Decided by the user on 2026-10-03; the facts checked were narrowed by the user on 2026-10-04 in phase B of `plan-prd`, because F-8 concerns the timeout of D-10, F-9 another service rejected in D-1, and F-10 and F-11 web pages rather than searches, against checking only F-1 - F-8 and against checking F-9 too.
2. Recorded real responses of the instance, kept in this initiative and not in the code, as material for the tests of the work package of `plans_finished/mvp/` that builds the search with a fake transport instead of the network. Decided by the user on 2026-10-03.
3. The script that sends the requests of the check is kept as an attachment of this initiative, so that the check can be run again, for example before the demo. It is a tool of the check, not code of the product, and nothing of the product imports it. Decided by the user on 2026-10-03, against a one-off script that does not enter the repository.
4. Besides the facts F-1 - F-8, the check covers new cases: a name of a public transport stop, because the seed names the stops of MSIP and a stop is a common start or destination; the same name in a different letter case, because the cache of D-8 keys the text in case-folded form and so assumes the case does not change the result; a text with a postcode; a text that matches nothing; and a typo in a name. The exact list of texts is decided in phase B of `plan-prd`. Agent decision at C:40, without asking: each case checks a decision of D-4 - D-10 or a scenario of `plans_finished/geocoding/GEOCODING_SHAPE.md` that F-1 - F-11 do not cover.

## Scenarios: input, flow, expected state after the run

1. A run with every text answered. Input: a person starts the script with a list of 40 texts. Flow: the script sends one text per 1.1 seconds and records each response together with its text, its status and its time. State after: about 44 seconds later the attachments hold 40 responses, each fact of F-1 - F-8 and each new case is marked as confirming or contradicting a decision of D-4 - D-10, and nothing was retried.
2. A refusal in the middle of a run. Input: the twelfth text gets the status 429. Flow: the script stops at once. State after: 11 responses and the refusal with its status are recorded, texts 13 - 40 were not sent, and no further run starts until a person decides, because the team machine may now be blocked.
3. A fact contradicts a decision. Input: "ul. Lema 7", which returned nothing on 2026-10-03 (F-5), now returns the arena. Flow: the fact is recorded as contradicting D-4 and shown to the user and the external API person. State after: D-4 changes only by their ruling, and a change is carried into `plans_finished/mvp/MVP_PLAN.md` D-3; `plans_finished/geocoding/` stays unchanged.
4. The MVP uses the recordings. Input: the work package of `plans_finished/mvp/` that builds the search writes its tests. Flow: its unit tests feed the recorded responses through a fake transport. State after: those tests cover real shapes of responses without any request to the network.
5. A run again before the demo. Input: on 4 October 2026 a person decides to check the instance again. Flow: the script from the attachments runs under the same limits as in scenario 1. State after: the new responses show whether the instance still answers as recorded; a difference is handled as in scenario 3.

## Challenging own assumptions

- Does Valhalla or the stops of MSIP named in the seed change the need for Nominatim? No: Valhalla takes only coordinates and has no search of text, the OpenStreetMap copy from Geofabrik holds address tags but is not a search service, and the stops of MSIP name only stops. The search of M2 and M5 stays with Nominatim. The seed naming Valhalla differs from `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` D-1, which rejected Valhalla, but the routing engine does not touch the address search, so this initiative does not settle it.
- What does "interface" mean in the seed: the client of the outside service inside the backend, the operation of the programming interface that the frontend calls, or the search field in the frontend? Not settled, and no longer needed: writing the interface is out of scope (Out of scope).
- Does the cut of the interface leave an ordered item without an executor? No: the interface stays with a work package of `plans_finished/mvp/` and Q-11, and the testing stays here.
- What does "testing" mean in the seed: automated tests without the network, a check of the live public instance, or a check from the hosted server? Settled by the user: the live instance from a machine of the team and recorded responses for the tests of the MVP; the automated tests stay with the code in the MVP, and the check from the server stays with D-16 of `plans_finished/geocoding/`.
- Are all of F-1 - F-11 of `plans_finished/geocoding/GEOCODING_PLAN.md` facts about the answers of the instance? No, and the shape first assumed they were: F-8 is the time of the answers, behind the timeout of D-10, F-9 concerns the public Photon instance, and F-10 and F-11 are readings of policy pages. Found on 2026-10-04 in phase B of `plan-prd` and settled by the user (Functional requirements, item 1).
- Can a test of the live instance change a decision on its own? No. A fact that contradicts a decision of `plans_finished/geocoding/` is shown to the user and the external API person, the owner of this initiative, and the decision changes only by their ruling. Agent decision at C:40, without asking: `CLAUDE.md` forbids resolving such a conflict silently, and D-1 there was decided by the user with the external API person.

## Domain rules or explicit TODO

- The rules of `plans_finished/geocoding/GEOCODING_PLAN.md` D-1 - D-16 and of `docs/product/specification.md` M2, Address search, apply as decided.
- One run of the check sends at most 40 texts, at most one request per 1.1 seconds, so it lasts about 44 seconds, with the User-Agent of `GEOCODING_PLAN.md` D-5. Decided by the user on 2026-10-03, against 80 and 20 texts.
- A response 403 or 429, or no response within 5 seconds, stops the run at once: nothing is retried and the remaining texts are not sent. Another run starts only by the decision of a person. Agent decision at C:40, without asking: the pace and the timeout are those of D-9 and D-10 there, and the policy warns that a client repeating queries may be blocked (F-10 there), which would also block the team machine for the rest of the hackathon.
- Within one run each text is sent once, and a recorded response replaces sending the same text again while the initiative is worked on; a whole run is repeated only by the decision of a person, as above. Agent decision at C:40, without asking: it follows from the same warning of the policy and from requirements 2 and 3.
- The script of requirement 3 is run only by hand, never by the tests or by an automatic check of the repository. Agent decision at C:40, without asking: unit and integration tests use no real network (`GEOCODING_PLAN.md` F-18).
- The searched texts are names of public places and addresses of public buildings, never an address tied to a person, such as the home of a member of the team. Agent decision at C:40, without asking: the check needs no personal data, and the recorded responses stay in a public repository.

## Notes on data, performance and security

- The searched text is treated like the current location: never in a log or in the database (`GEOCODING_PLAN.md` D-12, specification M2). The texts of this check are not of any person (Domain rules), so recording them with their responses does not break that rule.
- Query volume: at most 40 requests per run at about one per second, below the absolute limit of the policy (Domain rules). Of the cost, only the time of a person and the risk of a block of the team machine remain, because the public instance is free.
- The recorded responses are OpenStreetMap data under the ODbL, which each response states in its field `licence` (`GEOCODING_PLAN.md` F-2); they keep that field and their source, so the attribution travels with them. Keeping them in a public repository touches the open entry of `docs/standards/decision_registry.md` on the repository licence; this shape does not settle that entry.
- A copy of someone else's document in `plans/<INITIATIVE>/attachments/` comes under the formatting gate like any other file (`docs/standards/standard_formatting.md`, section Emphasis in prose). A name in OpenStreetMap may hold a character forbidden there, and then the user chooses how the copy is handled.

## Open questions

None.
