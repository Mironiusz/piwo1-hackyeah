import { slideText } from '../lib/lang.js';
import { routeStates } from '../components/route-states.js';
import './title.css';

const t = slideText('title');

/** The title slide: the name, one line of promise and the four segment states drawn as one route. Intro only. */
export default {
  id: 'title',
  summary: t.summary,
  html: `
    <div class="title-slide">
      <p class="kicker">${t.kicker}</p>
      <h1 class="title-main">${t.heading}</h1>
      <p class="title-sub">${t.subtitle}</p>
      <svg class="title-route" viewBox="0 0 1440 260" aria-hidden="true">${routeStates({ x: 60, y: 170, width: 1320 })}</svg>
    </div>`,
  notes: t.notes,

  animate(root) {
    return [
      (tl) => {
        tl.from(root.querySelectorAll('.kicker, .title-main, .title-sub'), { opacity: 0, y: 24, duration: 0.6, stagger: 0.12, ease: 'power2.out' });
        tl.from(root.querySelectorAll('.rs-seg'), { opacity: 0, duration: 0.4, stagger: 0.18 }, '-=0.2');
      },
    ];
  },
};
