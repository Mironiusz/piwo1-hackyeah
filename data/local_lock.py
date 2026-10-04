"""Retain local exclusion independently of database session lifetimes."""

import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


class ImportAlreadyRunningError(RuntimeError):
    """Refuse a contender immediately while import work still owns exclusion."""


ImportAlreadyRunning = ImportAlreadyRunningError


@dataclass
class LocalExclusion:
    """Keep the locked descriptor available to supervised Linux children."""

    stream: BinaryIO

    def fetch_descriptor(self) -> int:
        """Return the descriptor whose lifetime protects the workspace."""
        return self.stream.fileno()


@contextmanager
def apply_local_exclusion(root: Path) -> Iterator[LocalExclusion]:
    """Acquire a permanent lock inode without waiting or replacing it."""
    if not root.is_absolute() or root.is_symlink():
        raise ValueError("Import workspace must be an absolute real directory")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root / "admission.lock"
    if path.is_symlink():
        raise ValueError("Import lock must not be a symlink")
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(descriptor, "r+b") as stream:
        try:
            if sys.platform == "linux":
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif sys.platform == "win32":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                raise RuntimeError("Unsupported import execution platform")
        except (BlockingIOError, PermissionError):
            raise ImportAlreadyRunning("Another import still owns exclusion") from None
        if os.fstat(stream.fileno()).st_size == 0:
            stream.write(b"0")
            stream.flush()
            os.fsync(stream.fileno())
        yield LocalExclusion(stream)
