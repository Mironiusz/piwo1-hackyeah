# PRD: MVP accounts and shared actor resolution

Document state: 2026-10-04, awaiting user confirmation

## Business goal

Make the MVP's light accounts work and give community and moderation features one consistent way to recognize a signed-in person and their current permissions. A person can register, log in, use their account and delete it without exposing who contributed a report or vote.

Give Kuba the account-related storage requirements needed to deliver the agreed behavior. Account implementation must use the shared foundation delivered by the separate skeleton initiative so parallel work can converge without competing infrastructure.

## Problem and its consequences

The product rules and client-facing account contract are agreed, but the account operations and shared account recognition are not implemented. Community features cannot finish authenticated contributions or moderator access without this responsibility being delivered.

Incorrect session handling could save an anonymous contribution while a person believes they are signed in. Incorrect deletion could erase community contributions, change their weight or let an old session access a newly created account. A role remembered after revocation could permit further moderation.

The closed shape assigned account-related storage requirements and the pseudonym-contract correction to this initiative. The existing storage target covers the requirements established so far; its explanatory handoff and the contract correction are already recorded. Those documents do not prove that working account behavior has been delivered.

## Scope

- Registration, login, reading one's own account and deleting one's own account.
- Input rules, case-insensitive pseudonym uniqueness and password confidentiality.
- Session persistence, rolling inactivity expiry and refusal of invalid sessions.
- Shared recognition of an account and its current moderator permissions for consumer features.
- Retention and detachment of existing contributions after account deletion.
- Account-related storage requirements and their handoff to Kuba, including any later justified additions established within the agreed product scope.
- Alignment of the account contract with specification M9, preserving the existing client-facing operations.
- Verification of account behavior, denied access, competing registrations and deletion, with clear identification of undelivered consumer prerequisites.

The scope follows the closed accounts shape at C:40. The product specification M9, M11 and Personal data remains authoritative; the programming interface contract governs the client-facing operations.

## Out of scope

- Password recovery, password-change flows, email addresses and additional personal-profile information.
- Storing disability information, preference profiles, current location or route requests on accounts.
- Points and rankings, which remain optional product work.
- Creating reports, writing votes, evaluating reliability statuses and performing content moderation. The community initiative consumes account recognition and delivers those operations.
- Routing and address search, which do not use account identity.
- Implementing the database foundation assigned to Kuba or replacing the shared skeleton foundation.
- Building frontend account screens. Kuber and Adrian deliver the client, including logout and the confirmation before account deletion.
- Introducing another logout operation or changing the already agreed session behavior.

## Functional requirements

FR-1. Registration and pseudonyms. A person can register with a pseudonym and password. Leading and trailing spaces are removed from the pseudonym, which then has 3 to 30 Unicode code points and contains only letters, including Polish letters, digits, the underscore and the hyphen. It is unique without regard to letter case. A new account has no moderator permission, and registration does not log the person in.

FR-2. Password rules. Passwords have 5 to 128 Unicode code points and accept printable ASCII, spaces and Unicode. There is no character-composition requirement, common-password rejection or periodic-change rule. Passwords are never retained as plaintext.

FR-3. Login. A person can log in using their pseudonym and password. Pseudonym comparison ignores letter case after trimming. An unknown account and an incorrect password produce the same failure without disclosing which condition occurred.

FR-4. Session lifetime. Login starts a session that survives browser closure and reopening. Every request in an active authenticated session, including a read-only request, renews the 24-hour inactivity period. Route planning, address search, registration and login do not consume or renew an existing session. Account deletion ends access to that account instead of renewing it.

FR-5. Invalid or absent sessions. A malformed, invalid, expired or deleted-account session is refused and never becomes an anonymous contribution. A request without a session can proceed anonymously only where its operation permits this. Reading or deleting one's own account requires an active account session.

FR-6. Own-account access. A signed-in person can read their own pseudonym and current moderator status. The account feature adds no way to browse other people's accounts or associate a public contribution with its author.

FR-7. Current moderator permissions. Moderator access requires an active account with the moderator role at the time of the request. Removing that role denies the next moderator request even when the account session remains active. An ordinary account cannot obtain moderator permission through registration or a claimed role.

FR-8. Account deletion. A person can delete their own account without providing the password again after the client's confirmation. The account and pseudonym are removed; reports and votes remain detached with their weight, and each detached vote counts as a person of its own under the existing reliability rules. Existing sessions of the deleted account cease to resolve. The released pseudonym can be registered again without inheriting the deleted account's contributions, sessions or permissions.

FR-9. Shared recognition and consistent deletion. Community and moderation consumers receive the same account and permission decisions as account operations. Account deletion and concurrent community or import work must preserve committed contributions and their agreed identity-detachment behavior. A failure must not leave deletion partly completed.

FR-10. Privacy and failure handling. Account responses, failures and diagnostic output follow the existing contract. Logs expose no password, session credential, pseudonym, account identity, IP address or browser characteristics. Responses expose neither password material nor internal infrastructure details. Routing and address search remain independent of account identity.

FR-11. Storage handoff for Kuba. Document the storage requirements established by accounts, reconcile them with the shared approved target and hand the result to Kuba. Existing coverage is identified instead of duplicated. Any necessary addition is agreed and incorporated into the target before implementation; it must not introduce unapproved product behavior or personal data.

FR-12. Contract alignment. Keep the account pseudonym rule aligned with M9 while preserving the established operations, request and response shapes, trim behavior and case-insensitive uniqueness. Record approval supplied by the user in place of Kuber and Adrian separately from confirmation by them.

FR-13. Verification and readiness. Demonstrate the agreed behavior using delivered shared prerequisites, including allowed and denied account access, competing registrations and retained contributions after deletion. Clearly distinguish implemented account behavior, shared consumer behavior and integrations that still depend on other initiatives.

## Acceptance criteria

AC-1. Registering with `  Wózek_KRK  ` and an accepted password creates an ordinary account whose pseudonym is `Wózek_KRK`. The response grants no active session; a subsequent login is required. Covers FR-1.

AC-2. Pseudonyms of 3 and 30 permitted Unicode code points are accepted; 2 and 31 are refused. Polish letters, digits, the underscore and the hyphen are accepted. An internal space or `!` is refused with the existing input-validation failure identifying the pseudonym. Covers FR-1 and FR-12.

AC-3. Two concurrent registrations submit `Wózek_KRK` and `wózek_krk`. Exactly one account is created; the other receives the established duplicate-pseudonym failure. The same uniqueness holds for sequential requests and Polish letter case. Covers FR-1 and FR-13.

AC-4. Passwords of 5 and 128 Unicode code points are accepted, including permitted spaces and Unicode; lengths 4 and 129 are refused. A password is not rejected solely for lacking mixed character classes or being common. No plaintext password is retained or appears in responses or diagnostics. Covers FR-2 and FR-10.

AC-5. An existing account can log in with a differently cased, trimmed pseudonym and the correct password. An unknown pseudonym and an incorrect password return the same established login failure. Covers FR-3.

AC-6. A person logs in at 10:00 on day 1 and reads their own account at 15:00. Their active session then expires at 15:00 on day 2. Closing and reopening the browser preserves it before that instant. A request at or after expiry is refused and creates no anonymous contribution. Covers FR-4 and FR-5.

AC-7. After the authenticated read at 15:00 on day 1, route planning, address search and registration performed at 16:00 do not move that session's expiry beyond 15:00 on day 2. An existing account session supplied to an operation that ignores it changes neither account recognition nor renewal there. A new successful login starts its own active session under the login contract. Covers FR-4 and FR-10.

AC-8. Malformed, invalid, expired and deleted-account sessions are each refused on an operation that consumes sessions. No case saves an anonymous contribution. With no session, an anonymous-capable operation can take its permitted anonymous path, while own-account reading and deletion are refused. The shared account-recognition checks demonstrate these distinctions without claiming that unfinished community operations are implemented. Covers FR-5, FR-9 and FR-13.

AC-9. A signed-in person receives only their own pseudonym and current moderator status through the own-account operation. An ordinary account is denied moderator access. A moderator is permitted until the team removes the role; the next moderator request is then denied while ordinary account access remains possible. Covers FR-6 and FR-7.

AC-10. Deleting an account requires no repeated password input. After completion, that account cannot be read or resolved through its previous sessions. Existing reports and votes remain; vote weight is preserved and detached votes retain the counting behavior of M9. Covers FR-8 and FR-13.

AC-11. After deletion, a new ordinary account can register the released pseudonym. The new account acquires none of the old account's votes, moderator permission or session access. Old sessions remain refused after the new registration. Covers FR-1, FR-7 and FR-8.

AC-12. Verification interleaves account deletion with community or import work affecting existing vote history. Committed contributions are preserved and no retained vote remains attached to the account after successful deletion. A failed deletion leaves no partly completed account removal. Consumer scenarios not yet available are recorded as remaining integration work, not as passed acceptance. Covers FR-8, FR-9 and FR-13.

AC-13. Captured account responses and diagnostic output expose none of the prohibited personal or password material and no internal infrastructure details. Request logging carries only the information permitted by the existing contract. Covers FR-2 and FR-10.

AC-14. Kuba receives an account-storage handoff that matches the approved target and explains coverage of registration, pseudonym uniqueness, password confidentiality, current roles and retained contributions. No required addition is implemented before it is agreed and recorded. The handoff does not claim that the target is already delivered. Covers FR-11 and FR-13.

AC-15. The account contract states the pseudonym character rule of M9 and preserves its existing operations and message shapes. The user-approved correction is recorded, with Kuber and Adrian's confirmation explicitly pending until actually obtained. Covers FR-12.

AC-16. Completion evidence identifies the applicable checks, their actual results and any remaining dependencies. Account integration is not reported as ready on the strength of document-only or substitute-consumer checks. Covers FR-13.

## Domain rules

- Product behavior comes from specification M9 and M11; this initiative changes no reliability threshold, contribution weight or anonymous-vote rule.
- An account consists of a pseudonym and password with no email, disability information or stored preference profile.
- Account and anonymous contributions remain distinct under M9. An anonymous contribution is never linked to an account to deduplicate the two identities.
- Removing a moderator role affects the next moderator request. Deleting an account invalidates its sessions and preserves its contributions as specified.
- A request with an invalid session is refused. Only an absent session permits anonymous behavior where the operation allows it.
- User input limits count Unicode code points. Pseudonym uniqueness ignores letter case, including Polish letters.
- Forgotten passwords are not recoverable. No points or ranking behavior is added.
- The client owns logout and the single deletion confirmation; the service owns account access and the deletion result.

## Dependencies and impact on other modules

- The skeleton initiative delivers the common application foundation, configuration, logging and data-access mechanisms. Marek coordinates accounts with that separate session.
- Kuba delivers the initial storage implementation and its verification. The closed shape carries the account-specific handoff; the requirements established so far fit the existing target.
- Community features depend on account recognition and current moderator permissions. Their report, vote and moderation behavior remains with their owner.
- Mateusz's importer and account deletion both affect how retained vote history is interpreted. Their integration must agree consistent behavior before it is reported as verified.
- Kuber and Adrian build account screens, retain the active session, handle logout and expiry, and explain and confirm deletion. This initiative supplies the established service behavior rather than implementing those screens.
- The API pseudonym correction and storage explanation were completed during shape. They remain part of this initiative's acceptance evidence, not a reason to recreate an already completed document change.

## Risks and notes

- The shared foundation and initial storage are being delivered separately. Their documented target is not evidence of working integration.
- The 5-character password minimum and lack of common-password rejection are deliberate product choices. Password recovery is absent, so losing a password can permanently prevent account access.
- Logging out on one browser ends that browser's active session. The existing session contract does not promise revocation of copies retained elsewhere; deleting the account ends their account access.
- Password protection and simultaneous logins have a resource cost that must be checked during implementation. This PRD adds no unmeasured capacity guarantee.
- Deletion changes the person identities used to interpret retained votes. Concurrent work requires verification of that boundary without transferring the vote evaluator or importer into accounts.
- Kuber and Adrian have not yet confirmed the user-approved contract correction. This remains visible in the handoff.
- Technical decisions and storage verification belong to the implementation-plan phase. No product code is implemented by writing this PRD.
