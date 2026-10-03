# Standard review i Definition of Done

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

"Review" w tym repozytorium nazywa dziś dwie różne rzeczy pod bardzo podobnymi nazwami: artefakt `<ZADANIE>_REVIEW.md` w łańcuchu agentowym (log przebiegu jednego zadania) i proces oceny, czy zmiana jest gotowa do mergu (to, co robi `dod-reviewer`). Bez jednego miejsca opisującego drugie z nich, kryteria gotowości i kolejność raportu żyją wyłącznie rozproszone po plikach skilla i agenta, w dwóch niezależnie utrzymywanych kopiach (Claude Code i Codex) - a to jest dokładnie ten koszt duplikacji, przed którym przestrzega `standard_architecture.md`.

Ten standard rozstrzyga trzy pytania: co odróżnia review od artefaktu o tej samej nazwie z łańcucha agentowego, jaki jest mechanizm i kolejność raportu review w tym repozytorium, oraz jakie punkty definiują zmianę jako gotową do mergu.

## Zakres i granice

Ten standard odpowiada za proces review zmiany i za Definition of Done repozytorium: mechanizm, którym review się wykonuje, kolejność raportu, kryteria tego, co zgłaszać i czego nie, oraz checklistę końcową.

Czego tu nie ma:

- Sam mechanizm łańcucha agentowego prowadzącego do review (seed -> shape -> PRD -> plan -> implementacja -> review) - to jest `standard_agentic_workflow.md`.
- Artefakt `<ZADANIE>_REVIEW.md` - log przebiegu konkretnego zadania (co pominięto, na co agent trafił, jakie decyzje padły przy kodzie). To dokument opisujący historię jednego zadania i traci znaczenie po jego zamknięciu; ten standard opisuje powtarzalny proces oceny, ważny dla każdej zmiany. Zdanie rozstrzygające: `_REVIEW.md` jest dziennikiem zdarzeń, ten standard jest kryterium oceny.
- Definition of Done dla wewnętrznej architektury jednej warstwy nie istnieje jako osobna checklista, bo zbiór nie ma dziś standardu opisującego tę architekturę - patrz `docs/standards/README.md`, sekcja granic i długów. Checklista tego standardu stosuje się zawsze, do każdej zmiany.
- Same reguły, które review sprawdza (jakość kodu, architektura, dokumentacja, formatowanie, bezpieczeństwo i tak dalej) - każda mieszka we właściwym standardzie. Ten dokument mówi, jak i w jakiej kolejności je sprawdzić, nie co dokładnie każda z nich nakazuje.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Doprecyzowanie właściwe dla tego standardu: obowiązek przejścia przez ten proces dotyczy każdej zmiany kodu produkcyjnego w ramach zadania, niezależnie od jej rozmiaru - definicja "modułu dotkniętego" z `docs/standards/README.md` zawęża, których standardów dotyczy obowiązek dostosowania, nie zawęża tego, czy review w ogóle się odbywa. Przyjęcie tego standardu nie wymusza retroaktywnego review zmian już zamergowanych.

## Mechanizm review w tym repozytorium

Review wykonuje skill `implementation-dod-review`, wołany wprost albo przez subagenta `dod-reviewer`. Skill ma kanoniczną parę objętą testem parytetu (`standard_agentic_workflow.md`, rozdz. 6.2): `.claude/skills/implementation-dod-review/SKILL.md` dla Claude Code i `.agents/skills/implementation-dod-review/SKILL.md` dla Codeksa, identyczne co do znaku poza różnicami jawnie dozwolonymi przez ten test.

Subagent `dod-reviewer` (`.claude/agents/dod-reviewer.md`) istnieje wyłącznie w Claude Code - subagenci w tym sensie są mechanizmem Claude-only, bez odpowiednika w `.agents/` (`standard_agentic_workflow.md`, rozdz. 6.4). `.codex/agents/dod-reviewer.toml` jest odpowiednikiem po stronie Codeksa w innym mechanizmie (natywna rola Codeksa, nie subagent) - zgodny treściowo z wersją Claude i objęty kontrolą parytetu par ról w `tests/architecture/test_agent_docs_parity.py`. Kontrola porównuje instrukcje odczytane z obu wariantów i dopuszcza między nimi dokładnie jedną jawnie nazwaną różnicę: nazwę uruchamiacza komend, bo Codex nie zna narzędzi o nazwach `Bash` i `PowerShell`. Rozjazd w czymkolwiek innym zatrzymuje testy, zamiast czekać na wychwycenie okiem.

Subagent `dod-reviewer` nie ma dostępu do `Edit` ani `Write` i działa w `permissionMode: plan` - nie może wprowadzić poprawki, tylko ją opisać. To wymuszenie na poziomie uprawnień, nie tylko instrukcji: review ocenia gotowość zmiany, nie naprawia jej za autora.

Review wywołuje się automatycznie na końcu `plan-implement` (`standard_agentic_workflow.md`, rozdz. 4.3, krok 8) oraz ręcznie, w dowolnym momencie, na żądanie użytkownika - na aktualnym diffie, jeśli kontekst gita jest dostępny, albo na plikach wskazanych przez użytkownika, gdy nie jest.

## Mapa standard - narzędzie weryfikujące

Tabela niżej mapuje każdy standard na komendę, która sprawdza jego regułę automatycznie - tam, gdzie taka komenda istnieje. Kolumna Grupa mówi, czy standard należy do rdzenia workflow, czy do profilu Pythona. Projekt spoza profilu Pythona usuwa wiersze profilu razem z plikami standardów, według `docs/standards/README.md`. Żadna z tych komend nie pokrywa całej checklisty swojego standardu: sprawdza mechaniczną, powtarzalną część (składnię, format, znany wzorzec), nie regułę domenową ani decyzję architektoniczną. Przegląd checklisty standardu względem zmiany odbywa się zawsze, niezależnie od tego, czy komenda dla niego istnieje.

| Standard                       | Grupa          | Automatyczna weryfikacja                                                                                                                                 |
| ------------------------------ | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standard_agentic_workflow.md` | rdzeń          | `pytest tests/architecture/test_agent_docs_parity.py tests/architecture/test_session_context_hook.py tests/architecture/test_dangerous_commands_hook.py` |
| `standard_agent_docs.md`       | rdzeń          | `pytest tests/architecture/test_plan_document_contract.py`                                                                                               |
| `standard_review.md`           | rdzeń          | brak narzędzia - przegląd ręczny (ten dokument)                                                                                                          |
| `standard_documentation.md`    | rdzeń          | brak narzędzia - przegląd ręczny                                                                                                                         |
| `standard_formatting.md`       | rdzeń          | `ruff format --check .`, `npx --no-install prettier --check "**/*.md"`, `pytest tests/architecture/test_prose_style.py`                                  |
| `standard_git.md`              | rdzeń          | `pytest tests/architecture/test_conflict_markers.py`                                                                                                     |
| `standard_architecture.md`     | profil Pythona | brak narzędzia - przegląd ręczny                                                                                                                         |
| `standard_config.md`           | profil Pythona | brak w szablonie - test kontraktu środowiska powstaje z pierwszą pozycją środowiska                                                                      |
| `standard_database.md`         | profil Pythona | `bandit` (reguła B608, sklejanie zapytania ze stringów)                                                                                                  |
| `standard_errors.md`           | profil Pythona | brak narzędzia - przegląd ręczny                                                                                                                         |
| `standard_idempotency.md`      | profil Pythona | brak narzędzia - przegląd ręczny                                                                                                                         |
| `standard_code_quality.md`     | profil Pythona | `ruff check .`, `mypy`, `vulture`, `deptry .`                                                                                                            |
| `standard_logging.md`          | profil Pythona | `ruff check .` (reguła G, leniwe placeholdery zamiast f-stringa)                                                                                         |
| `standard_naming.md`           | profil Pythona | `ruff check .` (reguła N)                                                                                                                                |
| `standard_security.md`         | profil Pythona | `bandit`, `pip-audit` (tylko przy nowej albo podniesionej zależności)                                                                                    |
| `standard_tests.md`            | profil Pythona | `pytest`                                                                                                                                                 |
| `standard_time.md`             | profil Pythona | brak narzędzia - przegląd ręczny                                                                                                                         |
| `standard_worker.md`           | profil Pythona | brak w szablonie - test spójności rejestru zadań powstaje z pierwszym zadaniem okresowym                                                                 |

Komenda uruchamia się z korzenia repozytorium, w środowisku z zainstalowaną grupą zależności `dev`. Tabela wskazuje samo narzędzie, nie nazwę targetu w `makefile` - targety mogą się przemianować, narzędzie stojące za regułą standardu nie zmienia się przy takiej zmianie.

## Kolejność raportu i werdykt

Raport review ma zawsze pięć sekcji, w tej kolejności:

1. Blockery - problemy, które oznaczają, że zmiana nie jest gotowa.
2. Ryzyka - problemy, które mogą być akceptowalne, ale wymagają świadomej decyzji, nie przeoczenia.
3. Usprawnienia - opcjonalne porządki i sugestie jakościowe, niewymagane do gotowości.
4. Weryfikacja - przejście po wszystkich standardach z mapy wyżej, każdy z jednym z czterech stanów: nie dotyczy (zmiana nie dotyka obszaru tego standardu, z krótkim powodem), sprawdzono automatycznie (standard ma zmapowaną komendę, komenda została odpalona, a wynik albo jego streszczenie jest w raporcie), sprawdzono ręcznie (standard nie ma zmapowanej komendy, więc weryfikacją jest wyłącznie przegląd checklisty), niesprawdzone (reviewer nie zdążył przed limitem wywołań; pozycja wymaga dokończenia, zanim werdykt obejmie ten standard). Naruszenie znalezione po drodze idzie do Blockerów albo Ryzyk, nie zostaje tutaj.
5. Werdykt - jeden z trzech: `ready`, `ready after minor fixes`, `not ready`.

Ta kolejność nie jest przypadkowa: blockery i ryzyka muszą być widoczne, zanim czytelnik dotrze do drobnych usprawnień, inaczej realne zagrożenie ginie w szumie stylistycznych uwag. Werdykt jest zawsze ostatni, bo jest wnioskiem z sekcji wyżej, nie punktem wyjścia do ich uzasadniania.

Przejście po całej mapie, nie tylko po standardach, które reviewer po przeczytaniu diffu uzna za właściwe, jest zamierzonym wymogiem. Wybór relevantnych standardów zostawiony wyłącznie ocenie reviewera jest niewidoczny z zewnątrz - pominięcie standardu, którego zmiana faktycznie dotyka, wygląda z raportu identycznie jak jego świadome i uzasadnione wykluczenie. Jawna lista wszystkich standardów z mapy, z jednym ze stanów przy każdym, zamienia to w coś, co czytelnik raportu może zweryfikować sam, bez odtwarzania toku myślenia reviewera.

`ready after minor fixes` jest zarezerwowany dla sytuacji, w której jedyne znalezione problemy są w sekcji Ryzyka albo Usprawnienia, nie Blockery - obecność choćby jednego blockera wyklucza ten werdykt.

Przebieg waży więcej niż review. Tam, gdzie da się podnieść środowisko i uruchomić przebieg, odczyt kodu i dokumentów nie zastępuje przebiegu. Znana porażka przebiegu w zakresie zmiany (testy, łańcuch na środowisku, testy e2e) wyklucza werdykt `ready`, nawet gdy litera kryterium akceptacji jest spełniona. Przed werdyktem reviewer sprawdza, czy przebieg późniejszy niż ocena kryterium nie przeczy ocenianemu zakresowi, i ocenia kod gałęzi docelowej, nie to, która inicjatywa miała daną rzecz domknąć.

Werdykt nazywa swój zakres: całą inicjatywę, jedno zadanie z kilku, sam plan albo wskazane pliki. Od tego zdania zależy, co dzieje się z katalogiem inicjatywy po review: końcowe `ready` dla całej inicjatywy kwalifikuje ją do archiwum `plans_finished/`, `ready` dla jednego zadania, planu albo części kodu nie (`standard_agentic_workflow.md`, rozdz. 4.6). Review tę kwalifikację raportuje, ale nie wykonuje przeniesienia - pozostaje w trybie odczytu, a przenosi `plan-implement` po powrocie z review albo agent, któremu użytkownik polecił porządki wprost. Review wywołane na inicjatywie już jawnie zakończonej mówi o tym w raporcie zamiast oceniać ją od nowa.

## Co zgłaszać i czego nie zgłaszać

Review podpiera każdy finding konkretną ścieżką pliku i powodem - ogólna uwaga bez wskazania miejsca nie daje autorowi zmiany niczego do poprawienia. Review nie zgaduje kontraktu, którego nie znajduje w kodzie ani w standardach - brakujący plik, standard, granica modułu, test albo dokument jest zgłaszany jawnie jako brak, nie domyślany.

Review nie zgłasza:

- spekulatywnych przepisań, których zmiana nie wymaga,
- preferencji stylistycznych bez konkretnego, nazwanego ryzyka,
- problemów zastanych, spoza zakresu bieżącej zmiany, chyba że utrudniają zrozumienie samej zmiany.

Uzasadnienie: review oceniający zmianę względem wszystkiego, co kiedykolwiek było niedoskonałe w repozytorium, przestaje być użyteczny - autor zmiany nie może naprawić całej historii kodu w jednym PR, a rozmycie uwagi na problemy zastane odciąga ją od problemów, które ta konkretna zmiana faktycznie wprowadziła.

## Checklista

Zadanie można uznać za zakończone, gdy:

- zmiany są zgodne z zasadami DRY, SOLID i KISS,
- kod jest prosty, czytelny i nie zawiera niepotrzebnych fallbacków,
- fallbacki wynikają z realnej potrzeby bezpieczeństwa kodu, a nie z nieznajomości kontraktu,
- niejasne miejsca zostały jasno wskazane zamiast zgadywania,
- potencjalne błędy lub ryzyka zostały opisane użytkownikowi,
- kod nie zawiera komentarzy linijkowych,
- funkcje wymagające wyjaśnienia mają docstringi opisujące po ludzku, co robią,
- formatowanie kodu jest zgodne z zasadami z tego pliku,
- jeśli implementacja była większa lub zmieniała jakiś moduł, całość musi być po zmianie zgodne ze wszystkimi standardami z /docs/standards
- odpowiedź końcowa jasno opisuje, co zostało zmienione,
- odpowiedź końcowa wyjaśnia, dlaczego zmiany zostały wykonane,
- odpowiedź końcowa opisuje podjęte decyzje,
- odpowiedź końcowa wskazuje potencjalne problemy,
- odpowiedź końcowa mówi wprost, czego nie udało się ustalić, jeśli coś było niejasne,
- sekcja Weryfikacja przechodzi po wszystkich standardach z mapy, nie tylko po podzbiorze uznanym za właściwy, i dla standardu ze zmapowaną komendą ta komenda faktycznie została odpalona, nie tylko oceniona na oko,
- kryteria akceptacji rozliczono przebiegiem wszędzie, gdzie przebieg był możliwy, a żaden znany przebieg nie przeczy werdyktowi.
