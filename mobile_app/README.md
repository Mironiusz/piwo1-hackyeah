# EnableMe - the HarmonyOS client

HackYeah 2026, challenges "Kraków bez barier" and Huawei "Imagine What's Next". A native OpenHarmony application
(ArkTS / ArkUI, Stage model, API 20) in `accessway/`, a second client of the same programming interface as
the web app (`docs/product/api_contract.md` in the root of the repository). It never embeds the web app.

The person marks which barriers they avoid (stairs, high kerb, poor surface, steep incline, narrow passage) and
which amenities they need (elevator, ramp, lowered kerb, accessible toilet, rest place, handrail on stairs). The
app never asks about disability. It then:

- shows facts about barriers and amenities on a map of Kraków, each with its source (OpenStreetMap or a user
  report), date and status (unverified, confirmed, disputed, outdated);
- plans a walking route and shows every segment in the four states of the service: barrier from your needs, no
  barriers with full data, incomplete data, no data; missing information is never shown as accessible;
- lists the barriers from the needs, the other barriers, the amenities on the route and the stretches without
  data, and offers an alternative route around an unverified barrier;
- lets anyone report a barrier, an amenity or an area after checking for the same fact within 15 m, and vote
  "still there" or "gone" once a day;
- has pseudonym accounts without e-mail, a privacy page, a data page and a moderation view.

Platform capabilities: the device location (`geoLocationManager`) as the start of a route and the place of a
report, HTTP to the service, worker threads (`taskpool`) for decoding the map, Canvas drawing.

## Versions

| Item                          | Version                                                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| Target                        | OpenHarmony API 20 (`compileSdkVersion` and `compatibleSdkVersion` 20)                                  |
| OpenHarmony SDK               | 6.0.0.47 (API 20)                                                                                       |
| Command Line Tools            | 5.1.0.840 (hvigor 5.18.5, ohpm 5.1.3, codelinter 5.1.140)                                               |
| `@oniroproject/oniro-app` CLI | 0.11.0 (pinned in `scripts/env.sh`)                                                                     |
| Emulator                      | Oniro emulator, OpenHarmony 6.1.0.31, QEMU x86_64                                                       |
| Host                          | Linux x86_64 with KVM, or Windows with WSL2; Node.js 20 or newer (22 used), JDK 17+, QEMU 8.x, Python 3 |

## From a clean clone to a running package

All commands run in this directory. The full installation guide, Windows included, and what to do without KVM
is `docs/setup/EMULATOR_SETUP.md` in the root of the repository.

```bash
cd mobile_app
make setup-deps                      # once: qemu and JDK with apt, SDK, command-line tools, emulator, signing
make emulator-fast EMU_RES=540x1080  # boots the emulator (about 1 to 2 min)
make run                             # signs, builds, installs and launches
make test                            # unit tests on Node, no emulator needed
```

The signed package is `accessway/entry/build/default/outputs/default/entry-default-signed.hap`; install it on any
OpenHarmony 6.x device with `hdc install -r entry-default-signed.hap`.

`make sign` generates the debug signing material on each machine and writes it into
`accessway/build-profile.json5`; do not commit that change (`docs/setup/EMULATOR_SETUP.md`, What gets installed).

## The service and the map

`accessway/entry/src/main/resources/rawfile/config/api.json`:

- `base_url` - the address of the service without `/api`; empty means no service, the app then works on bundled
  sample data around Tauron Arena;
- `tiles_url` - the full address of the PMTiles archive of Kraków, which the app reads in byte ranges like the
  web app; empty means the bundled sample map.

The address of the hosted demo is never committed. For development, `make tiles` downloads the archive and
`make mock` runs the mock of the host of the project from `tools/mock_backend/`: all sixteen operations of the
contract under `/api` and the archive next to them. Details are in `accessway/README.md`.

## Repository layout

```
accessway/                   OpenHarmony project (hvigor, ohpm)
  entry/src/main/ets/
    pages/                   screens (Index shell, needs, map, plan, search, route, fact, report, account, info, moderation)
    components/              theme tokens, UI parts, Canvas map, route diagram, fact glyphs
    data/                    Repository interface, local and API implementations, API client, map tiles (PMTiles, MVT)
    domain/                  pure logic: OSM mapping, edge rules, routing, route plan, facts, trust, needs
    model/                   types, labels (PL/EN), i18n
  entry/src/test/            unit tests (hypium, run on Node)
tools/mock_backend/          mock of the service and the map archive, contract check
tools/run-unit-tests.js      runs unit tests on Node with the SDK compiler
docs/ARCHITECTURE.md         architecture of the client
AI_WORKFLOW.md               AI tools used while building the client
```

## Privacy

- Needs stay on the device and are not part of an account.
- Reports and votes carry no author information visible to others.
- The location is read only when the person presses "My location" and travels only in the route request.
- No analytics, no keys, hosts or personal data in the repository.
