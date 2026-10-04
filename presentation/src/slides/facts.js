import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './facts.css';

const t = slideText('facts');
const brand = slideText('title').heading;

/**
 * A fact as the app shows it, set straight on the sheet: type, source, date, status and the two votes. The first
 * click adds the four statuses and the rules against abuse, the second marks the contradiction with OpenStreetMap.
 */
export default {
  id: 'facts',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <div class="facts-grid">
        <article class="fact">
          <h3>${t.card.type}</h3>
          <dl>
            <dt>${t.card.sourceLabel}</dt><dd>${t.card.source}</dd>
            <dt>${t.card.dateLabel}</dt><dd>${t.card.date}</dd>
            <dt>${t.card.statusLabel}</dt><dd><span class="status-chip">${t.card.status}</span></dd>
          </dl>
          <div class="fact-conflict">
            <p class="fact-conflict-head">${t.card.conflict}</p>
            <p>${t.card.rule}</p>
          </div>
          <div class="vote-row">${t.votes.map((v) => `<span class="vote-btn">${v}</span>`).join('')}</div>
        </article>
        <div class="facts-side">
          <ul class="chip-row statuses">${t.statuses.map((s) => `<li class="chip">${s}</li>`).join('')}</ul>
          <ul class="plain-list facts-rules">${t.rules.map((r) => `<li>${r}</li>`).join('')}</ul>
        </div>
      </div>
    </div>`,
  notes: t.notes,

  animate(root) {
    const side = root.querySelector('.facts-side');
    const sideItems = root.querySelectorAll('.statuses .chip, .facts-rules li');
    const conflict = root.querySelector('.fact-conflict');
    gsap.set(side, { opacity: 0 });
    gsap.set(sideItems, { opacity: 0, y: 12 });
    gsap.set(conflict, { opacity: 0 });
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelector('.fact'), { opacity: 0, y: 20, duration: 0.45, ease: 'power2.out' }, '-=0.25');
      },
      (tl) => {
        tl.to(side, { opacity: 1, duration: 0.3, ease: 'power2.out' });
        tl.to(sideItems, { opacity: 1, y: 0, duration: 0.35, stagger: 0.1, ease: 'power2.out' }, '<');
      },
      (tl) => {
        tl.to(conflict, { opacity: 1, duration: 0.45 });
      },
    ];
  },
};
