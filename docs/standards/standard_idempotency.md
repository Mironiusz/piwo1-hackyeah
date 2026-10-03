# Standard idempotencji i uzgadniania danych

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Serwis przyjmuje zapisy, które z natury mogą się powtórzyć: klient ponawia żądanie po błędzie sieciowym, zadanie okresowe workera uruchamia się co minutę i może zostać uruchomione podwójnie, import wsadowy jest odpalany drugi raz po incydencie. Każde z tych powtórzeń ma dać ten sam efekt co pierwsze wykonanie - nie efekt zdublowany.

Ryzyko nie jest teoretyczne i nie mieszka w sieci. Mieszka w technice: sprawdzenie w Pythonie przed zapisem - odczytaj, czy rekord już istnieje, i zdecyduj - jest poprawne w pojedynczym, sekwencyjnym przebiegu i przepuszcza duplikat, gdy dwa przebiegi tej samej operacji trafią na siebie. Bez jednego miejsca, które to nazywa, ta technika wygląda na wystarczającą, bo w testach zawsze jest.

Ten standard rozstrzyga trzy pytania: co czyni dwa wykonania "tą samą operacją"; gdzie żyje ostateczna ochrona przed zdublowaniem efektu; i jak wybrać między dostępnymi technikami zapisu zależnie od charakteru operacji.

## Zakres i granice

Ten standard odpowiada za:

- klucz uzgadniania (reconcile) - co czyni dwa wykonania tą samą logiczną operacją,
- miejsce ostatecznej ochrony przed zdublowaniem efektu,
- wybór techniki zapisu (upsert, dedup) zależnie od charakteru operacji,
- idempotencję wywołania do systemu zewnętrznego, gdy to wywołanie może zostać ponowione.

Czego tu nie ma:

- Dostęp do danych, struktura zapytań i połączenie z bazą - to jest `standard_database.md`. Zdanie rozstrzygające granicę: baza mówi, jak sięgnąć po dane, idempotencja mówi, jak nie zdublować efektu.
- Decyzja, czy i kiedy ponowić operację po błędzie, trwały licznik prób, limity czasu - to jest `standard_errors.md`. Zdanie rozstrzygające: błędy mówią, czy ponowić, idempotencja mówi, że to ponowienie jest bezpieczne, gdy już zapada decyzja o ponowieniu.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Doprecyzowanie właściwe dla tego standardu: nowy mechanizm zapisu, który może zostać wywołany więcej niż raz dla tej samej logicznej operacji - przez retry, drugi przebieg schedulera albo ręczny resend - ma ochronę przed duplikatem od pierwszego dnia. Nie jest dopuszczalne dodanie go "na razie bez dedup, poprawimy po zaobserwowaniu duplikatów na produkcji" - to odwraca kolejność, w jakiej ten problem powinien być rozwiązany.

## Klucz uzgadniania

Klucz, który czyni dwa wykonania tą samą operacją, jest deterministyczną funkcją tożsamości biznesowej tej operacji - nie technicznego identyfikatora przypisanego w chwili wykonania, takiego jak wartość auto-increment albo losowy identyfikator wygenerowany na nowo przy każdej próbie. Dwa niezależne wykonania tej samej logicznej operacji muszą wyliczyć identyczny klucz - w przeciwnym razie "uzgadnianie" nie ma punktu odniesienia i sprowadza się do zgadywania, czy dany zapis już się wydarzył.

Konwencja przyjęta w tym repozytorium: kolumna niosąca taki klucz nazywa się `idempotency_key`, a jej wartość jest skrótem (SHA-256) pól tożsamości biznesowej operacji - typu operacji i identyfikatorów encji, których dotyczy, wraz z każdym innym polem odróżniającym tę operację od innej, logicznie różnej. Zmiana jednego z tych pól jest zmianą tożsamości operacji i ma dać inny klucz; ponowne wykonanie tej samej operacji ma dać ten sam klucz co pierwsze.

Ręczny resend operacji po incydencie może i powinien nosić własny, nowy identyfikator śledzenia próby - żeby odróżnić, która z kilku ręcznych prób to była - ale finalny zapis efektu wciąż przechodzi przez ten sam klucz uzgadniania co automatyczny retry tej samej operacji. Identyfikator śledzenia odpowiada na pytanie "kto i kiedy spróbował"; klucz uzgadniania odpowiada na pytanie "czy efekt tej operacji już istnieje".

## Backstop przed duplikatem

Sprawdzenie w Python przed zapisem - odczytanie, czy rekord już istnieje, i podjęcie na tej podstawie decyzji o wstawieniu albo aktualizacji - jest optymalizacją, nie ochroną. Dwa równoległe przebiegi tej samej operacji mogą oba przejść ten odczyt, zanim któryś zdąży wykonać zapis, i oba dojść do wniosku, że rekordu jeszcze nie ma. Ostateczna ochrona przed zdublowaniem efektu żyje w bazie, jednym z dwóch sposobów:

- unique constraint albo unique index na kluczu uzgadniania - baza sama odrzuca drugi zapis tego samego klucza, a kod łapie ten konflikt i traktuje go jako sygnał "operacja już wykonana", nie jako błąd do zgłoszenia dalej;
- transakcja z blokadą - `SELECT ... FOR UPDATE` na wierszu, który reprezentuje okno, albo blokada doradcza (`pg_advisory_xact_lock`), gdy nie ma jeszcze wiersza do zablokowania - sprawdzająca istnienie i wykonująca zapis atomowo w jednym kroku. Stosowana, gdy sam zapis nie jest permanentnym stanem, tylko oknem czasowym, patrz sekcja niżej.

Kod, który reaguje na konflikt unikalności zamiast propagować go jako nieoczekiwany błąd, robi to poprawnie: taki konflikt nie jest sytuacją opisaną w `standard_errors.md`, jest oczekiwanym, prawidłowym skutkiem współbieżności - backstop właśnie zrobił to, do czego został wprowadzony.

Jak na niego reagować, jest na PostgreSQL rozstrzygnięte, a nie do wyboru. Naruszenie ograniczenia przewraca całą transakcję: sesja wchodzi w stan błędu i żadna kolejna instrukcja w tej transakcji się nie wykona. Przechwycenie wyjątku i kontynuowanie pracy, które na innych silnikach jest poprawnym wzorcem, tutaj wymagałoby `SAVEPOINT` wokół każdego takiego zapisu - wyłącznie po to, żeby utrzymać transakcję przy życiu. Dlatego domyślną formą jest `INSERT ... ON CONFLICT`: konflikt jest wtedy raportowany jako brak wiersza w `RETURNING`, bez wyjątku i bez niczego do wycofania. `ON CONFLICT DO NOTHING` znaczy "już istnieje, nie ruszaj", `ON CONFLICT DO UPDATE` znaczy "nadpisz stan", i oba są jedną instrukcją, której nie da się przegrać wyścigu. Przechwytywanie wyjątku zostaje wyłącznie tam, gdzie konflikt naprawdę jest błędem do zgłoszenia dalej.

## Dwa rodzaje duplikatu

Operacja synchronizacji zwykle chroni się przed duplikatem permanentnym: raz zapisany rekord o danym kluczu biznesowym nie ma powstać drugi raz, niezależnie od tego, ile czasu minęło od pierwszego zapisu. Backstop dla tego rodzaju duplikatu jest twardym unique constraint w bazie.

Powiadomienia i alerty chronią się przed duplikatem innego rodzaju - okienkowym: to samo zdarzenie zgłoszone drugi raz w krótkim oknie czasu jest duplikatem i ma zostać wyciszone, ale to samo zdarzenie zgłoszone po upływie tego okna jest nowym, zasadnym zgłoszeniem, nie duplikatem starego. Twardy unique constraint na kluczu zdarzenia zablokowałby tu każde następne, prawidłowe wystąpienie na zawsze - dlatego backstop dla tego rodzaju duplikatu jest inny: klucz zdarzenia razem z momentem, do którego duplikat ma być wyciszony, sprawdzane i zapisywane atomowo w jednej transakcji z blokadą, nie przez fizyczny constraint na samym kluczu.

Wybór między tymi dwoma rodzajami jest świadomą decyzją przy projektowaniu nowego mechanizmu, rozstrzyganą jednym pytaniem: czy powtórzenie tego samego zdarzenia po dowolnie długim czasie ma nadal liczyć się jako duplikat starego zdarzenia, czy jako nowe, niezależne zdarzenie. Permanentny mechanizm zastosowany tam, gdzie zdarzenie faktycznie się powtarza w czasie, zablokuje każde powtórzenie na zawsze po pierwszym; okienkowy mechanizm zastosowany tam, gdzie duplikat ma być permanentny, przepuści go ponownie po wygaśnięciu okna.

## Wybór techniki zapisu

Właściwa technika zapisu zależy od dwóch cech operacji: jej rozmiaru (pojedynczy rekord kontra batch) i tego, czy istniejący rekord ma być nadpisywany, czy dane są wyłącznie dopisywane, a nowy wpis nigdy nie zmienia poprzedniego.

- Batch, dane tylko dopisywane: jedna instrukcja `INSERT ... ON CONFLICT (klucz) DO NOTHING` na cały batch. Nie ma tabeli tymczasowej i nie ma antyzłączenia - konflikt rozstrzyga indeks unikalny, a nie zapytanie porównujące zbiory, więc nie ma też okna między sprawdzeniem i zapisem.
- Batch, stan nadpisywany: jedna instrukcja `INSERT ... ON CONFLICT (klucz) DO UPDATE SET ...`, a nie dwa kroki, aktualizacja i wstawienie z antyzłączeniem. `ON CONFLICT DO UPDATE` jest jedną instrukcją, więc nie ma dwóch kroków, których kolejność można pomylić.
- Pojedynczy rekord: ta sama instrukcja co wyżej, z `RETURNING`, żeby kod wiedział, czy wstawił, czy trafił na istniejący. Odczyt przed zapisem zostaje tylko wtedy, gdy sam wynik odczytu jest potrzebny do czegoś innego - nigdy jako sposób podjęcia decyzji o zapisie.

Wspólna zasada za tymi trzema: zapis i rozstrzygnięcie konfliktu są jedną instrukcją, a nie sekwencją, w której coś może się wcisnąć. Mechanizm napisany jako odczyt i decyzja dla każdego wiersza z osobna w Pythonie jest jednocześnie wolniejszy i podatny na wyścig - i to drugie jest poważniejsze, bo nie widać go w pomiarze.

## Idempotencja wywołania do systemu zewnętrznego

Wywołanie do systemu zewnętrznego, które może zostać ponowione - przez retry po błędzie sieciowym albo przez ręczny resend - przekazuje stabilny, deterministyczny identyfikator operacji, wyliczony tak samo przy każdej próbie, nigdy generowany na nowo (na przykład jako świeży losowy identyfikator) przy każdym wywołaniu. System zewnętrzny, który rozpoznaje taki identyfikator i sam wykonuje pod nim upsert, a nie tylko tworzenie nowego obiektu, rozpoznaje retry jako powtórzenie tej samej operacji, nie jako nową - efekt po drugiej stronie integracji nie dubluje się, mimo że wywołanie sieciowe faktycznie poszło dwa razy.

Wywołanie bez takiego identyfikatora - które tworzy nowy obiekt po drugiej stronie integracji za każdym razem, niezależnie od tego, czy poprzednia próba już się powiodła - nie ma żadnej ochrony przed zdublowaniem efektu na retry. To rozróżnienie ma praktyczne znaczenie właśnie przy timeoucie: timeout, który nastąpił po tym, jak żądanie dotarło do systemu zewnętrznego i zostało tam wykonane, ale przed odebraniem potwierdzenia przez wywołującego, jest z punktu widzenia wywołującego nie do odróżnienia od timeoutu, który nastąpił, zanim żądanie w ogóle dotarło. Retry po każdym z tych dwóch scenariuszy ma inny, prawidłowy skutek tylko wtedy, gdy identyfikator operacji jest stabilny - w przeciwnym razie pierwszy scenariusz kończy się dwoma obiektami po stronie integracji zamiast jednego.

## Checklista

- Czy klucz uzgadniania jest deterministyczną funkcją tożsamości biznesowej operacji, nie technicznego identyfikatora przypisanego przy wykonaniu?
- Czy dwa niezależne wykonania tej samej logicznej operacji - automatyczny retry, ręczny resend - wyliczają identyczny klucz uzgadniania?
- Czy ostateczna ochrona przed zdublowaniem żyje w bazie (unique constraint albo transakcja z blokadą), a nie tylko w sprawdzeniu wykonanym w Python przed zapisem?
- Czy rozstrzygnięcie konfliktu przechodzi przez `INSERT ... ON CONFLICT`, a nie przez przechwycony wyjątek, który na PostgreSQL przewraca całą transakcję?
- Czy konflikt unikalności jest traktowany jako oczekiwany sygnał "operacja już wykonana", nie jako błąd do zgłoszenia dalej?
- Czy dla duplikatu okienkowego (throttling powtarzających się zdarzeń) sprawdzenie i zapis okna czasu dzieją się atomowo w jednej transakcji z blokadą (`FOR UPDATE` albo blokada doradcza), nie przez twardy constraint, który zablokowałby też prawidłowe powtórzenie po czasie?
- Czy technika zapisu - `ON CONFLICT DO NOTHING` kontra `DO UPDATE` - jest dobrana do tego, czy stan ma być nadpisywany, a nie do przyzwyczajenia autora?
- Czy nowe wywołanie do systemu zewnętrznego, które może zostać ponowione, przekazuje stabilny, deterministyczny identyfikator operacji, nie generowany na nowo przy każdej próbie?
- Czy nowy mechanizm idempotencji ma test sprawdzający, że dwa wykonania z tymi samymi danymi wejściowymi dają jeden efekt, nie dwa?
