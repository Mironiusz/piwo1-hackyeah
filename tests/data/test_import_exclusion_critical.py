"""Exercise local and PostgreSQL admission and stale guard refusal."""

import subprocess
import sys
import time

import pytest
from sqlalchemy import text

from common_time import build_deadline, fetch_monotonic_seconds
from data.locks import ImportAlreadyRunning, ImportLeaseLost, apply_import_exclusion
from data.publication import apply_publication

pytestmark = pytest.mark.critical


def test_second_database_contender_is_refused_without_wait(scratch_database, tmp_path):
    """Use separate local roots to independently verify database admission."""
    _owner, service = scratch_database
    with apply_import_exclusion(service, tmp_path / "first"), pytest.raises(ImportAlreadyRunning), apply_import_exclusion(service, tmp_path / "second"):
        pytest.fail("Overlap was admitted")
    with apply_import_exclusion(service, tmp_path / "second"):
        pass


def test_lost_guard_never_reacquires_for_publication(scratch_database, tmp_path):
    """Refuse the callback after the original guard backend is terminated."""
    owner, service = scratch_database
    with apply_import_exclusion(service, tmp_path) as lease:
        with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.execute(text("SELECT pg_terminate_backend(:pid)"), {"pid": lease.identity.pid})
        with pytest.raises(ImportLeaseLost):
            apply_publication(lease, build_deadline(2, fetch_monotonic_seconds()), lambda connection: pytest.fail("Lost lease wrote"))


def apply_owner_crash(tmp_path, child_seconds: float, deadline_seconds: float) -> None:
    """Start an admitted import owner whose contained child writes an invented file and keeps running, then kill only the owner."""
    command = f"""
import sys
from pathlib import Path
from common_time import build_deadline, fetch_monotonic_seconds
from data.engine import build_import_engine
from data.locks import apply_import_exclusion
from data.import_process import apply_import_process
engine = build_import_engine(5000)
with apply_import_exclusion(engine, Path(sys.argv[1])) as lease:
    apply_import_process(lease.workspace_lease, [sys.executable, '-c', "from pathlib import Path; import time; Path('ready').write_text('invented'); time.sleep({child_seconds})"], build_deadline({deadline_seconds}, fetch_monotonic_seconds()))
"""
    process = subprocess.Popen([sys.executable, "-c", command, str(tmp_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        expires = fetch_monotonic_seconds() + 5
        while not list(tmp_path.glob("*/work/ready")) and fetch_monotonic_seconds() < expires:
            assert process.poll() is None
            time.sleep(0.01)
        assert list(tmp_path.glob("*/work/ready"))
        process.kill()
        process.wait(timeout=3)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)


@pytest.mark.skipif(sys.platform != "linux", reason="Only Linux lets a contained writer outlive its owner")
def test_next_manual_launch_recovers_after_owner_crash(scratch_database, tmp_path):
    """Keep admission closed through an orphan writer, then recover private files."""
    _owner, service = scratch_database
    apply_owner_crash(tmp_path, 1, 5)
    with pytest.raises(ImportAlreadyRunning), apply_import_exclusion(service, tmp_path):
        pytest.fail("Orphan writer was ignored")
    time.sleep(1.1)
    with apply_import_exclusion(service, tmp_path) as lease:
        assert not list(tmp_path.glob("*/work/ready"))
        assert lease.workspace_lease.workspace.exists()


@pytest.mark.skipif(sys.platform != "win32", reason="Requires native Windows Job Objects")
def test_next_manual_launch_recovers_after_windows_owner_crash(scratch_database, tmp_path):
    """Lose the owner and its database guard together; its job ends the long writer, and the next launch recovers before admission."""
    _owner, service = scratch_database
    apply_owner_crash(tmp_path, 30, 40)
    expires = fetch_monotonic_seconds() + 10
    while True:
        try:
            with apply_import_exclusion(service, tmp_path) as lease:
                assert not list(tmp_path.glob("*/work/ready"))
                assert lease.workspace_lease.workspace.exists()
            break
        except ImportAlreadyRunning:
            assert fetch_monotonic_seconds() < expires, "The contained writer outlived its crashed owner"
            time.sleep(0.05)
