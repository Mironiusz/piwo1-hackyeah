# Importer data layer

Document state: 2026-10-04

## Role and API

The layer reads source files, prepares routing files and exposes database operations on a caller-supplied SQLAlchemy connection. It does not construct a database engine or manage the publication transaction.

`fetch_osm_header_timestamp` returns the raw source-state header. `fetch_osm_elements` yields immutable `OsmElementSnapshot` values copied from pyosmium objects, including node references, relation members and assembled area WKB. Missing coordinates or source timestamps fail with `OsmReadError`. The caller decides selection and mapping.

`apply_osm_network_pbf` writes prepared snapshots, validates duplicate identities and node references, preserves ordered references and records the source instant in the PBF header. It publishes a completed temporary file with a non-overwriting link. Failure raises `OsmNetworkFileError`. Inputs are materialized to validate references before writing, so memory scales with the selected network.

`apply_osm_routing_manifest` creates a versioned manifest for network.osm.pbf and valhalla_tiles.tar with source state, byte sizes and SHA-256 hashes. `fetch_osm_routing_manifest` validates the recorded schema and file contents. Existing manifests, symlinks and empty or corrupt files are rejected with `RoutingDataError`.

## Limits

Tests use invented XML/PBF and temporary directories. No full Geofabrik import, Valhalla tile build, database reconciliation or routing activation is provided yet. The future orchestrator must hold import exclusion across preparation and publication; a manifest alone does not establish database commit state. See DATA_ALGORITHM.md.

## HTTP and Valhalla integrations

`data/osm_source.py` owns the HTTPX client factory and all source requests. It exposes redirect and checksum reads and streamed file writing. TLS verification stays enabled, redirects are not followed and HTTP environment configuration is disabled. Transport errors become `OsmDownloadError`; requests are not retried inside a manual run. `httpx==0.28.1` is the selected transport pin.

`data/osm_valhalla.py` owns configuration-file output and child-process execution. It invokes valhalla_build_tiles and valhalla_build_extract without a shell, fails on nonzero exit and rejects missing or empty output. Deadlines and caller cancellation kill and reap the process before returning. Process groups require the Linux execution environment of the delivered image. Tool output is discarded rather than exposed as an unsafe exception or an independently configured logger.

The build tools and base configuration are supplied by the caller, following the existing Valhalla handoff. No image name, shared environment configuration or database connection factory is invented here. Real tile construction remains unverified on this machine because Docker access is unavailable.

## Delivered database adapter

`data/osm_copy.py` imports the actual `accessibility_db` tables and enums. It upserts selected network rows, replaces ordered membership and removes obsolete network rows. Present facts are identified by OSM element type, element identity and fact type; only source-owned fields are updated. Existing identifiers, moderation, creation time and user content survive. Copy metadata and disappearance changes use the same supplied connection. No function commits or opens a connection.

Fact locks are acquired in ascending fact identity order; vote history is locked in ascending fact and vote identity order. Person identifiers are excluded from snapshot representations. The caller must perform source completeness checks and hold shared exclusion before any writes. The shared vote evaluator must decide disappearance changes; this adapter does not duplicate that rule. Tests compile PostgreSQL statements but do not establish that a deployed schema accepts them.
