"""Check strict recovery ownership and refusal without destructive guessing."""

from uuid import uuid4

import pytest

from data.import_workspace import ImportWorkspaceUnconfirmed, WorkspaceJournal, apply_exact_workspace_cleanup, apply_journal_write, apply_workspace_exclusion, apply_workspace_recovery, fetch_journal
from data.local_lock import ImportAlreadyRunning, apply_local_exclusion


def test_contender_is_refused_until_local_owner_closes(tmp_path):
    """Refuse immediately while retaining a stable lock inode."""
    with apply_local_exclusion(tmp_path):
        inode = (tmp_path / "admission.lock").stat().st_ino
        with pytest.raises(ImportAlreadyRunning), apply_local_exclusion(tmp_path):
            pytest.fail("Contender was admitted")
    with apply_local_exclusion(tmp_path):
        assert (tmp_path / "admission.lock").stat().st_ino == inode


def test_recovery_removes_private_work_before_new_admission(tmp_path):
    """Recover an abandoned registered run without deleting unrelated files."""
    with apply_workspace_exclusion(tmp_path) as abandoned:
        apply_workspace_recovery(abandoned, lambda identity: True)
        (abandoned.workspace / "scratch").write_text("invented", encoding="utf-8")
        old = abandoned.run_directory
    with apply_workspace_exclusion(tmp_path) as current:
        apply_workspace_recovery(current, lambda identity: True)
        assert not old.exists()
        assert current.workspace.is_dir()


def test_unexpected_entry_preserves_journal_and_work(tmp_path):
    """Keep recovery evidence intact when an entry has no known contract."""
    with apply_workspace_exclusion(tmp_path) as lease:
        apply_workspace_recovery(lease, lambda identity: True)
        (lease.run_directory / "unexpected").write_text("invented", encoding="utf-8")
        with pytest.raises(ImportWorkspaceUnconfirmed):
            apply_exact_workspace_cleanup(lease.run_directory)
        assert (lease.run_directory / "journal.json").exists()
        assert lease.workspace.exists()


def test_corrupt_job_identity_is_refused(tmp_path):
    """Never query a job that does not belong to the recorded run."""
    identifier = uuid4()
    directory = tmp_path / str(identifier)
    directory.mkdir()
    apply_journal_write(directory / "journal.json", WorkspaceJournal(run_id=identifier, windows_job_name="unrelated"))
    with pytest.raises(ImportWorkspaceUnconfirmed):
        fetch_journal(directory / "journal.json")
