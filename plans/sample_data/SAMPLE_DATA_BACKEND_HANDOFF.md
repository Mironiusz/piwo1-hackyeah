# Sample critical-fixture handoff

Document state: 2026-10-04, owner-engine fixture delivered in `sample_data` (plan D-10); critical sample tests pass on a local database

## Approval and ownership

On 2026-10-04 the user authorized defining the missing fixture contract in `sample_data`. The first version handed the owner-engine fixture to `backend_skeleton`. At the merge of `mw-osm-import` the user removed `build_migration_engine` from that initiative (`plans_finished/backend_skeleton/BACKEND_SKELETON_PLAN.md`, D-10 change note), so `sample_data` now defines the fixture itself, as its plan D-10 decides. This does not authorize replacing shared engine or configuration infrastructure or any hosted database action.

`sample_data` supplies `tests/common_database_fixtures.py`, the shared registry fixture and collection guard in `tests/conftest.py`, the `schema_owner_engine` fixture in `tests/data/conftest.py`, and sample-specific fixtures and tests under `tests/data/`. Other initiatives preserve these pieces and reuse `schema_owner_engine` instead of building another owner engine.

## Shared backend inputs

- `config.config.APP_ENVIRONMENT`: the same validated `local` or `target` constant used to select the runtime environment. No test-specific environment selector is introduced.
- `data.engine.build_engine(statement_timeout_ms: int) -> Engine`: the actual restricted service-account engine, with UTC sessions and the documented connection and pool bounds. The sample runtime asks for 5000 ms.
- `data.engine.apply_engine_construction(address, statement_timeout_ms, unpooled) -> Engine`: the one engine construction, which the owner fixture uses with the explicit local address.
- `schema_owner_engine: Engine`: a fixture in `tests/data/conftest.py`. It builds an unpooled engine from the `--scratch-database-url` option with `apply_engine_construction` and a 30000 ms statement limit, fails the test when the option is absent, yields the engine until the dependent fixtures finish and disposes it afterwards. `scratch_database` consumes it instead of building its own owner engine. Owner credentials never enter the runtime facade or a file of the repository.
- `common_time.fetch_business_now()` and `config.logging.fetch_logger(name)`: the provider inputs. The sample fixture replaces `service.sample_data.fetch_business_now` with its invented clock.

## Cleanup registry

`database_cleanup_registry` is a fixture in `tests/conftest.py`, returning `DatabaseFixtureRegistry` from `tests/common_database_fixtures.py`. It depends on `schema_owner_engine`. There is no fake successful registry when the owner engine is absent.

`DatabaseFixtureRegistry.apply_registration(action: Callable[[Connection], None])` registers a fixture's exact-key cleanup before durable writes. Every registered action must use fixed, bound SQL and only registered keys; fixture ownership predicates remain with that fixture. `apply_cleanup()` runs actions in reverse registration order in one owner transaction. A cleanup failure rolls back cleanup and remains a failed test. No broad name filter, schema reset or deletion by the restricted runtime role is allowed.

The sample fixture seeds an invented network: the eight reference ways shortened to the nodes around each sample point, with the node positions of the public OpenStreetMap response, their memberships, the lowered kerb node 317034340 on way 252778084 and one unique copy marker. Sample cleanup checks that its marker is the sole copy and that every fact on a reserved identifier carries the creation pair the first loading writes for it, so another publication, an occupied unrelated identifier or later unrelated content is not treated as owned fixture data. Tests refuse an existing copy, way or node and occupied sample identifiers before their durable setup. Cleanup removes dependent votes before facts, memberships before ways and nodes, and deletes only the registered copy marker. The fixture resets the route-graph cache of the process before and after each test, so a changed network is never answered from a graph cached for the same copy instant. A test fixture's advisory lease serializes other sample fixtures during setup, execution and cleanup; it does not claim full production-loader exclusion.

## Collection guard

Before any fixture runs, `pytest_collection_finish` checks whether the selected collection contains a `critical` test. For such a session, inability to import or validate the shared facade refuses with exit 4 and a fixed message. Any value other than `local` also refuses with exit 4. This applies to `--collect-only` as well. Noncritical tests require no runtime configuration.

Other initiatives may extend the same guard for their tests; they must not create a second guard using another environment value or weaken refusal when configuration is absent. `tests/architecture/test_sample_critical_guard.py` supplies framework evidence using invented configuration and a write sentinel, without a real database.

## Executable evidence

On 2026-10-04 the 17 critical sample cases passed against a separate local database of `db/compose.yaml` with the first product revision applied, the restricted service account and throwaway local values passed only through the process environment. The cases that use `scratch_database` passed on the same database after it moved to `schema_owner_engine`. The fixture contract does not itself prove the imported copy, the actual route or a completed common demo flow.
