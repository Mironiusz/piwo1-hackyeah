from __future__ import annotations

import difflib
import re
import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

PLAN_REFERENCE = "docs/standards/standard_agentic_workflow.md ch. 6.2"
CODEX_ONLY_SKILLS: frozenset[str] = frozenset()
"""
Skills allowed only on the Codex side. The set is empty and is to stay that way - the conditions for
adding an exception are described in standard_agentic_workflow.md ch. 6.1.
"""

CODEX_ROLE_INSTRUCTIONS_KEY = "developer_instructions"
FRONTMATTER_MARKER = "---"
AGENT_ROLE_REFERENCE = "docs/standards/standard_agentic_workflow.md ch. 6.4"

_NORMALIZATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^# (AGENTS|CLAUDE)\.md$"), "# <ROOT>.md"),
    (re.compile(r"(Codex|Claude Code) is to apply"), "<TOOL> is to apply"),
    (re.compile(r"\.claude/skills/[\w-]+/scripts/"), "scripts/"),
]

AGENT_ROLE_NORMALIZATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"via `Bash` or `PowerShell`|via the terminal"), "via <RUNNER>"),
]
"""
The only allowed difference between the role variant for Claude Code and the variant for Codex: the name
of the tool the role runs commands with. It is real, not cosmetic - on the Claude Code side the tools
are called `Bash` and `PowerShell`, and Codex does not know such names. Every other difference
is to be fixed in the content of the files, not hidden by adding a second item to this list.
"""


def _normalize_line(line: str, normalizations: list[tuple[re.Pattern[str], str]]) -> str:
    """
    Replaces known, intended differences (the tool name in the core, the path
    to a skill script, the name of the command runner in a role definition) with a common
    form, so that the diff sees only real divergences. Each rule on the normalization
    list is one deliberately allowed difference - adding another one
    is to be a decision, not an accident.
    """
    normalized = line

    for pattern, replacement in normalizations:
        normalized = pattern.sub(replacement, normalized)

    return normalized


def _normalized_lines(path: Path) -> list[str]:
    """
    Reads the file and returns the normalized lines. Path.read_text does universal
    translation of line endings to \\n, so CRLF versus LF is never a difference.
    """
    return [_normalize_line(line, _NORMALIZATIONS) for line in path.read_text(encoding="utf-8").splitlines()]


def _real_differences(name_a: str, lines_a: list[str], name_b: str, lines_b: list[str]) -> list[str]:
    """
    Returns descriptions of the real differences between two sets of lines after normalization.
    An empty list means full parity. Uses difflib instead of line-by-line
    positions, so that a section inserted or removed in one file does not
    shift the numbering and generate false differences for the rest of the file.
    """
    matcher = difflib.SequenceMatcher(a=lines_a, b=lines_b, autojunk=False)
    differences: list[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        differences.append(f"{name_a} line {i1 + 1}: {lines_a[i1:i2]!r}\n{name_b} line {j1 + 1}: {lines_b[j1:j2]!r}")

    return differences


def _assert_parity(path_a: Path, path_b: Path, pair_name: str) -> None:
    """
    Parity assertion for one pair of files, with a reference to the rollout plan
    for the list of allowed exceptions and the rationale of the test.
    """
    assert path_a.is_file(), f"Missing file {path_a} for the pair {pair_name}"
    assert path_b.is_file(), f"Missing file {path_b} for the pair {pair_name}"

    differences = _real_differences(path_a.name, _normalized_lines(path_a), path_b.name, _normalized_lines(path_b))
    assert not differences, f"The pair {pair_name} diverged beyond the allowed differences:\n" + "\n".join(differences) + f"\nSee {PLAN_REFERENCE} for the list of allowed exceptions."


def _strip_blank_edges(lines: list[str]) -> list[str]:
    """
    Cuts blank lines off the beginning and the end of the list. The markdown variant has a blank
    line after the frontmatter and at the end of the file, the TOML variant has none -
    that is a difference of format, not of content.
    """
    trimmed = list(lines)

    while trimmed and not trimmed[0].strip():
        trimmed.pop(0)

    while trimmed and not trimmed[-1].strip():
        trimmed.pop()

    return trimmed


def fetch_claude_role_instructions(path: Path) -> list[str]:
    """
    Reads the role definition on the Claude Code side and returns only the normalized
    instruction lines, without the frontmatter. The frontmatter carries the tool
    configuration (tool list, permission mode, turn limit), which has no
    counterpart on the Codex side and is not subject to parity.
    """
    lines = path.read_text(encoding="utf-8").splitlines()

    if lines and lines[0].strip() == FRONTMATTER_MARKER:
        closing_index = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == FRONTMATTER_MARKER)
        lines = lines[closing_index + 1 :]

    return [_normalize_line(line, AGENT_ROLE_NORMALIZATIONS) for line in _strip_blank_edges(lines)]


def fetch_codex_role_instructions(path: Path) -> list[str]:
    """
    Reads the role definition on the Codex side and returns the normalized lines
    of the `developer_instructions` key.

    The comparison goes by the value read by the parser, not by the raw text
    of the file: the value carries literal line-ending escape sequences, which
    the parser turns into real characters, while the raw text would show them as
    a difference against the markdown variant.
    """
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    instructions = document[CODEX_ROLE_INSTRUCTIONS_KEY]

    return [_normalize_line(line, AGENT_ROLE_NORMALIZATIONS) for line in _strip_blank_edges(instructions.splitlines())]


def _discover_skill_names(skills_dir: Path) -> set[str]:
    """
    Returns the names of the skills (subdirectories containing SKILL.md) in the given
    skills/ directory.
    """
    if not skills_dir.is_dir():
        return set()

    return {entry.name for entry in skills_dir.iterdir() if entry.is_dir() and (entry / "SKILL.md").is_file()}


def _discover_role_names(roles_dir: Path, suffix: str) -> set[str]:
    """
    Returns the names of the roles (files with the given extension) in the given role definition directory.
    """
    if not roles_dir.is_dir():
        return set()

    return {entry.stem for entry in roles_dir.iterdir() if entry.is_file() and entry.suffix == suffix}


def test_agents_and_claude_core_files_are_at_parity() -> None:
    """
    Ensures that AGENTS.md and CLAUDE.md do not diverge beyond the tool name -
    the same repo is to be read by Codex and Claude Code, so the rules must be
    identical.
    """
    _assert_parity(ROOT_DIR / "AGENTS.md", ROOT_DIR / "CLAUDE.md", "AGENTS.md / CLAUDE.md")


def test_every_local_skill_exists_in_both_claude_and_agents() -> None:
    """
    Ensures full parity outside the strict list of approved Codex-only
    skills and does not let the allowlist hide a dead entry or a copy
    also created on the Claude side.
    """
    claude_skills = _discover_skill_names(ROOT_DIR / ".claude" / "skills")
    agents_skills = _discover_skill_names(ROOT_DIR / ".agents" / "skills")

    only_in_claude = sorted(claude_skills - agents_skills)
    only_in_agents = sorted((agents_skills - claude_skills) - CODEX_ONLY_SKILLS)

    assert not only_in_claude, f"Skills exist only in .claude/skills/, missing in .agents/skills/: {only_in_claude}"
    assert not only_in_agents, f"Unknown skills exist only in .agents/skills/, missing in .claude/skills/: {only_in_agents}"
    assert agents_skills >= CODEX_ONLY_SKILLS, f"The Codex-only allowlist contains missing skills: {sorted(CODEX_ONLY_SKILLS - agents_skills)}"
    assert CODEX_ONLY_SKILLS.isdisjoint(claude_skills), f"A Codex-only skill has a disallowed copy in .claude/skills/: {sorted(CODEX_ONLY_SKILLS & claude_skills)}"


def test_every_paired_skill_is_at_parity() -> None:
    """
    Ensures that the content of every skill existing in both locations is
    identical apart from explicitly allowed differences, mainly paths to
    scripts.
    """
    claude_skills_dir = ROOT_DIR / ".claude" / "skills"
    agents_skills_dir = ROOT_DIR / ".agents" / "skills"

    shared_skills = sorted(_discover_skill_names(claude_skills_dir) & _discover_skill_names(agents_skills_dir))

    assert shared_skills, "No pair of skills to compare was found - check whether .claude/skills and .agents/skills exist"

    for skill_name in shared_skills:
        _assert_parity(
            claude_skills_dir / skill_name / "SKILL.md",
            agents_skills_dir / skill_name / "SKILL.md",
            skill_name,
        )


def test_every_paired_agent_role_is_at_parity() -> None:
    """
    Ensures that the instruction of every agent role reads the same in the variant for
    Claude Code and in the variant for Codex, apart from the only explicitly allowed
    difference in the name of the command runner.

    Until now the agreement of both variants was guarded only by a human, who did not
    manage it: both role pairs diverged in content before this test was created.
    """
    claude_roles_dir = ROOT_DIR / ".claude" / "agents"
    codex_roles_dir = ROOT_DIR / ".codex" / "agents"

    claude_roles = _discover_role_names(claude_roles_dir, ".md")
    codex_roles = _discover_role_names(codex_roles_dir, ".toml")

    assert claude_roles, "No role definition was found in .claude/agents - check whether the directory exists"
    assert claude_roles == codex_roles, (
        f"Roles without a pair: only in .claude/agents {sorted(claude_roles - codex_roles)}, only in .codex/agents {sorted(codex_roles - claude_roles)}. See {AGENT_ROLE_REFERENCE}."
    )

    for role_name in sorted(claude_roles):
        claude_path = claude_roles_dir / f"{role_name}.md"
        codex_path = codex_roles_dir / f"{role_name}.toml"

        differences = _real_differences(claude_path.name, fetch_claude_role_instructions(claude_path), codex_path.name, fetch_codex_role_instructions(codex_path))

        assert not differences, (
            f"The role pair {role_name} diverged beyond the allowed differences:\n" + "\n".join(differences) + f"\nSee {AGENT_ROLE_REFERENCE} for the rationale and the list of allowed exceptions."
        )
