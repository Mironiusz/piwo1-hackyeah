#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

DEFAULT_EXTENSIONS = (".py", ".html", ".js", ".css", ".sql", ".md")
DEFAULT_IGNORE_DIRS = (
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "node_modules",
    "logs",
    "exports",
    "old",
)
SECRET_EXTENSIONS = (".pem", ".key", ".p12", ".pfx")
ALLOWED_SPECIAL_FILES = {".env.example"}


def parse_args() -> argparse.Namespace:
    """Parsuje argumenty CLI dla prostego dumpowania kontekstu folderu."""
    parser = argparse.ArgumentParser(description="Dump selected text files from a folder into one output.txt style context file.")
    parser.add_argument("--input", required=True, help="Folder to dump, for example ./database_schema_export.")
    parser.add_argument("--output", default="output.txt", help="Output file path. Default: output.txt.")
    parser.add_argument("--extensions", nargs="*", default=list(DEFAULT_EXTENSIONS), help="Allowed file extensions. Default: .py .html .js .css .sql .md.")
    parser.add_argument("--ignore-dirs", nargs="*", default=list(DEFAULT_IGNORE_DIRS), help="Directory names ignored during recursive scan.")
    parser.add_argument("--extra-ignore-dirs", nargs="*", default=[], help="Extra directory names to ignore in addition to --ignore-dirs.")
    parser.add_argument("--ignore-extensions", nargs="*", default=[], help="Allowed extensions to skip for this run, for example .md .css.")
    return parser.parse_args()


def normalize_extensions(values: list[str]) -> set[str]:
    """Normalizuje listę rozszerzeń do postaci z kropką i małymi literami."""
    normalized = set()

    for value in values:
        stripped = value.strip().lower()

        if not stripped:
            continue

        normalized.add(stripped if stripped.startswith(".") else f".{stripped}")

    return normalized


def should_include_file(path: Path, allowed_extensions: set[str], ignored_extensions: set[str]) -> bool:
    """Sprawdza, czy plik powinien wejść do dumpa kontekstu."""
    name = path.name.lower()
    suffix = path.suffix.lower()

    if name in ALLOWED_SPECIAL_FILES:
        return True

    if name == ".env" or name.startswith(".env."):
        return False

    if suffix in SECRET_EXTENSIONS:
        return False

    if suffix in ignored_extensions:
        return False

    return suffix in allowed_extensions


def display_path(path: Path, cwd: Path) -> str:
    """Zwraca krótką ścieżkę do nagłówka pliku w dumpie."""
    try:
        relative_path = path.resolve().relative_to(cwd.resolve())
        return f"./{relative_path.as_posix()}"
    except ValueError:
        return str(path)


def save_files_content_to_txt(root_folder: Path, output_file: Path, ignore_dirs: set[str], allowed_extensions: set[str], ignored_extensions: set[str]) -> tuple[int, int]:
    """Rekurencyjnie zapisuje treść wybranych plików tekstowych do jednego pliku output.txt style."""
    included_count = 0
    failed_count = 0
    cwd = Path.cwd()
    output_file_resolved = output_file.resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(root_folder):
            dirs[:] = sorted(directory for directory in dirs if directory not in ignore_dirs)

            for file_name in sorted(files):
                file_path = Path(root) / file_name

                if file_path.resolve() == output_file_resolved:
                    continue

                if not should_include_file(file_path, allowed_extensions, ignored_extensions):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                except OSError as error:
                    failed_count += 1
                    print(f"Nie udało się odczytać pliku {file_path}: {error}")
                    continue

                outfile.write(f"==== {display_path(file_path, cwd)} ====\n")
                outfile.write(content)
                outfile.write("\n\n")
                included_count += 1

    return included_count, failed_count


def main() -> None:
    """Uruchamia prosty dump kontekstu folderu do jednego pliku tekstowego."""
    args = parse_args()
    root_folder = Path(args.input)
    output_file = Path(args.output)
    ignore_dirs = set(args.ignore_dirs) | set(args.extra_ignore_dirs)
    allowed_extensions = normalize_extensions(args.extensions)
    ignored_extensions = normalize_extensions(args.ignore_extensions)

    if not root_folder.is_dir():
        raise SystemExit(f"Folder wejściowy nie istnieje albo nie jest folderem: {root_folder}")

    included_count, failed_count = save_files_content_to_txt(root_folder, output_file, ignore_dirs, allowed_extensions, ignored_extensions)

    print(f"Zawartość plików została zapisana do {output_file}")
    print(f"Uwzględnione pliki: {included_count}")
    print(f"Nieudane odczyty: {failed_count}")


if __name__ == "__main__":
    main()
