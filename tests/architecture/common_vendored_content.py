"""
Third-party content that its own installer put into the repository, shared by the gates that enforce the rules
of the team: the parity of the Claude Code and Codex variants (`test_agent_docs_parity.py`) and the prose style
(`test_prose_style.py`).

Those gates judge what the team writes. A skill installed by a third-party installer is written in someone else's
style, and the installer generates its variant for each tool separately, so the two copies differ on purpose: in the
invocation prefix, in the frontmatter keys and in the place of the Codex agent roles. An edit made by hand to bring
it in line would be overwritten by the next update of the skill. This is the same reason `node_modules` stays
out of the prose scan. The rule and its boundaries are in `docs/standards/standard_agentic_workflow.md` ch. 6.1.

The list is narrow on purpose: it names every skill and every agent role separately, never a pattern, and
`test_vendored_content.py` fails when an entry points to something no longer in the repository.
"""

from __future__ import annotations

VENDORED_SKILL_NAMES: frozenset[str] = frozenset({"impeccable"})
"""
Skills installed by a third-party installer into both `.claude/skills/` and `.agents/skills/`.

`impeccable` - Impeccable 4.5.0, Apache 2.0, installed on 2026-10-03 in commit `9578638`.
"""

VENDORED_AGENT_ROLE_NAMES: frozenset[str] = frozenset({"impeccable-asset-producer", "impeccable-documenter", "impeccable-finish-reviewer", "impeccable-manual-edit-applier"})
"""
Claude Code agent roles in `.claude/agents/` installed together with a vendored skill. Their Codex variants
live inside the skill itself, in `.agents/skills/<skill>/agents/`, where the installer put them, not in `.codex/agents/`.
"""

SKILL_DIRECTORIES: tuple[str, ...] = (".claude/skills", ".agents/skills")
CLAUDE_AGENT_ROLE_DIRECTORY = ".claude/agents"

VENDORED_DIRECTORY_PREFIXES: tuple[str, ...] = tuple(f"{skills_directory}/{skill_name}/" for skills_directory in SKILL_DIRECTORIES for skill_name in sorted(VENDORED_SKILL_NAMES))
"""
The directories of the vendored skills, relative to the repository root, each ending with a slash, so that a skill
whose name only starts with the name of a vendored one is not taken for it.
"""

VENDORED_FILE_PATHS: frozenset[str] = frozenset(f"{CLAUDE_AGENT_ROLE_DIRECTORY}/{role_name}.md" for role_name in VENDORED_AGENT_ROLE_NAMES)
"""The files of the vendored agent roles on the Claude Code side, relative to the repository root."""


def is_vendored_path(relative_path: str) -> bool:
    """
    Says whether a file belongs to third-party content: whether it lies inside the directory of a vendored skill
    or is the definition of a vendored agent role. The path is relative to the repository root and uses forward
    slashes, the form `Path.as_posix` gives.
    """
    return relative_path in VENDORED_FILE_PATHS or relative_path.startswith(VENDORED_DIRECTORY_PREFIXES)
