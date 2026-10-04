/**
 * Time plan: seconds per slide, by slide id, shared by both languages. After a rehearsal with the clock
 * (`?rehearsal`) the numbers are corrected only here. The presenter view (S) uses them to show whether the talk
 * runs late, and the notes give the planned time at which each slide ends. `npm run snapshots` reports a slide
 * without a time as an error.
 *
 * The plan is 5 minutes: about 3 minutes of slides and the live demo on the slide `demo`. The real length of the
 * Kraków pitch is check 1.2 of `FINAL_CHECKLIST.md`.
 */
export const TIMING = {
  title: 15,
  problem: 25,
  solution: 25,
  states: 30,
  facts: 30,
  demo: 90,
  data: 20,
  architecture: 25,
  business: 30,
  status: 20,
};

/** Formats a number of seconds as "2:15". */
export function clock(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}
