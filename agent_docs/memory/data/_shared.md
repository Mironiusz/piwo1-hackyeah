## 2026-10-04 - Sample transaction completion and data-layer documentation (sample_data)

- What changed: sample storage uses one Repeatable Read snapshot, explicit bound projections and batch inserts, returning provider success only after acknowledged commit.
- Why: site checks must not mix published network versions, and a retry after uncertainty must preserve existing facts and votes.
- Reusable pattern: a primary-key conflict does not overwrite; only returned new identifiers receive author votes. A failed or invalidated connection is insufficient rollback evidence, and failure around a sent commit remains unknown unless the server explicitly rejects it.
- Risk / notes: use the sole shared engine factory; no runtime delete or DDL belongs in this provider. The data layer owns no domain rule yet, so it has no documentation pair. Create `data/DATA.md` and `data/DATA_ALGORITHM.md` when the layer first gains behavior requiring that pair, according to `standard_documentation.md`; storage contracts currently live in the service construction document and operation runbook.
