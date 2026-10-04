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
