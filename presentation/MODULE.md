# EnableMe deck

Document state: 2026-10-04

## Module role

`presentation/` builds the pitch deck of EnableMe in two languages from one codebase: Polish for the Kraków bez barier submission on HackTribe, which asks for a PDF of at most 10 slides in Polish, and English for Imagine What's Next (Huawei). Each language becomes one HTML file that works offline, with GSAP animations bound to the clicks of a remote, a presenter view with timing, and PDFs printed from that file.

The code unit holds no product behavior. It does not call the programming interface of the service, does not run in the hosted demo and is not part of the web frontend in `frontend/`. What the product does is decided by `docs/product/specification.md`; the slides only present it.

## Public interface

The interface of the code unit is its npm scripts, listed in [README.md](README.md): `dev:pl`, `dev:en`, `build`, `build:pl`, `build:en`, `preview`, `snapshots`, `pdf`, `lint` and `format`.

Inside the code unit there are two contracts other files depend on:

- `window.__deck`, set by `src/main.js` once reveal.js is ready, read by the Playwright scripts: `reveal` (the reveal.js instance), `settle()` (brings the running animation to its end), `slides` (per slide `id`, `steps`, `timing`, `summary`, `clicks`) and `totalTime`.
- In rehearsal mode, the console functions `__rehearsal()` and `__rehearsal.reset()`.

## Technical inputs and outputs

Inputs:

- the content files `src/content/pl.js` and `src/content/en.js`,
- the slide modules in `src/slides/`, their order in `src/slides/index.js` and their times in `src/slides/timing.js`,
- the npm packages `reveal.js`, `gsap`, `@fontsource/barlow-semi-condensed` and `@fontsource/barlow-condensed`.

Writes:

- `dist/pl/index.html` and `dist/en/index.html`, the built decks,
- `dist/<lang>/enableme-deck-<lang>.pdf`, `dist/<lang>/enableme-deck-<lang>-steps.pdf` and `dist/<lang>/enableme-deck-<lang>-notes.pdf`,
- `snapshots/<lang>/NN-<id>-stepK.png`, one screenshot per slide and step,
- in rehearsal mode, the localStorage key `enableme-deck-rehearsal-<lang>` of the browser.

The built deck makes no network request; the snapshot and PDF scripts fail on any.

## Operating modes

- Language: the Vite mode is the language, `--mode pl` or `--mode en`. Any other mode stops the build or the dev server with an error, so there is no default language. `vite preview` is the one command without a language, because it serves the whole `dist/`.
- Presentation: the default view of a built deck. The intro of a slide plays on entry, and every click plays one step.
- Print view: `?print-pdf` in the address, used by `scripts/pdf.mjs`. Every timeline is set to its end, so each slide shows its final state.
- Rehearsal: `?rehearsal` in the address. The time of each slide is measured and kept in localStorage until `__rehearsal.reset()`.

## File structure

```text
presentation/
  package.json, package-lock.json
  vite.config.js
  index.html
  .prettierrc, .prettierignore, .gitignore
  README.md, MODULE.md
  scripts/
    deck.mjs
    snapshots.mjs
    pdf.mjs
    style-check.mjs
    content-check.mjs
  src/
    main.js
    content/
      index.js
      pl.js
      en.js
    lib/
      lang.js
      steps.js
      rehearsal.js
      theme.js
    components/
      flow.js
      icons.js
    styles/
      theme.css
      components.css
    slides/
      index.js
      timing.js
      title.js
```

## File responsibilities

- `vite.config.js` - builds one self-contained file per language into `dist/<lang>/`, validates the mode through `contentFor`, puts the page title of the language into `index.html`, and trims the fonts to the latin and latin-ext subsets in woff2 (`trimFonts`).
- `index.html` - the page shell; Vite fills `lang` from the mode and the title from `page.title` of the content file.
- `src/main.js` - assembles the slides into reveal.js sections, renders the speaker notes with timing and the `Next:` line, attaches the timelines and starts reveal.js.
- `src/content/index.js` - the map of content per language, `LANGUAGES`, and `contentFor(lang)`, which throws on an unknown language. It is imported by the build config, the deck and the scripts.
- `src/content/pl.js`, `src/content/en.js` - every word of the deck, one file per language. `pl.js` is the only file of the code unit with Polish text.
- `src/lib/lang.js` - `LANG` and `content` of the build, and `slideText(id)`, which throws when a slide has no entry in the content file.
- `src/lib/steps.js` - turns the segments of a slide into one GSAP timeline with a label per step, adds one invisible reveal.js fragment per step and keeps the timeline in sync with the reveal.js events.
- `src/lib/rehearsal.js` - the rehearsal mode.
- `src/lib/theme.js` - `token(name)`, the value of a color token, for color tweens.
- `src/components/flow.js` - flow diagrams: `flowRow`, `flowColumn`, `vArrow`, `vArrowUp`, `hArrow`; returns the SVG and the geometry of the boxes.
- `src/components/icons.js` - symbols missing from the fonts, drawn in SVG: `ARROW`, `APPROX`, `CHECK`, `CROSS` for HTML, `svgArrow`, `svgArrowDown`, `svgCheck`, `svgCross` for SVG drawings. Their spoken labels come from `page.icons` of the content file.
- `src/styles/theme.css` - the color and font tokens, the slide frame, the progress bar and the slide number.
- `src/styles/components.css` - the shared classes: `.slide-title`, `.kicker`, `.footnote`, `.accent`, `.tag`, `.canvas`, the title slide, SVG text, icons, flow diagrams and the notes page of the PDF.
- `src/slides/index.js` - the order of the slides.
- `src/slides/timing.js` - `TIMING`, the seconds per slide, and `clock(seconds)`.
- `src/slides/title.js` - the placeholder title slide that proves the pipeline; it is to be replaced by the real deck.
- `scripts/deck.mjs` - shared by the Playwright scripts: the language arguments, opening a built deck from disk with every network request and page error recorded, and moving to a slide and step.
- `scripts/snapshots.mjs` - the screenshots and the contract checks of the deck.
- `scripts/pdf.mjs` - the three PDFs per language.
- `scripts/style-check.mjs` - forbidden characters, emojis and line comments in JavaScript, CSS and HTML files.
- `scripts/content-check.mjs` - the same structure of both content files.

## Main records and contracts

### Slide module

One file per slide, `src/slides/<id>.js`, imported in `src/slides/index.js`. Styles used by that slide alone go next to it as `src/slides/<id>.css`, imported from the module. The default export is an object:

| Field              | Required | Meaning                                                                                |
| ------------------ | -------- | -------------------------------------------------------------------------------------- |
| `id`               | yes      | unique; the key in the content files, in `timing.js`, in the URL and in snapshot names |
| `summary`          | yes      | one phrase about the slide, shown as `Next:` in the notes of the previous slide        |
| `html`             | yes      | the content of the slide, without a `<section>` tag                                    |
| `notes`            | no       | speaker notes in HTML, one `[click]` marker per step                                   |
| `animate(section)` | no       | returns the segments `[intro, step1, step2, ...]`                                      |

Each segment is `(tl) => { tl.to(...) }` and appends its tweens to the timeline of the slide; an empty intro is `null`. The intro plays on entering the slide, every next segment is one click. A slide holds structure and animation only, and takes every word from the content file:

```js
import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';

const ID = 'example';
const text = slideText(ID);

export default {
  id: ID,
  summary: text.summary,
  html: `
    <h2 class="slide-title">${text.heading}</h2>
    <p class="example-later">${text.later}</p>`,
  notes: text.notes,

  animate(root) {
    const later = root.querySelector('.example-later');
    gsap.set(later, { opacity: 0 });
    return [
      null,
      (tl) => {
        tl.to(later, { opacity: 1, duration: 0.5 });
      },
    ];
  },
};
```

A new slide therefore takes four places: its module, its import in `src/slides/index.js`, its entry under `slides.<id>` in both content files and its time in `src/slides/timing.js`.

### Content module

`src/content/pl.js` and `src/content/en.js` export by default an object of the same structure:

```js
export default {
  page: {
    title: 'the title of the HTML page',
    icons: { arrow: '...', approx: '...', check: '...', cross: '...' },
  },
  slides: {
    title: { summary: '...', kicker: '...', heading: '...', subtitle: '...', notes: '<p>...</p>' },
  },
};
```

- `page.title` becomes the `<title>` of the built page, `page.icons` the spoken labels of the icons.
- `slides.<id>` holds the words of one slide. `summary` and `notes` are read by the engine; every other key is chosen by the slide and read only by its module. A value may be a string, a list or a nested object, and may carry HTML, as the notes do.
- Both files have the same keys at every level, the same type of every value and the same length of every list. `scripts/content-check.mjs`, run by `npm run lint`, fails on any difference.
- A content entry without a slide, and a slide without a content entry, are errors: the first is reported by `npm run snapshots`, the second throws when the deck loads.

### Timing

`src/slides/timing.js` exports `TIMING`, an object from slide id to seconds, shared by both languages. `src/main.js` passes it to reveal.js (`data-timing` per slide, `totalTime`) for the pace clock of the presenter view and writes the time and the planned end of each slide at the top of its notes, formatted by `clock(seconds)`. A slide without a time fails `npm run snapshots`.

### Animation rules

- A state that changes in a later step is set with `gsap.set()` outside the timeline, and the timeline uses `to()`. Going back to step 0 then restores the state from `set()`.
- `from()` is allowed for a simple entrance, but never twice on the same property of the same element: the second `from()` records the hidden value as its end and the element never appears. An element that enters in a later step after being visible before uses `fromTo(..., { immediateRender: false })`.
- The first tween of a segment never has a relative position (`'<'`, `'<0.3'`). It would be counted from the start of the last tween of the previous step and the animation would run into a step that is not its own.
- GSAP does not interpolate `var(--...)`; color tweens take the value from `token('--name')`.
- No DOM measurements: reveal.js hides inactive slides, so a measurement while building returns zeros. Geometry comes from constants, as in `flow.js`.
- Motion that has to be seen is drawn above the nodes, not under them.
- The `html` of a slide never contains `<section>`: reveal.js treats a nested section as a vertical slide.
- The number of `[click]` markers in the notes equals the number of steps; `npm run snapshots` fails otherwise. Intermediate states of an animation are checked with a separate Playwright run that clicks and waits, because a snapshot shows only the end of a step.

### Colors

Slides use only the tokens of `src/styles/theme.css`, never a raw hex value. One color has one meaning in the whole deck:

| Token                                                                   | Flow and tag class                                  | Meaning                                                |
| ----------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------ |
| `--primary` (navy), `--on-primary`                                      | `is-primary`                                        | the product, our system; slide titles                  |
| `--accent` (yellow), `--on-accent`                                      | `is-accent`, `.accent`                              | what we look at now; the progress bar                  |
| `--state-barrier`, `--state-clear`, `--state-partial`, `--state-nodata` | `is-barrier`, `is-clear`, `is-partial`, `is-nodata` | the four route segment states, only those              |
| `--state-disputed`                                                      | `is-disputed`                                       | the disputed status of a fact                          |
| `--text`, `--text-dim`, `--text-muted`                                  | `is-dim`, `.t-dim`                                  | main text, secondary text, decoration that is not read |
| `--bg`, `--surface`, `--surface-2`, `--line`, `--line-strong`           | -                                                   | background, cards, lines and arrows                    |

- Yellow is a background with dark text on it (`--on-accent`), never a text color on the light background.
- The four segment state colors mean nothing but the segment states, and always come with a label or a pattern, never color alone. The tokens and their values are those of the HarmonyOS app (`mobile_app/accessway/entry/src/main/ets/components/Theme.ets`), where the same colors draw the segments of a route.
- `--text-muted` is below the 4.5:1 contrast on `--bg`, so it never colors text that has to be read; such text uses `--text` or `--text-dim`.

### Typography and layout

- A slide is 1600 x 900 px. `src/main.js` wraps the `html` of a module in a `.slide-frame` of fixed size with 80 px side padding (`--pad-x`). Absolutely positioned elements are placed relative to that frame. No padding is set on `<section>`, because the reveal.js print view resets it.
- Barlow Semi Condensed (400, 600, 700) for text, Barlow Condensed 700 for slide titles and the title slide. Both come from Fontsource, in the latin and latin-ext subsets, which carry the Polish letters but no arrows, check marks or mathematical symbols; those are drawn by `icons.js`. A glyph a slide has to show from the list of forbidden characters stands in the code as an HTML entity.
- Body text on a slide is at least 26 px, a footnote at least 18 px.
- The bottom right corner belongs to the slide number, the bottom left to `.footnote`.

## Architectural decisions

- The engine is a pre-existing component, and the Huawei submission names it as such. It was ported on 2026-10-04 from LLM-prezentacja, an earlier presentation project of Rafał. The port kept the mechanics - reveal.js, the step timelines, the offline build, the presenter notes with timing, the rehearsal mode, the snapshot and PDF scripts, the flow diagrams and the icons - translated the code into English, and replaced the theme, the fonts and every slide.
- The deck runs in the browser instead of being a PowerPoint file, because animations built step by step are its core, and reveal.js gives remote navigation, the presenter view and a print view for the PDF.
- Steps are bound to clicks. Each animated slide has one GSAP timeline split by labels into steps, and every step is an invisible reveal.js fragment, so the remote and the keyboard work without extra handling. The state of a slide always follows from the number of visible fragments: a step forward is animated, while a step back and every jump set the state at once, so going back, returning from the next slide and reloading the page always give the right picture.
- Each deck is one file that works offline, because the room may have no internet. Vite with `vite-plugin-singlefile` puts the scripts, styles and fonts into one HTML file that works opened from disk. The fonts are installed from Fontsource, never fetched from a font service, and `trimFonts` keeps only the latin and latin-ext subsets in woff2, so the file stays near 0.5 MB. The subsets are filtered out of the full Fontsource files, because only those carry a `unicode-range` per subset.
- Both languages come from one codebase. The Vite mode is the language and the slides take their words from a content module per language, so a change of structure or animation is made once for both decks. A build with any other mode fails instead of falling back to a default language. The content check keeps the two files in step, and the time plan is shared, because the slides are the same.
- The deck uses the light theme, the color tokens and the typefaces of the EnableMe app, so the slides and the screenshots of the app look like one product.
- The submitted PDF comes from the print view, which shows every slide in its final state with vector text. A slide with intermediate states can only be presented from a PDF viewer through the steps PDF made of screenshots, so both are produced.
- The notes end with the `summary` of the next slide, which is kept in the module of the slide it describes, so a change of order in `src/slides/index.js` corrects every announcement by itself. The labels of the notes - `Time`, `ends at`, `Next:` and the `Speaker notes` heading of reveal.js - are English in both decks.
- The code unit has its own `.prettierrc` with single quotes in JavaScript, the style the engine was written in. The double quotes of `docs/standards/standard_frontend.md` apply to the web frontend in `frontend/`, not to this unit.
- Several parts of the source engine were dropped. The stage map in the corner went with its list of stages, because a deck of at most 10 slides needs no map of its parts. The slide variants switched by a digit went, because the pitch has no decision taken live. KaTeX and `math.js` went, because the deck has no formulas and KaTeX would add its own fonts to the file. The 3D vector space, the token chips and the components that drew the content of the earlier talk went with that content. The IBM Plex fonts went with their monospace face, and with it the `.mono` class and the code card, because the brand has no monospace face and a system one would look different on every computer. `svg-text.js` and `visibility.js` went, because no kept module used them.

## Summary

`npm run snapshots` prints the time plan of each language and the number of screenshots saved; `npm run pdf` prints the path of each PDF and the page count of the steps PDF. Both end with exit code 1 and a list of the problems found, each prefixed with its language. `scripts/style-check.mjs` lists each violation by file and line, `scripts/content-check.mjs` by its path in the content object; both end with exit code 1 when they find anything and 0 otherwise.

## Relation to MODULE_ALGORITHM.md

There is no `MODULE_ALGORITHM.md`: the code unit has no domain behavior, and what the product does is described in `docs/product/specification.md`.
