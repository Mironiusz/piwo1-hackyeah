# Standard logowania

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Bez ustalonej reguły poziom logowania jest wybierany niekonsekwentnie: ten sam rodzaj sytuacji - błąd walidacji danych wejściowych bez żadnego wyjątku i realny, złapany wyjątek - trafia czasem na ten sam poziom `error`, bez rozróżnienia, które z tych dwóch zdarzeń wymaga dalszej uwagi, a które jest normalnym, oczekiwanym odrzuceniem złych danych. Drugi, osobny problem dotyczy samego zapisu wyjątku: w analogicznych blokach obsługi błędu jedno miejsce zapisuje pełny traceback, a sąsiednie tylko treść komunikatu wyjątku jako string - bez żadnej reguły, która z tych dwóch form jest właściwa. Traceback zgubiony w tym momencie nie wraca później; jedyny zapis okoliczności awarii, jaki mielibyśmy szansę mieć, po prostu nie powstał.

Trzeci problem dotyczy treści wpisu, nie jego poziomu czy formy. Identyfikator jednoznacznie wskazujący na konkretną osobę - imię i nazwisko, adres e-mail - trafia do logu zbyt łatwo, bo w momencie pisania kodu wygląda jak zwykłe pole diagnostyczne. "Zaloguję to tylko na debug" nie jest tu ochroną, jeśli debug jest tym, co i tak zbiera środowisko uruchomieniowe. To nie jest teoretyczne ryzyko stylu - to ekspozycja danych osobowych w miejscu, do którego dostęp bywa szerszy niż dostęp do samej bazy, z której te dane pochodzą.

Ten standard rozstrzyga cztery pytania: jaki poziom logowania odpowiada jakiej sytuacji; jak zbudować treść wpisu, żeby była czytelna i przeszukiwalna; jakich danych wpis logu nigdy nie zawiera; i jak zapisać złapany wyjątek, żeby nie zgubić informacji potrzebnej do diagnozy.

## Zakres i granice

Ten standard odpowiada za:

- znaczenie każdego poziomu logowania i sytuację, do której jest zarezerwowany,
- format treści wpisu - sposób budowania komunikatu,
- zawartość wpisu - jakie dane wolno, a jakich nigdy nie wolno w nim umieszczać,
- sposób zapisu złapanego wyjątku, zachowujący informację potrzebną do diagnozy,
- obecność identyfikatora łączącego wpisy jednego przebiegu, gdy dotyczą wielu modułów.

Czego tu nie ma:

- Skąd pochodzi logger i jak skonfigurowany jest centralny mechanizm - handlery, rotacja plików, routing wpisów do plików per grupa modułów, wspólna hierarchia nazw loggerów - to jest `standard_architecture.md`, sekcja Loggery. Zdanie rozstrzygające granicę: architektura mówi, skąd logger pochodzi i dokąd trafia zapisany wpis; logowanie mówi, co i jak w tym wpisie zapisać.
- Decyzja, co się dzieje po błędzie - ponowienie, przerwanie runa, degradacja - to jest `standard_errors.md`. Logowanie mówi jak zapisać, obsługa błędów mówi co zrobić.
- Miejsce przechowywania wartości sterujących logowaniem, takich jak poziom skonfigurowany dla środowiska - to jest `standard_config.md`, w warstwie zmiennych środowiskowych. Ten standard mówi, co znaczy dany poziom i kiedy go użyć, nie gdzie leży jego wartość.
- Generowanie i propagacja identyfikatora przebiegu wewnątrz workera jako mechanizm - to należy do `standard_worker.md`. Tutaj tylko wymóg, że taki identyfikator jest częścią zawartości wpisu.
- Wykrywanie sekretu zaszytego wprost w kodzie źródłowym - to jest `standard_security.md`, statyczna analiza bandit. Ten standard pilnuje innego momentu: żeby sekret będący wartością w czasie działania programu, choćby nigdy nie zapisaną w kodzie jako literał, nie trafił do treści wpisu logu.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Doprecyzowanie właściwe dla tego standardu: obowiązek dostosowania obejmuje każdy wpis logu w module dotkniętym zmianą, niezależnie od tego, czy dokładnie ta funkcja była celem zadania - w szczególności zamianę zapisu wyjątku bez tracebacku na zapis z pełnym tracebackiem, oraz usunięcie albo zamaskowanie danych osobowych z istniejących wpisów logu. Dane osobowe logowane wprost są jedynym miejscem w tym standardzie, gdzie zwykłe odstępstwo "poprawiam przy najbliższym dotknięciu modułu" nie jest wystarczającą odpowiedzią samą z siebie - patrz sekcja Dane w treści wpisu.

## Poziomy logowania

`debug` jest poziomem szczegółu przydatnego przy diagnozowaniu konkretnego przypadku, ale niepotrzebnego do zrozumienia normalnego przebiegu - stan pojedynczego elementu w pętli przetwarzania, wartość pośrednia, decyzja podjęta przez warunek. Wpis na tym poziomie nie jest potrzebny nikomu czytającemu logi w poszukiwaniu ogólnego obrazu tego, co się stało - jest potrzebny tylko wtedy, gdy trzeba zrozumieć, czemu jeden konkretny przypadek zachował się inaczej niż oczekiwano.

`info` jest poziomem checkpointów normalnego przebiegu - start i koniec runa, zbiorcze podsumowanie liczby przetworzonych elementów, potwierdzenie wykonania operacji, która się powiodła. Wpis na tym poziomie nie niesie szczegółu pojedynczego elementu przetwarzania - to jest zadanie poziomu `debug`. Log złożony wyłącznie z wpisów `info` ma dać czytelny, zwięzły ślad tego, co się działo, bez przewijania przez detale, które w normalnym przebiegu nikogo nie interesują.

`warning` jest poziomem degradacji i sytuacji przejściowej, opisanym już w `standard_errors.md`: krok, który wykonał się, ale gorzej niż zwykle, bez przerywania runa. Ten standard nie powtarza tamtej definicji - odsyła do niej jako do jedynego źródła tego, kiedy `warning` jest właściwym poziomem.

`error` jest zarezerwowany dla sytuacji, w której operacja albo krok faktycznie zawiodły - złapany wyjątek albo naruszony warunek, który uniemożliwił dokończenie tej konkretnej pracy. `error` nie jest poziomem dla oczekiwanego, obsłużonego odrzucenia złych danych wejściowych, jeśli to odrzucenie jest normalnym, przewidzianym wynikiem walidacji, a nie awarią - taki wpis, jeśli w ogóle jest potrzebny, należy do `info` albo `warning`, zależnie od tego, czy sam fakt odrzucenia wymaga czyjejś uwagi. Rozróżnienie to nie jest kwestią stylu: poziom `error` używany dla obu sytuacji naraz zabiera przeglądającemu logi możliwość odróżnienia rzeczy wymagającej reakcji od rzeczy, która po prostu się zdarza.

`critical` jest zarezerwowany dla awarii, po której proces albo run nie jest w stanie kontynuować w żadnej formie - nie kolejny krok czy element, ale cały przebieg. To jest węższe znaczenie niż `error`: krok, który zawiódł, ale run mógł przejść do następnego kroku albo zakończyć się z degradacją, jest `error`, nie `critical`. Sytuacja, w której proces kończy się awaryjnie, zanim zrobił cokolwiek pożytecznego, jest `critical`. To rozróżnienie ma sens tylko wtedy, gdy `critical` faktycznie jest używany rzadko i konsekwentnie dla tej węższej sytuacji - poziom używany zamiennie z `error` przestaje nieść dodatkową informację i staje się kolejną nazwą tego samego.

## Format treści wpisu

Komunikat logu jest budowany przez leniwe placeholdery mechanizmu logowania (`logger.info("x=%s", x)`), nigdy przez interpolację do stringa przed wywołaniem (f-string albo `.format()` wklejone w argument komunikatu). Leniwy placeholder odkłada budowę finalnego stringa do chwili, w której wpis faktycznie zostanie zapisany na skonfigurowanym poziomie - komunikat złożony przez f-string jest budowany zawsze, nawet gdy dany poziom jest wyłączony i wpis i tak zostanie odrzucony, co jest zbędnym kosztem powtarzanym przy każdym wywołaniu niezależnie od tego, czy ktokolwiek go zobaczy.

Ta konkretna reguła jest jedyną w tym standardzie sprawdzaną automatycznie: reguła `G` w `ruff check .`, wymieniona w `standard_code_quality.md`, wykrywa f-string i `.format()` przekazane bezpośrednio do wywołania loggera. Reszta tego dokumentu - poziomy, treść danych, zapis wyjątku - zostaje na przeglądzie, bo żadne narzędzie nie odróżnia dziś oczekiwanego odrzucenia złych danych od faktycznej awarii ani nie rozpoznaje identyfikatora wskazującego na konkretną osobę.

Treść komunikatu opisuje operację słowami, a dane zmienne dołącza w postaci `klucz=wartość` przez kolejne placeholdery - na przykład nazwę encji, jej identyfikator i liczbę przetworzonych elementów, każde jako własna para. Ten kształt jest przeszukiwalny: znalezienie w logu wszystkich wpisów dotyczących konkretnego identyfikatora albo operacji nie wymaga parsowania swobodnej prozy, tylko wyszukania nazwy klucza. Wpis złożony z gołej prozy bez wydzielonych par niesie tę samą informację, ale czyni ją nieporównywalnie trudniejszą do odnalezienia w rosnącym pliku logu.

Wpis logu nie jest zrzutem całej struktury danych w jednym argumencie - ani gotowym stringiem JSON wklejonym jako komunikat, ani wynikiem `str()` na złożonym obiekcie. Wyjątkiem jest wpis stworzony jawnie jako dana do maszynowego przetworzenia, nie do czytania przez człowieka - taki wpis jest jawnie oznaczony jako coś innego niż zwykły log narracyjny i nie jest wzorcem do skopiowania przy pisaniu kolejnego, zwykłego wpisu.

## Zapis złapanego wyjątku

Wpis logu tworzony wewnątrz bloku obsługującego złapany wyjątek zapisuje pełny traceback, nie tylko treść komunikatu wyjątku jako string. Mechanizm logowania ma do tego dedykowaną metodę (`logger.exception(...)`, równoważnie `exc_info=True` przy innej metodzie) - jej pominięcie i zapisanie samej treści wyjątku (`logger.error("...: %s", exc)`) zachowuje się z zewnątrz podobnie, ale gubi ślad tego, w którym miejscu kodu i przez jaką ścieżkę wywołań wyjątek faktycznie powstał. Ten ślad nie da się odtworzyć później - jest dostępny wyłącznie w momencie, w którym wyjątek jest jeszcze złapany, i wyłącznie wtedy, gdy zapisujący o niego poprosi.

Zapis bez tracebacku jest dopuszczalny wyłącznie, gdy w danym miejscu nie ma już żywego wyjątku do zapisania - na przykład wpis odtworzony z trwałego licznika prób opisanego w `standard_errors.md`, gdzie zapisywana jest klasa i treść błędu odczytana z bazy, a nie sam obiekt wyjątku z chwili jego wystąpienia. W takim wypadku wpis niesie przynajmniej to, co trwały licznik prób i tak wymaga przechowywać - klasę błędu i jego treść - żeby nie ograniczać się do samego faktu "coś zawiodło" bez żadnego szczegółu.

## Dane w treści wpisu

Sekret - hasło, klucz API, token, connection string - nie trafia do treści wpisu logu w żadnej formie i na żadnym poziomie, niezależnie od tego, czy istnieje w kodzie jako literał, czy tylko przechodzi przez zmienną w czasie działania programu. To dopełnienie reguły z `standard_security.md`: statyczna analiza wykrywa sekret zaszyty w kodzie, ale nie wykrywa sekretu, który nigdy nie był literałem, tylko trafił do treści logu jako wartość runtime - na przykład token odczytany z odpowiedzi systemu zewnętrznego i zapisany do logu przy debugowaniu integracji. Jedyną ochroną przed tym drugim przypadkiem jest ta reguła, egzekwowana przy pisaniu i przy review, nie żadne narzędzie automatyczne.

Identyfikator jednoznacznie wskazujący na konkretną osobę - imię i nazwisko, pełny adres e-mail, numer telefonu, identyfikator zewnętrzny pracownika - nie trafia do treści wpisu logu w pełnej postaci. Gdy log rzeczywiście musi odnosić się do takiego identyfikatora, żeby diagnoza była możliwa, wpis odnosi się do niego przez formę zamaskowaną (na przykład kilka końcowych znaków) albo przez identyfikator wewnętrzny, techniczny (klucz bazy, identyfikator rekordu), nie przez pełną wartość. Zamaskowana forma wystarcza do powiązania wpisu logu z konkretnym, znanym rekordem przez osobę mającą do niego dostęp z innej strony, na przykład z bazy, a jednocześnie nie czyni z samego pliku logu drugiego źródła danych osobowych, z osobnym, słabszym zestawem zabezpieczeń dostępu niż baza, z której te dane pochodzą. Identyfikator konta osoby nadany przez zewnętrznego dostawcę tożsamości, na przykład `sub` z tokenu, jest identyfikatorem zewnętrznym i idzie do logu wyłącznie zamaskowany.

Odpowiedź systemu zewnętrznego, zapisywana do logu przy błędzie integracji, nie jest zapisywana w całości jako nieprzetworzony zrzut ciała odpowiedzi. Treść odpowiedzi systemu, którego nie kontrolujemy, może nieść dowolną zawartość - w tym fragmenty danych osobowych albo treści, które nie powinny trafić do pliku logu tylko dlatego, że akurat znalazły się w odpowiedzi błędu. Wpis niesie kod statusu i świadomie wybrany, ograniczony zestaw pól z odpowiedzi, nie całość.

Ta reguła nie ma tu okresu przejściowego i nie podlega złagodzeniu przy zastanym kodzie, gdy taki się pojawi. Powód: dane osobowe zapisane do logu są ryzykiem czynnym od momentu zapisu, nie kosztem odłożonym na kolejną zmianę, a wpisu logu nie da się wycofać tak jak zmiany w kodzie.

## Kontekst przebiegu

Każde żądanie dostaje w warstwie wejścia identyfikator, sanitowany i dołączany do treści każdego wpisu logu związanego z tym żądaniem, w tej samej parze `klucz=wartość`, o której mówi sekcja Format wyżej. Dzięki temu wszystkie wpisy dotyczące jednego żądania, niezależnie od tego, która warstwa je zapisała, da się odnaleźć jednym wyszukaniem po wspólnej wartości.

Mechanizm stoi w `config/logging.py`, a nie w warstwie wejścia: tam mieszka zmienna kontekstowa z identyfikatorem, filtr wstawiający go do każdego wpisu, para wejść, którą warstwa wejścia tę wartość ustawia i cofa, oraz menedżer zakresu dla miejsc logujących poza kontekstem żądania. To ostatnie nie jest wygodą: obsługę niezłapanego wyjątku framework rejestruje wyżej niż pośrednika nadającego identyfikator, więc wykonuje się ona już po cofnięciu wartości i bez jawnego ustawienia zakresu wpis z tropem wywołań nie dałby się powiązać z odpowiedzią, którą dostał wywołujący. Powód jest architektoniczny - wpis logu z sondy w warstwie danych ma nieść ten sam identyfikator, a ta warstwa nie ma prawa wiedzieć o istnieniu żądania (`standard_architecture.md`, granica warstw). Wartość powstaje w warstwie wejścia: jest przepisywana z nagłówka `X-Request-Id`, gdy wywołujący go podał i gdy przechodzi sanitowanie, a w przeciwnym razie generowana. Wpis spoza żądania - przy starcie procesu i w workerze - dostaje w tym polu znak `-`, żeby format nie przewracał się na nieistniejącym polu.

Sanitowanie znaczy tu konkretną regułę, nie ostrożność ogólną: przepuszczana jest wyłącznie wartość ze znaków alfanumerycznych, myślnika i podkreślenia, nie dłuższa niż 128 znaków. Wartość spoza tego zbioru jest zastępowana wygenerowaną, nie obcinana - nagłówek pochodzi od wywołującego i trafia do każdej linii logu, więc znak nowej linii w nim wstawia do logu wpis wyglądający jak wpis serwisu.

Przebieg zadania okresowego workera, dotykający więcej niż jednej warstwy, ma dostać ten sam rodzaj identyfikatora, dołączany do treści wpisu logu w każdym miejscu, które ten przebieg dotyka - nie tylko tam, gdzie przebieg się zaczyna. Bez wspólnego identyfikatora wpisy dotyczące jednego, konkretnego przebiegu, zapisane przez różne moduły, można powiązać dopiero po fakcie, przez zgadywanie na podstawie zbliżonego czasu zapisu - co w logu obejmującym wiele równoległych albo częstych przebiegów nie jest wiarygodną metodą. Sam mechanizm generowania i propagacji takiego identyfikatora wewnątrz workera jest tematem `standard_worker.md`; ten standard wymaga tylko, żeby taki identyfikator, gdy już istnieje, trafiał do treści wpisu logu.

## Checklista

- Czy poziom `debug` niesie tylko szczegół nieprzydatny do zrozumienia normalnego przebiegu, a nie checkpoint runa?
- Czy poziom `info` niesie checkpointy i podsumowania, nie szczegół pojedynczego elementu przetwarzania?
- Czy poziom `error` jest zarezerwowany dla faktycznej awarii operacji albo kroku, nie dla oczekiwanego, obsłużonego odrzucenia złych danych?
- Czy poziom `critical` jest używany wyłącznie dla awarii uniemożliwiającej kontynuację całego procesu albo runa, nie dla zawodzącego kroku?
- Czy nowy komunikat logu jest budowany przez leniwe placeholdery mechanizmu logowania, nigdy przez f-string albo `.format()` wklejone w argument?
- Czy dane zmienne w komunikacie są dołączone jako pary `klucz=wartość`, a nie jako swobodna proza albo zrzut całej struktury?
- Czy wpis tworzony wewnątrz bloku obsługującego złapany wyjątek zapisuje pełny traceback (`logger.exception` albo `exc_info=True`), nie tylko treść komunikatu wyjątku jako string?
- Czy treść wpisu nie zawiera sekretu - hasła, klucza, tokenu, connection stringa - niezależnie od tego, czy pochodzi z literału czy z wartości runtime?
- Czy treść wpisu nie zawiera identyfikatora jednoznacznie wskazującego na konkretną osobę w pełnej, niezamaskowanej postaci?
- Czy odpowiedź systemu zewnętrznego zapisywana przy błędzie niesie kod statusu i wybrane pola, nie cały nieprzetworzony zrzut ciała odpowiedzi?
- Czy przebieg dotykający więcej niż jednego modułu niesie wspólny identyfikator w treści wpisu logu każdego z tych modułów?
