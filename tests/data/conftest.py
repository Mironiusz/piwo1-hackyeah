"""Own isolated local scratch objects without changing product revisions."""

import pytest
from sqlalchemy import make_url, text

from data.engine import apply_engine_construction, build_import_engine

SCRATCH_OWNER_STATEMENT_TIMEOUT_MS = 30000


@pytest.fixture
def scratch_database(request, registered_cleanup):
    """Create exact invented objects as the schema owner of db/ and grant only scratch DML to the service account."""
    address = request.config.getoption("--scratch-database-url")
    if address is None:
        pytest.fail("Pass --scratch-database-url with a local schema-owner URL for database acceptance")
    owner = apply_engine_construction(make_url(address), SCRATCH_OWNER_STATEMENT_TIMEOUT_MS, True)
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
        from config.config import DB_SERVICE_ACCOUNT_NAME

        statement = connection.execute(
            text("SELECT format('GRANT SELECT, INSERT, DELETE ON public.backend_skeleton_scratch TO %I', CAST(:role AS text))"), {"role": DB_SERVICE_ACCOUNT_NAME}
        ).scalar_one()
        connection.exec_driver_sql(statement)
    return owner, service
