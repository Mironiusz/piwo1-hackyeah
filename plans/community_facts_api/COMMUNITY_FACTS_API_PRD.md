# PRD: API and service layers of community facts

Document state: 2026-10-04, approved by the user

## Business goal

Enable both clients to show accessibility facts with their source, date and reliability status, accept reports and geozones with or without an account, and let people confirm, deny or flag facts while moderators can hide and restore flagged content. The result makes checks 5.1 - 5.3 of `FINAL_CHECKLIST.md` verifiable through the running service and supplies the community contribution part of EnableMe's main scenario.

This PRD follows the closed `COMMUNITY_FACTS_API_SHAPE.md` at C:40 and version 18 of `docs/product/specification.md`, especially M3 - M5, M9 - M11 and Personal data. The specification prevails; `docs/product/api_contract.md`, sections Shared objects, Sessions and actors, Facts and Moderation, governs what the clients send and receive.

## Problem and its consequences

The behavior of community facts is agreed, but clients cannot yet use its nine operations through the service. Kuba's part supplies the data access and shared status evaluation; it does not by itself provide the request validation, recognition of the caller, coordination of an action and contracted responses this task delivers.

Without this part, the map cannot show real facts from the backend, a person cannot save or verify a barrier, and moderation cannot remove flagged content from public use. A report retried after a lost response risks being counted twice unless the agreed single-save behavior is enforced. Incorrect visibility or anonymous identification would either expose hidden content or apply a person's voting limit to the wrong identity.

## Scope

- The API and service behavior of all nine capabilities: facts in an area, one fact by identifier, nearby facts of the same type, saving a report or geozone, casting a vote, flagging a fact, listing flagged facts, hiding a flagged fact and restoring it.
- Validation, safe failures, the shared fact representation, caller recognition and session renewal required by the existing contract.
- Saving a report together with its author's first confirmation, single-save behavior on retry, and daily voting limits.
- Anonymous identification from IP + User-Agent only, including the accepted shared identity of identical pairs.
- Integration with Kuba's data access and shared status evaluation and with the account recognition supplied by the accounts initiative.
- Verification and documentation of the delivered behavior. Marek owns this task; Kuba retains the data layer and the status evaluator.

The agreed delivery order is reads, reports and geozones, votes, then flags and moderation. An intermediate delivery of reads alone does not complete the task.

## Out of scope

- Building Kuba's data operations or replacing the shared status evaluator.
- Changing the target schema, account operations or shared account and moderator recognition.
- Client screens, the device's memory of its own vote, report-summary approval in the client, route calculation, OpenStreetMap importing or sample-data generation.
- Photos, editing saved reports or geozones, automatically merging facts, and other optional product features.
- Hosting changes. The implementation plan must agree how the service obtains the permitted identifying inputs; this PRD introduces no hosting solution.

## Functional requirements

FR-1. Contracted operations. All nine capabilities in Scope accept and return exactly what the agreed programming-interface contract specifies. Missing, unknown, wrongly typed or invalid input is refused with the appropriate safe failure. No failure exposes internal diagnostics or identifying data.

FR-2. Fact presentation and visibility. Public reads return the source, the applicable dates, reliability status, sample-data marker and flagging eligibility of a fact. They reveal neither its author's identity nor whether the author had an account. Hidden facts are treated as missing in every non-moderator operation, including public reads, votes, flags and responses to repeated saves.

FR-3. Area read. Return the facts whose point is in the requested rectangle, with every reliability status except facts outdated because they were removed in OpenStreetMap. A geozone is included by its point. Return at most 1000 facts and indicate when there are more. An invalid rectangle is refused.

FR-4. Detail and nearby reads. A non-hidden fact can be read by identifier in any status, including one removed in OpenStreetMap. The nearby check returns facts of the requested type within 15 m, nearest first, with distances in whole metres. It includes OpenStreetMap facts and ordinary outdated facts, and excludes hidden facts and facts removed in OpenStreetMap. The service merges nothing automatically.

FR-5. Saving a contribution. Save a point report or barrier geozone together with the author's first confirmation, both or neither. The types are the closed list of M3. A description is optional and is limited to 500 characters after leading and trailing spaces are removed; an empty description becomes absent. A step count is optional, applies only to stairs and is from 1 to 999. A geozone has a barrier type and a radius of 10, 25, 50 or 100 m. A new contribution is unverified. Saved contributions are immutable.

FR-6. One save per approved contribution. The first save succeeds as a new contribution. A repeated save with the same client-generated idempotency key and the same normalized content returns the original fact without another fact or author confirmation, subject to FR-2. Reusing that key for different content is refused and changes nothing. Retrying after a lost response must not produce a duplicate.

FR-7. Votes and returned status. Accept a confirmation or denial from an account or an anonymous person on a non-hidden fact, including an OpenStreetMap fact. Return the fact with its status after the accepted vote, using the shared rules of M4. Account deletion does not change the weight of existing votes. A vote that arrives during publication of a fresh OpenStreetMap copy is checked against the committed publication state before it is accepted; a failed publication leaves the prior state in force.

FR-8. Daily limit. The same person may vote on the same fact at most once per Europe/Warsaw calendar day. A refused same-day vote states the instant of the next midnight from which another vote may be accepted. A later-day vote replaces that person's earlier vote for status calculation and never adds that person's weight again. A same-day retry after a lost vote response is refused by the same rule.

FR-9. Anonymous identity and privacy. The service derives anonymous identity from IP + User-Agent only and keeps only their one-way hash for the agreed purpose and retention. Identical pairs share one identity for both the daily limit and the latest-vote rule. The client sends no additional identifier and receives none. Raw identifying inputs and the hash are absent from responses and request logs. A flag records nothing about its author.

FR-10. Sessions and permissions. Reuse the existing recognition of an anonymous person, an account and a current moderator, including renewal on requests with a valid session. A supplied invalid, expired or deleted-account session is refused and never converted into an anonymous contribution. An ordinary account and an anonymous person cannot moderate. Removing the moderator role revokes moderation on the next request.

FR-11. Flagging and moderation. Anyone can flag a visible report, geozone or fact converted from OpenStreetMap to a user report. An OpenStreetMap fact cannot be flagged. Repeating a flag preserves its first instant. A moderator can read all flagged facts, hidden ones included, most recently flagged first, with the flag day and hidden state but no author identity. Only flagged facts can be hidden or restored; repeating either action is harmless. Restoration preserves the votes and exposes the fact under its resulting status again.

FR-12. Verification and records. Demonstrate the contracted behavior of all nine capabilities, including refusal and retry cases, through service-level checks. Document the delivered behavior and its dependencies, and update the MVP handoff and decision records for what this task actually settles. The work does not claim completion of the client screens or of another initiative.

## Acceptance criteria

AC-1. The nine capabilities of Scope are callable through the running service and match the agreed requests, successful responses and failures. Invalid types, unknown input, invalid rectangles and invalid contribution values are refused without a write or disclosure of protected input. Meets FR-1 and FR-12.

AC-2. An area containing an unverified report, an ordinary outdated report, a hidden report and a removed OpenStreetMap fact returns the first two and excludes the latter two. A matching geozone is included by its point. A result with more than 1000 eligible facts contains at most 1000 and indicates truncation. Meets FR-2 and FR-3.

AC-3. Opening an ordinary outdated fact or a non-hidden removed OpenStreetMap fact by identifier succeeds. Opening a hidden or missing fact returns the contracted missing-fact failure. Every returned fact has its applicable source, dates, status, sample marker and flagging eligibility without author identity. Meets FR-2 and FR-4.

AC-4. At 08:00 an OpenStreetMap stairs fact is marked removed. At 08:05 a person checks for stairs 8 m away: the removed fact is absent, but an ordinary outdated stairs report in the radius remains a candidate. Eligible candidates are ordered nearest first; facts of another type, hidden facts and facts farther than 15 m are absent. Meets FR-4.

AC-5. Saving stairs with three steps creates one unverified fact and one author confirmation. A failure during either part leaves neither a partial fact nor a partial confirmation. Saving a barrier geozone with each permitted radius succeeds; an amenity geozone, unsupported radius, excessive description or invalid step count is refused. Meets FR-5.

AC-6. A successful stairs report with key K loses its response. Repeating the same normalized content with K returns the original fact and stores no second fact or vote. Repeating K with four steps instead of three is refused and changes nothing. If the original fact has been hidden, the repeated response reveals no hidden content and treats it as missing. Meets FR-2 and FR-6.

AC-7. An anonymous report's initial confirmation has weight 0.5. Two distinct accounts then confirm it on eligible days: confirmations progress from 0.5 to 1.5 to 2.5, and the status progresses from unverified to unverified to confirmed. A denial then makes it disputed unless the outdated rule applies. Responses carry the resulting status, while weights and voter identity remain internal. Meets FR-2, FR-5 and FR-7.

AC-8. The shared status rules count only each person's latest vote among the five persons who voted most recently. A later-day repeat confirmation by one person adds no weight; a sixth person displaces the oldest person's vote from that window. A vote from a deleted account retains its original weight and counts as a person of its own. The day of the last confirmation remains correct. Meets FR-7 and FR-8.

AC-9. A confirmation at `2026-10-04T23:59:59.000+02:00` is accepted. A second vote by the same identity on that fact at `2026-10-04T23:59:59.900+02:00` is refused with `2026-10-05T00:00:00.000+02:00` as the next permitted instant. A vote just after that midnight succeeds; a retry on that same new day is refused. Meets FR-8.

AC-10. At 10:00 person A confirms a fact anonymously. At 10:01 person B with the same IP and User-Agent is refused on that fact as the same identity. After the next midnight B may vote, and the latest vote represents their shared identity. Changing only another browser characteristic does not change that identity. Neither the identifying inputs nor the hash appear in a response or request log. Meets FR-9.

AC-11. A report or vote sent with an expired, invalid or deleted-account session is refused, writes nothing and is not retried internally as anonymous. Requests carrying a valid session follow the contract's renewal rule. Anonymous and ordinary-account moderation requests are refused; a removed moderator role is effective on the next request. Meets FR-10.

AC-12. A person flags a visible report on 3 October and another person repeats the flag on 4 October. The flag day remains 3 October and no author or reason is recorded. A geozone and a converted user fact can be flagged; a current OpenStreetMap fact cannot. A hidden fact is treated as missing. Meets FR-2, FR-9 and FR-11.

AC-13. A moderator's list contains all flagged facts, including hidden ones, ordered by their first flag instant from latest to earliest. Hiding a flagged confirmed report removes it from public reads and nearby checks and prevents voting or flagging it; repeating hide succeeds without a further change. Restoring it exposes it again with its retained votes and status; repeating restore is harmless. Hiding or restoring an unflagged fact is refused. Meets FR-2 and FR-11.

AC-14. A vote arrives while a fresh OpenStreetMap publication is reconciling that fact. It is evaluated against the committed outcome rather than an intermediate state, and the returned status reflects the accepted vote and that outcome. If publication fails, the vote is evaluated against the prior committed state. Meets FR-7.

AC-15. The documentation explains the complete delivered operation set, permission and visibility rules, retry behavior and accepted anonymous-identity limitation. Checks 5.1 - 5.3 can exercise this task's behavior when its data and account dependencies are delivered; records name remaining dependencies rather than claiming that other initiatives are complete. Meets FR-12.

## Domain rules

- A fact describes a concrete barrier or amenity, not a general accessible / inaccessible score. Its source and reliability status are separate; missing information is never a confirmation of accessibility.
- Statuses are unverified, confirmed, disputed and outdated. They do not decay with time alone. Every new report and an OpenStreetMap fact without votes is unverified.
- A vote with an account weighs 1 and an anonymous vote weighs 0.5, including the author's first confirmation. The latest votes of the five persons who voted most recently determine the status: outdated when denials reach 2 and outweigh confirmations; otherwise disputed when both exist; otherwise confirmed when confirmations reach 2; otherwise unverified. The sums and voter identities stay internal.
- A fact removed in OpenStreetMap stays outdated regardless of votes until a later OpenStreetMap copy restores it under the existing import rules. It is absent from the map and nearby check, but may be read directly when not hidden. Ordinary outdated facts remain available for confirmation.
- One identity may vote on one fact once per Europe/Warsaw calendar day. Anonymous identity is IP + User-Agent; identical pairs share that identity. Voting anonymously and through an account counts as two identities, as M9 already accepts.
- Dates are Europe/Warsaw calendar days; a next-vote instant includes the offset applicable at that next midnight.
- A report and its first confirmation are saved together or not at all. The client-generated idempotency key identifies a save; repeating its normalized content does not create another contribution.
- The client decides whether a nearby fact is the same barrier. A new report is never automatically merged with another fact and is immutable after saving.
- A flag has no author and no reason and keeps its first instant. Only flagged facts can be hidden or restored. Moderator visibility includes hidden facts; public visibility never does.
- The anonymous hash is retained for the vote limit and latest-vote rule until the demo and its data are deleted on 4 October 2026, with no raw IP or User-Agent kept by vote identification. No disability disclosure is required.

## Dependencies and impact on other modules

- Kuba supplies the community-fact data operations and shared status evaluation, including coordination with OpenStreetMap publication. This task consumes them; their actual delivery and integration contracts must be verified when preparing the implementation plan.
- The accounts initiative supplies shared recognition of the caller and current moderator role and session renewal. Those capabilities are required even for optional-session reads; absence of their delivery does not authorize bypassing them.
- The backend foundation supplies shared request correlation, safe failures and logging. This task extends that foundation rather than defining a competing contract.
- Adrian and Kuber consume the agreed community-fact responses in the web and HarmonyOS clients. Their confirmation of the existing contract and its amendments remains outstanding, as recorded in the contract and MVP.
- Mateusz's importer and Marek's route work consume the shared status rules. Coordination of a vote with an import must preserve the publication agreement, and hidden facts remain excluded from route behavior by the specification. This task does not implement routing or importing.
- The implementation plan must settle the hashing method, trusted source of the IP address, invalid or missing identifying-input behavior and query-volume checks within the already approved data boundary. It must also verify the local database state and the team handoff recorded in the decision registry before claiming implementation readiness.

## Risks and notes

- IP + User-Agent is a request identity, not proof of a unique human. People with identical pairs share a daily limit and a status contribution; a changed pair can represent another identity. The identical-pair limitation was disclosed and accepted for the demo.
- Replaying a save after the fact was hidden must still respect public visibility. Single-save behavior cannot expose hidden content.
- Data and account delivery are prerequisites for full running-service acceptance. A completed PRD is not evidence of those prerequisites or of working operations.
- The area read is bounded at 1000 facts, but the moderator list returns all flagged facts under the existing contract. Actual query cost and vote-history volume require verification in the implementation plan; this PRD claims no measured latency.
- The source of the IP address and the handling of malformed or missing User-Agent must not be guessed. Those technical decisions must be explicit before implementation, and they cannot expand the accepted identifying inputs.
- This document adds no product behavior beyond the closed shape and authoritative specification and contract. Technical verification that contradicts an assumption requires returning to the PRD rather than working around it silently.
