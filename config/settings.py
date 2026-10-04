"""Validate supplied settings without reading the environment."""

import ipaddress
import re
from pathlib import Path
from typing import Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

ENVIRONMENT_ENTRY_FILES = {
    "APP_ENVIRONMENT": ".env.local",
    "API_BIND_HOST": ".env.local",
    "API_PORT": ".env.local",
    "BUSINESS_TIMEZONE": ".env.local",
    "LOG_LEVEL": ".env.local",
    "IMPORT_WORKSPACE_ROOT": ".env.local",
    "DATABASE_URL": ".env",
    "MIGRATION_DATABASE_URL": ".env",
    "POSTGRES_PASSWORD": ".env",
    "DATABASE_OWNER_PASSWORD": ".env",
    "DATABASE_SERVICE_PASSWORD": ".env",
    "POSTGRES_USER": ".env.local",
    "DATABASE_OWNER_USER": ".env.local",
    "DATABASE_SERVICE_USER": ".env.local",
    "DATABASE_NAME": ".env.local",
    "DATABASE_HOST_PORT": ".env.local",
}


class ConfigurationError(ValueError):
    """Identify a missing or invalid setting without including its value."""


def apply_database_address_validation(address: SecretStr) -> SecretStr:
    """Require the selected PostgreSQL driver and an explicit database."""
    try:
        parsed = make_url(address.get_secret_value())
    except ArgumentError:
        raise ValueError("invalid_database_address") from None
    if parsed.drivername != "postgresql+psycopg" or not parsed.database or not parsed.username:
        raise ValueError("invalid_database_address")
    if any(marker in address.get_secret_value() for marker in ("<", ">")):
        raise ValueError("unfilled_database_address")
    return address


class Settings(BaseModel):
    """Hold the validated application contract and optional import path."""

    model_config = ConfigDict(extra="ignore", hide_input_in_errors=True)
    APP_ENVIRONMENT: Literal["local", "target"]
    API_BIND_HOST: str
    API_PORT: int = Field(ge=1, le=65535)
    BUSINESS_TIMEZONE: str
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    DATABASE_URL: SecretStr
    IMPORT_WORKSPACE_ROOT: Path | None = None

    def __init__(self, **data: Any) -> None:
        """Replace library validation details with safe key-only failures."""
        try:
            super().__init__(**data)
        except ValidationError as error:
            names = sorted({str(item["loc"][0]) for item in error.errors(include_input=False, include_context=False)})
            entries = ", ".join(f"{name} ({ENVIRONMENT_ENTRY_FILES[name]})" for name in names)
            raise ConfigurationError(f"Missing or invalid configuration: {entries}") from None

    @field_validator("DATABASE_URL")
    @classmethod
    def apply_database_validation(cls, value: SecretStr) -> SecretStr:
        """Validate the runtime address without connecting to the database."""
        return apply_database_address_validation(value)

    @field_validator("BUSINESS_TIMEZONE")
    @classmethod
    def apply_timezone_validation(cls, value: str) -> str:
        """Require an explicitly configured IANA business timezone."""
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("invalid_business_timezone") from None
        return value

    @field_validator("API_BIND_HOST")
    @classmethod
    def apply_host_validation(cls, value: str) -> str:
        """Accept an IP address or a syntactically valid DNS bind name."""
        try:
            ipaddress.ip_address(value)
        except ValueError:
            labels = value.split(".")
            if len(value) > 253 or not all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label) for label in labels):
                raise ValueError("invalid_bind_host") from None
        return value

    @field_validator("IMPORT_WORKSPACE_ROOT", mode="before")
    @classmethod
    def build_workspace_path(cls, value: Any) -> Any:
        """Treat an empty administrative entry as unconfigured."""
        return None if value == "" else value

    @field_validator("IMPORT_WORKSPACE_ROOT")
    @classmethod
    def apply_workspace_path_validation(cls, value: Path | None) -> Path | None:
        """Require an absolute import workspace without probing its existence."""
        if value is not None and not value.is_absolute():
            raise ValueError("workspace_must_be_absolute")
        return value
