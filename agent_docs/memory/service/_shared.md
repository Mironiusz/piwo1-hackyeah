## 2026-10-04 - Explicit administrative boundary (backend skeleton)

- What changed: The synchronous administrative wrapper uses the same configuration and log scope as the API.
- Why: An import is manually launched and introduces no periodic worker or duplicate environment reader.
- Reusable pattern: Keep the wrapper open around the complete consumer action and preserve specific publication outcomes.
- Risk / notes: There is no domain rule yet. Create SERVICE.md and SERVICE_ALGORITHM.md with the first product rule.
