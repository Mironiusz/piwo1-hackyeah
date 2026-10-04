# SERVICE_ALGORITHM

Document state: 2026-10-04

## Algorithm goal

Load four fictional demonstration examples atomically while retaining existing votes and moderation decisions.

## Domain concepts

The examples are an explicitly contradictory poor-surface point, separate stairs with three steps, a rest place near the contradiction path and a separate poor-surface circle of 25 m. Their locations come from checked public OSM geometry; their barrier and amenity content is invented.

## General process map

1. Validate a published source copy and the intended paths in one stable network snapshot.
2. Validate existing fixed content and original fictional author history.
3. Insert missing examples with one fictional confirmation each.
4. Validate the complete dataset and return counts after commit acknowledgement.

## Detailed run order

### Source and sites

The two point barriers require their intended uniquely nearest pedestrian way within 15 m. Equal nearest distances fail. The contradiction requires explicit poor-surface absence; unknown data and default absence are insufficient. The rest place must be within 50 m of the contradiction path. The circle must intersect its own path and remain farther than its radius from the contradiction path. Actual-route and frontend evidence is a separate joint acceptance check.

### Existing content and initial history

An occupied identifier must belong to the expected sample with the same type, exact coordinates, description, radius and step count. Source is a user report and source identity and report-save key are null. Each existing sample requires exactly one reserved fictional author's historical confirmation with its original creation instant and offset. Invalid history is refused rather than repaired with a new vote.

### Missing examples

Missing definitions share one business-clock reading. Only newly inserted facts receive initial author confirmations; both batches are in the same transaction. Each new confirmation has weight 0.5 and the initial status is unverified under the ordinary vote rules. Samples introduce no account or alternate reliability evaluator.

## Domain rules

No missing source information is treated as confirmed accessibility. Samples remain visibly marked as fictional user reports. Loading does not update existing sample content, flags, hiding, contributor votes or reliability status.

## Reconcile and deduplication

The fixed identifiers are -1, -2, -3 and -4 in definition order. Primary-key conflict leaves the stored row untouched, followed by validation. A changed definition fails. The fictional author identity is stable across dates and initial votes are tied to newly returned identifiers, so a retry does not add later-day history.

## Diagnostics and summary

`created` means at least one missing example was inserted; `unchanged` means all four already existed and passed validation. Both require acknowledged commit. Unchanged does not imply visible or still unverified examples. A failure aborts this sample step. Loss of commit evidence stays unknown; no automatic retry is performed and preceding common-loader effects are not rolled back.
