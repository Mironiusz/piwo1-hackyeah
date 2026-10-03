# Standard agentowego workflow

Stan dokumentu: 2026-10-03

Cel: ten dokument opisuje cały system agentowy repozytorium - łańcuch prowadzący zadanie od surowego zgłoszenia do zaimplementowanej zmiany, system pamięci trwałej oraz mechanizm, który utrzymuje spójność między dwoma narzędziami agentowymi używanymi w tym repo (Claude Code i Codex). Dokument jest pisany pod człowieka: kogoś, kto dołącza do zespołu i chce zrozumieć, jak tu się pracuje z agentami. Ma też służyć przyszłej instancji agenta jako materiał źródłowy. Po przeczytaniu całości powinno dać się ręcznie odtworzyć każdy krok procesu, nawet bez wołania odpowiadającego mu narzędzia po nazwie.

---

## 1. Po co ten dokument

Wiedza o systemie agentowym rozkłada się na kilka miejsc: `CLAUDE.md`/`AGENTS.md` opisuje reguły ogólne i mapowanie "co otworzyć przed zadaniem", `agent_docs/ai_workflows/shape_prd_workflow.md` opisuje metodologię łańcucha w skrócie, a skille niosą zachowanie właściwe dla swojej fazy. Uzasadnienia decyzji, na przykład dlaczego seed jest niemodyfikowalny albo dlaczego przejścia między fazami są ręczne, nie mają miejsca w żadnym z nich.

Bez jednego miejsca na uzasadnienia trudno wdrożyć nową osobę do procesu, a rationale ginie razem z zadaniem, przy którym powstało. Ten dokument zbiera to wszystko w jednym miejscu, świadomie akceptując, że część treści pokrywa się z tym, co już jest w `CLAUDE.md`, `AGENTS.md` i `agent_docs/ai_workflows/shape_prd_workflow.md` - te pliki pozostają nietknięte i nadal obowiązują jako rdzeń reguł repozytorium. Ten dokument jest ich uzupełnieniem o pełny obraz i o "dlaczego", nie ich zamiennikiem.

### 1.1. Zakres i granice

W środku: mechanizm łańcucha seed -> shape -> PRD -> plan -> implementacja -> review i jego punkty kontrolne (rozdz. 3-4), dziesięć kategorii ryzyka blokującego (rozdz. 3.3), regulator szczegółowości wywiadu (rozdz. 3.5), skille i subagenci obsługujący łańcuch, archiwizacja zakończonej inicjatywy do `plans_finished/` i jej wznowienie (rozdz. 4.6), praca równoległa na jednym drzewie roboczym (rozdz. 4.7), system `agent_docs`/memory jako mechanizm, nie jako format (rozdz. 5), dualizm narzędzi agentowych Claude Code/Codex, hooki, subagenci i test parytetu (rozdz. 6).

Ten dokument świadomie pokrywa się częściowo z `CLAUDE.md`/`AGENTS.md` (reguły ogólne i mapowanie "co otworzyć przed zadaniem") oraz z `agent_docs/ai_workflows/shape_prd_workflow.md` (metodologia łańcucha w skrócie) - te pliki pozostają rdzeniem obowiązujących reguł, ten dokument jest ich uzupełnieniem o pełny obraz i uzasadnienia, nie zamiennikiem.

Czego tu nie ma: format i szablon każdego z pięciu artefaktów łańcucha (SEED, SHAPE, PRD, PLAN, REVIEW) oraz format wpisu `agent_docs/memory` - to jest wyłącznie `standard_agent_docs.md` (rozdz. 5.2 tego dokumentu odsyła tam wprost).

### 1.2. Reguła odstępstwa

Reguła odstępstwa wspólna dla wszystkich standardów (`docs/standards/README.md`) obowiązuje w wersji zaostrzonej: standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita, bo projekt założony z szablonu nie ma stanu zastanego, który wymagałby okresu przejściowego. Rozluźnienie tej reguły ma być kiedyś jawną decyzją zapisaną w mapie standardów, nie stanem wchodzącym w życie samym.

Zawężenie właściwe dla tego standardu: jednostką odstępstwa jest plik mechanizmu łańcucha - definicja skilla (`SKILL.md`), hook, subagent, plik konfiguracji (`settings.json`, `hooks.json`) albo test architektury (`tests/architecture/test_agent_docs_parity.py`) - nie moduł kodu produkcyjnego ani artefakt zadania w `plans/`. Modyfikacja jednego z tych plików jest momentem powstania obowiązku dostosowania go do tego standardu.

## 2. Słownik pojęć

- Inicjatywa - katalog `plans/<INICJATYWA>/`, grupujący jedno albo więcej powiązanych zadań agentowych. Nazwa inicjatywy jest trwała i widoczna w repo, więc ustala się ją raz, na początku, i nie zmienia potem bez dobrego powodu. Gdy inicjatywa niesie więcej niż jedno zadanie, jej pięć artefaktów na zadanie może stać płasko albo w podkatalogu `<ZADANIE>/` - patrz sekcja 3.2. Inicjatywa jawnie zakończona albo anulowana przechodzi w całości, pod tą samą nazwą, do archiwum `plans_finished/<INICJATYWA>/` (rozdz. 4.6).
- Zadanie i prefiks zadania - pojedyncza jednostka pracy w ramach inicjatywy. Wszystkie pliki jednego zadania dzielą wspólny prefiks `<ZADANIE>_`, na przykład `docs_SEED.md` i `docs_SHAPE.md` należą do zadania `docs` w inicjatywie `agentic_workflow_docs`.
- SEED - dosłowny zapis zgłoszenia, z jawnym źródłem pochodzenia. Niemodyfikowalny po zapisaniu.
- SHAPE - luźny plan, powstający z wywiadu doprecyzowującego prowadzonego po zapisaniu seeda.
- PRD - dokument odpowiadający na "co i dlaczego", bez żadnych decyzji technicznych.
- PLAN - dokument odpowiadający na "jak", oparty na faktach zweryfikowanych w kodzie, bazie i dokumentacji.
- REVIEW - log przebiegu implementacji: co zostało pominięte, na co agent trafił, jakie decyzje padły przy pisaniu kodu i co wymaga powrotu w przyszłości. To nie jest trwała pamięć - to stan konkretnego zadania.
- Kategoria ryzyka blokującego - jedna z dziesięciu z góry ustalonych dziedzin (na przykład schemat bazy albo kontrakt zewnętrznego API), w których pytanie zadane w fazie shape musi zostać jednoznacznie rozstrzygnięte, zanim zadanie może przejść do PRD.
- Regulator szczegółowości - parametr zadania, liczba od 0 do 100 podawana w seedzie i obowiązująca z nagłówka shape'a, ustalająca, ile decyzji agent podejmuje sam, a o ile pyta. Nie sięga pytań blokujących na żadnej pozycji skali.
- Parytet - stan, w którym odpowiadające sobie pliki po stronie Claude Code (`.claude/`) i Codeksa (`.agents/`) mają identyczną treść regułową, różniącą się wyłącznie w jawnie dozwolonych miejscach.
- Hook - skrypt Claude Code uruchamiany automatycznie przy określonym zdarzeniu, na przykład przy starcie sesji albo przy próbie wywołania narzędzia.
- Subagent - osobna definicja agenta, z własnym zestawem narzędzi i ograniczeń, wywoływana z głównej sesji do wąsko zdefiniowanego zadania.
- Dogfooding - przepuszczenie realnego zadania przez cały łańcuch, żeby sprawdzić, czy system faktycznie działa w praktyce, a nie tylko wygląda spójnie na papierze.

## 3. Łańcuch decyzyjny - co to jest i jak działa

### 3.1. Sekwencja faz i punkty kontrolne

Zadanie przechodzi przez sekwencję: seed -> shape -> PRD -> plan -> implementacja -> review -> (opcjonalnie) trwała pamięć -> archiwizacja inicjatywy, gdy jest jawnie zakończona (rozdz. 4.6). Trzy skille obsługują tę sekwencję: `plan-shape` (seed -> shape), `plan-prd` (shape -> PRD -> plan) i `plan-implement` (plan -> implementacja -> review -> archiwizacja).

Każde przejście między skillami jest ręczne, z jednym wyjątkiem. Skill kończy pracę, mówi wprost co powstało i co można zawołać dalej, ale nie uruchamia następnego skilla sam. Powód: każda granica faz jest punktem kontrolnym, w którym użytkownik ma zobaczyć wynik i móc zawrócić - automatyczne przechodzenie zamieniłoby łańcuch w jeden nieprzerwany przebieg bez miejsc na korektę, co jest odwrotnością tego, po co ten łańcuch w ogóle powstał. Jedyny wyjątek to koniec pracy `plan-implement`, które samo wywołuje review (`implementation-dod-review`) zaraz po zakończeniu implementacji - opisane szczegółowo w sekcji 4.4.

### 3.2. Pięć artefaktów zadania

Każde zadanie zostawia po sobie do pięciu plików, każdy z jednym dozwolonym rodzajem treści: `<ZADANIE>_SEED.md`, `<ZADANIE>_SHAPE.md`, `<ZADANIE>_PRD.md`, `<ZADANIE>_PLAN.md`, `<ZADANIE>_REVIEW.md`. Dokładny szablon sekcji każdego z nich jest opisany w sekcji 4, przy skillu, który go produkuje.

Domyślne miejsce to płasko w `plans/<INICJATYWA>/` - poprawne dopóki inicjatywa niesie jedno zadanie. Gdy inicjatywa grupuje więcej niż jedno zadanie, dopuszczalny jest podkatalog per zadanie: `plans/<INICJATYWA>/<ZADANIE>/<ZADANIE>_SEED.md` i tak dalej dla pozostałych czterech. Piątka artefaktów jednego zadania zostaje razem w obu wariantach - podział, jeśli w ogóle, idzie po zadaniu, nigdy po rodzaju artefaktu (nie ma osobnego katalogu zbierającego same SHAPE albo same PRD z różnych zadań). Wybór wariantu zapada raz, przy pierwszym zapisie seeda dla danej inicjatywy, i nie zmienia się później bez dobrego powodu - tak jak nazwa inicjatywy.

Stan procesu żyje wyłącznie w tych plikach, nigdy w historii rozmowy - dzięki temu przerwanie sesji nic nie kosztuje, a każdy skill wołany ponownie na tym samym zadaniu wczytuje istniejące artefakty i kontynuuje od pierwszej niewypełnionej rzeczy, zamiast zaczynać od zera (więcej w sekcji 4.5).

### 3.3. Dziesięć kategorii ryzyka blokującego

Pytanie zadane w fazie shape, które dotyka jednej z poniższych kategorii, musi zostać oznaczone `Block: yes` wraz z nazwą kategorii i wstrzymuje przejście do PRD, dopóki nie zostanie jednoznacznie rozstrzygnięte - zawsze przez zapytanie użytkownika, nigdy przez domysł. Lista jest dobrana dla serwisu z bazą danych i interfejsem programistycznym. Projekt o innym profilu ryzyka zmienia ją jednocześnie tutaj, w `agent_docs/ai_workflows/shape_prd_workflow.md` i w skillu `plan-shape`.

1. Kontrakt tokenu dostępowego i zakresów uprawnień - blokada obowiązuje, gdy zadanie zakłada cokolwiek o zawartości tokenu, sposobie rozwiązywania go na aktora albo o zakresach uprawnień. Kontrakt jest ustalany z wystawcą tokenu i z konsumentami interfejsu, nie odgadywany z kodu. Prawie wszystko w serwisie zależy od tej warstwy, więc błędne założenie tutaj unieważnia pracę zrobioną wyżej.
2. Stabilność kontraktu interfejsu programistycznego - blokada obowiązuje, gdy zmiana dotyka kształtu żądania albo odpowiedzi, ścieżki, kodu błędu albo semantyki istniejącego pola. Po drugiej stronie jest konsument spoza tego repozytorium, którego pracy nie widzimy.
3. Schemat bazy - blokada obowiązuje, gdy zadanie zakłada istnienie tabeli, kolumny, widoku albo typu danych bez sprawdzenia. Weryfikacja: zrzut schematu dla stanu faktycznego serwera, specyfikacja produktu dla stanu docelowego. Te dwa źródła mogą się różnić i ta różnica sama jest informacją.
4. Forma zmiany schematu - blokada obowiązuje przy każdej zmianie schematu. Weryfikacja: czy zmiana idzie formą opisaną w `standard_database.md`. Kategoria zostaje blokująca po rozstrzygnięciu formy, bo pilnuje nie tylko tego, że forma jest nieznana, ale też tego, że schemat jest jedyną rzeczą w serwisie, której nie da się wydać ponownie.
5. Źródło prawdy dla danych - blokada obowiązuje, gdy ta sama informacja występuje w więcej niż jednym miejscu i zadanie nie mówi jednoznacznie, które z nich jest autorytatywne. Zawsze pytanie do użytkownika - tego nie da się rozstrzygnąć czytaniem kodu.
6. Semantyka czasu i przesunięcia strefowego - blokada obowiązuje, gdy zadanie zapisuje albo czyta wartość czasu w sposób, który mógłby zmienić jej przesunięcie. Gdy projekt zachowuje przesunięcie obowiązujące w momencie zdarzenia (`standard_time.md`), warstwa sterownika jest tu obciążona ryzykiem, którego nie wykryje test porównujący same momenty.
7. Idempotencja i deduplikacja - blokada obowiązuje, gdy zmiana może spowodować podwójny zapis, zgubienie rekordu przy ponowieniu albo dotyka klucza uzgadniania: identyfikatora zewnętrznego rekordu albo kluczy idempotencji (`standard_idempotency.md`).
8. Widoczność odczytu i uprawnienia - blokada obowiązuje, gdy zmiana dotyka tego, kto co może przeczytać albo zrobić. Pomyłka w stronę permisywną otwiera cudze dane, w stronę restrykcyjną wygląda jak zepsuty serwis; jedno i drugie łatwo wprowadzić w jednym miejscu i nie w drugim.
9. Dane osobowe - blokada obowiązuje, gdy zadanie dotyka imion i nazwisk, danych kontaktowych albo informacji o działaniach konkretnej osoby. Informacja o tym, kto czego nie zrobił albo czyja praca została odrzucona, jest danymi o ocenie osoby, nawet jeśli nigdzie nie nazywa się oceną. Dotyczy też logów i raportów, nie tylko zapisu do bazy.
10. Wolumen i koszt zapytania - blokada obowiązuje, gdy nie da się oszacować liczby wierszy przechodzących przez zmianę albo gdy zmiana leży na ścieżce odczytu wykonywanego przy każdym wyświetleniu listy. Predykat widoczności źle dobrany do indeksów zamienia wyszukanie w skan, a koszt rośnie razem z liczbą wierszy i uprawnień.

### 3.4. Czarna lista treści zakazanych w PRD

PRD odpowiada wyłącznie na "co i dlaczego", nigdy na "jak". Zakazane w PRD: modele danych, listy kolumn, migracje, ścieżki plików kodu, nazwy funkcji, decyzje o bibliotekach, szczegóły deploymentu, sekrety i credentiale. Jeśli podczas pisania PRD pojawia się chęć zapisania rozwiązania technicznego, ten materiał należy do planu implementacji, nie do PRD.

### 3.5. Regulator szczegółowości wywiadu

Ten sam łańcuch prowadzi drobną poprawkę w dokumencie i zmianę dotykającą kontraktu z zespołem zewnętrznym, a wywiad w obu wypadkach ma tę samą głębokość. Regulator jest pokrętką, którą zgłaszający mówi, ile decyzji chce podjąć osobiście: liczbą od 0 do 100, gdzie niska wartość znaczy więcej decyzji podjętych przez agenta, a wysoka więcej pytań postawionych człowiekowi. Ten rozdział jest źródłem prawdy dla całego mechanizmu - definicje skilli (rozdz. 4.1-4.3) niosą zachowanie właściwe dla swojej fazy i odsyłają tutaj po resztę.

Parametr i jego rozpoznawanie. Wartość podaje się w treści zgłoszenia. Agent rozpoznaje ją niezależnie od użytej etykiety, pod jednym warunkiem: bezpośrednio po etykiecie stoi liczba z zakresu 0-100. Warunek nie jest formalnością - wzorzec złożony z pojedynczej litery i dwukropka otwiera każdą ścieżkę dyskową Windowsa, a takie ścieżki w zgłoszeniach tego repozytorium występują. Formą wzorcową, podawaną w dokumentacji i zapisywaną przez samego agenta, jest `C:N`. Zgłoszenie niosące dwa różne wystąpienia parametru zatrzymuje agenta na jednym pytaniu o to, którą wartość przyjąć, zadanym przed pierwszym pytaniem wywiadu: dopóki konflikt trwa, nie wiadomo nawet, jak dociekliwy ma być dalszy ciąg, a milczący wybór między dwiema równorzędnymi wartościami byłby dokładnie tą cichą decyzją, której cały mechanizm ma zapobiegać.

Miejsce podania i miejsce obowiązywania. Wartość podaje się w seedzie, a obowiązuje z nagłówka `<ZADANIE>_SHAPE.md`, gdzie `plan-shape` przepisuje ją jako osobną linię pod stanem dokumentu. Wszystkie trzy skille czytają ją wyłącznie stamtąd. Rozdzielenie tych dwóch miejsc jest zamierzone i nie jest błędem: seed jest dosłownym i niemodyfikowalnym zapisem zgłoszenia, więc parametr procesu musi mieć drugie miejsce, żeby dało się go zmienić bez łamania tej nietykalności. Różnica między wartością w seedzie a wartością w nagłówku nie jest przez to konfliktem i nie wywołuje pytania - obowiązuje nagłówek, bo jest z definicji nowszy.

Wartość domyślna. Brak parametru w zgłoszeniu znaczy 40, czyli próg, na którym agent pyta o każdy wybór o odmiennych konsekwencjach dla zakresu albo dla zadań przyszłych.

Pięć progów. Liczbę podaje się jako dowolną wartość z zakresu, ale obowiązuje ona jako jeden z pięciu progów o wprost opisanym zachowaniu. Powód jest sprawdzalnościowy: model nie ma sposobu, żeby odróżnić zachowanie przy 61 od zachowania przy 64, więc skala ciągła dawałaby wrażenie, a nie regułę, wobec której da się stwierdzić naruszenie. Każdy próg zawiera wszystko, co niższy, i dokłada swoje:

- 0-19: wyłącznie pytania blokujące. Wszystko pozostałe agent rozstrzyga sam. Zadanie nietykające żadnej kategorii ryzyka może przejść fazę bez ani jednego pytania.
- 20-39: dodatkowo wybory, których odwrócenie wymagałoby przepisania pracy już wykonanej.
- 40-59: dodatkowo każdy wybór między wariantami o odmiennych konsekwencjach dla zakresu zadania albo dla zadań przyszłych. Agent rozstrzyga sam to, co jest konsekwencją decyzji już podjętych. To jest poziom domyślny.
- 60-79: dodatkowo rzeczy, które na progach niższych agent wyprowadziłby jako konsekwencję, oraz granice zakresu, których zgłoszenie nie nazywa wprost.
- 80-100: pytanie o każdą decyzję mającą więcej niż jeden rozsądny wariant. Agent rozstrzyga sam wyłącznie to, co ma wariant jeden albo stoi wprost w repozytorium.

Opis progu mówi, co na nim zostaje, nie tylko co znika. Zachowanie właściwe dla fazy - co progi znaczą przy pytaniach o problem i zakres, co przy decyzjach technicznych planu, a co przy brakach wykrytych w trakcie implementacji - jest w definicjach trzech skilli, bo różni się między nimi na tyle, że wspólne brzmienie przestałoby być sprawdzalne.

Dno regulatora. Dziesięć kategorii ryzyka blokującego z rozdz. 3.3 oraz zakaz zgadywania kontraktu stoją poza zasięgiem regulatora na całej skali. Powód jest hierarchiczny, nie kosmetyczny: `CLAUDE.md` stawia "brak zgadywania kontraktu - lepiej zapytać niż dorobić fallback" na drugim miejscu w hierarchii rozstrzygania konfliktów, wyżej niż zgodność ze standardami i czytelność, więc parametr zadania nie może stać ponad tą regułą. Ustawienie 0 daje wywiad złożony wyłącznie z pytań blokujących, nie wywiad pusty, a brak należnego pytania blokującego jest naruszeniem, nie oszczędnością.

Trafność jako druga oś. Przed zadaniem pytania agent sprawdza, czy odpowiedzi nie ma w repozytorium. Obowiązek działa na każdej pozycji skali, także przy 100, i we wszystkich trzech fazach. Regulator i trafność są dwiema osiami, nie jedną: to sprawdzenie odejmuje pytania zbędne, a regulator steruje wyłącznie tym, co po tym odjęciu zostaje. Zlepienie obu w jedno spowodowałoby, że obniżanie wartości ucina pytania trafne równie chętnie co zbędne. Znalezioną odpowiedź agent zapisuje w artefakcie wraz ze wskazaniem źródła, zamiast pytać o nią człowieka.

Cztery sygnały. Znalezienie odpowiedzi nie zamyka tematu, gdy zachodzi jeden z poniższych. Wtedy pytanie pada mimo znalezienia i mówi wprost, który sygnał je wywołał:

1. Dwa źródła mówią co innego o tej samej rzeczy, w tym różnica między stanem faktycznym a docelowym - przy bazie różnica między zrzutem schematu a specyfikacją produktu jest informacją samą w sobie (rozdz. 3.3, kategoria 3).
2. Temat jest objęty otwartym wpisem w `docs/standards/decision_registry.md` albo opisany w standardzie o statusie częściowym - reguły tam świadomie nie ma.
3. Odpowiedź stoi wyłącznie w artefakcie zamkniętego zadania w `plans/`, bez potwierdzenia w kodzie, standardzie albo specyfikacji produktu. Dziennik zadania opisuje stan z momentu pisania, nie stan obowiązujący.
4. Dokument nie był aktualizowany po jawnie wskazanym zdarzeniu, które mogło go unieważnić. Ten sygnał wymaga konkretnego zdarzenia odniesienia i nie działa jako ogólny termin ważności dokumentu - bez tego zawężenia każdy starszy plik generowałby pytanie, co zamieniłoby regułę trafności w jej przeciwieństwo.

Oznaczanie decyzji podjętych bez pytania. Pozycja artefaktu rozstrzygnięta przez agenta zamiast zapytania niesie w prozie frazę "Decyzja agenta przy C:N, bez pytania", w miejscu tej pozycji, nie w zbiorczej sekcji na końcu dokumentu. Oznaczenie w miejscu nie rozjeżdża się z treścią, a czytający jedną regułę od razu widzi, czy stał za nią człowiek.

Zmiana wartości w trakcie zadania. Wartość wolno zmienić w dowolnym momencie. Agent aktualizuje wtedy nagłówek shape'a i dopisuje jedną linię o tym, od którego momentu obowiązuje nowa wartość; pozycje powstałe wcześniej zostają nietknięte. Swoboda jest potrzebna, bo właściwa wartość często wychodzi dopiero po kilku pytaniach, a wymaganie trafienia jej przed rozmową przenosiłoby koszt pomyłki na całe zadanie. Zapis momentu zmiany jest warunkiem tej swobody - bez niego nie da się czytać dokumentu wstecz, bo nie wiadomo, które pozycje powstały przy której wartości.

Czego regulator nie zmienia. Reguła jednego pytania na raz obowiązuje bez zmian na całej skali: regulator steruje doborem i głębokością pytań, nigdy sposobem ich zadawania. Seria krótkich pytań daje możliwość zmiany kierunku po każdej odpowiedzi, na czym stoi zmienialność wartości opisana wyżej. Nie zmienia się też miejsce pytań technicznych - padają wyłącznie w fazie B `plan-prd` (rozdz. 4.2). Shape zostaje nietechniczny na każdej pozycji skali, a wysoka wartość podnosi tam głębokość pytań o problem, zakres i reguły, nie o rozwiązanie. Każde inne umiejscowienie tworzyłoby ścieżkę omijającą PRD, a PRD jest kontraktem, którego planowi nie wolno cicho obejść.

Granice mechanizmu. Żadna kontrola automatyczna nie sprawdzi, ile pytań padło ani czy padły zasadnie - takiego testu nie da się napisać i ten standard go nie obiecuje. Regulator jest przez to deklaracją zamiaru wiążącą agenta, a nie przełącznikiem o gwarantowanym zachowaniu, a granica między progami nigdy nie będzie ostra tak, jak granica liczbowa. Weryfikacja jest wyłącznie obserwacyjna, rozłożona na kolejne zadania, i dlatego oznaczanie decyzji podjętych bez pytania nie jest ozdobnikiem: jest jedynym materiałem, na którym da się tę obserwację oprzeć.

## 4. Każdy krok łańcucha szczegółowo

### 4.1. `plan-shape`

Wejście do całego łańcucha. Ma trzy obowiązki, których nie mają pozostałe skille:

1. Ustala nazwę inicjatywy i prefiks zadania. Jeśli użytkownik ich nie podał, proponuje oba na podstawie treści zgłoszenia i czeka na potwierdzenie, zanim utworzy cokolwiek na dysku - nazwa jest trwała i widoczna w repo.
2. Sprawdza, czy `<ZADANIE>_SEED.md` już istnieje. Użytkownik mógł stworzyć ten plik sam, wklejając gotową notatkę zamiast dyktować seed w rozmowie - w takim wypadku `plan-shape` nigdy go nie nadpisuje, tylko wczytuje. Jeśli plik nie istnieje, `plan-shape` zapisuje go dosłownie jako pierwszą czynność, przed zadaniem jakiegokolwiek pytania, z jawnym źródłem pochodzenia (rozmowa z użytkownikiem, wklejony mail, notatka ze spotkania, opis z brancha, zgłoszenie od kogoś z zespołu).
3. Tworzy `<ZADANIE>_SHAPE.md` ze szkieletem sekcji (Problem, Odbiorca i wyzwalacz, Stan obecny, Najmniejszy sensowny zakres, Poza zakresem, Wymagania funkcjonalne, Scenariusze, Podważenie własnych założeń, Reguły domenowe albo jawne TODO, Uwagi o danych/wydajności/bezpieczeństwie, Otwarte pytania), wypełniając na starcie tylko to, co wynika bezpośrednio z seeda.

Dalej prowadzi wywiad: jedno pytanie na raz, zamknięte przez `AskUserQuestion`, otwarte zwykłym tekstem. Wartość regulatora (rozdz. 3.5) odczytuje z treści seeda i wpisuje do nagłówka `<ZADANIE>_SHAPE.md`, skąd czytają ją pozostałe fazy, a progi rządzą doborem i głębokością pytań, nigdy sposobem ich zadawania. Po każdej odpowiedzi dopisuje minimalną notatkę do właściwej sekcji, usuwa odpowiadający wpis z "Otwarte pytania" i zapisuje plik - wywiad można przerwać w dowolnym momencie, bo stan żyje w pliku, nie w rozmowie. Każde pytanie dotykające jednej z dziesięciu kategorii ryzyka (sekcja 3.3) oznacza `Block: yes` wraz z nazwą kategorii. Sekcja "Podważenie własnych założeń" - zapis pytań, które agent zadał sam sobie o własne rozumienie problemu, wraz z tym, co z nich wyszło - jest obowiązkowa i nie może zostać pusta: jeśli nic nie budzi wątpliwości, to znak, że problem nie został jeszcze zrozumiany.

Skill kończy pracę, gdy wszystkie sekcje są wypełnione i żadna pozycja w "Otwarte pytania" nie ma `Block: yes`. Wtedy zmienia stan dokumentu na "wywiad zamknięty" i informuje, że można wywołać `plan-prd` - nie robi tego sam.

### 4.2. `plan-prd`

Produkuje dwa pliki w dwóch wyraźnie rozdzielonych fazach, bo PRD ma zakaz treści technicznych, a plan implementacji jej wymaga - mieszanie obu w jednym przebiegu prowadziłoby do przedwczesnego zamrożenia decyzji technicznych.

Faza A - PRD: wczytuje `<ZADANIE>_SHAPE.md` i `<ZADANIE>_SEED.md`; przerywa, jeśli shape ma nierozstrzygnięte pytania `Block: yes` (nie próbuje ich rozstrzygać domysłem, tylko zadaje je użytkownikowi i wraca po odpowiedzi); pisze `<ZADANIE>_PRD.md` wg szablonu (Cel biznesowy, Problem i jego skutki, Zakres, Poza zakresem, Wymagania funkcjonalne, Kryteria akceptacji, Reguły domenowe, Zależności i wpływ na inne moduły, Ryzyka i uwagi), pilnując czarnej listy z sekcji 3.4; pokazuje PRD użytkownikowi i czeka na potwierdzenie przed przejściem do fazy B - to jedyna bramka między "co" i "jak" w tym skillu, więc nigdy nie przechodzi przez nią milcząco.

Faza B - plan implementacji: otwiera dokumenty wskazane przez mapowanie typ zadania -> dokument z `CLAUDE.md`/`AGENTS.md`; weryfikuje w kodzie, bazie i dokumentacji wszystko, co PRD zakłada, i zapisuje ustalenia w sekcji "Fakty" w formacie ze `standard_agent_docs.md`; wylicza promień rażenia zmiany, czyli miejsca wywołań, obiekty schematu, klucze konfiguracji i kontrole automatyczne dotknięte pośrednio, a gdy ta lista wychodzi poza zakres uzgodniony w PRD, zatrzymuje się i pyta o podział planu zamiast rozszerzać zakres po cichu; pisze `<ZADANIE>_PLAN.md` wg szablonu (Cel, Fakty, Decyzje, Zakres zmian, Kolejność wdrożenia, Definition of Done, Ryzyka, Otwarte pytania, Pliki uzupełniające), gdzie każdy krok w "Zakres zmian" ma konkretne nazwy plików, funkcji i kontraktów danych, nigdy opis w stylu "coś w rodzaju"; jeśli weryfikacja obali założenie z PRD, zatrzymuje się i wraca do fazy A, bo PRD jest kontraktem i nie wolno go cicho obejść w planie. Kończy, gdy plan spełnia kryteria kompletności, których `plan-implement` i tak będzie wymagał: zero TODO, zero pozycji w "Otwarte pytania", każdy krok z jednoznacznym wejściem i wyjściem. Wartość regulatora (rozdz. 3.5) odczytuje z nagłówka `<ZADANIE>_SHAPE.md`, nigdy z seeda, i to ona ustala tutaj, ile decyzji technicznych skill podejmuje sam, a ile stawia użytkownikowi.

### 4.3. `plan-implement`

Zaimplementowanie dokładnie tego, co jest w podanym planie i w plikach uzupełniających, bez zgadywania tego, czego plan nie precyzuje. Przebieg ma dziewięć kroków:

1. Wczytanie planu i wszystkich plików uzupełniających, na które wskazuje.
2. Przegląd kompletności planu przed napisaniem jakiegokolwiek kodu: czy każdy krok ma jednoznaczne wejście i wyjście oraz konkretne nazwy, a nie "coś w stylu"; czy zostały TODO, `[NIEJASNE]` albo pozycje w "Otwarte pytania"; czy plan zakłada coś, co da się i trzeba zweryfikować w kodzie albo bazie zamiast przyjmować na wiarę; czy fakty planu są nadal prawdziwe po zmianach, które zaszły od daty ich sprawdzenia - kontrola formatu sprawdza wyłącznie formę dowodu, a plan przestaje być prawdziwy przy pierwszym mergu w pliki, które cytuje.
3. Jeśli znajdzie braki, przerywa przed napisaniem kodu i dopytuje - jedno pytanie na raz, zamknięte przez `AskUserQuestion`, otwarte tekstem - po odpowiedzi dopisuje minimalny fragment do planu, usuwa wpis z "Otwarte pytania" i wraca do kroku 2. Sprawdza też, czy powiązany SHAPE nie ma nierozstrzygniętych `Block: yes` - jeśli ma, wraca do `plan-prd` zamiast próbować rozstrzygać to samodzielnie. To, ile braków rozstrzyga sam, a o ile pyta, ustala regulator odczytany z nagłówka shape'a (rozdz. 3.5). Jest to miejsce, w którym cicha decyzja agenta kosztuje najwięcej, bo trafia prosto do kodu.
4. Gdy plan jest kompletny, implementuje go krok po kroku, zgodnie z konwencjami repo (`CLAUDE.md`, `docs/standards`).
5. Jeśli w trakcie implementacji trafi na coś, czego plan nie przewidział, zatrzymuje się w tym miejscu i pyta użytkownika. Zapisuje co się stało w `<ZADANIE>_REVIEW.md` (nie w samym planie - `_PLAN.md` jest kontraktem i nie rozrasta się w trakcie pracy, `_REVIEW.md` jest właśnie na to, co pominięto, na co trafiono i jakie decyzje padły przy kodzie), po czym kontynuuje od miejsca przerwania.
6. Na koniec podsumowuje, co zostało zrobione względem planu i czy coś zostało pominięte albo zmienione, wraz z powodem.
7. Ocenia, czy z zadania wynika coś wartego trwałego zapisania w `agent_docs/memory/<grupa>/<moduł>.md` - pełne kryteria w sekcji 5.2. Jeśli nic się nie kwalifikuje, nic nie dopisuje - to świadoma ocena, nie obowiązek za wszelką cenę.
8. Wywołuje `implementation-dod-review` na wprowadzonych zmianach. To jedyne w całym łańcuchu przejście, które dzieje się automatycznie - `plan-implement` samo uruchamia review po zakończeniu swojej pracy, zamiast czekać, aż użytkownik zawoła go ręcznie.
9. Po powrocie z review domyka zapis w `<ZADANIE>_REVIEW.md` i sprawdza, czy cała inicjatywa jest jawnie zakończona w rozumieniu rozdz. 4.6: werdykt `ready` obejmujący cały jej zakres albo inne jawne zamknięcie. Rozliczenie jednego zadania nie zamyka katalogu wielozadaniowego. Jeśli inicjatywa jest zakończona, przenosi cały katalog do `plans_finished/` i podaje nową ścieżkę w końcowym komunikacie. Review planu albo części kodu nie uruchamia przeniesienia; niejednoznaczny status zostawia katalog na miejscu i kończy się pytaniem do użytkownika.

### 4.4. Review końcowy: `implementation-dod-review` i `dod-reviewer`

Kryteria review, kolejność raportu i Definition of Done repozytorium są opisane w `docs/standards/standard_review.md` - to jest źródło prawdy dla tego tematu, nie ten rozdział.

Ten sam proces jest dostępny w dwóch formach: jako skill `implementation-dod-review`, wołany wprost albo automatycznie przez `plan-implement` (krok 8 rozdz. 4.3), oraz jako subagent `dod-reviewer` (`.claude/agents/dod-reviewer.md`), który ma dostęp do `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, nie implementuje poprawek, i ma ten sam skill (`implementation-dod-review`) przypisany wprost w swojej definicji. `dod-reviewer` pracuje w trybie `permissionMode: plan` (nie może wprowadzać zmian) z limitem 16 tur.

Review pozostaje w trybie odczytu także wobec archiwum: raportuje, jaki zakres obejmuje werdykt i czy inicjatywa kwalifikuje się do `plans_finished/` według rozdz. 4.6, ale samego przeniesienia nie wykonuje - to należy do `plan-implement` (krok 9 rozdz. 4.3) albo do agenta, któremu użytkownik polecił porządki wprost.

### 4.5. Wznawianie po przerwie

Każdy z trzech skilli działa tak samo pod tym względem: stan procesu żyje wyłącznie w plikach `plans/<INICJATYWA>/`, nigdy w historii rozmowy. Skill wołany ponownie na zadaniu, którego artefakty już istnieją, wczytuje je i kontynuuje od pierwszej niewypełnionej rzeczy, zamiast zaczynać od zera. Dzięki temu przerwanie sesji - z dowolnego powodu, w dowolnym momencie - nic nie kosztuje: wystarczy wywołać ten sam skill na tym samym pliku ponownie.

Wznowienie z notatki przekazania zostawionej przez przerwaną sesję zaczyna się od odczytu stanu, nie od naprawy: `git status`, zawartość obu lokalizacji inicjatywy i porównanie plików z `git show HEAD:<plik>`. Przerwana sesja albo zatrzymywany agent mogą dokończyć pracę już po zapisaniu notatki, więc stan opisany w niej jako pilny bywa nieaktualny, a naprawa takiego stanu na drzewie, które jest już spójne, niszczy jedyną kopię. Rozjazd notatki ze stanem faktycznym zapisuje się w review.

Wznowienie po przerwie dotyczy inicjatywy, która nadal stoi w `plans/`. Inicjatywa jawnie zakończona i przeniesiona do archiwum wraca do pracy inną drogą - opisaną w rozdz. 4.6.

### 4.6. Archiwizacja i wznowienie inicjatywy

Ten rozdział jest jedynym pełnym opisem tego, kiedy inicjatywa opuszcza `plans/`, dokąd trafia i jak wraca. Pozostałe miejsca w repozytorium - rdzeń `CLAUDE.md`/`AGENTS.md`, `agent_docs/ai_workflows/shape_prd_workflow.md`, skille łańcucha, definicje reviewera i `plans_finished/README.md` - odsyłają tutaj zamiast powtarzać regułę.

Dwie lokalizacje. `plans/` jest miejscem bieżącej pracy. `plans_finished/` jest archiwum całych inicjatyw, które zostały jawnie zakończone albo jawnie anulowane. Katalog inicjatywy przechodzi między nimi w całości, pod tą samą nazwą i z tym samym układem plików - także wtedy, gdy niesie podkatalogi zadań z sekcji 3.2. Archiwizacja nie zmienia nazw ani prefiksów, nie scala katalogów i nie wybiera, które pliki zachować. Puste albo nieistniejące `plans_finished/` nie jest błędem: katalog powstaje przy pierwszym przeniesieniu, a `plans_finished/README.md` mówi tylko, czym to miejsce jest, i odsyła tutaj. Archiwum nie ma osobnego rejestru statusów, pliku statusu per inicjatywa ani nowego markera zamknięcia - o stanie inicjatywy mówią jej własne artefakty.

Jednostką archiwizacji jest cała inicjatywa, czyli katalog. Zamknięcie jednego etapu, jednego zadania albo części zakresu nie jest zamknięciem inicjatywy: katalog z kilkoma zadaniami zostaje w `plans/`, dopóki wszystkie jego zadania nie są rozliczone albo sama inicjatywa nie jest jawnie zamknięta. Powód: katalog trzyma historię jednej sprawy w całości, a przeniesienie części plików rozerwałoby wzajemne odwołania między artefaktami.

Dowód zakończenia musi być jawny, dotyczyć całej inicjatywy i odnosić się do aktualnego stanu prac. Wystarcza jedno z dwojga:

1. Końcowy werdykt `ready` w `<ZADANIE>_REVIEW.md`, obejmujący cały zakres inicjatywy. Nie wymaga osobnego wpisu o zamknięciu - to sam werdykt jest zamknięciem.
2. Gdy `ready` nie ma: inne jawne oznaczenie zakończenia albo anulowania całej inicjatywy, zapisane w jej artefaktach - na przykład linia stanu review mówiąca "inicjatywa zamknięta" albo "inicjatywa anulowana", z zapisanym powodem. Pełny łańcuch artefaktów nie jest warunkiem: inicjatywa rozliczona samym review, bez PRD i PLAN, kwalifikuje się tak samo.

Czego nie wolno uznać za dowód, choć bywa kuszące: samego wystąpienia słowa `ready` gdziekolwiek w dokumencie, werdyktu `ready after minor fixes` albo `not ready`, review obejmującego tylko plan albo część kodu, kompletu pięciu plików, zamkniętego wywiadu w SHAPE, markera "plan zamknięty" w PLAN (ten marker wciąga plan pod kontrolę formatu z `standard_agent_docs.md`, nie zamyka inicjatywy), wieku katalogu ani braku aktywności. Każda z tych rzeczy opisuje etap, nie koniec sprawy. Brak aktywności nie jest anulowaniem - anulowanie też musi zostać zapisane.

Sprzeczności nie rozstrzyga się domysłem. Gdy jeden wpis mówi o zamknięciu, a inny o niedokończonej albo wznowionej pracy, agent czyta kolejność i zakres wpisów. Późniejszy wpis zamykający, który jawnie rozlicza wcześniejszą listę braków, nie jest sprzecznością. Czynności pozostawione użytkownikowi jako działania po zamknięciu nie blokują archiwizacji, ale archiwizacja niczego o nich nie dowodzi: przeniesienie katalogu nie potwierdza wykonania tych czynności ani wdrożenia kodu. Nierozliczona sprzeczność, status niejednoznaczny albo rekomendacja zamknięcia czekająca na decyzję użytkownika zatrzymują przeniesienie - katalog zostaje w `plans/`, a agent pyta użytkownika o stan inicjatywy przed czymkolwiek innym.

Kto przenosi i kiedy. Przy jednoznacznym dowodzie agent przenosi inicjatywę sam, bez pytania. W łańcuchu robi to `plan-implement` po powrocie z review (krok 9 rozdz. 4.3): najpierw domyka bieżący zapis w review, potem sprawdza, czy werdykt obejmuje całą inicjatywę i czy nic nie podważa jej zakończenia, i dopiero wtedy przenosi katalog. Końcowy komunikat podaje nową ścieżkę. Poza łańcuchem to samo kryterium stosuje agent, któremu użytkownik polecił uporządkować `plans/` albo zamknąć konkretną inicjatywę. Review - skill `implementation-dod-review` i subagent `dod-reviewer` - pozostaje w trybie odczytu: raportuje, jaki zakres obejmuje werdykt i czy inicjatywa kwalifikuje się do archiwum, ale nie przenosi niczego. Jawne ograniczenie użytkownika do odczytu ma pierwszeństwo przed każdą regułą z tego rozdziału.

Jak przenieść. Przed przeniesieniem agent sprawdza: że cel `plans_finished/<INICJATYWA>/` nie istnieje (istniejący cel oznacza kolizję do wyjaśnienia z użytkownikiem, nigdy scalanie ani nadpisanie); że katalog źródłowy nie ma zmian w `git status` powstałych po kwalifikacji, bo zmiana po zamknięciu podważa zamknięcie; że rozwiązane ścieżki źródła i celu leżą w tym samym repozytorium i katalog nie zawiera dowiązań prowadzących poza repozytorium; że zna listę plików i ich sumy kontrolne, żeby po przeniesieniu potwierdzić komplet. Przenosi natywnym poleceniem przenoszenia katalogu, nie `git mv` - indeksem gita i commitem zajmuje się człowiek, zgodnie z regułami pracy z gitem w rdzeniu repozytorium. Błąd w trakcie zatrzymuje dalsze przenoszenie; agent nie kasuje ani źródła, ani pozostałości, i nie nadpisuje celu przy ponowieniu.

Ochrona historii. Przeniesienie nie zmienia treści seedów, dotychczasowych wpisów w review, wpisów `agent_docs/memory/` ani zamrożonych materiałów inicjatywy: datowanych raportów, odczytów, załączników i korespondencji. Stara ścieżka w takim zapisie jest zapisem historycznym i taka zostaje. Aktualizacji podlegają wyłącznie edytowalne odwołania: dokumentacja, docstringi, aktywne artefakty innych inicjatyw, mapy, indeksy i rejestry - w `_PLAN.md` innej inicjatywy zmienia się wyłącznie lokalizacja odsyłacza, nigdy kontrakt. Dwie granice tej reguły trzeba nazwać wprost, bo bez tego są szarą strefą: załącznik jest zamrożony co do danych, zapytań i logiki, ale instrukcja uruchomienia w docstringu skryptu załącznika jest odsyłaczem i dostaje nową ścieżkę - to jedyna dopuszczalna zmiana w takim pliku, potwierdzana porównaniem tokenów poza docstringiem; `_SHAPE.md` i `_PLAN.md` samej archiwizowanej inicjatywy traktuje się jak plan innej inicjatywy, czyli zmienia się w nich wyłącznie lokalizację odsyłaczy między artefaktami, nigdy treść ustaleń, chyba że dokument sam deklaruje regułę dopisywania zamiast przepisywania - wtedy zostaje zapisem historycznym w całości. Odwołania w kodzie i narzędziach, które faktycznie czytają pliki inicjatywy, muszą po przeniesieniu nadal działać; skan samych nazw ścieżek trzeba przy tym rozdzielić na edytowalny odsyłacz, zapis historyczny i rzeczywistego konsumenta ścieżki. Ta sama reguła obowiązuje w obu kierunkach przeniesienia.

Wznowienie. Inicjatywa wraca z `plans_finished/` do `plans/` wyłącznie na polecenie kontynuowania tej samej pracy. Sam odczyt archiwum, pytanie o historyczny wynik albo review dawnej zmiany nie wznawia niczego. Powrót jest przeniesieniem całego katalogu pod tą samą nazwą, z tymi samymi sprawdzeniami co przy archiwizacji, po którym agent dopisuje do review wpis o wznowieniu: datę, powód i zakres. Dotychczasowa historia zamknięcia zostaje nietknięta - wznowienie jest kolejnym wpisem, nie poprawką poprzedniego. Gdy inicjatywa nie ma review, agent tworzy go według `standard_agent_docs.md` z tym wpisem jako pierwszym. Nowy zakres, który tylko dotyka tematu zamkniętej inicjatywy, dostaje osobną inicjatywę zamiast wznowienia. Przed założeniem nowego katalogu w `plans/` agent sprawdza obie lokalizacje; ta sama nazwa obecna w obu naraz jest stanem do wyjaśnienia z użytkownikiem, nie do arbitralnego wyboru.

Kontrole automatyczne nie słabną przez archiwizację: kontrola formatu planów z `standard_agent_docs.md` obejmuje `plans_finished/` na równi z `plans/`, kontrola stylu prozy skanuje je rekurencyjnie bez wyjątku dla archiwum, a formatowanie markdown pomija je świadomie (`.prettierignore`), żeby kontrola formatu nie wymuszała przepisania zamrożonych materiałów. Poza formatowaniem przeniesione dokumenty podlegają tym samym regułom, którym podlegały w `plans/`. Archiwizacja nie jest okazją do hurtowego formatowania chronionych materiałów.

### 4.7. Praca równoległa na jednym drzewie roboczym

Na jednym drzewie roboczym może równolegle pracować druga sesja agenta albo człowiek. Przebieg testów mierzy całe drzewo, nie jedną zmianę, więc czerwień z cudzej pracy w toku wygląda dokładnie jak własny regres, a naprawianie tego, co ktoś właśnie pisze, jest wchodzeniem mu w ręce.

- Przy nieoczekiwanej czerwieni agent sprawdza `git status --short` i czas modyfikacji plików, których nie dotykał. Zapis późniejszy niż start sesji oznacza cudzą pracę. Agent mówi o tym użytkownikowi zamiast naprawiać i powtarza przebieg dopiero po domknięciu tamtej pracy.
- Krok destrukcyjny wobec środowiska, na przykład odtworzenie bazy, kasowanie danych albo przesunięcie głowy łańcucha migracji, wymaga na współdzielonym drzewie pytania do użytkownika, także wtedy, gdy stoi wprost w zatwierdzonym planie.
- Pomiar zrobiony na starcie zadania starzeje się. Przed zapisem na zewnątrz, do cudzego systemu albo bazy, agent powtarza pomiar tuż przed samym zapisem.
- Ruch `HEAD` w trakcie sesji, commit albo merge wykonany przez człowieka, unieważnia wnioski wydane na wcześniejszym stanie. Przed każdą fazą agent sprawdza `git log --oneline -3` i `git status --short`, a po ruchu `HEAD` porównuje pliki dowodowe i weryfikuje wydane werdykty ponownie, zostawiając ich pierwotne brzmienie jako historię.
- Komunikat narzędzia edycji, że plik zmienił się od ostatniego odczytu, jest sygnałem cudzej edycji szybszym niż czas modyfikacji. Agent sprawdza wtedy `git diff` pliku i nie cofa cudzej zmiany, tylko bierze ją jako stan bieżący.
- Przy dłuższej redakcji artefaktu agent przed zamknięciem pracy czyta kluczowe sekcje ponownie i porównuje je z odczytem ze startu. Własny zapis stempluje plik czasem agenta i ukrywa cudzą edycję przed kontrolą czasu modyfikacji.

## 5. System `agent_docs`/memory

### 5.1. `docs/` kontra `agent_docs/`

Repozytorium rozróżnia dwie warstwy dokumentacji. `docs/` jest stałe i nieedytowalne przez agenta. Trzyma `docs/standards/` (stałe standardy pisane przez człowieka, ten dokument jest jednym z nich) oraz katalogi, które projekt dokłada sam, na przykład zrzut schematu generowany maszynowo, dokumentację producenta albo wiedzę operacyjną o środowisku - każdy wpisany do mapy w `docs/standards/README.md` razem z proweniencją. Agent nigdy nie edytuje `docs/` poza zadaniem, które wprost tego dotyczy.

`agent_docs/` jest przeciwieństwem - to warstwa aktywnie zapisywana przez agenta, złożona z trzech części: `agent_docs/session_context.md` (opis projektu wstawiany na start sesji przez hook z rozdz. 6.3), `agent_docs/ai_workflows/shape_prd_workflow.md` (metodologia łańcucha opisanego w sekcjach 3-4 tego dokumentu) oraz `agent_docs/memory/` (trwała pamięć decyzji per moduł, opisana niżej).

### 5.2. `agent_docs/memory`

`agent_docs/memory/` to trwała pamięć decyzji per moduł - coś innego niż globalna auto-memory Claude (`~/.claude/projects/.../memory/`), która trzyma preferencje i kontekst konkretnego użytkownika. `agent_docs/memory/` trzyma wiedzę o samym repozytorium, dostępną każdemu narzędziu - Claude Code i Codeksowi jednakowo.

Format wpisu, struktura grup i zasady kiedy pisać/nie pisać: patrz `docs/standards/standard_agent_docs.md`, sekcja "Format wpisu agent_docs/memory" - to jest jedyne źródło prawdy dla tej konwencji.

## 6. Implementacja i technikalia

### 6.1. Dualizm `.claude/` vs `.agents/` (Claude Code kontra Codex)

Repozytorium jest używane z dwóch narzędzi agentowych - Claude Code i Codeksa - i utrzymuje dla nich dwa równoległe zestawy skilli: `.claude/skills/` i `.agents/skills/`. To zamierzona duplikacja, nie przypadkowy rozrost: domyślnie treść skilla ma się różnić między kopiami wyłącznie ścieżką do skryptów, nigdy regułami. Pełna identyczność obu narzędzi nie jest celem - subagenci w sensie zdefiniowanym w słowniku są mechanizmem wyłącznie Claude Code, a `.agents/` zawiera wyłącznie `skills`. Hooki istnieją po obu stronach, ale nie w pełnym, symetrycznym zestawie - patrz rozdz. 6.3. Wymóg jest węższy: każdy wspólny krok łańcucha musi dać się przejść w obu narzędziach na tych samych artefaktach i tych samych regułach.

Pięć skilli ma parę po obu stronach: `plan-shape`, `plan-prd`, `plan-implement`, `implementation-dod-review`, `load-context`. Nie ma dziś ani jednego skilla istniejącego wyłącznie po jednej stronie - allowlista wyjątków w teście parytetu jest pusta i taka ma zostać. Wyjątek jednostronny wymaga łącznie: zależności od możliwości dostępnej tylko w jednym narzędziu, jawnej decyzji w zaakceptowanym planie zadania i wpisu na tę allowlistę. Sama wygoda albo brak czasu na drugą wersję nie jest powodem - skill bez pary cicho dzieli repozytorium na dwa różne procesy w zależności od tego, czym ktoś je otworzył.

Wyjątek Codex-only wymaga łącznie zależności platformowej, jawnej decyzji w zaakceptowanym planie zadania i wpisu na ścisłej allowliście testu architektury. Nie wolno używać go dla zwykłego skilla wspólnego ani do ukrywania przypadkowego braku kopii. Każdy wpis allowlisty musi faktycznie istnieć tylko w `.agents/skills/`.

`load-context` zasługuje na osobne wyjaśnienie, bo nie jest krokiem łańcucha seed -> plan opisanego w sekcji 4 - to osobne narzędzie pomocnicze, które na żądanie tworzy jeden zrzut (`output.txt`) zawartości wskazanego folderu repozytorium, żeby analiza mogła się oprzeć na jednym pliku zamiast wielu pojedynczych odczytów. Mimo to jest objęte tym samym mechanizmem parytetu co skille łańcucha, bo istnieje w obu lokalizacjach.

### 6.2. Test parytetu

`tests/architecture/test_agent_docs_parity.py` jest bramką anty-dryfową dla całego dualizmu opisanego wyżej. Zawiera cztery testy: parytet `AGENTS.md`/`CLAUDE.md`; zakaz skilli istniejących tylko po stronie Claude i zakaz nieznanych skilli istniejących tylko po stronie Codexa poza ścisłą allowlistą; identyczność treści każdej wspólnej pary skilli po normalizacji; oraz identyczność instrukcji każdej pary definicji ról agentowych (rozdz. 6.4). Test dodatkowo wymaga, aby każdy allowlistowany skill Codex-only istniał w `.agents/skills/` i nie miał kopii w `.claude/skills/`, a każda rola miała wariant po obu stronach.

Normalizacja par rdzenia i skilli dopuszcza trzy, i tylko trzy, jawnie nazwane różnice: nazwę pliku rdzenia (`AGENTS.md` albo `CLAUDE.md` sprowadzone do wspólnej formy), frazę "Codex ma stosować" / "Claude Code ma stosować" (sprowadzoną do wspólnej formy), oraz ścieżkę do skryptów skilla (`.claude/skills/<nazwa>/scripts/` sprowadzoną do `scripts/`). Normalizacja par ról jest osobną listą i ma na niej dokładnie jedną pozycję: nazwę uruchamiacza komend ("przez `Bash` albo `PowerShell`" kontra "przez terminal"), bo Codex nie zna narzędzi o tych nazwach. Każda z tych reguł jest jedną świadomie dozwoloną różnicą - dopisanie kolejnej ma być decyzją, nie przypadkiem, a różnica przypadkowa ma zostać naprawiona w treści plików, nie ukryta normalizacją. Porównanie działa przez `difflib.SequenceMatcher`, a nie linia po linii, żeby wstawiona albo usunięta sekcja w jednym pliku nie fałszowała diffu dla reszty pliku. Kod testu (stała `PLAN_REFERENCE`) wskazuje w komunikacie błędu na ten rozdział jako miejsce z listą dozwolonych wyjątków; komunikat o rozjeździe pary ról odsyła osobno, do rozdz. 6.4.

Pary ról porównuje się po treści odczytanej, nie po surowym tekście pliku: wariant dla Claude Code jest plikiem markdown z frontmatterem, wariant dla Codeksa kluczem `developer_instructions` w pliku TOML z literalnymi sekwencjami ucieczki końca linii. Frontmatter zostaje poza porównaniem, bo niesie konfigurację narzędzia (lista narzędzi, tryb uprawnień, limit tur), która nie ma odpowiednika po drugiej stronie.

### 6.3. Hooki

Jeden hook ma odpowiednik po obu stronach, jeden działa wyłącznie w Claude Code:

- `local_docs_context.py` - hook `SessionStart`, zarejestrowany osobno dla każdego narzędzia (`.claude/settings.json` i `.codex/hooks.json`), z tym samym skryptem w `.claude/hooks/` i `.codex/hooks/`. Bajtową identyczność obu kopii pilnuje `tests/architecture/test_session_context_hook.py`. Na starcie każdej sesji dopisuje do kontekstu treść `agent_docs/session_context.md` (opis projektu i wskazanie specyfikacji produktu), ostrzeżenie o skillach osobistych przykrywających skille projektu (rozdz. 6.5), wskazanie mapy `docs/standards/README.md` i rejestru decyzji oraz dwie pozycje z `agent_docs/` (workflow łańcucha i konwencja memory). Poza `session_context.md` sprawdza tylko, czy pliki istnieją, i nie czyta ich treści, żeby nie podnosić kosztu startu sesji.
- `block_dangerous_commands.py` - hook `PreToolUse`, wyłącznie w Claude Code, bez odpowiednika w Codeksie. Uruchamiany przy próbie wywołania `Bash` albo `PowerShell`. Blokuje `git reset --hard`, `git clean`, `git restore` dotykające drzewa roboczego, formy `git checkout` wskazujące ścieżkę lub pathspec, rekursywne kasowanie przez `rm`, `Remove-Item`, aliasy PowerShell i polecenia cmd z flagą `/s`, kasowanie przez `find -delete`, kasowanie katalogu `.git` i plików `.env` oraz `git commit` i `git push`, także z opcją `-C` albo `-c` przed poleceniem - commit i wypchnięcie wykonuje człowiek. `git restore --staged` bez flagi `--worktree` przechodzi, bo zmienia tylko indeks. Niejednoznaczny `git checkout <nazwa>` jest blokowany, gdy `<nazwa>` jest też istniejącą ścieżką; do przełączenia takiej gałęzi służy jednoznaczny `git switch`. Przy niepoprawnym wejściu albo wyjątku hook działa fail-closed: zwraca poprawną decyzję `deny` z kodem 0 i podaje typ błędu bez treści komendy. Dzięki temu błąd strażnika nie wyłącza ochrony jako nieblokujący błąd hooka.

Codex dostaje więc ten sam kontekst startowy co Claude Code, ale nie ma ochrony przed niebezpiecznymi komendami odpowiadającej `block_dangerous_commands.py`.

### 6.4. Subagenci Claude-only

Dwa subagenci istnieją wyłącznie w `.claude/agents/`, bez odpowiednika w `.agents/` (który zawiera wyłącznie skille):

- `repo-researcher` - agent do szybkiego, read-only researchu w repozytorium. Ma dostęp do `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, pracuje w trybie `permissionMode: plan` (nie edytuje plików ani nie uruchamia komend ze skutkami ubocznymi), limit 12 tur. Zwraca dokładnie trzy rodzaje pozycji: ustalenie wraz ze wskazaniem pliku i linii, jawne "nie znaleziono" dla pytania bez odpowiedzi w repozytorium i jawne "niesprawdzone" dla pytania, do którego nie dotarł przed limitem wywołań. Nie zwraca rekomendacji ani oceny ryzyka, bo ocena należy do wołającego: rola researchowa zna wycinek repozytorium, ale nie zna kontekstu zadania, więc jej rekomendacja byłaby wnioskiem z niepełnego obrazu. Brak odpowiedzi jest tu wynikiem, nie porażką.
- `dod-reviewer` - agent do review względem Definition of Done. Te same narzędzia co wyżej, plus jawnie przypisany skill `implementation-dod-review`, limit 16 tur. Nie implementuje poprawek, tylko ocenia gotowość zmian, w tej samej kolejności raportowania co opisano wyżej w tej sekcji.

Każda z tych ról ma wariant po stronie Codeksa, w innym mechanizmie i innym formacie: `.codex/agents/<nazwa>.toml`, natywna rola Codeksa, nie subagent. Para wariantów jest objęta kontrolą parytetu z rozdz. 6.2 - zmiana treści roli idzie równolegle do obu plików, a rozjazd poza jedyną dopuszczoną różnicą w nazwie uruchamiacza komend zatrzymuje testy.

Limit tur. Obie role kończą pracę na limicie tur, a bez wyraźnej instrukcji potrafią stanąć na nim bez raportu, bo szeroki wycinek repozytorium zjada limit na samo czytanie. Dlatego obie definicje każą oddać raport najpóźniej po około dziesięciu wywołaniach narzędzi, z jawną listą tego, czego nie zdążyły sprawdzić. Wołający zawęża listę plików w poleceniu, a duży zakres dzieli na kilka równoległych wywołań z rozłącznymi listami plików i wspólnym opisem bramek już odpalonych przez główną sesję, żeby role ich nie powtarzały. Rolę zatrzymaną bez raportu wznawia się poleceniem oddania raportu bez dalszych wywołań narzędzi, nie prośbą o kontynuację.

Poza kontrolą zostaje co innego: zgodność treści między skillem `implementation-dod-review` a definicją `dod-reviewer` - te dwa dokumenty opisują ten sam proces, ale nie są swoimi kopiami, więc porównanie ich maszynowo nie ma sensu i trzeba to pilnować ręcznie.

### 6.5. Kolizja nazw skilli personal/project

Gdy skill o tej samej nazwie istnieje jednocześnie w katalogu projektu (`.claude/skills/`) i w katalogu osobistym użytkownika (`~/.claude/skills/`), Claude Code ładuje kopię osobistą - to udokumentowane zachowanie, bez opcji konfiguracyjnej, która by je zmieniała. Przy subagentach jest odwrotnie: definicja z `.claude/agents/` projektu wygrywa z osobistą. Kolejność ładowania przy takiej samej kolizji po stronie Codeksa nie została ustalona.

Reguła: w katalogu osobistym nie trzyma się skilli o nazwach skilli projektu. Kopia osobista nie jest objęta testem parytetu z rozdz. 6.2 i starzeje się niezależnie, więc wywołanie skilla po nazwie uruchamiałoby treść inną niż opisana w tym standardzie, bez żadnego komunikatu. Hook `local_docs_context.py` sprawdza na starcie sesji katalogi `~/.claude/skills`, `~/.agents/skills` i `~/.codex/skills` i wypisuje ostrzeżenie z nazwami kolidujących skilli. Do czasu usunięcia kolizji treść skilla czyta się wprost z `.claude/skills/<nazwa>/SKILL.md`.

## 7. Gdzie szukać żywych przykładów

Ten dokument opisuje łańcuch abstrakcyjnie. Szablon nie niesie przykładowej inicjatywy - pierwszym żywym przykładem jest pierwsza inicjatywa projektu przepuszczona przez pełny łańcuch.

Ogólniej: dowolny katalog zawierający komplet plików `_SEED.md`, `_SHAPE.md`, `_PRD.md`, `_PLAN.md` (i opcjonalnie `_REVIEW.md`) - czy to `plans/<INICJATYWA>/` wprost, czy `plans/<INICJATYWA>/<ZADANIE>/`, czy ich odpowiedniki pod `plans_finished/` - jest żywym przykładem tego, jak łańcuch wygląda w praktyce dla konkretnego typu zadania. Odwołania do `plans/<INICJATYWA>/` w seedach, dawnych wpisach review i memory zarchiwizowanej inicjatywy są zapisem historycznym - katalog o tej nazwie trzeba wtedy szukać w `plans_finished/`.

## 8. Checklista

- Zadanie przechodzi seed -> shape -> PRD -> plan -> implementacja -> review, z ręcznym przejściem między fazami poza jednym wyjątkiem: `plan-implement` samo wywołuje review na końcu.
- Każde pytanie fazy shape dotykające jednej z dziesięciu kategorii ryzyka blokującego (rozdz. 3.3) ma `Block: yes` i jest jednoznacznie rozstrzygnięte przed przejściem do PRD.
- PRD nie zawiera nic z czarnej listy: modeli danych, kolumn, migracji, ścieżek kodu, nazw funkcji, bibliotek, deploymentu, sekretów (rozdz. 3.4).
- PLAN ma konkretne nazwy plików, funkcji i kontraktów danych w każdym kroku "Zakres zmian", zero TODO, zero otwartych pytań.
- Wartość regulatora stoi w nagłówku shape'a, a każda pozycja rozstrzygnięta bez pytania niesie frazę o decyzji agenta (rozdz. 3.5).
- Regulator nie usunął ani jednego pytania blokującego - dziesięć kategorii obowiązuje na każdej pozycji skali (rozdz. 3.3 i 3.5).
- Format każdego z pięciu artefaktów łańcucha i wpisu `agent_docs/memory` - patrz `standard_agent_docs.md`, nie ten dokument.
- REVIEW opisuje przebieg konkretnego zadania i traci znaczenie po jego zamknięciu - trwała wiedza idzie do `agent_docs/memory`, nigdy odwrotnie.
- Inicjatywa trafia do `plans_finished/` w całości i tylko na jawny dowód zakończenia albo anulowania: końcowe `ready` dla całego zakresu albo inne jawne zamknięcie. Komplet plików, zamknięty wywiad, zamknięty plan, rozliczenie jednego zadania z kilku, częściowy werdykt ani wiek katalogu tego nie zastępują; sprzeczny status oznacza pytanie do użytkownika, nie przeniesienie (rozdz. 4.6).
- Przeniesienie nie zmienia seedów, dawnych wpisów review i memory ani zamrożonych materiałów; aktualizuje wyłącznie edytowalne odwołania, w obu kierunkach. Wznowienie tej samej pracy to powrót katalogu do `plans/` z dopisanym wpisem o wznowieniu; nowy zakres to nowa inicjatywa (rozdz. 4.6).
- Wspólny krok łańcucha działa tak samo w Claude Code i Codeksie, na tych samych artefaktach i regułach (rozdz. 6.1).
- Każdy wyjątek Codex-only w skillach ma allowlistę w teście architektury i uzasadnienie w zaakceptowanym planie zadania (rozdz. 6.1-6.2).
- Hooki i subagenci nie są symetryczne między Claude Code i Codeksem - sprawdź rozdz. 6.3-6.4 przed założeniem, że mechanizm działa tak samo po obu stronach.
- Na współdzielonym drzewie nieoczekiwana czerwień i krok destrukcyjny zaczynają się od sprawdzenia `git status` i czasu modyfikacji plików, a cudzej pracy w toku się nie naprawia (rozdz. 4.7).
- Wywołanie roli `repo-researcher` albo `dod-reviewer` ma zawężoną listę plików, a rola oddaje raport przed limitem tur (rozdz. 6.4).
- W katalogu osobistym użytkownika nie ma skilli o nazwach skilli projektu; ostrzeżenie hooka o kolizji znaczy, że treść skilla trzeba czytać wprost z `.claude/skills/<nazwa>/SKILL.md` (rozdz. 6.5).
- Numeracja rozdziałów tego dokumentu jest cytowana przez inne pliki repo - każda przyszła zmiana numeracji wymaga sprawdzenia wszystkich cytujących miejsc, nie tylko treści samego dokumentu.
