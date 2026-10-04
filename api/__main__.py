"""Launch one API process with the shared configuration and logger."""

import sys

import uvicorn

from config.settings import ConfigurationError


def main() -> None:
    """Start the API without access logs, schema changes or imported data."""
    try:
        from config.config import API_BIND_HOST, API_PORT
        from config.logging import apply_logging_configuration

        apply_logging_configuration()
    except ConfigurationError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from None
    uvicorn.run("api.app:build_app", host=API_BIND_HOST, port=API_PORT, workers=1, factory=True, log_config=None, access_log=False)


if __name__ == "__main__":
    main()
