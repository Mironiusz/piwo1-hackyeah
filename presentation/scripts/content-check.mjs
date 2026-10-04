/**
 * Checks that the content files of all languages (`src/content/*.js`) have exactly the same structure:
 * the same keys at every level, the same type of every value and the same length of every list.
 * A missing or extra translation fails loudly here instead of showing up as a hole in one of the decks.
 * Usage: npm run lint. Ends with an error listing every difference.
 */

import { CONTENT, LANGUAGES } from '../src/content/index.js';

const [first, ...others] = LANGUAGES;

const kind = (value) => (Array.isArray(value) ? 'list' : typeof value);

/** Differences between the value of the first language and the value of `lang`, found under `path`. */
function compare(reference, other, lang, path) {
  const [a, b] = [kind(reference), kind(other)];
  if (a !== b) return [`${path}: ${a} in ${first}, ${b} in ${lang}`];
  if (a === 'list') {
    if (reference.length !== other.length) return [`${path}: ${reference.length} items in ${first}, ${other.length} in ${lang}`];
    return reference.flatMap((item, i) => compare(item, other[i], lang, `${path}[${i}]`));
  }
  if (a !== 'object') return [];
  const keys = new Set([...Object.keys(reference), ...Object.keys(other)]);
  return [...keys].flatMap((key) => {
    const at = path ? `${path}.${key}` : key;
    if (!(key in other)) return [`${at}: missing in ${lang}`];
    if (!(key in reference)) return [`${at}: missing in ${first}`];
    return compare(reference[key], other[key], lang, at);
  });
}

const problems = others.flatMap((lang) => compare(CONTENT[first], CONTENT[lang], lang, ''));
if (problems.length) {
  console.error(problems.join('\n'));
  console.error(`\nContent check: ${problems.length} differences between ${LANGUAGES.join(' and ')}.`);
  process.exit(1);
}
console.log(`Content check: ${LANGUAGES.join(' and ')} have the same structure.`);
