"""
Enforces the rules from `standard_agent_docs.md`, section PLAN format, that no other tool in the
repository checks: the format of the items in the Facts section and the empty Open questions section.

The scope of the check is narrow on purpose. It covers only plans marked with the "plan closed" marker
and not older than the date the rule took effect. A plan in progress stays outside it, so that a document
written in installments does not block unrelated work on the same tree, and a plan from before the threshold
date stays outside it, because a retrofit would require writing in check dates nobody knows today - that is,
breaking the very rule this check introduces.

There is one boundary and it is worth naming right next to the code: the form of the evidence is checked,
never its truthfulness. A made-up finding written in the correct form will pass this gate.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]

PLAN_GLOB_PATTERNS: tuple[str, ...] = ("plans/**/PLAN.md", "plans/**/*_PLAN.md", "plans_finished/**/PLAN.md", "plans_finished/**/*_PLAN.md")
"""
Four patterns: two forms of the name in two locations. The repository uses the name without the task
prefix, while the standard and the skills describe the pattern with the prefix - a check accepting only one
of these forms would stop seeing documents at the first artifact named with the other. The second location
is the `plans_finished/` archive from `standard_agentic_workflow.md`, ch. 4.6: a closed plan moves there
together with the whole initiative and is to be subject to the same check as before the move, otherwise
archiving would be a way around the gate. The double asterisk covers the task subdirectories allowed
in ch. 3.2 of the same standard, which a one-level pattern did not see.
"""

RULE_EFFECTIVE_DATE = date(2026, 8, 17)
"""
The date the rule took effect, described in `standard_agent_docs.md`, section Enforcement. A project
created from the template comes into existence after this date, so the check covers every closed plan of it.
A constant, not a read of the system clock: a moving threshold would change the scope
of the check from day to day, without any change in the repository.
"""

CLOSED_STATE_MARKER = "plan closed"
IN_PROGRESS_STATE_MARKER = "plan in progress"

EVIDENCE_PREFIXES: tuple[str, ...] = ("code:", "cmd:", "db:", "doc:")
ASSUMPTION_MARKER = "ASSUMPTION:"

FACTS_HEADING = "## Facts"
OPEN_QUESTIONS_HEADING = "## Open questions"

NO_OPEN_QUESTIONS_PREFIX = "None"

FIELD_SEPARATOR = "|"
EVIDENCE_SEPARATOR = ";"
INLINE_CODE_MARKER = "`"
EXPECTED_FIELD_COUNT = 3

FACT_LINE_PATTERN = re.compile(r"^(F-\d+)\.\s+(\S.*)$")
STATE_LINE_PATTERN = re.compile(r"^Document state:\s*(\d{4}-\d{2}-\d{2})\s*(?:,\s*(.+?))?\s*$")
CHECKED_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECTION_HEADING_PATTERN = re.compile(r"^##\s")
LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")

UNKNOWN_IDENTIFIER = "no identifier"


@dataclass(frozen=True)
class PlanDocumentState:
    """
    The state of a plan document read from the header line: the date and the marker, if the line carries one.

    A missing marker is not a violation here - a document without it simply stays outside the scope
    of the check, just like a document marked as a plan in progress.
    """

    state_date: date | None
    marker: str | None

    @property
    def is_under_gate(self) -> bool:
        """
        Says whether the document is subject to the check. The marker decides, and the date only comes
        second - a plan in progress stays outside the check no matter how fresh it is.
        """
        if self.marker != CLOSED_STATE_MARKER:
            return False

        return self.state_date is not None and self.state_date >= RULE_EFFECTIVE_DATE


@dataclass(frozen=True)
class FactViolation:
    """
    An item of the Facts section that does not match the format, together with the rejection reason ready
    to read without opening the standard.
    """

    path: str
    line_number: int
    identifier: str
    reason: str

    @property
    def report_line(self) -> str:
        """One line of the failed test message, with the path, the line number and the identifier."""
        return f"{self.path}:{self.line_number} - {self.identifier}: {self.reason}"


@dataclass(frozen=True)
class OpenQuestionViolation:
    """Content in the Open questions section that makes a closed plan have it non-empty."""

    path: str
    line_number: int
    reason: str

    @property
    def report_line(self) -> str:
        """One line of the failed test message, with the path and the line number."""
        return f"{self.path}:{self.line_number} - {self.reason}"


def fetch_plan_documents(root: Path) -> list[Path]:
    """
    Returns a sorted list of plan documents under `root`, in both naming conventions, from current
    work and from the archive, also from task subdirectories. A file hit by two patterns counts once.
    """
    documents: set[Path] = set()

    for pattern in PLAN_GLOB_PATTERNS:
        documents.update(path for path in root.glob(pattern) if path.is_file())

    return sorted(documents)


def fetch_document_state(path: Path) -> PlanDocumentState:
    """
    Reads the document and returns the state from the first `Document state` line. A document without
    such a line or with a date that cannot be read gets an empty state and therefore stays outside the check.
    """
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STATE_LINE_PATTERN.match(line.strip())

        if match is not None:
            return PlanDocumentState(state_date=resolve_readable_date(match.group(1)), marker=match.group(2))

    return PlanDocumentState(state_date=None, marker=None)


def resolve_readable_date(text: str) -> date | None:
    """
    Returns the date read from the text, or `None` when the text is just an arrangement of digits and
    hyphens, not an existing date.
    """
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def resolve_section_lines(lines: Sequence[str], heading: str) -> list[tuple[int, str]]:
    """
    Cuts out the lines of one document section together with their numbers, from the `heading` heading to
    the next heading of the same level. The heading itself is not part of the result.
    """
    section: list[tuple[int, str]] = []
    inside_section = False

    for line_number, line in enumerate(lines, start=1):
        if line.strip() == heading:
            inside_section = True
            continue

        if inside_section and SECTION_HEADING_PATTERN.match(line):
            break

        if inside_section:
            section.append((line_number, line))

    return section


def resolve_fact_violations(path: str, lines: Sequence[str]) -> list[FactViolation]:
    """
    Points out the items of the Facts section that do not have the shape required by the standard: an
    identifier with a claim, evidence of one of the five kinds and a check date, in three fields separated
    by a vertical bar.

    Each item gets at most one report, with the first reason encountered - the message is meant to say
    what to fix, not to list every consequence of the same mistake.
    """
    violations: list[FactViolation] = []

    for line_number, line in resolve_section_lines(lines, FACTS_HEADING):
        position = line.strip()

        if not position:
            continue

        identifier_match = FACT_LINE_PATTERN.match(position)

        if identifier_match is None:
            violations.append(
                FactViolation(path=path, line_number=line_number, identifier=UNKNOWN_IDENTIFIER, reason="a line of the Facts section is not a finding item - the F-N shaped identifier is missing.")
            )
            continue

        identifier = identifier_match.group(1)
        fields = resolve_separated_fields(position, FIELD_SEPARATOR)

        if len(fields) != EXPECTED_FIELD_COUNT:
            violations.append(
                FactViolation(
                    path=path, line_number=line_number, identifier=identifier, reason=f"the item has {len(fields)} fields instead of three separated by a vertical bar: claim, evidence, check date."
                )
            )
            continue

        claim, evidence_field, checked_date = fields

        if FACT_LINE_PATTERN.match(claim) is None:
            violations.append(FactViolation(path=path, line_number=line_number, identifier=identifier, reason="the identifier stands without a claim - the first field carries the finding."))
            continue

        unknown_evidence = resolve_unknown_evidence(evidence_field)

        if unknown_evidence is not None:
            violations.append(FactViolation(path=path, line_number=line_number, identifier=identifier, reason=f"the evidence does not start with any of the five allowed kinds: {unknown_evidence!r}."))
            continue

        if CHECKED_DATE_PATTERN.match(checked_date) is None or resolve_readable_date(checked_date) is None:
            violations.append(FactViolation(path=path, line_number=line_number, identifier=identifier, reason=f"the check date is not a date in the YYYY-MM-DD format: {checked_date!r}."))

    return violations


def resolve_separated_fields(text: str, separator: str) -> list[str]:
    """
    Splits the text on the separator and trims whitespace, skipping occurrences of the separator that stand
    inside text in backticks.

    The backtick exception is not cosmetic: evidence can quote a command with a regex or a query with
    its own semicolon, and the literalness of the quote matters more here than the simplicity of the split.
    Without this exception the format would force rewriting a command that was actually run.
    """
    fields: list[str] = []
    current: list[str] = []
    inside_inline_code = False

    for character in text:
        if character == INLINE_CODE_MARKER:
            inside_inline_code = not inside_inline_code

        if character == separator and not inside_inline_code:
            fields.append("".join(current).strip())
            current = []
            continue

        current.append(character)

    fields.append("".join(current).strip())

    return fields


def resolve_unknown_evidence(evidence_field: str) -> str | None:
    """
    Returns the first piece of evidence that does not open with any of the five allowed kinds, or `None`
    when the whole field is correct. Several pieces of evidence for one item are separated by a semicolon.
    """
    allowed_openings = (*EVIDENCE_PREFIXES, ASSUMPTION_MARKER)

    for evidence in resolve_separated_fields(evidence_field, EVIDENCE_SEPARATOR):
        if not evidence.startswith(allowed_openings):
            return evidence

    return None


def resolve_open_question_violations(path: str, lines: Sequence[str]) -> list[OpenQuestionViolation]:
    """
    Points out the content that makes the Open questions section stop being empty: a list item and
    a first paragraph other than a statement of absence.

    A sentence starting with the word None is the record of an empty section, not an item - nine out of ten
    plans existing at the moment this check was created record the absence exactly like that.
    """
    violations: list[OpenQuestionViolation] = []
    section_lines = [(line_number, line.strip()) for line_number, line in resolve_section_lines(lines, OPEN_QUESTIONS_HEADING) if line.strip()]

    for position, (line_number, line) in enumerate(section_lines):
        if LIST_ITEM_PATTERN.match(line):
            violations.append(OpenQuestionViolation(path=path, line_number=line_number, reason="the Open questions section of a closed plan has a list item."))
            continue

        if position == 0 and not line.startswith(NO_OPEN_QUESTIONS_PREFIX):
            violations.append(
                OpenQuestionViolation(
                    path=path,
                    line_number=line_number,
                    reason=f"the Open questions section of a closed plan does not open with a statement of absence - expected a paragraph starting with {NO_OPEN_QUESTIONS_PREFIX!r}.",
                )
            )

    return violations


def build_violation_report(header: str, violations: Sequence[FactViolation | OpenQuestionViolation]) -> str:
    """
    Builds the failed test message: a header saying what went wrong, and one line per violation,
    each with the path and the line number to fix.
    """
    return "\n".join([header, *(violation.report_line for violation in violations)])


@pytest.fixture(scope="module")
def gated_plan_documents() -> list[tuple[str, list[str]]]:
    """
    Returns the path and the lines of every plan document covered by the check, reading each file once
    per module instead of once per test.

    An empty list is an error when the repository has plans marked as closed but none of them passes
    the date threshold: a check that sees not a single document then looks like it works and guards
    nothing. When the repository has no closed plan yet, like a fresh project from the template, the tests
    using this fixture are skipped with a reason visible in the run summary.
    """
    documents: list[tuple[str, list[str]]] = []
    closed_document_count = 0

    for path in fetch_plan_documents(ROOT_DIR):
        state = fetch_document_state(path)

        if state.marker == CLOSED_STATE_MARKER:
            closed_document_count += 1

        if not state.is_under_gate:
            continue

        documents.append((path.relative_to(ROOT_DIR).as_posix(), path.read_text(encoding="utf-8").splitlines()))

    if not documents and not closed_document_count:
        pytest.skip(f"The repository has no plan marked {CLOSED_STATE_MARKER!r} yet - the check starts working with the first such plan.")

    assert documents, f"No closed plan is covered by the check - verify the threshold {RULE_EFFECTIVE_DATE.isoformat()}"

    return documents


def test_every_closed_plan_states_evidence_for_each_fact(gated_plan_documents: list[tuple[str, list[str]]]) -> None:
    """
    Ensures that every item of the Facts section in a closed plan carries an identifier, a claim,
    evidence of one of the five kinds and a check date.
    """
    violations: list[FactViolation] = []

    for path, lines in gated_plan_documents:
        violations.extend(resolve_fact_violations(path, lines))

    assert not violations, build_violation_report("Items of the Facts section not compliant with standard_agent_docs.md, section PLAN format:", violations)


def test_every_closed_plan_has_no_open_questions(gated_plan_documents: list[tuple[str, list[str]]]) -> None:
    """
    Ensures that a plan marked as closed has an empty Open questions section - a document with a real
    question inside is not ready to be handed to the implementation phase.
    """
    violations: list[OpenQuestionViolation] = []

    for path, lines in gated_plan_documents:
        violations.extend(resolve_open_question_violations(path, lines))

    assert not violations, build_violation_report("Non-empty Open questions sections in closed plans, contrary to standard_agent_docs.md:", violations)


def write_plan_document(path: Path, content: str = "# Plan\n") -> Path:
    """Writes a plan document at the given path, creating the missing initiative directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return path


def test_fetch_plan_documents_finds_both_naming_conventions_in_both_locations(tmp_path: Path) -> None:
    """
    Ensures that the check sees the name used in the repository and the name described in the standard,
    in current work and in the archive, also in the task subdirectory of a multi-task initiative.
    """
    expected = [
        write_plan_document(tmp_path / "plans" / "without_prefix" / "PLAN.md"),
        write_plan_document(tmp_path / "plans" / "with_prefix" / "TASK_PLAN.md"),
        write_plan_document(tmp_path / "plans" / "multi_task" / "TASK-2" / "TASK-2_PLAN.md"),
        write_plan_document(tmp_path / "plans_finished" / "closed_without_prefix" / "PLAN.md"),
        write_plan_document(tmp_path / "plans_finished" / "closed_with_prefix" / "TASK_PLAN.md"),
        write_plan_document(tmp_path / "plans_finished" / "closed_multi_task" / "TASK-1" / "TASK-1_PLAN.md"),
    ]

    assert fetch_plan_documents(tmp_path) == sorted(expected)


def test_fetch_plan_documents_reports_each_document_once(tmp_path: Path) -> None:
    """Ensures that a file matching more than one pattern does not come under the check twice."""
    document = write_plan_document(tmp_path / "plans" / "initiative" / "PLAN.md")

    assert fetch_plan_documents(tmp_path) == [document]


def test_fetch_plan_documents_treats_a_missing_archive_as_empty(tmp_path: Path) -> None:
    """Ensures that a missing archive directory is not an error - a repository without archiving has a plain list."""
    document = write_plan_document(tmp_path / "plans" / "initiative" / "PLAN.md")

    assert not (tmp_path / "plans_finished").exists()
    assert fetch_plan_documents(tmp_path) == [document]


def test_fetch_plan_documents_skips_other_artifacts(tmp_path: Path) -> None:
    """Ensures that the other chain artifacts do not come under the plan format check, in any location."""
    for location in ("plans", "plans_finished"):
        (tmp_path / location / "initiative").mkdir(parents=True)
        (tmp_path / location / "initiative" / "SHAPE.md").write_text("# Shape\n", encoding="utf-8")
        (tmp_path / location / "initiative" / "PRD.md").write_text("# PRD\n", encoding="utf-8")
        (tmp_path / location / "initiative" / "REVIEW.md").write_text("# Review\n", encoding="utf-8")

    assert fetch_plan_documents(tmp_path) == []


def test_archiving_a_faulty_closed_plan_keeps_its_violations(tmp_path: Path) -> None:
    """
    Ensures that moving an initiative to the archive is not a way around the gate: a faulty closed plan
    reports the same violations after the move as before it, differing only in the path.
    """
    faulty_plan = "\n".join(
        [
            "# Plan",
            "",
            f"Document state: 2026-09-17, {CLOSED_STATE_MARKER}",
            "",
            FACTS_HEADING,
            "",
            "F-1. A finding without evidence and date.",
            "",
            OPEN_QUESTIONS_HEADING,
            "",
            "- Does the consumer guarantee key uniqueness?",
            "",
        ]
    )
    active_path = write_plan_document(tmp_path / "plans" / "initiative" / "PLAN.md", faulty_plan)

    def resolve_gated_violations() -> list[tuple[int, str]]:
        """Collects the violations of every plan under the check as line-reason pairs, without the path."""
        collected: list[tuple[int, str]] = []

        for path in fetch_plan_documents(tmp_path):
            assert fetch_document_state(path).is_under_gate
            lines = path.read_text(encoding="utf-8").splitlines()
            collected.extend((violation.line_number, violation.reason) for violation in resolve_fact_violations(path.name, lines))
            collected.extend((violation.line_number, violation.reason) for violation in resolve_open_question_violations(path.name, lines))

        return collected

    violations_before = resolve_gated_violations()
    assert len(violations_before) == 2

    archived_dir = tmp_path / "plans_finished" / "initiative"
    archived_dir.parent.mkdir()
    active_path.parent.rename(archived_dir)

    assert not active_path.exists()
    assert fetch_plan_documents(tmp_path) == [archived_dir / "PLAN.md"]
    assert resolve_gated_violations() == violations_before


def test_fetch_document_state_reads_date_and_closed_marker(tmp_path: Path) -> None:
    """Ensures that a state line with the closed marker brings the document under the check."""
    path = tmp_path / "PLAN.md"
    path.write_text(f"# Plan\n\nDocument state: 2026-08-17, {CLOSED_STATE_MARKER}\n", encoding="utf-8")

    state = fetch_document_state(path)

    assert state.state_date == date(2026, 8, 17)
    assert state.marker == CLOSED_STATE_MARKER
    assert state.is_under_gate


def test_fetch_document_state_leaves_a_plan_in_progress_outside_the_gate(tmp_path: Path) -> None:
    """Ensures that a plan in progress stays outside the check, despite a date after the threshold."""
    path = tmp_path / "PLAN.md"
    path.write_text(f"Document state: 2026-12-31, {IN_PROGRESS_STATE_MARKER}\n", encoding="utf-8")

    assert not fetch_document_state(path).is_under_gate


def test_fetch_document_state_leaves_a_plan_older_than_the_rule_outside_the_gate(tmp_path: Path) -> None:
    """Ensures that a closed plan from before the rule took effect does not require a retrofit."""
    path = tmp_path / "PLAN.md"
    path.write_text(f"Document state: 2026-08-16, {CLOSED_STATE_MARKER}\n", encoding="utf-8")

    assert not fetch_document_state(path).is_under_gate


def test_fetch_document_state_leaves_a_plan_without_a_marker_outside_the_gate(tmp_path: Path) -> None:
    """Ensures that the ten plans with only a date in the state line stay outside the check."""
    path = tmp_path / "PLAN.md"
    path.write_text("Document state: 2026-08-18\n", encoding="utf-8")

    state = fetch_document_state(path)

    assert state.marker is None
    assert not state.is_under_gate


def test_resolve_fact_violations_accepts_a_well_formed_position() -> None:
    """Ensures that an item with the full set of fields and two pieces of evidence passes without a report."""
    lines = [
        FACTS_HEADING,
        "",
        "F-1. The probe reads the address from the configuration. | code:`data/engine.py` function `build_engine`; doc:`docs/standards/standard_config.md` section One place of reading | 2026-08-17",
        "",
        "## Decisions",
        "F-2. This is no longer a fact.",
    ]

    assert resolve_fact_violations("PLAN.md", lines) == []


def test_resolve_fact_violations_accepts_an_explicit_assumption() -> None:
    """Ensures that an explicitly marked assumption is an allowed kind of evidence."""
    lines = [FACTS_HEADING, f"F-1. The consumer calls this endpoint once a minute. | {ASSUMPTION_MARKER} no measurement on the consumer side | 2026-08-17"]

    assert resolve_fact_violations("PLAN.md", lines) == []


def test_resolve_fact_violations_accepts_a_separator_quoted_inside_inline_code() -> None:
    """
    Ensures that a vertical bar and a semicolon quoted in backticks do not split fields.

    The input is taken from real life: the evidence quotes a regex with a vertical bar, and without this
    exception the format would require rewriting a command that was actually run.
    """
    lines = [FACTS_HEADING, 'F-1. The TOML parser is in the standard library. | cmd:`rg "tomllib|tomli" --glob "*.py"` -> no occurrences | 2026-08-17']

    assert resolve_fact_violations("PLAN.md", lines) == []


def test_resolve_separated_fields_splits_only_outside_inline_code() -> None:
    """Ensures splitting on the separator outside backticks and no splitting inside a quote."""
    assert resolve_separated_fields("a | `b | c` | d", FIELD_SEPARATOR) == ["a", "`b | c`", "d"]


def test_resolve_fact_violations_flags_a_position_without_evidence() -> None:
    """Ensures that a finding written as one sentence, without fields, is reported together with its identifier."""
    lines = [FACTS_HEADING, "F-1. The probe reads the address from the configuration. Source: data/engine.py."]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].identifier == "F-1"
    assert violations[0].line_number == 2


def test_resolve_fact_violations_flags_an_unknown_evidence_kind() -> None:
    """Ensures that evidence outside the five kinds is reported together with its content."""
    lines = [FACTS_HEADING, "F-3. The service returns code 409 on a repeat. | I know it from a conversation | 2026-08-17"]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert "I know it from a conversation" in violations[0].reason


def test_resolve_fact_violations_flags_a_second_evidence_without_its_kind() -> None:
    """Ensures that evidence added after a semicolon must also carry its kind."""
    lines = [FACTS_HEADING, "F-4. Type checking does not cover the tests. | code:`pyproject.toml` table `[tool.mypy]`; same in the second tool | 2026-08-17"]

    assert len(resolve_fact_violations("PLAN.md", lines)) == 1


def test_resolve_fact_violations_flags_a_position_without_an_identifier() -> None:
    """Ensures that a paragraph without an identifier in the Facts section is reported."""
    lines = [FACTS_HEADING, "The findings below come from reading the repository."]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].identifier == UNKNOWN_IDENTIFIER


def test_resolve_fact_violations_flags_a_checked_date_that_is_not_a_date() -> None:
    """Ensures that an arrangement of digits that is not an existing date does not pass as a check date."""
    lines = [FACTS_HEADING, "F-5. The environment runs on Python 3.13. | cmd:`python --version` -> `Python 3.13.14` | 2026-13-45"]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert "2026-13-45" in violations[0].reason


def test_resolve_fact_violations_ignores_a_document_without_the_section() -> None:
    """Ensures that a missing Facts section does not produce a report out of thin air."""
    assert resolve_fact_violations("PLAN.md", ["# Plan", "", "## Goal", "F-1. This stands outside the Facts section."]) == []


def test_resolve_open_question_violations_accepts_a_statement_of_absence() -> None:
    """Ensures that a sentence about the absence of questions is the record of an empty section, not an item."""
    lines = [OPEN_QUESTIONS_HEADING, "", "None. All items were resolved in the shape phase.", "", "## Supplementary files"]

    assert resolve_open_question_violations("PLAN.md", lines) == []


def test_resolve_open_question_violations_flags_a_list_item() -> None:
    """Ensures that a real question written as a list item stops the check."""
    lines = [OPEN_QUESTIONS_HEADING, "", "None settled yet in two places.", "", "- Does the consumer guarantee key uniqueness?"]

    violations = resolve_open_question_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].line_number == 5


def test_resolve_open_question_violations_flags_a_paragraph_other_than_absence() -> None:
    """Ensures that a paragraph not opening with a statement of absence is reported."""
    lines = [OPEN_QUESTIONS_HEADING, "We are waiting for an answer about the alert channel."]

    violations = resolve_open_question_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].line_number == 2


def test_build_violation_report_keeps_the_header_and_every_violation() -> None:
    """Ensures that the message carries the header and one line for every violation."""
    violations = [
        FactViolation(path="plans/x/PLAN.md", line_number=12, identifier="F-1", reason="missing evidence."),
        OpenQuestionViolation(path="plans/x/PLAN.md", line_number=40, reason="list item."),
    ]

    report = build_violation_report("Header:", violations)

    assert report.splitlines() == ["Header:", "plans/x/PLAN.md:12 - F-1: missing evidence.", "plans/x/PLAN.md:40 - list item."]
