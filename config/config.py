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
DB_HOST = _settings.DB_HOST
DB_PORT = _settings.DB_PORT
DB_NAME = _settings.DB_NAME
DB_SERVICE_ACCOUNT_NAME = _settings.DB_SERVICE_ACCOUNT_NAME
DB_SERVICE_ACCOUNT_PASSWORD = _settings.DB_SERVICE_ACCOUNT_PASSWORD
SESSION_SIGNING_KEY = _settings.SESSION_SIGNING_KEY
IMPORT_WORKSPACE_ROOT = _settings.IMPORT_WORKSPACE_ROOT
ROUTING_SERVICE_URL = _settings.ROUTING_SERVICE_URL
ROUTING_DATA_DIR = _settings.ROUTING_DATA_DIR
VALHALLA_TOOL_DIR = _settings.VALHALLA_TOOL_DIR
VALHALLA_CONFIG_TEMPLATE = _settings.VALHALLA_CONFIG_TEMPLATE
PUBLIC_TRANSPORT_ENABLED = _settings.PUBLIC_TRANSPORT_ENABLED
del _values, _settings, _path
