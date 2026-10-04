/**
 * PDFs from the offline build (dist/<lang>/index.html). Usage: npm run build && npm run pdf [-- pl|en]
 * Without a language both decks are printed. File names take `name` from package.json and the language.
 * Output in dist/<lang>/:
 * - NAME-<lang>.pdf: one page per slide in its final state, from the reveal.js print view. Vector text and
 *   clickable links. This is the file submitted to HackTribe (Kraków: PDF, at most 10 slides).
 * - NAME-<lang>-steps.pdf: one page per click, made of screenshots. For running the talk from a PDF viewer when
 *   the HTML file fails: the remote turns pages like steps.
 * - NAME-<lang>-notes.pdf: like the first one, with a page of notes and timing after every slide.
 */

import { resolve } from 'node:path';
import { chromium } from 'playwright';

import { deckName, goToStep, langDir, openDeck, parseLanguages, reportErrors } from './deck.mjs';

const { languages, rest } = parseLanguages(process.argv.slice(2));
if (rest.length) {
  console.error(`Unknown arguments: ${rest.join(' ')}. Usage: npm run pdf [-- pl|en]`);
  process.exit(1);
}

const browser = await chromium.launch();
const errors = [];

/** A PDF from the reveal.js print view (`query` picks the variant, for example with notes). */
async function printView(lang, query, file) {
  const page = await openDeck(browser, errors, lang, query);
  await page.waitForFunction(() => document.querySelectorAll('.pdf-page').length === window.__deck.slides.length);
  const path = resolve(langDir(lang), file);
  await page.pdf({ path, preferCSSPageSize: true, printBackground: true });
  await page.close();
  console.log(`Saved ${path}`);
}

/** A PDF made of screenshots: one page per step of every slide. */
async function stepsPdf(lang, file) {
  const page = await openDeck(browser, errors, lang);
  const slides = await page.evaluate(() => window.__deck.slides);
  const shots = [];
  for (const [h, slide] of slides.entries()) {
    for (let step = 0; step <= slide.steps; step++) {
      await goToStep(page, h, step);
      shots.push((await page.screenshot({ type: 'jpeg', quality: 90 })).toString('base64'));
    }
  }
  await page.close();

  const sheet = await browser.newPage();
  await sheet.setContent(`<!doctype html>
    <style>
      @page { size: 1600px 900px; margin: 0; }
      body { margin: 0; }
      img { display: block; width: 1600px; height: 900px; break-after: page; }
      img:last-child { break-after: auto; }
    </style>
    ${shots.map((s) => `<img src="data:image/jpeg;base64,${s}">`).join('')}`);
  await sheet.evaluate(() => Promise.all([...document.images].map((img) => img.decode())));
  const path = resolve(langDir(lang), file);
  await sheet.pdf({ path, preferCSSPageSize: true, printBackground: true });
  await sheet.close();
  console.log(`Saved ${path} (${shots.length} pages)`);
}

for (const lang of languages) {
  await printView(lang, '?print-pdf', `${deckName}-${lang}.pdf`);
  await stepsPdf(lang, `${deckName}-${lang}-steps.pdf`);
  await printView(lang, '?print-pdf&showNotes=separate-page', `${deckName}-${lang}-notes.pdf`);
}

await browser.close();
reportErrors(errors);
