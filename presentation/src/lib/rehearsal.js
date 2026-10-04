import { LANG } from './lang.js';

/**
 * Timing of a rehearsal with the clock. Turns on only with the `?rehearsal` parameter in the address.
 *
 * It measures how long each slide was on screen (adding up returns to it) and keeps the result in localStorage,
 * so reloading the page does not erase it. The key carries the language, because both decks opened from disk
 * share one storage origin and the slide ids are the same in both. Without localStorage (for example blocked
 * in the browser) the measurement lasts until the page is reloaded. After the rehearsal, in the browser console:
 * - `__rehearsal()`: a table of times and ready entries for `src/slides/timing.js`;
 * - `__rehearsal.reset()`: a new measurement.
 */

const KEY = `enableme-deck-rehearsal-${LANG}`;

/** Whether the deck was opened with `?rehearsal`. */
export function isRehearsal() {
  return new URLSearchParams(window.location.search).has('rehearsal');
}

/** Starts measuring the time per slide and exposes `__rehearsal()` in the console. */
export function startRehearsal(deck, slides) {
  const load = () => {
    try {
      return JSON.parse(localStorage.getItem(KEY)) ?? {};
    } catch {
      return {};
    }
  };
  const times = load();
  let current = deck.getCurrentSlide()?.id;
  let since = performance.now();

  function flush() {
    const now = performance.now();
    if (current) times[current] = (times[current] ?? 0) + (now - since) / 1000;
    since = now;
    try {
      localStorage.setItem(KEY, JSON.stringify(times));
    } catch {}
  }

  deck.on('slidechanged', (event) => {
    flush();
    current = event.currentSlide.id;
  });
  window.addEventListener('pagehide', flush);

  window.__rehearsal = () => {
    flush();
    const rows = slides.map((s) => ({ id: s.id, seconds: Math.round(times[s.id] ?? 0) }));
    console.table(rows);
    const total = rows.reduce((sum, r) => sum + r.seconds, 0);
    const entries = rows.map((r) => `  '${r.id}': ${Math.max(15, Math.round(r.seconds / 15) * 15)},`).join('\n');
    return `Total ${Math.round(total / 60)} min. Entries for src/slides/timing.js:\n${entries}`;
  };
  window.__rehearsal.reset = () => {
    for (const id of Object.keys(times)) delete times[id];
    since = performance.now();
    flush();
  };

  console.info('Rehearsal: slide times are measured. After the rehearsal type __rehearsal() in the console.');
}
