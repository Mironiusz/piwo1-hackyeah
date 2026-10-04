# Seed: Tile-archive step of the common demo-loading program

Source: conversation with the user
Date: 2026-10-04

## Verbatim content

The request was made in Polish on 2026-10-04, in the conversation that resumed `plans/osm_import/` with the goal of completing it in full. It is the user's answer to a closed question of the agent, followed by the user's answer to a closed naming question. Both questions are quoted first, as the context the answers refer to; they are the agent's text, not part of the request. Each part is quoted verbatim in Polish and followed by an English translation by the agent. The translations are not part of the verbatim record; in case of doubt the Polish original applies.

Closed question of the agent, original in Polish, quoted for context:

```text
Co load_demo ma robić z kafelkami, skoro map_tiles nie dostarczył kroku, tylko plik do ręcznego wgrania?

- Bez kafelków (Recommended): load_demo ma dwa kroki: OSM, potem próbki. Plik pmtiles wgrywa się ręcznie według MAP_SETUP.md, zgodnie z D-1 Adriana. Poprawiam PRD (FR-3, FR-4, AC-4, AC-6, AC-9, AC-10), wiersz osm_import w MVP.md i FINAL_CHECKLIST 3.4. Nie dochodzi żaden klucz konfiguracji.
- Krok weryfikujący: Plik dalej wgrywa się ręcznie, ale load_demo w kroku tiles sprawdza, czy archiwum leży pod skonfigurowaną ścieżką i ma zapisany SHA-256. Brak pliku albo zły hash daje 'Tiles: failed'. Potrzebny jest nowy klucz konfiguracji ze ścieżką, a kontener loadera musi widzieć wolumen proxy, którego konfiguracji jeszcze nie ma.
- Krok kopiujący: load_demo sam kopiuje plik ze ścieżki źródłowej do katalogu serwowanego (atomowa podmiana i weryfikacja SHA-256). Ten krok implementuje osm_import zamiast map_tiles, więc zmienia się własność zapisana w PRD. Potrzebne są dwa klucze konfiguracji i ten sam brakujący wolumen.
```

Closed question of the agent, English translation by the agent:

```text
What should load_demo do with the tiles, given that map_tiles delivered no step, only a file to be uploaded by hand?

- Without tiles (Recommended): load_demo has two steps: OSM, then samples. The pmtiles file is uploaded by hand following MAP_SETUP.md, in line with Adrian's D-1. I correct the PRD (FR-3, FR-4, AC-4, AC-6, AC-9, AC-10), the osm_import row in MVP.md and FINAL_CHECKLIST 3.4. No configuration key is added.
- Verifying step: The file is still uploaded by hand, but load_demo, in the tiles step, checks whether the archive lies under a configured path and has the recorded SHA-256. A missing file or a wrong hash gives 'Tiles: failed'. A new configuration key with the path is needed, and the loader container must see the proxy volume, whose configuration does not exist yet.
- Copying step: load_demo itself copies the file from a source path into the served directory (atomic replacement and SHA-256 verification). This step is implemented by osm_import instead of map_tiles, so the ownership recorded in the PRD changes. Two configuration keys are needed, and the same missing volume.
```

User answer, original in Polish:

```text
postaw inicjatywę, która spełni wymagania tych kafelków, zaraz ja zrobię. Z tą się wstrzymajmy na razie
```

User answer, English translation by the agent:

```text
set up an initiative that will meet the requirements of these tiles, I will do it shortly. Let's hold off on this one for now
```

Closed naming question of the agent, original in Polish, quoted for context:

```text
Jak nazwać nową inicjatywę na krok ładowania kafelków? Nazwa katalogu i prefiks plików zostają na stałe.
```

Closed naming question of the agent, English translation by the agent:

```text
What should the new initiative for the tile-loading step be called? The directory name and the file prefix are permanent.
```

User answer, as selected:

```text
tile_loading (Recommended)
```
