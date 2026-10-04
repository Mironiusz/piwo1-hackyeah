"""
Launch one API process with the shared configuration and logger.

The address of the person behind the proxy reaches the request only from the proxy named in `API_TRUSTED_PROXY_ADDRESSES`:
uvicorn then takes the rightmost untrusted entry of X-Forwarded-For, and with no trusted proxy the peer of the connection is
the person. The list is passed explicitly, so uvicorn never falls back to `FORWARDED_ALLOW_IPS` or to the loopback
addresses (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-16).
"""

import sys

import uvicorn

from config.settings import ConfigurationError


def main() -> None:
    """Start the API without access logs, schema changes or imported data, trusting X-Forwarded-For only from the configured proxy."""
    try:
        from config.config import API_BIND_HOST, API_PORT, API_TRUSTED_PROXY_ADDRESSES
        from config.logging import apply_logging_configuration

        apply_logging_configuration()
    except ConfigurationError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from None
    uvicorn.run(
        "api.app:build_app",
        host=API_BIND_HOST,
        port=API_PORT,
        workers=1,
        factory=True,
        log_config=None,
        access_log=False,
        proxy_headers=True,
        forwarded_allow_ips=list(API_TRUSTED_PROXY_ADDRESSES),
    )


if __name__ == "__main__":
    main()
