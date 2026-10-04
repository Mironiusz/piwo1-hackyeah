# Plan: Contract of the programming interface between the frontend and the backend of the MVP

Document state: 2026-10-03, plan closed

## Goal

Write the contract that `plans_finished/api_contract/API_CONTRACT_PRD.md` requires (FR-1 - FR-8, AC-1 - AC-8) as `docs/product/api_contract.md`: every operation between the clients and the service with its request, responses and errors, approved by the user in place of the frontend person. Bring the four product rules the user decided in phase B into the specification as version 7, settle Q-9 of `plans/mvp/MVP_PLAN.md`, record that Q-11 moves to a separate initiative together with the implementation of the operations, point the standards and the maps at the contract, and hand the storage of the idempotency key to the task `SCHEMA_REVISION` of `plans_finished/schema_revision/`. No code is written here (D-1).

## Facts

F-1. The PRD passed its gate again on 2026-10-03 after phase B: the implementation of the operations and the backend architecture are out of scope, a route request carries no identity of an account, a repeated save does not create a second fact, outdated facts except those removed from OpenStreetMap are visible in an area of the map, a pseudonym has 3 to 30 characters, and an expired session is refused with its own outcome. | doc:`plans_finished/api_contract/API_CONTRACT_PRD.md` line 22, lines 31, 35, 37 and 41 | 2026-10-03
F-2. No product code exists: no tracked file lies under a directory of a code layer or of the frontend. | cmd:`git ls-files` filtered by `^(api|service|data|worker|config|alembic|frontend)/` -> no output | 2026-10-03
F-3. Version 6 of the specification, approved by the user on 2026-10-03, makes the target database schema part of it, and its open questions say "None at version 6." | doc:`docs/product/specification.md` line 3, line 279, line 290 | 2026-10-03
F-4. The target schema stores the closed lists as text domains with English codes in snake case: eleven fact types, the sources `openstreetmap` and `user_report`, and the verdicts `confirm` and `deny`. | doc:`docs/product/schema.md` lines 31, 34 and 46 | 2026-10-03
F-5. A fact of the target schema has an optional geozone radius of 10, 25, 50 or 100 m allowed only for a barrier type, an optional description and number of steps, the sample data mark, the mark of a fact removed from OpenStreetMap and the flag and hiding instants, and the schema has no column for an idempotency key. | doc:`docs/product/schema.md` lines 122 - 134 and 143; cmd:`grep -n idempotency docs/product/schema.md` -> no match | 2026-10-03
F-6. The status of a fact, its sums and the date of its last confirmation are derived from the votes on every read, and a vote refused by the vote limit is a normal outcome of the write, signalled by no returned row. | doc:`docs/product/schema.md` line 160; doc:`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` line 56 D-4, line 66 D-9 | 2026-10-03
F-7. The database sets no length limit on the description and the pseudonym; the limit of the description is left to this initiative and the rules of the pseudonym to the input that accepts it. | doc:`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` line 70 D-11, line 76 D-14 | 2026-10-03
F-8. A session is a signed token kept by the browser across its closing, renewed by every authenticated request for 24 hours, removed from the browser at logout, unable to resolve once its account is deleted, with the moderator role read on every moderator request, and this initiative owns its transport. | doc:`plans_finished/account_sessions/ACCOUNT_SESSIONS_PLAN.md` line 29 D-3 | 2026-10-03
F-9. Address search takes its text only in the body of a POST request, rejects a text longer than 200 characters as received or empty after normalization, returns matches of a label, a latitude and a longitude, and ends in a list, an empty list or an unavailable outcome, whose path and JSON shape this initiative decides. | doc:`plans_finished/geocoding/GEOCODING_PLAN.md` line 40 D-3, line 42 D-4, line 48 D-7, line 56 D-11 | 2026-10-03
F-10. The frontend is served from the same host as the programming interface, needs a code for everything from a closed list, and applies no product rule and no time zone conversion, so the segment states, the groups of the list and the calendar day of every fact arrive as the specification defines them. | doc:`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` line 52 D-3, line 62 D-8, line 92 D-13; doc:`docs/standards/standard_frontend.md` line 58 | 2026-10-03
F-11. A route is made of segments that are stretches of the network plus the two straight stretches to it in the state no data, carries at most one alternative around unverified or disputed barriers with the reason naming them, states when no route without barriers exists, lists the amenities of the profile within 50 m, and is unavailable when the graph cannot be built or a read fails. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md` line 58 D-5, line 60 D-6, line 62 D-7, line 66 D-9, line 68 D-10, line 74 D-13 | 2026-10-03
F-12. The specification defines the four segment states, the missing attributes kerbs, surface, incline, width and steps, the `wheelchair=no` message, the three groups of the list, the calendar day in Europe/Warsaw, and that a fact from OpenStreetMap cannot be flagged while hidden content disappears for everyone. | doc:`docs/product/specification.md` lines 170 - 181 M7, line 185 M8, lines 205 - 206 M10, line 214 M11 | 2026-10-03
F-13. The specification says that the current location travels only in the route request, that every request in the active session renews it, that a fact removed from OpenStreetMap disappears from the map, and that an OpenStreetMap fact shows the date of its last OpenStreetMap edit while a confirmation updates its date of last confirmation. | doc:`docs/product/specification.md` line 67 M2, line 193 M9, line 120 M4, line 118 M4 | 2026-10-03
F-14. Two standards say that the response codes and bodies and the path names of the programming interface are decided by the product specification. | doc:`docs/standards/standard_errors.md` line 22, line 44; doc:`docs/standards/standard_naming.md` line 20 | 2026-10-03
F-15. The request identifier comes from the header `X-Request-Id` when it has only alphanumeric characters, hyphens and underscores and at most 128 characters, and is generated otherwise. | doc:`docs/standards/standard_logging.md` line 85 | 2026-10-03
F-16. A write that can be repeated for the same logical operation needs duplicate protection from its first day, keyed by a stable identifier of the operation rather than one generated anew on each attempt. | doc:`docs/standards/standard_idempotency.md` line 35, line 39, line 76 | 2026-10-03
F-17. The programming interface exposes instants with milliseconds. | doc:`docs/standards/standard_time.md` line 41 | 2026-10-03
F-18. In the MVP plan D-11 is the last decision, Q-9 and Q-11 are open, and the Risks item that begins "The open questions depend on each other" names Q-9 and `plans_finished/api_contract/`. | doc:`plans/mvp/MVP_PLAN.md` line 45, line 56, line 60, line 61, line 77 | 2026-10-03
F-19. The pointers to version 6 of the specification stand in `PRODUCT.md`, in the Goal of the MVP plan and in the Scope and Domain rules of the MVP PRD. | cmd:`grep -rn "version 6"` over `PRODUCT.md`, `docs`, `plans/mvp` -> `PRODUCT.md:45`, `PRODUCT.md:100`, `plans/mvp/MVP_PLAN.md:7`, `plans/mvp/MVP_PRD.md:17`, `plans/mvp/MVP_PRD.md:111`, plus the provenance of the schema in `docs/product/schema.md:3`, `docs/standards/README.md:54` and `plans/mvp/MVP_PLAN.md:45` | 2026-10-03
F-20. The registry entry of the technical directions says that `plans_finished/account_sessions/` and `plans_finished/api_contract/` are in their interviews and that phase B of `plans/mvp/` resumes with the backend architecture. | doc:`docs/standards/decision_registry.md` line 48, line 49 | 2026-10-03
F-21. `PRODUCT.md` lists the routing engine and this contract as undecided, although the routing engine is D-9 of the MVP plan. | doc:`PRODUCT.md` line 94; doc:`plans/mvp/MVP_PLAN.md` line 41 | 2026-10-03
F-22. The shape of the task `SCHEMA_REVISION` has its interview in progress and one open question. | doc:`plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md` line 3, lines 65 - 67 | 2026-10-03
F-23. The standards map names `docs/product/` with the specification and the schema, and its table of tasks has no row for the programming interface. | doc:`docs/standards/README.md` line 54, lines 92 - 95 | 2026-10-03
F-24. While this plan was written, another session implemented the task `FACT_SCHEMA` on the same working tree, leaving its changes uncommitted, among them the path updates and the item of its step 6.1 in the files of this initiative. | cmd:`git status --short` -> 23 changed files, among them `plans_finished/api_contract/API_CONTRACT_PRD.md` and `plans_finished/api_contract/API_CONTRACT_SHAPE.md`; doc:`plans_finished/fact_schema/FACT_SCHEMA_REVIEW.md` line 3 | 2026-10-03
F-25. The project virtual environment has Python 3.13.14 with pytest 9.1.1, and prettier is installed in `node_modules`. | cmd:`venv/Scripts/python.exe --version` -> `Python 3.13.14`; cmd:`venv/Scripts/python.exe -m pytest --version` -> `pytest 9.1.1`; cmd:`ls node_modules/.bin/prettier` -> found | 2026-10-03

## Decisions

D-1. This initiative writes the contract and no code. The backend architecture of Q-11 of the MVP plan goes to a separate initiative set up later, and the implementation of the operations goes with it. Decided by the user on 2026-10-03 in phase B, first choosing to decide Q-11 here and then moving it out, against two tasks in this directory and against a plan waiting for Q-11 (F-1, F-2).

D-2. The contract is the Markdown document `docs/product/api_contract.md`, with the shapes as JSON blocks; it is not part of the specification, which prevails over it. Decided by the user on 2026-10-03, against an OpenAPI file written by hand and against a contract that is part of the specification. Because of that choice, the boundary sentences of `docs/standards/standard_errors.md` and `docs/standards/standard_naming.md`, which give the response codes, bodies and paths to the specification (F-14), point at the contract, and the standards map names it (F-23). Agent decision at C:40, without asking, for the standards and the map: otherwise two standards would send a reader to a document that does not hold these things.

D-3. The four product rules of the PRD on a route request and an address search without an account, outdated facts on the map, the pseudonym and an expired session enter the specification as version 7, which only adds them, approved by the user before the rest of the plan runs; the pointers that name the version of the specification move to version 7 as they moved to version 6 (F-19). Decided by the user at the gate of the PRD on 2026-10-03, against keeping the rules only in the contract.

D-4. The session token travels in the request header `Authorization: Bearer <token>`. Decided by the user on 2026-10-03, against an HttpOnly cookie. The operation `log_in` returns the token in the response header `Session-Token`, and every response to a request that carried a valid token returns the renewed token there, so the renewal of F-8 works the same way for every operation and for a client that is not a browser. Logging out is the client deleting its token, without an operation, because the token is signed and the server keeps no session (F-8). `create_account` does not log in, so a token comes from one operation only. Agent decision at C:40, without asking, for the header, the logout and the account creation.

D-5. A token that is malformed, wrongly signed, expired or of a deleted account is refused with `401 session_expired` and never handled as a request without an account. Decided by the user on 2026-10-03, against treating such a request as anonymous.

D-6. `plan_route` and `search_address` take no token: the client does not send it and the service ignores it, resolves no account and renews no session. Decided by the user on 2026-10-03, against sending the token with every request. `create_account` and `log_in` take no token either. Agent decision at C:40, without asking, for those two: a stale token kept by the client must not refuse the operations that replace it.

D-7. `list_facts_in_area` returns facts in every status except a fact outdated because it was removed from OpenStreetMap, and never a hidden one. Decided by the user on 2026-10-03, against leaving out every outdated fact. `find_nearby_facts` leaves out only hidden facts, as `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` FR-13 says, and `read_fact` returns any fact that is not hidden.

D-8. A pseudonym has 3 to 30 characters after leading and trailing spaces are removed and no character of the Unicode category Cc. Decided by the user on 2026-10-03, against 1 to 50 characters. A password has 5 to 128 characters, all accepted, which meets the minimum of 5 and the maximum of at least 64 of M9; characters are counted as Unicode code points. Agent decision at C:40, without asking, for the 128 and the counting.

D-9. `create_fact` carries an `idempotency_key`, a UUID the client generates once, when the person approves the summary, and repeats unchanged with every attempt of the same save; a repetition with the same content returns the first fact with `200`, and the same key with another content is refused with `409 idempotency_key_reused`. The user had no preference on 2026-10-03 between this and accepting duplicates as a recorded deviation from `docs/standards/standard_idempotency.md`, so this is an agent decision at C:40, without asking: the standard requires the protection from the first day and a stable identifier of the operation (F-16). The target schema has no column for the key (F-5), and how it is stored is a schema change, so this plan does not decide it: it hands the need to the task `SCHEMA_REVISION` as a blocking question (step 9).

D-10. The user approves the contract in place of the frontend person on 2026-10-03, with the frontend person's confirmation still to be obtained. Decided by the user, against waiting for that person before the contract is approved.

D-11. Conventions of the contract, each an agent decision at C:40, without asking: the prefix `/api` on the host of the page (F-10); JSON bodies with field names in snake case and a refusal of unknown fields, because the service and its clients change together; the codes of the closed lists of the schema reused unchanged (F-4), so the service maps nothing; a point as an object of `lat` and `lon`, and a line as `[lon, lat]` pairs of RFC 7946, which MapLibre takes as they come; distances in whole metres; a day as `YYYY-MM-DD` in Europe/Warsaw computed by the service (F-10, F-12); an instant in ISO 8601 with milliseconds and the offset of Europe/Warsaw (F-17); `GET` with identifiers only and coordinates and free text only in `POST` bodies, extending the reason of F-9 to every request that carries a point; the header `X-Request-Id` read and returned under F-15; one error body with a `code`; the heading of every operation as the operation name of the request log.

D-12. A fact is one object for every operation, with `osm_edited_on` only for a fact whose source is OpenStreetMap, `last_confirmed_on` for any confirmed fact, `is_removed_from_osm` for the reason of M4 and `can_be_flagged` computed by the service, so the client shows the dates it gets and applies no rule (F-10, F-13). Agent decision at C:40, without asking: the specification gives an OpenStreetMap fact both an edit date and a confirmation date, and a converted fact only the confirmation date, so the service, not the client, decides which dates exist.

D-13. The route response carries the day of the copy, whether a route without barriers exists, the route and an optional alternative with the barriers it avoids; a route carries its segments with state, missing attributes and the `wheelchair=no` mark, and the three groups of the list as route facts with their distance from the start and whether OpenStreetMap overrules them. Agent decision at C:40, without asking: it carries what F-11 and F-12 name, in a form the client draws without a rule of its own.

D-14. Input limits: a description of at most 500 characters after the trim, empty meaning none, the limit F-7 hands here; a number of steps from 1 to 999; at most 1000 facts in an area, with `is_truncated` when there are more. Agent decision at C:40, without asking: a description names a concrete fact, and the number of facts in a screen of the map was not measured, so the response says when it was cut instead of the client guessing.

D-15. For a vote or a report without an account the service derives the identifier of the person from the request itself (M9), and the contract asks nothing from the client for it. Agent decision at C:40, without asking: how the hash is computed belongs to the implementation of voting (`plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-8), and a field from the client would be a fingerprint the specification does not ask for.

D-16. A repeated vote within a day is refused with `409 vote_too_soon` and the instant from which the next one is accepted, so a vote whose response was lost never counts twice (F-6); flagging, hiding and restoring set a state and answer the same way when the state is already set. Agent decision at C:40, without asking.

D-17. The address match of `search_address` is `{label, point}`, with the point object of D-11, instead of the `lat` and `lon` at the top level of the example the user saw when choosing the format. Agent decision at C:40, without asking: one shape of a point in the whole contract.

D-18. In the MVP plan, Q-9 becomes the next free decision, D-12 on the tree of 2026-10-03, and its item leaves Open questions; the item Q-11 records that it goes to a separate initiative with the implementation of the operations (D-1). The new initiative of Q-11 is set up by the user, not by this plan. Agent decision at C:40, without asking, for the wording; the move of Q-11 was decided by the user.

How the decisions meet the acceptance criteria of the PRD:

- AC-1: `plan_route` in step 1, with D-6, D-11 and D-13, and the sentence on the current location in its request.
- AC-2: `routing_unavailable` of `plan_route`.
- AC-3: `find_nearby_facts`, `cast_vote` with `confirm`, and `create_fact` sent after the approved summary with the `idempotency_key` of D-9.
- AC-4: the optional token of the fact operations, `vote_too_soon`, `flag_fact`, the three moderator operations with `moderator_role_required`, `fact_not_found` for a hidden fact, and `session_expired` of D-5.
- AC-5: the fact object of D-12 with its closing paragraph.
- AC-6: `search_address` with D-6 and D-17.
- AC-7: the last item of Conventions and the route object, which carries only codes, numbers and days.
- AC-8: the section Request logs and failures.

## Scope of changes

Texts to insert are given in fenced blocks and are inserted without the fence. Every existing file is read again right before it is edited; when a quoted passage no longer matches the file, the step stops and the difference goes to the user (F-24). YYYY-MM-DD is the day of the edit; in step 1 and in steps 2.1, 2.9 and 2.10 it is the day of the user's approval.

### Step 1. `docs/product/api_contract.md`, new file

Create the file with this content:

````text
# Programming interface contract

Document state: YYYY-MM-DD, approved by the user in place of the frontend person, whose confirmation is still to be obtained

## Why this document exists

This is the contract of the programming interface between the clients of the app - the web frontend and a possible HarmonyOS client - and its service: every operation with its request, its responses and its errors. The clients and the service are built in parallel against it and change together, so it keeps no backward compatibility for a client released on its own. A change of an operation is a change of this document first, agreed by the backend person and the frontend person.

The behavior behind the operations is that of `docs/product/specification.md`, with the target database schema `docs/product/schema.md`, and it prevails over this document; this document says how that behavior crosses the boundary between a client and the service. It was decided in `plans_finished/api_contract/`.

## Conventions

- Every operation has the path prefix `/api` and is served from the host of the page.
- Bodies are JSON in UTF-8 with `Content-Type: application/json`. An operation without a body in one direction says so.
- Field names are in snake case. A request with a field this document does not name, without a required field, or with a value of a wrong type is refused with `invalid_request`.
- A value from a closed list is a stable code in English snake case, which the client translates into the language of the interface. The codes of fact types, sources and votes are those of `docs/product/schema.md`, section Extensions and domains; the other lists are defined here.
- A point is an object `{ "lat": 50.0678, "lon": 19.9914 }` in degrees of WGS 84. A line is an array of `[lon, lat]` pairs, in the order of RFC 7946.
- Distances and lengths are whole metres.
- A day is a string `YYYY-MM-DD`: the calendar day in the Europe/Warsaw zone, computed by the service (M10). The client converts no time zone.
- An instant is a string of ISO 8601 with milliseconds and the offset of the Europe/Warsaw zone at that instant, for example `2026-10-04T00:30:00.000+02:00`.
- A `GET` request carries only identifiers in its path and has no query string. Coordinates and free text travel only in the body of a `POST` request, because every access log on the way records the URL.
- Every response carries the header `X-Request-Id`. A client may send its own; the service keeps it when it has only letters, digits, hyphens and underscores and at most 128 characters, and replaces it with a generated one otherwise.
- Text in a language appears in a response only in the label of an address match, which comes from OpenStreetMap in Polish, and in a description a person wrote. Everything else is a code, a number, a day or an instant, so a client switches the language of the interface without repeating a request.

## Sessions and actors

- A session is a signed token. The client sends it in the header `Authorization: Bearer <token>` and keeps it in the storage of the browser, so it survives closing the browser (M9).
- `log_in` returns the token in the response header `Session-Token`. Every response to a request that carried a valid token carries a renewed token in `Session-Token`, valid until 24 hours after that request, and the client replaces the token it keeps with it.
- Logging out is the client deleting its token; no operation exists for it.
- A request without the header `Authorization` is made by a person without an account.
- A request whose token is malformed, wrongly signed, expired or of an account that no longer exists is refused with `session_expired` and is never handled as a request of a person without an account (M9). The client then deletes its token, tells the person they are logged out and lets them repeat the action.
- `plan_route`, `search_address`, `create_account` and `log_in` take no token: the client does not send the header `Authorization` with them, and the service ignores it there and renews nothing (M2, M9).
- A moderator operation needs a valid token of an account that holds the moderator role at the moment of the request; the role is read again on every such request (M11).
- For a vote or a report without an account the service derives the identifier of the person from the request itself (M9). The client sends nothing for it, and no response carries it.

## Request logs and failures

- The entry the service logs for a request carries only the name of the operation, as the headings of this document name it, the response status, the duration and the request identifier. It carries no body of the request or the response, no header, no pseudonym, no account identifier, no location, no preferences, no IP address and no browser characteristics. A failure may add a separate diagnostic entry with the traceback.
- No response carries an exception, a query fragment, a database object name, a connection string or anything about the infrastructure.

## Errors

An error response has the body:

```json
{ "error": { "code": "invalid_request", "fields": ["start.lat"] } }
```

`code` is always present; another field of `error` exists only for the code that names it. The codes every operation can return:

| Status | `code`                    | When                                                                                                                                  |
| ------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 422    | `invalid_request`         | The body is not JSON, or a field is missing, unknown, of a wrong type or outside the rules of its operation; `fields` lists its paths. |
| 401    | `authentication_required` | The operation needs an account and the request has no token.                                                                          |
| 401    | `session_expired`         | The token is malformed, wrongly signed, expired or of an account that no longer exists.                                               |
| 403    | `moderator_role_required` | The account does not hold the moderator role at the moment of the request.                                                           |
| 404    | `not_found`               | No operation exists at this method and path.                                                                                          |
| 404    | `fact_not_found`          | No fact has the identifier of the path, or the fact is hidden and the operation is not a moderator one (M11).                         |
| 500    | `internal_error`          | The service failed in a way this document does not name.                                                                             |

The codes of one operation are named in its section.

## Shared objects

### Fact

A barrier or an amenity of the closed list at a point: a report, a geozone, a fact from OpenStreetMap or a fact converted from one (M3 - M6).

```json
{
  "id": 1042,
  "type": "stairs",
  "point": { "lat": 50.0678, "lon": 19.9914 },
  "geozone_radius_m": null,
  "description": null,
  "step_count": 3,
  "source": "openstreetmap",
  "status": "confirmed",
  "is_removed_from_osm": false,
  "osm_edited_on": "2026-09-14",
  "last_confirmed_on": "2026-10-03",
  "is_sample": false,
  "can_be_flagged": false
}
```

- `id` - the identifier of the fact, an integer.
- `type` - the barriers `stairs`, `high_kerb`, `poor_surface`, `steep_incline`, `narrow_passage` or the amenities `ramp`, `elevator`, `lowered_kerb`, `accessible_toilet`, `rest_place`, `handrail_at_stairs` (M3).
- `point` - the point of the fact; for a fact of a way, a point on the way.
- `geozone_radius_m` - 10, 25, 50 or 100 for a geozone, `null` otherwise (M5).
- `description` - the description a person wrote, or `null`.
- `step_count` - the number of steps of stairs, from the report or from OpenStreetMap, or `null`.
- `source` - `openstreetmap` or `user_report` (M10); a fact converted from OpenStreetMap is `user_report` (M4).
- `status` - `unverified`, `confirmed`, `disputed` or `outdated`, derived by the service from the votes (M4).
- `is_removed_from_osm` - `true` only for a fact outdated because it was removed in OpenStreetMap, the reason M4 shows.
- `osm_edited_on` - the day of the last OpenStreetMap edit of the element of the fact, only when `source` is `openstreetmap`, `null` otherwise (M4).
- `last_confirmed_on` - the day of the latest confirmation of the fact, `null` when it has none (M4). A report carries the confirmation of its author, so it always has one.
- `is_sample` - `true` for the sample data of the demo, which the client marks as sample data wherever it shows the fact (M10).
- `can_be_flagged` - `false` for a fact from OpenStreetMap, which cannot be flagged, `true` otherwise (M11).

The client shows the source, every day that is not `null` and the status (M10). No fact carries anything about the author of a report, a vote or a geozone, whether that person was logged in, or the weights behind the status (M9).

### Account

```json
{ "pseudonym": "Wózek_KRK", "is_moderator": false }
```

The account of the session itself. No operation returns the account of anybody else.

## Route

### plan_route

`POST /api/routes`, no token.

Request:

```json
{
  "start": { "lat": 50.0645, "lon": 19.9837 },
  "destination": { "lat": 50.0678, "lon": 19.9914 },
  "avoid": ["stairs", "high_kerb", "poor_surface", "narrow_passage"],
  "need": ["elevator", "ramp", "lowered_kerb"]
}
```

- `start` and `destination` - the chosen points: the current location, a match of `search_address` or a point on the map. The current location travels only in this request; the service does not store it, does not log it and links it to nothing (M2).
- `avoid` - the barriers of the profile, barrier types, each at most once, possibly none.
- `need` - the amenities of the profile, amenity types, each at most once, possibly none.

The request carries no identity of an account, so the profile and the chosen points are never linked to one, and nothing of the request leaves the project (M1, M2).

Response `200`:

```json
{
  "osm_copy_date": "2026-10-02",
  "barrier_free_route_exists": true,
  "route": { "...": "a route" },
  "alternative": null
}
```

- `osm_copy_date` - the day of the OpenStreetMap copy the route was computed from (M6).
- `barrier_free_route_exists` - `false` when every way to the destination crosses a barrier of the profile or a geozone of a type of the profile that a route avoids; the client then says plainly that no route without barriers exists, `route` is the route with the fewest such barriers, and its `profile_barriers` say where they are (M2).
- `route` - the route.
- `alternative` - `null`, or the alternative that avoids the unverified or disputed barriers of the profile `route` keeps (M2):

```json
{ "route": { "...": "a route" }, "avoided_barriers": [{ "...": "a route fact" }] }
```

`avoided_barriers` are the barriers of `route` the alternative avoids, each with its status, which the client names as the reason.

A route:

```json
{
  "length_m": 1840,
  "segments": [
    {
      "line": [
        [19.9837, 50.0645],
        [19.9839, 50.0646]
      ],
      "length_m": 14,
      "state": "no_data",
      "missing_attributes": ["kerbs", "surface", "incline", "width", "steps"],
      "is_marked_wheelchair_no": false
    }
  ],
  "profile_barriers": [],
  "additional_barriers": [],
  "amenities": []
}
```

- `segments` - the segments in order from the start, the straight stretches between a chosen point and the pedestrian network included (M2).
- `state` - `barrier`, `no_barrier`, `partial_data` or `no_data`, the four states of M7, decided by the service. The client draws each with its own color and its own icon or line pattern.
- `missing_attributes` - for a segment in `partial_data` or `no_data`, the attributes behind the barriers of the profile that are not known, from `kerbs`, `surface`, `incline`, `width` and `steps`, in this order; empty in the other states (M7, M8).
- `is_marked_wheelchair_no` - `true` when OpenStreetMap marks the way as not accessible for wheelchairs; the list then says so (M7, M8).
- `profile_barriers`, `additional_barriers` and `amenities` - the three groups of the list for the route (M8), each in order along the route: the barriers of the profile on the route, the barriers outside the profile on the route, and the amenities of the profile within 50 m of the route. Only `profile_barriers` and `amenities` appear on the map (M7).

A route fact is a fact with two more fields:

```json
{ "...": "the fields of a fact", "distance_from_start_m": 230, "is_overruled_by_osm": false }
```

- `distance_from_start_m` - the distance along the route from the start to the place of the fact on the route.
- `is_overruled_by_osm` - `true` for a report that OpenStreetMap contradicts and that has not reached the threshold of M4: the client shows it as an unverified report icon, and the segment follows OpenStreetMap (M7).

Errors:

| Status | `code`                | When                                                                                                    |
| ------ | --------------------- | ------------------------------------------------------------------------------------------------------- |
| 503    | `routing_unavailable` | No route can be computed right now (M10). The response carries no route, and no route is guessed.      |

## Address search

### search_address

`POST /api/address-search`, no token.

Request:

```json
{ "text": "Tauron Arena" }
```

The text travels only in this body (M2, Address search).

Response `200`:

```json
{ "matches": [{ "label": "Tauron Arena Kraków, Stanisława Lema 7, Czyżyny, 31-571 Kraków", "point": { "lat": 50.0678, "lon": 19.9914 } }] }
```

`matches` are the places in Kraków in the order of the search service, each with its full label and its point, and an empty array when nothing is found. The client always shows a list to pick from, also for one match, and sets a point only when the person picks it (M2).

Errors:

| Status | `code`                       | When                                                                                       |
| ------ | ---------------------------- | ------------------------------------------------------------------------------------------ |
| 422    | `invalid_search_text`        | `text` has more than 200 characters as received, or is empty once its spaces are trimmed and collapsed and the words "ul." and "ulica" are removed. |
| 503    | `address_search_unavailable` | The search cannot be answered right now; the client says so with a message different from nothing found (M2). |

## OpenStreetMap copy

### read_osm_copy

`GET /api/osm-copy`, token optional, no request body.

Response `200`:

```json
{ "date": "2026-10-02" }
```

`date` is the day of the OpenStreetMap copy in use (M6), or `null` before the first copy exists.

## Facts

### list_facts_in_area

`POST /api/facts/in-area`, token optional.

Request:

```json
{ "south_west": { "lat": 50.064, "lon": 19.983 }, "north_east": { "lat": 50.07, "lon": 19.995 } }
```

`south_west` has to be south and west of `north_east`, otherwise the request is refused with `invalid_request`.

Response `200`:

```json
{ "facts": [{ "...": "a fact" }], "is_truncated": false }
```

- `facts` - the facts of every type whose point lies in the rectangle, in no particular order: unverified, confirmed, disputed and outdated ones, except a fact outdated because it was removed in OpenStreetMap, which disappears from the map (M4), and never a hidden one (M11). A geozone is in the rectangle when its point is.
- At most 1000 facts. `is_truncated` is `true` when the rectangle holds more, and the client then asks the person to zoom in.

### read_fact

`GET /api/facts/{id}`, token optional, no request body.

Response `200`:

```json
{ "fact": { "...": "a fact" } }
```

Any fact that is not hidden, in any status.

### find_nearby_facts

`POST /api/facts/nearby`, token optional. The check of M3 before a report is saved.

Request:

```json
{ "type": "high_kerb", "point": { "lat": 50.0661, "lon": 19.9878 } }
```

Response `200`:

```json
{ "facts": [{ "fact": { "...": "a fact" }, "distance_m": 8 }] }
```

The facts of the same type within 15 m of the point, OpenStreetMap facts included and hidden ones left out, nearest first (M3). The client asks whether the report is one of them: yes is `cast_vote` with `confirm` on that fact, no is `create_fact`. The service merges nothing.

### create_fact

`POST /api/facts`, token optional. Saves a point report or a geozone, sent only after the person approves its summary (M3, M5).

Request:

```json
{
  "idempotency_key": "6f1c2a9e-0b8d-4c55-9a51-3e2f7d1b9c40",
  "type": "stairs",
  "point": { "lat": 50.0661, "lon": 19.9878 },
  "description": "Three steps at the side entrance",
  "step_count": 3,
  "geozone_radius_m": null
}
```

- `idempotency_key` - a UUID the client generates once, when the person approves the summary, and sends unchanged with every attempt of the same save.
- `description` - optional, at most 500 characters once leading and trailing spaces are removed; an empty description is `null`.
- `step_count` - optional, only for `stairs`, from 1 to 999.
- `geozone_radius_m` - `null` for a point report; 10, 25, 50 or 100 for a geozone, whose `type` has to be a barrier (M5).

Response `201`:

```json
{ "fact": { "...": "a fact" } }
```

The new fact, `unverified`, with the confirmation of its author as its first vote (M4). An attempt with an `idempotency_key` already saved with the same content returns the fact of the first save with `200` and creates nothing. No operation of this contract creates sample data or edits a saved fact (M3, M5).

Errors:

| Status | `code`                   | When                                                          |
| ------ | ------------------------ | ------------------------------------------------------------- |
| 409    | `idempotency_key_reused` | The key was already used for a save with a different content. |

### cast_vote

`POST /api/facts/{id}/votes`, token optional. A confirmation that the fact is still there, or a denial that it is.

Request:

```json
{ "verdict": "confirm" }
```

`verdict` is `confirm` or `deny`.

Response `201`:

```json
{ "fact": { "...": "a fact" } }
```

The fact with its status after the vote.

Errors:

| Status | `code`          | When                                                                                                        |
| ------ | --------------- | ----------------------------------------------------------------------------------------------------------- |
| 409    | `vote_too_soon` | The same person voted on this fact less than a day ago (M4); `repeat_allowed_at` is the instant from which their next vote is accepted. |

```json
{ "error": { "code": "vote_too_soon", "repeat_allowed_at": "2026-10-04T09:12:44.120+02:00" } }
```

A vote repeated because its response was lost is refused in the same way, so a vote never counts twice. A hidden fact cannot be voted on and answers `fact_not_found` (M11).

### flag_fact

`POST /api/facts/{id}/flag`, token optional, no request body.

Response `204`, no body, also when the fact is already flagged. A flag keeps nothing about who flagged (M11).

Errors:

| Status | `code`               | When                                       |
| ------ | -------------------- | ------------------------------------------ |
| 409    | `fact_not_flaggable` | The fact is from OpenStreetMap (M11).      |

## Accounts

### create_account

`POST /api/accounts`, no token.

Request:

```json
{ "pseudonym": "Wózek_KRK", "password": "five or more characters" }
```

- `pseudonym` - leading and trailing spaces are removed, then it has 3 to 30 characters, none of them a control character of the Unicode category Cc; it is kept as it is after the trim, and it is unique without regard to letter case (M9).
- `password` - 5 to 128 characters, all accepted: printable ASCII, spaces and Unicode, with no rule of composition (M9).
- A character is a Unicode code point.

Response `201`:

```json
{ "account": { "pseudonym": "Wózek_KRK", "is_moderator": false } }
```

It does not log in: the client calls `log_in` next.

Errors:

| Status | `code`            | When                                                                                     |
| ------ | ----------------- | ---------------------------------------------------------------------------------------- |
| 409    | `pseudonym_taken` | An account has a pseudonym that differs from this one at most in letter case (M9).       |

A pseudonym or a password outside its rules is refused with `invalid_request` and its field in `fields`.

### log_in

`POST /api/sessions`, no token.

Request:

```json
{ "pseudonym": "wózek_krk", "password": "five or more characters" }
```

The pseudonym is compared after the trim and without regard to letter case.

Response `200`, with the token in the header `Session-Token`:

```json
{ "account": { "pseudonym": "Wózek_KRK", "is_moderator": false } }
```

Errors:

| Status | `code`                | When                                                                 |
| ------ | --------------------- | -------------------------------------------------------------------- |
| 401    | `invalid_credentials` | No account has this pseudonym, or the password is wrong; the two are not told apart. |

### read_own_account

`GET /api/accounts/me`, token required, no request body.

Response `200`:

```json
{ "account": { "pseudonym": "Wózek_KRK", "is_moderator": false } }
```

### delete_own_account

`DELETE /api/accounts/me`, token required, no request body.

Response `204`, no body and no `Session-Token`. The account and its pseudonym are removed, its reports and votes stay detached with their weight, and its token stops resolving (M9); the client deletes it.

## Moderation

### list_flagged_facts

`GET /api/moderation/flagged-facts`, moderator, no request body.

Response `200`:

```json
{ "facts": [{ "fact": { "...": "a fact" }, "flagged_on": "2026-10-03", "is_hidden": false }] }
```

Every flagged fact, hidden ones included so that they can be restored, the latest flag first, without anything about its author (M11).

### hide_fact

`POST /api/moderation/flagged-facts/{id}/hide`, moderator, no request body.

Response `200` with the item of `list_flagged_facts` for the fact, `is_hidden` `true`, also when it was already hidden. A hidden fact disappears from every operation that is not a moderator one (M11).

Errors:

| Status | `code`             | When                                       |
| ------ | ------------------ | ------------------------------------------ |
| 409    | `fact_not_flagged` | Only flagged content can be hidden.        |

### restore_fact

`POST /api/moderation/flagged-facts/{id}/restore`, moderator, no request body.

Response `200` with the item of `list_flagged_facts` for the fact, `is_hidden` `false`, also when it was not hidden. A restored fact counts again with the votes it still has (M11).

Errors:

| Status | `code`             | When                                       |
| ------ | ------------------ | ------------------------------------------ |
| 409    | `fact_not_flagged` | The fact is not flagged, so it is not hidden. |
````

### Step 2. `docs/product/specification.md`, version 7, and the pointers to it

2.1. Replace the whole state line, which starts "Document state:" and names version 6, with:

```text
Document state: YYYY-MM-DD, version 7 - a route request and an address search without the identity of an account, outdated facts on the map, the pseudonym and an expired session, decided in phase B of `plans_finished/api_contract/`
```

2.2. In the section Why this document exists, after the sentence "Version 6 makes the target database schema in `docs/product/schema.md`, decided in `plans_finished/fact_schema/`, part of this specification, without changing any rule of version 5." insert:

```text
 Version 7 adds, from phase B of `plans_finished/api_contract/`, that a route request and an address search carry no identity of an account, that an outdated fact stays on the map unless it was removed in OpenStreetMap, the length of a pseudonym and the refusal of a request with an expired session; the requests and responses that carry the rules of this document are in `docs/product/api_contract.md`, which is not part of this specification.
```

2.3. In M2, at the end of the paragraph that begins "A walking route from A to B within Kraków.", after "it is not stored, not logged and not linked to the account.", insert:

```text
 A route request carries no identity of an account, even when the person is logged in, so the current location and the preferences of the profile never travel together with one.
```

2.4. In M2, section Address search, after the item "- The search returns only places within Kraków.", insert the item:

```text
- The search text travels without any identity of an account, even when the person is logged in.
```

2.5. In M4, after the item that begins "- A status does not change with time alone.", insert the item:

```text
- An outdated fact stays on the map with its status, so that the user judges it and can confirm it again; only a fact outdated because it was removed in OpenStreetMap disappears from the map.
```

2.6. In M9, after the sentence "A pseudonym is unique without regard to letter case, and the pseudonym of a deleted account can be taken again.", insert:

```text
 A pseudonym has 3 to 30 characters after leading and trailing spaces are removed, and contains no control characters.
```

2.7. In M9, after the sentence "The session remains active when the browser is closed and reopened.", insert:

```text
 A route request and an address search carry no identity of an account (M2), so they do not renew this period. A request made with an expired session, or with the session of a deleted account, is refused and the person is told that they are logged out; it is never handled as a contribution without an account, so nobody contributes with the lower weight of M4 while believing they are logged in.
```

2.8. In the section Open questions, replace "None at version 6." with "None at version 7."

2.9. In the section Decision provenance, after the item that starts "- Version 6:", insert the item:

```text
- Version 7: that a route request and an address search carry no identity of an account (M2, M9), that an outdated fact stays on the map unless it was removed in OpenStreetMap (M4), the length of a pseudonym and the refusal of a request with an expired session (M9) were decided by the user on 2026-10-03 in phase B of `plans_finished/api_contract/`, as product behavior version 6 did not describe, and the user chose at the gate of its PRD to bring them into this specification; the wording was proposed by the agent. The user approved this version on YYYY-MM-DD.
```

2.10. The pointers to the version of the specification follow (D-3, F-19): in `PRODUCT.md`, "`docs/product/specification.md`, version 6" becomes "`docs/product/specification.md`, version 7" in both places; in `plans/mvp/MVP_PLAN.md`, Goal, "`docs/product/specification.md`, version 6," becomes "`docs/product/specification.md`, version 7,"; in `plans/mvp/MVP_PRD.md`, "of the specification, version 6," in Scope and "The rules are those of the specification, version 6," in Domain rules name version 7, and the item of its section Domain rules that begins "Changed after the gate on 2026-10-03, to follow version 4" gets this sentence appended:

```text
 Scope and the first sentence of this section name version 7 since YYYY-MM-DD, which adds the rules of `plans_finished/api_contract/` on a route request and an address search without an account, outdated facts on the map, the pseudonym and an expired session; a route request and an address search carry no account, so they are not requests of the session of FR-12 and AC-11, and nothing else of this PRD changes.
```

The mentions of version 6 as the version that made the schema part of the specification - `docs/product/schema.md` line 3, `docs/standards/README.md` line 54 and D-11 of `plans/mvp/MVP_PLAN.md` - stay as they are.

### Step 3. `plans/mvp/MVP_PLAN.md`

3.1. In Decisions, after the last decision, append the next free decision. On the tree of 2026-10-03 it is D-12; if another initiative took that number in the meantime, the next free number replaces D-12 here, in 3.2, in 3.4 and in 3.5:

```text
D-12. Programming interface contract, settling the former Q-9. Every operation between the clients and the service, with its request, responses and errors, is in `docs/product/api_contract.md`, with the decisions of `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-1 - D-18. Constraints for the rest of this plan: the clients and the service use the operations, codes and shapes of that document, and a change of an operation is a change of that document first (D-2 there); the session token of D-8 travels in the header `Authorization: Bearer` and comes back renewed in the response header `Session-Token`, and a request with an expired token is refused, never handled without an account (D-4, D-5 there); a route request, an address search, an account creation and a login carry no token (D-6 there); a saved report or geozone carries an idempotency key that the stored data of D-11 does not hold yet, which the task `SCHEMA_REVISION` of `plans_finished/schema_revision/` answers (D-9 there); the implementation of the operations goes with Q-11. Decided by the user on 2026-10-03 in phase B of `plans_finished/api_contract/`, approving the contract in place of the frontend person, whose confirmation is still to be obtained; the rest by the agent at C:40.
```

3.2. In Risks, in the item that begins "The open questions depend on each other", replace "Q-9 depends on D-11 and Q-6 and not on Q-1 (U-5 of `plans_finished/consistency_check/`), and `plans_finished/api_contract/` is settled after `plans_finished/account_sessions/` (U-3 of `plans_finished/dependency_check/`);" with "the former Q-9 is settled as D-12 after D-11 and D-8, not depending on Q-1 (U-5 of `plans_finished/consistency_check/`), in the order of U-3 of `plans_finished/dependency_check/`;".

3.3. In Open questions, remove the item that begins "- Q-9. Contract of the programming interface between the frontend and the backend".

3.4. In Open questions, in the item Q-11, replace "- Q-11. The backend architecture with the worker. Decided in this plan, owner: backend." with "- Q-11. The backend architecture with the worker, owner: backend. On 2026-10-03 the user decided, in phase B of `plans_finished/api_contract/`, that it is decided in a separate initiative set up later, and that the implementation of the operations of D-12 goes with it."

3.5. In Supplementary files, after the item "- `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md`, the decision behind D-11.", append the item "- `plans_finished/api_contract/API_CONTRACT_PLAN.md`, the decision behind D-12."

### Step 4. `docs/standards/standard_errors.md`

4.1. In Scope and boundaries, replace "- specific API response codes and bodies - they are decided by the product specification pointed to in `CLAUDE.md`." with "- specific API response codes and bodies - they are decided by the programming interface contract `docs/product/api_contract.md`, under the product specification pointed to in `CLAUDE.md`."

4.2. In Reaction while handling a request, replace "in the shape set by the specification." with "in the shape set by the programming interface contract `docs/product/api_contract.md`."

### Step 5. `docs/standards/standard_naming.md`

In Scope and boundaries, replace "- path names in the programming interface - those are settled by the product specification indicated in `CLAUDE.md`." with "- path names in the programming interface - those are settled by the programming interface contract `docs/product/api_contract.md`."

### Step 6. `docs/standards/README.md`

6.1. In the section Project documents outside the standards, at the end of the item that begins "- `docs/product/` - the product specification", after "Its first version, written on 2026-10-03, settles the target group and the MVP scope.", insert " Next to it, `docs/product/api_contract.md` is the contract of the programming interface between the clients and the service, decided in `plans_finished/api_contract/`; it is not part of the specification, which prevails over it."

6.2. In the table What to open before a task, after the row "Frontend code, the map, interface texts", insert the row "| A request, a response, a path or an error code of the programming interface | `docs/product/api_contract.md` and the product specification |", and realign the table with prettier.

### Step 7. `docs/standards/decision_registry.md`

7.1. In the entry Technical directions of the MVP plan, item Blocks, replace "`plans_finished/account_sessions/` and `plans_finished/api_contract/` are in their interviews." with "`plans_finished/account_sessions/` is decided (`plans/mvp/MVP_PLAN.md` D-8); `plans_finished/api_contract/` decided the contract `docs/product/api_contract.md` (`plans/mvp/MVP_PLAN.md` D-12), and on 2026-10-03 the user moved the backend architecture of Q-11, with the implementation of the operations of that contract, to a separate initiative set up later."

7.2. In the same entry, item Condition, replace "and phase B of `plans/mvp/` resumes with the backend architecture." with "and the backend architecture of Q-11 is decided in its separate initiative."

### Step 8. `PRODUCT.md`

8.1. In the list Undecided, replace the item "- The routing engine (`plans_finished/routing_engine/`) and the contract of the programming interface (`plans_finished/api_contract/`)." with "- The backend architecture with the worker, which the user moved on 2026-10-03 from Q-11 of `plans/mvp/MVP_PLAN.md` to a separate initiative set up later." The routing engine is already D-9 of the MVP plan (F-21).

8.2. In the section Evidence on Hand, after the item that begins "- `docs/product/specification.md`, version", insert the item "- `docs/product/api_contract.md`: every operation between the clients and the service, with its request, responses and errors."

### Step 9. `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md`

9.1. In Current state, after the item "- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).", insert the item:

```text
- `plans_finished/api_contract/` decided on 2026-10-03 (`docs/product/api_contract.md`, operation `create_fact`; `plans_finished/api_contract/API_CONTRACT_PLAN.md` D-9) that saving a report or a geozone carries an idempotency key, a UUID the client generates once per approved summary and repeats with every attempt of the same save, and that an attempt with a key already saved with the same content returns the first fact instead of creating a second one, as `docs/standards/standard_idempotency.md` requires. `docs/product/schema.md` holds no column for that key, so the stored data needs a change of the target schema, which `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md` D-21 allows only through a new version of the specification approved by the user.
```

9.2. In Open questions, after question 1, append:

```text
2. How does the stored data hold the idempotency key of a saved report or geozone that `docs/product/api_contract.md` requires (Current state), and which new version of the specification brings it into `docs/product/schema.md`? `Block: yes` (category: database schema)
```

## Rollout order

1. Run `git status --short` and read every file of steps 2 - 9 again; a quoted passage that no longer matches stops its step (F-24).
2. Step 1 and step 2.1 - 2.9, without the approval date.
3. Show the user `docs/product/api_contract.md` and the diff of `docs/product/specification.md`, and ask for the approval of both: of the contract in place of the frontend person (D-10) and of version 7 (D-3). On approval, write its date into step 1 and steps 2.1 and 2.9 and continue; on any requested change, stop and change this plan first, because the contract is what the frontend and the later implementation build on.
4. Step 2.10 and steps 3 - 9, in any order.
5. `npx --no-install prettier --write` on every changed or created markdown file, then the checks of the Definition of Done.

Steps for a human: the approval of step 3; the confirmation of the contract by the frontend person, after which any change is agreed with that person first; setting up the separate initiative of Q-11, which also implements the operations; the answer to question 2 of `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md`; the commit and the Merge Request of the changed files.

## Definition of Done

- `docs/product/api_contract.md` exists with the content of step 1 and the date of the user's approval in its state line.
- `docs/product/specification.md` carries exactly the changes of steps 2.1 - 2.9, with the date of the user's approval, and no rule of version 6 changes except by the additions of step 2.
- `PRODUCT.md`, `plans/mvp/MVP_PLAN.md`, `plans/mvp/MVP_PRD.md`, `docs/standards/standard_errors.md`, `docs/standards/standard_naming.md`, `docs/standards/README.md`, `docs/standards/decision_registry.md` and `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md` carry exactly the changes of steps 2.10 - 9, and `plans_finished/` is unchanged.
- `plans/mvp/MVP_PLAN.md` has the decision of step 3.1, no item that begins with Q-9 under Open questions, and the item Q-11 of step 3.4.
- `npx --no-install prettier --check` passes on every changed or created markdown file and on the files of `plans_finished/api_contract/`.
- The changed and created files contain none of the characters forbidden by `docs/standards/standard_formatting.md` and no bold in prose.
- `venv/Scripts/python.exe -m pytest tests/architecture -o addopts=-ra` reports no violation in a file this plan changes or creates or in `plans_finished/api_contract/`, the check of this closed plan by `tests/architecture/test_plan_document_contract.py` included.
- The review of `plan-implement` finds no blocking issue.

## Risks

- Another session worked on the same tree while this plan was written (F-24); a passage quoted here may change before the implementation, and its step then stops.
- The frontend person has not confirmed the contract yet (D-10). A change asked for later changes the contract and whatever was already built on it.
- The repetition of `create_fact` cannot be implemented until question 2 of `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md` is answered (D-9). If the db person rejects a stored key, the contract changes, or the user records a deviation from `docs/standards/standard_idempotency.md`.
- A vote repeated after a lost response gets `vote_too_soon`, so the client cannot tell its own first vote from an earlier one of the same day (D-16).
- A token in the storage of the browser can be read by a script running on the page (D-4); the frontend loads no script from another host (F-10), which narrows that risk without removing it.
- A person who only plans routes and searches addresses for more than 24 hours is logged out, because those requests carry no token (D-6).
- The specification does not say what happens to a start or a destination far outside Kraków; the contract refuses nothing for it, and the routing engine joins the nearest stretch with a long segment in the state no data (F-11). It is a question for the user when the implementation meets it.
- The limit of 1000 facts in an area is not measured against the density of OpenStreetMap facts in Kraków (D-14); a screen of the city centre may be cut more often than expected.
- A geozone whose point lies outside the rectangle of `list_facts_in_area` is not listed even when its circle reaches into it.
- `find_nearby_facts` also returns a fact outdated because it was removed in OpenStreetMap, as FR-13 of `plans_finished/fact_schema/FACT_SCHEMA_PRD.md` excludes only hidden facts; a confirmation of such a fact follows the status rule of M4.
- No initiative of Q-11 exists yet, so nobody is scheduled to implement the operations before the Kraków deadline at 11:00 on 4 October 2026 (D-1).
- When this initiative moves to `plans_finished/`, the references to `plans_finished/api_contract/` in `plans/mvp/MVP_PLAN.md`, `docs/standards/decision_registry.md`, `docs/standards/README.md`, `docs/product/api_contract.md`, `docs/product/specification.md` and `plans_finished/schema_revision/SCHEMA_REVISION_SHAPE.md` follow the move, as ch. 4.6 of `docs/standards/standard_agentic_workflow.md` requires.

## Open questions

None.

## Supplementary files

- `plans_finished/api_contract/API_CONTRACT_PRD.md`, the requirements this plan meets.
- `plans_finished/api_contract/API_CONTRACT_SHAPE.md`, the scope and the scenarios behind the PRD.
- `plans_finished/api_contract/API_CONTRACT_SEED.md`, the verbatim request.
- `docs/product/specification.md` and `docs/product/schema.md`, the behavior and the stored data behind the operations.
- `plans_finished/account_sessions/ACCOUNT_SESSIONS_PLAN.md`, the session behind D-4 - D-6.
- `plans_finished/geocoding/GEOCODING_PLAN.md`, the address search behind `search_address`.
- `plans_finished/routing_engine/ROUTING_ENGINE_PLAN.md`, the route behind `plan_route`.
- `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`, the inputs of the first consumer.
- `plans_finished/fact_schema/FACT_SCHEMA_PLAN.md`, the schema decisions behind the fact object, the vote limit and D-9.
