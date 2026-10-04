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
