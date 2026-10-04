"""Check shared administrative logging and redacted failure results."""

import importlib
import sys
from pathlib import Path

import pytest

from service.administrative import apply_administrative_run

pytestmark = pytest.mark.integration


@pytest.fixture
def administrative_settings(monkeypatch):
    """Provide invented runtime values without leaking changes to other tests."""
    previous = sys.modules.pop("config.config", None)
    for key, value in {
        "APP_ENVIRONMENT": "local",
        "API_BIND_HOST": "127.0.0.1",
        "API_PORT": "8000",
        "BUSINESS_TIMEZONE": "Europe/Warsaw",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "invented",
        "DB_SERVICE_ACCOUNT_NAME": "invented",
        "DB_SERVICE_ACCOUNT_PASSWORD": "invented",
        "SESSION_SIGNING_KEY": "invented-session-signing-key-of-32",
        "VOTER_HASH_KEY": "invented-voter-hash-key-of-32-chars",
        "API_TRUSTED_PROXY_ADDRESSES": "",
        "ROUTING_SERVICE_URL": "http://routing:8002",
        "ROUTING_DATA_DIR": str(Path(__file__).resolve().parent / "invented_routing_data"),
    }.items():
        monkeypatch.setenv(key, value)
    importlib.invalidate_caches()
    yield
    sys.modules.pop("config.config", None)
    if previous is not None:
        sys.modules["config.config"] = previous


@pytest.mark.usefixtures("administrative_settings")
def test_action_has_scope_and_success_exit(capsys):
    """Use the shared logger for one explicit synchronous action."""
    assert apply_administrative_run("scratch", lambda: 0) == 0
    output = capsys.readouterr().out
    assert "request_id=" in output and "operation=scratch" in output and "exit_code=0" in output


@pytest.mark.usefixtures("administrative_settings")
def test_action_failure_keeps_protected_values_out_of_logs(capsys):
    """Keep traceback locations while hiding callback exception text."""

    def apply_failure():
        """Raise an invented sensitive-looking value."""
        raise ValueError("private-admin-value")

    assert apply_administrative_run("scratch", apply_failure) == 1
    output = capsys.readouterr().out
    assert "private-admin-value" not in output
    assert "Traceback" in output
