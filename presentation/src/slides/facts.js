import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import './facts.css';

const t = slideText('facts');

/**
 * A fact as the app shows it: type, source, date, status and the two votes. The first click adds the four statuses
 * and the rules against abuse, the second marks the contradiction with OpenStreetMap.
 */
export default {
  id: 'facts',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <div class="facts-grid">
      <article class="fact-card">
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
    </div>`,
  notes: t.notes,

  animate(root) {
    const side = root.querySelectorAll('.statuses .chip, .facts-rules li');
    const conflict = root.querySelector('.fact-conflict');
    gsap.set(side, { opacity: 0, y: 12 });
    gsap.set(conflict, { opacity: 0 });
    return [
      (tl) => {
        tl.from(root.querySelector('.fact-card'), { opacity: 0, y: 24, duration: 0.5 });
      },
      (tl) => {
        tl.to(side, { opacity: 1, y: 0, duration: 0.35, stagger: 0.1 });
      },
      (tl) => {
        tl.to(conflict, { opacity: 1, duration: 0.45 });
      },
    ];
  },
};
