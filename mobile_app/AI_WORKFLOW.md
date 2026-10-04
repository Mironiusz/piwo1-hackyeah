# AI Workflow

No API keys, credentials or personal data are stored in this repository.

## 1. AI tools used in development

| Tool / model | Used for |
|---|---|
| Claude (Anthropic), agentic coding session with access to the project folders | reading the product specification and mock-ups, writing ArkTS code, unit tests, sample data and documentation |
| Local verification harness (built during the session) | ArkTS strict type checking against the OpenHarmony SDK 6.0 (API 20) before each build; unit tests on Node with the SDK's TypeScript fork; full hvigor builds |

Reusable instructions: `CLAUDE.md` / `AGENTS.md` (English in the repo, no commits by the agent, API 20, no secrets, ask instead of guessing contracts).

## 2. Workflow

- **Scope.** The user asked for the app only, without a backend ("masz zrobic tylko frontend w postaci aplikacji"); product rules come from the piwo1-hackyeah specification.
- **Design.** The user pointed to the mock-up artifact "Widoki MVP: makiety" and asked for the app to look exactly like it, with an API connection added later. The agent captured every artboard (System, V-2 to V-14) and rebuilt the screens, tokens and fonts (Barlow Semi Condensed, Barlow Condensed) from them.
- **Name.** The header shows the product name EnableMe, decided by the team on 2026-10-04, where the mock-ups first had a placeholder; the user asked the agent to put it everywhere the repository named the product otherwise.
- **Data layer.** Because the API is not decided, screens use a `Repository` interface implemented on the device (`LocalRepository`), so no endpoint is guessed.
- **Sample data.** `tools/accessway_sample.py` generates a schematic network around Tauron Arena laid out like the mock-ups, with all four segment states, a lowered kerb, a steep incline, stairs at the park entrance and an alternative path. Every sample report is labelled "dane przykładowe" in the app.
- **Validation.** 0 ArkTS errors in the hvigor build, unit tests for the domain rules, and the sample scenarios printed and checked against the mock-ups (route length, data gaps, facts on the route, alternative route).

## 3. AI features in the product

None. Statuses, route ratings and alternatives come from fixed, tested rules.

## 4. Limitations

- Everything runs on the device until the API is connected; accounts, votes and reports are local.
- Visual comparison with the mock-ups on the emulator is manual.

## 5. Third-party components

| Component | Licence | Use |
|---|---|---|
| `@oniroproject/oniro-app` CLI | Apache-2.0 | build tooling |
| OpenHarmony SDK 6.0 | Apache-2.0 | compilation |
| `@ohos/hypium` | Apache-2.0 | unit test framework |
| Barlow fonts | SIL OFL 1.1 | typography |
| Material Symbols (part of the icons) | Apache-2.0 | icons |
| OpenStreetMap data (optional download) | ODbL | map data |
