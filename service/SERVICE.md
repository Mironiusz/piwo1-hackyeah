# Service layer

Document state: 2026-10-04

## Role

The layer implements product decisions independently of an administrative command or an API request. The importer provides pure source validation, pedestrian-network selection, barrier and amenity mapping, fact locations and routing-tag preparation. Source acquisition and walking-data preparation are implemented; reconciliation and database publication remain unimplemented.

## Public API

| Function | Input | Output |
| -------- | ----- | ------ |
| `resolve_osm_source_location` | Absolute redirect location | Validated source URL |
| `resolve_osm_checksum` | Published checksum text, selected filename, computed digest | Matching lowercase MD5 |
| `resolve_osm_source_state` | Source header timestamp | Aware `datetime` preserving the offset |
| `resolve_osm_source_is_newer` | Source and optional current instants | Whether processing a newer copy is allowed |
| `resolve_is_pedestrian_network_way` | Read-only tag mapping | Network eligibility |

Rejected source metadata raises `OsmSourceError`. These functions perform no filesystem, HTTP or database operation and create no timestamps from the current clock. The caller supplies the computed file digest and current copy instant.

## Construction

`osm_source_validation.py` owns source metadata validation. `osm_tag_rule.py` owns the network predicate selected in the backend architecture contract. `osm_tag_thresholds.py` holds its closed tag lists. The future stored-network reader and routing-file writer must call the same predicate.

Tests in `tests/service/` use invented values. They can run through pytest or through Python's unittest discovery when pytest is unavailable. Geometry uses pinned Shapely and pyproj dependencies. All tests use invented data and leave the hosted database untouched.

## Architectural decisions

There is no substitute database engine, HTTP transport, logger, clock or vote evaluator. Source validation is in the rules layer because it decides which metadata may be accepted, rather than reading external data. Inputs are not mutated. The source header's offset and precision survive parsing; persistence must separately meet the database's millisecond precision contract.

`SERVICE_ALGORITHM.md` describes the implemented behavior.

## Mapping and geometry API

`resolve_way_facts` and `resolve_node_facts` return immutable attributes and fact-type sets. `resolve_osm_amenity_states` handles supported amenities. Numeric values are parsed in `osm_tag_values.py`; thresholds live in `osm_tag_thresholds.py`. Contradictory presence and absence produce unknown and no fact, as approved in specification version 14. An explicitly supplied smoothness value takes precedence over surface. Opposite handrail sides describe separate physical locations.

`resolve_osm_fact_location` preserves node coordinates, interpolates half a way's metric length or selects an interior area point outside holes. Calculations use EPSG:2180 and results use EPSG:4326. `resolve_osm_element_coverage` retains whole ways having an inside node. Unusable geometry raises `OsmGeometryError`.

`build_osm_routing_node_tags` and `build_osm_routing_way_tags` return new tag dictionaries. Select ways using the original tags before normalization. These functions prepare routing inputs; they do not run Valhalla or activate a copy.

## Acquisition and preparation

`service/osm_acquisition.py` exposes the asynchronous context manager `fetch_osm_extract(client, deadline)`. It validates the latest redirect before reading dated resources, checks MD5 and the header, and removes run-local source bytes when the context closes. The deadline uses the active event loop's monotonic clock; it is not a calendar timestamp.

`service/osm_preparation.py` provides `build_osm_boundary`, `build_osm_network` and `build_osm_routing_network`. Boundary verification checks every member ring and compares the assembled outline with the complete referenced geometry. Network selection preserves whole ways, ordered node references and original tags. The source is materialized in separate passes; memory grows with extract size.

`service/osm_routing_preparation.py` provides `prepare_osm_network_data` and asynchronous `prepare_osm_routing_data`. The latter accepts an existing source, a new output directory, a supplied Valhalla configuration, the directory of delivered build tools and the monotonic deadline. It prepares the network, enables the three agreed node/platform options, invokes the tools and creates the integrity manifest. It never publishes a database copy or changes current.

The synchronous pyosmium passes cannot be interrupted by an asyncio timeout. The future full importer must execute preparation under its process-level cancellation wrapper before claiming the whole-run deadline. Current tests prove HTTP-stream cancellation and Valhalla-process cancellation independently.

## Database row preparation

`build_osm_database_network` maps selected original snapshots to the delivered database enums and EPSG:4326 EWKT. The caller supplies motor-traffic node membership from all source ways, including ways excluded from the pedestrian network. Repeated references retain their sequence. This prepares network rows only; it does not claim a complete fact selection or publication.
