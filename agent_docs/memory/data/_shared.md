## 2026-10-04 - Crash-safe import ownership (backend skeleton)

- What changed: Dedicated service sessions, a persistent private workspace journal and local OS exclusion protect import admission through cleanup.
- Why: Session-bound database locks alone cannot protect file cleanup after every database session disappears.
- Reusable pattern: Keep apply_import_exclusion open through all work; execute mutating tools through apply_import_process; use one publication deadline and distinguish unknown commit acknowledgement from confirmed rollback.
- Risk / notes: One database uses one machine and one persistent local filesystem root. Linux tools must preserve inherited descriptors and stay in the supervised group; Windows uses a non-breakaway Job Object. Consumer pointer reconciliation is not a foundation contract. There is no product domain rule yet; create DATA.md and DATA_ALGORITHM.md when product access is implemented.
