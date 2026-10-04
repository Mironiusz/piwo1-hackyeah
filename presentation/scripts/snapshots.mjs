/**
 * Screenshots of every slide at every animation step, from the offline build (dist/<lang>/index.html).
 * Usage: npm run build && npm run snapshots [-- [pl|en] [slide-id ...]]
 * Without a language both decks are shot; slide ids limit the screenshots, not the checks.
 *
 * Output: snapshots/<lang>/NN-id-stepK.png. Ends with an error when the page reports an error in the console,
 * reaches the network (the file has to work offline) or the deck breaks its contract: more slides than the
 * Kraków submission allows, a number of [click] markers in the notes different from the number of steps,
 * a slide without a time in src/slides/timing.js or without a summary, or a content entry without a slide.
 */

import { mkdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';
import { chromium } from 'playwright';

import { CONTENT } from '../src/content/index.js';
import { clock } from '../src/slides/timing.js';
import { goToStep, openDeck, parseLanguages, reportErrors, root } from './deck.mjs';

/** The Kraków challenge accepts a PDF of at most 10 slides (docs/hackathon/challenge_requirements.md). */
const MAX_SLIDES = 10;

const { languages, rest } = parseLanguages(process.argv.slice(2));
const only = new Set(rest);
const outDir = resolve(root, 'snapshots');

const browser = await chromium.launch();
const errors = [];
let count = 0;

/** Checks the contract of the deck of one language. */
function checkDeck(lang, slides) {
  const fail = (message) => errors.push(`[${lang}] ${message}`);
  if (slides.length > MAX_SLIDES) fail(`${slides.length} slides, the Kraków submission allows at most ${MAX_SLIDES}`);
  for (const slide of slides) {
    if (slide.clicks !== slide.steps) fail(`${slide.id}: ${slide.clicks} x [click] in the notes, but ${slide.steps} animation steps`);
    if (!slide.timing) fail(`${slide.id}: no time in src/slides/timing.js`);
    if (!slide.summary) fail(`${slide.id}: no summary field (the "Next:" line in the notes of the previous slide)`);
  }
  const ids = new Set(slides.map((s) => s.id));
  for (const id of Object.keys(CONTENT[lang].slides)) {
    if (!ids.has(id)) fail(`slides.${id} in src/content/${lang}.js has no slide in src/slides/index.js`);
  }
}

for (const lang of languages) {
  const dir = resolve(outDir, lang);
  await rm(dir, { recursive: true, force: true });
  await mkdir(dir, { recursive: true });
  const page = await openDeck(browser, errors, lang);
  const { slides, totalTime } = await page.evaluate(() => window.__deck);
  checkDeck(lang, slides);
  console.log(`[${lang}] Time plan: ${clock(totalTime)}`);

  for (const [h, slide] of slides.entries()) {
    if (only.size && !only.has(slide.id)) continue;
    for (let step = 0; step <= slide.steps; step++) {
      await goToStep(page, h, step);
      await page.screenshot({ path: resolve(dir, `${String(h + 1).padStart(2, '0')}-${slide.id}-step${step}.png`) });
      count++;
    }
  }
  await page.close();
}

await browser.close();
console.log(`Saved ${count} screenshots in ${outDir}`);
reportErrors(errors);
