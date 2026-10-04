"""Own isolated local scratch objects without changing product revisions, give rolled-back service connections and seed the invented sample network."""

from collections.abc import Iterator
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Connection, Engine, make_url, text

from data.engine import API_STATEMENT_TIMEOUT_MS, apply_engine_construction, build_engine, build_import_engine
from service.route_graph import ROUTE_GRAPH_CACHE
from tests.common_database_fixtures import DatabaseFixtureRegistry
from tests.data.common_sample_data_fixtures import SAMPLE_FIXTURE_LOCK_KEY, SAMPLE_FIXTURE_LOCK_NAMESPACE, SampleCriticalDataset, apply_sample_network_fixture, build_sample_critical_dataset

SCRATCH_OWNER_STATEMENT_TIMEOUT_MS = 30000


@pytest.fixture
def service_transaction() -> Iterator[Connection]:
    """Give a connection of the service account of db/ inside a transaction rolled back after the test, so no seeded row stays behind."""
    engine = build_engine(API_STATEMENT_TIMEOUT_MS)
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                yield connection
            finally:
                transaction.rollback()
    finally:
        engine.dispose()


@pytest.fixture
def schema_owner_engine(request: pytest.FixtureRequest) -> Iterator[Engine]:
    """Give an unpooled engine of the local schema owner of db/ from --scratch-database-url, disposed after the fixtures that use it."""
    address = request.config.getoption("--scratch-database-url")
    if address is None:
        pytest.fail("Pass --scratch-database-url with a local schema-owner URL for database acceptance")
    owner = apply_engine_construction(make_url(address), SCRATCH_OWNER_STATEMENT_TIMEOUT_MS, True)
    try:
        yield owner
    finally:
        owner.dispose()


@pytest.fixture
def scratch_database(schema_owner_engine: Engine, registered_cleanup):
    """Create exact invented objects as the schema owner of db/ and grant only scratch DML to the service account."""
    owner = schema_owner_engine
    service = build_import_engine(5000)
    with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        if connection.execute(text("SELECT to_regclass('public.backend_skeleton_scratch') IS NOT NULL")).scalar_one():
            pytest.fail("Scratch table already exists; refusing to overwrite it")

        def apply_cleanup():
            """Remove only this fixture's exact registered objects."""
            with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as cleanup:
                cleanup.execute(text("DROP TABLE IF EXISTS public.backend_skeleton_scratch"))
            service.dispose()

        registered_cleanup(apply_cleanup)
        connection.execute(text("CREATE TABLE public.backend_skeleton_scratch (run_id text NOT NULL, value text NOT NULL)"))
        from config.config import DB_SERVICE_ACCOUNT_NAME

        statement = connection.execute(
            text("SELECT format('GRANT SELECT, INSERT, DELETE ON public.backend_skeleton_scratch TO %I', CAST(:role AS text))"), {"role": DB_SERVICE_ACCOUNT_NAME}
        ).scalar_one()
        connection.exec_driver_sql(statement)
    return owner, service


@pytest.fixture
def sample_critical_dataset(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, database_cleanup_registry: DatabaseFixtureRegistry) -> Iterator[SampleCriticalDataset]:
    """Holds a test-only lease through cleanup, registers before durable seeding and keeps no route graph between tests."""
    business_now = request.param if hasattr(request, "param") else datetime(2026, 1, 10, 8, 0, tzinfo=ZoneInfo("Europe/Warsaw"))
    dataset = build_sample_critical_dataset(business_now)
    lease = database_cleanup_registry.owner_engine.connect().execution_options(isolation_level="AUTOCOMMIT")
    acquired = False
    ROUTE_GRAPH_CACHE.graph = None
    try:
        acquired = lease.execute(text("SELECT pg_try_advisory_lock(:namespace, :key)"), {"namespace": SAMPLE_FIXTURE_LOCK_NAMESPACE, "key": SAMPLE_FIXTURE_LOCK_KEY}).scalar_one()
        if not acquired:
            raise RuntimeError("Another sample fixture owns the local test lease.")
        database_cleanup_registry.apply_registration(dataset.apply_cleanup)
        with database_cleanup_registry.owner_engine.begin() as connection:
            apply_sample_network_fixture(connection, dataset)
        dataset.durable_setup_completed = True
        monkeypatch.setattr("service.sample_data.fetch_business_now", dataset.fetch_business_now)
        yield dataset
    finally:
        ROUTE_GRAPH_CACHE.graph = None
        try:
            database_cleanup_registry.apply_cleanup()
        finally:
            try:
                if acquired:
                    lease.execute(text("SELECT pg_advisory_unlock(:namespace, :key)"), {"namespace": SAMPLE_FIXTURE_LOCK_NAMESPACE, "key": SAMPLE_FIXTURE_LOCK_KEY})
            finally:
                lease.close()
