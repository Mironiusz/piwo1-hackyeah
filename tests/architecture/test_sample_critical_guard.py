"""Proves the critical collection guard stops writes before fixtures run."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("configuration", ["target", "absent", "invalid", "local"])
@pytest.mark.parametrize("collect_only", [False, True])
def test_critical_selection_requires_validated_local_configuration(configuration: str, collect_only: bool, tmp_path: Path) -> None:
    """Uses invented configuration and a sentinel instead of a real database."""
    shutil.copyfile(ROOT_DIR / "tests" / "conftest.py", tmp_path / "conftest.py")
    config = tmp_path / "config"
    config.mkdir()
    (config / "__init__.py").write_text("", encoding="utf-8")
    if configuration != "absent":
        content = 'raise ValueError("invented invalid settings")\n' if configuration == "invalid" else f'APP_ENVIRONMENT = "{configuration}"\n'
        (config / "config.py").write_text(content, encoding="utf-8")
    sentinel = tmp_path / "write-sentinel"
    test_path = tmp_path / "test_guard_probe.py"
    test_path.write_text(
        'from pathlib import Path\nimport pytest\n\n@pytest.fixture\ndef durable_write():\n    Path("write-sentinel").write_text("invented write")\n\n@pytest.mark.critical\ndef test_write(durable_write):\n    assert True\n',
        encoding="utf-8",
    )
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(test_path)]
    if collect_only:
        command.append("--collect-only")
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join((str(tmp_path), str(ROOT_DIR), os.environ.get("PYTHONPATH", "")))}
    result = subprocess.run(command, cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=20, check=False)
    assert result.returncode == (0 if configuration == "local" else 4), result.stdout + result.stderr
    assert sentinel.exists() == (configuration == "local" and not collect_only)
