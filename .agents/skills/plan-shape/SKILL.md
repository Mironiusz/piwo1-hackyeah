---
name: plan-shape
description: Zamienia surowe zgłoszenie (seed) w doprecyzowany luźny plan poprzez wywiad z użytkownikiem. Zapisuje seed dosłownie w osobnym, niemodyfikowalnym pliku, potem prowadzi wywiad zapisywany do pliku shape, z sekcjami o problemie, odbiorcy, zakresie, scenariuszach i podważeniu własnych założeń, oraz z otwartymi pytaniami oznaczonymi kategorią ryzyka blokującego. Pierwszy skill łańcucha plan-shape -> plan-prd -> plan-implement. Użyj na początku nowego zadania o nieustalonym kształcie.
---

# Zamiana seeda w luźny plan (shape)

Cel: zbudować `<ZADANIE>_SHAPE.md` na bazie surowego zgłoszenia, prowadząc wywiad, który wyłapuje niejasności zanim powstanie PRD.

## Ustalenie nazwy i wznowienie

Ustal nazwę inicjatywy (katalog w `plans/<INICJATYWA>/`) i prefiks zadania. Jeśli user ich nie podał, zaproponuj oba na podstawie treści wejścia i poczekaj na potwierdzenie - nie twórz niczego na dysku przed potwierdzeniem, bo nazwa jest trwała i widoczna w repo.

Jeśli `plans/<INICJATYWA>/<ZADANIE>_SHAPE.md` już istnieje, to wznowienie: wczytaj shape wraz z seedem i przejdź od razu do sekcji "Prowadź wywiad", pomijając tworzenie plików.

## Archiwum

Zanim założysz nowy katalog, sprawdź obie lokalizacje: `plans/` i archiwum `plans_finished/`. Nazwa obecna w `plans_finished/` oznacza inicjatywę jawnie zakończoną albo anulowaną - nie zakładaj dla niej drugiego seeda ani drugiego prefiksu zadania. Jeśli zgłoszenie jest tą samą pracą, to wznowienie: katalog wraca do `plans/` z wpisem o wznowieniu w review według `docs/standards/standard_agentic_workflow.md` rozdz. 4.6, a wywiad kontynuuje istniejący shape. Jeśli zgłoszenie jest nowym zakresem na ten sam temat, zaproponuj nową nazwę. O tym, która z tych dwóch sytuacji zachodzi, rozstrzyga użytkownik, nie podobieństwo nazw. Ta sama nazwa obecna w obu lokalizacjach naraz jest stanem do wyjaśnienia, nie do wyboru.

## Seed

Sprawdź, czy `<ZADANIE>_SEED.md` już istnieje - user mógł go stworzyć sam, wklejając gotową notatkę zamiast dyktować seed w rozmowie. Nigdy nie nadpisuj istniejącego seeda, tylko go wczytaj.

Wymóg jawnego `Źródło:` dotyczy tylko sytuacji, gdy to `plan-shape` sam tworzy plik na podstawie rozmowy - tam zawsze zapisujesz, skąd wzięło się zgłoszenie. Jeśli plik już istnieje, bo user stworzył go ręcznie, fakt, że to on go napisał, jest wystarczającym źródłem - nie dopytuj o brakującą linię `Źródło:` ani o dokładny nagłówek `## Treść dosłowna`, jeśli treść jest gdzieś w pliku pod inną nazwą sekcji. Jedyny realny wymóg dla ręcznie stworzonego pliku: musi zawierać jakąkolwiek treść. Jeśli plik jest pusty, dopytaj, co user miał na myśli - pustego seeda nie da się przetworzyć.

Jeśli seed nie istnieje, zapisz go jako pierwszą czynność, przed pierwszym pytaniem:

```text
# Seed: <jednozdaniowy tytuł>

Źródło: <rozmowa z użytkownikiem | wklejony mail | notatka ze spotkania | opis z brancha | zgłoszenie od kogoś z zespołu>
Data: YYYY-MM-DD

## Treść dosłowna

<dokładnie to, co zostało powiedziane albo wklejone, bez redakcji i bez interpretacji>
```

Plik nie ma innych sekcji i po zapisaniu jest niemodyfikowalny - zmiana zakresu zawsze idzie do `_SHAPE.md`, nigdy do seeda. Jeśli seed jest zbyt ubogi, żeby cokolwiek z niego wynikało, zapisz go i tak dosłownie, a braki adresuj pytaniami w fazie shape.

## Regulator szczegółowości

Zgłoszenie może nieść parametr sterujący liczbą i głębokością pytań: liczbę od 0 do 100, zapisywaną wzorcowo jako `C:N`. Rozpoznaj każdą formę etykiety, pod jednym warunkiem - bezpośrednio po niej stoi liczba z tego zakresu. Warunek jest konieczny, bo seedy w tym repozytorium bywają pisane ze ścieżkami dyskowymi zaczynającymi się tym samym wzorcem.

Brak parametru w seedzie znaczy 40. Dwie różne wartości w jednym seedzie zatrzymują cię na jednym pytaniu o to, którą przyjąć, zadanym przed pierwszym pytaniem wywiadu - dopóki konflikt trwa, nie wiadomo nawet, jak dociekliwy ma być dalszy ciąg.

Ustaloną wartość wpisz do nagłówka `<ZADANIE>_SHAPE.md` i od tego momentu czytaj ją stamtąd, nie z seeda. Użytkownik może ją zmienić w dowolnym momencie - wtedy zaktualizuj nagłówek i dopisz jedną linię o tym, od którego momentu obowiązuje nowa wartość. Gdy wartość w nagłówku różni się od tej w seedzie, obowiązuje nagłówek i nie jest to powód do pytania.

Pięć progów, po jednym dla przedziału. Każdy zawiera wszystko, co niższe, i dokłada swoje:

- 0-19: wyłącznie pytania blokujące. Wszystko pozostałe rozstrzygasz sam. Zadanie nietykające żadnej kategorii ryzyka może przejść wywiad bez ani jednego pytania.
- 20-39: dodatkowo wybory, których odwrócenie wymagałoby przepisania pracy już wykonanej.
- 40-59: dodatkowo każdy wybór między wariantami o odmiennych konsekwencjach dla zakresu zadania albo dla zadań przyszłych. Rozstrzygasz sam to, co jest konsekwencją decyzji już podjętych. To jest poziom domyślny.
- 60-79: dodatkowo rzeczy, które na progach niższych wyprowadziłbyś jako konsekwencję, oraz granice zakresu, których zgłoszenie nie nazywa wprost.
- 80-100: pytasz o każdą decyzję mającą więcej niż jeden rozsądny wariant. Sam rozstrzygasz wyłącznie to, co ma wariant jeden albo stoi wprost w repozytorium.

Regulator nie sięga blokad na żadnym progu. Dziesięć kategorii ryzyka blokującego i zakaz zgadywania kontraktu obowiązują tak samo przy 0, jak przy 100 - wartość 0 daje wywiad złożony z samych pytań blokujących, nie wywiad pusty.

Regulator nie zmienia też tego, że shape jest nietechniczny. Wysoka wartość podnosi tu głębokość pytań o problem, zakres i reguły, nigdy o rozwiązanie - pytania techniczne należą do fazy B `plan-prd`.

Pozycję, którą rozstrzygnąłeś sam zamiast zapytać, oznacz w dokumencie frazą "Decyzja agenta przy C:N, bez pytania". Bez tego nie widać, co potwierdził człowiek, a co przyjąłeś sam.

Pełna definicja mechanizmu: `docs/standards/standard_agentic_workflow.md` rozdz. 3.5.

## Zanim zapytasz

Przed każdym pytaniem sprawdź, czy odpowiedzi nie ma w repozytorium. Reguła obowiązuje na każdej pozycji regulatora, także przy 100 - regulator steruje wyłącznie tym, co zostaje po odjęciu pytań, na które odpowiedź już jest zapisana. Znalezioną odpowiedź zapisz w shapie wraz ze wskazaniem źródła, zamiast pytać o nią użytkownika.

Znalezienie odpowiedzi nie zamyka tematu, gdy zachodzi jeden z czterech sygnałów. Wtedy pytanie pada mimo znalezienia i mówi wprost, który sygnał je wywołał:

1. Dwa źródła mówią co innego o tej samej rzeczy, w tym różnica między stanem faktycznym a docelowym.
2. Temat jest objęty otwartym wpisem w `docs/standards/decision_registry.md` albo opisany w standardzie o statusie częściowym - reguły tam świadomie nie ma.
3. Odpowiedź stoi wyłącznie w artefakcie zamkniętego zadania w `plans/`, bez potwierdzenia w kodzie, standardzie albo specyfikacji produktu wskazanej w `CLAUDE.md`. Dziennik zadania opisuje stan z momentu pisania, nie stan obowiązujący.
4. Dokument nie był aktualizowany po jawnie wskazanym zdarzeniu, które mogło go unieważnić. Sygnał wymaga konkretnego zdarzenia odniesienia i nie działa jako ogólny termin ważności dokumentu.

## Szkielet `_SHAPE.md`

```text
# Shape: <tytuł zadania>

Stan dokumentu: YYYY-MM-DD, wywiad w toku | wywiad zamknięty
Regulator: C:N

## Problem

## Odbiorca i wyzwalacz

## Stan obecny

## Najmniejszy sensowny zakres

## Poza zakresem

## Wymagania funkcjonalne

## Scenariusze: wejście, przebieg, oczekiwany stan po runie

## Podważenie własnych założeń

## Reguły domenowe albo jawne TODO

## Uwagi o danych, wydajności i bezpieczeństwie

## Otwarte pytania
```

"Odbiorca i wyzwalacz" pyta, kto albo co odbiera efekt zmiany i co go uruchamia: osoba w konkretnej roli, żądanie konsumenta interfejsu programistycznego, zadanie okresowe, inny system czytający wynik. Gdy projekt nie ma interfejsu użytkownika, odbiorcą jest system, a pytanie o personę nie ma odpowiedzi. "Scenariusze" opisują wejście, przebieg i stan po zakończeniu, nie historyjki użytkownika.

Utwórz plik ze szkieletem, wypełniając na starcie tylko to, co wynika bezpośrednio z seeda. Nie wypełniaj sekcji domysłami.

## Prowadź wywiad

Jedno pytanie na raz - AskUserQuestion dla zamkniętych decyzji, zwykły tekst dla pytań otwartych. Ile pytań pada i jak głęboko sięgają, ustala regulator; sposób ich zadawania nie zależy od niego - jedno pytanie na raz obowiązuje na całej skali. Po każdej odpowiedzi dopisz minimalną notatkę do właściwej sekcji, usuń odpowiadający wpis z `## Otwarte pytania` i zapisz plik. Wywiad można przerwać w dowolnym momencie - stan żyje w pliku, nie w rozmowie.

Każde pytanie dotykające jednej z dziesięciu kategorii ryzyka blokującego oznacz `Block: yes` wraz z nazwą kategorii:

```text
1. <pytanie> `Block: yes` (kategoria: <nazwa>)
2. <pytanie> `Block: no`
```

Dziesięć kategorii, pełny opis i sposób weryfikacji każdej w `agent_docs/ai_workflows/shape_prd_workflow.md`: kontrakt tokenu dostępowego i zakresów uprawnień, stabilność kontraktu interfejsu programistycznego, schemat bazy, forma zmiany schematu, źródło prawdy dla danych, semantyka czasu i przesunięcia strefowego, idempotencja i deduplikacja, widoczność odczytu i uprawnienia, dane osobowe, wolumen i koszt zapytania. Pytania blokujące muszą zostać rozstrzygnięte przed przejściem do PRD.

Pytanie o zachowanie w czasie stawiaj na konkretnym przebiegu, nie na nazwach mechanizmów: trzy do sześciu punktów z godzinami i stanem po każdym kroku, a pytanie dopiero pod nimi. Skutek niepożądany podawaj liczbą, nie przymiotnikiem. Gdy pytanie odwołuje się do artefaktu repozytorium, najpierw przytocz jego fragment w rozmowie - sama ścieżka z nazwą sekcji nie wystarcza. Pytanie abstrakcyjne potrafi dostać odpowiedź na pytanie zrozumiane inaczej niż zadane, a ta trafia potem do shape'a jako decyzja, której nikt nie podjął.

Odpowiedź, którą da się sprawdzić odczytem kodu albo danych, sprawdź przed zapisem i pokaż wynik. Odpowiedź niejednoznaczną dopytaj wariantami zamiast wybierać wariant za użytkownika. Odpowiedź właściciela repozytorium na pytanie adresowane do innej roli zapisz z tym zastrzeżeniem - zdejmuje pytanie z listy, nie zastępuje orzeczenia tamtej roli.

Po każdej odpowiedzi, która wycina coś z zakresu, wróć do seeda i sprawdź, czy każda pozycja zamówienia ma jeszcze wykonawcę. Gdy żadna nie ma, przerwij wywiad i powiedz to wprost, zamiast dorabiać inicjatywie zastępczy cel - właściwym wynikiem bywa wtedy wpis do `docs/standards/decision_registry.md` z warunkiem powrotu. Pozycja wyjęta z zakresu znika z listy wymagań i lista zostaje przenumerowana; powód cięcia opisuje sekcja `## Poza zakresem`. Praca, która zmienia wykonawcę albo repozytorium, a nie wypada z zakresu, zostaje na liście.

Gdy w wywiadzie wyjdzie usterka tej samej klasy co zakres (ten sam ekran, ta sama reguła, ten sam przepływ), rekomenduj wciągnięcie jej do zakresu z nazwaniem kosztu. Osobny seed rekomenduj, gdy usterka leży w innym repozytorium albo poza kodem tego projektu.

Wypełnij `## Podważenie własnych założeń` - zapis pytań, które zadałeś sam sobie o własne rozumienie problemu, wraz z tym, co z nich wyszło. Ta sekcja nie może zostać pusta.

## Zakończenie

Zakończ, gdy wszystkie sekcje są wypełnione, a w `## Otwarte pytania` nie ma pozycji z `Block: yes`. Zmień stan dokumentu na "wywiad zamknięty" i powiedz userowi, że można wołać `plan-prd`. Nie wołaj go samodzielnie - każda granica faz jest punktem kontrolnym, w którym user ma zobaczyć wynik i móc zawrócić.

## Zasady

- Zero zgadywania kontraktów, nazw, zakresów - to pytanie do usera, nie decyzja modelu.
- Regulator zmienia liczbę i głębokość pytań, nigdy nietykalność blokad ani obowiązek sprawdzenia repozytorium przed pytaniem.
- Nazwa inicjatywy i prefiks zadania wymagają potwierdzenia usera, zanim cokolwiek powstanie na dysku.
- Dokument nie ma pogrubień w prozie ani pogrubionych etykiet otwierających akapit lub punkt listy - wyróżnia kolejność, nie krój pisma. Patrz `docs/standards/standard_formatting.md`, sekcja o wyróżnieniach w prozie.
