"""Record crash recovery before allowing another import to acquire data."""

import os
import shutil
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from data.import_identity import BackendIdentity
from data.local_lock import ImportAlreadyRunning, LocalExclusion, apply_local_exclusion


class ImportWorkspaceUnconfirmedError(RuntimeError):
    """Refuse admission when old work or workspace cleanup is unconfirmed."""


ImportWorkspaceUnconfirmed = ImportWorkspaceUnconfirmedError


class BackendRecord(BaseModel):
    """Persist one strictly validated database identity without a connection URL."""

    model_config = ConfigDict(extra="forbid", strict=True)
    pid: int = Field(gt=0)
    backend_started_at: str
    database_oid: int = Field(gt=0)


class WorkspaceJournal(BaseModel):
    """Describe one pending run using only infrastructure recovery metadata."""

    model_config = ConfigDict(extra="forbid", strict=True)
    version: int = Field(default=1, ge=1, le=1)
    run_id: UUID
    backends: list[BackendRecord] = Field(default_factory=list)
    windows_job_name: str | None = None
    commit_attempted: bool = False


def apply_journal_write(path: Path, journal: WorkspaceJournal) -> None:
    """Durably replace the recovery record before the corresponding mutation."""
    temporary = path.with_suffix(".pending")
    with temporary.open("w", encoding="utf-8") as stream:
        stream.write(journal.model_dump_json())
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    if sys.platform == "linux":
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def fetch_journal(path: Path) -> WorkspaceJournal:
    """Read a bounded strict record without returning raw errors or values."""
    try:
        if path.is_symlink() or path.stat().st_size > 65536:
            raise ValueError("Invalid journal file")
        journal = WorkspaceJournal.model_validate_json(path.read_text(encoding="utf-8"))
        if str(journal.run_id) != path.parent.name:
            raise ValueError("Mismatched run identity")
        if journal.windows_job_name is not None and journal.windows_job_name != f"Global\\piwo1-import-{journal.run_id}":
            raise ValueError("Mismatched job identity")
        return journal
    except (OSError, ValueError, ValidationError):
        raise ImportWorkspaceUnconfirmed("Import recovery metadata is unconfirmed") from None


@dataclass
class WorkspaceLease:
    """Retain one private workspace and its persistent recovery ownership."""

    root: Path
    exclusion: LocalExclusion
    journal: WorkspaceJournal
    run_directory: Path
    recovery_directories: tuple[Path, ...]
    active: bool = False
    windows_job: object | None = None

    @property
    def workspace(self) -> Path:
        """Expose only this run's mutable private work directory."""
        if not self.active:
            raise ImportWorkspaceUnconfirmed("Import workspace is not admitted")
        return self.run_directory / "work"

    def apply_backend_registration(self, identity: BackendIdentity) -> None:
        """Record a backend before it can begin publication or source work."""
        self.journal.backends.append(BackendRecord(pid=identity.pid, backend_started_at=identity.backend_started_at.isoformat(), database_oid=identity.database_oid))
        apply_journal_write(self.run_directory / "journal.json", self.journal)

    def apply_commit_attempt_record(self) -> None:
        """Keep uncertain completion distinct after a process crash."""
        self.journal.commit_attempted = True
        apply_journal_write(self.run_directory / "journal.json", self.journal)


def apply_exact_workspace_cleanup(directory: Path) -> None:
    """Remove only a verified run's private work and exact metadata files."""
    if directory.is_symlink():
        raise ImportWorkspaceUnconfirmed("Import recovery directory is unconfirmed")
    allowed = {"work", "journal.json", "journal.pending", "activity.lock"}
    if any(entry.name not in allowed or entry.is_symlink() for entry in directory.iterdir()):
        raise ImportWorkspaceUnconfirmed("Import run contains unconfirmed entries")
    workspace = directory / "work"
    if workspace.is_symlink():
        raise ImportWorkspaceUnconfirmed("Import recovery workspace is unconfirmed")
    if workspace.exists():
        shutil.rmtree(workspace)
    for name in ("activity.lock", "journal.pending", "journal.json"):
        (directory / name).unlink(missing_ok=True)
    directory.rmdir()


def apply_workspace_recovery(lease: WorkspaceLease, database_work_finished: Callable[[BackendIdentity], bool]) -> None:
    """Clean registered old runs after process and database completion evidence."""
    from datetime import datetime

    for directory in lease.recovery_directories:
        if not (directory / "journal.json").exists():
            if any(entry.name != "journal.pending" or entry.is_symlink() for entry in directory.iterdir()):
                raise ImportWorkspaceUnconfirmed("Unregistered import work is unconfirmed")
            apply_exact_workspace_cleanup(directory)
            continue
        journal = fetch_journal(directory / "journal.json")
        if journal.windows_job_name is not None:
            from data.windows_job import fetch_job_completion

            if not fetch_job_completion(journal.windows_job_name):
                raise ImportAlreadyRunning("Previous import processes are still active")
        for record in journal.backends:
            try:
                started = datetime.fromisoformat(record.backend_started_at)
                if started.utcoffset() is None:
                    raise ValueError("Backend timestamp must be aware")
                identity = BackendIdentity(record.pid, started, record.database_oid)
                finished = database_work_finished(identity)
            except Exception:
                raise ImportWorkspaceUnconfirmed("Previous database work is unconfirmed") from None
            if not finished:
                raise ImportAlreadyRunning("Previous database work is still active")
        try:
            apply_exact_workspace_cleanup(directory)
        except OSError:
            raise ImportWorkspaceUnconfirmed("Previous import cleanup is incomplete") from None
    lease.active = True
    (lease.run_directory / "work").mkdir(mode=0o700)


@contextmanager
def apply_workspace_exclusion(root: Path) -> Iterator[WorkspaceLease]:
    """Keep the local lock while examining, recovering and cleaning one run."""
    with apply_local_exclusion(root) as exclusion:
        recovery: list[Path] = []
        for candidate in root.iterdir():
            if candidate.name == "admission.lock":
                continue
            try:
                if candidate.is_symlink() or not candidate.is_dir() or str(UUID(candidate.name)) != candidate.name:
                    raise ValueError("Unexpected workspace entry")
            except ValueError:
                raise ImportWorkspaceUnconfirmed("Import root contains unconfirmed recovery metadata") from None
            recovery.append(candidate)
        identifier = uuid4()
        directory = root / str(identifier)
        directory.mkdir(mode=0o700)
        journal = WorkspaceJournal(run_id=identifier)
        apply_journal_write(directory / "journal.json", journal)
        lease = WorkspaceLease(root, exclusion, journal, directory, tuple(recovery))
        try:
            yield lease
        finally:
            lease.active = False
