# Standard obsługi błędów

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Błąd bez ustalonej reakcji dostaje reakcję przypadkową - taką, jaka wyszła autorowi w tym jednym miejscu. Skutek jest widoczny dopiero z dystansu: część kodu przerywa całą operację przy błędzie jednego rekordu, część połyka błąd i idzie dalej z niekompletnym wynikiem, a nikt nie umie powiedzieć, która reakcja jest tutaj poprawna, bo nigdzie nie jest zapisane, jak się to rozstrzyga.

Serwis z osobnym procesem workera ma dodatkowy powód: ten sam błąd znaczy dwie różne rzeczy w zależności od tego, co go wywołało. Odmowa uprawnienia w trakcie obsługi żądania jest poprawną odpowiedzią dla wołającego. Ta sama odmowa w zadaniu okresowym workera jest sygnałem, że dane są w stanie, którego nikt nie przewidział - i nie ma komu jej zwrócić.

## Zakres i granice

Ten standard odpowiada za: klasyfikację błędu, reakcję w dwóch kontekstach uruchomienia, mapowanie błędu domenowego na odpowiedź interfejsu programistycznego, trwały licznik prób i limity czasu.

Czego tu nie ma:

- format zapisu błędu w logu i pytanie, czy zapisać tracebackiem - to `standard_logging.md`;
- czy ponowienie zdubluje efekt - to `standard_idempotency.md`; ten standard mówi, czy ponawiać, tamten, czy ponowienie jest bezpieczne;
- strategia ponawiania pojedynczego wywołania systemu zewnętrznego - to `standard_architecture.md`;
- konkretne kody i treści odpowiedzi interfejsu programistycznego - przesądza je specyfikacja produktu wskazana w `CLAUDE.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Trzy klasy błędu

Błąd wołającego. Żądanie jest niepoprawne albo niedozwolone: brakujące pole, zły format, brak uprawnienia, próba przejścia stanu, którego reguły nie pozwalają. To nie jest awaria - to normalna, przewidziana odpowiedź. Nie loguje się go jako błędu aplikacji i nie ponawia.

Błąd przejściowy. Zerwane połączenie, zakleszczenie transakcji, chwilowa niedostępność zasobu plikowego. Ta sama operacja powtórzona za moment ma sensowną szansę się udać. Wolno ponawiać, pod warunkiem że ponowienie jest bezpieczne wg `standard_idempotency.md`.

Błąd trwały. Stan, którego kod nie przewidział: naruszony niezmiennik, dane w kształcie niemożliwym wg reguł, brakująca konfiguracja. Ponawianie nie ma sensu, bo powtórzy dokładnie ten sam wynik. Wymaga zapisania i zgłoszenia, nie ukrycia.

Klasyfikacja jest decyzją autora kodu, nie skutkiem typu wyjątku, który akurat poleciał. Ten sam wyjątek biblioteki może być przejściowy albo trwały w zależności od tego, co go wywołało.

## Reakcja przy obsłudze żądania

Jedno żądanie to jedna transakcja i jeden wynik. Nie ma tu reakcji częściowej: operacja albo się wykonała w całości, albo nie zmieniła nic.

Błąd wołającego zamienia się na odpowiedź opisującą, co jest nie tak, w kształcie ustalonym przez specyfikację. Odpowiedź nie zawiera treści wyjątku, nazwy tabeli, fragmentu zapytania ani connection stringa - to nie jest ostrożność teoretyczna, bo dokładnie tymi kanałami wycieka najwięcej informacji o wnętrzu systemu.

Błąd przejściowy w obsłudze żądania nie jest ponawiany w nieskończoność ani przez czas dłuższy niż wołający jest w stanie czekać. Konflikt równoczesnej modyfikacji tego samego rekordu jest szczególnym przypadkiem: wraca on do wołającego jako informacja o nieaktualnym stanie, a nie jest po cichu nadpisywany ponowną próbą. Cicha ponowna próba po takim konflikcie kasuje zmianę, której nikt nie widział.

Błąd trwały to odpowiedź o awarii, wpis w logu z pełnym kontekstem i nic więcej. Nie próbuje się ratować operacji zgadywaniem, czego wołający mógł chcieć.

## Reakcja w zadaniu okresowym

Zadanie okresowe nie ma komu zwrócić błędu, więc jego reakcja jest inna: liczy się to, żeby jeden zepsuty rekord nie zablokował pozostałych, i żeby fakt pominięcia nie zniknął.

Trzy dopuszczalne reakcje, wybierane świadomie:

- kontynuacja - błąd dotyczy jednego elementu, pozostałe są niezależne, więc element zostaje pominięty i zapisany jako pominięty. Przebieg kończy się wynikiem mówiącym, ile elementów przeszło i ile nie;
- przerwanie - błąd podważa sens całego przebiegu (brak konfiguracji, niedostępna baza), więc przebieg kończy się bez dalszych prób;
- degradacja - część pracy wykonuje się w węższym zakresie, jawnie zapisanym w logu. Dopuszczalna tylko wtedy, gdy węższy zakres jest sam w sobie poprawnym stanem, nie połowicznym.

Kontynuacja bez zapisu pominięcia nie jest kontynuacją, tylko cichym gubieniem pracy. Przebieg, który pominął połowę elementów i zakończył się jako udany, jest gorszy od przebiegu, który się wywalił - bo nikt się nie dowie.

Zadanie okresowe, które ma alertować o naruszeniu, zgłasza to wspólnym kanałem alertu operacyjnego. Log zostaje przy tym zawsze, bo alert może nie dolecieć - a nieudane dostarczenie ma być zapisane jako nieudane, w szczegółach przebiegu i w logu. Udawać, że powiadomienie dotarło, nie wolno w żadnym z tych dwóch miejsc.

Awaria całego przebiegu jest podłączona do tego samego kanału z obwódki wspólnej dla całego rejestru zadań okresowych, więc każde zadanie okresowe alertuje o niej niezależnie od tego, czy jego własna praca cokolwiek zgłasza. Dołożenie kolejnej pozycji rejestru nie wymaga dopisania alertu w jej pracy, a alert reguły jakościowej zostaje decyzją tej pracy. Powód alertu wchodzi do klucza deduplikacji, więc alert jakościowy nie wycisza awarii tego samego zadania w tym samym oknie deduplikacji.

## Trwały licznik prób

Element, który zawodzi powtarzalnie, nie może być ponawiany bez końca przy każdym przebiegu - bo zajmuje czas kolejnym i zaśmieca log tym samym błędem. Element ponawiany między przebiegami ma trwały licznik prób o pięciu składnikach: liczba prób, klasa błędu, treść błędu, moment pierwszego wystąpienia i moment ostatniego.

Próg, po którym element przestaje być ponawiany, jest ustalany per klasa błędu, nie jedną wartością dla wszystkiego: błąd przejściowy zasługuje na więcej prób niż trwały, który nie zasługuje na żadną. Element odstawiony po przekroczeniu progu nie jest usuwany ani ukrywany - zostaje widoczny wraz z powodem, bo cały sens licznika polega na tym, żeby ktoś mógł to zobaczyć i zdecydować.

## Limity czasu

Każde wywołanie, które czeka na coś poza procesem - baza, zasób plikowy, usługa - ma jawny limit czasu. Brak limitu nie oznacza, że nic się nie stanie; oznacza, że w razie problemu proces będzie czekał, aż ktoś go zabije, trzymając przy tym zajęte zasoby, których nie zwolni.

Wartość limitu jest świadoma i wynika z tego, ile wołający może czekać, nie z domyślnej wartości biblioteki. Zadanie okresowe ma limit czasu całego przebiegu, żeby jeden zawieszony przebieg nie zablokował następnego.

## Checklista

- Czy każdy nowy blok obsługi wyjątku ma świadomie przypisaną klasę błędu, a nie reakcję wynikającą z typu wyjątku, który akurat poleciał?
- Czy błąd wołającego nie jest logowany jako awaria aplikacji i nie jest ponawiany?
- Czy treść odpowiedzi nie zawiera wyjątku, fragmentu zapytania, nazwy obiektu bazy ani connection stringa?
- Czy konflikt równoczesnej modyfikacji wraca do wołającego, a nie jest po cichu nadpisywany ponowną próbą?
- Czy każda reakcja w zadaniu okresowym jest jedną z trzech dopuszczalnych i wybrana świadomie?
- Czy pominięty element jest zapisany jako pominięty, a przebieg raportuje liczbę elementów przetworzonych i pominiętych?
- Czy element ponawiany między przebiegami ma trwały licznik prób z pięcioma składnikami i próg per klasa błędu?
- Czy element odstawiony po przekroczeniu progu pozostaje widoczny wraz z powodem?
- Czy każde wywołanie czekające na coś poza procesem ma jawny limit czasu, dobrany świadomie?
- Czy nowe zadanie okresowe ma limit czasu całego przebiegu?
