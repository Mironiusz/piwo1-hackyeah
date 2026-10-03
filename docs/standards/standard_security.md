# Standard bezpieczeństwa kodu

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Kod serwisu łączy się z bazami danych i z systemami zewnętrznymi oraz przetwarza dane osobowe - błąd bezpieczeństwa w tym miejscu ma inny koszt niż błąd stylu albo wydajności, bo jego skutek może wyjść poza samo repozytorium. Ten standard opisuje wprost, jakiej klasy podatności kod ma unikać i jak sprawdzać, czy zależności zewnętrzne nie niosą znanych luk bezpieczeństwa.

## Zakres i granice

Ten standard odpowiada za statyczną analizę bezpieczeństwa kodu produkcyjnego, za skan zależności projektu pod kątem znanych, publicznie opisanych podatności (CVE) oraz za obchodzenie się z realnymi danymi osobowymi na środowiskach lokalnych.

Czego tu nie ma:

- Higiena zależności - rozjazd między zadeklarowanymi a faktycznie używanymi pakietami, bez związku z bezpieczeństwem - to `standard_code_quality.md`.
- Miejsce i format przechowywania sekretów i konfiguracji modułu - to `standard_config.md`. Tutaj tylko wykrywanie sekretów zaszytych bezpośrednio w kodzie.
- Skan sekretów w historii kontroli wersji - nieobjęty żadnym standardem repozytorium.
- Właściwy sposób pisania zapytania SQL, schemat bazy jako źródło prawdy, migracje i zakaz triggerów - to `standard_database.md`. Tutaj tylko automatyczne wykrycie odstępstwa od parametryzacji.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Skan podatności zależności działa na poziomie całego repozytorium, nie pojedynczego modułu - nowa podatność w istniejącej zależności może ujawnić się bez żadnej zmiany w kodzie, tylko przez publikację nowego CVE. Reguła odstępstwa obowiązuje mimo to w węższym zakresie: zmiana wprowadzająca nową zależność albo podnosząca jej wersję ma obowiązek sprawdzenia tej zależności, nie ponownego audytu całego drzewa zależności przy każdej niepowiązanej zmianie.

## Statyczna analiza bezpieczeństwa kodu

Kod przechodzi statyczną analizę bezpieczeństwa narzędziem bandit bez zgłoszeń o wysokim i średnim poziomie pewności. Bandit wykrywa między innymi: hardkodowane hasła i klucze wpisane wprost do kodu, niebezpieczne wywołania takie jak `eval` albo uruchamianie procesów z `shell=True`, oraz konstrukcje podatne na SQL injection przy budowaniu zapytań przez konkatenację stringów zamiast parametryzacji. Podatność wykryta statycznie i naprawiona przed połączeniem zmiany kosztuje jedno spojrzenie na kod - ta sama podatność znaleziona po wdrożeniu, przez incydent albo audyt zewnętrzny, kosztuje analizę skutków, powiadomienie zainteresowanych stron i naprawę pod presją czasu.

## Skan podatności zależności

Zależności projektu są skanowane narzędziem pip-audit pod kątem znanych, publicznie zgłoszonych podatności (CVE) przed wdrożeniem zmiany wprowadzającej nową zależność albo podnoszącej jej wersję. Zależność z odkrytą podatnością, użyta bez świadomości tego faktu, wprowadza do repozytorium znane, udokumentowane w publicznych bazach ryzyko - różnica względem podatności we własnym kodzie polega na tym, że sposób jej wykorzystania jest już opisany publicznie, więc czas między publikacją CVE a próbą jego wykorzystania bywa krótszy niż czas potrzebny na ręczne zauważenie problemu.

## Realne dane osobowe na środowisku lokalnym

Realne dane osobowe w lokalnej bazie są dozwolone. To jest decyzja, nie przeoczenie: diagnoza zgłoszenia z produkcji na danych zmyślonych bywa diagnozą innego problemu.

Z tej zgody wynika reguła, a nie jej brak: środowisko lokalne przestaje być środowiskiem bez danych osobowych i obowiązują na nim te same zasady, co gdziekolwiek indziej.

Trzy z nich są konkretne i sprawdzalne:

- eksport czegokolwiek z lokalnej bazy poza maszynę jest zakazany. Dotyczy to wklejenia wyniku zapytania do zgłoszenia, do rozmowy z narzędziem agentowym i do dowolnego dokumentu w chmurze. Zrzut schematu bazy jest bezpieczny dlatego, że nie zawiera ani jednego wiersza danych, a nie dlatego, że nikt tam nie zagląda;
- poziom logowania na środowisku lokalnym z realnymi danymi zostaje na `INFO` albo wyżej. `DEBUG` w połączeniu z regułą ze `standard_logging.md` zamienia każde niedopatrzenie w kodzie w ekspozycję danych, a lokalnie nikt tych logów nie rotuje ani nie pilnuje;
- usunięcie tych danych z maszyny ma jedną prostą drogę i trzeba ją znać, zanim będzie potrzebna: reset lokalnej bazy kasuje wolumen razem z zawartością. Robi się to przed oddaniem sprzętu i po skończonej diagnozie, a nie wtedy, gdy ktoś zapyta.

## Checklista

- Czy nowy albo zmieniony kod przechodzi bandit bez zgłoszeń wysokiego i średniego poziomu pewności?
- Czy zapytania do bazy danych są budowane przez parametryzację, nie przez konkatenację stringów z danymi wejściowymi?
- Czy kod nie zawiera hardkodowanych haseł, kluczy ani tokenów?
- Czy nowa albo podniesiona zależność została sprawdzona narzędziem pip-audit pod kątem znanych CVE?
- Czy sekret potrzebny nowemu kodowi trafia do wspólnego miejsca prawdy (`standard_config.md`), a nie jest wpisany wprost w kodzie?
- Czy zmiana nie eksportuje poza maszynę zawartości lokalnej bazy - w zgłoszeniu, w rozmowie z narzędziem agentowym albo w pliku dołączonym do review?
- Czy zmiana dotykająca logowania nie podnosi szczegółowości logu tam, gdzie mogą przechodzić dane osobowe?
