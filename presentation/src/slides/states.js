import { gsap } from 'gsap';

import { slideText } from '../lib/lang.js';
import { routeStates, stateSample } from '../components/route-states.js';
import './states.css';

const t = slideText('states');

/**
 * The four segment states with their legend, then the rule that missing data is never shown as accessible, then
 * the same route in grayscale to prove the states do not depend on color.
 */
export default {
  id: 'states',
  summary: t.summary,
  html: `
    <h2 class="slide-title">${t.heading}</h2>
    <div class="states-routes">
      <svg class="states-route" viewBox="0 0 1100 200" role="img" aria-label="${t.legend.map((l) => l.label).join(', ')}">${routeStates({ x: 40, y: 150, width: 1020 })}</svg>
      <div class="states-gray">
        <svg class="states-route is-gray" viewBox="0 0 1100 200" aria-hidden="true">${routeStates({ x: 40, y: 150, width: 1020 })}</svg>
        <p class="states-gray-label">${t.grayscale}</p>
      </div>
    </div>
    <ul class="legend">${t.legend.map((l) => `<li>${stateSample(l.key)}<span>${l.label}</span></li>`).join('')}</ul>
    <p class="statement is-accent states-rule">${t.rule}</p>
    <p class="footnote states-channels">${t.channels}</p>`,
  notes: t.notes,

  animate(root) {
    const rule = root.querySelector('.states-rule');
    const gray = root.querySelectorAll('.states-gray, .states-channels');
    gsap.set(rule, { opacity: 0, y: 16 });
    gsap.set(gray, { opacity: 0 });
    return [
      (tl) => {
        tl.from(root.querySelectorAll('.states-route:not(.is-gray) .rs-seg'), { opacity: 0, duration: 0.35, stagger: 0.2 });
        tl.from(root.querySelectorAll('.legend li'), { opacity: 0, x: -12, duration: 0.3, stagger: 0.12 }, '<');
      },
      (tl) => {
        tl.to(rule, { opacity: 1, y: 0, duration: 0.45 });
      },
      (tl) => {
        tl.to(gray, { opacity: 1, duration: 0.5 });
      },
    ];
  },
};
