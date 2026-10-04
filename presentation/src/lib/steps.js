import { gsap } from 'gsap';

/**
 * Slide animations driven by reveal.js steps.
 *
 * A slide module returns from `animate(section)` a list of segments `[intro, step1, step2, ...]`.
 * Each segment appends its tweens to the end of one shared GSAP timeline and gets the label
 * `s{i}`. The intro (`s0`) plays by itself when the slide is entered, and every next step is one
 * invisible reveal.js fragment, that is one click of the remote.
 *
 * The state of a slide always follows from the number of visible fragments: a step forward is
 * animated, while a step back and every jump (coming back from the next slide, reloading the
 * page, picking a slide in the overview) set the state at once.
 */

const MARKER = 'step-marker';

/** Builds one paused timeline from the segments of a slide, with a label after each segment. */
export function buildTimeline(segments) {
  const tl = gsap.timeline({ paused: true });
  segments.forEach((segment, i) => {
    segment?.(tl);
    tl.addLabel(`s${i}`);
  });
  return { tl, stepCount: segments.length - 1, step: null };
}

/** Adds one invisible fragment per step, so reveal.js counts the clicks of the slide. */
export function addStepMarkers(section, count) {
  for (let i = 0; i < count; i++) {
    const marker = document.createElement('span');
    marker.className = `fragment ${MARKER}`;
    marker.setAttribute('aria-hidden', 'true');
    section.append(marker);
  }
}

/** Connects the timelines to the reveal.js events: entering a slide, showing and hiding a fragment, the print view. */
export function bindTimelines(deck, timelines) {
  let playhead = null;

  const visibleSteps = (section) => section.querySelectorAll(`:scope > .${MARKER}.visible`).length;

  function stop() {
    playhead?.kill();
    playhead = null;
  }

  function jump(entry, step) {
    stop();
    entry.tl.pause().seek(`s${step}`);
    entry.step = step;
  }

  function play(entry, step, { restart = false } = {}) {
    stop();
    if (restart) entry.tl.pause().seek(0);
    playhead = entry.tl.tweenTo(`s${step}`);
    entry.step = step;
  }

  function enter(section) {
    const entry = timelines.get(section);
    if (!entry) return;
    const step = visibleSteps(section);
    if (step === 0) play(entry, 0, { restart: true });
    else jump(entry, step);
  }

  /**
   * Fragment events also arrive on a slide change, in no fixed order relative to `slidechanged`.
   * Comparing with the last applied step turns them into a no-op.
   */
  function onFragmentChange() {
    const section = deck.getCurrentSlide();
    const entry = timelines.get(section);
    if (!entry) return;
    const step = visibleSteps(section);
    if (step === entry.step) return;
    if (entry.step !== null && step === entry.step + 1) play(entry, step);
    else jump(entry, step);
  }

  deck.on('ready', (event) => {
    if (deck.isPrintView()) {
      for (const entry of timelines.values()) entry.tl.seek(entry.tl.duration());
      return;
    }
    enter(event.currentSlide);
  });
  deck.on('slidechanged', (event) => enter(event.currentSlide));
  deck.on('fragmentshown', onFragmentChange);
  deck.on('fragmenthidden', onFragmentChange);

  return {
    /** Brings the running animation to its end (used by the snapshot and PDF scripts). */
    settle() {
      playhead?.progress(1);
      stop();
    },
  };
}
