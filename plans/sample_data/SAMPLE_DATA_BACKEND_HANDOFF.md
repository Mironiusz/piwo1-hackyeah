# Sample critical-fixture handoff

Document state: 2026-10-04, contract authorized by the user; backend engine/configuration delivery outstanding

## Approval and ownership

On 2026-10-04 the user authorized defining the missing fixture contract in `sample_data` and handing it to `backend_skeleton`. This clarifies sample plan S-4 and D-13. It does not authorize replacing shared engine/configuration infrastructure or a hosted database action.

`sample_data` supplies `tests/common_database_fixtures.py`, the shared registry fixture and collection guard in `tests/conftest.py`, and sample-specific fixtures and tests under `tests/data/`. `backend_skeleton` must preserve these pieces when delivering its remaining shared test foundation and add its owner-engine fixture to the existing `tests/data/conftest.py`.

## Shared backend inputs

- `config.config.APP_ENVIRONMENT`: the same validated `local` or `target` constant used to select the runtime environment. No test-specific environment selector is introduced.
- `data.engine.build_engine(statement_timeout_ms: int) -> Engine`: the actual restricted service-account engine, with UTC sessions and the documented connection/pool bounds. The sample runtime asks for 5000 ms.
- `data.engine.build_migration_engine(address: SecretStr) -> Engine`: the explicit local-owner engine factory, independent of runtime settings. Owner credentials never enter the runtime facade.
- `schema_owner_engine: Engine`: a fixture delivered by `backend_skeleton` in `tests/data/conftest.py`. It reads validated local owner configuration through the established settings/parser path, refuses nonlocal operation and uses `build_migration_engine`. It yields the engine until dependent fixtures finish and disposes it afterwards. No test recreates configuration precedence or a raw connection factory.
- `common_time.fetch_business_now()` and `config.logging.fetch_logger(name)`: the documented provider inputs, required for real entry-point tests.

## Cleanup registry

`database_cleanup_registry` is a fixture in `tests/conftest.py`, returning `DatabaseFixtureRegistry` from `tests/common_database_fixtures.py`. It depends on `schema_owner_engine`. There is no fake successful registry when the owner engine is absent.

`DatabaseFixtureRegistry.apply_registration(action: Callable[[Connection], None])` registers a fixture's exact-key cleanup before durable writes. Every registered action must use fixed, bound SQL and only registered keys; fixture ownership predicates remain with that fixture. `apply_cleanup()` runs actions in reverse registration order in one owner transaction. A cleanup failure rolls back cleanup and remains a failed test. No broad name filter, schema reset or deletion by the restricted runtime role is allowed.

Sample cleanup also checks that its unique copy marker is the sole copy and checks the original sample creation pair, so another publication, an occupied unrelated identifier or later unrelated content is not treated as owned fixture data. Tests refuse existing copy/network fixtures and occupied sample identifiers before their durable setup. Cleanup removes dependent votes before facts and network links before ways, and deletes only the registered copy marker. A test fixture's advisory lease serializes other sample fixtures during setup, execution and cleanup; it does not claim full production-loader exclusion. The fixture finishes registered cleanup before explicitly unlocking its pooled lease; the shared registry clears acknowledged cleanup actions, so its final teardown does not repeat them.

## Collection guard

Before any fixture runs, `pytest_collection_finish` checks whether the selected collection contains a `critical` test. For such a session, inability to import or validate the shared facade refuses with exit 4 and a fixed message. Any value other than `local` also refuses with exit 4. This applies to `--collect-only` as well. Noncritical tests require no runtime configuration.

`backend_skeleton` may extend the same guard for its tests; it must not create a second guard using another environment value or weaken refusal when configuration is absent. `tests/architecture/test_sample_critical_guard.py` supplies framework evidence using invented configuration and a write sentinel, without a real database.

## Remaining executable evidence

The guard and isolated transaction decisions can be tested immediately. Real provider tests require the delivered engine/configuration/clock/logger, local owner fixture and separately applied first product revision. The shared fixture contract does not itself prove a running schema, SQL correctness, permission behavior, source-copy evidence or a completed common demo flow.
