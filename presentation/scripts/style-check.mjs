/**
 * Style check of the JavaScript, CSS and HTML files of this code unit, by `docs/standards/standard_formatting.md` of
 * the repository: forbidden characters (homoglyphs included), emojis, and line comments in JavaScript. Prettier does
 * not catch these. Markdown is not checked here: the repository gate `tests/architecture/test_prose_style.py` already
 * scans every markdown file of the repository. Usage: npm run lint (together with prettier --check). Ends with an error
 * listing files and lines when it finds anything.
 *
 * A glyph a slide has to show stands in the code as an HTML entity (`&mdash;`, `&rarr;`), so this check does not see it
 * and needs no exceptions. The list of characters is written as code points, so the script does not contain what it forbids.
 */

import { readdirSync, readFileSync } from 'node:fs';
import { dirname, extname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SKIP_DIRS = new Set(['node_modules', 'dist', 'snapshots']);
const CHECKED_EXT = new Set(['.js', '.mjs', '.css', '.html']);
const JS_EXT = new Set(['.js', '.mjs']);

/** Forbidden characters of `standard_formatting.md`, section Forbidden characters, with a name for the message. */
const FORBIDDEN = new Map(
  [
    [0x2014, 'em dash'],
    [0x2013, 'en dash'],
    [0x2212, 'minus sign'],
    [0x201c, 'left curly double quotation mark'],
    [0x201d, 'right curly double quotation mark'],
    [0x2018, 'left curly single quotation mark'],
    [0x2019, 'right curly single quotation mark'],
    [0x02bc, 'modifier letter apostrophe'],
    [0x2026, 'ellipsis'],
    [0x00b7, 'middle dot'],
    [0x2192, 'rightwards arrow'],
    [0x2190, 'leftwards arrow'],
    [0x2194, 'left right arrow'],
    [0x00d7, 'multiplication sign'],
    [0x0430, 'Cyrillic letter a'],
    [0x037e, 'Greek question mark'],
    [0x2215, 'division slash'],
  ].map(([code, name]) => [String.fromCodePoint(code), name]),
);
const EMOJI = /\p{Extended_Pictographic}/u;
const LINE_COMMENT = /^\s*\/\/|\s\/\/\s/;

/** All checked files of the code unit, outside the dependency and output directories. */
function checkedFiles(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = resolve(dir, entry.name);
    if (entry.isDirectory()) return SKIP_DIRS.has(entry.name) ? [] : checkedFiles(path);
    return CHECKED_EXT.has(extname(entry.name)) ? [path] : [];
  });
}

/** Violations in one file as a list of `{ line, rule }`. */
function checkFile(path) {
  const isJs = JS_EXT.has(extname(path));
  return readFileSync(path, 'utf8')
    .split('\n')
    .flatMap((text, i) => {
      const found = [...FORBIDDEN].filter(([ch]) => text.includes(ch)).map(([, name]) => `forbidden character: ${name}`);
      if (EMOJI.test(text)) found.push('emoji');
      if (isJs && LINE_COMMENT.test(text)) found.push('line comment');
      return found.map((rule) => ({ line: i + 1, rule }));
    });
}

const problems = checkedFiles(root).flatMap((path) => checkFile(path).map((p) => `${relative(root, path)}:${p.line}: ${p.rule}`));
if (problems.length) {
  console.error(problems.join('\n'));
  console.error(`\nStyle check: ${problems.length} violations.`);
  process.exit(1);
}
console.log('Style check: no violations.');
