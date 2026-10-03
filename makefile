.PHONY: lint lint-python lint-docs format test test-unit typecheck deadcode deps security audit check

# Żadna recepta w tym pliku nie zawiera składni powłoki: ani `||`, ani bloków w klamrach, ani
# apostrofów, ani wczytywania pliku. Nie jest to kwestia stylu. GNU make na Windowsie wybiera powłokę
# sam - używa sh.exe, jeśli znajdzie go w PATH, a cmd w przeciwnym razie - więc recepta ze składnią
# powłoki zachowywałaby się różnie na dwóch maszynach z tym samym systemem.

# Cel złożony z dwóch celów niżej, bo dwa ekosystemy sprawdzeń, Python i Node, mogą w potoku CI jechać
# na dwóch różnych obrazach i każdy z nich ma się dać zawołać osobno.
lint: lint-python lint-docs

lint-python:
	ruff check .
	ruff format --check .

# Markdown formatuje prettier, bo ruff go nie obejmuje (extend-exclude w pyproject.toml, powód przy tym
# wpisie). Wersja jest przypięta dokładnie w package.json, opcje stoją w .prettierrc - oba pliki czyta
# także rozszerzenie VS Code, więc zapis z edytora i przebieg z tego pliku dają ten sam wynik. Flaga
# --no-install każe npx użyć wyłącznie kopii z node_modules i przerwać, gdy jej nie ma: bez niej npx
# po cichu pobrałby najnowsze wydanie i sprawdzał inną wersją niż edytor. Wzorzec plików stoi
# w cudzysłowie, żeby rozwinął go prettier, a nie powłoka - wtedy pomija ścieżki z .gitignore.
lint-docs:
	npx --no-install prettier --check "**/*.md"

format:
	ruff format .
	ruff check --fix .
	npx --no-install prettier --write "**/*.md"

test:
	pytest

# Szybki przebieg bez testów z realną zależnością, do odpalenia bez postawionej bazy.
test-unit:
	pytest -m "not critical"

typecheck:
	mypy

deadcode:
	vulture

deps:
	deptry .

# Bandit idzie osobnym przebiegiem na każdy katalog, bo wyciszenie ma obowiązywać tylko tam, gdzie stoi
# jego powód. Projekt dopisuje przebieg dla każdej warstwy kodu, bez wyciszeń, dopóki konkretny powód
# ich nie wymaga.
# W .claude/hooks wyciszone są B404, B603 i B607: hook SessionStart woła gita listą argumentów, bez
# powłoki, po nazwie z PATH, żeby odczytać korzeń repozytorium - polecenie jest stałą pliku, a nie
# wejściem użytkownika.
#
# Każdy przebieg ma próg --confidence-level medium, bo standard_security.md liczy jako naruszenie
# zgłoszenie o średnim albo wysokim poziomie pewności, niezależnie od ważności. Wyjątkiem jest B608,
# sklejanie zapytania ze stringów: idzie osobnym przebiegiem, bez progu, bo standard_review.md robi
# z niego weryfikację standard_database.md, a ten zakazuje sklejania zapytania bez wyjątków.
security:
	bandit -r .claude/hooks -s B404,B603,B607 --confidence-level medium
	bandit -r .claude/hooks -t B608

audit:
	pip-audit

# Cel nie obejmuje testów krytycznych z realną bazą: kontrola jakości kodu ma działać także na maszynie,
# na której baza nie stoi. Projekt dokłada osobny cel dla przebiegu krytycznego razem z pierwszym takim testem.
check: lint typecheck deadcode deps security audit test
