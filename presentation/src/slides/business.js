import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './business.css';

const t = slideText('business');
const brand = slideText('title').heading;

const column = (part, cls) => `<div class="biz-col ${cls}"><h3>${part.head}</h3><ul class="plain-list">${part.items.map((i) => `<li>${i}</li>`).join('')}</ul></div>`;

/** Who uses the app for free, who pays, and who runs it outside the infrastructure of the city, one column per click. */
export default {
  id: 'business',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <div class="biz-row">
        ${column(t.free, 'is-free')}
        ${column(t.paid, 'is-paid')}
        ${column(t.run, 'is-run')}
      </div>
    </div>
    <p class="plate biz-footer">${t.footer}</p>`,
  notes: t.notes,

  animate(root) {
    const paid = root.querySelector('.biz-col.is-paid');
    const run = root.querySelector('.biz-col.is-run');
    const footer = root.querySelector('.biz-footer');
    gsap.set(paid, { opacity: 0, y: 16 });
    gsap.set(run, { opacity: 0, y: 16 });
    gsap.set(footer, { opacity: 0, y: -18 });
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelector('.biz-col.is-free'), { opacity: 0, y: 16, duration: 0.45, ease: 'power2.out' }, '-=0.25');
      },
      (tl) => {
        tl.to(paid, { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' });
      },
      (tl) => {
        tl.to(run, { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' });
        tl.to(footer, { opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.6)' }, '+=0.1');
      },
    ];
  },
};
