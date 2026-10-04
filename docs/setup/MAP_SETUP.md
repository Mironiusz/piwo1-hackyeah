# Map setup: the tile archive, the fonts and the style of the base map

Document state: 2026-10-04

## Why this document exists

The frontend draws one map of Kraków, and the browser takes every file of that map from the host of the page. This document says which files those are, where each of them comes from, how a member of the team gets a working map, and how the tile archive is handed to the persons who load it on the server. It also keeps the record of the archive, by which a copy of it is checked.

It was written by `plans/map_tiles/`; the decisions and their reasons are in `plans/map_tiles/MAP_TILES_PLAN.md`.

## What the map needs

| Address the browser asks for         | File                                   | In the repository  |
| ------------------------------------ | -------------------------------------- | ------------------ |
| `/tiles/krakow.pmtiles`              | `frontend/public/tiles/krakow.pmtiles` | no, git ignores it |
| `/map/style-pl.json`                 | `frontend/public/map/style-pl.json`    | yes, generated     |
| `/map/style-en.json`                 | `frontend/public/map/style-en.json`    | yes, generated     |
| `/map/fonts/{fontstack}/{range}.pbf` | `frontend/public/map/fonts/`           | yes, nine files    |

The style uses no sprite, so there is no fifth kind of file. The application loads the style of the current language of the interface.

## The tile archive

The archive is one file of vector tiles in the PMTiles format, cut out of the daily Protomaps build of OpenStreetMap data. It is never committed: it is a binary file of tens of megabytes.

| Property              | Value                                                              |
| --------------------- | ------------------------------------------------------------------ |
| Build it was cut from | `20261003`                                                         |
| OpenStreetMap state   | 2026-10-03 04:00 UTC                                               |
| Size                  | 34 785 215 bytes                                                   |
| Bounds                | longitude 19.792236 to 20.217346, latitude 49.967667 to 50.126134  |
| Zoom                  | 0 to 15                                                            |
| Tiles                 | 1295                                                               |
| SHA-256               | `21cc383fd4b33a55e25c900ac8aded3f672c8bcb4758a30dcd3c813d7d7ab8b1` |

Adrian cut it on 2026-10-03 with the pmtiles command line tool 1.31.2:

```bash
pmtiles extract https://build.protomaps.com/20261003.pmtiles krakow.pmtiles --bbox=19.7922355,49.9676668,20.2173455,50.1261338
```

The bounding box is the one of the administrative boundary of Kraków (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`, D-5 and F-15).

## A machine of the team

1. Get the file `krakow.pmtiles` from Adrian. When that is not possible, cut it with the command above, as long as Protomaps still offers the build `20261003`.
2. Check the file. A copy of the file of Adrian has the SHA-256 value of the table:

   ```bash
   sha256sum krakow.pmtiles
   ```

   A file cut again may differ in its bytes; check it with `pmtiles show krakow.pmtiles` against the bounds, the zoom range and the number of tiles of the table.

3. Put the file at `frontend/public/tiles/krakow.pmtiles`. Git ignores that directory.
4. The fonts and the two style files are already in the repository, so nothing else is fetched.

The application that draws the map is the frontend in `frontend/`, built by `plans/frontend_app/`. To see the map, install its packages once and start its two development programs, each in its own terminal, then open the address the second one prints:

```bash
npm --prefix frontend install
npm --prefix frontend run mock
npm --prefix frontend run dev
```

The first program is the temporary mock of the service, which the frontend runs on until a backend answers (`frontend/FRONTEND.md`, section Operating modes). The map itself needs only the archive of step 3.

## Handing the archive to the server

The archive is not in the repository, so it reaches the server of the demo as a file. Adrian hands it to the backend persons, who load it on the server; this initiative builds no step of the loading program (`plans/map_tiles/MAP_TILES_PLAN.md`, D-1). The backend persons have not confirmed this yet.

What the server has to provide:

- The file answers at the address `/tiles/krakow.pmtiles` on the host of the page.
- The server answers byte range requests for it, because the browser reads the file in parts and never as a whole.
- After the copy, the SHA-256 value of the file on the server equals the one of the table above.

No address, login or secret of the server is written into the repository. Until the server serves the archive, the frontend takes it from `frontend/public/tiles/` on the machine it runs on.

## The fonts

The labels of the map use three weights of Noto Sans. The repository holds nine files, three ranges of each weight, copied without a change from the directory `fonts/` of `https://github.com/protomaps/basemaps-assets` on 2026-10-03. The full set there has 768 font files for every script of the world; Kraków needs the three ranges below, which hold the Latin letters with the Polish ones and the general punctuation. A label in another script is not drawn.

| File under `frontend/public/map/fonts/` | Bytes  | SHA-256                                                            |
| --------------------------------------- | ------ | ------------------------------------------------------------------ |
| `Noto Sans Regular/0-255.pbf`           | 76044  | `62c6d49b15fa836eb6aa45e259c7ca6762f44b011b09e47776efbe4a6db1b397` |
| `Noto Sans Regular/256-511.pbf`         | 127726 | `2eca7561f9f566bcacfda5dd04fb5880baec1328ec0f5484678289a13994de8a` |
| `Noto Sans Regular/8192-8447.pbf`       | 64220  | `8ea977a587352fe31b4159ffdbc9a40be79056f2472017c742ea1e4a931864b9` |
| `Noto Sans Medium/0-255.pbf`            | 77628  | `ba2f0118dd024e3041b158e5f9eb49bc0a658019f53f458e9f5c0b8efcd79b91` |
| `Noto Sans Medium/256-511.pbf`          | 129635 | `d5e801a1a5b1d409d3298c3a1e1ca76328e2314a751078833a618620e8e66e4d` |
| `Noto Sans Medium/8192-8447.pbf`        | 65101  | `cc38e4956207f0edba1aaf749b61e8f6f1678ef1ad443d32ee285b21d0eb67aa` |
| `Noto Sans Italic/0-255.pbf`            | 79344  | `43edfca91c285ba1226f09d5e74d68e1473a088c517f02a5212ff6ccb10037dc` |
| `Noto Sans Italic/256-511.pbf`          | 132976 | `a6f9f6574c86a4a28aba630ca1017857ceadd2370ed32a1293c35f819ab9bd60` |
| `Noto Sans Italic/8192-8447.pbf`        | 52891  | `5dc4e6680116fef01be024e272859d130262613c7e634409a590e5d50ad124ae` |

## The style

The two style files are generated by `frontend/scripts/generate_base_map_style.mjs` from the Protomaps style package, release 5.7.2. They are committed, and a change of a color is made in the script, never in a generated file.

The style package is a development dependency of the frontend project, pinned by `frontend/package-lock.json`, so `npm --prefix frontend install` installs it.

Write both files, with the script itself or with `npm --prefix frontend run map-style`:

```bash
node frontend/scripts/generate_base_map_style.mjs
```

Check that the committed files equal what the script generates and keep every rule below, with the script itself or with `npm --prefix frontend run map-style:check`. The rules also have unit tests, `frontend/scripts/generate_base_map_style.test.ts`, run with the tests of the frontend:

```bash
node frontend/scripts/generate_base_map_style.mjs --check
```

The colors follow the mocks of `.impeccable/briefs/views/`:

| What                                 | Color     |
| ------------------------------------ | --------- |
| The ground                           | `#ECECE3` |
| Parks, woods and other green         | `#D3E1CB` |
| Other land use, for example a school | `#E6E6DC` |
| Water                                | `#C5D6DF` |
| Buildings                            | `#DDDDD2` |
| Streets, paths and bridges           | `#FFFFFF` |
| Tunnels                              | `#F4F5F2` |
| The outline of a street              | `#D5D8DC` |
| Railways and boundaries              | `#B9BDC4` |
| Every label                          | `#4B5058` |

The rules the script keeps and its check verifies:

- The style has no sprite and no layer that draws an icon. The points of interest, the arrows of one-way streets and the road shields of the style package are left out, and the names of localities keep their text and lose their icon.
- The only fonts are the three weights of the section above.
- The only addresses are `pmtiles:///tiles/krakow.pmtiles` for the archive and `/map/fonts/{fontstack}/{range}.pbf` for the fonts. The one outside address is the link of the attribution, which a browser opens only when a person presses it.
- The attribution is the one the archive stores: a link to the copyright page of OpenStreetMap with the text of the copyright sign and the name OpenStreetMap. The map shows it always open.
- The file with Polish labels shows the Polish name of a place, and the file with English labels the English name where the archive has one and the local name otherwise.
- The files hold none of the characters `docs/standards/standard_formatting.md` forbids, and they are formatted with the prettier configuration of the repository.

The look of the style on a drawn map was not checked when these files were written, because no application existed yet. It was checked on 2026-10-04, when `plans/frontend_app/` built the map: the result is in `plans/map_tiles/MAP_TILES_REVIEW.md`, section Acceptance criteria checked on the drawn map.

## Licences

- The data of the archive come from OpenStreetMap under the Open Database License, with the attribution shown on the map.
- The style package of Protomaps is under the BSD-3-Clause licence.
- The fonts are under the SIL Open Font License.

Nothing here is legal advice.
