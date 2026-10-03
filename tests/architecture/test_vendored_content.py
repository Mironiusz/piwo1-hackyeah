from __future__ import annotations

from pathlib import Path

from tests.architecture.common_vendored_content import (
    CLAUDE_AGENT_ROLE_DIRECTORY,
    SKILL_DIRECTORIES,
    VENDORED_AGENT_ROLE_NAMES,
    VENDORED_SKILL_NAMES,
    is_vendored_path,
)

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_every_vendored_skill_still_exists_on_both_sides() -> None:
    """
    Ensures that every skill on the vendored list is still installed in both skill directories.

    The exemption exists only for content the installer put here. An entry left after the skill was removed
    would quietly exempt from the gates whatever somebody later writes under the same name.
    """
    missing_skills = [
        f"{skills_directory}/{skill_name}"
        for skills_directory in SKILL_DIRECTORIES
        for skill_name in sorted(VENDORED_SKILL_NAMES)
        if not (ROOT_DIR / skills_directory / skill_name / "SKILL.md").is_file()
    ]

    assert not missing_skills, f"Vendored skills no longer installed - remove them from VENDORED_SKILL_NAMES: {missing_skills}"


def test_every_vendored_agent_role_still_exists() -> None:
    """
    Ensures that every agent role on the vendored list still has its definition in `.claude/agents/`, for the same
    reason as the test above.
    """
    missing_roles = [role_name for role_name in sorted(VENDORED_AGENT_ROLE_NAMES) if not (ROOT_DIR / CLAUDE_AGENT_ROLE_DIRECTORY / f"{role_name}.md").is_file()]

    assert not missing_roles, f"Vendored agent roles no longer installed - remove them from VENDORED_AGENT_ROLE_NAMES: {missing_roles}"


def test_is_vendored_path_covers_the_vendored_skill_on_both_sides() -> None:
    """Ensures that a file inside a vendored skill counts as third-party content in the Claude Code and the Codex copy alike."""
    assert is_vendored_path(".claude/skills/impeccable/SKILL.md")
    assert is_vendored_path(".agents/skills/impeccable/reference/adapt.md")


def test_is_vendored_path_covers_the_vendored_agent_role() -> None:
    """Ensures that the definition of a vendored agent role counts as third-party content."""
    assert is_vendored_path(".claude/agents/impeccable-documenter.md")


def test_is_vendored_path_leaves_the_team_content_in_the_gates() -> None:
    """
    Ensures that the exemption does not spread beyond the named entries: an own skill, an own agent role,
    a skill whose name only starts with the name of a vendored one and a project file next to the skill stay in the gates.
    """
    assert not is_vendored_path(".claude/skills/plan-shape/SKILL.md")
    assert not is_vendored_path(".claude/agents/dod-reviewer.md")
    assert not is_vendored_path(".claude/skills/impeccable-extra/SKILL.md")
    assert not is_vendored_path(".impeccable/briefs/route-result.md")
