import { slideText } from '../lib/lang.js';
import './demo.css';

const t = slideText('demo');
const brand = slideText('title').heading;

/** The frame of the live demo: the four scenes the jury is about to see, in order, so the PDF tells them too. */
export default {
  id: 'demo',
  summary: t.summary,
  html: `
    <p class="brand">${brand}</p>
    <h2 class="slide-title">${t.heading}</h2>
    <div class="sheet">
      <ol class="demo-steps">
        ${t.steps.map((s, i) => `<li><span class="card-num">${i + 1}</span><div><h3>${s.head}</h3><p>${s.text}</p></div></li>`).join('')}
      </ol>
      <p class="note demo-note">${t.footnote}</p>
    </div>`,
  notes: t.notes,

  animate(root) {
    return [
      (tl) => {
        tl.from(root.querySelector('.slide-title'), { opacity: 0, y: 24, duration: 0.5, ease: 'power3.out' });
        tl.from(root.querySelector('.sheet'), { y: 110, duration: 0.6, ease: 'power3.out' }, '-=0.3');
        tl.from(root.querySelectorAll('.demo-steps li'), { opacity: 0, y: 16, duration: 0.4, stagger: 0.12, ease: 'power2.out' }, '-=0.25');
        tl.from(root.querySelector('.demo-note'), { opacity: 0, duration: 0.4 }, '-=0.1');
      },
    ];
  },
};
