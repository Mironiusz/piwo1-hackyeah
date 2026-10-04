import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './status.css';

const t = slideText('status');
const brand = slideText('title').heading;

const column = (part, cls, list) => `<div class="status-col ${cls}"><h3>${part.head}</h3><ul class="plain-list ${list}">${part.items.map((i) => `<li>${i}</li>`).join('')}</ul></div>`;

/** What works today and what is next, with the known limits of the prototype, closing with the one line to remember. */
export default {
  id: 'status',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <div class="status-row">
        ${column(t.works, 'is-works', '')}
        ${column(t.next, 'is-next', 'is-open')}
      </div>
      <p class="note status-limits">${t.limits}</p>
    </div>
    <p class="plate closing">${t.closing}</p>`,
  notes: t.notes,

  animate(root) {
    const next = root.querySelectorAll('.status-col.is-next, .status-limits');
    const closing = root.querySelector('.closing');
    gsap.set(next, { opacity: 0, y: 16 });
    gsap.set(closing, { opacity: 0, y: -18 });
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelector('.status-col.is-works'), { opacity: 0, y: 16, duration: 0.45, ease: 'power2.out' }, '-=0.25');
      },
      (tl) => {
        tl.to(next, { opacity: 1, y: 0, duration: 0.45, stagger: 0.15, ease: 'power2.out' });
      },
      (tl) => {
        tl.to(closing, { opacity: 1, y: 0, duration: 0.55, ease: 'back.out(1.6)' });
      },
    ];
  },
};
