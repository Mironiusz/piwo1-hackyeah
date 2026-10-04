# Service layer algorithm

Document state: 2026-10-04

## Algorithm goal

Reject unusable or stale source metadata and select only the ways permitted by M2 of the product specification. These rules do not publish a copy.

## Domain concepts

A dated extract is a Małopolska PBF in the selected Geofabrik directory. Its published MD5 validates the downloaded bytes, not the truth of accessibility tags. The source instant describes the source state independently of download time. A pedestrian-network way satisfies the specification's highway and access rules.

## General process map

```text
redirect location -> validate source directory and dated filename
published and computed MD5 -> validate selected file and compare digests
header timestamp -> parse an aware source instant
source and current instants -> first/newer, unchanged, or rejected older copy
way tags -> allowed highway -> access exclusions -> network eligibility
```

## Detailed run order

The caller validates the redirect before downloading. Only an absolute HTTPS URL with the exact Geofabrik host, directory and six-digit dated filename is accepted. Credentials, explicit ports, whitespace, query strings, fragments and relative addresses are rejected.

Checksum validation accepts one 32-digit hexadecimal digest, optionally followed by the exact selected filename with the standard text or binary checksum marker. Multiple records, a different filename or a digest mismatch fail. Uppercase hexadecimal digits have the same meaning as lowercase digits.

The header instant must include a timezone offset or UTC marker. Invalid calendar values, offsets outside the schema's range and precision exceeding Python's microsecond representation fail. The parser does not replace missing source time with the current time or normalize away the supplied offset.

The first copy and a strictly newer instant may proceed. Equal instants are unchanged even when represented with different offsets. An earlier instant or a naive comparison input fails.

## Domain rules

The pedestrian predicate follows M2's closed list of highways. A cycleway additionally needs an explicit permitted foot value. Forbidden foot values and motorroads are excluded. Restricted access requires explicit foot permission. A separate sidewalk excludes motor-traffic ways, even with explicit foot permission. Unknown highway values remain outside the network.

The predicate does not classify accessibility, normalize routing tags or change input tags. No preference profile is involved in network selection.

## Diagnostics and summary

Invalid source metadata raises a named source exception. Messages describe the failure category and do not include the supplied URL or raw response. The pure rules create no logs or aggregate counters; their future caller owns run reporting.

## Attribute mapping and routing preparation

Parse only accepted numeric forms; unrecognized values remain unknown. Compare inclination, width and kerb height against the centralized thresholds. Preserve explicit absence separately from the stairs default. Combine contradictory statements about the same attribute into unknown. Add facts only for present barriers or amenities; never infer accessibility from missing tags. A positive step count exceeding the schema's smallint range raises `OsmTagError`.

For geometry, validate coordinates and topology before projecting. Interpolate line length in metres or obtain a strict interior representative point for areas. Transform back and verify area membership. Network coverage tests source vertices and never clips selected ways.

After original-tag network selection, remove routing access restrictions that would suppress an accepted way. Keep conveying direction. Nodes retain only name and ref. Database integration and full-copy orchestration remain deferred.

## Integrated acquisition and file preparation

Request the latest redirect without following it. Validate the absolute dated source URL, read a bounded checksum response, and stream its PBF under the whole-run acquisition deadline. Both metadata requests have their own 30-second elapsed budgets; transport connection and read-inactivity limits are 30 seconds. There is no separate 15-minute download ceiling and no automatic transport retry. Validate the digest before parsing the source header. Temporary source data stays outside the checkout and is removed on every context exit.

For a local accepted PBF, read the source instant and administrative relation 449696. Require its assembled area and all referenced ring ways. Verify closed endpoint connectivity and exact topological agreement of the assembled outline with every member ring, so native assembly cannot silently omit a hole. Nested ring relations and open ring junctions fail explicitly rather than inventing geometry.

On the next source pass, select permitted ways from original tags and retain every referenced node, including nodes outside the boundary. Verify coordinate consistency before writing normalized copies. Build Valhalla tiles and their tar archive with supplied tools and configuration. Set the archive modification time to the source instant, then hash both files into the manifest. An existing output directory is preserved and rejected. A failed build leaves an unpublished directory for the future guarded cleanup protocol.

## Database row mapping

Resolve node and way attributes from original source tags before routing normalization. Convert the states through the delivered closed-list enums, retain full geometry and enumerate each original node reference. Require source-wide motor membership as an explicit input rather than deriving it from selected ways.
