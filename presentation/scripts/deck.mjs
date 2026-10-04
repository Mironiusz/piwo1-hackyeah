/**
 * Shared by the Playwright scripts: the languages to work on, opening the offline build (dist/<lang>/index.html)
 * and walking through the steps.
 */

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { LANGUAGES } from '../src/content/index.js';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

/** Name of the deck from the `name` field of package.json, used in the names of the PDF files. */
export const deckName = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8')).name;

const TRANSITION_MS = 600;

/**
 * Splits the command line arguments into the languages to work on and the rest. A language is named by its code
 * (`pl`, `en`); without any, the script works on both decks.
 */
export function parseLanguages(args) {
  const named = args.filter((arg) => LANGUAGES.includes(arg));
  return { languages: named.length ? named : LANGUAGES, rest: args.filter((arg) => !LANGUAGES.includes(arg)) };
}

/** The output directory of one language, where its index.html and PDFs lie. */
export const langDir = (lang) => resolve(root, 'dist', lang);

/**
 * Opens the deck of one language in a new tab. Page errors and every network request (the file has to work
 * offline) go to `errors`, prefixed with the language.
 */
export async function openDeck(browser, errors, lang, query = '') {
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  page.on('pageerror', (err) => errors.push(`[${lang}] ${err.message}`));
  page.on('console', (msg) => msg.type() === 'error' && errors.push(`[${lang}] ${msg.text()}`));
  await page.route(/^(?!file:|data:|blob:)/, (route) => {
    errors.push(`[${lang}] Network request: ${route.request().url()}`);
    route.abort();
  });

  await page.goto(pathToFileURL(resolve(langDir(lang), 'index.html')).href + query);
  await page.waitForFunction(() => window.__deck);
  await page.evaluate(() => document.fonts.ready);
  return page;
}

/** Sets slide `h` at step `step` (0 = after the intro) and waits until the animation and the transition end. */
export async function goToStep(page, h, step) {
  await page.evaluate(([hh, f]) => window.__deck.reveal.slide(hh, 0, f), [h, step - 1]);
  await page.waitForTimeout(TRANSITION_MS);
  await page.evaluate(() => window.__deck.settle());
  await page.waitForTimeout(100);
}

/** Prints the collected page errors and ends the script with code 1 if there was any. */
export function reportErrors(errors) {
  if (!errors.length) return;
  console.error('Errors:\n' + errors.join('\n'));
  process.exit(1);
}
