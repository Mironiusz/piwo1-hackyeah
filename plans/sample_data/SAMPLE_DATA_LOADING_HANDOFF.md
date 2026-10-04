# Sample-loading step handoff

Document state: 2026-10-04, updated for the eight facts of the demo scenario; sample-provider contract implemented, common-loader integration remains to be delivered

## Ownership and approval

On 2026-10-04 the user chose to establish this provider contract in `sample_data` and hand it to `osm_import`. Mateusz owns both initiatives. This settles the sample-provider part of the common loading contract; it does not settle the importer's outcome mapping or the tile provider's interface.

`sample_data` implements the operation, its records, prerequisites, transaction, duplicate protection and tests. `osm_import` implements the adapter in its `service/demo_loading.py` and records that adapter in `docs/deployment/loading_program.md`, as its plan S-2 and S-3 require. The common command is the approved `python -m worker.load_demo`, with the order OpenStreetMap, tiles, samples and stopping at the first unsuccessful required effect. This provider adds no worker command.

The dataset changed on 2026-10-04 from four examples to the eight facts of `stage7_demo_scenario` (plan D-1). The names below are unchanged except one failure code, and the adapter carries the counts through without assuming the size of the dataset.

## Callable and records

The service-level callable is `service.sample_data.apply_sample_data() -> SampleDataResult`. It takes no argument, owns its transaction and returns only after an acknowledged successful commit, including when the invocation inserts nothing. The common program calls it synchronously without holding an outer database transaction. The connection factory, clock and logger are the shared `data.engine.build_engine`, `common_time.fetch_business_now` and `config.logging.fetch_logger`.

`common_sample_data.py` defines immutable `SampleDataResult` and `SampleDataOutcome` records:

- `outcome`: `created` when one or more missing facts were inserted, otherwise `unchanged`.
- `created_count`: the number of facts inserted in this invocation, from 0 to 8.
- `unchanged_count`: the number of already existing, validated sample facts, from 0 to 8; it sums with `created_count` to 8.
- `initial_votes_created_count`: the number of sample votes inserted together with the newly created facts, from 0 to 25.
- `fact_ids`: the stable tuple `(-1, -2, -3, -4, -5, -6, -7, -8)` in S-1 to S-8 order.

An unchanged result means that the present invocation validated the prerequisites and the existing dataset. It does not mean the facts are still in their starting status, visible or unchanged by moderation. Their legitimate votes, flags and hidden state are preserved.

## Failure contract

The provider raises `SampleDataFailure`, the public alias of `SampleDataError` in `common_sample_data.py`, with a safe `reason` and a `commit_state`. It does not return a success-shaped fallback or catch a failure and continue with fewer facts. Unexpected exceptions also mean that this required step is unsuccessful; the caller must not infer success from their absence of a named reason.

Reason codes are `copy_missing`, `site_invalid`, `contradiction_missing`, `identity_collision`, `content_mismatch`, `initial_vote_invalid`, `database_failed` and `commit_unknown`. `contradiction_missing` replaces the earlier `surface_not_absent`, because the contradiction of S-5 is now a lowered kerb; the `osm_import` session was told of the rename on 2026-10-04. `commit_state` is `not_attempted`, `rolled_back` or `unknown`; rollback is reported only after acknowledgement, and loss of the commit acknowledgement is `unknown`. No exception text, connection string or contributor information becomes a result field or ordinary loading message.

The common adapter treats both `created` and `unchanged` as a completed sample effect. It retains these provider counts, records a failure when the provider raises, and preserves an unknown sample commit as unknown rather than reporting proven rollback. It never claims that previously committed OpenStreetMap or tile effects were rolled back because samples failed.

Recovery is the existing manually triggered full-flow retry. The provider performs no automatic retry and does not implement selective resumption. Stable identifiers and transactional insertion make repeating an uncertain attempt safe once the next invocation can reach the database.

## Reserved identifiers and write rules

The user chose stable negative sample identifiers on 2026-10-04 instead of a schema change, and reserved `fact.id` -1 to -8 for S-1 to S-8 in that order (Q-6 of the shape). The convention is recorded in `docs/product/schema.md`, section Facts, and awaits Kuba's confirmation as the owner of that document; it does not prove that the fact operations already accept negative identifiers. Ordinary writes keep the identity-generated identifiers. Other manual writes must not use these identifiers, and new sample versions must not silently reuse them for different content.

The existing `PK_fact` is the database backstop. Sample insertion uses bound values, `OVERRIDING SYSTEM VALUE` and `ON CONFLICT (id) DO NOTHING`, with explicit returned columns. Samples keep `idempotency_key` and every OpenStreetMap identity field null under the existing schema. The provider verifies the immutable sample content of every conflicting row and fails on an unrelated row or changed dataset; it never overwrites the row.

## Sample votes, dates and moderation

Every sample vote is a vote without an account, of weight 0.5, with its own fictional voter. The 25 votes give each fact its intended status under M4: S-1 and S-3 confirmed, S-4 and S-7 disputed, the others unverified, and S-5 at a confirmation weight of 1.5 so that one presenter's confirmation without an account brings it to 2. The voter identity of the n-th vote of a fact is SHA-256 of `sample-data:voter:v2:` followed by the fact identifier and n in decimal, joined by `:`, in UTF-8. It is fictional input, not a hash of a real IP address, browser or account, and the presenter's identity never equals it.

All dates are relative to the first successful loading. The loading instant is the business-zone clock truncated to whole seconds. Every creation, vote, flag and hiding lies its fixed number of minutes before it, from 144 to 2880, computed in UTC and stored with the Europe/Warsaw offset in force at its own instant. The flag and hide pairs of S-6, S-7 and S-8 are written with the facts themselves; a hidden fact is always flagged.

Sample votes are inserted only for fact identifiers actually returned as newly inserted, in the same transaction, and a vote batch that returns another count fails. On a retry, an existing fact's expected votes are dated from its stored creation pair by the same minute differences, so retry needs no knowledge of the first loading instant. Each defined voter must appear exactly once with its verdict, without an account, at its expected instant and offset. Missing or inconsistent history is an integrity failure, not permission to fabricate a vote on a later day. Flags, hiding, other votes and status are never compared or reset.

## Prerequisites and concurrency

The schema exists through the supplied first revision, and the shared service-account connection is available. The provider validates in one Repeatable Read transaction before any write: an OpenStreetMap copy exists, every reference way exists, each point fact's reference way is its unique nearest way within 15 m, each geozone's reference way lies within its radius, and the lowered kerb contradicts S-5 under route planning's own rule (`fetch_route_graph`, `build_nearest_stretch`, `resolve_report_contradiction`). It does not fetch source data over the network, start or refresh an import, or move a place. Exact places are in `SAMPLE_DATA_OSM_EVIDENCE.md` and plan D-3.

The sample transaction cannot mix network versions across its statements. When the process holds no graph of the current copy, the provider builds it inside its transaction with the 60 s statement limit of a graph build, so the transaction lasts as long as that build. A concurrent writer can cause a serialization failure; that invocation reports failure and relies on a manual full-flow retry. Primary-key uniqueness prevents duplicate facts even when two sample invocations overlap. This is not a claim of exclusion for the whole loading program, which remains the common loader's responsibility.

Other statements use the shared engine's 5000 ms limit and its documented connection and pool limits. The provider adds no new environment entry. Source changes after this transaction are normal new source states; a later loading attempt validates the same places again rather than moving them.

## Integration checks

The common adapter must verify successful `created` and `unchanged` results, each named failure class, an unknown commit and an unexpected exception. The full flow must show that a sample failure leaves preceding committed effects intact and a manual retry calls every required provider without duplicating samples or their votes. These are common-loader integration checks under `osm_import`; this provider supplies its own real-database evidence and the fixed provider contract.

The final API checks must also prove that negative sample fact identifiers are accepted by the existing detail, vote and moderation operations. The public contract defines the fact identifier as an integer and specifies no positive-only range. No consumer rejection may be bypassed by replacing identifiers or adding another interface.
