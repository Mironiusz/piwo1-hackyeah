import { gsap } from 'gsap';

import { ARROW } from '../components/icons.js';
import { slideText } from '../lib/lang.js';
import './architecture.css';

const t = slideText('architecture');

const column = (part, cls) => `<div class="arch-col ${cls}"><h3>${part.head}</h3><ul>${part.items.map((i) => `<li>${i}</li>`).join('')}</ul></div>`;

/**
 * Data acquisition apart from presentation: the ingest column, then the API and its two clients, then how a source,
 * a category and a city are added and what stays private.
 */
export default {
  id: 'architecture',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <div class="arch-row">
      ${column(t.ingest, 'is-ingest')}
      <span class="arch-arrow">${ARROW}</span>
      ${column(t.api, 'is-api')}
      <span class="arch-arrow">${ARROW}</span>
      ${column(t.clients, 'is-clients')}
    </div>
    <div class="arch-bottom">
      <div><h3>${t.extendHead}</h3><ul class="plain-list">${t.extend.map((e) => `<li>${e}</li>`).join('')}</ul></div>
      <div><h3>${t.privacyHead}</h3><ul class="plain-list">${t.privacy.map((p) => `<li>${p}</li>`).join('')}</ul></div>
    </div>`,
  notes: t.notes,

  animate(root) {
    const serving = root.querySelectorAll('.arch-arrow, .arch-col.is-api, .arch-col.is-clients');
    const bottom = root.querySelectorAll('.arch-bottom > div');
    gsap.set(serving, { opacity: 0 });
    gsap.set(bottom, { opacity: 0, y: 16 });
    return [
      (tl) => {
        tl.from(root.querySelector('.arch-col.is-ingest'), { opacity: 0, y: 16, duration: 0.45 });
      },
      (tl) => {
        tl.to(serving, { opacity: 1, duration: 0.4, stagger: 0.15 });
      },
      (tl) => {
        tl.to(bottom, { opacity: 1, y: 0, duration: 0.4, stagger: 0.15 });
      },
    ];
  },
};
