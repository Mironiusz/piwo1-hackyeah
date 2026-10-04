"""Exercise compliant local tools with actual inherited file descriptors."""

import sys

import pytest

from common_time import DeadlineExpiredError, build_deadline, fetch_monotonic_seconds
from data.import_process import ImportProcessFailedError, apply_import_process
from data.import_workspace import apply_workspace_exclusion, apply_workspace_recovery

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux descriptor lifetime integration")


def test_successful_tool_creates_private_file(tmp_path):
    """Run a non-shell tool in the admitted private directory."""
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        apply_import_process(lease, [sys.executable, "-c", "from pathlib import Path; Path('scratch').write_text('invented')"], build_deadline(3, fetch_monotonic_seconds()))
        assert (lease.workspace / "scratch").read_text() == "invented"


def test_failure_does_not_expose_arguments(tmp_path):
    """Return only a safe condition after a nonzero tool exit."""
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        with pytest.raises(ImportProcessFailedError) as error:
            apply_import_process(lease, [sys.executable, "-c", "raise ValueError('private-value')"], build_deadline(3, fetch_monotonic_seconds()))
        assert "private-value" not in str(error.value)


def test_deadline_terminates_tool_before_return(tmp_path):
    """Confirm the tool has finished before reporting a spent deadline."""
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        with pytest.raises(DeadlineExpiredError):
            apply_import_process(lease, [sys.executable, "-c", "import time; time.sleep(30)"], build_deadline(0.15, fetch_monotonic_seconds()))


def test_forked_writer_outlives_parent_without_early_cleanup(tmp_path):
    """Wait for inherited writer descriptors after the direct child exits."""
    command = "import os,time; child=os.fork(); time.sleep(0.3) if child == 0 else None; os._exit(0)"
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        started = fetch_monotonic_seconds()
        apply_import_process(lease, [sys.executable, "-c", command], build_deadline(3, started))
        assert fetch_monotonic_seconds() - started >= 0.3
