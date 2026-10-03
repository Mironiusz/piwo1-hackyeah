# Standard nazewnictwa

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Nazwa pliku i nazwa funkcji są pierwszą informacją, jaką dostaje ktoś szukający czegoś w repozytorium - i jedyną, którą widzi, zanim cokolwiek otworzy. Gdy ta sama odpowiedzialność nazywa się w trzech miejscach na trzy sposoby, szukanie przestaje działać: trzeba znać historię repozytorium, żeby wiedzieć, czego szukać. Ten standard ustala nazwy docelowe, żeby ta wiedza nie była potrzebna.

## Zakres i granice

Ten standard odpowiada za konwencje nazw plików i funkcji.

Czego tu nie ma:

- rejestr nazw faktycznie występujących w repozytorium - to `naming_registry.md`, który opisuje stan faktyczny, nie docelowy;
- co dokładnie robi dana warstwa kodu i czego nie robi - to `standard_architecture.md`, sekcja o granicy warstw;
- nazwy w bazie danych: tabele, kolumny, indeksy, constrainty - to `standard_database.md` oraz specyfikacja produktu wskazana w `CLAUDE.md`;
- nazwy ścieżek w interfejsie programistycznym - przesądza je specyfikacja produktu wskazana w `CLAUDE.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Język nazw w kodzie

Identyfikatory w kodzie są po angielsku: nazwy funkcji, zmiennych, klas, stałych, plików, testów i fixture'ów. Docstringi, komunikaty błędów, treść logów i cała dokumentacja są po polsku, zgodnie z rdzeniem reguł.

Powód nie jest estetyczny. Kod miesza się z nazwami z bibliotek, które są angielskie i pozostaną angielskie - `logging`, `pytest`, warstwa dostępu do bazy. Polska nazwa funkcji stojąca obok angielskiej nazwy z biblioteki wymusza przeskakiwanie między dwoma językami w jednej linii, a przy pochodnych formach (liczba mnoga, odmiana przez przypadki) prowadzi do nazw, które trudno przewidzieć przy szukaniu. Nazwa `entries` jest jedna; `wpisy`, `wpisow`, `wpisy_pliku` to trzy wersje tego samego pojęcia.

Dokumentacja i docstringi zostają po polsku bez wyjątku; ta reguła dotyczy wyłącznie identyfikatorów.

## Nazwy zakazane

Nazwa pliku ani funkcji nie może być ogólna do tego stopnia, że nie mówi nic o zawartości: `utils.py`, `helpers.py`, `misc.py`, `common.py` bez tematu, `process_data`, `handle_items`, `do_work`, `manager`. Taka nazwa jest zaproszeniem do wrzucania wszystkiego, co nie miało lepszego miejsca - a plik, do którego wszystko pasuje, po pół roku nie ma właściciela ani granicy.

Plik ze wspólnymi pomocnikami jest dopuszczalny, ale nazwany tematem, nie funkcją w projekcie: `common_dates.py`, nie `common.py`.

## Nazwy funkcji: czasownik mówiący o odpowiedzialności

Prefiks nazwy funkcji mówi, do której odpowiedzialności ona należy. Cztery prefiksy obowiązujące:

- `fetch_` - odczyt danych ze źródła zewnętrznego wobec tej funkcji: bazy, pliku, usługi. Sam odczyt, bez decyzji o tym, co z danymi zrobić.
- `build_` - złożenie wartości albo struktury z danych już posiadanych. Bez odczytu i bez zapisu.
- `resolve_` - decyzja domenowa: wybór, klasyfikacja, rozstrzygnięcie na podstawie reguł. Zwraca decyzję, nie wykonuje jej.
- `apply_` - wykonanie decyzji: zapis, wysłanie, zmiana stanu.

Nazwa `get_` nie jest używana dla odczytu ze źródła - dla tego jest `fetch_`. `get_` bywa mylące, bo w wielu bibliotekach oznacza tani dostęp do już posiadanej wartości, a nie zapytanie do bazy, którego koszt jest o kilka rzędów wielkości inny.

Funkcja, której nazwa wymagałaby dwóch prefiksów naraz, robi dwie rzeczy - to jest sygnał do podziału, nie do wyboru jednego z prefiksów.

## Nazwy plików

Jednostką kodu jest warstwa. Z tego wynika kształt nazw: katalog nazywa warstwę, plik nazywa odpowiedzialność wewnątrz tej warstwy.

Katalogi warstw stoją w korzeniu repozytorium: `api` przyjmuje żądania, `service` trzyma reguły, `data` czyta i zapisuje, a `worker` wyzwala zadania okresowe. Nazwa pliku w takim katalogu mówi, za co w tej warstwie odpowiada, na przykład `api/errors.py`, `api/health.py`, `service/readiness.py`, `data/engine.py`.

Sufiksu z nazwą warstwy w nazwie pliku nie ma i jest to zamierzone. Gdy warstwa jest jednostką, to ona jest katalogiem, a plik nie ma czego po katalogu powtarzać - `data/database_probe.py` jest tym samym co `data/data_database_probe.py`, tylko krótszym o powtórzenie. To odwrotność reguły, która obowiązywałaby, gdyby jednostką była poddomena.

Nazwa pliku z pomocnikiem wspólnym dla wielu warstw ma odwrotny kształt niż nazwa pliku warstwy: temat wspólny idzie prefiksem (`common_<temat>.py`). To rozróżnienie pozwala odpowiedzieć na pytanie "czy mogę to zmienić, nie patrząc na resztę repozytorium" po samej nazwie pliku. Dwa jawne miejsca na wiedzę przekrojową w jednej warstwie i między warstwami opisuje `standard_agent_docs.md` dla pamięci trwałej i ta reguła dla kodu.

## Nazwy stałych z zapytaniami

Stała trzymająca zapytanie do bazy ma nazwę w kształcie `<CZASOWNIK>_<CO>_SQL`. Kolejność jest odwrotna niż w prefiksie `SQL_`, bo wtedy nazwy sortują się po czasowniku i temacie, a nie po wspólnym przedrostku, który nie odróżnia niczego.

## Nazwy w testach

Plik testowy nazywa się od tego, co testuje, plus warstwa testu. Konwencja warstw testów jest w `standard_tests.md`, wraz z tym, jak podział warstwowy kodu przekłada się na katalogi testów.

Fixture może nazywać się jak klasa, którą zwraca, łamiąc konwencję nazw funkcji - to jest jawnie dopuszczone i wyłączone z reguł lintera w `pyproject.toml`.

## Checklista

- Czy żadna nowa nazwa pliku ani funkcji nie jest ogólna do stopnia, w którym nie mówi nic o zawartości?
- Czy prefiks każdej nowej funkcji odpowiada jej faktycznej odpowiedzialności, a nie temu, jak wygodnie było ją nazwać?
- Czy żadna nowa funkcja nie potrzebowałaby dwóch prefiksów naraz?
- Czy nowy plik leży w katalogu warstwy, do której należy, a jego nazwa mówi o odpowiedzialności wewnątrz tej warstwy, nie powtarza jej nazwy?
- Czy nowy plik z pomocnikami wspólnymi ma temat w nazwie i kształt prefiksowy, a nie sufiksowy?
- Czy nowa stała z zapytaniem ma kształt `<CZASOWNIK>_<CO>_SQL`?
- Czy nowe nazwy, których ten standard jeszcze nie przesądza, zostały dopisane do `naming_registry.md`, żeby następna osoba nie wymyślała ich od nowa?
