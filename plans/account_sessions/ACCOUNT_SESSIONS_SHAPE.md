# Shape: Choice of the session mechanism of MVP accounts

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) has light accounts with a pseudonym and a password, contributions without an account, and a moderator role assigned by hand. How a logged-in person is recognized on later requests, and how the service tells a moderator from other users, was not decided in phase B of `plans/mvp/`; the user handed the decision to the people responsible for it.

## Recipient and trigger

- The owner of the decision is the backend person of the team. The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-6, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- No product code exists. The backend is decided in `plans/mvp/MVP_PLAN.md` D-1: Python 3.13 with FastAPI, on PostgreSQL with PostGIS.
- `docs/product/specification.md`, M9: an account is a pseudonym and a password, without an email address and without any question about a disability; deleting an account removes the account and the pseudonym, while reports and votes stay detached with their weight. M11: a moderator is a member of the team whose role is assigned by hand.
- `plans/mvp/MVP_PRD.md`, FR-14 and AC-13: in the mandatory MVP, moderators see flagged reports and geozones and can hide them; users without the role cannot open the moderator view. The PRD makes photo requirements conditional on optional feature O2, so photo moderation is not part of the mandatory scope.
- `docs/standards/standard_tests.md`, Mandatory tests: permissions and visibility are tested with a matrix over all roles, separately for the list and the detail view, in both directions.
- `docs/standards/standard_config.md`, Secrets: a secret never enters the repository, and a secret in the settings model has the type `SecretStr`.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- `plans/demo_environment/`, open question 3, asks whether people outside the team create accounts or votes in the demo environment and who deletes that data after the hackathon; the answer decides whose pseudonyms and passwords the accounts of this initiative hold.
- On 2026-10-03 the repository was checked for answers to the open questions of this shape - the specification, `plans/mvp/`, `docs/standards/` and the shapes of the sibling initiatives. None of them settles any of the questions.

## Smallest meaningful scope

Following from the seed: a decision on the session mechanism of accounts and on how a request is resolved to an actor and a role, taken by the right people. The initiative records the decision and hands it to `plans/mvp/MVP_PLAN.md` Q-6; it does not build the accounts. The user chose this scope on 2026-10-03.

## Out of scope

The other technical decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/osm_barrier_mapping/`, `plans/local_database/`, `plans/geocoding/`. The identifier of a vote without an account is decided by `plans/mvp/MVP_PRD.md` FR-13 and is not changed here.

## Functional requirements

The decision has to make these requirements of `plans/mvp/MVP_PRD.md` achievable:

1. FR-12 and AC-11 - create an account with a pseudonym and a password, log in, log out, delete the account; after deletion the pseudonym cannot be found anywhere in the app.
2. FR-14 and AC-13 - a moderator sees flagged reports and geozones in a moderator view and hides them; a user without the role cannot open the view. Photo moderation applies if optional feature O2 is implemented.
3. FR-6 and AC-6 - one vote per fact per account, so a request has to be resolved to the account reliably.
4. FR-1 - the preference profile never reaches the account.

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Without an email address there is no password recovery. The user confirmed on 2026-10-03 that a forgotten password may result in a lost account and that the MVP will not implement password recovery.
- Is the moderator role only a technical flag? No: it decides who sees hidden and flagged content, which is a visibility rule tested in both directions (question 3).
- Can one person vote twice on the same fact, once without an account and once logged in? By the letter of `docs/product/specification.md` M4 yes: "per account for logged-in users, per hashed identifier for others" makes them two separate voters, so the same person can add 0.5 and then 1. This is a rule of the specification and of `plans/mvp/MVP_PRD.md` FR-13, not of this initiative; it is recorded here to be raised with the user, not decided here.

## Domain rules or explicit TODO

- Weights: a logged-in person counts 1 and a person without an account 0.5 (`docs/product/specification.md`, M4); whether a request comes from an account therefore changes the status of a fact.
- Nothing about the author of a report, vote or geozone is shown to other users (`docs/product/specification.md`, M9).
- The user chose a rolling session that expires 24 hours after the last activity, survives closing and reopening the browser, and renews on every request in the active session, including read-only requests, on 2026-10-03.

## Notes on data, performance and security

- The password is kept only as a hash; the pseudonym is personal data stated in the privacy information (`plans/mvp/MVP_PRD.md` FR-20).
- A session secret or signing key is a secret under `docs/standards/standard_config.md`.
- The pseudonym points to a specific person, so it goes into a log only masked or replaced by an internal technical identifier (`docs/standards/standard_logging.md`, the rule on identifiers of a person in log entries); a password or a session value never goes into a log in any form (the same standard, the rule on secrets).

## Open questions

1. How is a request resolved to an actor - an account, a person without an account, a moderator - and what does the session carry? `Block: yes` (category: access token and permission scope contract)
2. What happens when two accounts try to use the same pseudonym, including differences only in letter case? `Block: yes` (category: personal data)
3. What validation rules apply to passwords? `Block: yes` (category: personal data)
4. When the team removes a moderator role, when must the account lose access to the moderator view? `Block: yes` (category: read visibility and permissions)
5. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
