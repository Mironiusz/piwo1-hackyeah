# PRD: Domain model and database schema of facts and votes for the MVP

Document state: 2026-10-03

## Business goal

Give every part of the MVP one agreed answer to what a barrier or an amenity is, who can vote on it, how its status follows from the votes and what happens to it when OpenStreetMap changes, and make that answer exist as stored data in the local database. The programming interface (`plans/api_contract/`, Q-9 of `plans/mvp/MVP_PLAN.md`) waits for it to name its resources and statuses, and it is the start of the critical path Q-10 -> Q-9 towards the Kraków deadline at 11:00 on 4 October 2026.

It serves the judging criterion "Data reliability, presentation and updates" (15%) of the Kraków brief directly: source, date and status of every fact, and the contradiction between OpenStreetMap and a user report that the demo has to show, all rest on these rules.

## Problem and its consequences

Reports, votes, statuses, geozones, OpenStreetMap facts, accounts and moderation all read and write the same data, and nothing says yet what that data is. Without one model the import, the route, the voting and the interface each guess the shape of a fact: a status computed differently in two places shows a barrier as confirmed on the map and disputed on the list, a vote counted twice lets one person confirm a barrier alone, and an OpenStreetMap fact that loses its votes on a refresh throws away what people confirmed. The specification, version 3, still contradicts its own scenario on the disputed status, and does not state that a vote without an account keeps its weight after its identifier is deleted, a rule that lives only in `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-21.

## Scope

- The rules of facts, votes, statuses, geozones, OpenStreetMap facts, accounts, flags and hiding of `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, section Domain rules, with the values of x and k approved at the gate of this PRD.
- The target schema written as the part of the product specification against which a schema change is reviewed, decided in the shape (question 2).
- The proposal of the changes to the specification and to `plans/mvp/MVP_PRD.md` that these rules require, for the user to approve.
- The stored data created in the local database, with tests that run the scenarios of the acceptance criteria below.
- The initiative is delivered in two tasks, decided by the user on 2026-10-03 in phase B of the task `FACT_SCHEMA` (`plans/fact_schema/FACT_SCHEMA_REVISION_SEED.md`). The task `FACT_SCHEMA` writes the target schema that holds FR-1 - FR-13 and the proposed changes of FR-14, and meets AC-13. The task `FACT_SCHEMA_REVISION` creates the stored data of FR-15 and meets AC-1 - AC-12, once the local database and the backend skeleton named under Dependencies exist. The importer and the backend share the stored data, so the target schema is one schema for both.

## Out of scope

- The backend architecture with the worker, including the job that deletes expired votes on time: `plans/mvp/MVP_PLAN.md` Q-11.
- The programming interface: `plans/api_contract/` (Q-9). The session storage of logged-in users: `plans/account_sessions/` (Q-6).
- How the identifier of a vote without an account is computed from the IP address and the browser characteristics, and how a route is related to the stretches of way: the voting and route work packages of `plans/mvp/`, and `plans/routing_engine/`.
- The thresholds and value lists of the tag mapping, constants of `plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-14, and the source of the OpenStreetMap copy, settled by `plans/mvp/MVP_PLAN.md` D-4.
- The import itself, which writes OpenStreetMap facts by these rules: a work package of `plans/mvp/` after Q-11.
- The optional features O1-O8; the rules must not block them, in particular photos (O2), which add weight to a vote, and points (O3), which are removed with an account.

## Functional requirements

FR-1. A fact is a barrier or an amenity of a type from the closed list of `docs/product/specification.md` M3, at a place, with a source - OpenStreetMap or user report - a status, and the date it was obtained or last confirmed. The same requirement covers point reports, geozones and OpenStreetMap facts.

FR-2. A point report has an optional description and, for stairs, an optional number of steps. Once saved it is never edited. It carries the vote of its author as a confirmation. A report and a geozone can carry the sample data mark.

FR-3. A geozone is a point with a radius chosen from 10, 25, 50 and 100 m and a barrier type. It is never edited after saving and gets votes and statuses like a point report.

FR-4. An OpenStreetMap fact is identified by the type of its OpenStreetMap element (node, way or relation), the identifier of that element and the fact type, as `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-7 decides. It shows the date of its last OpenStreetMap edit, the calendar day of `plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-15. The date of the OpenStreetMap copy in use is known at any time.

FR-5. For every way of the pedestrian network, what is known about each of stairs, poor surface, steep incline and narrow passage is kept as one of the states present, absent, absent by default and unknown, where absent by default exists only for stairs, together with the rest of what the tag mapping gives: the number of steps, the `wheelchair=no` marking, the point facts and kerb points of its nodes, whether a node also belongs to a way for motor traffic, and the amenity facts of any element at a point (`plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6). All of it is kept once and independently of any profile. The state of a route segment is not kept; it is derived for each route.

FR-6. On a fresh OpenStreetMap copy: an OpenStreetMap fact missing from the copy becomes a user fact with its votes when its confirmations outweigh its denials, otherwise it becomes outdated with the reason that it was removed in OpenStreetMap; a fact that returns on the same element with the same type is the same OpenStreetMap fact again with all its votes; an OpenStreetMap fact and a user fact of the same type at the same place stay separate. The reconciliation follows `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-10, and a fresh copy, its reconciliation and its date become visible in one commit or not at all (D-9 there).

FR-7. A person is an account, or for a vote without an account the hashed identifier of `docs/product/specification.md` M9. A person confirms or denies a fact, with the weight 1 for an account and 0.5 without one. A person votes on the same fact again only once x days have passed since their previous vote on it; an earlier vote is refused. Of the votes of one person on a fact only the latest counts. A vote cannot be withdrawn without casting another.

FR-8. The status of a fact is derived from the latest votes of the k persons who voted on it most recently, in this order: outdated when the denials reach at least 2 and outweigh the confirmations; otherwise disputed when there are both confirmations and denials; otherwise confirmed when the confirmations reach 2; otherwise unverified. An OpenStreetMap fact prevails until the denials in its window reach 2, and then becomes outdated. A confirmation updates the date of last confirmation of any fact.

FR-9. The identifier of a vote without an account is deleted 30 days after the vote was cast. The vote stays with its weight for as long as the fact exists (`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-21), belongs from then on to no person and counts in the window as the vote of a person of its own. Votes of an account never expire. No status changes with time alone.

FR-10. An account has a pseudonym, unique without regard to letter case, and a password, and can hold the moderator role, assigned by hand. Deleting an account removes the account and the pseudonym; its reports and votes stay with their weight, detached, each vote counting as a person of its own, and the pseudonym can be taken again.

FR-11. Anyone can flag a report, a geozone or a fact converted from OpenStreetMap; an OpenStreetMap fact cannot be flagged. A flag keeps nothing about who flagged. A moderator hides flagged content and can restore it. A hidden fact is out of the map, the list, the route, the segment states and the duplicate check, and cannot be voted on; restored, it counts again with the votes it still has.

FR-12. Nothing about the author of a report, a vote or a geozone, nor the weights behind a status, reaches any user, a moderator included.

FR-13. The facts of a given type within about 15 m of a point can be found, OpenStreetMap facts included and hidden facts excluded, for the duplicate check of a report.

FR-14. The target schema is written as the part of the product specification decided in the shape, and the changes these rules make to `docs/product/specification.md` and to `plans/mvp/MVP_PRD.md` are proposed for the user to approve, before the stored data is created.

FR-15. The stored data exists in the local database and refuses, by itself, the states these rules forbid: a second counted vote of one person within x days, a fact type outside the closed list, a geozone radius outside the list, two accounts with pseudonyms differing only in letter case, and two facts with the same OpenStreetMap identity, converted and outdated ones included (`plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-10, point 7).

## Acceptance criteria

AC-1 (FR-7, FR-8). The run of `plans/mvp/MVP_SHAPE.md` scenario 3 gives, after each step: unverified, unverified, confirmed, disputed.

AC-2 (FR-8). The run of `plans/mvp/MVP_SHAPE.md` scenario 5 keeps the OpenStreetMap stairs after the second denial and marks them outdated after the third.

AC-3 (FR-7, FR-8). The run of `plans/fact_schema/FACT_SCHEMA_SHAPE.md` scenario 3 with x = 1 day and k = 5 gives: the repeated vote of U on 1 October refused and F unverified; F confirmed on 3 October; disputed on 8 October with confirmations 1.5 and denials 1; outdated on 10 October with person A out of the window.

AC-4 (FR-9). The run of `plans/fact_schema/FACT_SCHEMA_SHAPE.md` scenario 1 gives G confirmed on 3 October with the repeated confirmation refused, and still confirmed with 2.0 on 31 October and on 2 November, with the report still existing. No identifier of a vote exists 30 days after the vote was cast, while the vote still counts.

AC-5 (FR-9). The run of `plans/fact_schema/FACT_SCHEMA_SHAPE.md` scenario 2 gives S outdated on 1 October and still outdated on 31 October, with denials of 2.5.

AC-6 (FR-6). The runs of `plans/osm_data_source/OSM_DATA_SOURCE_SHAPE.md` scenarios 1 to 3 give their expected states: stairs on W a user fact with 1.5 of confirmations after the fresh copy; poor surface on V outdated with the reason that it was removed in OpenStreetMap, the denial kept in its history; one stairs fact on W, an OpenStreetMap fact with its 2.0 of confirmations, after the return.

AC-7 (FR-4, FR-6). A way of an OpenStreetMap stairs fact with 1.5 of confirmations is split in a fresh copy, the first part keeping the identifier: that part keeps the fact with 1.5, and the other part has a new stairs fact with no votes.

AC-8 (FR-7). Two votes on the same fact from the same account, or from the same identifier without an account, less than x days apart: the second is refused. The same two votes x days apart: both are kept and only the second counts.

AC-9 (FR-10). After an account that confirmed a fact is deleted, its pseudonym exists nowhere, the fact keeps its status, and a new account with the same pseudonym can be created and can vote on the same fact, both votes counting. An account with a pseudonym differing from an existing one only in letter case is refused.

AC-10 (FR-11, FR-13). A hidden report is not found by the duplicate check, cannot be voted on and is not among the facts of a route; after it is restored, it is again, with its earlier status. A flag on an OpenStreetMap fact is refused.

AC-11 (FR-3, FR-15). A geozone with a radius of 30 m, a fact of a type outside the closed list and a second fact with the same OpenStreetMap identity are refused by the stored data itself.

AC-12 (FR-12). No reading of a fact, its status or the moderator view returns the author of a report, a vote or a geozone, the pseudonym or the weights.

AC-13 (FR-14). The target schema exists as the part of the specification decided in the shape, the stored data matches it line by line, and the proposed changes to `docs/product/specification.md` and `plans/mvp/MVP_PRD.md` are approved by the user.

## Domain rules

The rules are those of `plans/fact_schema/FACT_SCHEMA_SHAPE.md`, section Domain rules, with these values approved at the gate of this PRD:

- x = 1 day: a person votes on the same fact at most once a day. Proposed by the agent and approved by the user on 2026-10-03, in place of the db person; the ruling of the db person is still to be confirmed.
- k = 5: the status counts the latest votes of the five persons who voted most recently. Same provenance. With k = 5, four persons without an account can confirm a fact alone, and every scenario quoted in the acceptance criteria keeps its result.
- x and k stay configuration values, so that a later change does not change the rules.
- The 1 day and the 30 days run from the instant of the vote, not from calendar days in the Europe/Warsaw zone.
- Dates shown to users are calendar days in the Europe/Warsaw zone (`docs/product/specification.md`, M10).
- Missing information is never presented as a confirmation of accessibility, and no status changes with time alone, also when the identifier of a vote is deleted (`plans/fact_schema/FACT_SCHEMA_SHAPE.md`, section Challenging own assumptions).

## Dependencies and impact on other modules

- `plans/api_contract/` (Q-9) waits for this PRD for the resources and statuses it exposes; it can start once this PRD is confirmed, before the stored data exists.
- The stored data waits for the local database with PostGIS of `plans/local_database/` (Q-4) and for a backend skeleton that holds the schema changes, which no plan has built yet (`docs/standards/decision_registry.md`, Technical directions of the MVP plan). That wait belongs to the task `FACT_SCHEMA_REVISION` only; the task `FACT_SCHEMA` waits for neither.
- `docs/product/specification.md` changes in a later version, since version 3 was approved without these rules: M4 (vote limit and window, order of statuses), M9 (the identifier serves the vote limit of M4, and a vote keeps its weight after its identifier is deleted, the rule of `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` D-21 that version 3 left out) and M11 (restoring hidden content). The specification gains the part with the target schema.
- `plans/mvp/MVP_PRD.md` changes in AC-6: a second confirmation by the same account is refused within x days, not for ever.
- `plans/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6 decides what the import gives for every element, which FR-5 keeps, and D-15 the date of an OpenStreetMap fact.
- `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` settles, in parallel with the shape of this initiative, the identity of a split or joined way (D-7), which FR-4 and AC-7 follow, and the weight of a vote after its identifier is deleted (D-21), which FR-9 follows. Its D-9 leaves to this initiative how a fresh copy is stored - written in one transaction, or switched to once fully written - under the constraint of FR-6, and its D-10 fixes the reconciliation and the unique constraint of FR-15.
- Deleting the identifiers of votes without an account after 30 days needs a job of the worker of `plans/mvp/MVP_PLAN.md` Q-11.
- `plans/routing_engine/` relates a route to the stretches of way of FR-5; to be checked against it when it closes.

## Risks and notes

- Time: the stored data cannot be created before Q-4 and a backend skeleton exist, and every hour they wait is taken from the time before the Kraków deadline.
- The rules were decided by the user, not by the db person who owns Q-10, and the OpenStreetMap rules by the user for the import person; either ruling can still change them.
- After 30 days the browser of a person without an account can vote on the same fact again as a new person, and both votes count, because the earlier vote keeps its weight but no longer its identifier. This is visible only after 30 days, so not in the demo.
- One person with two accounts confirms a fact alone; the specification names no protection, and none is added.
- With x = 1 day, a person who confirmed a barrier in the morning and sees it gone in the afternoon denies it only the next day.
- Until the job of Q-11 runs, an identifier older than 30 days still exists, which keeps pseudonymized personal data longer than `docs/product/specification.md` M9 allows; it changes no status.
- The identifier of a vote without an account is pseudonymized personal data in the sense of the GDPR; the optional description of a report is free text that may carry personal data, controlled only by moderation.
- The pseudonym rule, the closed list of geozone radii, the ban on flagging OpenStreetMap facts, a flag without its author, a vote without an identifier counting as a person of its own, and proposing D-21 of `plans/osm_data_source/OSM_DATA_SOURCE_PLAN.md` for M9 are agent decisions of the shape, open to correction by the user.
