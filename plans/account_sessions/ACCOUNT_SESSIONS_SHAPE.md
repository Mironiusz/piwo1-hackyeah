# Shape: Choice of the session mechanism of MVP accounts

Document state: 2026-10-03, interview closed
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) has light accounts with a pseudonym and a password, contributions without an account, and a moderator role assigned by hand. How a logged-in person is recognized on later requests, and how the service tells a moderator from other users, was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the backend person of the team. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- The frontend consumes the session contract and is to be consulted before the backend decision is handed to `plans/mvp/MVP_PLAN.md` Q-6.
- `plans/mvp/MVP_PLAN.md`, open question Q-6, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.
- Agent decision at C:40, without asking: record the decision before `plans/mvp/MVP_PLAN.md` resumes and no later than the Kraków submission deadline at 11:00 on 2026-10-04.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- `docs/product/specification.md`, M9: an account is a pseudonym and a password, without an email address and without any question about a disability; deleting an account removes the account and the pseudonym, while reports and votes stay detached with their weight. M11: a moderator is a member of the team whose role is assigned by hand.
- `plans/mvp/MVP_PRD.md`, FR-14 and AC-13: in the mandatory MVP, moderators see flagged reports and geozones and can hide them; users without the role cannot open the moderator view. The PRD makes photo requirements conditional on optional feature O2, so photo moderation is not part of the mandatory scope.
- `docs/standards/standard_tests.md`, Mandatory tests: permissions and visibility are tested with a matrix over all roles, separately for the list and the detail view, in both directions.
- `docs/standards/standard_config.md`, Secrets: a secret never enters the repository, and a secret in the settings model has the type `SecretStr`.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans/demo_environment/`, open question 3, asks whether people outside the team create accounts or votes in the demo environment and who deletes that data after the hackathon; the answer decides whose pseudonyms and passwords the accounts of this initiative hold.
- At the start of this interview, the repository was checked for answers to its open questions - the specification, `plans/mvp/`, `docs/standards/` and the shapes of the sibling initiatives. They did not settle the decisions recorded below.

## Smallest meaningful scope

Following from the seed: a decision on the session mechanism of accounts and on how a request is resolved to an actor and a role, taken by the backend owner in agreement with the frontend consumer. It also settles how the same 30-day hash prevents a second vote when a person switches between an account and an anonymous contribution. The initiative records the decision and hands it to `plans/mvp/MVP_PLAN.md` Q-6; it does not build the accounts. The user chose this scope on 2026-10-03.

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`. The derivation and 30-day retention of the hash stay as specified in `plans/mvp/MVP_PRD.md` FR-13; this initiative extends its use to account votes to prevent cross-mode duplicate votes.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-12 and AC-11 - create an account with a pseudonym and a password, log in, log out, delete the account; after deletion the pseudonym cannot be found anywhere in the app.
2. FR-14 and AC-13 - a moderator sees flagged reports and geozones in a moderator view and hides them; a user without the role cannot open the view. Photo moderation applies if optional feature O2 is implemented.
3. FR-6 and AC-6 - one vote per fact per account and no second vote when the same 30-day hash switches between account and anonymous contributions.
4. FR-1 - the preference profile never reaches the account.

## Scenarios: input, flow, expected state after the run

1. Rolling session. Input: an account logs in on Monday at 08:00 and makes a request at 20:00, then closes and reopens the browser on Tuesday at 07:00. Flow: every request in the active session renews its lifetime. Expected state: the account is recognized after reopening, and the session expires 24 hours after the most recent request if there is no later activity.
2. Cross-mode duplicate vote. Input: a person votes on a fact while logged in, logs out, then votes on the same fact anonymously from the same browser and network within 30 days. Flow: both requests produce the same one-way hash of the IP address and browser characteristics. Expected state: the second vote is rejected, the person contributes only once, and raw IP and browser values are not kept.
   After the hash expires and is deleted, a later anonymous vote with the same hash may be accepted. Account-level uniqueness still prevents a second vote from the same account.
3. Moderator role removal. Input: a moderator is logged in and the team removes the role. Flow: the account's next request attempts to open the moderator view while its session remains active. Expected state: access is denied because the role is no longer assigned.
4. Password forgotten. Input: a person created an account and later forgets its password. Flow: the person attempts to log in without an email address or recovery method. Expected state: the account cannot be recovered; reports and votes remain after account deletion, detached from the account.

## Challenging own assumptions

- Without an email address there is no password recovery. The user confirmed on 2026-10-03 that a forgotten password may result in a lost account and that the MVP will not implement password recovery.
- The moderator role is not only a technical flag: it decides who sees flagged content and can hide it, which is a visibility rule tested in both directions.
- The same 30-day hash must prevent a person from voting twice on a fact after switching between account and anonymous contributions. The user chose this and approved retaining the hash for account votes as well on 2026-10-03.

## Domain rules or explicit TODO

- Weights: a logged-in person counts 1 and a person without an account 0.5 (`docs/product/specification.md`, M4); whether a request comes from an account therefore changes the status of a fact.
- Nothing about the author of a report, vote or geozone is shown to other users (`docs/product/specification.md`, M9).
- The user chose a rolling session that expires 24 hours after the last activity, survives closing and reopening the browser, and renews on every request in the active session, including read-only requests, on 2026-10-03.
- Pseudonyms are unique without regard to letter case; the user chose this on 2026-10-03.
- Passwords follow NIST SP 800-63B-4, except the user chose a minimum of 5 characters and no rejection of common or breached passwords on 2026-10-03. The remaining rules are a maximum length of at least 64 characters, accepting printable ASCII, spaces and Unicode, and no character-composition or periodic-change requirements. This is an explicit deviation from NIST's 15-character minimum and blocklist requirement for single-factor passwords.
- The team chose that removing a moderator role revokes access on the next request, even if the account's 24-hour session remains active, on 2026-10-03.
- Every vote is subject to the same 30-day one-way hash of the IP address and browser characteristics, including votes made by account. The user chose this to reject a second vote with the same hash after switching authentication state on 2026-10-03. The hash is deleted after 30 days and raw values are never retained. Once it expires, a later anonymous vote with the same hash may be accepted; account-level uniqueness continues to reject another vote by the same account.

## Notes on data, performance and security

- Password storage and the technical session mechanism are implementation decisions for phase B of `plan-prd`; any secret used by the selected mechanism is governed by `docs/standards/standard_config.md`.
- The pseudonym is personal data stated in the privacy information (`plans/mvp/MVP_PRD.md` FR-20).
- The 5-character minimum and omission of a common or breached password blocklist make passwords easier to guess than the NIST SP 800-63B-4 policy. That standard requires a 15-character minimum and a blocklist for single-factor passwords: [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html).
- The pseudonym points to a specific person, so it goes into a log only masked or replaced by an internal technical identifier (`docs/standards/standard_logging.md`, the rule on identifiers of a person in log entries); a password or a session value never goes into a log in any form (the same standard, the rule on secrets).
- Retaining the anonymous vote hash for account votes makes the account's network and browser characteristics pseudonymously linkable to its votes for up to 30 days. After expiry, the hash no longer blocks a later anonymous vote, while the per-account uniqueness rule remains in force.

## Open questions

1. The technical session mechanism and request contract are decisions for phase B of `plan-prd`, in agreement with the frontend consumer. `Block: no`
