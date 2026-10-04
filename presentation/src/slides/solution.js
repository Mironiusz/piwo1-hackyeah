import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './solution.css';

const t = slideText('solution');
const brand = slideText('title').heading;

/** The answer in three steps, needs, route and facts, one row per click, then the line that the judgement stays with the person. */
export default {
  id: 'solution',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <ol class="step-rows">
        ${t.steps.map((s, i) => `<li class="step-row"><span class="card-num">${i + 1}</span><h3>${s.head}</h3><p>${s.text}</p></li>`).join('')}
      </ol>
    </div>
    <p class="plate solution-footer">${t.footer}</p>`,
  notes: t.notes,

  animate(root) {
    const rows = root.querySelectorAll('.step-row');
    const footer = root.querySelector('.solution-footer');
    gsap.set(rows, { opacity: 0, y: 24 });
    gsap.set(footer, { opacity: 0, y: -18 });
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
      },
      (tl) => {
        tl.to(rows[0], { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' });
      },
      (tl) => {
        tl.to(rows[1], { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' });
      },
      (tl) => {
        tl.to(rows[2], { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' });
        tl.to(footer, { opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' }, '+=0.15');
      },
    ];
  },
};
