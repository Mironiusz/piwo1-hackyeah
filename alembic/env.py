"""Read the migration-only identity without importing runtime configuration.

Alembic runs outside the application and is the documented exception allowed to
read MIGRATION_DATABASE_URL. It uses the same file parser and source precedence.
"""

import os
from pathlib import Path

from pydantic import SecretStr

from alembic import context
from config.env_file import build_environment_values
from config.settings import apply_database_address_validation
from data.engine import build_migration_engine

values: dict[str, str] = {}
for path in (Path(".env"), Path(".env.local")):
    if path.exists():
        values.update(build_environment_values(path.read_text(encoding="utf-8")))
values.update(os.environ)
if not values.get("MIGRATION_DATABASE_URL"):
    raise ValueError("MIGRATION_DATABASE_URL is required for Alembic")
if not values.get("DATABASE_SERVICE_USER"):
    raise ValueError("DATABASE_SERVICE_USER is required for revision grants")
try:
    address = apply_database_address_validation(SecretStr(values["MIGRATION_DATABASE_URL"]))
except ValueError:
    raise ValueError("MIGRATION_DATABASE_URL is invalid") from None
context.config.attributes["service_role_name"] = values["DATABASE_SERVICE_USER"]
engine = build_migration_engine(address)
try:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
