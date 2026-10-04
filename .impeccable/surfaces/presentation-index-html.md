---
version: 1
slug: "presentation-index-html"
primary_target: "presentation/index.html"
related_targets: []
---

# Design brief: pitch deck

Document state: 2026-10-04, direction approved by Adrian on two mock slides; the deck is rebuilt in this direction

Product truth is in `PRODUCT.md` and `docs/product/specification.md`, and this brief does not repeat it. How the deck is built, its slide module contract and its gates are in `presentation/MODULE.md` and `presentation/README.md`. The approved look is in `.impeccable/briefs/deck/`: `approved-title-pl.jpg`, `approved-states-pl.jpg`, their English counterparts and `mock.html`, the source of the four images.

## Job and audience

- Who arrives: the jury of two HackYeah 2026 challenges. For Kraków bez barier the deck is read as a Polish PDF of at most 10 pages and seen once in a hall on a projector; for Imagine What's Next it is the English deck.
- Situation: a short pitch, a room that may be lit, a remote in the hand of the speaker, people sitting far from the screen. The PDF is read later on a laptop, without the speaker.
- Need: understand in a few minutes what EnableMe does that a map with one label does not, and believe that it works.
- Visitor mode: Persuade.

## Outcome and proof

- After the talk a juror can repeat one sentence: missing information is never shown as accessible.
- The proof the deck carries: the four segment states in the line patterns of the app, a fact with its source, date and status, the contradiction between the map data and a report, and the honest list of what works and what is next.
- Every page of the PDF stands on its own in its final state.

## Selected direction

The fact panel at room scale. Every slide is built the way the app builds the detail of a fact, enlarged to the whole screen. The surface seed of this choice is `2debe8f4`; the two other structures of the deal, a slide as a wayfinding sign and a slide split into what is known and what is not, were declined by Adrian.

- The claim stands on the navy shell: the heading of the slide in Barlow Condensed 700 at about 100 px, white, in at most two balanced lines, top left.
- The evidence lies on a white sheet anchored to the bottom edge, with large rounded top corners and the handle of the bottom sheet of the app. Its height follows the content of the slide. Everything dense is set on the sheet, in ink on white.
- The rule sits on a yellow plate on the seam between the shell and the sheet, left aligned, in one line where the sentence allows it. It replaces the statement box with a stripe on its left side.
- A caveat is a note with a dashed border on the sheet, the note the app uses for missing data. It replaces the small grey footnote at the bottom of a slide.
- The route is drawn in the line patterns of the app: red with white stripes for a barrier, solid green for no barriers, amber with dark dashes for partial data, grey dots for no data, with a badge over each segment and the ends marked A and B. The deck drew a barrier as a solid red line until now.
- Progress is ten blocks along the top edge, the blocks up to the current slide in yellow, with the slide number at the top right. A small EnableMe mark with a yellow square stands at the top left of every slide but the title.
- Color strategy: committed. Navy owns the ground of every slide, white owns the sheet, yellow owns the plates and the progress. The four state colors mean only the states.
- Type scale for 1600 by 900: claim about 100 px, the name on the title slide about 310 px, plate 40 px, text on the sheet 29 to 34 px, nothing under 27 px.
- What it refuses: the heading over a row of equal cards on a light page, which is what the deck was.

Raised by the hands it beat: hierarchy by scale contrast alone, from a type specimen; progress in whole blocks, from an install wizard; the courage of type that fills the frame, from a wood type manifesto page.

## Scope and boundaries

- Target: the ten slides of `presentation/`, in both languages, from one codebase.
- Changes: `src/styles/theme.css`, `src/styles/components.css`, the styles next to each slide, the markup and the animation segments inside the slide modules, and `src/components/route-states.js` for the line patterns and the end marks.
- Untouched: every word in `src/content/pl.js` and `src/content/en.js`, the speaker notes, the order and the number of slides, the number of steps of each slide, `src/slides/timing.js`, the scripts, `vite.config.js` and the public interface of the code unit.
- Fidelity: production. The result is the deck the team presents and the PDF it submits.
- Anti-goals: no new claim, no new slide, no decorative imagery, no dark page with glowing accents, no second accent color.

## States and ranges

Each slide maps onto the same four parts. A slide without a rule has no plate, and a slide without a caveat has no note.

| Slide        | Claim on the shell | Evidence on the sheet                                                         | Plate on the seam | Dashed note |
| ------------ | ------------------ | ----------------------------------------------------------------------------- | ----------------- | ----------- |
| title        | the name, at scale | the route in the four states, from A to B                                     | the kicker, above | none        |
| problem      | heading            | who it concerns and the five barriers as chips                                | `gap`             | none        |
| solution     | heading            | the three steps as numbered rows across the sheet                             | `footer`          | none        |
| states       | heading            | the route with a legend label under each segment, then the route in grayscale | `rule`            | `channels`  |
| facts        | heading            | the fact card with its conflict, the four statuses as chips, the four rules   | none              | none        |
| demo         | heading            | the four steps of the live demo as numbered rows                              | none              | `footnote`  |
| data         | heading            | the table of sources with its four columns                                    | `footer`          | none        |
| architecture | heading            | the three boxes joined by arrows, then how it grows and privacy as two lists  | none              | none        |
| business     | heading            | free, paying and operation as three columns                                   | `footer`          | none        |
| status       | heading            | what works and what is next as two lists                                      | `closing`         | `limits`    |

Ranges to hold: a heading from 4 to 49 characters in English and from 4 to 48 in Polish; a plate sentence up to about 70 characters, which wraps to two lines when it does not fit; lists of 3 to 5 items; the table of 4 rows by 4 columns; legend labels that wrap to two lines.

## Interaction and layout

- Entering a slide: the claim settles and the sheet rises from below, the way the bottom sheet of the app opens. One motion grammar for all ten slides.
- A click reveals the next row, column or part of the evidence on the sheet, in the order the slide has now. The plate lands on the seam on its own step where the slide gives the rule a step.
- Moving to the next slide advances the progress by one block.
- The print view shows every slide in its final state, plate and note included.
- Layout is fixed to the 1600 by 900 frame of the deck. Content is anchored to the left edge of the frame and to the sheet, not centered.

## Constraints and open decisions

- The rules of `presentation/MODULE.md` hold: slides use only the tokens of `theme.css`, never a raw color value; a state color always comes with a label or a pattern; yellow is a ground for dark text and never a text color on a light ground; fonts come only from Fontsource; no line comments; every word comes from the content files.
- New tokens are needed for the shell ground, the text on the shell and the soft text on the shell. The meaning table of the Colors section of `MODULE.md` is updated in the same change.
- The gates of the deck pass after the change: `npm run lint`, `npm run build`, `npm run snapshots`, which also checks that the deck has at most 10 slides and makes no network request, and `npm run pdf`.
- Contrast: white on navy and ink on yellow and on white all pass WCAG 2.2 AA; the soft text on the shell is checked against 4.5 to 1.
- The deck was light on purpose, so that slides and app screenshots look like one product (`presentation/MODULE.md`, design decisions). The new look keeps that link through the shell, the sheet and the plates of the app instead of through a light page. Rafał wrote that decision and has to agree before the change is merged.
- Open for the builder to settle with Adrian: whether the slides that show the app (demo, facts) get real screenshots of the app on the sheet. The content files have no image today, so this brief assumes none.

## Direction contract

- THESIS: Every slide is one fact of the app at room scale: a claim on the navy shell, its evidence on a white sheet, its rule on a yellow plate on the seam. It refuses the heading over a row of equal cards on a light page.
- OWN-WORLD: Navy ground on every slide with a soft light at the top right, a white sheet with large rounded top corners and a handle rising from the bottom edge, yellow plates with ink text, dashed notes, route lines in four patterns with round badges and ends marked A and B, ten progress blocks along the top. Barlow Condensed for claims, Barlow Semi Condensed for everything else.
- STORY: The juror understands that the product shows what it knows and what it does not, believes it because the deck shows the patterns, a fact and its contradiction, and remembers that missing information is never shown as accessible.
- FIRST VIEWPORT: The title slide. The challenge on a yellow plate at the top left, the name at about 310 px across three quarters of the frame, the promise under it, and a short sheet along the bottom with the route from A to B in the four states.
- FORM: The fact panel, index 4 of the ordered list of seven structures, seed key 2debe8f4, code-led.
- FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
