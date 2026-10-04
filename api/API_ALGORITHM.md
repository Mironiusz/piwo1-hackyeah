# Programming interface algorithm

Document state: 2026-10-04

## Algorithm goal

A client gets either the answer of an operation in the shape of `docs/product/api_contract.md` or one contracted refusal, and nothing of its request reaches a log or another system beyond what the contract allows.

## Domain concepts

- Operation: one entry of the contract, named in the request log by its name, for example `plan_route`.
- Refusal: an answer with an error body of one code, with `fields` only for `invalid_request` and `points` only for `point_outside_krakow`.

## General process map

A request gets its identifier, is matched to an operation, is checked against the request model of that operation, is handed to the service layer, and its answer or refusal is written; one log entry closes it.

## Detailed run order

For `plan_route`:

1. The body must be a JSON object with exactly `start`, `destination`, `avoid` and `need`. A point holds `lat` between -90 and 90 and `lon` between -180 and 180, both numbers, not strings. `avoid` holds barrier types and `need` amenity types of M3, each at most once, possibly none. Anything else is refused with `invalid_request` and the paths of the wrong fields, for example `start.lat`, `avoid.1` or `need`, and no route is planned.
2. The two points and the two sets go to `resolve_route` of the service layer.
3. A point outside the boundary of Kraków ends with 422 `point_outside_krakow` and `points`, which names `start`, `destination` or both in this order.
4. A route that cannot be computed now ends with 503 `routing_unavailable` and no route.
5. Otherwise the answer is 200 with the route, its segments, its list and the alternative or `null`.

When the process starts, the graph of the copy in use is built once before the first request is accepted; a failure there only postpones the build to the first route request.

## Domain rules

- The state `not_assessed` is passed to the client as the service decides it; the layer derives nothing from the request.
- The header `Authorization` changes nothing for `plan_route`, and no token is answered.

## Reconcile and deduplication

None: the layer keeps nothing between requests.

## Diagnostics and summary

The request log names the method, the operation, the status and the duration. No entry of this layer holds a coordinate, a body or an address of a request; an uncaught failure is logged with its traceback under the identifier of its request and answered `internal_error`.

## Accounts and sessions

The boundary decides for every request whether it carries a session, which session it is, and whether its response carries a renewed token, so that every client sees one behavior of sessions whatever operation it calls (`docs/product/api_contract.md`, section Sessions and actors; `plans_finished/accounts/ACCOUNTS_PLAN.md` D-7, D-8).

```text
request -> operation without a token: answer, no Session-Token
        -> no header Authorization: a person without an account -> authentication_required where an account is needed
        -> header present: resolve the session -> session_expired, or the actor with a renewed token
           -> moderator_role_required where the role is missing
           -> answer, with the renewed token in Session-Token
```

- `plan_route`, `search_address`, `create_account` and `log_in` take no token: the header `Authorization` changes nothing for them and their response carries no `Session-Token`.
- A request without the header `Authorization` is a person without an account. A request whose header does not resolve to an existing account, more than one such header included, is refused as `session_expired` and is never handled as a person without an account.
- A response to a request that carried a valid token carries the renewed token, on success and on a refusal the operation names, such as `moderator_role_required` or `invalid_request` of its body. A refusal as `session_expired` carries none, because the client deletes its token on it. A successful `delete_own_account` answers 204 with none, because its account no longer exists. `log_in` gives the token of its new session the same way. A failure the contract does not name, `internal_error`, carries no renewed token, and the token the client keeps stays valid until its own expiry.
- A body of `create_account` or `log_in` with another field, a missing field or a value that is not a string is refused as `invalid_request` with its paths before any rule of accounts runs; a pseudonym or a password outside its rules is refused as `invalid_request` with its field by the service layer.
- No pseudonym, password, token, header or account identifier of an account operation reaches a log entry or a response other than the one the contract names.

## Community facts

The boundary of the nine operations of the community facts turns a request into one call of `service/community_facts.py` and its answer or refusal into the body of `docs/product/api_contract.md`, sections Facts and Moderation (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-2, D-3, D-7, D-8).

```text
request -> session: a bad token -> session_expired, nothing read or written
        -> moderator operation: no token -> authentication_required, no role now -> moderator_role_required
        -> body and path against the strict model -> invalid_request with the paths
        -> save or vote without an account: read the client address and User-Agent
        -> service -> its refusal -> its code, or the answer -> 200, 201 or 204
```

1. The session is resolved first. A token that does not resolve is refused as `session_expired` and is never turned into a person without an account, so a save or a vote with an expired token writes nothing.
2. The body and the identifier of the path are checked against the model of the operation; a refusal names the paths and the service is not called.
3. A save or a vote of a person without an account reads the client address uvicorn resolved and the User-Agent, and passes them to the service, which hashes them; an account passes its `AccountActor`. No other operation reads either input, and no log entry holds them.
4. The service decides. `list_facts_in_area` answers the facts and `is_truncated`, `read_fact` the fact, `find_nearby_facts` each fact with its distance, `create_fact` 201 for a first save and 200 for a repeated one with the same fact, `cast_vote` 201 with the fact after the vote, `flag_fact` 204 without a body, `list_flagged_facts` every moderator item and `hide_fact` and `restore_fact` the moderator item of the fact.
5. A refusal of the service becomes its code: `invalid_request` with the paths, `fact_not_found`, `idempotency_key_reused`, `vote_too_soon` with the next midnight, `fact_not_flaggable` or `fact_not_flagged`. A response to a valid session carries the renewed token on success and on these refusals alike.

No body, coordinate, description, address, User-Agent, token or hash reaches a log entry; the request log names the operation, the status and the duration only.
