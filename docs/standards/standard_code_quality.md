# Standard jakości kodu

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Kod w tym repozytorium ma być czytelny, bezpieczny w utrzymaniu i możliwy do zweryfikowania automatycznie, zanim człowiek albo agent zacznie go czytać linijka po linijce. Ten standard zbiera wymogi jakości kodu produkcyjnego, które nie mają własnego, dedykowanego standardu: styl komentowania, automatyczne sprawdzanie stylu i formatowania, złożoność funkcji, typowanie statyczne, martwy kod, spójność zależności i wydajność. Bez jednego miejsca opisującego te wymogi każdy reviewer i każdy agent musiałby je odtwarzać z pamięci albo z rozproszonych fragmentów w innych plikach, z ryzykiem, że różne osoby przyjmą różny próg tego, co jest wystarczająco dobre.

## Zakres i granice

Ten standard odpowiada za jakość kodu produkcyjnego niezwiązaną z jego architekturą: styl komentowania i kontrolę treści generowanej przez czata, automatyczne sprawdzanie stylu i formatowania oraz jego zakres, złożoność funkcji, typowanie statyczne, wykrywanie martwego kodu, spójność deklarowanych i faktycznie używanych zależności oraz wymagania wydajnościowe.

Czego tu nie ma:

- Testy - to `standard_tests.md`. Ten dokument nie reguluje niczego, co dotyczy plików w `tests/`.
- Formatowanie kodu jako samodzielny temat: długość linii, znaki zakazane, cudzysłowy, styl zapisu parametrów - to `standard_formatting.md`.
- Statyczna analiza bezpieczeństwa kodu i skan podatności zależności - to `standard_security.md`.
- Architektura ponad pojedynczą jednostką kodu - to `standard_architecture.md`. Wewnętrzna architektura samej warstwy nie ma dziś standardu; powód i warunek powstania są w `docs/standards/README.md`, sekcja granic i długów.
- Dokumentacja modułu - to `standard_documentation.md`.
- Docstringi jako element jakości kodu należą do tego standardu. Struktura osobnego dokumentu opisującego jednostkę kodu - to `standard_documentation.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Dokumentacja

Struktura i treść dokumentacji modułu - patrz `standard_documentation.md`.

## Komentarze w kodzie

Kod nie zawiera linijkowych komentarzy, dopóki nie są naprawdę konieczne. Dwa wyjątki: skomplikowany algorytm, którego nie da się wystarczająco opisać docstringiem, oraz stała konfiguracyjna działająca jak switch - wtedy krótki komentarz linijkowy wskazujący, jakie opcje ten switch może przyjąć, jest dopuszczalny. Poza tymi dwoma wyjątkami dokumentowanie logiki idzie do docstringa, nie do komentarza przy linii - docstring opisuje całość zamiaru funkcji w jednym miejscu, komentarz linijkowy rozjeżdża się z kodem przy pierwszej zmianie w pobliżu, bo nikt o nim nie pamięta przy refaktorze.

Dokumenty, w tym ten, nie nadużywają pogrubień - pogrubienie ma wyróżniać rzeczywiście najważniejszą myśl akapitu, nie każde drugie zdanie.

Znaki zakazane w kodzie i dokumentacji - patrz `standard_formatting.md`.

Kod wygenerowany przez czata (agenta) przechodzi dokładną kontrolę przed przyjęciem: czy nie usunął istniejącej dokumentacji, i czy nie wprowadził regresji w miejscach, których zadanie nie miało dotyczyć. Czat potrafi przy okazji skasować docstring albo test przy niepowiązanej zmianie - taka strata jest łatwa do przeoczenia, bo diff wygląda na spójny z zadaniem, dopóki nikt nie porówna go linia po linii z tym, co było wcześniej.

## Statyczna analiza i formatowanie

Kod musi przechodzić `ruff check` i `ruff format` bez naruszeń przed połączeniem zmiany. Obowiązujący zakres sprawdzania (`select` w `pyproject.toml`) to: `E4`, `E7`, `E9` (błędy składniowe i oczywiste błędy), `F` (Pyflakes - nieużywane importy i zmienne, niezdefiniowane nazwy), `I` (porządek importów), `B` (bugbear - typowe pułapki), `UP` (składnia zgodna z docelową wersją Pythona), `SIM` (uproszczenia), `C4` (comprehensions), `C90` (złożoność cyklomatyczna, próg opisany w sekcji o złożoności kodu), `A` (przesłanianie wbudowanych nazw), `N` (konwencje nazewnicze PEP 8), `RUF` (reguły specyficzne dla ruff), `G` (leniwe placeholdery w wywołaniu loggera zamiast f-stringa albo `.format()`, zgodnie z `standard_logging.md`, sekcja Format treści wpisu). Zmiana tego zakresu w `pyproject.toml` jest zmianą stanu docelowego tego standardu - wymaga świadomej decyzji, nie cichej edycji konfiguracji bez pamięci o tym, że ten standard ją tu wymienia.

Sprawdzanie nie obejmuje plików markdown. Od wersji 0.16 ruff formatuje bloki kodu wewnątrz dokumentacji, a przy włączonym `docstring-code-format` formatowanie kodu przepisywałoby przy okazji przykłady w `docs/`. Wykluczenie stoi w `extend-exclude` i dotyczy wyłącznie dokumentacji - formatowanie przykładów w docstringach samego kodu zostaje włączone. Pliki markdown mają własny formater, prettiera, uruchamiany z tych samych celów `make lint` i `make format` co ruff; reguła i konfiguracja są w `standard_formatting.md`, sekcja Formatowanie markdown.

## Złożoność kodu

Złożoność cyklomatyczna pojedynczej funkcji nie przekracza 15, egzekwowane regułą `C901` w ruff (`[tool.ruff.lint.mccabe]`, `max-complexity = 15`). Próg wynosi 15, a nie 10: przy 10 duża część naruszeń to funkcje z naturalną serią warunków jednego zamierzenia, na przykład normalizacja albo parsowanie wielu wariantów wejścia, gdzie wymuszony podział na mniejsze funkcje rozjeżdża spójną logikę bez poprawy czytelności. Przy 15 próg trafia głównie w funkcje, których rozmiar faktycznie sygnalizuje sklejenie kilku odrębnych odpowiedzialności w jednym miejscu. Funkcja z rozgałęzieniami i pętlami przekraczającymi ten próg jest trudna do ogarnięcia w całości podczas review i trudna do pokrycia testami wyczerpująco - liczba możliwych ścieżek wykonania rośnie z każdym kolejnym warunkiem, a review realistycznie sprawdza tylko część z nich. Przekroczenie progu jest sygnałem do podziału funkcji na mniejsze, nazwane kroki, nie do podniesienia progu dla pojedynczego przypadku.

## Typowanie statyczne

Kod ma adnotacje typów sprawdzane narzędziem mypy w trybie podstawowym, bez `--strict`. Oczywiste niezgodności typów - zły argument, zła wartość zwracana, brak atrybutu - są wyłapywane przed uruchomieniem kodu, bez wymogu pełnego pokrycia adnotacjami każdej linii istniejącego kodu. Brak typowania przenosi wykrywanie takich błędów z etapu review na etap runtime, gdzie koszt naprawy jest wyższy, a błąd może ujawnić się dopiero na produkcji, na konkretnym zestawie danych wejściowych, który akurat trafił na niezgodny typ.

## Martwy kod

Kod nie zawiera funkcji, zmiennych ani importów, które nie są nigdzie używane, wykrywane narzędziem vulture z progiem pewności domyślnym dla tego narzędzia. Skan obejmuje kod produkcyjny razem z testami, bo użycie w teście jest użyciem - skan samego kodu produkcyjnego zgłasza jako martwe rzeczy, które testy wołają, i daje przez to wynik gorszy niż skan szerszy. Nazwy pomijane stoją w `ignore_names` w `pyproject.toml`, każda z zapisanym przy niej powodem; są to wyłącznie nazwy czytane po tekście przez bibliotekę albo framework, których vulture nie ma jak zobaczyć jako użycia. Dopisanie nazwy do tej listy jest zmianą stanu docelowego tego standardu, tak samo jak zmiana zakresu reguł lintera - wymaga świadomej decyzji z powodem, nie cichej edycji konfiguracji. Martwy kod myli czytelnika co do rzeczywistego zachowania modułu - sugeruje ścieżkę wykonania albo zależność, której realnie nie ma, i rośnie w czasie, bo nikt nie ma bodźca, żeby go usunąć, dopóki jawnie nie przeszkadza.

## Spójność zależności

Zależności zadeklarowane w `pyproject.toml` odpowiadają zależnościom faktycznie importowanym w kodzie, wykrywane narzędziem deptry. Nieużywana zadeklarowana zależność zwiększa niepotrzebnie powierzchnię aktualizacji bezpieczeństwa i rozmiar środowiska. Zależność faktycznie importowana, ale niezadeklarowana, działa dziś tylko dzięki przypadkowej obecności w środowisku - na przykład jako zależność przechodnia innego pakietu - i przestaje działać w chwili, gdy ta przypadkowa obecność zniknie.

Ten wymóg jest sprawdzany na poziomie całego repozytorium, nie pojedynczego modułu - zmiana w jednym module może ujawnić rozjazd wprowadzony wcześniej gdzie indziej. Reguła odstępstwa obowiązuje mimo to: naprawie podlega rozjazd wynikający ze zmienianego modułu, nie każdy inny rozjazd zastany w repo przy okazji.

## Wymagania wydajności kodu

### Wydajność interakcji z bazą danych i API

- O(1) lub O(n/batch_size) złożoność dla operacji batchowych.
- O(n) złożoność dla operacji niebatchowych. Większa złożoność wymaga jawnego uzasadnienia w kodzie albo w dokumentacji jednostki kodu.
- Szacowanie czasu wykonania całości i konfrontacja z wymaganiami przed wdrożeniem.

### Profilowanie i pomiar czasu

Podejrzenie regresji wydajności jest sprawdzane profilerem, na przykład `cProfile`, nie optymalizowane na podstawie domysłu, które miejsce w kodzie jest wolne - domysł bez pomiaru regularnie trafia w niewłaściwe miejsce i kończy się optymalizacją fragmentu, który i tak nie był wąskim gardłem.

Kod z twardym wymogiem czasowym, oznaczony testem `critical` (patrz `standard_tests.md`), ma pomiar rzeczywistego czasu wykonania w teście, nie tylko szacowanie na papierze - szacowanie zrobione raz, przy pierwszym wdrożeniu, nie wykrywa późniejszej regresji wprowadzonej przez niepowiązaną zmianę w tym samym module.

## Stosowanie architektonicznych standardów

Styl architektoniczny ponad pojedynczym modułem - helpery wspólne, wrappery do systemów zewnętrznych, loggery, cache, spójność bibliotek - patrz `standard_architecture.md`.

## Checklista

- Czy nowy albo zmieniony kod ma komentarze linijkowe poza dwoma dozwolonymi wyjątkami (skomplikowany algorytm, stała-switch)?
- Czy dokumentacja usunięta albo zmieniona przy okazji niepowiązanej zmiany została zauważona i przywrócona albo świadomie uzasadniona?
- Czy kod przechodzi `ruff check` i `ruff format` bez naruszeń?
- Czy złożoność cyklomatyczna każdej nowej albo zmienionej funkcji mieści się w progu 15 (reguła C901)?
- Czy nowy albo zmieniony kod ma adnotacje typów zgodne z podstawowym trybem mypy?
- Czy zmiana nie wprowadza martwego kodu - nieużywanych funkcji, zmiennych, importów?
- Czy zależności w `pyproject.toml` odpowiadają faktycznie używanym - brak nieużywanych, brak brakujących?
- Czy złożoność operacji batchowych i niebatchowych mieści się w wymogu O(1)/O(n/batch_size)/O(n), z jawnym uzasadnieniem przy przekroczeniu?
- Czy przy podejrzeniu regresji wydajności użyto profilera zamiast optymalizacji na domysł?
- Czy kod z twardym wymogiem czasowym ma pomiar rzeczywistego czasu wykonania w teście `critical`?
