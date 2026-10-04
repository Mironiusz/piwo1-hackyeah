"""Check templates and runtime settings without importing environment values."""

from pathlib import Path

from config.env_file import build_environment_values
from config.settings import ENVIRONMENT_ENTRY_FILES, Settings

ROOT = Path(__file__).resolve().parents[2]


def test_every_setting_has_one_matching_template_entry():
    """Require each configured name in its documented local template layer."""
    observed = {}
    for filename in (".env", ".env.local", ".env.priv"):
        for key in build_environment_values((ROOT / (filename + ".example")).read_text()):
            assert key not in observed
            observed[key] = filename
    assert observed == ENVIRONMENT_ENTRY_FILES
    assert set(Settings.model_fields) <= set(observed)
