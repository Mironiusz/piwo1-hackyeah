import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './status.css';

const t = slideText('status');

const column = (part, cls) => `<div class="status-col ${cls}"><h3>${part.head}</h3><ul class="plain-list">${part.items.map((i) => `<li>${i}</li>`).join('')}</ul></div>`;

/** What works today and what is next, with the known limits of the prototype, closing with the one line to remember. */
export default {
  id: 'status',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <div class="status-row">
      ${column(t.works, 'is-works')}
      ${column(t.next, 'is-next')}
    </div>
    <p class="footnote status-limits">${t.limits}</p>
    <p class="closing">${t.closing}</p>`,
  notes: t.notes,

  animate(root) {
    const next = root.querySelectorAll('.status-col.is-next, .status-limits');
    const closing = root.querySelector('.closing');
    gsap.set(next, { opacity: 0, y: 16 });
    gsap.set(closing, { opacity: 0, y: 16 });
    return [
      (tl) => {
        tl.from(root.querySelector('.status-col.is-works'), { opacity: 0, y: 16, duration: 0.45 });
      },
      (tl) => {
        tl.to(next, { opacity: 1, y: 0, duration: 0.45, stagger: 0.15 });
      },
      (tl) => {
        tl.to(closing, { opacity: 1, y: 0, duration: 0.5 });
      },
    ];
  },
};
