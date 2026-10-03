# Standard formatowania kodu

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść. Pełny opis pozycji tego standardu wobec pozostałych jest w `docs/standards/README.md`.

## Po co ten dokument

Formatowanie jest tym, co review widzi jako pierwsze, zanim dojdzie do logiki zmiany - linia, która łamie się w innym miejscu niż resztę pliku, cudzysłów innego rodzaju niż sąsiednie, znak, który wygląda jak myślnik, ale nim nie jest. Żaden z tych szczegółów nie zmienia zachowania programu, ale każdy z nich kosztuje uwagę recenzenta, którą powinien dostać sam diff logiki, nie jego wizualna otoczka. Ten standard ustala jeden kształt dla tych szczegółów, żeby review mogło je pominąć, a nie oceniać przy każdej zmianie od nowa.

Większość reguł niżej jest już dziś wymuszana automatycznie przez `ruff format` na podstawie ustawień w `pyproject.toml` - w przeciwieństwie do większości standardów tego repozytorium, dostosowanie istniejącego kodu do reguł tego standardu nie wymaga przepisywania niczego ręcznie. Wystarczy odpalić formatter na dotkniętym module.

## Zakres i granice

Ten standard odpowiada za formatowanie kodu: długość linii i moment łamania wywołania na wiele linii, znaki zakazane, cudzysłowy i wyróżnienia - w kodzie Python i w prozie dokumentacji. Odpowiada też za formatowanie plików markdown przez prettier: które narzędzie, z jaką konfiguracją i którym celem `make` je uruchamia.

Znaki zakazane mają dziś dwie wersje: skróconą w `CLAUDE.md`/`AGENTS.md` (twarde zakazy stosowalne bez kontekstu) i pełną, z uzasadnieniem, tutaj - to zamierzona architektura opisana w `docs/standards/README.md`, nie duplikacja do naprawienia. Skrócona wersja w `CLAUDE.md`/`AGENTS.md` numerycznie różni się od pełnej listy poniżej - ten rozjazd jest znany i pozostaje nienaprawiony.

Czego tu nie ma: komentarze linijkowe i docstringi - to jest w `standard_code_quality.md`.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

Doprecyzowanie właściwe dla tego standardu: dla reguł wymuszanych automatycznie przez `ruff format` (długość linii, cudzysłów w kodzie) i przez prettiera (układ pliku markdown) obowiązek dostosowania sprowadza się do odpalenia `make format`, nie do ręcznej pracy. Dla reguł niewymuszanych automatycznie - znaki zakazane w dokumentacji, cudzysłów w prozie - obowiązek dostosowania jest zwykłym przeglądem zmienionego tekstu, tak jak w każdym innym standardzie.

## Długość linii i łamanie wywołań

Limit długości linii to 200 znaków, ustawiony w `pyproject.toml` (`[tool.ruff] line-length = 200`) i egzekwowany przez `ruff format`. Wywołanie funkcji i definicja funkcji, których parametry mieszczą się w tym limicie rozdzielone spacjami po przecinku, stoją w jednej linii. Po przekroczeniu limitu każdy parametr trafia w osobną linię, z przecinkiem na końcu, a zamykający nawias wraca do wcięcia linii, w której wywołanie się zaczęło.

Ten podział nie jest decyzją podejmowaną ręcznie przy pisaniu kodu - jest efektem odpalenia `ruff format` na pliku. Pisanie kodu z myślą "to na pewno będzie za długie, więc od razu łamię linię" jest zbędne: formatter złamie ją sam, jeśli trzeba, i scali z powrotem, jeśli nie trzeba.

Limit 200 znaków jest wyższy niż domyślne 79 czy 88 przyjęte gdzie indziej w ekosystemie Pythona. Uzasadnienie: funkcje w tym repozytorium często mają kilka parametrów nazwanych (`timeout`, `autocommit`, `limit`), a przy krótszym limicie sama sygnatura funkcji z adnotacjami typów i wartościami domyślnymi łamałaby się na wiele linii już przy umiarkowanej liczbie parametrów, mimo że w jednej linii jest równie czytelna. Wyższy limit oznacza mniej sztucznych łamań linii bez straty czytelności na współczesnym, szerokim ekranie.

Magic trailing comma jest respektowana (`[tool.ruff.format] skip-magic-trailing-comma = false`): przecinek zostawiony po ostatnim elemencie listy albo argumencie wymusza wielolinijkowy zapis, nawet jeśli całość zmieściłaby się w jednej linii. To jest świadomy wyjątek od reguły "formatter decyduje o łamaniu wyłącznie na podstawie długości" - dostępny, gdy autor kodu uzna, że lista argumentów jest czytelniejsza rozbita, mimo że zmieściłaby się w limicie, na przykład bo każdy z nich zasługuje na osobne spojrzenie przy review.

## Cudzysłowy

W kodzie Python cudzysłów jest zawsze podwójny (`[tool.ruff.format] quote-style = "double"`), wymuszany automatycznie przez `ruff format`. Wybór między `'` i `"` nie jest decyzją do podjęcia przy pisaniu - jedyny przypadek, w którym formatter sam użyje pojedynczego, to string zawierający dosłowny znak `"`, żeby uniknąć jego escapowania.

W prozie - docstringach, komentarzach, treści standardów, komunikacji - cudzysłów jest używany tylko wtedy, gdy jest do czegoś potrzebny: dosłowny cytat, nazwa pola albo fragmentu kodu wklejonego w tekst. Cudzysłów postawiony wokół słowa bez żadnej z tych funkcji, tylko dla podkreślenia, jest szumem: zaciera różnicę między miejscem, w którym cudzysłów faktycznie znaczy "to jest dosłowny cytat czegoś", a miejscem, w którym jest tylko ozdobnikiem. Niezależnie od kontekstu, jedynym dozwolonym znakiem jest zwykły ASCII `"` - nigdy zakrzywiony, patrz sekcja niżej.

## Wyróżnienia w prozie

Proza nie używa pogrubienia: ani wewnątrz zdania, ani jako etykiety otwierającej akapit czy punkt listy. Dotyczy to standardów, dokumentacji w `docs/`, warstwy `agent_docs/` oraz wszystkich artefaktów zadania w `plans/` - SEED, SHAPE, PRD, PLAN i REVIEW. Pogrubienie zostaje dozwolone wyłącznie tam, gdzie jest elementem struktury dokumentu, a nie podkreśleniem treści: w nagłówku i w komórce tabeli.

Uzasadnienie jest to samo co przy cudzysłowie w sekcji wyżej, tylko koszt jest wyższy. Etykieta w rodzaju:

```markdown
**Na co wpływa:** `standard_database.md`, struktura repozytorium, kolejność pracy.
```

udaje nagłówek, którym nie jest. Nie trafia do spisu treści, nie da się do niej odesłać z innego dokumentu, a przy czytaniu wygląda na szkielet dokumentu, mimo że jest zwykłym akapitem. Jeśli fragment naprawdę jest osobną częścią dokumentu, ma dostać nagłówek. Jeśli nie jest, wystarczy zwykłe zdanie:

```markdown
Na co wpływa: `standard_database.md`, struktura repozytorium, kolejność pracy.
```

Pogrubienie pojedynczego słowa w środku zdania psuje się w drugą stronę: im więcej takich wyróżnień, tym mniej każde z nich znaczy, a czytający zaczyna skakać po pogrubieniach i gubi zdanie, które je łączy. Ciężar wyróżnienia bierze na siebie kolejność, nie krój pisma - rzecz najważniejsza stoi na początku akapitu albo na początku listy, a nie w jego środku obłożona gwiazdkami.

Regułę pilnuje `tests/architecture/test_prose_style.py`, razem z listą znaków zakazanych. Bramka ma trzy własności, które łatwo wziąć za jej błąd:

- Skanuje każdy plik `.md` i `.py` w drzewie, także nieśledzony przez gita, więc czerwień bywa winą cudzego pliku, nie bieżącej zmiany. Przy czerwonej bramce najpierw sprawdza się, które ścieżki ją zapalają.
- Kopia cudzego dokumentu w `plans/<INICJATYWA>/attachments/` wchodzi pod bramkę jak każdy inny plik. Przed skopiowaniem cudzego dokumentu sprawdza się w nim pogrubienia i znaki zakazane, a przy trafieniu użytkownik wybiera: redakcja kopii z jawną notą o rozjeździe, wykluczenie katalogu z bramki albo rezygnacja z kopii.
- Detektor pogrubień nie wyłącza kodu inline. Dwie pary gwiazdek w jednej linii, na przykład dwa rozpakowania słownika w Pythonie albo dwie maski z potrójną gwiazdką, zapalają bramkę także w backtickach. W jednej linii markdown stoi najwyżej jedno takie wystąpienie, a drugie opisuje się słowami.

## Formatowanie markdown

Pliki markdown formatuje prettier, tak jak kod Python formatuje `ruff format`. Plik markdown musi przechodzić `prettier --check` bez różnic przed połączeniem zmiany; sprawdza to `make lint` (a przez niego `make check`), a doprowadza do porządku `make format`. Ruff markdownu nie obejmuje świadomie - powód stoi w `standard_code_quality.md`, sekcja Statyczna analiza i formatowanie.

Konfiguracja stoi w dwóch śledzonych plikach w korzeniu repozytorium. `.prettierrc` niesie opcje: końce linii LF, brak zawijania prozy (`proseWrap: preserve`), szerokość 200 znaków spójna z limitem ruffa, wcięcie dwóch spacji dla list zagnieżdżonych. `package.json` przypina dokładną wersję prettiera w `devDependencies`, a `npm ci` instaluje ją do `node_modules`; `node` i `npm` są wymaganiem wstępnym po stronie developera, wymienionym w `README.md` repozytorium. Cele `make` wołają `npx --no-install`, żeby użyć wyłącznie przypiętej kopii i przerwać, gdy jej nie ma - goły `npx prettier` pobrałby po cichu najnowsze wydanie i sprawdzał plik inną wersją niż edytor.

Oba pliki czyta również rozszerzenie prettiera w VS Code, którym `.vscode/settings.json` formatuje markdown przy zapisie. Przy obecnym pliku konfiguracji rozszerzenie ignoruje własne ustawienia `prettier.*` w VS Code, a kopię z `node_modules` wybiera przed wersją wbudowaną, więc zapis z edytora i `make format` dają identyczny wynik. Podniesienie wersji prettiera jest zmianą w `package.json`, nie aktualizacją rozszerzenia.

Co prettier zmienia w pliku: wyrównuje kolumny tabel do najszerszej komórki, normalizuje puste linie wokół nagłówków i bloków, ustawia wcięcie kontynuacji punktu listy, ujednolica znaczniki wyróżnień i formatuje bloki kodu w płotkach z językiem, który zna (`json`, `yaml`), do tej samej szerokości 200 znaków. Czego nie zmienia: treści i zawijania akapitów, bloków `python` i `sql`, których nie parsuje. Nazwa techniczna z podkreśleniem stojąca w prozie bez backticków bywa czytana jako kursywa i przepisywana na gwiazdki (`trigger_params` na `trigger*params`), dlatego nazwa techniczna w prozie stoi w backtickach. Powód jest mechaniczny, nie stylistyczny: formater nie tyka tego, co jest oznaczone jako kod.

## Szerokość tabel w dokumentacji

Komórka tabeli w prozie dokumentacji nosi krótką frazę albo jedno krótkie zdanie, nie kilka zdań uzasadnienia. Powód jest mechaniczny, nie estetyczny: prettier, tak jak każdy formater markdown, wyrównuje całą kolumnę do szerokości jej najdłuższej komórki, więc jedna rozwlekła komórka rozciąga do tej samej szerokości każdy wiersz tabeli, także te, które same w sobie są krótkie. Efekt widać w źródle jako linie po kilkaset znaków, których nie da się przeczytać bez przewijania w bok - to jest to zwężenie widocznego pola, o które chodzi w tej regule, nie subiektywne wrażenie.

Tabela, w której każdy wiersz i tak jest osobnym akapitem uzasadnienia - decyzja z powodem, ryzyko z konsekwencją i mitygacją, odrzucona alternatywa z wyjaśnieniem - nie jest tabelą tylko z nazwy. Taki układ ma dostać formę właściwą prozie: nagłówek na wiersz, jeśli wiersz ma stabilny identyfikator używany gdzie indziej w dokumentacji (na przykład `D14`, `R7`), albo punkt listy, jeśli identyfikatora nie ma. Tabela zostaje tabelą tam, gdzie faktycznie zestawia krótkie, równoległe fakty do skanowania wzrokiem - kod HTTP obok nazwy błędu, pole obok tego, kto może je zmienić - i w takim przypadku pojedynczy wiersz, który się rozrósł, warto skrócić do frazy, a resztę wyjaśnienia przenieść do zwykłego akapitu pod tabelą, zamiast zostawiać go w komórce.

## Znaki zakazane

Kod i dokumentacja w tym repozytorium nie zawierają poniższych znaków. Część z nich to oczywiste znaki typograficzne czata (myślniki, cudzysłowy zakrzywione, wielokropek, strzałki, znak mnożenia) - ich obecność w kodzie albo dokumentacji zdradza tekst wygenerowany bez przejścia przez styl repozytorium. Część to celowo dobrane homoglify: znaki wizualnie nieodróżnialne od zwykłych znaków ASCII, które model językowy mógłby wstawić bez zauważenia różnicy - dla tych znaków punkt kodowy jest podany wprost, żeby uniknąć pomyłki przy czytaniu tej listy na oko.

- `—` (U+2014, myślnik em) - zamiast niego zwykły `-`.
- `–` (U+2013, myślnik en) - zamiast niego zwykły `-`.
- `−` (U+2212, minus) - zamiast niego zwykły `-`.
- `“` (U+201C, cudzysłów otwierający zakrzywiony) - zamiast niego zwykły `"`.
- `”` (U+201D, cudzysłów zamykający zakrzywiony) - zamiast niego zwykły `"`.
- `‘` (U+2018, apostrof otwierający zakrzywiony) - zamiast niego zwykły `'`.
- `’` (U+2019, apostrof zamykający zakrzywiony) - zamiast niego zwykły `'`.
- `ʼ` (U+02BC, modyfikujący apostrof) - zamiast niego zwykły `'`.
- `…` (U+2026, wielokropek) - zamiast niego trzy zwykłe kropki `...`.
- `·` (U+00B7, kropka środkowa) - zamiast niej zwykła kropka albo myślnik, zależnie od kontekstu.
- `→` (U+2192, strzałka w prawo) - zamiast niej `->`.
- `←` (U+2190, strzałka w lewo) - zamiast niej `<-`.
- `↔` (U+2194, strzałka dwustronna) - zamiast niej `<->`.
- `×` (U+00D7, znak mnożenia) - zamiast niego litera `x` albo `*`, zależnie od kontekstu.
- `а` (U+0430, cyrylickie litera "a") - wygląda identycznie jak łacińskie "a" (U+0061), ale to inny punkt kodowy - zamiast niego zwykłe łacińskie `a`.
- `;` (U+037E, grecki znak zapytania) - wygląda identycznie jak zwykły średnik (U+003B), ale to inny punkt kodowy - zamiast niego, gdy potrzebny jest średnik, zwykły `;`.
- `∕` (U+2215, ukośnik dzielenia) - wygląda podobnie do zwykłego ukośnika (U+002F), ale to inny punkt kodowy - zamiast niego zwykły `/`.
- Emotikony, na przykład 🙂 🚀 ✅ - bezwzględnie nie są używane w kodzie ani w dokumentacji.

## Checklista

- Czy nowy albo zmieniony kod przeszedł przez `ruff format` przed połączeniem zmiany, zamiast łamać linie i wybierać cudzysłów ręcznie?
- Czy żadna linia kodu nie przekracza 200 znaków (poza przypadkami, w których `ruff format` sam by ją zostawił dłuższą - np. długi string, który się nie dzieli)?
- Czy magic trailing comma jest używana świadomie, tam gdzie autor chce wielolinijkowego zapisu mimo że zmieściłby się w limicie, nie przypadkiem?
- Czy string w kodzie Python używa cudzysłowu podwójnego, poza przypadkiem stringa zawierającego dosłowny znak `"`?
- Czy cudzysłów w prozie (docstring, komentarz, dokumentacja) występuje tylko dla dosłownego cytatu, nazwy pola albo fragmentu kodu w tekście, nie jako ozdobnik?
- Czy nowy albo zmieniony plik markdown przeszedł przez `make format` przed połączeniem zmiany i `make lint` nie zgłasza dla niego różnic prettiera?
- Czy nazwa techniczna z podkreśleniem, stojąca w prozie pliku markdown, jest w backtickach, żeby prettier nie przepisał jej jako wyróżnienia?
- Czy proza jest wolna od pogrubień - zarówno w środku zdania, jak i w postaci etykiety otwierającej akapit albo punkt listy - a pogrubienie występuje wyłącznie w nagłówkach i komórkach tabel?
- Czy żadna komórka tabeli nie niesie więcej niż krótkiej frazy albo jednego krótkiego zdania, a tabela, której wiersze są w istocie osobnymi akapitami uzasadnienia, została zamieniona na nagłówki albo listę?
- Czy kod i dokumentacja nie zawierają żadnego znaku z listy znaków zakazanych, w tym homoglifów?
- Czy żadna linia markdown nie ma dwóch par gwiazdek, także w kodzie inline w backtickach?
- Czy tekst nie zawiera emotikonów?
