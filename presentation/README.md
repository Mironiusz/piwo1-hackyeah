# EnableMe deck

The pitch deck of EnableMe for the two HackYeah 2026 challenges, built from one codebase in two languages: Polish for Kraków bez barier (the PDF submitted on HackTribe) and English for Imagine What's Next (Huawei). Each language builds into one HTML file that works offline, with animations bound to the clicks of a remote, a presenter view with timing, and PDFs made from the same file.

How the code is built, the slide module API and the rules for colors and animation: [MODULE.md](MODULE.md).

## Running

All commands run in `presentation/`. Node and npm are the only prerequisites.

| Command                           | What it does                                                          |
| --------------------------------- | --------------------------------------------------------------------- |
| `npm install`                     | installs the dependencies pinned in `package-lock.json`               |
| `npx playwright install chromium` | once per machine: the browser used for snapshots and PDFs             |
| `npm run dev:pl`                  | live preview of the Polish deck at the address printed in the console |
| `npm run dev:en`                  | the same for the English deck                                         |
| `npm run build`                   | builds both decks: `dist/pl/index.html` and `dist/en/index.html`      |
| `npm run build:pl`                | builds the Polish deck only (`build:en` for the English one)          |
| `npm run preview`                 | serves the whole `dist/`, the decks are at `/pl/` and `/en/`          |
| `npm run snapshots`               | after a build: a screenshot of every slide at every step              |
| `npm run pdf`                     | after a build: the PDFs of both decks                                 |
| `npm run lint`                    | prettier check, style check and content check                         |
| `npm run format`                  | formats the code unit with prettier                                   |

`snapshots` and `pdf` work on both languages by default. A language code limits them to one deck, and `snapshots` also takes slide ids to limit the screenshots:

```bash
npm run pdf -- pl
npm run snapshots -- en title
```

For the talk it is enough to open `dist/pl/index.html` or `dist/en/index.html` in Chrome or Firefox. The file carries its scripts, styles and fonts inside and needs neither a server nor internet, so it can be copied to a USB stick or sent by e-mail.

## Presenter keys

| Key                     | Action                                               |
| ----------------------- | ---------------------------------------------------- |
| `->`, `Space`, `PgDown` | next animation step or next slide (the remote)       |
| `<-`, `PgUp`            | step back, the state is set at once                  |
| `S`                     | presenter view: notes, clock and pace, the next step |
| `F`                     | full screen                                          |
| `Esc`                   | overview of all slides                               |

The speaker notes start with the planned time of the slide and the time at which it should end, mark every click as `[click]`, and end with a `Next:` line that says what the next slide is about.

## PDFs

`npm run pdf` writes three files per language next to the built deck, in `dist/<lang>/`:

- `enableme-deck-pl.pdf` - one page per slide in its final state, with vector text. This is the file submitted to HackTribe for Kraków bez barier, which accepts a PDF of at most 10 slides; `npm run snapshots` fails when the deck has more. `enableme-deck-en.pdf` is its English counterpart for Huawei.
- `enableme-deck-<lang>-steps.pdf` - one page per click, made of screenshots, for running the talk from a PDF viewer when the HTML file fails.
- `enableme-deck-<lang>-notes.pdf` - the slides with a page of speaker notes after each, for a rehearsal from paper.

A new build of a language empties its `dist/<lang>/`, so the PDFs always have to be made again after a build.

## Rehearsal mode

Opening a deck with `?rehearsal` at the end of the address, for example `dist/pl/index.html?rehearsal`, measures how long each slide stays on screen. The times survive a reload of the page and are kept apart for each language. After the rehearsal, in the browser console:

- `__rehearsal()` prints a table of times and returns ready entries for `src/slides/timing.js`,
- `__rehearsal.reset()` starts a new measurement.

## Checks

`npm run lint` runs three checks. Prettier checks the formatting of the whole code unit. `scripts/style-check.mjs` looks for the forbidden characters of `docs/standards/standard_formatting.md`, emojis and line comments in the JavaScript, CSS and HTML files; markdown is covered by the repository gate `tests/architecture/test_prose_style.py`. `scripts/content-check.mjs` compares the structure of the two content files, so a missing translation fails the lint.

`npm run snapshots` writes the screenshots to `snapshots/<lang>/`, which git ignores, and fails when a page reports an error, reaches the network or has more than 10 slides, when a slide has a number of `[click]` markers different from its steps, no time or no summary, and when a content entry has no slide. A screenshot shows the state at the end of a step, not the motion, so the smoothness of an animation is judged in the browser.
