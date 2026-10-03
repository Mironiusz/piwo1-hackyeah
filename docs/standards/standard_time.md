# Standard czasu i stref czasowych

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Serwis przechowuje każdy moment w czasie jako parę kolumn: `timestamptz(3)` z samym instantem oraz `<kolumna>_utc_offset_minutes` z przesunięciem strefowym, jakie obowiązywało w chwili zapisu. Ta para odpowiada na dwa różne pytania - "który to moment" i "jaką godzinę widział człowiek, który to wpisał" - i cała jej wartość zależy od tego, że obie kolumny są zapisywane razem. Zapisana połowa nie jest brakiem danych. Jest wierszem, który wygląda poprawnie, ma prawidłowy instant i renderuje godzinę zegarową, której nigdy nie było.

Drugi powód jest osobny od pierwszego: `timestamptz` nie przechowuje strefy ani przesunięcia. Normalizuje wartość do UTC przy zapisie i renderuje ją w strefie sesji przy odczycie. Kod, który tego nie wie, pisze poprawne zapytania i dostaje wartości zależne od konfiguracji serwera, a nie od danych.

Ten standard rozstrzyga cztery pytania: jaki typ kolumny czasu wybrać dla nowej wartości; co dokładnie oznacza wartość odczytana z pary i jak ją bezpiecznie zapisać; skąd brać "teraz" po stronie bazy i po stronie Pythona; oraz jak liczyć granice doby, gdy doba lokalna nie pokrywa się z dobą UTC.

## Zakres i granice

Ten standard odpowiada za:

- wybór typu kolumny czasu w PostgreSQL dla nowej wartości (`timestamptz` kontra `date`, oraz `timestamp` bez strefy jako typ zamknięty),
- semantykę pary instant plus przesunięcie - co przechowuje, jak to czytać i zapisywać z Pythona przez psycopg,
- konwencję dla wartości "teraz" po obu stronach: `now()` kontra `clock_timestamp()` w SQL, funkcje z jednego miejsca zamiast gołego `datetime.now()` w Pythonie,
- granice doby i miesiąca liczone względem czasu lokalnego w oknach czasowych zapytań i raportów.

Czego tu nie ma:

- Harmonogram uruchomień zadań okresowych, okna uruchomień, blokady i częstotliwość - to jest `standard_worker.md`. Zdanie rozstrzygające: ten standard mówi, co znaczy dana wartość czasu; worker mówi, kiedy zadanie w ogóle wystartuje.
- Limit czasu (timeout) na wywołaniu do bazy albo do systemu zewnętrznego - to jest `standard_errors.md`. To inny sens słowa "czas": tam chodzi o to, jak długo czekać na odpowiedź, tutaj o to, co oznacza wartość daty zapisana w danych.
- Duplikat okienkowy w idempotencji, czyli wyciszanie powtórzonego zdarzenia w krótkim oknie czasu - to jest `standard_idempotency.md`. Tam okno jest mechanizmem wyciszania duplikatu, nie tematem reprezentacji czasu.
- Jeden sposób otwarcia połączenia z bazą i ogólna zasada jednego miejsca definicji wspólnego mechanizmu - to jest `standard_database.md` i `standard_architecture.md`. Ten standard tylko nazywa, jaka opcja strefowa ma być ustawiona na takim połączeniu i dlaczego, nie ustala samej zasady jednego punktu definicji.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Zawężenie właściwe dla tego standardu dotyczy kolumn bazy: każda migracja dodająca albo zmieniająca kolumnę czasu obejmuje również jej kolumnę przesunięcia. Nie da się dodać instanta "na razie bez pary" i wrócić do tego później - wiersze zapisane w tym czasie nie mają skąd odzyskać godziny zegarowej.

## Trzy typy czasu w PostgreSQL i wybór między nimi

- `timestamptz` (`timestamp with time zone`) - jedyny typ dla momentu w czasie. Wbrew nazwie nie przechowuje strefy: przy zapisie przelicza wartość do UTC i zapamiętuje sam instant, przy odczycie renderuje go w strefie sesji. Precyzja to `(3)`, czyli milisekundy, zgodnie z formatem, jaki interfejs programistyczny wystawia na zewnątrz.
- `timestamp` bez strefy - naiwna data i godzina, bez informacji o tym, do jakiego momentu się odnosi. Typ zamknięty dla nowej kolumny. Powód: przy zmianie czasu jedna godzina w roku jest naprawdę dwuznaczna i nic w samej wartości nie mówi, o które z dwóch odczytań chodzi. Ten typ pojawia się wyłącznie jako wynik wyrażenia, nie jako kolumna: `created_at AT TIME ZONE 'Europe/Warsaw'` zwraca właśnie `timestamp` i o to w raportach chodzi.
- `date` - sama data kalendarzowa, bez godziny i bez strefy. Właściwa tam, gdzie wartość naprawdę jest dniem, nie momentem. Wymóg podania przesunięcia na wejściu interfejsu dotyczy momentu, nie daty - rozciągnięcie go na wartość typu `date` zaczyna odrzucać poprawne zgłoszenia.

Do tego jedna domena, wspólna dla całego schematu:

```sql
CREATE DOMAIN utc_offset_minutes AS smallint
    CONSTRAINT CK_utc_offset_minutes_range CHECK (VALUE BETWEEN -840 AND 840);
```

Zakres od `-840` do `840` to pełny zakres rzeczywistych przesunięć UTC, od `-14:00` do `+14:00`. Wartość poza nim nie jest strefą, tylko błędem w tym, co ją policzyło. Domena jest jednym miejscem, które to mówi dla wszystkich par w schemacie, zamiast powtórzonego warunku przy każdej kolumnie.

Wybór dla nowej wartości nie jest więc wyborem między typami - jest wyborem, czy wartość jest momentem, czy dniem. Moment to zawsze para: `timestamptz(3)` plus `utc_offset_minutes`. Dzień to `date` i nic więcej.

## Para instant plus przesunięcie: co przechowuje i dlaczego jest parą

Kolumna `timestamptz` przechowuje moment. Kolumna przesunięcia przechowuje liczbę minut, jaką miało przesunięcie UTC w chwili, w której ten moment został zapisany. Razem odtwarzają godzinę zegarową, którą widział człowiek: `2026-07-14T06:00:00+02:00` w lipcu i `2026-01-14T06:00:00+01:00` w styczniu, mimo że oba instanty są przechowane jako UTC.

Skutek: dwa wiersze tej samej kolumny, zapisane w różnych porach roku, mają różne przesunięcia i to jest poprawne, nie błąd danych.

Dlaczego przesunięcie, a nie nazwa strefy. Interfejs programistyczny dostaje na wejściu offset i tylko offset - `+02:00` to w lipcu Warszawa, Sztokholm, Paryż i kilkanaście innych miejsc. Zapisanie nazwy strefy wymagałoby zgadnięcia faktu, którego wywołujący nigdy nie przesłał, a to jest dokładnie to, czego zabrania `CLAUDE.md`. Tam, gdzie nazwa strefy jest realnym wejściem, na przykład przy wyrażeniu cron, ma ona własną kolumnę.

Porównanie i sortowanie idą po samej kolumnie `timestamptz`. Żaden warunek `WHERE`, żaden indeks i żadne `ORDER BY` w serwisie nie czyta kolumny przesunięcia - jest faktem o renderowaniu, nigdy o filtrowaniu. W szczególności nie wolno grupować raportu po kolumnie przesunięcia: mówi ona, co pokazywał zegar, a nie w jakiej strefie stał.

## Zapis pary: jedna wartość, nie dwie kolumny

Para jest mapowana jako jeden atrybut przez `composite()` w SQLAlchemy. To nie jest wygoda, to jest jedyna rzecz, która czyni zapis połowy pary niemożliwym: skoro nie istnieje atrybut na samo przesunięcie, nie istnieje przypisanie, które zaktualizuje instant i zostawi stare przesunięcie.

Warunek `CK_<tabela>_offset_pairs` w bazie odrzuca parę, w której dokładnie jedna kolumna jest `NULL`. Nie wyłapie natomiast przesunięcia, które zostało z poprzedniego zapisu, bo wtedy żadna z kolumn nie jest `NULL`. Dlatego obrona jest trzystopniowa i każdy stopień pilnuje czegoś innego: `composite()` w modelu nie pozwala napisać takiego kodu, warunek w bazie łapie połowę pary, a okresowe zadanie kontrolne workera przelicza przesunięcia i raportuje wiersze, których żadna używana strefa nie tłumaczy. Trzeci stopień istnieje dla przypadku, w którym ktoś napisze surowy SQL albo migrację obok modelu.

Kod, który zapisuje moment, nigdy nie wylicza przesunięcia z konfiguracji "przy okazji". Dla wartości podanej przez klienta przesunięcie jest tym, co przyszło na wejściu. Dla wartości stemplowanej serwerowo jest przesunięciem strefy biznesowej w tej chwili, a strefa biznesowa pochodzi z konfiguracji, nie z literału w kodzie ani w DDL.

Reguła zdania wyżej nie zna wyjątku dla zapisu, którego nie wywołał człowiek. Zapis z przebiegu okresowego, z synchronizacji z systemem zewnętrznym, z danych rozruchowych i z zapytania testowego stemplowany jest tak samo jak zapis z komendy - przesunięciem strefy biznesowej obowiązującym w chwili zapisu. Zero wpisane wprost, żeby oznaczyć zapis maszynowy, nie oznacza niczego: jest poprawnym przesunięciem czasu uniwersalnego, więc przy odczycie nie da się go odróżnić od wiersza zapisanego naprawdę w takiej strefie. Wyjątek nie byłby więc oznaczeniem, tylko wprowadzeniem wartości nierozpoznawalnej - i to samo dotyczy każdej innej wartości umownej wstawionej w miejsce przesunięcia. Znaczenie tej kolumny jest jedno w całym serwisie, niezależnie od tego, co zapis wywołało.

## Odczyt: sesja przypięta do UTC

psycopg dekoduje `timestamptz` do świadomego `datetime` w strefie sesji, nie w strefie zapisu - bo strefy zapisu w tej kolumnie nie ma. Nieprzypięta sesja oznacza, że wartość po stronie Pythona zależy od `postgresql.conf` serwera, a nie od danych.

Każde połączenie ustawia więc `options=-c timezone=UTC`, w jednym miejscu, tam gdzie połączenie powstaje (`standard_database.md`). Odczytany `datetime` jest wtedy nudno przewidywalny: zawsze świadomy, zawsze w UTC. Godzina zegarowa dla człowieka powstaje z tego instanta i z zapisanego przesunięcia, nigdy z tego, na co akurat ustawiona jest sesja.

To jest pierwsza rzecz do sprawdzenia, gdy znaczniki czasu wracają przesunięte. Test round-trip sprawdza ją wprost, gdy uruchamia odczyt na sesji celowo ustawionej na inną strefę.

## Czas "teraz": po stronie bazy i po stronie Pythona

W SQL są dwie funkcje i różnią się znaczeniem, nie precyzją:

- `now()` zwraca moment rozpoczęcia transakcji i nie zmienia się w jej trakcie. To jest domyślny wybór: wszystkie wiersze zapisane jedną komendą mają ten sam znacznik, a przebieg zadania okresowego ocenia wszystkie wiersze względem jednego momentu, więc "przedawnione na godzinę 03:15:00" jest prawdziwym zdaniem o całej paczce.
- `clock_timestamp()` zwraca realny zegar w chwili wywołania. Właściwa tylko tam, gdzie mierzy się upływ czasu wewnątrz jednej transakcji, na przykład jak długo trwał przebieg zadania.

Pomylenie tych dwóch nie daje błędu, daje pomiar równy zeru albo znacznik, który wygląda dziwnie dopiero w logu.

W Pythonie wartość `datetime.now()` bez podanej strefy jest naiwna i zależy od strefy systemu operacyjnego procesu, który ją wywołał - nie od niczego widocznego w samym kodzie. To samo wywołanie na maszynie z inną strefą systemową daje inny wynik dla tej samej linijki, bez żadnej zmiany w repozytorium.

Rozwiązaniem są dwie funkcje w jednym wspólnym miejscu, zwracające odpowiednio aktualny moment w UTC i aktualny moment w strefie biznesowej, obie jako wartość świadomą. Kod wybiera jedną z nich, dobraną do tego, do czego czas jest potrzebny: wersję UTC dla znacznika technicznego, wersję lokalną tam, gdzie wartość ma sens w odniesieniu do doby albo godziny zegarowej. Nigdy gołego `datetime.now()`.

Naiwny `datetime` docierający do sesji bazy jest błędem, nie danymi, i jest wyłapywany w jednym miejscu: walidator na bazowym modelu Pydantic plus asercja w `before_flush`. Świadomy `datetime` w nieoczekiwanej strefie jest natomiast danymi - klient ma prawo przysłać termin w swojej strefie i serwis ma prawo go tak zapisać.

Biblioteką stref czasowych jest wyłącznie `zoneinfo` ze standardowej biblioteki Pythona, nie `pytz`. `zoneinfo` rozstrzyga czas letni i zimowy z aktualnej bazy IANA systemu, bez własnej, potencjalnie nieaktualnej kopii danych stref. Nazwy stref są po obu stronach te same, bo PostgreSQL również używa nazw IANA - to jedyny powód, dla którego w schemacie i w kodzie nie ma dwóch różnych zapisów tej samej strefy.

## Arytmetyka na momentach

Każde dodawanie i odejmowanie na momencie przechodzi przez UTC: przelicz do UTC, dodaj albo odejmij tam, przelicz z powrotem do strefy biznesowej i wylicz przesunięcie na nowo.

Nie wolno robić arytmetyki na świadomej wartości bezpośrednio. `aware - timedelta` w Pythonie jest arytmetyką na zegarze ściennym i przenosi pierwotne `tzinfo` bez zmian, więc przy `ZoneInfo` potrafi wyprodukować czas lokalny, którego strefa nigdy nie miała, albo taki, którego przesunięcie jest o godzinę nieaktualne. Wtedy błędny jest sam moment, nie tylko sposób jego pokazania - i tylko dla okien przechodzących przez zmianę czasu, czyli dokładnie tak, jak taki błąd przechodzi przez testy.

## Okna czasowe w danych: doba lokalna kontra doba UTC

Doba kalendarzowa strefy biznesowej nie odpowiada dobie UTC - jej granice w UTC przesuwają się o godzinę między czasem letnim i zimowym. Okno filtrujące "dzisiaj", "wczoraj" albo "ostatnie N dni" nie może wyliczyć tych granic jako samych dat zrzutowanych na `00:00`, bo wtedy jest przesunięte o godzinę w jedną albo drugą stronę, zależnie od pory roku, i systematycznie gubi albo dodaje rekordy z granicznej godziny.

Po stronie SQL narzędziem jest `AT TIME ZONE` z nazwą IANA, i wynikiem jest naiwny `timestamp` w tej strefie - właśnie to, po czym się kubełkuje:

```sql
date_trunc('day', created_at AT TIME ZONE 'Europe/Warsaw')
```

Nazwa strefy pochodzi z parametru zapytania albo z konfiguracji, nigdy z literału skopiowanego do każdego raportu. Dla strefy `Europe/Warsaw` różnica między dobą lokalną i dobą UTC to wszystko, co zostało zapisane między północą a drugą w nocy, więc nie jest to zaokrąglenie.

Po stronie Pythona granica okna przechodzi przez świadomy `datetime` w strefie biznesowej i dopiero na końcu jest przeliczana do UTC. Funkcje operujące na samych obiektach `date` wyliczają granice w kalendarzu, nie w konkretnej strefie - są bezpieczne tam, gdzie okno trafia do zapytania po kolumnie `date` bez składnika godziny, albo tam, gdzie okno jest z zamierzenia szerokie i przesunięcie o godzinę nic nie zmienia.

## Wartości UTC jako klucze

Wszędzie tam, gdzie moment jest częścią identyfikatora albo klucza idempotencji, używa się jego reprezentacji w UTC.

Powód jest wprost widoczny przy jesiennej zmianie czasu: lokalna reprezentacja powtórzonej godziny `02:30` daje jeden i ten sam napis dla dwóch różnych momentów, więc dwa osobne rekordy zapadłyby się w jeden. Klucz musi być jednym stabilnym napisem na jedno wystąpienie, a to daje tylko UTC.

## Checklista

- Czy nowa wartość momentu jest parą kolumn: `timestamptz(3)` plus `utc_offset_minutes`, a nie samym `timestamptz`?
- Czy nowa kolumna czasu jest `timestamptz` albo `date`, nigdy `timestamp` bez strefy?
- Czy para jest mapowana jako jeden atrybut przez `composite()`, bez osobnego atrybutu na przesunięcie?
- Czy tabela z nową parą ma warunek `CK_<tabela>_offset_pairs`?
- Czy żaden warunek `WHERE`, indeks ani `ORDER BY` nie czyta kolumny przesunięcia?
- Czy żaden raport nie kubełkuje po kolumnie przesunięcia zamiast po `AT TIME ZONE`?
- Czy przesunięcie wartości podanej przez klienta pochodzi z wejścia, a nie z konfiguracji?
- Czy przesunięcie wartości stemplowanej serwerowo pochodzi ze strefy biznesowej także dla zapisu maszynowego - okresowego, synchronizującego, rozruchowego i testowego?
- Czy połączenie z bazą ustawia `timezone=UTC` w jedynym obowiązującym miejscu?
- Czy wybór między `now()` i `clock_timestamp()` wynika ze znaczenia wartości, a nie z przyzwyczajenia?
- Czy nowy kod używa funkcji "teraz" z jednego wspólnego miejsca, a nie gołego `datetime.now()`?
- Czy nowy kod stref czasowych używa wyłącznie `zoneinfo`, nie wprowadza `pytz`?
- Czy arytmetyka na momencie przechodzi przez UTC, a przesunięcie jest wyliczane po niej na nowo?
- Czy okno filtrujące dobę po kolumnie z godziną wylicza granice w strefie biznesowej, a nie z samej daty kalendarzowej?
- Czy moment użyty jako klucz albo identyfikator jest renderowany w UTC?
