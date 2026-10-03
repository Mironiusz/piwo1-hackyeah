# Standard pracy z gitem

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Zbiór standardów opisuje, jak pisać kod, a ten dokument - jak kod trafia do gałęzi. Kierunek przepływu zmian, rola każdej gałęzi i granica uprawnień agenta, jeśli nie są zapisane, żyją wyłącznie w głowach osób, które je ustaliły, a każda nowa osoba i każda dłuższa przerwa w pracy kosztuje odtwarzanie reguły z historii repozytorium.

Drugi powód dotyczy agenta. Agent pracujący w tym repozytorium ma dostęp do terminala i technicznie może na gicie zrobić wszystko: zacommitować cudzą pracę, wysłać ją na zdalne repozytorium, przepisać historię gałęzi. Hook `block_dangerous_commands.py` blokuje commit i push, ale działa wyłącznie po stronie Claude Code i nie obejmuje przepisywania historii. Granica, która nie jest w pełni wymuszona mechanizmem, musi być przynajmniej zapisana - inaczej nie istnieje w ogóle.

## Zakres i granice

Ten standard odpowiada za uprawnienia agenta wobec gita, role gałęzi tego repozytorium oraz kierunki, w których zmiana między nimi przechodzi.

Czego tu nie ma:

- Komendy do konkretnych sytuacji (cofanie zmian, przenoszenie commitów między gałęziami, odzyskiwanie zgubionej pracy) i konfiguracja środowiska gita (tożsamość autora commitów, klucze i klient SSH). To wiedza operacyjna, którą projekt trzyma poza standardami. Tutaj są reguły, tam czynności.
- Treść komunikatów commita, w tym konwencja prefiksów. Świadomie nieobjęta żadną regułą tego repozytorium - konsekwencją jest historia niejednorodna i nic jej nie ujednolica.
- Ustawienia ochrony gałęzi po stronie hostingu repozytorium. Mieszkają poza repozytorium, więc żaden dokument w drzewie nie może ich wymusić ani zweryfikować.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - praca niezgodna ze standardem blokuje review niezależnie od tego, kto ją wykonał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Doprecyzowanie właściwe dla tego standardu: reguła dotyczy każdej pracy z gitem w tym repozytorium, niezależnie od rozmiaru zmiany, i nie działa wstecz na historię już istniejącą. Commit, który powstał przed przyjęciem tego dokumentu, nie jest naruszeniem i nie ma potrzeby go przepisywać.

## Uprawnienia agenta wobec gita

O przypisaniu operacji do stopnia rozstrzyga jedno kryterium: czy operacja dotyka historii. Nie rozstrzyga tego, czy jest lokalna - operacja lokalna też potrafi historię przepisać, a operacja sięgająca do zdalnego repozytorium potrafi jej nie tknąć.

Zakazane bezwarunkowo, bez furtki na wyraźną prośbę użytkownika: `git commit` oraz `git push`. Commit tworzy nowy obiekt w historii i podpisuje go tożsamością człowieka, który go nie napisał. Push wystawia ten obiekt innym ludziom, więc od tego momentu cofnięcie przestaje być czynnością lokalną. Prośba użytkownika nie odblokowuje żadnej z tych dwóch operacji - jeśli commit ma powstać, tworzy go człowiek.

Dozwolone wyłącznie na wyraźną prośbę użytkownika: `git add` oraz `git rebase`. Stage nie dotyka historii i jest odwracalny jednym poleceniem, więc nie zasługuje na zakaz trwały, ale jest ostatnim krokiem przed commitem i nie ma powodu, żeby działo się z inicjatywy agenta. Rebase przepisuje historię lokalną, której autorem jest człowiek, a reflog daje z niej drogę powrotu - to za mało na zakaz bezwarunkowy i za dużo na inicjatywę agenta.

Dozwolone bez pytania: wszystko pozostałe. Operacje odczytowe, w tym `git status`, `git log`, `git diff`, `git show` i `git blame`. Pobieranie zmian ze zdalnego repozytorium, czyli `git fetch` i `git pull`. Odkładanie zmian na bok przez `git stash`. Przełączanie i tworzenie gałęzi przez `git switch` i `git checkout`. Scalanie lokalne przez `git merge`. Dodatkowe katalogi robocze przez `git worktree`.

Operacja, której ten dokument nie wymienia, rozstrzyga się kryterium, nie analogią do najbliższej nazwy. Pytanie brzmi, czy operacja tworzy, przepisuje albo publikuje historię - a nie, czy przypomina którąś z wypisanych.

## Role gałęzi i kierunki scalania

Repozytorium ma trzy role gałęzi. `main` jest gałęzią wydania, `dev` gałęzią integracji, do której trafia zamknięta praca przed wydaniem, i obie są chronione po stronie hostingu repozytorium tak, że bezpośredni push i force-push nie są możliwe na żadnej z nich. Pozostałe to stałe gałęzie robocze, po jednej na osobę w zespole.

Gałąź robocza jest osobowa i długowieczna. Nie powstaje per zadanie i nie znika po scaleniu - ta sama gałąź obsługuje kolejne zadania tej samej osoby.

Do `main` i do `dev` zmiana wchodzi wyłącznie przez Merge Requesta, w skrócie MR. W drugą stronę, czyli z `main` albo `dev` na gałąź roboczą, zmiana schodzi zwykłym mergem wykonanym lokalnie - tam MR nie jest potrzebny, bo nikt poza właścicielem gałęzi na tę zmianę nie patrzy.

Gdy projekt ma potok CI, każdy Merge Request do `dev` i do `main` uruchamia go, a potok mechanicznie odbija Definition of Done repozytorium. Scalenie wymaga wtedy zielonego potoku. Szablon nie zawiera definicji potoku - projekt dodaje ją dla swojego hostingu repozytorium.

Potok sprawdza gałąź w chwili przebiegu, nie w chwili scalenia: MR, który zestarzał się po ostatnim przebiegu, bo do `dev` weszła inna zmiana, zachowuje swój ostatni zielony wynik. Reguła miękka dla scalającego domyka tę lukę: przed scaleniem uruchomić potok ponownie, jeśli od jego ostatniego przebiegu do `dev` weszła inna zmiana - nic tego nie wymusza mechanicznie.

Gdy środowisko docelowe podnosi wdrożenie w odpowiedzi na scalenie do gałęzi wydania, bez udziału człowieka, Merge Request na tę gałąź jest ostatnim momentem, w którym zmianę widać przed jej wejściem na środowisko z prawdziwymi danymi.

Merge Request powstaje po każdym zamkniętym zadaniu, nie po kilku naraz. Jest to reguła miękka i nic jej nie pilnuje, ale jest jedynym miejscem, w którym model gałęzi osobowych różni się w praktyce od zadaniowych: gałąź, która zbiera kilka niepowiązanych zmian, przestaje mieścić się w jednym MR, review dostaje worek zamiast jednej zmiany, a wycofanie pojedynczej rzeczy wymaga rozplątywania reszty.

## Czego ten standard nie egzekwuje

Mechanizm egzekwuje z tego dokumentu jedną regułę i tylko po stronie Claude Code: hook `block_dangerous_commands.py` blokuje `git commit` i `git push`, także z opcją `-C` albo `-c` przed poleceniem, obok komend niszczących pliki i lokalne zmiany. Nie obejmuje `git add` ani `git rebase`. Hook nie ma odpowiednika po stronie Codeksa, więc tam zakaz commita i pusha jest regułą zapisaną, nie wymuszoną. Zapisane jest to wprost, bo reguła miękka opisana jako miękka nadal działa, a reguła miękka wyglądająca na twardą usypia czujność.

Naruszenie reguł niewymuszonych wykrywa się po fakcie, przez `git log` i autora commita. Nie ma sygnału w momencie, w którym naruszenie się dzieje.

Ochrona gałęzi `dev` i `main` przed bezpośrednim pushem i force-pushem stoi poza repozytorium, po stronie hostingu, i nic w tym drzewie jej nie weryfikuje ani jej nie zastępuje.

## Checklista

- Czy operacja, którą agent zamierza wykonać, tworzy, przepisuje albo publikuje historię?
- Czy prośba użytkownika o `git add` albo `git rebase` była wyraźna, a nie domniemana z kontekstu rozmowy?
- Czy commit powstał ręką człowieka?
- Czy zmiana wchodzi do `main` albo `dev` przez Merge Requesta, a nie przez merge wykonany lokalnie?
- Czy Merge Request zawiera jedno zamknięte zadanie, a nie kilka zebranych po drodze?
- Czy zmiana schodząca z `main` albo `dev` na gałąź roboczą idzie zwykłym mergem, bez zakładania zbędnego Merge Requesta?
