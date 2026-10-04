What the module does: see `service/SERVICE_ALGORITHM.md`, sections "Algorithm goal" and "General process map".

## 2026-10-04 - Fixed sample identity and author history (sample_data)

- What changed: the no-argument sample provider and shared records reserve four negative fact identifiers and one fictional author identity per sample.
- Why: the current schema forbids a report-save key on samples; retries must preserve contributors and must not create a new daily author vote.
- Reusable pattern: reconcile the exact immutable definition under its fixed primary key; create the initial author vote only for a newly inserted fact, and validate the original instant plus offset on later runs. Changing a definition is a refusal, not an update.
- Risk / notes: detail, vote and moderation consumers must accept integer identifiers without a positive-only restriction. Unchanged sample loading does not assert visibility or initial reliability. The clock and logger are required shared runtime inputs; pure imports do not read configuration.
