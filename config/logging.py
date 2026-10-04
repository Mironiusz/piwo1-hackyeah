"""Configure one privacy-preserving log hierarchy and run scope."""

import logging
import re
import sys
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from types import TracebackType
from typing import override
from uuid import uuid4

LOGGER_ROOT = "piwo1-hackyeah"
REQUEST_ID = ContextVar("request_id", default="-")
REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,128}")


class RequestScopeFilter(logging.Filter):
    """Attach the current request or administrative scope to each record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Keep the entry and attach only the sanitized scope identifier."""
        record.request_id = REQUEST_ID.get()
        return True


class DiagnosticFormatter(logging.Formatter):
    """Keep traceback locations without exception text or source-line values."""

    @override
    def formatException(self, exc_info: tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None]) -> str:
        """Render all stack frames while excluding values and chained messages."""
        frames = traceback.extract_tb(exc_info[2])
        locations = [f"  {Path(frame.filename).name}:{frame.lineno} in {frame.name}" for frame in frames]
        return "Traceback (values redacted):\n" + "\n".join(locations) + "\nException details redacted"


def apply_logging_configuration() -> None:
    """Install the single application stdout handler and silence foreign logs."""
    from config.config import LOG_LEVEL

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(logging.NullHandler())
    root.setLevel(logging.CRITICAL + 1)
    logger = logging.getLogger(LOGGER_ROOT)
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestScopeFilter())
    handler.setFormatter(DiagnosticFormatter("%(levelname)s request_id=%(request_id)s %(message)s"))
    logger.addHandler(handler)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy", "httpx", "httpcore", "psycopg"):
        foreign = logging.getLogger(name)
        foreign.handlers.clear()
        foreign.addHandler(logging.NullHandler())
        foreign.propagate = False
        foreign.setLevel(logging.CRITICAL + 1)


def fetch_logger(name: str) -> logging.Logger:
    """Return a logger in the application's single hierarchy."""
    application = logging.getLogger(LOGGER_ROOT)
    application.propagate = False
    if not application.handlers:
        application.addHandler(logging.NullHandler())
    return logging.getLogger(f"{LOGGER_ROOT}.{name}")


def build_request_id(candidate: str | None) -> str:
    """Keep a safe caller identifier or generate a fresh correlation value."""
    if candidate is not None and REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return uuid4().hex


@contextmanager
def apply_log_scope(request_id: str) -> Iterator[None]:
    """Apply one sanitized scope and restore the previous context afterwards."""
    token = REQUEST_ID.set(build_request_id(request_id))
    try:
        yield
    finally:
        REQUEST_ID.reset(token)
