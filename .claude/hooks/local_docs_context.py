import json
import os
import subprocess
import sys
from pathlib import Path

SESSION_CONTEXT_PATH = Path("agent_docs") / "session_context.md"
PROJECT_SKILL_DIRS = (Path(".claude") / "skills", Path(".agents") / "skills")
PERSONAL_SKILL_DIRS = (Path(".claude") / "skills", Path(".agents") / "skills", Path(".codex") / "skills")


def main() -> None:
    """Gives the agent a short context about the project, about the source of truth about the product and about the local standards."""
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
    """Reads the JSON passed by Claude Code on stdin."""
    raw_input = sys.stdin.read().strip()

    if not raw_input:
        return {}

    try:
        return json.loads(raw_input)
    except json.JSONDecodeError:
        return {}


def find_repo_root(cwd: Path) -> Path:
    """Finds the root of the Git repository or returns the current directory."""
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
    Builds a concise description of the sources of the repository rules: the project description from
    `agent_docs/session_context.md`, a warning about personal skills shadowing project skills and pointers
    to the standards map and to `agent_docs/`.
    """
    candidates = [
        ("standards map", standards_dir / "README.md"),
        ("deliberately deferred decisions", standards_dir / "decision_registry.md"),
    ]

    lines = [read_session_context(root)]
    lines.extend(build_skill_collision_warning(root, Path.home()))

    lines.extend(
        [
            "Local standards are in docs/standards. Read the full files only when the current task concerns a given area.",
            "",
            "Start with the map:",
        ]
    )

    for label, path in candidates:
        if path.is_file():
            lines.append(f"- {label}: {display_path(root, path)}")

    agent_docs_dir = root / "agent_docs"

    if agent_docs_dir.is_dir():
        lines.append("")
        lines.append("The repository also has agent_docs/ - the task chain workflow and the durable memory of decisions per code unit.")
        lines.append("Open it only when the task requires it:")

        agent_docs_candidates = [
            ("workflow seed -> shape -> PRD -> plan", agent_docs_dir / "ai_workflows" / "shape_prd_workflow.md"),
            ("memory convention", agent_docs_dir / "memory" / "README.md"),
        ]

        for label, path in agent_docs_candidates:
            if path.is_file():
                lines.append(f"- {label}: {display_path(root, path)}")

    return "\n".join(lines)


def read_session_context(root: Path) -> str:
    """
    Returns the project description from `agent_docs/session_context.md`. The project fills the file in when
    it is created from the template; when it is missing or empty, returns a sentence saying so instead of guessing a description.
    """
    path = root / SESSION_CONTEXT_PATH

    if path.is_file():
        content = path.read_text(encoding="utf-8").strip()

        if content:
            return content

    return f"No project description in {SESSION_CONTEXT_PATH.as_posix()} - fill it in according to README.md."


def discover_skill_names(skills_dir: Path) -> set[str]:
    """Returns the names of the skills, that is subdirectories with a SKILL.md file, in the given directory."""
    if not skills_dir.is_dir():
        return set()

    return {entry.name for entry in skills_dir.iterdir() if entry.is_dir() and (entry / "SKILL.md").is_file()}


def build_skill_collision_warning(root: Path, home: Path) -> list[str]:
    """
    Returns the warning lines when the user's personal directory holds a skill with the name of a project skill.

    With the same name the agentic tool loads the personal copy instead of the project one and does not say
    a word about it, so without this warning calling a skill by name runs different content than
    the one described by the repository standards. An empty list means no collision.
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
        "WARNING: personal skills shadow project skills with the same name. Calling one by name runs the personal copy:",
        *collisions,
        "Delete or rename the personal copies, and until then read the skill content directly from .claude/skills/<name>/SKILL.md.",
    ]


def display_path(root: Path, path: Path) -> str:
    """Returns the path relative to the repo root, if possible."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def print_json(payload: dict) -> None:
    """Prints JSON compliant with the Claude Code hooks contract."""
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
