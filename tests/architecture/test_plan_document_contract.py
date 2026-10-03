"""
Pilnuje reguł ze `standard_agent_docs.md`, sekcja Format PLAN, których nie sprawdza żadne inne
narzędzie w repozytorium: formatu pozycji w sekcji Fakty oraz pustej sekcji Otwarte pytania.

Zasięg kontroli jest wąski celowo. Obejmuje wyłącznie plany oznaczone markerem "plan zamknięty"
i nie starsze niż data wejścia reguły w życie. Plan w toku zostaje poza nią, żeby dokument pisany
na raty nie blokował niezwiązanej pracy na tym samym drzewie, a plan sprzed daty progowej zostaje
poza nią, bo retrofit wymagałby wpisania dat sprawdzenia, których dziś nikt nie zna - czyli złamania
reguły, którą ta kontrola wprowadza.

Granica jest jedna i warto ją nazwać przy samym kodzie: sprawdzana jest forma dowodu, nigdy jego
prawdziwość. Ustalenie zmyślone i zapisane w poprawnej formie przejdzie tę bramkę.
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
Cztery wzorce: dwie postacie nazwy w dwóch lokalizacjach. Repozytorium stosuje nazwę bez prefiksu
zadania, a standard i skille opisują wzorzec z prefiksem - kontrola przyjmująca tylko jedną z tych
form przestałaby widzieć dokumenty przy pierwszym artefakcie nazwanym drugą. Drugą lokalizacją jest
archiwum `plans_finished/` ze `standard_agentic_workflow.md`, rozdz. 4.6: plan zamknięty przenosi
się tam razem z całą inicjatywą i ma podlegać tej samej kontroli co przed przeniesieniem, inaczej
archiwizacja byłaby drogą obejścia bramki. Podwójna gwiazdka obejmuje podkatalogi zadań dopuszczone
w rozdz. 3.2 tego samego standardu, których wzorzec z jednym poziomem nie widział.
"""

RULE_EFFECTIVE_DATE = date(2026, 8, 17)
"""
Data wejścia reguły w życie, opisana w `standard_agent_docs.md`, sekcja Egzekwowanie. Projekt
założony z szablonu powstaje po tej dacie, więc kontrola obejmuje każdy jego plan zamknięty.
Stała, nie odczyt zegara systemowego: próg ruchomy zmieniałby zakres
kontroli z dnia na dzień, bez żadnej zmiany w repozytorium.
"""

CLOSED_STATE_MARKER = "plan zamknięty"
IN_PROGRESS_STATE_MARKER = "plan w toku"

EVIDENCE_PREFIXES: tuple[str, ...] = ("kod:", "cmd:", "db:", "dok:")
ASSUMPTION_MARKER = "ZAŁOŻENIE:"

FACTS_HEADING = "## Fakty"
OPEN_QUESTIONS_HEADING = "## Otwarte pytania"

NO_OPEN_QUESTIONS_PREFIX = "Brak"

FIELD_SEPARATOR = "|"
EVIDENCE_SEPARATOR = ";"
INLINE_CODE_MARKER = "`"
EXPECTED_FIELD_COUNT = 3

FACT_LINE_PATTERN = re.compile(r"^(F-\d+)\.\s+(\S.*)$")
STATE_LINE_PATTERN = re.compile(r"^Stan dokumentu:\s*(\d{4}-\d{2}-\d{2})\s*(?:,\s*(.+?))?\s*$")
CHECKED_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECTION_HEADING_PATTERN = re.compile(r"^##\s")
LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")

UNKNOWN_IDENTIFIER = "bez identyfikatora"


@dataclass(frozen=True)
class PlanDocumentState:
    """
    Stan dokumentu planu odczytany z linii nagłówka: data oraz marker, jeśli linia go niesie.

    Brak markera nie jest tu naruszeniem - dokument bez niego po prostu zostaje poza zasięgiem
    kontroli, tak jak dokument oznaczony jako plan w toku.
    """

    state_date: date | None
    marker: str | None

    @property
    def is_under_gate(self) -> bool:
        """
        Mówi, czy dokument podlega kontroli. Rozstrzyga marker, a data dopiero w drugiej
        kolejności - plan w toku zostaje poza kontrolą niezależnie od tego, jak jest świeży.
        """
        if self.marker != CLOSED_STATE_MARKER:
            return False

        return self.state_date is not None and self.state_date >= RULE_EFFECTIVE_DATE


@dataclass(frozen=True)
class FactViolation:
    """
    Pozycja sekcji Fakty niezgodna z formatem, wraz z powodem odrzucenia gotowym do przeczytania
    bez otwierania standardu.
    """

    path: str
    line_number: int
    identifier: str
    reason: str

    @property
    def report_line(self) -> str:
        """Jedna linia komunikatu nieudanego testu, ze ścieżką, numerem linii i identyfikatorem."""
        return f"{self.path}:{self.line_number} - {self.identifier}: {self.reason}"


@dataclass(frozen=True)
class OpenQuestionViolation:
    """Treść w sekcji Otwarte pytania, która sprawia, że plan zamknięty ma ją niepustą."""

    path: str
    line_number: int
    reason: str

    @property
    def report_line(self) -> str:
        """Jedna linia komunikatu nieudanego testu, ze ścieżką i numerem linii."""
        return f"{self.path}:{self.line_number} - {self.reason}"


def fetch_plan_documents(root: Path) -> list[Path]:
    """
    Zwraca posortowaną listę dokumentów planu spod `root`, w obu konwencjach nazwy, z bieżącej
    pracy i z archiwum, także z podkatalogów zadań. Plik trafiony dwoma wzorcami liczy się raz.
    """
    documents: set[Path] = set()

    for pattern in PLAN_GLOB_PATTERNS:
        documents.update(path for path in root.glob(pattern) if path.is_file())

    return sorted(documents)


def fetch_document_state(path: Path) -> PlanDocumentState:
    """
    Czyta dokument i zwraca stan z pierwszej linii `Stan dokumentu`. Dokument bez takiej linii
    albo z datą, której nie da się odczytać, dostaje stan pusty i przez to zostaje poza kontrolą.
    """
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STATE_LINE_PATTERN.match(line.strip())

        if match is not None:
            return PlanDocumentState(state_date=resolve_readable_date(match.group(1)), marker=match.group(2))

    return PlanDocumentState(state_date=None, marker=None)


def resolve_readable_date(text: str) -> date | None:
    """
    Zwraca datę odczytaną z tekstu albo `None`, gdy tekst jest samym układem cyfr i kresek,
    a nie istniejącą datą.
    """
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def resolve_section_lines(lines: Sequence[str], heading: str) -> list[tuple[int, str]]:
    """
    Wycina linie jednej sekcji dokumentu wraz z ich numerami, od nagłówka `heading` do następnego
    nagłówka tego samego poziomu. Sam nagłówek nie wchodzi do wyniku.
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
    Wskazuje pozycje sekcji Fakty, które nie mają kształtu wymaganego przez standard: identyfikatora
    z twierdzeniem, dowodu jednego z pięciu rodzajów i daty sprawdzenia, w trzech polach rozdzielonych
    kreską pionową.

    Każda pozycja dostaje najwyżej jedno zgłoszenie, z pierwszym napotkanym powodem - komunikat ma
    powiedzieć, co poprawić, a nie wyliczyć wszystkie skutki tej samej pomyłki.
    """
    violations: list[FactViolation] = []

    for line_number, line in resolve_section_lines(lines, FACTS_HEADING):
        position = line.strip()

        if not position:
            continue

        identifier_match = FACT_LINE_PATTERN.match(position)

        if identifier_match is None:
            violations.append(
                FactViolation(path=path, line_number=line_number, identifier=UNKNOWN_IDENTIFIER, reason="linia sekcji Fakty nie jest pozycją ustalenia - brakuje identyfikatora w kształcie F-N.")
            )
            continue

        identifier = identifier_match.group(1)
        fields = resolve_separated_fields(position, FIELD_SEPARATOR)

        if len(fields) != EXPECTED_FIELD_COUNT:
            violations.append(
                FactViolation(
                    path=path, line_number=line_number, identifier=identifier, reason=f"pozycja ma {len(fields)} pól zamiast trzech rozdzielonych kreską pionową: twierdzenie, dowód, data sprawdzenia."
                )
            )
            continue

        claim, evidence_field, checked_date = fields

        if FACT_LINE_PATTERN.match(claim) is None:
            violations.append(FactViolation(path=path, line_number=line_number, identifier=identifier, reason="identyfikator stoi bez twierdzenia - pierwsze pole ma nieść treść ustalenia."))
            continue

        unknown_evidence = resolve_unknown_evidence(evidence_field)

        if unknown_evidence is not None:
            violations.append(FactViolation(path=path, line_number=line_number, identifier=identifier, reason=f"dowód nie zaczyna się od żadnego z pięciu dozwolonych rodzajów: {unknown_evidence!r}."))
            continue

        if CHECKED_DATE_PATTERN.match(checked_date) is None or resolve_readable_date(checked_date) is None:
            violations.append(FactViolation(path=path, line_number=line_number, identifier=identifier, reason=f"data sprawdzenia nie jest datą w formacie RRRR-MM-DD: {checked_date!r}."))

    return violations


def resolve_separated_fields(text: str, separator: str) -> list[str]:
    """
    Dzieli tekst separatorem i przycina białe znaki, pomijając wystąpienia separatora stojące
    wewnątrz zapisu w backtickach.

    Wyjątek dla backticków nie jest kosmetyczny: dowód potrafi cytować komendę z regexem albo
    zapytanie z własnym średnikiem, a dosłowność cytatu jest tu ważniejsza niż prostota podziału.
    Bez tego wyjątku format wymuszałby przepisanie komendy, która faktycznie została uruchomiona.
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
    Zwraca pierwszy dowód, który nie otwiera się żadnym z pięciu dozwolonych rodzajów, albo `None`,
    gdy całe pole jest poprawne. Kilka dowodów przy jednej pozycji rozdziela średnik.
    """
    allowed_openings = (*EVIDENCE_PREFIXES, ASSUMPTION_MARKER)

    for evidence in resolve_separated_fields(evidence_field, EVIDENCE_SEPARATOR):
        if not evidence.startswith(allowed_openings):
            return evidence

    return None


def resolve_open_question_violations(path: str, lines: Sequence[str]) -> list[OpenQuestionViolation]:
    """
    Wskazuje treść, przez którą sekcja Otwarte pytania przestaje być pusta: pozycję listy oraz
    pierwszy akapit inny niż stwierdzenie braku.

    Zdanie zaczynające się od słowa Brak jest zapisem pustej sekcji, nie pozycją - dziewięć z dziesięciu
    planów istniejących w chwili powstania tej kontroli zapisuje brak właśnie tak.
    """
    violations: list[OpenQuestionViolation] = []
    section_lines = [(line_number, line.strip()) for line_number, line in resolve_section_lines(lines, OPEN_QUESTIONS_HEADING) if line.strip()]

    for position, (line_number, line) in enumerate(section_lines):
        if LIST_ITEM_PATTERN.match(line):
            violations.append(OpenQuestionViolation(path=path, line_number=line_number, reason="sekcja Otwarte pytania planu zamkniętego ma pozycję listy."))
            continue

        if position == 0 and not line.startswith(NO_OPEN_QUESTIONS_PREFIX):
            violations.append(
                OpenQuestionViolation(
                    path=path,
                    line_number=line_number,
                    reason=f"sekcja Otwarte pytania planu zamkniętego nie otwiera się stwierdzeniem braku - oczekiwano akapitu zaczynającego się od {NO_OPEN_QUESTIONS_PREFIX!r}.",
                )
            )

    return violations


def build_violation_report(header: str, violations: Sequence[FactViolation | OpenQuestionViolation]) -> str:
    """
    Składa komunikat nieudanego testu: nagłówek mówiący, co poszło nie tak, i po jednej linii
    na naruszenie, każda ze ścieżką i numerem linii do poprawienia.
    """
    return "\n".join([header, *(violation.report_line for violation in violations)])


@pytest.fixture(scope="module")
def gated_plan_documents() -> list[tuple[str, list[str]]]:
    """
    Zwraca ścieżkę i linie każdego dokumentu planu objętego kontrolą, czytając każdy plik raz
    na moduł zamiast raz na test.

    Pusta lista jest błędem, gdy repozytorium ma plany oznaczone jako zamknięte, a żaden nie
    przechodzi progu daty: kontrola, która nie widzi ani jednego dokumentu, wygląda wtedy na
    działającą i nie pilnuje niczego. Gdy repozytorium nie ma jeszcze żadnego planu zamkniętego,
    jak świeży projekt z szablonu, testy korzystające z tej fixture są pomijane z powodem
    widocznym w podsumowaniu przebiegu.
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
        pytest.skip(f"Repozytorium nie ma jeszcze planu oznaczonego {CLOSED_STATE_MARKER!r} - kontrola zacznie działać z pierwszym takim planem.")

    assert documents, f"Żaden plan zamknięty nie jest objęty kontrolą - sprawdź próg {RULE_EFFECTIVE_DATE.isoformat()}"

    return documents


def test_every_closed_plan_states_evidence_for_each_fact(gated_plan_documents: list[tuple[str, list[str]]]) -> None:
    """
    Pilnuje, że każda pozycja sekcji Fakty w planie zamkniętym niesie identyfikator, twierdzenie,
    dowód jednego z pięciu rodzajów i datę sprawdzenia.
    """
    violations: list[FactViolation] = []

    for path, lines in gated_plan_documents:
        violations.extend(resolve_fact_violations(path, lines))

    assert not violations, build_violation_report("Pozycje sekcji Fakty niezgodne ze standard_agent_docs.md, sekcja Format PLAN:", violations)


def test_every_closed_plan_has_no_open_questions(gated_plan_documents: list[tuple[str, list[str]]]) -> None:
    """
    Pilnuje, że plan oznaczony jako zamknięty ma pustą sekcję Otwarte pytania - dokument z realnym
    pytaniem w środku nie jest gotowy do podania do fazy implementacji.
    """
    violations: list[OpenQuestionViolation] = []

    for path, lines in gated_plan_documents:
        violations.extend(resolve_open_question_violations(path, lines))

    assert not violations, build_violation_report("Niepuste sekcje Otwarte pytania w planach zamkniętych, wbrew standard_agent_docs.md:", violations)


def write_plan_document(path: Path, content: str = "# Plan\n") -> Path:
    """Zapisuje dokument planu pod wskazaną ścieżką, tworząc brakujące katalogi inicjatywy."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return path


def test_fetch_plan_documents_finds_both_naming_conventions_in_both_locations(tmp_path: Path) -> None:
    """
    Pilnuje, że kontrola widzi nazwę stosowaną w repozytorium i nazwę opisaną w standardzie,
    w bieżącej pracy i w archiwum, także w podkatalogu zadania inicjatywy wielozadaniowej.
    """
    expected = [
        write_plan_document(tmp_path / "plans" / "bez_prefiksu" / "PLAN.md"),
        write_plan_document(tmp_path / "plans" / "z_prefiksem" / "ZADANIE_PLAN.md"),
        write_plan_document(tmp_path / "plans" / "wielozadaniowa" / "ZADANIE-2" / "ZADANIE-2_PLAN.md"),
        write_plan_document(tmp_path / "plans_finished" / "zamknieta_bez_prefiksu" / "PLAN.md"),
        write_plan_document(tmp_path / "plans_finished" / "zamknieta_z_prefiksem" / "ZADANIE_PLAN.md"),
        write_plan_document(tmp_path / "plans_finished" / "zamknieta_wielozadaniowa" / "ZADANIE-1" / "ZADANIE-1_PLAN.md"),
    ]

    assert fetch_plan_documents(tmp_path) == sorted(expected)


def test_fetch_plan_documents_reports_each_document_once(tmp_path: Path) -> None:
    """Pilnuje, że plik pasujący do więcej niż jednego wzorca nie wchodzi pod kontrolę dwa razy."""
    document = write_plan_document(tmp_path / "plans" / "inicjatywa" / "PLAN.md")

    assert fetch_plan_documents(tmp_path) == [document]


def test_fetch_plan_documents_treats_a_missing_archive_as_empty(tmp_path: Path) -> None:
    """Pilnuje, że brak katalogu archiwum nie jest błędem - repozytorium bez archiwizacji ma zwykłą listę."""
    document = write_plan_document(tmp_path / "plans" / "inicjatywa" / "PLAN.md")

    assert not (tmp_path / "plans_finished").exists()
    assert fetch_plan_documents(tmp_path) == [document]


def test_fetch_plan_documents_skips_other_artifacts(tmp_path: Path) -> None:
    """Pilnuje, że pozostałe artefakty łańcucha nie trafiają pod kontrolę formatu planu, w żadnej lokalizacji."""
    for location in ("plans", "plans_finished"):
        (tmp_path / location / "inicjatywa").mkdir(parents=True)
        (tmp_path / location / "inicjatywa" / "SHAPE.md").write_text("# Shape\n", encoding="utf-8")
        (tmp_path / location / "inicjatywa" / "PRD.md").write_text("# PRD\n", encoding="utf-8")
        (tmp_path / location / "inicjatywa" / "REVIEW.md").write_text("# Review\n", encoding="utf-8")

    assert fetch_plan_documents(tmp_path) == []


def test_archiving_a_faulty_closed_plan_keeps_its_violations(tmp_path: Path) -> None:
    """
    Pilnuje, że przeniesienie inicjatywy do archiwum nie jest drogą obejścia bramki: wadliwy plan
    zamknięty zgłasza po przeniesieniu te same naruszenia co przed nim, różniąc się tylko ścieżką.
    """
    faulty_plan = "\n".join(
        [
            "# Plan",
            "",
            f"Stan dokumentu: 2026-09-17, {CLOSED_STATE_MARKER}",
            "",
            FACTS_HEADING,
            "",
            "F-1. Ustalenie bez dowodu i daty.",
            "",
            OPEN_QUESTIONS_HEADING,
            "",
            "- Czy konsument gwarantuje unikalność klucza?",
            "",
        ]
    )
    active_path = write_plan_document(tmp_path / "plans" / "inicjatywa" / "PLAN.md", faulty_plan)

    def resolve_gated_violations() -> list[tuple[int, str]]:
        """Zbiera naruszenia każdego planu pod kontrolą jako pary linia-powód, bez ścieżki."""
        collected: list[tuple[int, str]] = []

        for path in fetch_plan_documents(tmp_path):
            assert fetch_document_state(path).is_under_gate
            lines = path.read_text(encoding="utf-8").splitlines()
            collected.extend((violation.line_number, violation.reason) for violation in resolve_fact_violations(path.name, lines))
            collected.extend((violation.line_number, violation.reason) for violation in resolve_open_question_violations(path.name, lines))

        return collected

    violations_before = resolve_gated_violations()
    assert len(violations_before) == 2

    archived_dir = tmp_path / "plans_finished" / "inicjatywa"
    archived_dir.parent.mkdir()
    active_path.parent.rename(archived_dir)

    assert not active_path.exists()
    assert fetch_plan_documents(tmp_path) == [archived_dir / "PLAN.md"]
    assert resolve_gated_violations() == violations_before


def test_fetch_document_state_reads_date_and_closed_marker(tmp_path: Path) -> None:
    """Pilnuje, że linia stanu z markerem zamknięcia wciąga dokument pod kontrolę."""
    path = tmp_path / "PLAN.md"
    path.write_text(f"# Plan\n\nStan dokumentu: 2026-08-17, {CLOSED_STATE_MARKER}\n", encoding="utf-8")

    state = fetch_document_state(path)

    assert state.state_date == date(2026, 8, 17)
    assert state.marker == CLOSED_STATE_MARKER
    assert state.is_under_gate


def test_fetch_document_state_leaves_a_plan_in_progress_outside_the_gate(tmp_path: Path) -> None:
    """Pilnuje, że plan w toku zostaje poza kontrolą, mimo daty po progu."""
    path = tmp_path / "PLAN.md"
    path.write_text(f"Stan dokumentu: 2026-12-31, {IN_PROGRESS_STATE_MARKER}\n", encoding="utf-8")

    assert not fetch_document_state(path).is_under_gate


def test_fetch_document_state_leaves_a_plan_older_than_the_rule_outside_the_gate(tmp_path: Path) -> None:
    """Pilnuje, że plan zamknięty sprzed daty wejścia reguły nie wymaga retrofitu."""
    path = tmp_path / "PLAN.md"
    path.write_text(f"Stan dokumentu: 2026-08-16, {CLOSED_STATE_MARKER}\n", encoding="utf-8")

    assert not fetch_document_state(path).is_under_gate


def test_fetch_document_state_leaves_a_plan_without_a_marker_outside_the_gate(tmp_path: Path) -> None:
    """Pilnuje, że dziesięć planów z samą datą w linii stanu zostaje poza kontrolą."""
    path = tmp_path / "PLAN.md"
    path.write_text("Stan dokumentu: 2026-08-18\n", encoding="utf-8")

    state = fetch_document_state(path)

    assert state.marker is None
    assert not state.is_under_gate


def test_resolve_fact_violations_accepts_a_well_formed_position() -> None:
    """Pilnuje, że pozycja z kompletem pól i dwoma dowodami przechodzi bez zgłoszenia."""
    lines = [
        FACTS_HEADING,
        "",
        "F-1. Sonda czyta adres z konfiguracji. | kod:`data/engine.py:31`; dok:`docs/standards/standard_config.md` par. Jedno miejsce odczytu | 2026-08-17",
        "",
        "## Decyzje",
        "F-2. To już nie jest fakt.",
    ]

    assert resolve_fact_violations("PLAN.md", lines) == []


def test_resolve_fact_violations_accepts_an_explicit_assumption() -> None:
    """Pilnuje, że jawnie oznaczone założenie jest dopuszczalnym rodzajem dowodu."""
    lines = [FACTS_HEADING, f"F-1. Konsument woła ten endpoint raz na minutę. | {ASSUMPTION_MARKER} brak pomiaru po stronie konsumenta | 2026-08-17"]

    assert resolve_fact_violations("PLAN.md", lines) == []


def test_resolve_fact_violations_accepts_a_separator_quoted_inside_inline_code() -> None:
    """
    Pilnuje, że kreska pionowa i średnik zacytowane w backtickach nie rozdzielają pól.

    Wejście jest wzięte z życia: dowód cytuje regex z kreską pionową, a bez tego wyjątku format
    kazałby przepisać komendę, która faktycznie została uruchomiona.
    """
    lines = [FACTS_HEADING, 'F-1. Parser TOML jest w bibliotece standardowej. | cmd:`rg "tomllib|tomli" --glob "*.py"` -> brak wystąpień | 2026-08-17']

    assert resolve_fact_violations("PLAN.md", lines) == []


def test_resolve_separated_fields_splits_only_outside_inline_code() -> None:
    """Pilnuje podziału po separatorze poza backtickami i braku podziału w środku cytatu."""
    assert resolve_separated_fields("a | `b | c` | d", FIELD_SEPARATOR) == ["a", "`b | c`", "d"]


def test_resolve_fact_violations_flags_a_position_without_evidence() -> None:
    """Pilnuje, że ustalenie zapisane jednym zdaniem, bez pól, jest zgłaszane wraz z identyfikatorem."""
    lines = [FACTS_HEADING, "F-1. Sonda czyta adres z konfiguracji. Źródło: data/engine.py."]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].identifier == "F-1"
    assert violations[0].line_number == 2


def test_resolve_fact_violations_flags_an_unknown_evidence_kind() -> None:
    """Pilnuje, że dowód spoza pięciu rodzajów jest zgłaszany razem ze swoją treścią."""
    lines = [FACTS_HEADING, "F-3. Serwis zwraca kod 409 przy powtórzeniu. | wiem z rozmowy | 2026-08-17"]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert "wiem z rozmowy" in violations[0].reason


def test_resolve_fact_violations_flags_a_second_evidence_without_its_kind() -> None:
    """Pilnuje, że dowód dopisany po średniku też musi nieść swój rodzaj."""
    lines = [FACTS_HEADING, "F-4. Kontrola typów nie obejmuje testów. | kod:`pyproject.toml` sekcja mypy; tak samo w drugim narzędziu | 2026-08-17"]

    assert len(resolve_fact_violations("PLAN.md", lines)) == 1


def test_resolve_fact_violations_flags_a_position_without_an_identifier() -> None:
    """Pilnuje, że akapit bez identyfikatora w sekcji Fakty jest zgłaszany."""
    lines = [FACTS_HEADING, "Ustalenia poniżej pochodzą z odczytu repozytorium."]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].identifier == UNKNOWN_IDENTIFIER


def test_resolve_fact_violations_flags_a_checked_date_that_is_not_a_date() -> None:
    """Pilnuje, że układ cyfr niebędący istniejącą datą nie przechodzi jako data sprawdzenia."""
    lines = [FACTS_HEADING, "F-5. Środowisko stoi na Pythonie 3.13. | cmd:`python --version` -> `Python 3.13.14` | 2026-13-45"]

    violations = resolve_fact_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert "2026-13-45" in violations[0].reason


def test_resolve_fact_violations_ignores_a_document_without_the_section() -> None:
    """Pilnuje, że brak sekcji Fakty nie produkuje zgłoszenia z powietrza."""
    assert resolve_fact_violations("PLAN.md", ["# Plan", "", "## Cel", "F-1. To stoi poza sekcją Fakty."]) == []


def test_resolve_open_question_violations_accepts_a_statement_of_absence() -> None:
    """Pilnuje, że zdanie o braku pytań jest zapisem pustej sekcji, nie pozycją."""
    lines = [OPEN_QUESTIONS_HEADING, "", "Brak. Wszystkie pozycje zostały rozstrzygnięte w fazie shape.", "", "## Pliki uzupełniające"]

    assert resolve_open_question_violations("PLAN.md", lines) == []


def test_resolve_open_question_violations_flags_a_list_item() -> None:
    """Pilnuje, że realne pytanie zapisane pozycją listy zatrzymuje kontrolę."""
    lines = [OPEN_QUESTIONS_HEADING, "", "Brak rozstrzygnięcia w dwóch miejscach.", "", "- Czy konsument gwarantuje unikalność klucza?"]

    violations = resolve_open_question_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].line_number == 5


def test_resolve_open_question_violations_flags_a_paragraph_other_than_absence() -> None:
    """Pilnuje, że akapit nieotwierający się stwierdzeniem braku jest zgłaszany."""
    lines = [OPEN_QUESTIONS_HEADING, "Czekamy na odpowiedź w sprawie kanału alertu."]

    violations = resolve_open_question_violations("PLAN.md", lines)

    assert len(violations) == 1
    assert violations[0].line_number == 2


def test_build_violation_report_keeps_the_header_and_every_violation() -> None:
    """Pilnuje, że komunikat niesie nagłówek i po jednej linii na każde naruszenie."""
    violations = [
        FactViolation(path="plans/x/PLAN.md", line_number=12, identifier="F-1", reason="brak dowodu."),
        OpenQuestionViolation(path="plans/x/PLAN.md", line_number=40, reason="pozycja listy."),
    ]

    report = build_violation_report("Nagłówek:", violations)

    assert report.splitlines() == ["Nagłówek:", "plans/x/PLAN.md:12 - F-1: brak dowodu.", "plans/x/PLAN.md:40 - pozycja listy."]
