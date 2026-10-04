# Importer data algorithm

Document state: 2026-10-04

## Algorithm goal

Read the source and write routing files and database rows exactly as the service layer decided, without losing information and without leaving a partial result that could be taken for a complete copy.

## Domain concepts

A snapshot is an owned copy of one pyosmium node, way, relation or assembled area. A copy directory is the immutable set of routing files of one source instant. A preparation directory is private work that becomes a copy directory only by a rename. The pointer names the copy directory the routing service is to load.

## Detailed run order

Source reading opens the local PBF or XML with location storage and area assembly enabled. It copies every yielded value before advancing the native iterator and checks the run deadline before each element. Ways with unresolved coordinates and elements without usable edit timestamps are rejected. The pyosmium epoch sentinel is rejected rather than replaced with the current clock. Area WKB keeps the original node, way or relation identity. Arbitrary non-area relations receive no invented geometry.

Transport reads metadata through streamed HTTPX responses with bounded elapsed time, no redirects and no retry. It rejects non-success dated responses, oversized checksum bodies, empty extracts and mismatching declared lengths. MD5 is computed incrementally while a new file is written. The owning service context removes the temporary storage, and transport, timeout and filesystem failures become named acquisition errors.

Network preparation materializes prepared nodes and ways and validates unique identities and complete ordered references. It writes a temporary PBF in the target directory with the source instant in UTC in its header, and after closing the writer links the completed file to the destination without overwriting it. The temporary directory is always removed.

Tile building writes the build configuration once, without overwriting, and runs each supplied executable with an argument list and no shell under the shared process supervisor, inside the remaining deadline. A spent deadline ends the whole process group or job before the error is raised. Archive creation precedes the source-time modification and manifest hashing.

Completeness verification requires the two nonempty regular routing files, hashes their contents and records sizes and the aware source instant. The temporary JSON manifest is flushed before it is linked into place without overwrite. On reuse, the exact versioned schema is validated and both digests and sizes are recomputed, and a mismatch fails.

A new copy is placed by renaming its preparation directory, never over an existing directory. The pointer is replaced through a synced temporary file and a rename, so a reader sees either the old or the new name. A preparation directory and an incomplete copy directory are deleted only when the service layer decided that no committed copy owns them; a linked directory is refused.

Database writes use the delivered table metadata, including PostGIS geography binding, in batches of at most 1000 within one caller-owned transaction:

1. Upsert nodes and ways.
2. Replace membership, preserving repeated node references by their zero-based sequence position.
3. Remove obsolete ways and then unreferenced nodes.
4. Upsert facts, resolving conflicts by updating source, geography, step count, source edit date and removal state only. Creation fields are written on insertion only.
5. Lock the facts under reconciliation in ascending identity order, then their votes in fact and vote identity order, and write the source and removal mark decided for each of them.

Naive timestamps, non-minute offsets and precision beyond the schema's milliseconds are rejected instead of being silently cut. No commit, connection factory or vote evaluation happens in this layer.

## Diagnostics and summary

Every failure is a named exception with a constant message. Tool output and raw responses are never logged. A failed build or placement leaves no copy directory; a leftover preparation is removed by the next run.

## Address search

One search is one GET of the search address of the public instance with the prepared text and the fixed parameters, sent once and never retried. A limit of 5 seconds bounds the whole call, from the connection to the last byte of the answer, not each phase on its own.

The call ends in places or in one named failure with one of four causes:

- `timeout`, when the limit passes or the client reports a timeout;
- `connection`, for any other transport failure;
- `status`, with the code, for any answer other than 200, 403 for a blocked address and 429 for an exceeded limit included;
- `invalid_body`, when the answer is not a JSON list, or one of its results is not an object, has no address object, or has a latitude or a longitude that is not a string of a finite number.

A text part of a result that is not a string or is blank is read as absent, so it only shortens the label. Nothing else of the answer is kept, and neither the answer nor the request is written anywhere.

## GTFS step

A fetch writes each feed into a new file of a fresh `gtfs/.prepare-*` directory while streaming it, after the status and the `Last-Modified` header are accepted, and compares the byte count with the declared length at the end. A GTFS copy is made only from a preparation holding all three feeds with their days: each file must be a regular, intact zip, its compressed bytes included, whose root holds `agency.txt`, `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt` and `calendar_dates.txt`. The days are then written to `feeds.json` without overwriting, the preparation is renamed to the instant the copy is made, and `gtfs/current` is replaced last. A refused preparation is left for the caller to remove, and `gtfs/current` keeps naming the earlier copy. Reading a copy refuses a `feeds.json` without exactly the three feeds and their days, and a missing feed file.

A build writes into a fresh `transit/.prepare-*` directory. The timezone database must exist and be nonempty after its tool, because the shell creates the file of a redirection even when the tool writes nothing. The archive is built by the walking build of the importer, its modification time set to the instant of the OpenStreetMap copy, and the preparation is renamed to `transit/<copy name>-<GTFS name>`, never over an existing directory. The pointer `transit/current` is not written by the build; the caller writes it after the placement.

## Walking route

The reads of one route request run inside one snapshot its caller opens, so the copy in use, the network, the facts and the votes belong to one state of the database.

- The network is read whole: every way with its four barrier states and its flags, the nodes of every way in their order, and every node with its point, its kerb point and its flags.
- The facts of a route are those of the asked types that are neither hidden nor removed in OpenStreetMap and whose point lies within the given distance of the area, a geozone within that distance plus its radius, together with the fact of every asked way, whose point stands at the middle of the way and may lie far from the part a route takes. Without an area every such fact of the copy is read. A report gets the nearest way of the network within 15 m. Every geometry and distance travels as a bound parameter.
- The votes of the facts are read in the order of their facts and identities, with the fields the status rule needs.
- A geozone is paired with every way of the network within its radius.

The boundary of Kraków of a copy is the file `krakow_boundary.wkb` in the directory of that copy, `copies/<whole seconds of its instant>/`, written by the import from the boundary it assembles, before the manifest, so the manifest guards it with the network and the tiles. It is read only when the manifest of the directory names the same instant and every file matches it; otherwise the read is refused.

A call to the routing service waits at most 2 seconds. Error 442 means no path and error 443 a shape that cannot be traced; every other failure, a timeout and a body that cannot be read are the same failure, an unavailable service. `/status` gives the instant of the tiles the service loaded, in whole seconds. A traced edge gives its way, the OpenStreetMap nodes it begins and ends at, and its part of the traced shape.
