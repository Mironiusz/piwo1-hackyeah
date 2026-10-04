# HackTribe form of the Kraków submission

Polish material for the Kraków submission on HackTribe (check 10.5); kept in Polish as the challenge requires (CLAUDE.md, Language).

Product name EnableMe: Rafał's decision of 2026-10-04, not yet recorded in docs/product/specification.md

Document state: 2026-10-04, 05:30, draft for Rafał. The Kraków submission closes at 11:00 on 2026-10-04 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Before pasting

- The texts below describe the MVP as `docs/product/specification.md`, version 13, and `MVP.md` define it. At about 05:00 on 2026-10-04 the repository held no product code of the backend or of the web frontend (`plans/stage6_official_requirements/STAGE6_OFFICIAL_REQUIREMENTS_SHAPE.md`, Current state). Before pasting, every sentence of the description is checked against the built state with the table Verification of the description below, and a sentence about something that does not work at 10:30 is removed, not softened.
- The exact fields of the HackTribe form are not recorded in the repository. The field list below follows the formal deliverables of the Kraków brief (`docs/hackathon/challenge_requirements.md`, Formal deliverables; `FINAL_CHECKLIST.md`, check 10.5). Rafał matches it with the real form.
- No address, host or login of the hosted demo enters this file or any file of the repository (`CLAUDE.md`, Target environment). A demo link, if the form has a field for it, is typed by hand into the form only.

## Field checklist

| Pole formularza                                                               | Source                                                                                              | Status                                              |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Tytuł projektu                                                                | this file, section Project title                                                                    | szkic - czeka na wybór Rafała                       |
| ID zespołu                                                                    | HackTribe, the team account                                                                         | do uzupełnienia przez Rafała                        |
| Hasło / krótki opis, if the form has such a field                             | this file, section Tagline                                                                          | szkic                                               |
| Opis projektu: problem, grupa docelowa, sposób użycia                         | this file, section Project description                                                              | szkic - czeka na sprawdzenie ze stanem zbudowanym   |
| Źródła danych: pochodzenie, warunki, aktualność, wiarygodność, niedostępność  | Tekst z inicjatywy stage6_official_requirements (9.1 / 9.2 / 9.3) - do wklejenia, gdy będzie gotowy | czeka na 9.1                                        |
| Architektura: komponenty, przepływ danych, dodanie źródła, kategorii i miasta | Tekst z inicjatywy stage6_official_requirements (9.1 / 9.2 / 9.3) - do wklejenia, gdy będzie gotowy | czeka na 9.1                                        |
| Model biznesowy i opcje rozwoju                                               | Tekst z inicjatywy stage6_official_requirements (9.1 / 9.2 / 9.3) - do wklejenia, gdy będzie gotowy | czeka na 9.2 i wybór wariantu przez Rafała          |
| Utrzymanie poza infrastrukturą miasta, koszty, ochrona danych, licencje       | Tekst z inicjatywy stage6_official_requirements (9.1 / 9.2 / 9.3) - do wklejenia, gdy będzie gotowy | czeka na 9.2                                        |
| Co działa, co wymaga pracy, znane ograniczenia                                | Tekst z inicjatywy stage6_official_requirements (9.1 / 9.2 / 9.3) - do wklejenia, gdy będzie gotowy | czeka na 9.3, a 9.3 na 6.5                          |
| Prezentacja PDF, najwyżej 10 slajdów, po polsku                               | `stage8_materials_and_pitch`, check 10.1, the deck in `presentation/`                               | czeka na 10.1 (robi inna sesja)                     |
| Wideo mp4, najwyżej 3 minuty, po polsku, w otwartym repozytorium              | `stage8_materials_and_pitch`, check 10.2                                                            | czeka na 10.2 (robi inna sesja)                     |
| Link do repozytorium kodu, optional                                           | Rafał                                                                                               | czeka na 9.5 (repozytorium publiczne, bez sekretów) |
| Link do demo, optional                                                        | Rafał, typed by hand into the form, never into the repository                                       | czeka na 7.1 i 7.2                                  |
| Zrzuty ekranu i grafiki, optional                                             | `stage8_materials_and_pitch`, from the scenario of check 7.2                                        | czeka na 7.2                                        |

Every text of the form is in Polish (`docs/hackathon/challenge_requirements.md`, Formal deliverables). If the form has a single description field instead of separate ones, the texts of stage6_official_requirements are appended after the description, in the order of the table.

## Project title

Variants, all in Polish:

1. `EnableMe - trasy piesze w Krakowie dopasowane do Twoich potrzeb` - recommended. It says what the product does and for whom, and it repeats the subtitle of the Polish deck (`presentation/src/content/pl.js`, slide title), so the form and the deck carry one message.
2. `EnableMe - Kraków bez barier` - the title of the page of the deck, but it repeats the name of the challenge and says nothing about the solution.
3. `EnableMe - społecznościowa mapa barier i udogodnień w Krakowie` - stresses the community and the facts, but leaves the routes out.

## Tagline

```text
Konkretne bariery i udogodnienia na trasie, każde ze źródłem, datą i statusem - a decyzję zostawiamy Tobie.
```

## Project description

Paste-ready text:

```text
Osoba na wózku, rodzic z wózkiem dziecięcym albo ktoś, komu chodzenie sprawia trudność, rzadko wie z góry, czy trasa po Krakowie jest dla niego do przejścia. Zwykła mapa pokazuje drogę, ale nie schody, wysoki krawężnik czy złą nawierzchnię, a etykieta "dostępne / niedostępne" nie mówi, co dokładnie czeka na miejscu.

EnableMe to społecznościowa aplikacja webowa, projektowana pod telefon, po polsku i angielsku. Użytkownik zaznacza, jakich barier unika i jakich udogodnień potrzebuje (np. winda, rampa, obniżony krawężnik), albo wybiera gotowy zestaw: "Poruszam się na wózku", "Chodzę z wózkiem dziecięcym", "Chodzenie sprawia mi trudność". Nie pytamy o niepełnosprawność, a profil zostaje tylko na urządzeniu.

Aplikacja wyznacza pieszą trasę w całym Krakowie od adresu, punktu na mapie lub bieżącej lokalizacji i omija bariery z profilu, a przy niepotwierdzonej barierze proponuje objazd i mówi dlaczego. Każdy odcinek ma stan: bariera z potrzeb, bez barier (dane pełne), dane niepełne albo brak danych - oznaczony kolorem i dodatkowo ikoną lub wzorem linii. Mapę uzupełnia lista tekstowa: bariery z profilu, bariery spoza profilu, udogodnienia przy trasie. Przy każdym fakcie widać źródło, datę uzyskania lub ostatniego potwierdzenia i status: niezweryfikowane, potwierdzone, sporne albo nieaktualne.

Dane na start pochodzą z OpenStreetMap, więc mapa nie jest pusta od pierwszej minuty. Resztę dokłada społeczność: każdy, z kontem lub bez, zgłasza barierę, udogodnienie albo niedostępny obszar oraz potwierdza lub zaprzecza istniejącym faktom, także tym z OpenStreetMap. Gdy zgłoszenie przeczy danym mapy, widać oba, a trasa trzyma się danych mapy, dopóki zgłoszenie nie zostanie potwierdzone.

Brak informacji nigdy nie jest pokazywany jako potwierdzenie dostępności: odcinek bez pełnych danych nie jest oznaczony jako wolny od barier. Sama aplikacja celuje w WCAG 2.2 AA: główny scenariusz ma działać z klawiatury i z czytnikiem ekranu, a lista trasy jest tekstową alternatywą mapy.

EnableMe nie korzysta z wewnętrznych systemów miasta, a reguły odczytu OpenStreetMap są wszędzie te same, więc rozwiązanie da się przenieść do innego miasta. API projektujemy dla dwóch klientów: aplikacji webowej i klienta HarmonyOS, którego przygotowujemy na wyzwanie Huawei.

Zgłoszenia w demo, w Czyżynach przy Tauron Arenie, to dane przykładowe, wyraźnie tak oznaczone. Znane ograniczenie: demo działa po zwykłym HTTP, więc pod jego linkiem nie zadziała start z bieżącej lokalizacji.
```

### Only if routes with public transport are shown

Routes with public transport of ZTP Kraków are the optional feature O9, in progress within its time box (`docs/product/specification.md`, O9; `MVP.md`, Scope). Leave the description as it is if O9 is not in the demo at 10:30. If it is, make two changes, because the absolute sentence on missing information would no longer be true (`MVP.md`, Known departures from the Kraków brief):

- Replace the first sentence of the paragraph that begins with "Brak informacji" by:

```text
Na trasach pieszych brak informacji nigdy nie jest pokazywany jako potwierdzenie dostępności: odcinek bez pełnych danych nie jest oznaczony jako wolny od barier.
```

- Append to the last paragraph:

```text
Opcjonalnie trasa może użyć tramwajów i autobusów ZTP Kraków (GTFS). Przejazd, dla którego GTFS nie podaje danych o dostępności, liczymy jako dostępny - to świadomy wyjątek i znane ograniczenie prototypu.
```

## Character count

Counted on the paste-ready description above, without the optional O9 changes: 2479 characters with spaces and line breaks, 2119 without spaces and line breaks. The O9 changes add about 225 characters.

## Verification of the description

Each claim, the rule behind it and the check of `FINAL_CHECKLIST.md` that proves it works. A claim whose check is not ticked at 10:30 is verified by hand on the running demo or removed.

| Claim of the description                                                                        | Rule                                                                             | Check         |
| ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------- |
| Profile of barriers and amenities, three presets, no question about a disability, device only   | specification M1                                                                 | 6.1           |
| Web app for a phone, Polish and English                                                         | specification, Area, device and language                                         | 6.3           |
| Walking route in the whole of Kraków from an address, a point on the map or the location        | specification M2, Address search                                                 | 2.4, 4.1, 6.1 |
| Route avoids barriers of the profile, detour proposed around an unverified barrier              | specification M2                                                                 | 4.1, 6.1      |
| Four segment states, color plus icon or line pattern                                            | specification M7                                                                 | 4.1, 6.1, 6.5 |
| Text list in three groups                                                                       | specification M8                                                                 | 4.1, 6.1      |
| Source, date and status on every fact, four statuses                                            | specification M4, M10                                                            | 5.1, 5.2, 6.2 |
| OpenStreetMap data from the start                                                               | specification M6                                                                 | 3.1, 3.2      |
| Reports of barriers, amenities and areas, with or without an account                            | specification M3, M5, M9                                                         | 5.1, 6.2      |
| Confirmations and denials, OpenStreetMap facts included                                         | specification M4                                                                 | 5.2, 6.2      |
| Contradiction between a report and the map data, the route follows the map data until confirmed | specification M2, M4, M7                                                         | 3.3, 7.3      |
| Missing information never shown as accessible                                                   | specification M7, M10                                                            | 7.3           |
| WCAG 2.2 AA as the goal, keyboard, screen reader, list as the text alternative                  | specification M8, M10; `PRODUCT.md`, Accessibility & Inclusion                   | 6.5, 9.3      |
| No internal systems of the city                                                                 | `CLAUDE.md`, What we are building                                                | -             |
| Can be moved to another city                                                                    | inference from M6, whose tag rules name no city; not a rule of the specification | 9.1           |
| One API for two clients, the HarmonyOS client in preparation                                    | `PRODUCT.md`, Stack and Operating Context; `MVP.md`, Goal and deadline           | 8.1, 8.2      |
| Sample reports in Czyżyny marked as sample data                                                 | specification M10; `MVP.md`, Scope                                               | 3.3, 6.2      |
| Plain HTTP, no start from the current location on the hosted link                               | `MVP.md`, Known departures from the Kraków brief                                 | 7.1           |

## Left out on purpose

- Photos in reports. They are the optional feature O2, outside the MVP (`docs/product/specification.md`, O2; `MVP.md`, Scope). Mention them only if O2 is built and works in the demo.
- Every other optional feature O1, O3 - O8, the points, the ranking and the rewards included.
- The business model. It is chosen by Rafał in `stage6_official_requirements` from the variants of check 9.2, and nothing of it enters a description before that choice (`plans/stage6_official_requirements/STAGE6_OFFICIAL_REQUIREMENTS_SHAPE.md`, Domain rules).
- Data sources beyond OpenStreetMap, the architecture, the costs, the licences and the list of what works - the texts of checks 9.1 - 9.3.
- Moderation and the weights of votes. Both are true of the MVP (M4, M9, M11) and left out only for length.

## Open questions for Rafał

1. Team ID: not in the repository, to be filled in from HackTribe.
2. Title: variant 1 is recommended. If the deck of check 10.1 changes its subtitle, the title follows it, or the other way round.
3. Photos: the brief of this task asked for community reports with photos, but photos are O2, outside the MVP. Left out; confirm, or say if O2 is being built after all.
4. Built state: which features of the table Verification of the description work on the hosted link at 10:30. A sentence about a feature that does not work is removed before pasting.
5. HarmonyOS client: check 8.1 has not chosen the client yet, and `mobile_app/` runs on bundled sample data without the programming interface (`plans/stage6_official_requirements/STAGE6_OFFICIAL_REQUIREMENTS_SHAPE.md`, Current state). The sentence says the API is designed for two clients, which `PRODUCT.md` supports; if the client does not call the API by 10:30, keep the sentence as it is and do not strengthen it.
6. O9: whether routes with public transport are in the demo at 10:30, which decides the optional changes above.
7. Form fields: whether the form has separate fields for the data sources, the business model and the rest, and whether any field has a character limit. The description fits in 2500 characters with spaces.
8. Business model in the description: the Kraków task description gives it 20% and says business potential weighs strongly (`docs/hackathon/challenge_requirements.md`, Judging). After the choice of check 9.2, add one sentence about it to the description, or leave it to its own field.
9. Product name: EnableMe is not yet in `docs/product/specification.md`; `CLAUDE.md` and `PRODUCT.md` still say the name is not chosen, and `mobile_app/README.md` says AccessWay. Recording it is for `repository_consistency`, check 1.6.
