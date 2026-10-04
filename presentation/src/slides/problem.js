import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';

const t = slideText('problem');

/** The problem: the barriers people meet only on the spot, and the single label maps give instead of facts. */
export default {
  id: 'problem',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <p class="lead">${t.who}</p>
    <ul class="chip-row">${t.barriers.map((b) => `<li class="chip">${b}</li>`).join('')}</ul>
    <p class="statement problem-gap">${t.gap}</p>`,
  notes: t.notes,

  animate(root) {
    const gap = root.querySelector('.problem-gap');
    gsap.set(gap, { opacity: 0, y: 20 });
    return [
      (tl) => {
        tl.from(root.querySelectorAll('.lead, .chip'), { opacity: 0, y: 16, duration: 0.45, stagger: 0.1 });
      },
      (tl) => {
        tl.to(gap, { opacity: 1, y: 0, duration: 0.5 });
      },
    ];
  },
};
