"""Provide invented runtime settings for the rules that read the business zone or the logger through the configuration facade."""

import pytest

from tests.common_runtime_settings import apply_invented_runtime_settings


@pytest.fixture
def runtime_settings(monkeypatch: pytest.MonkeyPatch):
    """Load valid invented configuration and restore module state afterwards."""
    with apply_invented_runtime_settings(monkeypatch):
        yield
