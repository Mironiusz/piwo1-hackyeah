import { contentFor } from '../content/index.js';

/**
 * The language of this build, taken from the Vite mode (`vite --mode pl`, `vite build --mode en`).
 * One codebase gives two decks: slide modules hold structure and animation, and take their words from here.
 */
export const LANG = import.meta.env.MODE;

/** The content of the active language. Importing this module with any other mode throws at once. */
export const content = contentFor(LANG);

/** The words of one slide. A slide without an entry in the content file is an error that names the file to fix. */
export function slideText(id) {
  const text = content.slides[id];
  if (!text) throw new Error(`Slide "${id}" has no entry in src/content/${LANG}.js.`);
  return text;
}
