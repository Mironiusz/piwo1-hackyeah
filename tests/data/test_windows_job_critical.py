"""Run native Windows containment acceptance only on a Windows executor."""

import sys

import pytest

from common_time import build_deadline, fetch_monotonic_seconds
from data.import_process import apply_import_process
from data.import_workspace import apply_workspace_exclusion, apply_workspace_recovery

pytestmark = [pytest.mark.critical, pytest.mark.skipif(sys.platform != "win32", reason="Requires native Windows Job Objects")]


def test_windows_tool_is_contained_and_reaped(tmp_path):
    """Execute a real contained child and confirm its private output."""
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        apply_import_process(lease, [sys.executable, "-c", "from pathlib import Path; Path('scratch').write_text('invented')"], build_deadline(5, fetch_monotonic_seconds()))
        assert (lease.workspace / "scratch").read_text() == "invented"
        assert lease.windows_job is None


def test_windows_deadline_terminates_the_contained_tree(tmp_path):
    """Confirm every descendant has exited before a deadline failure returns."""
    from common_time import DeadlineExpiredError
    from data.windows_job import fetch_job_completion

    command = "import subprocess,sys,time; subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)']); time.sleep(30)"
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        with pytest.raises(DeadlineExpiredError):
            apply_import_process(lease, [sys.executable, "-c", command], build_deadline(0.5, fetch_monotonic_seconds()))
        assert fetch_job_completion(lease.journal.windows_job_name)


def test_windows_owner_crash_is_recovered_on_next_manual_launch(tmp_path):
    """Check job destruction and private-file recovery after abrupt owner loss."""
    import subprocess
    import time

    from data.local_lock import ImportAlreadyRunning

    command = """
import sys
from pathlib import Path
from common_time import build_deadline, fetch_monotonic_seconds
from data.import_workspace import apply_workspace_exclusion, apply_workspace_recovery
from data.import_process import apply_import_process
with apply_workspace_exclusion(Path(sys.argv[1])) as lease:
    apply_workspace_recovery(lease, lambda identity: True)
    apply_import_process(lease, [sys.executable, '-c', "from pathlib import Path; import time; Path('ready').write_text('invented'); time.sleep(30)"], build_deadline(40, fetch_monotonic_seconds()))
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
        expires = fetch_monotonic_seconds() + 5
        while True:
            try:
                with apply_workspace_exclusion(tmp_path) as lease:
                    apply_workspace_recovery(lease, lambda identity: True)
                    assert not list(tmp_path.glob("*/work/ready"))
                break
            except ImportAlreadyRunning:
                assert fetch_monotonic_seconds() < expires
                time.sleep(0.05)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)
