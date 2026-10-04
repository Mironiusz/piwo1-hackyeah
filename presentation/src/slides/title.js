import { slideText } from '../lib/lang.js';
import { routeStates } from '../components/route-states.js';
import './title.css';

const t = slideText('title');

/**
 * The title slide: the challenge on a plate, the name at the scale of the frame, one line of promise, and on the
 * sheet the four segment states drawn as one route from A to B. Intro only.
 */
export default {
  id: 'title',
  summary: t.summary,
  html: `
    <p class="plate title-kicker">${t.kicker}</p>
    <h1 class="title-main">${t.heading}</h1>
    <p class="title-sub">${t.subtitle}</p>
    <div class="sheet">
      <svg class="title-route" viewBox="0 0 1600 268" aria-hidden="true">${routeStates({ x: 150, y: 176, width: 1300 })}</svg>
    </div>`,
  notes: t.notes,

  animate(root) {
    return [
      (tl) => {
        tl.from(root.querySelector('.title-main'), { opacity: 0, y: 44, duration: 0.6, ease: 'power3.out' });
        tl.from(root.querySelectorAll('.title-kicker, .title-sub'), { opacity: 0, y: 18, duration: 0.45, stagger: 0.12, ease: 'power2.out' }, '-=0.3');
        tl.from(root.querySelector('.sheet'), { y: 130, duration: 0.6, ease: 'power3.out' }, '-=0.4');
        tl.from(root.querySelectorAll('.rs-seg'), { opacity: 0, duration: 0.35, stagger: 0.16 }, '-=0.2');
      },
    ];
  },
};
