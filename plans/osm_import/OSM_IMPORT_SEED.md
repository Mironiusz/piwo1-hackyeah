# Seed: OpenStreetMap import of the MVP

Source: conversation with the user
Date: 2026-10-04

## Verbatim content

The request was made in Polish, in one conversation of 2026-10-04: three messages of the user and the answers of the user to two closed questions of the agent. Messages 2 and 3 answer numbered open questions of the agent, which are not quoted here; what the answers decided is recorded in `MVP.md`, sections How the MVP is built and Initiatives. Each part is quoted verbatim in Polish and followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

User message 1, original in Polish:

```text
będziemy musieli zmodyfikować zakres mvp, by nie zakładał implementacji niczego, a jedynie stworzenie pliku mvp oraz założenie inicjatyw na implementację nowych rzeczy. Przejrzyj go, jeszcze nie zmieniaj, i przygtowuj się do tego
```

User message 1, English translation by the agent:

```text
we will have to modify the scope of the mvp so that it does not assume implementing anything, but only creating the mvp file and setting up initiatives for implementing new things. Review it, do not change it yet, and get ready for it
```

User message 2, original in Polish:

```text
1 - MVP.md w roocie, w formie drugiej opcji, co podsumuje wszystko co ustaliliśmy
2 - tak, pasuje
3 - tak, sam seed
4 - robimy opcję 2
5 - to właśnie ma trafić do MVP.md
6 - tak, ma wejść
7 - teraz je rozwiązuję, ty nic z nimi nie rób teraz
```

User message 2, English translation by the agent:

```text
1 - MVP.md in the root, in the form of the second option, which summarizes everything we have settled
2 - yes, it fits
3 - yes, the seed alone
4 - we go with option 2
5 - that is exactly what is to go into MVP.md
6 - yes, it is to be included
7 - I am resolving them now, do not do anything with them now
```

User message 3, original in Polish:

```text
1 - ok
2 - ok
3 - import
4 - tak.

Merge zrobiony , możesz zmieniać ten mvp
```

User message 3, English translation by the agent:

```text
1 - ok
2 - ok
3 - import
4 - yes.

Merge done, you can change this mvp
```

Closed question 1 of the agent with the options offered, original in Polish:

```text
Po wykonaniu planu `plans/mvp/` idzie do archiwum, a jego dokumenty stają się historią. Tymczasem FR-3 z `BACKEND_ARCHITECTURE_SHAPE.md` każe zapisać regułę hasha głosu (trzymanego do usunięcia dema) m.in. w "AC-12 of `plans/mvp/MVP_PRD.md`" i w "Q-11 of `plans/mvp/MVP_PLAN.md`". Gdzie FR-3 ma to zapisać po zmianie?

Opcje:
- Do MVP.md (Recommended): Datowany dopisek w shape backend_architecture: FR-3 pisze do specyfikacji, schema.md i MVP.md zamiast do AC-12 i Q-11 zarchiwizowanego planu MVP. MVP.md od razu notuje, że AC-12 ustępuje nowej wersji specyfikacji.
- Wstrzymać archiwizację: plans/mvp zostaje w plans/ do czasu, aż backend_architecture wykona FR-3 na AC-12 i Q-11. Archiwizacja dopiero potem, ręcznie.
```

Closed question 1 of the agent, English translation by the agent:

```text
After the plan is carried out, `plans/mvp/` goes to the archive and its documents become history. Meanwhile FR-3 of `BACKEND_ARCHITECTURE_SHAPE.md` has the rule of the hash of a vote (kept until the demo is deleted) written, among other places, into "AC-12 of `plans/mvp/MVP_PRD.md`" and into "Q-11 of `plans/mvp/MVP_PLAN.md`". Where is FR-3 to write it after the change?

Options:
- Into MVP.md (Recommended): A dated note in the shape of backend_architecture: FR-3 writes into the specification, schema.md and MVP.md instead of AC-12 and Q-11 of the archived MVP plan. MVP.md notes at once that AC-12 gives way to the new version of the specification.
- Hold the archiving: plans/mvp stays in plans/ until backend_architecture carries out FR-3 on AC-12 and Q-11. Archiving only afterwards, by hand.
```

User answer to closed question 1, original:

```text
Do MVP.md (Recommended)
```

User answer to closed question 1, English translation by the agent:

```text
Into MVP.md (Recommended)
```

Closed question 2 of the agent with the options offered, original in Polish:

```text
Instrukcja `docs/deployment/hosted_demo.md` mówi o jednym "separate loading program", który ładuje kopię OSM z danymi routingu, archiwum kafelków i dane przykładowe. DEPLOYMENT_PRD mówi tylko, że trzy pakiety "together make the loading program". Kto składa z trzech części jeden program?

Opcje:
- osm_import (Recommended): osm_import buduje program ładujący z wyzwalaczem, który Q-11 wybierze dla przebiegu importu. map_tiles i sample_data dokładają do niego swoje kroki.
- DEPLOYMENT_CONFIG: Każda inicjatywa buduje własną część. Task DEPLOYMENT_CONFIG z plans/deployment skleja je w jedną komendę dla serwera.
```

Closed question 2 of the agent, English translation by the agent:

```text
The instructions `docs/deployment/hosted_demo.md` speak of one "separate loading program" that loads the OSM copy with the routing data, the tile archive and the sample data. DEPLOYMENT_PRD says only that three packages "together make the loading program". Who joins the three parts into one program?

Options:
- osm_import (Recommended): osm_import builds the loading program with the trigger that Q-11 chooses for the import run. map_tiles and sample_data add their steps to it.
- DEPLOYMENT_CONFIG: Each initiative builds its own part. The task DEPLOYMENT_CONFIG of plans/deployment joins them into one command for the server.
```

User answer to closed question 2, original:

```text
osm_import (Recommended)
```

User answer to closed question 2, English translation by the agent:

```text
osm_import (Recommended)
```

The scope of this initiative, as the table Initiatives of `MVP.md` recorded it when this seed was saved, is quoted below verbatim, so that this record keeps what was asked for if `MVP.md` changes later. The quote is in English in the original.

```text
| `plans/osm_import/`               | Mateusz (import)                                    | D-4, the import side of D-5 and the import side of D-9 (`plans/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-2), the operation `read_osm_copy`, and the one loading program of `docs/deployment/hosted_demo.md`, section Loading the data, started in the form D-14 decides for the import run, into which `map_tiles` and `sample_data` add their steps.                                                                                                                                                                                                                                                                                     | `schema_first_revision`.                                                                                                |
```
