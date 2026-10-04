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

## 2026-10-04 - Complete manual import on the delivered shared interfaces (OSM_IMPORTER)

- What changed: `service/osm_import.py` runs one import under `apply_import_exclusion`, a 60-minute `Deadline` and one `apply_publication`; `service/osm_facts.py` derives the facts of a copy, `service/osm_routing_preparation.py` places `copies/<name>/` and `service/osm_routing_recovery.py` republishes the pointer; `worker/osm_import.py` is the entry point `python -m worker.osm_import`.
- Why: the backend foundation delivered the engine, exclusion, publication, process supervisor, clock and logger, so the importer consumes them instead of guessing contracts (`plans/osm_importer/OSM_IMPORTER_PLAN.md` D-43 - D-50).
- Reusable pattern: the shared `apply_transaction` turns every exception of a publication callback into an anonymous `PublicationRolledBack` raised `from None`, so a caller that must report a named refusal keeps it in a closure and re-raises it after the rollback (`apply_osm_publication_step`). A server stamp written through an adapter that refuses sub-millisecond precision is cut to the whole millisecond of `timestamptz(3)` first (`build_osm_stamp`). The synchronous source passes check the run deadline before every element; this replaces the process-level cancellation the earlier entry expected. Fact reads for reconciliation take no row locks while no fact is reconciled; only facts under reconciliation and their votes are locked.
- Risk / notes: the shared vote evaluator is not delivered, so a refresh with a first disappearance is refused (D-40); `service/fact_status.py` of another session may become that evaluator once it is committed and agreed. Peak memory grows with the whole Małopolska extract and a real run is unmeasured.

## 2026-10-04 - Disappearing OSM facts decided by the shared evaluator (OSM_IMPORTER)

- What changed: `apply_osm_disappearance` of `service/osm_publication.py` replaces the refusal of D-40. It locks the facts that disappear for the first time with `fetch_osm_facts_for_update`, then their votes with `fetch_osm_fact_history`, and `resolve_osm_fact_changes` turns the sums of `resolve_fact_status` into a user report or a removal mark (`plans/osm_importer/OSM_IMPORTER_PLAN.md` D-52).
- Why: `service/fact_status.py` delivered the one M4 rule for every caller, and the user accepted it as the evaluator D-40 waited for.
- Reusable pattern: inside a long publication transaction, take the locks that freeze other people's writes as late as possible - here after the network and present-fact writes, right before the copy row - and decide on the rows read under those locks. Two connections with `FOR UPDATE NOWAIT` prove that a lock is held without making the test wait. `resolve_fact_status` reads the business zone through the configuration facade whenever a fact has a confirmation, so a unit test that calls it needs the `runtime_settings` fixture.
- Risk / notes: the vote write that must lock its fact before validating (D-15) is still not delivered; the shape of plans/community_facts/ lists its own status evaluator, and a change of `resolve_fact_status` must be followed by the importer's call.
