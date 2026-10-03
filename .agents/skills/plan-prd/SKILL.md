---
name: plan-prd
description: Zamienia gotowy luźny plan (shape) w PRD, a potem w plan implementacji, w dwóch rozdzielonych fazach z bramką potwierdzenia między nimi. PRD odpowiada na co i dlaczego bez decyzji technicznych, plan implementacji na jak, ze zweryfikowanymi faktami z kodu i bazy. Drugi skill łańcucha plan-shape -> plan-prd -> plan-implement. Użyj po zamknięciu wywiadu w plan-shape, na pliku `_SHAPE.md`.
---

# Od shape do PRD i planu implementacji

Cel: dokończyć łańcuch `plan-shape -> plan-prd -> plan-implement`, produkując `_PRD.md` i `_PLAN.md` w dwóch wyraźnie rozdzielonych fazach. Rozdział jest konieczny, bo PRD ma zakaz treści technicznych, a plan implementacji jej wymaga - mieszanie obu w jednym przebiegu prowadzi do przedwczesnego zamrożenia decyzji technicznych.

## Wznowienie

Prefiks zadania i nazwę inicjatywy odczytaj ze ścieżki pliku, na którym jesteś wołany - nigdy nie wymyślaj własnych. Jeśli `_PRD.md` już istnieje, ale `_PLAN.md` nie, to wznowienie: przejdź od razu do fazy B. Jeśli oba istnieją, zapytaj usera, co ma się zmienić, zamiast zaczynać od zera.

## Archiwum

Plik pod `plans_finished/` należy do inicjatywy jawnie zakończonej albo anulowanej. Nie pisz PRD ani planu w archiwum: praca nad taką inicjatywą zaczyna się od jej wznowienia, czyli powrotu całego katalogu do `plans/` na polecenie usera, według `docs/standards/standard_agentic_workflow.md` rozdz. 4.6. Sam odczyt archiwalnego shape'a albo pytanie o dawny wynik nie jest wznowieniem.

## Regulator szczegółowości

Wartość regulatora odczytaj z nagłówka `<ZADANIE>_SHAPE.md`, nigdy z seeda. Brak nagłówka z wartością znaczy 40.

W fazie A regulator nie zmienia niczego poza głębokością pytań o zakres i reguły domenowe - PRD i tak nie rozstrzyga rozwiązań technicznych, a bramka potwierdzenia przed fazą B obowiązuje na każdej pozycji skali.

W fazie B regulator steruje tym, ile decyzji technicznych podejmujesz sam, a ile stawiasz użytkownikowi:

- 0-19: wyłącznie pytania blokujące. Wszystkie decyzje techniczne podejmujesz sam i zapisujesz w `## Decyzje` wraz z powodem.
- 20-39: dodatkowo wybory, których odwrócenie wymagałoby przepisania pracy już wykonanej.
- 40-59: dodatkowo każdy wybór o odmiennych konsekwencjach dla zakresu albo dla zadań przyszłych. To jest poziom domyślny.
- 60-79: dodatkowo kierunek rozwiązania tam, gdzie istnieje więcej niż jedno sensowne podejście, nawet jeśli jedno z nich wyraźnie przeważa.
- 80-100: pytasz o każdą decyzję mającą więcej niż jeden rozsądny wariant, łącznie z kolejnością kroków, granicami zmiany i sposobem weryfikacji.

Blokady i zakaz zgadywania kontraktu stoją poza zasięgiem regulatora na każdym progu. Obowiązek sprawdzenia w kodzie, bazie i dokumentacji wszystkiego, co PRD zakłada, także - regulator nie zwalnia z kroku 5, tylko z pytania o to, co ten krok już ustalił.

Decyzję podjętą samodzielnie zamiast zapytania oznacz w `## Decyzje` frazą "Decyzja agenta przy C:N, bez pytania".

Pełna definicja mechanizmu: `docs/standards/standard_agentic_workflow.md` rozdz. 3.5.

## Faza A: PRD

1. Wczytaj `<ZADANIE>_SHAPE.md` oraz `<ZADANIE>_SEED.md`.
2. Przerwij, jeśli shape ma nierozstrzygnięte pytania `Block: yes`. Nie próbuj ich rozstrzygać domysłem - zadaj je userowi i dopisz odpowiedzi do shape'a, potem wróć.
3. Napisz `<ZADANIE>_PRD.md` wg szablonu:

```text
# PRD: <tytuł zadania>

Stan dokumentu: YYYY-MM-DD

## Cel biznesowy

## Problem i jego skutki

## Zakres

## Poza zakresem

## Wymagania funkcjonalne

## Kryteria akceptacji

## Reguły domenowe

## Zależności i wpływ na inne moduły

## Ryzyka i uwagi
```

Twarda czarna lista treści zakazanych w PRD: modele danych, listy kolumn, migracje, ścieżki plików kodu, nazwy funkcji, decyzje o bibliotekach, szczegóły deploymentu, sekrety i credentiale. PRD odpowiada na "co i dlaczego", nigdy na "jak". Jeśli podczas pisania PRD pojawia się chęć zapisania rozwiązania technicznego, ten materiał należy do `_PLAN.md`, nie tutaj.

4. Pokaż userowi, co powstało, i zapytaj o potwierdzenie przed przejściem do fazy B. To jedyna bramka między "co" i "jak", więc nie przechodź jej milcząco.

## Faza B: plan implementacji

5. Otwórz dokumenty wskazane przez mapowanie zadanie -> dokument w `AGENTS.md` / `CLAUDE.md` dla tego typu zadania. Zweryfikuj w kodzie, bazie i dokumentacji wszystko, co PRD zakłada, i zapisz ustalenia w sekcji `## Fakty` w formacie opisanym w `docs/standards/standard_agent_docs.md`, sekcja Format PLAN: identyfikator, twierdzenie, dowód jednego z pięciu rodzajów i data sprawdzenia. Nie powtarzaj tu wzorca - standard jest jego jedynym adresem, a kontrola automatyczna czyta go stamtąd.
6. Wylicz promień rażenia zmiany, zanim spiszesz zakres zmian: wszystkie miejsca wywołań, obiekty schematu bazy, klucze konfiguracji i kontrole automatyczne, których planowana zmiana dotyka pośrednio. Wyprowadź tę listę z odczytów z kroku 5, nie ze zgadywania. Jeśli wychodzi poza zakres uzgodniony w PRD, zatrzymaj się i zapytaj usera o podział planu, zamiast rozszerzać zakres po cichu. To zatrzymanie jest czym innym niż powrót z kroku 8: tam PRD okazało się błędne, tu PRD może być poprawne, a jedynie za wąskie.
7. Napisz `<ZADANIE>_PLAN.md` wg szablonu:

```text
# Plan: <tytuł zadania>

Stan dokumentu: YYYY-MM-DD, plan w toku

## Cel

## Fakty

## Decyzje

## Zakres zmian

## Kolejność wdrożenia

## Definition of Done

## Ryzyka

## Otwarte pytania

## Pliki uzupełniające
```

Każdy krok w `## Zakres zmian` musi mieć konkretne nazwy plików, funkcji i kontraktów danych, a nie opis w stylu "coś w rodzaju".

8. Jeśli weryfikacja z kroku 5 obali założenie z PRD, zatrzymaj się i wróć do fazy A. PRD jest kontraktem, więc nie wolno go cicho obejść w planie.
9. Zakończ, gdy plan spełnia kryteria kompletności, których `plan-implement` i tak będzie wymagał: zero TODO, zero pozycji w `## Otwarte pytania`, każdy krok z jednoznacznym wejściem i wyjściem. Zmień wtedy marker w linii stanu na `plan zamknięty` - dopiero on wciąga dokument pod kontrolę formatu ustaleń, więc plan pisany na raty zostaje przy `plan w toku` do samego końca. Powiedz userowi, że można wołać `plan-implement`. Nie wołaj go samodzielnie.

## Zasady

- Zero zgadywania kontraktów, nazw, zakresów - to pytanie do usera, nie decyzja modelu.
- Faza A i faza B są rozdzielone bramką potwierdzenia - nigdy nie przechodź z PRD do planu bez pokazania PRD userowi.
- Pytania do usera stawiaj tak samo jak w `plan-shape`: zachowanie w czasie na konkretnym przebiegu z godzinami i stanem po każdym kroku, skutek liczbą, a artefakt, o który pytasz, przytoczony fragmentem, nie samą ścieżką.
- Wymaganie wyjęte z zakresu znika z listy wymagań i lista zostaje przenumerowana, a powód cięcia trafia do `## Poza zakresem`. Pozycja oznaczona adnotacją "poza zakresem" zostawiona na liście przy każdym czytaniu wymaga rozstrzygania, czy się liczy.
- Człowiekowi przypisuj w planie wyłącznie kroki, których agent wykonać nie może albo nie powinien: instalację aplikacji, zmianę ustawień systemu, commit, push, Merge Request, operację na bazie współdzielonej i zgody wymagane regułami bezpieczeństwa. Resztę wykonuje agent. Kroki człowieka zbierz w jednej zwięzłej liście na końcu `## Kolejność wdrożenia`.
- Oba dokumenty nie mają pogrubień w prozie ani pogrubionych etykiet otwierających akapit lub punkt listy - wyróżnia kolejność, nie krój pisma. Patrz `docs/standards/standard_formatting.md`, sekcja o wyróżnieniach w prozie. Identyfikatory faktów, decyzji i wymagań w rodzaju F-1, D-1, WF-1 zostają zwykłym tekstem, bo służą do odsyłania, nie do wyróżniania.
