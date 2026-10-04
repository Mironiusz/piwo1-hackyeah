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
  materials/
    video_script.md
    pitch.md
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
      icons.js
      route-states.js
    styles/
      theme.css
      components.css
    slides/
      index.js
      timing.js
      <id>.js, <id>.css   one module per slide, with the styles only that slide uses
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
- `src/components/icons.js` - `ARROW`, the arrow missing from the fonts, drawn in SVG, with its spoken label from `page.icons` of the content file.
- `src/components/route-states.js` - `routeStates`, a route of four segments from A to B in the four segment states of the app, each with its color, its icon in a badge and the line pattern the app draws it in, in the sizes `large` and `small`, and `STATE_KEYS`, the order of the states; used by the slides `title` and `states`.
- `src/styles/theme.css` - the color, font and layout tokens, the shell with its light, the slide frame, and the progress blocks and the slide number drawn inside the frame, with the position of every slide.
- `src/styles/components.css` - the shared classes: the four parts of a slide (`.slide-title`, `.sheet`, `.plate`, `.note`), `.brand`, SVG text, icons, the notes page of the PDF, the text blocks shared by the slides (`.lead`, `.plain-list`, `h3`, `.chip-row`, `.chip`, `.card-num`) and the `.rs-*` styles of the route.
- `src/slides/index.js` - the order of the slides.
- `src/slides/timing.js` - `TIMING`, the seconds per slide, and `clock(seconds)`.
- `src/slides/<id>.js` - the ten slides, in order: `title`, `problem`, `solution`, `states`, `facts`, `demo`, `data`, `architecture`, `business`, `status`. The notes of each slide are the spoken text of the pitch.
- `materials/video_script.md` - the script of the Polish video of the Kraków submission, recorded on the HarmonyOS emulator.
- `materials/pitch.md` - how the pitch is given: timing, roles, the live demo and its fallbacks, the rehearsal and the answers to the questions of the jury.
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
    icons: { arrow: '...' },
  },
  slides: {
    title: { summary: '...', kicker: '...', heading: '...', subtitle: '...', notes: '<p>...</p>' },
  },
};
```

- `page.title` becomes the `<title>` of the built page, `page.icons` the spoken label of the arrow icon.
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
- No DOM measurements: reveal.js hides inactive slides, so a measurement while building returns zeros. Geometry comes from constants, as in `route-states.js`.
- Motion that has to be seen is drawn above the nodes, not under them.
- The `html` of a slide never contains `<section>`: reveal.js treats a nested section as a vertical slide.
- The number of `[click]` markers in the notes equals the number of steps; `npm run snapshots` fails otherwise. Intermediate states of an animation are checked with a separate Playwright run that clicks and waits, because a snapshot shows only the end of a step.

### Colors

Slides use only the tokens of `src/styles/theme.css`, never a raw hex value. One color has one meaning in the whole deck:

| Token                                                                   | Where                                                                                                                    | Meaning                                       |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| `--bg` (navy), `--bg-lift`, `--bg-deep`                                 | the ground of every slide, with the light in its top right corner                                                        | the shell of the app                          |
| `--on-shell`, `--on-shell-dim`, `--on-shell-faint`                      | the claim, `.brand` and the slide number; the subtitle of the title slide; the progress blocks not reached yet           | text and marks on the shell                   |
| `--surface`                                                             | `.sheet`, the badges and the ends of the route, the notes page of the PDF                                                | the sheet, where the evidence lies            |
| `--primary` (navy), `--on-primary`                                      | headings and list marks on the sheet, `.card-num`, the API box, the vote buttons                                         | the product, our system                       |
| `--accent` (yellow), `--on-accent`                                      | `.plate`, the progress blocks reached, the mark of `.brand`, the conflict of a fact, the selection                       | the rule of the slide and what we look at now |
| `--state-barrier`, `--state-clear`, `--state-partial`, `--state-nodata` | `.rs-seg.is-<state>`                                                                                                     | the four route segment states, only those     |
| `--text`, `--text-dim`                                                  | the sheet                                                                                                                | main text, secondary text                     |
| `--line`, `--line-strong`                                               | hairlines between the parts of a sheet and the handle of the sheet; the borders of chips and the dashed frame of `.note` | lines and borders on the sheet                |
| `--shadow`                                                              | under the sheet and under the plates                                                                                     | the lift of a layer above the shell           |

- `--bg` and `--primary` hold the same navy in two roles: the first is the ground of a slide, the second the color of the product on the sheet. `src/main.js` gives `--bg` to reveal.js as the background of every slide, which reaches the print view; `theme.css` lays the light over it.
- Yellow is a background with dark text on it (`--on-accent`), never a text color, on the shell or on the sheet.
- The four segment state colors mean nothing but the segment states, and always come with a label or a pattern, never color alone. The tokens and their values are those of the HarmonyOS app (`mobile_app/accessway/entry/src/main/ets/components/Theme.ets`), where the same colors draw the segments of a route. The route of the deck also takes the line patterns of the app: red with white stripes, solid green, amber with dark dashes and grey dots, so the states stay apart in grayscale.
- The deck has no muted text token: every text on the sheet is `--text` or `--text-dim`, and every text on the shell `--on-shell` or `--on-shell-dim`. The muted text color of the app, `#6F7480`, appears in the deck only as `--state-nodata`.

### Typography and layout

- A slide is 1600 x 900 px. `src/main.js` wraps the `html` of a module in a `.slide-frame` of that size, without padding. The parts of a slide are placed relative to that frame, 80 px from its sides (`--pad-x`). No padding is set on `<section>`, because the reveal.js print view resets it.
- A slide has up to four parts, each a class of `components.css`. The claim (`.slide-title`) is the heading of the slide, on the shell, at most two lines. The sheet (`.sheet`) is the white panel that rises from the bottom edge and holds the evidence. The plate (`.plate`) is the rule of the slide, in yellow, on the seam between the shell and the sheet. The note (`.note`) is a caveat in a dashed frame on the sheet. Every slide has a sheet; a plate and a note only where the content has a rule or a caveat.
- A slide sets the height of its sheet (`--sheet-h`), the top padding of the sheet (`--sheet-pad`) and the size of its claim (`--claim-size`) on its own id in `src/slides/<id>.css`. The claim is 100 px; a slide changes that only when its claim would not fit above its sheet, or is one short word. A claim that is one line in one language and two in the other takes its size per language through `:lang()`, as on `facts` and `data`.
- The sheet runs past the frame on the left, the right and the bottom, so in the browser it reaches the edges of the screen through the margin reveal.js keeps around a slide. `--sheet-x` is how far its left edge lies outside the frame, for the parts of a slide placed by frame coordinates. In the print view the sheet runs past the bottom only by `--bleed`: reveal.js measures the height of a slide there, and a slide taller than the page takes two pages of the PDF.
- The progress and the slide number are drawn inside the frame, so they are on every page of the PDF: ten blocks along the top edge, and the number with the total in the top right corner. The progress bar and the slide number of reveal.js are hidden. The position of a slide is the `--done` value set per slide id in `theme.css`, and the total stands in the `counter-reset` of `.slide-frame` and in the width of a block; a change of the order or of the number of slides in `src/slides/index.js` changes both. They are written down and not counted, because reveal.js takes the slides that are not on screen out of the page, and a CSS counter skips them.
- The name of the product with its yellow mark (`.brand`) stands in the top left corner of every slide but the title.
- Barlow Semi Condensed (400, 600, 700) for text and for the name on the title slide, Barlow Condensed 700 for the claims and the slide number. Both come from Fontsource, in the latin and latin-ext subsets, which carry the Polish letters but no arrows, check marks or mathematical symbols; those are drawn by `icons.js`. A glyph a slide has to show from the list of forbidden characters stands in the code as an HTML entity.
- Text on a slide is at least 27 px. The letters A and B in the ends of the small route are part of the drawing and are smaller.

## Architectural decisions

- The engine is a pre-existing component, and the Huawei submission names it as such. It was ported on 2026-10-04 from LLM-prezentacja, an earlier presentation project of Rafał. The port kept the mechanics - reveal.js, the step timelines, the offline build, the presenter notes with timing, the rehearsal mode, the snapshot and PDF scripts and the arrow icon - translated the code into English, and replaced the theme, the fonts and every slide.
- The deck runs in the browser instead of being a PowerPoint file, because animations built step by step are its core, and reveal.js gives remote navigation, the presenter view and a print view for the PDF.
- Steps are bound to clicks. Each animated slide has one GSAP timeline split by labels into steps, and every step is an invisible reveal.js fragment, so the remote and the keyboard work without extra handling. The state of a slide always follows from the number of visible fragments: a step forward is animated, while a step back and every jump set the state at once, so going back, returning from the next slide and reloading the page always give the right picture.
- Each deck is one file that works offline, because the room may have no internet. Vite with `vite-plugin-singlefile` puts the scripts, styles and fonts into one HTML file that works opened from disk. The fonts are installed from Fontsource, never fetched from a font service, and `trimFonts` keeps only the latin and latin-ext subsets in woff2, so the file stays near 0.5 MB. The subsets are filtered out of the full Fontsource files, because only those carry a `unicode-range` per subset.
- Both languages come from one codebase. The Vite mode is the language and the slides take their words from a content module per language, so a change of structure or animation is made once for both decks. A build with any other mode fails instead of falling back to a default language. The content check keeps the two files in step, and the time plan is shared, because the slides are the same.
- The deck takes its look from the fact panel of the EnableMe app, at room scale. The navy shell of the app is the ground of every slide, the evidence lies on a white sheet like the bottom sheet of the app, a rule stands on the yellow of the app, a caveat takes the dashed frame the app gives to a note about missing data, and the route is drawn in the line patterns of the app. The color tokens and the typefaces are those of the app, so the slides and the screenshots of the app look like one product. This look replaced the earlier light page on 2026-10-04; the direction and its contract are recorded in `.impeccable/surfaces/presentation-index-html.md`.
- The submitted PDF comes from the print view, which shows every slide in its final state with vector text. A slide with intermediate states can only be presented from a PDF viewer through the steps PDF made of screenshots, so both are produced.
- The notes end with the `summary` of the next slide, which is kept in the module of the slide it describes, so a change of order in `src/slides/index.js` corrects every announcement by itself. The labels of the notes - `Time`, `ends at`, `Next:` and the `Speaker notes` heading of reveal.js - are English in both decks.
- The code unit has its own `.prettierrc` with single quotes in JavaScript, the style the engine was written in. The double quotes of `docs/standards/standard_frontend.md` apply to the web frontend in `frontend/`, not to this unit.
- Several parts of the source engine were dropped. The stage map in the corner went with its list of stages, because a deck of at most 10 slides needs no map of its parts. The slide variants switched by a digit went, because the pitch has no decision taken live. KaTeX and `math.js` went, because the deck has no formulas and KaTeX would add its own fonts to the file. The 3D vector space, the token chips and the components that drew the content of the earlier talk went with that content. The IBM Plex fonts went with their monospace face, and with it the `.mono` class and the code card, because the brand has no monospace face and a system one would look different on every computer. `svg-text.js` and `visibility.js` went, because no kept module used them, and so did the flow diagrams, the tags, the drawing area, the `.accent` class and the icons other than the arrow, once the slides were written without them.

## Summary

`npm run snapshots` prints the time plan of each language and the number of screenshots saved; `npm run pdf` prints the path of each PDF and the page count of the steps PDF. Both end with exit code 1 and a list of the problems found, each prefixed with its language. `scripts/style-check.mjs` lists each violation by file and line, `scripts/content-check.mjs` by its path in the content object; both end with exit code 1 when they find anything and 0 otherwise.

## Relation to MODULE_ALGORITHM.md

There is no `MODULE_ALGORITHM.md`: the code unit has no domain behavior, and what the product does is described in `docs/product/specification.md`.
