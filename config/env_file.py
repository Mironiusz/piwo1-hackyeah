"""Parse environment entries without executing shell syntax."""

import re

ENTRY_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class EnvironmentFileError(ValueError):
    """Report an invalid environment file without exposing its values."""


def build_environment_values(text: str) -> dict[str, str]:
    """Build a unique key map from plain environment entries."""
    values: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not ENTRY_PATTERN.fullmatch(key):
            raise EnvironmentFileError(f"Invalid environment entry at line {number}")
        if key in values:
            raise EnvironmentFileError(f"Duplicate environment key {key}")
        value = value.strip()
        if value.startswith(("'", '"')):
            if len(value) < 2 or value[-1] != value[0]:
                raise EnvironmentFileError(f"Unmatched quote for {key}")
            value = value[1:-1]
        values[key] = value
    return values
