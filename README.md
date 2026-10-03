# agentic-workflow

Szablon startowy nowych projektów: workflow agentowy dla Claude Code i Codeksa oraz profil standardów serwisu w Pythonie. Szablon nie zawiera kodu żadnego produktu.

## Co jest w środku

- `.claude/`, `.agents/`, `.codex/` - skille łańcucha (`plan-shape`, `plan-prd`, `plan-implement`, `implementation-dod-review`, `load-context`), subagenci `repo-researcher` i `dod-reviewer` z wariantami dla Codeksa, hook `local_docs_context.py` z kontekstem startowym sesji, hook `block_dangerous_commands.py` blokujący komendy niszczące oraz `git commit` i `git push`, ustawienia blokujące odczyt plików sekretów.
- `agent_docs/` - opis projektu dla hooka, metodologia łańcucha i konwencja pamięci trwałej.
- `docs/standards/` - mapa standardów, sześć standardów rdzenia workflow, dwanaście standardów profilu Pythona i dwa puste rejestry.
- `tests/architecture/` - bramki rdzenia: parytet Claude Code i Codeksa, hooki, styl prozy, kontrakt dokumentu planu, markery konfliktu.
- `plans/` i `plans_finished/` - miejsce na inicjatywy w toku i ich archiwum, puste.
- `pyproject.toml`, `makefile`, `package.json`, `.prettierrc` - narzędzia jakości i formatowania.

Pełny opis systemu jest w `docs/standards/standard_agentic_workflow.md`, a punkt wejścia do standardów w `docs/standards/README.md`.

## Wymagania

Na maszynie muszą być `make`, `python` w wersji 3.13 oraz `node` z `npm` dla prettiera formatującego markdown. Narzędzia Pythona idą do środowiska wirtualnego, prettier do `node_modules` w wersji przypiętej w `package.json`.

```bash
python -m venv venv
venv/Scripts/python -m pip install -e ".[dev]"
npm ci
make check
```

## Jak założyć projekt z szablonu

1. Skopiuj pliki szablonu do nowego repozytorium, bez katalogu `.git` szablonu.
2. Wypełnij miejsca oznaczone `<...>` w `CLAUDE.md`, `AGENTS.md` i `agent_docs/session_context.md`: opis projektu, specyfikację produktu, zespół i uprawnienia agenta wobec środowiska docelowego. `CLAUDE.md` i `AGENTS.md` mają być identyczne poza nazwą narzędzia - pilnuje tego test parytetu.
3. Wpisz nazwę projektu w `pyproject.toml`, `package.json` i `package-lock.json`.
4. Projekt w profilu Pythona dopisuje katalogi warstw do `[tool.mypy]` i `[tool.vulture]` w `pyproject.toml` oraz do celu `security` w `makefile` razem z pierwszym kodem, a bramki profilu (granice warstw, kontrakt środowiska, spójność rejestru zadań okresowych) zakłada razem z pierwszym kodem danej warstwy.
5. Projekt spoza profilu Pythona usuwa standardy profilu wymienione w `docs/standards/README.md`, ich wiersze w mapach `docs/standards/README.md` i `docs/standards/standard_review.md` oraz narzędzia Pythona, których nie używa. Bramki rdzenia zostają, bo są testami w Pythonie i wymagają `pytest`.
6. Lista dziesięciu kategorii ryzyka blokującego jest dobrana dla serwisu z bazą danych i interfejsem programistycznym. Projekt o innym profilu ryzyka zmienia ją w trzech miejscach wymienionych w `docs/standards/standard_agentic_workflow.md` rozdz. 3.3.
7. Uruchom `make check`.

## Skille osobiste a skille projektu

Gdy w `~/.claude/skills` leży skill o nazwie skilla projektu, Claude Code ładuje kopię osobistą zamiast projektowej, bez żadnego komunikatu. Hook SessionStart ostrzega o takiej kolizji na starcie sesji, a regułę opisuje `docs/standards/standard_agentic_workflow.md` rozdz. 6.5.

## Przenoszenie poprawek do szablonu

Szablon służy wyłącznie na start: projekty założone z niego nie dostają jego późniejszych zmian same, a szablon nie dostaje poprawek z projektów. Poprawkę workflow zrobioną w projekcie przenosi się do szablonu ręcznie:

- plik rdzenia (skill, subagent, hook, bramka, standard rdzenia albo profilu) przenosi się w całości, po usunięciu treści specyficznej dla projektu: nazw produktu i systemów, odwołań do specyfikacji, decyzji i inicjatyw projektu,
- plik części projektowej (`CLAUDE.md`, `AGENTS.md`, `agent_docs/session_context.md`, mapa standardów, rejestry) przenosi się wyłącznie w części ogólnej.

Po przeniesieniu `make check` w szablonie ma przechodzić, a grep po nazwie projektu źródłowego ma nie dawać trafień.
