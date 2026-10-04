"""Read the one runtime environment and expose validated constants."""

import os
from pathlib import Path

from config.env_file import EnvironmentFileError, build_environment_values
from config.settings import ConfigurationError, Settings

_values: dict[str, str] = {}
for _path in (Path(".env"), Path(".env.local")):
    if _path.exists():
        try:
            _values.update(build_environment_values(_path.read_text(encoding="utf-8")))
        except (OSError, EnvironmentFileError):
            raise ConfigurationError(f"Invalid configuration file: {_path.name}") from None
_values.update(os.environ)
_settings = Settings(**_values)
APP_ENVIRONMENT = _settings.APP_ENVIRONMENT
API_BIND_HOST = _settings.API_BIND_HOST
API_PORT = _settings.API_PORT
BUSINESS_TIMEZONE = _settings.BUSINESS_TIMEZONE
LOG_LEVEL = _settings.LOG_LEVEL
DATABASE_URL = _settings.DATABASE_URL
IMPORT_WORKSPACE_ROOT = _settings.IMPORT_WORKSPACE_ROOT
del _values, _settings, _path
