"""Own isolated local scratch objects without changing product revisions."""

import pytest
from pydantic import SecretStr
from sqlalchemy import text

from data.engine import build_import_engine, build_migration_engine


@pytest.fixture
def scratch_database(request, registered_cleanup):
    """Create exact invented objects and grant only scratch DML to the service."""
    address = request.config.getoption("--scratch-database-url")
    if address is None:
        pytest.fail("Pass --scratch-database-url with a local owner URL for database acceptance")
    owner = build_migration_engine(SecretStr(address))
    service = build_import_engine(5000)
    with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        if connection.execute(text("SELECT to_regclass('public.backend_skeleton_scratch') IS NOT NULL")).scalar_one():
            pytest.fail("Scratch table already exists; refusing to overwrite it")

        def apply_cleanup():
            """Remove only this fixture's exact registered objects."""
            with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as cleanup:
                cleanup.execute(text("DROP TABLE IF EXISTS public.backend_skeleton_scratch"))
            service.dispose()
            owner.dispose()

        registered_cleanup(apply_cleanup)
        connection.execute(text("CREATE TABLE public.backend_skeleton_scratch (run_id text NOT NULL, value text NOT NULL)"))
        from sqlalchemy.engine import make_url

        from config.config import DATABASE_URL

        role = make_url(DATABASE_URL.get_secret_value()).username
        statement = connection.execute(text("SELECT format('GRANT SELECT, INSERT, DELETE ON public.backend_skeleton_scratch TO %I', CAST(:role AS text))"), {"role": role}).scalar_one()
        connection.exec_driver_sql(statement)
    return owner, service
