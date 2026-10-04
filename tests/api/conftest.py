"""Provide invented runtime settings only for API integration tests."""

import importlib
import sys

import pytest


@pytest.fixture
def _runtime_settings(monkeypatch: pytest.MonkeyPatch):
    """Load valid invented configuration and restore module state afterwards."""
    values = {
        "APP_ENVIRONMENT": "local",
        "API_BIND_HOST": "127.0.0.1",
        "API_PORT": "8000",
        "BUSINESS_TIMEZONE": "Europe/Warsaw",
        "DATABASE_URL": "postgresql+psycopg://invented:private@127.0.0.1/invented",
        "LOG_LEVEL": "DEBUG",
    }
    saved = sys.modules.pop("config.config", None)
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    importlib.import_module("config.config")
    try:
        yield
    finally:
        sys.modules.pop("config.config", None)
        if saved is not None:
            sys.modules["config.config"] = saved
