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
    "SESSION_SIGNING_KEY": "invented-private-session-signing-key",
    "VOTER_HASH_KEY": "invented-private-voter-hash-key-of-32",
    "API_TRUSTED_PROXY_ADDRESSES": "",
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
        ("TILE_ARCHIVE_SOURCE", "relative/krakow.pmtiles"),
        ("TILE_ARCHIVE_DIR", "relative"),
        ("ROUTING_SERVICE_URL", "ftp://routing"),
        ("ROUTING_SERVICE_URL", "routing:8002"),
        ("ROUTING_DATA_DIR", "routing_data"),
        ("API_TRUSTED_PROXY_ADDRESSES", "*"),
        ("API_TRUSTED_PROXY_ADDRESSES", "10.0.0.1, *"),
        ("API_TRUSTED_PROXY_ADDRESSES", "proxy.internal"),
        ("API_TRUSTED_PROXY_ADDRESSES", "10.0.0.1/8"),
        ("API_TRUSTED_PROXY_ADDRESSES", "10.0.0.0/33"),
        ("API_TRUSTED_PROXY_ADDRESSES", "10.0.0.1,,10.0.0.2"),
        ("API_TRUSTED_PROXY_ADDRESSES", "999.0.0.1"),
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
    "key",
    [
        "APP_ENVIRONMENT",
        "API_BIND_HOST",
        "API_PORT",
        "BUSINESS_TIMEZONE",
        "DB_HOST",
        "DB_NAME",
        "DB_SERVICE_ACCOUNT_NAME",
        "DB_SERVICE_ACCOUNT_PASSWORD",
        "SESSION_SIGNING_KEY",
        "VOTER_HASH_KEY",
        "ROUTING_SERVICE_URL",
        "ROUTING_DATA_DIR",
    ],
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
    assert str(settings.ROUTING_DATA_DIR) == ABSOLUTE_ROUTING_DATA_DIR


def test_optional_valhalla_paths_do_not_block_api_configuration() -> None:
    """Permit API settings before the Valhalla tool directory and configuration template of the import are configured."""
    settings = Settings(**VALID, VALHALLA_TOOL_DIR="", VALHALLA_CONFIG_TEMPLATE="")
    assert settings.VALHALLA_TOOL_DIR is None
    assert settings.VALHALLA_CONFIG_TEMPLATE is None


def test_optional_tile_places_do_not_block_api_configuration() -> None:
    """Permit API settings before the source and the served directory of the tile archive are configured."""
    settings = Settings(**VALID, TILE_ARCHIVE_SOURCE="", TILE_ARCHIVE_DIR="")
    assert settings.TILE_ARCHIVE_SOURCE is None
    assert settings.TILE_ARCHIVE_DIR is None


def test_absent_public_transport_switch_keeps_walking_routes_only() -> None:
    """Keep routes with public transport off when the switch entry is missing."""
    assert Settings(**VALID).PUBLIC_TRANSPORT_ENABLED is False


@pytest.mark.parametrize(("value", "expected"), [("true", True), ("false", False), ("", False)])
def test_public_transport_switch_reads_true_false_and_the_empty_marker(value: str, expected: bool) -> None:
    """Turn routes with public transport on only for true, and off for false and the empty template marker."""
    assert Settings(**VALID, PUBLIC_TRANSPORT_ENABLED=value).PUBLIC_TRANSPORT_ENABLED is expected


@pytest.mark.parametrize("value", ["yes", "1", "True"])
def test_public_transport_switch_refuses_another_text_by_name(value: str) -> None:
    """Refuse a switch value other than true, false or empty, naming the entry and its file without the value."""
    with pytest.raises(ConfigurationError) as caught:
        Settings(**VALID, PUBLIC_TRANSPORT_ENABLED=value)
    assert "PUBLIC_TRANSPORT_ENABLED (.env.local)" in str(caught.value)
    assert value not in str(caught.value)


def test_session_signing_key_shorter_than_32_characters_is_refused_by_name() -> None:
    """Refuse a signing key of 31 characters, naming the entry and its file without the key."""
    key = "private" + "k" * 24
    with pytest.raises(ConfigurationError) as caught:
        Settings(**{**VALID, "SESSION_SIGNING_KEY": key})
    assert "SESSION_SIGNING_KEY (.env)" in str(caught.value)
    assert key not in str(caught.value)


def test_session_signing_key_of_32_characters_is_accepted_and_kept_secret() -> None:
    """Accept a signing key of exactly 32 characters and keep it out of the text of the settings."""
    key = "private" + "k" * 25
    settings = Settings(**{**VALID, "SESSION_SIGNING_KEY": key})
    assert settings.SESSION_SIGNING_KEY.get_secret_value() == key
    assert key not in repr(settings)


def test_voter_hash_key_shorter_than_32_characters_is_refused_by_name() -> None:
    """Refuse a key of the anonymous identity of 31 characters, naming the entry and its file without the key."""
    key = "private" + "v" * 24
    with pytest.raises(ConfigurationError) as caught:
        Settings(**{**VALID, "VOTER_HASH_KEY": key})
    assert "VOTER_HASH_KEY (.env)" in str(caught.value)
    assert key not in str(caught.value)


def test_voter_hash_key_of_32_characters_is_accepted_and_kept_secret() -> None:
    """Accept a key of the anonymous identity of exactly 32 characters and keep it out of the text of the settings."""
    key = "private" + "v" * 25
    settings = Settings(**{**VALID, "VOTER_HASH_KEY": key})
    assert settings.VOTER_HASH_KEY.get_secret_value() == key
    assert key not in repr(settings)


def test_empty_trusted_proxy_entry_trusts_no_proxy() -> None:
    """Read the empty marker of the trusted proxy as no trusted address, the local case in which the peer is the person."""
    assert Settings(**VALID).API_TRUSTED_PROXY_ADDRESSES == ()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("172.18.0.5", ("172.18.0.5",)),
        ("172.18.0.0/16", ("172.18.0.0/16",)),
        (" 172.18.0.5 , fd00::/8 ,::1", ("172.18.0.5", "fd00::/8", "::1")),
    ],
)
def test_trusted_proxy_entry_accepts_addresses_and_networks(value: str, expected: tuple[str, ...]) -> None:
    """Accept single addresses and networks without host bits, trimmed of the spaces around each entry."""
    entries = Settings(**{**VALID, "API_TRUSTED_PROXY_ADDRESSES": value}).API_TRUSTED_PROXY_ADDRESSES
    assert entries == expected
