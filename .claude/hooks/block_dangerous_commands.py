import json
import re
import sys
from pathlib import Path

RULES = [
    ("Zablokowano `git reset --hard`, bo może bezpowrotnie usunąć lokalne zmiany.", re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE)),
    ("Zablokowano `git clean`, bo usuwa nieśledzone pliki.", re.compile(r"\bgit\s+clean\b", re.IGNORECASE)),
    ("Zablokowano kasowanie katalogu `.git`.", re.compile(r"\b(rm|del|erase|remove-item|rmdir|rd)\b.*(^|[\\/\s])\.git([\\/\s]|$)", re.IGNORECASE)),
    ("Zablokowano kasowanie plików `.env`.", re.compile(r"\b(rm|del|erase|remove-item)\b.*(^|[\\/\s])\.env([.\s\\/*]|$)", re.IGNORECASE)),
    ("Zablokowano rekursywne kasowanie przez polecenie cmd z flagą `/s`.", re.compile(r"\b(del|erase|rmdir|rd)\b.*\s/s\b", re.IGNORECASE)),
    ("Zablokowano kasowanie przez `find -delete`.", re.compile(r"\bfind\b[^;&|\r\n]*\s-delete(?:\s|$)", re.IGNORECASE)),
    ("Zablokowano `git commit`, bo commit tworzy człowiek.", re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+commit\b", re.IGNORECASE)),
    ("Zablokowano `git push`, bo wypchnięcie na zdalne repozytorium wykonuje człowiek.", re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+push\b", re.IGNORECASE)),
]

SECRET_FILE_NAMES = frozenset({".env", ".env.priv", ".env.production", ".env.development"})
"""
Nazwy plików, których zawartość nie ma prawa trafić na wyjście polecenia.

Zbiór wymienia nazwy dokładnie, a nie wzorcem, i to jest celowe: wersjonowane szablony `.env.example`
oraz `.env.priv.example` mają tę samą przedrostkową nazwę i muszą przechodzić bez przeszkód, bo bez
nich nie da się postawić środowiska. Lista jest ta sama, co lista blokad odczytu w
`.claude/settings.json` - nowy plik sekretów trzeba dopisać w obu miejscach, bo jedno chroni przed
narzędziem czytającym pliki, a to tutaj przed powłoką.

Nazwy `.env.local` na tej liście nie ma i jest to decyzja, nie przeoczenie. W większości ekosystemów
oznacza ona plik lokalnych sekretów, ale według `docs/standards/standard_config.md` niesie wyłącznie
nie-sekrety zależne od maszyny albo od środowiska, a jej zawartość wolno cytować w rozmowie i w raporcie. Cena jest realna i przyjęta świadomie: sekret
wpisany tam z przyzwyczajenia nie zostanie złapany przez żadną z dwóch osłon.
"""

CONTENT_READING_COMMANDS = frozenset(
    {
        "cat",
        "tac",
        "type",
        "more",
        "less",
        "head",
        "tail",
        "nl",
        "od",
        "xxd",
        "hexdump",
        "strings",
        "grep",
        "egrep",
        "fgrep",
        "rg",
        "ack",
        "ag",
        "findstr",
        "awk",
        "sed",
        "cut",
        "paste",
        "sort",
        "uniq",
        "tr",
        "get-content",
        "gc",
        "select-string",
        "sls",
        "import-csv",
    }
)
"""
Polecenia, które wypisują zawartość wskazanego pliku na wyjście.

Nie ma tu poleceń kopiujących i przenoszących, bo `cp .env.example .env` jest właśnie tą czynnością,
którą instrukcja stawiania środowiska każe wykonać. Nie ma też interpreterów: program czytający token
z pliku prywatnej konfiguracji i wstawiający go do nagłówka żądania jest zalecanym sposobem użycia
sekretu w narzędziach repozytorium, więc blokada objęłaby jedyną drogę jego legalnego użycia.
"""

RECURSIVE_SEARCH_COMMANDS = frozenset({"grep", "egrep", "fgrep", "rg", "ack", "ag", "findstr"})

RM_PATTERN = re.compile(r"\brm\b(?P<arguments>[^;&|\r\n]*)", re.IGNORECASE)
SEGMENT_SEPARATOR_PATTERN = re.compile(r"\|\||&&|[;|\n]")
TREE_ROOT_PATHS = frozenset({".", "./", ".\\"})
POWERSHELL_REMOVE_PATTERN = re.compile(r"\b(remove-item|del|erase|rmdir|rd)\b(?P<arguments>[^;&|\r\n]*)", re.IGNORECASE)
GIT_RESTORE_PATTERN = re.compile(r"\bgit\s+restore\b(?P<arguments>[^;&|\r\n]*)", re.IGNORECASE)
GIT_CHECKOUT_PATTERN = re.compile(r"\bgit\s+checkout\b(?P<arguments>[^;&|\r\n]*)", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r""""[^"]*"|'[^']*'|\S+""")
RM_SHORT_OPTIONS = frozenset("dfiIrRv")
GIT_STAGED_OPTION = "--staged"
GIT_WORKTREE_OPTION = "--worktree"


def main() -> None:
    """Blokuje destrukcyjne komendy przed ich uruchomieniem przez Claude Code."""
    try:
        handle_payload(read_payload())
    except Exception as error:
        deny_after_hook_failure(error)


def handle_payload(payload: dict) -> None:
    """Sprawdza poprawne wejście hooka i odsyła decyzję blokującą, gdy jest potrzebna."""
    tool_name = str(payload.get("tool_name") or "")

    if tool_name.lower() not in {"bash", "powershell"}:
        return

    command = extract_command(payload)

    if not command:
        return

    cwd = resolve_working_directory(payload)
    reason = find_block_reason(command, cwd)

    if reason:
        deny(reason)


def read_payload() -> dict:
    """Czyta obiekt JSON zdarzenia hooka z stdin i odrzuca wejście o innym kształcie."""
    raw_input = sys.stdin.read().strip()

    if not raw_input:
        raise ValueError("Hook nie dostał wejścia JSON")

    payload = json.loads(raw_input)

    if not isinstance(payload, dict):
        raise TypeError("Wejście hooka nie jest obiektem JSON")

    return payload


def extract_command(payload: dict) -> str:
    """Wyciąga komendę shellową z wejścia hooka."""
    tool_input = payload.get("tool_input")

    if not isinstance(tool_input, dict):
        return ""

    for key in ("command", "script"):
        value = tool_input.get(key)

        if isinstance(value, str):
            return value

    return ""


def resolve_working_directory(payload: dict) -> Path:
    """Zwraca katalog roboczy przekazany przez Claude Code albo katalog procesu hooka."""
    cwd = payload.get("cwd")

    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd)

    return Path.cwd()


def find_block_reason(command: str, cwd: Path | None = None) -> str:
    """Zwraca powód blokady dla komendy albo pusty string."""
    collapsed = " ".join(command.split())

    for reason, pattern in RULES:
        if pattern.search(collapsed):
            return reason

    if contains_recursive_removal(collapsed):
        return "Zablokowano rekursywne kasowanie przez `rm`, `Remove-Item` albo alias PowerShell."

    if git_restore_touches_worktree(collapsed):
        return "Zablokowano `git restore` dotykające drzewa roboczego, bo cofa lokalne zmiany w plikach."

    if git_checkout_touches_path(collapsed, cwd or Path.cwd()):
        return "Zablokowano `git checkout` dotykające ścieżki, bo cofa lokalne zmiany w plikach."

    if command_reads_secret_file(collapsed):
        return "Zablokowano wypisanie zawartości pliku sekretów. Wartości z `.env` i `.env.priv` nie trafiają na wyjście - jeśli potrzebna jest nazwa klucza bez wartości, użyj `sed -E 's/=.*/=<UKRYTE>/'` na kopii albo zajrzyj do `.env.example`."

    if tree_search_lacks_secret_exclusion(collapsed):
        return "Zablokowano przeszukiwanie całego drzewa bez wykluczenia plików sekretów, bo wzorzec trafia w nie tak samo jak w kod, a wynik idzie na wyjście z pełną wartością. Dopisz `--exclude=.env --exclude=.env.priv` albo zawęź ścieżkę do konkretnych katalogów."

    return ""


def command_reads_secret_file(command: str) -> bool:
    """
    Rozpoznaje polecenie, które wypisałoby zawartość pliku sekretów na wyjście.

    Sprawdzane jest wyłącznie polecenie stojące na początku segmentu, bo tylko ono decyduje, co się
    z plikiem stanie. Nazwa pliku jest porównywana po samej nazwie, bez katalogu, więc odwołanie
    ścieżką bezwzględną albo względną łapie się tak samo - a wersjonowany szablon o nazwie kończącej
    się na `.example` nie łapie się wcale.
    """
    for segment in split_segments(command):
        tokens = tokenize(segment)

        if not tokens or base_file_name(tokens[0]) not in CONTENT_READING_COMMANDS:
            continue

        if any(is_secret_file_reference(token) for token in tokens[1:]):
            return True

    return False


def tree_search_lacks_secret_exclusion(command: str) -> bool:
    """
    Rozpoznaje rekursywne przeszukiwanie korzenia drzewa, które nie wyklucza plików sekretów.

    Reguła obejmuje wyłącznie przeszukiwanie sięgające korzenia, czyli wskazujące kropkę albo
    niewskazujące ścieżki wcale. Wyszukiwanie zawężone do katalogów z kodem przechodzi bez przeszkód,
    bo nie ma tam czego ujawnić - inaczej reguła zamieniłaby się w podatek od każdego przeszukania
    repozytorium i pierwszą rzeczą, którą ktoś by obszedł.

    Powodem powstania jest faktyczne ujawnienie dwóch tokenów instalacji w przebiegu, którego celem
    było policzenie wystąpień nazwy zmiennej. Wzorzec trafił w plik prywatnej konfiguracji, a wynik
    poszedł na wyjście z pełnymi wartościami.
    """
    for segment in split_segments(command):
        tokens = tokenize(segment)

        if not tokens:
            continue

        command_name = base_file_name(tokens[0])

        if command_name not in RECURSIVE_SEARCH_COMMANDS:
            continue

        arguments = tokens[1:]

        if command_name != "rg" and not any(has_recursive_search_flag(token) for token in arguments):
            continue

        if excludes_secret_files(arguments):
            continue

        searched_paths = [token for token in arguments if not token.startswith("-")][1:]

        if searched_paths and not any(path in TREE_ROOT_PATHS for path in searched_paths):
            continue

        return True

    return False


def has_recursive_search_flag(token: str) -> bool:
    """Rozpoznaje flagę rekursji wyszukiwania, także w zapisie połączonym z innymi krótkimi flagami."""
    lowered = token.lower()

    if lowered in {"--recursive", "--dereference-recursive"}:
        return True

    return token.startswith("-") and not token.startswith("--") and "r" in token[1:].lower()


def excludes_secret_files(arguments: list[str]) -> bool:
    """
    Sprawdza, czy wyszukiwanie jawnie wyklucza pliki sekretów.

    Wystarcza jakiekolwiek wykluczenie wskazujące nazwę zaczynającą się od `.env`, bo celem reguły
    jest świadomość autora polecenia, nie kompletność jego wzorca. Kropka w porównaniu jest istotna:
    bez niej wykluczenie katalogu środowiska wirtualnego liczyłoby się jako wykluczenie sekretów.
    """
    return any(token.startswith("-") and ".env" in token.partition("=")[2] for token in arguments)


def split_segments(command: str) -> list[str]:
    """Dzieli wiersz poleceń na segmenty rozdzielone operatorami powłoki, żeby każdy oceniać osobno."""
    return [segment for segment in SEGMENT_SEPARATOR_PATTERN.split(command) if segment.strip()]


def base_file_name(token: str) -> str:
    """Zwraca samą nazwę pliku bez katalogu, niezależnie od separatora ścieżki i cudzysłowów."""
    cleaned = token.strip().strip('"').strip("'")

    for separator in ("/", "\\"):
        cleaned = cleaned.rsplit(separator, 1)[-1]

    return cleaned.lower()


def is_secret_file_reference(token: str) -> bool:
    """Rozpoznaje odwołanie do pliku sekretów, nie łapiąc przy tym wersjonowanych szablonów."""
    return base_file_name(token) in SECRET_FILE_NAMES


def contains_recursive_removal(command: str) -> bool:
    """Rozpoznaje rekursywne kasowanie niezależnie od krótkiej albo długiej formy flag."""
    for match in RM_PATTERN.finditer(command):
        if has_recursive_option(tokenize(match.group("arguments"))):
            return True

    return any(has_powershell_recurse_option(tokenize(match.group("arguments"))) for match in POWERSHELL_REMOVE_PATTERN.finditer(command))


def has_recursive_option(tokens: list[str]) -> bool:
    """Sprawdza flagę rekursji polecenia rm w zapisie POSIX albo PowerShell."""
    for token in tokens:
        lowered = token.lower()

        if lowered in {"--recursive", "-recurse", "-r"} or lowered.startswith("-rec"):
            return True

        if token.startswith("-") and not token.startswith("--"):
            short_options = token[1:]

            if short_options and set(short_options) <= RM_SHORT_OPTIONS and ("r" in short_options or "R" in short_options):
                return True

    return False


def has_powershell_recurse_option(tokens: list[str]) -> bool:
    """Sprawdza pełną i bezpiecznie rozpoznawalną skróconą formę parametru Recurse."""
    return any(token.lower() == "-r" or token.lower().startswith("-rec") for token in tokens)


def git_restore_touches_worktree(command: str) -> bool:
    """Rozróżnia bezpieczne wycofanie stage od przywracania zawartości plików."""
    for match in GIT_RESTORE_PATTERN.finditer(command):
        tokens = tokenize(match.group("arguments"))
        staged = GIT_STAGED_OPTION in tokens or any(is_combined_git_option(argument, "S") for argument in tokens)
        worktree = GIT_WORKTREE_OPTION in tokens or any(is_combined_git_option(argument, "W") for argument in tokens)

        if worktree or not staged:
            return True

    return False


def git_checkout_touches_path(command: str, cwd: Path) -> bool:
    """Rozpoznaje formy checkout wskazujące plik lub katalog bez blokowania zmiany gałęzi."""
    for match in GIT_CHECKOUT_PATTERN.finditer(command):
        tokens = tokenize(match.group("arguments"))

        if "--" in tokens:
            return True

        if any(token in {"-p", "--patch"} for token in tokens):
            return True

        if any(token in {"-b", "-B", "--orphan", "--detach"} for token in tokens):
            continue

        positional = [token for token in tokens if not token.startswith("-")]

        if len(positional) > 1:
            return True

        if len(positional) == 1 and (checkout_candidate_is_path(positional[0], cwd) or contains_git_pathspec_wildcard(positional[0])):
            return True

    return False


def checkout_candidate_is_path(candidate: str, cwd: Path) -> bool:
    """Traktuje istniejącą ścieżkę jako cel przywracania zawartości pliku albo katalogu."""
    if candidate in {".", ".."}:
        return True

    candidate_path = Path(candidate)

    if not candidate_path.is_absolute():
        candidate_path = cwd / candidate_path

    return candidate_path.exists()


def contains_git_pathspec_wildcard(candidate: str) -> bool:
    """Rozpoznaje znaki globu niedozwolone w nazwie referencji Gita, ale działające w pathspecie."""
    return any(character in candidate for character in "*?[")


def is_combined_git_option(token: str, option: str) -> bool:
    """Rozpoznaje wielką literę opcji Gita także w połączonym zapisie krótkich flag."""
    return token.startswith("-") and not token.startswith("--") and option in token[1:]


def tokenize(arguments: str) -> list[str]:
    """Dzieli argumenty wystarczająco do odczytu flag i zdejmuje proste cudzysłowy."""
    tokens: list[str] = []

    for match in TOKEN_PATTERN.finditer(arguments):
        token = match.group(0)

        if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
            token = token[1:-1]

        tokens.append(token)

    return tokens


def deny_after_hook_failure(error: Exception) -> None:
    """Przy błędzie diagnostycznym blokuje komendę i zostawia typ wyjątku w logu debug."""
    error_name = type(error).__name__
    print(f"block_dangerous_commands.py: {error_name}", file=sys.stderr)
    deny(f"Hook bezpieczeństwa nie mógł zweryfikować komendy ({error_name}), więc zablokował ją zamiast wyłączyć ochronę.")


def deny(reason: str) -> None:
    """Wysyła decyzję blokującą do Claude Code."""
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
