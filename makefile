.PHONY: lint lint-python lint-docs format test test-unit test-critical typecheck deadcode deps security audit check check-unit frontend-typecheck frontend-lint frontend-test frontend-format-check frontend-check backend

# No recipe in this file contains shell syntax: no `||`, no brace blocks, no
# apostrophes, no file sourcing. This is not a matter of style. GNU make on Windows picks the shell
# itself - it uses sh.exe if it finds it in PATH, and cmd otherwise - so a recipe with shell
# syntax would behave differently on two machines with the same operating system.

# A target composed of the targets named in it, because the two check ecosystems, Python and Node, may run in the CI pipeline
# on two different images and each of them has to be callable separately. The format check of the frontend files
# belongs to the Node side, next to the one of markdown: the same prettier runs both.
lint: lint-python lint-docs frontend-format-check

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

# The last line formats the frontend files with the pattern of the target frontend-format-check, where the pattern is explained.
format:
	ruff format .
	ruff check --fix .
	npx --no-install prettier --write "**/*.md"
	npx --no-install prettier --write "frontend/**/*.{ts,tsx,css,html,json,mjs}"

test:
	python -m pytest

# A quick run without the tests with a real dependency, to fire without a database set up.
test-unit:
	python -m pytest -m "not critical"

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
	bandit -r service --confidence-level medium
	bandit -r service -t B608
	python -m bandit -r config -x config/settings.py --confidence-level medium
# Settings B105 reports environment filenames as passwords, not credential literals.
	python -m bandit config/settings.py -s B105 --confidence-level medium
	python -m bandit -r api worker common_time.py --confidence-level medium
	python -m bandit -r data -x data/import_process.py,data/windows_job.py --confidence-level medium
# The process supervisor accepts an absolute executable from the trusted administrative caller, with shell=False and suppressed output.
	python -m bandit data/import_process.py -s B404,B603 --confidence-level medium
# The Windows supervisor uses subprocess only to encode argv for CreateProcessW; no shell is involved.
	python -m bandit data/windows_job.py -s B404 --confidence-level medium
	python -m bandit -r config api data worker common_time.py -t B608
# The start script of the routing service runs in its own container: it reads the defaults of valhalla_build_config through
# subprocess and replaces itself with valhalla_service, both with an argument list of constants, without a shell, by the name
# from PATH of the routing image.
	python -m bandit valhalla/start_routing_service.py -s B404,B603,B606,B607 --confidence-level medium
	python -m bandit valhalla/start_routing_service.py -t B608

audit:
	pip-audit

# The gates of the web frontend from docs/standards/standard_frontend.md, section Gates. The first three call a script of
# frontend/package.json through npm with --prefix, so they start in the repository root like every other target here:
# a change of directory inside a recipe would be shell syntax. The commands behind the scripts are tsc -b, oxlint and
# vitest run, the ones a person working in frontend/ calls by hand.
frontend-typecheck:
	npm --prefix frontend run typecheck

frontend-lint:
	npm --prefix frontend run lint

frontend-test:
	npm --prefix frontend run test

# The frontend files are formatted by the prettier of lint-docs: the copy from the node_modules of the repository root, with
# the same .prettierrc and the same --no-install flag. The pattern with its braces stands in quotes so that prettier expands it,
# not the shell - sh and cmd then pass it on unchanged, and prettier skips the paths from .gitignore, which keeps the installed
# packages, the build output and the tile archive out of the check.
frontend-format-check:
	npx --no-install prettier --check "frontend/**/*.{ts,tsx,css,html,json,mjs}"

# Everything the frontend standard checks with a tool of the Node side. Its fourth gate, the forbidden characters check,
# is a test of tests/architecture and runs with the target test.
frontend-check: frontend-typecheck frontend-lint frontend-test frontend-format-check

# The target does not cover the critical tests with a real database: the code quality check is to work also on a machine
# where the database is not running. The project adds a separate target for the critical run together with the first such test.
# It ends with the gates of the frontend, so that one call checks both the Python side and the frontend.
check: lint typecheck deadcode deps security audit test frontend-check

backend:
	python -m api

test-critical:
	python -m pytest -m critical $(PYTEST_ARGS)

check-unit: lint typecheck deadcode deps security audit test-unit
