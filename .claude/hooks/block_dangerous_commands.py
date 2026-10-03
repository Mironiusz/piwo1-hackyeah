import json
import re
import sys
from pathlib import Path

RULES = [
    ("Blocked `git reset --hard`, because it can irreversibly remove local changes.", re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE)),
    ("Blocked `git clean`, because it deletes untracked files.", re.compile(r"\bgit\s+clean\b", re.IGNORECASE)),
    ("Blocked deleting the `.git` directory.", re.compile(r"\b(rm|del|erase|remove-item|rmdir|rd)\b.*(^|[\\/\s])\.git([\\/\s]|$)", re.IGNORECASE)),
    ("Blocked deleting `.env` files.", re.compile(r"\b(rm|del|erase|remove-item)\b.*(^|[\\/\s])\.env([.\s\\/*]|$)", re.IGNORECASE)),
    ("Blocked recursive deletion through a cmd command with the `/s` flag.", re.compile(r"\b(del|erase|rmdir|rd)\b.*\s/s\b", re.IGNORECASE)),
    ("Blocked deletion through `find -delete`.", re.compile(r"\bfind\b[^;&|\r\n]*\s-delete(?:\s|$)", re.IGNORECASE)),
    ("Blocked `git commit`, because a human creates commits.", re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+commit\b", re.IGNORECASE)),
    ("Blocked `git push`, because a human pushes to the remote repository.", re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+push\b", re.IGNORECASE)),
]

SECRET_FILE_NAMES = frozenset({".env", ".env.priv", ".env.production", ".env.development"})
"""
Names of files whose contents must never reach the command output.

The set lists the names exactly, not by a pattern, and that is deliberate: the versioned templates `.env.example`
and `.env.priv.example` share the same prefix name and must pass unhindered, because without
them the environment cannot be set up. The list is the same as the list of read blocks in
`.claude/settings.json` - a new secrets file has to be added in both places, because one protects against
the tool that reads files, and this one here against the shell.

The name `.env.local` is not on this list and that is a decision, not an oversight. In most ecosystems
it means a file of local secrets, but according to `docs/standards/standard_config.md` it carries only
non-secrets that depend on the machine or the environment, and its contents may be quoted in conversation and in a report.
The price is real and accepted deliberately: a secret written there out of habit will not be caught by either of the two guards.
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
Commands that print the contents of the given file to the output.

There are no copying and moving commands here, because `cp .env.example .env` is exactly the step
that the environment setup instructions tell you to perform. There are no interpreters either: a program reading a token
from the private configuration file and putting it into a request header is the recommended way of using
a secret in the repository tools, so a block would cover the only path of its legitimate use.
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
    """Blocks destructive commands before Claude Code runs them."""
    try:
        handle_payload(read_payload())
    except Exception as error:
        deny_after_hook_failure(error)


def handle_payload(payload: dict) -> None:
    """Checks a valid hook input and sends back a blocking decision when one is needed."""
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
    """Reads the JSON object of the hook event from stdin and rejects input of any other shape."""
    raw_input = sys.stdin.read().strip()

    if not raw_input:
        raise ValueError("The hook received no JSON input")

    payload = json.loads(raw_input)

    if not isinstance(payload, dict):
        raise TypeError("The hook input is not a JSON object")

    return payload


def extract_command(payload: dict) -> str:
    """Extracts the shell command from the hook input."""
    tool_input = payload.get("tool_input")

    if not isinstance(tool_input, dict):
        return ""

    for key in ("command", "script"):
        value = tool_input.get(key)

        if isinstance(value, str):
            return value

    return ""


def resolve_working_directory(payload: dict) -> Path:
    """Returns the working directory passed by Claude Code or the directory of the hook process."""
    cwd = payload.get("cwd")

    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd)

    return Path.cwd()


def find_block_reason(command: str, cwd: Path | None = None) -> str:
    """Returns the block reason for the command or an empty string."""
    collapsed = " ".join(command.split())

    for reason, pattern in RULES:
        if pattern.search(collapsed):
            return reason

    if contains_recursive_removal(collapsed):
        return "Blocked recursive deletion through `rm`, `Remove-Item` or a PowerShell alias."

    if git_restore_touches_worktree(collapsed):
        return "Blocked `git restore` touching the working tree, because it reverts local changes in files."

    if git_checkout_touches_path(collapsed, cwd or Path.cwd()):
        return "Blocked `git checkout` touching a path, because it reverts local changes in files."

    if command_reads_secret_file(collapsed):
        return (
            "Blocked printing the contents of a secrets file. Values from `.env` and `.env.priv` do not go to the output - "
            "if you need a key name without its value, use `sed -E 's/=.*/=<HIDDEN>/'` on a copy or look into `.env.example`."
        )

    if tree_search_lacks_secret_exclusion(collapsed):
        return (
            "Blocked searching the whole tree without excluding secrets files, because the pattern hits them just as it hits code, "
            "and the result goes to the output with the full value. Add `--exclude=.env --exclude=.env.priv` or narrow the path to specific directories."
        )

    return ""


def command_reads_secret_file(command: str) -> bool:
    """
    Recognizes a command that would print the contents of a secrets file to the output.

    Only the command standing at the beginning of a segment is checked, because only it decides what happens
    to the file. The file name is compared by the bare name, without the directory, so a reference
    by an absolute or a relative path is caught the same way - and a versioned template with a name ending
    in `.example` is not caught at all.
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
    Recognizes a recursive search of the tree root that does not exclude secrets files.

    The rule covers only a search reaching the root, that is one pointing at the dot or
    pointing at no path at all. A search narrowed to code directories passes unhindered,
    because there is nothing to reveal there - otherwise the rule would turn into a tax on every search
    of the repository and the first thing somebody would work around.

    The reason it was created is an actual disclosure of two installation tokens in a run whose goal
    was counting the occurrences of a variable name. The pattern hit the private configuration file, and the result
    went to the output with the full values.
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
    """Recognizes the search recursion flag, also when written combined with other short flags."""
    lowered = token.lower()

    if lowered in {"--recursive", "--dereference-recursive"}:
        return True

    return token.startswith("-") and not token.startswith("--") and "r" in token[1:].lower()


def excludes_secret_files(arguments: list[str]) -> bool:
    """
    Checks whether the search explicitly excludes secrets files.

    Any exclusion pointing at a name starting with `.env` is enough, because the goal of the rule
    is the awareness of the command author, not the completeness of their pattern. The dot in the comparison matters:
    without it, excluding the virtual environment directory would count as excluding secrets.
    """
    return any(token.startswith("-") and ".env" in token.partition("=")[2] for token in arguments)


def split_segments(command: str) -> list[str]:
    """Splits the command line into segments separated by shell operators, so that each is judged separately."""
    return [segment for segment in SEGMENT_SEPARATOR_PATTERN.split(command) if segment.strip()]


def base_file_name(token: str) -> str:
    """Returns the bare file name without the directory, regardless of the path separator and quotes."""
    cleaned = token.strip().strip('"').strip("'")

    for separator in ("/", "\\"):
        cleaned = cleaned.rsplit(separator, 1)[-1]

    return cleaned.lower()


def is_secret_file_reference(token: str) -> bool:
    """Recognizes a reference to a secrets file, without catching the versioned templates."""
    return base_file_name(token) in SECRET_FILE_NAMES


def contains_recursive_removal(command: str) -> bool:
    """Recognizes recursive deletion regardless of the short or long form of the flags."""
    for match in RM_PATTERN.finditer(command):
        if has_recursive_option(tokenize(match.group("arguments"))):
            return True

    return any(has_powershell_recurse_option(tokenize(match.group("arguments"))) for match in POWERSHELL_REMOVE_PATTERN.finditer(command))


def has_recursive_option(tokens: list[str]) -> bool:
    """Checks the recursion flag of the rm command in POSIX or PowerShell notation."""
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
    """Checks the full and the safely recognizable abbreviated form of the Recurse parameter."""
    return any(token.lower() == "-r" or token.lower().startswith("-rec") for token in tokens)


def git_restore_touches_worktree(command: str) -> bool:
    """Tells a safe unstaging apart from restoring the contents of files."""
    for match in GIT_RESTORE_PATTERN.finditer(command):
        tokens = tokenize(match.group("arguments"))
        staged = GIT_STAGED_OPTION in tokens or any(is_combined_git_option(argument, "S") for argument in tokens)
        worktree = GIT_WORKTREE_OPTION in tokens or any(is_combined_git_option(argument, "W") for argument in tokens)

        if worktree or not staged:
            return True

    return False


def git_checkout_touches_path(command: str, cwd: Path) -> bool:
    """Recognizes the checkout forms pointing at a file or a directory without blocking a branch switch."""
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
    """Treats an existing path as the target of restoring the contents of a file or a directory."""
    if candidate in {".", ".."}:
        return True

    candidate_path = Path(candidate)

    if not candidate_path.is_absolute():
        candidate_path = cwd / candidate_path

    return candidate_path.exists()


def contains_git_pathspec_wildcard(candidate: str) -> bool:
    """Recognizes glob characters that are not allowed in a Git reference name but work in a pathspec."""
    return any(character in candidate for character in "*?[")


def is_combined_git_option(token: str, option: str) -> bool:
    """Recognizes the uppercase letter of a Git option also in the combined notation of short flags."""
    return token.startswith("-") and not token.startswith("--") and option in token[1:]


def tokenize(arguments: str) -> list[str]:
    """Splits the arguments well enough to read the flags and strips simple quotes."""
    tokens: list[str] = []

    for match in TOKEN_PATTERN.finditer(arguments):
        token = match.group(0)

        if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
            token = token[1:-1]

        tokens.append(token)

    return tokens


def deny_after_hook_failure(error: Exception) -> None:
    """On a diagnostic error blocks the command and leaves the exception type in the debug log."""
    error_name = type(error).__name__
    print(f"block_dangerous_commands.py: {error_name}", file=sys.stderr)
    deny(f"The security hook could not verify the command ({error_name}), so it blocked it instead of disabling the protection.")


def deny(reason: str) -> None:
    """Sends a blocking decision to Claude Code."""
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
