---
name: load-context
description: use this skill when you need the context of a folder, a code unit or a repository feature before analysis, explanation, debugging, refactoring, documenting or review. run the bundled script dump_context.py on the indicated folder to make a single dump into output.txt, and use that dump as the main source instead of opening many files one by one.
---

# Loading context

Use `scripts/dump_context.py` when you need context from a repository folder.

The goal is simple: make one dump of the indicated folder into `output.txt`, read that file and base the analysis on it, instead of manually opening many files one after another.

## Default command

```bash
python scripts/dump_context.py --input <folder> --output output.txt
```

Example:

```bash
python scripts/dump_context.py --input ./config --output output.txt
```

After the file is created, read `output.txt` and base the analysis on it.

## Available flags

`--input` is required and points to the folder to dump.

`--output` sets the output file path. Default: `output.txt`.

`--extensions` replaces the default list of allowed extensions. Default: `.py .html .js .css .sql .md`.

`--ignore-dirs` replaces the default list of ignored directory names. By default, directories that are technical noise are ignored, for example `venv`, `.venv`, `__pycache__`, `.git`, `node_modules`, `build`, `dist`, `logs`, `exports` and `old`.

`--extra-ignore-dirs` adds further ignored directory names, keeping the default ones.

`--ignore-extensions` skips selected extensions in this run, even if they are allowed by `--extensions`.

## Useful examples

Dump of a code unit with default settings:

```bash
python scripts/dump_context.py --input ./service --output output.txt
```

Dump of only Python, Markdown and SQL files:

```bash
python scripts/dump_context.py --input ./service --output output.txt --extensions .py .md .sql
```

Dump skipping Markdown and CSS:

```bash
python scripts/dump_context.py --input ./config --output output.txt --ignore-extensions .md .css
```

Dump with additionally ignored local folders:

```bash
python scripts/dump_context.py --input ./config --output output.txt --extra-ignore-dirs tmp generated snapshots
```

## Security

The script never includes `.env`, `.env.*`, `.pem`, `.key`, `.p12` or `.pfx` files.

`.env.example` is allowed.

Keep this flow small. Do not build manifests, dry runs or audit reports for this skill.
