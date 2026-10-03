"""
Enforces two rules from `standard_formatting.md` that no other linter configured in the repository
today checks: forbidden characters and bold in prose outside a heading
and a table cell. `ruff format` checks the formatting of Python code, but deliberately skips
markdown files (`extend-exclude` in `pyproject.toml`) and does not know the bold rule at all.

The rule is enforced by a test, not by a separate tool called from the command line, because the test goes
into `make test`, and through it into `make check` and into the standard - verifying tool map
in `standard_review.md`. Thanks to that it fires on its own during implementation and review, instead of being
a target whose call has to be remembered separately.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]

SCANNED_FILE_SUFFIXES: frozenset[str] = frozenset({".py", ".md"})

EXCLUDED_DIRECTORY_NAMES: frozenset[str] = frozenset({".venv", "venv", ".git", ".cache", "__pycache__", "build", "dist", "node_modules", "temp"})
EXCLUDED_DIRECTORY_PREFIXES: tuple[str, ...] = ("pytest_tmp",)
"""
Repeats `exclude` from `[tool.ruff]` in `pyproject.toml`, so that both tools agree on what
is code and documentation of the repository and what is an artifact of the environment or a tool. `node_modules`
is the local prettier installation from `package.json`, with the package's own documentation in someone else's style.
"""

FORBIDDEN_CHARACTER_REPLACEMENTS: tuple[tuple[int, str], ...] = (
    (0x2014, "-"),
    (0x2013, "-"),
    (0x2212, "-"),
    (0x201C, '"'),
    (0x201D, '"'),
    (0x2018, "'"),
    (0x2019, "'"),
    (0x02BC, "'"),
    (0x2026, "..."),
    (0x00B7, ". or -, depending on context"),
    (0x2192, "->"),
    (0x2190, "<-"),
    (0x2194, "<->"),
    (0x00D7, "x or *, depending on context"),
    (0x0430, "a (plain Latin)"),
    (0x037E, "; (plain semicolon)"),
    (0x2215, "/"),
)
"""
Code point -> replacement hint, one to one with the list in `standard_formatting.md`,
section Forbidden characters. The keys are code points, not literal characters - otherwise this file
would itself contain every forbidden character and would report itself as a violation in its own scan.
"""

FORBIDDEN_CHARACTERS: dict[str, str] = {chr(codepoint): hint for codepoint, hint in FORBIDDEN_CHARACTER_REPLACEMENTS}

EMOJI_CODEPOINT_RANGES: tuple[tuple[int, int], ...] = (
    (0x2600, 0x26FF),
    (0x2700, 0x27BF),
    (0x1F300, 0x1F5FF),
    (0x1F600, 0x1F64F),
    (0x1F680, 0x1F6FF),
    (0x1F900, 0x1F9FF),
    (0x1FA70, 0x1FAFF),
)

EMOJI_REPLACEMENT_HINT = "remove - emojis are not allowed"

FORMATTING_STANDARD_PATH = "docs/standards/standard_formatting.md"

RULE_DEFINING_PATHS: frozenset[str] = frozenset({"AGENTS.md", "CLAUDE.md", FORMATTING_STANDARD_PATH})
"""
These three files document the list of forbidden characters outright and therefore have to quote them literally -
that is the content of the rule definition, not its violation. The standard carries the full list, `AGENTS.md`
and `CLAUDE.md` one shortened to the hard bans applicable without context; this divergence is intended
and described in the standard itself, section Scope and boundaries.

The exception is narrow, names every file separately and concerns only characters - the bold rule
applies in these files normally. Two tests below make sure it does not turn into a quiet loophole.
"""

_HEADER_LINE_PATTERN = re.compile(r"^#{1,6}\s")
_TABLE_ROW_PATTERN = re.compile(r"^\s*\|")
_BOLD_SPAN_PATTERN = re.compile(r"\*\*[^*\n]+\*\*")
_FENCE_MARKER_PATTERN = re.compile(r"^\s*```")
_BLOCKQUOTE_PREFIX_PATTERN = re.compile(r"^\s*(?:>\s*)+")
"""
The blockquote prefix, stripped before recognizing the kind of the line.

Without it, a verbatim quote of a table row from another document looks like prose, because `_TABLE_ROW_PATTERN`
requires a vertical bar at the beginning of the line, and in a quote a greater-than sign stands there. Task artifacts
in `plans/` copy table rows verbatim from other documents, together with their bold, and the seed is
unmodifiable - fixing such a quote is unavailable by definition. `standard_formatting.md`
allows bold in a table cell, and quoting a table does not turn its cells into prose.

The exception is narrow on purpose: only the prefix is stripped, and the kind of the line under it is recognized by the
same rule as everywhere else. Bold in a quoted sentence is still reported, because a sentence is not
a structure of the document.
"""

BOLD_MARKED_LINE = "This is a **bold** phrase in the middle of a sentence."
"""Test input for the bold rule, shared by the four cases below."""


@dataclass(frozen=True)
class ForbiddenCharacterViolation:
    """
    An occurrence of a character from the forbidden list (`standard_formatting.md`, section Forbidden characters)
    in a specific file and line.

    `replacement_hint` carries a ready hint of what to replace the character with - exactly the one the standard
    assigns to this specific character, so that the result can be fixed without opening the
    standard again.
    """

    path: str
    line_number: int
    character: str
    replacement_hint: str

    @property
    def report_line(self) -> str:
        """One line of the failed test message, ready to paste into the editor search."""
        return f"{self.path}:{self.line_number} - character U+{ord(self.character):04X} ({self.character}), replacement: {self.replacement_hint}"


@dataclass(frozen=True)
class BoldInProseViolation:
    """
    An occurrence of bold in prose outside a heading and a table cell (`standard_formatting.md`,
    section Emphasis in prose), in a specific file and line.
    """

    path: str
    line_number: int

    @property
    def report_line(self) -> str:
        """One line of the failed test message, ready to paste into the editor search."""
        return f"{self.path}:{self.line_number} - bold in prose outside a heading and a table cell"


@dataclass(frozen=True)
class ProseStyleScanSummary:
    """
    The result of one scan run: the number of files reviewed and all violations found.
    """

    scanned_file_count: int
    forbidden_character_violations: tuple[ForbiddenCharacterViolation, ...]
    bold_in_prose_violations: tuple[BoldInProseViolation, ...]

    @property
    def violated_paths(self) -> frozenset[str]:
        """
        The set of paths in which the run found anything - without distinguishing which of the two rules
        they violate. A file is clean only when it has neither a forbidden character nor
        bold in prose.
        """
        return frozenset(violation.path for violation in self.forbidden_character_violations) | frozenset(violation.path for violation in self.bold_in_prose_violations)


def fetch_scanned_files(root: Path) -> list[Path]:
    """
    Returns a sorted list of .py and .md files under `root`, skipping the tool directories.
    """
    scanned_files: list[Path] = []

    for directory, directory_names, file_names in root.walk(on_error=lambda _: None):
        directory_names[:] = [name for name in directory_names if name not in EXCLUDED_DIRECTORY_NAMES and not name.startswith(EXCLUDED_DIRECTORY_PREFIXES)]
        scanned_files.extend(directory / name for name in file_names if Path(name).suffix in SCANNED_FILE_SUFFIXES)

    return sorted(scanned_files)


def resolve_forbidden_character_hint(character: str) -> str | None:
    """
    Classifies a single character: returns the replacement hint for a forbidden character or an emoji,
    `None` for an allowed character.
    """
    if character in FORBIDDEN_CHARACTERS:
        return FORBIDDEN_CHARACTERS[character]

    codepoint = ord(character)

    if any(start <= codepoint <= end for start, end in EMOJI_CODEPOINT_RANGES):
        return EMOJI_REPLACEMENT_HINT

    return None


def resolve_forbidden_character_violations(path: str, lines: list[str]) -> list[ForbiddenCharacterViolation]:
    """
    Points out every occurrence of a forbidden character in the given lines of a file.
    """
    violations: list[ForbiddenCharacterViolation] = []

    for line_number, line in enumerate(lines, start=1):
        for character in line:
            replacement_hint = resolve_forbidden_character_hint(character)

            if replacement_hint is not None:
                violations.append(ForbiddenCharacterViolation(path=path, line_number=line_number, character=character, replacement_hint=replacement_hint))

    return violations


def resolve_bold_in_prose_violations(path: str, lines: list[str]) -> list[BoldInProseViolation]:
    """
    Points out the lines of a markdown file in which bold stands outside a heading and a table cell.

    A code block fenced with triple backticks is skipped entirely, because `standard_formatting.md`
    itself illustrates the forbidden pattern with a markdown example inside such a block - without this exception
    the standard's own example would look like a violation of the rule it describes.

    The blockquote prefix is stripped before recognizing the kind of the line, so a verbatim quoted
    table row is a table row, and a quoted heading is a heading. A quoted sentence stays a sentence
    and bold in it is still reported.
    """
    violations: list[BoldInProseViolation] = []
    inside_fenced_code_block = False

    for line_number, line in enumerate(lines, start=1):
        unquoted_line = _BLOCKQUOTE_PREFIX_PATTERN.sub("", line)

        if _FENCE_MARKER_PATTERN.match(unquoted_line):
            inside_fenced_code_block = not inside_fenced_code_block
            continue

        if inside_fenced_code_block:
            continue

        if _HEADER_LINE_PATTERN.match(unquoted_line) or _TABLE_ROW_PATTERN.match(unquoted_line):
            continue

        if _BOLD_SPAN_PATTERN.search(line):
            violations.append(BoldInProseViolation(path=path, line_number=line_number))

    return violations


def fetch_prose_style_summary(root: Path) -> ProseStyleScanSummary:
    """
    Reads all scanned files under `root` and returns the summary of the run.
    """
    forbidden_character_violations: list[ForbiddenCharacterViolation] = []
    bold_in_prose_violations: list[BoldInProseViolation] = []
    scanned_files = fetch_scanned_files(root)

    for path in scanned_files:
        relative_path = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()

        if relative_path not in RULE_DEFINING_PATHS:
            forbidden_character_violations.extend(resolve_forbidden_character_violations(relative_path, lines))

        if path.suffix == ".md":
            bold_in_prose_violations.extend(resolve_bold_in_prose_violations(relative_path, lines))

    return ProseStyleScanSummary(
        scanned_file_count=len(scanned_files),
        forbidden_character_violations=tuple(forbidden_character_violations),
        bold_in_prose_violations=tuple(bold_in_prose_violations),
    )


def build_violation_report(header: str, violations: Sequence[ForbiddenCharacterViolation | BoldInProseViolation]) -> str:
    """
    Builds the failed test message: a header saying what went wrong, and one line per violation,
    each with the path and the line number to fix.
    """
    return "\n".join([header, *(violation.report_line for violation in violations)])


@pytest.fixture(scope="module")
def repository_scan() -> ProseStyleScanSummary:
    """
    Scans the whole repository once per module. A single run takes more than a second, and all
    three tests below ask about the same state - repeating the scan for each of them would triple
    that cost without any benefit.
    """
    return fetch_prose_style_summary(ROOT_DIR)


def test_repository_has_no_forbidden_characters(repository_scan: ProseStyleScanSummary) -> None:
    """
    Ensures that no .py or .md file in the repository contains a character from the forbidden list
    or an emoji.

    The test has no list of exceptions other than `RULE_DEFINING_PATHS` and is to stay that way: adding to it
    an exception for a document nobody bothered to fix turns the gate into a wish list.
    """
    violations = repository_scan.forbidden_character_violations

    assert not violations, build_violation_report("Forbidden characters from standard_formatting.md, section Forbidden characters:", violations)


def test_repository_has_no_bold_in_prose(repository_scan: ProseStyleScanSummary) -> None:
    """
    Ensures that no .md file in the repository has bold in prose - the weight of emphasis
    is carried by order, not by typeface. Bold stays allowed where it is
    an element of the document structure: in a heading and in a table cell.
    """
    violations = repository_scan.bold_in_prose_violations

    assert not violations, build_violation_report("Bold in prose, contrary to standard_formatting.md, section Emphasis in prose:", violations)


def test_formatting_standard_still_quotes_every_forbidden_character() -> None:
    """
    Ensures that the standard still literally quotes every character it lists itself, and an emoji.

    This test defends the `RULE_DEFINING_PATHS` exception from the other side than the test below. A character gone
    from the standard but still standing in `FORBIDDEN_CHARACTER_REPLACEMENTS` means a divergence between the rule
    and the tool that enforces it - and since the standard is exempt from the character scan, nothing else
    will notice that divergence. A change of the list itself in the standard is to entail a change of the table
    in this file, and this test is the place where the two meet.
    """
    text = (ROOT_DIR / FORMATTING_STANDARD_PATH).read_text(encoding="utf-8")
    missing_characters = [f"U+{codepoint:04X}" for codepoint, _ in FORBIDDEN_CHARACTER_REPLACEMENTS if chr(codepoint) not in text]

    assert not missing_characters, f"{FORMATTING_STANDARD_PATH} stopped quoting characters it defines itself: {missing_characters}"
    assert any(resolve_forbidden_character_hint(character) == EMOJI_REPLACEMENT_HINT for character in text), f"{FORMATTING_STANDARD_PATH} stopped showing an example emoji"


def test_every_rule_defining_path_still_needs_its_exemption() -> None:
    """
    Ensures that every file exempt from the character scan still quotes at least one forbidden character.

    The exception exists only so that a document can quote what it defines. A file that
    stopped quoting anything does not need the exception - and an exception without justification quietly
    lets through everything somebody pastes into that file later.
    """
    unnecessary_paths: list[str] = []

    for relative_path in sorted(RULE_DEFINING_PATHS):
        text = (ROOT_DIR / relative_path).read_text(encoding="utf-8")

        if not any(resolve_forbidden_character_hint(character) for character in text):
            unnecessary_paths.append(relative_path)

    assert not unnecessary_paths, f"These files no longer quote any forbidden character - remove them from RULE_DEFINING_PATHS: {unnecessary_paths}"


def test_resolve_forbidden_character_hint_flags_every_character_from_the_standard() -> None:
    """Ensures that every character from the standard_formatting.md list gets a replacement hint."""
    for codepoint, _ in FORBIDDEN_CHARACTER_REPLACEMENTS:
        assert resolve_forbidden_character_hint(chr(codepoint)) is not None


def test_resolve_forbidden_character_hint_flags_emoji() -> None:
    """Ensures that a character from the emoji range gets a hint, even though it is not listed outright."""
    checkmark_emoji = chr(0x2705)

    assert resolve_forbidden_character_hint(checkmark_emoji) == EMOJI_REPLACEMENT_HINT


def test_resolve_forbidden_character_hint_allows_plain_and_polish_characters() -> None:
    """
    Ensures that plain ASCII characters and Polish diacritics are not treated as forbidden.

    This is a refusal test: if the emoji ranges or the forbidden character map accidentally
    covered Polish letters, every document of this repository would start failing falsely.
    """
    for character in "aZ9-.,\"'ąćęłńóśźż":
        assert resolve_forbidden_character_hint(character) is None


def test_resolve_forbidden_character_violations_reports_line_and_character() -> None:
    """Ensures that a violation carries the correct line number, character and replacement hint."""
    lines = ["first line with nothing", f"second line with an em dash {chr(0x2014)} in the middle"]

    violations = resolve_forbidden_character_violations("document.md", lines)

    assert len(violations) == 1
    assert violations[0].line_number == 2
    assert violations[0].character == chr(0x2014)
    assert violations[0].replacement_hint == "-"


def test_resolve_bold_in_prose_violations_flags_bold_outside_header_and_table() -> None:
    """Ensures that bold in the middle of a regular sentence is reported."""
    violations = resolve_bold_in_prose_violations("document.md", [BOLD_MARKED_LINE])

    assert len(violations) == 1
    assert violations[0].line_number == 1


def test_resolve_bold_in_prose_violations_allows_bold_in_header() -> None:
    """Ensures that bold in a heading is allowed and not reported."""
    lines = [f"## {BOLD_MARKED_LINE}"]

    assert resolve_bold_in_prose_violations("document.md", lines) == []


def test_resolve_bold_in_prose_violations_allows_bold_in_table_row() -> None:
    """Ensures that bold in a table cell is allowed and not reported."""
    lines = [f"| {BOLD_MARKED_LINE} | second row |"]

    assert resolve_bold_in_prose_violations("document.md", lines) == []


def test_resolve_bold_in_prose_violations_allows_bold_in_quoted_table_row() -> None:
    """
    Ensures that bold in a cell of a verbatim quoted table is allowed.

    Task artifacts copy table rows from other documents together with their bold, and the seed is
    unmodifiable - fixing such a quote is unavailable by definition.
    """
    lines = [f"> | {BOLD_MARKED_LINE} | second row |"]

    assert resolve_bold_in_prose_violations("document.md", lines) == []


def test_resolve_bold_in_prose_violations_flags_bold_in_quoted_sentence() -> None:
    """Ensures that stripping the quote prefix does not let bold through in a quoted sentence - a sentence is not a structure of the document."""
    violations = resolve_bold_in_prose_violations("document.md", [f"> {BOLD_MARKED_LINE}"])

    assert len(violations) == 1
    assert violations[0].line_number == 1


def test_resolve_bold_in_prose_violations_ignores_fenced_code_block() -> None:
    """
    Ensures that bold inside a code block fenced with triple backticks is skipped.

    standard_formatting.md illustrates the forbidden pattern with a markdown example in such a block - without this
    exception the standard's own example would look like a violation of the rule it describes.
    """
    lines = ["```markdown", BOLD_MARKED_LINE, "```"]

    assert resolve_bold_in_prose_violations("document.md", lines) == []


def test_fetch_scanned_files_skips_excluded_directories(tmp_path: Path) -> None:
    """Ensures that files in tool directories (e.g. venv) do not get into the scan."""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "settings.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "venv" / "lib").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "site.py").write_text("y = 2\n", encoding="utf-8")

    scanned = fetch_scanned_files(tmp_path)

    assert tmp_path / "config" / "settings.py" in scanned
    assert not any("venv" in path.parts for path in scanned)


def test_fetch_scanned_files_finds_only_python_and_markdown_files(tmp_path: Path) -> None:
    """Ensures that files other than .py and .md (e.g. .txt) do not get into the scan."""
    (tmp_path / "note.txt").write_text("content\n", encoding="utf-8")
    (tmp_path / "document.md").write_text("# title\n", encoding="utf-8")

    scanned = fetch_scanned_files(tmp_path)

    assert scanned == [tmp_path / "document.md"]


def test_fetch_prose_style_summary_excludes_the_files_that_define_the_forbidden_character_list(tmp_path: Path) -> None:
    """
    Ensures that AGENTS.md, CLAUDE.md and standard_formatting.md are not reported for quoting
    the characters they define themselves - that is the content of the rule, not its violation.
    """
    forbidden_character = chr(0x2014)
    (tmp_path / "AGENTS.md").write_text(f"Do not use the character {forbidden_character}.\n", encoding="utf-8")
    (tmp_path / "docs" / "standards").mkdir(parents=True)
    (tmp_path / "docs" / "standards" / "standard_formatting.md").write_text(f"- `{forbidden_character}` (U+2014).\n", encoding="utf-8")
    (tmp_path / "other_document.md").write_text(f"Here is the same character {forbidden_character} by accident.\n", encoding="utf-8")

    summary = fetch_prose_style_summary(tmp_path)

    assert {violation.path for violation in summary.forbidden_character_violations} == {"other_document.md"}


def test_fetch_prose_style_summary_reports_nothing_for_a_clean_document(tmp_path: Path) -> None:
    """Ensures that a run without any violation does not report a single path."""
    (tmp_path / "document.md").write_text("# Title\n\nPlain prose with nothing forbidden.\n", encoding="utf-8")

    summary = fetch_prose_style_summary(tmp_path)

    assert summary.violated_paths == frozenset()
    assert summary.scanned_file_count == 1
