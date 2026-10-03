# AGENTS.md

## Cel pliku

Ten plik opisuje stałe zasady pracy w tym repozytorium. Codex ma stosować je podczas analizy, pisania kodu, refaktoryzacji, dokumentowania i wyjaśniania zmian.

## Co budujemy

<Nazwa produktu> to <jedno albo dwa zdania o tym, czym jest projekt, dla kogo jest i czego świadomie nie robi>.

Źródłem prawdy o produkcie jest `<ścieżka do specyfikacji produktu>`: <co specyfikacja zawiera>. Przy rozbieżności między specyfikacją a czymkolwiek innym w repozytorium obowiązuje specyfikacja. Ten sam opis w dwóch zdaniach stoi w `agent_docs/session_context.md`, skąd hook SessionStart wstawia go na początek każdej sesji.

## Zespół

<Skład zespołu i zasady dotyczące osób, które dołączyły albo odeszły, jeśli wpływają na pracę agenta: czyje gałęzie, inicjatywy i decyzje przejmuje użytkownik, kogo nie pytać o zdanie. Sekcję usuń, jeśli nie ma nic do zapisania.>

## Język i styl komunikacji

- Pisz po polsku.
- Używaj luźnego, potocznego i studenckiego języka, ale zachowuj profesjonalną terminologię.
- Zawsze używaj polskich znaków w rozmowie i w dokumentacji.
- Normalnie rozmawiaj z użytkownikiem i wyjaśniaj swoje decyzje.
- Gdy coś nie jest jasne, powiedz o tym wprost zamiast zgadywać.
- Gdy widzisz potencjalny błąd w kodzie, poinformuj o nim.

## Zasady pracy z kodem

- Dbaj o zasady DRY, SOLID i KISS.
- Unikaj fallbacków, gdy nie znasz kontekstu. W takim wypadku lepiej nie stworzyć nic i dopytać się lub poszukać, niż robić fallback na potencjalny kontrakt, który naprawdę nie istnieje.
- Używaj tylko koniecznych fallbacków, wynikających z dobrych praktyk pisania bezpiecznego kodu, a nie z niewiedzy.
- Gdy poprawność danych nie jest pewna, zapytaj, czy można ją zagwarantować.
- Zawsze wyjaśniaj podjęte decyzje.
- Zawsze jasno mów, co zostało zmienione.

## Hierarchia rozstrzygania konfliktów reguł

Gdy dwie zasady z tego pliku albo ze standardów w docs/standards się gryzą, rozstrzygaj w tej kolejności:

1. Poprawność i integralność danych.
2. Brak zgadywania kontraktu - lepiej zapytać niż dorobić fallback.
3. Zgodność z docs/standards.
4. Czytelność.
5. Wydajność.
6. DRY i unikanie zbędnej sprytności.

Ta kolejność wynika wprost z zasad powyżej: zakaz fallbacków bez kontekstu i dopytywanie zamiast zgadywania są tu najmocniej akcentowane, więc stoją najwyżej.

## Praca z gitem

- Nie twórz commitów i nie wysyłaj niczego na zdalne repozytorium. `git commit` i `git push` są zakazane bezwarunkowo, także na wyraźną prośbę użytkownika - commit tworzy człowiek.
- `git add` i `git rebase` wykonuj wyłącznie na wyraźną prośbę użytkownika, nigdy z własnej inicjatywy.
- Pozostałe operacje wykonuj bez pytania: odczyt, `git fetch`, `git pull`, `git stash`, przełączanie i tworzenie gałęzi, `git merge` lokalny, `git worktree`.
- O operacji spoza tych list rozstrzyga jedno kryterium: czy dotyka historii. Jeśli tworzy, przepisuje albo publikuje historię, nie rób jej sam.
- Do main i dev zmiana wchodzi wyłącznie przez Merge Requesta. W drugą stronę, na gałąź roboczą, schodzi zwykłym mergem.
- Uzasadnienia, role gałęzi i przypadki graniczne są w docs/standards/standard_git.md.

## Środowisko docelowe

<Gdzie stoi środowisko docelowe i jakie uprawnienia ma wobec niego agent, w trzech poziomach:>

- bez pytania: <na przykład odczyt stanu, tokenem tylko do odczytu>,
- wyłącznie na wyraźną prośbę użytkownika: <na przykład zmiana zmiennej środowiskowej, wdrożenie, restart>,
- zakazane bezwarunkowo, także na wyraźną prośbę: <na przykład kasowanie zasobów i kopii zapasowych, zmiana ustawień serwera, tworzenie i rotacja tokenów>.

Niezależnie od projektu: żaden adres, host, login ani sekret środowiska docelowego nie wchodzi do repozytorium w jakiejkolwiek formie - ani do kodu, ani do dokumentacji, ani do artefaktów inicjatywy. Regułę opisuje docs/standards/standard_config.md.

## Komentarze i dokumentowanie kodu

- Nie pisz w kodzie komentarzy linijkowych.
- Zamiast komentarzy linijkowych stosuj docstringi.
- Docstringi mają po ludzku opisywać, co robi dana funkcja.
- Zakaz komentarzy linijkowych nie oznacza braku komunikacji z użytkownikiem.
- W rozmowie normalnie wyjaśniaj decyzje, ryzyka i zmiany.
- Po więcej informacji o dokumentacji, odwołaj się do docs/standards/standard_documentation.md

## Formatowanie kodu

- Przekazuj parametry do funkcji rozdzielone spacjami, dopóki linijka nie przekroczy 200 znaków.
- Po przekroczeniu 200 znaków rozbij parametry na wiele linii.
- Nie używaj w kodzie znaków: —, –, −.
- Zamiast nich używaj zwykłego znaku: -.
- Nie używaj w kodzie znaków: “, ”.
- Zamiast nich używaj zwykłego znaku: ".
- Nie używaj w kodzie znaków: →, ←, ↔.
- Zamiast nich używaj: ->, <-, <->.
- Nie używaj emotek.
- Nie nadużywaj cudzysłowów.
- Używaj cudzysłowów tylko wtedy, gdy są potrzebne, na przykład dla dosłownego cytatu, nazwy pola albo fragmentu kodu w tekście.

## Odpowiedź po wykonaniu zadania

Po każdej zmianie opisz:

- co zostało zmienione,
- dlaczego zostało zmienione,
- jakie decyzje zostały podjęte,
- jakie potencjalne problemy zostały zauważone,
- czego nie udało się ustalić, jeśli coś było niejasne.

## Definition of Done

Pełna checklista Definition of Done jest w `docs/standards/standard_review.md`.

## Pełna zgodność ze standardami

To repozytorium nie ma zastanego kodu, więc standardy obowiązują w wersji zaostrzonej: pełna zgodność od pierwszego commita, bez okresu przejściowego. Miękka reguła odstępstwa, dopuszczająca niezgodny kod dopóki nikt go nie modyfikuje, tutaj nie obowiązuje. Gdy repozytorium będzie mieć zastany kod, rozluźnienie tej reguły ma być jawną decyzją zapisaną w mapie standardów, nie stanem odziedziczonym.

## Schemat bazy danych

Jeśli projekt trzyma zrzut schematu bazy, jego miejsce jest wpisane w mapie standardów. Zrzut jest obrazem stanu faktycznego serwera, nie źródłem prawdy o schemacie - edycja pliku zrzutu nie zmienia bazy.

## Decyzje odroczone

Część decyzji jest świadomie odłożona, z zapisanym powodem i warunkiem rozstrzygnięcia - lista jest w `docs/standards/decision_registry.md`. Zanim uznasz brak reguły za lukę, sprawdź, czy nie jest tam wpisany jako odroczenie. Nie rozstrzygaj takiego wpisu domysłem.

## Cykl zadania i system agentowy

Repozytorium ma warstwę agent_docs/ obok stałego docs/ oraz łańcuch plan-shape -> plan-prd -> plan-implement, który prowadzi zadanie od zgłoszenia przez pięć artefaktów w plans/<INICJATYWA>/ (SEED, SHAPE, PRD, PLAN, REVIEW) do zaimplementowanej zmiany i trwałej pamięci w agent_docs/memory/. Pełny opis całego systemu - artefakty zadania, kategorie ryzyka blokującego, kolizja nazw skilli personal/project, praca równoległa na jednym drzewie, granica między \_REVIEW.md a agent_docs/memory/, dualizm Claude Code i Codeksa - jest w docs/standards/standard_agentic_workflow.md. Inicjatywa jawnie zakończona albo anulowana przechodzi w całości do plans_finished/<INICJATYWA>/, a wznowiona wraca do plans/ - kryterium, ochrona historii i obsługa odwołań są w rozdz. 4.6 tego standardu; plans/ trzyma tylko pracę w toku.

## Mapowanie: co otworzyć przed zadaniem

Pełna tabela mapowania typu zadania na dokumenty do otwarcia, w tym kiedy sięgać po agent_docs/ i po docs/, jest w docs/standards/README.md.
