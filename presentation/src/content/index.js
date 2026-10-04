import en from './en.js';
import pl from './pl.js';

/** The words of the deck per language. The build mode picks one of them (`vite build --mode pl`). */
export const CONTENT = { pl, en };

export const LANGUAGES = Object.keys(CONTENT);

/**
 * Returns the content of one language. An unknown language is an error, not a silent default, because a deck
 * built in the wrong language would look correct until someone reads it.
 */
export function contentFor(lang) {
  if (!LANGUAGES.includes(lang)) throw new Error(`Unknown deck language "${lang}": use --mode ${LANGUAGES.join(' or --mode ')}.`);
  return CONTENT[lang];
}
