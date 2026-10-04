import { slideText } from '../lib/lang.js';
import './data.css';

const t = slideText('data');

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
    <h2 class="slide-title">${t.heading}</h2>
    <table class="data-table">
      <thead><tr>${t.head.map((h) => `<th scope="col">${h}</th>`).join('')}</tr></thead>
      <tbody>${t.rows.map(row).join('')}</tbody>
    </table>
    <p class="statement data-footer">${t.footer}</p>`,
  notes: t.notes,

  animate(root) {
    return [
      (tl) => {
        tl.from(root.querySelectorAll('.data-table tbody tr'), { opacity: 0, y: 12, duration: 0.35, stagger: 0.12 });
      },
    ];
  },
};
