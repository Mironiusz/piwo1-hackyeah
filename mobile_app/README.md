# EnableMe - walking routes in Kraków for your needs

HackYeah 2026, challenge "Kraków bez barier". An OpenHarmony application (ArkTS / ArkUI, Stage model) targeting **API 20**, in `accessway/`.

The user marks which barriers they avoid (stairs, high kerb, poor surface, steep incline, narrow passage) and which amenities they need (elevator, ramp, lowered kerb, accessible toilet, rest place, handrail). The app never asks about disability. It then:

- shows facts about barriers and amenities on a map, each with its source (OpenStreetMap or a user report), date and status (confirmed, unverified, disputed);
- plans a walking route and rates every segment against the needs in four states: barrier from your needs, no barriers with full data, incomplete data, no data; missing information is never shown as accessible;
- lists barriers from the needs, other barriers, amenities on the route and the stretches without data, and offers an alternative route around an unverified barrier;
- lets anyone report a barrier, an amenity or an area, checks for the same fact within 15 m first, and lets others vote "still there" or "gone" once a day;
- has pseudonym accounts without e-mail, a privacy page, a data page and a moderation view.

The screens follow the team mock-ups "Widoki MVP: makiety" (artboards System and V-2 to V-14). Today all data is computed on the device from bundled sample data around Tauron Arena; the data layer is an interface ready for the team's API.

## Repository layout

```
accessway/                   OpenHarmony project (hvigor, ohpm)
  entry/src/main/ets/
    pages/                   screens (Index shell, needs, map, plan, search, route, fact, report, account, info, moderation)
    components/              theme tokens, UI parts, Canvas map, route diagram, fact glyphs
    data/                    Repository interface, LocalRepository, app state, demo reports, storage, location
    domain/                  pure logic: OSM mapping, edge rules, routing, route plan, facts, trust, needs
    model/                   types, labels (PL/EN), i18n
  entry/src/main/resources/rawfile/data/osm_sample.json   sample map data
  entry/src/test/            unit tests (hypium, run on Node)
tools/accessway_sample.py    regenerates the sample data
tools/accessway_fetch_osm.py downloads real OSM data for Kraków centre
tools/run-unit-tests.js      runs unit tests on Node with the SDK compiler
docs/                        architecture, emulator setup
AI_WORKFLOW.md               AI tools used during development
```

## Requirements

Linux x86_64 with KVM (or Windows with WSL2), Node.js >= 20, JDK 17+, QEMU, about 15 GB of free disk. Full installation guide, including Windows: `docs/EMULATOR_SETUP.md`.

## Build and run

```bash
make setup-deps     # once: apt-installs qemu + JDK 17, SDK (API 20), tools, emulator, signs the app
make emulator-fast EMU_RES=540x1080   # boots the emulator (about 1 min)
make run            # build -> install -> launch
make test           # unit tests
make uninstall      # removes the app with its saved data
```

The signed package: `accessway/entry/build/default/outputs/default/entry-default-signed.hap`. Install on any OpenHarmony 6.x device with `hdc install -r entry-default-signed.hap`.

The demo scenario (Polish) is in `accessway/README.md`.

## Privacy

- Needs stay on the device and are not part of an account.
- Reports and votes carry no author information visible to others.
- Location is read only when the user presses "Moja lokalizacja" and is not stored.
- No analytics, no keys or personal data in the repository.
