import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './solution.css';

const t = slideText('solution');

/** The answer in three steps, needs, route and facts, one card per click, then the line that the judgement stays with the person. */
export default {
  id: 'solution',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <ol class="card-row">
      ${t.steps.map((s, i) => `<li class="card"><span class="card-num">${i + 1}</span><h3>${s.head}</h3><p>${s.text}</p></li>`).join('')}
    </ol>
    <p class="statement solution-footer">${t.footer}</p>`,
  notes: t.notes,

  animate(root) {
    const cards = root.querySelectorAll('.card');
    const footer = root.querySelector('.solution-footer');
    gsap.set(cards, { opacity: 0, y: 24 });
    gsap.set(footer, { opacity: 0 });
    return [
      null,
      (tl) => {
        tl.to(cards[0], { opacity: 1, y: 0, duration: 0.45 });
      },
      (tl) => {
        tl.to(cards[1], { opacity: 1, y: 0, duration: 0.45 });
      },
      (tl) => {
        tl.to(cards[2], { opacity: 1, y: 0, duration: 0.45 });
        tl.to(footer, { opacity: 1, duration: 0.4 }, '+=0.15');
      },
    ];
  },
};
