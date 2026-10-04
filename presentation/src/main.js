/**
 * Entry point: turns the slides from `src/slides/index.js` into reveal.js sections, attaches the GSAP timelines
 * to the steps and starts the deck.
 *
 * The fonts are the full Fontsource files, because only they carry a `unicode-range` for every subset.
 * The build drops the subsets other than latin and latin-ext (`trimFonts` in `vite.config.js`).
 */

import Reveal from 'reveal.js';
import Notes from 'reveal.js/plugin/notes';
import 'reveal.js/reset.css';
import 'reveal.js/reveal.css';

import '@fontsource/barlow-semi-condensed/400.css';
import '@fontsource/barlow-semi-condensed/600.css';
import '@fontsource/barlow-semi-condensed/700.css';
import '@fontsource/barlow-condensed/700.css';

import './styles/theme.css';
import './styles/components.css';

import { token } from './lib/theme.js';
import { isRehearsal, startRehearsal } from './lib/rehearsal.js';
import { addStepMarkers, bindTimelines, buildTimeline } from './lib/steps.js';
import { slides } from './slides/index.js';
import { clock, TIMING } from './slides/timing.js';

const CLICK = '[click]';

/**
 * Speaker notes: at the top the time of the slide and the planned time at which it ends, and the [click] markers
 * in bold, so they stand out at a glance. At the bottom the summary of the next slide, taken from its `summary`
 * field, so the speaker knows where the transition leads.
 */
function renderNotes(slide, endsAt, next) {
  const seconds = TIMING[slide.id];
  const timing = seconds ? `<p><small>Time: ${clock(seconds)} - ends at: ${clock(endsAt)}</small></p>` : '';
  const upcoming = next ? `<p><em>Next: ${next.summary}</em></p>` : '';
  return timing + (slide.notes ?? '').replaceAll(CLICK, `<strong>${CLICK}</strong>`) + upcoming;
}

/**
 * Builds the `<section>` of one slide.
 *
 * The background goes through reveal.js (`data-background-color`), not only through CSS, because only then does it
 * reach the print view (PDF). The content lies in a `.slide-frame` of fixed size: the frame carries the padding
 * and is the reference for absolutely positioned elements, because the print view resets the padding and the
 * height of `<section>`. `data-timing` feeds the pace clock of the presenter view.
 */
function renderSection(slide, endsAt, next) {
  const section = document.createElement('section');
  section.id = slide.id;
  section.dataset.backgroundColor = token('--bg');
  section.innerHTML = `<div class="slide-frame">${slide.html}</div>`;
  if (TIMING[slide.id]) section.dataset.timing = TIMING[slide.id];
  section.insertAdjacentHTML('beforeend', `<aside class="notes">${renderNotes(slide, endsAt, next)}</aside>`);
  return section;
}

/**
 * Assembles the slides, starts reveal.js and exposes `window.__deck` for the Playwright scripts
 * (`scripts/snapshots.mjs`, `scripts/pdf.mjs`).
 */
async function main() {
  const container = document.querySelector('.reveal .slides');
  const timelines = new Map();
  let elapsed = 0;
  const sections = slides.map((slide, i) => renderSection(slide, (elapsed += TIMING[slide.id] ?? 0), slides[i + 1]));

  for (const [i, slide] of slides.entries()) {
    const section = sections[i];
    container.append(section);
    if (slide.animate) {
      const entry = buildTimeline(slide.animate(section));
      addStepMarkers(section, entry.stepCount);
      timelines.set(section, entry);
    }
  }

  const deck = new Reveal(document.querySelector('.reveal'), {
    width: 1600,
    height: 900,
    margin: 0.04,
    center: false,
    hash: true,
    controls: false,
    progress: true,
    slideNumber: 'c/t',
    transition: 'fade',
    transitionSpeed: 'fast',
    backgroundTransition: 'none',
    pdfSeparateFragments: false,
    totalTime: elapsed,
    plugins: [Notes],
  });

  const steps = bindTimelines(deck, timelines);
  await deck.initialize();
  if (isRehearsal() && !deck.isPrintView()) startRehearsal(deck, slides);

  window.__deck = {
    reveal: deck,
    settle: steps.settle,
    slides: slides.map((s, i) => ({
      id: s.id,
      steps: timelines.get(sections[i])?.stepCount ?? 0,
      timing: TIMING[s.id] ?? 0,
      summary: s.summary ?? '',
      clicks: (s.notes ?? '').split(CLICK).length - 1,
    })),
    totalTime: elapsed,
  };
}

main();
