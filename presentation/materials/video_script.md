# Video script

Document state: 2026-10-04

This is the script of the video of the Kraków submission, check 10.2 of `FINAL_CHECKLIST.md`: an mp4 of at most 3 minutes in Polish, placed in an open repository. The challenge requires the whole Kraków solution, the video included, in Polish (`docs/hackathon/challenge_requirements.md`, Challenge 1, Formal deliverables), so the voice-over and the texts on screen below are in Polish; the instructions around them are in English.

The video is recorded on the HarmonyOS emulator with the EnableMe client in `mobile_app/accessway/`, which computes everything on the device from the bundled sample data around the Tauron Arena (decided by the user on 2026-10-04: the web frontend of checks 6.1 and 6.2 is not ready, so the video does not wait for it). The scenes follow the demo scenario of `mobile_app/accessway/README.md`, section Scenariusz demonstracji.

## Relation to the demo scenario

The run of the demo is decided by check 7.2, drafted in `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_DRAFT.md` and not yet approved by Rafał. This script follows the scenario of the app README, which the draft maps one to one onto its sample facts S-1 - S-8 (section 5 of the draft); when the draft is approved, the scenes follow it. The differences today:

- The draft leaves out the route without a barrier-free way and reporting a barrier (scenes 4 and 6 here), because they do not serve checks 7.2 and 7.3; the video keeps them, because the jury of the video sees no live demo.
- The draft turns the contradiction of S-5 with a vote (its step 7). On the emulator that vote changes nothing on screen, because S-5 starts with one confirmation of weight 1 and an anonymous vote adds 0.5 (question Q-3 of the draft), so scene 5 shows the vote buttons and claims no change.
- Item 4 of section 9 of the draft lists the local rules of the app that differ from the specification. No scene here shows a case where they differ; whoever records checks it on the emulator, and when the screen shows something else than the voice-over says, the voice-over follows the screen.

## Before recording

1. Set the product name: the constant `PRODUCT_NAME` in `mobile_app/accessway/entry/src/main/ets/data/AppModel.ets` still holds `[Nazwa produktu]`, and the header of every screen shows it. It has to read `EnableMe` before the first take.
2. Use the schematic sample map, not the real tiles: `make tiles-sample`, then `make mock`. With `make tiles` the local route lies off the real streets (`mobile_app/accessway/README.md`, section Mapa z kafelków wektorowych).
3. Start from a clean install, so the first screen is the needs screen: `make uninstall`, then `make run`.
4. Emulator in Polish, resolution at least 1080 x 2160 if the machine allows it (`make emulator-fast EMU_RES=1080x2160`), otherwise 540 x 1080.
5. Rehearse the taps once without recording; every scene below is one continuous take, so a mistake costs one scene, not the whole video.

## Recording and editing

- Record the emulator window with OBS or the Xbox Game Bar of Windows 11 (Win + Alt + R), one file per scene.
- Record the voice-over separately with a headset microphone in a quiet place, one file per scene, and lay it over the picture; reading while tapping makes both worse.
- Put the phone picture in the middle of a 1920 x 1080 frame on the background color `#F4F5F2` of the app.
- Burn in Polish subtitles from the voice-over below. The video is judged by a jury of an accessibility challenge, and subtitles are the accessibility of the video itself. Clipchamp, which comes with Windows 11, generates Polish subtitles automatically; check them against the text below.
- Export to mp4 (H.264, AAC) and check the length: at most 3:00. GitHub refuses files over 100 MB; when the file is larger, compress it: `ffmpeg -i enableme.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k enableme_small.mp4`.
- The file goes into the public repository of the project (check 9.5) and its link goes into the Kraków submission (check 10.5).

## Scenes

The times are targets; the voice-over of all scenes has about 340 words, about 2:45 at a calm pace.

### Scene 1. The problem (0:00 - 0:15)

On screen: the slide `title` of the deck in `presentation/`, or the first screen of the app with the name EnableMe.

Voice-over:

```text
Schody, wysoki krawężnik, brak windy. Osoba na wózku albo z wózkiem dziecięcym zwykle dowiaduje się o nich dopiero na miejscu. EnableMe pozwala sprawdzić trasę w Krakowie, zanim wyjdziesz z domu.
```

### Scene 2. Needs, not a diagnosis (0:15 - 0:35)

On screen: the needs screen. Tap the preset "Poruszam się na wózku", scroll through the lists "Unikam" and "Potrzebuję", tap "Gotowe".

Voice-over:

```text
Zaczynasz od potrzeb, nie od diagnozy. Wybierasz gotowy zestaw, na przykład: poruszam się na wózku, i poprawiasz go. Zaznaczasz, czego unikasz i czego potrzebujesz. Aplikacja nie pyta o niepełnosprawność, a Twoje potrzeby zostają tylko na Twoim telefonie.
```

### Scene 3. The route and the four segment states (0:35 - 1:20)

On screen: "Dokąd idziesz?", type "ogród", "Szukaj", choose Ogród Doświadczeń. Start: "Adres", type "tauron", "Szukaj", choose Tauron Arena Kraków. "Wyznacz trasę". On the result, hold on the map with the segments for two seconds, then scroll slowly through the group "Z Twoich potrzeb" and the alternative route. Do not open the rows of the group "Czego nie wiemy": the app names the missing attributes there, which M8 of the specification does not allow (`plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_DRAFT.md`, section 9, item 3).

Voice-over:

```text
Wyznaczamy trasę spod Tauron Areny do Ogrodu Doświadczeń. Każdy odcinek ma jeden z czterech stanów: bariera z Twoich potrzeb, brak barier przy pełnych danych, dane niepełne albo brak danych. Stan rozpoznasz po kolorze, ikonie i wzorze linii, więc nie musisz rozróżniać barw. Pod mapą jest lista. Wysoki krawężnik na ulicy Lema potwierdzili użytkownicy. Schodów przy alei Pokoju nikt jeszcze nie sprawdził, więc aplikacja proponuje trasę alternatywną i mówi, dlaczego. Odcinki, o których nic nie wiemy, są szare i przerywane. Brak informacji nigdy nie jest pokazywany jako dostępność.
```

### Scene 4. No route without barriers (1:20 - 1:40)

On screen: change the destination to Park Lotników Polskich and plan the route; hold on the message "Nie ma trasy bez barier z Twoich potrzeb." and the list of barriers under it.

Voice-over:

```text
Do Parku Lotników Polskich każda droga prowadzi przez schody z danych mapy. Aplikacja mówi to wprost, pokazuje trasę z najmniejszą liczbą barier i wymienia je po kolei.
```

### Scene 5. Contradictory data and votes (1:40 - 2:10)

On screen: open the fact "Wysoki krawężnik" of the sample `demo-kerb-medweckiego` (`mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets`). Hold on the source, the date and the status, then on the note that OpenStreetMap marks a lowered kerb here, then on the buttons "Nadal jest" and "Już nie ma".

The sample is named after ul. Medweckiego in its identifier and in `mobile_app/accessway/README.md`, but its street field says Stanisława Lema, so the app may show it at ul. Lema; the voice-over names no street for that reason.

Voice-over:

```text
Każdy fakt ma źródło, datę i status. Tutaj użytkownik zgłosił wysoki krawężnik, a dane mapy mówią o obniżonym. Aplikacja pokazuje obie informacje, zamiast wybierać za Ciebie. Każdy może potwierdzić, że bariera nadal jest, albo zgłosić, że jej już nie ma, raz na dobę. Z tych głosów powstaje status: niezweryfikowany, potwierdzony, sporny albo nieaktualny.
```

### Scene 6. Reporting a barrier (2:10 - 2:35)

On screen: the reporting entry, choose a barrier, its type and the point on the map; show the step with the facts of the same type within 15 m, then the summary, approve it.

Voice-over:

```text
Barierę zgłaszasz w kilku krokach, z kontem albo bez. Najpierw aplikacja pokazuje podobne zgłoszenia w promieniu piętnastu metrów, żeby nie dublować faktów, a przed zapisem prosi o zatwierdzenie podsumowania. Treści, które ktoś oflaguje, przegląda moderator.
```

### Scene 7. Closing (2:35 - 2:55)

On screen: the page about the data from the menu, with the sources, the statuses in words and the label "Dane przykładowe", as step 9 of the draft demo scenario closes; then the last slide of the deck or a plain board with the name EnableMe, the attribution "Dane mapy: OpenStreetMap, licencja ODbL" and the address of the repository.

Voice-over:

```text
Dane mapy pochodzą z OpenStreetMap, a zgłoszenia w tym pokazie to oznaczone dane przykładowe z okolic Tauron Areny. EnableMe: konkretne fakty zamiast etykiet i uczciwie pokazana niepewność.
```

## What the video deliberately leaves out

- The web frontend and the hosted demo: not ready at the time of recording; the deck and the pitch say what works where.
- The profile without any barrier, the route without assessed segments: step 5 of the demo scenario of the app, cut to stay under 3 minutes. If the cut voice-over leaves time, it fits after scene 4 with one sentence: "Bez żadnej bariery w potrzebach aplikacja nie ocenia odcinków i mówi to wprost."
- Accounts, the privacy page and moderation beyond one sentence: they are on the slides.
