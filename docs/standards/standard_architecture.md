# Standard architektury systemu

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Kod, który nie należy do jednej konkretnej jednostki - bo jest wspólną infrastrukturą albo mechanizmem przecinającym wiele miejsc naraz - nie ma naturalnego właściciela, więc decyzje o nim zapadają osobno i po cichu się rozjeżdżają. Ten standard daje im wspólny punkt odniesienia.

Drugi powód dotyczy reguł przekrojowych, czyli wołanych z wielu miejsc, takich jak uprawnienia i widoczność odczytu. Reguła wołana z wielu miejsc ma jedno źródło, bo dwie kopie rozjeżdżają się po cichu: zawodzi bez błędu, gdy ktoś odtworzy jej warunek w endpoincie zamiast ją wywołać. Ten standard stawia dla nich regułę, zanim powstanie pierwszy endpoint.

## Zakres i granice

Ten standard odpowiada za styl architektoniczny ponad pojedynczą jednostką kodu: granicę warstw serwisu, jedno miejsce dla reguł przekrojowych, helpery wspólne, loggery, cache, spójność bibliotek i wywołania systemów zewnętrznych.

Czego tu nie ma:

- wewnętrzna architektura pojedynczej warstwy, czyli podział odpowiedzialności między pliki w jej katalogu - zbiór standardów nie ma osobnego dokumentu na ten temat;
- format, poziomy i treść wpisu logu - to `standard_logging.md`, tutaj tylko to, skąd logger pochodzi;
- co się dzieje po błędzie - to `standard_errors.md`;
- miejsce i format konfiguracji - to `standard_config.md`, tutaj tylko wymóg jednego miejsca prawdy;
- kto konkretnie ma jakie uprawnienia - to przesądza specyfikacja produktu wskazana w `CLAUDE.md`, tutaj tylko reguła, gdzie ta wiedza mieszka.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Granica warstw

Serwis ma trzy warstwy o rozdzielnych odpowiedzialnościach.

Warstwa wejścia przyjmuje żądanie: waliduje jego kształt, ustala, kto działa, i tłumaczy wynik na odpowiedź. Nie zawiera reguł domenowych. Endpoint, który sprawdza warunek domenowy samodzielnie, jest naruszeniem tej granicy - nawet gdy warunek jest jednolinijkowy, bo jednolinijkowy warunek jest dokładnie tym, co ktoś skopiuje do drugiego endpointu, gdy będzie potrzebny drugi raz.

Warstwa reguł decyduje, co wolno i co się stanie. Tu mieszkają wszystkie warunki przejść stanu, uprawnienia i walidacja domenowa. Ta warstwa nie wie, że została zawołana z żądania - to samo wywołanie musi być poprawne z zadania okresowego workera.

Warstwa danych zapisuje i czyta. Nie podejmuje decyzji o tym, czy zapis wolno wykonać.

Kierunek zależności jest jednostronny: wejście woła reguły, reguły wołają dane. Warstwa danych nie wie o istnieniu warstwy wejścia.

## Jedno miejsce dla reguł przekrojowych

Reguła przekrojowa, czyli wołana z wielu miejsc - na przykład matryca uprawnień albo predykat widoczności odczytu - żyje w jednym module i jest wołana, nigdy odtwarzana.

Reguła wołana z wielu miejsc ma jedno źródło, bo dwie kopie rozjeżdżają się po cichu. Zmianę łatwo wprowadzić w jednym miejscu i nie wprowadzić w drugim - a wtedy oba zachowania współistnieją, w zależności od tego, którym wywołaniem się trafi. Warunek liczony w dwóch miejscach z dwóch różnych zestawów danych rozjedzie się przy pierwszej zmianie reguły.

Konsekwencja praktyczna: zapytanie listujące i zapytanie po szczegół używają tego samego predykatu widoczności, nie dwóch podobnych. Jeśli różnią się z powodów wydajnościowych, ta różnica jest jawna, opisana i pokryta testem po obu stronach.

## Helpery wspólne

Kod infrastrukturalny używany w więcej niż jednym miejscu - dostęp do bazy, budowanie konfiguracji, wspólne klienty - ma jedno miejsce definicji, z którego wszyscy korzystają. Nie kopiuje się jego logiki, nawet w drobnej, ulepszonej wersji. Gdy ten sam mechanizm istnieje w dwóch miejscach, poprawka w jednym nie dotrze do drugiego, a użytkownicy tego samego mechanizmu zaczynają się po cichu różnić - do dnia, w którym zawiedzie akurat ta nieaktualizowana kopia.

Gdy wspólny helper już istnieje, korzystanie z niego jest obowiązkowe. Ręczne odtworzenie jego logiki niżej poziomu - przez wywołanie surowego mechanizmu biblioteki - jest dopuszczalne wyłącznie wtedy, gdy helper faktycznie nie pokrywa danego przypadku, nigdy z wygody. Częściowe odtworzenie, bez jednego z zabezpieczeń helpera, tworzy cichy wyjątek od reguły obowiązującej wszędzie indziej.

Sekrety i dane konfiguracyjne mają jedno miejsce prawdy - patrz `standard_config.md`.

## Loggery

Repozytorium ma jeden centralny mechanizm dostarczania loggera, wspólny dla wszystkich warstw i obu punktów wejścia procesu. Żadne miejsce nie konfiguruje własnego, równoległego mechanizmu logowania obok centralnego - własnego handlera ani własnego globalnego wywołania konfiguracji. Równoległy mechanizm oznacza, że te logi trafiają gdzie indziej niż reszta, a przy diagnozowaniu awarii brakuje właśnie tej jednej, nieprzewidywalnie milczącej części obrazu.

Logger pochodzi zawsze z tego mechanizmu, z nazwą w jednej wspólnej hierarchii, której korzeniem jest nazwa projektu. Logger spoza tej hierarchii nie dziedziczy centralnej konfiguracji, nawet działając w tym samym procesie.

Świadomy fallback na wypadek pracy poza pełnym środowiskiem aplikacji jest dopuszczalny, ale musi być jawny i wąski - ograniczony do sytuacji braku dostępności centralnego mechanizmu, nie do każdego możliwego błędu importu.

## Cache

Każdy cache współdzielony między wywołaniami ma jawną strategię unieważniania: czas życia, porównanie ze źródłem albo jawne wywołanie unieważniające. Brak jakiejkolwiek strategii jest dopuszczalny wyłącznie wtedy, gdy dane źródłowe faktycznie nie zmieniają się w czasie życia procesu - a to założenie musi być zapisane, nie domyślne. Cache bez unieważniania nie psuje się głośno: system działa dalej, tylko coraz bardziej rozjeżdża się z rzeczywistością, a objaw pojawia się daleko od przyczyny.

Cache nigdy nie przechowuje wyniku nieudanej próby jako wartości do zwrócenia. Zapamiętany błąd zamienia jednorazową awarię źródła w trwałą awarię funkcjonalności aż do restartu procesu - dokładne przeciwieństwo tego, po co cache istnieje.

Zasięg życia cache jest świadomym wyborem dopasowanym do tego, jak dane są współdzielone, nie skutkiem tego, gdzie wygodnie było umieścić zmienną. Zbyt szeroki przecieka nieaktualne dane między niezależnymi jednostkami pracy; zbyt wąski tylko przenosi koszt na bazę, którą miał odciążyć.

## Spójność bibliotek

Dla danego rodzaju problemu - dostęp do bazy, obsługa czasu i stref, walidacja i reprezentacja danych, komunikacja z systemem zewnętrznym, ponawianie operacji - repozytorium utrzymuje jedno narzędzie. Nie wprowadza się drugiego, równoległego sposobu rozwiązania tego samego problemu bez jawnej, udokumentowanej decyzji o migracji. Dwa narzędzia do jednego problemu oznaczają, że każda przyszła poprawka i każda aktualizacja bezpieczeństwa musi być rozważona dwa razy, a zwykle wykonuje się ją raz - tam, gdzie ktoś akurat pracuje.

Stos jest przesądzony w specyfikacji produktu wskazanej w `CLAUDE.md` i to on jest punktem odniesienia dla tej reguły. Nowa biblioteka wchodzi do repozytorium świadomie, nie dlatego że była pod ręką.

Gdy repozytorium ma już bibliotekę pokrywającą dany problem, nowy kod korzysta z niej, zamiast pisać własną, równoległą implementację tej samej logiki. Ręczne przepisanie logiki, którą biblioteka rozwiązuje poprawnie razem z przypadkami brzegowymi łatwymi do przeoczenia, wprowadza ryzyko błędu, który w bibliotece został dawno znaleziony i naprawiony.

## Wywołania systemów zewnętrznych

Każda zależność zewnętrzna serwisu - obca usługa, obca baza, wystawca tokenów, współdzielony zasób plikowy, kanał alertu - jest nazwana i ma jedno miejsce wywołania w warstwie danych. Reguły korzystające z odczytu systemu zewnętrznego wołają jeden szew w warstwie reguł, który odpowiada za ten odczyt, nie moduł warstwy danych wprost.

Każdą integrację wychodzącą obowiązują trzy wymogi: jawnie zdecydowana i udokumentowana strategia ponawiania, własne nazwane wyjątki zamiast surowych wyjątków biblioteki transportowej oraz jeden sposób czytania konfiguracji. Brak ponawiania jest dopuszczalną strategią, jeśli jest zapisany razem z powodem - na przykład integracja wołana z przebiegu bez nadzoru nie ponawia w obrębie wywołania, bo ponowieniem jest następny przebieg.

Odczyt systemu zewnętrznego wolno wykonać wyłącznie z przebiegu bez nadzoru albo z administracyjnego wymuszenia tej samej pracy, nigdy z obsługi żądania, bo czas odpowiedzi serwisu zależałby wtedy od cudzej usługi. Wyjątkiem jest wywołanie, bez którego żądania nie da się obsłużyć w ogóle, na przykład pobranie kluczy publicznych do sprawdzenia tokenu wołającego. Taki wyjątek jest jawny i ograniczony: nie ponawia w obrębie wywołania, bo niedostępność kończy żądanie odmową, którą wołający sam ponawia; ma jawny limit czasu; jego koszt ogranicza cache z jawnym czasem życia, który nie zapamiętuje nieudanego pobrania; a wywołanie blokujące idzie z obsługi żądania przez pulę wątków.

Zdarzenie wysyłane do systemu zewnętrznego w następstwie komendy zapisuje się w transakcji tej komendy, a transport wykonuje wyłącznie worker, bez otwartej transakcji bazy podczas oczekiwania na odpowiedź. Transport ma jedno miejsce w warstwie danych, a reguły treści zdarzenia, klasyfikacji odpowiedzi i ponawiania mają jedno miejsce w warstwie reguł.

## Checklista

- Czy zmiana nie przenosi reguły domenowej do warstwy wejścia?
- Czy kierunek zależności między warstwami pozostaje jednostronny?
- Czy zmiana woła regułę przekrojową, na przykład matrycę uprawnień albo predykat widoczności, zamiast odtwarzać jej warunek na miejscu?
- Czy zapytanie listujące i zapytanie po szczegół używają tego samego predykatu widoczności?
- Czy nowy kod infrastrukturalny trafia do jednego wspólnego miejsca, zamiast do kolejnej kopii?
- Czy zmiana nie omija istniejącego wspólnego helpera bez jawnego, uzasadnionego powodu?
- Czy logger pochodzi z centralnego mechanizmu i ze wspólnej hierarchii projektu?
- Czy zmiana nie wprowadza równoległego mechanizmu logowania obok centralnego?
- Czy każdy nowy cache ma jawną strategię unieważniania, nie przechowuje błędu jako wyniku i ma świadomie dobrany zasięg?
- Czy zmiana nie wprowadza drugiej biblioteki do problemu, który repozytorium już rozwiązuje inną?
- Czy nowa integracja wychodząca ma jawną strategię ponawiania, własne wyjątki i jeden sposób czytania konfiguracji?
- Czy odczyt systemu zewnętrznego nie stoi na ścieżce obsługi żądania, a jeśli stoi, to czy jest jawnym wyjątkiem z limitem czasu, bez ponawiania i z cache, który nie pamięta porażki?
- Czy zdarzenie do systemu zewnętrznego jest zapisane w transakcji komendy, a transport idzie z workera bez otwartej transakcji bazy?
