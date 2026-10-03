import json
import os
import subprocess
import sys
from pathlib import Path

SESSION_CONTEXT_PATH = Path("agent_docs") / "session_context.md"
PROJECT_SKILL_DIRS = (Path(".claude") / "skills", Path(".agents") / "skills")
PERSONAL_SKILL_DIRS = (Path(".claude") / "skills", Path(".agents") / "skills", Path(".codex") / "skills")


def main() -> None:
    """Dodaje agentowi krótki kontekst o projekcie, o źródle prawdy o produkcie i o lokalnych standardach."""
    payload = read_payload()
    cwd = Path(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    root = find_repo_root(cwd)
    standards_dir = root / "docs" / "standards"

    if not standards_dir.is_dir():
        print_json({})
        return

    context = build_context(root, standards_dir)
    print_json({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}})


def read_payload() -> dict:
    """Czyta JSON przekazany przez Claude Code na stdin."""
    raw_input = sys.stdin.read().strip()

    if not raw_input:
        return {}

    try:
        return json.loads(raw_input)
    except json.JSONDecodeError:
        return {}


def find_repo_root(cwd: Path) -> Path:
    """Znajduje root repozytorium Git albo zwraca bieżący katalog."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")

    if project_dir:
        return Path(project_dir)

    try:
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(cwd), text=True, capture_output=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return cwd

    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())

    return cwd


def build_context(root: Path, standards_dir: Path) -> str:
    """
    Buduje zwięzły opis źródeł zasad repozytorium: opis projektu z `agent_docs/session_context.md`,
    ostrzeżenie o skillach osobistych przykrywających skille projektu i wskazania na mapę standardów
    oraz `agent_docs/`.
    """
    candidates = [
        ("mapa standardów", standards_dir / "README.md"),
        ("decyzje świadomie odroczone", standards_dir / "decision_registry.md"),
    ]

    lines = [read_session_context(root)]
    lines.extend(build_skill_collision_warning(root, Path.home()))

    lines.extend(
        [
            "Lokalne standardy są w docs/standards. Pełne pliki warto czytać dopiero, gdy bieżące zadanie dotyczy danego obszaru.",
            "",
            "Zacznij od mapy:",
        ]
    )

    for label, path in candidates:
        if path.is_file():
            lines.append(f"- {label}: {display_path(root, path)}")

    agent_docs_dir = root / "agent_docs"

    if agent_docs_dir.is_dir():
        lines.append("")
        lines.append("Repozytorium ma też agent_docs/ - workflow łańcucha zadania i trwałą pamięć decyzji per jednostka kodu.")
        lines.append("Otwórz dopiero, gdy zadanie tego wymaga:")

        agent_docs_candidates = [
            ("workflow seed -> shape -> PRD -> plan", agent_docs_dir / "ai_workflows" / "shape_prd_workflow.md"),
            ("konwencja memory", agent_docs_dir / "memory" / "README.md"),
        ]

        for label, path in agent_docs_candidates:
            if path.is_file():
                lines.append(f"- {label}: {display_path(root, path)}")

    return "\n".join(lines)


def read_session_context(root: Path) -> str:
    """
    Zwraca opis projektu z `agent_docs/session_context.md`. Plik wypełnia projekt przy zakładaniu
    z szablonu; gdy go brakuje albo jest pusty, zwraca zdanie, które o tym mówi, zamiast zgadywać opis.
    """
    path = root / SESSION_CONTEXT_PATH

    if path.is_file():
        content = path.read_text(encoding="utf-8").strip()

        if content:
            return content

    return f"Brak opisu projektu w {SESSION_CONTEXT_PATH.as_posix()} - uzupełnij go według README.md szablonu."


def discover_skill_names(skills_dir: Path) -> set[str]:
    """Zwraca nazwy skilli, czyli podkatalogów z plikiem SKILL.md, w podanym katalogu."""
    if not skills_dir.is_dir():
        return set()

    return {entry.name for entry in skills_dir.iterdir() if entry.is_dir() and (entry / "SKILL.md").is_file()}


def build_skill_collision_warning(root: Path, home: Path) -> list[str]:
    """
    Zwraca linie ostrzeżenia, gdy w katalogu osobistym użytkownika leży skill o nazwie skilla projektu.

    Przy tej samej nazwie narzędzie agentowe ładuje kopię osobistą zamiast projektowej i nie mówi
    o tym ani słowem, więc bez tego ostrzeżenia wywołanie skilla po nazwie uruchamia inną treść niż
    ta, którą opisują standardy repozytorium. Pusta lista znaczy brak kolizji.
    """
    project_skills: set[str] = set()

    for skills_dir in PROJECT_SKILL_DIRS:
        project_skills |= discover_skill_names(root / skills_dir)

    collisions = []

    for skills_dir in PERSONAL_SKILL_DIRS:
        personal_dir = home / skills_dir
        shared_names = sorted(project_skills & discover_skill_names(personal_dir))

        if shared_names:
            collisions.append(f"- {personal_dir}: {', '.join(shared_names)}")

    if not collisions:
        return []

    return [
        "",
        "UWAGA: skille osobiste przykrywają skille projektu o tej samej nazwie. Wywołanie po nazwie uruchomi kopię osobistą:",
        *collisions,
        "Usuń albo przemianuj kopie osobiste, a do tego czasu czytaj treść skilla wprost z .claude/skills/<nazwa>/SKILL.md.",
    ]


def display_path(root: Path, path: Path) -> str:
    """Zwraca ścieżkę względem root repo, jeśli to możliwe."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def print_json(payload: dict) -> None:
    """Wypisuje JSON zgodny z kontraktem hooków Claude Code."""
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
