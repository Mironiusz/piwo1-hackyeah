"""Check safe process-boundary configuration reading and precedence."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.integration


def test_malformed_file_exits_without_values_or_traceback(tmp_path):
    """Reject literal-parser failures through the same safe startup boundary."""
    (tmp_path / ".env").write_text("DB_SERVICE_ACCOUNT_PASSWORD=private-first\nDB_SERVICE_ACCOUNT_PASSWORD=private-second\n", encoding="utf-8")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), environment.get("PYTHONPATH", "")))
    result = subprocess.run([sys.executable, "-m", "api"], cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=5, check=False)
    assert result.returncode == 1
    assert ".env" in result.stderr
    assert "private-" not in result.stderr and "Traceback" not in result.stderr


def test_trusted_proxy_that_trusts_everyone_exits_by_name_without_value(tmp_path):
    """Refuse the asterisk of the trusted proxy at startup, naming the entry and its file and printing no value."""
    (tmp_path / ".env.local").write_text("API_TRUSTED_PROXY_ADDRESSES=*\nDB_NAME=private-name\n", encoding="utf-8")
    environment = {key: value for key, value in os.environ.items() if key != "API_TRUSTED_PROXY_ADDRESSES"}
    environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), environment.get("PYTHONPATH", "")))
    result = subprocess.run([sys.executable, "-m", "api"], cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=5, check=False)
    assert result.returncode == 1
    assert "API_TRUSTED_PROXY_ADDRESSES (.env.local)" in result.stderr
    assert "*" not in result.stderr and "private-" not in result.stderr and "Traceback" not in result.stderr
