What the module does: see `service/SERVICE_ALGORITHM.md`, sections "Algorithm goal" and "General process map".

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
