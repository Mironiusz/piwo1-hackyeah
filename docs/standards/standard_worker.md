# Standard workera i zadań okresowych

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Worker działa bez nadzoru, więc jego błąd nie jest widoczny od razu - ujawnia się jako brak czegoś, co miało się stać. Zadanie, które przestało się uruchamiać, nie zgłasza się samo; zadanie, które uruchomiło się dwa razy równolegle, zgłasza się jako zdublowane dane w miejscu, w którym nikt nie szuka przyczyny w harmonogramie.

Ten standard ustala kontrakt, który każde zadanie okresowe spełnia, żeby te dwa przypadki dały się wykryć i żeby nie zależały od pamięci osoby dopisującej kolejne zadanie.

## Zakres i granice

Ten standard odpowiada za: kontrakt zadania okresowego, mechanizm i konwencję blokad, limity czasu zadania, wynik przebiegu i sposób dopisywania nowego zadania.

Czego tu nie ma:

- co dokładnie robi każde zadanie - przesądza to specyfikacja produktu wskazana w `CLAUDE.md` i to ona jest tu źródłem prawdy, nie ten dokument;
- reakcja na błąd w trakcie zadania i trwały licznik prób - to `standard_errors.md`;
- czy powtórzony przebieg zdubluje efekt - to `standard_idempotency.md`;
- znaczenie wartości czasu i strefa, w której liczone są wyrażenia harmonogramu - to `standard_time.md`;
- format wpisu logu i identyfikator przebiegu - to `standard_logging.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Jeden proces, jeden rejestr zadań

Worker jest drugim punktem wejścia tego samego obrazu, nie osobnym serwisem i nie osobnym repozytorium. Dzieli z interfejsem programistycznym warstwę reguł i warstwę danych - zadanie okresowe woła te same reguły, co żądanie, i nie ma własnej, równoległej kopii logiki domenowej.

Rejestr zadań okresowych jest jeden i mieszka w warstwie reguł. Worker ma własną warstwę katalogową `worker/`, która odmierza czas i uruchamia zadania z tego rejestru. Warstwa nie ma ani jednej reguły domenowej i mieć nie ma: jedyna reguła, którą niesie, to okno godzinowe zadania, sprawdzane przy każdym jego starcie. Zależność biegnie tylko od warstwy `worker/` do warstwy reguł: warstwa nie zna ani obsługi żądania, ani warstwy danych, a żadna z pozostałych warstw nie zna jej, bo punkt wejścia procesu nie jest niczyją zależnością. Projekt pilnuje tej reguły testem architektury, który zakłada razem z pierwszym kodem tej warstwy; szablon go nie zawiera.

Konsekwencja: reguła wołana z zadania okresowego nie może zakładać, że istnieje wołający, jego token ani jego uprawnienia. Reguła, która tego wymaga, jest napisana pod obsługę żądania i wymaga poprawienia, a nie obejścia przez podstawienie sztucznego aktora w workerze.

Poprawność zadania nie opiera się na założeniu, że worker działa w jednej instancji - patrz sekcja Blokady niżej. Ta sama blokada bazodanowa chroni przed zdublowanym wyzwoleniem przez harmonogram, na przykład po restarcie albo przy drugiej instancji wyzwalacza, i przed dwoma procesami prowadzącymi to samo zadanie: zderzą się o nią tak samo jak dwie instancje jednego procesu. Gdy zadania z rejestru prowadzi więcej niż jeden proces, podział idzie po kolejce albo po procesie, nie po drugim rejestrze i nie po drugim punkcie wejścia.

## Kontrakt zadania okresowego

Każde zadanie okresowe ma wszystkie poniższe, jawnie, w kodzie:

- nazwę, unikalną w całym repozytorium, używaną w logu i w blokadzie;
- częstotliwość albo wyrażenie harmonogramu, liczone w strefie biznesowej projektu (`standard_time.md`);
- jawny limit czasu przebiegu, nie odziedziczony i nie domyślny;
- jawny limit czekania na blokadę, domyślnie zerowy - patrz niżej;
- nazwę blokady, unikalną, powiązaną z nazwą zadania;
- okno godzinowe, w którym zadanie wolno wystartować, albo jawny jego brak.

Brak którejkolwiek z tych wartości nie jest drobnym niedopatrzeniem: zadanie bez limitu czasu potrafi zablokować kolejny przebieg na godziny, a zadanie bez blokady potrafi wykonać swoją pracę dwa razy równolegle.

Okno godzinowe jest opcjonalne, ale jego brak jest wartością, nie pominięciem: znaczy zadanie chodzące o każdej porze. Godziny liczą się w strefie biznesowej, bo zadanie nocne ma być nocne dla człowieka, a nie dla serwera - liczone w czasie uniwersalnym przesuwałoby się o godzinę dwa razy w roku bez żadnej zmiany w repozytorium. Okno obejmuje godzinę początkową i nie obejmuje końcowej, więc dwa okna stykające się końcem i początkiem nie mają godziny wspólnej. Okna zadań nocnych prowadzonych przez ten sam proces mają być rozłączne: zadania jednego procesu jednowątkowego wykonują się jedno po drugim, więc zadanie startujące o tej samej godzinie co inne z tego procesu przestaje mieć własną porę. Okno musi być dłuższe od limitu czasu przebiegu, inaczej zadanie bywa ucinane terminem mimo zapasu w samym limicie.

## Blokady

Zadanie okresowe bierze blokadę przed rozpoczęciem pracy i zwalnia ją po zakończeniu, niezależnie od tego, czy zakończyło się powodzeniem. Blokada żyje w bazie, nie w pamięci procesu - blokada w pamięci nie chroni przed drugą instancją procesu, a to jest dokładnie ten scenariusz, przed którym ma chronić.

Limit czekania na blokadę jest domyślnie zerowy: gdy blokada jest zajęta, zadanie odpuszcza ten przebieg, zapisuje to i kończy się. Nie czeka w kolejce. Powód: zadanie okresowe uruchamiane co minutę, które czeka na blokadę, po godzinie awarii ma sześćdziesiąt oczekujących przebiegów, które wykonają się kaskadą jeden po drugim - zamiast jednego, który zrobi to samo raz.

Odpuszczenie przebiegu z powodu zajętej blokady nie jest błędem i nie jest logowane jako błąd. Jest normalnym stanem, który ma być widoczny w logu jako informacja.

## Wynik przebiegu

Wynik przebiegu odpowiada na pytanie, czy próba się odbyła, a nie czy zakończyła się sukcesem. Rozróżnia dwa stany: przebieg wykonany oraz przebieg odpuszczony z powodu zajętej blokady. To jest świadomy kontrakt, nie brak precyzji - o powodzeniu samej pracy mówi jej własny wynik: ile elementów przetworzono, ile pominięto i dlaczego.

Przebieg, który przetworzył część elementów i pominął resztę, jest przebiegiem wykonanym z zapisanymi pominięciami, nie przebiegiem nieudanym. Reguły tego zapisu są w `standard_errors.md`.

## Dopisywanie nowego zadania

Nowe zadanie okresowe wymaga: nazwy i blokady niekolidujących z istniejącymi, jawnych obu limitów, wpisu w `standard_worker.md`, jeśli zmienia się kontrakt, oraz uzupełnienia testu spójności zadań.

Test spójności sprawdza to, czego człowiek nie zauważy przy kolejnym zadaniu: unikalność nazw i blokad oraz obecność obu limitów. Projekt pilnuje tej reguły testem architektury, który zakłada razem z pierwszym kodem tej warstwy; szablon go nie zawiera. Dopisanie zadania bez uzupełnienia testu jest naruszeniem tego standardu, nawet jeśli samo zadanie działa poprawnie.

Zadanie usuwające dane wymaga osobnej uwagi. Usunięcie danych przez zadanie okresowe jest regułą produktową, nie decyzją techniczną: zadanie usuwające cokolwiek, czego specyfikacja produktu jawnie nie dopuszcza, wymaga rozstrzygnięcia przez właściciela produktu.

## Zachowanie na produkcji

Zmiana częstotliwości, okna czasowego, blokady albo kolejności kroków istniejącego zadania jest zmianą zachowania systemu działającego bez nadzoru. Taka zmiana należy do kategorii ryzyka blokującego w fazie shape (`standard_agentic_workflow.md` rozdz. 3.3) i wymaga jawnego rozstrzygnięcia, nie decyzji przy pisaniu kodu.

## Checklista

- Czy nowe zadanie ma unikalną nazwę i unikalną nazwę blokady?
- Czy ma jawny limit czasu przebiegu i jawny limit czekania na blokadę?
- Czy ma okno godzinowe albo jawny jego brak, a jeśli ma, to czy jest ono dłuższe od limitu czasu przebiegu i rozłączne z oknami pozostałych zadań nocnych tego samego procesu?
- Czy limit czekania na blokadę jest zerowy, a jeśli nie, czy jest do tego zapisany powód?
- Czy blokada żyje w bazie, a nie w pamięci procesu?
- Czy odpuszczenie przebiegu z powodu zajętej blokady jest logowane jako informacja, nie jako błąd?
- Czy wynik przebiegu rozróżnia przebieg wykonany od odpuszczonego, a o powodzeniu pracy mówi jej własny wynik?
- Czy zadanie raportuje liczbę elementów przetworzonych i pominiętych?
- Czy reguły wołane z zadania nie wymagają istnienia wołającego ani jego uprawnień?
- Czy test spójności zadań został uzupełniony o nowe zadanie?
- Czy zmiana częstotliwości, okna albo blokady istniejącego zadania przeszła przez rozstrzygnięcie w fazie shape?
- Czy zadanie nie usuwa danych, których usunięcia specyfikacja produktu jawnie nie dopuszcza?
