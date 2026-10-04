"""Validate supplied settings without reading the environment."""

import ipaddress
import re
from pathlib import Path
from typing import Any, Final, Literal
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator

ENVIRONMENT_ENTRY_FILES = {
    "APP_ENVIRONMENT": ".env.local",
    "API_BIND_HOST": ".env.local",
    "API_PORT": ".env.local",
    "BUSINESS_TIMEZONE": ".env.local",
    "LOG_LEVEL": ".env.local",
    "IMPORT_WORKSPACE_ROOT": ".env.local",
    "ROUTING_SERVICE_URL": ".env.local",
    "ROUTING_DATA_DIR": ".env.local",
    "VALHALLA_TOOL_DIR": ".env.local",
    "VALHALLA_CONFIG_TEMPLATE": ".env.local",
    "PUBLIC_TRANSPORT_ENABLED": ".env.local",
    "DB_SERVICE_ACCOUNT_PASSWORD": ".env",
    "SESSION_SIGNING_KEY": ".env",
    "DB_SERVICE_ACCOUNT_NAME": ".env.local",
    "DB_NAME": ".env.local",
    "DB_HOST": "launch environment",
    "DB_PORT": "launch environment",
}
DEFAULT_LOG_LEVEL: Final = "INFO"
SESSION_SIGNING_KEY_MIN_LENGTH: Final = 32


class ConfigurationError(ValueError):
    """Identify a missing or invalid setting without including its value."""


class Settings(BaseModel):
    """
    Hold the validated application contract, the service-account entries of db/, the key that signs session tokens,
    the routing service and its data, the optional import path and the switch of public transport.
    """

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
    SESSION_SIGNING_KEY: SecretStr = Field(min_length=SESSION_SIGNING_KEY_MIN_LENGTH)
    IMPORT_WORKSPACE_ROOT: Path | None = None
    ROUTING_SERVICE_URL: str
    ROUTING_DATA_DIR: Path
    VALHALLA_TOOL_DIR: Path | None = None
    VALHALLA_CONFIG_TEMPLATE: Path | None = None
    PUBLIC_TRANSPORT_ENABLED: bool = False

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

    @field_validator("PUBLIC_TRANSPORT_ENABLED", mode="before")
    @classmethod
    def build_public_transport_switch(cls, value: Any) -> Any:
        """Turn routes with public transport on only for the exact text true, off for false or the empty template marker, and refuse any other text."""
        if isinstance(value, bool):
            return value
        switch = {"true": True, "false": False, "": False}
        if not isinstance(value, str) or value not in switch:
            raise ValueError("invalid_public_transport_switch")
        return switch[value]

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

    @field_validator("IMPORT_WORKSPACE_ROOT", "ROUTING_DATA_DIR", "VALHALLA_TOOL_DIR", "VALHALLA_CONFIG_TEMPLATE", mode="before")
    @classmethod
    def build_path_entry(cls, value: Any) -> Any:
        """Treat an empty path entry as unset, so a required one is refused by name and an optional one stays None."""
        return None if value == "" else value

    @field_validator("IMPORT_WORKSPACE_ROOT", "ROUTING_DATA_DIR", "VALHALLA_TOOL_DIR", "VALHALLA_CONFIG_TEMPLATE")
    @classmethod
    def apply_absolute_path_validation(cls, value: Path | None) -> Path | None:
        """Require an absolute path without probing its existence."""
        if value is not None and not value.is_absolute():
            raise ValueError("path_must_be_absolute")
        return value

    @field_validator("ROUTING_SERVICE_URL")
    @classmethod
    def apply_routing_url_validation(cls, value: str) -> str:
        """Require an http or https address of the routing service of the project with a host, so no other scheme can be called."""
        parts = urlsplit(value)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError("invalid_routing_service_url")
        return value
