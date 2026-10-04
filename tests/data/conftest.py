"""Sample fixtures consuming the shared, validated local owner-engine contract."""

from collections.abc import Iterator

import pytest
from sqlalchemy import text

from tests.common_database_fixtures import DatabaseFixtureRegistry
from tests.data.common_sample_data_fixtures import SAMPLE_FIXTURE_LOCK_KEY, SAMPLE_FIXTURE_LOCK_NAMESPACE, SampleCriticalDataset, apply_sample_network_fixture, build_sample_critical_dataset


@pytest.fixture
def sample_critical_dataset(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, database_cleanup_registry: DatabaseFixtureRegistry) -> Iterator[SampleCriticalDataset]:
    """Holds a test-only lease through cleanup and registers before durable seeding."""
    from common_time import fetch_business_now

    dataset = build_sample_critical_dataset(request.param if hasattr(request, "param") else 1)
    lease = database_cleanup_registry.owner_engine.connect().execution_options(isolation_level="AUTOCOMMIT")
    acquired = False
    try:
        acquired = lease.execute(text("SELECT pg_try_advisory_lock(:namespace, :key)"), {"namespace": SAMPLE_FIXTURE_LOCK_NAMESPACE, "key": SAMPLE_FIXTURE_LOCK_KEY}).scalar_one()
        if not acquired:
            raise RuntimeError("Another sample fixture owns the local test lease.")
        database_cleanup_registry.apply_registration(dataset.apply_cleanup)
        with database_cleanup_registry.owner_engine.begin() as connection:
            apply_sample_network_fixture(connection, dataset)
        dataset.durable_setup_completed = True
        monkeypatch.setattr("common_time.fetch_business_now", dataset.fetch_business_now)
        assert callable(fetch_business_now)
        yield dataset
    finally:
        try:
            database_cleanup_registry.apply_cleanup()
        finally:
            try:
                if acquired:
                    lease.execute(text("SELECT pg_advisory_unlock(:namespace, :key)"), {"namespace": SAMPLE_FIXTURE_LOCK_NAMESPACE, "key": SAMPLE_FIXTURE_LOCK_KEY})
            finally:
                lease.close()
