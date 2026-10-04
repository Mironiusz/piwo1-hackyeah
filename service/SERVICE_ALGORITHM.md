# Service layer algorithm

Document state: 2026-10-04

## Algorithm goal

Make one complete OpenStreetMap copy of Kraków current - its pedestrian network, its present barrier and amenity facts and its matching walking-routing data - or leave the previous complete copy and its routing pointer unchanged. Votes, independent user reports and moderation decisions are never changed.

## Domain concepts

A dated extract is a Małopolska PBF in the selected Geofabrik directory. Its published MD5 validates the downloaded bytes, not the truth of accessibility tags. The source instant describes the source state independently of download time. A pedestrian-network way satisfies the specification's highway and access rules.

A fact of the copy is identified by its OpenStreetMap element type and identifier together with its fact type, never by distance. A fact disappears for the first time when it still has the source openstreetmap without the removal mark and the fresh copy no longer holds its identity. A copy directory holds the network file, the tile archive and a manifest of one source instant; the pointer `current` names the directory the routing service is to load.

## General process map

```text
admission under exclusion, or skipped
-> remove leftover preparations, recover the pointer of the latest committed copy
-> acquire: redirect, checksum, download, header instant
-> equal instant: unchanged; older instant: failure
-> read the source: boundary, network, facts
-> prepare or reuse copies/<name>/
-> one publication transaction: recheck the state, network, facts, first disappearances, copy row
-> after a confirmed commit: pointer
```

## Detailed run order

The run starts its 60-minute deadline and asks for exclusion. A run that cannot be admitted, because another run or its unfinished work holds exclusion, ends as skipped without touching anything. The Valhalla template is read first, so a missing template fails before any download.

Leftover `.prepare-` directories of interrupted runs are removed, because no preparation directory is ever published. The pointer is then compared with the latest committed copy:

- without a committed copy there is nothing to recover;
- a pointer naming that copy needs nothing;
- a missing pointer, or one naming an older copy, is republished after the copy's manifest verifies its files and its source instant;
- missing or incomplete files, a manifest of another instant and a pointer naming a newer copy than the database are integrity failures, which stop the run before acquisition.

The caller validates the redirect before downloading. Only an absolute HTTPS URL with the exact Geofabrik host, directory and six-digit dated filename is accepted. Credentials, explicit ports, whitespace, query strings, fragments and relative addresses are rejected. The checksum response is bounded. The PBF is streamed under the whole-run deadline with 30-second connection and read-inactivity limits. Both metadata requests have their own 30-second elapsed budgets. There is no separate download ceiling and no automatic transport retry.

Checksum validation accepts one 32-digit hexadecimal digest, optionally followed by the exact selected filename with the standard text or binary checksum marker. Multiple records, a different filename or a digest mismatch fail, and uppercase digits mean the same as lowercase ones. The digest is validated before the header is parsed.

The header instant must include a timezone offset or UTC marker. Invalid calendar values, offsets outside the schema's range and precision exceeding Python's microsecond representation fail. The parser neither replaces missing source time with the current time nor normalizes away the supplied offset.

The first copy and a strictly newer instant proceed. Equal instants are unchanged even when represented with different offsets, and an earlier instant fails.

The source is read in three passes, each checking the run deadline before every element.

1. The first pass reads administrative relation 449696 and requires its assembled area and every referenced ring way. It verifies closed endpoint connectivity and the exact topological agreement of the assembled outline with every member ring, so that native assembly cannot silently omit a hole. Nested ring relations and open ring junctions fail explicitly.
2. The second pass selects permitted ways from their original tags and keeps every referenced node, including nodes outside the boundary, after checking coordinate consistency.
3. The third pass derives the facts of the copy and the motor-traffic membership of nodes. The downloaded file is removed after this pass.

The copy directory of the source instant is then reused when its manifest verifies it. An incomplete directory of an instant never committed is replaced only after its replacement has been built and verified; one of a committed copy stops the run.

A new copy is prepared in a fresh `.prepare-` directory:

1. Write the normalized network file.
2. Write a build configuration specialized from the template into the run workspace, with tiles there and the archive in the preparation.
3. Run `valhalla_build_tiles` and `valhalla_build_extract` through the shared process supervisor.
4. Set the archive's modification time to the source instant.
5. Write the boundary of Kraków assembled by the first pass as `krakow_boundary.wkb`, WKB in longitude and latitude, which the route reads to refuse a point outside Kraków.
6. Write and verify the manifest, which covers the network, the archive and the boundary.
7. Rename the preparation into `copies/<name>/`.

A failed build removes the preparation, and the next run removes it if that removal failed.

Publication runs in one shared transaction of at most 120 seconds and the remaining run time.

1. The callback reads the latest copy again and refuses a state that is no longer newer.
2. It replaces the network and upserts the present facts.
3. It reads the stored OpenStreetMap facts without row locks, locks those that disappear for the first time in ascending identity order and then their votes, and decides each of them on what it read under the locks.
4. It appends the copy row stamped with the business-zone instant cut to whole milliseconds.

A refusal inside the callback is reported by its own name, not as an anonymous rollback. When the commit confirmation is lost, at most three checks after 1, 2 and 4 seconds read the copy history with the original guard still valid:

- a row with the run's instant counts as committed;
- an absent row is a failure;
- no answer before the deadline, or a lost guard, leaves the outcome unknown and the pointer unchanged.

After a confirmed commit, the pointer is replaced with the new directory name. A pointer failure reports a committed copy with incomplete routing activation, never a rollback.

## Domain rules

The pedestrian predicate follows M2's closed list of highways:

- a cycleway additionally needs an explicit permitted foot value;
- forbidden foot values and motorroads are excluded;
- restricted access requires explicit foot permission;
- a separate sidewalk excludes a motor-traffic way, even with explicit foot permission;
- unknown highway values remain outside the network.

The predicate does not classify accessibility, normalize routing tags or change input tags. No preference profile is involved in network selection or mapping.

Way barriers come only from network ways, and point barriers and kerb facts only from network nodes. Amenities come from every node, way and assembled area of the copy: a node inside the boundary, a way with at least one node inside it, an area of such a way off the network, and an area of a relation with such a member way. Motor-traffic membership comes from every source way with a motor-traffic highway value, including ways excluded from the network.

Parse only accepted numeric forms, and leave unrecognized values unknown. Compare inclination, width and kerb height against the centralized thresholds. Preserve explicit absence separately from the stairs default. Contradictory presence and absence of the same item give unknown and no fact, as specification version 14 approves. An explicitly supplied smoothness value takes precedence over surface, and opposite handrail sides describe separate physical locations. Facts are added only for present barriers or amenities; accessibility is never inferred from missing tags.

Each element identity has one location:

- a node keeps its coordinates;
- a network way, or another way without an assembled area, uses the point at half its metric length in node order;
- another way with an assembled area, or a relation area, uses a strict interior point outside its holes.

Lines are interpolated and areas checked in metres, then transformed back and checked for area membership. Every fact of an identity shares its location. A step count belongs only to the stairs fact. The edit day is the element's own edit instant as a calendar day in the business zone.

After original-tag selection, the routing copy removes access restrictions that would suppress an accepted way. It keeps conveying direction, and its nodes retain only name and ref. Database rows resolve node and way attributes from the original source tags, convert states through the delivered closed lists and enumerate each original node reference, so repeated references retain their sequence.

## Reconcile and deduplication

A present fact is upserted by its identity. Its imported fields - source openstreetmap, geometry, step count, edit day and a cleared removal mark - are refreshed, while its id, creation instant, votes and moderation fields are kept. This also returns a converted or removed fact to openstreetmap. A new identity, including a split way under a new identifier, creates a new fact without votes, and a nearby independent report is never merged.

A converted or removed fact that stays absent needs no new decision. A fact that disappears for the first time is decided by M4 with the shared evaluator: when the confirmations exceed the denials, both summed over the latest votes of five persons, it becomes a user report; otherwise - no votes, only denials or a tie - it stays an OpenStreetMap fact marked as removed. Its votes are kept either way. The fact and its votes stay locked until the publication commits or rolls back, so no vote changes between the evaluation and the write (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-15 and D-52). The same source instant never creates a second copy row, and an older instant is refused.

## Diagnostics and summary

Invalid source metadata, geometry, tags, tools, routing files and integrity each raise a named exception. Their messages are constant texts without URLs, raw responses or values. The worker reports one outcome line with the source instant, duration and the counts of nodes, ways, memberships and facts written. Unexpected failures are reported by their type only.

## Address search

The search turns a text a person typed into the places in Kraków the person picks from, or into a plain refusal, without keeping anything that ties the text to the person.

The text is checked first: more than 200 characters as received is refused. It is then prepared: trimmed, every run of whitespace joined into one space, and the standalone words "ul." and "ulica" dropped in any letter case, because the public instance finds nothing with them; nothing else changes, so "ul.Lipska" and "al. Pokoju" stay as they are. A text with nothing left is refused. A refused text sends nothing out and is not remembered.

The prepared text in lower case is the key of the memory of the process. An answer kept for less than 24 hours is given back at once, also when it was an empty list. The memory keeps at most 1000 answers, drops the oldest first, and starts empty after a restart.

Otherwise the search waits for its turn: outgoing searches of the whole process start at least 1.1 seconds apart, and a search whose turn is more than 3 seconds away is unavailable at once and takes no turn. Five searches arriving together on an empty memory therefore start after 0, 1.1 and 2.2 seconds, and the other two are unavailable.

The prepared text, not the key, goes out once. Of the places received, only those whose address names Kraków as the city stay, in the order of the service. Each gets the label: the name when present and different from the street; the street with the house number, or without a street the estate with the house number; the first present of the quarter, the suburb and the district; and the postcode with Kraków, or Kraków alone. A place whose label an earlier place of the same list already has is left out, so no two items look the same. The answer is remembered and returned.

A failed call, whatever its cause, ends the search as unavailable, distinct from an empty list, and is never remembered, so the next search for the same text asks again. No point is guessed and nothing is retried.

The log gets one error entry with the cause, the status and the elapsed milliseconds of a failed call, and one warning when the gate gives no turn. No entry holds the text, the prepared text, the request sent out, the answer or a point.

## GTFS step of the loading program

The step makes the routing data with public transport of O9 follow the OpenStreetMap copy in use, from the last complete copy of the three GTFS feeds of ZTP Kraków (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-6 - D-10). It runs after the import, by hand, never on a schedule.

```text
admission under the exclusion of the importer, or skipped
-> remove leftover gtfs/.prepare-* and transit/.prepare-*
-> fetch the three feeds into a preparation: placed and pointed to as a whole, or the earlier copy kept
-> no GTFS copy, or no OpenStreetMap copy in use: nothing built
-> data of the same two copies placed earlier: reused
-> otherwise prepare the feeds, build in a preparation, place it
-> pointer transit/current
```

The run has 30 minutes and the 30-second limits of each request. A feed counts only with status 200, a `Last-Modified` header and a nonempty body of its declared length; a redirect, another status or a transport failure is refused without a retry. The day a feed was published is the calendar day of its `Last-Modified` in the business zone, never the day of the download. All three feeds must be intact zips with `agency.txt`, `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt` and `calendar_dates.txt`, and each must pass the preparation below in a throwaway directory of the workspace; only then are the days written, the preparation renamed to the instant the copy is made, in whole seconds since the epoch right after the fetch, and `gtfs/current` replaced. A failed, incomplete or refused fetch is logged as a warning, its preparation is removed and the earlier copy stays in use, so the build still runs from it. A copy that cannot be stored, a directory or a pointer that cannot be written, ends the run instead.

Each feed is unpacked into its own directory of the ingest input, and a member with a path in its name is refused. Three columns are rewritten, every other file is copied unchanged:

- `wheelchair_boarding` of a stop: 1 and 2 never change; an empty value or 0 of a stop whose parent station has 1 or 2 takes that value, as a child stop inherits it in the GTFS reference, and otherwise becomes 1;
- `wheelchair_accessible` of a trip: 1 and 2 never change, and an empty value or 0 becomes 1;
- `route_type` 900, tram service, becomes 0, the tram type the ingest reads.

A missing accessibility column is added, and a value outside 0, 1, 2 and empty is refused. This is the exception of O9: missing accessibility of public transport counts as accessible, while a stop or a trip marked 2 stays not accessible.

The data is named by the OpenStreetMap copy and the GTFS copy it was built from. It is built from the network file of the verified copy directory `current` names, with the configuration of the walking build plus the GTFS input, the ingest output and the timezone database in the run workspace, by `valhalla_build_timezones`, `valhalla_ingest_transit`, `valhalla_convert_transit`, `valhalla_build_tiles` and `valhalla_build_extract`. The archive carries the instant of the OpenStreetMap copy, and the preparation is renamed into place before `transit/current` is replaced. A failed build removes its preparation and leaves the earlier data and pointer.

The worker writes one outcome line with the outcome, what became of the fetch, the name of the data and the duration, and exits 0 only when the data in use was built from the OpenStreetMap copy in use and the run did not fail.

## Accounts

A light account lets a person sign their contributions with a pseudonym, and the moderator role lets the team hide flagged content (M9, M11). The rules below are those of `plans_finished/accounts/ACCOUNTS_PLAN.md` D-3 - D-7 and D-10.

```text
registration: check the pseudonym and the password -> hash the password -> insert, the index deciding uniqueness -> the account, not logged in
login: trim the pseudonym -> find it without regard to letter case -> verify the password -> a token valid for 24 hours
request with a token: verify the token -> read the account again -> the actor with its current role and a renewed token
deletion: delete the row of the account -> its votes stay, detached, with their weight
```

A pseudonym loses the spaces U+0020 at both ends and is then kept as it is, without Unicode normalization. It has 3 to 30 code points, each one of the 26 Latin letters, the nine Polish letters `ąćęłńóśźż` in both cases, a digit `0` - `9`, the underscore or the hyphen, so a decomposed Polish letter, a letter of another alphabet and an inner space are refused. It is unique without regard to letter case, the Polish letters included, as the database lowers them, and free again once its account is deleted.

A password has 5 to 128 code points, every character accepted, never trimmed, with no rule of composition and no list of common passwords. A password text that UTF-8 cannot encode, a lone surrogate, is refused. Only its Argon2id hash with 19 MiB of memory, 2 iterations and 1 degree of parallelism is stored, and the parameters travel inside the hash.

A login does not tell its failures apart: a pseudonym no account has, a pseudonym or a password outside the rules of registration and a wrong password all end the same way, and a pseudonym with no account is verified against the hash of a random value, so it takes as long as a wrong password.

A session is a signed token of an account identifier and an expiry 24 hours after the request that issued it. A token is valid while the current instant is earlier than its expiry. Every request with a valid token gets a new token valid for 24 hours from that request, and an earlier token stays valid until its own expiry. A request without the header `Authorization` is a person without an account. A header that is not the scheme `Bearer`, in any letter case, followed by one space and a token without spaces, a token that is malformed, wrongly signed or expired, and a token of an account that no longer exists are all an expired session, never a person without an account.

The account of a token is read again on every request, so a deleted account fails at once and a moderator role removed by the team is refused on the next moderator request, while the account itself still passes. An identifier of a deleted account is never given to another account, so an old token never resolves to the account that later took its pseudonym.

Deleting an account removes its row in one statement. Its reports stay, and its votes stay with the weight of a vote cast with an account and no person, so each counts as a person of its own. A deletion that finds no row, because another request deleted the account first, is an expired session. A vote insert in progress for the account makes the deletion wait for it; a vote committed first is detached, and a vote insert after the deletion committed fails on the foreign key, which its operation answers as an expired session.

Nothing of an account operation is logged: no pseudonym, identifier, password, hash or token.

## Status of a fact

The status tells a person how far the community confirms a fact (M4). It is derived from the stored votes every time it is needed and never stored.

The person of a vote is its account, else its hashed identifier, else - a vote of a deleted account - the vote itself. Votes are ordered by their instant and then by their identity, so of two votes with the same instant the one stored later counts as later. Only the latest vote of each person counts, and only for the five persons who voted most recently. A vote cast with an account weighs 1 and a vote without one 0.5.

The status follows from the two sums in this order: outdated when the denials reach 2 and outweigh the confirmations; disputed when both are above 0; confirmed when the confirmations reach 2; unverified otherwise. A fact removed in OpenStreetMap is outdated whatever its votes, and its sums are still given, because the importer compares them. The day of the latest confirmation is taken over every vote of the fact in the Europe/Warsaw zone, since older votes stop counting only toward the status.

## Walking route

A route request gives the walking route of M2 for a profile from the copy in use, with the state of every segment (M7), the list of the route (M8) and, when it helps, one alternative; or it refuses plainly (M10). It follows `plans_finished/route_planning/ROUTE_PLANNING_PLAN.md` D-1 - D-15 and the rules of `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` it keeps.

Run order:

1. The copy in use is read; without one the request ends with `routing_unavailable`.
2. The boundary of Kraków of that copy decides the points: a point outside names itself in `point_outside_krakow`, start before destination, and a point on the boundary counts as inside. Without a readable boundary the request ends with `routing_unavailable`, because no point is guessed inside or outside.
3. The routing service must serve that copy: the instant of its tiles must equal the instant of the copy in whole seconds; otherwise, or when the service does not answer, `routing_unavailable`.
4. The graph of the copy is taken from the process or built.
5. The facts of the corridor are read with their votes and statuses. The corridor is the rectangle around the straight line between the points, each side as wide as a quarter of its length and at least 1000 m.
6. A route avoids an OpenStreetMap barrier of the profile that is not outdated and that no contradicting report with confirmations of at least 2 replaces, a confirmed barrier report of the profile lying on a stretch, and a geozone of a type of the profile that is not outdated. The walking request excludes a barrier of a stretch at the middle of its longest pair of nodes, a barrier of a node at the node, every stretch of a way whose way fact is avoided, and each geozone as a polygon of 32 vertices around its circle, except a geozone holding a chosen point, which no request can avoid.
7. When no route avoids them all, the path with the fewest of them is found on the graph over the whole copy, each stretch weighing its count of barriers times 1 000 000 plus its length; the route excludes every other barrier, and `barrier_free_route_exists` is false. When even that route cannot be requested, `routing_unavailable`.
8. The route is traced and tied to the stretches of the copy; an edge across several stretches is split, the first and last edge keep only their traversed part, and a straight stretch joins each chosen point to the network.
9. The facts of the traced line and of its ways are read. A route that crosses something it had to avoid, other than what the path with the fewest barriers chose and a geozone holding a chosen point, is requested once more with that excluded too; a second crossing ends with `routing_unavailable`.
10. Every segment gets its state and the route its list.
11. When the route keeps an unverified or disputed barrier report of the profile, one more request around those reports gives the alternative, if its ways differ and it avoids at least one of them. The alternative may still cross what the path with the fewest barriers chose, and a request of it that finds no path gives no alternative, never a refusal of the route.
12. The day of the copy in the Europe/Warsaw zone is the `osm_copy_date`.

Domain rules of a segment:

- A report lies on the stretch of its nearest way nearest to it within 15 m. A kerb report is contradicted by an opposite kerb point on its stretch within 5 m, a report of a barrier of a way by the state absent of that barrier on its way, and a report of stairs never. A contradicted report that is not outdated replaces the fact of OpenStreetMap once its confirmations reach 2, and is overruled by OpenStreetMap until then.
- A segment is `barrier` when a prevailing barrier of the profile lies on it: a fact of OpenStreetMap not replaced, a report not overruled and not outdated, or a geozone of the profile covering it.
- Otherwise each barrier of the profile has its attribute known or unknown by D-7 of the mapping plan, the kerbs only on a segment that meets a carriageway: `no_barrier` when all are known, `partial_data` when some are, `no_data` when none is known other than the stairs by default. A way marked `wheelchair=no` turns `no_barrier` into `partial_data`. The straight stretches are `no_data`.
- `missing_attributes` lists the unknown attributes in the order kerbs, surface, incline, width, steps, and is empty for `barrier`, `no_barrier` and `not_assessed`.
- A profile without barriers gives every segment `not_assessed` and puts every barrier of the route in `additional_barriers`.
- A report of an amenity makes no attribute known, and a way state present whose fact is outdated makes no barrier and leaves its attribute unknown, because missing or disputed information is never shown as a confirmation of accessibility (M10).

The list holds the visible facts that are not outdated: the barriers of the profile on the route, the other barriers on it, geozones included, and the amenities of the profile within 50 m, each group ordered by the distance along the route to the projection of the fact onto the route line.

Nothing of a route request is stored. The only log entries the route writes are at ERROR, naming the kind of a failure or the count of crossed barriers, never a coordinate.

## Sample data

The sample step loads the eight sample facts of the demo scenario atomically while retaining existing votes and moderation decisions (`plans/sample_data/`).

The facts are S-1 - S-8 of `stage7_demo_scenario`, with the content of the bundled HarmonyOS demonstration: a confirmed high kerb, unverified stairs, a confirmed ramp, a disputed poor-surface geozone of 25 m, a high kerb contradicted by a real lowered kerb, flagged stairs, a flagged and disputed narrow-passage geozone of 50 m and a flagged and hidden high kerb. Their places come from checked public OpenStreetMap geometry; their content is fictional.

```text
validate a published source copy, the reference ways and the kerb contradiction in one stable network snapshot
-> validate existing fixed content and the sample vote history dated from each stored creation
-> insert missing facts with their moderation, then the votes of exactly the newly inserted facts
-> validate the complete dataset and return counts after commit acknowledgement
```

### Source and places

Each point fact requires its reference way as the uniquely nearest pedestrian way within 15 m, the way route planning places a report on; equal nearest distances fail. Each geozone requires its reference way within its radius. S-5 requires the contradiction of M2 in the route graph of the current copy: the stretch of its reference way nearest to it holds a lowered kerb point within 5 m. A high, unknown or missing kerb point, a farther one or one on another stretch establishes none. Whether a place lies on or off the actual route is a separate joint acceptance check.

### Existing content and vote history

An occupied identifier must belong to the expected sample with the same type, exact coordinates, description, radius and step count. Its source is a user report, and its source identity and report-save key are null. The expected sample votes are dated from the stored creation pair by the minute differences of the definition. Each defined fictional voter must appear exactly once with its verdict, without an account and at its expected instant and offset. Invalid history is refused rather than repaired with a new vote.

### Missing facts

Missing definitions share one business-clock reading truncated to whole seconds. Each creation, vote, flag and hiding lies its fixed minutes before it, computed in UTC and paired with the business-zone offset in force at its own instant. Only newly inserted facts receive their sample votes, and both batches are in the same transaction. Each sample vote is a vote without an account of weight 0.5, and the statuses follow from the votes under the ordinary rule of M4. Samples introduce no account and no alternate reliability evaluator.

### Domain rules

No missing source information is treated as confirmed accessibility or as a contradiction. Samples remain visibly marked as user reports with the sample mark. Loading does not update existing sample content, flags, hiding, contributor votes or reliability status.

### Reconcile and deduplication

The fixed identifiers are -1 to -8 in definition order. A primary-key conflict leaves the stored row untouched and is followed by validation. A changed definition fails. The fictional voter identities are stable across dates and sample votes are tied to newly returned identifiers, so a retry does not add later-day history.

### Diagnostics and summary

`created` means at least one missing fact was inserted; `unchanged` means all eight already existed and passed validation. Both require an acknowledged commit. Unchanged does not imply visible facts or their starting statuses. A failure aborts this sample step. Loss of commit evidence stays unknown; no automatic retry is performed and preceding common-loader effects are not rolled back.

## Tile archive step

The step puts the recorded map tile archive under the served name `krakow.pmtiles` of the directory the proxy serves, taking it from the source place a person put it in (`plans_finished/tile_loading/TILE_LOADING_PLAN.md` D-7). It runs by hand, inside the common loading program or on its own, never on a schedule.

```text
admission under the exclusion of the importer, or skipped (standalone command only)
-> refuse a source inside the served directory, then a missing served directory
-> remove leftover .tile-archive-* files of the served directory
-> served file of the recorded value: unchanged, the source is not read
-> source: missing, unreadable or of another value refused
-> copy into a new .tile-archive-* file of the served directory, then check the copy
-> check the deadline, then replace the served name with the copy in one os.replace
-> loaded
```

Repeat: when the file under the served name already has the recorded SHA-256 value, the run writes nothing under the served name and reports `unchanged`, which completes the tile effect; the source place is not needed then, so a retry after the source was removed still succeeds. When the served name is missing, holds a file of another value or is a link, the run loads the archive and replaces what was there, logging an information line when it replaces a file of another value. A link at the source counts as no source file.

Every failure ends the run with its reason and leaves the served name as it was, because the archive reaches it only through the one replacement after both checks: a reader of the served name finds the earlier file or the complete checked archive, never part of a file. The one exception is a failed sync of the directory on Linux after the replacement, which ends as `copy_failed` with the complete checked archive already under the served name. A temporary copy that is not placed is removed; when even that fails, a warning is logged and the next run removes it. A copy that cannot be read back ends as `copy_failed`, a copy of another value as `copy_mismatch`. The placed file is readable by everyone and writable by its owner, because the proxy may read it as another user and the archive is public.
