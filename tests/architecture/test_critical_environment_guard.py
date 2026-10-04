"""Prove critical collection refuses target before scratch fixtures run."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("collect_only", [False, True])
def test_target_collection_never_runs_write_fixture(tmp_path, collect_only):
    """Use a sentinel to prove the refusal occurs before fixture setup."""
    (tmp_path / "conftest.py").write_text((ROOT / "tests" / "conftest.py").read_text(), encoding="utf-8")
    (tmp_path / "test_probe.py").write_text(
        'import pytest\nfrom pathlib import Path\n@pytest.fixture\ndef write():\n    Path(__file__).with_name("sentinel").touch()\n@pytest.mark.critical\ndef test_probe(write):\n    pass\n',
        encoding="utf-8",
    )
    environment = dict(
        os.environ,
        APP_ENVIRONMENT="target",
        API_BIND_HOST="127.0.0.1",
        API_PORT="8000",
        BUSINESS_TIMEZONE="Europe/Warsaw",
        DB_HOST="localhost",
        DB_PORT="5432",
        DB_NAME="invented",
        DB_SERVICE_ACCOUNT_NAME="invented",
        DB_SERVICE_ACCOUNT_PASSWORD="invented-private",
    )
    environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), environment.get("PYTHONPATH", "")))
    arguments = [sys.executable, "-m", "pytest", "-o", "addopts=-ra", str(tmp_path)]
    if collect_only:
        arguments.append("--collect-only")
    result = subprocess.run(arguments, cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode == 4, result.stdout + result.stderr
    assert not (tmp_path / "sentinel").exists()
    assert "invented-private" not in result.stdout + result.stderr
