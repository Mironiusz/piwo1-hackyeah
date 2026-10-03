# Standard rozpisywania dokumentacji agentowej

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Ten standard jest jedynym źródłem prawdy dla formatu pięciu artefaktów łańcucha agentowego (SEED, SHAPE, PRD, PLAN, REVIEW) oraz dla formatu wpisu `agent_docs/memory`. Zamyka problem, który ten plik sam odnotowywał w wersji szkieletowej: konwencja pamięci agentowej miała czterokrotny adres - ten plik, `standard_agentic_workflow.md` rozdz. 5.2, `agent_docs/README.md` i `agent_docs/memory/README.md`. Od teraz pozostałe trzy miejsca odsyłają tutaj, zamiast powtarzać tę samą treść.

## Zakres i granice

W środku: format każdego z pięciu artefaktów łańcucha i format wpisu `agent_docs/memory`, wraz z uzasadnieniem - co się psuje, gdy się danej reguły nie przestrzega.

Czego tu nie ma:

- sam mechanizm łańcucha, kolejność faz, punkty kontrolne i opis skilli, które go obsługują - to jest w `standard_agentic_workflow.md`;
- pełny opis dziesięciu kategorii ryzyka blokującego - to jest w `standard_agentic_workflow.md` rozdz. 3.3, tutaj tylko odniesienie;
- dualizm Claude Code/Codex i test parytetu skilli - to również `standard_agentic_workflow.md`;
- kiedy inicjatywa przechodzi do archiwum `plans_finished/` i jak wraca - to `standard_agentic_workflow.md` rozdz. 4.6; tutaj jest wyłącznie to, jak zapisać w REVIEW zakres werdyktu, zamknięcie i wznowienie;
- formatowanie prozy w tych artefaktach: znaki zakazane, cudzysłów i zakaz pogrubień inline - to jest w `standard_formatting.md`. Reguła o wyróżnieniach obowiązuje wszystkie pięć artefaktów łańcucha i wpisy pamięci, mimo że są pisane przez agenta, nie przez człowieka.

## Reguła odstępstwa

Reguła odstępstwa wspólna dla wszystkich standardów (`docs/standards/README.md`) obowiązuje w wersji zaostrzonej: standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita, bo projekt założony z szablonu nie ma stanu zastanego, który wymagałby okresu przejściowego. Rozluźnienie tej reguły ma być kiedyś jawną decyzją zapisaną w mapie standardów, nie stanem wchodzącym w życie samym.

Zawężenie właściwe dla tego standardu: jednostką odstępstwa jest zadanie (`plans/<INICJATYWA>/<ZADANIE>_*`), nie moduł kodu - ogólna reguła mówi o module dotkniętym zmianą kodu produkcyjnego, co nie ma odpowiednika w dokumentach `plans/`.

## Format SEED

SEED jest dosłownym zapisem zgłoszenia, z jawnym źródłem pochodzenia: rozmowa z użytkownikiem, wklejony mail, notatka ze spotkania, opis z brancha, zgłoszenie od kogoś z zespołu. Jest niemodyfikowalny po zapisaniu - zmiana zakresu zawsze idzie do SHAPE, nigdy do SEED. Jeśli seed jest zbyt ubogi, żeby cokolwiek z niego wynikało, zapisuje się go i tak dosłownie, a braki adresuje się pytaniami w fazie shape - nie poprawia się seeda domysłem, bo wtedy przestaje być zapisem tego, co faktycznie zostało powiedziane.

Użytkownik może stworzyć plik seeda sam, wklejając gotową notatkę zamiast dyktować go w rozmowie - w takim wypadku `plan-shape` nigdy go nie nadpisuje, tylko wczytuje. Jedyny twardy wymóg dla pliku stworzonego ręcznie: musi zawierać jakąkolwiek treść, bo pustego seeda nie da się przetworzyć.

Bez tej reguły seed przestałby być wiarygodnym punktem odniesienia - gdyby dało się go poprawiać w miarę postępu prac, żadna przyszła osoba nie mogłaby sprawdzić, co faktycznie zostało zgłoszone na starcie, w odróżnieniu od tego, co zrozumiano później.

SEED może nieść parametr regulatora szczegółowości, zapisywany wzorcowo jako `C:N` (pełna definicja: `standard_agentic_workflow.md` rozdz. 3.5). Nie łamie to nietykalności seeda, bo parametr jest częścią dosłownej treści zgłoszenia i obowiązuje z nagłówka SHAPE, nie stąd - zmiana wartości w trakcie zadania idzie do SHAPE i nigdy nie wraca do tego pliku.

## Format SHAPE

SHAPE ma jedenaście sekcji: Problem, Odbiorca i wyzwalacz, Stan obecny, Najmniejszy sensowny zakres, Poza zakresem, Wymagania funkcjonalne, Scenariusze, Podważenie własnych założeń, Reguły domenowe albo jawne TODO, Uwagi o danych/wydajności/bezpieczeństwie, Otwarte pytania. "Odbiorca i wyzwalacz" pyta o odbiorcę zmiany i jej wyzwalacz: osobę w konkretnej roli, konsumenta interfejsu programistycznego, zadanie okresowe workera, inny system. Gdy projekt nie ma interfejsu użytkownika, odbiorcą jest system, a pytanie o personę nie ma odpowiedzi.

Wywiad prowadzi się jedno pytanie na raz: `AskUserQuestion` dla decyzji zamkniętych, zwykły tekst dla otwartych. Po każdej odpowiedzi dopisuje się minimalną notatkę do właściwej sekcji, usuwa się odpowiadający wpis z "Otwarte pytania" i zapisuje plik - dzięki temu wywiad można przerwać w dowolnym momencie bez utraty postępu.

Nagłówek SHAPE niesie dwie linie: stan dokumentu z datą oraz `Regulator: C:N` z wartością regulatora szczegółowości obowiązującą w tym zadaniu (pełna definicja: `standard_agentic_workflow.md` rozdz. 3.5). To jest miejsce, z którego wartość czytają wszystkie trzy skille łańcucha - nie z seeda. Wartość wolno zmienić w trakcie zadania, ale wtedy dokument dostaje jedną linię o tym, od którego momentu obowiązuje nowa, bo bez niej nie da się czytać dokumentu wstecz. Pozycja rozstrzygnięta przez agenta zamiast zapytania niesie przy sobie frazę "Decyzja agenta przy C:N, bez pytania", w miejscu tej pozycji, nie w zbiorczej sekcji na końcu.

Sekcja "Podważenie własnych założeń" nie może zostać pusta. Jeśli nic w niej nie budzi wątpliwości, to znak, że problem nie został jeszcze zrozumiany, a nie że jest wyjątkowo jasny.

Każde pytanie dotykające jednej z dziesięciu kategorii ryzyka blokującego (pełna lista i sposób weryfikacji: `standard_agentic_workflow.md` rozdz. 3.3) oznacza się `Block: yes` wraz z nazwą kategorii. Faza kończy się dopiero, gdy wszystkie sekcje są wypełnione i żadna pozycja w "Otwarte pytania" nie ma `Block: yes` - to zabezpieczenie przed przejściem do PRD z nierozstrzygniętym pytaniem, które dotyka kontraktu API, schematu bazy albo innego realnego ryzyka.

## Format PRD

PRD ma dziewięć sekcji: Cel biznesowy, Problem i jego skutki, Zakres, Poza zakresem, Wymagania funkcjonalne, Kryteria akceptacji, Reguły domenowe, Zależności i wpływ na inne moduły, Ryzyka i uwagi. Odpowiada wyłącznie na "co i dlaczego", nigdy na "jak".

Czarna lista treści zakazanych w PRD: modele danych, listy kolumn, migracje, ścieżki plików kodu, nazwy funkcji, decyzje o bibliotekach, szczegóły deploymentu, sekrety i credentiale. Jeśli podczas pisania PRD pojawia się chęć zapisania rozwiązania technicznego, ten materiał należy do PLAN, nie do PRD - mieszanie obu prowadzi do przedwczesnego zamrożenia decyzji technicznych, zanim ktokolwiek potwierdził, że sam problem i zakres są uzgodnione.

PRD kończy się bramką potwierdzenia z użytkownikiem, zanim powstanie PLAN. To jedyny punkt kontrolny między "co" a "jak" w całym łańcuchu - nigdy nie przechodzi się przez niego milcząco.

## Format PLAN

PLAN ma dziewięć sekcji: Cel, Fakty, Decyzje, Zakres zmian, Kolejność wdrożenia, Definition of Done, Ryzyka, Otwarte pytania, Pliki uzupełniające. Odpowiada na "jak", oparty na faktach zweryfikowanych w kodzie, bazie i dokumentacji - nigdy na założeniach przyjętych na wiarę.

Każdy krok w "Zakres zmian" ma konkretne nazwy plików, funkcji i kontraktów danych - nigdy opis w stylu "coś w rodzaju". Decyzja techniczna podjęta samodzielnie zamiast zapytania niesie w sekcji "Decyzje" tę samą frazę co w SHAPE: "Decyzja agenta przy C:N, bez pytania".

### Marker stanu planu

Linia stanu dokumentu niesie datę i marker stanu, w jednym z dokładnie dwóch brzmień: "plan w toku" albo "plan zamknięty". Marker jest tą samą konwencją, którą SHAPE już niesie (wywiad w toku, wywiad zamknięty), i nie wprowadza nowego pojęcia.

```text
Stan dokumentu: 2026-08-17, plan zamknięty
```

Lista brzmień jest zamknięta, bo od markera zależy objęcie dokumentu kontrolą opisaną niżej, a drugi człon linii stanu bywał wcześniej zwykłym zdaniem opisowym - bez zamkniętej listy nie da się odróżnić markera od takiego zdania.

Marker rozstrzyga o objęciu kontrolą w pierwszej kolejności, data dopiero w drugiej: kontrola obejmuje plan zamknięty o dacie nie wcześniejszej niż data wejścia reguły w życie, zapisana w stałej `RULE_EFFECTIVE_DATE` testu z sekcji Egzekwowanie. Plan w toku nie podlega jej wcale. Powód jest praktyczny: plan pisany na raty nie ma blokować niezwiązanej pracy na tym samym drzewie, a zamknięcie jest właściwym momentem kontroli, bo dopiero wtedy plan jest podawany do fazy implementacji. Znana cena, przyjęta świadomie: plan porzucony w stanie w toku nigdy pod kontrolę nie wejdzie.

### Format ustalenia w sekcji Fakty

Sekcja "Fakty" zawiera wyłącznie pozycje ustaleń, po jednej w linii, bez zdania wprowadzającego i bez treści innego rodzaju. Zdanie wprowadzające, jeśli jest potrzebne, stoi przed nagłówkiem sekcji.

Pozycja niesie cztery rzeczy: identyfikator, twierdzenie, dowód i datę sprawdzenia. Zapisuje się je w trzech polach rozdzielonych znakiem kreski pionowej: identyfikator wraz z twierdzeniem, dowód, data sprawdzenia w formacie RRRR-MM-DD. Identyfikator ma kształt `F-N.` z kropką, tak jak identyfikatory w pozostałych sekcjach. Kilka dowodów przy jednym ustaleniu rozdziela średnik.

```text
F-1. Sonda osiągalności bazy czyta adres z konfiguracji, nie ze zmiennej środowiskowej. | kod:`data/engine.py:31`; dok:`docs/standards/standard_config.md` par. Trzy warstwy konfiguracji i cztery miejsca przechowywania | 2026-08-17
```

Dowód należy do jednego z pięciu rodzajów, rozpoznawalnych po samym początku zapisu, bez interpretacji treści:

- `kod:` - odczyt kodu ze wskazaniem pliku i linii,
- `cmd:` - uruchomienie wraz z wynikiem. Rodzaj jest szeroki: obejmuje komendę powłoki, fragment kodu i odczyt stanu środowiska, czyli wszystko, co zostało uruchomione i czego skutek widać w wyniku,
- `db:` - zapytanie do bazy wraz z wynikiem,
- `dok:` - odesłanie do dokumentu ze wskazaniem paragrafu albo linii,
- `ZAŁOŻENIE:` - treść przyjęta bez weryfikacji, oznaczona jawnie.

Ustalenie wyprowadzone z kilku źródeł niesie kilka dowodów przy jednej pozycji. Nie ma osobnego rodzaju dowodu dla wnioskowania i nie ma go mieć - taki rodzaj byłby furtką dokładnie dla tez bez pokrycia, przed którymi ten format chroni.

Oba separatory działają wyłącznie poza zapisem w backtickach: kreska pionowa i średnik zacytowane wewnątrz backticków należą do cytatu, nie do struktury pozycji. Bez tego wyjątku format kazałby przepisać komendę, która faktycznie została uruchomiona - regex z kreską pionową albo zapytanie ze średnikiem przestałyby dać się zacytować dosłownie, a dosłowność cytatu jest tu ważniejsza niż prostota podziału.

Granica kontroli, nazwana tu wprost, żeby zielona bramka nie była czytana jako dowód prawdziwości ustaleń: sprawdzana jest forma dowodu, nigdy jego prawdziwość. Ustalenie zmyślone i zapisane w poprawnej formie przejdzie. Format podnosi koszt zmyślenia i czyni je wykrywalnym przy kontroli ręcznej, nie czyni go niemożliwym. Najwygodniejszą furtką jest tu rodzaj `ZAŁOŻENIE:`, bo pozwala wypełnić formę bez żadnej weryfikacji - użycie go dla czegoś, co dało się sprawdzić, jest złamaniem tej reguły, mimo że kontrola automatyczna tego nie zauważy.

### Pusta sekcja otwartych pytań

Plan zamknięty ma pustą sekcję "Otwarte pytania". Sekcja jest pusta, gdy nie ma w niej ani jednej pozycji listy, a pierwszy jej akapit jest stwierdzeniem braku zaczynającym się od słowa "Brak". Zdanie stwierdzające brak pytań jest więc zapisem pustej sekcji, nie pozycją.

### Egzekwowanie

Reguły formatu ustalenia, markera stanu i pustej sekcji otwartych pytań egzekwuje `tests/architecture/test_plan_document_contract.py`, dla planów oznaczonych jako zamknięte i nie starszych niż data wejścia reguły w życie (stała `RULE_EFFECTIVE_DATE` w tym teście). Projekt założony z szablonu powstaje po tej dacie, więc kontrola obejmuje każdy jego plan zamknięty. Kontrola idzie razem z resztą testów architektury, więc odpala się sama przy implementacji i przy review.

Jeśli weryfikacja w trakcie pisania planu obali założenie z PRD, plan wraca do fazy PRD zamiast po cichu je obchodzić - PRD jest kontraktem, nie szkicem do dowolnej korekty. PLAN kończy się dopiero, gdy spełnia te same kryteria kompletności, których i tak będzie wymagał `plan-implement`: zero TODO, zero pozycji w "Otwarte pytania", każdy krok z jednoznacznym wejściem i wyjściem.

## Format REVIEW

REVIEW jest logiem przebiegu implementacji, nie trwałą pamięcią - opisuje stan konkretnego zadania, nie wiedzę uniwersalną o repozytorium. Zapisuje się w nim to, co zostało pominięte, na co agent trafił w trakcie pracy, jakie decyzje padły przy pisaniu kodu i co wymaga powrotu w przyszłości.

Różnica względem wpisu `agent_docs/memory` jest kluczowa: REVIEW opisuje przebieg tego jednego zadania i traci znaczenie, gdy zadanie się zamyka; wpis memory zapisuje trwały wzorzec albo decyzję, użyteczną w przyszłych, niepowiązanych zadaniach dotyczących tego samego modułu. Mylenie tych dwóch miejsc prowadzi do sytuacji, w której trwała wiedza ginie razem z zamkniętym zadaniem, albo odwrotnie - `agent_docs/memory` zapełnia się jednorazową trywią.

Luka planu wypełniona samodzielnie w trakcie implementacji, zamiast pytaniem do użytkownika, jest zapisywana w REVIEW z tą samą frazą co w pozostałych artefaktach: "Decyzja agenta przy C:N, bez pytania".

REVIEW dopisuje `plan-implement`, w trakcie implementacji (gdy trafia na coś, czego plan nie przewidział) i na końcu, jako podsumowanie. `implementation-dod-review`/`dod-reviewer` może REVIEW uzupełnić, ale nie jest jego właścicielem.

REVIEW jest też jedynym miejscem, z którego czyta się zakończenie inicjatywy (`standard_agentic_workflow.md`, rozdz. 4.6). Werdykt review zapisany w REVIEW mówi wprost, jaki zakres obejmuje: całą inicjatywę, jedno zadanie z kilku, sam plan albo część kodu - bez tego zdania czytelnik nie odróżni końcowego `ready` całej sprawy od `ready` jednego etapu, a tylko to pierwsze kwalifikuje katalog do archiwum. W inicjatywie wielozadaniowej rozliczenie jednego zadania jest werdyktem dla tego zadania, nie dla katalogu. Zamknięcie bez werdyktu `ready` - rozliczenie samym review, anulowanie - zapisuje się jawnie w linii stanu dokumentu ("inicjatywa zamknięta", "inicjatywa anulowana") wraz z powodem, w tym samym pliku, nie w osobnym pliku statusu. Linia stanu review nie ma zamkniętej listy brzmień i nie podlega kontroli automatycznej - w odróżnieniu od markera planu opisanego wyżej, który mówi o gotowości planu do implementacji, nigdy o zakończeniu inicjatywy.

Wznowienie zarchiwizowanej inicjatywy dopisuje się do REVIEW jako kolejny wpis, z datą, powodem i zakresem wznowionej pracy. Dotychczasowe wpisy, w tym zapis zamknięcia, zostają nietknięte - REVIEW jest dziennikiem, w którym historia zamknięcia i wznowienia stoją obok siebie w kolejności zdarzeń. Inicjatywa zamknięta bez REVIEW dostaje ten plik przy wznowieniu, z wpisem o wznowieniu jako pierwszym.

## Format wpisu agent_docs/memory

`agent_docs/memory/` to trwała pamięć decyzji per moduł - coś innego niż globalna auto-memory Claude (`~/.claude/projects/.../memory/`), która trzyma preferencje i kontekst konkretnego użytkownika między sesjami. `agent_docs/memory/` trzyma wiedzę o samym repozytorium, dostępną każdemu narzędziu - Claude Code i Codeksowi jednakowo. Jeśli coś dotyczy wyłącznie sposobu współpracy z konkretnym użytkownikiem, idzie do auto-memory Claude, nie tutaj.

Struktura i wybór ścieżki. Plik per jednostka kodu, w folderze grupy odpowiadającej strukturze repozytorium. W profilu Pythona jednostką kodu jest warstwa ze `standard_architecture.md`, więc grupa dla kodu serwisu odpowiada warstwie: `api/`, `service/`, `data/`, `worker/`. Katalogi infrastrukturalne obok kodu serwisu, na przykład `config/` albo `alembic/`, mają własne grupy o tej samej nazwie co katalog. Projekt spoza profilu Pythona ustala jednostkę kodu w `standard_documentation.md` i stosuje tę samą zasadę. Reguła nadrzędna zostaje bez zmian: ścieżka pliku memory wynika wprost ze ścieżki opisywanego kodu, nigdy nie jest zgadywana, a grupa powstaje razem z pierwszym wpisem, nie z góry. Osobna grupa `tests/` jest przewidziana od początku - trzyma wzorce infrastruktury testowej przecinające wiele plików testowych, więc ma tylko `_wspolne.md`, bez plików per jednostka.

Wiedza dotycząca kilku modułów. Plik per moduł nie obsługuje wiedzy przekrojowej, więc są dwa jawne miejsca: `_wspolne.md` w folderze grupy (decyzja dotycząca kilku modułów tej samej grupy) oraz `_przekrojowe.md` w `memory/` (decyzja przecinająca grupy). Oba, tak jak pliki modułowe, powstają dopiero gdy jest co w nich zapisać - nie tworzy się ich z góry.

Szablon wpisu. Każdy wpis ma ten sam kształt:

```text
## YYYY-MM-DD - Krótki tytuł (TICKET-ID albo krótki opis zadania)

- What changed:
- Why:
- Reusable pattern:
- Risk / notes:
```

Piąte, opcjonalne pole `- Decisions:` dodaje się, gdy wpis rozstrzyga wcześniej otwarte pytanie z innego wpisu. Między plikami memory linkuje się przez wiki-link `[[nazwa-pliku]]` (bez rozszerzenia) - lżejsza konwencja niż pełne ścieżki z backtickami używane gdzie indziej w repo, zarezerwowana wyłącznie dla tej warstwy. Wpisy dopisuje się, nigdy nie nadpisuje - to log append-only.

Linia orientacyjna. Moduł, który ma `<MODULE>_ALGORITHM.md`, dostaje plik memory od razu, ale zawiera on wyłącznie jedną linię orientacyjną przed pierwszym wpisem:

```text
Co robi moduł: patrz `<ścieżka>/<MODULE>_ALGORITHM.md`, sekcje "Cel algorytmu" i "Ogólna mapa procesu".
```

To wskaźnik, nie kopia, więc nigdy się nie dezaktualizuje. Sam log decyzji powstaje dopiero przy pierwszej realnej decyzji. Moduły bez `ALGORITHM.md` nie dostają tej linii ani pliku z góry - dla nich plik powstaje wraz z pierwszym wpisem.

Kiedy pisać wpis. Zapisuje się decyzję na trwałe, gdy widać jeden z sygnałów: powtarzający się wzorzec zadania w module, powtarzający się finding z code review, nieoczywisty workflow, który następny agent odkrywałby od zera, łatwą do zapomnienia regułę domenową, albo nową decyzję architektoniczną wpływającą na przyszłe zmiany.

Czego nie robić. Nie dokumentować jednorazowej trywii jako trwałej reguły. Nie pisać generycznych porad pasujących do każdego modułu - wpis ma być konkretny, ugruntowany w tym, co faktycznie się wydarzyło. Nie zapisywać tu stanu bieżącego zadania - to należy do REVIEW. Nie traktować tego jak changelog.

Kto pisze. Wpis dopisuje `plan-implement` na koniec zadania, jako ostatni krok po implementacji i podsumowaniu - dopiero wtedy wiadomo, co okazało się trwałym wzorcem, a co jednorazową okolicznością. Review (`implementation-dod-review`, `dod-reviewer`) może wpis uzupełnić, ale nie jest jego właścicielem.

## Checklista

- SEED ma jawne źródło pochodzenia i jest niezmieniony od zapisania.
- SHAPE ma wypełnione wszystkie jedenaście sekcji, zero otwartych `Block: yes`, niepustą sekcję "Podważenie własnych założeń".
- SHAPE niesie w nagłówku wartość regulatora, a pozycje rozstrzygnięte bez pytania niosą frazę o decyzji agenta.
- PRD nie zawiera nic z czarnej listy: modeli danych, kolumn, migracji, ścieżek kodu, nazw funkcji, bibliotek, deploymentu, sekretów.
- PLAN ma konkretne nazwy plików, funkcji i kontraktów danych w każdym kroku "Zakres zmian", zero TODO, zero otwartych pytań.
- PLAN niesie w linii stanu marker w jednym z dwóch dozwolonych brzmień: plan w toku albo plan zamknięty.
- Sekcja "Fakty" planu zamkniętego ma same pozycje ustaleń, po jednej w linii, każda z identyfikatorem, twierdzeniem, dowodem jednego z pięciu rodzajów i datą sprawdzenia, w trzech polach rozdzielonych kreską pionową.
- Rodzaj dowodu `ZAŁOŻENIE:` stoi wyłącznie przy treści, której faktycznie nie dało się sprawdzić - nie jest workiem na to, czego nie chciało się zweryfikować.
- Sekcja "Otwarte pytania" planu zamkniętego nie ma ani jednej pozycji listy i otwiera się stwierdzeniem braku.
- Wpis `agent_docs/memory` (jeśli powstał) ma komplet pól, jest dopisany - nie nadpisany - i trafił pod właściwą ścieżkę `memory/<grupa>/<moduł>.md`.
- REVIEW mówi, jaki zakres obejmuje werdykt, a zamknięcie bez `ready` albo anulowanie stoi jawnie w linii stanu; wznowienie jest dopisanym wpisem, nie poprawką zamknięcia.
- Żaden z artefaktów nie ma pogrubień w prozie ani pogrubionych etykiet otwierających akapit lub punkt listy - patrz `standard_formatting.md`. Identyfikatory faktów, decyzji i odstępstw (F-1, D-1, O-1) zostają jako zwykły tekst, bo służą do odsyłania, nie do wyróżniania.
