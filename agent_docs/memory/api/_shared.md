## 2026-10-04 - Safe API foundation (backend skeleton)

- What changed: HTTP failures use the contracted envelope and one sanitized request identifier, including uncaught exceptions.
- Why: The shared completion log and diagnostic formatter prevent request or driver details from escaping.
- Reusable pattern: Extend the app factory through service dependencies; keep raw paths, payloads and exception text out of logs.
- Risk / notes: There is no domain rule yet. Create API.md and API_ALGORITHM.md when the first product operation is implemented; the setup protocol remains in docs/setup/backend.md.
