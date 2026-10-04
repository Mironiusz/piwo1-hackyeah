import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './business.css';

const t = slideText('business');

const column = (part, cls) => `<div class="biz-col ${cls}"><h3>${part.head}</h3><ul class="plain-list">${part.items.map((i) => `<li>${i}</li>`).join('')}</ul></div>`;

/** Who uses the app for free, who pays, and who runs it outside the infrastructure of the city, one column per click. */
export default {
  id: 'business',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <div class="biz-row">
      ${column(t.free, 'is-free')}
      ${column(t.paid, 'is-paid')}
      ${column(t.run, 'is-run')}
    </div>
    <p class="statement biz-footer">${t.footer}</p>`,
  notes: t.notes,

  animate(root) {
    const paid = root.querySelector('.biz-col.is-paid');
    const run = root.querySelectorAll('.biz-col.is-run, .biz-footer');
    gsap.set(paid, { opacity: 0, y: 16 });
    gsap.set(run, { opacity: 0, y: 16 });
    return [
      (tl) => {
        tl.from(root.querySelector('.biz-col.is-free'), { opacity: 0, y: 16, duration: 0.45 });
      },
      (tl) => {
        tl.to(paid, { opacity: 1, y: 0, duration: 0.45 });
      },
      (tl) => {
        tl.to(run, { opacity: 1, y: 0, duration: 0.45, stagger: 0.2 });
      },
    ];
  },
};
