# Standard testów

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Test pisany bez ustalonej konwencji trafia tam, gdzie autorowi było wygodnie, i sprawdza to, co było łatwe do sprawdzenia. Po kilku miesiącach daje to zbiór, w którym nie da się odpowiedzieć na pytanie, czy dana reguła jest pokryta - trzeba przeczytać wszystkie testy, żeby to ustalić.

Ten standard ustala, gdzie test ma leżeć i co ma sprawdzać, oraz wymienia wprost testy obowiązkowe niezależnie od domeny projektu.

## Zakres i granice

Ten standard odpowiada za: warstwy testów i ich nazewnictwo, lokalność konfiguracji testów, zakres pokrycia, znaczniki, oraz obowiązkowe testy wynikające z ryzyk specyfikacji.

Czego tu nie ma:

- architektura kodu produkcyjnego, którego te testy dotyczą, w tym granica warstw i kierunek zależności - to `standard_architecture.md`;
- co dokładnie ma robić testowana logika - to specyfikacja produktu wskazana w `CLAUDE.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Warstwy testów

Unity sprawdzają jedną funkcję albo jedną regułę w izolacji, bez bazy, bez sieci i bez systemu plików. Leżą w katalogu odpowiadającym ścieżce testowanego kodu, w plikach nazwanych od tego, co sprawdzają.

Jednostką kodu jest warstwa, więc katalogi testów są odbiciem katalogów warstw: `tests/api/`, `tests/service/`, `tests/data/`, `tests/worker/`. Każdy z nich testuje tę warstwę, którą nazywa, i wolno mu podmieniać wyłącznie to, co ta warstwa woła - test warstwy wejścia podmienia zależność endpointu, a nie sondę w warstwie danych. Podział na katalogi jest więc tym samym podziałem, co kierunek zależności między warstwami z `standard_architecture.md`: test, który musi podmienić coś z dwóch warstw niżej, mówi o kodzie, nie o sobie. Projekt pilnuje kierunku zależności testem architektury, który zakłada razem z pierwszym kodem tej warstwy; szablon go nie zawiera.

Testy scenariuszowe sprawdzają regułę na zestawie przypadków wejściowych, w tym brzegowych. Plik ma sufiks `_cases.py`. Ta warstwa jest właściwym miejscem na przypadki, które w specyfikacji są opisane słowem "chyba że" - one są najczęstszym źródłem błędów.

Testy integracyjne sklejają kilka warstw i mają znacznik `integration`. Nie używają realnej sieci ani realnej bazy - jeśli test wymaga jednego albo drugiego, należy do warstwy niżej albo dostaje znacznik `critical`.

Testy interfejsu programistycznego sprawdzają zachowanie widoczne dla konsumenta: kod odpowiedzi, kształt odpowiedzi, odmowę uprawnienia. Sprawdzają kontrakt, nie implementację - test, który przechodzi po zmianie kodu odpowiedzi z odmowy uprawnienia na błąd walidacji, nie sprawdza kontraktu.

Testy infrastruktury w `tests/architecture/` pilnują reguł samego repozytorium, nie logiki serwisu. Szablon ma tam bramki dokumentów i narzędzi agentowych: parytet obu gałęzi narzędziowych (`test_agent_docs_parity.py`), styl prozy w dokumentach (`test_prose_style.py`), kontrakt dokumentów planu (`test_plan_document_contract.py`), brak znaczników konfliktu (`test_conflict_markers.py`) i hak niebezpiecznych komend (`test_dangerous_commands_hook.py`). Reguły kodu serwisu, na przykład kierunek zależności między warstwami, zgodność szablonu środowiska z rzeczywistością albo spójność zadań okresowych, projekt pilnuje testem architektury, który zakłada razem z pierwszym kodem danej warstwy; szablon go nie zawiera.

Reguła repozytorium, którą da się sprawdzić maszynowo, należy do tej warstwy, a nie do osobnego narzędzia z linii poleceń. Test wchodzi do `make test`, przez to do `make check` i przez to do mapy standard - narzędzie weryfikujące w `standard_review.md`, więc odpala się sam przy implementacji i przy review. Osobny cel w `makefile` trzeba pamiętać zawołać, a reguła, o której trzeba pamiętać, nie jest pilnowana.

Testy krytyczne ze znacznikiem `critical` używają realnych zależności i mają wywalić środowisko szybko, gdy coś nie działa. Nie są uruchamiane w każdym przebiegu. Szybki przebieg bez realnych zależności wyklucza je wyrażeniem `-m "not critical"`.

Test krytyczny, który zasiewa dane trwałym zapisem, sprząta po sobie. Trwały zapis jest tam konieczny, gdy wołana funkcja otwiera własne połączenie i nie widzi transakcji fixture, więc rollback nie wystarcza. Sprzątanie idzie przez wspólną fixture w `tests/conftest.py`: test rejestruje w niej przed wywołaniem klucz naturalny zasianego wiersza albo, gdy wiersz założył sam test, jego identyfikator. Po teście fixture rozwiązuje klucze na identyfikatory i kasuje zarejestrowane wiersze razem z wierszami, które na nie wskazują. Gdy klucze obce nie mają `ON DELETE`, kolejność kasowania jest częścią fixture. Kasowanie idzie wyłącznie po zarejestrowanych kluczach, nigdy po wzorcu nazwy.

Test krytyczny może pisać i uruchamia trwały seed, więc zawsze idzie na bazę lokalną. Sesja z testem krytycznym odmawia startu, gdy konfiguracja aplikacji wskazuje środowisko docelowe. Robi to hak `pytest_collection_finish` w `tests/conftest.py`: po zebraniu kolekcji, przed pierwszym testem, kończy sesję kodem 4 (`pytest.ExitCode.USAGE_ERROR`) i komunikatem złożonym ze stałych, bez żadnego adresu. Środowisko czyta z tej samej wartości konfiguracji, według której kod serwisu wybiera bazę. Hak działa także przy samym zbieraniu (`--collect-only`), więc IDE zbierające testy w kopii skonfigurowanej na środowisko docelowe też zostaje zatrzymane. Obejścia nie ma: przebieg krytyczny na środowisku docelowym nigdy nie jest zamierzony. Ograniczeniem zabezpieczenia jest brak wykrywania błędnego adresu lokalnego, który wskazuje serwer docelowy: repozytorium nie może znać adresu docelowego, więc porównać go nie ma z czym. Projekt pilnuje tej reguły testem architektury, który zakłada razem z pierwszym testem krytycznym; szablon go nie zawiera.

## Konfiguracja testów jest lokalna

Plik `conftest.py` leży najbliżej testów, których dotyczy. Fixture potrzebna w jednym katalogu nie trafia do `conftest.py` w korzeniu, bo tam obowiązuje wszędzie i po pół roku nikt nie wie, co ją włączyło ani co się stanie po jej usunięciu.

Fixture podmieniająca cokolwiek globalnego jest zamknięta do swojego katalogu i wycofuje zmianę po sobie.

## Doraźne uruchomienie

Konfiguracja pytesta w `pyproject.toml` ma `addopts = "-ra -q"`. Drugie `-q` podane w wywołaniu sumuje się z tym z konfiguracji do `-qq`, które ukrywa linię podsumowania, więc zielonego przebiegu nie da się odróżnić od pustego. Doraźne przebiegi uruchamiaj z `-o addopts=-ra`, które nadpisuje opcje z konfiguracji.

## Testy obowiązkowe

Specyfikacja produktu wskazana w `CLAUDE.md` nazywa wprost miejsca, w których spodziewa się błędów. Każde z nich ma mieć własny test, nazwany tak, żeby było widać, czego pilnuje. Te testy wynikają z domeny projektu, więc ten standard ich nie wylicza.

Niezależnie od domeny obowiązkowe są testy niżej.

Kod czytający albo zapisujący bazę ma test krytyczny na realnej bazie. Unit i test integracyjny z założenia nie dotykają realnej bazy, więc zapytanie sprawdzone tylko nimi nigdy nie zostało wykonane na serwerze.

Reguła repozytorium, którą da się sprawdzić maszynowo, ma test w `tests/architecture/`, opisany w sekcji Warstwy testów.

Przejście wartości czasu w obie strony. Zapisać wartość z konkretnym przesunięciem strefowym, przeczytać ją i sprawdzić, że przesunięcie jest to samo - nie tylko że moment jest ten sam. Test porównujący same momenty przejdzie także wtedy, gdy warstwa sterownika po cichu znormalizuje wszystko do czasu uniwersalnego, a wtedy reguła zachowania przesunięcia z `standard_time.md` jest niewykonalna, choć nikt tego nie zauważy. Ten test jest pierwszy, przed kodem, który na nim stoi.

Uprawnienia i widoczność, osobno dla listy i dla szczegółu. Macierz po wszystkich rolach, które projekt definiuje, sprawdzająca zarówno to, co wolno, jak i to, czego nie wolno. Sprawdzenie tylko pozytywnej strony przepuszcza najgorszy błąd tej klasy, czyli otwarcie cudzych danych dla wszystkich.

## Zakres pokrycia

Pokrycie nie jest celem samym w sobie, ale poniżej pewnego poziomu przestaje mówić cokolwiek. Cel: każda reguła domenowa ma co najmniej jeden test sprawdzający jej pozytywną stronę i co najmniej jeden sprawdzający, że reguła faktycznie odmawia.

Reguła, której test sprawdza wyłącznie, że działa, gdy wolno, nie jest przetestowana - najdroższe błędy polegają na tym, że coś przeszło, choć nie miało prawa.

Pokrycie nie jest dziś wymuszane automatycznie: repozytorium nie ma progu w konfiguracji ani zewnętrznego przebiegu, który by go pilnował. Egzekwowanie zostaje po stronie człowieka i review - to jest znany dług, zapisany w mapie standardów.

## Czego test nie robi

Test nie powtarza implementacji, żeby sprawdzić, czy implementacja robi to, co robi. Test sprawdzający, że funkcja wywołała inną funkcję, nie mówi nic o poprawności - mówi tylko, że kod jest napisany tak, jak jest napisany.

Test nie zależy od aktualnej daty, chyba że sprawdza właśnie zachowanie zależne od czasu - wtedy czas jest podawany jawnie, nie brany z zegara systemowego.

Test nie zależy od kolejności innych testów ani od stanu pozostawionego przez poprzedni.

## Checklista

- Czy nowa reguła domenowa ma test na stronę pozytywną i na odmowę?
- Czy nowy test leży w warstwie odpowiadającej temu, co faktycznie sprawdza?
- Czy test integracyjny ma znacznik `integration` i nie używa realnej sieci ani bazy?
- Czy test wymagający realnej zależności ma znacznik `critical`?
- Czy kod czytający albo zapisujący bazę ma test krytyczny na realnej bazie?
- Czy reguła repozytorium sprawdzalna maszynowo ma test w `tests/architecture/`, a nie osobne narzędzie z linii poleceń?
- Czy nowa fixture leży najbliżej testów, których dotyczy, i wycofuje po sobie zmiany globalne?
- Czy zmiana w `tests/conftest.py` zachowuje odmowę startu testów krytycznych przy konfiguracji docelowej?
- Czy test krytyczny zasiewający dane trwałym zapisem rejestruje je w fixture sprzątającej przed wywołaniem, a sprzątanie idzie po zarejestrowanych kluczach, nie po wzorcu nazwy?
- Czy zmiana dotykająca zapisu albo odczytu wartości czasu jest pokryta testem sprawdzającym zachowanie przesunięcia, nie tylko momentu?
- Czy zmiana dotykająca uprawnień albo widoczności ma test dla listy i osobny dla szczegółu, po wszystkich rolach, w obie strony?
- Czy test nie sprawdza wyłącznie tego, że jedna funkcja zawołała drugą?
- Czy test nie bierze aktualnej daty z zegara systemowego bez powodu?
