# Standard pisania dokumentacji modułów

Stan dokumentu: 2026-10-03

Status: gotowy - minimalistyczny standard dokumentowania jednostek kodu.

Nota terminologiczna: ten dokument mówi "moduł" na jednostkę kodu, którą dokumentujesz. W profilu Pythona tą jednostką jest warstwa ze `standard_architecture.md` - `api`, `service`, `data` oraz `worker`. Projekt spoza profilu Pythona zapisuje tutaj własną jednostkę kodu. Para dokumentów powstaje więc dla warstwy, nie dla pojedynczego pliku w niej: `MODULE_ALGORITHM.md` opisuje reguły domenowe tej warstwy, `MODULE.md` jej konstrukcję i podział odpowiedzialności między pliki. Słowo "moduł" zostaje w treści niżej, bo opisuje to samo pojęcie, a przepisanie całego dokumentu na "warstwę" zmieniłoby wyłącznie słownictwo.

Warstwa, która nie ma jeszcze ani jednej reguły domenowej, nie dostaje tej pary z góry. Dokument zachowania bez ani jednej reguły do opisania i dokument konstrukcji powtarzający listę plików widoczną z drzewa katalogów są gorsze niż ich brak - wyglądają na wiedzę o warstwie, a niosą jej nazwę. Warunek powstania pary zapisuje się wtedy wprost w pamięci trwałej warstwy (`agent_docs/memory/<warstwa>/_wspolne.md`), i tam do tego czasu mieszkają jej decyzje.

Cel: dokumentacja modułu ma szybko wyjaśniać zachowanie oraz konstrukcję techniczną modułu. Nie ma zastępować czytania kodu, nie ma być runbookiem i nie ma powtarzać tych samych informacji w kilku miejscach.

Formatowanie samej prozy - znaki zakazane, cudzysłów tylko tam, gdzie jest do czegoś potrzebny, oraz zakaz pogrubień w prozie i pogrubionych etykiet otwierających akapit - jest w `standard_formatting.md` i obowiązuje każdy dokument opisany niżej. Szablony sekcji w tym standardzie podają nagłówki, nie pogrubienia: jeśli fragment dokumentacji zasługuje na wyodrębnienie, dostaje nagłówek.

---

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - dokumentacja niezgodna ze standardem blokuje review niezależnie od tego, kto ją pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Ten standard nie ma pozostałych sekcji rdzeniowych (zakresu i granic, checklisty) - to znany dług, zapisany w sekcji granic i długów `docs/standards/README.md`. Reguła odstępstwa musi być w każdym standardzie zbioru, bez wyjątku.

## Ton prozy

Dokumentacja jest kontraktem dla osoby piszącej kod, nie tekstem do czytania dla przyjemności. Proza jest sucha i rzeczowa: zdanie nazywa mechanizm wprost, pełnym zdaniem orzekającym, nie urwanym fragmentem. Bez metafor, zwrotów efekciarskich i puent, które sprzedają treść zamiast ją podawać - efektowna fraza kosztuje czytelnika rundę dekodowania i nie wnosi precyzji. Uzasadnienie zostaje, ale w formie przyczyny technicznej, nie puenty.

Przy przepisywaniu stylu istniejącego dokumentu nie może zginąć żaden fakt. Zbiory identyfikatorów w backtickach, liczb, odwołań do paragrafów i nagłówków porównuje się przed zmianą i po niej.

## 1. Dwa poziomy dokumentacji

Każdy większy moduł powinien mieć dwa pliki dokumentacji:

1. `MODULE_ALGORITHM.md` - opis zachowania modułu i reguł domenowych.
2. `MODULE.md` - opis technicznej konstrukcji modułu i podziału odpowiedzialności.

Najważniejsza zasada:

```text
ALGORITHM.md tłumaczy zachowanie.
MODULE.md tłumaczy konstrukcję.
```

Nie powtarzamy tej samej informacji w obu miejscach. Jeżeli informacja naturalnie należy do jednego poziomu, nie dublujemy jej w drugim.

`MODULE_ALGORITHM.md` powinien przeżyć refactor nazw plików i helperów. `MODULE.md` nie musi, bo jest mapą aktualnej implementacji.

---

## 2. `MODULE_ALGORITHM.md`

### 2.1. Rola dokumentu

`MODULE_ALGORITHM.md` jest dla osoby, która chce zrozumieć, jak moduł działa z punktu widzenia procesu, danych i reguł domenowych.

Czytelnik po tym pliku powinien wiedzieć:

- jakie dane wchodzą do modułu,
- jakie pojęcia domenowe są potrzebne do zrozumienia procesu,
- co po kolei dzieje się z danymi,
- według jakich reguł powstaje wynik,
- co jest odrzucane, pomijane, aktualizowane albo zapisywane,
- jak działa reconcile, idempotencja albo deduplikacja,
- jakie diagnostyki i najważniejsze liczniki summary mogą się pojawić.

Ten dokument nie opisuje struktury plików, listy helperów, importów ani instrukcji rozwoju kodu.

### 2.2. Minimalna struktura

Standardowy `MODULE_ALGORITHM.md` powinien zawierać tylko te sekcje:

```text
# MODULE_NAME_ALGORITHM

Stan dokumentu: YYYY-MM-DD

## Cel algorytmu

## Pojęcia domenowe

## Ogólna mapa procesu

## Szczegółowa kolejność runa

## Reguły domenowe

## Reconcile i deduplikacja

## Diagnostyka i summary
```

Sekcję można pominąć, jeżeli nie ma sensu dla danego modułu. Nie dodajemy dodatkowych sekcji bez uzasadnienia.

### 2.3. Czego nie ma w standardowym `MODULE_ALGORITHM.md`

Domyślnie nie dodajemy sekcji:

- `Zakres dokumentu`,
- `Skutki uboczne`,
- `Własności runa`,
- `Ograniczenia aktualnej wersji`,
- `Przykładowe scenariusze`,
- `Jak testować`,
- `Jak rozwijać`.

Takie informacje można dodać tylko wtedy, gdy moduł bez nich jest realnie niezrozumiały albo użytkownik wyraźnie tego chce. Nie są częścią bazowego template'u.

---

## 3. Sekcje `MODULE_ALGORITHM.md`

### 3.1. Cel algorytmu

Krótko opisz, co moduł robi z danymi i jaki wynik ma powstać.

Dobry poziom:

```text
Algorytm importuje zgłoszenia z formularza WWW i z pliku CSV od partnera, normalizuje je do wspólnego modelu, dzieli na zgłoszenia aktywne, oczekujące na potwierdzenie i odrzucone, a następnie uzgadnia wynik z istniejącym stanem DB.
```

Nie opisuj tutaj plików, klas, helperów ani szczegółów implementacyjnych.

### 3.2. Pojęcia domenowe

Opisz tylko pojęcia potrzebne do czytania algorytmu.

Przykłady:

- provider,
- source file,
- secondary source,
- normalized signup,
- bucket,
- reconcile key,
- conflict alert.

Jeżeli pojęcie nie wraca potem w algorytmie, nie trzeba go opisywać.

### 3.3. Ogólna mapa procesu

To najważniejsza sekcja w `MODULE_ALGORITHM.md`.

`Ogólna mapa procesu` to krótka, semantyczna wersja algorytmu. Nie jest to lista haseł i nie jest to spis nazw funkcji.

Każdy punkt ma opisywać konkretną transformację danych albo decyzję domenową. Punkt może mieć 1-3 zdania, jeżeli jedno zdanie wymusza skrót myślowy.

Dobry punkt powinien mówić przynajmniej część z tych rzeczy:

- jaki zakres danych jest brany,
- według jakiego klucza działa etap,
- jaki warunek decyduje o przejściu dalej,
- co powstaje po etapie,
- co jest traktowane jako kontekst,
- co jest świadomie pomijane,
- jaki stan danych trafia do następnego kroku.

Zły poziom:

```text
1. Pobierz dane.
2. Przygotuj dane.
3. Zgrupuj rekordy.
4. Policz wynik.
5. Zapisz do DB.
```

Dobry poziom:

```text
1. Dla każdego providera wybierz źródła wejściowe, które mają wejść do bieżącego runa. Pliki lokalne są wybierane według okna czasu od ostatniego udanego importu, a źródła bezplikowe są dołączane tylko wtedy, gdy mają kompletną konfigurację.

2. Zamień wszystkie źródła providera na wspólny kontrakt surowego zgłoszenia. Plik i formularz WWW mogą mieć różne formaty wejścia, ale po adapterze mają być porównywalne jako jeden strumień raw records.

3. Znormalizuj raw records do wspólnego modelu zgłoszenia. Na tym etapie powstają ujednolicony adres e-mail, data zgłoszenia, źródło, klasyfikacja bucketu i dane pomocnicze potrzebne do reconcile.
```

Unikaj pustych czasowników i ocen jakościowych bez konkretu:

- pobierz dane,
- przygotuj dane,
- zbuduj okno,
- zgrupuj rekordy,
- policz wynik,
- obsłuż błędy,
- zapisz do DB,
- poprawnie,
- sensownie,
- dobry,
- lepszy,
- odpowiedni.

Można ich użyć tylko wtedy, gdy od razu pada konkret: zakres, klucz, limit, warunek albo skutek.

### 3.4. Szczegółowa kolejność runa

Ta sekcja rozwija ogólną mapę procesu, ale nadal nie powinna być książką.

Dobra forma:

```text
### 1. Dobór źródeł

Opis konkretny, naturalny i domenowy. Wskazuje, które dane wchodzą do etapu, jakie warunki są stosowane i co trafia dalej.

### 2. Normalizacja

Opis konkretny, naturalny i domenowy. Wskazuje, które pola są normalizowane, co jest odrzucane i jaki model danych powstaje.
```

Nie wymuszamy formularza `Wejście / Reguły / Wyjście / Diagnostyka` przy każdym kroku. Taki format można zastosować tylko wtedy, gdy poprawia czytelność.

Krok warto rozbić na mniejsze, jeżeli:

- opis miesza kilka niezależnych reguł,
- etap łączy pobranie danych, decyzję domenową i zapis,
- pojawia się kilka statusów diagnostycznych,
- trudno napisać jednoznaczne wejście i wyjście.

### 3.5. Reguły domenowe

W tej sekcji opisujemy tylko reguły przekrojowe, które są ważniejsze niż sama kolejność runa albo wracają w kilku etapach.

Przykłady reguł:

- klasyfikacja,
- agregacja,
- scoring,
- matching,
- odrzucanie danych,
- diagnostyka,
- przejścia stanu,
- ochrona przed degradacją,
- fallbacki.

Reguła ma być konkretna i weryfikowalna.

Słabo:

```text
Formularz WWW jest lepszym źródłem niż import partnera.
```

Lepiej:

```text
Jeżeli istniejący adres e-mail w bazie pochodzi z formularza WWW, moduł nie nadpisuje go żadnym adresem z importu partnera. Jeżeli istniejący adres pochodzi z importu partnera, wolno go zastąpić tylko adresem z formularza WWW i tylko w skonfigurowanym oknie czasu od zgłoszenia.
```

### 3.6. Reconcile i deduplikacja

Ta sekcja jest obowiązkowa tylko dla modułów, które zapisują trwały stan albo uzgadniają dane z istniejącym stanem.

Opisz:

- klucz albo klucze reconcile,
- kiedy jest insert,
- kiedy jest update,
- kiedy jest skip,
- czy update zmienia pola klucza,
- jak działa batch merge albo deduplikacja, jeżeli istnieje.

Dobry poziom:

```text
Klucz reconcile dla zgłoszeń to `email + data_zgloszenia`.

Brak rekordu w DB oznacza insert. Rekord zgodny po normalizacji oznacza skip. Różnica poza kluczem oznacza update po technicznym id.

Update nie zmienia pól klucza.
```

### 3.7. Diagnostyka i summary

Ta sekcja ma być krótka. Nie robimy z niej runbooka debugowania.

Opisz tylko:

- najważniejsze diagnostyki,
- co trafia do osobnej tabeli albo summary,
- co oznaczają mylące liczniki,
- czy diagnostyka zatrzymuje proces, czy tylko go opisuje.

Dobry poziom:

```text
`rows_loaded` oznacza liczbę zgłoszeń po normalizacji, nie liczbę wierszy pliku wejściowego.

Conflict alert jest diagnostyczny. Trafia do tabeli konfliktów, ale nie zatrzymuje importu i nie zmienia wyniku reconcile.

Źródła bezplikowe, np. formularz WWW, nie zwiększają licznika `files`.
```

---

## 4. `MODULE.md`

### 4.1. Rola dokumentu

`MODULE.md` jest dla osoby, która chce zrozumieć, jak moduł jest zbudowany technicznie.

Czytelnik po tym pliku powinien wiedzieć:

- jaki jest publiczny interfejs,
- co moduł czyta i zapisuje,
- jakie ma tryby pracy,
- jakie pliki istnieją,
- za co odpowiada każdy plik,
- jakie są główne recordy,
- jakie decyzje architektoniczne są ważne.

`MODULE.md` nie jest drugim algorytmem i nie jest instrukcją rozwoju krok po kroku.

### 4.2. Minimalna struktura

Standardowy `MODULE.md` powinien zawierać tylko te sekcje:

```text
# MODULE_NAME

Stan dokumentu: YYYY-MM-DD

## Rola modułu

## Publiczny interfejs

## Wejścia i wyjścia techniczne

## Tryby pracy

## Struktura plików

## Odpowiedzialności plików

## Główne rekordy i kontrakty

## Decyzje architektoniczne

## Summary

## Relacja z MODULE_ALGORITHM.md
```

Sekcję można pominąć, jeżeli nie ma sensu dla danego modułu. Dokument powinien pozostać zwięzły.

### 4.3. Czego nie ma w standardowym `MODULE.md`

Domyślnie nie dodajemy:

- pełnego algorytmu,
- ogólnej mapy procesu,
- diagnostyki outlierów,
- przykładowych scenariuszy,
- ograniczeń aktualnej wersji,
- instrukcji rozwoju,
- runbooka debugowania,
- pełnych pól recordów,
- testowania, chyba że moduł ma nietypowy tryb testowy, który trzeba znać.

---

## 5. Sekcje `MODULE.md`

### 5.1. Rola modułu

W 2-4 zdaniach opisz, gdzie moduł leży w systemie, za co odpowiada i czego nie robi.

Dobry poziom:

```text
`newsletter_import` jest krokiem 1 potoku marketingowego. Importuje zgłoszenia z formularza WWW i z pliku CSV od partnera, normalizuje je do wspólnego modelu i zasila tabele zgłoszeń aktywnych, oczekujących i odrzuconych.

Moduł nie wysyła e-maili powitalnych, nie liczy statystyk kampanii i nie wykonuje segmentacji odbiorców. Te odpowiedzialności należą do późniejszych kroków potoku.
```

### 5.2. Publiczny interfejs

Opisz krótko:

- entrypoint,
- co eksportuje `__init__.py`,
- co zwraca,
- czy przyjmuje `deps`,
- czy istnieją inne publiczne funkcje.

Dobry poziom:

```text
Moduł eksportuje jedynie entrypoint `run_once()`.
```

Jeżeli moduł potrzebuje więcej niż jednego publicznego entrypointu, trzeba opisać dlaczego. Publiczne API nie powinno powstawać przypadkiem.

### 5.3. Wejścia i wyjścia techniczne

Lista technicznych źródeł i targetów.

Dobry poziom:

```text
Wejścia:
- plik CSV partnera,
- formularz WWW,
- import zaległych zgłoszeń,
- reguły walidacji adresów.

Zapis:
- tabela zgłoszeń aktywnych,
- tabela zgłoszeń oczekujących,
- tabela zgłoszeń odrzuconych,
- rejestr plików,
- tabela konfliktów.
```

Tu muszą być pełne nazwy tabel, endpointów i folderów. Nie opisujemy tutaj pełnego procesu domenowego.

### 5.4. Tryby pracy

Opisz tylko realne tryby modułu:

- produkcja,
- shadow,
- file pick mode,
- dry-run, jeżeli istnieje,
- CSV, jeżeli istnieje,
- degraded mode, jeżeli istnieje.

Krótko i konkretnie.

### 5.5. Struktura plików

Pokaż drzewko katalogu modułu.

Nie tłumacz tutaj algorytmu.

### 5.6. Odpowiedzialności plików

To jest główna sekcja `MODULE.md`.

Każdy plik powinien mieć 1-2 zdania opisu.

Dobry poziom:

```text
`newsletter_import_logic.py` - orchestrator jednego runa. Spina providerów, normalizację, reconcile, sinki, statusy plików i cleanup.

`newsletter_import_records.py` - typowany model danych modułu. Trzyma kontrakty raw, normalized, insert/update, existing DB, conflict i summary.

`newsletter_import_helpers_reconcile.py` - czysta domena reconcile. Planuje insert, update i skip na podstawie payloadów oraz gotowego snapshotu existing DB.
```

Nie dodajemy rozbudowanych list `Może` i `Nie może` przy każdym pliku. Wyjątek: miejsce, gdzie ryzyko pomyłki architektonicznej jest duże.

### 5.7. Główne rekordy i kontrakty

Opisz tylko najważniejsze recordy i ich rolę.

Nie opisuj każdego pola.

Dobry poziom:

```text
- `RawSignupRecord` - wspólny kontrakt po adapterach providerów.
- `NormalizedSignupRecord` - zgłoszenie po normalizacji domenowej.
- `ActiveSignupInsertRecord`, `PendingSignupInsertRecord`, `RejectedSignupInsertRecord` - payloady zapisu per bucket.
- `ReconcilePlanRecord` - plan insert/update/skip.
- `SignupRunSummary` - wynik publicznego entrypointu.
```

Dla trudnych modułów można dodać przepływ modeli:

```text
raw source row
  -> RawSignupRecord
  -> NormalizedSignupRecord
  -> insert/update payload
  -> DB
```

### 5.8. Decyzje architektoniczne

Ta sekcja ma być krótka i zawierać tylko decyzje, które wyjaśniają konstrukcję modułu.

Dobry poziom:

```text
- Providerzy mapują źródła do raw kontraktu, ale nie klasyfikują biznesowo bucketu.
- Reconcile jest rozdzielony na czystą domenę i stage I/O.
- Sink wykonuje gotowe decyzje i nie podejmuje reguł domenowych.
- `__init__.py` eksportuje tylko publiczny entrypoint.
```

Jeżeli decyzja jest regułą domenową, jej pełny opis powinien być w `MODULE_ALGORITHM.md`.

### 5.9. Summary

Opisz typ summary i główne grupy liczników.

Pełne znaczenie liczników, jeżeli jest domenowe, powinno trafić do `MODULE_ALGORITHM.md`.

Dobry poziom:

```text
`run_once()` zwraca `SignupRunSummary`, który zawiera `ProviderRunSummary` per provider.

Najważniejsze liczniki:
- `files`,
- `rows_loaded`,
- `inserted_*`,
- `updated_*`,
- `skipped_*`.
```

### 5.10. Relacja z `MODULE_ALGORITHM.md`

Jedno zdanie wystarczy.

Dobry poziom:

```text
Ten dokument opisuje konstrukcję modułu. Zachowanie, reguły domenowe i reconcile są opisane w `MODULE_ALGORITHM.md`.
```

---

## 6. Definition of Done dla dokumentacji modułu

Dokumentację modułu uznajemy za gotową, gdy:

- `MODULE_ALGORITHM.md` opisuje zachowanie bez zależności od struktury plików,
- `MODULE_ALGORITHM.md` ma konkretną ogólną mapę procesu, a nie listę haseł,
- `MODULE_ALGORITHM.md` opisuje szczegółowe kroki, reguły, reconcile, diagnostykę i summary,
- `MODULE.md` opisuje publiczne API, wejścia, wyjścia, tryby pracy i strukturę plików,
- `MODULE.md` jasno pokazuje odpowiedzialności plików,
- `MODULE.md` nie dubluje algorytmu,
- nie ma sprzeczności między kodem, `MODULE.md` i `MODULE_ALGORITHM.md`.
