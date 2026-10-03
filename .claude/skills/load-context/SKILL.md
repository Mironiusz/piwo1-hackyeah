---
name: load-context
description: użyj tego skilla, gdy potrzebujesz kontekstu folderu, jednostki kodu albo funkcjonalności repozytorium przed analizą, wyjaśnieniem, debugowaniem, refaktoryzacją, dokumentowaniem albo review. uruchom dołączony skrypt dump_context.py na wskazanym folderze, żeby zrobić jeden zrzut do output.txt, i użyj tego zrzutu jako głównego źródła zamiast otwierać wiele plików po kolei.
---

# Wczytanie kontekstu

Użyj `scripts/dump_context.py`, gdy potrzebujesz kontekstu z folderu repozytorium.

Cel jest prosty: zrobić jeden zrzut wskazanego folderu do `output.txt`, przeczytać ten plik i oprzeć na nim analizę, zamiast ręcznie otwierać wiele plików jeden po drugim.

## Domyślna komenda

```bash
python .claude/skills/load-context/scripts/dump_context.py --input <folder> --output output.txt
```

Przykład:

```bash
python .claude/skills/load-context/scripts/dump_context.py --input ./config --output output.txt
```

Po utworzeniu pliku przeczytaj `output.txt` i oprzyj analizę na nim.

## Dostępne flagi

`--input` jest wymagany i wskazuje folder do zrzucenia.

`--output` ustawia ścieżkę pliku wyjściowego. Domyślnie: `output.txt`.

`--extensions` zastępuje domyślną listę dozwolonych rozszerzeń. Domyślnie: `.py .html .js .css .sql .md`.

`--ignore-dirs` zastępuje domyślną listę ignorowanych nazw katalogów. Domyślnie ignorowane są katalogi będące technicznym szumem, na przykład `venv`, `.venv`, `__pycache__`, `.git`, `node_modules`, `build`, `dist`, `logs`, `exports` i `old`.

`--extra-ignore-dirs` dodaje kolejne ignorowane nazwy katalogów, zachowując domyślne.

`--ignore-extensions` pomija wybrane rozszerzenia w tym przebiegu, nawet jeśli są dozwolone przez `--extensions`.

## Przydatne przykłady

Zrzut jednostki kodu z domyślnymi ustawieniami:

```bash
python .claude/skills/load-context/scripts/dump_context.py --input ./service --output output.txt
```

Zrzut tylko plików Python, Markdown i SQL:

```bash
python .claude/skills/load-context/scripts/dump_context.py --input ./service --output output.txt --extensions .py .md .sql
```

Zrzut z pominięciem Markdown i CSS:

```bash
python .claude/skills/load-context/scripts/dump_context.py --input ./config --output output.txt --ignore-extensions .md .css
```

Zrzut z dodatkowo ignorowanymi folderami lokalnymi:

```bash
python .claude/skills/load-context/scripts/dump_context.py --input ./config --output output.txt --extra-ignore-dirs tmp generated snapshots
```

## Bezpieczeństwo

Skrypt nigdy nie dołącza plików `.env`, `.env.*`, `.pem`, `.key`, `.p12` ani `.pfx`.

`.env.example` jest dozwolony.

Trzymaj ten przepływ mały. Nie buduj dla tego skilla manifestów, przebiegów na próbę ani raportów audytowych.
