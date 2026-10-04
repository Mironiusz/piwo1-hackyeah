"""Verify pure configuration rejection and administrative optionality."""

import pytest

from config.settings import ConfigurationError, Settings

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


@pytest.mark.parametrize("key", ["DB_HOST", "DB_NAME", "DB_SERVICE_ACCOUNT_NAME", "DB_SERVICE_ACCOUNT_PASSWORD"])
def test_unfilled_database_entry_is_refused_by_name(key: str) -> None:
    """Refuse the empty marker an unfilled template leaves, naming the entry and its file."""
    values = VALID.copy()
    values[key] = ""
    with pytest.raises(ConfigurationError) as caught:
        Settings(**values)
    assert key in str(caught.value)
    assert "private" not in str(caught.value)


def test_optional_workspace_does_not_block_api_configuration() -> None:
    """Permit API settings before an import workspace has been configured."""
    settings = Settings(**VALID, IMPORT_WORKSPACE_ROOT="")
    assert settings.IMPORT_WORKSPACE_ROOT is None
    assert settings.LOG_LEVEL == "INFO"
    assert "private" not in repr(settings)
