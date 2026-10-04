# Shape: API and service layers of community facts

Document state: 2026-10-04, interview closed
Regulator: C:40

## Problem

The product has a decided contract for reports, geozones, votes, flags and moderation, but the current FastAPI application exposes none of the nine community-fact operations. Kuba narrowed `COMMUNITY_FACTS_SHAPE.md` to their data layer and the status evaluator. Those parts alone do not make checks 5.1 - 5.3 of `FINAL_CHECKLIST.md` verifiable on the service.

This task supplies the missing API and service layers on Kuba's data layer. The user accepted the scope and confirmed the task prefix in the conversation of 2026-10-04. The work belongs to Marek's backend part; confirmation of the team handoff remains subject to `MVP.md`, section Open decisions and confirmations.

## Recipient and trigger

- The web frontend and the HarmonyOS client request facts for a map, open a fact, check nearby facts, save a report or a geozone, vote or flag content.
- A moderator requests flagged content and hides or restores it.
- The demo checks 5.1 - 5.3 exercise the operations on the running backend.

## Current state

- `docs/product/specification.md`, version 18, is the source of truth. M3 - M5, M9 - M11 and Personal data govern this work; `docs/product/schema.md` is its target schema.
- `docs/product/api_contract.md`, sections Shared objects, Sessions and actors, Facts and Moderation, names the nine operations and their responses and errors. The user approved the contract in place of Kuber and Adrian; their confirmation remains outstanding.
- `api/app.py` builds the shared FastAPI foundation with request correlation and error handlers. It registers no product route. The absence of the skeleton recorded in the earlier community-facts shape is no longer the current state.
- `service/fact_status.py` already supplies `resolve_fact_status`, `FactStatusResult` and `FactView`; the evaluator must be reused rather than implemented a second time. Its delivery is distinct from completion of Kuba's data operations.
- The database models and revision chain exist in `db/accessibility_db/`. This interview has not connected to a database or verified its applied revisions.
- Kuba's `COMMUNITY_FACTS_SHAPE.md` orders the data layer of all nine operations and fact locking before a vote's visibility check. No corresponding community-fact data-operation module is present in the current tree.
- `plans/accounts/ACCOUNTS_PLAN.md`, D-7 and S-5 - S-6, names the shared actor resolution and API dependencies. Their modules are not present in the current tree, so this task depends on their delivery and does not replace them.
- The earlier data-layer shape proposed excluding facts removed in OpenStreetMap from the nearby check, while version 16 of M3 and the contract did not name that exception. The user settled the discrepancy on 2026-10-04 in question 1: exclude removed facts. Version 17 of the specification and `find_nearby_facts` of the contract now contain the exception; ordinary outdated facts remain included. Kuber and Adrian's confirmation of the contract amendment remains outstanding.
- The registry entry Executor of the API and service layers of the community facts records the executor and anonymous-identity handoff. This task supplies the executor, and question 2 settles the permitted identifying inputs as IP + User-Agent. Exact hashing, the trusted-proxy boundary and confirmation of the team handoff remain to be settled before implementation.

## Smallest meaningful scope

All nine operations of the contract working through API and service layers on the shared foundation, actor resolution and Kuba's data operations: `list_facts_in_area`, `read_fact`, `find_nearby_facts`, `create_fact`, `cast_vote`, `flag_fact`, `list_flagged_facts`, `hide_fact` and `restore_fact`.

The agreed order starts with the three reads, then saving point reports and geozones, then votes, then flags and moderation. A read-only subset is an intermediate delivery, not completion of this task. The derivation of an anonymous voter's identifier belongs here because creating a report also writes its author's first confirmation.

## Out of scope

- Kuba's data operations, schema changes and status-evaluator ownership. This task consumes them and records any required handoff rather than inventing their contract.
- Account operations and shared actor resolution, which `accounts` supplies.
- The OpenStreetMap importer, route planning, sample-data generation, hosting changes and the clients' reporting or moderation screens.
- Optional product features, including photos and editing saved reports. M3 and M5 make saved reports immutable, and the MVP excludes photos.

## Functional requirements

1. Expose the nine operations with the requests, responses, status codes and safe error envelopes of the contract, validating required fields, closed lists, types and unknown fields.
2. Return facts with their source, dates, sample marker and reliability status through the shared fact object and evaluator. Hidden facts are absent from every non-moderator operation.
3. Read at most 1000 facts in an area and indicate truncation. Include geozones by their point. Leave out facts removed in OpenStreetMap from this map read, as the contract requires.
4. Read one non-hidden fact by identifier, including an outdated one. Find nearby facts of the same type within 15 m, nearest first, returning whole-metre distances. Include ordinary outdated facts but exclude hidden facts and facts removed in OpenStreetMap, as approved by the user in question 1.
5. Save a point report or a barrier geozone together with its author's first confirmation in one transaction. Normalize the description, enforce the permitted step count and geozone radii, and neither edit nor automatically merge a saved fact.
6. A retry with the same idempotency key and the same normalized content returns the first fact with 200 and stores no second fact or vote; changed content yields `idempotency_key_reused`. The first save returns 201.
7. Accept confirmations and denials with an account or without one; derive anonymous identity on the server from IP + User-Agent only, as approved by the user in question 2 and recorded in M9. Identical pairs share the daily vote limit and one identity for the latest-vote status rule. Neither raw identifying inputs nor the resulting identifier appear in a response or request log.
8. Refuse a second vote of the same person on the same fact on the same Europe/Warsaw calendar day with `vote_too_soon` and the next midnight as `repeat_allowed_at`. Read the returned status after the write. Cooperate with the data-layer fact lock during OSM publication.
9. Flag eligible user content without recording who flagged it and without changing the first flag instant on retry. Refuse flagging an OSM fact. Hide and restore only flagged facts; repeated hide and restore requests are harmless.
10. Reuse the shared actor recognition and session renewal of `accounts`. A bad or expired token is never treated as anonymous. Only a current moderator may list flagged facts, including hidden ones, or hide and restore them.
11. Update the implementation's layer documentation and records, and verify the contracted behavior and the critical transaction, visibility and retry scenarios. Update `MVP.md` and the decision registry for the handoff and decisions this task settles.

## Scenarios: input, flow, expected state after the run

1. Map and detail. A client requests an area containing an unverified report, an outdated report, a hidden report and an OSM fact marked removed. The map response includes the first two. Opening the outdated report succeeds; opening the hidden report yields `fact_not_found`. A removed OSM fact can still be opened by identifier, as `read_fact` allows every non-hidden status.
2. One save despite a lost response. A person approves stairs with three steps and sends key K. The first save commits one fact and one author confirmation but its response is lost. The same normalized request with K returns 200 and the first fact. K with four steps yields 409; nothing changes.
3. Calendar-day voting. An account confirms a fact at `2026-10-04T23:59:59.000+02:00`. A denial at `2026-10-04T23:59:59.900+02:00` is refused with `2026-10-05T00:00:00.000+02:00`. A denial just after that midnight succeeds. Only that account's latest vote counts toward the status.
4. Anonymous identity. At 10:00 person A confirms a fact without an account. At 10:01 person B requests a vote on the same fact from the same public IP address with the same User-Agent and receives `vote_too_soon`, because both requests resolve to one identity. After the next midnight B may vote, and that latest vote replaces A's vote in the status calculation for the shared identity. This limitation was disclosed and accepted in question 2. The raw inputs and the hash never reach the response or logs.
5. Flag, hide and restore. A person flags a report twice; its first flag date remains. An ordinary account cannot moderate it. A moderator hides it, after which public reads and votes treat it as missing. Restoration exposes it again with the votes it kept.
6. An expired token. A client sends a report or vote with an expired token. The service returns `session_expired`, writes nothing and does not derive an anonymous voter instead.
7. Nearby check after an OSM removal. At 08:00 the import marks an OSM stairs fact removed, and it disappears from the map. At 08:05 a person reports stairs 8 m away; the nearby check excludes the removed fact, so the person can save a new visible report. An ordinary outdated stairs report in the same radius remains a candidate for confirmation.

## Challenging own assumptions

- Does the existing initiative already cover this work? Its seed orders the complete operations, but Kuba's closed shape explicitly excludes API and service. A separate task within the same initiative fills that gap without replacing his task.
- Can the earlier current-state section be copied? No: the backend skeleton and evaluator now exist. Delivery of the data operations and actor resolution still needs checking before implementation.
- Can the nearby search simply follow Kuba's shape? Initially no: its proposed exception had not reached the authoritative specification or the contract. Question 1 settled the discrepancy, and the user-approved rule now appears in both documents.
- Is anonymous identity needed only for `cast_vote`? No: `create_fact` also writes a confirmation of the author, including an anonymous one.
- Does IP + User-Agent guarantee a distinct identity per human? No. The user chose that input boundary after the shared-limit example; identical pairs are one identity for both the daily limit and the latest-vote rule. The implementation must preserve this stated limitation rather than silently collect more browser characteristics.
- Can reads be treated as anonymous-only while accounts are unfinished? No: the contract says their token is optional and a supplied invalid token must be refused. Actor integration remains a delivery dependency.

## Domain rules or explicit TODO

The rules already decided in the specification and contract are recorded above, rather than put to the user again: the five latest distinct voters, weights 1 and 0.5, unchanged weights after account deletion, no status decay with time, calendar-day limits, geozone radii 10/25/50/100 m, first-author confirmation and moderator visibility.

Question 1, answered on 2026-10-04: the user said, translated from Polish, "Exclude facts removed in OSM from the suggestions". The nearby check therefore excludes precisely those facts and still includes ordinary outdated facts. The decision is recorded in version 17 of the specification and in the contract; it matches Kuba's earlier ruling rather than replacing it.

Question 2, answered on 2026-10-04: the user said "IP + User-Agent" after the two variants and shared-limit example were presented. Only those two request-derived inputs may identify anonymous voters; Accept-Language is not included. The choice accepts collisions for identical pairs. Version 18 of the specification and the Sessions and actors section of the API contract record the decision; Kuber and Adrian's confirmation of the contract amendment remains outstanding.

Exact hashing, trusted-proxy handling and consumer signatures belong to phase B. The open identity handoff in the registry must be closed before implementation, not replaced with defaults. Missing or malformed User-Agent handling is part of that request-input contract to settle in the plan, not a permission to add another identifying input.

Agent decision at C:40, without asking: retain the initiative's existing flat artifact layout. The user confirmed the task prefix and existing initiative; adding a second prefix requires no move of Kuba's artifacts.

## Notes on data, performance and security

No hosted-demo database or personal data has been read. The task uses the local setup for validation. No target address or secret belongs in its artifacts.

The fact object reveals no author identity, and a flag records none. Anonymous identity is derived from the IP address and User-Agent only and is kept only as the 32-byte hash required by the target schema, until the demo and its data are deleted. The trusted source of the IP address behind the reverse proxy and the hashing method require explicit resolution in phase B, not trust of an arbitrary forwarded header.

The area limit is 1000; the moderator contract returns all flagged facts and names no pagination. Query volume, vote-history reading and index use must be checked against the delivered data operations before the implementation plan closes. This shape claims no measured latency or database readiness.

## Open questions

None in the shape phase. The user answered both blocking questions. Delivery of the data operations and shared actor resolution, verification of local database readiness, technical hashing and proxy decisions, query-volume checks and outstanding team confirmations remain dependencies and checks for the implementation plan.
