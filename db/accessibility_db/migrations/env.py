"""
The environment of the schema revisions: connects as the schema owner and applies the chain online.

This file reads its entries directly from the environment, not through a configuration facade, because the revisions
run outside the application and the account that changes the schema must not sit in a layer every service process
imports (`docs/standards/standard_config.md`, the exception of `alembic/env.py`). A missing entry stops the run with its
name. Applying the chain to the target environment also needs the consent `DB_REVISION_CONSENT=apply` given at the call
and never written in a file.
"""

import os

from alembic import context
from sqlalchemy import URL, create_engine

LOCAL_ENVIRONMENT = "local"
TARGET_ENVIRONMENT = "target"
REVISION_CONSENT = "apply"
SERVICE_ACCOUNT_NAME_ATTRIBUTE = "service_account_name"


def fetch_environment_value(name: str) -> str:
    """Reads one required entry from the environment and stops with its name when it is missing or empty."""
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Set the environment entry {name} before applying the schema revisions.")
    return value


def resolve_application_allowed(environment: str, consent: str) -> bool:
    """Decides whether the chain may be applied: always locally, in the target environment only with the consent."""
    if environment == LOCAL_ENVIRONMENT:
        return True
    if environment == TARGET_ENVIRONMENT:
        return consent == REVISION_CONSENT
    raise RuntimeError(f"DB_ENVIRONMENT must be {LOCAL_ENVIRONMENT} or {TARGET_ENVIRONMENT}.")


def build_schema_owner_url() -> URL:
    """Builds the address of the schema owner account from its entries, without writing any value in the repository."""
    return URL.create(
        "postgresql+psycopg",
        username=fetch_environment_value("DB_SCHEMA_OWNER_NAME"),
        password=fetch_environment_value("DB_SCHEMA_OWNER_PASSWORD"),
        host=fetch_environment_value("DB_HOST"),
        port=int(fetch_environment_value("DB_PORT")),
        database=fetch_environment_value("DB_NAME"),
    )


def apply_schema_revisions() -> None:
    """Applies the chain online as the schema owner, with the session zone pinned to UTC and the service account named."""
    if not resolve_application_allowed(fetch_environment_value("DB_ENVIRONMENT"), os.environ.get("DB_REVISION_CONSENT", "")):
        raise RuntimeError("Applying the schema revisions to the target environment needs DB_REVISION_CONSENT=apply given at the call.")
    context.config.attributes[SERVICE_ACCOUNT_NAME_ATTRIBUTE] = fetch_environment_value("DB_SERVICE_ACCOUNT_NAME")
    engine = create_engine(build_schema_owner_url(), connect_args={"options": "-c timezone=UTC"})
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=None)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    raise RuntimeError("The schema revisions are applied online only, against a running database.")

apply_schema_revisions()
