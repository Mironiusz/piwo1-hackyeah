# Programming interface layer

Document state: 2026-10-04

## Module role

The layer is the boundary of the service toward its clients over HTTP. It builds the one FastAPI application, refuses a request outside the contract of `docs/product/api_contract.md` before any rule runs, hands an accepted request to the service layer, and turns the answer or a named refusal of that layer into the body and the status the contract names. It decides no product rule and reads no database: it imports only `service` and `config` (`docs/standards/standard_architecture.md`).

## Public interface

| Name                   | Input                                                 | Output                                                                                                                                                 |
| ---------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `build_app`            | Nothing                                               | The application with every operation, its refusals, the lifespan of the route graph and the request log                                                |
| `build_error_response` | Code, status, `fields`, `points`, `repeat_allowed_at` | The contracted error body; `fields` only for `invalid_request`, `points` only for `point_outside_krakow`, `repeat_allowed_at` only for `vote_too_soon` |
| `apply_error_handlers` | Application                                           | The answers of a validation failure, an unmatched operation and an uncaught error                                                                      |
| `plan_route`           | `POST /api/routes` with `RouteRequestBody`            | The response 200 of the contract, or `invalid_request`, `point_outside_krakow`, `routing_unavailable`                                                  |
| `apply_route_routes`   | Application                                           | `plan_route` and the answers of `RoutingUnavailableError` and `PointOutsideKrakowError`                                                                |
| `apply_route_lifespan` | Application                                           | The graph of the copy in use built in the thread pool when the process starts                                                                          |
| `build_fact_body`      | `FactView`                                            | The shared object Fact of the contract                                                                                                                 |

## Technical inputs and outputs

A request arrives as JSON over HTTP; the bind address, the port and the trusted proxy come from the configuration facade through `__main__.py`, which passes `proxy_headers=True` and the list of `API_TRUSTED_PROXY_ADDRESSES` to uvicorn explicitly, so the client address of a request is the rightmost untrusted entry of X-Forwarded-For only behind that proxy, and the peer of the connection otherwise. The answer is JSON. The only log entry of a request is the one `RequestContextMiddleware` writes: the method, the name of the operation, the status and the duration, with no address, query or body.

## Operating modes

One mode: one process of `python -m api`, started by hand or by the container of the demo.

## File structure

```text
api/
  __main__.py         start of one process
  app.py              the application and its operations
  errors.py           the error envelope and the shared failure answers
  request_context.py  the request identifier and the request log
  route.py            plan_route, its request model, its refusals and the lifespan of the route graph
  point_body.py       the one point object of the contract
  fact_body.py        the shared object Fact of the contract and the bodies of the community facts
  facts.py            the six public operations of the community facts
  moderation.py       the three moderator operations
  fact_models.py      the request models of the community facts
  fact_errors.py      the answers of the refusals of the community facts
  fact_identity.py    the address and the User-Agent of a person without an account
  address_search.py   search_address of plans_finished/address_search/
  accounts.py         the account operations of plans_finished/accounts/
  sessions.py         the session of a request of plans_finished/accounts/
```

## File responsibilities

`point_body.py` holds `PointBody`, the one point object of every operation, and `route.py` holds `RouteRequestBody`; both are strict Pydantic models that refuse an unknown field, a string for a number, a latitude outside -90 - 90, a longitude outside -180 - 180, a type outside the closed lists of M3 and a type repeated in `avoid` or `need`. The endpoint is a plain `def`, so FastAPI runs it in its thread pool while the service waits for the database and the routing service. The route of `plan_route` is named `plan_route`, so the request log names the operation of the contract. `fact_body.py` writes `osm_edited_on` only for a fact of the source `openstreetmap` and sets `can_be_flagged` false only for it, and writes nothing about the persons behind the votes or their weights (M9, M11). `address_search.py`, `accounts.py` and `sessions.py` belong to `plans_finished/address_search/` and `plans_finished/accounts/`.

## Main records and contracts

The answer of `plan_route` is built from `RouteAnswer` of `service/route_planning.py`: `osm_copy_date` as `YYYY-MM-DD`, every line as pairs of longitude and latitude, every state and missing attribute as its value, and every fact of a list as the shared object Fact with `distance_from_start_m` and `is_overruled_by_osm`. The refusals are `{ "error": { "code": "routing_unavailable" } }` with 503 and `{ "error": { "code": "point_outside_krakow", "points": [...] } }` with 422.

## Architectural decisions

The header `Authorization` is not read by `plan_route`, and its answer carries no `Session-Token`, because the operation takes no token (section Sessions and actors of the contract). The fields `route_kind`, `public_transport_unavailable` and `public_transport` of a segment, added to the contract by `plans/public_transport_routing/`, are not handled yet: that initiative adds them to this endpoint in its stage 2. Tests in `tests/api/` replace `resolve_route` at its seam and build the application with invented settings, so they need neither a database nor a routing service.

## Summary

Every request passes the request log and the error envelope; an accepted `plan_route` request becomes one call of `resolve_route`, and its answer or one of its two refusals becomes the body of the contract.

## Accounts

`accounts.py` and `sessions.py` hold the four account operations of `plans_finished/accounts/` and the shared handling of sessions every operation with a token depends on.

| Name                    | Input                              | Output                                                                                                         |
| ----------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `apply_account_routes`  | Application                        | The account router, the answers of its refusals, the session refusals and `SessionTokenMiddleware`             |
| `fetch_request_session` | Request                            | `SessionResolution`, for an operation open to a person without an account                                      |
| `fetch_account_actor`   | `SessionResolution` of the request | `AccountActor`, for an operation that needs an account, or `authentication_required`, `session_expired`        |
| `fetch_moderator_actor` | `SessionResolution` of the request | `AccountActor` holding the role now, for a moderator operation, or `moderator_role_required` and the two above |
| `apply_session_token`   | Request, token or `None`           | The token the response of the request carries in `Session-Token`, or none                                      |

An operation that takes no token depends on none of the three dependencies, so it ignores the header `Authorization` and its response carries no `Session-Token`.

`accounts.py` holds `ACCOUNTS_ROUTER` with the routes `create_account`, `log_in`, `read_own_account` and `delete_own_account`, and the request models `CreateAccountRequest` and `LogInRequest` of `AccountCredentialsRequest`: two `StrictStr` fields and no other. It passes `fetch_business_now()` to a registration, for the creation instant of the account, and `fetch_utc_now()` to a login, for the expiry of its token. `InvalidAccountInputError` becomes `invalid_request` with its field, `PseudonymTakenError` `pseudonym_taken` with 409 and `InvalidCredentialsError` `invalid_credentials` with 401.

`sessions.py` holds the three dependencies, `apply_session_token`, `SessionTokenMiddleware`, a pure ASGI middleware that writes the kept token into `Session-Token` when the response starts, and `apply_session_error_handlers`, which answers `SessionExpiredError` as `session_expired` and `AuthenticationRequiredError` as `authentication_required`, both 401, and `ModeratorRoleRequiredError` as `moderator_role_required` with 403. A request with more than one header `Authorization` is refused as an expired session.

The renewed token travels through the state of the request, not through a return value, because a dependency alone cannot reach a response built by an exception handler; the middleware therefore adds it to a success and to a handled refusal alike (`plans_finished/accounts/ACCOUNTS_PLAN.md` D-8). The answer of `session_expired` clears it, and `delete_own_account` clears it after the deletion, so neither carries a token. `build_app()` calls `apply_account_routes` before it adds `RequestContextMiddleware`, so the correlation middleware stays outermost. A response of `internal_error` built outside the handlers passes neither middleware and carries no renewed token. The tests of `tests/api/test_accounts_api_integration.py` replace the rules layer and build the client without the lifespan of the application.

## Community facts

`facts.py`, `moderation.py`, `fact_models.py`, `fact_errors.py` and `fact_identity.py` hold the nine operations of `docs/product/api_contract.md`, sections Facts and Moderation, built by `plans/community_facts_api/` on `service/community_facts.py`.

| Name                                                                                                                              | Input                                                        | Output                                                                                          |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `list_facts_in_area`                                                                                                              | `POST /api/facts/in-area` with `FactAreaRequest`             | 200 with `facts` and `is_truncated`                                                             |
| `read_fact`                                                                                                                       | `GET /api/facts/{id}`                                        | 200 with `fact`, or `fact_not_found`                                                            |
| `find_nearby_facts`                                                                                                               | `POST /api/facts/nearby` with `NearbyFactsRequest`           | 200 with `facts`, each a fact and `distance_m`                                                  |
| `create_fact`                                                                                                                     | `POST /api/facts` with `CreateFactRequest`                   | 201 for a first save, 200 for a repeated one, or `idempotency_key_reused`, `fact_not_found`     |
| `cast_vote`                                                                                                                       | `POST /api/facts/{id}/votes` with `CastVoteRequest`          | 201 with the fact after the vote, or `vote_too_soon` with `repeat_allowed_at`, `fact_not_found` |
| `flag_fact`                                                                                                                       | `POST /api/facts/{id}/flag`                                  | 204 without a body, or `fact_not_flaggable`, `fact_not_found`                                   |
| `list_flagged_facts`                                                                                                              | `GET /api/moderation/flagged-facts`, moderator               | 200 with every moderator item                                                                   |
| `hide_fact`, `restore_fact`                                                                                                       | `POST /api/moderation/flagged-facts/{id}/hide` or `/restore` | 200 with the moderator item, or `fact_not_flagged`, `fact_not_found`                            |
| `apply_fact_routes`                                                                                                               | Application                                                  | The six public routes and the answers of the six refusals of the community facts                |
| `apply_moderation_routes`                                                                                                         | Application                                                  | The three moderator routes                                                                      |
| `fetch_anonymous_voter_input`                                                                                                     | Request                                                      | `AnonymousVoterInput` of the client address and the User-Agent                                  |
| `build_area_facts_body`, `build_nearby_facts_body`, `build_flagged_fact_body`, `build_flagged_facts_body`, `build_fact_item_body` | The views of the service                                     | The bodies of the contract, each fact through `build_fact_body`                                 |

The six public operations take an optional token through `fetch_request_session`, and the three moderator ones need a current moderator through `fetch_moderator_actor`; the operations that do not use the resolved actor declare the dependency in `dependencies`, so it still refuses a bad token and renews a good one. Only `create_fact` and `cast_vote` of a person without an account call `fetch_anonymous_voter_input`; an account goes to the service as its `AccountActor`. `fetch_anonymous_voter_input` takes the client host uvicorn resolved and the User-Agent, the empty text when it is missing and repeated headers joined with `, ` in the order received (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-16, D-17); a request without a client IP address raises `InvalidAnonymousVoterInputError`, which has no handler and ends in the sanitized `internal_error`, because it is a fault of the transport.

The request models are strict: an unknown field, a missing required field, a string for a number, a boolean for an integer, a type outside `FactType` and a verdict other than `confirm` or `deny` are refused with `invalid_request` and the paths of the fields before the service runs. `type` is read into `FactType` with only its own values accepted, so a refused type names the field `type` alone. `idempotency_key` is a UUID of 8-4-4-4-12 hexadecimal digits with hyphens, in either letter case, and `description`, `step_count` and `geozone_radius_m` may be absent. The identifier of a path is an integer of the range of a PostgreSQL `bigint`; another one is refused with `invalid_request` and the field `id`, and one no fact has reaches the service and ends in `fact_not_found`. The rules that tie fields together are the service's and come back as `InvalidFactInputError`, answered with the sorted paths it names.

`fact_errors.py` answers `FactNotFoundError` with 404 `fact_not_found`, `IdempotencyKeyReusedError` with 409 `idempotency_key_reused`, `VoteTooSoonError` with 409 `vote_too_soon` and `repeat_allowed_at` in ISO 8601 with milliseconds and its own offset, `FactNotFlaggableError` with 409 `fact_not_flaggable` and `FactNotFlaggedError` with 409 `fact_not_flagged`, all through `build_error_response`. A refusal answered to a valid session carries the renewed token like a success. Every endpoint is a plain `def`, so FastAPI runs it in its thread pool, and its route is named after the operation, so the request log names the operation and nothing of the request. The tests of `tests/api/test_facts_api_integration.py`, `tests/api/test_moderation_api_integration.py` and `tests/api/test_fact_identity_integration.py` replace the rules layer and the session resolution, and the last one runs the proxy handling of uvicorn itself.

## Relation to API_ALGORITHM.md

`API_ALGORITHM.md` describes what the layer accepts, refuses and answers, in the order a request meets it.
