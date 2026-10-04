# Pitch

Document state: 2026-10-04

How the team gives the Kraków pitch with a live demo, check 10.6 of `FINAL_CHECKLIST.md`, and how it answers the questions of the jury. The spoken text of every slide is not here: it is in the speaker notes of the deck, `presentation/src/content/pl.js` for Polish and `presentation/src/content/en.js` for English, shown by the key S during the presentation, so the slides and what is said about them change in one place. The answers below are in Polish, because the Kraków pitch is given in Polish (`docs/hackathon/challenge_requirements.md`, Challenge 1, Formal deliverables); the rest is in English.

## Timing

The time and length of the Kraków pitch are not known yet; check 1.2 of `FINAL_CHECKLIST.md` records them. The deck is planned for 5 minutes: about 3 minutes of slides and 2 minutes of the live demo on slide `demo`. The plan per slide is in `presentation/src/slides/timing.js`, and the presenter view (S) shows whether the talk is ahead or behind.

When check 1.2 gives a different length:

- 3 minutes: the live demo shrinks to scenes 3 and 5 of `presentation/materials/video_script.md` (the route with its states and the contradiction, about 60 seconds), and slides `community` and `data` get one sentence each.
- 7 minutes or more: the demo adds the report of scene 6 and the route without barriers of scene 4, and the time left goes to questions, not to more slides.

## Roles

A proposal, to be confirmed by Rafał and Adrian, who carry the Polish materials and the pitch (`TEAM.md`): Rafał speaks, Adrian drives the emulator during the demo and takes the questions about the interface and accessibility. Questions about the data go to Mateusz and about routing and the backend to Marek, if they are in the room.

## Live demo

The demo runs on the HarmonyOS emulator with the EnableMe client of `mobile_app/accessway/`, the same build and the same scenes as the video (`presentation/materials/video_script.md`, section Before recording, for the preparation). The laptop shows the deck on the projector and the emulator in a second window; switching between them is rehearsed.

Fallbacks, in this order:

1. The emulator does not start or hangs: play the recorded video from the local file, from the scene the demo was at.
2. The laptop with the emulator fails: the deck from `dist/pl/index.html` on any other laptop, it works offline from one file, and the video from the same pendrive.
3. No working laptop: the PDF of the deck from the pendrive or from the phone.

## Rehearsal and the day

- One rehearsal with a clock in the rehearsal mode of the deck (`?rehearsal` in the address, `presentation/README.md`), then the times of `timing.js` corrected to what the rehearsal measured.
- One full run of the demo on the emulator right before the pitch, from a clean install, so the first screen is the needs screen.
- On a pendrive: `dist/pl/index.html`, `enableme-deck-pl.pdf`, the video mp4. The English deck goes with them in case the Huawei jury invites the team (check 10.4).
- Projector test: the slides are 16:9; with a 4:3 projector reveal.js scales them down, nothing has to change.
- Phone notifications off on every device on the stage.

## Questions and answers

The answers are short on purpose: one or two sentences, then stop. A question the team cannot answer is answered with what we know and what we would check, never with a guess.

### Skąd macie dane i jak często je odświeżacie?

```text
Podstawą jest OpenStreetMap: wycinek Małopolski od Geofabrik przycięty do granic Krakowa. Kopię pobieramy w całości albo wcale, więc aplikacja zawsze pokazuje jedną spójną kopię z jej datą, a gdy źródło jest niedostępne, pracuje na ostatniej pełnej kopii. Na to nakładamy zgłoszenia i głosy ludzi. W prototypie kopię odświeżamy ręcznie, w usłudze byłoby to zadanie cykliczne.
```

### Co, jeśli ktoś zgłosi fałszywą barierę albo będzie trollował?

```text
Pojedyncze zgłoszenie jest niezweryfikowane i tak je pokazujemy. Status liczy się z ostatnich głosów pięciu osób, jedna osoba głosuje na fakt najwyżej raz dziennie i liczy się tylko jej ostatni głos, a głos bez konta waży pół. Każdy może oflagować zgłoszenie, a moderator je ukrywa.
```

### Dlaczego nie pytacie o niepełnosprawność?

```text
Bo nie potrzebujemy tej informacji. Do dopasowania trasy wystarczy wiedzieć, czego ktoś unika i czego potrzebuje. Informacja o niepełnosprawności to dane o zdrowiu, szczególna kategoria z artykułu 9 RODO, więc jej nie zbieramy. Potrzeby zostają na telefonie.
```

### Czym się różnicie od istniejących map dostępności?

```text
Mapy dostępności zwykle oceniają miejsce jedną etykietą: dostępne albo nie. My oceniamy drogę, odcinek po odcinku, pokazujemy konkretne bariery z ich źródłem, datą i statusem i mówimy wprost, czego nie wiemy. Brak danych nigdy nie udaje dostępności.
```

Before the pitch, the team checks the claim against the two or three services the jury is most likely to name; the sentence above says nothing about any service by name on purpose.

### Kto za to zapłaci?

```text
Dla mieszkańców i turystów aplikacja jest bezpłatna. Płacą ci, którzy zyskują na dostępności: miasto albo zarządca dróg za wdrożenie i zgłoszenia barier mieszkańców w jednym miejscu, obiekty i organizatorzy wydarzeń za trasę bez barier do swojego wejścia. Sprzedajemy usługę, a nie dane: dane z OpenStreetMap zostają otwarte.
```

This answer follows the business model slide, which is a proposal of the agent waiting for the approval of the team (check 9.2).

### Ile kosztuje utrzymanie?

```text
Cały system działa na jednym serwerze w kontenerach Docker: serwis, baza PostGIS i silnik tras Valhalla. Największym kosztem nie jest serwer, tylko praca moderatora i odświeżanie danych.
```

No amount is named until check 9.2 settles the running costs.

### Jak uruchomić to w innym mieście?

```text
Nowe miasto to nowy wycinek OpenStreetMap z granicą miasta i przeliczony graf tras. Reguły, które tłumaczą tagi OpenStreetMap na bariery i udogodnienia, są wspólne dla całej mapy, więc nie piszemy ich od nowa.
```

### A osoby niewidome i słabowidzące?

```text
Świadomie są poza prototypem, bo ich potrzeby zależą od innych danych, na przykład ścieżek dotykowych i sygnalizacji dźwiękowej. Sam interfejs ma działać z czytnikiem ekranu. To naturalny następny zakres.
```

### Dlaczego demo działa po HTTP, a nie HTTPS?

```text
To świadome uproszczenie demo na hackathonie i znane ograniczenie prototypu, które opisujemy w zgłoszeniu. W docelowej usłudze ruch idzie wyłącznie po HTTPS.
```

### Jak chronicie konta?

```text
Konto to pseudonim i hasło, bez adresu e-mail. Hasło przechowujemy jako skrót Argon2id, sesja wygasa po 24 godzinach od ostatniego użycia. Innym użytkownikom nie pokazujemy niczego o autorze zgłoszenia.
```

### Co z licencją OpenStreetMap?

```text
Dane OpenStreetMap są na licencji ODbL: podajemy atrybucję na mapie i na stronie o danych, a baza zbudowana z OpenStreetMap zostaje na tej samej licencji. Pomysł na rozwój to odsyłanie potwierdzonych zgłoszeń z powrotem do OpenStreetMap.
```

### Co tu naprawdę działa, a co jest makietą?

```text
Na emulatorze działa cała ścieżka: potrzeby, trasa ze stanami odcinków, lista, fakty ze źródłem, datą i statusem, głosy, zgłoszenia, konta i moderacja. Liczy się na telefonie, na oznaczonych danych przykładowych z okolic Tauron Areny. Serwer z danymi całego Krakowa jest w budowie i ma to samo API, do którego aplikacja jest już przygotowana.
```

This answer has to match the slide `status` on the day; whoever updates that slide updates this answer.

### Co sprawdziliście pod kątem dostępności interfejsu?

To be written from check 6.5 of `FINAL_CHECKLIST.md`, the accessibility check of the main scenario, when it is done. Until then: the segment states are told apart by an icon and a line pattern, not by color alone, and the list for the route is the text form of the map.

### A transport publiczny?

```text
Trasy z tramwajami i autobusami ZTP na danych GTFS są funkcją opcjonalną, która nie weszła do tego prototypu.
```

Before the pitch, check the state of check 4.2 of `FINAL_CHECKLIST.md`; when it is ticked, this answer changes.
