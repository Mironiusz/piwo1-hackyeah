"""Validate supplied settings without reading the environment."""

import ipaddress
import re
from pathlib import Path
from typing import Any, Final, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator

ENVIRONMENT_ENTRY_FILES = {
    "APP_ENVIRONMENT": ".env.local",
    "API_BIND_HOST": ".env.local",
    "API_PORT": ".env.local",
    "BUSINESS_TIMEZONE": ".env.local",
    "LOG_LEVEL": ".env.local",
    "IMPORT_WORKSPACE_ROOT": ".env.local",
    "DB_SERVICE_ACCOUNT_PASSWORD": ".env",
    "DB_SERVICE_ACCOUNT_NAME": ".env.local",
    "DB_NAME": ".env.local",
    "DB_HOST": "launch environment",
    "DB_PORT": "launch environment",
}
DEFAULT_LOG_LEVEL: Final = "INFO"


class ConfigurationError(ValueError):
    """Identify a missing or invalid setting without including its value."""


class Settings(BaseModel):
    """Hold the validated application contract, the service-account entries of db/ and the optional import path."""

    model_config = ConfigDict(extra="ignore", hide_input_in_errors=True)
    APP_ENVIRONMENT: Literal["local", "target"]
    API_BIND_HOST: str
    API_PORT: int = Field(ge=1, le=65535)
    BUSINESS_TIMEZONE: str
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = DEFAULT_LOG_LEVEL
    DB_HOST: str
    DB_PORT: int = Field(ge=1, le=65535)
    DB_NAME: str = Field(min_length=1)
    DB_SERVICE_ACCOUNT_NAME: str = Field(min_length=1)
    DB_SERVICE_ACCOUNT_PASSWORD: SecretStr
    IMPORT_WORKSPACE_ROOT: Path | None = None

    def __init__(self, **data: Any) -> None:
        """Replace library validation details with safe key-only failures."""
        try:
            super().__init__(**data)
        except ValidationError as error:
            names = sorted({str(item["loc"][0]) for item in error.errors(include_input=False, include_context=False)})
            entries = ", ".join(f"{name} ({ENVIRONMENT_ENTRY_FILES[name]})" for name in names)
            raise ConfigurationError(f"Missing or invalid configuration: {entries}") from None

    @field_validator("DB_SERVICE_ACCOUNT_PASSWORD")
    @classmethod
    def apply_password_validation(cls, value: SecretStr) -> SecretStr:
        """Refuse an empty service-account password, which an unfilled template marker leaves behind."""
        if not value.get_secret_value():
            raise ValueError("empty_service_account_password")
        return value

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def build_log_level(cls, value: Any) -> Any:
        """Treat the empty template marker as the documented default level, never as a more verbose one."""
        return DEFAULT_LOG_LEVEL if value == "" else value

    @field_validator("BUSINESS_TIMEZONE")
    @classmethod
    def apply_timezone_validation(cls, value: str) -> str:
        """Require an explicitly configured IANA business timezone."""
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("invalid_business_timezone") from None
        return value

    @field_validator("API_BIND_HOST", "DB_HOST")
    @classmethod
    def apply_host_validation(cls, value: str) -> str:
        """Accept an IP address or a syntactically valid DNS name, for the bind host and for the database host alike."""
        try:
            ipaddress.ip_address(value)
        except ValueError:
            labels = value.split(".")
            if len(value) > 253 or not all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label) for label in labels):
                raise ValueError("invalid_host") from None
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
