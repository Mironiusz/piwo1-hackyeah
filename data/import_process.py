"""Supervise private-file writers while preserving exclusion across crashes."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from common_time import Deadline, DeadlineExpiredError, fetch_monotonic_seconds, resolve_remaining_milliseconds
from data.import_workspace import ImportWorkspaceUnconfirmed, WorkspaceLease, apply_journal_write


class ImportProcessFailedError(RuntimeError):
    """Report a completed tool failure without exposing arguments or output."""


def fetch_activity_completion(path: Path) -> bool:
    """Prove all compliant Linux writers released their inherited descriptor."""
    import fcntl

    descriptor = os.open(path, os.O_RDWR | os.O_NOFOLLOW)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True
    finally:
        os.close(descriptor)


def apply_linux_process(lease: WorkspaceLease, arguments: list[str], deadline: Deadline) -> int:
    """Contain a compliant tool group and wait for every inherited writer."""
    import fcntl

    path = lease.run_directory / "activity.lock"
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        process = subprocess.Popen(
            arguments,
            cwd=lease.workspace,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            start_new_session=True,
            pass_fds=(lease.exclusion.fetch_descriptor(), descriptor),
        )
    finally:
        os.close(descriptor)
    try:
        while process.poll() is None or not fetch_activity_completion(path):
            resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
            time.sleep(0.05)
    except (DeadlineExpiredError, KeyboardInterrupt):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            if not fetch_activity_completion(path):
                raise ImportWorkspaceUnconfirmed("Import process containment is unconfirmed") from None
        while process.poll() is None or not fetch_activity_completion(path):
            time.sleep(0.05)
        process.wait()
        raise
    return process.wait()


def apply_windows_process(lease: WorkspaceLease, arguments: list[str], deadline: Deadline) -> int:
    """Contain a Windows writer tree before its first instruction executes."""
    from data.windows_job import WindowsJob, fetch_active_processes

    name = f"Global\\piwo1-import-{lease.journal.run_id}"
    lease.journal.windows_job_name = name
    apply_journal_write(lease.run_directory / "journal.json", lease.journal)
    job = WindowsJob.apply_creation(name)
    lease.windows_job = job
    try:
        process = job.apply_process_start(arguments, str(lease.workspace))
    except BaseException:
        job.apply_close()
        lease.windows_job = None
        raise
    expired = False
    try:
        result = job.fetch_process_exit(process)
        while result is None or fetch_active_processes(job.kernel, job.handle) != 0:
            try:
                if not expired:
                    resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
            except DeadlineExpiredError:
                expired = True
                job.apply_termination()
            time.sleep(0.05)
            result = job.fetch_process_exit(process)
        if expired:
            raise DeadlineExpiredError("Import process deadline expired")
        return result
    finally:
        job.kernel.CloseHandle(process)
        job.apply_close()
        lease.windows_job = None


def apply_import_process(lease: WorkspaceLease, arguments: list[str], deadline: Deadline) -> None:
    """Run an explicit executable without leaking tool output into shared logs."""
    if not lease.active or not arguments or not Path(arguments[0]).is_absolute():
        raise ImportWorkspaceUnconfirmed("Import process requires an admitted workspace and absolute executable")
    resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
    if sys.platform == "linux":
        result = apply_linux_process(lease, arguments, deadline)
    elif sys.platform == "win32":
        result = apply_windows_process(lease, arguments, deadline)
    else:
        raise ImportWorkspaceUnconfirmed("Unsupported import process platform")
    if result != 0:
        raise ImportProcessFailedError("Import process failed")
