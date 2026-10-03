# Shape: Choice of the address search for the MVP

Document state: 2026-10-03, interview closed
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) lets a user give the start and the destination of a route, and the point of a geozone, by an address. How an address typed by the user is turned into a point on the map was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the external API person of the team; the import person is consulted, because OpenStreetMap carries address tags. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- The interview from 2026-10-03 on is answered by the user together with the external API person, so its answers are decisions of the owner of the initiative.
- `plans/mvp/MVP_PLAN.md`, open question Q-5, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.
- The decision has no deadline of its own: `plans/mvp/MVP_PLAN.md` cannot be closed until Q-5 is settled, and nothing of the MVP is implemented before that, so it is made as early as possible before 11:00 on 4 October 2026 (`plans/mvp/MVP_PLAN.md`, Risks). Agent decision at C:40, without asking: it follows from that recorded risk.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- On 2026-10-03, from the machine of the agent's session, the public Nominatim instance answered a search for an address in Kraków with HTTP 200.
- The usage policy of the public Nominatim instance, read on 2026-10-03 at `operations.osmfoundation.org/policies/nominatim/`: an absolute limit of 1 request per second, search as you type (autocomplete) forbidden also when built on the client side, the application identified by its own User-Agent or HTTP Referer, results cached by the client, attribution displayed.
- The privacy policy of the OpenStreetMap Foundation, read on 2026-10-03 at `osmfoundation.org/wiki/Privacy_Policy`: its services collect the IP address and the pages accessed; it gives no retention period specific to Nominatim and says some legacy practices are not yet documented.
- `plans/demo_environment/` decided on 2026-10-03 that the demo runs on a hosted service reachable at a public link, so the jury and anyone who gets the link can use the search, not only the team.
- `plans/api_contract/`, Current state, waits for this initiative to know whether the address search goes through the backend.
- `docs/standards/standard_architecture.md`, section Calls to external systems: a read from an external system on the request path is allowed only as an explicit exception with a timeout, without retries and with a cache that does not remember a failure.
- The source of the OpenStreetMap data is undecided (`plans_finished/osm_data_source/`); OpenStreetMap carries address tags. Since the search may go to an outside service through the server (Domain rules), this dependency matters only if phase B of `plan-prd` picks an own search instance built from the same data.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

A decision on how the MVP searches addresses and places, taken by the right people: the product rules of the search recorded in this shape, and the technical choice - which service answers the search and how it is connected to the backend - made in phase B of `plan-prd` of this initiative. The result closes `plans/mvp/MVP_PLAN.md` Q-5. Decided by the user with the external API person on 2026-10-03, against this initiative also building the search.

## Out of scope

- Building the search. The code is written as a work package of `plans/mvp/`, together with the rest of the backend, because the backend architecture is decided there (`plans/mvp/MVP_PLAN.md` Q-10) and building the search here first would mean guessing it. Decided by the user with the external API person on 2026-10-03.
- The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans/demo_environment/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans/account_sessions/`. The shape of the search request and response is part of `plans/api_contract/`; the map tiles are part of `plans_finished/frontend_stack/`.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-2 - the start and the destination of a route given as an address within Kraków.
2. FR-8 and AC-7 - the point of a geozone given by an address, with the keyboard alone.
3. FR-16 - the address search usable with a keyboard and a screen reader.

## Scenarios: input, flow, expected state after the run

1. A place by name as the destination. Input: the user types "Tauron Arena" in the destination field and presses Enter. Flow: the frontend sends the text to the server; the server finds nothing in its cache, asks the outside service for places within Kraków and keeps the result in the cache; the user gets a list of one item with the full address and picks it. State after: the destination is set; no log and no database row holds the text or the point; the cache in memory holds "Tauron Arena" with its result, without who asked or when.
2. Several matches. Input: the user types "Biedronka" and presses Enter. Flow: the list shows the matches within Kraków, each with its full address; a screen reader announces how many there are; the user moves through the list with the keyboard and picks one with Enter. State after: the picked place is set; nothing was taken without the user's choice.
3. The same text again. Input: another user searches "Tauron Arena" while the server process still runs. Flow: the server answers from the cache without asking the outside service. State after: the same list as in scenario 1; the outside service got no second request.
4. Nothing found. Input: the user searches a place that does not exist in Kraków, or exists only outside it. Flow: the user gets a plain message that nothing was found in Kraków. State after: no point is set; choosing a point on the map stays available.
5. The outside service does not answer. Input: any search while the outside service times out or refuses. Flow: the user gets a plain message that the search is unavailable, distinct from nothing found. State after: no point is guessed; the failure is not kept in the cache, so the next search asks the outside service again; choosing a point on the map stays available.
6. The point of a geozone with the keyboard alone (AC-7). Input: the user moves to the search field of the geozone form with Tab, types an address and presses Enter. Flow: the list of matches gets the focus, the user picks with the arrow keys and Enter, and the form moves on to the radius. State after: the point of the geozone is set without using a pointer.
7. A restart of the server. Input: the server process restarts during the demo. Flow: the cache starts empty. State after: the next search for any text asks the outside service again; nothing about earlier searches survived the restart.

## Challenging own assumptions

- Is an address a piece of personal data here? Yes, when it can be tied to a person: a destination such as a hospital can reveal information about health, and the specification keeps even the current location out of storage and logs (`docs/product/specification.md`, M2). Decided on 2026-10-03: the typed text may reach a service outside the project only from the server of the project, never together with the IP address of the person (Domain rules).
- Does sending the search only from the server keep the person's IP address away from the OpenStreetMap Foundation altogether? Not by itself: if the browser loads map tiles straight from `tile.openstreetmap.org`, that service sees the IP address of the person and the area they look at. The tiles are a choice of `plans_finished/frontend_stack/`, not of this initiative; the risk is recorded here so that it reaches that initiative.
- Does the search have to cover places by name, for example "Tauron Arena", or only street addresses? Decided on 2026-10-03: names of places too, because the demo takes place at the Tauron Arena and a search through an outside service finds names at no extra cost (Domain rules).

## Domain rules or explicit TODO

- Routes work only within Kraków (`docs/product/specification.md`, Area, device and language).
- The text a user types into the search may be sent to a service outside the project only by the server of the project. The browser never sends it to an outside service, so the outside service never gets the text together with the IP address of the person. Decided by the user with the external API person on 2026-10-03, against two variants: the text never leaving the project (an own address index built from OpenStreetMap data) and the browser querying the outside service directly.
- The typed text and the point found for it are treated like the current location: never written to a log or to the database, and never linked to an account or to an IP address. The only place they may be kept is a cache in the memory of the server process, keyed by the text alone, without who asked or when, and lost when the process restarts. Decided by the user with the external API person on 2026-10-03, against two variants: a cache in the database that survives a restart, and no cache at all.
- The search finds street addresses, with or without a house number, and places by name, for example "Tauron Arena" or "Rynek Główny". Decided by the user with the external API person on 2026-10-03, against street addresses only.
- When a search matches several places, the user picks one from a list; each item shows the full address, so places with the same name can be told apart, and the list works with a keyboard alone and with a screen reader (FR-16). The app never takes a match on its own. Decided by the user with the external API person on 2026-10-03, against taking the best match, which could send a route to a wrong place without anyone noticing.
- A single match is also shown as a list of one item for the user to pick. Agent decision at C:40, without asking: one flow for any number of results is simpler for a screen reader user and still catches a typo that matched a different place.
- The search returns only places within Kraków. Agent decision at C:40, without asking: it follows from the rule that routes work only within Kraków, so a place outside it could not be used anyway.
- The search runs only after the user submits the text, with the Enter key or a search button; nothing is suggested while the user types. Decided by the user with the external API person on 2026-10-03, against suggestions while typing, which the usage policy of the public Nominatim instance forbids and which would need another provider or an own index.
- When nothing is found, or the outside service does not answer, the user gets a plain message saying which of the two happened, no point is guessed, and choosing a point on the map stays available. Agent decision at C:40, without asking: it applies to the search the rule the specification sets for routing in M10 - a plain message and no guessed result when a source is unavailable - and the point on the map is already a way to give a place in M2 and M5.

## Notes on data, performance and security

- The current location is not stored, not logged and not linked to the account (`docs/product/specification.md`, M2); the typed text follows the same rule (Domain rules).
- A cache of results is required by the usage policy of the public Nominatim instance; the cache in memory decided above satisfies it, and repeated searches for the same text within the life of the process do not reach the outside service again.
- "Never written to a log" covers every log in the path of the request, not only the log entries of the application: an access log of the HTTP server or of the hosting records the client IP address and the full URL, so the text must not travel in a part of the request that such a log records. How this is achieved is a question for phase B of `plan-prd`.
- Nothing about the search is kept that is tied to a person, so the privacy information (`plans/mvp/MVP_PRD.md` FR-20) gets no new kept item. Whether it also names the address search among the data that is not kept is left to `plans/mvp/`, which owns FR-20.
- Because the search goes through the server, an outside service with a per-client limit, such as the public Nominatim instance with 1 request per second, sees all users of the public demo link as one client.
- The search going through the server answers the dependency recorded in `plans/api_contract/`, Current state: the address search is part of the contract between the frontend and the backend.
- Query volume, an estimate by the agent: the public link is used by the team and the jury, at most a few dozen people, each making a few searches over several minutes, which stays below the 60 searches per minute that a limit of 1 request per second allows, and cache hits lower it further. A burst above the limit ends in the plain message of scenario 5, never in a wrong point.
- Two risks for phase B of `plan-prd`: a hosting service often sends outgoing requests from an IP address shared with other customers, which the public Nominatim instance may already block; and the public instance is a single outside dependency of the live demo.

## Open questions

None.
