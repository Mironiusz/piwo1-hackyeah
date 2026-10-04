# Programming interface contract

Document state: 2026-10-04, approved by the user in place of Kuber and Adrian, whose confirmation is still to be obtained; the pseudonym rule is aligned with specification M9 by `plans/accounts/ACCOUNTS_SHAPE.md`, its letters made explicit and a lone surrogate refused by Kuba on 2026-10-04 for `plans/accounts/` (`ACCOUNTS_PLAN.md` D-3, `ACCOUNTS_REVIEW.md`), with the confirmation of Adrian still to be obtained, and `cast_vote` changed on 2026-10-04 with version 13 of `docs/product/specification.md`; `plan_route` changed on 2026-10-04 by `plans/route_planning/` with the state `not_assessed` and the refusal `point_outside_krakow`, to be confirmed by Kuber and Adrian; `find_nearby_facts` changed on 2026-10-04 with version 17 of the specification to exclude facts removed in OpenStreetMap, approved by the user with Kuber and Adrian's confirmation still outstanding; the identifying inputs for anonymous votes and reports are aligned with version 18 of the specification, with Kuber and Adrian's confirmation still outstanding

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
- For a vote or a report without an account the service derives the identifier from the IP address and User-Agent header of the request only (M9). Identical pairs share the daily vote limit and one identity for the latest-vote status rule. The client sends no additional identifier, and no response carries it.

## Request logs and failures

- The entry the service logs for a request carries only the name of the operation, as the headings of this document name it, the response status, the duration and the request identifier. It carries no body of the request or the response, no header, no pseudonym, no account identifier, no location, no preferences, no IP address and no browser characteristics. A failure may add a separate diagnostic entry with the traceback.
- No response carries an exception, a query fragment, a database object name, a connection string or anything about the infrastructure.

## Errors

An error response has the body:

```json
{ "error": { "code": "invalid_request", "fields": ["start.lat"] } }
```

`code` is always present; another field of `error` exists only for the code that names it. The codes every operation can return:

| Status | `code`                    | When                                                                                                                                   |
| ------ | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 422    | `invalid_request`         | The body is not JSON, or a field is missing, unknown, of a wrong type or outside the rules of its operation; `fields` lists its paths. |
| 401    | `authentication_required` | The operation needs an account and the request has no token.                                                                           |
| 401    | `session_expired`         | The token is malformed, wrongly signed, expired or of an account that no longer exists.                                                |
| 403    | `moderator_role_required` | The account does not hold the moderator role at the moment of the request.                                                             |
| 404    | `not_found`               | No operation exists at this method and path.                                                                                           |
| 404    | `fact_not_found`          | No fact has the identifier of the path, or the fact is hidden and the operation is not a moderator one (M11).                          |
| 500    | `internal_error`          | The service failed in a way this document does not name.                                                                               |

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
- `state` - `barrier`, `no_barrier`, `partial_data` or `no_data`, the four states of M7, decided by the service; or `not_assessed` for every segment, the straight stretches included, when `avoid` is empty, and in no other case (M1, M7). The client draws each with its own color and its own icon or line pattern.
- `missing_attributes` - for a segment in `partial_data` or `no_data`, the attributes behind the barriers of the profile that are not known, from `kerbs`, `surface`, `incline`, `width` and `steps`, in this order; empty in the other states, and empty for `not_assessed` (M7, M8).
- `is_marked_wheelchair_no` - `true` when OpenStreetMap marks the way as not accessible for wheelchairs; the list then says so (M7, M8).
- `profile_barriers`, `additional_barriers` and `amenities` - the three groups of the list for the route (M8), each in order along the route: the barriers of the profile on the route, the barriers outside the profile on the route, and the amenities of the profile within 50 m of the route. Only `profile_barriers` and `amenities` appear on the map (M7).

A route fact is a fact with two more fields:

```json
{ "...": "the fields of a fact", "distance_from_start_m": 230, "is_overruled_by_osm": false }
```

- `distance_from_start_m` - the distance along the route from the start to the place of the fact on the route.
- `is_overruled_by_osm` - `true` for a report that OpenStreetMap contradicts and that has not reached the threshold of M4: the client shows it as an unverified report icon, and the segment follows OpenStreetMap (M7).

Errors:

| Status | `code`                 | When                                                                                                                                                                                             |
| ------ | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 422    | `point_outside_krakow` | The start or the destination lies outside the administrative boundary of Kraków of the copy in use (M2); `points` lists `start`, `destination` or both, in this order, and no route is computed. |
| 503    | `routing_unavailable`  | No route can be computed right now (M10). The response carries no route, and no route is guessed.                                                                                                |

```json
{ "error": { "code": "point_outside_krakow", "points": ["start"] } }
```

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

| Status | `code`                       | When                                                                                                                                                |
| ------ | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 422    | `invalid_search_text`        | `text` has more than 200 characters as received, or is empty once its spaces are trimmed and collapsed and the words "ul." and "ulica" are removed. |
| 503    | `address_search_unavailable` | The search cannot be answered right now; the client says so with a message different from nothing found (M2).                                       |

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

The facts of the same type within 15 m of the point, OpenStreetMap facts and ordinary outdated facts included, hidden facts and facts outdated because they were removed in OpenStreetMap left out, nearest first (M3). The client asks whether the report is one of them: yes is `cast_vote` with `confirm` on that fact, no is `create_fact`. The service merges nothing.

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

| Status | `code`          | When                                                                                                                                                                                                      |
| ------ | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 409    | `vote_too_soon` | The same person already voted on this fact on the same calendar day in Europe/Warsaw (M4); `repeat_allowed_at` is the start of the next calendar day, the instant from which their next vote is accepted. |

```json
{ "error": { "code": "vote_too_soon", "repeat_allowed_at": "2026-10-05T00:00:00.000+02:00" } }
```

A vote repeated because its response was lost is refused in the same way when it arrives on the same calendar day; repeated after midnight it is accepted as a new vote, which adds no weight, because only the latest vote of a person counts. A hidden fact cannot be voted on and answers `fact_not_found` (M11).

### flag_fact

`POST /api/facts/{id}/flag`, token optional, no request body.

Response `204`, no body, also when the fact is already flagged. A flag keeps nothing about who flagged (M11).

Errors:

| Status | `code`               | When                                  |
| ------ | -------------------- | ------------------------------------- |
| 409    | `fact_not_flaggable` | The fact is from OpenStreetMap (M11). |

## Accounts

### create_account

`POST /api/accounts`, no token.

Request:

```json
{ "pseudonym": "Wózek_KRK", "password": "five or more characters" }
```

- `pseudonym` - leading and trailing spaces are removed, then it has 3 to 30 characters: letters, the Polish ones included, digits, the underscore and the hyphen; it is kept as it is after the trim, and it is unique without regard to letter case (M9). The letters are the 26 Latin letters and the nine Polish letters `ąćęłńóśźż`, each in both cases, and the digits are `0` - `9`; any other character, a letter of another alphabet or a decomposed Polish letter included, is refused.
- `password` - 5 to 128 characters, all accepted: printable ASCII, spaces and Unicode, with no rule of composition (M9).
- A character is a Unicode code point. A pseudonym or a password holding a lone surrogate, which no text in UTF-8 can carry, is refused with `invalid_request` and its field.

Response `201`:

```json
{ "account": { "pseudonym": "Wózek_KRK", "is_moderator": false } }
```

It does not log in: the client calls `log_in` next.

Errors:

| Status | `code`            | When                                                                               |
| ------ | ----------------- | ---------------------------------------------------------------------------------- |
| 409    | `pseudonym_taken` | An account has a pseudonym that differs from this one at most in letter case (M9). |

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

| Status | `code`                | When                                                                                 |
| ------ | --------------------- | ------------------------------------------------------------------------------------ |
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

| Status | `code`             | When                                |
| ------ | ------------------ | ----------------------------------- |
| 409    | `fact_not_flagged` | Only flagged content can be hidden. |

### restore_fact

`POST /api/moderation/flagged-facts/{id}/restore`, moderator, no request body.

Response `200` with the item of `list_flagged_facts` for the fact, `is_hidden` `false`, also when it was not hidden. A restored fact counts again with the votes it still has (M11).

Errors:

| Status | `code`             | When                                          |
| ------ | ------------------ | --------------------------------------------- |
| 409    | `fact_not_flagged` | The fact is not flagged, so it is not hidden. |
