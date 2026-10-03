from __future__ import annotations

import difflib
import re
import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

PLAN_REFERENCE = "docs/standards/standard_agentic_workflow.md rozdz. 6.2"
CODEX_ONLY_SKILLS: frozenset[str] = frozenset()
"""
Skille dopuszczone wyłącznie po stronie Codeksa. Zbiór jest pusty i taki ma zostać - warunki
dopisania wyjątku opisuje standard_agentic_workflow.md rozdz. 6.1.
"""

CODEX_ROLE_INSTRUCTIONS_KEY = "developer_instructions"
FRONTMATTER_MARKER = "---"
AGENT_ROLE_REFERENCE = "docs/standards/standard_agentic_workflow.md rozdz. 6.4"

_NORMALIZATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^# (AGENTS|CLAUDE)\.md$"), "# <ROOT>.md"),
    (re.compile(r"(Codex|Claude Code) ma stosować"), "<NARZĘDZIE> ma stosować"),
    (re.compile(r"\.claude/skills/[\w-]+/scripts/"), "scripts/"),
]

AGENT_ROLE_NORMALIZATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"przez `Bash` albo `PowerShell`|przez terminal"), "przez <URUCHAMIACZ>"),
]
"""
Jedyna dozwolona różnica między wariantem roli dla Claude Code a wariantem dla Codeksa: nazwa
narzędzia, którym rola uruchamia komendy. Jest realna, nie kosmetyczna - po stronie Claude Code
narzędzia nazywają się `Bash` i `PowerShell`, a Codex takich nazw nie zna. Każda inna różnica
ma być naprawiona w treści plików, nie ukryta dopisaniem drugiej pozycji na tę listę.
"""


def _normalize_line(line: str, normalizations: list[tuple[re.Pattern[str], str]]) -> str:
    """
    Zamienia znane, zamierzone różnice (nazwa narzędzia w rdzeniu, ścieżka
    do skryptu skilla, nazwa uruchamiacza komend w definicji roli) na wspólną
    formę, żeby diff widział tylko realne rozjazdy. Każda reguła na liście
    normalizacji to jedna świadomie dozwolona różnica - dopisanie kolejnej
    ma być decyzją, nie przypadkiem.
    """
    normalized = line

    for pattern, replacement in normalizations:
        normalized = pattern.sub(replacement, normalized)

    return normalized


def _normalized_lines(path: Path) -> list[str]:
    """
    Czyta plik i zwraca znormalizowane linie. Path.read_text robi uniwersalną
    translację końców linii do \\n, więc CRLF kontra LF nigdy nie jest różnicą.
    """
    return [_normalize_line(line, _NORMALIZATIONS) for line in path.read_text(encoding="utf-8").splitlines()]


def _real_differences(name_a: str, lines_a: list[str], name_b: str, lines_b: list[str]) -> list[str]:
    """
    Zwraca opisy realnych różnic między dwoma zestawami linii po normalizacji.
    Pusta lista znaczy pełny parytet. Używa difflib zamiast pozycji
    linia-po-linii, żeby wstawiona albo usunięta sekcja w jednym pliku nie
    rozjechała numeracji i nie wygenerowała fałszywych różnic dla reszty pliku.
    """
    matcher = difflib.SequenceMatcher(a=lines_a, b=lines_b, autojunk=False)
    differences: list[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        differences.append(f"{name_a} linia {i1 + 1}: {lines_a[i1:i2]!r}\n{name_b} linia {j1 + 1}: {lines_b[j1:j2]!r}")

    return differences


def _assert_parity(path_a: Path, path_b: Path, pair_name: str) -> None:
    """
    Asercja parytetu dla jednej pary plików, z odesłaniem do planu wdrożenia
    po listę dozwolonych wyjątków i uzasadnienie testu.
    """
    assert path_a.is_file(), f"Brak pliku {path_a} dla pary {pair_name}"
    assert path_b.is_file(), f"Brak pliku {path_b} dla pary {pair_name}"

    differences = _real_differences(path_a.name, _normalized_lines(path_a), path_b.name, _normalized_lines(path_b))
    assert not differences, f"Para {pair_name} rozjechała się poza dozwolone różnice:\n" + "\n".join(differences) + f"\nZobacz {PLAN_REFERENCE} po listę dozwolonych wyjątków."


def _strip_blank_edges(lines: list[str]) -> list[str]:
    """
    Odcina puste linie z początku i z końca listy. Wariant markdown ma pustą
    linię po frontmatterze i na końcu pliku, wariant TOML nie ma ani jednej -
    to różnica formatu, nie treści.
    """
    trimmed = list(lines)

    while trimmed and not trimmed[0].strip():
        trimmed.pop(0)

    while trimmed and not trimmed[-1].strip():
        trimmed.pop()

    return trimmed


def fetch_claude_role_instructions(path: Path) -> list[str]:
    """
    Czyta definicję roli po stronie Claude Code i zwraca same znormalizowane
    linie instrukcji, bez frontmatteru. Frontmatter niesie konfigurację
    narzędzia (lista narzędzi, tryb uprawnień, limit tur), która nie ma
    odpowiednika po stronie Codeksa i nie podlega parytetowi.
    """
    lines = path.read_text(encoding="utf-8").splitlines()

    if lines and lines[0].strip() == FRONTMATTER_MARKER:
        closing_index = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == FRONTMATTER_MARKER)
        lines = lines[closing_index + 1 :]

    return [_normalize_line(line, AGENT_ROLE_NORMALIZATIONS) for line in _strip_blank_edges(lines)]


def fetch_codex_role_instructions(path: Path) -> list[str]:
    """
    Czyta definicję roli po stronie Codeksa i zwraca znormalizowane linie
    z klucza `developer_instructions`.

    Porównanie idzie po wartości odczytanej parserem, nie po surowym tekście
    pliku: wartość niesie literalne sekwencje ucieczki końca linii, które
    parser zamienia na prawdziwe znaki, a surowy tekst pokazywałby je jako
    różnicę wobec wariantu markdown.
    """
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    instructions = document[CODEX_ROLE_INSTRUCTIONS_KEY]

    return [_normalize_line(line, AGENT_ROLE_NORMALIZATIONS) for line in _strip_blank_edges(instructions.splitlines())]


def _discover_skill_names(skills_dir: Path) -> set[str]:
    """
    Zwraca nazwy skilli (podkatalogów zawierających SKILL.md) w danym
    katalogu skills/.
    """
    if not skills_dir.is_dir():
        return set()

    return {entry.name for entry in skills_dir.iterdir() if entry.is_dir() and (entry / "SKILL.md").is_file()}


def _discover_role_names(roles_dir: Path, suffix: str) -> set[str]:
    """
    Zwraca nazwy ról (pliki o podanym rozszerzeniu) w danym katalogu definicji ról.
    """
    if not roles_dir.is_dir():
        return set()

    return {entry.stem for entry in roles_dir.iterdir() if entry.is_file() and entry.suffix == suffix}


def test_agents_and_claude_core_files_are_at_parity() -> None:
    """
    Pilnuje, że AGENTS.md i CLAUDE.md nie rozjadą się poza nazwę narzędzia -
    to samo repo ma czytać Codex i Claude Code, więc reguły muszą być
    identyczne.
    """
    _assert_parity(ROOT_DIR / "AGENTS.md", ROOT_DIR / "CLAUDE.md", "AGENTS.md / CLAUDE.md")


def test_every_local_skill_exists_in_both_claude_and_agents() -> None:
    """
    Pilnuje pełnego parytetu poza ścisłą listą zatwierdzonych skilli
    Codex-only i nie pozwala, aby allowlista ukrywała martwy wpis albo kopię
    utworzoną również po stronie Claude.
    """
    claude_skills = _discover_skill_names(ROOT_DIR / ".claude" / "skills")
    agents_skills = _discover_skill_names(ROOT_DIR / ".agents" / "skills")

    only_in_claude = sorted(claude_skills - agents_skills)
    only_in_agents = sorted((agents_skills - claude_skills) - CODEX_ONLY_SKILLS)

    assert not only_in_claude, f"Skille istnieją tylko w .claude/skills/, brakuje w .agents/skills/: {only_in_claude}"
    assert not only_in_agents, f"Nieznane skille istnieją tylko w .agents/skills/, brakuje w .claude/skills/: {only_in_agents}"
    assert agents_skills >= CODEX_ONLY_SKILLS, f"Allowlista Codex-only zawiera brakujące skille: {sorted(CODEX_ONLY_SKILLS - agents_skills)}"
    assert CODEX_ONLY_SKILLS.isdisjoint(claude_skills), f"Skill Codex-only ma niedozwoloną kopię w .claude/skills/: {sorted(CODEX_ONLY_SKILLS & claude_skills)}"


def test_every_paired_skill_is_at_parity() -> None:
    """
    Pilnuje, że treść każdego skilla istniejącego w obu lokalizacjach jest
    identyczna poza jawnie dozwolonymi różnicami, głównie ścieżkami do
    skryptów.
    """
    claude_skills_dir = ROOT_DIR / ".claude" / "skills"
    agents_skills_dir = ROOT_DIR / ".agents" / "skills"

    shared_skills = sorted(_discover_skill_names(claude_skills_dir) & _discover_skill_names(agents_skills_dir))

    assert shared_skills, "Nie znaleziono żadnej pary skilli do porównania - sprawdź, czy .claude/skills i .agents/skills istnieją"

    for skill_name in shared_skills:
        _assert_parity(
            claude_skills_dir / skill_name / "SKILL.md",
            agents_skills_dir / skill_name / "SKILL.md",
            skill_name,
        )


def test_every_paired_agent_role_is_at_parity() -> None:
    """
    Pilnuje, że instrukcja każdej roli agentowej brzmi tak samo w wariancie dla
    Claude Code i w wariancie dla Codeksa, poza jedyną jawnie dopuszczoną
    różnicą w nazwie uruchamiacza komend.

    Do tej pory zgodność obu wariantów pilnował wyłącznie człowiek i nie
    upilnował: obie pary ról rozjechały się treściowo, zanim ten test powstał.
    """
    claude_roles_dir = ROOT_DIR / ".claude" / "agents"
    codex_roles_dir = ROOT_DIR / ".codex" / "agents"

    claude_roles = _discover_role_names(claude_roles_dir, ".md")
    codex_roles = _discover_role_names(codex_roles_dir, ".toml")

    assert claude_roles, "Nie znaleziono żadnej definicji roli w .claude/agents - sprawdź, czy katalog istnieje"
    assert claude_roles == codex_roles, (
        f"Role bez pary: tylko w .claude/agents {sorted(claude_roles - codex_roles)}, tylko w .codex/agents {sorted(codex_roles - claude_roles)}. Zobacz {AGENT_ROLE_REFERENCE}."
    )

    for role_name in sorted(claude_roles):
        claude_path = claude_roles_dir / f"{role_name}.md"
        codex_path = codex_roles_dir / f"{role_name}.toml"

        differences = _real_differences(claude_path.name, fetch_claude_role_instructions(claude_path), codex_path.name, fetch_codex_role_instructions(codex_path))

        assert not differences, (
            f"Para ról {role_name} rozjechała się poza dozwolone różnice:\n" + "\n".join(differences) + f"\nZobacz {AGENT_ROLE_REFERENCE} po uzasadnienie i listę dozwolonych wyjątków."
        )
