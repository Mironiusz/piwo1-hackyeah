# PRD: Backend skeleton and local database of the MVP

Document state: 2026-10-04, awaiting user approval

## Business goal

Unblock parallel MVP development by giving Marek, Mateusz and Kuba one runnable backend foundation, a repeatable local environment and shared mechanisms for database access, logging and safe administrative work.

The initiative succeeds when its consumers can use the documented foundation without duplicating infrastructure or waiting for a product operation to be implemented. It also delivers the shared import-exclusion and publication-deadline mechanisms explicitly assigned to skeleton by the user on 2026-10-04.

## Problem and its consequences

The team has agreed the backend architecture and product interface, but the shared foundation is not implemented. Mateusz cannot connect his integrations to a delivered backend contract, and Kuba cannot finish the initial product database implementation without the local environment and a configured way to apply approved storage changes.

Without a common foundation, parallel initiatives would have to invent separate configuration, logging and database-access mechanisms. They could also implement incompatible import-exclusion or cancellation behavior, allowing overlapping writes or reporting a failed publication while work continues.

Completion must remain independent of product database structures and operations that consume the foundation. Making skeleton wait for those consumers would recreate the dependency cycle the MVP split was intended to remove.

## Scope

- A runnable backend foundation and the boundaries agreed for application handling, business rules, data access and administrative work.
- Shared configuration validation, database access and logging, including the request-correlation and failure-handling foundation required by the existing programming interface contract.
- A repeatable local database environment and a ready way for Kuba to apply approved storage changes explicitly.
- The administrative launch foundation needed by the importer, without implementing the import.
- Shared exclusion of concurrent import runs and enforcement of one deadline for the complete database publication.
- Verification of the foundation, local critical-test protection, documentation of the handoff and recording the implemented backend choice in the repository's standards map.

The scope follows the closed shape and the user's extension of its requirements 8 and 9. This PRD defines observable results; technical choices and exact consumer interfaces are settled in the implementation plan.

## Out of scope

- The initial product database implementation and verification that depends on its objects or permissions; Kuba delivers these through `schema_first_revision`.
- Product operations for accounts, reports, votes, moderation, address search, copy metadata and route planning.
- Vote-status evaluation and the rules coordinating individual votes with an import. These remain with `community_facts` and its handoff to the importer.
- Acquiring and processing OpenStreetMap data, deriving facts, reconciliation, preparing routing data and selecting or activating a routing copy. These remain with their assigned initiatives.
- The common demo-data loading workflow, sample data and map assets.
- Operating or changing the hosted demo and accessing its database.
- Periodic scheduling or automatic import runs.

## Functional requirements

FR-1. A team member can start the backend foundation using documented instructions and valid configuration before any product operation or imported data is available. Starting it does not apply storage changes or load data.

FR-2. Request handling and administrative consumers use one validated configuration contract. Missing or invalid required settings produce an identifiable failure without exposing secret values. Settings needed only for an administrative operation do not prevent unrelated application startup; the operation refuses to run when its required settings are absent.

FR-3. Database consumers use one shared connection mechanism under the configured service-level permissions and the existing time-handling contract. Application use does not gain database-maintenance privileges.

FR-4. A team member can prepare their own local database and the storage-change runner from the documented instructions. Skeleton verification is independent of the initial product database implementation.

FR-5. Provide shared logging for requests and administrative runs. The request-correlation, error responses and request-log contents follow the existing programming interface contract. Failure responses and logs do not reveal credentials, request bodies or protected user inputs.

FR-6. Provide the foundation for explicitly launched administrative work under the current MVP contract. It reuses the shared configuration and logging and introduces no schedule or alternative importer.

FR-7. Deliver the checks required with the first backend implementation, including agreed responsibility boundaries and a guard that refuses critical tests under target-environment configuration before any test can write. The included critical checks run against the team member's local database.

FR-8. Only one import run can hold shared import exclusion for the configured database. A second run is refused without waiting or beginning acquisition. Exclusion remains held until the owning run's outstanding work, rollback and cleanup have ended.

FR-9. Enforce one 120-second elapsed-time budget from the start of a publication transaction through commit, including all writes and waiting. If the importer has less whole-run time remaining, use that earlier deadline. The budget is not renewed for individual statements and excludes acquisition and preparation completed before publication.

FR-10. On deadline expiration, stop further publication and roll back an uncommitted transaction before releasing import exclusion. Distinguish successful completion, confirmed rollback and an uncertain commit outcome; never report an uncertain outcome as proof that the previous copy is unchanged.

FR-11. Provide documented readiness, launch and verification instructions and identify the delivered shared interfaces for Kuba and Mateusz. Update the standards map and the technology-profile decision record when their implementation condition is met. Completion reports distinguish verified behavior from prerequisites still owned by other initiatives.

## Acceptance criteria

AC-1. A team member following the documented instructions can start the application foundation with valid configuration before the initial product database implementation and imported data exist. Startup performs no product storage change or data loading. Checks requiring a product operation are not claimed to have passed. Covers FR-1 and FR-4.

AC-2. Invalid or missing required application settings prevent startup with an identifiable failure that does not disclose their values. An absent administrative-only setting permits unrelated application startup but prevents the affected administrative operation from starting. Covers FR-2.

AC-3. Local database access through the shared mechanism uses the configured service-level permissions and the agreed UTC session behavior. The application does not use the maintenance identity. Verification that requires the initial product database implementation is left to its owner. Covers FR-3.

AC-4. The documented local setup is reproducible on the team's agreed development systems. Its independent checks demonstrate that Polish text is handled as agreed, including lowercase conversion of `ŁÓDŹ` to `łódź`. Checks requiring product storage objects or their grants are excluded from skeleton completion. Covers FR-4.

AC-5. Request correlation, foundation error responses and request-log contents match the existing programming interface contract. Request logs contain only the permitted operation, status, duration and request identifier. Administrative runs use the same logging policy. Failure handling exposes no protected input or infrastructure details. Covers FR-5.

AC-6. The delivered administrative foundation can be used with the shared configuration and logging under the current agreed launch contract. Its verification does not depend on a real importer being complete and does not introduce a scheduled run. Covers FR-6.

AC-7. The applicable foundation gates pass. A critical test session configured for the target environment is refused before any test writes; approved local critical checks run against the team member's own database. Covers FR-7.

AC-8. Two independent local consumers attempt to acquire import exclusion for the same database. While A owns it, B is refused with zero wait and does not begin acquisition. After A's work and cleanup end, a later attempt can acquire it. Covers FR-8.

AC-9. A publication starts with a 120-second budget, waits until second 80 and then needs another 50 seconds of work. It is interrupted at the shared deadline rather than allowed to complete at second 130. A confirmed rollback leaves its uncommitted changes invisible. Covers FR-9 and FR-10.

AC-10. A publication performs multiple individually short operations whose combined elapsed time exceeds the budget. Its deadline still expires; no operation resets the remaining time. Covers FR-9.

AC-11. A publication begins with 45 seconds remaining in the whole-run budget. Its effective deadline is 45 seconds rather than 120 seconds, including waiting and commit. Covers FR-9.

AC-12. A publication completes within its effective budget. Its confirmed changes become visible together and its outcome is reported as successful. Deadline handling also covers the commit phase; it does not stop measuring after the final write. Covers FR-9 and FR-10.

AC-13. Deadline expiration occurs while work or rollback is outstanding. A second consumer remains excluded until that work, rollback and cleanup have ended. No work from the expired publication can continue after exclusion has been released. Covers FR-8 and FR-10.

AC-14. Verification exercises an uncertain commit outcome. It is reported separately from confirmed success and confirmed rollback, without asserting that the previous copy is unchanged. Covers FR-10.

AC-15. All skeleton criteria can be verified without product storage structures, a vote evaluator, imported data or working route operations. Instructions identify which consumer prerequisites remain undelivered, and the backend implementation choice is recorded where future initiatives look for it. Covers FR-4 and FR-11.

Verification of shared exclusion and deadline behavior belongs to skeleton. Full import publication and concurrency with actual votes remain acceptance responsibilities of the importer and community-facts initiatives.

## Domain rules

- The product specification remains the authority for behavior. Skeleton changes no rule about accessibility, facts, votes, accounts or personal-data retention.
- The existing programming interface contract remains the authority for requests, responses, correlation and request logging. Skeleton adds no product operation or alternative response contract.
- Storage changes and data loading are explicit administrative actions, never consequences of application startup.
- Critical tests are confined to local development databases. No target-environment address, login or secret is stored in repository artifacts.
- Current location, route endpoints, preferences, address-search text, passwords and tokens are not exposed by foundation logs or errors.
- The 120-second publication budget includes waiting and commit. It is shortened when less whole-run time remains and does not include earlier acquisition or preparation.
- Excluding another importer does not establish safe coordination with community votes. The agreed vote-writing and identity-maintenance behavior must still be delivered by its owner.
- Confirmed rollback and uncertain commit are different outcomes. A timeout alone is not evidence that changes were rolled back.

## Dependencies and impact on other modules

- Marek owns skeleton; Kuba contributes the local database setup. The existing architecture and local-environment decisions constrain the later technical plan.
- `schema_first_revision` consumes the local environment, shared database access and storage-change runner. Skeleton does not wait for that initiative's product structures or tests.
- `osm_importer` consumes shared configuration, database access, logging, exclusion and deadline enforcement. Mateusz connects these mechanisms to his import orchestration; importer readiness still requires the product database implementation and other agreed handoffs.
- `address_search` consumes the runnable backend foundation and shared configuration and logging.
- `accounts`, `community_facts` and `route_planning` build their operations on the same foundation and retain their existing product responsibilities. The vote evaluator and vote-writing protocol are not transferred to skeleton.
- `osm_import` retains the copy-read operation and common loading workflow. It consumes the actual importer and does not build another one.
- `deployment_config` consumes the documented backend launch and configuration contract. This initiative does not carry out its hosted actions.
- Shared implementation interfaces and ownership of files edited by several initiatives are finalized in the technical plan, with the concurrent importer work checked again before writing.

## Risks and notes

- The importer and shared MVP documents are changing in another session. The technical plan must use their current agreed contracts and preserve other contributors' edits.
- Timeout enforcement that only stops the caller could leave database work running. Acceptance must demonstrate that exclusion is not released while the expired publication can still write.
- Bounding individual operations does not bound their combined publication time. Verification must cover waiting, multiple operations, commit and the earlier whole-run deadline.
- An uncertain commit requires an explicit outcome and a recovery handoff. Skeleton cannot claim that a complete copy was preserved without evidence of rollback.
- Tests requiring the initial product database implementation would make skeleton depend on its consumer. Shared infrastructure verification must remain independent while leaving full import and vote-concurrency checks to their owners.
- The 120-second budget is a required ceiling, not evidence that the full OpenStreetMap dataset can be published within it. The importer must measure its actual workload separately.
- The exact shared interfaces, cancellation mechanism and verification commands remain decisions for the implementation plan. PRD approval agrees the scope and observable behavior; it does not claim that the foundation has been implemented.
