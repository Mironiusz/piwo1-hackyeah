from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CLAUDE_HOOK_PATH = ROOT_DIR / ".claude" / "hooks" / "local_docs_context.py"
CODEX_HOOK_PATH = ROOT_DIR / ".codex" / "hooks" / "local_docs_context.py"


def _run_hook(project_dir: Path, home_dir: Path) -> str:
    """
    Runs the SessionStart hook the way the agentic tool does it, with the project directory and the home
    directory swapped for temporary ones. Returns the context added to the session.
    """
    environment = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir), "HOME": str(home_dir), "USERPROFILE": str(home_dir)}
    payload = json.dumps({"cwd": str(project_dir)})
    result = subprocess.run([sys.executable, str(CLAUDE_HOOK_PATH)], input=payload, text=True, capture_output=True, timeout=10, check=True, env=environment)

    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


def _make_skill(skills_dir: Path, name: str) -> None:
    """Creates a skill with the given name in the given directory, with an empty SKILL.md file."""
    (skills_dir / name).mkdir(parents=True)
    (skills_dir / name / "SKILL.md").write_text("", encoding="utf-8")


def _make_project(tmp_path: Path, session_context: str | None) -> Path:
    """Creates a minimal project: the standards directory, one project skill and an optional session description."""
    project_dir = tmp_path / "project"
    (project_dir / "docs" / "standards").mkdir(parents=True)
    _make_skill(project_dir / ".claude" / "skills", "plan-shape")

    if session_context is not None:
        (project_dir / "agent_docs").mkdir()
        (project_dir / "agent_docs" / "session_context.md").write_text(session_context, encoding="utf-8")

    return project_dir


def test_hook_warns_when_personal_skill_shadows_project_skill(tmp_path: Path) -> None:
    """Ensures that a personal skill with the name of a project skill produces a warning with the path and the name."""
    project_dir = _make_project(tmp_path, "Project description.")
    home_dir = tmp_path / "home"
    _make_skill(home_dir / ".claude" / "skills", "plan-shape")
    _make_skill(home_dir / ".claude" / "skills", "other-skill")

    context = _run_hook(project_dir, home_dir)

    assert "WARNING: personal skills shadow project skills" in context
    assert "plan-shape" in context
    assert "other-skill" not in context


def test_hook_is_silent_about_collisions_when_names_differ(tmp_path: Path) -> None:
    """Ensures that without a shared name the hook does not warn, and the project description reaches the context verbatim."""
    project_dir = _make_project(tmp_path, "Project description.\n")
    home_dir = tmp_path / "home"
    _make_skill(home_dir / ".claude" / "skills", "other-skill")

    context = _run_hook(project_dir, home_dir)

    assert "WARNING" not in context
    assert context.startswith("Project description.")


def test_hook_says_when_session_context_is_missing(tmp_path: Path) -> None:
    """Ensures that a missing project description is named outright instead of being replaced with a guess."""
    project_dir = _make_project(tmp_path, None)

    context = _run_hook(project_dir, tmp_path / "home")

    assert context.startswith("No project description in agent_docs/session_context.md")


def test_codex_hook_is_identical_to_claude_hook() -> None:
    """Ensures that the hook variant for Codex does not diverge from the variant for Claude Code."""
    assert CODEX_HOOK_PATH.read_bytes() == CLAUDE_HOOK_PATH.read_bytes()
