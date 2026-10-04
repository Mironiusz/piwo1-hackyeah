# AI workflow of the HarmonyOS client

Document state: 2026-10-04. This file covers the HarmonyOS client in `mobile_app/`; the workflow of the rest of
the repository is in `AI_WORKFLOW.md` in its root. No API keys, credentials or personal data are stored in this
repository.

## 1. Tools

| Tool                                                                                                             | Used for                                                                                                                                                                                                     |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Claude (Anthropic), model Claude Opus 5.5, in one long agentic session of the Claude app on 3 and 4 October 2026 | reading the specification, the contract and the mock-ups; writing the ArkTS code, the unit tests, the mock of the service and the documentation; building, running and debugging                             |
| A cloud workspace of that session (Linux container)                                                              | QEMU emulator runs without KVM, the reference tile decoder in Python, comparisons, screenshots                                                                                                               |
| The bridge of the Claude desktop app to Kuber's computer (MCP server `remote-devices`)                           | a shell limited to the folders Kuber connected (the working folder of the client and this repository), moving files between the computer and the cloud workspace, hvigor builds with the SDK installed there |
| Claude subagents (general-purpose), same model                                                                   | an independent review of the mock of the service against `docs/product/api_contract.md`; the translation of the Polish comments and the client README into English, four agents on disjoint sets of files    |
| OpenHarmony toolchain                                                                                            | the ArkTS checker of hvigor as a gate before every build, `hdc` and `uitest` for driving the emulator                                                                                                        |

No AI feature is part of the product (section 5).

Reusable instructions: `CLAUDE.md` and `AGENTS.md` in `mobile_app/` (English in the repository, Polish in the
conversation, no commits or pushes by the agent, API 20, no secrets, no line comments, ask instead of guessing a
contract), and the rules of the root of the repository, which the agent followed once the client moved here.

## 2. How the work went, with the main prompts

The prompts were in Polish; each is quoted verbatim, followed by an English translation by the agent.

1. The app from the mock-ups. Kuber pointed at the team artifact "Widoki MVP: makiety" and asked for the app to
   look exactly like it, with the API connected later: "masz zrobic tylko frontend w postaci aplikacji" (you are
   to make only the frontend, as an app). The agent captured every artboard (System, V-2 to V-14) and rebuilt the
   screens, the tokens and the fonts. Screens use a `Repository` interface implemented on the device, so no
   endpoint was guessed.
2. "przygotuj plik .md z instrukcjami odnośnie instalacji emulatora na windowsa i linuxa" (prepare a .md file with
   instructions for installing the emulator on Windows and Linux) - now `docs/setup/EMULATOR_SETUP.md` in the root.
3. "nie pisz api, ale przygotuj aplikacje pod podane endpointy, podaj gdzie podac adres do api i jak to podpiac"
   (do not write the API, but prepare the app for the given endpoints, say where to put the API address and how to
   connect it) - `ApiRepository`, `ApiClient` and `ApiMapping` from `docs/product/api_contract.md`, the address in
   `rawfile/config/api.json`.
4. "przygotuj mock backendowy zwracajacy odpowiednie map_tiles, polacz go z aplikacja i odpowiednio renderuj te
   kafelki. pobierz mape dla krakowa" (prepare a backend mock returning the right map tiles, connect it to the app
   and render the tiles properly; get the map of Kraków) - the Kraków archive cut from the Protomaps build and a
   Canvas renderer of vector tiles.
5. "jak mapa jest oddalona to aplikacja strasznie zwalnia, jest jakas opcja aby to zoptymalizowac?" (when the map
   is zoomed out the app slows down terribly, is there a way to optimise it?) - fewer and simpler tiles and a
   cached bitmap of the base map that panning only moves.
6. The initiative `plans/stage5_harmonyos_port/`: the shape interview with Kuber chose the native client, all
   sixteen operations, the map read from the same PMTiles archive as the web app, the clean-up of tracked
   non-source files and one set of instructions. On the map Kuber answered: "kafelki sa pobierane z api zgodnie z
   zalozeniami w pozostalych plikach .md. jest dostepny mockowy serwer w folderze hujawei i powinien byc zgodny z
   zalozeniami api. jesli tak nie jest to popraw" (tiles are fetched from the API as the other .md files assume;
   the mock server in the hujawei folder should match the API assumptions; if it does not, fix it). The JSON tile
   endpoint of the first mock was not in any document, so it was removed and the client got its own PMTiles
   reader.
7. "zbuduj poprawny mockowy serwer api na podstawie dokumentacji i stestuj całą aplikację w qemu" (build a correct
   mock API server from the documentation and test the whole app in QEMU) - `tools/mock_backend/api_mock.py`, the
   contract check, the independent review by a subagent and an end-to-end run on the emulator.
8. "przenies zmiany do piwo1" and "popraw wszystkie z tych zmian" (move the changes to piwo1; fix all of these) -
   the client moved into `mobile_app/`, signing material and build output untracked, one emulator guide, comments
   translated.

## 3. How generated output was reviewed and validated

- The ArkTS checker of hvigor: every change was built before it was reported; 0 errors.
- Unit tests on Node with the TypeScript compiler of the SDK (`make test`): domain rules, contract mapping and the
  map decoder.
- The tile decoder against a reference implementation in Python on 57 tiles of the Kraków archive:
  byte-identical output.
- The mock of the service against the contract: `tools/mock_backend/contract_check.py`, 50 checks, plus a review by
  a separate subagent that had not written the mock. It found nine discrepancies in the mock and three in the
  client; all were fixed before the emulator run.
- An end-to-end run on the Oniro emulator against the mock, step by step with screenshots: needs, map, address
  search, route, fact and vote with its daily limit, report, account, moderation. The run found a defect the tests
  had not: buttons and switches did not update inside a screen, because the parts in `components/Ui.ets` did not
  take their values as `@Prop`.
- After the translation of the comments a script removed the comments from every file and compared the rest with
  the code before: all 54 files identical.
- A build from a copy holding only the tracked files, with signing material generated by `make sign`, to check
  the instructions from a clean clone.
- Kuber reviewed the changes in the repository and committed them himself; the agent never commits or pushes.

## 4. Unsuccessful approaches and lessons learned

- A JSON tile endpoint in the mock: faster to draw, but not part of any document of the project, so it was
  replaced by reading the PMTiles archive in byte ranges, like the web app.
- Redrawing the whole base map on every frame made the app slow when zoomed out; a cached bitmap of the base map
  fixed it.
- The emulator without KVM: the software renderer llvmpipe crashed on the AVX2 code emulated by QEMU, older CPU
  models crashed system services that need AVX2, and the screenshots of `snapshot_display` were stale. What worked
  is in `docs/setup/EMULATOR_SETUP.md`, section Without KVM. Lesson: use the emulator with KVM for the demo.
- A script that normalised line endings while copying the client into this repository also changed eight binary
  files (images and fonts); they were restored from git and the copy was compared again. Lesson: never rewrite
  bytes of a file that is not text.
- History: the client was developed in a separate working folder that was not a git repository, and came into
  this repository in one commit ("Mobile app initial commit") and then on the branch `js/stage5_harmonyos_port`.
  Its progress is therefore recorded in this document and in `plans/stage5_harmonyos_port/` rather than in a long
  commit history.

## 5. AI features in the product

None. Statuses, segment states, routes and alternatives come from fixed, tested rules, on the device or in the
service.

## 6. Limitations

- The client has run against the mock of the service only; the service of the project was not running yet.
- The comparison with the mock-ups on the emulator is visual and manual.

## 7. Third-party components

| Component                                                                    | Licence                       | Use                             |
| ---------------------------------------------------------------------------- | ----------------------------- | ------------------------------- |
| `@oniroproject/oniro-app` CLI                                                | Apache-2.0                    | build tooling                   |
| OpenHarmony SDK 6.0                                                          | Apache-2.0                    | compilation                     |
| `@ohos/hypium`                                                               | Apache-2.0                    | unit test framework             |
| Barlow fonts                                                                 | SIL OFL 1.1                   | typography                      |
| Material Symbols (part of the icons)                                         | Apache-2.0                    | icons                           |
| OpenStreetMap data (optional download, and inside the Protomaps archive)     | ODbL                          | map data, attributed on the map |
| Protomaps basemap build (PMTiles archive cut by `make tiles`, not committed) | ODbL data, BSD-3-Clause tools | base map                        |
| go-pmtiles CLI (downloaded by `make tiles`, not committed)                   | BSD-3-Clause                  | cutting the archive             |
