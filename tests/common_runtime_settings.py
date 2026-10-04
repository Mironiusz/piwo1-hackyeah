"""Invented runtime settings shared by the tests that import the configuration facade."""

import importlib
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

INVENTED_RUNTIME_SETTINGS = {
    "APP_ENVIRONMENT": "local",
    "API_BIND_HOST": "127.0.0.1",
    "API_PORT": "8000",
    "BUSINESS_TIMEZONE": "Europe/Warsaw",
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "5432",
    "DB_NAME": "invented",
    "DB_SERVICE_ACCOUNT_NAME": "invented",
    "DB_SERVICE_ACCOUNT_PASSWORD": "invented-private",
    "LOG_LEVEL": "DEBUG",
    "ROUTING_SERVICE_URL": "http://routing:8002",
    "ROUTING_DATA_DIR": str(Path(__file__).resolve().parent / "invented_routing_data"),
}


@contextmanager
def apply_invented_runtime_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Load the configuration facade from invented values and restore the previously loaded facade afterwards."""
    saved = sys.modules.pop("config.config", None)
    for key, value in INVENTED_RUNTIME_SETTINGS.items():
        monkeypatch.setenv(key, value)
    importlib.import_module("config.config")
    try:
        yield
    finally:
        sys.modules.pop("config.config", None)
        if saved is not None:
            sys.modules["config.config"] = saved
