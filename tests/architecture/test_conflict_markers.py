"""
Pilnuje, że żaden plik tekstowy repozytorium nie niesie markerów konfliktu scalenia wpisanych do treści.

Konflikt tekstowy wykrywa hosting repozytorium i blokuje nim Merge Requesta sam, ale marker rozwiązany źle i scalony
jako zwykła treść przechodzi dalej niezauważony. `ruff` łapie go wyłącznie w kodzie Python i tylko poza
literałem napisu - w docstringu marker jest poprawną treścią. Markdown, YAML, pliki compose, `makefile`
i SQL nie mają dziś żadnego czytelnika, który by go zobaczył. Marker w `makefile` wystarczy, żeby żaden
cel `make` nie był uruchamialny.

Test skanuje każdy plik tekstowy, także Python, a nie wyłącznie te, których `ruff` nie czyta - z powodu
docstringów wyżej. Za plik binarny uznaje plik zawierający bajt zerowy i pomija go, bo marker w nim
nie jest treścią, którą ktokolwiek scala ręcznie. Skan idzie na bajtach, bez dekodowania, więc plik
w innym kodowaniu niż UTF-8 nie przerywa testu.

Pliki lokalnej konfiguracji wchodzą do skanu, bo marker w nich psuje środowisko tak samo, ale zgłoszenie
podaje wyłącznie ścieżkę, numer linii i rodzaj markera - nigdy treść linii.

Rozpoznawane są trzy markery: otwierający (siedem znaków mniejszości), zamykający (siedem znaków
większości) i znacznik wspólnego przodka stylu diff3 (siedem kresek pionowych), każdy na początku linii
i zakończony spacją albo końcem linii. Separator z siedmiu znaków równości świadomie nie jest
rozpoznawany: taka linia jest też poprawnym podkreśleniem nagłówka w markdownie, a konflikt zostawiający
wyłącznie separator bez obu markerów otaczających nie powstaje przy żadnym rozwiązaniu, które zaczyna
się od treści wygenerowanej przez gita.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

EXCLUDED_DIRECTORY_NAMES: frozenset[str] = frozenset({".venv", "venv", ".git", ".cache", "__pycache__", "build", "dist", "node_modules", "temp", ".context"})
EXCLUDED_DIRECTORY_PREFIXES: tuple[str, ...] = ("pytest_tmp",)
"""
Powtarza wykluczenia katalogów z `test_prose_style.py`, żeby oba skany repozytorium zgadzały się co do
tego, co jest treścią repozytorium, a co artefaktem środowiska albo narzędzia. Lista jest powtórzona,
nie importowana, bo pomocniki testu infrastruktury zostają w jego własnym pliku
(`docs/standards/naming_registry.md`, rozdział Nazwy w testach).
"""

MARKER_LENGTH = 7

CONFLICT_MARKER_PATTERN = re.compile(rb"^(?P<marker><{7}|>{7}|\|{7})(?: [^\n]*)?\r?$", re.MULTILINE)
"""
Linia zaczynająca się od jednego z trzech markerów gita, po którym stoi spacja z etykietą albo koniec
linii. Ósmy znak tego samego rodzaju nie jest markerem, więc linia z ośmioma znakami większości, na
przykład zagnieżdżony cytat, nie jest zgłaszana.
"""

MARKER_KINDS: dict[bytes, str] = {b"<" * MARKER_LENGTH: "otwierający", b">" * MARKER_LENGTH: "zamykający", b"|" * MARKER_LENGTH: "wspólnego przodka"}

BINARY_FILE_SIGNATURE = b"\x00"


@dataclass(frozen=True)
class ConflictMarkerViolation:
    """
    Jedno wystąpienie markera konfliktu: plik, linia i rodzaj markera, bez treści linii.
    """

    path: str
    line_number: int
    marker_kind: str

    @property
    def report_line(self) -> str:
        """
        Składa jedną linię raportu wskazującą, gdzie stoi marker i jakiego jest rodzaju.
        """
        return f"  {self.path}:{self.line_number} - marker {self.marker_kind}"


def fetch_scanned_files(root: Path) -> list[Path]:
    """
    Zwraca posortowaną listę wszystkich plików pod `root`, z pominięciem katalogów narzędziowych
    wykluczonych tak samo jak w skanie stylu prozy.
    """
    scanned_files: list[Path] = []

    for directory, directory_names, file_names in root.walk(on_error=lambda _: None):
        directory_names[:] = [name for name in directory_names if name not in EXCLUDED_DIRECTORY_NAMES and not name.startswith(EXCLUDED_DIRECTORY_PREFIXES)]
        scanned_files.extend(directory / name for name in file_names)

    return sorted(scanned_files)


def resolve_conflict_marker_violations(path: str, content: bytes) -> list[ConflictMarkerViolation]:
    """
    Wskazuje każdy marker konfliktu w treści jednego pliku. Plik binarny nie daje żadnego zgłoszenia.
    """
    if BINARY_FILE_SIGNATURE in content:
        return []

    violations: list[ConflictMarkerViolation] = []

    for match in CONFLICT_MARKER_PATTERN.finditer(content):
        line_number = content.count(b"\n", 0, match.start()) + 1
        violations.append(ConflictMarkerViolation(path=path, line_number=line_number, marker_kind=MARKER_KINDS[match.group("marker")]))

    return violations


def fetch_repository_violations(root: Path) -> list[ConflictMarkerViolation]:
    """
    Skanuje całe repozytorium i zbiera wszystkie markery konfliktu ze wszystkich plików tekstowych.
    """
    violations: list[ConflictMarkerViolation] = []

    for file_path in fetch_scanned_files(root):
        try:
            content = file_path.read_bytes()
        except OSError:
            continue

        violations.extend(resolve_conflict_marker_violations(file_path.relative_to(root).as_posix(), content))

    return violations


def build_violation_report(violations: Sequence[ConflictMarkerViolation]) -> str:
    """
    Składa komunikat nieudanego testu: nagłówek i po jednej linii na każdy znaleziony marker.
    """
    return "\n".join(["Markery konfliktu scalenia w treści plików - rozwiąż konflikt do końca:", *(violation.report_line for violation in violations)])


def build_marker_line(marker: bytes, label: bytes = b"") -> bytes:
    """
    Składa linię markera z opcjonalną etykietą, tak jak zapisuje ją git.
    """
    return marker + (b" " + label if label else b"")


def test_repository_has_no_conflict_markers() -> None:
    """
    Pilnuje, że żaden plik tekstowy repozytorium nie zawiera markera konfliktu na początku linii.
    """
    violations = fetch_repository_violations(ROOT_DIR)

    assert not violations, build_violation_report(violations)


def test_resolve_conflict_marker_violations_reports_each_marker_with_its_line() -> None:
    """
    Pilnuje, że pełny blok konfliktu w stylu diff3 daje trzy zgłoszenia z właściwymi numerami linii i rodzajami.
    """
    content = b"\n".join(
        [
            b"tytul",
            build_marker_line(b"<" * MARKER_LENGTH, b"HEAD"),
            b"nasza wersja",
            build_marker_line(b"|" * MARKER_LENGTH, b"merged common ancestors"),
            b"wersja przodka",
            b"=" * MARKER_LENGTH,
            b"ich wersja",
            build_marker_line(b">" * MARKER_LENGTH, b"origin/dev"),
            b"",
        ]
    )

    violations = resolve_conflict_marker_violations("plik.md", content)

    assert [(violation.line_number, violation.marker_kind) for violation in violations] == [(2, "otwierający"), (4, "wspólnego przodka"), (8, "zamykający")]


def test_resolve_conflict_marker_violations_flags_marker_without_label_and_with_crlf() -> None:
    """
    Pilnuje, że marker bez etykiety i marker zakończony końcem linii Windows są zgłaszane tak samo.
    """
    content = b"\r\n".join([b"a", b"<" * MARKER_LENGTH, b"b", build_marker_line(b">" * MARKER_LENGTH, b"feature"), b""])

    violations = resolve_conflict_marker_violations("compose.yaml", content)

    assert [violation.line_number for violation in violations] == [2, 4]


def test_resolve_conflict_marker_violations_ignores_setext_underline() -> None:
    """
    Pilnuje, że podkreślenie nagłówka w markdownie z siedmiu znaków równości nie jest zgłaszane.
    """
    content = b"Naglowek\n" + b"=" * MARKER_LENGTH + b"\n\ntresc\n"

    assert resolve_conflict_marker_violations("plik.md", content) == []


def test_resolve_conflict_marker_violations_ignores_marker_not_starting_the_line() -> None:
    """
    Pilnuje, że marker zacytowany w środku linii, na przykład w dokumentacji o konfliktach, nie jest zgłaszany.
    """
    content = b"Linia z markerem `" + b"<" * MARKER_LENGTH + b"` w cytacie.\n"

    assert resolve_conflict_marker_violations("plik.md", content) == []


def test_resolve_conflict_marker_violations_ignores_longer_run_of_the_same_character() -> None:
    """
    Pilnuje, że osiem znaków większości na początku linii, czyli zagnieżdżony cytat, nie jest markerem.
    """
    content = b">" * (MARKER_LENGTH + 1) + b" cytat\n"

    assert resolve_conflict_marker_violations("plik.md", content) == []


def test_resolve_conflict_marker_violations_skips_binary_content() -> None:
    """
    Pilnuje, że plik z bajtem zerowym jest traktowany jako binarny i nie daje zgłoszeń mimo markera w treści.
    """
    content = BINARY_FILE_SIGNATURE + b"\n" + build_marker_line(b"<" * MARKER_LENGTH, b"HEAD") + b"\n"

    assert resolve_conflict_marker_violations("obraz.png", content) == []


def test_repository_scan_reports_marker_planted_in_a_scanned_file(tmp_path: Path) -> None:
    """
    Pilnuje, że skan katalogu znajduje marker w pliku compose, ale pomija ten sam marker w katalogu wykluczonym.
    """
    marker_line = build_marker_line(b"<" * MARKER_LENGTH, b"HEAD") + b"\n"
    (tmp_path / "compose.yaml").write_bytes(b"services:\n" + marker_line)
    excluded_directory = tmp_path / "node_modules"
    excluded_directory.mkdir()
    (excluded_directory / "README.md").write_bytes(marker_line)

    violations = fetch_repository_violations(tmp_path)

    assert [(violation.path, violation.line_number) for violation in violations] == [("compose.yaml", 2)]
