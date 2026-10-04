# Shape: MVP accounts and shared actor resolution

Document state: 2026-10-04, interview closed
Regulator: C:40

## Problem

The MVP needs working accounts and one way to recognize a signed-in person and their current moderator role. The agreed product behavior and programming interface exist, but their account operations have no implementation in the current working tree. Community operations need this shared account recognition instead of implementing their own authentication.

On 2026-10-04 the user selected `accounts` for work alongside the separate `backend_skeleton` session and explicitly requested a schema handoff for Kuba in this shape. The existing `ACCOUNTS_SEED.md` remains unchanged; this request extends its scope here.

The user clarified Q-1 on 2026-10-04: add to the target schema what is developed through `accounts`. This initiative therefore owns documenting any account-related storage additions it establishes and integrating them into the target schema, rather than only reproducing the existing account definition. The clarification does not itself specify a new field, table or change to session behavior.

The user answered yes to Q-2 on 2026-10-04: this initiative also aligns the pseudonym rule in the programming interface contract with specification M9. The rule was updated in `docs/product/api_contract.md`; the user approved the correction in place of Kuber and Adrian, whose confirmation of the contract remains outstanding.

## Recipient and trigger

- A person creates an account, logs in, reads their own account or deletes it through the web client.
- Community and moderation operations consume the resolved account and its current permissions when a request carries a session token.
- Kuba receives the account-related schema requirements before implementing the initial revision in `schema_first_revision`.
- Marek coordinates the account implementation with the separate skeleton session. Kuber and Adrian consume the established account and session interface in the client.

## Current state

- `plans/accounts/` had only `ACCOUNTS_SEED.md` before this shape was created. No initiative named `accounts` was found in `plans_finished/`.
- `docs/product/specification.md`, version 12, M9 and M11, settles account behavior, deletion, session expiry and moderator-role removal.
- `docs/product/api_contract.md`, Accounts and Sessions and actors, defines the four account operations and credential transport. Registration does not log the person in. Logout is performed by the client discarding its token and has no service operation.
- `docs/product/schema.md`, Accounts and votes, already defines the account and its relationship to votes. This is the target schema, not proof of an applied database revision. No actual-schema dump is registered in the standards map or was found in the relevant repository files.
- `MVP.md`, D-8, records signed tokens and Argon2id password hashes. The detailed decision record is `plans_finished/account_sessions/ACCOUNT_SESSIONS_PLAN.md`, D-3 and D-4.
- The local database, shared infrastructure and revision runner are delivered by `backend_skeleton`; the initial schema and its tests are delivered by Kuba through `schema_first_revision`.
- At the start of the interview, the API contract allowed any non-control character in a pseudonym, while specification M9 allowed only letters, digits, the underscore and the hyphen. The user assigned this correction to accounts in Q-2; the contract now follows M9 and `MVP.md` records the alignment. No input limit, request shape or endpoint was changed.

## Smallest meaningful scope

Deliver registration, login, reading and deleting one's own account, plus the account and current-role recognition used by other operations. Follow the existing interface and product behavior, including rejection of invalid sessions and preservation of contributions after account deletion.

During shape, establish the account-related storage requirements and record any required additions relative to the existing target schema. Carry the agreed additions into `docs/product/schema.md` with the corresponding specification-version record before handing the resulting target to Kuba. The existing target schema remains the starting point; new schema objects are justified by established account requirements rather than invented to make an addition. This scope was confirmed by the user's answer to Q-1 on 2026-10-04.

The completed comparison found that the existing target DDL covers the agreed account requirements. The target-schema prose now records the encoded password-hash storage, input-validation boundary and ordinary-account role assignment. This clarifies existing decisions without changing the schema DDL or product behavior, so specification version 12 remains in force. On 2026-10-04 the user decided in `plans/repository_consistency/` that the notes nevertheless make version 13, because the target schema is changed and approved like the specification; no rule changes. Any later structural addition still requires the corresponding target-schema and specification update before Kuba implements it.

Parallel preparation must not introduce another configuration, logging, database connection or error-handling foundation. Agent decision at C:40, without asking: this follows the shared-infrastructure ownership in `MVP.md` and `BACKEND_SKELETON_PRD.md`, Dependencies and impact on other modules.

## Out of scope

- Implementing the initial database revision or applying it as part of application startup. Kuba owns the initial revision under `MVP.md`; any change to that ownership needs an explicit decision.
- Password recovery, email addresses, disability information and storing the preference profile on an account, excluded by specification M9 and Personal data.
- Points and rankings, which belong to optional feature O3.
- Creating reports, voting, evaluating fact statuses, flagging and hiding content. `community_facts` owns those operations; it consumes account recognition from this initiative.
- Route planning and address search, which carry no account identity.
- Adding a logout endpoint or persisted session records contrary to the existing contract and target schema.
- Operating the hosted demo or accessing its personal data. This initiative begins with repository artifacts and later local implementation and verification.

## Functional requirements

1. A person can create an account with a pseudonym and password under specification M9 and the existing registration interface. A newly created account has no moderator role. Registration does not start a session.
2. Pseudonyms are trimmed, have 3 to 30 Unicode code points, contain only the characters permitted by M9 and are unique without regard to letter case. Competing registrations cannot create two accounts with equivalent pseudonyms.
3. A person can log in with their pseudonym and password. An unknown account and an incorrect password produce the same credential failure. Passwords have 5 to 128 Unicode code points, accept printable ASCII, spaces and Unicode without a composition rule, and are stored only as hashes, under M9 and the API contract.
4. An active session survives browser closure and expires 24 hours after the latest authenticated request. Authenticated reads renew it too; routing, address search, registration and login do not consume an existing session or renew it.
5. A malformed, wrongly signed, expired or orphaned session is refused instead of becoming an anonymous contribution. An absent token permits anonymous behavior only on operations whose contract allows it.
6. A signed-in person can read only their own account through the own-account operation. Moderator authorization uses the current role, so removing it denies the next moderator request.
7. A person can delete their own account without entering the password again, after the client's confirmation described by M9. The account and pseudonym disappear, the pseudonym can be reused, and existing reports and votes stay detached with their weight. Tokens of the deleted account cease to resolve.
8. Provide the shared account and current-role recognition needed by `community_facts`. Define the concrete consumer interfaces in the implementation plan against the delivered skeleton.
9. Define the account-related schema additions arising from this initiative in shape, integrate the agreed result into `docs/product/schema.md` with the corresponding specification-version record, and give Kuba the resulting schema requirements. Cover account storage, pseudonym uniqueness, retained votes after deletion and required database rights. If the existing target already meets a requirement, identify that coverage without creating a duplicate object. Kuba implements the resulting approved target through the schema revision.
10. Verify account and session behavior, denied access, duplicate registration and deletion against the delivered local schema. Explain any prerequisites that remain undelivered instead of claiming integration readiness.
11. Align the account pseudonym rule in the API contract with specification M9, as approved by the user in Q-2. Keep the endpoints, request and response shapes, trim behavior and case-insensitive uniqueness unchanged, and record that Kuber and Adrian have not yet confirmed the contract correction.

## Scenarios: input, flow, expected state after the run

1. Registration and duplicate pseudonym. Two people submit `Wózek_KRK` and `wózek_krk`. Exactly one account can be created; the competing registration receives `pseudonym_taken`. The successful response contains no active session. Login is a separate request.
2. Session renewal. At 10:00 a person logs in. At 15:00 they read their own account, extending expiry to 15:00 the next day. At 16:00 they plan a route, which does not extend expiry. After 15:00 the next day, a request with the expired token is refused and saves no anonymous contribution.
3. Permission removal. A moderator has an active session. The team removes that account's moderator role. Its next moderator request is denied, while the account may still use ordinary authenticated operations.
4. Deletion and pseudonym reuse. An account has existing votes. The person confirms deletion in the client and calls the own-account deletion operation. The account disappears, its votes remain with their original weight and without that account identity, and its token is refused. A new account can take the released pseudonym without acquiring the old account's votes or permissions.
5. Invalid credential on an anonymous-capable operation. A request supplies a wrongly signed token. The service refuses it with `session_expired`; it does not record a report or vote as anonymous. The client removes the token and may let the person submit a new request without it.
6. Schema handoff. Account planning identifies the storage it needs and compares it with the existing target. This initiative records any required additions in shape and integrates the agreed result into the versioned target schema. Kuba receives that target with its account-related dependencies and implements it through the approved schema revision. Account integration is checked against the delivered revision; the handoff text alone is not evidence that the database contains these objects.

## Challenging own assumptions

- Does starting `accounts` require another seed? No. The initiative already has an immutable seed, and the user selected that exact initiative. The added schema request belongs in this shape.
- Does asking for a schema imply that no account model exists? No. The target already defines it. The user resolved Q-1 by assigning account-related schema additions to this initiative. New requirements must be compared with that target, so the result extends the shared schema instead of introducing an independently invented account model.
- Does a 24-hour session imply a database table of sessions? No. The current interface uses signed tokens and the target schema explicitly excludes persisted sessions.
- Can account deletion remove votes or simply recalculate them as anonymous? No. M9 and the target schema preserve their weight and detach their identity. The implementation plan must also address concurrent deletion, voting and OSM reconciliation with their existing owners.
- Can every token failure fall through to anonymous access? No. The interface explicitly refuses invalid credentials. Only the absence of a token allows the anonymous path where that path is permitted.
- Can all account implementation proceed independently of skeleton? No. Planning can proceed, but shared implementation interfaces and local database delivery are prerequisites for integration. Agent decision at C:40, without asking: this follows the ownership and dependencies recorded in `MVP.md` and the skeleton PRD.

## Domain rules or explicit TODO

Specification M9 and M11 remain authoritative. The account schema is part of that specification. Existing API paths and response shapes remain governed by `docs/product/api_contract.md`, whose pseudonym rule was aligned with M9 following the user's answer to Q-2.

### Schema handoff baseline for Kuba

This subsection is included during shape at the user's explicit request. It quotes the existing target account DDL as the starting point for the account-related additions assigned to this initiative by the answer to Q-1. It is not a second authoritative schema or a command to execute. Source checked on 2026-10-04: `docs/product/schema.md`, Accounts and votes, part of specification version 12. The agreed result must be integrated into the target and this handoff reconciled before Kuba implements it.

```sql
CREATE TABLE account (
    id bigint GENERATED ALWAYS AS IDENTITY,
    pseudonym text NOT NULL,
    password_hash text NOT NULL,
    is_moderator boolean NOT NULL,
    created_at timestamptz(3) NOT NULL,
    created_at_utc_offset_minutes utc_offset_minutes NOT NULL,
    CONSTRAINT PK_account PRIMARY KEY (id)
);

CREATE UNIQUE INDEX UX_account_pseudonym_lower ON account (lower(pseudonym));
```

- The existing `utc_offset_minutes` domain is a `smallint` restricted to -840 through 840. Creation time retains its original offset through the paired columns. Domain creation remains part of the shared initial revision.
- The existing vote relationship is `FOREIGN KEY (account_id) REFERENCES account (id) ON DELETE SET NULL`, named `FK_vote_account`. The existing partial index `IX_vote_account_id` covers non-null `account_id`. Full vote DDL remains in the target schema and belongs to the initial revision, not a separate account-owned revision.
- Deletion preserves vote rows, `is_cast_with_account` and their weight. The schema stores no author on a fact and adds no new report ownership relationship for accounts.
- The service database account needs the existing select, insert, update and delete rights on `account`. It owns no schema objects and performs no DDL. Grants are delivered by revisions, not by local setup or application startup.
- Account identifiers are generated by the database. A new ordinary account is explicitly created with `is_moderator` false. Case-insensitive uniqueness is enforced by the existing expression index; input length and allowed characters are checked by application rules.
- `password_hash` remains text for the agreed encoded Argon2id hash. The deferred 32-byte hash report in `docs/standards/decision_registry.md` does not authorize changing the password-hash representation.
- No session, email, preference, disability or points storage is added by this baseline. A request to change the target schema must be recorded and approved as a specification change before Kuba implements it.

### Account schema outcome for Kuba

Q-1 is resolved: this initiative adds the storage requirements developed through accounts to the shared target schema and records them here for Kuba. The closed interview establishes no new column, table, index or constraint. The target-schema prose was extended with the existing encoded-hash, validation and role-assignment requirements. The baseline DDL above remains the approved account target, with these dependencies:

| Account requirement                                | Existing storage coverage                                                                              | Handoff result                                                                                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Account identity and registration time             | `account.id`, `created_at`, `created_at_utc_offset_minutes`, `PK_account` and the shared offset domain | Kuba delivers these through the initial revision.                                                                                               |
| Pseudonym and case-insensitive uniqueness          | `pseudonym` and `UX_account_pseudonym_lower`                                                           | Application validation follows the aligned API contract; no additional text constraint is required.                                             |
| Password verification                              | `password_hash` as text                                                                                | The account writer stores an encoded Argon2id hash; the target-schema prose records this requirement.                                           |
| Current moderator permissions                      | `is_moderator`                                                                                         | Registration writes false, and authorization reads the current role; no role snapshot is stored in a token as the authority.                    |
| Contributions retained after deletion              | `FK_vote_account` with `ON DELETE SET NULL`, the retained vote-kind field and `IX_vote_account_id`     | The initial revision preserves this relationship; account implementation coordinates deletion with concurrent vote-history readers and writers. |
| Rolling account session                            | Signed-token behavior of the existing API contract                                                     | No persisted session or last-activity column is required by the agreed design.                                                                  |
| Account writes under the service database identity | Existing account table rights in the target schema                                                     | Kuba delivers the rights through the revision and verifies account writes locally.                                                              |

If technical planning reveals an uncovered storage requirement, this initiative must establish its necessity and update the target and handoff before it is implemented. A product-behavior change returns to the shape/specification decision rather than being added silently in code. Agent decision at C:40, without asking: this follows the source-of-truth and no-guessed-contract rules, while preserving the schema-update scope explicitly assigned by the user.

## Notes on data, performance and security

- Request logs and diagnostic failures must not expose passwords, session tokens, pseudonyms, account identifiers, IP addresses or browser characteristics. Follow Request logs and failures of the API contract.
- A valid token must still resolve to an existing account; moderator access must read the current role. Concrete token contents, signing configuration and consumer interfaces belong to the implementation plan.
- Password hashing has a cost and simultaneous logins need verification within the agreed local implementation. No unmeasured throughput guarantee is made here.
- Account deletion affects retained vote identities and can overlap import reconciliation. Its concurrency contract must be agreed with `community_facts` and `osm_importer` before implementation; importer exclusion alone does not protect that history.
- Secrets and target-environment addresses never enter this handoff. Database verification is confined to the approved local setup; no hosted database was inspected.
- Own the account initiative artifacts and the agreed account-specific target-schema updates during this interview. The schema-update scope follows the user's answer to Q-1; coordinate its handoff with Kuba and preserve unrelated schema work. Shared skeleton files and its initiative remain with the other session. Agent decision at C:40, without asking, for the separation from skeleton: this applies the user's parallel-work context and `standard_agentic_workflow.md`, section 4.7.

## Open questions

None at the shape stage. Q-1 assigns the account schema additions and handoff to this initiative; Q-2 assigns the API pseudonym correction, now recorded in the contract. Token encoding, signing settings, concrete consumer interfaces and the deletion concurrency protocol are technical-plan work, not new product decisions. Skeleton and the initial schema remain implementation prerequisites. The contract correction is approved by the user in place of Kuber and Adrian; their outstanding confirmation is recorded rather than represented as obtained.
