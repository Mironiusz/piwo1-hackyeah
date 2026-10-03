# Seed: Choice of the routing engine for the MVP, delegated to the responsible people

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in one conversation, as answers to questions the agent asked in phase B of `plan-prd` for `plans/mvp/`. The answers are short and refer to the questions, so each answer is quoted together with the agent question it answers. Both are quoted verbatim in Polish, the options offered with a question being part of the question, and each is followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

Agent question 1, original in Polish:

```text
Silnik routingu. PRD wymaga rzeczy, których zwykłe silniki nie robią same: unikanie tylko barier z profilu, czerwone odcinki z niezweryfikowanym zgłoszeniem plus trasa alternatywna, trasa z najmniejszą liczbą barier, gdy nie da się bez nich, i 4 stany odcinka z listą brakujących atrybutów. Fakty: publiczny Valhalla odpowiada, Overpass teraz nie odpowiada (timeout). Jak liczymy trasy?

Opcje:
- Własny graf w Pythonie (Recommended): Graf pieszy Krakowa z OSM w pamięci backendu, Dijkstra (scipy) z kosztem per profil: najpierw liczba barier, potem długość. Pełna kontrola nad stanami odcinków i alternatywą, testowalne bez sieci, bez zależności od zewnętrznej usługi.
- pgRouting w PostGIS: Routing w bazie (pgr_dijkstra). Koszt per profil wymaga składania SQL krawędzi jako tekstu, co gryzie się z zakazem budowania zapytań ze stringów (standard_database, bandit B608). Wymaga obrazu z pgRouting.
- Zewnętrzny Valhalla: Publiczna instancja (exclude_locations/exclude_polygons). Stany odcinków i tak trzeba liczyć u nas z mapowania na drogi OSM; zależność od fair-use cudzej usługi na ścieżce żądania, co standard architektury dopuszcza tylko jako jawny wyjątek.
```

Agent question 1, English translation by the agent:

```text
Routing engine. The PRD requires things that ordinary engines do not do on their own: avoiding only the barriers from the profile, red segments with an unverified report plus an alternative route, the route with the fewest barriers when it cannot be done without them, and 4 segment states with a list of missing attributes. Facts: the public Valhalla answers, Overpass does not answer right now (timeout). How do we compute routes?

Options:
- Own graph in Python (Recommended): A pedestrian graph of Kraków from OSM in the memory of the backend, Dijkstra (scipy) with a cost per profile: first the number of barriers, then the length. Full control over the segment states and the alternative, testable without the network, without a dependency on an external service.
- pgRouting in PostGIS: Routing in the database (pgr_dijkstra). A cost per profile requires assembling the edge SQL as text, which clashes with the ban on building queries from strings (standard_database, bandit B608). Requires an image with pgRouting.
- External Valhalla: A public instance (exclude_locations/exclude_polygons). The segment states have to be computed on our side anyway from the mapping onto OSM ways; a dependency on someone else's fair-use service on the request path, which the architecture standard allows only as an explicit exception.
```

User answer 1, original in Polish:

```text
decyzja na później
```

User answer 1, English translation by the agent:

```text
decision for later
```

Agent question 2, original in Polish:

```text
Odkładasz routing i źródło danych OSM. Jak chcesz domknąć fazę B? Bez tych decyzji plan nie może dostać statusu closed, a plan-implement nie ruszy.

Opcje:
- Decyduj sam, ja przejrzę plan: Obniżasz regulator dla fazy B (np. C:20). Wszystkie kierunki techniczne, w tym routing i dane OSM, rozstrzygam sam z rekomendacji, oznaczam jako decyzje agenta, a Ty przeglądasz gotowy plan przed implementacją.
- Pytaj dalej o resztę: Zadaję pozostałe 6 pytań. Routing i dane OSM zostają otwarte do Twojej decyzji później, plan zostaje w stanie in progress.
- Wstrzymaj fazę B: Zapisuję stan (D-1 i otwarte pytania) w MVP_PLAN.md i kończę. Wrócicie do tego z zespołem, a ja nic nie implementuję.
```

Agent question 2, English translation by the agent:

```text
You are deferring routing and the source of the OSM data. How do you want to close phase B? Without these decisions the plan cannot get the status closed, and plan-implement will not start.

Options:
- Decide yourself, I will review the plan: You lower the regulator for phase B (for example C:20). I settle all technical directions myself from the recommendations, routing and the OSM data included, mark them as agent decisions, and you review the finished plan before implementation.
- Keep asking about the rest: I ask the remaining 6 questions. Routing and the OSM data stay open for your decision later, and the plan stays in the state in progress.
- Pause phase B: I save the state (D-1 and the open questions) in MVP_PLAN.md and finish. You come back to it with the team, and I implement nothing.
```

User answer 2, original in Polish:

```text
na kazdą decyzję techniczną postaw nową inicjatywę po prostu, odpowiedni ludzie podejmą decyzję, nie na wszystko a
```

User answer 2, English translation by the agent:

```text
for every technical decision just set up a new initiative, the right people will make the decision, not for everything a

(Translator's note: the original message ends mid-sentence after the word "a", and the translation keeps the break.)
```

Agent question 3, original in Polish:

```text
Routing i źródło danych OSM dostają osobne inicjatywy. Które z pozostałych decyzji też mają dostać własną inicjatywę? Te, których nie zaznaczysz, rozstrzygam sam w MVP_PLAN.md jako decyzje agenta (z uzasadnieniem, do Twojego przeglądu).

Opcje:
- Frontend: Technologia (np. React+TS+Vite+Leaflet vs HTML renderowany na serwerze) i to, jak kod frontu podlega standardom, bo profil Pythona go nie obejmuje.
- Środowisko dema: Gdzie działa demo: laptop vs hosting. To otwarta pozycja w decision_registry, od której zależą uprawnienia agenta w CLAUDE.md.
- Mapowanie tagów OSM na bariery: Progi typu: od ilu % nachylenie jest strome, jaka szerokość to wąskie przejście, kiedy krawężnik jest wysoki, jakie nawierzchnie są złe. To raczej reguła produktowa niż techniczna.
- Baza, geokoder, sesje: Trzy mniejsze: PostGIS lokalnie (Docker vs instalacja w PG18), wyszukiwanie adresów (własny indeks z OSM vs Nominatim), sesje kont (cookie + sesja w bazie vs JWT).
```

Agent question 3, English translation by the agent:

```text
Routing and the source of the OSM data get separate initiatives. Which of the remaining decisions should also get their own initiative? Those you do not tick I settle myself in MVP_PLAN.md as agent decisions (with a justification, for your review).

Options:
- Frontend: The technology (for example React+TS+Vite+Leaflet vs HTML rendered on the server) and how the frontend code is held to the standards, because the Python profile does not cover it.
- Demo environment: Where the demo runs: a laptop vs hosting. This is an open entry in decision_registry, on which the permissions of the agent in CLAUDE.md depend.
- Mapping of OSM tags to barriers: Thresholds such as: from what % an incline is steep, what width is a narrow passage, when a kerb is high, which surfaces are poor. This is more a product rule than a technical one.
- Database, geocoder, sessions: Three smaller ones: PostGIS locally (Docker vs installation in PG18), address search (own index from OSM vs Nominatim), account sessions (cookie + session in the database vs JWT).
```

User answer 3, original in Polish:

```text
Frontend,Środowisko dema,Mapowanie tagów OSM na bariery,Baza, geokoder, sesje
```

User answer 3, English translation by the agent:

```text
Frontend, Demo environment, Mapping of OSM tags to barriers, Database, geocoder, sessions

(Translator's note: the question allowed ticking several options, and all four were ticked.)
```

Agent question 4, original in Polish:

```text
Proponowane nazwy 8 inicjatyw (katalog -> prefiks): 1) plans/routing_engine -> ROUTING_ENGINE, 2) plans/osm_data_source -> OSM_DATA_SOURCE, 3) plans/frontend_stack -> FRONTEND_STACK, 4) plans/demo_environment -> DEMO_ENVIRONMENT, 5) plans/osm_barrier_mapping -> OSM_BARRIER_MAPPING, 6) plans/local_database -> LOCAL_DATABASE, 7) plans/geocoding -> GEOCODING, 8) plans/account_sessions -> ACCOUNT_SESSIONS. W każdej powstanie SEED (dosłowny zapis naszej rozmowy po polsku z tłumaczeniem) i szkielet SHAPE z faktami, które już zebrałem, bez rozstrzygania. Regulator C:40 (domyślny, bo w tych seedach nie ma wartości). Pasuje?

Opcje:
- Pasuje, twórz: Zakładam 8 katalogów z SEED i szkieletem SHAPE, a MVP_PLAN.md zostaje w stanie in progress z odesłaniem do nich.
- Pasuje, ale bez SHAPE: Tylko SEED w każdej inicjatywie. SHAPE zrobi plan-shape, gdy właściwa osoba przejmie temat.
```

Agent question 4, English translation by the agent:

```text
Proposed names of 8 initiatives (directory -> prefix): 1) plans/routing_engine -> ROUTING_ENGINE, 2) plans/osm_data_source -> OSM_DATA_SOURCE, 3) plans/frontend_stack -> FRONTEND_STACK, 4) plans/demo_environment -> DEMO_ENVIRONMENT, 5) plans/osm_barrier_mapping -> OSM_BARRIER_MAPPING, 6) plans/local_database -> LOCAL_DATABASE, 7) plans/geocoding -> GEOCODING, 8) plans/account_sessions -> ACCOUNT_SESSIONS. In each of them a SEED (a verbatim record of our conversation in Polish with a translation) and a SHAPE skeleton with the facts I have already gathered will be created, without settling anything. Regulator C:40 (the default, because these seeds carry no value). Does it fit?

Options:
- Fits, create: I set up 8 directories with a SEED and a SHAPE skeleton, and MVP_PLAN.md stays in the state in progress with a pointer to them.
- Fits, but without SHAPE: Only a SEED in each initiative. SHAPE will be done by plan-shape when the right person takes over the topic.
```

User answer 4, original in Polish:

```text
Pasuje, twórz
```

User answer 4, English translation by the agent:

```text
Fits, create
```
