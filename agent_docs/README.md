# agent_docs

Indeks warstwy agentowej repozytorium. Ta warstwa jest edytowalna przez agenta - w przeciwieństwie do `docs/`, które jest stałym źródłem standardów i wiedzy wygenerowanej maszynowo. Nigdy nie mieszaj tych dwóch: jeśli piszesz nowy standard albo poprawiasz opis jednostki kodu, to idzie do `docs/`; jeśli zapisujesz decyzję albo wzorzec z realnego zadania, to idzie tutaj.

## Co tu jest

- `session_context.md` - dwa zdania o projekcie i wskazanie specyfikacji produktu. Hook SessionStart wstawia je na początek każdej sesji, więc plik ma zostać krótki.
- `ai_workflows/shape_prd_workflow.md` - opis łańcucha seed -> shape -> PRD -> plan, obsługiwanego przez skille `plan-shape` i `plan-prd`, wraz z regułą archiwizacji zakończonej inicjatywy do `plans_finished/` i jej wznowienia. Otwórz przy każdym nowym zadaniu o nieustalonym kształcie i przed zamknięciem albo wznowieniem inicjatywy.
- `memory/` - trwałe decyzje per jednostka kodu, jeden plik na jednostkę, w folderze grupy odpowiadającej strukturze repozytorium. Konwencja wpisu, jednostka kodu i wybór pliku: patrz `docs/standards/standard_agent_docs.md`.

## Jak wybrać plik w memory

Patrz `docs/standards/standard_agent_docs.md`, sekcja "Format wpisu agent_docs/memory".

## Indeks docs/

`docs/` jest stałe i agent nie edytuje go poza zadaniem, które wprost tego dotyczy (`docs/standards/standard_agentic_workflow.md`, rozdz. 5.1).

- `docs/standards/` - stałe standardy pisane przez człowieka. Pełna lista, status gotowości i granice każdego standardu są w `docs/standards/README.md` - to jest punkt wejścia do tego katalogu, nie ta lista. Otwieraj konkretny standard wg mapowania w tamtym pliku, nie z góry.
- Katalogi, które projekt dokłada sam, na przykład zrzut schematu bazy wygenerowany maszynowo albo wiedzę operacyjną o środowisku, projekt wpisuje do mapy w `docs/standards/README.md` razem z ich proweniencją. Zrzut schematu jest obrazem stanu faktycznego serwera, nie źródłem prawdy o schemacie - edycja takiego pliku nie zmienia bazy.

Poza `docs/` jest jeszcze jedno źródło, nadrzędne wobec wszystkich: specyfikacja produktu wskazana w `CLAUDE.md`, sekcja Co budujemy. Przy rozbieżności z czymkolwiek innym obowiązuje ona.

Pełne mapowanie typ zadania -> dokument do otwarcia, w tym kiedy sięgać po `agent_docs/` i po `docs/`, jest w `docs/standards/README.md`.
