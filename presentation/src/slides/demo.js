import { slideText } from '../lib/lang.js';
import './demo.css';

const t = slideText('demo');

/** The frame of the live demo: the four scenes the jury is about to see, in order, so the PDF tells them too. */
export default {
  id: 'demo',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <ol class="demo-steps">
      ${t.steps.map((s, i) => `<li><span class="card-num">${i + 1}</span><div><h3>${s.head}</h3><p>${s.text}</p></div></li>`).join('')}
    </ol>
    <p class="footnote">${t.footnote}</p>`,
  notes: t.notes,

  animate(root) {
    return [
      (tl) => {
        tl.from(root.querySelectorAll('.demo-steps li'), { opacity: 0, y: 16, duration: 0.4, stagger: 0.12 });
      },
    ];
  },
};
