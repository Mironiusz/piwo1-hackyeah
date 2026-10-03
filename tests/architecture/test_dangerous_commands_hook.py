from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
HOOK_PATH = ROOT_DIR / ".claude" / "hooks" / "block_dangerous_commands.py"


def _run_hook(command: str) -> subprocess.CompletedProcess[str]:
    """Uruchamia hook tak, jak robi to Claude Code, z wejściem JSON podanym na stdin."""
    payload = {
        "cwd": str(ROOT_DIR),
        "tool_name": "PowerShell",
        "tool_input": {"command": command},
    }
    return subprocess.run([sys.executable, str(HOOK_PATH)], input=json.dumps(payload), text=True, capture_output=True, timeout=5, check=False)


def _read_decision(result: subprocess.CompletedProcess[str]) -> str | None:
    """Zwraca decyzję PreToolUse z odpowiedzi hooka albo brak decyzji dla dozwolonej komendy."""
    if not result.stdout.strip():
        return None

    payload = json.loads(result.stdout)
    return payload["hookSpecificOutput"]["permissionDecision"]


@pytest.mark.parametrize(
    "command",
    [
        "rm --recursive --force build",
        "rm --force --recursive build",
        "rm -R -f build",
        "Remove-Item -Path build -Recurse -Force",
        "cmd /c rd /s /q build",
        "cmd /c del /s /q '*.tmp'",
        "git restore .",
        "git restore --staged --worktree .",
        "git checkout .",
        "git checkout README.md",
        "git checkout --patch",
        "git checkout '*.py'",
        "find . -name '*.py' -delete",
    ],
)
def test_hook_denies_commands_that_can_destroy_local_work(command: str) -> None:
    """Pilnuje wariantów destrukcyjnych poleceń znalezionych przez audyt."""
    result = _run_hook(command)

    assert result.returncode == 0
    assert _read_decision(result) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m 'zmiana'",
        "git commit --amend --no-edit",
        "git -C ../inne-repo commit -m 'zmiana'",
        "git -c user.name=agent commit -m 'zmiana'",
        "git push",
        "git push origin main",
        "git -C ../inne-repo push --force",
    ],
)
def test_hook_denies_commands_that_create_or_publish_history(command: str) -> None:
    """Pilnuje reguły z `CLAUDE.md`, że commit i wypchnięcie na zdalne repozytorium wykonuje człowiek."""
    result = _run_hook(command)

    assert result.returncode == 0
    assert _read_decision(result) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cat .env",
        "cat .env.priv",
        "head -n 5 .env",
        "tail -n 5 .env.priv",
        "type .env",
        "Get-Content .env.priv",
        "gc .env",
        "sed -n '1,5p' .env",
        "cat ./.env.priv",
        "grep DATABASE .env",
    ],
)
def test_hook_denies_commands_that_print_secret_file_contents(command: str) -> None:
    """Pilnuje, że zawartość pliku zmiennych środowiskowych nie trafia na wyjście polecenia."""
    result = _run_hook(command)

    assert result.returncode == 0
    assert _read_decision(result) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "grep -r TOKEN .",
        "grep -rn PASSWORD ./",
        "grep --recursive SECRET .",
        "rg TOKEN",
        "rg PASSWORD .",
    ],
)
def test_hook_denies_tree_search_without_secret_exclusion(command: str) -> None:
    """
    Pilnuje, że przeszukanie korzenia drzewa bez wykluczenia sekretów jest zatrzymane przed uruchomieniem.

    Znana granica reguły: rozpoznawana jest flaga rekursji w zapisie z myślnikiem, więc windowsowe
    `findstr /s` przechodzi.
    """
    result = _run_hook(command)

    assert result.returncode == 0
    assert _read_decision(result) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cat .env.example",
        "cat .env.priv.example",
        "cp .env.example .env",
        "grep -r TOKEN --exclude=.env --exclude=.env.priv .",
        "grep -r TOKEN tests/",
        "rg TOKEN tests/",
    ],
)
def test_hook_leaves_commands_that_cannot_leak_secrets(command: str) -> None:
    """Pilnuje, że ochrona sekretów nie blokuje stawiania środowiska ani zawężonego wyszukiwania."""
    result = _run_hook(command)

    assert result.returncode == 0
    assert _read_decision(result) is None


@pytest.mark.parametrize(
    "command",
    [
        "rm build.log",
        "git restore --staged README.md",
        "git checkout feature/docs",
        "find . -name '*.py' -print",
        "Write-Output 'gotowe'",
        "git status --short",
        "git log --oneline --grep commit",
        "git fetch origin",
        "git pull",
        "git diff --stat",
    ],
)
def test_hook_leaves_non_destructive_commands_to_normal_permissions(command: str) -> None:
    """Pilnuje, że blokada nie zastępuje zwykłego systemu uprawnień dla bezpiecznych poleceń."""
    result = _run_hook(command)

    assert result.returncode == 0
    assert _read_decision(result) is None


@pytest.mark.parametrize("invalid_payload", ["", "[]", "nie-json"])
def test_hook_fails_closed_without_exiting_with_error(invalid_payload: str) -> None:
    """Pilnuje, że awaria wejścia blokuje komendę poprawną decyzją zamiast wyłączać hook kodem 1."""
    result = subprocess.run([sys.executable, str(HOOK_PATH)], input=invalid_payload, text=True, capture_output=True, timeout=5, check=False)

    assert result.returncode == 0
    assert _read_decision(result) == "deny"
    assert "block_dangerous_commands.py:" in result.stderr


def test_hook_configuration_uses_exec_form_for_python_script() -> None:
    """Pilnuje zarejestrowania hooka jako programu Python z osobnym argumentem ścieżki."""
    settings = json.loads((ROOT_DIR / ".claude" / "settings.json").read_text(encoding="utf-8"))
    handler = settings["hooks"]["PreToolUse"][0]["hooks"][0]

    assert settings["hooks"]["PreToolUse"][0]["matcher"] == "Bash|PowerShell"
    assert handler["command"] == "python"
    assert handler["args"] == ["${CLAUDE_PROJECT_DIR}/.claude/hooks/block_dangerous_commands.py"]
