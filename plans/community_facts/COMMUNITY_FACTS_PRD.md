# PRD: Data layer of the community facts

Document state: 2026-10-04, approved by Kuba

## Business goal

Give the nine operations of the community facts - `list_facts_in_area`, `read_fact`, `find_nearby_facts`, `create_fact`, `cast_vote`, `flag_fact`, `list_flagged_facts`, `hide_fact` and `restore_fact` of `docs/product/api_contract.md`, sections Facts and Moderation - every read and write of the stored facts and votes they need, so that the API and service layers Marek builds in `plans/community_facts_api/` can serve point reports, geozones, confirmations and denials, votes without an account, flags and moderator hiding (M3 - M5, M9 - M11 of `docs/product/specification.md`). Together with that initiative it lets the main scenario pass step 4 and the Kraków demo show the contradiction between OpenStreetMap and a user report that M10 requires.

This PRD follows the closed `COMMUNITY_FACTS_SHAPE.md` at C:40 and `docs/product/specification.md`, which prevails. The target schema of `docs/product/schema.md` is part of the specification and is not changed here.

Amended on 2026-10-04 in phase B with the approval of Kuba: the verification of the plan found that FR-6, FR-8 and FR-9 made this layer refuse writes, while `docs/standards/standard_architecture.md`, section Layer boundary, says that the data layer writes and reads and does not decide whether a write may be performed. These requirements and AC-2, AC-3 and AC-7 now give the service layer the locked state it decides on. The Scope gained the local schema-owner test fixture.

## Problem and its consequences

The behavior, the target schema and the contract of the community facts are decided and the schema is built, but no operation can read or write a report, a vote, a flag or a hidden mark. The only stored-fact reads that exist serve a route, and they leave out every outdated fact and every hidden one, which is wrong for the reading of one fact and for the moderator list.

Without this layer:

- the API and service plan of `plans/community_facts_api/` cannot close, because its question Q-4, `Block: yes`, waits for the contract of these data operations;
- the vote write that the publication of a fresh OpenStreetMap copy freezes does not exist, so the agreement of `plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-15 rests on nothing, and the registry entry Backend handoff for vote locking during OSM publication of `docs/standards/decision_registry.md` stays open;
- a lost response of a report could save it twice, and a retried vote could break the daily limit of M4, if each operation wrote the stored data its own way.

## Scope

- The data operations of the nine contract operations: every read and write of facts and votes they need, against the local database of `db/`, inside a transaction their caller opens and commits.
- The vote write: a lock of its fact that gives back the state the service layer decides on, then the store of the vote, in that order inside one transaction of the caller, so that a publication of a fresh OpenStreetMap copy and a vote on the same fact never interleave.
- The local schema-owner test fixture that the cleanup of committed facts and votes needs and that no initiative delivered (`plans/sample_data/SAMPLE_DATA_REVIEW.md`, B-2). Added on 2026-10-04 at the decision of Kuba, because FR-7 is verified on a real concurrent publication, which needs committed rows the service account cannot delete.
- The contract of these data operations, agreed with Marek as the answer to Q-4 of `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md`.
- Verification on stored data in the local database, and the documentation of the delivered operations and of what the service layer has to keep to use them correctly.
- The records this initiative settles: the consent of Kuba to the move of the status rule, and the lock rule of the registry entry Backend handoff for vote locking during OSM publication.

Kuba owns this initiative (`MVP.md`, section Initiatives; `TEAM.md`).

## Out of scope

- The API and service layers of the nine operations - the endpoints, the validation of a request, the mapping of outcomes to the responses and errors of the contract, the recognition of the actor and of the moderator role, the renewal of a session and the orchestration of a request into one transaction. Cut by Kuba on 2026-10-04 in the shape, question 1, and since the same day the initiative `plans/community_facts_api/` of Marek.
- The derivation of the identifier of a person without an account from the request. Decided in `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-15 - D-17; this layer stores the 32 bytes it is given.
- The rule that derives the status of a fact from its votes, requirement 8 of the shape. It is built by `plans_finished/route_planning/` as FR-16 of `plans_finished/route_planning/ROUTE_PLANNING_PRD.md`, with the scenarios 2, 7 and 8 of the shape as its AC-18; Kuba consented to the move on 2026-10-04, answering the question of this PRD. This layer reads the votes the rule needs and never derives a status itself.
- The rule of the shape, requirement 9, that a fact removed in OpenStreetMap takes no part in the check for existing facts: already written in M3 of the specification and in `find_nearby_facts` of the contract, so nothing is left to change in those documents.
- The client side of M3 and M5, the summary a person approves and the device's memory of its own vote, which belong to `frontend_app` and `stage5_harmonyos_port`.
- The facts of a route and the state of a segment of `route_planning`, the publication of a fresh copy of `osm_importer` and the sample data of `sample_data`, which use the same stored data but are written by those initiatives.
- Any change of the target schema, of the rights of the service account or of the contract.
- Every decision whether a fact may be voted on, flagged, hidden or restored, and the refusals that follow. The service layer of `community_facts_api` decides them from the state this layer gives back (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-5), because the data layer does not decide whether a write may be performed (`docs/standards/standard_architecture.md`, Layer boundary). Moved out on 2026-10-04 at the decision of Kuba in phase B.

## Functional requirements

FR-1. Facts in an area. Read the facts whose point lies in a rectangle, at most 1000 and a sign that the rectangle holds more, leaving out hidden facts and the facts outdated because they were removed in OpenStreetMap (M4, M11).

FR-2. One fact. Read a fact by its identifier in any status, a fact removed in OpenStreetMap included; a hidden fact reads as not found, like a missing one (M11). Hiding and restoring of FR-9 reach a hidden fact without this read.

FR-3. Facts near a point. Read the facts of one type within 15 m of a point, nearest first, with their distance in whole metres, OpenStreetMap facts and ordinary outdated facts included, hidden facts and the facts removed in OpenStreetMap left out (M3, M11).

FR-4. The votes of the facts read. Give, for the facts any read returns, all their stored votes, so that the status rule of FR-16 of `plans_finished/route_planning/ROUTE_PLANNING_PRD.md` derives their status, sums and day of the latest confirmation. The votes of up to 1000 facts are read together, never once per fact.

FR-5. Saving a report or a geozone. Save the fact and the confirmation of its author as its first vote together or not at all, once per idempotency key: a repeated save with the same key finds the fact of the first save, whether hidden or not, and creates nothing, and the stored fact is what the caller compares the content of a repeated request with (`docs/product/schema.md`, `idempotency_key`; `docs/standards/standard_idempotency.md`).

FR-6. Saving a vote. Lock a fact for a vote and give back whether it exists, whether it is hidden and whether it was removed in OpenStreetMap, so that the service layer decides whether the vote may be written (M11). Then store a confirmation or a denial of a person - an account, or the 32 bytes of a person without an account the caller supplies - at the instant the caller supplies. The store refuses a second vote of the same person on the same fact on the same calendar day in Europe/Warsaw, which the database holds, and gives back that calendar day, from whose next day the next vote is accepted (M4, M9). A retry never stores a second vote on the same day. A vote of an account that no longer exists stores nothing and is told apart from the daily refusal, so that the service layer answers it as an expired session.

FR-7. A vote during a publication. The lock of FR-6 comes before the service layer checks the fact and before the vote is stored, all inside the transaction of its caller. A vote on a fact that a publication of a fresh OpenStreetMap copy holds waits until that publication commits or rolls back, at most the 120 seconds of `plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-16, and is then checked against the state in force. Agreed by Kuba on 2026-10-04 in the shape, question 3.

FR-8. Flagging. Lock a fact for a flag and give back whether it exists, its source and whether it is hidden, so that the service layer decides whether it may be flagged (M11). Then mark it flagged at its first flag and keep that first instant, storing nothing about who flagged.

FR-9. Moderation. Read every flagged fact, hidden ones included, the most recently first flagged first, with the calendar day of its flag and whether it is hidden. Lock a fact for moderation and give back whether it exists, whether it is flagged and whether it is hidden, so that the service layer decides whether it may be hidden or restored. Then hide or restore it, both repeatable without a change; a restored fact keeps all its votes (M11).

FR-10. Protected data. No read returns the author of a fact, the account or the identifier of a person behind a vote to anything but the status rule, and the layer never derives, logs or returns the identifier of a person without an account (`plans_finished/fact_schema/FACT_SCHEMA_PRD.md` AC-12; specification, Personal data).

FR-11. The agreed contract. The names, inputs, results, refusals and transaction duties of the data operations are written down and agreed with Marek before `plans/community_facts_api/` builds on them, so that its Q-4 closes on delivered code rather than on a promise.

FR-12. Verification and records. Show every requirement above on stored data in the local database, the wait of FR-7 on a real concurrent publication included; document the delivered operations; record in `MVP.md` and `docs/standards/decision_registry.md` the consent of Kuba to the move of the status rule and the lock rule of FR-7.

## Acceptance criteria

Every day is a calendar day in Europe/Warsaw in October 2026, every instant carries the offset of that zone.

AC-1. A report saved once. The caller saves a point report of stairs with 3 steps, the idempotency key K and the 32 bytes H1 of a person without an account; then saves the same with K again, as after a lost response. After the run there is one fact with one vote, a confirmation of H1 without an account, and the second save finds that fact and stores neither a fact nor a vote. If the save of the vote fails, neither the fact nor the vote is stored. Meets FR-5.

AC-2. The daily limit. Account A confirms fact F at `2026-10-04T23:59:59.000+02:00` - stored; A denies F at `2026-10-04T23:59:59.900+02:00` - refused, giving back 4 October, so the next vote is accepted from `2026-10-05T00:00:00.000+02:00`; A denies F at `2026-10-05T00:00:00.500+02:00` - stored; the same denial repeated at `2026-10-05T00:00:03.000+02:00` - refused. After the run F has two votes of A, the latest a denial. A vote refused on 25 October, the day the offset changes, gives back 25 October. Meets FR-6.

AC-3. A vote during a publication. An OpenStreetMap fact F with a confirmation of account A and a denial of account B is no longer in a fresh copy. At 03:00:00 the publication locks F and its votes; at 03:00:02 account C confirms F and its write waits; at 03:00:40 the publication commits F as removed in OpenStreetMap and the lock of C is granted, gives F back as not hidden, and the confirmation is stored. After the run F is removed in OpenStreetMap with the confirmation of C in its history, and the decision of the publication matches the votes it read. When the publication rolls back instead, the lock gives back the state before it. Meets FR-6 and FR-7.

AC-4. The check for existing facts. Within 15 m of a point lie an ordinary outdated report of stairs at 8 m, an OpenStreetMap fact of stairs at 12 m, the fact F of AC-3, a hidden report of stairs, a report of a high kerb at 5 m and a report of stairs at 16 m. The read for stairs gives the OpenStreetMap fact and the outdated report, the outdated report first, with 8 and 12 m, and none of the others. Meets FR-3.

AC-5. Area and one fact. A rectangle holds an unverified report, an ordinary outdated report, a hidden report, the fact F of AC-3 and a geozone whose point is inside and whose circle reaches outside. The area read gives the first two and the geozone. Reading F by its identifier succeeds; reading the hidden report or a missing identifier gives not found. A rectangle with 1001 eligible facts gives 1000 and the sign that it holds more. Meets FR-1 and FR-2.

AC-6. The votes of the facts read. The votes of the facts of an area of 1000 facts come back in one read for all of them, each vote with its fact, and the status rule derives from them the same statuses it derives fact by fact. Meets FR-4.

AC-7. Flags and moderation. On 3 October a person without an account flags a confirmed report R; on 4 October another person flags R again; a person asks to flag an OpenStreetMap fact O. After each step: R is flagged with the day 3 October and nothing about who flagged; the second flag keeps 3 October; the lock for the flag of O gives back the source OpenStreetMap, on which the service layer refuses it, and O stays unflagged. The moderator list holds R with 3 October, not hidden. R is hidden, then hidden again - no change; while hidden R is in no area and no nearby read, its reading by identifier gives not found, the locks for a vote and for a flag give it back as hidden, and the moderator list still holds it as hidden. After the restore R is everywhere again with all its votes. The lock for moderation of a fact that was never flagged gives it back as not flagged, and nothing is written. Meets FR-2, FR-6, FR-8 and FR-9.

AC-8. A deleted account. Account A confirmed fact F on 2 October and on 3 October; A is deleted. Both votes stay with F, with no account and with the weight of an account, and a later vote written for A stores nothing and is reported as a vote of an account that no longer exists. Meets FR-4 and FR-6.

AC-9. Protected data. No result of a read of FR-1 - FR-3 or FR-9 carries the author of a fact, an account or the identifier of a person, and no log line of the layer carries the identifier of a person without an account. Meets FR-10.

AC-10. The contract and the records. Marek confirms that the written contract of the data operations answers Q-4 of `plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md`. `MVP.md` names `route_planning` as the builder of the status rule with the consent of Kuba, and the registry entry Backend handoff for vote locking during OSM publication is resolved by the rule of FR-7. Meets FR-11 and FR-12.

## Domain rules

- A person is an account or, without an account, its 32-byte identifier; a vote of a deleted account has no person and keeps the weight of an account (M4, M9; `docs/product/schema.md`, Accounts and votes).
- A report carries the confirmation of its author as its first vote, saved with it (M4).
- A person votes on a fact at most once per calendar day in Europe/Warsaw; the next vote is accepted from the start of the next calendar day, whatever the hours between them (M4).
- A fact removed in OpenStreetMap leaves the map, the routes and the check for existing facts, but can still be read by its identifier and voted on; it stays outdated until a later copy brings it back (M3, M4).
- A flag keeps nothing about who flagged, carries no reason and keeps its first instant; a fact from OpenStreetMap cannot be flagged; only a flagged fact is hidden or restored; a hidden fact takes part in no operation that is not a moderator one (M11).
- No fact and no vote is ever deleted, and a saved fact is never edited (`docs/product/schema.md`, Who writes what).
- The status of a fact is never stored and never derived here; it comes from the one status rule of `route_planning` on every read (D-11 of `MVP.md`).

## Dependencies and impact on other modules

- `schema_first_revision` built the tables, constraints and rights this layer uses; the layer works within them and changes none.
- `route_planning` supplies the status rule of its FR-16, which the service layer applies to the votes of FR-4. The existing reads of a route stay as they are; whether the new reads share code with them is a question of the plan.
- `plans/community_facts_api/` of Marek consumes every operation of this PRD and waits for FR-11; the order of delivery agreed there - reads, reports and geozones, votes, then flags and moderation - is the order in which this layer is most useful to it.
- `osm_importer` holds the other side of FR-7: it locks the disappearing facts and their votes during the publication. This layer must not add an order of locks that could deadlock with it.
- `accounts` deletes an account and detaches its votes; FR-6 tells the service layer when a vote arrived for an account deleted meanwhile.
- `sample_data` writes sample reports and geozones outside any operation; this layer reads them like any other fact. Its critical tests wait for the same local schema-owner fixture this initiative delivers (`plans/sample_data/SAMPLE_DATA_REVIEW.md`, B-2).
- `FINAL_CHECKLIST.md` places this initiative at stage 2; checks 5.1 - 5.3 are verified on the running service only after `community_facts_api` is delivered.

## Risks and notes

- The deadline: the work starts on 4 October 2026, the day the Kraków submission closes and the demo is deleted, while `community_facts_api` waits for FR-11. The contract of FR-11 is worth delivering before the full verification of FR-12.
- The wait of FR-7 can hold a vote for up to 120 seconds during a publication; the service layer and its clients have to tolerate it, which is a question of `community_facts_api`.
- Scenario 8 of the shape: deleting an account can raise the status of a fact, because its votes become persons of their own. The specification says so explicitly; it is reported to the user, not changed.
- `docs/product/specification.md` names version 17 in its Document state, while `plans/community_facts_api/COMMUNITY_FACTS_API_PRD.md` and the registry cite version 18 for the IP + User-Agent rule of M9, whose text is already in the specification. The discrepancy is reported, not resolved here.
- `MVP.md` says in one place that the status rule moved to `route_planning` and in another that Kuba retains the status evaluator; the consent of this PRD settles it for FR-12, and `plans/community_facts_api/COMMUNITY_FACTS_API_PRD.md`, approved, keeps its wording until its owner changes it.
- No query time has been measured; the volume - facts in the thousands in Kraków, at most 1000 per area, tens of votes per fact at most - is estimated in the shape, Notes on data, performance and security, and the plan measures it on the local database.
