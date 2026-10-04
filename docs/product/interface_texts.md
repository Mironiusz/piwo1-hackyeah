# Texts of the interface in Polish and English

Document state: 2026-10-04, proposed by the agent from the mocks of the views; the rules of the wording and the open choices decided by the frontend person on 2026-10-04

## Why this document exists

The interface is in Polish and English (`docs/product/specification.md`, M10). This document is the one place where both builders of the frontend take their words from: every label, name and message of the views of `docs/product/views.md`, in both languages. It adds no product rule. In case of a discrepancy the specification prevails, then the list of views.

The Polish texts come from the mocks in `.impeccable/briefs/views/`, which the user reviewed on 2026-10-03. The English texts and the texts of the states that have no mock were written by the agent. The Polish texts are an exception to the rule that the repository is in English: they are content of the product, not documentation.

The keys are proposals for the names the frontend uses in its two dictionaries. Where a key ends with a code - a fact type, a status, a source, a segment state, an error - the code is the one of `docs/product/api_contract.md`.

## Rules of the wording

- Plain words, short sentences, no jargon. The interface says what it knows and what it does not know.
- The interface never says OpenStreetMap. It says map data, in Polish "dane mapy". The name stands only in the attribution on the map and once on the page about the data (M10).
- No verdict about a place and no word that reads as one: the texts name facts and unknowns.
- The Polish texts address the person directly and use no verb form that assumes a gender. A form such as "zalogowany" or "zrobiłeś" is replaced by a neutral one.
- A text contains none of the characters `docs/standards/standard_formatting.md` forbids: no ellipsis, no arrow, no typographic dash or quotation mark. A range is written with the word "do" or "to".
- A message says what happened and what the person can do next. It does not blame the person and shows no code.

## Formats

- A date is a calendar day. Polish: `3.10.2026`. English: `3 Oct 2026`.
- A distance under 1000 m is in metres: `400 m`. From 1000 m it is in kilometres with one decimal place: Polish `1,3 km`, English `1.3 km`.
- The day from which the next vote is accepted is a calendar day, in the format of a date: Polish `5.10.2026`, English `5 Oct 2026`.
- A placeholder is written in braces, for example `{date}`.
- Polish has three plural forms and English two. A text with a number names its forms in the order one, few, many for Polish and one, other for English.

## Terms

Fact types, shown as the name of a row and in the lists of the needs:

| Key                       | Polish               | English            |
| ------------------------- | -------------------- | ------------------ |
| `type.stairs`             | Schody               | Stairs             |
| `type.high_kerb`          | Wysoki krawężnik     | High kerb          |
| `type.poor_surface`       | Zła nawierzchnia     | Poor surface       |
| `type.steep_incline`      | Strome nachylenie    | Steep incline      |
| `type.narrow_passage`     | Wąskie przejście     | Narrow passage     |
| `type.ramp`               | Rampa                | Ramp               |
| `type.elevator`           | Winda                | Elevator           |
| `type.lowered_kerb`       | Obniżony krawężnik   | Lowered kerb       |
| `type.accessible_toilet`  | Dostępna toaleta     | Accessible toilet  |
| `type.rest_place`         | Miejsce odpoczynku   | Rest place         |
| `type.handrail_at_stairs` | Poręcz przy schodach | Handrail at stairs |

Statuses, sources and kinds:

| Key                       | Polish                 | English     |
| ------------------------- | ---------------------- | ----------- |
| `status.unverified`       | niezweryfikowane       | unverified  |
| `status.confirmed`        | potwierdzone           | confirmed   |
| `status.disputed`         | sporne                 | disputed    |
| `status.outdated`         | nieaktualne            | outdated    |
| `source.openstreetmap`    | dane mapy              | map data    |
| `source.user_report`      | zgłoszenie             | report      |
| `source.user_report.full` | zgłoszenie użytkownika | user report |
| `kind.barrier`            | bariera                | barrier     |
| `kind.amenity`            | udogodnienie           | amenity     |
| `kind.area`               | obszar                 | area        |
| `sample.mark`             | dane przykładowe       | sample data |
| `sample.badge`            | Dane przykładowe       | Sample data |

Segment states, in the legend:

| Key                    | Polish                   | English                          |
| ---------------------- | ------------------------ | -------------------------------- |
| `segment.barrier`      | bariera z potrzeb        | barrier from your needs          |
| `segment.no_barrier`   | bez barier, dane pełne   | no barriers, complete data       |
| `segment.partial_data` | dane niepełne            | partial data                     |
| `segment.no_data`      | brak danych              | no data                          |
| `segment.not_assessed` | trasa bez oceny odcinków | route without assessed stretches |

Names with a number:

| Key               | Polish, one, few, many                             | English, one, other        |
| ----------------- | -------------------------------------------------- | -------------------------- |
| `count.barriers`  | {n} bariera, {n} bariery, {n} barier               | {n} barrier, {n} barriers  |
| `count.amenities` | {n} udogodnienie, {n} udogodnienia, {n} udogodnień | {n} amenity, {n} amenities |
| `count.steps`     | {n} stopień, {n} stopnie, {n} stopni               | {n} step, {n} steps        |
| `count.results`   | {n} wynik, {n} wyniki, {n} wyników                 | {n} result, {n} results    |

A row of stairs with a known number of steps reads `Schody, {count.steps}` and `Stairs, {count.steps}`. A row of an area reads `Obszar: {type}, {radius} m` and `Area: {type}, {radius} m`, with the type in lower case.

## Shell, V-1 and V-10

| Key                | Polish                      | English                  |
| ------------------ | --------------------------- | ------------------------ |
| `app.name`         | EnableMe                    | EnableMe                 |
| `nav.map`          | Mapa                        | Map                      |
| `nav.report`       | Zgłoś                       | Report                   |
| `nav.needs`        | Potrzeby                    | Needs                    |
| `menu.open`        | Menu                        | Menu                     |
| `menu.close`       | Zamknij menu                | Close menu               |
| `menu.account`     | Konto                       | Account                  |
| `menu.account.in`  | zalogowano jako {pseudonym} | logged in as {pseudonym} |
| `menu.account.out` | bez konta                   | no account               |
| `menu.language`    | Język                       | Language                 |
| `menu.privacy`     | Informacja o prywatności    | Privacy information      |
| `menu.data`        | O danych                    | About the data           |
| `menu.data.date`   | dane mapy z dnia {date}     | map data from {date}     |
| `menu.moderation`  | Moderacja                   | Moderation               |
| `map.data_date`    | Dane mapy z dnia {date}.    | Map data from {date}.    |
| `action.back`      | Wróć                        | Back                     |
| `action.cancel`    | Anuluj                      | Cancel                   |
| `action.next`      | Dalej                       | Next                     |
| `action.change`    | Zmień                       | Change                   |
| `action.show`      | Pokaż                       | Show                     |
| `action.retry`     | Spróbuj ponownie            | Try again                |
| `field.optional`   | (opcjonalnie)               | (optional)               |

The names of the two languages are never translated: `Polski` and `English`. The attribution on the map is the same in both languages: `© OpenStreetMap contributors`.

## Needs, V-2

| Key                       | Polish                        | English                     |
| ------------------------- | ----------------------------- | --------------------------- |
| `needs.title`             | Twoje potrzeby                | Your needs                  |
| `needs.presets`           | Zacznij od gotowego zestawu   | Start from a ready set      |
| `needs.preset.wheelchair` | Poruszam się na wózku         | I use a wheelchair          |
| `needs.preset.stroller`   | Chodzę z wózkiem dziecięcym   | I walk with a baby stroller |
| `needs.preset.walking`    | Chodzenie sprawia mi trudność | Walking is difficult for me |
| `needs.avoid`             | Unikam                        | I avoid                     |
| `needs.need`              | Potrzebuję                    | I need                      |
| `needs.skip`              | Pomiń                         | Skip                        |
| `needs.done`              | Gotowe                        | Done                        |

- `needs.intro`
  - PL: Zaznacz, czego unikasz i czego potrzebujesz po drodze. Nie pytamy o niepełnosprawność. Te ustawienia zostają tylko na tym urządzeniu.
  - EN: Mark what you avoid and what you need on the way. We do not ask about disability. These settings stay only on this device.
- `needs.no_barrier`
  - PL: Bez żadnej zaznaczonej bariery pokażemy trasę, ale nie ocenimy jej odcinków.
  - EN: With no barrier marked we will show a route, but we will not assess its stretches.

## Map of facts, V-3

| Key                 | Polish                       | English                           |
| ------------------- | ---------------------------- | --------------------------------- |
| `facts.plan`        | Dokąd idziesz? Wyznacz trasę | Where are you going? Plan a route |
| `facts.scope.needs` | Z moich potrzeb              | From my needs                     |
| `facts.scope.all`   | Wszystkie                    | All                               |
| `facts.list`        | Fakty w tym miejscu          | Facts in this area                |

- `facts.none`
  - PL: W tym miejscu nie znamy żadnych barier ani udogodnień z Twoich potrzeb. To nie znaczy, że ich tu nie ma.
  - EN: We know of no barriers or amenities from your needs in this area. That does not mean there are none.
- `facts.none_at_all`
  - PL: W tym miejscu nie znamy żadnych barier ani udogodnień. To nie znaczy, że ich tu nie ma.
  - EN: We know of no barriers or amenities in this area. That does not mean there are none.
- `facts.too_many`
  - PL: Tu jest za dużo faktów, żeby pokazać wszystkie. Przybliż mapę.
  - EN: There are too many facts here to show them all. Zoom in.
- `facts.empty_needs`
  - PL: Twoje potrzeby są puste, więc pokazujemy wszystkie fakty.
  - EN: Your needs are empty, so we show every fact.

## Route planning and address search, V-4 and V-8

| Key                        | Polish                              | English                            |
| -------------------------- | ----------------------------------- | ---------------------------------- |
| `plan.title`               | Zaplanuj trasę                      | Plan a route                       |
| `plan.start`               | Start                               | Start                              |
| `plan.destination`         | Cel                                 | Destination                        |
| `plan.my_location`         | Moja lokalizacja                    | My location                        |
| `plan.address`             | Adres                               | Address                            |
| `plan.map_point`           | Punkt na mapie                      | Point on the map                   |
| `plan.change_needs`        | Zmień potrzeby                      | Change needs                       |
| `plan.submit`              | Wyznacz trasę                       | Plan route                         |
| `plan.set_point`           | Ustaw ten punkt                     | Set this point                     |
| `plan.loading`             | Wyznaczamy trasę.                   | Planning the route.                |
| `search.title.start`       | Start: wyszukaj adres               | Start: search for an address       |
| `search.title.destination` | Cel: wyszukaj adres                 | Destination: search for an address |
| `search.field`             | Adres albo nazwa miejsca w Krakowie | Address or place name in Kraków    |
| `search.submit`            | Szukaj                              | Search                             |
| `search.count`             | {count.results} w Krakowie          | {count.results} in Kraków          |
| `search.map_point`         | Wskaż punkt na mapie                | Pick a point on the map            |
| `search.close`             | Zamknij wyszukiwanie                | Close search                       |

- `plan.needs_summary`
  - PL: Trasa dla Twoich potrzeb: {count.barriers}, {count.amenities}.
  - EN: Route for your needs: {count.barriers}, {count.amenities}.
- `plan.unavailable.title`, for the error `routing_unavailable`
  - PL: Nie możemy teraz wyznaczyć trasy.
  - EN: We cannot plan a route right now.
- `plan.unavailable.body`
  - PL: Usługa wyznaczania tras nie odpowiada. Nie pokazujemy trasy zgadywanej. Spróbuj ponownie za chwilę.
  - EN: The routing service is not answering. We show no guessed route. Try again in a moment.
- `plan.outside`
  - PL: Ten punkt leży poza Krakowem. Trasy działają tylko w granicach Krakowa.
  - EN: This point is outside Kraków. Routes work only within Kraków.
- `plan.location_refused`
  - PL: Nie mamy dostępu do Twojej lokalizacji. Wpisz adres albo wskaż punkt na mapie.
  - EN: We have no access to your location. Enter an address or pick a point on the map.
- `plan.location_failed`
  - PL: Nie udało się ustalić Twojej lokalizacji. Wpisz adres albo wskaż punkt na mapie.
  - EN: We could not find your location. Enter an address or pick a point on the map.
- `plan.location_insecure`, when the page has no secure connection
  - PL: Przeglądarka podaje lokalizację tylko stronie z bezpiecznym połączeniem, a ta strona go nie ma. Wpisz adres albo wskaż punkt na mapie.
  - EN: Your browser gives the location only to a page with a secure connection, and this page has none. Enter an address or pick a point on the map.
- `plan.pick_point`
  - PL: Przesuń mapę, aż znacznik na środku wskaże to miejsce. Na klawiaturze przesuwasz mapę strzałkami.
  - EN: Move the map until the marker in the middle points at the place. On a keyboard you move the map with the arrow keys.
- `search.hint`
  - PL: Szukamy po naciśnięciu Enter albo przycisku. Niczego nie podpowiadamy w trakcie pisania.
  - EN: We search when you press Enter or the button. We suggest nothing while you type.
- `search.pick`
  - PL: Wybierz wynik z listy. Sami niczego nie wybieramy, także gdy wynik jest jeden.
  - EN: Pick a result from the list. We choose nothing for you, also when there is one result.
- `search.none.title`
  - PL: Nic nie znaleźliśmy w Krakowie.
  - EN: We found nothing in Kraków.
- `search.none.body`
  - PL: Trasy działają tylko w granicach Krakowa. Sprawdź pisownię, wpisz samą ulicę albo samą nazwę miejsca.
  - EN: Routes work only within Kraków. Check the spelling, or enter only the street or only the name of the place.
- `search.none.point`
  - PL: Punkt nie został ustawiony. Możesz też wskazać go na mapie.
  - EN: The point is not set. You can also pick it on the map.
- `search.unavailable`, for the error `address_search_unavailable`
  - PL: Wyszukiwarka adresów teraz nie odpowiada. Spróbuj ponownie za chwilę albo wskaż punkt na mapie.
  - EN: The address search is not answering right now. Try again in a moment or pick a point on the map.
- `search.invalid`, for the error `invalid_search_text`
  - PL: Wpisz adres albo nazwę miejsca, najwyżej 200 znaków.
  - EN: Enter an address or a place name, at most 200 characters.

## Route result and legend, V-5 and V-9

| Key                           | Polish                                                 | English                                           |
| ----------------------------- | ------------------------------------------------------ | ------------------------------------------------- |
| `route.needs`                 | Potrzeby: {count.barriers}                             | Needs: {count.barriers}                           |
| `route.needs.none`            | Potrzeby: brak barier                                  | Needs: no barriers                                |
| `route.change`                | Zmień trasę                                            | Change route                                      |
| `route.tile.barriers`         | bariera z potrzeb, bariery z potrzeb, barier z potrzeb | barrier from your needs, barriers from your needs |
| `route.tile.no_data`          | bez danych                                             | without data                                      |
| `route.tile.length`           | cała trasa                                             | whole route                                       |
| `route.tile.not_assessed`     | bez oceny                                              | not assessed                                      |
| `route.tile.not_assessed.why` | potrzeby nie mają żadnej bariery                       | your needs have no barrier                        |
| `route.group.profile`         | Z Twoich potrzeb                                       | From your needs                                   |
| `route.group.additional`      | Dodatkowe bariery                                      | Additional barriers                               |
| `route.group.amenities`       | Udogodnienia na trasie                                 | Amenities on the route                            |
| `route.group.all`             | Bariery na trasie                                      | Barriers on the route                             |
| `route.from_start`            | {distance} od startu                                   | {distance} from the start                         |
| `route.alternative.back`      | Wróć do pierwszej trasy                                | Back to the first route                           |
| `route.set_needs`             | Ustaw potrzeby                                         | Set your needs                                    |
| `route.replanning`            | Wyznaczamy trasę ponownie.                             | Planning the route again.                         |

- `route.no_data_note`
  - PL: Niektóre odcinki tej trasy nie mają danych. Nie wiemy, czy są tam bariery.
  - EN: Some stretches of this route have no data. We do not know whether there are barriers on them.
- `route.wheelchair_no`
  - PL: Fragment tej trasy jest w danych mapy oznaczony jako niedostępny dla wózków.
  - EN: A part of this route is marked in the map data as not accessible for wheelchairs.
- `route.alternative`
  - PL: Trasa alternatywna omija tę barierę i jest o {distance} dłuższa. Powód: {type}, status {status}.
  - EN: An alternative route avoids this barrier and is {distance} longer. Reason: {type}, status {status}.
- `route.alternative.shown`
  - PL: To trasa alternatywna. Omija bariery, których nikt jeszcze nie potwierdził albo które są sporne.
  - EN: This is the alternative route. It avoids barriers that nobody has confirmed yet or that are disputed.
- `route.none.title`
  - PL: Nie ma trasy bez barier z Twoich potrzeb.
  - EN: There is no route without barriers from your needs.
- `route.none.body`
  - PL: Każda droga do tego celu prowadzi przez barierę z Twoich potrzeb. Pokazujemy trasę, na której takich barier jest najmniej: {n}.
  - EN: Every way to this destination crosses a barrier from your needs. We show the route with the fewest such barriers: {n}.
- `route.empty.profile`
  - PL: Nie znamy żadnych barier z Twoich potrzeb na tej trasie. {distance} trasy nie ma danych.
  - EN: We know of no barriers from your needs on this route. {distance} of the route has no data.
- `route.empty.additional`
  - PL: Nie znamy żadnych innych barier na tej trasie. {distance} trasy nie ma danych.
  - EN: We know of no other barriers on this route. {distance} of the route has no data.
- `route.empty.amenities`
  - PL: Żadne udogodnienie z Twoich potrzeb nie leży bliżej niż 50 m od tej trasy.
  - EN: No amenity from your needs lies closer than 50 m to this route.
- `route.empty.amenities.no_needs`
  - PL: Twoje potrzeby nie zawierają żadnego udogodnienia, więc nie mamy czego tu pokazać.
  - EN: Your needs include no amenity, so there is nothing to show here.
- `route.not_assessed`
  - PL: Nie oceniamy odcinków tej trasy, bo Twoje potrzeby nie zawierają żadnej bariery. To nie znaczy, że trasa jest wolna od barier: znane bariery są na liście niżej.
  - EN: We do not assess the stretches of this route, because your needs include no barrier. That does not mean the route is free of barriers: the known barriers are in the list below.

## Fact detail and votes, V-6

| Key                 | Polish                   | English                 |
| ------------------- | ------------------------ | ----------------------- |
| `fact.source`       | Źródło                   | Source                  |
| `fact.status`       | Status                   | Status                  |
| `fact.confirmed_on` | Ostatnio potwierdzone    | Last confirmed          |
| `fact.edited_on`    | Ostatnia zmiana na mapie | Last changed on the map |
| `fact.description`  | Opis                     | Description             |
| `fact.steps`        | Liczba stopni            | Number of steps         |
| `fact.radius`       | Promień                  | Radius                  |
| `fact.close`        | Zamknij szczegóły        | Close details           |
| `vote.confirm`      | Nadal jest               | Still here              |
| `vote.deny`         | Już nie ma               | No longer here          |
| `flag.action`       | Zgłoś do moderacji       | Report to moderation    |
| `flag.done`         | Zgłoszone do moderacji.  | Reported to moderation. |

- `vote.question.barrier`
  - PL: Czy ta bariera nadal tu jest?
  - EN: Is this barrier still here?
- `vote.question.amenity`
  - PL: Czy to udogodnienie nadal tu jest?
  - EN: Is this amenity still here?
- `vote.question.area`
  - PL: Czy ten obszar nadal jest niedostępny?
  - EN: Is this area still inaccessible?
- `vote.own.confirm`
  - PL: Twój głos: nadal jest.
  - EN: Your vote: still here.
- `vote.own.deny`
  - PL: Twój głos: już nie ma.
  - EN: Your vote: no longer here.
- `vote.own.saved`
  - PL: Zapisaliśmy go {date}. Kolejny głos na ten fakt będzie możliwy następnego dnia.
  - EN: We saved it on {date}. You can vote on this fact again the next day.
- `vote.saved`, announced after a vote
  - PL: Głos zapisany. Status: {status}.
  - EN: Vote saved. Status: {status}.
- `vote.too_soon`, for the error `vote_too_soon`
  - PL: Twój głos na ten fakt jest już zapisany. Kolejny będzie możliwy od {day}.
  - EN: Your vote on this fact is already saved. The next one is possible from {day}.
- `fact.outdated`
  - PL: Ten fakt jest nieaktualny: przeważają zgłoszenia, że tego już nie ma. Jeśli nadal jest, potwierdź go.
  - EN: This fact is outdated: reports that it is gone prevail. If it is still here, confirm it.
- `fact.contradiction`
  - PL: Dane mapy pokazują tu co innego. Trasa trzyma się danych mapy, dopóki to zgłoszenie nie zostanie potwierdzone.
  - EN: The map data show something else here. The route follows the map data until this report is confirmed.
- `fact.gone`, for the error `fact_not_found`
  - PL: Tej informacji już nie ma.
  - EN: This information is no longer available.
- `flag.confirm`
  - PL: Zgłosić tę treść do moderacji?
  - EN: Report this content to moderation?

## Reporting, V-7

| Key                        | Polish                     | English                         |
| -------------------------- | -------------------------- | ------------------------------- |
| `report.step`              | Krok {n} z {total}         | Step {n} of {total}             |
| `report.cancel`            | Anuluj zgłoszenie          | Cancel report                   |
| `report.kind.title`        | Co zgłaszasz?              | What are you reporting?         |
| `report.kind.barrier`      | Barierę                    | A barrier                       |
| `report.kind.amenity`      | Udogodnienie               | An amenity                      |
| `report.kind.area`         | Obszar                     | An area                         |
| `report.point.barrier`     | Wskaż miejsce bariery      | Point at the barrier            |
| `report.point.amenity`     | Wskaż miejsce udogodnienia | Point at the amenity            |
| `report.point.area`        | Wskaż środek obszaru       | Point at the middle of the area |
| `report.type.barrier`      | Jaka to bariera?           | Which barrier is it?            |
| `report.type.amenity`      | Jakie to udogodnienie?     | Which amenity is it?            |
| `report.area.title`        | Jaki to obszar?            | What kind of area is it?        |
| `report.area.radius`       | Promień obszaru            | Radius of the area              |
| `report.area.type`         | Co utrudnia przejście?     | What makes it hard to pass?     |
| `report.existing.title`    | Czy to jest już zgłoszone? | Is this already reported?       |
| `report.existing.distance` | {n} m stąd                 | {n} m from here                 |
| `report.existing.same`     | To to samo                 | It is the same                  |
| `report.existing.other`    | To coś innego              | It is something else            |
| `report.summary.title`     | Sprawdź zgłoszenie         | Check your report               |
| `report.summary.kind`      | Rodzaj                     | Kind                            |
| `report.summary.type`      | Typ                        | Type                            |
| `report.summary.place`     | Miejsce                    | Place                           |
| `report.summary.point`     | punkt na mapie powyżej     | the point on the map above      |
| `report.save`              | Zapisz zgłoszenie          | Save report                     |
| `report.saved.title`       | Zgłoszenie zapisane        | Report saved                    |
| `report.again`             | Zgłoś kolejne              | Report another                  |
| `report.to_map`            | Wróć do mapy               | Back to the map                 |

- `report.kind.barrier.hint`
  - PL: schody, wysoki krawężnik, zła nawierzchnia, strome nachylenie, wąskie przejście
  - EN: stairs, high kerb, poor surface, steep incline, narrow passage
- `report.kind.amenity.hint`
  - PL: rampa, winda, obniżony krawężnik, dostępna toaleta, miejsce odpoczynku, poręcz
  - EN: ramp, elevator, lowered kerb, accessible toilet, rest place, handrail
- `report.kind.area.hint`
  - PL: większy niedostępny fragment, na przykład remont chodnika
  - EN: a larger inaccessible stretch, for example pavement works
- `report.point.hint`
  - PL: Przesuń mapę, aż znacznik na środku wskaże to miejsce. Na klawiaturze przesuwasz mapę strzałkami.
  - EN: Move the map until the marker in the middle points at the place. On a keyboard you move the map with the arrow keys.
- `report.point.location`
  - PL: Przycisk Moja lokalizacja tylko przesuwa mapę na tym urządzeniu. Zapisujemy punkt, który ustawisz, a nie Twoje położenie.
  - EN: The My location button only moves the map on this device. We save the point you set, not your position.
- `report.description.hint`
  - PL: Opis jest publiczny. Nie podawaj danych osób.
  - EN: The description is public. Do not give personal details of anyone.
- `report.existing.body`
  - PL: W promieniu około 15 m od Twojego punktu są już fakty tego samego typu. Jeśli to to samo miejsce, potwierdzisz istniejący fakt zamiast dodawać nowy.
  - EN: Within about 15 m of your point there are already facts of the same type. If it is the same place, you will confirm the existing fact instead of adding a new one.
- `report.existing.confirmed`
  - PL: Potwierdziliśmy istniejący fakt zamiast dodawać nowy.
  - EN: We confirmed the existing fact instead of adding a new one.
- `report.summary.note`
  - PL: Po zapisaniu nikt nie zmieni tego zgłoszenia, Ty też nie. Inni zobaczą je bez żadnej informacji o autorze.
  - EN: After saving, nobody can change this report, you included. Others will see it without any information about its author.
- `report.saved.body`
  - PL: Zgłoszenie jest już na mapie. Status: niezweryfikowane.
  - EN: The report is on the map now. Status: unverified.
- `report.saved.hint`
  - PL: Inni mogą teraz potwierdzić, że to nadal jest, albo zgłosić, że tego już nie ma. Od tego zależy status.
  - EN: Others can now confirm that it is still there or report that it is gone. The status depends on that.
- `report.failed`
  - PL: Nie udało się zapisać zgłoszenia. Spróbuj ponownie, niczego nie zapiszemy dwa razy.
  - EN: We could not save the report. Try again, nothing will be saved twice.

The radii of an area are written the same in both languages: `10 m`, `25 m`, `50 m`, `100 m`.

## Account, V-11

| Key                      | Polish                    | English                         |
| ------------------------ | ------------------------- | ------------------------------- |
| `account.title`          | Konto                     | Account                         |
| `account.pseudonym`      | Pseudonim                 | Pseudonym                       |
| `account.password`       | Hasło                     | Password                        |
| `account.log_in`         | Zaloguj się               | Log in                          |
| `account.no_account`     | Nie masz konta?           | No account yet?                 |
| `account.create`         | Załóż konto               | Create an account               |
| `account.have_account`   | Mam już konto             | I already have an account       |
| `account.logged_in_as`   | Zalogowano jako           | Logged in as                    |
| `account.log_out`        | Wyloguj się               | Log out                         |
| `account.delete.section` | Usunięcie konta           | Deleting the account            |
| `account.delete`         | Usuń konto                | Delete account                  |
| `account.delete.title`   | Usunąć konto {pseudonym}? | Delete the account {pseudonym}? |
| `account.delete.goes`    | Co zniknie                | What goes                       |
| `account.delete.stays`   | Co zostanie               | What stays                      |
| `account.delete.final`   | Tego nie da się cofnąć.   | This cannot be undone.          |
| `account.deleted`        | Konto zostało usunięte.   | The account has been deleted.   |

- `account.intro`
  - PL: Konto to pseudonim i hasło, bez adresu e-mail. Zgłaszać i głosować możesz też bez konta.
  - EN: An account is a pseudonym and a password, without an email address. You can also report and vote without an account.
- `account.create.intro`
  - PL: Wystarczy pseudonim i hasło. Nie pytamy o adres e-mail ani o niepełnosprawność.
  - EN: A pseudonym and a password are enough. We do not ask for an email address or about disability.
- `account.pseudonym.rule`
  - PL: 3 do 30 znaków: litery, cyfry, podkreślenie i myślnik.
  - EN: 3 to 30 characters: letters, digits, the underscore and the hyphen.
- `account.pseudonym.taken`, for the error `pseudonym_taken`
  - PL: Ten pseudonim jest już zajęty. Wybierz inny.
  - EN: This pseudonym is already taken. Choose another one.
- `account.password.rule`
  - PL: Co najmniej 5 znaków. Mogą być spacje.
  - EN: At least 5 characters. Spaces are allowed.
- `account.no_recovery.title`
  - PL: Hasła nie da się odzyskać.
  - EN: The password cannot be recovered.
- `account.no_recovery.body`
  - PL: Nie mamy Twojego adresu e-mail, więc jeśli zapomnisz hasła, stracisz dostęp do konta na stałe.
  - EN: We do not have your email address, so if you forget the password, you lose access to the account for good.
- `account.invalid_credentials`, for the error `invalid_credentials`
  - PL: Pseudonim i hasło do siebie nie pasują. Sprawdź oba i spróbuj ponownie.
  - EN: The pseudonym and the password do not match. Check both and try again.
- `account.session`
  - PL: Logowanie na tym urządzeniu trwa 24 godziny od ostatniego użycia aplikacji, także po zamknięciu przeglądarki.
  - EN: You stay logged in on this device for 24 hours after you last used the app, also after closing the browser.
- `account.needs`
  - PL: Twoje potrzeby nie są częścią konta. Zostają tylko na tym urządzeniu.
  - EN: Your needs are not part of the account. They stay only on this device.
- `account.delete.intro`
  - PL: Usuniemy konto i pseudonim. Twoje zgłoszenia i głosy zostaną, odłączone od Ciebie.
  - EN: We will remove the account and the pseudonym. Your reports and votes stay, detached from you.
- `account.delete.goes.account`
  - PL: Konto i możliwość logowania.
  - EN: The account and the ability to log in.
- `account.delete.goes.pseudonym`
  - PL: Pseudonim {pseudonym}. Ktoś inny będzie mógł go potem zająć.
  - EN: The pseudonym {pseudonym}. Someone else can take it afterwards.
- `account.delete.stays.content`
  - PL: Twoje zgłoszenia i głosy, odłączone od Ciebie. Nadal liczą się do statusów.
  - EN: Your reports and votes, detached from you. They still count towards statuses.
- `account.delete.stays.needs`
  - PL: Twoje potrzeby na tym urządzeniu, bo nie są częścią konta.
  - EN: Your needs on this device, because they are not part of the account.
- `account.session_expired`, for the error `session_expired`
  - PL: Sesja wygasła. Zaloguj się ponownie i powtórz ostatnią czynność.
  - EN: Your session has ended. Log in again and repeat the last action.

## Privacy information, V-12

| Key                | Polish                       | English                 |
| ------------------ | ---------------------------- | ----------------------- |
| `privacy.kept`     | Co przechowujemy             | What we keep            |
| `privacy.not_kept` | Czego nie przechowujemy      | What we do not keep     |
| `privacy.others`   | Kto jeszcze widzi Twoje dane | Who else sees your data |
| `privacy.demo`     | To demo                      | This demo               |

- `privacy.intro`
  - PL: Co o Tobie przechowujemy, po co i jak długo, oraz czego nie przechowujemy.
  - EN: What we keep about you, why and for how long, and what we do not keep.
- `privacy.kept.account`
  - PL: Pseudonim i hasło konta. Po to, żeby rozpoznać Twoje konto. Do chwili, gdy je usuniesz.
  - EN: The pseudonym and the password of an account. To recognize your account. Until you delete it.
- `privacy.kept.vote`
  - PL: Identyfikator głosu bez konta. Nieodwracalny skrót adresu IP i cech przeglądarki, żeby odróżnić jedną osobę bez konta od drugiej. Do usunięcia dema i wszystkich jego danych 4 października 2026. To dane osobowe w postaci spseudonimizowanej, nie dane anonimowe.
  - EN: The identifier of a vote without an account. An irreversible digest of the IP address and of browser characteristics, to tell one person without an account from another. Until the demo and all its data are deleted on 4 October 2026. It is pseudonymized personal data, not anonymous data.
- `privacy.kept.route_log`
  - PL: Punkty zapytań o trasę, także Twojej bieżącej lokalizacji, w dzienniku usługi wyznaczania tras. Żeby w wersji demonstracyjnej dało się sprawdzić, jak działa wyznaczanie tras. Do usunięcia dema i wszystkich jego danych 4 października 2026.
  - EN: The points of route requests, your current location among them, in the log of the route planning service. To check how route planning works in this demo. Until the demo and all its data are deleted on 4 October 2026.
- `privacy.not_kept.needs`
  - PL: Twoich potrzeb. Zostają tylko na Twoim urządzeniu i nie są częścią konta.
  - EN: Your needs. They stay only on your device and are not part of the account.
- `privacy.not_kept.location`
  - PL: Bieżącej lokalizacji poza dziennikiem usługi wyznaczania tras. Używamy jej tylko do wyznaczenia jednej trasy.
  - EN: Your current location, apart from the log of the route planning service. We use it only to plan one route.
- `privacy.not_kept.email`
  - PL: Adresu e-mail. Nie pytamy o niego.
  - EN: An email address. We do not ask for one.
- `privacy.not_kept.disability`
  - PL: Informacji o niepełnosprawności. Nie pytamy o nią.
  - EN: Information about disability. We do not ask about it.
- `privacy.others.server`
  - PL: Twoja przeglądarka rozmawia tylko z naszym serwerem. Mapa, kroje pisma i skrypty pochodzą od nas, więc żadna zewnętrzna usługa nie poznaje Twojego adresu IP ani miejsca, które oglądasz.
  - EN: Your browser talks only to our server. The map, the typefaces and the scripts come from us, so no outside service learns your IP address or the place you look at.
- `privacy.others.search`
  - PL: Tekst wyszukiwania adresu przekazujemy zewnętrznej wyszukiwarce z naszego serwera, bez niczego, co Cię identyfikuje.
  - EN: We pass the text of an address search to an outside search service from our server, without anything that identifies you.
- `privacy.others.users`
  - PL: Inni użytkownicy nie widzą, kto dodał zgłoszenie albo głos.
  - EN: Other users do not see who added a report or a vote.
- `privacy.demo.body`
  - PL: Demo i wszystkie jego dane zostaną usunięte 4 października 2026, po ogłoszeniu wyników.
  - EN: The demo and all its data will be deleted on 4 October 2026, after the results are announced.

## About the data, V-13

| Key             | Polish                  | English                          |
| --------------- | ----------------------- | -------------------------------- |
| `data.sources`  | Skąd są informacje      | Where the information comes from |
| `data.statuses` | Co znaczą statusy       | What the statuses mean           |
| `data.segments` | Co znaczą odcinki trasy | What the route stretches mean    |
| `data.sample`   | Dane przykładowe        | Sample data                      |
| `data.fix`      | Jak poprawić błąd       | How to correct an error          |
| `data.licence`  | Licencja mapy           | Licence of the map               |

- `data.intro`
  - PL: Skąd wiemy o barierach i udogodnieniach i na ile można temu ufać.
  - EN: How we know about barriers and amenities, and how far it can be trusted.
- `data.sources.map`
  - PL: Dane mapy. Pochodzą z OpenStreetMap, otwartej mapy tworzonej przez wolontariuszy. Korzystamy z kopii z dnia {date}, a przy każdym fakcie podajemy datę jego ostatniej zmiany na mapie.
  - EN: Map data. They come from OpenStreetMap, an open map made by volunteers. We use the copy from {date}, and every fact shows the date it was last changed on the map.
- `data.sources.reports`
  - PL: Zgłoszenia ludzi. Każdy może zgłosić barierę, udogodnienie albo obszar. Przy zgłoszeniu podajemy datę ostatniego potwierdzenia.
  - EN: Reports from people. Anyone can report a barrier, an amenity or an area. A report shows the date it was last confirmed.
- `data.status.unverified`
  - PL: nikt jeszcze tego nie potwierdził albo potwierdzeń jest za mało.
  - EN: nobody has confirmed it yet, or there are too few confirmations.
- `data.status.confirmed`
  - PL: inne osoby potwierdziły, że to nadal tu jest.
  - EN: other people confirmed that it is still here.
- `data.status.disputed`
  - PL: jedne osoby potwierdzają, inne zgłaszają, że tego już nie ma.
  - EN: some people confirm it, others report that it is gone.
- `data.status.outdated`
  - PL: przeważają zgłoszenia, że tego już nie ma. Fakt zostaje na mapie, żeby można go było potwierdzić ponownie, ale trasa go nie uwzględnia.
  - EN: reports that it is gone prevail. The fact stays on the map, so that it can be confirmed again, but a route does not count it.
- `data.status.time`
  - PL: Status nie zmienia się sam z upływem czasu. Datę widzisz przy każdym fakcie i oceniasz ją samodzielnie.
  - EN: A status does not change with time alone. You see the date next to every fact and judge it yourself.
- `data.segment.barrier`
  - PL: Bariera z potrzeb. Na odcinku jest bariera, której unikasz.
  - EN: Barrier from your needs. The stretch has a barrier that you avoid.
- `data.segment.no_barrier`
  - PL: Bez barier, dane pełne. Znamy wszystko, co ważne dla Twoich potrzeb, i żadna z tych rzeczy nie jest barierą.
  - EN: No barriers, complete data. We know everything that matters for your needs, and none of it is a barrier.
- `data.segment.partial_data`
  - PL: Dane niepełne. To, co wiemy, nie jest barierą, ale części informacji brakuje.
  - EN: Partial data. What we know is not a barrier, but some information is missing.
- `data.segment.no_data`
  - PL: Brak danych. Nie wiemy o odcinku nic, co ważne dla Twoich potrzeb.
  - EN: No data. We know nothing about the stretch that matters for your needs.
- `data.missing`
  - PL: Brak informacji nigdy nie oznacza u nas, że miejsce jest dostępne.
  - EN: Missing information never means here that a place is accessible.
- `data.sample.body`
  - PL: W okolicy Tauron Areny dodaliśmy zgłoszenia i obszary na potrzeby pokazu. Każde ma znak dane przykładowe.
  - EN: Around the Tauron Arena we added reports and areas for the demonstration. Each one carries the mark sample data.
- `data.fix.body`
  - PL: Otwórz fakt i odpowiedz, czy nadal jest, albo dodaj własne zgłoszenie. Zapisanego zgłoszenia nikt nie edytuje.
  - EN: Open a fact and answer whether it is still here, or add your own report. Nobody edits a saved report.
- `data.licence.body`
  - PL: Mapa i dane: © OpenStreetMap contributors, licencja ODbL.
  - EN: Map and data: © OpenStreetMap contributors, ODbL licence.

## Moderation, V-14

| Key                      | Polish                 | English             |
| ------------------------ | ---------------------- | ------------------- |
| `moderation.title`       | Moderacja              | Moderation          |
| `moderation.flagged`     | Zgłoszone do moderacji | Flagged             |
| `moderation.hidden`      | Ukryte                 | Hidden              |
| `moderation.on_map`      | Pokaż na mapie         | Show on the map     |
| `moderation.hide`        | Ukryj                  | Hide                |
| `moderation.restore`     | Przywróć               | Restore             |
| `moderation.hidden.mark` | ukryte dla wszystkich  | hidden for everyone |
| `moderation.flagged_on`  | zgłoszone {date}       | flagged {date}      |

- `moderation.intro`
  - PL: Treści zgłoszone przez użytkowników. Nie widać tu, kto dodał treść ani kto ją zgłosił.
  - EN: Content flagged by users. This view does not show who added the content or who flagged it.
- `moderation.no_dismiss`
  - PL: Zgłoszenia do moderacji nie da się odrzucić. Treść, której nie ukryjesz, zostaje na tej liście.
  - EN: A flag cannot be dismissed. Content you do not hide stays on this list.
- `moderation.hidden.note`
  - PL: Ukryta treść znika z map, list i tras, nie bierze udziału w sprawdzaniu duplikatów i nie można na nią głosować. Po przywróceniu wraca z głosami, które ma.
  - EN: Hidden content disappears from maps, lists and routes, takes no part in the duplicate check and cannot be voted on. After it is restored it comes back with the votes it has.
- `moderation.empty`
  - PL: Nie ma treści zgłoszonych do moderacji.
  - EN: There is no flagged content.
- `moderation.denied`, for the error `moderator_role_required`
  - PL: Ten widok jest tylko dla moderatora.
  - EN: This view is only for a moderator.

## Messages of every view

- `state.loading`
  - PL: Wczytujemy.
  - EN: Loading.
- `state.map_failed`
  - PL: Nie udało się wczytać mapy. Listy i formularze działają dalej.
  - EN: The map could not be loaded. The lists and forms still work.
- `state.offline`
  - PL: Brak połączenia z serwerem. Sprawdź internet i spróbuj ponownie.
  - EN: No connection to the server. Check your internet connection and try again.
- `state.failed`, for the errors `internal_error`, `invalid_request` and every code without a text of its own
  - PL: Coś poszło nie tak po naszej stronie. Spróbuj ponownie.
  - EN: Something went wrong on our side. Try again.

## Names read by a screen reader

| Key              | Polish                                    | English                                     |
| ---------------- | ----------------------------------------- | ------------------------------------------- |
| `aria.nav`       | Główna nawigacja                          | Main navigation                             |
| `aria.language`  | Zmień język na angielski                  | Switch the language to Polish               |
| `aria.scope`     | Zakres faktów na mapie                    | Scope of the facts on the map               |
| `aria.summary`   | Podsumowanie trasy                        | Summary of the route                        |
| `aria.legend`    | Legenda odcinków                          | Legend of the stretches                     |
| `aria.map.facts` | Mapa okolicy z barierami i udogodnieniami | Map of the area with barriers and amenities |
| `aria.map.route` | Mapa trasy                                | Map of the route                            |
| `aria.map.pick`  | Mapa, wskazywanie punktu                  | Map, picking a point                        |

The summary line of the route result has a text description of its stretches in order, built from the names of the segment states and the distances, for example `Start, 40 m brak danych, 600 m bez barier, dane pełne, bariera z potrzeb: wysoki krawężnik` and its English counterpart. It is the text form of the states (`docs/product/views.md`, V-5).

## Texts added while the views were built

The texts below did not stand in the mocks. They were written by the agents that built the views on 2026-10-04, by the rules of the wording above, for the states and the names the build needed, and they were not approved one by one. A key that ends with `_one`, `_few`, `_many` or `_other` is one plural form of a text with a number.

| Key                          | Polish                                                                                                                              | English                                                                                                            |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `account.created`            | Konto jest założone. Zaloguj się.                                                                                                   | The account is created. Log in.                                                                                    |
| `account.logged_out`         | Wylogowano na tym urządzeniu. Możesz zalogować się ponownie.                                                                        | You are logged out on this device. You can log in again.                                                           |
| `action.close`               | Zamknij                                                                                                                             | Close                                                                                                              |
| `data.sources.map.no_date`   | Dane mapy. Pochodzą z otwartej mapy tworzonej przez wolontariuszy. Przy każdym fakcie podajemy datę jego ostatniej zmiany na mapie. | Map data. They come from an open map made by volunteers. Every fact shows the date it was last changed on the map. |
| `fact.area_row`              | Obszar: {type}, {radius} m                                                                                                          | Area: {type}, {radius} m                                                                                           |
| `fact.marker`                | {name}, {status}                                                                                                                    | {name}, {status}                                                                                                   |
| `fact.removed`               | Tego nie ma już w danych mapy.                                                                                                      | This is no longer in the map data.                                                                                 |
| `fact.stairs_with_steps`     | Schody, {steps}                                                                                                                     | Stairs, {steps}                                                                                                    |
| `fact.title`                 | Szczegóły faktu                                                                                                                     | Details of the fact                                                                                                |
| `facts.failed`               | Nie udało się wczytać faktów. Mapa działa dalej.                                                                                    | The facts could not be loaded. The map still works.                                                                |
| `facts.zoom_in`              | Przybliż mapę, żeby zobaczyć bariery i udogodnienia w okolicy.                                                                      | Zoom the map in to see the barriers and amenities of the area.                                                     |
| `flag.failed`                | Nie udało się zgłosić treści do moderacji. Spróbuj ponownie.                                                                        | The content could not be passed to moderation. Try again.                                                          |
| `flag.yes`                   | Tak, zgłoś                                                                                                                          | Yes, flag it                                                                                                       |
| `language.en`                | English                                                                                                                             | English                                                                                                            |
| `language.pl`                | Polski                                                                                                                              | Polski                                                                                                             |
| `legend.markers`             | Legenda znaczników                                                                                                                  | Legend of the markers                                                                                              |
| `legend.outdated`            | fakt nieaktualny                                                                                                                    | outdated fact                                                                                                      |
| `legend.overruled`           | zgłoszenie sprzeczne z danymi mapy                                                                                                  | report the map data contradict                                                                                     |
| `map.zoom_in`                | Przybliż mapę                                                                                                                       | Zoom the map in                                                                                                    |
| `map.zoom_out`               | Oddal mapę                                                                                                                          | Zoom the map out                                                                                                   |
| `map.locate`                 | Pokaż moją lokalizację na mapie                                                                                                     | Show my location on the map                                                                                        |
| `map.locate_unavailable`     | Lokalizacja jest niedostępna                                                                                                        | Location is not available                                                                                          |
| `map.locate_insecure`        | Lokalizacja jest niedostępna, bo ta strona nie ma bezpiecznego połączenia                                                           | Location is not available, because this page has no secure connection                                              |
| `map.resize`                 | Wysokość mapy                                                                                                                       | Height of the map                                                                                                  |
| `moderation.hide.done`       | Ukryto: {title}. Możesz to przywrócić na liście ukrytych.                                                                           | Hidden: {title}. You can restore it in the list of hidden content.                                                 |
| `moderation.restore.done`    | Przywrócono: {title}. Jest znowu widoczne dla wszystkich.                                                                           | Restored: {title}. Everyone can see it again.                                                                      |
| `needs.empty`                | Bez żadnej zaznaczonej pozycji mapa pokaże wszystkie fakty.                                                                         | With no item marked the map shows every fact.                                                                      |
| `needs.preset.applied`       | Ustawiono zestaw: {barriers}, {amenities}.                                                                                          | The set was applied: {barriers}, {amenities}.                                                                      |
| `notfound.title`             | Nie ma takiej strony.                                                                                                               | There is no such page.                                                                                             |
| `pick.title.destination`     | Cel: wskaż punkt na mapie                                                                                                           | Destination: pick a point on the map                                                                               |
| `pick.title.start`           | Start: wskaż punkt na mapie                                                                                                         | Start: pick a point on the map                                                                                     |
| `plan.clear`                 | Usuń punkt                                                                                                                          | Clear the point                                                                                                    |
| `plan.locating`              | Czekamy na lokalizację z urządzenia.                                                                                                | Waiting for the location of the device.                                                                            |
| `plan.not_set`               | nie ustawiono                                                                                                                       | not set                                                                                                            |
| `report.area.radius.missing` | Wybierz promień obszaru.                                                                                                            | Choose the radius of the area.                                                                                     |
| `report.existing.checking`   | Sprawdzamy, czy to jest już zgłoszone.                                                                                              | Checking whether this is already reported.                                                                         |
| `report.map.existing`        | Mapa z punktem zgłoszenia i faktami w pobliżu                                                                                       | Map with the point of the report and the facts nearby                                                              |
| `report.map.plain`           | Mapa okolicy                                                                                                                        | Map of the area                                                                                                    |
| `report.map.point`           | Mapa z punktem zgłoszenia                                                                                                           | Map with the point of the report                                                                                   |
| `report.map.saved`           | Mapa z nowym zgłoszeniem                                                                                                            | Map with the new report                                                                                            |
| `report.marker.point`        | Punkt zgłoszenia                                                                                                                    | Point of the report                                                                                                |
| `report.point.located`       | Mapa pokazuje teraz okolicę urządzenia. Ustaw znacznik na zgłaszanym miejscu i wybierz Ustaw ten punkt.                             | The map now shows the area around the device. Put the marker on the place you report and choose Set this point.    |
| `report.point.no_map`        | Nie możemy odczytać punktu z mapy. Odśwież stronę i spróbuj ponownie.                                                               | We cannot read the point from the map. Reload the page and try again.                                              |
| `report.point.no_map.area`   | Nie możemy odczytać punktu z mapy. Wyszukaj adres i wybierz wynik z listy.                                                          | We cannot read the point from the map. Search for an address and pick a result from the list.                      |
| `report.point.to_map`        | Przejdź do mapy                                                                                                                     | Go to the map                                                                                                      |
| `report.saving`              | Zapisujemy zgłoszenie.                                                                                                              | Saving the report.                                                                                                 |
| `report.search.picked`       | Wybrane miejsce: {label}. Żeby przejść dalej, wybierz Ustaw ten punkt.                                                              | Picked place: {label}. To go on, choose Set this point.                                                            |
| `report.steps.invalid`       | Wpisz liczbę stopni od 1 do 999 albo zostaw pole puste.                                                                             | Enter a number of steps from 1 to 999 or leave the field empty.                                                    |
| `report.type.missing`        | Wybierz typ z listy.                                                                                                                | Choose a type from the list.                                                                                       |
| `route.end.destination`      | Cel trasy                                                                                                                           | Destination of the route                                                                                           |
| `route.end.start`            | Start trasy                                                                                                                         | Start of the route                                                                                                 |
| `route.failed`               | Nie udało się wyznaczyć trasy ponownie.                                                                                             | The route could not be planned again.                                                                              |
| `route.no_route`             | Nie ma jeszcze trasy. Ustaw start i cel.                                                                                            | There is no route yet. Set the start and the destination.                                                          |
| `route.summary.destination`  | Cel                                                                                                                                 | Destination                                                                                                        |
| `route.summary.not_assessed` | Trasa bez oceny odcinków, {distance}.                                                                                               | A route whose stretches are not assessed, {distance}.                                                              |
| `route.summary.start`        | Start                                                                                                                               | Start                                                                                                              |
| `route.summary.stretch`      | {distance} {state}                                                                                                                  | {distance} {state}                                                                                                 |
| `route.summary.text`         | Odcinki trasy po kolei: {stretches}.                                                                                                | The stretches of the route in order: {stretches}.                                                                  |
| `route.title`                | Trasa                                                                                                                               | Route                                                                                                              |
| `search.searching`           | Szukamy.                                                                                                                            | Searching.                                                                                                         |
| `segment.short.barrier`      | bariera                                                                                                                             | barrier                                                                                                            |
| `segment.short.no_barrier`   | bez barier                                                                                                                          | no barriers                                                                                                        |
| `segment.short.no_data`      | brak danych                                                                                                                         | no data                                                                                                            |
| `segment.short.partial_data` | dane niepełne                                                                                                                       | partial data                                                                                                       |
| `vote.failed`                | Nie udało się zapisać głosu. Nic się nie zmieniło. Spróbuj ponownie.                                                                | The vote could not be saved. Nothing changed. Try again.                                                           |
| `vote.saving`                | Zapisujemy głos.                                                                                                                    | We are saving your vote.                                                                                           |

## Decisions behind the texts

Decided by the user, the frontend person of the team, on 2026-10-04:

1. No Polish text assumes the gender of the person, also where a mock did.
2. The alternative route, the way marked as not accessible for wheelchairs and the note of a contradiction have one general wording each. They name no street and do not say what the map data show, because the programming interface does not carry that; no second, specific wording is kept.
3. The check for existing facts asks one general question for every type, in place of a question that names the type.
4. A user fact shows one date, labelled as its last confirmation, because the programming interface gives one date for it. The label of a day of reporting is not used.
5. An English date is written as `3 Oct 2026`, and the amenity is called an elevator, as in the specification.
6. The name of the product is EnableMe, written the same in both languages. Decided by the team, as Adrian reported on 2026-10-04.

The mocks in `.impeccable/briefs/views/` were brought in line with these decisions on the same day.

## What stays open

- The single texts are working copy until the views are built: the frontend person decided the rules and the choices above and did not approve the texts one by one.
