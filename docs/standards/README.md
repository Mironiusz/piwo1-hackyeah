# Mapa standardów

Stan dokumentu: 2026-10-03

Ten katalog jest zbiorem wszystkich standardów obowiązujących w repozytorium. Ten plik jest punktem wejścia do zbioru - nie otwieraj standardu z pominięciem tej mapy, bo status dokumentu i jego grupa są zapisane tutaj.

Źródłem prawdy dla każdej reguły jest standard, nie `CLAUDE.md` ani `AGENTS.md`. Przy rozbieżności między rdzeniem repozytorium a standardem obowiązuje standard - rdzeń celowo zatrzymuje tylko twarde zakazy stosowalne bez kontekstu, a uzasadnienia, wyjątki i przypadki graniczne mieszkają tutaj. Ponad wszystkim stoi specyfikacja produktu wskazana w `CLAUDE.md`, sekcja Co budujemy: przy rozbieżności między standardem a specyfikacją obowiązuje specyfikacja.

## Standardy

Zbiór dzieli się na dwie grupy:

- Rdzeń workflow - sześć standardów opisujących pracę z agentami, dokumentację, formatowanie, review i gita. Obowiązują w każdym projekcie założonym z szablonu.
- Profil Pythona - dwanaście standardów serwisu w Pythonie z bazą PostgreSQL, migracjami Alembica i osobnym procesem worker. Projekt, który nie jest takim serwisem, usuwa ich pliki, ich wiersze z tej mapy i z mapy w `standard_review.md`, a odwołania do nich w rdzeniu zastępuje własnymi standardami albo usuwa.

Znaczenie statusów: gotowy - dokument ma pełną treść reguł. częściowy - dokument ma treść, ale co najmniej jedna jego reguła czeka na decyzję albo pomiar; powód jest w samym standardzie. szkielet - dokument ma tylko sekcje rdzeniowe z jednozdaniowymi opisami tego, co ma tu powstać.

| Plik                           | Grupa          | Status | Za co odpowiada                                                                      |
| ------------------------------ | -------------- | ------ | ------------------------------------------------------------------------------------ |
| `standard_agentic_workflow.md` | rdzeń          | gotowy | łańcuch seed -> plan -> review, hooki, subagenci, parytet Claude Code i Codeksa      |
| `standard_agent_docs.md`       | rdzeń          | gotowy | format SEED, SHAPE, PRD, PLAN, REVIEW i wpisów `agent_docs/memory`                   |
| `standard_review.md`           | rdzeń          | gotowy | proces review, mapa standard - narzędzie, Definition of Done                         |
| `standard_documentation.md`    | rdzeń          | gotowy | dokumentacja jednostek kodu i ton prozy                                              |
| `standard_formatting.md`       | rdzeń          | gotowy | formatowanie kodu i markdownu, znaki zakazane, zakaz pogrubień w prozie              |
| `standard_git.md`              | rdzeń          | gotowy | uprawnienia agenta wobec gita, role gałęzi, kierunki scalania                        |
| `standard_architecture.md`     | profil Pythona | gotowy | granica warstw, jedno miejsce dla reguł przekrojowych, wywołania zewnętrzne          |
| `standard_config.md`           | profil Pythona | gotowy | trzy warstwy konfiguracji, pliki środowiska, walidacja, sekrety                      |
| `standard_database.md`         | profil Pythona | gotowy | forma zmian schematu, prywatność bazy, dostęp do danych, zapytania                   |
| `standard_errors.md`           | profil Pythona | gotowy | obsługa błędów, ponowienia, limity czasu                                             |
| `standard_idempotency.md`      | profil Pythona | gotowy | klucz idempotencji, uzgadnianie, deduplikacja                                        |
| `standard_code_quality.md`     | profil Pythona | gotowy | statyczna analiza, złożoność, komentarze, wydajność                                  |
| `standard_logging.md`          | profil Pythona | gotowy | format wpisu logu, poziomy, dane osobowe w logu                                      |
| `standard_naming.md`           | profil Pythona | gotowy | nazwy plików, funkcji i stałych                                                      |
| `standard_security.md`         | profil Pythona | gotowy | statyczna analiza bezpieczeństwa, podatności zależności, dane na środowisku lokalnym |
| `standard_tests.md`            | profil Pythona | gotowy | warstwy testów, testy krytyczne, testy obowiązkowe                                   |
| `standard_time.md`             | profil Pythona | gotowy | model czasu, strefy, okna czasowe w danych                                           |
| `standard_worker.md`           | profil Pythona | gotowy | proces worker, kontrakt zadania okresowego, blokady                                  |

Granice między standardami opisuje sekcja Zakres i granice w każdym z nich.

## Rejestry obok standardów

Dwa pliki w tym katalogu nie są standardami i nie mają sekcji rdzeniowych:

- `naming_registry.md` - rozwijalny rejestr nazw faktycznie używanych w repozytorium, opisujący stan faktyczny, nie docelowy. `standard_naming.md` odsyła do niego wprost. W szablonie jest pusty.
- `decision_registry.md` - decyzje świadomie odłożone, z powodem odroczenia i warunkiem rozstrzygnięcia. Patrzy w przyszłość, w odróżnieniu od sekcji granic i długów na końcu tego pliku, która patrzy w przeszłość. W szablonie jest pusty.

## Reguła odstępstwa

Wspólna dla wszystkich standardów, w wersji zaostrzonej wobec repozytorium bez zastanego kodu:

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany - na przykład po pierwszym wydaniu na produkcję - rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w tym pliku wraz z datą i powodem. W wersji miękkiej niezgodny kod nie blokuje review, dopóki nikt go nie modyfikuje, a obowiązek dostosowania powstaje w module dotkniętym zmianą, czyli w jednostce kodu ze `standard_documentation.md`, w której zmiana modyfikuje choć jeden plik. Wersja miękka nie jest stanem, który wchodzi w życie sam.

Każdy standard powtarza tę regułę w swojej sekcji `Reguła odstępstwa`, z ewentualnym zawężeniem właściwym dla tematu. Wyjątek: `naming_registry.md` opisuje stan faktyczny z definicji, więc reguła stosuje się do niego inaczej - zapisane wprost w samym rejestrze.

## Co otworzyć przed zadaniem

| Typ zadania                                                    | Dokumenty do otwarcia przed pracą                                                                     |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Cokolwiek dotyczące zachowania produktu                        | specyfikacja produktu wskazana w `CLAUDE.md` - to jest źródło prawdy, nie punkt odniesienia           |
| Nowe zadanie o nieustalonym kształcie                          | `agent_docs/ai_workflows/shape_prd_workflow.md` i skill `plan-shape`, zanim powstanie jakikolwiek kod |
| Zamknięcie, anulowanie albo wznowienie inicjatywy w `plans/`   | `standard_agentic_workflow.md` rozdz. 4.6                                                             |
| Ocena gotowości zmiany do mergu                                | skill `implementation-dod-review` oraz `standard_review.md` z pozostałymi standardami z mapy          |
| Praca nad czymś, co ktoś już wcześniej zmieniał                | `agent_docs/memory/`, jeśli istnieje wpis                                                             |
| Cokolwiek dotyczące gita, gałęzi albo Merge Requesta           | `standard_git.md`                                                                                     |
| Pisanie albo aktualizacja dokumentacji kodu                    | `standard_documentation.md`                                                                           |
| Formatowanie kodu i markdownu                                  | `standard_formatting.md`                                                                              |
| Nowa jednostka kodu albo zmiana struktury istniejącej          | `standard_architecture.md` oraz `standard_naming.md`, sekcja o nazwach plików                         |
| Jakość kodu, komentarze, złożoność, wydajność                  | `standard_code_quality.md`                                                                            |
| Bezpieczeństwo kodu, statyczna analiza, podatności zależności  | `standard_security.md`                                                                                |
| Testy                                                          | `standard_tests.md`                                                                                   |
| Nazewnictwo plików i funkcji                                   | `standard_naming.md` oraz `naming_registry.md`                                                        |
| Konfiguracja i sekrety                                         | `standard_config.md`                                                                                  |
| Logowanie                                                      | `standard_logging.md`                                                                                 |
| Obsługa błędów, ponowienia, limity czasu                       | `standard_errors.md`                                                                                  |
| Idempotencja, uzgadnianie, deduplikacja                        | `standard_idempotency.md`                                                                             |
| Czas, strefy czasowe, okna czasowe w danych                    | `standard_time.md`                                                                                    |
| Cokolwiek dotyka tabeli, kolumny, widoku albo schematu         | `standard_database.md`, zrzut schematu dla stanu faktycznego, specyfikacja produktu dla docelowego    |
| Zadanie okresowe workera, blokada, okno czasowe, częstotliwość | `standard_worker.md`                                                                                  |
| Uprawnienia, widoczność odczytu                                | `standard_architecture.md`, sekcja o jednym miejscu dla reguł przekrojowych                           |

Projekt dopisuje do tej tabeli własne dokumenty, na przykład wiedzę operacyjną o środowisku albo zrzut schematu bazy, razem z ich proweniencją.

Jeśli po przeczytaniu wskazanych dokumentów kontrakt nadal nie jest jednoznaczny, to pytanie do użytkownika, nie miejsce na fallback - patrz hierarchia rozstrzygania konfliktów w `CLAUDE.md` i `AGENTS.md`. Sprawdź przy tym `decision_registry.md`: brak reguły może być zapisanym odroczeniem, nie luką.

## Granice nierozstrzygnięte i długi

Ta sekcja jest dziennikiem decyzji już podjętych i długu już zastanego. Rośnie o wpis za każdym razem, gdy inicjatywa zostawia po sobie świadomie nienaprawione znalezisko - artefakt `REVIEW.md` danej inicjatywy notuje je w skali jednego zadania, a tutaj trafia to, co ten zakres przekracza.

Długi, z którymi szablon startuje:

- Zbiór nie ma standardu opisującego wewnętrzną architekturę jednej warstwy, czyli podział odpowiedzialności między pliki w jej katalogu. Reguła podziału napisana przed powstaniem kodu byłaby zgadywaniem. Warunek powstania: warstwa ma tyle plików, że ich podział zaczyna budzić pytania przy review.
- `standard_documentation.md` nie ma sekcji Zakres i granice ani checklisty.
- Bramki profilu Pythona, które sprawdzają kod (granice warstw, kontrakt środowiska, spójność rejestru zadań okresowych), nie są częścią szablonu, bo szablon nie ma kodu. Projekt zakłada je razem z pierwszym kodem danej warstwy.
