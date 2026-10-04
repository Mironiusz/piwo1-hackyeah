# Importer data algorithm

Document state: 2026-10-04

## Source reading

Open the local PBF or XML with location storage and area assembly enabled. Copy every yielded value before advancing the native iterator. Reject ways with unresolved coordinates and elements without usable edit timestamps. The pyosmium epoch sentinel is rejected rather than replaced with the current clock. Assemble area WKB using the original node, way or relation identity. Arbitrary non-area relations receive no invented geometry.

## Network preparation

Materialize prepared nodes and ways, validate unique identities and complete ordered references, then write a temporary PBF in the target directory. Convert the source instant to UTC for its header. After closing the writer, link the completed file to the destination without overwriting it. Always remove the temporary directory. Source selection and tag normalization belong to the service layer.

## Completeness verification

Require the two nonempty regular routing files. Hash their contents and record sizes and aware source state. Flush the temporary JSON manifest before publishing it without overwrite. On reuse, validate the exact versioned schema and recompute both digests and sizes. A mismatch fails; no file is treated as a substitute for another copy. Database comparison and routing-pointer recovery remain integration work.

## Transport and tool lifetime

Read metadata through streamed HTTPX responses with bounded elapsed time, no redirects and no retry. Reject non-success dated responses, oversized checksum bodies, empty extracts and mismatching declared lengths. Compute MD5 incrementally while writing a new file; the owning service context removes incomplete temporary storage. Translate transport, timeout and filesystem failures into named acquisition errors.

Write configuration only in a new build directory. Run each supplied Valhalla executable with an argument tuple and no shell, inside the remaining monotonic deadline. On timeout or cancellation, kill its Linux process group and await its termination. Preserve caller cancellation rather than converting it into success. Archive creation must precede its source-time modification and manifest hashing. An uncommitted failed directory is never activated or treated as a valid copy.

## Database writes

Use the delivered table metadata, including PostGIS geography binding. Batch writes in groups of at most 1000. Upsert nodes and ways, replace membership, remove obsolete ways and then unreferenced nodes within one caller-owned transaction. Preserve repeated node references by their zero-based sequence position. Fact conflict resolution updates source, geography, step count, source edit date and removal state only. Keep creation fields insertion-only. Reject naive timestamps, non-minute offsets and precision beyond the schema instead of silently losing information. No independent commit, connection factory or vote evaluation occurs.
