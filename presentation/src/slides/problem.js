import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './problem.css';

const t = slideText('problem');
const brand = slideText('title').heading;

/** The sentences of the plate, each kept on one line, so a plate of two lines breaks between its sentences. */
const sentences = t.gap
  .split(/(?<=[.])[ ]+/)
  .map((sentence) => `<span class="plate-sentence">${sentence}</span>`)
  .join(' ');

/** The problem: the barriers people meet only on the spot, and the single label maps give instead of facts. */
export default {
  id: 'problem',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <p class="lead">${t.who}</p>
      <ul class="chip-row">${t.barriers.map((b) => `<li class="chip">${b}</li>`).join('')}</ul>
    </div>
    <p class="plate problem-gap">${sentences}</p>`,
  notes: t.notes,

  animate(root) {
    const gap = root.querySelector('.problem-gap');
    gsap.set(gap, { opacity: 0, y: -18 });
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelectorAll('.lead, .chip'), { opacity: 0, y: 16, duration: 0.4, stagger: 0.08, ease: 'power2.out' }, '-=0.3');
      },
      (tl) => {
        tl.to(gap, { opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' });
      },
    ];
  },
};
