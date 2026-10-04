"""Verify pure configuration rejection and administrative optionality."""

from pathlib import Path

import pytest

from config.settings import ConfigurationError, Settings

ABSOLUTE_ROUTING_DATA_DIR = str(Path(__file__).resolve().parent / "invented_routing_data")
VALID = {
    "APP_ENVIRONMENT": "local",
    "API_BIND_HOST": "127.0.0.1",
    "API_PORT": "8000",
    "BUSINESS_TIMEZONE": "Europe/Warsaw",
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "5432",
    "DB_NAME": "invented",
    "DB_SERVICE_ACCOUNT_NAME": "invented",
    "DB_SERVICE_ACCOUNT_PASSWORD": "invented-private",
    "ROUTING_SERVICE_URL": "http://routing:8002",
    "ROUTING_DATA_DIR": ABSOLUTE_ROUTING_DATA_DIR,
}


@pytest.mark.parametrize("key", list(VALID))
def test_required_entry_has_safe_named_failure(key: str) -> None:
    """Reject missing runtime settings by key without including secret values."""
    values = VALID.copy()
    del values[key]
    with pytest.raises(ConfigurationError) as caught:
        Settings(**values)
    assert key in str(caught.value)
    assert "private" not in str(caught.value)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("API_PORT", "0"),
        ("API_PORT", "65536"),
        ("BUSINESS_TIMEZONE", "invented/no-zone"),
        ("APP_ENVIRONMENT", "production"),
        ("API_BIND_HOST", "http://bad"),
        ("DB_HOST", "http://bad"),
        ("DB_PORT", "0"),
        ("DB_PORT", "65536"),
        ("IMPORT_WORKSPACE_ROOT", "relative"),
        ("VALHALLA_TOOL_DIR", "relative"),
        ("VALHALLA_CONFIG_TEMPLATE", "relative/valhalla.json"),
        ("ROUTING_SERVICE_URL", "ftp://routing"),
        ("ROUTING_SERVICE_URL", "routing:8002"),
        ("ROUTING_DATA_DIR", "routing_data"),
    ],
)
def test_invalid_entries_do_not_leak_values(key: str, value: str) -> None:
    """Reject invalid values while preserving the key-only failure contract."""
    values = VALID.copy()
    values[key] = value
    with pytest.raises(ConfigurationError) as caught:
        Settings(**values)
    assert key in str(caught.value)
    assert value not in str(caught.value)


@pytest.mark.parametrize(
    "key", ["APP_ENVIRONMENT", "API_BIND_HOST", "API_PORT", "BUSINESS_TIMEZONE", "DB_HOST", "DB_NAME", "DB_SERVICE_ACCOUNT_NAME", "DB_SERVICE_ACCOUNT_PASSWORD", "ROUTING_SERVICE_URL", "ROUTING_DATA_DIR"]
)
def test_unfilled_required_entry_is_refused_by_name(key: str) -> None:
    """Refuse the empty marker an unfilled template leaves, naming the entry and its file."""
    values = VALID.copy()
    values[key] = ""
    with pytest.raises(ConfigurationError) as caught:
        Settings(**values)
    assert key in str(caught.value)
    assert "private" not in str(caught.value)


def test_unfilled_log_level_uses_the_default_level() -> None:
    """Read the empty template marker of the log level as the documented default, not as an error or a verbose level."""
    settings = Settings(**VALID, LOG_LEVEL="")
    assert settings.LOG_LEVEL == "INFO"


def test_optional_workspace_does_not_block_api_configuration() -> None:
    """Permit API settings before an import workspace has been configured."""
    settings = Settings(**VALID, IMPORT_WORKSPACE_ROOT="")
    assert settings.IMPORT_WORKSPACE_ROOT is None
    assert settings.LOG_LEVEL == "INFO"
    assert "private" not in repr(settings)


def test_routing_entries_accept_a_service_address_and_an_absolute_directory() -> None:
    """Accept the address of the routing service on the internal network and an absolute routing data directory."""
    settings = Settings(**VALID)
    assert settings.ROUTING_SERVICE_URL == "http://routing:8002"
    assert settings.ROUTING_DATA_DIR == Path(ABSOLUTE_ROUTING_DATA_DIR)


def test_optional_valhalla_paths_do_not_block_api_configuration() -> None:
    """Permit API settings before the Valhalla tool directory and configuration template of the import are configured."""
    settings = Settings(**VALID, VALHALLA_TOOL_DIR="", VALHALLA_CONFIG_TEMPLATE="")
    assert settings.VALHALLA_TOOL_DIR is None
    assert settings.VALHALLA_CONFIG_TEMPLATE is None
