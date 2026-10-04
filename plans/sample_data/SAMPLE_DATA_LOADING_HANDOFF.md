# Sample-loading step handoff

Document state: 2026-10-04, sample-provider contract approved by the user; common-loader integration remains to be delivered

## Ownership and approval

On 2026-10-04 the user chose to establish this provider contract in `sample_data` and hand it to `osm_import`. Mateusz owns both initiatives. This settles the sample-provider part of the common loading contract; it does not settle the importer's outcome mapping or the tile provider's interface.

`sample_data` implements the operation, its records, prerequisites, transaction, duplicate protection and tests. `osm_import` implements the adapter in its `service/demo_loading.py` and records that adapter in `docs/deployment/loading_program.md`, as its plan S-2 and S-3 require. The common command is the approved `python -m worker.load_demo`, with the order OpenStreetMap, tiles, samples and stopping at the first unsuccessful required effect. This provider adds no worker command.

## Callable and records

The service-level callable is `service.sample_data.apply_sample_data() -> SampleDataResult`. It takes no argument, owns its transaction and returns only after an acknowledged successful commit, including when the invocation inserts nothing. The common program calls it synchronously without holding an outer database transaction. Runtime configuration, the connection factory, clock and logger come from the shared backend contracts identified in `SAMPLE_DATA_PLAN.md`.

`common_sample_data.py` defines immutable `SampleDataResult` and `SampleDataOutcome` records:

- `outcome`: `created` when one or more missing examples were inserted, otherwise `unchanged`.
- `created_count`: the number of facts inserted in this invocation, from 0 to 4.
- `unchanged_count`: the number of already existing, validated sample facts, from 0 to 4; it sums with `created_count` to 4.
- `initial_votes_created_count`: equal to `created_count`, because every newly inserted fact gets one initial fictional author confirmation in the same transaction.
- `fact_ids`: the stable tuple `(-1, -2, -3, -4)` in S-1 to S-4 order.

An unchanged result means that the present invocation validated the prerequisites and existing dataset. It does not mean the examples are still unverified, visible or unchanged by moderation. Their legitimate votes, flags and hidden state are preserved.

## Failure contract

The provider raises `SampleDataFailure`, defined in `common_sample_data.py`, with a safe `reason` and a `commit_state`. It does not return a success-shaped fallback or catch a failure and continue with fewer examples. Unexpected exceptions also mean that this required step is unsuccessful; the caller must not infer success from their absence of a named reason.

Reason codes are `copy_missing`, `site_invalid`, `surface_not_absent`, `identity_collision`, `content_mismatch`, `initial_vote_invalid`, `database_failed` and `commit_unknown`. `commit_state` is `not_attempted`, `rolled_back` or `unknown`; rollback is reported only after acknowledgement, and loss of the commit acknowledgement is `unknown`. No exception text, connection string or contributor information becomes a result field or ordinary loading message.

The common adapter treats both `created` and `unchanged` as a completed sample effect. It retains these provider counts, records a failure when the provider raises, and preserves an unknown sample commit as unknown rather than reporting proven rollback. It never claims that previously committed OpenStreetMap or tile effects were rolled back because samples failed.

Recovery is the existing manually triggered full-flow retry. The provider performs no automatic retry and does not implement selective resumption. Stable identifiers and transactional insertion make repeating an uncertain attempt safe once the next invocation can reach the database.

## Reserved identifiers and write rules

The user chose stable negative sample identifiers on 2026-10-04 instead of a schema change. Reserve `fact.id=-1` for S-1, `-2` for S-2, `-3` for S-3 and `-4` for S-4. The convention was approved by the user in Kuba's place and is a storage handoff for Kuba to confirm; it does not prove that his consumer code already supports it. Ordinary writes keep the identity-generated identifiers. Other manual writes must not use these four identifiers, and new sample versions must not silently reuse them for different content.

The existing `PK_fact` is the database backstop. Sample insertion uses bound values, `OVERRIDING SYSTEM VALUE` and `ON CONFLICT (id) DO NOTHING`, with explicit returned columns. Samples keep `idempotency_key` and every OpenStreetMap identity field null under the existing schema. The provider verifies the immutable sample content of every conflicting row and fails on an unrelated row or changed dataset; it never overwrites the row.

Initial votes are inserted only for fact identifiers actually returned as newly inserted. Their timestamps equal those newly inserted facts' creation instants and their fictional identity is SHA-256 of `sample-data:initial-author:v1:` followed by the sample identifier in decimal form. This hash is fictional input, not a hash of a real IP address, browser or account. Existing samples must already have exactly one such historical author confirmation with the original creation instant and offset. Missing or inconsistent initial history is an integrity failure, not permission to fabricate another confirmation on a later day.

A changed definition under a reserved identifier is rejected for review rather than replacing content. Existing community votes and moderation fields are not compared to their initial values and are never reset.

## Prerequisites and concurrency

The schema exists through the supplied first revision, and the shared service-account connection is available. The provider checks that an OpenStreetMap copy exists and validates the current-network sites in one Repeatable Read transaction. It does not fetch source data over the network and does not start or refresh an import. Exact site prerequisites are in `SAMPLE_DATA_OSM_EVIDENCE.md` and plan D-3.

The sample transaction cannot mix network versions across its statements. A concurrent writer can cause serialization failure; that invocation reports failure and relies on a manual full-flow retry. Primary-key uniqueness prevents duplicate facts even when two sample invocations overlap. This is not a claim of exclusion for the whole loading program, which remains the common loader's responsibility.

Statement waits use the shared engine's explicit 5000 ms limit and its documented connection/pool limits. The provider adds no new environment entry. Source changes after this transaction are normal new source states; a later loading attempt validates the same sites again rather than moving them automatically.

## Integration checks

The common adapter must verify successful `created` and `unchanged` results, each named failure class, an unknown commit and an unexpected exception. The full flow must show that a sample failure leaves preceding committed effects intact and a manual retry calls every required provider without duplicating samples or their initial votes. These are common-loader integration checks under `osm_import`; this provider supplies its own real-database evidence and the fixed provider contract.

The final API checks must also prove that negative sample fact identifiers are accepted by the existing detail, vote and moderation operations. The public contract defines the fact identifier as an integer and specifies no positive-only range. No consumer rejection may be bypassed by replacing identifiers or adding another interface.
