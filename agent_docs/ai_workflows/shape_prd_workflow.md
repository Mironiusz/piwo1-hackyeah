# Workflow: seed -> shape -> PRD -> plan

Ten dokument opisuje metodologię łańcucha realizowanego przez skille `plan-shape`, `plan-prd` i `plan-implement`. Używaj go razem z `AGENTS.md` / `CLAUDE.md` - nie zastępuje reguł repozytorium, tylko je uzupełnia o proces prowadzący od surowego zgłoszenia do zaimplementowanej zmiany.

Wzorzec ma dziesięć kategorii ryzyka blokującego dobranych dla serwisu z bazą danych i interfejsem programistycznym, odbiorcę zmiany zamiast persony i seed jako osobny, niemodyfikowalny artefakt zamiast sekcji wewnątrz notatek. Projekt o innym profilu ryzyka zmienia listę kategorii jednocześnie w trzech miejscach: tutaj, w skillu `plan-shape` i w `docs/standards/standard_agentic_workflow.md` rozdz. 3.3.

## Sekwencja

```
plan-shape   <opis zadania albo wskazanie na gotowy plik seeda>
plan-prd     <ZADANIE>_SHAPE.md
plan-implement  <ZADANIE>_PLAN.md
```

Każde wywołanie jest ręczne. Skill kończy pracę, mówi wprost co powstało i co można zawołać dalej, ale nie uruchamia następnego skilla sam - każda granica faz jest punktem kontrolnym, w którym można zobaczyć wynik i zawrócić.

## Artefakty

Jeden generyczny łańcuch skilli obsługuje dowolne zadanie poprzez parametr - prefiks nazwy zadania i nazwę inicjatywy (katalog w `plans/`). Nie tworzymy osobnego skilla per zadanie.

Pięć plików, każdy z jednym dozwolonym rodzajem treści - pełne szablony sekcji są wpisane bezpośrednio w skille `plan-shape` i `plan-prd`. Domyślnie płasko w `plans/<INICJATYWA>/`; gdy inicjatywa niesie więcej niż jedno zadanie, dopuszczalny jest podkatalog per zadanie, `plans/<INICJATYWA>/<ZADANIE>/` - szczegóły i przykład w `docs/standards/standard_agentic_workflow.md`, sekcja 3.2:

- `<ZADANIE>_SEED.md` - surowe zgłoszenie, niemodyfikowalne po zapisaniu.
- `<ZADANIE>_SHAPE.md` - luźny plan z wywiadem doprecyzowującym.
- `<ZADANIE>_PRD.md` - co ma się stać i dlaczego.
- `<ZADANIE>_PLAN.md` - jak to zrobić technicznie.
- `<ZADANIE>_REVIEW.md` - stan i przebieg zadania, nie trwała pamięć.

## Archiwizacja i wznowienie

`plans/` trzyma wyłącznie inicjatywy w toku. Inicjatywa jawnie zakończona albo jawnie anulowana przechodzi w całości, pod tą samą nazwą i z podkatalogami zadań, do `plans_finished/<INICJATYWA>/`. Dowodem jest końcowy werdykt `ready` obejmujący cały zakres inicjatywy albo inne jawne zamknięcie zapisane w jej review - komplet plików, zamknięty wywiad, zamknięty plan, rozliczenie jednego zadania z kilku, werdykt dla części prac ani wiek katalogu nim nie są. Przy jednoznacznym dowodzie agent przenosi katalog sam (w łańcuchu robi to `plan-implement` po powrocie z review); przy sprzecznym albo niejednoznacznym stanie pyta użytkownika i zostawia katalog na miejscu. Przeniesienie nie zmienia seedów, dawnych wpisów review i memory ani zamrożonych materiałów - aktualizuje tylko edytowalne odwołania i pilnuje, żeby narzędzia czytające pliki inicjatywy dalej działały.

Wznowienie tej samej pracy to powrót katalogu z `plans_finished/` do `plans/` z dopisanym do review wpisem o wznowieniu; sam odczyt archiwum niczego nie wznawia, a nowy zakres dostaje nową inicjatywę. Zanim założysz nowy katalog, sprawdź obie lokalizacje - nazwa obecna w archiwum oznacza wznowienie, nie drugi seed. Pełna reguła wraz z uzasadnieniami: `docs/standards/standard_agentic_workflow.md` rozdz. 4.6.

## Seed

Zawsze zapisuj dosłowną treść zgłoszenia i jawne źródło pochodzenia: rozmowa z użytkownikiem, wklejony mail, notatka ze spotkania, opis z brancha, zgłoszenie od kogoś z zespołu. Użytkownik może stworzyć plik seeda sam, zamiast dyktować go w rozmowie - `plan-shape` nigdy nie nadpisuje istniejącego seeda, tylko go wczytuje.

Jeśli seed jest zbyt ubogi, żeby cokolwiek z niego wynikało, zapisz go i tak dosłownie, a braki adresuj pytaniami w fazie shape. Seed nie jest miejscem na domysły agenta - to zapis tego, co faktycznie zostało powiedziane, nic więcej.

## Kategorie ryzyka blokującego

Pytanie w fazie shape dotykające jednej z tych kategorii musi być oznaczone `Block: yes` i wstrzymuje przejście do PRD, dopóki nie zostanie rozstrzygnięte:

1. Kontrakt tokenu dostępowego i zakresów uprawnień - czy zawartość tokenu, sposób rozwiązania go na aktora i zakresy uprawnień są ustalone z wystawcą tokenu i z konsumentami interfejsu, a nie założone.
2. Stabilność kontraktu interfejsu programistycznego - czy zmiana dotyka kształtu żądania, odpowiedzi, ścieżki albo semantyki pola, którego używa konsument spoza tego repozytorium.
3. Schemat bazy - czy tabela, kolumna, widok albo typ istnieją. Weryfikacja: zrzut schematu dla stanu faktycznego, specyfikacja produktu dla docelowego.
4. Forma zmiany schematu - blokada obowiązuje przy każdej zmianie schematu. Weryfikacja: czy zmiana idzie formą opisaną w `docs/standards/standard_database.md`, czyli rewizją Alembica z surowym SQL-em.
5. Źródło prawdy dla danych - gdy ta sama informacja jest w kilku miejscach i nie wiadomo, które jest autorytatywne. Zawsze pytanie do użytkownika, nie do rozstrzygnięcia czytaniem kodu.
6. Semantyka czasu i przesunięcia strefowego - czy zapis albo odczyt wartości czasu może zmienić jej przesunięcie.
7. Idempotencja i deduplikacja - czy zmiana może dać podwójny zapis, zgubić rekord przy ponowieniu albo dotyka klucza uzgadniania.
8. Widoczność odczytu i uprawnienia - czy zmiana dotyka tego, kto co może przeczytać albo zrobić.
9. Dane osobowe - imiona i nazwiska, dane kontaktowe oraz każda informacja o działaniach albo ocenie konkretnej osoby. Dotyczy też logów i raportów.
10. Wolumen i koszt zapytania - gdy nie da się oszacować liczby wierszy albo zmiana leży na ścieżce odczytu wykonywanego przy każdym wyświetleniu listy.

## Regulator szczegółowości

Zgłoszenie może nieść parametr sterujący liczbą i głębokością pytań: liczbę od 0 do 100, zapisywaną wzorcowo jako `C:N`. Rozpoznawana jest każda forma etykiety, pod warunkiem że bezpośrednio po niej stoi liczba z tego zakresu - inaczej ścieżka dyskowa Windowsa byłaby czytana jako parametr. Dwa różne wystąpienia w jednym seedzie zatrzymują agenta na pytaniu o to, którą wartość przyjąć, zadanym przed pierwszym pytaniem wywiadu.

Wartość podaje się w seedzie, a obowiązuje z nagłówka `<ZADANIE>_SHAPE.md`, gdzie `plan-shape` wpisuje ją jako linię `Regulator: C:N`. Pozostałe skille czytają ją wyłącznie stamtąd. Brak parametru znaczy 40. Wartość wolno zmienić w trakcie zadania - wtedy nagłówek niesie nową, a dokument jedną linię o momencie zmiany.

Pięć progów, każdy zawiera wszystko, co niższy:

1. 0-19 - wyłącznie pytania blokujące, wszystko pozostałe rozstrzyga agent.
2. 20-39 - dodatkowo wybory, których odwrócenie wymagałoby przepisania pracy już wykonanej.
3. 40-59 - dodatkowo każdy wybór o odmiennych konsekwencjach dla zakresu albo dla zadań przyszłych. Poziom domyślny.
4. 60-79 - dodatkowo to, co niżej byłoby wyprowadzone jako konsekwencja, oraz granice zakresu nienazwane wprost w zgłoszeniu.
5. 80-100 - pytanie o każdą decyzję mającą więcej niż jeden rozsądny wariant.

Blokady są nietykalne na całej skali: dziesięć kategorii wyżej i zakaz zgadywania kontraktu obowiązują tak samo przy 0, jak przy 100. Pytania techniczne padają wyłącznie w fazie B `plan-prd`, niezależnie od wartości.

Przed każdym pytaniem agent sprawdza, czy odpowiedzi nie ma w repozytorium - obowiązek niezależny od regulatora, działający także przy 100. Pytanie o rzecz znalezioną pada tylko przy jednym z czterech sygnałów i mówi wprost, który to sygnał:

1. Dwa źródła mówią co innego o tej samej rzeczy, w tym różnica między stanem faktycznym a docelowym.
2. Temat objęty otwartym wpisem w `docs/standards/decision_registry.md` albo opisany w standardzie o statusie częściowym.
3. Odpowiedź wyłącznie w artefakcie zamkniętego zadania w `plans/`, bez potwierdzenia w kodzie, standardzie albo specyfikacji produktu.
4. Dokument nieaktualizowany po jawnie wskazanym zdarzeniu, które mogło go unieważnić. Wymaga konkretnego zdarzenia odniesienia, nie działa jako ogólny termin ważności.

Pozycja rozstrzygnięta przez agenta zamiast zapytania niesie frazę "Decyzja agenta przy C:N, bez pytania".

Pełna definicja mechanizmu: `docs/standards/standard_agentic_workflow.md` rozdz. 3.5.

## Czarna lista treści w PRD

PRD odpowiada na "co i dlaczego", nigdy na "jak". Zakazane: modele danych, listy kolumn, migracje, ścieżki plików kodu, nazwy funkcji, decyzje o bibliotekach, szczegóły deploymentu, sekrety i credentiale. Jeśli podczas pisania PRD pojawia się chęć zapisania rozwiązania technicznego, ten materiał należy do planu implementacji, nie do PRD.

## Podważenie własnych założeń

Faza shape wymaga sekcji, w której agent zapisuje pytania, jakie zadał sam sobie o własne rozumienie problemu, wraz z tym, co z nich wyszło. Ta sekcja nie może być pusta - jeśli nic nie budzi wątpliwości, problem nie został jeszcze zrozumiany.

## Odbiorca zamiast persony

Zamiast pytać o personę i jej dostęp, faza shape pyta o odbiorcę zmiany i jej wyzwalacz: osobę w konkretnej roli, żądanie konsumenta interfejsu programistycznego, zadanie okresowe, inny system czytający wynik. Gdy projekt nie ma interfejsu użytkownika, odbiorcą jest system, a pytanie o personę nie ma odpowiedzi.
