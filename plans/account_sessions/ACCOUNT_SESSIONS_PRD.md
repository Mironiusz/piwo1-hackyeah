# PRD: MVP account sessions and actor resolution

Document state: 2026-10-03

## Business goal

Settle the account and session behavior needed for the MVP so the backend owner and frontend consumer can agree on how signed-in people, anonymous contributors and moderators are recognized across requests. The decision also makes vote deduplication consistent when a person switches between account and anonymous contributions.

## Problem and its consequences

The MVP includes accounts, anonymous contributions and a manually assigned moderator role, but the behavior for recognizing an account across requests and enforcing its role has not been decided. The same 30-day vote hash also needs to apply to account votes so switching authentication state cannot bypass vote deduplication.

Without these decisions, account behavior and moderator authorization cannot be specified consistently for the frontend and backend, and the MVP implementation plan cannot settle the account-session question. If vote identity differs between account and anonymous contributions, a person may vote twice on the same fact within the hash retention period.

## Scope

- Decide the behavior of account sessions and the resolution of each request to an account, an anonymous contributor or a moderator.
- Decide how removal of a moderator role affects access while an account session remains active.
- Apply the same 30-day vote hash to account and anonymous votes, with the same-fact deduplication behavior defined below.
- Record the decision for `plans/mvp/MVP_PLAN.md` Q-6. The backend owner makes the technical decision in agreement with the frontend consumer.
- Keep the account behavior consistent with the product specification, version 3, including case-insensitive pseudonym uniqueness, the password rules and lack of password recovery.

## Out of scope

- Implementing account registration, login, logout, deletion, sessions, moderator authorization or vote deduplication. This initiative records the decision; implementation is part of the MVP.
- Password recovery. A forgotten password can make the account permanently inaccessible.
- Account profiles, email addresses, disability information or storing a person's preference profile on the account.
- Deciding other technical matters assigned to `plans/api_contract/`, `plans/frontend_stack/` or `plans/mvp/`.

## Functional requirements

FR-1. Account session behavior. After login, the account remains recognized across browser closure and reopening until 24 hours have passed without activity. Every request in an active session, including a read-only request, renews the 24-hour inactivity period. After the period expires, the request is treated as unauthenticated until the person logs in again.

FR-2. Request actor and role. Each request is handled as an account contribution, an anonymous contribution or a moderator action according to the current account and moderator-role state. Moderator status is assigned by the team. Removing the role prevents moderator access on the account's next request, even if its session is active.

FR-3. Account lifecycle and credentials. A person can create an account with a pseudonym and password, log in and out, and delete the account. Pseudonyms are unique without regard to letter case. Passwords have a minimum length of 5 characters, accept printable ASCII characters, spaces and Unicode, allow a maximum length of at least 64 characters, and have no character-composition or periodic-change rules. Common or breached passwords are not rejected. There is no password recovery. Account deletion removes the account and pseudonym; reports and votes remain detached from the account and retain their contribution weight.

FR-4. Cross-mode vote deduplication. Every vote, including an account vote, has the same one-way hash derived from the IP address and browser characteristics, and the raw values are never retained. While the hash exists, it prevents a second vote on the same fact across account and anonymous contributions. The hash is deleted after 30 days. Once it has expired, a later anonymous vote with the same hash may be accepted. A person can still vote only once per fact per account.

FR-5. Privacy boundaries. The preference profile remains separate from the account. Other users cannot see the author of a report, vote or geozone, or whether that contribution was made while logged in. Privacy information states that account and anonymous vote hashes are kept for 30 days and describes the pseudonym and password as account data.

## Acceptance criteria

AC-1 (FR-1). A person logs in at 08:00, makes any request at 20:00 and closes the browser. After reopening at 07:00 the next day, the account is still recognized. If there are no further requests, it expires 24 hours after the 20:00 request. Read-only requests produce the same renewal as other requests.

AC-2 (FR-2). A moderator has access while the team assigns the role. After the team removes it, the next request to moderator-only content is denied, even if the account's session has not expired.

AC-3 (FR-3). Pseudonyms that differ only by letter case cannot be used for separate accounts. Passwords may be as short as 5 characters; printable ASCII, spaces and Unicode are accepted; the maximum supported length is at least 64 characters; and common or breached passwords are not rejected. No email address or recovery path is required. Deleting an account removes its pseudonym while its reports and votes remain detached with their weight.

AC-4 (FR-4). A person votes on a fact while signed in, then attempts to vote on the same fact anonymously with the same hash before 30 days have passed. The second vote is rejected. The same result holds when the anonymous vote comes first and the account vote follows.

AC-5 (FR-4). After a vote hash has been deleted at 30 days, a later anonymous vote on the same fact with the same hash may be accepted. A second vote from the same account remains rejected by the per-account uniqueness rule.

AC-6 (FR-4). Account votes and anonymous votes retain the same hash for 30 days. Raw IP and browser-characteristic values are not retained, and the hash is no longer present after its retention period, including when an account has been deleted.

AC-7 (FR-5). A profile set on one device does not appear on another device after login. No other user can determine from a report, vote or geozone whether its author was logged in. The privacy information lists the pseudonym, password and 30-day vote hash with their purposes and retention.

## Domain rules

- A logged-in person's contribution weighs 1; a contribution without an account weighs 0.5, including a person's own contribution.
- Pseudonyms are unique case-insensitively.
- Password requirements are based on NIST SP 800-63B-4, except for the user-chosen 5-character minimum and the decision not to reject common or breached passwords. The remaining stated rules include accepting printable ASCII, spaces and Unicode, a maximum length of at least 64 characters, and no character-composition or periodic-change rules.
- A rolling session expires 24 hours after its last activity. Every request within an active session, including a read-only request, renews it; closing and reopening the browser does not end it.
- The team assigns moderator roles. Removing a role revokes moderator access on the next request.
- Every vote has the same 30-day hash, regardless of authentication state. While it exists, the hash allows at most one vote per fact across account and anonymous contributions. Once deleted, a later anonymous vote with the same hash may be accepted. A separate per-account uniqueness rule remains in force.
- The vote hash may conflate different people who share browser and network characteristics. Different hashes do not establish that votes came from the same person across devices or networks.
- Account deletion removes the account and pseudonym. Existing reports and votes remain detached and retain their weight; a vote hash still within its 30-day retention remains until expiry.
- The account does not contain the user's preference profile, email address or information about a disability.

## Dependencies and impact on other modules

- `plans/mvp/MVP_PLAN.md` Q-6 waits for this initiative's account-session decision.
- The backend owner is responsible for the decision; the frontend person is its consumer and must agree on the request behavior before the decision is handed back to the MVP plan.
- Vote rules in M4 and account rules in M9 of `docs/product/specification.md` apply to MVP vote and account behavior. The corresponding requirements and acceptance criteria in `plans/mvp/MVP_PRD.md` must stay aligned.
- `plans/api_contract/` depends on how a request is resolved to an actor. The API contract may be prepared in parallel, but its account behavior must follow the decision from this initiative.
- No product code exists for this initiative, so this PRD does not assume changes to existing code or a database.

## Risks and notes

- A 5-character password minimum and no rejection of common or breached passwords make accounts easier to guess than the NIST SP 800-63B-4 policy, which requires at least 15 characters for single-factor passwords and a blocklist: [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html).
- Keeping the same vote hash on account votes makes the account's network and browser characteristics pseudonymously linkable to its votes for up to 30 days. This hash is pseudonymized personal data, not anonymous data for the purposes of the app's privacy information.
- Two people sharing browser and network characteristics can be treated as one vote identity for a fact. Conversely, one person using different devices or networks can receive different hashes. A later anonymous vote may be accepted after the hash expires.
- There is no password recovery. A forgotten password may permanently prevent access to an account, while its reports and votes remain detached if the account is deleted.
- The specific session mechanism and the details of the request contract remain phase B decisions. They require agreement between the backend owner and the frontend consumer and are not fixed by this PRD.
