# SERVICE

Document state: 2026-10-04

## Module role

The service layer owns product decisions. Its current sample operation validates four fictional demonstration facts and reconciles them without resetting contributions.

## Public interface

`service.sample_data.apply_sample_data() -> SampleDataResult` takes no arguments. It returns only after acknowledged commit or raises the failure described in `plans/sample_data/SAMPLE_DATA_LOADING_HANDOFF.md`.

## Technical inputs and outputs

The operation reads typed network, fact and fictional-author snapshots through `data.sample_data`. It prepares missing facts and receives an acknowledged transaction result. The database package supplies the enums and offset pairs; shared backend infrastructure supplies the clock and logger.

## Operating modes

Samples are a synchronous administrative loading step. No endpoint, separate command, automatic retry or periodic task is supplied here.

## File responsibilities

`sample_data.py` holds the fixed dataset, pure network/content/history decisions and transactional orchestration. `__init__.py` marks the layer and exports no operations.

## Main records and contracts

`common_sample_data.py` holds immutable definitions, measured prerequisites, reconciliation snapshots and results. `SampleDataFailure` is the approved public alias of `SampleDataError`, retaining the handoff while satisfying exception naming checks.

## Architectural decisions

Database access stays behind the data layer. The provider binds the documented backend clock and logger when called; importing its pure decisions neither reads configuration nor configures logging. Runtime dependencies are required, with no private replacement.

## Summary

The result carries `outcome`, `created_count`, `unchanged_count`, `initial_votes_created_count` and the stable four identifiers. The common program owns its adapter and command.

## Relation to SERVICE_ALGORITHM.md

`SERVICE_ALGORITHM.md` describes sample validation, preservation and failure behavior.
