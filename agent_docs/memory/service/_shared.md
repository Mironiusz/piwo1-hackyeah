What the module does: see `service/SERVICE_ALGORITHM.md`, sections "Algorithm goal" and "General process map".

## 2026-10-04 - Account input rules, password hashes and session tokens (plans/accounts)

- What changed: the first code of the rules layer, written by `plans/accounts/` before the skeleton existed: `service/account_rules.py` checks the pseudonym and the password of M9 with the explicit character set of `plans/accounts/ACCOUNTS_PLAN.md` D-3, `service/passwords.py` hashes with Argon2id at the floor of D-4 through argon2-cffi 25.1.0, and `service/session_tokens.py` issues and checks the HMAC-SHA256 token of D-6 with the standard library only.
- Why: these three need nothing of `backend_skeleton`, so the plan built them first; the actor resolution, the account operations, the data access and the programming interface wait for it.
- Reusable pattern: every way a token can be wrong ends in one `SessionExpiredError`, because the contract answers all of them with `session_expired`; a base64url part is accepted only in canonical form, its re-encoding equal to the input, which refuses padding, foreign characters and loose trailing bits at once; the signature is compared with `hmac.compare_digest` before the JSON is parsed; a JSON integer is checked with `type(value) is int`, because `bool` is an `int` in Python. A pseudonym trims only U+0020 and is never normalized, so a decomposed Polish letter is refused. Tests of time give explicit instants with their offset.
- Risk / notes: a renewed token does not revoke the earlier ones, which stay valid until their own expiry; whoever holds `SESSION_SIGNING_KEY` can forge a session of any account; a login with an unknown pseudonym is verified against `UNKNOWN_ACCOUNT_PASSWORD_HASH`, so its duration matches a wrong password.

## 2026-10-04 - Explicit administrative boundary (backend skeleton)

- What changed: The synchronous administrative wrapper uses the same configuration and log scope as the API.
- Why: An import is manually launched and introduces no periodic worker or duplicate environment reader.
- Reusable pattern: Keep the wrapper open around the complete consumer action and preserve specific publication outcomes.
- Risk / notes: There is no domain rule yet. Create SERVICE.md and SERVICE_ALGORITHM.md with the first product rule.

## 2026-10-04 - One pedestrian-network predicate (OSM_IMPORTER)

- What changed: `service/osm_tag_rule.py` implements `resolve_is_pedestrian_network_way` with the tag lists in `service/osm_tag_thresholds.py`.
- Why: stored network selection and Valhalla PBF preparation must describe the same set of ways.
- Reusable pattern: both consumers call this pure predicate on original source tags before routing-specific normalization; access exclusions must not be evaluated after the routing writer has removed access tags.
- Risk / notes: the predicate establishes network eligibility only, not accessibility. Future tag mapping must retain unknown information and the difference between explicit absence and the stairs default.

## 2026-10-04 - Contradictory OSM information (OSM_IMPORTER)

- What changed: specification version 13 and the importer resolve conflicting explicit presence and absence to unknown, without creating a fact.
- Why: the user approved this product behavior; an inconsistent element must not confirm accessibility.
- Reusable pattern: preserve smoothness precedence and distinguish different handrail sides from contradictory statements about the same attribute.
- Risk / notes: data/osm_reader.py snapshots must be copied before the pyosmium iterator advances. Source reading does not establish database readiness.

## 2026-10-04 - Importer preparation without HTTP backend (OSM_IMPORTER)

- What changed: source acquisition and local walking-file preparation consume the documented source and Valhalla contracts directly.
- Why: writing these stages does not require a running HTTP backend or changes to backend_skeleton.
- Reusable pattern: native assembled boundaries are checked against every member ring, and original tags survive routing normalization for later database mapping. The acquisition context owns temporary file lifetime.
- Risk / notes: async HTTP and child-process deadlines do not interrupt synchronous pyosmium parsing. The final administrative wrapper must provide process-level cancellation. Shared engine and vote evaluation still use their owners' implementations.

## 2026-10-04 - Delivered database model adapter (OSM_IMPORTER)

- What changed: network row mapping and connection-supplied database operations use the real accessibility_db package.
- Why: the merged database models establish the row contract without needing a running HTTP API.
- Reusable pattern: update only source-owned fact fields on the three-column OSM identity conflict; preserve original tags and source-wide motor membership. Install the local db package before root dependencies.
- Risk / notes: SQL compilation tests are not PostgreSQL execution tests. Publication, vote evaluation and recovery require the shared implementations; this subset does not open or commit a connection.
