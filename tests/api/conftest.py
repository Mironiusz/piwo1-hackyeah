"""Provide invented runtime settings only for API integration tests."""

import pytest

from tests.common_runtime_settings import apply_invented_runtime_settings


@pytest.fixture
def _runtime_settings(monkeypatch: pytest.MonkeyPatch):
    """Load valid invented configuration and restore module state afterwards."""
    with apply_invented_runtime_settings(monkeypatch):
        yield
