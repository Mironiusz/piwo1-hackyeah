.PHONY: lint lint-python lint-docs format test test-unit typecheck deadcode deps security audit check

# No recipe in this file contains shell syntax: no `||`, no brace blocks, no
# apostrophes, no file sourcing. This is not a matter of style. GNU make on Windows picks the shell
# itself - it uses sh.exe if it finds it in PATH, and cmd otherwise - so a recipe with shell
# syntax would behave differently on two machines with the same operating system.

# A target composed of the two targets below, because the two check ecosystems, Python and Node, may run in the CI pipeline
# on two different images and each of them has to be callable separately.
lint: lint-python lint-docs

lint-python:
	ruff check .
	ruff format --check .

# Markdown is formatted by prettier, because ruff does not cover it (extend-exclude in pyproject.toml, the reason is next to that
# entry). The version is pinned exactly in package.json, the options live in .prettierrc - both files are also read
# by the VS Code extension, so a save from the editor and a run from this file give the same result. The
# --no-install flag tells npx to use only the copy from node_modules and to stop when it is missing: without it npx
# would quietly download the latest release and check with a different version than the editor. The file pattern stands
# in quotes so that prettier expands it, not the shell - then it skips the paths from .gitignore.
lint-docs:
	npx --no-install prettier --check "**/*.md"

format:
	ruff format .
	ruff check --fix .
	npx --no-install prettier --write "**/*.md"

test:
	pytest

# A quick run without the tests with a real dependency, to fire without a database set up.
test-unit:
	pytest -m "not critical"

typecheck:
	mypy

deadcode:
	vulture

deps:
	deptry .

# Bandit runs as a separate pass for each directory, because a suppression is to apply only where
# its reason stands. The project adds a pass for each code layer, without suppressions, until a specific reason
# requires them.
# In .claude/hooks B404, B603 and B607 are suppressed: the SessionStart hook calls git with an argument list, without
# a shell, by the name from PATH, to read the repository root - the command is a constant of the file, not
# user input.
#
# Every pass has the --confidence-level medium threshold, because standard_security.md counts as a violation
# a finding with a medium or high confidence level, regardless of severity. The exception is B608,
# building a query from strings: it runs as a separate pass, without a threshold, because standard_review.md makes
# it the verification of standard_database.md, which forbids building a query from strings without exceptions.
security:
	bandit -r .claude/hooks -s B404,B603,B607 --confidence-level medium
	bandit -r .claude/hooks -t B608
	bandit -r db -s B101 --confidence-level medium

audit:
	pip-audit

# The target does not cover the critical tests with a real database: the code quality check is to work also on a machine
# where the database is not running. The project adds a separate target for the critical run together with the first such test.
check: lint typecheck deadcode deps security audit test
