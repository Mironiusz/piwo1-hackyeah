import { slideText } from '../lib/lang.js';
import './data.css';

const t = slideText('data');
const brand = slideText('title').heading;

const row = (cells) =>
  `<tr><th scope="row">${cells[0]}</th>${cells
    .slice(1)
    .map((c) => `<td>${c}</td>`)
    .join('')}</tr>`;

/** The data sources with what each gives, how fresh it is and what happens when it is unavailable, as one table. */
export default {
  id: 'data',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <table class="data-table">
        <thead><tr>${t.head.map((h) => `<th scope="col">${h}</th>`).join('')}</tr></thead>
        <tbody>${t.rows.map(row).join('')}</tbody>
      </table>
    </div>
    <p class="plate data-footer">${t.footer}</p>`,
  notes: t.notes,

  animate(root) {
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelectorAll('.data-table tbody tr'), { opacity: 0, y: 12, duration: 0.35, stagger: 0.12, ease: 'power2.out' }, '-=0.25');
        tl.from(root.querySelector('.data-footer'), { opacity: 0, y: -18, duration: 0.5, ease: 'back.out(1.6)' }, '-=0.1');
      },
    ];
  },
};
