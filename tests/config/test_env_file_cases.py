"""Verify literal environment parsing without shell execution."""

import pytest

from config.env_file import EnvironmentFileError, build_environment_values


def test_values_preserve_shell_text_without_expansion() -> None:
    """Keep quotes, substitutions and equals signs as literal data."""
    assert build_environment_values('A="$(echo secret)"\nB=x=y\nC=\n') == {"A": "$(echo secret)", "B": "x=y", "C": ""}


@pytest.mark.parametrize("content", ["A=1\nA=2", "not an entry", "A='unclosed"])
def test_invalid_file_is_refused_without_raw_content(content: str) -> None:
    """Refuse malformed or duplicate entries without echoing their values."""
    with pytest.raises(EnvironmentFileError) as caught:
        build_environment_values(content)
    assert content not in str(caught.value)
