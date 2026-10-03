# Standard bazy danych

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Baza jest jedyną rzeczą w tym serwisie, której nie da się wydać ponownie. Kod można wycofać do poprzedniej wersji w minutę; kolumnę usuniętą razem z danymi odtwarza się z kopii zapasowej, jeśli ktoś ją miał. Ta asymetria jest powodem, dla którego reguły dotyczące bazy są ostrzejsze niż reguły dotyczące kodu.

Drugi powód jest właściwy dla tego serwisu: baza należy wyłącznie do niego. Nic innego jej nie czyta ani nie zapisuje, i to jest świadoma decyzja, na której stoi możliwość wydawania i zastępowania tego serwisu osobno. Reguła, która tę prywatność narusza, kosztuje znacznie więcej niż wygląda.

## Zakres i granice

Ten standard odpowiada za: rozdział źródła prawdy o schemacie od zrzutu stanu faktycznego, formę zmian schematu, prywatność bazy, zakaz logiki w bazie, dostęp do danych i pisanie zapytań.

Czego tu nie ma:

- kształt konkretnych tabel, kolumn, indeksów i ograniczeń - przesądza specyfikacja produktu wskazana w `CLAUDE.md`; ten standard nie powtarza ich, żeby nie powstało drugie źródło prawdy;
- wybór typu kolumny czasu i semantyka przesunięcia strefowego - to `standard_time.md`;
- czy powtórzony zapis zdubluje dane - to `standard_idempotency.md`;
- limity czasu zapytań - to `standard_errors.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Dwa różne dokumenty o schemacie i dlaczego nie wolno ich pomylić

Źródłem prawdy o tym, jaki schemat ma być, jest kod repozytorium: definicje modeli oraz historia zmian schematu. To jest jedyne miejsce, którego edycja zmienia bazę.

Zrzut schematu bazy jest obrazem stanu faktycznego serwera - tego, co w bazie rzeczywiście jest, wraz z datą wykonania zrzutu. Zrzut powstaje maszynowo, jest nieedytowalny ręcznie i niczego nie zmienia. Edycja pliku zrzutu nie zmienia bazy, a jedynie psuje jedyne miejsce, które mówi prawdę o serwerze.

Różnica między tymi dwoma jest sama w sobie informacją: oznacza, że baza rozjechała się z repozytorium. To nie jest błąd zrzutu do poprawienia - to znalezisko do wyjaśnienia.

Przed czymkolwiek, co dotyka tabeli albo kolumny, otwiera się oba: specyfikacja produktu mówi, jak ma być, zrzut schematu mówi, jak jest.

## Forma zmian schematu

Każda zmiana schematu jest rewizją Alembica i nie ma drugiej dopuszczonej formy. Ręczny plik `.sql` wykonany na bazie, zmiana zrobiona w kliencie graficznym, `ALTER TABLE` wklejony w trakcie awarii - to nie są warianty tej samej rzeczy, tylko zmiany, których repozytorium nie widzi. Baza rozjeżdża się wtedy z repozytorium w sposób, o którym dowiadujemy się dopiero przy następnym zrzucie, o ile ktoś go zrobi.

Rewizje tworzą łańcuch liniowy. Nie ma gałęzi i nie ma dwóch rewizji o tym samym poprzedniku - kolejność nakładania ma być jedna i widoczna z nazw plików.

Treścią rewizji jest surowy SQL w `op.execute`, jedna instrukcja na wywołanie. Nie używamy `op.create_table` ani generowania rewizji z modeli. Powód jest praktyczny: review rewizji jest porównaniem linia w linię z DDL-em zapisanym w specyfikacji produktu, a nie czytaniem tłumaczenia na interfejs biblioteki. Drugi powód jest mocniejszy: generowanie z modeli przemilcza bez śladu obiekty, na których stoją niezmienniki schematu - domenę przesunięcia strefowego, klauzulę `NULLS NOT DISTINCT`, warunki sprawdzające strukturę dokumentów, listy `INCLUDE` i warunki indeksów częściowych. Migracja przechodzi czysto i produkuje schemat bez tego jednego indeksu, który czynił duplikat niemożliwym.

W SQL wewnątrz rewizji nie ma komentarzy linijkowych. Wyjaśnienie mieszka w docstringu rewizji, po polsku, i mówi, co ta rewizja dodaje i dlaczego akurat w tym miejscu łańcucha. Nie dodajemy też `COMMENT ON` do obiektów bazy: uzasadnienia są w specyfikacji produktu, a ich druga kopia w bazie rozjechałaby się z pierwszą.

Uprawnienia nadaje się w rewizjach, nie w skrypcie należącym do lokalnego uruchomienia. Zrzut schematu pomija uprawnienia, więc rewizje są jedynym miejscem w repozytorium, które odpowiada na pytanie, kto co może w bazie. Skrypt tworzący bazę i konta zostaje przy tym, czego rewizja zrobić nie może: przy samej bazie i samych kontach.

Uprawnienia domyślne obejmują wyłącznie obiekty tworzone po ich ustawieniu i wyłącznie przez tę samą rolę w tym samym schemacie. Dlatego stan docelowy jest dodatkowo zapisany jawnym nadaniem na wszystkich obiektach. To nie jest pas zapasowy na wypadek pomyłki: tabelę z wersją schematu tworzy sam Alembic, zanim wykona treść pierwszej rewizji, więc uprawnienia domyślne ustawione w tej rewizji jej nie obejmują.

Rewizje pierwszego postawienia bazy nie mają wycofania - zgłaszają odmowę z komunikatem wskazującym właściwą drogę. Wspieranym sposobem wycofania takiego bootstrapu jest odtworzenie bazy, a funkcje kasujące schemat byłyby kodem destrukcyjnym, którego nikt nie uruchomi i nikt nie przetestuje. Każda rewizja powstająca później ma mieć normalne wycofanie.

Wąskim wyjątkiem jest późniejsza rewizja nieodwracalnie scalająca albo rozdzielająca przestrzenie nazw, gdy wierne wycofanie wymagałoby utrzymywania martwej kopii usuwanych danych wyłącznie na potrzeby downgrade'u. Taki wyjątek musi być jawnie rozstrzygnięty w zaakceptowanym planie, zatrzymywać `downgrade()` przez `NotImplementedError`, wskazywać odtworzenie z kopii jako wspieraną drogę i mieć test albo próbę wdrożeniową potwierdzającą odmowę. Nie obejmuje migracji, której cofnięcie jest tylko pracochłonne.

Alembic nie wykrywa edycji rewizji, która została już nałożona. Po każdej poprawce w treści istniejącej rewizji obowiązuje odtworzenie bazy od zera, nie ponowne nałożenie. Jedyne, co łapie taki rozjazd po fakcie, to porównanie ze zrzutem stanu faktycznego - co jest jednym z powodów, dla których ten zrzut w ogóle istnieje.

Zmiana schematu nigdy nie dzieje się sama przy starcie środowiska, ani lokalnie, ani na serwerze. Jest zawsze decyzją człowieka, wywoływaną osobnym poleceniem.

Zanim powstanie propozycja nowej tabeli albo drugiego bytu obok istniejącego, sprawdza się liczność relacji. Relacja jeden do jednego to kolumna na istniejącym wierszu, nie tabela boczna. Gdy powodem nowego bytu jest to, że przebieg albo zapytanie musi po czymś filtrować, odpowiedzią jest kolumna.

## Baza jest prywatna

Żaden inny system nie czyta ani nie zapisuje tej bazy. Informacja, której serwis potrzebuje z zewnątrz, przychodzi jego własnym interfejsem, z jednym wąskim wyjątkiem: nazwane w specyfikacji produktu źródła tylko do odczytu, po które serwis sięga sam. Zapis do obcej bazy jest zakazany bez wyjątku. Granica odczytu źródła, które jest usługą HTTP, a nie bazą, stoi w `standard_architecture.md`, w sekcji o wywołaniach systemów zewnętrznych.

Konsekwencje praktyczne, które łatwo naruszyć w dobrej wierze:

- nie dodaje się widoku ani procedury "dla raportowania" po stronie bazy, żeby ktoś z zewnątrz mógł to wygodnie odpytać - to zamienia prywatną bazę we współdzielony interfejs bez kontraktu i bez wersjonowania;
- nie dodaje się kolumny na potrzeby innego systemu;
- nie przyjmuje się zapisu z zewnątrz, nawet jednorazowego, nawet ręcznego.

Sprawdzenie współwłasności przed zmianą obiektu przestaje mieć sens jako pytanie o inne systemy, ale zostaje jako pytanie o warstwy tego serwisu: czy ten obiekt jest czytany przez zadanie okresowe, przez odczyt listy, przez raport.

## Zakaz logiki w bazie

Reguły domenowe mieszkają w kodzie, nie w bazie. Nie dodaje się triggerów, a procedury i funkcje nie zawierają decyzji domenowych.

Powód: reguła w triggerze jest niewidoczna dla osoby czytającej kod, nie przechodzi przez review kodu, nie ma testu i nie da się jej wywołać ani sprawdzić lokalnie. Rekord zmieniony przez trigger wygląda jak rekord zmieniony bez powodu, a poszukiwanie przyczyny zaczyna się w kodzie, w którym jej nie ma.

Ograniczenia integralności są czym innym i są wymagane: klucze obce, unikalność, warunki poprawności wartości, domeny na powtarzalnym zakresie wartości oraz ograniczenia sprawdzające strukturę dokumentu w kolumnie dokumentowej. One nie podejmują decyzji - one nie pozwalają zapisać stanu, który nie ma prawa istnieć. Backstop przed duplikatem musi żyć w bazie, nie tylko w kodzie sprawdzającym przed zapisem, bo dwa równoległe przebiegi sprawdzą jednocześnie i oba przejdą (`standard_idempotency.md`).

Granica jest w tym, jak dużo taki warunek wie o domenie. Sprawdzenie, że dokument ma tablicę pod ustalonym kluczem albo że kolumna dyskryminatora zgadza się z polem w dokumencie, to integralność - nic nie decyduje, a stanu bez sensu nie da się zapisać. Sprawdzenie, czy pole dokumentu jest wymagane albo czy jego wartość mieści się w zakresie zapisanym w konfiguracji rekordu, to już reguła domenowa i mieszka w kodzie. Typ dokumentowy z natywną walidacją JSON nie przesuwa tej granicy - tylko zdejmuje potrzebę osobnego warunku na samą poprawność składni.

## Dostęp do danych

Jeden sposób otwarcia połączenia w całym repozytorium, z jednego miejsca. Kod, który otwiera połączenie po swojemu, omija wszystko, co to jedno miejsce ustawia - w tym przypięcie strefy sesji do UTC, bez którego odczytane wartości czasu zależą od konfiguracji serwera, a nie od danych (`standard_time.md`).

Wartości trafiają do zapytania wyłącznie jako parametry. Sklejanie zapytania z fragmentów tekstu zawierających dane jest zakazane bez wyjątków - także tam, gdzie wartość "na pewno" pochodzi z bezpiecznego źródła, bo to założenie przestaje być prawdziwe przy pierwszej zmianie wywołującego.

Zapytanie wymienia kolumny, których potrzebuje. `SELECT *` wiąże kod z aktualnym kształtem tabeli w sposób niewidoczny: dodanie kolumny zmienia wynik zapytania, którego nikt nie zmieniał.

Odczyt zwraca dane w otypowanej strukturze, nie w surowych wierszach przekazywanych dalej po pozycjach. Kod indeksujący wynik liczbami psuje się przy zmianie kolejności kolumn i nie mówi, co czyta.

Jedna operacja domenowa to jedna transakcja. Dotyczy to wprost komend interfejsu programistycznego: każda jest jedną transakcją i sama pilnuje swoich niezmienników. Sekwencja zapisów, która musi się udać w całości, nie jest wykonywana jako kilka niezależnych transakcji z nadzieją, że wszystkie przejdą.

## Zapytania w kodzie

Zapytanie w stałej ma nazwę w kształcie `<CZASOWNIK>_<CO>_SQL` (`standard_naming.md`).

Identyfikatory słownikowe nie są wpisywane w kod wprost. Wartości słownikowe są odwzorowane jako wyliczenia i tych wyliczeń używa logika, a nie liczby. Liczba wpisana w warunek jest poprawna do dnia, w którym ktoś zmieni zawartość słownika.

Kolumny tekstowe niosą pełny zakres znaków, bo treść jest po polsku. Na PostgreSQL wynika to z kodowania bazy (`UTF8`), nie z wyboru typu - `varchar(n)` i `text` przechowują to samo, a szerokość jest udokumentowanym limitem długości, nie decyzją o zestawie znaków.

Osobną decyzją jest kolacja, i ona nie jest domyślna. Baza powstaje z wbudowanego dostawcy lokalizacji z locale `C.UTF-8`, czyli porównanie i sortowanie idą po bajtach: deterministycznie, szybko i tak, że indeks da się użyć do dopasowania prefiksu.

Wybór dostawcy, a nie samo `LC_COLLATE = 'C'`, jest tu istotą rzeczy, bo kolacja i klasyfikacja znaków to dwie różne sprawy i potrzebne są obie naraz. Samo `LC_CTYPE = 'C'` daje porównanie bajtowe i zarazem zabiera `lower()` znajomość alfabetu: `lower('ŁÓDŹ')` zwraca `ŁÓDŹ`, więc wyszukiwanie po fragmencie nazwy przestaje działać dla każdego nazwiska z polskim znakiem. Wbudowany dostawca rozdziela te dwie sprawy: porównanie zostaje bajtowe, klasyfikacja znaków rozumie UTF-8. Wymaga PostgreSQL 17 lub nowszego; na starszym serwerze ten sam efekt daje dostawca libc z `LC_COLLATE = 'C'` i `LC_CTYPE = 'C.UTF-8'`.

Parametry te są nieodwracalne po utworzeniu bazy: ich zmiana wymaga przebudowania każdego indeksu na kolumnie tekstowej albo postawienia bazy od nowa. Dlatego są sprawdzane zachowaniem, a nie deklaracją - testem krytycznym na wartościach z polskimi znakami, nie na samym ASCII.

Konsekwencje trzeba znać, bo są widoczne dla użytkownika. Porównanie tekstu jest wrażliwe na wielkość liter, więc unikalność kodu słownikowego też - normalizacja kodów do wielkich liter dzieje się na wejściu interfejsu programistycznego, nie w bazie. Sortowanie po polsku nie wychodzi z bazy i należy do warstwy prezentacji. Wyszukiwanie po fragmencie nazwy idzie przez `lower()` i indeks wyrażeniowy, w jednym miejscu dla wszystkich takich wyszukiwań, nie przez kolację nierozróżniającą wielkości liter - ta ostatnia wyklucza użycie `LIKE`, czyli dokładnie to, do czego wyszukiwanie jest potrzebne.

## Checklista

- Czy zmiana dotykająca tabeli albo kolumny została poprzedzona otwarciem specyfikacji produktu oraz zrzutu schematu?
- Czy zmiana nie edytuje plików zrzutu schematu ręcznie?
- Czy rozjazd między zrzutem a modelami został wyjaśniony, a nie zignorowany?
- Czy przed propozycją nowej tabeli sprawdzono liczność relacji, a relacja jeden do jednego trafiła do kolumny na istniejącym wierszu?
- Czy zmiana nie otwiera bazy dla innego systemu przez widok, procedurę ani kolumnę dodaną na jego potrzeby?
- Czy zmiana nie zapisuje do obcej bazy?
- Czy zmiana nie wprowadza triggera ani decyzji domenowej po stronie bazy?
- Czy backstop przed duplikatem istnieje w bazie, nie tylko w kodzie sprawdzającym przed zapisem?
- Czy połączenie otwierane jest jedynym obowiązującym sposobem?
- Czy wszystkie wartości trafiają do zapytania jako parametry?
- Czy zapytanie wymienia kolumny zamiast używać `SELECT *`?
- Czy odczyt zwraca otypowaną strukturę, a nie surowe wiersze indeksowane pozycjami?
- Czy jedna operacja domenowa wykonuje się w jednej transakcji?
- Czy identyfikatory słownikowe pochodzą z wyliczeń, a nie z liczb wpisanych w kod?
- Czy nowa kolumna tekstowa ma udokumentowany limit długości albo świadomie go nie ma?
- Czy nowe wyszukiwanie po fragmencie tekstu idzie przez `lower()` i indeks wyrażeniowy, a nie przez kolację?
- Czy nowe ograniczenie na kolumnie dokumentowej sprawdza strukturę, a nie regułę domenową?
- Czy zmiana schematu idzie formą opisaną w sekcji o formie zmian schematu: rewizją Alembica, surowym SQL-em, w łańcuchu liniowym?
- Czy nowe uprawnienie w bazie zostało nadane w rewizji, a nie w skrypcie należącym do lokalnego uruchomienia?
- Czy po edycji rewizji już nałożonej baza została odtworzona od zera, a nie zaktualizowana?
