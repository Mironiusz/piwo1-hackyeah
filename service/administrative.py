"""Apply shared configuration and correlation to explicit administrative work."""

import sys
from collections.abc import Callable

from config.logging import apply_log_scope, apply_logging_configuration, build_request_id, fetch_logger
from config.settings import ConfigurationError


def apply_administrative_run(operation: str, action: Callable[[], int]) -> int:
    """Run one explicit action with shared logs and a safe failure exit."""
    with apply_log_scope(build_request_id(None)):
        try:
            apply_logging_configuration()
            logger = fetch_logger(__name__)
            logger.info("Administrative run started operation=%s", operation)
            result = action()
            logger.info("Administrative run completed operation=%s exit_code=%s", operation, result)
            return result
        except ConfigurationError as failure:
            print(str(failure), file=sys.stderr)
            return 1
        except Exception:
            fetch_logger(__name__).exception("Administrative run failed")
            return 1
