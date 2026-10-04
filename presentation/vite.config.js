import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

import { contentFor } from './src/content/index.js';

/**
 * The build gives one self-contained file per language, dist/<lang>/index.html (JS, CSS and fonts inside),
 * which works opened from disk, without a server and without internet. The Vite mode is the language:
 * `vite build --mode pl`, `vite build --mode en`. Any other mode stops the build with an error.
 */

/** Fontsource subsets the deck keeps: Polish and English need only latin and latin-ext. */
const SUBSETS_KEPT = /-(latin|latin-ext)-\d{3}-/;

/**
 * In one file every font lands inside as base64, so it weighs there what it really weighs.
 * Fontsource gives every face in two formats at once (woff2, woff) and adds subsets beyond latin and latin-ext.
 * The plugin removes both in the CSS source, before Vite notices those files, because a file without a reference
 * does not get into the build.
 *
 * First the whole `@font-face` rules of the other subsets disappear. The remaining ones keep their `unicode-range`
 * untouched, because it decides which file serves which characters. Then only woff2 stays in the `src` of each rule,
 * which every browser has read since 2017.
 */
function trimFonts() {
  return {
    name: 'trim-fonts',
    enforce: 'pre',
    transform(code, id) {
      if (!id.split('?')[0].endsWith('.css') || !code.includes('@font-face')) return null;

      let out = code.replace(/@font-face\s*{[^}]*}/g, (rule) => (SUBSETS_KEPT.test(rule) ? rule : ''));
      out = out.replace(/src:\s*([^;}]+)/g, (whole, sources) => {
        if (!sources.includes('woff2')) return whole;
        const kept = sources
          .split(/,(?![^(]*\))/)
          .map((part) => part.trim())
          .filter((part) => part.includes('woff2'));
        return `src: ${kept.join(', ')}`;
      });

      return out === code ? null : { code: out, map: null };
    },
  };
}

/**
 * `vite preview` serves the whole dist/, so both decks are at /pl/ and /en/ and no language is needed.
 * Every other command builds or serves one language: index.html gets its `lang` from `%MODE%` and its title from
 * `%DECK_TITLE%`, the `page.title` of the content file of that language.
 */
export default defineConfig(({ mode, isPreview }) => {
  if (isPreview) return { build: { outDir: 'dist' } };

  const content = contentFor(mode);
  return {
    base: './',
    define: { 'import.meta.env.DECK_TITLE': JSON.stringify(content.page.title) },
    plugins: [trimFonts(), viteSingleFile()],
    build: { target: 'es2022', outDir: `dist/${mode}` },
  };
});
