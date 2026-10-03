"""
Pilnuje dwóch reguł ze `standard_formatting.md`, których nie sprawdza żaden inny linter
skonfigurowany dziś w repozytorium: znaków zakazanych oraz pogrubienia w prozie poza nagłówkiem
i komórką tabeli. `ruff format` sprawdza formatowanie kodu Python, ale świadomie pomija pliki
markdown (`extend-exclude` w `pyproject.toml`) i nie zna wcale reguły o pogrubieniach.

Reguła jest pilnowana testem, a nie osobnym narzędziem wołanym z linii poleceń, bo test wchodzi
do `make test`, a przez to do `make check` i do mapy standard - narzędzie weryfikujące
w `standard_review.md`. Dzięki temu odpala się sam przy implementacji i przy review, zamiast być
targetem, o którego wywołaniu trzeba pamiętać osobno.
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
Powtarza `exclude` z `[tool.ruff]` w `pyproject.toml`, żeby oba narzędzia zgadzały się co do tego,
co jest kodem i dokumentacją repozytorium, a co artefaktem środowiska albo narzędzia. `node_modules`
to lokalna instalacja prettiera z `package.json`, z własną dokumentacją pakietu w cudzym stylu.
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
    (0x00B7, ". albo -, zależnie od kontekstu"),
    (0x2192, "->"),
    (0x2190, "<-"),
    (0x2194, "<->"),
    (0x00D7, "x albo *, zależnie od kontekstu"),
    (0x0430, "a (zwykłe łacińskie)"),
    (0x037E, "; (zwykły średnik)"),
    (0x2215, "/"),
)
"""
Punkt kodowy -> podpowiedź zastąpienia, jeden do jednego z listą w `standard_formatting.md`,
sekcja Znaki zakazane. Klucze są punktami kodowymi, nie dosłownymi znakami - inaczej ten plik
sam zawierałby każdy zakazany znak i sam siebie zgłaszałby jako naruszenie przy własnym skanie.
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

EMOJI_REPLACEMENT_HINT = "usuń - emotikony są niedozwolone"

FORMATTING_STANDARD_PATH = "docs/standards/standard_formatting.md"

RULE_DEFINING_PATHS: frozenset[str] = frozenset({"AGENTS.md", "CLAUDE.md", FORMATTING_STANDARD_PATH})
"""
Te trzy pliki dokumentują listę znaków zakazanych wprost i muszą przez to cytować je dosłownie -
to jest treść definicji reguły, nie jej naruszenie. Standard niesie listę pełną, `AGENTS.md`
i `CLAUDE.md` skróconą do twardych zakazów stosowalnych bez kontekstu; ten rozjazd jest zamierzony
i opisany w samym standardzie, sekcja Zakres i granice.

Wyjątek jest wąski, wymienia każdy plik z osobna i dotyczy wyłącznie znaków - reguła o pogrubieniach
obowiązuje w tych plikach normalnie. Dwa testy niżej pilnują, żeby nie zamienił się w cichą furtkę.
"""

_HEADER_LINE_PATTERN = re.compile(r"^#{1,6}\s")
_TABLE_ROW_PATTERN = re.compile(r"^\s*\|")
_BOLD_SPAN_PATTERN = re.compile(r"\*\*[^*\n]+\*\*")
_FENCE_MARKER_PATTERN = re.compile(r"^\s*```")
_BLOCKQUOTE_PREFIX_PATTERN = re.compile(r"^\s*(?:>\s*)+")
"""
Prefiks cytatu blokowego, zdejmowany przed rozpoznaniem rodzaju linii.

Bez tego cytat dosłowny wiersza tabeli z innego dokumentu wygląda jak proza, bo `_TABLE_ROW_PATTERN`
wymaga kreski pionowej na początku linii, a w cytacie stoi tam znak większości. Artefakty zadania
w `plans/` przepisują dosłownie wiersze tabel z innych dokumentów, razem z ich pogrubieniami, a seed jest
niemodyfikowalny - poprawka takiego cytatu jest niedostępna z definicji. `standard_formatting.md`
pogrubienie w komórce tabeli dozwala, a cytowanie tabeli nie zamienia jej komórek w prozę.

Wyjątek jest wąski celowo: zdejmowany jest wyłącznie prefiks, a rodzaj linii pod nim rozpoznaje ta
sama reguła co wszędzie. Pogrubienie w cytowanym zdaniu jest nadal zgłaszane, bo zdanie nie jest
strukturą dokumentu.
"""

BOLD_MARKED_LINE = "To jest **pogrubiona** fraza w środku zdania."
"""Wejście testowe dla reguły pogrubienia, wspólne dla czterech przypadków niżej."""


@dataclass(frozen=True)
class ForbiddenCharacterViolation:
    """
    Wystąpienie znaku z listy zakazanej (`standard_formatting.md`, sekcja Znaki zakazane)
    w konkretnym pliku i linii.

    `replacement_hint` niesie gotową podpowiedź, czym zastąpić znak - dokładnie tę, którą standard
    przypisuje temu konkretnemu znakowi, żeby wynik dało się poprawić bez ponownego otwierania
    standardu.
    """

    path: str
    line_number: int
    character: str
    replacement_hint: str

    @property
    def report_line(self) -> str:
        """Jedna linia komunikatu nieudanego testu, gotowa do wklejenia w wyszukiwarkę edytora."""
        return f"{self.path}:{self.line_number} - znak U+{ord(self.character):04X} ({self.character}), zamiennik: {self.replacement_hint}"


@dataclass(frozen=True)
class BoldInProseViolation:
    """
    Wystąpienie pogrubienia w prozie poza nagłówkiem i komórką tabeli (`standard_formatting.md`,
    sekcja Wyróżnienia w prozie), w konkretnym pliku i linii.
    """

    path: str
    line_number: int

    @property
    def report_line(self) -> str:
        """Jedna linia komunikatu nieudanego testu, gotowa do wklejenia w wyszukiwarkę edytora."""
        return f"{self.path}:{self.line_number} - pogrubienie w prozie poza nagłówkiem i komórką tabeli"


@dataclass(frozen=True)
class ProseStyleScanSummary:
    """
    Wynik jednego przebiegu skanu: liczba przejrzanych plików i wszystkie znalezione naruszenia.
    """

    scanned_file_count: int
    forbidden_character_violations: tuple[ForbiddenCharacterViolation, ...]
    bold_in_prose_violations: tuple[BoldInProseViolation, ...]

    @property
    def violated_paths(self) -> frozenset[str]:
        """
        Zbiór ścieżek, w których przebieg znalazł cokolwiek - bez rozróżnienia, którą z dwóch reguł
        naruszają. Plik jest czysty dopiero wtedy, gdy nie ma w nim ani znaku zakazanego, ani
        pogrubienia w prozie.
        """
        return frozenset(violation.path for violation in self.forbidden_character_violations) | frozenset(violation.path for violation in self.bold_in_prose_violations)


def fetch_scanned_files(root: Path) -> list[Path]:
    """
    Zwraca posortowaną listę plików .py i .md pod `root`, z pominięciem katalogów narzędziowych.
    """
    scanned_files: list[Path] = []

    for directory, directory_names, file_names in root.walk(on_error=lambda _: None):
        directory_names[:] = [name for name in directory_names if name not in EXCLUDED_DIRECTORY_NAMES and not name.startswith(EXCLUDED_DIRECTORY_PREFIXES)]
        scanned_files.extend(directory / name for name in file_names if Path(name).suffix in SCANNED_FILE_SUFFIXES)

    return sorted(scanned_files)


def resolve_forbidden_character_hint(character: str) -> str | None:
    """
    Klasyfikuje pojedynczy znak: zwraca podpowiedź zastąpienia dla znaku zakazanego albo emotikony,
    `None` dla znaku dozwolonego.
    """
    if character in FORBIDDEN_CHARACTERS:
        return FORBIDDEN_CHARACTERS[character]

    codepoint = ord(character)

    if any(start <= codepoint <= end for start, end in EMOJI_CODEPOINT_RANGES):
        return EMOJI_REPLACEMENT_HINT

    return None


def resolve_forbidden_character_violations(path: str, lines: list[str]) -> list[ForbiddenCharacterViolation]:
    """
    Wskazuje każde wystąpienie znaku zakazanego w podanych liniach pliku.
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
    Wskazuje linie pliku markdown, w których pogrubienie stoi poza nagłówkiem i komórką tabeli.

    Blok kodu ogrodzony potrójnym backtickiem jest pomijany w całości, bo `standard_formatting.md`
    sam ilustruje zakazany wzorzec przykładem markdown wewnątrz takiego bloku - bez tego wyjątku
    własny przykład standardu wyglądałby jak naruszenie reguły, którą opisuje.

    Prefiks cytatu blokowego jest zdejmowany przed rozpoznaniem rodzaju linii, więc cytowany dosłownie
    wiersz tabeli jest wierszem tabeli, a cytowany nagłówek nagłówkiem. Cytowane zdanie zostaje zdaniem
    i pogrubienie w nim jest nadal zgłaszane.
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
    Czyta wszystkie skanowane pliki spod `root` i zwraca podsumowanie przebiegu.
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
    Składa komunikat nieudanego testu: nagłówek mówiący, co poszło nie tak, i po jednej linii
    na naruszenie, każda ze ścieżką i numerem linii do poprawienia.
    """
    return "\n".join([header, *(violation.report_line for violation in violations)])


@pytest.fixture(scope="module")
def repository_scan() -> ProseStyleScanSummary:
    """
    Skanuje całe repozytorium raz na moduł. Pojedynczy przebieg zajmuje ponad sekundę, a wszystkie
    trzy testy poniżej pytają o ten sam stan - powtarzanie skanu dla każdego z nich potroiłoby
    ten koszt bez żadnej korzyści.
    """
    return fetch_prose_style_summary(ROOT_DIR)


def test_repository_has_no_forbidden_characters(repository_scan: ProseStyleScanSummary) -> None:
    """
    Pilnuje, że żaden plik .py ani .md w repozytorium nie zawiera znaku z listy zakazanej
    ani emotikony.

    Test nie ma listy wyjątków poza `RULE_DEFINING_PATHS` i taki ma zostać: dopisanie do niego
    wyjątku dla dokumentu, którego nie chciało się poprawić, zamienia gate w listę życzeń.
    """
    violations = repository_scan.forbidden_character_violations

    assert not violations, build_violation_report("Znaki zakazane ze standard_formatting.md, sekcja Znaki zakazane:", violations)


def test_repository_has_no_bold_in_prose(repository_scan: ProseStyleScanSummary) -> None:
    """
    Pilnuje, że żaden plik .md w repozytorium nie ma pogrubienia w prozie - ciężar wyróżnienia
    bierze na siebie kolejność, nie krój pisma. Pogrubienie zostaje dozwolone tam, gdzie jest
    elementem struktury dokumentu: w nagłówku i w komórce tabeli.
    """
    violations = repository_scan.bold_in_prose_violations

    assert not violations, build_violation_report("Pogrubienia w prozie, wbrew standard_formatting.md, sekcja Wyróżnienia w prozie:", violations)


def test_formatting_standard_still_quotes_every_forbidden_character() -> None:
    """
    Pilnuje, że standard nadal cytuje dosłownie każdy znak, który sam wymienia, oraz emotikonę.

    Ten test broni wyjątku `RULE_DEFINING_PATHS` z drugiej strony niż test niżej. Znak zniknięty
    ze standardu, ale wciąż stojący w `FORBIDDEN_CHARACTER_REPLACEMENTS`, oznacza rozjazd reguły
    z narzędziem, które ją egzekwuje - a że standard jest wyjęty spod skanu znaków, nic innego
    tego rozjazdu nie zauważy. Zmiana samej listy w standardzie ma pociągnąć za sobą zmianę tabeli
    w tym pliku, i ten test jest miejscem, w którym się to spotyka.
    """
    text = (ROOT_DIR / FORMATTING_STANDARD_PATH).read_text(encoding="utf-8")
    missing_characters = [f"U+{codepoint:04X}" for codepoint, _ in FORBIDDEN_CHARACTER_REPLACEMENTS if chr(codepoint) not in text]

    assert not missing_characters, f"{FORMATTING_STANDARD_PATH} przestał cytować znaki, które sam definiuje: {missing_characters}"
    assert any(resolve_forbidden_character_hint(character) == EMOJI_REPLACEMENT_HINT for character in text), f"{FORMATTING_STANDARD_PATH} przestał pokazywać przykładową emotikonę"


def test_every_rule_defining_path_still_needs_its_exemption() -> None:
    """
    Pilnuje, że każdy plik wyjęty spod skanu znaków nadal cytuje choć jeden znak zakazany.

    Wyjątek istnieje wyłącznie po to, żeby dokument mógł cytować to, co definiuje. Plik, który
    przestał cokolwiek cytować, wyjątku nie potrzebuje - a wyjątek bez uzasadnienia po cichu
    przepuszcza wszystko, co ktoś do tego pliku wklei później.
    """
    unnecessary_paths: list[str] = []

    for relative_path in sorted(RULE_DEFINING_PATHS):
        text = (ROOT_DIR / relative_path).read_text(encoding="utf-8")

        if not any(resolve_forbidden_character_hint(character) for character in text):
            unnecessary_paths.append(relative_path)

    assert not unnecessary_paths, f"Te pliki nie cytują już żadnego znaku zakazanego - usuń je z RULE_DEFINING_PATHS: {unnecessary_paths}"


def test_resolve_forbidden_character_hint_flags_every_character_from_the_standard() -> None:
    """Pilnuje, że każdy znak z listy standard_formatting.md dostaje podpowiedź zastąpienia."""
    for codepoint, _ in FORBIDDEN_CHARACTER_REPLACEMENTS:
        assert resolve_forbidden_character_hint(chr(codepoint)) is not None


def test_resolve_forbidden_character_hint_flags_emoji() -> None:
    """Pilnuje, że znak z zakresu emotikon dostaje podpowiedź, mimo że nie jest wpisany wprost."""
    checkmark_emoji = chr(0x2705)

    assert resolve_forbidden_character_hint(checkmark_emoji) == EMOJI_REPLACEMENT_HINT


def test_resolve_forbidden_character_hint_allows_plain_and_polish_characters() -> None:
    """
    Pilnuje, że zwykłe znaki ASCII i polskie znaki diakrytyczne nie są traktowane jako zakazane.

    To jest test na odmowę: gdyby zakresy emotikon albo mapa znaków zakazanych przypadkiem
    objęły polskie litery, każdy dokument tego repozytorium zacząłby fałszywie nie przechodzić.
    """
    for character in "aZ9-.,\"'ąćęłńóśźż":
        assert resolve_forbidden_character_hint(character) is None


def test_resolve_forbidden_character_violations_reports_line_and_character() -> None:
    """Pilnuje, że naruszenie niesie właściwy numer linii, znak i podpowiedź zastąpienia."""
    lines = ["pierwsza linia bez niczego", f"druga linia z myślnikiem em {chr(0x2014)} w środku"]

    violations = resolve_forbidden_character_violations("dokument.md", lines)

    assert len(violations) == 1
    assert violations[0].line_number == 2
    assert violations[0].character == chr(0x2014)
    assert violations[0].replacement_hint == "-"


def test_resolve_bold_in_prose_violations_flags_bold_outside_header_and_table() -> None:
    """Pilnuje, że pogrubienie w środku zwykłego zdania jest zgłaszane."""
    violations = resolve_bold_in_prose_violations("dokument.md", [BOLD_MARKED_LINE])

    assert len(violations) == 1
    assert violations[0].line_number == 1


def test_resolve_bold_in_prose_violations_allows_bold_in_header() -> None:
    """Pilnuje, że pogrubienie w nagłówku jest dozwolone i nie jest zgłaszane."""
    lines = [f"## {BOLD_MARKED_LINE}"]

    assert resolve_bold_in_prose_violations("dokument.md", lines) == []


def test_resolve_bold_in_prose_violations_allows_bold_in_table_row() -> None:
    """Pilnuje, że pogrubienie w komórce tabeli jest dozwolone i nie jest zgłaszane."""
    lines = [f"| {BOLD_MARKED_LINE} | drugi wiersz |"]

    assert resolve_bold_in_prose_violations("dokument.md", lines) == []


def test_resolve_bold_in_prose_violations_allows_bold_in_quoted_table_row() -> None:
    """
    Pilnuje, że pogrubienie w komórce tabeli cytowanej dosłownie jest dozwolone.

    Artefakty zadania przepisują wiersze tabel z innych dokumentów razem z ich pogrubieniami, a seed jest
    niemodyfikowalny - poprawka takiego cytatu jest niedostępna z definicji.
    """
    lines = [f"> | {BOLD_MARKED_LINE} | drugi wiersz |"]

    assert resolve_bold_in_prose_violations("dokument.md", lines) == []


def test_resolve_bold_in_prose_violations_flags_bold_in_quoted_sentence() -> None:
    """Pilnuje, że zdjęcie prefiksu cytatu nie przepuszcza pogrubienia w cytowanym zdaniu - zdanie nie jest strukturą dokumentu."""
    violations = resolve_bold_in_prose_violations("dokument.md", [f"> {BOLD_MARKED_LINE}"])

    assert len(violations) == 1
    assert violations[0].line_number == 1


def test_resolve_bold_in_prose_violations_ignores_fenced_code_block() -> None:
    """
    Pilnuje, że pogrubienie wewnątrz bloku kodu ogrodzonego potrójnym backtickiem jest pomijane.

    standard_formatting.md ilustruje zakazany wzorzec przykładem markdown w takim bloku - bez tego
    wyjątku własny przykład standardu wyglądałby jak naruszenie reguły, którą opisuje.
    """
    lines = ["```markdown", BOLD_MARKED_LINE, "```"]

    assert resolve_bold_in_prose_violations("dokument.md", lines) == []


def test_fetch_scanned_files_skips_excluded_directories(tmp_path: Path) -> None:
    """Pilnuje, że pliki w katalogach narzędziowych (np. venv) nie trafiają do skanu."""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "settings.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "venv" / "lib").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "site.py").write_text("y = 2\n", encoding="utf-8")

    scanned = fetch_scanned_files(tmp_path)

    assert tmp_path / "config" / "settings.py" in scanned
    assert not any("venv" in path.parts for path in scanned)


def test_fetch_scanned_files_finds_only_python_and_markdown_files(tmp_path: Path) -> None:
    """Pilnuje, że pliki spoza .py i .md (np. .txt) nie trafiają do skanu."""
    (tmp_path / "notatka.txt").write_text("tresc\n", encoding="utf-8")
    (tmp_path / "dokument.md").write_text("# tytul\n", encoding="utf-8")

    scanned = fetch_scanned_files(tmp_path)

    assert scanned == [tmp_path / "dokument.md"]


def test_fetch_prose_style_summary_excludes_the_files_that_define_the_forbidden_character_list(tmp_path: Path) -> None:
    """
    Pilnuje, że AGENTS.md, CLAUDE.md i standard_formatting.md nie są zgłaszane za cytowanie
    znaków, które same definiują - to jest treść reguły, nie jej naruszenie.
    """
    forbidden_character = chr(0x2014)
    (tmp_path / "AGENTS.md").write_text(f"Nie używaj znaku {forbidden_character}.\n", encoding="utf-8")
    (tmp_path / "docs" / "standards").mkdir(parents=True)
    (tmp_path / "docs" / "standards" / "standard_formatting.md").write_text(f"- `{forbidden_character}` (U+2014).\n", encoding="utf-8")
    (tmp_path / "inny_dokument.md").write_text(f"Tu jest ten sam znak {forbidden_character} przypadkiem.\n", encoding="utf-8")

    summary = fetch_prose_style_summary(tmp_path)

    assert {violation.path for violation in summary.forbidden_character_violations} == {"inny_dokument.md"}


def test_fetch_prose_style_summary_reports_nothing_for_a_clean_document(tmp_path: Path) -> None:
    """Pilnuje, że przebieg bez żadnego naruszenia nie zgłasza ani jednej ścieżki."""
    (tmp_path / "dokument.md").write_text("# Tytuł\n\nZwykła proza bez niczego zakazanego.\n", encoding="utf-8")

    summary = fetch_prose_style_summary(tmp_path)

    assert summary.violated_paths == frozenset()
    assert summary.scanned_file_count == 1
