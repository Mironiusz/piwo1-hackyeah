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
    Uruchamia hook SessionStart tak, jak robi to narzędzie agentowe, z katalogiem projektu i katalogiem
    domowym podmienionymi na tymczasowe. Zwraca kontekst dodany do sesji.
    """
    environment = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir), "HOME": str(home_dir), "USERPROFILE": str(home_dir)}
    payload = json.dumps({"cwd": str(project_dir)})
    result = subprocess.run([sys.executable, str(CLAUDE_HOOK_PATH)], input=payload, text=True, capture_output=True, timeout=10, check=True, env=environment)

    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


def _make_skill(skills_dir: Path, name: str) -> None:
    """Zakłada w podanym katalogu skill o podanej nazwie z pustym plikiem SKILL.md."""
    (skills_dir / name).mkdir(parents=True)
    (skills_dir / name / "SKILL.md").write_text("", encoding="utf-8")


def _make_project(tmp_path: Path, session_context: str | None) -> Path:
    """Zakłada minimalny projekt: katalog standardów, jeden skill projektu i opcjonalny opis sesji."""
    project_dir = tmp_path / "projekt"
    (project_dir / "docs" / "standards").mkdir(parents=True)
    _make_skill(project_dir / ".claude" / "skills", "plan-shape")

    if session_context is not None:
        (project_dir / "agent_docs").mkdir()
        (project_dir / "agent_docs" / "session_context.md").write_text(session_context, encoding="utf-8")

    return project_dir


def test_hook_warns_when_personal_skill_shadows_project_skill(tmp_path: Path) -> None:
    """Pilnuje, że skill osobisty o nazwie skilla projektu daje ostrzeżenie ze ścieżką i nazwą."""
    project_dir = _make_project(tmp_path, "Opis projektu.")
    home_dir = tmp_path / "dom"
    _make_skill(home_dir / ".claude" / "skills", "plan-shape")
    _make_skill(home_dir / ".claude" / "skills", "inny-skill")

    context = _run_hook(project_dir, home_dir)

    assert "UWAGA: skille osobiste przykrywają skille projektu" in context
    assert "plan-shape" in context
    assert "inny-skill" not in context


def test_hook_is_silent_about_collisions_when_names_differ(tmp_path: Path) -> None:
    """Pilnuje, że bez wspólnej nazwy hook nie ostrzega, a opis projektu trafia do kontekstu dosłownie."""
    project_dir = _make_project(tmp_path, "Opis projektu.\n")
    home_dir = tmp_path / "dom"
    _make_skill(home_dir / ".claude" / "skills", "inny-skill")

    context = _run_hook(project_dir, home_dir)

    assert "UWAGA" not in context
    assert context.startswith("Opis projektu.")


def test_hook_says_when_session_context_is_missing(tmp_path: Path) -> None:
    """Pilnuje, że brak opisu projektu jest nazwany wprost, zamiast zostać zastąpiony domysłem."""
    project_dir = _make_project(tmp_path, None)

    context = _run_hook(project_dir, tmp_path / "dom")

    assert context.startswith("Brak opisu projektu w agent_docs/session_context.md")


def test_codex_hook_is_identical_to_claude_hook() -> None:
    """Pilnuje, że wariant hooka dla Codeksa nie rozjedzie się z wariantem dla Claude Code."""
    assert CODEX_HOOK_PATH.read_bytes() == CLAUDE_HOOK_PATH.read_bytes()
