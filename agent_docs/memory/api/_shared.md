## 2026-10-04 - Safe API foundation (backend skeleton)

- What changed: HTTP failures use the contracted envelope and one sanitized request identifier, including uncaught exceptions.
- Why: The shared completion log and diagnostic formatter prevent request or driver details from escaping.
- Reusable pattern: Extend the app factory through service dependencies; keep raw paths, payloads and exception text out of logs.
- Risk / notes: There is no domain rule yet. Create API.md and API_ALGORITHM.md when the first product operation is implemented; the setup protocol remains in docs/setup/backend.md.

## 2026-10-04 - plan_route and the documents of the layer (route_planning)

- What changed: `api/route.py` registers `plan_route` with a strict request model and the answers of `RoutingUnavailableError` (503) and `PointOutsideKrakowError` (422 with `points`), and `api/API.md` and `api/API_ALGORITHM.md` now exist, so the note of the entry Safe API foundation is settled.
- Why: the first product operations arrived together, and the request log names an operation by the name of its route.
- Reusable pattern: an endpoint that waits for the database or another service is a plain `def` with `name=` equal to the operation of the contract; a refusal of the service layer gets its own exception handler that writes only the fields the contract names through `build_error_response`. Tests replace the service function at its seam in the API module (`api.route.resolve_route`) and the start-up work of the lifespan (`api.route.build_route_graph_at_start`), so `TestClient` needs no database.
- Risk / notes: the fields of O9 the contract now names for `plan_route` - `route_kind`, `public_transport_unavailable` and the segment field `public_transport` - are not handled yet; until `public_transport_routing` adds them, a request with `route_kind` is refused as `invalid_request`.

## 2026-10-04 - The nine operations of the community facts (COMMUNITY_FACTS_API)

- What changed: `api/facts.py` and `api/moderation.py` expose the nine operations of the contract, sections Facts and Moderation, with the strict request models of `api/fact_models.py`, the bodies of `api/fact_body.py`, the refusals of `api/fact_errors.py` and the inputs of the anonymous identity of `api/fact_identity.py`; `PointBody` moved to `api/point_body.py` and `build_error_response` gained `repeat_allowed_at`.
- Why: `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-2, D-3, D-8, D-11 and D-16 - D-18.
- Reusable pattern: an operation that needs a session only for its refusal and renewal declares it in `dependencies=[Depends(fetch_request_session)]` (or `fetch_moderator_actor`) instead of an unused parameter, which vulture would report. A closed list in a strict model is the enumeration of `accessibility_db.closed_lists` with `Field(strict=False)`: a union of two `Literal` aliases makes Pydantic report paths like `type.literal['stairs', ...]`, which the error envelope would pass to the client. A path identifier is `Annotated[int, Path(alias="id", ge=FACT_ID_MIN, le=FACT_ID_MAX)]`, the range of a PostgreSQL `bigint`: an identifier outside it is refused as `invalid_request` with the field `id`, while zero and negative identifiers reach the service, because sample facts have negative ones. `TestClient(app, client=(address, port))` gives a request an IP peer, and `uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware` around the app tests the real proxy handling; set `client.headers["User-Agent"]`, because a `headers` argument adds a second User-Agent next to `testclient`.
- Risk / notes: the HarmonyOS client gives up after 15 seconds while a vote may wait 120 seconds for a publication (R-10 of the plan); a hosted proxy that does not append X-Forwarded-For or a wrong `API_TRUSTED_PROXY_ADDRESSES` makes all people without an account one identity per User-Agent.
