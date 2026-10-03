# Rejestr decyzji odroczonych

Stan dokumentu: 2026-10-03

## Po co ten dokument

Ten plik zbiera decyzje, o których wiadomo, że muszą zostać podjęte, ale które świadomie zostały odłożone - bo brakuje pomiaru, bo zależą od kontraktu z kimś z zewnątrz, albo bo ich moment jeszcze nie nadszedł. Bez takiego miejsca decyzja odroczona w rozmowie ginie razem z rozmową, a wraca dopiero jako niespodzianka w trakcie implementacji, kiedy jest już najdroższa.

To nie jest standard i nie ma sekcji rdzeniowych. Jest rejestrem, tak jak `naming_registry.md` - opisuje stan faktyczny procesu decyzyjnego, nie stan docelowy repozytorium.

Granica wobec sąsiadów: `docs/standards/README.md` w sekcji granic i długów opisuje decyzje już podjęte i dług już zastany w zamkniętych inicjatywach - patrzy w przeszłość. Ten plik patrzy w przyszłość. Artefakt `<ZADANIE>_REVIEW.md` w `plans/` notuje, na co agent trafił w jednym zadaniu; jeśli z takiego znaleziska wynika decyzja przekraczająca to zadanie, jej miejsce jest tutaj.

## Jak się tego używa

Wpis powstaje w momencie, w którym ktoś stwierdza, że decyzji nie da się dziś podjąć odpowiedzialnie. Zawiera zawsze cztery rzeczy: na co ta decyzja wpływa, jakie są warianty, co blokuje rozstrzygnięcie i po czym poznamy, że można je podjąć.

Wpis znika z listy otwartych dopiero wtedy, gdy decyzja wylądowała w miejscu, gdzie jej szukają - we właściwym standardzie, w specyfikacji produktu albo w kodzie. Wtedy przenosi się do sekcji rozstrzygniętych z jednym zdaniem o tym, jak wypadła i gdzie teraz żyje. Sam wpis tutaj nigdy nie jest źródłem prawdy dla reguły - jest wyłącznie zapisem, że reguły jeszcze nie ma.

Odroczenie musi mieć powód. "Nie chcieliśmy o tym myśleć" nie jest powodem; "nie mamy pomiaru na docelowym sterowniku" jest.

## Decyzje otwarte

Brak.

## Decyzje rozstrzygnięte

Brak.
