"""
Guards the environment contract of `docs/standards/standard_config.md`.

Every entry of a template has a record in the section Environment entries of that standard, every template holds only
empty to-fill-in markers and no value, and every entry of a template is present in the local file of the same kind
where that file exists. A local file is never committed, so on a machine without it the last check is skipped with the
name of the file; the test reads the names of the entries and never prints their values.
"""

from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_STANDARD_PATH = ROOT_DIR / "docs" / "standards" / "standard_config.md"
TEMPLATE_LOCAL_FILES = {
    ".env.example": ".env",
    ".env.local.example": ".env.local",
    ".env.priv.example": ".env.priv",
}
ENTRIES_SECTION_START = "## Environment entries"
NEXT_SECTION_START = "\n## "


def fetch_entries(path: Path) -> dict[str, str]:
    """Reads the entries of an environment file as names and values, skipping empty lines."""
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            name, separator, value = line.partition("=")
            assert separator, f"{path.name}: a line without '=' in an environment file"
            entries[name.strip()] = value.strip()
    return entries


def fetch_existing_templates() -> list[Path]:
    """Reads which of the three templates exist in the repository root."""
    return [ROOT_DIR / template for template in TEMPLATE_LOCAL_FILES if (ROOT_DIR / template).exists()]


def fetch_entries_section() -> str:
    """Reads the section Environment entries of the configuration standard."""
    text = CONFIG_STANDARD_PATH.read_text(encoding="utf-8")
    start = text.index(ENTRIES_SECTION_START)
    end = text.find(NEXT_SECTION_START, start + len(ENTRIES_SECTION_START))
    return text[start:] if end == -1 else text[start:end]


def test_every_template_entry_has_a_record_in_the_configuration_standard() -> None:
    """Each entry of each template is named in the section Environment entries of `docs/standards/standard_config.md`."""
    section = fetch_entries_section()
    for template in fetch_existing_templates():
        for name in fetch_entries(template):
            assert f"`{name}`" in section, f"{template.name}: {name} has no record in the section Environment entries"


def test_every_template_holds_only_empty_markers() -> None:
    """No template carries a value, so a copied and unfilled template stops the start with the name of the entry."""
    for template in fetch_existing_templates():
        for name, value in fetch_entries(template).items():
            assert value == "", f"{template.name}: {name} carries a value instead of an empty marker"


@pytest.mark.parametrize("template_name", list(TEMPLATE_LOCAL_FILES))
def test_every_template_entry_is_present_in_its_local_file(template_name: str) -> None:
    """Each entry of a template is present in its local file, where that file exists on this machine."""
    template = ROOT_DIR / template_name
    local_file = ROOT_DIR / TEMPLATE_LOCAL_FILES[template_name]
    if not template.exists():
        pytest.skip(f"{template_name} does not exist in the repository")
    if not local_file.exists():
        pytest.skip(f"{local_file.name} does not exist on this machine; the contract is checked where it does")
    missing = sorted(set(fetch_entries(template)) - set(fetch_entries(local_file)))
    assert not missing, f"{local_file.name} lacks the entries {missing} of {template_name}"
